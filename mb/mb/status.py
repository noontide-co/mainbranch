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

from mb import __version__, github_activity
from mb import connect as connect_mod
from mb import onboard as onboard_mod
from mb import pushes as pushes_mod
from mb import ranker as ranker_mod
from mb import site as site_mod
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


def _read_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    raw = text[3:end].strip()
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
        for line in path.read_text(encoding="utf-8").splitlines():
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
    count_changes = _brain_count_changes(brain.get("counts") or {}, previous_counts)
    dirty_count = int(git.get("dirty_count") or 0)
    commits = git_since.get("commits") or []
    changed_files = git_since.get("changed_files") or []
    summary = {
        "commits": len(commits) if isinstance(commits, list) else 0,
        "files_changed": len(changed_files) if isinstance(changed_files, list) else 0,
        "dirty_files": dirty_count,
        "brain_count_changes": len(count_changes),
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


def _drift(report: dict[str, Any]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
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
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a deterministic daily briefing report."""
    repo_path = Path(path).resolve()
    generated_at = _format_timestamp(now or _utc_now())
    repo_shape = _looks_like_mainbranch_repo(repo_path)
    git = _git_info(repo_path)
    update = package_update_status(repo_path)
    github = _github(repo_path, git)
    brain = _brain(repo_path)
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
    report["since_last_check"] = _since_last_check(
        repo_path,
        marker=marker,
        git=git,
        brain=brain,
        generated_at=generated_at,
    )
    report["drift"] = _drift(report)
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

    claude = runtime["claude_code"]
    skills = runtime["skill_wiring"]
    claude_mark = "[green]found[/green]" if claude["found"] else "[yellow]missing[/yellow]"
    skill_mark = "[green]wired[/green]" if skills["ok"] else "[yellow]missing[/yellow]"
    console.print(f"[bold]Runtime[/bold] Claude Code: {claude_mark}  skills: {skill_mark}")

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
