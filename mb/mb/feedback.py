"""Local friction log for ``mb feedback`` (#986).

Agents and operators hit friction in ``mb``: a refused command, a confusing
message, a missing probe. ``mb feedback "<text>"`` appends one JSON line to a
local file in the user state directory so the friction survives the session,
and ``mb feedback rollup`` turns the file into a Markdown draft a maintainer
can turn into issues.
Nothing here sends anything anywhere. Every line is scrubbed before it is
written: secret-shaped text is redacted with connect's patterns and home
directory paths become ``~``.
"""

from __future__ import annotations

import functools
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mb import __version__
from mb.durable import state_lock
from mb.freshness import looks_like_business_repo

SCHEMA_VERSION = 1
FEEDBACK_FILENAME = "feedback.jsonl"
MAX_TEXT_CHARS = 4000

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


def _replace_home(text: str) -> str:
    home = str(Path.home())
    if home and home not in {"/", "\\"}:
        text = text.replace(home, "~")
    return _OTHER_HOME_RE.sub("~", text)


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

    cleaned = _redact_sensitive_text(text)
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


def render_record(result: dict[str, Any]) -> None:
    if not result["ok"]:
        for error in result["errors"]:
            print(f"mb feedback: {error['message']}")
        return
    print(f"Saved to {result['path']} (local only; nothing was sent).")
    print("Run `mb feedback rollup` to see this week's friction grouped by command.")
