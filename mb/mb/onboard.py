"""``mb onboard`` — adaptive human setup flow for Main Branch."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from mb import init as init_mod
from mb.engine import link_skills, link_status

LEVELS = {"beginner", "intermediate", "power"}
MODES = {"new", "connect", "auto"}


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _run_command(args: list[str], cwd: Path | None = None, timeout: float = 5.0) -> dict[str, Any]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"ok": False, "stdout": "", "stderr": f"{args[0]} not found", "returncode": 127}
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": "command timed out", "returncode": 124}
    except subprocess.SubprocessError as exc:
        return {"ok": False, "stdout": "", "stderr": str(exc), "returncode": 1}
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "my-business"


def _repo_markers(repo: Path) -> dict[str, bool]:
    return {
        "exists": repo.exists(),
        "git": (repo / ".git").exists(),
        "claude_md": (repo / "CLAUDE.md").is_file(),
        "core": (repo / "core").is_dir() or (repo / "reference" / "core").exists(),
        "research": (repo / "research").is_dir(),
        "decisions": (repo / "decisions").is_dir(),
        "skill_start": (repo / ".claude" / "skills" / "start" / "SKILL.md").is_file(),
    }


def _looks_initialized(markers: dict[str, bool]) -> bool:
    shaped_dirs = sum(1 for key in ("core", "research", "decisions") if markers[key])
    return markers["claude_md"] and shaped_dirs >= 2


def _tool_readiness(repo: Path) -> dict[str, Any]:
    git_path = _which("git")
    gh_path = _which("gh")
    claude_path = _which("claude")
    gh_auth = False
    git_repo = False

    if git_path:
        git_probe = _run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo)
        git_repo = git_probe["ok"] and git_probe["stdout"].strip() == "true"
    if gh_path:
        gh_probe = _run_command(["gh", "auth", "status"], cwd=repo)
        gh_auth = gh_probe["ok"]

    return {
        "git": {
            "found": bool(git_path),
            "path": git_path,
            "repo": git_repo,
            "repair": "" if git_path else "Install git, then run `mb doctor`.",
        },
        "github_cli": {
            "found": bool(gh_path),
            "authenticated": gh_auth,
            "path": gh_path,
            "repair": ""
            if gh_path and gh_auth
            else (
                "Install GitHub CLI: https://cli.github.com/ and run `gh auth login`."
                if not gh_path
                else "Run `gh auth login` to connect GitHub tasks and proposals."
            ),
        },
        "claude_code": {
            "found": bool(claude_path),
            "path": claude_path,
            "repair": "" if claude_path else "Install Claude Code: https://claude.ai/install",
        },
    }


def _infer_level(tool_readiness: dict[str, Any]) -> str:
    git = bool(tool_readiness["git"]["found"])
    gh = bool(
        tool_readiness["github_cli"]["found"] and tool_readiness["github_cli"]["authenticated"]
    )
    claude = bool(tool_readiness["claude_code"]["found"])
    if git and gh and claude:
        return "power"
    if git and (gh or claude):
        return "intermediate"
    return "beginner"


def _normalize_level(level: str) -> str:
    normalized = level.strip().lower().replace("_", "-")
    if normalized == "power-user":
        normalized = "power"
    if normalized and normalized not in LEVELS and normalized != "auto":
        raise ValueError("level must be beginner, intermediate, power, or auto")
    return normalized or "auto"


def _normalize_mode(mode: str, existing: bool) -> str:
    normalized = mode.strip().lower()
    if normalized not in MODES:
        raise ValueError("mode must be new, connect, or auto")
    if normalized == "auto":
        return "connect" if existing else "new"
    return normalized


def _next_steps(repo: Path) -> list[str]:
    return [
        f"cd {repo}",
        "claude",
        "/start",
    ]


def run(
    *,
    path: str,
    name: str = "",
    mode: str = "auto",
    level: str = "auto",
) -> dict[str, Any]:
    """Create or connect a business repo and verify the Claude Code handoff."""
    target = Path(path).expanduser().resolve()
    before = _repo_markers(target)
    normalized_mode = _normalize_mode(mode, _looks_initialized(before))

    errors: list[str] = []
    warnings: list[str] = []
    created: list[str] = []
    action = normalized_mode
    init_result: dict[str, Any] | None = None
    link_result: dict[str, Any] | None = None

    if normalized_mode == "connect" and not target.exists():
        errors.append(f"cannot connect missing repo: {target}")
    elif normalized_mode == "connect":
        link_result = link_skills(target)
        created.extend(str(item) for item in link_result.get("created", []))
        if not link_result.get("ok"):
            errors.extend(str(item) for item in link_result.get("errors", []))
        action = "repaired" if before["claude_md"] else "connected"
    else:
        business_name = name.strip() or target.name.replace("-", " ").title()
        init_result = init_mod.run(path=str(target), name=business_name)
        created.extend(str(item) for item in init_result.get("created", []))
        if init_result["status"] == "error":
            errors.append(str(init_result.get("error") or "mb init failed"))
        elif init_result["status"] == "already-initialized":
            action = "repaired"
        else:
            action = "created"

    after = _repo_markers(target)
    wiring = link_status(target)
    tools = _tool_readiness(target)
    selected_level = _normalize_level(level)
    if selected_level == "auto":
        selected_level = _infer_level(tools)

    if not after["git"]:
        warnings.append("Repo is not a git work tree. Run `git init` or `mb doctor` for repair.")
    if normalized_mode == "connect" and not _looks_initialized(after):
        errors.append(
            "Existing repo does not look like a Main Branch repo. "
            "Run `mb onboard --mode new --path <repo> --name <business>` to scaffold it."
        )
    if not tools["github_cli"]["found"] or not tools["github_cli"]["authenticated"]:
        warnings.append(str(tools["github_cli"]["repair"]))
    if not tools["claude_code"]["found"]:
        warnings.append(str(tools["claude_code"]["repair"]))
    if not wiring["ok"]:
        warnings.append("Claude Code skill discovery is not wired. Run `mb doctor` for details.")

    ok = not errors and wiring["ok"] and after["claude_md"]
    return {
        "ok": ok,
        "status": "ok" if ok else "error",
        "action": action,
        "path": str(target),
        "mode": normalized_mode,
        "level": selected_level,
        "business_name": name.strip() or target.name.replace("-", " ").title(),
        "created": created,
        "repo": {
            "before": before,
            "after": after,
            "looks_initialized": _looks_initialized(after),
        },
        "tools": tools,
        "skill_wiring": wiring,
        "warnings": [warning for warning in warnings if warning],
        "errors": errors,
        "doctor_command": f"mb doctor {target}",
        "next_steps": _next_steps(target),
        "init": init_result,
        "link": link_result,
    }


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()
