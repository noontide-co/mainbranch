"""`mb automation init` — steered-loop contract scaffold (#838)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import automation as automation_mod
from mb.cli import app

runner = CliRunner()


def test_automation_init_scaffolds_loop_state_contract(tmp_path: Path) -> None:
    result = runner.invoke(app, ["automation", "init", "--repo", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert "core/operations/loop-state.md" in payload["written"]

    text = (tmp_path / "core/operations/loop-state.md").read_text(encoding="utf-8")
    for section in ("## Steering", "## Priority order", "## Hard guardrails", "## Shipped"):
        assert section in text
    assert "Flagged for me" in text


def test_automation_template_encodes_inspectable_and_two_shapes(tmp_path: Path) -> None:
    automation_mod.init(tmp_path)
    text = (tmp_path / "core/operations/loop-state.md").read_text(encoding="utf-8").lower()
    # The core principle.
    assert "inspectable" in text
    # Both automation shapes named.
    assert "steered loop" in text
    assert "unattended cron" in text
    # Handoffs are rendered from the file, and cron pairs with pulse install.
    assert "rendered from this file" in text
    assert "mb pulse install" in text


def test_automation_init_refuses_overwrite_without_force(tmp_path: Path) -> None:
    automation_mod.init(tmp_path)
    marker = "# my live loop state\n"
    path = tmp_path / "core/operations/loop-state.md"
    path.write_text(marker, encoding="utf-8")

    refused = runner.invoke(app, ["automation", "init", "--repo", str(tmp_path)])
    assert refused.exit_code == 1
    assert path.read_text(encoding="utf-8") == marker

    forced = runner.invoke(app, ["automation", "init", "--repo", str(tmp_path), "--force"])
    assert forced.exit_code == 0
    assert "## Steering" in path.read_text(encoding="utf-8")


def test_automation_template_has_no_business_specifics(tmp_path: Path) -> None:
    automation_mod.init(tmp_path)
    text = (tmp_path / "core/operations/loop-state.md").read_text(encoding="utf-8").lower()
    for banned in ("booked out", "roofer", "noontide", "awake happy", "morning paper", "devon"):
        assert banned not in text, f"loop-state leaks {banned!r}"
