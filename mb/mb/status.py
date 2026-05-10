"""``mb status`` — cheap daily briefing for a Main Branch repo."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mb import __version__, github_activity, relationships
from mb import codex as codex_mod
from mb import connect as connect_mod
from mb import journal as journal_mod
from mb import onboard as onboard_mod
from mb import pushes as pushes_mod
from mb import ranker as ranker_mod
from mb import site as site_mod
from mb import topology as topology_mod
from mb import validate as validate_mod
from mb.engine import install_mode, link_status
from mb.freshness import format_update_alert, package_update_status

IMPORTANT_DIRS = (
    "core",
    "reference/core",
    "research",
    "decisions",
    "bets",
    "pushes",
    "campaigns",
    "log",
    "documents",
)
STATUS_SCHEMA_VERSION = "1.0"
LAST_STATUS_SEEN_RELATIVE_PATH = Path(".mb") / "last-status-seen.json"
LAST_STATUS_SEEN_GITIGNORE_ENTRY = ".mb/last-status-seen.json"
STALE_DECISION_DAYS = 14
STALE_RESEARCH_DAYS = 45
ACTIVE_BET_STATUSES = {"open", "paused"}
ACTIVE_PUSH_STATUSES = {"planned", "active", "paused"}
COMPLETED_PUSH_STATUSES = {"completed"}
LIVE_OFFER_STATUSES = {"accepted", "graduated", "running", "scaling"}
STALE_PUSH_DAYS = 14
PUSH_STATUSES_EXPECTING_PLAYBOOK = {"planned", "active"}
PLAYBOOK_STATUSES_NEEDING_ATTENTION = {"draft", "planned"}
PLAYBOOK_APPROVAL_STATUSES_NEEDING_ATTENTION = {"needed", "rejected", ""}
PLAYBOOK_PROVIDER_BOUNDARIES_NEEDING_ATTENTION = {
    "plan-only",
    "external-manual",
    "manual-provider",
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _run_command(args: list[str], cwd: Path | None = None, timeout: float = 3.0) -> dict[str, Any]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"ok": False, "returncode": 127, "stdout": "", "stderr": f"{args[0]} not found"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": 124, "stdout": "", "stderr": "command timed out"}
    except subprocess.SubprocessError as exc:
        return {"ok": False, "returncode": 1, "stdout": "", "stderr": str(exc)}
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _looks_like_mainbranch_repo(repo: Path) -> dict[str, Any]:
    markers = {
        "agents_md": (repo / "AGENTS.md").is_file(),
        "claude_md": (repo / "CLAUDE.md").is_file(),
        "core": (repo / "core").is_dir() or (repo / "reference" / "core").exists(),
        "research": (repo / "research").is_dir(),
        "decisions": (repo / "decisions").is_dir(),
        "skill_wiring": (repo / ".claude" / "skills" / "mb-start" / "SKILL.md").is_file(),
    }
    required_shape_count = sum(bool(markers[name]) for name in ("core", "research", "decisions"))
    looks_like = bool(markers["claude_md"] and required_shape_count >= 2)
    missing = [name for name, present in markers.items() if not present and name != "skill_wiring"]
    return {
        "looks_like_mainbranch_repo": looks_like,
        "markers": markers,
        "missing_markers": missing,
    }


def _git_info(repo: Path) -> dict[str, Any]:
    if not _which("git"):
        return {"available": False, "inside_work_tree": False, "error": "git not on PATH"}

    inside = _run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo)
    if not inside["ok"] or inside["stdout"].strip() != "true":
        return {
            "available": True,
            "inside_work_tree": False,
            "error": "not a git work tree",
        }

    branch = _run_command(["git", "branch", "--show-current"], cwd=repo)
    commit = _run_command(["git", "rev-parse", "--short", "HEAD"], cwd=repo)
    status = _run_command(["git", "status", "--porcelain"], cwd=repo)
    remote = _run_command(["git", "config", "--get", "remote.origin.url"], cwd=repo)

    dirty_lines = (
        [line for line in status["stdout"].splitlines() if line.strip()] if status["ok"] else []
    )
    return {
        "available": True,
        "inside_work_tree": True,
        "branch": branch["stdout"].strip() if branch["ok"] else "",
        "commit": commit["stdout"].strip() if commit["ok"] else "",
        "dirty": bool(dirty_lines),
        "dirty_count": len(dirty_lines),
        "dirty_files": dirty_lines[:10],
        "remote": remote["stdout"].strip() if remote["ok"] else "",
        "error": "" if status["ok"] else status["stderr"].strip(),
    }


def _git_recent_activity(repo: Path, git: dict[str, Any]) -> dict[str, Any]:
    if not git.get("inside_work_tree"):
        return {"available": False, "items": [], "error": git.get("error") or "git unavailable"}

    cmd = [
        "git",
        "log",
        "--since=14 days ago",
        "--date=short",
        "--pretty=format:%h%x09%ad%x09%s",
        "--name-only",
        "--",
        "core",
        "reference/core",
        "research",
        "decisions",
        "pushes",
        "campaigns",
        "log",
        "documents",
    ]
    result = _run_command(cmd, cwd=repo)
    if not result["ok"]:
        return {"available": False, "items": [], "error": result["stderr"].strip()}

    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in result["stdout"].splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t", 2)
        if len(parts) == 3 and re.fullmatch(r"[0-9a-f]{4,}", parts[0]):
            if current is not None:
                items.append(current)
            current = {"commit": parts[0], "date": parts[1], "subject": parts[2], "files": []}
            continue
        if current is not None:
            current["files"].append(line)
    if current is not None:
        items.append(current)

    return {"available": True, "items": items[:8], "error": ""}


def _parse_git_log_with_files(output: str, *, limit: int = 8) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t", 2)
        if len(parts) == 3 and re.fullmatch(r"[0-9a-f]{4,}", parts[0]):
            if current is not None:
                items.append(current)
            current = {"commit": parts[0], "date": parts[1], "subject": parts[2], "files": []}
            continue
        if current is not None:
            current["files"].append(line)
    if current is not None:
        items.append(current)
    return items[:limit]


def _git_since_last_seen(
    repo: Path,
    git: dict[str, Any],
    marker: dict[str, Any],
) -> dict[str, Any]:
    if not git.get("inside_work_tree"):
        return {
            "available": False,
            "commits": [],
            "changed_files": [],
            "error": git.get("error") or "git unavailable",
        }

    marker_git_raw = marker.get("git")
    marker_git: dict[str, Any] = marker_git_raw if isinstance(marker_git_raw, dict) else {}
    previous_commit = str(marker_git.get("commit") or "")
    current_commit = str(git.get("commit") or "")
    args = [
        "git",
        "log",
        "--date=short",
        "--pretty=format:%h%x09%ad%x09%s",
        "--name-only",
    ]
    if previous_commit and current_commit and previous_commit != current_commit:
        args.append(f"{previous_commit}..HEAD")
    else:
        previous_seen_at = _parse_timestamp(marker.get("seen_at"))
        if previous_seen_at is None:
            return {"available": True, "commits": [], "changed_files": [], "error": ""}
        args.append(f"--since={previous_seen_at.isoformat()}")
    result = _run_command(args, cwd=repo)
    if not result["ok"]:
        return {"available": False, "commits": [], "changed_files": [], "error": result["stderr"]}

    commits = _parse_git_log_with_files(result["stdout"])
    changed_files = sorted({file for item in commits for file in item["files"]})
    return {
        "available": True,
        "commits": commits,
        "changed_files": changed_files[:20],
        "error": "",
    }


def _empty_journal(repo: Path, *, available: bool) -> dict[str, Any]:
    return {
        "available": available,
        "ok": True,
        "repo": str(repo),
        "schema_version": journal_mod.JOURNAL_SCHEMA_VERSION,
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
        "error": "",
        "safe_to_share": True,
    }


def _journal_since_last_seen(
    repo: Path,
    git: dict[str, Any],
    marker: dict[str, Any],
) -> dict[str, Any]:
    if not git.get("inside_work_tree"):
        return _empty_journal(repo, available=False)

    marker_git_raw = marker.get("git")
    marker_git: dict[str, Any] = marker_git_raw if isinstance(marker_git_raw, dict) else {}
    previous_commit = str(marker_git.get("commit") or "")
    current_commit = str(git.get("commit") or "")
    if previous_commit and current_commit and previous_commit != current_commit:
        return journal_mod.collect(repo, limit=20, since=None, rev_range=f"{previous_commit}..HEAD")

    previous_seen_at = _parse_timestamp(marker.get("seen_at"))
    if previous_seen_at is None:
        return _empty_journal(repo, available=True)
    return journal_mod.collect(repo, limit=20, since=previous_seen_at.isoformat(), rev_range=None)


def _read_frontmatter(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            first = handle.readline()
            if first.strip() != "---":
                return {}
            lines: list[str] = []
            for line in handle:
                if line.strip() == "---":
                    break
                lines.append(line)
            else:
                return {}
    except OSError:
        return {}
    raw = "".join(lines).strip()
    try:
        parsed = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _parse_date(value: Any, fallback_path: Path) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            pass
    match = re.match(r"(\d{4}-\d{2}-\d{2})", fallback_path.name)
    if match:
        try:
            return date.fromisoformat(match.group(1))
        except ValueError:
            return None
    return None


def _parse_explicit_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return date.fromisoformat(value.strip()[:10])
        except ValueError:
            return None
    return None


def _relative_markdown_files(repo: Path, folder: str) -> list[Path]:
    root = repo / folder
    if not root.exists():
        return []
    return sorted(
        (path for path in root.rglob("*.md") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def _file_summary(
    repo: Path, path: Path, frontmatter: dict[str, Any] | None = None
) -> dict[str, Any]:
    meta = frontmatter if frontmatter is not None else _read_frontmatter(path)
    item_date = _parse_date(meta.get("date"), path)
    try:
        rel = path.relative_to(repo).as_posix()
    except ValueError:
        rel = str(path)
    return {
        "path": rel,
        "title": _title_from_markdown(path),
        "date": item_date.isoformat() if item_date else "",
        "status": str(meta.get("status", "") or ""),
        "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
    }


def _title_from_markdown(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped.startswith("# "):
                    return stripped[2:].strip()
    except OSError:
        pass
    return path.stem.replace("-", " ")


def _brain(repo: Path) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for folder in IMPORTANT_DIRS:
        root = repo / folder
        counts[folder] = (
            sum(1 for path in root.rglob("*.md") if path.is_file()) if root.exists() else 0
        )

    decision_files = _relative_markdown_files(repo, "decisions")
    decisions: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    today = date.today()

    for path in decision_files:
        meta = _read_frontmatter(path)
        item = _file_summary(repo, path, meta)
        decisions.append(item)
        status = item["status"].lower()
        decision_date = _parse_date(meta.get("date"), path)
        if status in {"proposed", "running"} and decision_date is not None:
            age_days = (today - decision_date).days
            if age_days > STALE_DECISION_DAYS:
                stale_item = dict(item)
                stale_item["age_days"] = age_days
                stale.append(stale_item)

    research_files = _relative_markdown_files(repo, "research")
    research: list[dict[str, Any]] = []
    stale_research: list[dict[str, Any]] = []
    for path in research_files:
        meta = _read_frontmatter(path)
        item = _file_summary(repo, path, meta)
        research.append(item)
        research_date = _parse_date(meta.get("date"), path)
        if research_date is not None:
            age_days = (today - research_date).days
            if age_days > STALE_RESEARCH_DAYS:
                stale_item = dict(item)
                stale_item["age_days"] = age_days
                stale_research.append(stale_item)
    bets = _bets(repo)
    push_facts = pushes_mod.facts(repo)

    return {
        "counts": counts,
        "recent_decisions": decisions[:5],
        "stale_decisions": stale[:5],
        "recent_research": research[:5],
        "stale_research": stale_research[:5],
        "bets": bets,
        "pushes": push_facts,
    }


def _bet_summary(repo: Path, path: Path) -> dict[str, Any]:
    meta = _read_frontmatter(path)
    opened = _parse_date(meta.get("opened"), path)
    deadline = _parse_explicit_date(meta.get("deadline"))
    try:
        rel = path.relative_to(repo).as_posix()
    except ValueError:
        rel = str(path)
    channels = meta.get("channels")
    if not isinstance(channels, list):
        channels = []
    return {
        "path": rel,
        "title": _title_from_markdown(path),
        "status": str(meta.get("status", "") or ""),
        "opened": opened.isoformat() if opened else "",
        "deadline": deadline.isoformat() if deadline else "",
        "appetite": str(meta.get("appetite", "") or ""),
        "hypothesis": str(meta.get("hypothesis", "") or ""),
        "metric": str(meta.get("metric", "") or ""),
        "target": str(meta.get("target", "") or ""),
        "result": str(meta.get("result", "") or ""),
        "public": bool(meta.get("public", False)),
        "channels": [str(channel) for channel in channels if isinstance(channel, str)],
        "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
    }


def _bet_sort_key(item: dict[str, Any]) -> tuple[str, str]:
    deadline = str(item.get("deadline") or "9999-12-31")
    return (deadline, str(item.get("path") or ""))


def _bets(repo: Path) -> dict[str, Any]:
    bet_items = [_bet_summary(repo, path) for path in _relative_markdown_files(repo, "bets")]
    active = [
        item for item in bet_items if str(item.get("status", "")).lower() in ACTIVE_BET_STATUSES
    ]
    active.sort(key=_bet_sort_key)
    today = date.today()
    due_soon: list[dict[str, Any]] = []
    overdue: list[dict[str, Any]] = []
    for item in active:
        deadline = _parse_explicit_date(item.get("deadline"))
        if deadline is None:
            continue
        days_until = (deadline - today).days
        if days_until < 0:
            overdue_item = dict(item)
            overdue_item["days_overdue"] = abs(days_until)
            overdue.append(overdue_item)
        elif days_until <= 7:
            due_item = dict(item)
            due_item["days_until_deadline"] = days_until
            due_soon.append(due_item)
    return {
        "active": active[:5],
        "due_soon": due_soon[:5],
        "overdue": overdue[:5],
        "recent": bet_items[:5],
    }


def _file_path_from_graph_id(value: Any) -> str:
    if not isinstance(value, str) or not value.startswith("file:"):
        return ""
    return value[len("file:") :]


def _relationship_adjacency(edges: list[dict[str, Any]]) -> dict[str, dict[str, set[str]]]:
    adjacency: dict[str, dict[str, set[str]]] = {}
    for edge in edges:
        rel_type = str(edge.get("rel_type") or edge.get("type") or "")
        source = _file_path_from_graph_id(edge.get("source"))
        target = _file_path_from_graph_id(edge.get("target"))
        if not rel_type or not source or not target:
            continue
        adjacency.setdefault(source, {}).setdefault(rel_type, set()).add(target)
        adjacency.setdefault(target, {}).setdefault(rel_type, set()).add(source)
    return adjacency


def _linked_push_paths_for_bet(
    adjacency: dict[str, dict[str, set[str]]],
    bet_path: str,
    push_paths: set[str],
) -> set[str]:
    direct_pushes = _linked_paths(adjacency, bet_path, "push")
    reverse_bet_links = _linked_paths(adjacency, bet_path, "bet") & push_paths
    return direct_pushes | reverse_bet_links


def _relationship_slug(value: str) -> str:
    lowered = value.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "unknown"


def _coerce_relationship_refs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _is_hidden_or_generated(path: Path, repo: Path) -> bool:
    try:
        rel_parts = path.relative_to(repo).parts
    except ValueError:
        return True
    is_bundled_data = rel_parts[:2] == ("mb", "_data") or rel_parts[:1] == ("_data",)
    return (
        any(
            part.startswith(".") or part in {"__pycache__", "node_modules", ".venv", "venv"}
            for part in rel_parts
        )
        or is_bundled_data
    )


def _relationship_markdown_files(repo: Path) -> list[Path]:
    return [
        path
        for path in sorted(repo.rglob("*.md"))
        if path.is_file() and not _is_hidden_or_generated(path, repo)
    ]


def _resolve_relationship_ref(repo: Path, ref: str) -> Path | None:
    clean_ref = relationships.clean_ref(ref)
    if not clean_ref:
        return None
    target = (repo / clean_ref).resolve()
    try:
        target.relative_to(repo)
    except ValueError:
        return None
    return target


def _relationship_reference_edges(repo: Path) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str, tuple[tuple[str, str], ...]]] = set()
    if not repo.exists():
        return edges

    for file_path in _relationship_markdown_files(repo):
        frontmatter = _read_frontmatter(file_path)
        if not frontmatter:
            continue
        source_rel = file_path.relative_to(repo).as_posix()
        source_id = f"file:{source_rel}"
        for field in relationships.relationship_fields_for_source(source_rel):
            rel_type = relationships.normalize_relationship(
                field,
                source_path=source_rel,
                fallback=field,
            )
            for ref in _coerce_relationship_refs(frontmatter.get(field)):
                clean_ref = relationships.clean_ref(ref)
                if not clean_ref and not relationships.is_external_ref(ref):
                    continue
                target = _resolve_relationship_ref(repo, ref)
                if target is not None and target.exists():
                    target_id = f"file:{target.relative_to(repo).as_posix()}"
                elif relationships.is_external_ref(ref):
                    target_id = f"external:{_relationship_slug(ref)}"
                else:
                    target_id = f"missing:{_relationship_slug(ref)}"
                evidence = {"kind": "frontmatter", "field": field, "path": source_rel}
                key = (source_id, target_id, rel_type, tuple(sorted(evidence.items())))
                if key in seen_edges:
                    continue
                seen_edges.add(key)
                edges.append(
                    {
                        "source": source_id,
                        "target": target_id,
                        "type": field,
                        "rel_type": rel_type,
                        "original_field": field,
                        "evidence": evidence,
                        "target_ref": ref,
                    }
                )
    return edges


def _linked_paths(
    adjacency: dict[str, dict[str, set[str]]],
    path: str,
    rel_type: str,
) -> set[str]:
    return adjacency.get(path, {}).get(rel_type, set())


def _offer_summaries(repo: Path) -> list[dict[str, Any]]:
    paths: list[Path] = []
    for folder in ("core/offers", "reference/core/offers"):
        paths.extend(
            path for path in _relative_markdown_files(repo, folder) if path.name == "offer.md"
        )
    for rel in ("core/offer.md", "reference/core/offer.md"):
        path = repo / rel
        if path.is_file():
            paths.append(path)
    unique_paths = sorted(set(paths), key=lambda path: path.stat().st_mtime, reverse=True)
    return [_file_summary(repo, path, _read_frontmatter(path)) for path in unique_paths]


def _coerce_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.strip()]
    return []


def _playbook_summary(repo: Path, path: Path) -> dict[str, Any]:
    meta = _read_frontmatter(path)
    try:
        rel = path.relative_to(repo).as_posix()
    except ValueError:
        rel = str(path)
    push_path = ""
    if path.parent.name == "playbooks" and path.parent.parent.name:
        push_path = f"pushes/{path.parent.parent.name}/push.md"
    approval_raw = meta.get("approval")
    approval: dict[str, Any] = approval_raw if isinstance(approval_raw, dict) else {}
    state_raw = meta.get("state")
    state: dict[str, Any] = state_raw if isinstance(state_raw, dict) else {}
    return {
        "path": rel,
        "title": _title_from_markdown(path),
        "status": str(meta.get("status", "") or ""),
        "push": str(meta.get("push", "") or ""),
        "resolved_push": push_path,
        "platform": str(meta.get("platform", "") or ""),
        "provider": str(meta.get("provider", "") or ""),
        "provider_boundary": str(meta.get("provider_boundary", "") or ""),
        "approval": {
            "required": bool(approval.get("required")),
            "status": str(approval.get("status", "") or ""),
            "approved_by": str(approval.get("approved_by", "") or ""),
            "approved_at": str(approval.get("approved_at", "") or ""),
        },
        "linked_outcomes": _coerce_string_list(meta.get("linked_outcomes")),
        "provider_refs_recorded": bool(state.get("provider_refs")),
        "updated_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
    }


def _playbook_summaries(repo: Path) -> list[dict[str, Any]]:
    return [
        _playbook_summary(repo, path)
        for path in sorted(repo.glob("pushes/*/playbooks/*.md"))
        if path.is_file()
    ]


def _gap(
    *,
    gap_id: str,
    severity: str,
    summary: str,
    records: list[dict[str, Any]],
    repair: str,
) -> dict[str, Any]:
    return {
        "id": gap_id,
        "severity": severity,
        "summary": summary,
        "count": len(records),
        "evidence": [str(item.get("path") or item.get("source") or "") for item in records[:5]],
        "records": records[:5],
        "repair": repair,
        "safe_to_share": True,
    }


def _playbook_health(
    repo: Path,
    *,
    brain: dict[str, Any],
) -> dict[str, Any]:
    push_report = brain.get("pushes") or {}
    pushes = [
        item
        for item in push_report.get("records", [])
        if isinstance(item, dict) and item.get("source") == "canonical"
    ]
    playbooks = _playbook_summaries(repo)
    playbooks_by_push: dict[str, list[dict[str, Any]]] = {}
    for playbook in playbooks:
        push_path = str(playbook.get("resolved_push") or "")
        if push_path:
            playbooks_by_push.setdefault(push_path, []).append(playbook)

    pushes_without_playbook = [
        item
        for item in pushes
        if str(item.get("status") or "").lower() in PUSH_STATUSES_EXPECTING_PLAYBOOK
        and not playbooks_by_push.get(str(item.get("path") or ""))
    ]
    pending_status = [
        item
        for item in playbooks
        if str(item.get("status") or "").lower() in PLAYBOOK_STATUSES_NEEDING_ATTENTION
    ]
    approval_needed = [
        item
        for item in playbooks
        if bool((item.get("approval") or {}).get("required"))
        and str(item.get("status") or "").lower() not in {"canceled", "retired"}
        and str((item.get("approval") or {}).get("status") or "").lower()
        in PLAYBOOK_APPROVAL_STATUSES_NEEDING_ATTENTION
    ]
    completed_without_outcome: list[dict[str, Any]] = []
    for push in pushes:
        if str(push.get("status") or "").lower() not in COMPLETED_PUSH_STATUSES:
            continue
        for playbook in playbooks_by_push.get(str(push.get("path") or ""), []):
            if not playbook.get("linked_outcomes"):
                item = dict(playbook)
                item["push_status"] = str(push.get("status") or "")
                completed_without_outcome.append(item)
    provider_boundary_attention = [
        item
        for item in playbooks
        if str(item.get("provider_boundary") or "").lower()
        in PLAYBOOK_PROVIDER_BOUNDARIES_NEEDING_ATTENTION
        and str(item.get("status") or "").lower() not in {"canceled", "retired"}
    ]

    gaps = [
        _gap(
            gap_id="pushes_without_playbook",
            severity="warn",
            summary=(
                f"{len(pushes_without_playbook)} active/planned push(es) need a playbook run."
            ),
            records=pushes_without_playbook,
            repair="Add a run record under `pushes/<push>/playbooks/` for each active push.",
        )
        if pushes_without_playbook
        else None,
        _gap(
            gap_id="pending_playbook_statuses",
            severity="warn",
            summary=f"{len(pending_status)} playbook run(s) are still draft/planned.",
            records=pending_status,
            repair="Review each playbook run and move it toward approved, active, or completed.",
        )
        if pending_status
        else None,
        _gap(
            gap_id="playbook_approval_needed",
            severity="warn",
            summary=f"{len(approval_needed)} playbook run(s) still need approval.",
            records=approval_needed,
            repair="Record approval status before publishing, spending, or mutating providers.",
        )
        if approval_needed
        else None,
        _gap(
            gap_id="completed_playbooks_without_outcome",
            severity="warn",
            summary=(
                f"{len(completed_without_outcome)} completed-push playbook run(s) "
                "need an outcome link."
            ),
            records=completed_without_outcome,
            repair="Add `linked_outcomes` to the playbook after the push is reviewed.",
        )
        if completed_without_outcome
        else None,
        _gap(
            gap_id="manual_provider_boundaries",
            severity="info",
            summary=(
                f"{len(provider_boundary_attention)} playbook run(s) are still "
                "plan/manual provider work."
            ),
            records=provider_boundary_attention,
            repair=(
                "Confirm the operator expects manual provider steps before treating this "
                "as automation."
            ),
        )
        if provider_boundary_attention
        else None,
    ]
    active_gaps = [gap_item for gap_item in gaps if gap_item is not None]
    return {
        "ok": not active_gaps,
        "source": "mb status playbook scan",
        "summary": {
            "gaps": len(active_gaps),
            "warnings": len([item for item in active_gaps if item["severity"] == "warn"]),
            "info": len([item for item in active_gaps if item["severity"] == "info"]),
            "playbooks": len(playbooks),
            "pushes_without_playbook": len(pushes_without_playbook),
            "pending_playbook_statuses": len(pending_status),
            "playbook_approval_needed": len(approval_needed),
            "completed_playbooks_without_outcome": len(completed_without_outcome),
            "manual_provider_boundaries": len(provider_boundary_attention),
        },
        "gaps": active_gaps,
        "sections": {
            "pushes": {
                "records": len(pushes),
                "expecting_playbook": len(
                    [
                        item
                        for item in pushes
                        if str(item.get("status") or "").lower() in PUSH_STATUSES_EXPECTING_PLAYBOOK
                    ]
                ),
                "without_playbook": pushes_without_playbook[:5],
            },
            "playbooks": {
                "records": playbooks[:5],
                "pending_status": pending_status[:5],
                "approval_needed": approval_needed[:5],
                "completed_without_outcome": completed_without_outcome[:5],
                "provider_boundary_attention": provider_boundary_attention[:5],
            },
        },
        "safe_to_share": True,
    }


def _is_push_stale(record: dict[str, Any], today: date) -> tuple[bool, int]:
    review_on = _parse_explicit_date(record.get("review_on"))
    if review_on is not None and review_on < today:
        return True, (today - review_on).days
    for key in ("started", "date"):
        item_date = _parse_explicit_date(record.get(key))
        if item_date is not None:
            age_days = (today - item_date).days
            if age_days > STALE_PUSH_DAYS:
                return True, age_days
            return False, age_days
    return False, 0


def _relationship_health(
    repo: Path,
    *,
    brain: dict[str, Any],
    today: date,
) -> dict[str, Any]:
    edges = _relationship_reference_edges(repo)
    adjacency = _relationship_adjacency(edges)
    all_bets = [_bet_summary(repo, path) for path in _relative_markdown_files(repo, "bets")]
    active_bets = [
        item for item in all_bets if str(item.get("status", "")).lower() in ACTIVE_BET_STATUSES
    ]
    closed_bets = [item for item in all_bets if str(item.get("status", "")).lower() == "closed"]
    push_report = brain.get("pushes") or {}
    pushes = [item for item in push_report.get("records", []) if isinstance(item, dict)]
    offers = _offer_summaries(repo)
    push_paths = {str(item.get("path") or "") for item in pushes}
    current_push_paths = {
        str(item.get("path") or "")
        for item in pushes
        if str(item.get("status", "")).lower() in ACTIVE_PUSH_STATUSES
    }

    active_bets_without_push = [
        item
        for item in active_bets
        if not _linked_push_paths_for_bet(adjacency, str(item["path"]), push_paths)
    ]
    closed_bets_without_outcome = [
        item for item in closed_bets if not _linked_paths(adjacency, str(item["path"]), "outcome")
    ]
    active_pushes_without_offer = [
        item
        for item in pushes
        if str(item.get("status", "")).lower() in ACTIVE_PUSH_STATUSES
        and not _linked_paths(adjacency, str(item.get("path") or ""), "offer")
    ]
    completed_pushes_without_outcome = [
        item
        for item in pushes
        if str(item.get("status", "")).lower() in COMPLETED_PUSH_STATUSES
        and not _linked_paths(adjacency, str(item.get("path") or ""), "outcome")
    ]
    stale_pushes_without_outcome: list[dict[str, Any]] = []
    for item in pushes:
        if str(item.get("status", "")).lower() not in ACTIVE_PUSH_STATUSES:
            continue
        if _linked_paths(adjacency, str(item.get("path") or ""), "outcome"):
            continue
        stale, age_days = _is_push_stale(item, today)
        if stale:
            stale_item = dict(item)
            stale_item["age_days"] = age_days
            stale_pushes_without_outcome.append(stale_item)

    offers_without_current_push_or_playbook: list[dict[str, Any]] = []
    for item in offers:
        status = str(item.get("status") or "").lower()
        if status not in LIVE_OFFER_STATUSES:
            continue
        path = str(item.get("path") or "")
        offer_pushes = _linked_paths(adjacency, path, "offer")
        linked_pushes = _linked_paths(adjacency, path, "push")
        has_current_push = bool((offer_pushes | linked_pushes) & current_push_paths)
        has_playbook = bool(_linked_paths(adjacency, path, "playbook"))
        if not has_current_push and not has_playbook:
            offers_without_current_push_or_playbook.append(item)

    relationship_types = {
        relationship.canonical_type for relationship in relationships.RELATIONSHIPS
    }
    missing_relationship_targets: list[dict[str, Any]] = []
    for edge in edges:
        rel_type = str(edge.get("rel_type") or "")
        target = str(edge.get("target") or "")
        if rel_type not in relationship_types or not target.startswith("missing:"):
            continue
        raw_evidence = edge.get("evidence")
        evidence: dict[str, Any] = raw_evidence if isinstance(raw_evidence, dict) else {}
        missing_relationship_targets.append(
            {
                "source": str(evidence.get("path") or _file_path_from_graph_id(edge.get("source"))),
                "relationship": rel_type,
                "field": str(edge.get("original_field") or evidence.get("field") or ""),
                "target": str(edge.get("target_ref") or target.removeprefix("missing:")),
            }
        )

    outcome_edges = [edge for edge in edges if str(edge.get("rel_type") or "") == "outcome"]
    gaps = [
        _gap(
            gap_id="active_bets_without_push",
            severity="warn",
            summary=f"{len(active_bets_without_push)} active bet(s) need a linked push.",
            records=active_bets_without_push,
            repair=(
                "Link each active bet to the push that supports it, or add the reverse "
                "`linked_bets` field on that push."
            ),
        )
        if active_bets_without_push
        else None,
        _gap(
            gap_id="closed_bets_without_outcome",
            severity="warn",
            summary=(
                f"{len(closed_bets_without_outcome)} closed bet(s) need a result or outcome link."
            ),
            records=closed_bets_without_outcome,
            repair="Record the bet result and link the outcome artifact.",
        )
        if closed_bets_without_outcome
        else None,
        _gap(
            gap_id="active_pushes_without_offer",
            severity="warn",
            summary=(
                f"{len(active_pushes_without_offer)} active/planned push(es) need an offer link."
            ),
            records=active_pushes_without_offer,
            repair="Set the push `offer:` field to the repo-relative offer file.",
        )
        if active_pushes_without_offer
        else None,
        _gap(
            gap_id="completed_pushes_without_outcome",
            severity="warn",
            summary=(
                f"{len(completed_pushes_without_outcome)} completed push(es) need review/outcome."
            ),
            records=completed_pushes_without_outcome,
            repair="Add `linked_outcomes` to the completed push after review.",
        )
        if completed_pushes_without_outcome
        else None,
        _gap(
            gap_id="stale_pushes_without_outcome",
            severity="warn",
            summary=f"{len(stale_pushes_without_outcome)} stale push(es) have not closed the loop.",
            records=stale_pushes_without_outcome,
            repair="Review stale pushes, capture the outcome, or update the review date.",
        )
        if stale_pushes_without_outcome
        else None,
        _gap(
            gap_id="offers_without_current_push_or_playbook",
            severity="info",
            summary=(
                f"{len(offers_without_current_push_or_playbook)} offer(s) have no current push "
                "or linked playbook."
            ),
            records=offers_without_current_push_or_playbook,
            repair=(
                "Connect each live offer to a current push or reusable playbook. Either set "
                "the push `offer:` to the repo-relative offer file or add `linked_pushes:` "
                "on the offer."
            ),
        )
        if offers_without_current_push_or_playbook
        else None,
        _gap(
            gap_id="missing_relationship_targets",
            severity="warn",
            summary=(
                f"{len(missing_relationship_targets)} relationship link(s) point at missing files."
            ),
            records=missing_relationship_targets,
            repair="Run `mb validate --cross-refs` for exact missing-link warnings.",
        )
        if missing_relationship_targets
        else None,
    ]
    active_gaps = [gap_item for gap_item in gaps if gap_item is not None]
    return {
        "ok": not active_gaps,
        "source": "mb status relationship scan",
        "registry_version": relationships.REGISTRY_VERSION,
        "summary": {
            "gaps": len(active_gaps),
            "warnings": len([item for item in active_gaps if item["severity"] == "warn"]),
            "info": len([item for item in active_gaps if item["severity"] == "info"]),
            "active_bets_without_push": len(active_bets_without_push),
            "closed_bets_without_outcome": len(closed_bets_without_outcome),
            "active_pushes_without_offer": len(active_pushes_without_offer),
            "completed_pushes_without_outcome": len(completed_pushes_without_outcome),
            "stale_pushes_without_outcome": len(stale_pushes_without_outcome),
            "offers_without_current_push_or_playbook": len(offers_without_current_push_or_playbook),
            "missing_relationship_targets": len(missing_relationship_targets),
        },
        "gaps": active_gaps,
        "sections": {
            "bets": {
                "active": len(active_bets),
                "closed": len(
                    [item for item in all_bets if str(item.get("status") or "").lower() == "closed"]
                ),
                "active_without_push": active_bets_without_push[:5],
                "closed_without_outcome": closed_bets_without_outcome[:5],
            },
            "pushes": {
                "records": len(pushes),
                "active_without_offer": active_pushes_without_offer[:5],
                "completed_without_outcome": completed_pushes_without_outcome[:5],
                "stale_without_outcome": stale_pushes_without_outcome[:5],
            },
            "offers": {
                "records": len(offers),
                "without_current_push_or_playbook": offers_without_current_push_or_playbook[:5],
            },
            "outcomes": {
                "linked_count": len(outcome_edges),
                "missing_targets": missing_relationship_targets[:5],
            },
        },
        "safe_to_share": True,
    }


def _repo_full_name(remote: str) -> str:
    return github_activity.repo_full_name(remote)


def _gh_json(args: list[str], repo: Path) -> tuple[bool, Any, str]:
    result = _run_command(args, cwd=repo, timeout=5.0)
    if not result["ok"]:
        return False, None, result["stderr"].strip() or result["stdout"].strip()
    try:
        return True, json.loads(result["stdout"] or "[]"), ""
    except json.JSONDecodeError:
        return False, None, "gh returned invalid JSON"


def _github(repo: Path, git: dict[str, Any]) -> dict[str, Any]:
    context = connect_mod.github_context(repo, which_func=_which, command_runner=_run_command)
    if not context["ok"]:
        sections: dict[str, list[dict[str, Any]]] = {
            "assigned_tasks": [],
            "attention_requests": [],
            "open_proposals": [],
            "shipped_this_week": [],
            "recently_closed_tasks": [],
            "blocked_or_stale_tasks": [],
        }
        return {
            "available": context["state"] != "missing_cli",
            "authenticated": context["state"] not in {"missing_cli", "unauthenticated"},
            "degraded": True,
            "source": "gh",
            "repo": "",
            "summary": {
                "assigned_tasks": 0,
                "attention_requests": 0,
                "open_proposals": 0,
                "shipped_this_week": 0,
                "recently_closed_tasks": 0,
                "blocked_or_stale_tasks": 0,
            },
            "sections": sections,
            "errors": [str(context["summary"])],
            "assigned_issues": [],
            "review_requests": [],
            "recent_merged_prs": [],
            "context": context,
        }
    report = github_activity.collect(
        repo,
        remote=str(git.get("remote", "")),
        which_func=_which,
        command_runner=_run_command,
        json_runner=_gh_json,
    )
    report["context"] = context
    return report


def _recent_merged_prs(prs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return github_activity.recent_merged_prs(prs)


def _summarize_pr(pr: dict[str, Any]) -> dict[str, Any]:
    return github_activity.summarize_pr(pr)


def _runtime(repo: Path) -> dict[str, Any]:
    claude_path = _which("claude")
    wiring = link_status(repo)
    codex = codex_mod.readiness(repo)
    return {
        "claude_code": {
            "found": bool(claude_path),
            "path": claude_path,
            "repair": "" if claude_path else "Install Claude Code: https://claude.ai/install",
        },
        "skill_wiring": {
            **wiring,
            "repair": ""
            if wiring["ok"]
            else "Run `mb skill repair --repo .`, then `mb skill link --repo .`.",
        },
        "codex_cli": codex,
    }


def _install() -> dict[str, Any]:
    mode = install_mode()
    return {
        "version": __version__,
        "mode": mode,
        "ok": mode != "unknown",
        "detail": f"mb {__version__} ({mode} mode)",
    }


def _schema() -> dict[str, Any]:
    return {
        "name": "mainbranch.status",
        "version": STATUS_SCHEMA_VERSION,
        "compatibility": "v1 additions are additive; existing v1 keys must not change meaning.",
    }


def push_facts(repo: str | Path) -> dict[str, Any]:
    """Return normalized push facts for JSON consumers."""
    return pushes_mod.facts(repo)


SITE_REPO_PATH_FIELDS = (
    "site_repo_path",
    "site_repo",
    "site_path",
    "site_repository_path",
)


def _site_repo_path_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        items: list[Any] = []
        for key in SITE_REPO_PATH_FIELDS:
            if key in value:
                items.append(value[key])
        return items
    if isinstance(value, list):
        return [item for entry in value for item in _site_repo_path_values(entry)]
    return [value]


def _resolve_site_repo_path(repo: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    if re.match(r"^[a-z][a-z0-9+.-]*://", raw, flags=re.IGNORECASE):
        return None
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = repo / candidate
    return candidate.resolve()


def _candidate_site_repo_records(repo: Path) -> list[dict[str, Any]]:
    paths = _relative_markdown_files(repo, "pushes")
    paths.extend(_relative_markdown_files(repo, "campaigns"))
    paths.extend(path for path in _relative_markdown_files(repo, "core") if path.name == "offer.md")
    paths.extend(
        path for path in _relative_markdown_files(repo, "reference/core") if path.name == "offer.md"
    )

    records: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for path in paths:
        meta = _read_frontmatter(path)
        candidate_values: list[Any] = []
        for key in SITE_REPO_PATH_FIELDS:
            if key in meta:
                candidate_values.append(meta[key])
        for nested_key in ("site", "site_record", "measurement", "launch"):
            if nested_key in meta:
                candidate_values.extend(_site_repo_path_values(meta[nested_key]))

        for value in candidate_values:
            site_repo = _resolve_site_repo_path(repo, value)
            if site_repo is None or site_repo in seen:
                continue
            if not (site_repo / site_mod.CONVERSION_RELATIVE_PATH).exists():
                continue
            try:
                source = path.relative_to(repo).as_posix()
            except ValueError:
                source = str(path)
            records.append({"path": site_repo, "source": source})
            seen.add(site_repo)
    return records


def _measurement_payload(result: dict[str, Any], *, repair_command: str) -> dict[str, Any]:
    return {
        "available": True,
        "state": result["state"],
        "ok": result["ok"],
        "summary": result["summary"],
        "repair": result["repair"],
        "repair_command": repair_command,
        "site_repo": result.get("site_repo", ""),
        "business_repo": result.get("business_repo", ""),
        "facts": {
            "conversion_kind": result["facts"].get("conversion_kind"),
            "expected_events": result["facts"].get("expected_events"),
            "gtm_container_id_present": bool(result["facts"].get("gtm_container_id")),
            "google_ads_customer_id_present": bool(result["facts"].get("google_ads_customer_id")),
            "primary_conversions": result["facts"].get("primary_conversions") or [],
        },
        "blocked_count": len(result.get("blocked") or []),
        "manual_count": len(result.get("manual") or []),
        "safe_to_share": True,
    }


def _measurement(repo: Path) -> dict[str, Any]:
    """Return a compact paid-traffic measurement summary for status consumers."""

    conversion_path = repo / site_mod.CONVERSION_RELATIVE_PATH
    if conversion_path.exists():
        result = site_mod.check(repo, business_repo=repo)
        return _measurement_payload(result, repair_command="mb site check")

    site_records = _candidate_site_repo_records(repo)
    if site_records:
        site_repo = site_records[0]["path"]
        result = site_mod.check(site_repo, business_repo=repo)
        payload = _measurement_payload(
            result,
            repair_command=f'mb site check "{site_repo}" --business-repo .',
        )
        payload["source_record"] = site_records[0]["source"]
        return payload

    return {
        "available": False,
        "state": "missing",
        "summary": "No paid-traffic site conversion plan found.",
        "repair": "Run `/mb-site` for a paid-traffic minisite before checking launch readiness.",
        "repair_command": "mb site check",
        "safe_to_share": True,
    }


def _marker_path(repo: Path) -> Path:
    return repo / LAST_STATUS_SEEN_RELATIVE_PATH


def _marker_gitignore_state(repo: Path) -> dict[str, Any]:
    gitignore = repo / ".gitignore"
    entry = LAST_STATUS_SEEN_GITIGNORE_ENTRY
    if _which("git"):
        check = _run_command(["git", "check-ignore", entry], cwd=repo)
        if check["ok"]:
            return {
                "ok": True,
                "path": ".gitignore",
                "entry": entry,
                "repair": "",
            }
    if not gitignore.exists():
        return {
            "ok": False,
            "path": ".gitignore",
            "entry": entry,
            "repair": f"Add `{entry}` to `.gitignore`.",
        }
    try:
        lines = gitignore.read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    ignored = entry in {line.strip() for line in lines}
    return {
        "ok": ignored,
        "path": ".gitignore",
        "entry": entry,
        "repair": "" if ignored else f"Add `{entry}` to `.gitignore`.",
    }


def _read_last_seen_marker(repo: Path) -> dict[str, Any]:
    path = _marker_path(repo)
    if not path.exists():
        return {
            "exists": False,
            "path": LAST_STATUS_SEEN_RELATIVE_PATH.as_posix(),
            "error": "",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "exists": True,
            "path": LAST_STATUS_SEEN_RELATIVE_PATH.as_posix(),
            "error": f"could not read last status marker: {exc}",
        }
    return data if isinstance(data, dict) else {"exists": True, "error": "invalid marker shape"}


def _brain_count_changes(
    current_counts: dict[str, int],
    previous_counts: dict[str, Any],
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for folder, current in sorted(current_counts.items()):
        try:
            previous = int(previous_counts.get(folder, 0))
        except (TypeError, ValueError):
            previous = 0
        delta = current - previous
        if delta:
            changes.append({"folder": folder, "before": previous, "after": current, "delta": delta})
    return changes


def _since_last_check(
    repo: Path,
    *,
    marker: dict[str, Any],
    git: dict[str, Any],
    brain: dict[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    marker_exists = bool(marker.get("exists", True)) and not marker.get("error")
    previous_seen_at = str(marker.get("seen_at") or "") if marker_exists else ""
    previous_brain_raw = marker.get("brain")
    previous_brain: dict[str, Any] = (
        previous_brain_raw if isinstance(previous_brain_raw, dict) else {}
    )
    previous_counts_raw = previous_brain.get("counts")
    previous_counts: dict[str, Any] = (
        previous_counts_raw if isinstance(previous_counts_raw, dict) else {}
    )
    git_since: dict[str, Any] = (
        _git_since_last_seen(repo, git, marker)
        if marker_exists
        else {
            "available": bool(git.get("inside_work_tree")),
            "commits": [],
            "changed_files": [],
            "error": "",
        }
    )
    journal_since: dict[str, Any] = (
        _journal_since_last_seen(repo, git, marker)
        if marker_exists
        else _empty_journal(repo, available=bool(git.get("inside_work_tree")))
    )
    count_changes = _brain_count_changes(brain.get("counts") or {}, previous_counts)
    dirty_count = int(git.get("dirty_count") or 0)
    commits = git_since.get("commits") or []
    changed_files = git_since.get("changed_files") or []
    journal_summary = journal_since.get("summary") or {}
    summary = {
        "commits": len(commits) if isinstance(commits, list) else 0,
        "files_changed": len(changed_files) if isinstance(changed_files, list) else 0,
        "dirty_files": dirty_count,
        "brain_count_changes": len(count_changes),
        "journal_events": int(journal_summary.get("events") or 0),
        "journal_groups": int(journal_summary.get("groups") or 0),
    }
    first_run = not marker_exists
    return {
        "ok": not bool(marker.get("error")),
        "marker_path": LAST_STATUS_SEEN_RELATIVE_PATH.as_posix(),
        "marker_gitignore": _marker_gitignore_state(repo),
        "previous_seen_at": previous_seen_at,
        "current_seen_at": generated_at,
        "first_run": first_run,
        "summary": summary,
        "git": git_since,
        "journal": journal_since,
        "brain_count_changes": count_changes,
        "error": str(marker.get("error") or ""),
        "safe_to_share": True,
    }


def _write_last_seen_marker(repo: Path, report: dict[str, Any]) -> dict[str, Any]:
    if not report["repo"].get("looks_like_mainbranch_repo"):
        return {
            "attempted": False,
            "ok": False,
            "reason": "not a Main Branch repo",
            "path": LAST_STATUS_SEEN_RELATIVE_PATH.as_posix(),
        }
    marker = {
        "kind": "mainbranch.status.last_seen",
        "schema_version": STATUS_SCHEMA_VERSION,
        "seen_at": report["generated_at"],
        "repo": str(repo),
        "git": {
            "branch": str(report["git"].get("branch") or ""),
            "commit": str(report["git"].get("commit") or ""),
        },
        "brain": {"counts": report["brain"].get("counts") or {}},
        "readiness": {
            "level": str(report["readiness"].get("level") or ""),
            "score": int(report["readiness"].get("score") or 0),
        },
        "safe_to_share": True,
    }
    path = _marker_path(repo)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        return {
            "attempted": True,
            "ok": False,
            "reason": str(exc),
            "path": LAST_STATUS_SEEN_RELATIVE_PATH.as_posix(),
        }
    return {
        "attempted": True,
        "ok": True,
        "reason": "",
        "path": LAST_STATUS_SEEN_RELATIVE_PATH.as_posix(),
    }


def _safe_exception_message(exc: Exception) -> str:
    message = str(exc) or exc.__class__.__name__
    message = re.sub(
        r"(?<![A-Za-z0-9:])(?:"
        r"/(?:Users|home|private|tmp|var|Volumes|opt|usr/local)/[^\s\"'`<>),;]+"
        r"|[A-Za-z]:\\[^\s\"'`<>),;]+"
        r")",
        "<local-path>",
        message,
    )
    return message[:240] + ("..." if len(message) > 240 else "")


def _validation_status(repo: Path, *, cross_refs: bool = True) -> dict[str, Any]:
    try:
        report = validate_mod.run(str(repo), cross_refs=cross_refs)
    except Exception as exc:  # pragma: no cover - defensive status boundary
        message = _safe_exception_message(exc)
        return {
            "ok": False,
            "state": "error",
            "summary": {"errors": 1, "warnings": 0, "top_category": "validation_unavailable"},
            "validation_categories": {
                "schema_version": "1.0",
                "total_categories": 1,
                "top_category": "validation_unavailable",
                "top_repair": "Run `mb validate --cross-refs --json` for the exact failure.",
                "by_category": {
                    "validation_unavailable": {
                        "count": 1,
                        "errors": 1,
                        "warnings": 0,
                        "examples": [{"path": "", "message": message}],
                        "repair": "Run `mb validate --cross-refs --json` for the exact failure.",
                    }
                },
                "safe_to_share": True,
            },
            "safe_to_share": True,
        }
    summary = report.get("summary") or {}
    errors = int(summary.get("errors") or 0)
    warnings = int(summary.get("warnings") or 0)
    return {
        "ok": bool(report.get("ok")),
        "state": "error" if errors else ("warn" if warnings else "ok"),
        "summary": summary,
        "validation_categories": report.get("validation_categories") or {},
        "legacy_repair": report.get("legacy_repair"),
        "cross_refs": {
            "enabled": bool((report.get("cross_refs") or {}).get("enabled")),
            "warnings": len((report.get("cross_refs") or {}).get("warnings") or []),
            "orphan_offers": len((report.get("cross_refs") or {}).get("orphan_offers") or []),
        },
        "migration_drift": (report.get("migration_drift") or {}).get("summary", {}),
        "safe_to_share": True,
    }


def _drift(report: dict[str, Any]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    validation = report.get("validation") or {}
    validation_state = str(validation.get("state") or "ok")
    if validation_state != "ok":
        categories = validation.get("validation_categories") or {}
        top_category = str(categories.get("top_category") or "")
        top_repair = str(categories.get("top_repair") or "Run `mb validate --cross-refs --json`.")
        summary = validation.get("summary") or {}
        items.append(
            {
                "id": "validation_debt",
                "severity": "error" if validation_state == "error" else "warn",
                "summary": (
                    f"{summary.get('errors', 0)} validation error(s), "
                    f"{summary.get('warnings', 0)} warning(s)"
                    + (f"; top category: {top_category}" if top_category else "")
                ),
                "evidence": list((categories.get("by_category") or {}).keys())[:5],
                "repair": top_repair,
                "safe_to_share": True,
            }
        )
    stale_decisions = report["brain"].get("stale_decisions") or []
    if stale_decisions:
        items.append(
            {
                "id": "stale_decisions",
                "severity": "warn",
                "summary": f"{len(stale_decisions)} proposed/running decision(s) are stale.",
                "evidence": [item["path"] for item in stale_decisions[:5]],
                "repair": "Review stale proposed/running decisions in `decisions/`.",
                "safe_to_share": True,
            }
        )
    stale_research = report["brain"].get("stale_research") or []
    if stale_research:
        items.append(
            {
                "id": "stale_research",
                "severity": "info",
                "summary": (
                    f"{len(stale_research)} research note(s) are older than "
                    "current freshness rules."
                ),
                "evidence": [item["path"] for item in stale_research[:5]],
                "repair": "Refresh or supersede stale research before using it for decisions.",
                "safe_to_share": True,
            }
        )
    relationship_health = report.get("relationship_health") or {}
    relationship_summary = relationship_health.get("summary") or {}
    if relationship_summary.get("gaps", 0):
        top_gap = (relationship_health.get("gaps") or [{}])[0]
        items.append(
            {
                "id": "relationship_health_gaps",
                "severity": "warn" if relationship_summary.get("warnings", 0) else "info",
                "summary": (
                    f"{relationship_summary.get('gaps', 0)} business relationship gap(s) "
                    "need review."
                ),
                "evidence": [
                    str(item.get("id") or "")
                    for item in (relationship_health.get("gaps") or [])[:5]
                ],
                "repair": str(
                    top_gap.get("repair")
                    or "Run `mb status --verbose --peek` to inspect relationship gaps."
                ),
                "safe_to_share": True,
            }
        )
    playbook_health = report.get("playbook_health") or {}
    playbook_summary = playbook_health.get("summary") or {}
    if playbook_summary.get("gaps", 0):
        top_gap = (playbook_health.get("gaps") or [{}])[0]
        items.append(
            {
                "id": "playbook_health_gaps",
                "severity": "warn" if playbook_summary.get("warnings", 0) else "info",
                "summary": (
                    f"{playbook_summary.get('gaps', 0)} push playbook health signal(s) need review."
                ),
                "evidence": [
                    str(item.get("id") or "") for item in (playbook_health.get("gaps") or [])[:5]
                ],
                "repair": str(
                    top_gap.get("repair")
                    or "Run `mb status --verbose --peek` to inspect playbook health."
                ),
                "safe_to_share": True,
            }
        )
    onboarding_summary = (report.get("onboarding") or {}).get("summary") or {}
    if onboarding_summary.get("status") == "in_progress":
        items.append(
            {
                "id": "incomplete_onboarding",
                "severity": "warn",
                "summary": (
                    f"{onboarding_summary.get('completed_required', 0)}/"
                    f"{onboarding_summary.get('total_required', 0)} required onboarding "
                    "steps complete."
                ),
                "evidence": list(onboarding_summary.get("missing_inputs") or [])[:5],
                "repair": str(
                    onboarding_summary.get("next_recommended_action")
                    or "Run `mb onboard status` to resume onboarding."
                ),
                "safe_to_share": True,
            }
        )
    skill_wiring = report["runtime"].get("skill_wiring") or {}
    if not skill_wiring.get("ok"):
        items.append(
            {
                "id": "broken_skill_wiring",
                "severity": "error",
                "summary": "Claude Code skill wiring is missing or unhealthy.",
                "evidence": list(skill_wiring.get("missing") or [])[:5],
                "repair": str(skill_wiring.get("repair") or "Run `mb skill link --repo .`."),
                "safe_to_share": True,
            }
        )
    codex_cli = report["runtime"].get("codex_cli") or {}
    codex_executable = codex_cli.get("executable") or {}
    codex_instructions = codex_cli.get("instructions") or {}
    if codex_executable.get("found") and not codex_instructions.get("ok"):
        items.append(
            {
                "id": "codex_instructions_not_ready",
                "severity": "warn",
                "summary": "Codex AGENTS.md instructions are missing or stale.",
                "evidence": [str(codex_instructions.get("path") or "AGENTS.md")],
                "repair": str(
                    codex_instructions.get("repair")
                    or "Run `mb doctor repair --plan`, then `mb doctor repair --apply`."
                ),
                "safe_to_share": True,
            }
        )
    broken_integrations = [
        item
        for item in (report.get("integrations") or {}).get("providers", [])
        if item.get("connected") and not item.get("ok")
    ]
    if broken_integrations:
        items.append(
            {
                "id": "unhealthy_integrations",
                "severity": "warn",
                "summary": f"{len(broken_integrations)} declared integration(s) need repair.",
                "evidence": [
                    f"{item['provider']}:{item['state']}" for item in broken_integrations[:5]
                ],
                "repair": str(broken_integrations[0].get("repair_command") or "mb connect doctor"),
                "safe_to_share": True,
            }
        )
    if not report["since_last_check"]["marker_gitignore"]["ok"]:
        items.append(
            {
                "id": "status_marker_not_gitignored",
                "severity": "info",
                "summary": "The local status marker is not ignored by git yet.",
                "evidence": [LAST_STATUS_SEEN_GITIGNORE_ENTRY],
                "repair": report["since_last_check"]["marker_gitignore"]["repair"],
                "safe_to_share": True,
            }
        )
    return {
        "ok": not any(item["severity"] == "error" for item in items),
        "summary": {
            "total": len(items),
            "errors": len([item for item in items if item["severity"] == "error"]),
            "warnings": len([item for item in items if item["severity"] == "warn"]),
            "info": len([item for item in items if item["severity"] == "info"]),
        },
        "items": items,
    }


def _readiness(report: dict[str, Any]) -> dict[str, Any]:
    checks = [
        {
            "name": "mainbranch_repo",
            "ok": bool(report["repo"]["looks_like_mainbranch_repo"]),
            "weight": 25,
            "repair": "Run `mb init` in a new business repo or cd into an existing one.",
        },
        {
            "name": "git_repo",
            "ok": bool(report["git"].get("inside_work_tree")),
            "weight": 20,
            "repair": "Run `git init` if this should be a business repo.",
        },
        {
            "name": "install",
            "ok": bool(report["install"]["ok"]) and report["update"]["severity"] != "required",
            "weight": 15,
            "repair": report["update"]["command"]
            if report["update"]["severity"] == "required"
            else "Reinstall Main Branch with `pipx install mainbranch`.",
        },
        {
            "name": "skill_wiring",
            "ok": bool(report["runtime"]["skill_wiring"]["ok"]),
            "weight": 25,
            "repair": report["runtime"]["skill_wiring"]["repair"],
        },
        {
            "name": "claude_code",
            "ok": bool(report["runtime"]["claude_code"]["found"]),
            "weight": 15,
            "repair": report["runtime"]["claude_code"]["repair"],
        },
    ]
    possible = sum(int(check["weight"]) for check in checks)
    score = sum(int(check["weight"]) for check in checks if check["ok"])
    next_actions = [str(check["repair"]) for check in checks if not check["ok"] and check["repair"]]

    if report["git"].get("dirty"):
        next_actions.append(
            "Review or commit the current git changes before handing work to an agent."
        )
    if report["brain"]["stale_decisions"]:
        next_actions.append("Review stale proposed/running decisions in `decisions/`.")
    if report["brain"].get("stale_research"):
        next_actions.append("Refresh or supersede stale research before relying on it.")
    bets = report["brain"].get("bets") or {}
    if bets.get("overdue"):
        next_actions.append("Close or update overdue active bets in `bets/`.")
    elif bets.get("due_soon"):
        next_actions.append("Review active bets with deadlines in the next 7 days.")
    relationship_health = report.get("relationship_health") or {}
    relationship_gaps = relationship_health.get("gaps") or []
    if relationship_gaps:
        first_gap = relationship_gaps[0]
        next_actions.append(
            str(
                first_gap.get("repair")
                or "Review relationship gaps with `mb status --verbose --peek`."
            )
        )
    playbook_health = report.get("playbook_health") or {}
    playbook_gaps = playbook_health.get("gaps") or []
    if playbook_gaps:
        first_gap = playbook_gaps[0]
        next_actions.append(
            str(
                first_gap.get("repair")
                or "Review playbook health with `mb status --verbose --peek`."
            )
        )
    onboarding_summary = (report.get("onboarding") or {}).get("summary") or {}
    if onboarding_summary.get("status") == "in_progress":
        next_actions.append(
            str(
                onboarding_summary.get("next_recommended_action")
                or "Run `mb onboard status` to resume onboarding."
            )
        )
    integration_repairs = [
        item
        for item in (report.get("integrations") or {}).get("providers", [])
        if item.get("connected") and not item["ok"]
    ]
    for item in integration_repairs[:3]:
        command = str(item.get("repair_command") or "mb connect doctor")
        next_actions.append(f"Repair {item['provider']} integration: `{command}`.")
    marker_gitignore = (report.get("since_last_check") or {}).get("marker_gitignore") or {}
    if marker_gitignore and not marker_gitignore.get("ok") and marker_gitignore.get("repair"):
        next_actions.append(str(marker_gitignore["repair"]))
    github_context = report["github"].get("context") or {}
    if github_context and not github_context.get("ok"):
        command = str(github_context.get("repair_command") or "gh auth login")
        next_actions.append(f"Repair GitHub context: `{command}`.")
    elif not report["github"]["authenticated"]:
        next_actions.append("Run `gh auth login` to include assigned issues and shipped PRs.")
    if not next_actions:
        next_actions.append("Run `claude` in this repo, then `/mb-start`.")

    percent = round((score / possible) * 100) if possible else 0
    if percent >= 85:
        level = "ready"
    elif percent >= 60:
        level = "needs_attention"
    else:
        level = "not_ready"
    return {
        "score": percent,
        "level": level,
        "checks": checks,
        "next_actions": next_actions[:5],
    }


def run(
    path: str = ".",
    *,
    update_marker: bool = True,
    validation_cross_refs: bool = True,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a deterministic daily briefing report."""
    repo_path = Path(path).resolve()
    current_time = now or _utc_now()
    generated_at = _format_timestamp(current_time)
    repo_shape = _looks_like_mainbranch_repo(repo_path)
    git = _git_info(repo_path)
    update = package_update_status(repo_path)
    github = _github(repo_path, git)
    brain = _brain(repo_path)
    topology_payload = topology_mod.collect(
        str(repo_path),
        git_remote=str(git.get("remote") or ""),
    )
    push_report = brain["pushes"]
    marker = _read_last_seen_marker(repo_path)
    report: dict[str, Any] = {
        "schema_version": STATUS_SCHEMA_VERSION,
        "schema": _schema(),
        "generated_at": generated_at,
        "ok": True,
        "repo": {"path": str(repo_path), **repo_shape},
        "install": _install(),
        "update": update,
        "runtime": _runtime(repo_path),
        "git": git,
        "git_activity": _git_recent_activity(repo_path, git),
        "journal": journal_mod.collect(repo_path, limit=12, since="14 days ago"),
        "brain": brain,
        "pushes": push_report["records"],
        "active_pushes": push_report["active"],
        "push_count": push_report["count"],
        "canonical_push_count": push_report["canonical_count"],
        "campaigns": push_report["legacy_campaigns"],
        "active_campaigns": push_report["active_legacy_campaigns"],
        "campaign_count": push_report["legacy_campaign_count"],
        "deprecated_campaign_keys": True,
        "push_compatibility": push_report["compatibility"],
        "onboarding": onboard_mod.onboarding_status(repo_path),
        "integrations": connect_mod.status_all(repo_path, github=github.get("context")),
        "measurement": _measurement(repo_path),
        "github": github,
    }
    report["relationship_health"] = _relationship_health(
        repo_path,
        brain=brain,
        today=current_time.date(),
    )
    report["playbook_health"] = _playbook_health(repo_path, brain=brain)
    report["since_last_check"] = _since_last_check(
        repo_path,
        marker=marker,
        git=git,
        brain=brain,
        generated_at=generated_at,
    )
    report["validation"] = _validation_status(repo_path, cross_refs=validation_cross_refs)
    report["drift"] = _drift(report)
    report["topology"] = {
        "schema": topology_payload["schema"],
        "safe_to_share": True,
        "summary": topology_payload["summary"],
        "registry": topology_payload["registry"],
        "descriptor": topology_payload["descriptor"],
        "current_repo": topology_payload["current_repo"],
        "child_counts": topology_payload["child_counts"],
        "restricted_repos": topology_payload["restricted_repos"],
        "findings": topology_payload["findings"],
        "local": {
            "repo_path": str(repo_path),
            "safe_to_share": False,
        },
    }
    report["readiness"] = _readiness(report)
    report["ranked_actions"] = ranker_mod.rank_status_report(report)
    report["ok"] = report["readiness"]["level"] != "not_ready"
    report["marker_update"] = (
        _write_last_seen_marker(repo_path, report)
        if update_marker
        else {
            "attempted": False,
            "ok": False,
            "reason": "disabled",
            "path": LAST_STATUS_SEEN_RELATIVE_PATH.as_posix(),
        }
    )
    return report


def render_human(
    report: dict[str, Any],
    *,
    verbose: bool = False,
    no_color: bool = False,
) -> None:
    """Print a concise terminal briefing."""
    from rich.console import Console

    console = Console(no_color=no_color)
    repo = report["repo"]
    git = report["git"]
    runtime = report["runtime"]
    brain = report["brain"]
    onboarding = report.get("onboarding") or {}
    integrations = report.get(
        "integrations",
        {"summary": {"configured": 0, "healthy": 0, "needs_repair": 0}, "providers": []},
    )
    github = report["github"]
    readiness = report["readiness"]
    since = report.get("since_last_check") or {}
    drift = report.get("drift") or {"summary": {"total": 0}, "items": []}
    relationship_health = report.get("relationship_health") or {
        "summary": {"gaps": 0},
        "gaps": [],
    }
    playbook_health = report.get("playbook_health") or {
        "summary": {"gaps": 0},
        "gaps": [],
    }

    console.print(f"\n[bold]mb status[/bold]  {repo['path']}")
    alert = format_update_alert(report.get("update", {}))
    if alert:
        console.print(alert)
        console.print()
    console.print(
        f"[bold]{readiness['level'].replace('_', ' ')}[/bold]  {readiness['score']}/100\n"
    )

    since_summary = since.get("summary") or {}
    if since.get("first_run"):
        console.print(
            f"[bold]Since last check[/bold] first run; recording {since.get('marker_path')}."
        )
    else:
        previous_seen = str(since.get("previous_seen_at") or "unknown")
        console.print(
            "[bold]Since last check[/bold] "
            f"{since_summary.get('commits', 0)} commit(s), "
            f"{since_summary.get('files_changed', 0)} tracked file change(s), "
            f"{since_summary.get('dirty_files', 0)} dirty file(s), "
            f"{since_summary.get('brain_count_changes', 0)} brain count change(s) "
            f"since {previous_seen}"
        )
    if since.get("error"):
        console.print(f"  [yellow]degraded:[/yellow] {since['error']}")
    since_journal = since.get("journal") or {}
    since_groups = since_journal.get("groups") or []
    if since_groups:
        console.print("  journal:")
        for group in since_groups[:3]:
            console.print(f"  - {group.get('label', 'Activity')}: {group.get('count', 0)} event(s)")
            if verbose:
                for summary in (group.get("summaries") or [])[:3]:
                    console.print(f"    - {summary}")
    elif not since.get("first_run") and since_journal.get("available") is False:
        console.print("  [yellow]journal unavailable[/yellow]")

    drift_summary = drift.get("summary") or {}
    if drift_summary.get("total", 0):
        console.print(
            "[bold]Drift[/bold] "
            f"{drift_summary.get('errors', 0)} error(s), "
            f"{drift_summary.get('warnings', 0)} warning(s), "
            f"{drift_summary.get('info', 0)} info"
        )
        for item in (drift.get("items") or [])[:5]:
            console.print(f"  - {item['severity']}: {item['summary']}")
            if verbose and item.get("repair"):
                console.print(f"    next: {item['repair']}")
    else:
        console.print("[bold]Drift[/bold] no stale or broken status signals detected")

    relationship_summary = relationship_health.get("summary") or {}
    if relationship_summary.get("gaps", 0):
        console.print(
            "[bold]Relationship health[/bold] "
            f"{relationship_summary.get('warnings', 0)} warning(s), "
            f"{relationship_summary.get('info', 0)} info"
        )
        for gap in (relationship_health.get("gaps") or [])[:3]:
            console.print(f"  - {gap['summary']}")
            if verbose and gap.get("repair"):
                console.print(f"    next: {gap['repair']}")
    else:
        console.print("[bold]Relationship health[/bold] no actionable business-link gaps detected")

    playbook_summary = playbook_health.get("summary") or {}
    if playbook_summary.get("gaps", 0):
        console.print(
            "[bold]Playbook health[/bold] "
            f"{playbook_summary.get('warnings', 0)} warning(s), "
            f"{playbook_summary.get('info', 0)} info"
        )
        for gap in (playbook_health.get("gaps") or [])[:3]:
            console.print(f"  - {gap['summary']}")
            if verbose and gap.get("repair"):
                console.print(f"    next: {gap['repair']}")

    repo_mark = (
        "[green]yes[/green]" if repo["looks_like_mainbranch_repo"] else "[yellow]no[/yellow]"
    )
    branch = git.get("branch") or "(unknown)"
    dirty = "dirty" if git.get("dirty") else "clean"
    if not git.get("inside_work_tree"):
        branch = "not a git repo"
        dirty = str(git.get("error") or "")
    console.print(
        f"[bold]Repo[/bold] {repo_mark} Main Branch repo  branch: {branch}  state: {dirty}"
    )
    console.print(f"[bold]Install[/bold] {report['install']['detail']}")

    topology = report.get("topology") or {}
    topology_summary = topology.get("summary") or {}
    topology_registry = topology.get("registry") or {}
    topology_current = topology.get("current_repo") or {}
    topology_counts = topology.get("child_counts") or {}
    if not topology_summary.get("registry_found"):
        console.print("[bold]Business map[/bold] no core/operations/repo-topology.md yet")
    elif not topology_summary.get("registry_ok"):
        console.print("[bold]Business map[/bold] [yellow]registry present but unparsable[/yellow]")
    else:
        display_name = topology_registry.get("business_display_name") or "(no display name)"
        total_children = topology_counts.get("total", 0)
        restricted = topology_summary.get("restricted_repo_count", 0)
        suffix = f", restricted {restricted}" if restricted else ""
        console.print(
            f"[bold]Business map[/bold] {display_name} — {total_children} child repo(s){suffix}"
        )
    if topology_current.get("matched"):
        identifier = topology_current.get("slug") or topology_current.get("remote_full_name") or "?"
        role = topology_current.get("role") or "?"
        console.print(f"  this repo: {role} ({identifier})")
    if verbose:
        topology_findings = topology.get("findings") or []
        shown = 0
        for finding in topology_findings:
            severity = finding.get("severity", "")
            if severity not in {"warn", "error"}:
                continue
            console.print(f"  - {severity}: {finding.get('summary', '')}")
            shown += 1
            if shown >= 3:
                break

    claude = runtime["claude_code"]
    skills = runtime["skill_wiring"]
    codex = runtime.get("codex_cli") or {}
    claude_mark = "[green]found[/green]" if claude["found"] else "[yellow]missing[/yellow]"
    skill_mark = "[green]wired[/green]" if skills["ok"] else "[yellow]missing[/yellow]"
    codex_mark = "[green]ready[/green]" if codex.get("ok") else "[blue]experimental[/blue]"
    console.print(
        f"[bold]Runtime[/bold] Claude Code: {claude_mark}  skills: {skill_mark}  "
        f"Codex: {codex_mark}"
    )

    integration_summary = integrations["summary"]
    if integration_summary["configured"]:
        console.print(
            "[bold]Integrations[/bold] "
            f"configured {integration_summary['configured']}  "
            f"healthy {integration_summary['healthy']}  "
            f"needs repair {integration_summary['needs_repair']}"
        )
        for item in integrations.get("providers", []):
            if not item["ok"] and verbose:
                console.print(
                    f"  - {item['provider']}: {item['state']}  next: {item['repair_command']}"
                )

    measurement = report.get("measurement") or {}
    if measurement.get("available"):
        console.print(
            f"[bold]Measurement[/bold] {measurement.get('state')}  {measurement.get('summary')}"
        )
        if verbose and measurement.get("repair"):
            console.print(f"  next: {measurement['repair']}")

    counts = brain["counts"]
    pushes_count = counts.get("pushes", 0)
    campaigns_count = counts.get("campaigns", 0)
    pushes_segment = f"pushes {pushes_count}"
    if campaigns_count:
        pushes_segment += f" (legacy campaigns {campaigns_count})"
    console.print(
        "[bold]Brain[/bold] "
        f"core {counts['core'] + counts['reference/core']}  "
        f"research {counts['research']}  decisions {counts['decisions']}  "
        f"bets {counts['bets']}  {pushes_segment}  "
        f"log {counts['log']}  documents {counts['documents']}"
    )

    if verbose and brain["recent_decisions"]:
        console.print("\n[bold]Recent decisions[/bold]")
        for item in brain["recent_decisions"][:3]:
            suffix = f" [{item['status']}]" if item["status"] else ""
            console.print(f"  - {item['date'] or item['updated_at'][:10]}  {item['title']}{suffix}")
    if verbose and brain["stale_decisions"]:
        console.print("[yellow]Stale proposed/running decisions[/yellow]")
        for item in brain["stale_decisions"][:3]:
            console.print(f"  - {item['path']} ({item['age_days']} days)")
    if verbose and brain.get("stale_research"):
        console.print("[yellow]Stale research[/yellow]")
        for item in brain["stale_research"][:3]:
            console.print(f"  - {item['path']} ({item['age_days']} days)")
    if verbose and brain["recent_research"]:
        console.print("\n[bold]Recent research[/bold]")
        for item in brain["recent_research"][:3]:
            console.print(f"  - {item['date'] or item['updated_at'][:10]}  {item['title']}")

    bets = brain.get("bets") or {}
    active_bets = bets.get("active") or []
    if active_bets:
        console.print("\n[bold]Active bets[/bold]")
        for item in active_bets[:3]:
            deadline = item.get("deadline") or "no deadline"
            console.print(f"  - {deadline}  {item['title']} [{item['status']}]")
    overdue_bets = bets.get("overdue") or []
    if overdue_bets:
        console.print("[yellow]Overdue active bets[/yellow]")
        for item in overdue_bets[:3]:
            console.print(f"  - {item['path']} ({item['days_overdue']} days overdue)")

    onboarding_summary = onboarding.get("summary") or {}
    if verbose and onboarding_summary.get("status") == "in_progress":
        console.print("\n[bold]Onboarding[/bold]")
        console.print(
            "  "
            f"{onboarding_summary.get('completed_required', 0)}/"
            f"{onboarding_summary.get('total_required', 0)} required steps complete"
        )
        missing = onboarding_summary.get("missing_inputs") or []
        if missing:
            console.print(f"  missing: {', '.join(missing[:5])}")
        console.print(f"  next: {onboarding_summary.get('next_recommended_action')}")

    journal = report.get("journal") or {}
    if verbose and journal.get("events"):
        console.print("\n[bold]Business journal[/bold]")
        for item in journal["events"][:5]:
            refs = item.get("refs") or []
            ref_label = f" refs {len(refs)}" if refs else ""
            console.print(
                f"  - {item.get('date')} {item.get('commit')}  {item.get('summary')}{ref_label}"
            )

    if verbose and report["git_activity"]["items"]:
        console.print("\n[bold]Recent git activity[/bold]")
        for item in report["git_activity"]["items"][:3]:
            files = ", ".join(item["files"][:2])
            if len(item["files"]) > 2:
                files += f" +{len(item['files']) - 2}"
            console.print(f"  - {item['date']} {item['commit']}  {item['subject']}  {files}")

    console.print("\n[bold]GitHub[/bold]")
    github_context = github.get("context") or {}
    if github_context and not github_context.get("ok"):
        console.print(f"  {github_context.get('summary')}")
        if github_context.get("repair_command"):
            console.print(f"  next: {github_context['repair_command']}")
    elif not github["available"]:
        console.print("  gh unavailable; skipping issues and PRs.")
    elif not github["authenticated"]:
        console.print("  gh not authenticated; run `gh auth login` to include business tasks.")
    else:
        summary = github.get("summary") or {}
        sections = github.get("sections") or {}
        assigned_count = summary.get("assigned_tasks", len(github.get("assigned_issues", [])))
        attention_count = summary.get(
            "attention_requests",
            len(github.get("review_requests", [])),
        )
        shipped_count = summary.get("shipped_this_week", len(github.get("recent_merged_prs", [])))
        console.print(
            f"  tasks assigned: {assigned_count}  "
            f"attention: {attention_count}  "
            f"open proposals: {summary.get('open_proposals', 0)}  "
            f"shipped this week: {shipped_count}"
        )
        assigned_tasks = sections.get("assigned_tasks") or github.get("assigned_issues", [])
        attention_requests = sections.get("attention_requests") or github.get("review_requests", [])
        open_proposals = sections.get("open_proposals") or []
        shipped = sections.get("shipped_this_week") or github.get("recent_merged_prs", [])
        blocked_or_stale = sections.get("blocked_or_stale_tasks") or []
        if verbose:
            for issue in assigned_tasks[:3]:
                console.print(f"  - task #{issue['number']}: {issue['title']}")
            for item in attention_requests[:3]:
                reason = item.get("reason", "Needs attention")
                console.print(f"  - attention #{item['number']}: {item['title']} ({reason})")
            for pr in open_proposals[:3]:
                console.print(f"  - proposal #{pr['number']}: {pr['title']}")
            for pr in shipped[:3]:
                console.print(f"  - shipped #{pr['number']}: {pr['what_shipped']}")
            for issue in blocked_or_stale[:3]:
                console.print(f"  - blocked/stale #{issue['number']}: {issue['title']}")
        for error in github["errors"][:2]:
            console.print(f"  [yellow]degraded:[/yellow] {error}")

    console.print("\n[bold]Next[/bold]")
    ranked_actions = report.get("ranked_actions") or []
    if ranked_actions:
        for index, action in enumerate(ranked_actions[:3], start=1):
            title = str(action.get("title") or action.get("id") or "Next action")
            reason = str(action.get("reason") or "")
            command = str(action.get("command") or "")
            console.print(f"  {index}. {title}")
            if reason:
                console.print(f"     why: {reason}")
            if command:
                console.print(f"     next: {command}")
    else:
        for action in readiness["next_actions"]:
            console.print(f"  - {action}")
    console.print()
