"""Steered-loop / automation scaffold (`mb automation init`).

Overnight loops and crons ran with no inspectable state, and loop handoffs
were hand-written markdown in a personal repo — so no one but the author could
tell what an automation was doing. This graduates the steered-loop contract
(the same shape this engine's own development loop runs on): one inspectable
loop-state file the agent reads first, updates each iteration, and renders
handoffs from.

v1 scaffolds the steered-loop contract. The unattended-cron shape pairs with
`mb pulse install` for deterministic fetch-and-record jobs. Live facts about
armed automations (next fire, last run, outcome) are a planned follow-up; until
then each run's outcome lands in the loop-state Shipped section.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any

_TEMPLATE_NAME = "loop-state.md"


def _loop_state_template() -> str:
    """Read the bundled loop-state template from _data/templates/."""
    try:
        ref = resources.files("mb").joinpath("_data").joinpath("templates").joinpath(_TEMPLATE_NAME)
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        here = Path(__file__).resolve().parent / "_data" / "templates" / _TEMPLATE_NAME
        return here.read_text(encoding="utf-8")


def init(repo: str | Path = ".", *, force: bool = False) -> dict[str, Any]:
    """Scaffold core/operations/loop-state.md (the steered-loop contract)."""
    root = Path(repo).resolve()
    state_path = root / "core" / "operations" / "loop-state.md"
    rel = "core/operations/loop-state.md"
    if state_path.exists() and not force:
        return {
            "ok": False,
            "repo": str(root),
            "written": [],
            "skipped": [rel],
            "summary": (
                "loop-state.md already exists; rerun with --force to overwrite "
                "(your loop's recorded state would be lost)"
            ),
        }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(_loop_state_template(), encoding="utf-8")
    return {
        "ok": True,
        "repo": str(root),
        "written": [rel],
        "skipped": [],
        "summary": (
            "steered-loop contract scaffolded — fill in Steering, Priority order, "
            "and Hard guardrails; the loop reads this first each run, appends to "
            "Shipped, and renders handoffs from it. Unattended cron jobs pair with "
            "`mb pulse install`"
        ),
        "safe_to_share": True,
    }


def render_init(result: dict[str, Any]) -> None:
    print(result["summary"])
    for path in result.get("written", []):
        print(f"  wrote {path}")
    for path in result.get("skipped", []):
        print(f"  kept  {path}")
