"""``mb canary init`` golden-path scaffold."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from mb import canary as canary_mod
from mb.cli import app

runner = CliRunner()


def test_canary_init_scaffolds_harness_and_doctrine(tmp_path: Path) -> None:
    result = runner.invoke(app, ["canary", "init", "--repo", str(tmp_path), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert "canary/smoke.mjs" in payload["written"]
    assert "canary/README.md" in payload["written"]

    smoke = (tmp_path / "canary" / "smoke.mjs").read_text(encoding="utf-8")
    assert "--expensive" in smoke
    assert "WARN never pages" in smoke
    assert "process.exit(fails.length === 0 ? 0 : 1)" in smoke

    readme = (tmp_path / "canary" / "README.md").read_text(encoding="utf-8")
    assert "FAIL pages the operator. WARN never pages." in readme
    assert "/test-alert" in readme
    assert "/simulate-break" in readme


def test_canary_init_refuses_overwrite_without_force(tmp_path: Path) -> None:
    canary_mod.init(tmp_path)
    marker = "// my custom check\n"
    smoke = tmp_path / "canary" / "smoke.mjs"
    smoke.write_text(marker, encoding="utf-8")

    refused = runner.invoke(app, ["canary", "init", "--repo", str(tmp_path)])
    assert refused.exit_code == 1
    assert smoke.read_text(encoding="utf-8") == marker

    forced = runner.invoke(app, ["canary", "init", "--repo", str(tmp_path), "--force"])
    assert forced.exit_code == 0
    assert "WARN never pages" in smoke.read_text(encoding="utf-8")


def test_canary_template_contains_no_business_specifics(tmp_path: Path) -> None:
    canary_mod.init(tmp_path)
    for name in ("smoke.mjs", "README.md"):
        text = (tmp_path / "canary" / name).read_text(encoding="utf-8").lower()
        for banned in ("booked", "roofer", "noontide", "lbe-", "crandall", "1307884"):
            assert banned not in text, f"{name} leaks {banned!r}"


def test_canary_template_is_valid_node_syntax(tmp_path: Path) -> None:
    canary_mod.init(tmp_path)
    proc = subprocess.run(
        ["node", "--check", str(tmp_path / "canary" / "smoke.mjs")],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert proc.returncode == 0, proc.stderr
