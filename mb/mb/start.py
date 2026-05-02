"""``mb start`` — hand off from the CLI to the configured agent runtime."""

from __future__ import annotations

import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from mb.engine import install_mode, link_status
from mb.status import _looks_like_mainbranch_repo


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _is_interactive_terminal() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _run_command(args: list[str], cwd: Path, timeout: float = 3.0) -> dict[str, Any]:
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


def _git_status(repo: Path) -> dict[str, Any]:
    if not repo.exists():
        return {
            "available": bool(_which("git")),
            "inside_work_tree": False,
            "branch": "",
            "dirty": False,
            "dirty_count": 0,
            "error": "repo path does not exist",
        }
    if not _which("git"):
        return {
            "available": False,
            "inside_work_tree": False,
            "branch": "",
            "dirty": False,
            "dirty_count": 0,
            "error": "git not on PATH",
        }

    inside = _run_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo)
    if not inside["ok"] or inside["stdout"].strip() != "true":
        return {
            "available": True,
            "inside_work_tree": False,
            "branch": "",
            "dirty": False,
            "dirty_count": 0,
            "error": "not a git work tree",
        }

    branch = _run_command(["git", "branch", "--show-current"], cwd=repo)
    status = _run_command(["git", "status", "--porcelain"], cwd=repo)
    dirty_lines = (
        [line for line in status["stdout"].splitlines() if line.strip()] if status["ok"] else []
    )
    return {
        "available": True,
        "inside_work_tree": True,
        "branch": branch["stdout"].strip() if branch["ok"] else "",
        "dirty": bool(dirty_lines),
        "dirty_count": len(dirty_lines),
        "dirty_files": dirty_lines[:10],
        "error": "" if status["ok"] else status["stderr"].strip(),
    }


def _display_command(repo: Path) -> str:
    return f"cd {shlex.quote(str(repo))} && claude"


def _launch_claude(repo: Path) -> int:
    try:
        return subprocess.call(["claude"], cwd=repo)
    except FileNotFoundError:
        return 127
    except subprocess.SubprocessError:
        return 1


def _build_checks(
    repo_shape: dict[str, Any],
    git: dict[str, Any],
    claude_path: str,
    wiring: dict[str, Any],
) -> list[dict[str, Any]]:
    dirty_detail = (
        f"{git['dirty_count']} changed file(s)" if git.get("dirty") else "clean working tree"
    )
    return [
        {
            "name": "mainbranch_repo",
            "ok": bool(repo_shape["looks_like_mainbranch_repo"]),
            "severity": "error",
            "detail": "Main Branch business repo"
            if repo_shape["looks_like_mainbranch_repo"]
            else "not a Main Branch business repo",
            "repair": "Run from a business repo, or pass `--repo /path/to/business-repo`.",
        },
        {
            "name": "git_work_tree",
            "ok": bool(git.get("inside_work_tree")),
            "severity": "error",
            "detail": git.get("branch") or git.get("error") or "git work tree",
            "repair": "Run `git init` if this should be a Main Branch business repo.",
        },
        {
            "name": "git_clean",
            "ok": not bool(git.get("dirty")),
            "severity": "warn",
            "detail": dirty_detail,
            "repair": (
                "Review, commit, or stash local changes before handing substantive work "
                "to an agent."
            ),
        },
        {
            "name": "claude_code",
            "ok": bool(claude_path),
            "severity": "error",
            "detail": claude_path or "claude not on PATH",
            "repair": "Install Claude Code: https://claude.ai/install",
        },
        {
            "name": "skill_wiring",
            "ok": bool(wiring["ok"]),
            "severity": "error",
            "detail": "start skill discoverable"
            if wiring["ok"]
            else "Claude Code start skill is not wired",
            "repair": "Run `mb skill link --repo .` from the business repo.",
        },
        {
            "name": "install_mode",
            "ok": install_mode() != "unknown",
            "severity": "info",
            "detail": install_mode(),
            "repair": "Reinstall Main Branch with `pipx install mainbranch` if commands fail.",
        },
    ]


def _hard_failures(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        check
        for check in checks
        if not check["ok"] and check.get("severity") not in {"warn", "info"}
    ]


def _next_actions(
    repo: Path,
    checks: list[dict[str, Any]],
    handoff_ready: bool,
) -> list[str]:
    actions = [str(check["repair"]) for check in checks if not check["ok"] and check["repair"]]
    if handoff_ready:
        actions.extend([f"Run `{_display_command(repo)}`.", "Then type `/start` in Claude Code."])
    return actions[:6]


def run(repo: str = ".", launch: bool = False) -> dict[str, Any]:
    """Build a handoff report and optionally launch Claude Code."""
    repo_path = Path(repo).expanduser().resolve()
    repo_shape = _looks_like_mainbranch_repo(repo_path)
    git = _git_status(repo_path)
    claude_path = _which("claude")
    wiring = link_status(repo_path)
    checks = _build_checks(repo_shape, git, claude_path, wiring)
    hard_failures = _hard_failures(checks)
    handoff_ready = not hard_failures

    launch_report: dict[str, Any] = {
        "requested": launch,
        "safe": handoff_ready and _is_interactive_terminal(),
        "attempted": False,
        "returncode": None,
        "blocked_reason": "",
    }
    if launch and not handoff_ready:
        launch_report["blocked_reason"] = "handoff checks are not passing"
    elif launch and not launch_report["safe"]:
        launch_report["blocked_reason"] = (
            "not an interactive terminal; run the printed command yourself"
        )
    elif launch:
        launch_report["attempted"] = True
        launch_report["returncode"] = _launch_claude(repo_path)

    ok = handoff_ready
    if launch:
        ok = bool(launch_report["attempted"] and launch_report["returncode"] == 0)

    return {
        "ok": ok,
        "handoff_ready": handoff_ready,
        "repo": {"path": str(repo_path), **repo_shape},
        "git": git,
        "runtime": {
            "name": "claude-code",
            "executable": "claude",
            "found": bool(claude_path),
            "path": claude_path,
            "skill_wiring": wiring,
        },
        "checks": checks,
        "command": {
            "cwd": str(repo_path),
            "argv": ["claude"],
            "display": _display_command(repo_path),
            "follow_up": "/start",
        },
        "launch": launch_report,
        "next_actions": _next_actions(repo_path, checks, handoff_ready),
    }


def render_human(report: dict[str, Any]) -> None:
    """Print the runtime handoff in a compact human-readable form."""
    from rich.console import Console

    console = Console()
    repo = report["repo"]
    git = report["git"]
    runtime = report["runtime"]
    wiring = runtime["skill_wiring"]
    command = report["command"]
    launch = report["launch"]

    console.print(f"\n[bold]mb start[/bold]  {repo['path']}\n")
    console.print(
        "[bold]Repo[/bold] "
        + ("[green]ok[/green]" if repo["looks_like_mainbranch_repo"] else "[red]missing[/red]")
        + "  Main Branch business repo"
    )
    git_label = git.get("branch") or git.get("error") or "unknown"
    dirty = "dirty" if git.get("dirty") else "clean"
    console.print(
        "[bold]Git[/bold]  "
        + ("[green]ok[/green]" if git.get("inside_work_tree") else "[red]missing[/red]")
        + f"  {git_label}  {dirty}"
    )
    console.print(
        "[bold]Runtime[/bold]  Claude Code "
        + ("[green]found[/green]" if runtime["found"] else "[red]missing[/red]")
    )
    console.print(
        "[bold]Skills[/bold]  /start "
        + ("[green]wired[/green]" if wiring["ok"] else "[red]missing[/red]")
    )

    console.print("\n[bold]Command[/bold]")
    console.print(f"  {command['display']}")
    console.print(f"  {command['follow_up']}")

    if launch["requested"]:
        if launch["attempted"]:
            console.print(f"\n[bold]Launch[/bold] claude exited {launch['returncode']}")
        else:
            console.print(f"\n[yellow]Launch skipped:[/yellow] {launch['blocked_reason']}")

    if report["next_actions"]:
        console.print("\n[bold]Next[/bold]")
        for action in report["next_actions"]:
            console.print(f"  - {action}")
    console.print()
