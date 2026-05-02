"""``mb status`` daily briefing."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

from mb import status as status_mod
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()


def _without_github_or_claude(name: str) -> str:
    if name in {"gh", "claude"}:
        return ""
    return shutil.which(name) or ""


def test_status_json_degrades_without_github(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    (repo / "decisions" / "2026-05-01-pricing.md").write_text(
        "---\ndate: 2026-05-01\nstatus: accepted\n---\n\n# Pricing\n",
        encoding="utf-8",
    )
    (repo / "research" / "2026-05-01-market.md").write_text(
        "---\ndate: 2026-05-01\nsource: desk\n---\n\n# Market\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["status", str(repo), "--json"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert report["repo"]["looks_like_mainbranch_repo"] is True
    assert report["runtime"]["skill_wiring"]["ok"] is True
    assert report["github"]["authenticated"] is False
    assert report["brain"]["counts"]["decisions"] == 1
    assert report["brain"]["recent_research"][0]["title"] == "Market"
    assert "readiness" in report


def test_status_human_output_mentions_core_sections(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["status", str(repo)])

    assert result.exit_code == 0
    assert "mb status" in result.stdout
    assert "Repo" in result.stdout
    assert "Runtime" in result.stdout
    assert "GitHub" in result.stdout
    assert "Next" in result.stdout


def test_status_detects_non_business_repo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(status_mod, "_which", _without_github_or_claude)
    report = status_mod.run(path=str(tmp_path))

    assert report["repo"]["looks_like_mainbranch_repo"] is False
    assert report["readiness"]["level"] == "not_ready"
    assert any("mb init" in action for action in report["readiness"]["next_actions"])
