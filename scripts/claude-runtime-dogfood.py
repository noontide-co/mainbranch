#!/usr/bin/env python3
"""Run the Main Branch Claude Code runtime dogfood harness."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "mb"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from mb.dogfood_harness import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
