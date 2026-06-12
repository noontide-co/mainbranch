"""Every CLI surface must be reachable from a discovery rail.

Operators never browse the CLI. A surface is discoverable when it appears
in at least one rail an operator or agent actually touches: a bundled
skill (mb-start routes, mb-help answers, workers cite), the docs index
corpus, or an engine-emitted nudge (repair/summary strings in the
package). A command reachable from none of those is invisible — this
gate fails the build instead of letting it ship.
"""

from __future__ import annotations

from pathlib import Path

from mb.cli import app

REPO_ROOT = Path(__file__).resolve().parents[2]

# Surfaces that are deliberately agent/engine-internal and are documented
# where agents actually find them (each entry needs a justification).
INTERNAL_ALLOWLIST = {
    # Invoked by mb-think's educational flow through the engine, not named
    # in prose; covered by the educational content itself.
    "educational",
    # Engine-internal resolution helper used by skills' path-resolution
    # reference, which documents the contract rather than the command name.
    "resolve",
}


def _cli_surfaces() -> set[str]:
    names: set[str] = set()
    for command in app.registered_commands:
        if command.name:
            names.add(command.name)
        elif command.callback is not None:
            names.add(command.callback.__name__)
    for group in app.registered_groups:
        if group.typer_instance is not None and group.typer_instance.info.name:
            names.add(str(group.typer_instance.info.name))
    return names


def _discovery_corpus() -> str:
    chunks: list[str] = []
    for pattern in (".claude/skills/**/*.md", "docs/*.md", "workflows/**/*.md"):
        for path in REPO_ROOT.glob(pattern):
            if path.is_file():
                chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    for path in (REPO_ROOT / "mb" / "mb").glob("*.py"):
        chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def test_every_cli_surface_is_discoverable() -> None:
    corpus = _discovery_corpus()
    unreachable = sorted(
        name
        for name in _cli_surfaces()
        if name not in INTERNAL_ALLOWLIST and f"mb {name}" not in corpus
    )
    assert unreachable == [], (
        "CLI surfaces unreachable from every discovery rail (no skill routes "
        "to them, no doc names them, no engine nudge emits them): "
        f"{unreachable}. Wire each into mb-start routing, mb-help's "
        "cli-surfaces map, or a doctor/status repair string — or add to "
        "INTERNAL_ALLOWLIST with a justification."
    )


def test_allowlist_stays_small_and_justified() -> None:
    # The allowlist growing silently would gut the gate.
    assert len(INTERNAL_ALLOWLIST) <= 4
