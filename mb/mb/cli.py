"""Typer CLI for ``mb``.

Thin dispatcher. Each subcommand lives in its own module so we can
unit-test in isolation. The shape echoes ``companyctx`` (Typer + sub-apps)
because that's the working pattern.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NoReturn

import typer

from mb import __version__
from mb import ads as ads_mod
from mb import books as books_mod
from mb import checkpoint as checkpoint_mod
from mb import connect as connect_mod
from mb import doctor as doctor_mod
from mb import educational as educational_mod
from mb import graph as graph_mod
from mb import image_rail as image_rail_mod
from mb import init as init_mod
from mb import issue as issue_mod
from mb import migrate as migrate_mod
from mb import onboard as onboard_mod
from mb import resolve as resolve_mod
from mb import similar_bets as similar_bets_mod
from mb import site as site_mod
from mb import skill_validate as skill_validate_mod
from mb import start as start_mod
from mb import status as status_mod
from mb import suggest as suggest_mod
from mb import think as think_mod
from mb import update as update_mod
from mb import validate as validate_mod
from mb.freshness import format_update_alert, looks_like_business_repo, package_update_status
from mb.json_result import envelope

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

onboard_app = typer.Typer(
    name="onboard",
    help="Create, connect, and resume business repo onboarding.",
    no_args_is_help=False,
    invoke_without_command=True,
)
app.add_typer(onboard_app, name="onboard")

issue_app = typer.Typer(
    name="issue",
    help="Draft and open privacy-safe GitHub issues.",
    no_args_is_help=True,
)
app.add_typer(issue_app, name="issue")

site_app = typer.Typer(
    name="site",
    help="Inspect site readiness for launch-adjacent workflows.",
    no_args_is_help=True,
)
app.add_typer(site_app, name="site")

books_app = typer.Typer(
    name="books",
    help="Check bookkeeping safety and the private books vault contract.",
    no_args_is_help=True,
)
app.add_typer(books_app, name="books")

books_report_app = typer.Typer(
    name="report",
    help="Generate privacy-bounded bookkeeping reports.",
    no_args_is_help=True,
)
books_app.add_typer(books_report_app, name="report")

ads_app = typer.Typer(
    name="ads",
    help="Read paid-channel account summaries.",
    no_args_is_help=True,
)
app.add_typer(ads_app, name="ads")

ads_meta_app = typer.Typer(
    name="meta",
    help="Read privacy-bounded Meta Ads account summaries.",
    no_args_is_help=True,
)
ads_app.add_typer(ads_meta_app, name="meta")

image_app = typer.Typer(
    name="image",
    help="Smoke fixture-safe creative image rails.",
    no_args_is_help=True,
)
app.add_typer(image_app, name="image")

suggest_app = typer.Typer(
    name="suggest",
    help="Suggest read-only business repo improvements.",
    no_args_is_help=True,
)
app.add_typer(suggest_app, name="suggest")

CONNECT_METADATA_OPTION = typer.Option(
    [],
    "--metadata",
    "-m",
    help="Non-sensitive provider metadata as key=value. Repeat as needed.",
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mb {__version__}")
        raise typer.Exit()


def _json_payload(payload: dict[str, Any], *, command: str, schema_name: str) -> str:
    return json.dumps(envelope(payload, command=command, schema_name=schema_name), indent=2)


def _is_interactive_terminal() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _connect_boundary_exit(command: str, exc: ValueError) -> NoReturn:
    typer.echo(f"{command}: {exc}", err=True)
    raise typer.Exit(2) from exc


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
            "  Daily work    mb start         check handoff / open Claude Code",
            "  Briefing      mb status        terminal-only status facts",
            "  Broken setup  mb doctor        check git, GitHub, Claude Code, and skills",
            "  Power user    mb --help        full command list",
            "",
            "Plain command reference: mb --plain",
            "",
        ]
    )
    typer.echo("\n".join(lines))


def _today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


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
    """Set up a fresh business repo (business folders, CLAUDE.md, git init)."""
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
            typer.echo("  /mb-start")
            typer.echo("")
            typer.echo("connected accounts:")
            typer.echo(
                "  See CLAUDE.md -> Connected accounts before wiring tools that "
                "spend, publish, or mutate customer accounts."
            )
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
    checkpoint_hook = result.get("checkpoint_hook") or {}
    git = tools["git"]
    github = tools["github_cli"]
    claude = tools["claude_code"]
    console.print("[bold]Checks[/bold]")
    console.print(f"  {'ok' if git['found'] else 'warn'}  git")
    github_state = "ok" if github["found"] and github["authenticated"] else "warn"
    console.print(f"  {github_state}  GitHub CLI")
    console.print(f"  {'ok' if claude['found'] else 'warn'}  Claude Code")
    console.print(f"  {'ok' if skill_wiring['ok'] else 'fail'}  Claude Code skill discovery")
    if checkpoint_hook:
        console.print(f"  {'ok' if checkpoint_hook.get('ok') else 'warn'}  checkpoint save hook")

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
    console.print(
        "\n[bold]Connected accounts[/bold]\n"
        "  See CLAUDE.md -> Connected accounts before wiring tools that spend, "
        "publish, or mutate customer accounts."
    )
    if warnings:
        console.print(f"\nFor a full setup check, run `{result['doctor_command']}`.")
    console.print()


@onboard_app.callback()
def onboard_cmd(
    ctx: typer.Context,
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
    team_size: str = typer.Option(
        "unknown",
        "--team-size",
        help="Onboarding persona: solo, small-team, larger-team, or unknown.",
    ),
    business_type: str = typer.Option(
        "",
        "--business-type",
        help="Short business category for onboarding progress.",
    ),
    success_stage: str = typer.Option(
        "unknown",
        "--success-stage",
        help="Current success stage: prelaunch, working, successful, scaling, or unknown.",
    ),
    desired_outcome: str = typer.Option(
        "",
        "--desired-outcome",
        help="Short target outcome for onboarding progress.",
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Use defaults and never prompt."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Guide a human through first setup or reconnect an existing repo."""
    if ctx.invoked_subcommand is not None:
        return
    interactive = onboard_mod.is_interactive()
    if not yes and not interactive:
        typer.echo(
            "mb onboard needs a terminal prompt. Use `mb onboard --yes` for scripts.", err=True
        )
        raise typer.Exit(2)

    selected_level = level
    selected_mode = mode
    target = _onboard_target_path("", path_opt, name)
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
            team_size=team_size,
            business_type=business_type,
            success_stage=success_stage,
            desired_outcome=desired_outcome,
        )
    except ValueError as exc:
        typer.echo(f"mb onboard: {exc}", err=True)
        raise typer.Exit(2) from exc
    if json_out:
        typer.echo(
            _json_payload(result, command="mb onboard", schema_name="mainbranch.onboard.result")
        )
    else:
        _render_onboard_human(result)
    raise typer.Exit(0 if result["ok"] else 1)


def _render_onboard_status_human(result: dict[str, Any]) -> None:
    from rich.console import Console

    console = Console()
    summary = result["summary"]
    console.print(f"\n[bold]mb onboard status[/bold]  {result['repo']}")
    console.print(
        f"{summary['status'].replace('_', ' ')}  "
        f"{summary['completed_required']}/{summary['total_required']} required steps complete"
    )
    if not result["state_exists"]:
        console.print("[yellow]No saved onboarding plan yet.[/yellow] Run `mb onboard plan`.")
    profile = result["profile"]
    console.print(
        "\n[bold]Profile[/bold] "
        f"team: {profile.get('team_size', 'unknown')}  "
        f"type: {profile.get('business_type') or 'unknown'}  "
        f"stage: {profile.get('success_stage', 'unknown')}"
    )
    console.print("\n[bold]Checklist[/bold]")
    for step in result["checklist"]:
        mark = "ok" if step["status"] == "complete" else "todo"
        missing = ", ".join(step["missing_inputs"])
        suffix = f" ({missing})" if missing else ""
        console.print(f"  {mark:<4} {step['title']}{suffix}")
    console.print("\n[bold]Next[/bold]")
    console.print(f"  {summary['next_recommended_action']}")
    console.print()


@onboard_app.command("status")
def onboard_status_cmd(
    repo: str = typer.Option(".", "--repo", help="Business repo to inspect."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Show saved onboarding progress and inferred missing core inputs."""
    result = onboard_mod.onboarding_status(repo)
    if json_out:
        typer.echo(
            _json_payload(
                result,
                command="mb onboard status",
                schema_name="mainbranch.onboard.status.result",
            )
        )
    else:
        _render_onboard_status_human(result)
    raise typer.Exit(0 if result["ok"] else 1)


@onboard_app.command("plan")
def onboard_plan_cmd(
    repo: str = typer.Option(".", "--repo", help="Business repo whose plan is updated."),
    name: str = typer.Option("", "--name", help="Business name."),
    team_size: str = typer.Option(
        "unknown",
        "--team-size",
        help="Onboarding persona: solo, small-team, larger-team, or unknown.",
    ),
    business_type: str = typer.Option("", "--business-type", help="Short business category."),
    success_stage: str = typer.Option(
        "unknown",
        "--success-stage",
        help="Current success stage: prelaunch, working, successful, scaling, or unknown.",
    ),
    desired_outcome: str = typer.Option("", "--desired-outcome", help="Short target outcome."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Create or update the lightweight onboarding progress plan."""
    try:
        result = onboard_mod.write_plan(
            repo,
            business_name=name,
            team_size=team_size,
            business_type=business_type,
            success_stage=success_stage,
            desired_outcome=desired_outcome,
        )
    except ValueError as exc:
        typer.echo(f"mb onboard plan: {exc}", err=True)
        raise typer.Exit(2) from exc
    if json_out:
        typer.echo(
            _json_payload(
                result,
                command="mb onboard plan",
                schema_name="mainbranch.onboard.plan.result",
            )
        )
    else:
        _render_onboard_status_human(result)
    raise typer.Exit(0 if result["ok"] else 1)


def _doctor_repair_from_args(args: list[str], *, json_out: bool) -> None:
    repo = "."
    plan = False
    apply_changes = False
    include_migration = False
    local_json = json_out
    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg == "--help":
            typer.echo(
                "Usage: mb doctor repair [--repo PATH] [--plan | --apply] "
                "[--include-migration] [--json]"
            )
            typer.echo("")
            typer.echo("Plan or apply guided business-repo reconciliation repairs.")
            typer.echo("")
            typer.echo(
                "Migration apply is opt-in: use `--include-migration` only with `--apply` "
                "after reviewing the plan."
            )
            raise typer.Exit(0)
        if arg == "--repo":
            idx += 1
            if idx >= len(args):
                typer.echo("mb doctor repair: --repo requires a path", err=True)
                raise typer.Exit(2)
            repo = args[idx]
        elif arg == "--plan":
            plan = True
        elif arg == "--apply":
            apply_changes = True
        elif arg == "--include-migration":
            include_migration = True
        elif arg == "--json":
            local_json = True
        else:
            typer.echo(f"mb doctor repair: unknown option {arg}", err=True)
            raise typer.Exit(2)
        idx += 1

    if plan and apply_changes:
        typer.echo("mb doctor repair: choose only one of --plan or --apply", err=True)
        raise typer.Exit(2)
    if include_migration and not apply_changes:
        typer.echo(
            "mb doctor repair: --include-migration requires --apply. "
            "First run `mb doctor repair --plan`; after review, rerun "
            "`mb doctor repair --apply --include-migration`.",
            err=True,
        )
        raise typer.Exit(2)

    if apply_changes:
        report = doctor_mod.repair_apply(repo=repo, include_migration=include_migration)
    else:
        report = doctor_mod.repair_plan(repo=repo)

    if local_json:
        typer.echo(
            _json_payload(
                report,
                command="mb doctor repair",
                schema_name="mainbranch.doctor.repair.result",
            )
        )
    else:
        doctor_mod.render_repair(report)
    raise typer.Exit(0 if report["ok"] else 1)


def _doctor_help() -> None:
    typer.echo("Usage: mb doctor [OPTIONS] [PATH]")
    typer.echo("")
    typer.echo("Check the health of a Main Branch repo. Exits 1 on red checks.")
    typer.echo("")
    typer.echo("Options:")
    typer.echo("  --json   Machine-readable output.")
    typer.echo("  --help   Show this message and exit.")
    typer.echo("")
    typer.echo("Repair:")
    typer.echo("  mb doctor repair [--repo PATH] [--plan | --apply] [--include-migration] [--json]")
    typer.echo("  Note: --include-migration is valid only with --apply after plan review.")


@app.command(
    "doctor",
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
        "help_option_names": [],
    },
)
def doctor_cmd(
    ctx: typer.Context,
    path: str = typer.Argument(".", help="Repo to diagnose."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Check the health of a Main Branch repo. Exits 1 on red checks."""
    if path == "--help":
        _doctor_help()
        raise typer.Exit(0)
    if path == "repair":
        _doctor_repair_from_args(list(ctx.args), json_out=json_out)
        return
    if path.startswith("-"):
        typer.echo(f"mb doctor: unknown option {path}", err=True)
        raise typer.Exit(2)
    if ctx.args:
        typer.echo(f"mb doctor: unknown option(s): {' '.join(ctx.args)}", err=True)
        raise typer.Exit(2)
    report = doctor_mod.run(path=path)
    if json_out:
        typer.echo(
            _json_payload(report, command="mb doctor", schema_name="mainbranch.doctor.result")
        )
    else:
        doctor_mod.render_human(report)
        if not report["ok"]:
            typer.echo(
                "\nIf this should become a public task, run "
                "`mb issue draft bug --command 'mb doctor' --what-happened '<summary>'` "
                "after removing private details."
            )
    raise typer.Exit(0 if report["ok"] else 1)


@issue_app.command("draft")
def issue_draft_cmd(
    kind: str = typer.Argument("bug", help="Issue shape: bug, feature, or question."),
    repo: str = typer.Option(".", "--repo", help="Business repo where the draft is stored."),
    title: str = typer.Option("", "--title", help="Issue title. Prefix is added by template."),
    command: str = typer.Option("", "--command", help="Command or skill that failed."),
    what_happened: str = typer.Option(
        "",
        "--what-happened",
        "--happened",
        help="Actual behavior or error output.",
    ),
    expected: str = typer.Option("", "--expected", help="Expected behavior."),
    diagnostics: str = typer.Option("", "--diagnostics", help="Extra diagnostic text to scrub."),
    diagnostics_file: str = typer.Option(
        "",
        "--diagnostics-file",
        help="Read extra diagnostics from a local file, then scrub them.",
    ),
    problem: str = typer.Option("", "--problem", help="Feature request problem statement."),
    surface: str = typer.Option(
        "Other / not sure",
        "--surface",
        help="Feature surface: CLI subcommand, Skill, Both, or Other / not sure.",
    ),
    proposal: str = typer.Option("", "--proposal", help="Feature request proposal."),
    alternatives: str = typer.Option("", "--alternatives", help="Alternatives considered."),
    related: str = typer.Option("", "--related", help="Related issues or PRs."),
    question: str = typer.Option("", "--question", help="Question to ask."),
    context: str = typer.Option("", "--context", help="Context for a question."),
    tried: str = typer.Option("", "--tried", help="What you have tried."),
    include_doctor: bool = typer.Option(
        True,
        "--doctor/--no-doctor",
        help="For bug drafts, include scrubbed `mb doctor --json` output.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Create a local, scrubbed issue draft under .mb/issue-drafts/."""
    diagnostics_text = diagnostics
    if diagnostics_file:
        try:
            diagnostics_text = Path(diagnostics_file).read_text(encoding="utf-8")
        except OSError as exc:
            typer.echo(f"mb issue draft: could not read diagnostics file: {exc}", err=True)
            raise typer.Exit(2) from exc
    fields = {
        "command": command,
        "happened": what_happened,
        "expected": expected,
        "diagnostics": diagnostics_text,
        "problem": problem,
        "surface": surface,
        "proposal": proposal,
        "alternatives": alternatives,
        "related": related,
        "question": question,
        "context": context,
        "tried": tried,
    }
    try:
        result = issue_mod.create_draft(
            repo=repo,
            kind=kind,
            title=title,
            fields=fields,
            include_doctor=include_doctor,
        )
    except ValueError as exc:
        typer.echo(f"mb issue draft: {exc}", err=True)
        raise typer.Exit(2) from exc
    if json_out:
        typer.echo(
            _json_payload(
                result,
                command="mb issue draft",
                schema_name="mainbranch.issue.draft.result",
            )
        )
    else:
        typer.echo(f"drafted {result['kind']} issue: {result['relative_path']}")
        typer.echo("review it before submitting; drafts are local and gitignored by default.")
        if result["redactions"]:
            summary = ", ".join(f"{key}={value}" for key, value in result["redactions"].items())
            typer.echo(f"redactions: {summary}")
        typer.echo("next:")
        typer.echo(f"  {result['next_command']} --yes")


@issue_app.command("open")
def issue_open_cmd(
    draft: str = typer.Argument(..., help="Draft markdown file from `mb issue draft`."),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Submit with gh after you have reviewed the draft.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Open a reviewed issue draft through gh, or print a manual fallback."""
    try:
        result = issue_mod.open_draft(draft, yes=yes)
    except ValueError as exc:
        typer.echo(f"mb issue open: {exc}", err=True)
        raise typer.Exit(2) from exc
    if json_out:
        typer.echo(
            _json_payload(
                result,
                command="mb issue open",
                schema_name="mainbranch.issue.open.result",
            )
        )
    elif result.get("submitted"):
        typer.echo(f"opened issue: {result['url']}")
    else:
        typer.echo("issue not submitted.")
        typer.echo(result["reason"])
        typer.echo("manual fallback:")
        for step in result["manual_steps"]:
            typer.echo(f"  - {step}")
    raise typer.Exit(0 if result["ok"] else 1)


@app.command("connect")
def connect_cmd(
    target: str = typer.Argument(
        "",
        help="Provider to connect, or `list` / `plan` / `status` / `doctor` / `test`.",
    ),
    provider: str = typer.Argument(
        "",
        help="Provider for subcommands such as `mb connect test <provider>`.",
    ),
    repo: str = typer.Option(".", "--repo", help="Business repo whose metadata is updated."),
    account_label: str = typer.Option("", "--account", "--label", help="Human account label."),
    token: str = typer.Option(
        "",
        "--token",
        help="Secret token or key. Prefer --token-stdin for real credentials.",
    ),
    token_stdin: bool = typer.Option(
        False,
        "--token-stdin",
        help="Read the secret token or key from stdin.",
    ),
    from_env: bool = typer.Option(
        False,
        "--from-env",
        help="Read the provider credential from a known environment variable.",
    ),
    metadata: list[str] = CONNECT_METADATA_OPTION,
    all_providers: bool = typer.Option(
        False,
        "--all",
        help="With `mb connect status`, include providers not connected yet.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Connect provider credentials without committing secrets."""
    if not target:
        try:
            result = connect_mod.list_providers(repo)
        except connect_mod.ConfigBoundaryError as exc:
            _connect_boundary_exit("mb connect", exc)
        if json_out:
            typer.echo(json.dumps(result, indent=2))
        else:
            connect_mod.render_list(result)
        raise typer.Exit(0)
    if target == "list":
        try:
            result = connect_mod.list_providers(repo)
        except connect_mod.ConfigBoundaryError as exc:
            _connect_boundary_exit("mb connect list", exc)
        if json_out:
            typer.echo(json.dumps(result, indent=2))
        else:
            connect_mod.render_list(result)
        raise typer.Exit(0)
    if target == "plan":
        try:
            result = connect_mod.provider_plan(repo)
        except connect_mod.ConfigBoundaryError as exc:
            _connect_boundary_exit("mb connect plan", exc)
        if json_out:
            typer.echo(json.dumps(result, indent=2))
        else:
            connect_mod.render_plan(result)
        raise typer.Exit(0)
    if target == "status":
        try:
            result = connect_mod.status_all(repo, include_all=all_providers)
        except connect_mod.ConfigBoundaryError as exc:
            _connect_boundary_exit("mb connect status", exc)
        if json_out:
            typer.echo(json.dumps(result, indent=2))
        else:
            connect_mod.render_status(result)
        raise typer.Exit(0 if result["ok"] else 1)
    if target == "doctor":
        try:
            result = connect_mod.doctor(repo)
        except connect_mod.ConfigBoundaryError as exc:
            _connect_boundary_exit("mb connect doctor", exc)
        if json_out:
            typer.echo(json.dumps(result, indent=2))
        else:
            connect_mod.render_doctor(result)
        raise typer.Exit(0 if result["ok"] else 1)
    if target == "test":
        if not provider:
            typer.echo("mb connect test: provider required", err=True)
            raise typer.Exit(2)
        try:
            result = connect_mod.test_provider(provider, repo)
        except ValueError as exc:
            typer.echo(f"mb connect test: {exc}", err=True)
            raise typer.Exit(2) from exc
        if json_out:
            typer.echo(json.dumps(result, indent=2))
        else:
            connect_mod.render_test_result(result)
        raise typer.Exit(0 if result["ok"] else 1)
    if provider:
        typer.echo(f"mb connect: unexpected extra argument {provider!r}", err=True)
        raise typer.Exit(2)

    try:
        provider_info = connect_mod.normalize_provider(target)
    except ValueError as exc:
        typer.echo(f"mb connect: {exc}", err=True)
        raise typer.Exit(2) from exc

    secret_value = token
    if token_stdin:
        secret_value = connect_mod.read_stdin_token()
    credential_source = "prompt" if not secret_value else "token"
    consumed_env_var = ""
    if token_stdin:
        credential_source = "stdin"
    if from_env and not secret_value and provider_info.required_secrets:
        for env_var in provider_info.env_vars:
            value = os.environ.get(env_var, "").strip()
            if value:
                secret_value = value
                credential_source = "env"
                consumed_env_var = env_var
                break
        if not secret_value:
            names = ", ".join(provider_info.env_vars) or "(none registered)"
            typer.echo(f"mb connect: no credential found in env vars: {names}", err=True)
            raise typer.Exit(1)
    if not secret_value and provider_info.required_secrets and sys.stdin.isatty():
        secret_value = typer.prompt(
            f"{provider_info.name} {provider_info.required_secrets[0]}",
            hide_input=True,
            default="",
            show_default=False,
        )

    try:
        result = connect_mod.connect_provider(
            provider_info.id,
            repo=repo,
            token=secret_value,
            account_label=account_label,
            metadata_pairs=metadata,
        )
        result["credential_source"] = {
            "type": credential_source if secret_value else "missing",
            "env_var": consumed_env_var,
        }
    except ValueError as exc:
        typer.echo(f"mb connect: {exc}", err=True)
        raise typer.Exit(2) from exc
    except RuntimeError as exc:
        typer.echo(f"mb connect: {exc}", err=True)
        raise typer.Exit(1) from exc
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        connect_mod.render_connect_result(result)
    raise typer.Exit(0 if result["ok"] else 1)


@app.command("status")
def status_cmd(
    path: str = typer.Argument(".", help="Business repo to brief."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed briefing sections."),
    no_color: bool = typer.Option(False, "--no-color", help="Disable ANSI color in human output."),
    peek: bool = typer.Option(
        False,
        "--peek",
        help="Read status without updating the last-status-seen marker.",
    ),
) -> None:
    """Show a cheap daily briefing for a Main Branch repo."""
    report = status_mod.run(path=path, update_marker=not peek, validation_cross_refs=not peek)
    if json_out:
        typer.echo(_json_payload(report, command="mb status", schema_name="mainbranch.status"))
    else:
        status_mod.render_human(report, verbose=verbose, no_color=no_color)


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
        typer.echo(_json_payload(report, command="mb start", schema_name="mainbranch.start.result"))
        raise typer.Exit(2)

    report = start_mod.run(repo=repo, launch=launch)
    if json_out:
        typer.echo(_json_payload(report, command="mb start", schema_name="mainbranch.start.result"))
    else:
        start_mod.render_human(report)
    raise typer.Exit(0 if report["ok"] else 1)


@books_app.command("check")
def books_check_cmd(
    repo: str = typer.Argument(".", help="Business repo to check."),
    validate_fixture: bool = typer.Option(
        False,
        "--fixture/--no-fixture",
        help=(
            "Validate a fake hledger journal fixture. Uses the bundled "
            "sample unless --fixture-path is given."
        ),
    ),
    fixture_path: str = typer.Option(
        "",
        "--fixture-path",
        help="Path to a fake hledger journal fixture to validate.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Check books safety: policy file, vault ignore rules, unsafe paths."""
    report = books_mod.run(
        repo=repo,
        validate_fixture=validate_fixture or bool(fixture_path),
        fixture=fixture_path or None,
    )
    if json_out:
        typer.echo(
            _json_payload(
                report,
                command="mb books check",
                schema_name="mainbranch.books.check.result",
            )
        )
    else:
        books_mod.render_human(report)
    raise typer.Exit(0 if report["ok"] else 1)


@books_app.command("status")
def books_status_cmd(
    repo: str = typer.Argument(".", help="Business repo to inspect."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Show hledger/private-books-vault setup and storage health."""
    report = books_mod.status(repo=repo)
    if json_out:
        typer.echo(
            _json_payload(
                report,
                command="mb books status",
                schema_name="mainbranch.books.status.result",
            )
        )
    else:
        books_mod.render_status(report)
    raise typer.Exit(0 if report["ok"] else 1)


@books_app.command("doctor")
def books_doctor_cmd(
    repo: str = typer.Argument(".", help="Business repo to inspect."),
    plan: bool = typer.Option(
        False,
        "--plan",
        help="Print a non-mutating repair plan. Required; apply is not implemented.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Plan safe books setup repairs without touching real ledger contents."""
    if not plan:
        message = "mb books doctor: --plan is required; apply is not implemented"
        if json_out:
            typer.echo(
                _json_payload(
                    {
                        "ok": False,
                        "state": "error",
                        "summary": message,
                        "errors": [message],
                        "safe_to_share": True,
                    },
                    command="mb books doctor",
                    schema_name="mainbranch.books.doctor.plan.result",
                )
            )
        else:
            typer.echo(message, err=True)
        raise typer.Exit(2)

    report = books_mod.doctor_plan(repo=repo)
    if json_out:
        typer.echo(
            _json_payload(
                report,
                command="mb books doctor --plan",
                schema_name="mainbranch.books.doctor.plan.result",
            )
        )
    else:
        books_mod.render_doctor_plan(report)
    raise typer.Exit(0)


@books_report_app.command("monthly")
def books_report_monthly_cmd(
    sample: bool = typer.Option(
        False,
        "--sample",
        help="Use the fake packaged sample journal. Required in this release.",
    ),
    month: str = typer.Option("", "--month", help="Report month as YYYY-MM."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Generate a sample monthly books report through hledger."""
    month = month.strip()
    command_parts = ["mb books report monthly"]
    if sample:
        command_parts.append("--sample")
    if month:
        command_parts.extend(["--month", month])
    command = " ".join(command_parts)
    if not sample:
        message = (
            "mb books report monthly: only --sample reports are implemented; "
            "private books reporting is out of scope for this release"
        )
        payload = books_mod.sample_monthly_rejection(
            month=month,
            finding_id="sample-required",
            title="Sample flag required",
            message=message,
            repair=(
                "Run `mb books report monthly --sample --month 2026-01` to view fake sample data."
            ),
        )
        if json_out:
            typer.echo(
                _json_payload(
                    payload,
                    command=command,
                    schema_name="mainbranch.books.report.v1",
                )
            )
        else:
            typer.echo(message, err=True)
        raise typer.Exit(2)

    if not month:
        message = "mb books report monthly: --month is required; use YYYY-MM, for example 2026-01"
        payload = books_mod.sample_monthly_rejection(
            month=month,
            finding_id="month-required",
            title="Report month required",
            message=message,
            repair="Run `mb books report monthly --sample --month 2026-01`.",
        )
        if json_out:
            typer.echo(
                _json_payload(
                    payload,
                    command=command,
                    schema_name="mainbranch.books.report.v1",
                )
            )
        else:
            books_mod.render_sample_monthly_report(payload)
        raise typer.Exit(2)

    try:
        report = books_mod.sample_monthly_report(month)
    except ValueError as exc:
        message = f"mb books report monthly: {exc}"
        payload = books_mod.sample_monthly_rejection(
            month=month,
            finding_id="month-invalid",
            title="Report month invalid",
            message=message,
            repair="Use YYYY-MM with a real calendar month, for example 2026-01.",
        )
        if json_out:
            typer.echo(
                _json_payload(
                    payload,
                    command=command,
                    schema_name="mainbranch.books.report.v1",
                )
            )
        else:
            books_mod.render_sample_monthly_report(payload)
        raise typer.Exit(2) from exc

    if json_out:
        typer.echo(
            _json_payload(
                report,
                command=command,
                schema_name="mainbranch.books.report.v1",
            )
        )
    else:
        books_mod.render_sample_monthly_report(report)
    raise typer.Exit(0 if report["ok"] else 1)


@ads_meta_app.command("summary")
def ads_meta_summary_cmd(
    repo: str = typer.Option(".", "--repo", help="Business repo with Meta readiness metadata."),
    window: str = typer.Option("7d", "--window", help="Recent bounded window, such as 7d."),
    since: str = typer.Option("", "--since", help="Start date as YYYY-MM-DD."),
    until: str = typer.Option("", "--until", help="End date as YYYY-MM-DD."),
    include_campaign_names: bool = typer.Option(
        False,
        "--include-campaign-names",
        help="Include campaign names for this run only.",
    ),
    include_exact_spend: bool = typer.Option(
        False,
        "--include-exact-spend",
        help="Include exact spend for this run only.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Pull a compact read-only Meta Ads account summary."""
    command_parts = ["mb ads meta summary"]
    if window:
        command_parts.extend(["--window", window])
    if since:
        command_parts.extend(["--since", since])
    if until:
        command_parts.extend(["--until", until])
    if include_campaign_names:
        command_parts.append("--include-campaign-names")
    if include_exact_spend:
        command_parts.append("--include-exact-spend")
    command = " ".join(command_parts)
    try:
        result = ads_mod.meta_summary(
            repo=repo,
            window=window,
            since=since,
            until=until,
            include_campaign_names=include_campaign_names,
            include_exact_spend=include_exact_spend,
        )
    except ads_mod.AdsSummaryError as exc:
        message = f"mb ads meta summary: {exc}"
        payload = {
            "ok": False,
            "schema_version": ads_mod.SUMMARY_SCHEMA_VERSION,
            "safe_to_share": False,
            "provider": "meta",
            "command": "mb ads meta summary",
            "state": "invalid_arguments",
            "summary": message,
            "errors": [message],
            "actions": [],
        }
        if json_out:
            typer.echo(
                _json_payload(
                    payload,
                    command=command,
                    schema_name="mainbranch.ads.meta.summary.v1",
                )
            )
        else:
            typer.echo(message, err=True)
        raise typer.Exit(2) from exc

    if json_out:
        typer.echo(
            _json_payload(
                result,
                command=command,
                schema_name="mainbranch.ads.meta.summary.v1",
            )
        )
    else:
        ads_mod.render_meta_summary_human(result)
    raise typer.Exit(0 if result["ok"] else 1)


@site_app.command("check")
def site_check_cmd(
    site_repo: str = typer.Argument(".", help="Site repo or built static site to inspect."),
    business_repo: str = typer.Option(
        "",
        "--business-repo",
        "--repo",
        help="Business repo with offer and provider metadata.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Check paid-traffic measurement readiness without mutating provider accounts."""
    result = site_mod.check(site_repo, business_repo=business_repo or None)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        site_mod.render_check(result)
    raise typer.Exit(0 if result["ok"] else 1)


@image_app.command("smoke-openai")
def image_smoke_openai_cmd(
    repo: str = typer.Option(
        ".",
        "--repo",
        help="Business repo where the fake push-local image-index.md should be written.",
    ),
    push_slug: str = typer.Option(
        image_rail_mod.DEFAULT_PUSH_SLUG,
        "--push-slug",
        help="Fake push slug for the fixture-safe smoke record.",
    ),
    docs_checked: str = typer.Option(
        "",
        "--docs-checked",
        help="Provider docs checked date. Defaults to today in UTC.",
    ),
    media_root: str = typer.Option(
        ".mb/media",
        "--media-root",
        help="Private media storage root used only when --generate writes a binary.",
    ),
    generate: bool = typer.Option(
        False,
        "--generate",
        help="Call OpenAI only when local credentials exist and the operator approved generation.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Smoke the narrow OpenAI GPT Image 2 rail with fake fixture context."""
    result = image_rail_mod.smoke_openai(
        repo=repo,
        push_slug=push_slug,
        docs_checked=docs_checked or _today_utc(),
        media_root=media_root,
        generate=generate,
    )
    if json_out:
        typer.echo(
            _json_payload(
                result,
                command="image smoke-openai",
                schema_name="mainbranch.image.smoke_openai.v1",
            )
        )
    elif result["state"] == "generated":
        typer.echo("OpenAI image rail smoke generated a fixture-safe asset.")
        typer.echo(f"record: {result['record_path']}")
        typer.echo(f"media:  {result['output_reference']}")
        typer.echo("binary committed: false")
    else:
        typer.echo("OpenAI image rail smoke blocked safely.")
        typer.echo(f"record: {result['record_path']}")
        typer.echo(f"reason: {result['blocker_code']}")
        typer.echo("I will not ask you to paste provider keys into chat or repo files.")
    raise typer.Exit(0)


@app.command("validate")
def validate_cmd(
    path: str = typer.Argument(".", help="Repo to validate."),
    repo: str | None = typer.Option(
        None,
        "--repo",
        help="Repo to validate. Alias for the positional PATH used by older scripts.",
    ),
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
    target = repo or path
    report = validate_mod.run(
        path=target,
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
    json_out: bool = typer.Option(False, "--json", help="Emit the machine-readable graph index."),
) -> None:
    """Build the repo graph index; emit DOT by default or JSON with --json."""
    if json_out and open_after:
        raise typer.BadParameter("--open cannot be combined with --json")
    index = graph_mod.build_index(path=path)
    if json_out:
        typer.echo(json.dumps(index, indent=2))
        return
    dot = graph_mod.index_to_dot(index)
    if open_after:
        graph_mod.open_dot(dot)
    else:
        typer.echo(dot)


@suggest_app.command("links")
def suggest_links_cmd(
    file: str = typer.Argument(..., help="Markdown file to inspect."),
    repo: str = typer.Option(".", "--repo", help="Business repo to query."),
    limit: int = typer.Option(10, "--limit", min=0, help="Maximum suggestions to return."),
    include_ignored: bool = typer.Option(
        False,
        "--include-ignored",
        help="Include candidates classified as ignore.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Suggest likely business connections without editing files."""
    try:
        report = suggest_mod.suggest_links(
            source_file=file,
            repo=repo,
            limit=limit,
            include_ignored=include_ignored,
        )
    except ValueError as exc:
        typer.echo(f"mb suggest links: {exc}", err=True)
        raise typer.Exit(2) from exc
    if json_out:
        typer.echo(json.dumps(report, indent=2))
    else:
        suggest_mod.render_human(report)
    raise typer.Exit(0 if report["ok"] else 1)


@app.command("similar-bets")
def similar_bets_cmd(
    thesis: str = typer.Argument(..., help="Current bet thesis to compare against repo memory."),
    path: str = typer.Option(".", "--repo", help="Business repo to query."),
    limit: int = typer.Option(5, "--limit", min=1, help="Maximum matches to return."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Find similar past bets and offer outcomes from repo truth."""
    report = similar_bets_mod.run(path=path, thesis=thesis, limit=limit)
    if json_out:
        typer.echo(json.dumps(report, indent=2))
    else:
        similar_bets_mod.render_human(report)


@app.command("think")
def think_cmd(
    topic: str = typer.Argument(..., help="Topic to think about."),
) -> None:
    """Print the /mb-think invocation hint (run inside Claude Code for full flow)."""
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
    """Print a beginner education topic for Main Branch rails and defaults."""
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


@app.command("checkpoint")
def checkpoint_cmd(
    repo: str = typer.Option(".", "--repo", help="Business repo to inspect."),
    plan: bool = typer.Option(
        False,
        "--plan",
        help="Preview checkpointable changes without committing.",
    ),
    status_check: bool = typer.Option(
        False,
        "--status",
        help="Show recent checkpoint commits plus pending checkpoint state.",
    ),
    message: str = typer.Option("", "--message", "-m", help="Commit message for --yes."),
    validate: str = typer.Option(
        "",
        "--validate",
        help="Validate a checkpoint message. Pass '-' to read the message from stdin.",
    ),
    hook_status: bool = typer.Option(
        False,
        "--hook-status",
        help="Inspect the repo-local checkpoint commit-message hook.",
    ),
    install_hook: bool = typer.Option(
        False,
        "--install-hook",
        help="Install or repair the repo-local checkpoint commit-message hook.",
    ),
    uninstall_hook: bool = typer.Option(
        False,
        "--uninstall-hook",
        help="Remove the Main Branch checkpoint commit-message hook.",
    ),
    yes: bool = typer.Option(False, "--yes", help="Save the checkpoint after safety gates pass."),
    mode: str = typer.Option(
        "beginner",
        "--mode",
        help="Checkpoint grouping mode: beginner or concern.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Plan or save a git checkpoint."""
    hook_operations = sum(1 for item in (hook_status, install_hook, uninstall_hook) if item)
    if hook_operations > 1:
        typer.echo("mb checkpoint: choose only one hook operation", err=True)
        raise typer.Exit(2)
    if validate and hook_operations:
        typer.echo("mb checkpoint: --validate cannot be combined with hook operations", err=True)
        raise typer.Exit(2)
    if install_hook:
        result = checkpoint_mod.install_commit_hook(repo=repo)
    elif uninstall_hook:
        result = checkpoint_mod.uninstall_commit_hook(repo=repo)
    elif hook_status:
        result = checkpoint_mod.hook_status(repo=repo)
    elif validate:
        validation_message = sys.stdin.read() if validate == "-" else validate
        result = checkpoint_mod.validate_message(validation_message)
    elif yes or message:
        result = checkpoint_mod.commit(repo=repo, message=message, mode=mode, yes=yes)
    elif status_check:
        result = checkpoint_mod.status(repo=repo, mode=mode)
    else:
        _ = plan
        result = checkpoint_mod.plan(repo=repo, mode=mode)
    if json_out:
        typer.echo(
            _json_payload(
                result,
                command="mb checkpoint",
                schema_name="mainbranch.checkpoint.result",
            )
        )
    else:
        checkpoint_mod.render_human(result)
    raise typer.Exit(0 if result["ok"] else 1)


@migrate_app.callback()
def migrate_cmd(
    ctx: typer.Context,
    repo: str = typer.Option(".", "--repo", help="Business repo to migrate."),
    check: bool = typer.Option(False, "--check", help="Dry-run pending migrations."),
    apply_changes: bool = typer.Option(False, "--apply", help="Apply pending migrations."),
    diff: bool = typer.Option(
        False,
        "--diff",
        help="With --check, include the full unified diff. May print private repo content.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Run `mb migrate --check` or `mb migrate --apply`; defaults to status."""
    ctx.obj = {"repo": repo}
    if ctx.invoked_subcommand is not None:
        if diff:
            typer.echo("mb migrate: --diff can only be used with --check", err=True)
            raise typer.Exit(2)
        return
    if check and apply_changes:
        typer.echo("mb migrate: choose only one of --check or --apply", err=True)
        raise typer.Exit(2)
    if diff and not check:
        typer.echo("mb migrate: --diff can only be used with --check", err=True)
        raise typer.Exit(2)
    if apply_changes:
        result = migrate_mod.apply(repo)
        if json_out:
            typer.echo(json.dumps(result, indent=2))
        else:
            migrate_mod.render_apply(result)
        raise typer.Exit(0 if result["ok"] else 1)
    if check:
        result = migrate_mod.check(repo, include_diff=diff)
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


@migrate_app.command("campaigns")
def migrate_campaigns_cmd(
    ctx: typer.Context,
    plan: bool = typer.Option(
        False,
        "--plan",
        help=(
            "Print a read-only plan classifying campaigns/ records as moves, "
            "ambiguous, or blockers."
        ),
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Preview the legacy ``campaigns/`` -> canonical ``pushes/`` migration.

    Plan-only in this release. The apply path lands in a follow-up PR with
    backups and explicit operator approval; running without ``--plan`` exits
    with the same plan output and a notice that apply is not yet implemented.
    """
    repo_value = ctx.obj.get("repo", ".") if ctx.obj else "."
    if not plan:
        typer.echo(
            "mb migrate campaigns: --plan is required (apply is not yet implemented)",
            err=True,
        )
        raise typer.Exit(2)
    result = migrate_mod.plan_campaigns_to_pushes(repo_value)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        migrate_mod.render_campaigns_plan(result)
    summary = result["summary"]
    has_blockers = summary.get("blockers", 0) > 0
    has_anything = sum(summary.values()) > 0
    raise typer.Exit(1 if has_blockers else (0 if has_anything else 0))


@migrate_app.command("status")
def migrate_status_cmd(
    ctx: typer.Context,
    repo: str | None = typer.Option(None, "--repo", help="Business repo to inspect."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Show current schema version and pending migrations."""
    root_repo = (ctx.obj or {}).get("repo", ".") if isinstance(ctx.obj, dict) else "."
    result = migrate_mod.status(repo or root_repo)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        migrate_mod.render_status(result)


@skill_app.command("path")
def skill_path_cmd(
    name: str = typer.Argument(..., help="Skill name (e.g. 'mb-site')."),
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
    name: str | None = typer.Argument(None, help="Skill name (e.g. 'mb-site')."),
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
            typer.echo("you're set — run `claude` and then /mb-start.")
        else:
            typer.echo("could not link Main Branch skills:", err=True)
            for error in result["errors"]:
                typer.echo(f"  - {error}", err=True)
            raise typer.Exit(1)


@skill_app.command("repair")
def skill_repair_cmd(
    repo: str = typer.Option(".", "--repo", help="Business repo to inspect."),
    apply_changes: bool = typer.Option(
        False,
        "--apply",
        help="Move stale or broken Main Branch personal skill links to a timestamped backup.",
    ),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Inspect or repair personal Claude Code skills that shadow Main Branch."""
    from mb.engine import inspect_personal_skill_conflicts

    result = inspect_personal_skill_conflicts(repo, apply=apply_changes)
    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        summary = result["summary"]
        typer.echo(f"checked personal Claude Code skills: {result['personal_skills_dir']}")
        if summary["findings"] == 0:
            typer.echo("no personal skill shadows or legacy Main Branch skill traps found.")
        else:
            typer.echo(
                f"found {summary['findings']} issue(s): "
                f"{summary['active_shadows']} active shadow(s), "
                f"{summary['legacy_globals']} legacy command trap(s)."
            )
            for finding in result["findings"]:
                typer.echo("")
                typer.echo(f"- {finding['name']} ({finding['classification']})")
                typer.echo(f"  path: {finding['global_path']}")
                if finding["global_target"]:
                    typer.echo(f"  target: {finding['global_target']}")
                if finding["safe_to_repair"]:
                    if finding["repaired"]:
                        typer.echo(f"  moved to: {finding['backup_path']}")
                    else:
                        typer.echo("  safe repair: run `mb skill repair --repo . --apply`")
                else:
                    typer.echo(
                        "  not changed: this is not a stale or broken Main Branch skill link"
                    )
        if not apply_changes and summary["repairable"]:
            typer.echo("")
            typer.echo("To move stale or broken Main Branch symlinks to backup:")
            typer.echo("  mb skill repair --repo . --apply")
    raise typer.Exit(0 if result["ok"] else 1)


def _entry() -> None:
    """Defensive entrypoint used by ``python -m mb`` and tests."""
    try:
        app()
    except typer.Exit:
        raise
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"mb: error: {exc}", err=True)
        sys.exit(2)
