"""``mb status`` — cheap daily briefing for a Main Branch repo."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from mb import __version__
from mb.engine import install_mode, link_status

IMPORTANT_DIRS = (
    "core",
    "reference/core",
    "research",
    "decisions",
    "campaigns",
    "log",
    "documents",
)
STALE_DECISION_DAYS = 14


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
        "skill_wiring": (repo / ".claude" / "skills" / "start" / "SKILL.md").is_file(),
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

    research = [
        _file_summary(repo, path) for path in _relative_markdown_files(repo, "research")[:5]
    ]

    return {
        "counts": counts,
        "recent_decisions": decisions[:5],
        "stale_decisions": stale[:5],
        "recent_research": research,
    }


def _repo_full_name(remote: str) -> str:
    if not remote:
        return ""
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$", remote)
    if not match:
        return ""
    return f"{match.group('owner')}/{match.group('repo')}"


def _gh_json(args: list[str], repo: Path) -> tuple[bool, Any, str]:
    result = _run_command(args, cwd=repo, timeout=5.0)
    if not result["ok"]:
        return False, None, result["stderr"].strip() or result["stdout"].strip()
    try:
        return True, json.loads(result["stdout"] or "[]"), ""
    except json.JSONDecodeError:
        return False, None, "gh returned invalid JSON"


def _github(repo: Path, git: dict[str, Any]) -> dict[str, Any]:
    if not _which("gh"):
        return {
            "available": False,
            "authenticated": False,
            "repo": _repo_full_name(str(git.get("remote", ""))),
            "assigned_issues": [],
            "review_requests": [],
            "recent_merged_prs": [],
            "errors": ["gh not on PATH"],
        }

    auth = _run_command(["gh", "auth", "status"], cwd=repo, timeout=5.0)
    if not auth["ok"]:
        return {
            "available": True,
            "authenticated": False,
            "repo": _repo_full_name(str(git.get("remote", ""))),
            "assigned_issues": [],
            "review_requests": [],
            "recent_merged_prs": [],
            "errors": ["gh not authenticated"],
        }

    errors: list[str] = []
    repo_name = _repo_full_name(str(git.get("remote", "")))
    assigned_ok, assigned, assigned_error = _gh_json(
        [
            "gh",
            "issue",
            "list",
            "--state",
            "open",
            "--assignee",
            "@me",
            "--limit",
            "5",
            "--json",
            "number,title,url,updatedAt,labels",
        ],
        repo,
    )
    if not assigned_ok:
        errors.append(f"issues: {assigned_error}")

    reviews_ok, reviews, reviews_error = _gh_json(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--search",
            "review-requested:@me",
            "--limit",
            "5",
            "--json",
            "number,title,url,updatedAt,author",
        ],
        repo,
    )
    if not reviews_ok:
        errors.append(f"review requests: {reviews_error}")

    merged_ok, merged, merged_error = _gh_json(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            "5",
            "--json",
            "number,title,url,mergedAt,body",
        ],
        repo,
    )
    if not merged_ok:
        errors.append(f"merged PRs: {merged_error}")

    merged_prs = [_summarize_pr(pr) for pr in merged] if isinstance(merged, list) else []
    return {
        "available": True,
        "authenticated": True,
        "repo": repo_name,
        "assigned_issues": assigned if isinstance(assigned, list) else [],
        "review_requests": reviews if isinstance(reviews, list) else [],
        "recent_merged_prs": merged_prs,
        "errors": errors,
    }


def _summarize_pr(pr: dict[str, Any]) -> dict[str, Any]:
    title = str(pr.get("title", "") or "")
    body = str(pr.get("body", "") or "")
    summary = ""
    for line in body.splitlines():
        stripped = line.strip().strip("-* ")
        if stripped and not stripped.startswith("#"):
            summary = stripped
            break
    if not summary:
        summary = title
    return {
        "number": pr.get("number"),
        "title": title,
        "url": pr.get("url", ""),
        "mergedAt": pr.get("mergedAt", ""),
        "what_shipped": summary[:220],
    }


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
            else "Run `mb skill link --repo .` from the business repo.",
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
            "ok": bool(report["install"]["ok"]),
            "weight": 15,
            "repair": "Reinstall Main Branch with `pipx install mainbranch`.",
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
    if not report["github"]["authenticated"]:
        next_actions.append("Run `gh auth login` to include assigned issues and shipped PRs.")
    if not next_actions:
        next_actions.append("Run `claude` in this repo, then `/start`.")

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


def run(path: str = ".") -> dict[str, Any]:
    """Build a deterministic daily briefing report."""
    repo_path = Path(path).resolve()
    repo_shape = _looks_like_mainbranch_repo(repo_path)
    git = _git_info(repo_path)
    report: dict[str, Any] = {
        "ok": True,
        "repo": {"path": str(repo_path), **repo_shape},
        "install": _install(),
        "runtime": _runtime(repo_path),
        "git": git,
        "git_activity": _git_recent_activity(repo_path, git),
        "brain": _brain(repo_path),
        "github": _github(repo_path, git),
    }
    report["readiness"] = _readiness(report)
    report["ok"] = report["readiness"]["level"] != "not_ready"
    return report


def render_human(report: dict[str, Any]) -> None:
    """Print a concise terminal briefing."""
    from rich.console import Console

    console = Console()
    repo = report["repo"]
    git = report["git"]
    runtime = report["runtime"]
    brain = report["brain"]
    github = report["github"]
    readiness = report["readiness"]

    console.print(f"\n[bold]mb status[/bold]  {repo['path']}")
    console.print(
        f"[bold]{readiness['level'].replace('_', ' ')}[/bold]  {readiness['score']}/100\n"
    )

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

    counts = brain["counts"]
    console.print(
        "[bold]Brain[/bold] "
        f"core {counts['core'] + counts['reference/core']}  "
        f"research {counts['research']}  decisions {counts['decisions']}  "
        f"campaigns {counts['campaigns']}  log {counts['log']}  documents {counts['documents']}"
    )

    if brain["recent_decisions"]:
        console.print("\n[bold]Recent decisions[/bold]")
        for item in brain["recent_decisions"][:3]:
            suffix = f" [{item['status']}]" if item["status"] else ""
            console.print(f"  - {item['date'] or item['updated_at'][:10]}  {item['title']}{suffix}")
    if brain["stale_decisions"]:
        console.print("[yellow]Stale proposed/running decisions[/yellow]")
        for item in brain["stale_decisions"][:3]:
            console.print(f"  - {item['path']} ({item['age_days']} days)")
    if brain["recent_research"]:
        console.print("\n[bold]Recent research[/bold]")
        for item in brain["recent_research"][:3]:
            console.print(f"  - {item['date'] or item['updated_at'][:10]}  {item['title']}")

    if report["git_activity"]["items"]:
        console.print("\n[bold]Recent git activity[/bold]")
        for item in report["git_activity"]["items"][:3]:
            files = ", ".join(item["files"][:2])
            if len(item["files"]) > 2:
                files += f" +{len(item['files']) - 2}"
            console.print(f"  - {item['date']} {item['commit']}  {item['subject']}  {files}")

    console.print("\n[bold]GitHub[/bold]")
    if not github["available"]:
        console.print("  gh unavailable; skipping issues and PRs.")
    elif not github["authenticated"]:
        console.print("  gh not authenticated; run `gh auth login` to include business tasks.")
    else:
        console.print(
            f"  assigned issues: {len(github['assigned_issues'])}  "
            f"review requests: {len(github['review_requests'])}  "
            f"recent merged PRs: {len(github['recent_merged_prs'])}"
        )
        for issue in github["assigned_issues"][:3]:
            console.print(f"  - issue #{issue['number']}: {issue['title']}")
        for pr in github["recent_merged_prs"][:3]:
            console.print(f"  - shipped #{pr['number']}: {pr['what_shipped']}")
        for error in github["errors"][:2]:
            console.print(f"  [yellow]degraded:[/yellow] {error}")

    console.print("\n[bold]Next[/bold]")
    for action in readiness["next_actions"]:
        console.print(f"  - {action}")
    console.print()
