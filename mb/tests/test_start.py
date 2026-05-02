"""``mb start`` runtime handoff."""

from __future__ import annotations

import json
import shlex
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
    assert "update" in report


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


def test_start_required_update_blocks_handoff_and_surfaces_json(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)
    monkeypatch.setattr(
        start_mod,
        "package_update_status",
        lambda repo: {
            "installed": "0.1.0",
            "latest": "0.2.1",
            "minimum_supported": "0.2.0",
            "severity": "required",
            "command": "pipx upgrade mainbranch",
            "post_update_commands": ["mb skill link --repo .", "mb doctor"],
            "reason": (
                "Installed version predates mb update and the current skill-link repair flow."
            ),
        },
    )
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["start", "--repo", str(repo), "--json"])

    assert result.exit_code == 1
    report = json.loads(result.stdout)
    assert report["handoff_ready"] is False
    assert report["update"]["severity"] == "required"
    update_check = next(check for check in report["checks"] if check["name"] == "mainbranch_update")
    assert update_check["severity"] == "error"
    assert update_check["repair"] == "pipx upgrade mainbranch"

    human_result = runner.invoke(app, ["start", "--repo", str(repo)])
    assert human_result.exit_code == 1
    assert "Update required." in human_result.stdout
    assert "pipx upgrade mainbranch" in human_result.stdout


def test_start_recommended_update_keeps_handoff_ready(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)
    monkeypatch.setattr(
        start_mod,
        "package_update_status",
        lambda repo: {
            "installed": "0.2.0",
            "latest": "0.2.1",
            "minimum_supported": "0.2.0",
            "severity": "recommended",
            "command": "mb update",
            "post_update_commands": ["mb skill link --repo .", "mb doctor"],
            "reason": "A newer compatible Main Branch package is available.",
        },
    )
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["start", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    report = json.loads(result.stdout)
    assert report["handoff_ready"] is True
    assert report["update"]["severity"] == "recommended"
    update_check = next(check for check in report["checks"] if check["name"] == "mainbranch_update")
    assert update_check["severity"] == "warn"


def test_start_asks_for_repo_when_path_is_not_business_repo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)

    result = runner.invoke(app, ["start", "--repo", str(tmp_path)])

    assert result.exit_code == 1
    assert "mb start" in result.stdout
    assert "--repo /path/to/business-repo" in result.stdout


def test_start_json_launch_is_rejected_without_launching(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)
    monkeypatch.setattr(start_mod, "_is_interactive_terminal", lambda: True)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    def fail_launch(path: Path) -> int:
        raise AssertionError(f"should not launch in JSON mode: {path}")

    monkeypatch.setattr(start_mod, "_launch_claude", fail_launch)

    result = runner.invoke(app, ["start", "--repo", str(repo), "--launch", "--json"])

    assert result.exit_code == 2
    report = json.loads(result.stdout)
    assert report["handoff_ready"] is True
    assert report["launch"]["requested"] is True
    assert report["launch"]["attempted"] is False
    assert "--json" in report["launch"]["blocked_reason"]
    assert "--launch" in report["errors"][0]


def test_start_launch_is_blocked_outside_interactive_terminal(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(start_mod, "_which", _with_claude)
    monkeypatch.setattr(start_mod, "_is_interactive_terminal", lambda: False)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["start", "--repo", str(repo), "--launch"])

    assert result.exit_code == 1
    assert "Launch skipped" in result.stdout
    assert "interactive terminal" in result.stdout


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

    result = runner.invoke(app, ["start", "--repo", str(repo), "--launch"])

    assert result.exit_code == 0
    assert launched["path"] == str(repo.resolve())
    assert "Launch" in result.stdout
    assert "claude exited 0" in result.stdout


def test_start_display_command_is_os_aware(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "path with spaces"

    monkeypatch.setattr(start_mod.os, "name", "posix")
    assert start_mod._display_command(repo) == f"cd {shlex.quote(str(repo))} && claude"

    monkeypatch.setattr(start_mod.os, "name", "nt")
    assert start_mod._display_command(repo).startswith("cd /d ")
    assert start_mod._display_command(repo).endswith(" && claude")
