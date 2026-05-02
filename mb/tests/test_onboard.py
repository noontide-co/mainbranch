"""``mb onboard`` adaptive setup flow."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

from mb import onboard as onboard_mod
from mb.cli import app

runner = CliRunner()


def _tool_path(name: str) -> str:
    if name == "git":
        return shutil.which("git") or ""
    return ""


def test_onboard_yes_creates_repo_and_reports_next_steps(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    repo = tmp_path / "acme"

    result = onboard_mod.run(
        path=str(repo),
        name="Acme Brewing",
        mode="new",
        level="beginner",
    )

    assert result["ok"] is True
    assert result["action"] == "created"
    assert result["level"] == "beginner"
    assert (repo / "CLAUDE.md").exists()
    assert (repo / ".claude" / "skills" / "start" / "SKILL.md").exists()
    assert result["skill_wiring"]["ok"] is True
    assert result["next_steps"] == [f"cd {repo.resolve()}", "claude", "/start"]
    assert any("Claude Code" in warning for warning in result["warnings"])
    assert any(
        "gh auth login" in warning or "GitHub CLI" in warning for warning in result["warnings"]
    )


def test_onboard_rerun_is_idempotent(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    repo = tmp_path / "acme"

    first = onboard_mod.run(path=str(repo), name="Acme", mode="new", level="auto")
    second = onboard_mod.run(path=str(repo), name="Acme", mode="auto", level="auto")

    assert first["action"] == "created"
    assert second["action"] == "repaired"
    assert second["ok"] is True
    assert second["repo"]["before"]["claude_md"] is True
    assert (repo / "CLAUDE.md").exists()


def test_onboard_connect_repairs_existing_initialized_repo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    repo = tmp_path / "acme"
    onboard_mod.run(path=str(repo), name="Acme", mode="new", level="power")
    settings = repo / ".claude" / "settings.local.json"
    settings.unlink()

    result = onboard_mod.run(path=str(repo), name="", mode="connect", level="power")

    assert result["ok"] is True
    assert result["action"] == "repaired"
    assert result["business_name"] == ""
    assert settings.exists()
    assert result["skill_wiring"]["ok"] is True


def test_onboard_connect_missing_repo_routes_to_doctor(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    repo = tmp_path / "missing"

    result = onboard_mod.run(path=str(repo), name="", mode="connect", level="power")

    assert result["ok"] is False
    assert "cannot connect missing repo" in result["errors"][0]
    assert result["doctor_command"].startswith("mb doctor ")


def test_onboard_connect_uninitialized_repo_explains_repair(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    repo = tmp_path / "plain"
    repo.mkdir()

    result = onboard_mod.run(path=str(repo), name="", mode="connect", level="power")

    assert result["ok"] is False
    assert any("does not look like a Main Branch repo" in error for error in result["errors"])
    assert result["doctor_command"].startswith("mb doctor ")
    assert result["created"] == []
    assert not (repo / ".claude").exists()
    assert not (repo / ".gitignore").exists()


def test_onboard_cli_noninteractive_requires_yes(monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "is_interactive", lambda: False)

    result = runner.invoke(app, ["onboard"])

    assert result.exit_code == 2
    assert "Use `mb onboard --yes`" in result.stderr


def test_onboard_cli_yes_json_smoke(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    monkeypatch.setattr(onboard_mod, "is_interactive", lambda: False)
    repo = tmp_path / "acme"

    result = runner.invoke(
        app,
        [
            "onboard",
            "--yes",
            "--name",
            "Acme Brewing",
            "--path",
            str(repo),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["path"] == str(repo.resolve())
    assert payload["next_steps"][-1] == "/start"


def test_onboard_cli_interactive_path_renders_clear_labels(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    monkeypatch.setattr(onboard_mod, "is_interactive", lambda: True)
    repo = tmp_path / "interactive"

    result = runner.invoke(
        app,
        ["onboard"],
        input=f"beginner\nnew\nInteractive Business\n{repo}\n",
    )

    assert result.exit_code == 0
    assert "Main Branch works because the business lives somewhere durable" in result.stdout
    assert "new/connect/auto" in result.stdout
    assert "repo:" in result.stdout
    assert "interactive" in result.stdout
    assert "level / action: beginner / created" in result.stdout
    assert "path: beginner / created" not in result.stdout
    assert "Show the short why" not in result.stdout
