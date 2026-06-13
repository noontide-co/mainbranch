"""`mb ledger init` — what's-working creative ledger scaffold (#886)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import ledger as ledger_mod
from mb.cli import app

runner = CliRunner()


def test_ledger_init_scaffolds_canonical_columns(tmp_path: Path) -> None:
    result = runner.invoke(app, ["ledger", "init", "--repo", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert "core/operations/creative-ledger.md" in payload["written"]

    text = (tmp_path / "core/operations/creative-ledger.md").read_text(encoding="utf-8")
    for column in (
        "asset_id",
        "angle_lever",
        "spend",
        "raw_cpl",
        "eligible_cpl",
        "downstream_event",
        "verdict",
    ):
        assert column in text
    # The verdict vocabulary.
    for verdict in ("KEEP", "KILL", "WATCH"):
        assert verdict in text


def test_ledger_encodes_eligible_not_cheap_doctrine(tmp_path: Path) -> None:
    ledger_mod.init(tmp_path)
    text = (tmp_path / "core/operations/creative-ledger.md").read_text(encoding="utf-8").lower()
    assert "not working until it produces an eligible lead" in text
    # Drives off eligible_cpl, explicitly not raw CPL / CTR alone.
    assert "never off `raw_cpl`" in text or "never off raw_cpl" in text
    assert "mb leads grade" in text
    # Graduation path named.
    assert "mb spine init --owned" in text


def test_ledger_init_refuses_overwrite_without_force(tmp_path: Path) -> None:
    ledger_mod.init(tmp_path)
    marker = "| my-asset | kept | meta | 2026-06-13 | 1 | 1% | 1 | 1 | booked | KEEP |\n"
    path = tmp_path / "core/operations/creative-ledger.md"
    path.write_text(marker, encoding="utf-8")

    refused = runner.invoke(app, ["ledger", "init", "--repo", str(tmp_path)])
    assert refused.exit_code == 1
    assert path.read_text(encoding="utf-8") == marker

    forced = runner.invoke(app, ["ledger", "init", "--repo", str(tmp_path), "--force"])
    assert forced.exit_code == 0
    assert "asset_id" in path.read_text(encoding="utf-8")


def test_ledger_template_has_no_business_specifics(tmp_path: Path) -> None:
    ledger_mod.init(tmp_path)
    text = (tmp_path / "core/operations/creative-ledger.md").read_text(encoding="utf-8").lower()
    for banned in ("booked out", "roofer", "noontide", "awake happy", "morning paper"):
        assert banned not in text, f"ledger leaks {banned!r}"
