"""Thin wrapper around .claude/skills/site/scripts/og_render.py.

Per master decision: do NOT rewrite the renderer. PR #100 already shipped
``og_render.py`` with rsvg + cairosvg fallback, live-tested at
thelastbill.com. This wrapper is the packaging seam — when ``mainbranch``
ships, ``mb og-render`` (or ``tool-og-render``) re-uses the existing code
directly.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _renderer_path() -> Path:
    """Locate og_render.py in the engine repo. v0.2 will install it as data."""
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        cand = parent / ".claude" / "skills" / "site" / "scripts" / "og_render.py"
        if cand.exists():
            return cand
    raise FileNotFoundError("og_render.py not located")


def main() -> None:
    """Forward argv to the bundled og_render.py via runpy."""
    target = _renderer_path()
    sys.argv = [str(target), *sys.argv[1:]]
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
