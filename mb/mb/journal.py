"""Business-readable git journal facts for status and handoff surfaces."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from mb import checkpoint_verbs

FIELD_SEP = "\x1f"
JOURNAL_SCHEMA_VERSION = "0.current"
DEFAULT_LIMIT = 12
VALID_LOOPS = {"sense", "decide", "ship", "reflect"}
SECTION_RE = re.compile(r"^\S[^:]*:\s*$")
GITHUB_ISSUE_RE = re.compile(r"(?:https?://github\.com/([^/\s]+)/([^/\s]+)/issues/(\d+)|#(\d+))")


def _run_git(repo: Path, args: list[str], timeout: float = 4.0) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=str(repo),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        return subprocess.CompletedProcess(["git", *args], 127, "", str(exc))
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(["git", *args], 124, "", "timed out")
    except subprocess.SubprocessError as exc:
        return subprocess.CompletedProcess(["git", *args], 1, "", str(exc))


def _git_root(repo: Path) -> tuple[Path | None, str]:
    result = _run_git(repo, ["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        return None, (result.stderr or result.stdout).strip() or "not a git repo"
    return Path(result.stdout.strip()).resolve(), ""


def _commit_shas(
    repo: Path,
    *,
    limit: int,
    since: str | None = None,
    rev_range: str | None = None,
) -> tuple[list[str], str]:
    args = ["log", f"--max-count={limit}", "--format=%H"]
    if rev_range:
        args.append(rev_range)
    elif since:
        args.append(f"--since={since}")
    result = _run_git(repo, args)
    if result.returncode != 0:
        return [], (result.stderr or result.stdout).strip()
    return [line.strip() for line in result.stdout.splitlines() if line.strip()], ""


def _commit_metadata(repo: Path, sha: str) -> dict[str, Any] | None:
    result = _run_git(
        repo,
        [
            "show",
            "-s",
            "--date=short",
            f"--format=%H{FIELD_SEP}%h{FIELD_SEP}%aI{FIELD_SEP}%ad{FIELD_SEP}%s{FIELD_SEP}%b",
            sha,
        ],
    )
    if result.returncode != 0:
        return None
    parts = result.stdout.rstrip("\n").split(FIELD_SEP, 5)
    if len(parts) != 6:
        return None
    full_sha, short_sha, authored_at, date, subject, body = parts
    return {
        "sha": full_sha,
        "commit": short_sha,
        "authored_at": authored_at,
        "date": date,
        "subject": subject,
        "body": body,
    }


def _commit_files(repo: Path, sha: str) -> list[str]:
    result = _run_git(repo, ["show", "--name-only", "--format=", "--no-renames", sha])
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _strip_ref_marker(line: str) -> str:
    stripped = line.strip()
    if stripped.startswith("- "):
        return stripped[2:].strip()
    return stripped


def _raw_refs_from_body(body: str) -> list[str]:
    refs: list[str] = []
    collecting = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            if collecting and refs:
                break
            continue
        if line.lower().startswith("refs:"):
            collecting = True
            inline = line[5:].strip()
            if inline:
                refs.extend(part.strip() for part in re.split(r"[, ]+", inline) if part.strip())
            continue
        if collecting and SECTION_RE.match(line):
            break
        if collecting:
            refs.append(_strip_ref_marker(line))
    return [ref for ref in refs if ref]


def parse_refs(body: str) -> list[dict[str, Any]]:
    """Parse business refs from the commit body ``Refs:`` section."""
    items: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw_ref in _raw_refs_from_body(body):
        ref = raw_ref.strip().strip("<>")
        kind = "link"
        slug = ""
        number: int | None = None
        legacy = False
        path = ""
        url = ""
        github_match = GITHUB_ISSUE_RE.search(ref)
        if github_match:
            kind = "github_issue"
            number_text = github_match.group(3) or github_match.group(4) or "0"
            number = int(number_text)
            if github_match.group(1) and github_match.group(2):
                url = (
                    f"https://github.com/{github_match.group(1)}/"
                    f"{github_match.group(2)}/issues/{number}"
                )
        elif re.match(r"^bets/[^/]+\.md$", ref):
            kind = "bet"
            path = ref
            slug = Path(ref).stem
        elif re.match(r"^decisions/[^/]+\.md$", ref):
            kind = "decision"
            path = ref
            slug = Path(ref).stem
        elif re.match(r"^pushes/[^/]+/push\.md$", ref):
            kind = "push"
            path = ref
            slug = Path(ref).parent.name
        elif re.match(r"^campaigns/[^/]+/campaign\.md$", ref):
            kind = "legacy_campaign"
            path = ref
            slug = Path(ref).parent.name
            legacy = True
        elif re.match(r"^https?://", ref):
            url = ref
        else:
            path = ref

        key_value = (url or path or f"#{number}") if number else ref
        key = (kind, str(key_value))
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "kind": kind,
                "value": ref,
                "path": path,
                "slug": slug,
                "url": url,
                "number": number,
                "legacy": legacy,
            }
        )
    return items


def _path_loop(path: str) -> str | None:
    if path.startswith(("core/", "reference/core/", "research/", "documents/")):
        return "sense"
    if path.startswith("decisions/"):
        return "decide"
    if path.startswith(("pushes/", "campaigns/")):
        return "ship"
    if path.startswith(("bets/", "log/")):
        return "reflect"
    return None


def _path_channel(path: str) -> str | None:
    if path.startswith("pushes/") or path.startswith("campaigns/"):
        return "pages" if "/site" in path or "lander" in path else None
    if path.startswith(("core/operations/", "reference/core/operations/", ".mb/")):
        return "ops"
    return None


def _best_loop(parsed: dict[str, Any], files: list[str], refs: list[dict[str, Any]]) -> str | None:
    verb = str(parsed.get("verb") or "")
    if verb in {"decided", "opened"}:
        return "decide"
    if verb == "closed":
        return "reflect"
    if verb in {"drafted", "shipped", "connected", "ran", "fixed"}:
        return "ship"
    for ref in refs:
        kind = ref.get("kind")
        if kind in {"bet", "legacy_campaign"} and verb == "closed":
            return "reflect"
        if kind == "bet" and verb == "opened":
            return "decide"
        if kind in {"push", "legacy_campaign"}:
            return "ship"
        if kind == "decision":
            return "decide"
    for file in files:
        loop = _path_loop(file)
        if loop:
            return loop
    loop = parsed.get("loop")
    return str(loop) if loop in VALID_LOOPS else None


def _best_channel(
    parsed: dict[str, Any],
    files: list[str],
    refs: list[dict[str, Any]],
) -> str | None:
    hint = parsed.get("channel_hint")
    if hint and hint != "path-derived":
        return str(hint)
    for file in files:
        channel = _path_channel(file)
        if channel:
            return channel
    if any(ref.get("kind") == "push" for ref in refs):
        return "pages"
    return None


def _target_kind(parsed: dict[str, Any], files: list[str], refs: list[dict[str, Any]]) -> str:
    for ref in refs:
        kind = str(ref.get("kind") or "")
        if kind in {"bet", "push", "decision", "legacy_campaign", "github_issue"}:
            return kind
    first_file = files[0] if files else ""
    if first_file.startswith("bets/"):
        return "bet"
    if first_file.startswith("pushes/"):
        return "push"
    if first_file.startswith("campaigns/"):
        return "legacy_campaign"
    if first_file.startswith("decisions/"):
        return "decision"
    if first_file.startswith(("core/", "reference/core/")):
        return "core"
    if first_file.startswith("research/"):
        return "research"
    return str(parsed.get("object") or "work")


def _event_summary(parsed: dict[str, Any], subject: str, recognized_as: str) -> str:
    if recognized_as == "legacy_checkpoint":
        remainder = subject.removeprefix("[checkpoint]").strip()
        return f"Saved checkpoint: {remainder or subject}"
    verb = str(parsed.get("verb") or "").strip()
    obj = str(parsed.get("object") or "").strip()
    result = str(parsed.get("result") or "").strip()
    if not verb or not obj:
        return subject
    words = f"{verb.capitalize()} {obj}"
    if result:
        words += f": {result}"
    return words


def event_from_commit(commit: dict[str, Any], files: list[str]) -> dict[str, Any]:
    """Turn one git commit into a business journal event."""
    subject = str(commit.get("subject") or "")
    parsed = checkpoint_verbs.parse_subject(subject)
    legacy_checkpoint = subject.startswith("[checkpoint]")
    refs = parse_refs(str(commit.get("body") or ""))
    recognized_as = (
        "legacy_checkpoint"
        if legacy_checkpoint
        else "business_verb"
        if parsed.get("recognized")
        else "unrecognized"
    )
    loop = _best_loop(parsed, files, refs)
    channel = _best_channel(parsed, files, refs)
    return {
        "id": str(commit.get("sha") or ""),
        "sha": str(commit.get("sha") or ""),
        "commit": str(commit.get("commit") or ""),
        "date": str(commit.get("date") or ""),
        "authored_at": str(commit.get("authored_at") or ""),
        "subject": subject,
        "summary": _event_summary(parsed, subject, recognized_as),
        "recognized_as": recognized_as,
        "verb": parsed.get("verb"),
        "object": parsed.get("object") or "",
        "result": parsed.get("result") or "",
        "loop": loop,
        "loops": parsed.get("loops") or ([] if loop is None else [loop]),
        "channel": channel,
        "channel_hint": parsed.get("channel_hint"),
        "target_kind": _target_kind(parsed, files, refs),
        "refs": refs,
        "files": files[:12],
        "file_count": len(files),
        "safe_to_share": True,
    }


def _group_label(loop: str | None) -> str:
    return {
        "sense": "Sensed business context",
        "decide": "Made decisions",
        "ship": "Shipped work",
        "reflect": "Captured lessons",
    }.get(loop or "", "Other activity")


def group_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group journal events into loop-oriented activity buckets."""
    order = ["sense", "decide", "ship", "reflect", None]
    groups: list[dict[str, Any]] = []
    for loop in order:
        matching = [event for event in events if event.get("loop") == loop]
        if not matching:
            continue
        refs = [ref for event in matching for ref in event.get("refs", []) if isinstance(ref, dict)]
        groups.append(
            {
                "loop": loop,
                "label": _group_label(loop),
                "count": len(matching),
                "summaries": [
                    str(event.get("summary") or event.get("subject")) for event in matching[:5]
                ],
                "events": [str(event.get("id") or "") for event in matching],
                "refs": refs[:12],
                "safe_to_share": True,
            }
        )
    return groups


def _summary(events: list[dict[str, Any]], groups: list[dict[str, Any]]) -> dict[str, Any]:
    refs = [ref for event in events for ref in event.get("refs", []) if isinstance(ref, dict)]
    recognized = [event for event in events if event.get("recognized_as") == "business_verb"]
    legacy = [event for event in events if event.get("recognized_as") == "legacy_checkpoint"]
    unrecognized = [event for event in events if event.get("recognized_as") == "unrecognized"]
    return {
        "events": len(events),
        "groups": len(groups),
        "recognized_events": len(recognized),
        "legacy_checkpoints": len(legacy),
        "unrecognized_events": len(unrecognized),
        "refs": len(refs),
    }


def collect(
    repo: str | Path = ".",
    *,
    limit: int = DEFAULT_LIMIT,
    since: str | None = "14 days ago",
    rev_range: str | None = None,
) -> dict[str, Any]:
    """Collect recent business-readable git journal events."""
    target = Path(repo).resolve()
    root, root_error = _git_root(target)
    if root is None:
        return {
            "available": False,
            "ok": False,
            "repo": str(target),
            "schema_version": JOURNAL_SCHEMA_VERSION,
            "events": [],
            "groups": [],
            "summary": {
                "events": 0,
                "groups": 0,
                "recognized_events": 0,
                "legacy_checkpoints": 0,
                "unrecognized_events": 0,
                "refs": 0,
            },
            "error": root_error,
            "safe_to_share": True,
        }
    shas, log_error = _commit_shas(root, limit=limit, since=since, rev_range=rev_range)
    if log_error:
        return {
            "available": False,
            "ok": False,
            "repo": str(root),
            "schema_version": JOURNAL_SCHEMA_VERSION,
            "events": [],
            "groups": [],
            "summary": _summary([], []),
            "error": log_error,
            "safe_to_share": True,
        }
    events: list[dict[str, Any]] = []
    for sha in shas:
        metadata = _commit_metadata(root, sha)
        if metadata is None:
            continue
        events.append(event_from_commit(metadata, _commit_files(root, sha)))
    groups = group_events(events)
    return {
        "available": True,
        "ok": True,
        "repo": str(root),
        "schema_version": JOURNAL_SCHEMA_VERSION,
        "events": events,
        "groups": groups,
        "summary": _summary(events, groups),
        "error": "",
        "safe_to_share": True,
    }
