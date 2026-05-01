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
