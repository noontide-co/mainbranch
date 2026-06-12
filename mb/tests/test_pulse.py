"""``mb pulse init`` daily-pulse scaffold."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from mb import pulse as pulse_mod
from mb.cli import app

runner = CliRunner()


def test_pulse_init_scaffolds_collectors_and_skill(tmp_path: Path) -> None:
    repo = tmp_path / "Acme Brewing"
    repo.mkdir()
    result = runner.invoke(app, ["pulse", "init", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert "core/operations/pulse/collectors/README.md" in payload["written"]
    assert "core/operations/pulse/collectors/collect-example.sh" in payload["written"]
    assert ".claude/skills/mb-pulse/SKILL.md" in payload["written"]

    readme = (repo / "core/operations/pulse/collectors/README.md").read_text(encoding="utf-8")
    assert "Date in, JSON out." in readme
    assert "Honest absence beats invented numbers." in readme
    assert "Read-only against every provider." in readme

    skill = (repo / ".claude/skills/mb-pulse/SKILL.md").read_text(encoding="utf-8")
    assert "one recommended action" in skill.lower()
    assert "A pulse that recommends three things recommends nothing." in skill
    assert "mb status --json" in skill
    assert "Do NOT re-rank repo facts" in skill
    # Slug derived from the repo directory name.
    assert "log/<date>-acme-brewing-pulse.md" in skill


def test_pulse_init_refuses_overwrite_without_force(tmp_path: Path) -> None:
    pulse_mod.init(tmp_path)
    collector = tmp_path / "core/operations/pulse/collectors/collect-example.sh"
    marker = "# my customized collector\n"
    collector.write_text(marker, encoding="utf-8")

    refused = runner.invoke(app, ["pulse", "init", "--repo", str(tmp_path)])
    assert refused.exit_code == 1
    assert collector.read_text(encoding="utf-8") == marker

    forced = runner.invoke(app, ["pulse", "init", "--repo", str(tmp_path), "--force"])
    assert forced.exit_code == 0
    assert "unavailable" in collector.read_text(encoding="utf-8")


def test_pulse_templates_contain_no_business_specifics(tmp_path: Path) -> None:
    pulse_mod.init(tmp_path)
    paths = (
        tmp_path / "core/operations/pulse/collectors/README.md",
        tmp_path / "core/operations/pulse/collectors/collect-example.sh",
        tmp_path / ".claude/skills/mb-pulse/SKILL.md",
    )
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for banned in ("booked", "roofer", "noontide", "awake", "morning paper", "cloudflare"):
            assert banned not in text, f"{path.name} leaks {banned!r}"


def test_pulse_example_collector_is_valid_bash_and_honors_contract(tmp_path: Path) -> None:
    pulse_mod.init(tmp_path)
    collector = tmp_path / "core/operations/pulse/collectors/collect-example.sh"
    assert os.access(collector, os.X_OK)

    syntax = subprocess.run(
        ["bash", "-n", str(collector)], capture_output=True, text=True, timeout=15
    )
    assert syntax.returncode == 0, syntax.stderr

    bad_date = subprocess.run(
        ["bash", str(collector), "not-a-date"], capture_output=True, text=True, timeout=15
    )
    assert bad_date.returncode != 0
    payload = json.loads(bad_date.stdout)
    assert payload["unavailable"] is True
    assert payload["error"] == "bad_date_arg"

    good = subprocess.run(
        ["bash", str(collector), "2026-06-12"], capture_output=True, text=True, timeout=15
    )
    assert good.returncode == 0
    assert json.loads(good.stdout)["date"] == "2026-06-12"


def test_pulse_init_explicit_slug_wins(tmp_path: Path) -> None:
    pulse_mod.init(tmp_path, slug="My Biz!!")
    skill = (tmp_path / ".claude/skills/mb-pulse/SKILL.md").read_text(encoding="utf-8")
    assert "log/<date>-my-biz-pulse.md" in skill
