"""``mb educational <topic>`` — load and print an educational triage file.

Files live at ``.claude/educational/<topic>.md`` in the engine repo and
are bundled as package data under the synthetic ``mb/_engine/.claude/``
root. Older wheels also carried copies under ``mb/_data/educational/``;
that path remains a compatibility fallback.
"""

from __future__ import annotations

import sys
from importlib import resources
from pathlib import Path

from mb.engine import engine_root


def _engine_path() -> Path | None:
    """Return the active engine .claude/educational/ path."""
    root = engine_root()
    if root is not None:
        cand = root / ".claude" / "educational"
        if cand.is_dir():
            return cand
    return None


def load(topic: str) -> str | None:
    """Return the markdown body for ``topic`` or None if not found."""
    engine = _engine_path()
    if engine is not None:
        cand = engine / f"{topic}.md"
        if cand.exists():
            return cand.read_text(encoding="utf-8")

    # Compatibility fallback for v0.1.0 package data.
    try:
        ref = (
            resources.files("mb").joinpath("_data").joinpath("educational").joinpath(f"{topic}.md")
        )
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        pass
    return None


def run(topic: str) -> None:
    """Print the educational file or an honest error."""
    body = load(topic)
    if body is None:
        print(
            f"educational topic not found: {topic}\n"
            "Try one of: anti-cloud-backup, cloudflare-vs-vercel, "
            "github-vs-gdocs, upgrading-mainbranch",
            file=sys.stderr,
        )
        sys.exit(1)
    print(body)
