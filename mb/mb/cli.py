"""Typer CLI for ``mb``.

Thin dispatcher. Each subcommand lives in its own module so we can
unit-test in isolation. The shape echoes ``companyctx`` (Typer + sub-apps)
because that's the working pattern.
"""

from __future__ import annotations

import json
import sys

import typer

from mb import __version__
from mb import doctor as doctor_mod
from mb import educational as educational_mod
from mb import graph as graph_mod
from mb import init as init_mod
from mb import resolve as resolve_mod
from mb import status as status_mod
from mb import think as think_mod
from mb import update as update_mod
from mb import validate as validate_mod

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


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"mb {__version__}")
        raise typer.Exit()


def _is_interactive_terminal() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _render_launch_screen() -> None:
    typer.echo(
        "\n".join(
            [
                "",
                "Main Branch",
                "Stay connected to the business while agents handle execution.",
                "",
                "Choose a trail:",
                "  New here      mb onboard       guided setup (coming in v0.2)",
                "  Daily work    mb status        business/repo briefing",
                "                mb start         open the agent runtime (coming in v0.2)",
                "  Broken setup  mb doctor        check git, GitHub, Claude Code, and skills",
                "  Power user    mb --help        full command list",
                "",
                "Plain command reference: mb --plain",
                "",
            ]
        )
    )


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


@app.command("validate")
def validate_cmd(
    path: str = typer.Argument(".", help="Repo to validate."),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Check the metadata at the top of your files (frontmatter shape)."""
    report = validate_mod.run(path=path, verbose=verbose)
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
