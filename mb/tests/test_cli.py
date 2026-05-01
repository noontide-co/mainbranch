"""Smoke tests for the Typer CLI surface."""

from __future__ import annotations

from typer.testing import CliRunner

from mb import __version__
from mb.cli import app

runner = CliRunner()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_help_runs() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "scaffolds" in result.stdout.lower() or "main branch" in result.stdout.lower()


def test_skill_list_runs() -> None:
    result = runner.invoke(app, ["skill", "list"])
    assert result.exit_code == 0
    assert "start" in result.stdout.splitlines()


def test_skill_link_wires_repo(tmp_path) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    result = runner.invoke(app, ["skill", "link", "--repo", str(repo), "--json"])
    assert result.exit_code == 0
    assert (repo / ".claude" / "settings.local.json").exists()
    assert (repo / ".claude" / "skills" / "start" / "SKILL.md").exists()
