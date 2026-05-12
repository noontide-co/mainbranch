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

BEGINNER_CATALOG_TOPICS = (
    "anti-cloud-backup",
    "cal-com",
    "cli-vs-dashboard",
    "cloudflare-pages",
    "cloudflare-vs-vercel",
    "cursor",
    "daily-owner-loop",
    "forgejo",
    "git-history-vs-cloud-sync",
    "github-vs-gdocs",
    "hledger",
    "markdown-vs-notion",
    "provider-readiness",
    "stripe",
    "upgrading-mainbranch",
    "why-mainbranch-not-saas",
)

DEFAULT_TOPIC_HINTS = (
    "daily-owner-loop",
    "why-mainbranch-not-saas",
    "github-vs-gdocs",
    "provider-readiness",
    "cloudflare-pages",
    "upgrading-mainbranch",
)


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


def topics() -> list[str]:
    """Return known educational topics from active engine and bundled data."""

    names: set[str] = set()
    engine = _engine_path()
    if engine is not None:
        names.update(path.stem for path in engine.glob("*.md"))
    try:
        ref = resources.files("mb").joinpath("_data").joinpath("educational")
        names.update(
            path.name.removesuffix(".md") for path in ref.iterdir() if path.name.endswith(".md")
        )
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        pass
    return sorted(names)


def run(topic: str) -> None:
    """Print the educational file or an honest error."""
    body = load(topic)
    if body is None:
        available = ", ".join(topics()) or ", ".join(DEFAULT_TOPIC_HINTS)
        print(
            f"educational topic not found: {topic}\nTry one of: {available}",
            file=sys.stderr,
        )
        sys.exit(1)
    print(body)
