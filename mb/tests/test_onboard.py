"""``mb onboard`` adaptive setup flow."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

from mb import onboard as onboard_mod
from mb import status as status_mod
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
    onboard_mod.run(
        path=str(repo),
        name="Acme",
        mode="new",
        level="power",
        team_size="solo",
        business_type="coaching",
        success_stage="working",
        desired_outcome="usable core reference",
    )
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
    assert (repo / ".mb" / "onboarding.json").exists()
    assert payload["onboarding"]["summary"]["status"] == "in_progress"


def test_onboard_status_reports_partial_small_team_progress(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    repo = tmp_path / "acme"
    onboard_mod.run(
        path=str(repo),
        name="Acme",
        mode="new",
        level="power",
        team_size="small-team",
        business_type="agency",
        success_stage="working",
        desired_outcome="usable core reference",
    )
    (repo / "core" / "offer.md").write_text("# Offer\n", encoding="utf-8")

    result = runner.invoke(app, ["onboard", "status", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["state_exists"] is True
    assert payload["profile"]["team_size"] == "small_team"
    assert payload["summary"]["status"] == "in_progress"
    assert payload["summary"]["next_step"] == "core_reference"
    assert "audience" in payload["summary"]["missing_inputs"]
    team_step = next(step for step in payload["checklist"] if step["id"] == "team_layer")
    assert team_step["title"] == "Small-team GitHub loop"
    assert team_step["required"] is True


def test_onboard_plan_updates_profile_without_raw_business_state(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    repo = tmp_path / "solo"
    onboard_mod.run(path=str(repo), name="Solo Co", mode="new", level="power")

    result = runner.invoke(
        app,
        [
            "onboard",
            "plan",
            "--repo",
            str(repo),
            "--team-size",
            "solo",
            "--business-type",
            "coaching",
            "--success-stage",
            "successful",
            "--desired-outcome",
            "document the core reference",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["profile"]["success_stage"] == "successful"
    state = json.loads((repo / ".mb" / "onboarding.json").read_text(encoding="utf-8"))
    assert "never_store_here" in state["contract"]
    assert "chat transcripts" in " ".join(state["contract"]["never_store_here"])


def test_status_includes_onboarding_progress(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(onboard_mod, "_which", _tool_path)
    monkeypatch.setattr(status_mod, "_which", _tool_path)
    repo = tmp_path / "acme"
    onboard_mod.run(
        path=str(repo),
        name="Acme",
        mode="new",
        level="power",
        team_size="solo",
        business_type="coaching",
        success_stage="working",
        desired_outcome="usable core reference",
    )

    report = status_mod.run(path=str(repo))

    assert report["onboarding"]["summary"]["status"] == "in_progress"
    assert any("Collect just enough" in action for action in report["readiness"]["next_actions"])


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
    assert "Connected accounts" in result.stdout
    assert "CLAUDE.md -> Connected accounts" in result.stdout
    assert "Show the short why" not in result.stdout
