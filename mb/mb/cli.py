"""Typer CLI for ``mb``.

Thin dispatcher. Each subcommand lives in its own module so we can
unit-test in isolation. The shape echoes ``companyctx`` (Typer + sub-apps)
because that's the working pattern.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import typer

from mb import __version__
from mb import doctor as doctor_mod
from mb import educational as educational_mod
from mb import graph as graph_mod
from mb import init as init_mod
from mb import migrate as migrate_mod
from mb import onboard as onboard_mod
from mb import resolve as resolve_mod
from mb import skill_validate as skill_validate_mod
from mb import start as start_mod
from mb import status as status_mod
from mb import think as think_mod
from mb import update as update_mod
from mb import validate as validate_mod
from mb.freshness import format_update_alert, looks_like_business_repo, package_update_status

app = typer.Typer(
    name="mb",
    help=(
        "Run your business as files in git. Main Branch scaffolds your repo, "
        "checks it, graphs it, and wires it into Claude Code."
    ),
    no_args_is_help=False,
    invoke_without_command=True,
    add_completion=False,
)

skill_app = typer.Typer(
    name="skill",
    help="Look at the bundled skills.",
    no_args_is_help=True,
)
app.add_typer(skill_app, name="skill")

migrate_app = typer.Typer(
    name="migrate",
    help="Inspect and apply repo schema migrations.",
    no_args_is_help=False,
    invoke_without_command=True,
)
app.add_typer(migrate_app, name="migrate")


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mb {__version__}")
        raise typer.Exit()


def _is_interactive_terminal() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _render_launch_screen() -> None:
    cwd = Path.cwd().resolve()
    repo = cwd if looks_like_business_repo(cwd) else None
    alert = format_update_alert(package_update_status(repo))
    lines = [""]
    if alert:
        lines.extend([alert, ""])
    lines.extend(
        [
            "Main Branch",
            "Stay connected to the business while agents handle execution.",
            "",
            "Choose a trail:",
            "  New here      mb onboard       guided setup",
            "  Daily work    mb status        business/repo briefing",
            "                mb start         open the agent runtime",
            "  Broken setup  mb doctor        check git, GitHub, Claude Code, and skills",
            "  Power user    mb --help        full command list",
            "",
            "Plain command reference: mb --plain",
            "",
        ]
    )
    typer.echo("\n".join(lines))


@app.callback()
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    plain: bool = typer.Option(
        False,
        "--plain",
        help="Show the plain command reference instead of the launch screen.",
    ),
) -> None:
    """Root callback — version flag and bare launch routing."""
    if ctx.invoked_subcommand is not None:
        return
    if plain or not _is_interactive_terminal():
        typer.echo(ctx.get_help())
        return
    _render_launch_screen()


@app.command("init")
def init_cmd(
    path: str = typer.Argument(".", help="Where to scaffold (default: current dir)."),
    name: str = typer.Option("", "--name", help="Business name (skips prompt if given)."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Set up a fresh business repo (six folders, CLAUDE.md, git init)."""
    result = init_mod.run(path=path, name=name)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        if result["status"] == "already-initialized":
            typer.echo(f"already set up at {result['path']} — nothing to do.")
        elif result["status"] == "ok":
            typer.echo(f"set up {result['business_name']}.")
            typer.echo("")
            for line in result["created"]:
                typer.echo(f"  + {line}")
            typer.echo("")
            typer.echo("next:")
            typer.echo(f"  cd {result['path']}")
            typer.echo("  claude")
            typer.echo("  /start")
        else:
            typer.echo(f"could not set up: {result.get('error')}", err=True)
            raise typer.Exit(1)


def _onboard_target_path(path_arg: str, path_opt: str, name: str) -> str:
    explicit = path_opt.strip() or path_arg.strip()
    if explicit:
        return explicit
    return onboard_mod._slug(name) if name.strip() else "."


def _render_onboard_intro(level: str) -> None:
    if level == "power":
        typer.echo("Main Branch keeps the business in local files, git history, and GitHub work.")
        return
    typer.echo("")
    typer.echo("Main Branch works because the business lives somewhere durable:")
    typer.echo("  local files  - readable, portable business memory")
    typer.echo("  git          - the evolution story and rollback layer")
    typer.echo("  GitHub       - tasks, proposals, reviews, and shipped history")
    typer.echo("  Claude Code  - the first execution runtime for judgment-heavy work")


def _render_onboard_human(result: dict[str, Any]) -> None:
    from rich.console import Console

    console = Console()
    mark = "[green]ready[/green]" if result["ok"] else "[red]needs repair[/red]"
    console.print(f"\n[bold]mb onboard[/bold]  {mark}")
    console.print(f"repo: {result['path']}")
    console.print(f"level / action: {result['level']} / {result['action']}\n")

    if result["level"] != "power":
        console.print("[bold]Why this stack[/bold]")
        console.print("  Local files are the business brain.")
        console.print("  Git remembers how the business changed.")
        console.print("  GitHub turns tasks and proposals into a team surface.")
        console.print("  Claude Code is the first runtime that can act on the repo.\n")

    tools = result["tools"]
    skill_wiring = result["skill_wiring"]
    git = tools["git"]
    github = tools["github_cli"]
    claude = tools["claude_code"]
    console.print("[bold]Checks[/bold]")
    console.print(f"  {'ok' if git['found'] else 'warn'}  git")
    github_state = "ok" if github["found"] and github["authenticated"] else "warn"
    console.print(f"  {github_state}  GitHub CLI")
    console.print(f"  {'ok' if claude['found'] else 'warn'}  Claude Code")
    console.print(f"  {'ok' if skill_wiring['ok'] else 'fail'}  Claude Code skill discovery")

    warnings = result["warnings"]
    errors = result["errors"]
    if warnings:
        console.print("\n[yellow]Repair notes[/yellow]")
        for warning in warnings:
            console.print(f"  - {warning}")
    if errors:
        console.print("\n[red]Could not finish setup[/red]")
        for error in errors:
            console.print(f"  - {error}")
        console.print(f"\nRun `{result['doctor_command']}` for repair steps.")
        return

    console.print("\n[bold]Next[/bold]")
    for step in result["next_steps"]:
        console.print(f"  {step}")
    if warnings:
        console.print(f"\nFor a full setup check, run `{result['doctor_command']}`.")
    console.print()


@app.command("onboard")
def onboard_cmd(
    path_arg: str = typer.Argument("", help="Repo path to create or connect."),
    path_opt: str = typer.Option("", "--path", help="Repo path to create or connect."),
    name: str = typer.Option("", "--name", help="Business name."),
    mode: str = typer.Option(
        "auto",
        "--mode",
        help="Setup mode: auto, new, or connect.",
    ),
    level: str = typer.Option(
        "auto",
        "--level",
        help="Experience level: auto, beginner, intermediate, or power.",
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Use defaults and never prompt."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Guide a human through first setup or reconnect an existing repo."""
    interactive = onboard_mod.is_interactive()
    if not yes and not interactive:
        typer.echo(
            "mb onboard needs a terminal prompt. Use `mb onboard --yes` for scripts.", err=True
        )
        raise typer.Exit(2)

    selected_level = level
    selected_mode = mode
    target = _onboard_target_path(path_arg, path_opt, name)
    business_name = name

    if not yes:
        typer.echo("Main Branch setup")
        selected_level = typer.prompt(
            "Comfort level (beginner/intermediate/power)",
            default="beginner" if level == "auto" else level,
        )
        if selected_level != "power":
            _render_onboard_intro(selected_level)
        selected_mode = typer.prompt(
            "Create a new repo, connect an existing one, or auto-detect? (new/connect/auto)",
            default="auto" if mode == "auto" else mode,
        )
        if not business_name and selected_mode != "connect":
            business_name = typer.prompt("Business name")
        default_path = target
        if target == "." and business_name:
            default_path = onboard_mod._slug(business_name)
        target = typer.prompt("Repo path", default=default_path)

    try:
        result = onboard_mod.run(
            path=target,
            name=business_name,
            mode=selected_mode,
            level=selected_level,
        )
    except ValueError as exc:
        typer.echo(f"mb onboard: {exc}", err=True)
        raise typer.Exit(2) from exc
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        _render_onboard_human(result)
    raise typer.Exit(0 if result["ok"] else 1)


@app.command("doctor")
def doctor_cmd(
    path: str = typer.Argument(".", help="Repo to diagnose."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Check the health of a Main Branch repo. Exits 1 on red checks."""
    report = doctor_mod.run(path=path)
    if json_out:
        typer.echo(json.dumps(report, indent=2))
    else:
        doctor_mod.render_human(report)
    raise typer.Exit(0 if report["ok"] else 1)


@app.command("status")
def status_cmd(
    path: str = typer.Argument(".", help="Business repo to brief."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Show a cheap daily briefing for a Main Branch repo."""
    report = status_mod.run(path=path)
    if json_out:
        typer.echo(json.dumps(report, indent=2))
    else:
        status_mod.render_human(report)


@app.command("start")
def start_cmd(
    repo: str = typer.Option(
        ".",
        "--repo",
        help="Business repo to hand off to the configured runtime.",
    ),
    launch: bool = typer.Option(
        False,
        "--launch",
        help="Launch Claude Code after readiness checks pass. Cannot be combined with --json.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Check runtime handoff readiness and print or launch the Claude Code command."""
    if json_out and launch:
        report = start_mod.run(repo=repo, launch=False)
        message = "`--json` cannot be combined with `--launch`; run without `--json` to launch."
        report["ok"] = False
        report["errors"] = [message]
        report["launch"]["requested"] = True
        report["launch"]["safe"] = False
        report["launch"]["attempted"] = False
        report["launch"]["blocked_reason"] = message
        typer.echo(json.dumps(report, indent=2))
        raise typer.Exit(2)

    report = start_mod.run(repo=repo, launch=launch)
    if json_out:
        typer.echo(json.dumps(report, indent=2))
    else:
        start_mod.render_human(report)
    raise typer.Exit(0 if report["ok"] else 1)


@app.command("validate")
def validate_cmd(
    path: str = typer.Argument(".", help="Repo to validate."),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    cross_refs: bool = typer.Option(
        False,
        "--cross-refs",
        help="Check known frontmatter links and offer directory references.",
    ),
    strict: bool = typer.Option(False, "--strict", help="Fail on warnings."),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Check frontmatter shape and optional cross-references."""
    report = validate_mod.run(
        path=path,
        verbose=verbose,
        cross_refs=cross_refs,
        strict=strict,
    )
    if json_out:
        typer.echo(json.dumps(report, indent=2))
    else:
        validate_mod.render_human(report, verbose=verbose)
    raise typer.Exit(0 if report["ok"] else 1)


@app.command("graph")
def graph_cmd(
    path: str = typer.Argument(".", help="Repo to graph."),
    open_after: bool = typer.Option(False, "--open", help="Render to PNG and open."),
) -> None:
    """Walk linked_research / linked_decisions / supersedes; emit Graphviz DOT."""
    dot = graph_mod.build_dot(path=path)
    if open_after:
        graph_mod.open_dot(dot)
    else:
        typer.echo(dot)


@app.command("think")
def think_cmd(
    topic: str = typer.Argument(..., help="Topic to think about."),
) -> None:
    """Print the /think invocation hint (run inside Claude Code for full flow)."""
    think_mod.run(topic=topic)


@app.command("resolve")
def resolve_cmd(
    key: str = typer.Argument(..., help="Reference key (e.g. 'voice')."),
    repo: str = typer.Option(".", "--repo"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Resolve a reference path (checks free first, then paid)."""
    result = resolve_mod.run(key=key, repo=repo)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        if result["resolved"]:
            typer.echo(result["path"])
            if result.get("is_stub"):
                typer.echo(
                    f"# stub — for the curated {key}, subscribe at mainbranch.io/run",
                    err=True,
                )
        else:
            typer.echo(f"unresolved: {key}", err=True)
            raise typer.Exit(1)


@app.command("educational")
def educational_cmd(
    topic: str = typer.Argument(..., help="Educational topic slug."),
) -> None:
    """Print an educational triage file. Powers doctor's 'tell me more' prompts."""
    educational_mod.run(topic=topic)


@app.command("update")
def update_cmd(
    repo: str = typer.Option(".", "--repo", help="Business repo whose skill links refresh."),
    check: bool = typer.Option(False, "--check", help="Dry-run only; do not upgrade or relink."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Refresh Main Branch according to its install mode."""
    result = update_mod.run(repo=repo, check=check)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        update_mod.render_human(result)
    raise typer.Exit(0 if result["ok"] else 1)


@migrate_app.callback()
def migrate_cmd(
    ctx: typer.Context,
    repo: str = typer.Option(".", "--repo", help="Business repo to migrate."),
    check: bool = typer.Option(False, "--check", help="Dry-run pending migrations."),
    apply_changes: bool = typer.Option(False, "--apply", help="Apply pending migrations."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Run `mb migrate --check` or `mb migrate --apply`; defaults to status."""
    if ctx.invoked_subcommand is not None:
        return
    if check and apply_changes:
        typer.echo("mb migrate: choose only one of --check or --apply", err=True)
        raise typer.Exit(2)
    if apply_changes:
        result = migrate_mod.apply(repo)
        if json_out:
            typer.echo(json.dumps(result, indent=2))
        else:
            migrate_mod.render_apply(result)
        raise typer.Exit(0 if result["ok"] else 1)
    if check:
        result = migrate_mod.check(repo)
        if json_out:
            typer.echo(json.dumps(result, indent=2))
        else:
            migrate_mod.render_check(result)
        pending = bool(result.get("pending"))
        raise typer.Exit(1 if pending or not result["ok"] else 0)

    result = migrate_mod.status(repo)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        migrate_mod.render_status(result)


@migrate_app.command("status")
def migrate_status_cmd(
    repo: str = typer.Option(".", "--repo", help="Business repo to inspect."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Show current schema version and pending migrations."""
    result = migrate_mod.status(repo)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        migrate_mod.render_status(result)


@skill_app.command("path")
def skill_path_cmd(
    name: str = typer.Argument(..., help="Skill name (e.g. 'site')."),
) -> None:
    """Print the on-disk path to a bundled skill."""
    from mb.resolve import skill_path

    result = skill_path(name)
    if result is None:
        typer.echo(f"skill not found: {name}", err=True)
        raise typer.Exit(1)
    typer.echo(str(result))


@skill_app.command("list")
def skill_list_cmd() -> None:
    """List bundled skills."""
    from mb.resolve import bundled_skills

    for s in bundled_skills():
        typer.echo(s)


@skill_app.command("validate")
def skill_validate_cmd(
    name: str | None = typer.Argument(None, help="Skill name (e.g. 'site')."),
    all_skills: bool = typer.Option(False, "--all", help="Validate every bundled skill."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Validate bundled skill frontmatter and local references."""
    if all_skills and name is not None:
        payload = {
            "ok": False,
            "command": "mb skill validate",
            "mode": "invalid",
            "skills": [],
            "summary": {"skills": 0, "passed": 0, "failed": 0, "errors": 1, "warnings": 0},
            "errors": ["choose either a skill name or --all, not both"],
        }
        if json_out:
            typer.echo(json.dumps(payload, indent=2))
        else:
            typer.echo("mb skill validate: choose either a skill name or --all", err=True)
        raise typer.Exit(2)
    if not all_skills and name is None:
        payload = {
            "ok": False,
            "command": "mb skill validate",
            "mode": "invalid",
            "skills": [],
            "summary": {"skills": 0, "passed": 0, "failed": 0, "errors": 1, "warnings": 0},
            "errors": ["provide a skill name or --all"],
        }
        if json_out:
            typer.echo(json.dumps(payload, indent=2))
        else:
            typer.echo("mb skill validate: provide a skill name or --all", err=True)
        raise typer.Exit(2)

    if all_skills:
        report = skill_validate_mod.run_all()
    else:
        assert name is not None
        skill_report = skill_validate_mod.run(name)
        if skill_report is None:
            payload = {
                "ok": False,
                "command": "mb skill validate",
                "mode": "single",
                "skills": [],
                "summary": {
                    "skills": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 1,
                    "warnings": 0,
                },
                "errors": [f"skill not found: {name}"],
            }
            if json_out:
                typer.echo(json.dumps(payload, indent=2))
            else:
                typer.echo(f"skill not found: {name}", err=True)
            raise typer.Exit(2)
        report = skill_validate_mod.envelope([skill_report], mode="single")

    if json_out:
        typer.echo(json.dumps(report, indent=2))
    else:
        skill_validate_mod.render_human(report)
    raise typer.Exit(0 if report["ok"] else 1)


@skill_app.command("link")
def skill_link_cmd(
    repo: str = typer.Option(".", "--repo", help="Business repo to wire for Claude Code."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Wire bundled skills into a business repo for Claude Code discovery."""
    from mb.engine import link_skills

    result = link_skills(repo)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        if result["ok"]:
            typer.echo(f"linked Main Branch: {result['engine_root']}")
            typer.echo(f"repo: {result['repo']}")
            if result["linked"]:
                typer.echo(f"  + linked {len(result['linked'])} skill(s)")
            if result["copied"]:
                typer.echo(f"  + copied {len(result['copied'])} skill(s)")
            if result["skipped"]:
                typer.echo(f"  · {len(result['skipped'])} already wired")
            typer.echo("")
            typer.echo("you're set — run `claude` and then /start.")
        else:
            typer.echo("could not link Main Branch skills:", err=True)
            for error in result["errors"]:
                typer.echo(f"  - {error}", err=True)
            raise typer.Exit(1)


def _entry() -> None:
    """Defensive entrypoint used by ``python -m mb`` and tests."""
    try:
        app()
    except typer.Exit:
        raise
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"mb: error: {exc}", err=True)
        sys.exit(2)
