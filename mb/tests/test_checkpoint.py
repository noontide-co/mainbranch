"""``mb checkpoint`` planning contract tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from mb import checkpoint as checkpoint_mod
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )


def _business_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial")
    return repo


def test_checkpoint_plan_clean_repo_returns_clean(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is True
    assert report["status"] == "clean"
    assert report["has_changes"] is False
    assert report["changes"] == []
    assert report["proposal"] is None


def test_checkpoint_plan_classifies_dirty_business_files(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)
    (repo / "core" / "offer.md").write_text("# Offer\n", encoding="utf-8")
    (repo / "decisions" / "2026-05-05-test.md").write_text("# Decision\n", encoding="utf-8")
    (repo / "campaigns" / "paid.md").write_text("# Campaign\n", encoding="utf-8")

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is True
    assert report["status"] == "ready"
    assert report["summary"]["changed_files"] == 3
    assert report["summary"]["surfaces"] == {
        "core": 1,
        "campaigns": 1,
        "decisions": 1,
    }
    assert report["proposal"]["message"] == "[checkpoint] Update core, campaigns, and decisions"
    paths = {change["path"] for change in report["changes"]}
    assert paths == {
        "core/offer.md",
        "decisions/2026-05-05-test.md",
        "campaigns/paid.md",
    }


def test_checkpoint_cli_json_contract(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)
    (repo / "research" / "market.md").write_text("# Market\n", encoding="utf-8")

    result = runner.invoke(app, ["checkpoint", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ready"
    assert payload["mode"] == "beginner"
    assert payload["summary"]["surfaces"] == {"research": 1}
    assert payload["proposal"]["message"] == "[checkpoint] Update research"


def test_checkpoint_blocks_env_and_secret_like_content(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)
    (repo / ".env").write_text("API_KEY=super-secret\n", encoding="utf-8")
    (repo / "core" / "credentials.md").write_text(
        "Authorization: Bearer abcdefghijklmnop\n",
        encoding="utf-8",
    )
    _git(repo, "add", "-f", ".env")

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is False
    assert report["status"] == "blocked"
    codes = {block["code"] for block in report["safety"]["blocks"]}
    assert "env_file" in codes
    assert "secret_like_content" in codes
    assert report["proposal"] is None


def test_checkpoint_blocks_service_account_json(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)
    (repo / "core" / "service-account.json").write_text(
        '{"type":"service_account","private_key":"-----BEGIN PRIVATE KEY-----"}',
        encoding="utf-8",
    )

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is False
    assert report["safety"]["blocks"][0]["code"] == "service_account_json"


def test_checkpoint_blocks_forced_local_bridge_files(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)
    _git(repo, "add", "-f", ".claude/settings.local.json")

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is False
    assert report["status"] == "blocked"
    assert report["safety"]["blocks"][0]["code"] == "local_bridge_file"


def test_checkpoint_blocks_engine_repo(tmp_path: Path) -> None:
    repo = tmp_path / "engine"
    (repo / "mb" / "mb").mkdir(parents=True)
    (repo / "mb" / "pyproject.toml").write_text("[project]\nname='mainbranch'\n")
    (repo / "mb" / "mb" / "cli.py").write_text("# cli\n")
    _git(repo, "init", "-q", "-b", "main")
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is False
    assert report["status"] == "blocked"
    assert report["safety"]["blocks"][0]["code"] == "engine_repo"


def test_checkpoint_rejects_invalid_mode(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)

    result = runner.invoke(app, ["checkpoint", "--repo", str(repo), "--mode", "auto", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "error"
    assert "mode must be beginner or concern" in payload["errors"][0]


def test_checkpoint_commit_requires_yes_after_plan_review(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)
    (repo / "core" / "offer.md").write_text("# Offer\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--repo",
            str(repo),
            "--message",
            "[checkpoint] Update offer",
            "--json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "approval_required"
    assert payload["committed"] is False
    assert "pass --yes" in payload["errors"][0]


def test_checkpoint_commit_saves_readable_checkpoint(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)
    (repo / "core" / "offer.md").write_text("# Offer\nUpdated\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--repo",
            str(repo),
            "--message",
            "[checkpoint] Update offer",
            "--yes",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "committed"
    assert payload["committed"] is True
    assert payload["commit"]["message"] == "[checkpoint] Update offer"
    assert "core/offer.md" in payload["commit"]["body"]
    assert payload["commit"]["sha"]
    assert _git(repo, "status", "--porcelain").stdout == ""
    log = _git(repo, "log", "-1", "--pretty=%B").stdout
    assert "[checkpoint] Update offer" in log
    assert "Changed:\n- core/offer.md" in log


def test_checkpoint_commit_refuses_blocked_plan_without_commit(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)
    (repo / ".env").write_text("API_KEY=super-secret\n", encoding="utf-8")
    _git(repo, "add", "-f", ".env")

    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--repo",
            str(repo),
            "--message",
            "[checkpoint] Unsafe",
            "--yes",
            "--json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["committed"] is False
    assert _git(repo, "log", "--oneline").stdout.count("\n") == 1


def test_checkpoint_commit_clean_repo_is_noop(tmp_path: Path) -> None:
    repo = _business_repo(tmp_path)

    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--repo",
            str(repo),
            "--message",
            "[checkpoint] Nothing",
            "--yes",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "clean"
    assert payload["committed"] is False
