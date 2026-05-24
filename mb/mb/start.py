"""``mb start`` — hand off from the CLI to the configured agent runtime."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from mb import books as books_mod
from mb import checkpoint as checkpoint_mod
from mb import codex as codex_mod
from mb import journal as journal_mod
from mb import vocabulary
from mb.engine import install_mode, link_status
from mb.freshness import format_update_alert, package_update_status
from mb.status import _looks_like_mainbranch_repo, push_facts


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
    if os.name == "nt":
        return f"cd /d {subprocess.list2cmdline([str(repo)])} && claude"
    return f"cd {shlex.quote(str(repo))} && claude"


def _codex_display_command(repo: Path) -> str:
    return f"codex -C {shlex.quote(str(repo))}"


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
    codex: dict[str, Any],
    update: dict[str, Any],
) -> list[dict[str, Any]]:
    dirty_detail = (
        f"{git['dirty_count']} changed file(s)" if git.get("dirty") else "clean working tree"
    )
    update_severity = str(update["severity"])
    update_check_severity = {
        "required": "error",
        "recommended": "warn",
        "unknown": "info",
    }.get(update_severity, "info")
    shadow_summary = wiring.get("shadow_report", {}).get("summary", {})
    active_shadows = int(shadow_summary.get("active_shadows", 0) or 0)
    legacy_globals = int(shadow_summary.get("legacy_globals", 0) or 0)
    skill_detail = (
        "mb-start skill discoverable"
        if wiring["ok"]
        else str(wiring.get("summary") or "Missing Main Branch start wiring.")
    )
    if wiring.get("stale_engine_paths"):
        current = wiring.get("current_mb") or {}
        wired = str(wiring.get("wired_engine_path") or wiring["stale_engine_paths"][0])
        skill_detail = (
            "Claude Code wiring points at a different Main Branch engine. "
            f"Current mb: {current.get('path') or 'unknown'} "
            f"{current.get('version') or ''}; wired engine: {wired}."
        )
        if wiring.get("stale_from_other_install"):
            skill_detail += " Multiple mb installs are active on PATH."
    checks = [
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
                "Review, save a checkpoint, or set aside local changes before handing "
                "substantive work to an agent."
            ),
        },
        {
            "name": "mainbranch_update",
            "ok": update_severity not in {"required", "recommended"},
            "severity": update_check_severity,
            "detail": update["reason"],
            "repair": update["command"],
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
            "detail": skill_detail,
            "repair": (
                "Run `mb doctor repair --plan`, review it, then run "
                "`mb doctor repair --apply` from the business repo."
            ),
        },
        {
            "name": "install_mode",
            "ok": install_mode() != "unknown",
            "severity": "info",
            "detail": install_mode(),
            "repair": "Reinstall Main Branch with `pipx install mainbranch` if commands fail.",
        },
    ]
    if active_shadows or legacy_globals:
        checks.append(
            {
                "name": "skill_shadows",
                "ok": active_shadows == 0,
                "severity": "error" if active_shadows else "warn",
                "detail": (
                    f"{active_shadows} active personal skill shadow(s), "
                    f"{legacy_globals} legacy personal skill trap(s)"
                ),
                "repair": "Run `mb skill repair --repo .` for details.",
            }
        )
    codex_executable = codex.get("executable") or {}
    codex_instructions = codex.get("instructions") or {}
    codex_runtime = codex.get("runtime") or {}
    codex_found = bool(codex_executable.get("found"))
    checks.extend(
        [
            {
                "name": "codex_cli",
                "ok": codex_found,
                "severity": "info",
                "detail": codex_executable.get("path") or "codex not on PATH",
                "repair": "",
            },
            {
                "name": "codex_agents_md",
                "ok": bool(codex_instructions.get("ok")),
                "severity": "warn" if codex_found else "info",
                "detail": (
                    "AGENTS.md, the global Codex plugin, and generated guidance point "
                    "Codex to mb facts, lifecycle routes, and workflow inventory"
                )
                if codex_instructions.get("ok")
                else (
                    "Codex AGENTS.md, plugin, marketplace, or generated guidance is "
                    "missing, stale, or missing required mb fact commands or lifecycle "
                    "discovery guidance"
                ),
                "repair": codex_instructions.get("repair") if codex_found else "",
            },
            {
                "name": "codex_runtime_mb",
                "ok": bool(
                    not codex_found or not codex_instructions.get("ok") or codex_runtime.get("ok")
                ),
                "severity": "warn",
                "detail": str(
                    codex_runtime.get("summary")
                    or "Codex runtime mb command has not been verified."
                ),
                "repair": str(codex_runtime.get("repair") or "") if codex_found else "",
            },
        ]
    )
    return checks


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
    codex: dict[str, Any] | None = None,
) -> list[str]:
    actions = [str(check["repair"]) for check in checks if not check["ok"] and check["repair"]]
    codex_actions = _codex_next_actions(repo, codex or {})
    if codex_actions:
        actions.extend(codex_actions)
        return actions[:6]
    if handoff_ready:
        actions.extend(
            [f"Run `{_display_command(repo)}`.", "Then type `/mb-start` in Claude Code."]
        )
    return actions[:6]


def _codex_next_actions(repo: Path, codex: dict[str, Any]) -> list[str]:
    executable = codex.get("executable") or {}
    if not executable.get("found"):
        return []
    instructions = codex.get("instructions") or {}
    if not instructions.get("ok"):
        repair = str(instructions.get("repair") or codex.get("repair") or "")
        return [repair] if repair else []
    runtime = codex.get("runtime") or {}
    if codex.get("status") == "runtime_mismatch" or runtime.get("mismatch"):
        repair = str(runtime.get("repair") or codex.get("repair") or "")
        actions = []
        if repair:
            actions.append(repair)
        actions.append("Rerun `mb status --json --peek` before continuing Codex owner-loop work.")
        return actions[:3]
    if not codex.get("runtime_ok"):
        repair = str(runtime.get("repair") or codex.get("repair") or "")
        return [repair] if repair else []
    if not codex.get("plugin_ok"):
        plugin_install = codex.get("plugin_install") or {}
        repair = str(plugin_install.get("repair") or codex.get("repair") or "")
        actions = []
        if repair:
            actions.append(repair)
        actions.append("Rerun `mb status --json --peek` before using Codex.")
        return actions[:3]
    if not codex.get("slash_commands_ready"):
        repair = str(codex.get("repair") or "")
        actions = []
        if repair:
            actions.append(repair)
        actions.append("Restart Codex, then type `/mb` to verify Main Branch commands.")
        return actions[:3]
    smoke_command = str(codex.get("smoke_command") or "")
    actions = [
        f"Run `{_codex_display_command(repo)}`.",
        "After Codex restarts, type `/mb-start` or `/mb-status`.",
    ]
    if smoke_command:
        actions.append(f"For a read-only Codex smoke, run `{smoke_command}`.")
    return actions


def run(repo: str = ".", launch: bool = False) -> dict[str, Any]:
    """Build a handoff report and optionally launch Claude Code."""
    repo_path = Path(repo).expanduser().resolve()
    repo_shape = _looks_like_mainbranch_repo(repo_path)
    git = _git_status(repo_path)
    claude_path = _which("claude")
    wiring = link_status(repo_path)
    codex = codex_mod.readiness(repo_path)
    update = package_update_status(repo_path)
    checkpoint = checkpoint_mod.status(repo_path)
    journal = journal_mod.collect(repo_path, limit=8, since="14 days ago")
    push_report = push_facts(repo_path)
    vocabulary_report = vocabulary.facts(repo_path)
    books = books_mod.readiness(repo_path)
    checks = _build_checks(repo_shape, git, claude_path, wiring, codex, update)
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

    codex_runtime: dict[str, Any] = {**codex}
    codex_executable = codex.get("executable") or {}
    if codex_executable.get("found"):
        codex_runtime["command"] = {
            "cwd": str(repo_path),
            "argv": ["codex", "-C", str(repo_path)],
            "display": _codex_display_command(repo_path),
            "startup_prompt": (
                "Start this Main Branch business day from `/mb-start` and read-only "
                "mb facts. Ask before writes. Stop if mb status/start reports "
                "runtime.codex_cli.status == runtime_mismatch or drift id "
                "codex_runtime_mb_mismatch."
            ),
            "next_actions": _codex_next_actions(repo_path, codex),
        }

    return {
        "ok": ok,
        "handoff_ready": handoff_ready,
        "repo": {"path": str(repo_path), **repo_shape},
        "update": update,
        "checkpoint": checkpoint,
        "journal": journal,
        "books": books,
        "pushes": push_report["records"],
        "active_pushes": push_report["active"],
        "push_count": push_report["count"],
        "canonical_push_count": push_report["canonical_count"],
        "campaigns": push_report["legacy_campaigns"],
        "active_campaigns": push_report["active_legacy_campaigns"],
        "campaign_count": push_report["legacy_campaign_count"],
        "deprecated_campaign_keys": True,
        "push_compatibility": push_report["compatibility"],
        "vocabulary": vocabulary_report,
        "git": git,
        "runtime": {
            "name": "claude-code",
            "executable": "claude",
            "found": bool(claude_path),
            "path": claude_path,
            "skill_wiring": wiring,
            "codex_cli": codex,
        },
        "experimental_runtimes": {"codex_cli": codex_runtime},
        "checks": checks,
        "command": {
            "cwd": str(repo_path),
            "argv": ["claude"],
            "display": _display_command(repo_path),
            "follow_up": "/mb-start",
        },
        "launch": launch_report,
        "next_actions": _next_actions(repo_path, checks, handoff_ready, codex),
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
    checkpoint = report.get("checkpoint", {})
    journal = report.get("journal", {})

    console.print(f"\n[bold]mb start[/bold]  {repo['path']}\n")
    alert = format_update_alert(report.get("update", {}))
    if alert:
        console.print(alert)
        console.print()
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
    codex = runtime.get("codex_cli") or {}
    codex_label = codex_mod.human_readiness_label(codex)
    codex_style = "green" if codex_label == "ready" else "yellow"
    console.print(
        "[bold]Codex[/bold]  " + f"[{codex_style}]{codex_label}[/{codex_style}]" + "  owner loop"
    )
    console.print(
        "[bold]Skills[/bold]  /mb-start "
        + ("[green]wired[/green]" if wiring["ok"] else "[red]missing[/red]")
    )
    if isinstance(checkpoint, dict):
        pending = checkpoint.get("pending", {})
        recent = checkpoint.get("recent", [])
        pending_status = pending.get("status") if isinstance(pending, dict) else "unknown"
        recent_label = recent[0]["subject"] if isinstance(recent, list) and recent else "none yet"
        console.print(f"[bold]Checkpoint[/bold]  pending={pending_status}  last={recent_label}")
    if isinstance(journal, dict) and journal.get("events"):
        latest = journal["events"][0]
        console.print(
            f"[bold]Journal[/bold]  {journal.get('summary', {}).get('events', 0)} event(s)  "
            f"last={latest.get('summary')}"
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
