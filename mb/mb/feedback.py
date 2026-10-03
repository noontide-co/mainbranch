"""Local friction log for ``mb feedback`` (#986).

Agents and operators hit friction in ``mb``: a refused command, a confusing
message, a missing probe. ``mb feedback "<text>"`` appends one JSON line to a
local file in the user state directory so the friction survives the session,
and ``mb feedback rollup`` turns the file into a Markdown draft a maintainer
can turn into issues. Credential and safety refusals log themselves through
``record_refusal``.

Nothing here sends anything anywhere. Every line is scrubbed before it is
written: secret-shaped text is redacted with connect's patterns and home
directory paths become ``~``. A refusal line carries the rule that fired and
the command, never the refused value.
"""

from __future__ import annotations

import functools
import json
import os
import re
from collections.abc import Iterator
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from mb import __version__
from mb.durable import atomic_write_text, state_lock
from mb.freshness import looks_like_business_repo

SCHEMA_VERSION = 1
FEEDBACK_FILENAME = "feedback.jsonl"
LOG_ENV_VAR = "MB_FEEDBACK_LOG"
SUBCOMMANDS = ("rollup", "list", "clear")
KINDS = ("feedback", "refusal")
MAX_TEXT_CHARS = 4000
DEFAULT_SINCE = "7d"

_SINCE_RE = re.compile(r"^\s*(\d+)\s*([hdw])\s*$", re.IGNORECASE)
# Home directories of any user, in case text quotes another account's path.
_OTHER_HOME_RE = re.compile(
    r"(?<![\w~])(?:/Users|/home)/[^/\s\"'`]+|[A-Za-z]:\\Users\\[^\\\s\"'`]+"
)


def state_dir() -> Path:
    """Return the Main Branch user state directory (honours ``XDG_STATE_HOME``)."""
    base = os.environ.get("XDG_STATE_HOME", "").strip()
    root = Path(base).expanduser() if base else Path.home() / ".local" / "state"
    return root / "mainbranch"


def feedback_path() -> Path:
    return state_dir() / FEEDBACK_FILENAME


def display_path(path: Path) -> str:
    """Render a path for output without an absolute path in it.

    Paths under the state directory read as ``$XDG_STATE_HOME/...`` when that
    variable is set, else the home directory reads as ``~``.
    """
    base = os.environ.get("XDG_STATE_HOME", "").strip()
    if base:
        try:
            return "$XDG_STATE_HOME/" + path.relative_to(Path(base).expanduser()).as_posix()
        except ValueError:
            pass
    return scrub(str(path))


def refusal_logging_enabled() -> bool:
    return os.environ.get(LOG_ENV_VAR, "").strip().lower() not in {"0", "false", "no", "off"}


def _replace_home(text: str) -> str:
    home = str(Path.home())
    if home and home not in {"/", "\\"}:
        text = text.replace(home, "~")
    return _OTHER_HOME_RE.sub("~", text)


# Key names that mark the value beside them as a secret. ``auth`` and ``sig``
# only count as whole words so ``author`` and ``design`` stay readable.
_SECRET_KEY = (
    r"[A-Za-z0-9_.-]*(?:token|secret|passw(?:or)?d|pwd|api[_-]?key|credentials?|"
    r"authorization|auth(?![a-z])|private[_-]?key|access[_-]?key|signature|sig(?![a-z]))"
    r"[A-Za-z0-9_.-]*"
)
_SECRET_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    # Before the key rule, which would otherwise take ``Basic`` or ``Bearer`` as the value.
    (re.compile(r"(?i)\b((?:basic|bearer)\s+)[A-Za-z0-9+/=._~-]{8,}"), r"\1<redacted>"),
    # scheme://user:password@host
    (re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://[^\s:/@]+:)[^\s@/]+@"), r"\1<redacted>@"),
    # "token": "value" and 'api_key': 'value'
    (
        re.compile(rf"(?i)([\"'])({_SECRET_KEY})\1(\s*:\s*)([\"'])[^\"'\n]*\4"),
        r"\1\2\1\3\4<redacted>\4",
    ),
    # GITHUB_TOKEN=value, export X_SECRET="value", ?client_secret=value
    (
        re.compile(rf"(?i)(?<![A-Za-z0-9_.-])({_SECRET_KEY})(\s*[:=]\s*)([\"']?)[^\s\"',;&]+\3"),
        r"\1\2\3<redacted>\3",
    ),
    # Provider token families, including GitHub's underscore family.
    (
        re.compile(
            r"(?<![\w-])(?:gh[pousr]_|github_pat_|glpat-|xox[abposr]-|"
            r"sk-(?:proj-|live-|test-)?|sk_(?:live|test)_|rk_(?:live|test)_|hf_|npm_|"
            r"pypi-|AIza|fal-)[A-Za-z0-9_-]{8,}"
        ),
        "<redacted>",
    ),
    (re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"), "<redacted>"),
)


@functools.cache
def _credential_token_re() -> re.Pattern[str]:
    from mb.connect import CREDENTIAL_VALUE_PREFIXES

    return re.compile(
        r"(?<![\w-])(?:"
        + "|".join(re.escape(prefix) for prefix in CREDENTIAL_VALUE_PREFIXES)
        + r")[A-Za-z0-9_\-]{8,}"
    )


def scrub(text: str) -> str:
    """Redact secret-shaped values and absolute paths from ``text``.

    Home-directory paths become ``~``; any other absolute path that ``mb issue``
    would scrub becomes ``<local-path>``.
    """
    # Imported here so connect can call ``record_refusal`` without an import cycle.
    from mb.connect import SECRET_REPLACEMENT, _redact_sensitive_text
    from mb.issue import ABSOLUTE_PATH_RE, QUERY_SECRET_RE, TOKEN_RE

    cleaned = text
    for pattern, replacement in _SECRET_RULES:
        cleaned = pattern.sub(replacement, cleaned)
    cleaned = _redact_sensitive_text(cleaned)
    cleaned = _credential_token_re().sub(SECRET_REPLACEMENT, cleaned)
    cleaned = TOKEN_RE.sub(SECRET_REPLACEMENT, cleaned)
    cleaned = QUERY_SECRET_RE.sub(lambda match: f"{match.group(1)}{SECRET_REPLACEMENT}", cleaned)
    cleaned = _replace_home(cleaned)
    cleaned = ABSOLUTE_PATH_RE.sub("<local-path>", cleaned)
    if len(cleaned) > MAX_TEXT_CHARS:
        cleaned = cleaned[:MAX_TEXT_CHARS] + " [truncated]"
    return cleaned


def repo_kind(repo: str | Path = ".") -> str:
    """Classify the repo a line was written from.

    One function so the classifier can be swapped for ``topology.classify_repo``
    once it lands; until then a business repo reads as ``hub`` and anything
    else as ``unknown``.
    """
    try:
        return "hub" if looks_like_business_repo(Path(repo).resolve()) else "unknown"
    except OSError:
        return "unknown"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clean_label(value: str | None) -> str:
    return scrub(" ".join((value or "").split()))[:200]


def _append(entry: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    line = json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n"
    with state_lock(path, timeout=2.0):
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as handle:
            handle.write(line)


def record(
    text: str,
    *,
    command: str | None = None,
    repo: str | Path = ".",
    path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Append one scrubbed ``kind: feedback`` line."""
    target = path or feedback_path()
    body = scrub(text.strip())
    if not body:
        return {
            "ok": False,
            "errors": [{"code": "empty_feedback", "message": "feedback text is empty"}],
            "path": display_path(target),
            "safe_to_share": True,
        }
    entry = {
        "schema": SCHEMA_VERSION,
        "kind": "feedback",
        "time": _iso(now or _now()),
        "mb_version": __version__,
        "command": _clean_label(command) or None,
        "repo_kind": repo_kind(repo),
        "text": body,
    }
    try:
        _append(entry, target)
    except (OSError, TimeoutError) as exc:
        return {
            "ok": False,
            "errors": [
                {
                    "code": "feedback_write_failed",
                    "message": scrub(f"could not write the feedback file: {exc.strerror or exc}"),
                }
            ],
            "path": display_path(target),
            "safe_to_share": True,
        }
    return {
        "ok": True,
        "entry": entry,
        "path": display_path(target),
        "sent": False,
        "safe_to_share": True,
    }


def record_refusal(
    rule: str,
    command: str,
    *,
    repo: str | Path = ".",
    path: Path | None = None,
) -> bool:
    """Append a ``kind: refusal`` line for a credential or safety boundary.

    Callers pass the rule that fired and the command, never the refused value.
    Logging is best effort: it never raises and never changes the refusal.
    ``MB_FEEDBACK_LOG=0`` turns it off. Returns whether a line was written.
    """
    if not refusal_logging_enabled():
        return False
    try:
        entry = {
            "schema": SCHEMA_VERSION,
            "kind": "refusal",
            "time": _iso(_now()),
            "mb_version": __version__,
            "command": _clean_label(command) or None,
            "rule": _clean_label(rule) or "unknown",
            "repo_kind": repo_kind(repo),
        }
        _append(entry, path or feedback_path())
    except Exception:  # noqa: BLE001 - logging must never break the refusal itself
        return False
    return True


def _iter_lines(path: Path) -> Iterator[dict[str, Any] | None]:
    try:
        handle = path.open(encoding="utf-8")
    except FileNotFoundError:
        return
    with handle:
        for raw in handle:
            if not raw.strip():
                continue
            try:
                item = json.loads(raw)
            except json.JSONDecodeError:
                yield None
                continue
            yield item if isinstance(item, dict) and isinstance(item.get("time"), str) else None


def _parse_time(value: str) -> datetime | None:
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment


def read_entries(path: Path | None = None) -> tuple[list[dict[str, Any]], int]:
    """Return parsed entries oldest first and the count of unreadable lines."""
    entries: list[dict[str, Any]] = []
    skipped = 0
    for item in _iter_lines(path or feedback_path()):
        if item is None or _parse_time(item["time"]) is None:
            skipped += 1
            continue
        entries.append(item)
    entries.sort(key=lambda item: item["time"])
    return entries, skipped


def parse_since(value: str, *, now: datetime | None = None) -> datetime:
    """Parse ``7d`` / ``12h`` / ``2w`` or an ISO date into a UTC cutoff."""
    current = now or _now()
    match = _SINCE_RE.match(value or "")
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()
        delta = {"h": timedelta(hours=amount), "d": timedelta(days=amount)}.get(
            unit, timedelta(weeks=amount)
        )
        return current - delta
    return _parse_date(value)


def _parse_date(value: str) -> datetime:
    text = (value or "").strip()
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        moment = _parse_time(text)
        if moment is None:
            raise ValueError(
                "expected a duration such as 7d, 12h or 2w, or a date such as "
                f"2026-10-01; got {text!r}"
            ) from None
        return moment
    return datetime(parsed.year, parsed.month, parsed.day, tzinfo=timezone.utc)


def _since_filter(entries: list[dict[str, Any]], cutoff: datetime | None) -> list[dict[str, Any]]:
    if cutoff is None:
        return entries
    return [item for item in entries if (_parse_time(item["time"]) or cutoff) >= cutoff]


def list_entries(
    *,
    since: str | None = None,
    kind: str | None = None,
    limit: int = 50,
    path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return the newest ``limit`` entries, optionally filtered by window and kind."""
    target = path or feedback_path()
    entries, skipped = read_entries(target)
    cutoff = parse_since(since, now=now) if since else None
    selected = _since_filter(entries, cutoff)
    if kind:
        selected = [item for item in selected if item.get("kind") == kind]
    total = len(selected)
    if limit > 0:
        selected = selected[-limit:]
    return {
        "ok": True,
        "path": display_path(target),
        "since": _iso(cutoff) if cutoff else None,
        "total": total,
        "shown": len(selected),
        "skipped_lines": skipped,
        "entries": selected,
        "safe_to_share": True,
    }


def rollup(
    *,
    since: str = DEFAULT_SINCE,
    path: Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Group entries in the window by kind, command and rule, with counts."""
    target = path or feedback_path()
    entries, skipped = read_entries(target)
    cutoff = parse_since(since, now=now)
    selected = _since_filter(entries, cutoff)
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in selected:
        kind = str(item.get("kind") or "feedback")
        command = str(item.get("command") or "")
        rule = str(item.get("rule") or "")
        key = (kind, command, rule)
        group = groups.setdefault(
            key,
            {
                "kind": kind,
                "command": command or None,
                "rule": rule or None,
                "count": 0,
                "oldest": item["time"],
                "newest": item["time"],
                "repo_kinds": [],
                "mb_versions": [],
                "texts": [],
            },
        )
        group["count"] += 1
        group["oldest"] = min(group["oldest"], item["time"])
        group["newest"] = max(group["newest"], item["time"])
        for field, value in (
            ("repo_kinds", item.get("repo_kind")),
            ("mb_versions", item.get("mb_version")),
        ):
            if value and value not in group[field]:
                group[field].append(value)
        text = item.get("text")
        if text:
            group["texts"].append(text)
    ordered = sorted(
        groups.values(),
        key=lambda group: (
            group["kind"] != "refusal",
            -group["count"],
            group["command"] or "",
            group["rule"] or "",
        ),
    )
    result = {
        "ok": True,
        "path": display_path(target),
        "since": _iso(cutoff),
        "window": since,
        "total": len(selected),
        "skipped_lines": skipped,
        "groups": ordered,
        "safe_to_share": True,
    }
    result["markdown"] = render_rollup_markdown(result)
    return result


def render_rollup_markdown(result: dict[str, Any]) -> str:
    """Render a rollup as a Markdown draft a maintainer can turn into issues."""
    lines = [
        "# mb feedback rollup",
        "",
        f"Window: since {result['since']} ({result['window']}). "
        f"Entries: {result['total']}. Local file: `{result['path']}`. Nothing was sent.",
    ]
    if result.get("skipped_lines"):
        lines.append(f"Unreadable lines skipped: {result['skipped_lines']}.")
    refusals = [group for group in result["groups"] if group["kind"] == "refusal"]
    notes = [group for group in result["groups"] if group["kind"] != "refusal"]
    if not result["groups"]:
        lines += ["", "No feedback or refusals in this window."]
        return "\n".join(lines) + "\n"
    if refusals:
        lines += [
            "",
            "## Refusals",
            "",
            "| Rule | Command | Count | Oldest | Newest |",
            "| --- | --- | ---: | --- | --- |",
        ]
        for group in refusals:
            lines.append(
                f"| `{group['rule'] or 'unknown'}` | `{group['command'] or '-'}` | "
                f"{group['count']} | {group['oldest']} | {group['newest']} |"
            )
    if notes:
        lines += ["", "## Feedback"]
        for group in notes:
            command = f"`{group['command']}`" if group["command"] else "No command given"
            lines += [
                "",
                f"### {command}: {group['count']} {'entry' if group['count'] == 1 else 'entries'}",
                "",
                f"Oldest {group['oldest']}, newest {group['newest']}. "
                f"Repo kinds: {', '.join(group['repo_kinds']) or 'unknown'}. "
                f"mb versions: {', '.join(group['mb_versions']) or 'unknown'}.",
                "",
            ]
            lines += [f"- {' '.join(text.split())}" for text in group["texts"]]
    return "\n".join(lines) + "\n"


def clear(*, before: str, path: Path | None = None) -> dict[str, Any]:
    """Drop entries older than ``before`` (a date or timestamp) and unreadable lines."""
    target = path or feedback_path()
    cutoff = _parse_date(before)
    if not target.exists():
        return {
            "ok": True,
            "path": display_path(target),
            "before": _iso(cutoff),
            "removed": 0,
            "kept": 0,
            "safe_to_share": True,
        }
    with state_lock(target):
        entries, skipped = read_entries(target)
        kept = [item for item in entries if (_parse_time(item["time"]) or cutoff) >= cutoff]
        removed = len(entries) - len(kept)
        text = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in kept)
        atomic_write_text(target, text)
    return {
        "ok": True,
        "path": display_path(target),
        "before": _iso(cutoff),
        "removed": removed,
        "removed_unreadable": skipped,
        "kept": len(kept),
        "safe_to_share": True,
    }


def render_record(result: dict[str, Any]) -> None:
    if not result["ok"]:
        for error in result["errors"]:
            print(f"mb feedback: {error['message']}")
        return
    print(f"Saved to {result['path']} (local only; nothing was sent).")
    print("Run `mb feedback rollup` to see this week's friction grouped by command.")


def render_list(result: dict[str, Any]) -> None:
    if not result["entries"]:
        print(f"No feedback in {result['path']}.")
        return
    for item in result["entries"]:
        kind = item.get("kind", "feedback")
        command = item.get("command") or "-"
        if kind == "refusal":
            print(f"{item['time']}  refusal  {command}  rule={item.get('rule') or 'unknown'}")
        else:
            print(f"{item['time']}  feedback  {command}  {item.get('text', '')}")
    if result["shown"] < result["total"]:
        print(f"Showing the newest {result['shown']} of {result['total']}; use --limit 0 for all.")


def render_clear(result: dict[str, Any]) -> None:
    print(
        f"Removed {result['removed']} entries before {result['before']}; "
        f"kept {result['kept']} in {result['path']}."
    )
