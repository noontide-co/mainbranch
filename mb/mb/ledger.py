"""What's-working creative ledger scaffold (`mb ledger init`).

Creative verdicts scatter across push logs, quality-gate research, and
operator briefs, so the durable signal — which asset actually produced an
ELIGIBLE customer, at what cost — is never queryable in one place. This
scaffolds the canonical ledger: one row per creative asset, the columns an
agent needs to call KEEP/KILL, and the doctrine that an asset is not working
until it produces an eligible lead (not a cheap one).

v1 is a markdown table (this scaffold). When an offer passes ~50 assets,
graduate the same columns to the owned SQLite/D1 spine (`mb spine init
--owned`) so the ledger is queryable at scale. The agent writes rows from
recorded facts; code never invents a verdict.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any

_TEMPLATE_NAME = "creative-ledger.md"


def _ledger_template() -> str:
    """Read the bundled creative-ledger template from _data/templates/."""
    try:
        ref = resources.files("mb").joinpath("_data").joinpath("templates").joinpath(_TEMPLATE_NAME)
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        here = Path(__file__).resolve().parent / "_data" / "templates" / _TEMPLATE_NAME
        return here.read_text(encoding="utf-8")


def init(repo: str | Path = ".", *, force: bool = False) -> dict[str, Any]:
    """Scaffold core/operations/creative-ledger.md (v1 markdown table)."""
    root = Path(repo).resolve()
    ledger_path = root / "core" / "operations" / "creative-ledger.md"
    rel = "core/operations/creative-ledger.md"
    if ledger_path.exists() and not force:
        return {
            "ok": False,
            "repo": str(root),
            "written": [],
            "skipped": [rel],
            "summary": (
                "creative-ledger.md already exists; rerun with --force to overwrite "
                "(your recorded rows would be lost)"
            ),
        }
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.write_text(_ledger_template(), encoding="utf-8")
    return {
        "ok": True,
        "repo": str(root),
        "written": [rel],
        "skipped": [],
        "summary": (
            "creative ledger scaffolded — append one row per asset; drive KEEP/KILL "
            "off eligible_cpl (mb leads grade), never raw CPL. Graduate to "
            "mb spine init --owned past ~50 assets"
        ),
        "safe_to_share": True,
    }


def render_init(result: dict[str, Any]) -> None:
    print(result["summary"])
    for path in result.get("written", []):
        print(f"  wrote {path}")
    for path in result.get("skipped", []):
        print(f"  kept  {path}")
