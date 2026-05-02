"""Smoke tests for the Typer CLI surface."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

import mb.cli as cli_mod
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
    assert "Choose a trail" not in result.stdout


def test_bare_mb_non_tty_keeps_plain_help(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_mod, "_is_interactive_terminal", lambda: False)

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Choose a trail" not in result.stdout


def test_bare_mb_tty_shows_launch_screen(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_mod, "_is_interactive_terminal", lambda: True)

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "Choose a trail" in result.stdout
    assert "mb onboard" in result.stdout
    assert "mb status" in result.stdout
    assert "mb status        business/repo briefing (coming in v0.2)" not in result.stdout
    assert "mb start" in result.stdout
    assert "mb doctor" in result.stdout
    assert "mb --help" in result.stdout
    assert "Usage:" not in result.stdout


def test_plain_escape_hatch_keeps_help_in_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_mod, "_is_interactive_terminal", lambda: True)

    result = runner.invoke(app, ["--plain"])

    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Choose a trail" not in result.stdout


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
