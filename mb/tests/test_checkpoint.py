"""``mb checkpoint`` planning contract tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from mb import checkpoint as checkpoint_mod
from mb.checkpoint_verbs import registry as verb_registry
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()


def _git(
    repo: Path,
    *args: str,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _business_repo(tmp_path: Path, monkeypatch: Any) -> Path:
    _install_mb_shim(tmp_path, monkeypatch)
    repo = tmp_path / "acme"
    init_run(path=str(repo), name="Acme")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "[added] business scaffold")
    return repo


def _install_mb_shim(tmp_path: Path, monkeypatch: Any) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    shim = bin_dir / "mb"
    package_root = Path(__file__).resolve().parents[1]
    shim.write_text(
        f'#!/bin/sh\nPYTHONPATH="{package_root}" exec "{sys.executable}" -m mb "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    return bin_dir


def _commit_file(repo: Path, relative_path: str, content: str, message: str) -> None:
    target = repo / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    result = _git(repo, "add", relative_path)
    assert result.returncode == 0, result.stderr
    result = _git(repo, "commit", "-m", message)
    assert result.returncode == 0, result.stderr


def test_checkpoint_resolves_current_absolute_mb_entrypoint(
    tmp_path: Path, monkeypatch: Any
) -> None:
    current_bin = tmp_path / "venv" / "bin"
    current_bin.mkdir(parents=True)
    current_mb = current_bin / "mb"
    current_mb.write_text("#!/bin/sh\n", encoding="utf-8")
    current_mb.chmod(0o755)
    older_bin = tmp_path / "global" / "bin"
    older_bin.mkdir(parents=True)
    older_mb = older_bin / "mb"
    older_mb.write_text("#!/bin/sh\n", encoding="utf-8")
    older_mb.chmod(0o755)
    monkeypatch.setattr(sys, "argv", [str(current_mb), "checkpoint", "--install-hook"])
    monkeypatch.setenv("PATH", f"{older_bin}{os.pathsep}{os.environ.get('PATH', '')}")

    assert checkpoint_mod._resolved_mb_path() == str(current_mb.resolve())


def test_checkpoint_plan_clean_repo_returns_clean(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is True
    assert report["status"] == "clean"
    assert report["has_changes"] is False
    assert report["changes"] == []
    assert report["proposal"] is None


def test_checkpoint_verb_registry_matches_operator_contract() -> None:
    registry = verb_registry()

    assert list(registry) == [
        "added",
        "updated",
        "decided",
        "opened",
        "closed",
        "drafted",
        "shipped",
        "connected",
        "ran",
        "fixed",
    ]
    assert registry["opened"].default_loop == "decide"
    assert registry["closed"].default_loop == "reflect"
    assert registry["connected"].channel_hint == "ops"


def test_checkpoint_plan_classifies_dirty_business_files(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / "core" / "offer.md").write_text("# Offer\n", encoding="utf-8")
    (repo / "decisions" / "2026-05-05-test.md").write_text("# Decision\n", encoding="utf-8")
    (repo / "pushes" / "paid.md").write_text("# Push\n", encoding="utf-8")

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is True
    assert report["status"] == "ready"
    assert report["summary"]["changed_files"] == 3
    assert report["summary"]["surfaces"] == {
        "core": 1,
        "pushes": 1,
        "decisions": 1,
    }
    assert report["proposal"]["message"] == "[added] core, pushes, and decisions"
    assert report["proposal"]["verb"] == "added"
    assert report["proposal"]["loop"] == "sense"
    assert report["proposal"]["validation"]["ok"] is True
    paths = {change["path"] for change in report["changes"]}
    assert paths == {
        "core/offer.md",
        "decisions/2026-05-05-test.md",
        "pushes/paid.md",
    }


def test_checkpoint_cli_json_contract(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / "research" / "market.md").write_text("# Market\n", encoding="utf-8")

    result = runner.invoke(app, ["checkpoint", "--repo", str(repo), "--plan", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ready"
    assert payload["mode"] == "beginner"
    assert payload["summary"]["surfaces"] == {"research": 1}
    assert payload["proposal"]["message"] == "[added] market.md"
    assert (
        payload["proposal"]["reason"] == "Chosen because new durable business context was created."
    )


def test_checkpoint_validate_accepts_business_verb_json() -> None:
    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--validate",
            "[opened] bet workshop-waitlist -- target 40 signups",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "valid"
    assert payload["validation"]["parsed"]["verb"] == "opened"
    assert payload["validation"]["parsed"]["loop"] == "decide"
    assert payload["validation"]["acceptable_for_beginner"] is True


def test_checkpoint_validate_rejects_vague_subject() -> None:
    result = runner.invoke(app, ["checkpoint", "--validate", "WIP", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid"
    codes = {error["code"] for error in payload["validation"]["errors"]}
    assert "vague_subject" in codes
    assert "missing_prefix" in codes


def test_checkpoint_validate_rejects_private_path_and_secret_like_subject() -> None:
    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--validate",
            "[updated] /Users/devon/private.md -- api_key=abcdefghi",
            "--json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    codes = {error["code"] for error in payload["validation"]["errors"]}
    assert "private_local_path" in codes
    assert "secret_like_subject" in codes


def test_checkpoint_validate_reads_stdin() -> None:
    result = runner.invoke(
        app,
        ["checkpoint", "--validate", "-", "--json"],
        input="[ran] mb update -- 0.2.6 to 0.3.0\n",
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["validation"]["parsed"]["verb"] == "ran"
    assert payload["validation"]["parsed"]["channel_hint"] == "ops"


def test_checkpoint_hook_status_install_and_uninstall(tmp_path: Path) -> None:
    repo = tmp_path / "manual"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")

    missing = checkpoint_mod.hook_status(repo)
    assert missing["state"] == "missing"
    assert missing["safe_to_install"] is True

    installed = checkpoint_mod.install_commit_hook(repo)
    assert installed["ok"] is True
    assert installed["state"] == "installed"
    assert Path(installed["hook"]).exists()

    uninstalled = checkpoint_mod.uninstall_commit_hook(repo)
    assert uninstalled["ok"] is True
    assert uninstalled["changed"] is True
    assert not Path(installed["hook"]).exists()


def test_checkpoint_hook_preserves_existing_user_hook(tmp_path: Path) -> None:
    repo = tmp_path / "manual"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    hook = repo / ".git" / "hooks" / "commit-msg"
    hook.write_text("#!/bin/sh\necho user hook\n", encoding="utf-8")

    result = checkpoint_mod.install_commit_hook(repo)

    assert result["ok"] is False
    assert result["state"] == "blocked_existing_hook"
    assert hook.read_text(encoding="utf-8") == "#!/bin/sh\necho user hook\n"


def test_checkpoint_hook_skips_engine_repo(tmp_path: Path) -> None:
    repo = tmp_path / "engine"
    (repo / "mb" / "mb").mkdir(parents=True)
    (repo / "mb" / "pyproject.toml").write_text("[project]\nname='mainbranch'\n")
    (repo / "mb" / "mb" / "cli.py").write_text("# cli\n")
    _git(repo, "init", "-q", "-b", "main")

    result = checkpoint_mod.install_commit_hook(repo)

    assert result["ok"] is True
    assert result["state"] == "engine_repo"
    assert not (repo / ".git" / "hooks" / "commit-msg").exists()


def test_checkpoint_hook_rejects_vague_raw_git_commit(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / "core" / "offer.md").write_text("# Offer\nUpdated\n", encoding="utf-8")
    _git(repo, "add", "core/offer.md")

    result = _git(repo, "commit", "-m", "WIP")

    assert result.returncode != 0
    assert "not business-readable" in result.stderr
    assert _git(repo, "status", "--porcelain").stdout


def test_checkpoint_hook_accepts_business_raw_git_commit(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / "core" / "offer.md").write_text("# Offer\nUpdated\n", encoding="utf-8")
    _git(repo, "add", "core/offer.md")

    result = _git(repo, "commit", "-m", "[updated] offer.md -- clarified guarantee")

    assert result.returncode == 0
    assert (
        "[updated] offer.md -- clarified guarantee" in _git(repo, "log", "-1", "--pretty=%s").stdout
    )


def test_checkpoint_hook_uses_installed_mb_when_runtime_path_is_minimal(
    tmp_path: Path, monkeypatch: Any
) -> None:
    bin_dir = _install_mb_shim(tmp_path, monkeypatch)
    repo = _business_repo(tmp_path, monkeypatch)
    hook = (repo / ".git" / "hooks" / "commit-msg").read_text(encoding="utf-8")
    assert f"MB_BIN={bin_dir / 'mb'}" in hook
    (repo / "core" / "offer.md").write_text("# Offer\nUpdated\n", encoding="utf-8")
    _git(repo, "add", "core/offer.md")

    result = _git(
        repo,
        "commit",
        "-m",
        "[updated] offer.md -- clarified guarantee",
        env={**os.environ, "PATH": "/usr/bin:/bin:/usr/sbin:/sbin"},
    )

    assert result.returncode == 0, result.stderr


def test_checkpoint_hook_allows_no_ff_merge_auto_message(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    _commit_file(repo, "core/offer.md", "# Offer\nMain\n", "[updated] offer.md")
    result = _git(repo, "checkout", "-b", "feature")
    assert result.returncode == 0, result.stderr
    _commit_file(repo, "research/feature.md", "# Feature\n", "[added] feature.md")
    result = _git(repo, "checkout", "main")
    assert result.returncode == 0, result.stderr
    _commit_file(repo, "research/main.md", "# Main\n", "[added] main.md")

    result = _git(repo, "merge", "--no-ff", "feature")

    assert result.returncode == 0, result.stderr
    assert _git(repo, "log", "-1", "--pretty=%s").stdout.startswith("Merge ")


def test_checkpoint_hook_allows_revert_auto_message(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    _commit_file(repo, "core/offer.md", "# Offer\nBefore\n", "[updated] offer.md")
    _commit_file(
        repo,
        "core/offer.md",
        "# Offer\nAfter\n",
        "[updated] offer.md -- changed for revert",
    )

    result = _git(repo, "revert", "HEAD", "--no-edit")

    assert result.returncode == 0, result.stderr
    assert _git(repo, "log", "-1", "--pretty=%s").stdout.startswith("Revert ")


def test_checkpoint_hook_allows_rebase_helper_subjects(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)

    for index, subject in enumerate(
        [
            "fixup! [updated] offer.md",
            "squash! [updated] offer.md",
            "amend! [updated] offer.md",
        ],
        start=1,
    ):
        _commit_file(
            repo,
            "research/rebase-helper.md",
            f"# Helper\n{index}\n",
            subject,
        )

    assert "amend! [updated] offer.md" in _git(repo, "log", "-1", "--pretty=%s").stdout


def test_checkpoint_blocks_env_and_secret_like_content(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
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


def test_checkpoint_blocks_service_account_json(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / "core" / "service-account.json").write_text(
        '{"type":"service_account","private_key":"-----BEGIN PRIVATE KEY-----"}',
        encoding="utf-8",
    )

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is False
    assert report["safety"]["blocks"][0]["code"] == "service_account_json"


def test_checkpoint_blocks_forced_local_bridge_files(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    _git(repo, "add", "-f", ".claude/settings.local.json")

    report = checkpoint_mod.plan(repo)

    assert report["ok"] is False
    assert report["status"] == "blocked"
    assert report["safety"]["blocks"][0]["code"] == "local_bridge_file"


def test_checkpoint_blocks_forced_claude_code_worktrees(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    worktree_state = repo / ".claude" / "worktrees" / "session" / "state.json"
    worktree_state.parent.mkdir(parents=True)
    worktree_state.write_text("{}", encoding="utf-8")
    _git(repo, "add", "-f", ".claude/worktrees/session/state.json")

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


def test_checkpoint_rejects_invalid_mode(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)

    result = runner.invoke(app, ["checkpoint", "--repo", str(repo), "--mode", "auto", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "error"
    assert "mode must be beginner or concern" in payload["errors"][0]


def test_checkpoint_commit_requires_yes_after_plan_review(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / "core" / "offer.md").write_text("# Offer\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--repo",
            str(repo),
            "--message",
            "[updated] offer.md",
            "--json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "approval_required"
    assert payload["committed"] is False
    assert "pass --yes" in payload["errors"][0]


def test_checkpoint_commit_saves_readable_checkpoint(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / "core" / "offer.md").write_text("# Offer\nUpdated\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--repo",
            str(repo),
            "--message",
            "[updated] offer.md",
            "--yes",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "committed"
    assert payload["committed"] is True
    assert payload["commit"]["message"] == "[updated] offer.md"
    assert "core/offer.md" in payload["commit"]["body"]
    assert payload["commit"]["sha"]
    assert _git(repo, "status", "--porcelain").stdout == ""
    log = _git(repo, "log", "-1", "--pretty=%B").stdout
    assert "[updated] offer.md" in log
    assert "Changed:\n- core/offer.md" in log


def test_checkpoint_commit_rejects_invalid_business_message(
    tmp_path: Path, monkeypatch: Any
) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
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

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "invalid_message"
    assert payload["committed"] is False
    assert payload["validation"]["errors"][0]["code"] == "generic_checkpoint_prefix"
    assert _git(repo, "status", "--porcelain").stdout


def test_checkpoint_commit_refuses_blocked_plan_without_commit(
    tmp_path: Path, monkeypatch: Any
) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / ".env").write_text("API_KEY=super-secret\n", encoding="utf-8")
    _git(repo, "add", "-f", ".env")

    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--repo",
            str(repo),
            "--message",
            "[updated] unsafe",
            "--yes",
            "--json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["committed"] is False
    assert _git(repo, "log", "--oneline").stdout.count("\n") == 1


def test_checkpoint_commit_clean_repo_is_noop(tmp_path: Path, monkeypatch: Any) -> None:
    repo = _business_repo(tmp_path, monkeypatch)

    result = runner.invoke(
        app,
        [
            "checkpoint",
            "--repo",
            str(repo),
            "--message",
            "[ran] daily checkpoint",
            "--yes",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "clean"
    assert payload["committed"] is False


def test_checkpoint_status_reports_recent_checkpoint_and_pending_work(
    tmp_path: Path, monkeypatch: Any
) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / "core" / "offer.md").write_text("# Offer\nUpdated\n", encoding="utf-8")
    checkpoint_mod.commit(
        repo,
        message="[updated] offer.md",
        yes=True,
    )
    (repo / "research" / "next.md").write_text("# Next\n", encoding="utf-8")

    result = runner.invoke(app, ["checkpoint", "--repo", str(repo), "--status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["recent"][0]["subject"] == "[updated] offer.md"
    assert payload["recent"][0]["recognized_as"] == "business_verb"
    assert payload["recent"][0]["verb"] == "updated"
    assert payload["recent"][0]["loop"] == "sense"
    assert payload["pending"]["status"] == "ready"
    assert payload["pending"]["summary"]["surfaces"] == {"research": 1}


def test_checkpoint_status_preserves_legacy_checkpoint_subjects(
    tmp_path: Path, monkeypatch: Any
) -> None:
    repo = _business_repo(tmp_path, monkeypatch)
    (repo / "core" / "offer.md").write_text("# Offer\nUpdated\n", encoding="utf-8")
    _git(repo, "add", "core/offer.md")
    _git(repo, "commit", "--no-verify", "-m", "[checkpoint] Update offer")

    payload = checkpoint_mod.status(repo)

    assert payload["ok"] is True
    assert payload["recent"][0]["subject"] == "[checkpoint] Update offer"
    assert payload["recent"][0]["recognized_as"] == "legacy_checkpoint"
