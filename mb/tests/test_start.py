"""``mb start`` runtime handoff."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from mb import start as start_mod
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()


def _with_claude(name: str) -> str:
    if name == "claude":
        return "/usr/local/bin/claude"
    return shutil.which(name) or ""


def _without_claude(name: str) -> str:
    if name == "claude":
        return ""
    return shutil.which(name) or ""


def test_start_json_prints_ready_handoff(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["start", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert report["handoff_ready"] is True
    assert report["runtime"]["found"] is True
    assert report["runtime"]["skill_wiring"]["ok"] is True
    assert report["command"]["argv"] == ["claude"]
    assert report["command"]["display"].endswith(" && claude")
    assert report["command"]["follow_up"] == "/start"
    assert report["launch"]["requested"] is False


def test_start_degrades_when_claude_is_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(start_mod, "_which", _without_claude)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["start", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    report = json.loads(result.stdout)
    assert report["handoff_ready"] is False
    claude_check = next(check for check in report["checks"] if check["name"] == "claude_code")
    assert claude_check["ok"] is False
    assert "Install Claude Code" in claude_check["repair"]


def test_start_asks_for_repo_when_path_is_not_business_repo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)

    result = runner.invoke(app, ["start", "--repo", str(tmp_path)])

    assert result.exit_code == 1
    assert "mb start" in result.stdout
    assert "--repo /path/to/business-repo" in result.stdout


def test_start_launch_is_blocked_outside_interactive_terminal(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)
    monkeypatch.setattr(start_mod, "_is_interactive_terminal", lambda: False)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["start", "--repo", str(repo), "--launch", "--json"])

    assert result.exit_code == 1
    report = json.loads(result.stdout)
    assert report["handoff_ready"] is True
    assert report["launch"]["requested"] is True
    assert report["launch"]["attempted"] is False
    assert "interactive terminal" in report["launch"]["blocked_reason"]


def test_start_launches_when_explicit_and_interactive(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)
    monkeypatch.setattr(start_mod, "_is_interactive_terminal", lambda: True)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    launched: dict[str, Any] = {}

    def fake_launch(path: Path) -> int:
        launched["path"] = str(path)
        return 0

    monkeypatch.setattr(start_mod, "_launch_claude", fake_launch)

    result = runner.invoke(app, ["start", "--repo", str(repo), "--launch", "--json"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert launched["path"] == str(repo.resolve())
    assert report["launch"]["attempted"] is True
    assert report["launch"]["returncode"] == 0
