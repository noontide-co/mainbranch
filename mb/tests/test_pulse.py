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
    # Schema parity with the sibling scaffolds (pulse install, ledger init).
    assert payload["safe_to_share"] is True
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


# --- mb pulse install (operator-owned scheduler wrapper) -------------------


def test_pulse_install_requires_collectors_first(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    result = pulse_mod.install(repo)
    assert result["ok"] is False
    assert "mb pulse init" in result["summary"]


def test_pulse_install_writes_wrapper_and_cron_line(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    pulse_mod.init(repo)

    result = pulse_mod.install(repo, at="07:13")
    assert result["ok"] is True
    assert "core/operations/pulse/run-pulse.sh" in result["written"]
    wrapper = repo / "core/operations/pulse/run-pulse.sh"
    assert wrapper.exists()
    assert os.access(wrapper, os.X_OK)
    # cron line carries the requested time (minute hour) and never auto-enables
    assert result["cron_line"].startswith("13 7 * * *")
    assert result["run_at"] == "07:13"
    assert any("yours to enable" in line.lower() for line in result["activation"])


def test_pulse_install_rejects_bad_time(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    pulse_mod.init(repo)
    result = pulse_mod.install(repo, at="25:00")
    assert result["ok"] is False
    assert "out of range" in result["summary"] or "HH:MM" in result["summary"]


def test_pulse_install_refuses_overwrite_without_force(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    pulse_mod.init(repo)
    pulse_mod.install(repo)
    again = pulse_mod.install(repo)
    assert again["ok"] is False
    forced = pulse_mod.install(repo, force=True)
    assert forced["ok"] is True


def test_pulse_install_wrapper_is_valid_bash(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    pulse_mod.init(repo)
    pulse_mod.install(repo)
    wrapper = repo / "core/operations/pulse/run-pulse.sh"
    proc = subprocess.run(["bash", "-n", str(wrapper)], capture_output=True, text=True, timeout=15)
    assert proc.returncode == 0, proc.stderr


def test_pulse_install_wrapper_assembles_bundle_from_collectors(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    pulse_mod.init(repo)
    pulse_mod.install(repo)
    # the example collector is a real, contract-following collector
    proc = subprocess.run(
        ["bash", str(repo / "core/operations/pulse/run-pulse.sh"), "2026-06-13"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    bundle_path = repo / "core/operations/pulse/data/2026-06-13.json"
    assert bundle_path.exists()
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle["date"] == "2026-06-13"
    assert "example" in bundle["collectors"]
    assert bundle["collectors"]["example"]["date"] == "2026-06-13"
