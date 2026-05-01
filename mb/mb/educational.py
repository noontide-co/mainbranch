"""``mb educational <topic>`` — load and print an educational triage file.

Files live at ``.claude/educational/<topic>.md`` in the engine repo and
are bundled as package data under ``mb/_data/educational/``. The doctor
subcommand wires "tell me more" prompts to this loader.
"""

from __future__ import annotations

import sys
from importlib import resources
from pathlib import Path


def _engine_path() -> Path | None:
    """Return the engine-repo .claude/educational/ path if running from a checkout."""
    here = Path(__file__).resolve()
    for parent in (here.parent.parent.parent.parent, here.parent.parent.parent):
        cand = parent / ".claude" / "educational"
        if cand.exists():
            return cand
    return None


def load(topic: str) -> str | None:
    """Return the markdown body for ``topic`` or None if not found."""
    # Try bundled data first.
    try:
        ref = (
            resources.files("mb").joinpath("_data").joinpath("educational").joinpath(f"{topic}.md")
        )
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        pass
    engine = _engine_path()
    if engine is not None:
        cand = engine / f"{topic}.md"
        if cand.exists():
            return cand.read_text(encoding="utf-8")
    return None


def run(topic: str) -> None:
    """Print the educational file or an honest error."""
    body = load(topic)
    if body is None:
        print(
            f"educational topic not found: {topic}\n"
            "Try one of: anti-cloud-backup, cloudflare-vs-vercel, github-vs-gdocs",
            file=sys.stderr,
        )
        sys.exit(1)
    print(body)
