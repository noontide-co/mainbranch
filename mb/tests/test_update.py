"""``mb update`` install-mode contract tests."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import __version__
from mb import codex as codex_mod
from mb import engine as engine_mod
from mb import update as update_mod
from mb.cli import app

runner = CliRunner()

# Captured before the autouse stub below replaces it, so the fixture-repo
# tests can run doctor's real Codex checks.
_REAL_CODEX_READINESS = codex_mod.readiness


@pytest.fixture(autouse=True)
def codex_adapter_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        codex_mod,
        "readiness",
        lambda repo: {
            "ok": True,
            "status": "ready",
            "static_ok": True,
            "runtime_ok": True,
            "plugin_ok": True,
            "command_surface_ok": True,
            "slash_commands_ready": True,
            "repair": "",
            "instructions": {
                "ok": True,
                "exists": True,
                "current": True,
                "repair_command": "",
            },
            "plugin_install": {
                "ok": True,
                "state": "ok",
                "plugin_installed": True,
                "plugin_enabled": True,
                "command_files_current": True,
                "command_surface_ok": True,
                "slash_commands_ready": True,
                "slash_commands_likely_loaded": False,
                "slash_commands_restart_required": False,
                "repair": "",
            },
        },
    )


@pytest.fixture(autouse=True)
def plugin_rail_wired(monkeypatch: pytest.MonkeyPatch) -> None:
    # Default: repo is already on the plugin rail, so the #931 follow-up stays
    # quiet. Tests that exercise the symlink-era path override this.
    monkeypatch.setattr(
        update_mod,
        "plugin_wiring_status",
        lambda repo: {
            "wired": True,
            "marketplace_known": True,
            "plugin_enabled": True,
            "settings_path": str(Path(repo) / ".claude" / "settings.json"),
        },
    )
    monkeypatch.setattr(
        update_mod,
        "claude_mainbranch_plugin_status",
        lambda *, expected_version=None, timeout=5.0: {
            "checked": True,
            "ok": True,
            "state": "current",
            "expected_version": expected_version or __version__,
            "installed_version": expected_version or __version__,
            "installed_versions": [expected_version or __version__],
            "enabled_versions": [expected_version or __version__],
            "entries": [],
            "command": "claude plugin list --json",
            "repair": engine_mod.PLUGIN_INSTALL_COMMAND,
            "summary": "Main Branch Claude Code plugin is enabled.",
        },
    )


# Captured before the autouse stub below replaces it, so the probe itself can
# still be unit tested.
_REAL_UV_TOOL_DIR_HOLDS_THIS_INSTALL = update_mod._uv_tool_dir_holds_this_install


@pytest.fixture(autouse=True)
def uv_tool_dir_quiet(monkeypatch: pytest.MonkeyPatch) -> None:
    # `mb update` asks uv for its tool directory when path detection is
    # inconclusive. Tests must never read the developer's or CI runner's uv.
    monkeypatch.setattr(update_mod, "_uv_tool_dir_holds_this_install", lambda: False)


@pytest.fixture(autouse=True)
def pypi_quiet(monkeypatch: pytest.MonkeyPatch) -> None:
    # Every install mode now asks PyPI whether this build is ahead of the latest
    # release (#1022). Tests that care set their own answer; the rest stay off
    # the network and independent of what PyPI currently publishes.
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: None)


def _completed(
    args: list[str],
    *,
    stdout: str = "",
    stderr: str = "",
    returncode: int = 0,
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=args,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


INSTALLER_PREFIXES = (["uv", "tool", "install"], ["uv", "tool", "upgrade"], ["pipx", "upgrade"])


def _installer_calls(calls: list[list[str]]) -> list[list[str]]:
    """Every recorded call that would have replaced an install."""
    return [
        args
        for args in calls
        if any(args[: len(prefix)] == prefix for prefix in INSTALLER_PREFIXES)
    ]


def _surface_refresh_runner(
    calls: list[list[str]],
) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Fake runner that satisfies the surface refresh and records everything."""

    def fake_run(
        args: list[str], *, cwd: Path | None = None, timeout: float = 0.0
    ) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args, stdout=json.dumps({"ok": True, "linked": ["mb-start"], "tracked_changes": []})
            )
        if args[:3] == ["mb", "doctor", "repair"]:
            return _codex_repair_completed(args)
        if args[1:] == ["--version"]:
            return _completed(args, stdout="mb 9.9.9\n")
        return _completed(args)

    return fake_run


def _codex_repair_completed(args: list[str]) -> subprocess.CompletedProcess[str]:
    return _completed(
        args,
        stdout=json.dumps(
            {
                "ok": True,
                "warnings": [],
                "errors": [],
                "actions": [],
                "applied_actions": [],
            }
        ),
    )


def test_run_command_returns_124_on_timeout(monkeypatch: Any) -> None:
    def fake_run(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs["timeout"])

    monkeypatch.setattr("mb.update.subprocess.run", fake_run)

    result = update_mod._run_command(["git", "fetch"], timeout=0.01)

    assert result.returncode == 124
    assert "timed out after" in result.stderr


def test_version_from_mb_command_uses_running_entrypoint(monkeypatch: Any, tmp_path: Path) -> None:
    mb = tmp_path / "mb"
    mb.write_text("#!/bin/sh\n", encoding="utf-8")
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return _completed(args, stdout="mb 0.5.0\n")

    monkeypatch.setattr("mb.update.sys.argv", [str(mb), "update"])
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    assert update_mod._version_from_mb_command() == "0.5.0"
    assert calls == [[str(mb), "--version"]]


def test_update_check_pipx_does_not_run_commands(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return _completed(args)

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(
        update_mod,
        "_release_context",
        lambda version: {
            "version": version,
            "tag": f"oe-v{version}",
            "url": f"https://github.com/noontide-co/mainbranch/releases/tag/oe-v{version}",
            "name": f"Main Branch {version}",
            "published_at": "2026-05-15T00:00:00Z",
            "summary": "Test release summary.",
            "available": True,
            "source": "github_release",
        },
    )
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start", "mb-update"])
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["ok"] is True
    assert result["old_version"] == __version__
    assert result["new_version"] == "9.9.9"
    assert result["skills_relinked_count"] == 2
    assert result["planned_skills_relink_count"] == 2
    assert result["release"]["url"].endswith("/oe-v9.9.9")
    assert result["release"]["summary"] == "Test release summary."
    assert calls == []


def test_update_check_exposes_surface_refresh_plan(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start", "mb-status"])

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["refresh_surfaces"] is True
    assert result["surface_refresh"]["enabled"] is True
    assert result["surface_refresh"]["claude"]["skill_count"] == 2
    assert result["surface_refresh"]["claude"]["command"].startswith("mb skill link")
    assert "--only codex" in result["surface_refresh"]["codex"]["command"]
    assert any("would run `mb skill link" in action for action in result["actions"])
    assert any("would run `mb doctor repair" in action for action in result["actions"])


def test_update_can_skip_surface_refresh_explicitly(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if args == ["pipx", "upgrade", "mainbranch"]:
            return _completed(args, stdout="upgraded package mainbranch")
        if args == ["mb", "--version"]:
            return _completed(args, stdout="mb 0.2.0\n")
        return _completed(args, returncode=1, stderr="unexpected")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(
        update_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/opt/homebrew/bin/pipx",
    )
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz", refresh_surfaces=False)

    assert result["ok"] is True
    assert result["refresh_surfaces"] is False
    assert result["surface_refresh"]["skipped"] == ["claude", "codex"]
    assert "skipped agent surface refresh" in result["actions"]
    assert calls == [["pipx", "upgrade", "mainbranch"], ["mb", "--version"]]


def test_update_cli_accepts_no_refresh_surfaces(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(
        update_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/opt/homebrew/bin/pipx",
    )
    monkeypatch.setattr(
        update_mod,
        "_run_command",
        lambda args, cwd=None: (
            _completed(args, stdout="mb 0.2.0\n")
            if args == ["mb", "--version"]
            else _completed(args, stdout="upgraded package mainbranch")
        ),
    )

    result = runner.invoke(
        app,
        ["update", "--repo", str(tmp_path / "biz"), "--no-refresh-surfaces", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["refresh_surfaces"] is False
    assert payload["surface_refresh"]["skipped"] == ["claude", "codex"]


def test_update_pipx_runs_upgrade_then_relinks(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if args == ["pipx", "upgrade", "mainbranch"]:
            return _completed(args, stdout="upgraded package mainbranch")
        if args == ["mb", "--version"]:
            return _completed(args, stdout="mb 0.2.0\n")
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args,
                stdout=json.dumps(
                    {
                        "ok": True,
                        "linked": [".claude/skills/mb-start"],
                        "copied": [],
                        "skipped": [".claude/skills/mb-update"],
                        "errors": [],
                        "tracked_changes": [],
                    }
                ),
            )
        if args[:3] == ["mb", "doctor", "repair"]:
            return _codex_repair_completed(args)
        return _completed(args, returncode=1, stderr="unexpected")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(
        update_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/opt/homebrew/bin/pipx",
    )
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    repo = tmp_path / "biz"
    result = update_mod.run(repo=repo)

    assert result["ok"] is True
    assert result["new_version"] == "0.2.0"
    assert result["skills_relinked_count"] == 1
    assert result["warnings"] == [
        "could not refresh existing non-link skill path(s): .claude/skills/mb-update"
    ]
    assert calls == [
        ["pipx", "upgrade", "mainbranch"],
        ["mb", "--version"],
        ["mb", "skill", "link", "--repo", str(repo.resolve()), "--plan", "--json"],
        [
            "mb",
            "doctor",
            "repair",
            "--repo",
            str(repo.resolve()),
            "--plan",
            "--only",
            "codex",
            "--json",
        ],
        ["mb", "skill", "link", "--repo", str(repo.resolve()), "--json"],
        [
            "mb",
            "doctor",
            "repair",
            "--repo",
            str(repo.resolve()),
            "--apply",
            "--only",
            "codex",
            "--json",
        ],
    ]
    assert result["codex_repaired"] is True


def test_update_points_to_scoped_codex_repair_when_adapter_missing(
    monkeypatch: Any, tmp_path: Path
) -> None:
    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        if args == ["pipx", "upgrade", "mainbranch"]:
            return _completed(args, stdout="upgraded package mainbranch")
        if args == ["mb", "--version"]:
            return _completed(args, stdout="mb 0.3.29\n")
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args,
                stdout=json.dumps(
                    {
                        "ok": True,
                        "linked": [],
                        "copied": [],
                        "skipped": [],
                        "errors": [],
                        "tracked_changes": [],
                    }
                ),
            )
        if args[:3] == ["mb", "doctor", "repair"]:
            return _codex_repair_completed(args)
        return _completed(args, returncode=1, stderr="unexpected")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(
        update_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/opt/homebrew/bin/pipx",
    )
    monkeypatch.setattr(update_mod, "_run_command", fake_run)
    monkeypatch.setattr(
        codex_mod,
        "readiness",
        lambda repo: {
            "ok": False,
            "status": "needs_setup",
            "static_ok": False,
            "runtime_ok": True,
            "plugin_ok": False,
            "repair": "mb doctor repair --apply --only codex",
            "instructions": {
                "ok": False,
                "exists": False,
                "current": False,
                "repair_command": "mb doctor repair --apply --only codex",
            },
            "plugin_install": {
                "ok": False,
                "state": "waiting_for_adapter_files",
                "plugin_installed": False,
                "plugin_enabled": False,
                "slash_commands_ready": False,
                "repair": "mb doctor repair --apply --only codex",
            },
        },
    )

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["codex_adapter"]["ok"] is False
    assert "mb doctor repair --plan --only codex" in result["next_actions"]
    assert any(
        "Codex AGENTS.md guidance still needs repo repair" in item for item in result["warnings"]
    )


def test_update_points_to_scoped_codex_repair_when_global_skills_are_missing(
    monkeypatch: Any, tmp_path: Path
) -> None:
    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        if args == ["pipx", "upgrade", "mainbranch"]:
            return _completed(args, stdout="upgraded package mainbranch")
        if args == ["mb", "--version"]:
            return _completed(args, stdout="mb 0.3.32\n")
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args,
                stdout=json.dumps(
                    {
                        "ok": True,
                        "linked": [],
                        "copied": [],
                        "skipped": [],
                        "errors": [],
                        "tracked_changes": [],
                    }
                ),
            )
        if args[:3] == ["mb", "doctor", "repair"]:
            return _codex_repair_completed(args)
        return _completed(args, returncode=1, stderr="unexpected")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(
        update_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/opt/homebrew/bin/pipx",
    )
    monkeypatch.setattr(update_mod, "_run_command", fake_run)
    monkeypatch.setattr(
        codex_mod,
        "readiness",
        lambda repo: {
            "ok": False,
            "status": "global_skill_missing_or_stale",
            "static_ok": True,
            "runtime_ok": True,
            "global_skill_ok": False,
            "plugin_ok": False,
            "repair": "mb doctor repair --apply --only codex",
            "instructions": {
                "ok": True,
                "exists": True,
                "current": True,
                "repair_command": "",
            },
            "global_skill": {
                "ok": False,
                "state": "global_skill_missing_or_stale",
                "repair": "mb doctor repair --apply --only codex",
            },
            "plugin_install": {
                "ok": False,
                "state": "plugin_not_installed",
                "plugin_installed": False,
                "plugin_enabled": False,
                "slash_commands_ready": False,
                "repair": f"Run `{codex_mod.CODEX_PLUGIN_INSTALL_COMMAND}`.",
            },
        },
    )

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["codex_adapter"]["status"] == "global_skill_missing_or_stale"
    assert result["codex_adapter"]["global_skill_ok"] is False
    assert "mb doctor repair --plan --only codex" in result["next_actions"]
    assert any(
        "global Main Branch Codex skills are not ready" in item for item in result["warnings"]
    )


def test_update_does_not_gate_ready_codex_on_slash_commands(
    monkeypatch: Any, tmp_path: Path
) -> None:
    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        if args == ["pipx", "upgrade", "mainbranch"]:
            return _completed(args, stdout="upgraded package mainbranch")
        if args == ["mb", "--version"]:
            return _completed(args, stdout="mb 0.3.34\n")
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args,
                stdout=json.dumps(
                    {
                        "ok": True,
                        "linked": [],
                        "copied": [],
                        "skipped": [],
                        "errors": [],
                        "tracked_changes": [],
                    }
                ),
            )
        if args[:3] == ["mb", "doctor", "repair"]:
            return _codex_repair_completed(args)
        return _completed(args, returncode=1, stderr="unexpected")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(
        update_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/opt/homebrew/bin/pipx",
    )
    monkeypatch.setattr(update_mod, "_run_command", fake_run)
    monkeypatch.setattr(
        codex_mod,
        "readiness",
        lambda repo: {
            "ok": True,
            "status": "ready",
            "static_ok": True,
            "runtime_ok": True,
            "global_skill_ok": True,
            "plugin_ok": True,
            "generated_guidance_ready": True,
            "command_surface_ok": True,
            "slash_commands_ready": False,
            "repair": codex_mod.CODEX_REPAIR_TEXT,
            "instructions": {
                "ok": True,
                "exists": True,
                "current": True,
                "repair_command": "",
            },
            "global_skill": {
                "ok": True,
                "state": "ok",
                "repair": "",
            },
            "plugin_install": {
                "ok": True,
                "state": "ok",
                "plugin_installed": True,
                "plugin_enabled": True,
                "skill_ready": False,
                "command_files_current": False,
                "command_surface_ok": False,
                "slash_commands_ready": False,
                "repair": codex_mod.CODEX_REPAIR_TEXT,
            },
        },
    )

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["codex_adapter"]["plugin_ok"] is True
    assert result["codex_adapter"]["ok"] is True
    assert result["codex_adapter"]["slash_commands_ready"] is False
    assert "mb doctor repair --plan --only codex" not in result["next_actions"]
    assert not any("missing or stale" in item for item in result["warnings"])
    assert not any("Codex command API" in item for item in result["next_actions"])
    assert not any("Codex command API" in item for item in result["warnings"])


def test_update_surfaces_fresh_codex_thread_when_plugin_commands_were_refreshed(
    monkeypatch: Any, tmp_path: Path
) -> None:
    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        if args == ["pipx", "upgrade", "mainbranch"]:
            return _completed(args, stdout="upgraded package mainbranch")
        if args == ["mb", "--version"]:
            return _completed(args, stdout="mb 0.3.34\n")
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args,
                stdout=json.dumps(
                    {
                        "ok": True,
                        "linked": [],
                        "copied": [],
                        "skipped": [],
                        "errors": [],
                        "tracked_changes": [],
                    }
                ),
            )
        if args[:3] == ["mb", "doctor", "repair"]:
            return _codex_repair_completed(args)
        return _completed(args, returncode=1, stderr="unexpected")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(
        update_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/opt/homebrew/bin/pipx",
    )
    monkeypatch.setattr(update_mod, "_run_command", fake_run)
    monkeypatch.setattr(
        codex_mod,
        "readiness",
        lambda repo: {
            "ok": True,
            "status": "ready",
            "static_ok": True,
            "runtime_ok": True,
            "plugin_ok": True,
            "generated_guidance_ready": True,
            "command_surface_ok": True,
            "slash_commands_ready": True,
            "repair": "",
            "instructions": {
                "ok": True,
                "exists": True,
                "current": True,
                "repair_command": "",
            },
            "plugin_install": {
                "ok": True,
                "state": "ok",
                "plugin_installed": True,
                "plugin_enabled": True,
                "skill_ready": False,
                "command_files_current": True,
                "command_surface_ok": True,
                "slash_commands_ready": True,
                "slash_commands_likely_loaded": False,
                "slash_commands_restart_required": True,
                "repair": "",
            },
        },
    )

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["codex_adapter"]["slash_commands_ready"] is True
    assert result["codex_adapter"]["slash_commands_likely_loaded"] is False
    assert result["codex_adapter"]["slash_commands_restart_required"] is True
    assert "Open a fresh Codex thread in the business repo." in result["next_actions"]
    assert any("global Main Branch skill bundle" in item for item in result["warnings"])


def test_update_check_clone_fetches_before_reading_origin(monkeypatch: Any, tmp_path: Path) -> None:
    root = tmp_path / "engine"
    (root / "mb" / "mb").mkdir(parents=True)
    (root / "mb" / "mb" / "__init__.py").write_text('__version__ = "0.1.2"\n')
    calls: list[tuple[list[str], Path | None]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append((args, cwd))
        return _completed(args)

    monkeypatch.setattr(update_mod, "install_mode", lambda: "clone")
    monkeypatch.setattr(update_mod, "engine_root", lambda: root)
    monkeypatch.setattr(update_mod, "_run_command", fake_run)
    monkeypatch.setattr(update_mod, "_version_from_git_ref", lambda _root, _ref: "0.2.0")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start", "mb-status", "mb-think"])

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["ok"] is True
    assert result["old_version"] == "0.1.2"
    assert result["new_version"] == "0.2.0"
    assert result["skills_relinked_count"] == 3
    assert calls == [(["git", "fetch", "origin", "main:refs/remotes/origin/main", "--quiet"], root)]
    assert "ran `git fetch origin main --quiet`" in result["actions"][0]
    assert "would run `git pull --ff-only origin main`" in result["actions"][1]
    assert result["actions"][2].endswith(" --json`")


def test_update_check_clone_reports_fetch_failure(monkeypatch: Any, tmp_path: Path) -> None:
    root = tmp_path / "engine"
    (root / "mb" / "mb").mkdir(parents=True)
    (root / "mb" / "mb" / "__init__.py").write_text('__version__ = "0.1.2"\n')

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return _completed(args, returncode=128, stderr="no network")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "clone")
    monkeypatch.setattr(update_mod, "engine_root", lambda: root)
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["ok"] is False
    assert result["new_version"] == "0.1.2"
    assert "no network" in result["errors"][0]


def test_update_clone_pulls_engine_root_then_relinks(monkeypatch: Any, tmp_path: Path) -> None:
    root = tmp_path / "engine"
    (root / "mb" / "mb").mkdir(parents=True)
    init_file = root / "mb" / "mb" / "__init__.py"
    init_file.write_text('__version__ = "0.1.2"\n')
    calls: list[tuple[list[str], Path | None]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append((args, cwd))
        if args == ["git", "pull", "--ff-only", "origin", "main"]:
            init_file.write_text('__version__ = "0.2.0"\n')
            return _completed(args, stdout="Already up to date.")
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args,
                stdout=json.dumps(
                    {
                        "ok": True,
                        "linked": [],
                        "copied": [],
                        "skipped": [".claude/skills/mb-start"],
                        "errors": [],
                        "tracked_changes": [],
                    }
                ),
            )
        if args[:3] == ["mb", "doctor", "repair"]:
            return _codex_repair_completed(args)
        return _completed(args, returncode=1, stderr="unexpected")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "clone")
    monkeypatch.setattr(update_mod, "engine_root", lambda: root)
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["old_version"] == "0.1.2"
    assert result["new_version"] == "0.2.0"
    assert result["skills_relinked_count"] == 0
    assert result["warnings"] == [
        "could not refresh existing non-link skill path(s): .claude/skills/mb-start"
    ]
    assert calls[0] == (["git", "pull", "--ff-only", "origin", "main"], root)
    assert calls[-1][0] == [
        "mb",
        "doctor",
        "repair",
        "--repo",
        str((tmp_path / "biz").resolve()),
        "--apply",
        "--only",
        "codex",
        "--json",
    ]


def test_update_json_cli_envelope(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(
        update_mod,
        "_release_context",
        lambda version: {
            "version": version,
            "tag": f"oe-v{version}",
            "url": f"https://github.com/noontide-co/mainbranch/releases/tag/oe-v{version}",
            "name": "",
            "published_at": "",
            "summary": "Release notes from GitHub.",
            "available": True,
            "source": "github_release",
        },
    )
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start"])

    result = runner.invoke(app, ["update", "--repo", str(tmp_path / "biz"), "--check", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["mode"] == "pipx"
    assert payload["old_version"] == __version__
    assert payload["new_version"] == "9.9.9"
    assert payload["skills_relinked_count"] == 1
    assert payload["planned_skills_relink_count"] == 1
    assert payload["release"]["summary"] == "Release notes from GitHub."
    assert payload["release"]["url"].endswith("/oe-v9.9.9")
    assert payload["errors"] == []


def test_update_check_current_release_still_exposes_notes_url(
    monkeypatch: Any, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: __version__)
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start"])

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["ok"] is True
    assert result["new_version"] == __version__
    assert result["release"]["source"] == "not_newer"
    assert result["release"]["url"].endswith(f"/oe-v{__version__}")


def test_update_rejects_unknown_install_mode(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "source")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is False
    assert result["mode"] == "source"
    assert result["new_version"] == result["old_version"]
    assert "unsupported install mode" in result["errors"][0]


def test_update_wheel_install_gets_pip_guidance_instead_of_refusal(
    monkeypatch: Any, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner(calls))

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["mode"] == "wheel"
    assert result["errors"] == []
    assert result["upgrade_performed"] is False
    assert result["manual_update_command"] == "pip install --upgrade mainbranch"
    assert "pip install --upgrade mainbranch" in result["next_actions"]
    assert _installer_calls(calls) == []


def test_update_wheel_install_still_refreshes_agent_surfaces(
    monkeypatch: Any, tmp_path: Path
) -> None:
    # Refreshing skill links needs no package upgrade. The guidance must not
    # promise a refresh that a later run would have to perform.
    calls: list[list[str]] = []

    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner(calls))

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["skills_relinked_count"] == 1
    assert result["codex_repaired"] is True
    assert any(args[:3] == ["mb", "skill", "link"] for args in calls)
    assert _installer_calls(calls) == []
    assert not any("run `mb update` again" in warning for warning in result["warnings"])


def test_update_manual_path_reports_the_version_pypi_offers(
    monkeypatch: Any, tmp_path: Path
) -> None:
    # `old == new` on a manual path would let `/mb-update` claim "already up to
    # date" on an install that is actually behind.
    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner([]))

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["old_version"] == __version__
    assert result["new_version"] == "9.9.9"
    assert result["new_version"] != result["old_version"]


def test_update_manual_path_falls_back_when_pypi_is_unreachable(
    monkeypatch: Any, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: None)
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner([]))

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["new_version"] == result["old_version"]


def test_update_wheel_install_json_exits_zero_with_next_action(
    monkeypatch: Any, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner([]))

    invoked = runner.invoke(app, ["update", "--repo", str(tmp_path / "biz"), "--json"])

    assert invoked.exit_code == 0
    payload = json.loads(invoked.stdout)
    assert payload["errors"] == []
    assert "pip install --upgrade mainbranch" in payload["next_actions"]


def test_update_uv_check_names_command_without_running_installer(
    monkeypatch: Any, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return _completed(args)

    monkeypatch.setattr(update_mod, "install_mode", lambda: "uv")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start"])
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["ok"] is True
    assert result["mode"] == "uv"
    assert result["new_version"] == "9.9.9"
    assert (
        "uv tool install --refresh-package mainbranch mainbranch@latest" in result["next_actions"]
    )
    assert any(
        "would run `uv tool install --refresh-package mainbranch mainbranch@latest`" in a
        for a in result["actions"]
    )
    assert calls == []


def test_update_uv_check_json_exits_zero_with_next_action(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "uv")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")

    invoked = runner.invoke(app, ["update", "--repo", str(tmp_path / "biz"), "--check", "--json"])

    assert invoked.exit_code == 0
    payload = json.loads(invoked.stdout)
    assert payload["mode"] == "uv"
    assert payload["errors"] == []
    assert (
        "uv tool install --refresh-package mainbranch mainbranch@latest" in payload["next_actions"]
    )


def test_update_uv_non_interactive_prints_command_and_exits_zero(
    monkeypatch: Any, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    def refuse_confirm(command: str, root: Path | None) -> bool:
        raise AssertionError("non-interactive update must never prompt")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "uv")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr("mb.update.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner(calls))

    result = update_mod.run(repo=tmp_path / "biz", interactive=False, confirm=refuse_confirm)

    assert result["ok"] is True
    assert result["upgrade_performed"] is False
    assert result["new_version"] == "9.9.9"
    assert (
        "uv tool install --refresh-package mainbranch mainbranch@latest" in result["next_actions"]
    )
    assert _installer_calls(calls) == []
    assert result["skills_relinked_count"] == 1


def test_update_uv_json_never_prompts(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr(update_mod, "install_mode", lambda: "uv")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr("mb.update.shutil.which", lambda name: f"/usr/bin/{name}")

    def explode(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("`--json` must never prompt")

    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner(calls))
    monkeypatch.setattr(update_mod, "_confirm_uv_update", explode)

    invoked = runner.invoke(app, ["update", "--repo", str(tmp_path / "biz"), "--json"])

    assert invoked.exit_code == 0
    payload = json.loads(invoked.stdout)
    assert payload["upgrade_performed"] is False
    assert (
        "uv tool install --refresh-package mainbranch mainbranch@latest" in payload["next_actions"]
    )
    assert _installer_calls(calls) == []


def test_update_uv_declined_prompt_leaves_install_alone(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []
    asked: list[str] = []

    def decline(command: str, root: Path | None) -> bool:
        asked.append(command)
        return False

    monkeypatch.setattr(update_mod, "install_mode", lambda: "uv")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr("mb.update.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner(calls))

    result = update_mod.run(repo=tmp_path / "biz", interactive=True, confirm=decline)

    assert asked == ["uv tool install --refresh-package mainbranch mainbranch@latest"]
    assert result["ok"] is True
    assert result["upgrade_performed"] is False
    assert (
        "uv tool install --refresh-package mainbranch mainbranch@latest" in result["next_actions"]
    )
    assert _installer_calls(calls) == []


def test_update_uv_accepted_prompt_runs_install_then_relinks(
    monkeypatch: Any, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args, stdout=json.dumps({"ok": True, "linked": ["mb-start"], "tracked_changes": []})
            )
        if args[:3] == ["mb", "doctor", "repair"]:
            return _codex_repair_completed(args)
        if args[1:] == ["--version"]:
            return _completed(args, stdout="mb 9.9.9\n")
        return _completed(args)

    monkeypatch.setattr(update_mod, "install_mode", lambda: "uv")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr("mb.update.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(
        repo=tmp_path / "biz",
        interactive=True,
        confirm=lambda command, root: True,
    )

    assert result["ok"] is True
    assert result["upgrade_performed"] is True
    assert result["new_version"] == "9.9.9"
    assert [
        "uv",
        "tool",
        "install",
        "--refresh-package",
        "mainbranch",
        "mainbranch@latest",
    ] in calls
    assert result["skills_relinked_count"] == 1
    assert any(
        "ran `uv tool install --refresh-package mainbranch mainbranch@latest`" in a
        for a in result["actions"]
    )


def test_update_uv_install_failure_surfaces_command(monkeypatch: Any, tmp_path: Path) -> None:
    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return _completed(args, returncode=1, stderr="network unreachable")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "uv")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr("mb.update.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(
        repo=tmp_path / "biz",
        interactive=True,
        confirm=lambda command, root: True,
    )

    assert result["ok"] is False
    assert result["upgrade_performed"] is False
    assert "network unreachable" in result["errors"][0]
    assert (
        "uv tool install --refresh-package mainbranch mainbranch@latest" in result["next_actions"]
    )


def test_update_uv_missing_binary_returns_error(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "uv")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr("mb.update.shutil.which", lambda name: None)

    result = update_mod.run(
        repo=tmp_path / "biz",
        interactive=True,
        confirm=lambda command, root: True,
    )

    assert result["ok"] is False
    assert "`uv` is not on PATH" in result["errors"][0]
    assert (
        "uv tool install --refresh-package mainbranch mainbranch@latest" in result["next_actions"]
    )


def test_update_uses_uv_tool_dir_when_path_detection_is_inconclusive(
    monkeypatch: Any, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "_uv_tool_dir_holds_this_install", lambda: True)
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["mode"] == "uv"
    assert (
        "uv tool install --refresh-package mainbranch mainbranch@latest" in result["next_actions"]
    )


def _uv_tool_dir_probe(
    monkeypatch: Any,
    tool_root: Path,
    engine: Path,
    interpreter: Path,
) -> bool:
    monkeypatch.setattr("mb.update.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        update_mod,
        "_run_command",
        lambda args, *, cwd=None, timeout=0.0: _completed(args, stdout=f"{tool_root}\n"),
    )
    monkeypatch.setattr(update_mod, "engine_root", lambda: engine)
    # The detector checks the running interpreter as well as the engine root,
    # so a test that models an install has to control both.
    monkeypatch.setattr("mb.engine.sys.executable", str(interpreter))
    return _REAL_UV_TOOL_DIR_HOLDS_THIS_INSTALL()


def test_uv_tool_dir_matches_an_install_under_the_reported_root(
    monkeypatch: Any, tmp_path: Path
) -> None:
    tool_root = tmp_path / "relocated" / "tools"
    engine = tool_root / "mainbranch" / "lib" / "site-packages" / "mb" / "_engine"
    interpreter = tmp_path / "uv" / "python" / "cpython-3.12" / "bin" / "python3.12"

    assert _uv_tool_dir_probe(monkeypatch, tool_root, engine, interpreter) is True


def test_uv_tool_dir_does_not_claim_an_unrelated_venv(monkeypatch: Any, tmp_path: Path) -> None:
    # The regression that `uv tool list` could not catch: this machine has a uv
    # tool install of Main Branch, but the running install is a plain
    # `pip install mainbranch` virtualenv somewhere else entirely.
    tool_root = tmp_path / "relocated" / "tools"
    (tool_root / "mainbranch").mkdir(parents=True)
    engine = tmp_path / "project" / ".venv" / "lib" / "site-packages" / "mb" / "_engine"
    interpreter = tmp_path / "project" / ".venv" / "bin" / "python3"

    assert _uv_tool_dir_probe(monkeypatch, tool_root, engine, interpreter) is False


def test_uv_tool_dir_probe_is_quiet_when_uv_is_absent(monkeypatch: Any) -> None:
    monkeypatch.setattr("mb.update.shutil.which", lambda name: None)

    assert _REAL_UV_TOOL_DIR_HOLDS_THIS_INSTALL() is False


def test_update_pipx_mode_still_upgrades_automatically(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args, stdout=json.dumps({"ok": True, "linked": ["mb-start"], "tracked_changes": []})
            )
        if args[:3] == ["mb", "doctor", "repair"]:
            return _codex_repair_completed(args)
        return _completed(args, stdout="mb 9.9.9\n")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr("mb.update.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["upgrade_performed"] is True
    assert result["manual_update_command"] == ""
    assert ["pipx", "upgrade", "mainbranch"] in calls
    assert not any(args[:2] == ["uv", "tool"] for args in calls)


def test_update_pipx_missing_binary_returns_error(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod.shutil, "which", lambda name: None)  # type: ignore[attr-defined]

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is False
    assert result["new_version"] == result["old_version"]
    assert result["errors"] == ["pipx install mode detected, but `pipx` is not on PATH"]


def test_update_pipx_upgrade_failure_skips_relink(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return _completed(args, returncode=2, stderr="network down")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(
        update_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/opt/homebrew/bin/pipx",
    )
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is False
    assert result["skills_relinked_count"] == 0
    assert calls == [["pipx", "upgrade", "mainbranch"]]
    assert "network down" in result["errors"][0]
    assert result["warnings"] == []
    assert result["next_actions"] == []


def test_update_pipx_local_wheel_parse_failure_surfaces_force_install(
    monkeypatch: Any, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return _completed(
            args,
            returncode=1,
            stderr=(
                "Unable to parse package spec: /tmp/Main Branch/dist/"
                "mainbranch-0.3.39-py3-none-any.whl"
            ),
        )

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(
        update_mod.shutil,  # type: ignore[attr-defined]
        "which",
        lambda name: "/opt/homebrew/bin/pipx",
    )
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is False
    assert result["new_version"] == result["old_version"]
    assert result["skills_relinked_count"] == 0
    assert calls == [["pipx", "upgrade", "mainbranch"]]
    assert "Unable to parse package spec" in result["errors"][0]
    assert result["warnings"] == [
        "pipx could not parse the saved Main Branch install spec. This can happen "
        "after installing from a local wheel path. Approve a forced pipx reinstall "
        "to reset the saved install source."
    ]
    assert result["next_actions"] == ["pipx install --force mainbranch==9.9.9"]


def test_update_render_human_failure_prints_next_action(capsys: Any) -> None:
    update_mod.render_human(
        {
            "ok": False,
            "check": False,
            "old_version": "0.3.39",
            "new_version": "0.3.39",
            "mode": "pipx",
            "skills_relinked_count": 0,
            "errors": ["pipx upgrade mainbranch failed with exit code 1"],
            "warnings": ["Approve a forced pipx reinstall to reset the saved install source."],
            "next_actions": ["pipx install --force mainbranch==0.3.40"],
        }
    )

    output = capsys.readouterr().out

    assert "error: pipx upgrade mainbranch failed with exit code 1" in output
    assert "warning: Approve a forced pipx reinstall" in output
    assert "next: pipx install --force mainbranch==0.3.40" in output


def test_update_relink_invalid_json_is_reported(monkeypatch: Any, tmp_path: Path) -> None:
    root = tmp_path / "engine"
    (root / "mb" / "mb").mkdir(parents=True)
    (root / "mb" / "mb" / "__init__.py").write_text('__version__ = "0.1.2"\n')

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        if args == ["git", "pull"]:
            return _completed(args)
        return _completed(args, stdout="not-json")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "clone")
    monkeypatch.setattr(update_mod, "engine_root", lambda: root)
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is False
    assert result["skills_relinked_count"] == 0
    assert result["errors"] == ["mb skill link --plan returned invalid JSON"]


def test_update_relink_payload_errors_are_reported(monkeypatch: Any, tmp_path: Path) -> None:
    payload = {
        "ok": False,
        "linked": [],
        "copied": [".claude/skills/mb-start"],
        "skipped": [".claude/skills/mb-update"],
        "errors": ["could not locate bundled Main Branch engine root"],
    }

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return _completed(args, stdout=json.dumps(payload))

    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    count, errors, warnings, parsed = update_mod._link_skills(tmp_path / "biz")

    assert count == 1
    assert errors == ["could not locate bundled Main Branch engine root"]
    assert warnings == [
        "could not refresh existing non-link skill path(s): .claude/skills/mb-update"
    ]
    assert parsed == payload


def test_update_render_human_check_and_error(capsys: Any) -> None:
    update_mod.render_human(
        {
            "check": True,
            "mode": "clone",
            "old_version": "0.1.2",
            "new_version": "0.2.0",
            "skills_relinked_count": 3,
            "release": {
                "url": "https://github.com/noontide-co/mainbranch/releases/tag/oe-v0.2.0",
                "summary": "Release context.",
                "available": True,
            },
            "actions": ["would run `git pull`"],
            "errors": ["boom"],
            "warnings": ["careful"],
        }
    )

    output = capsys.readouterr().out

    assert "install mode: clone" in output
    assert "version: 0.1.2 -> 0.2.0" in output
    assert (
        "release notes: https://github.com/noontide-co/mainbranch/releases/tag/oe-v0.2.0" in output
    )
    assert "release summary: Release context." in output
    assert "would refresh 3 skill link(s)" in output
    assert "error: boom" in output
    assert "warning: careful" in output


def test_update_render_human_check_labels_unavailable_release_url(capsys: Any) -> None:
    update_mod.render_human(
        {
            "check": True,
            "mode": "pipx",
            "old_version": "0.1.2",
            "new_version": "0.2.0",
            "skills_relinked_count": 0,
            "release": {
                "url": "https://github.com/noontide-co/mainbranch/releases/tag/oe-v0.2.0",
                "summary": "Fallback summary should not print.",
                "available": False,
                "source": "github_release_unavailable",
            },
            "actions": [],
            "errors": [],
            "warnings": [],
        }
    )

    output = capsys.readouterr().out

    assert "release notes:" not in output
    assert (
        "expected release notes URL: https://github.com/noontide-co/mainbranch/releases/tag/oe-v0.2.0"
        in output
    )
    assert "Fallback summary should not print." not in output


def test_update_render_human_check_skips_current_release_url(capsys: Any) -> None:
    update_mod.render_human(
        {
            "check": True,
            "mode": "pipx",
            "old_version": "0.2.0",
            "new_version": "0.2.0",
            "skills_relinked_count": 0,
            "release": {
                "url": "https://github.com/noontide-co/mainbranch/releases/tag/oe-v0.2.0",
                "available": False,
                "source": "not_newer",
            },
            "actions": [],
            "errors": [],
            "warnings": [],
        }
    )

    output = capsys.readouterr().out

    assert "release notes:" not in output
    assert "expected release notes URL:" not in output


def test_update_render_human_success(capsys: Any) -> None:
    update_mod.render_human(
        {
            "ok": True,
            "check": False,
            "old_version": "0.1.2",
            "new_version": "0.2.0",
            "skills_relinked_count": 4,
            "errors": [],
        }
    )

    output = capsys.readouterr().out

    assert "updated Main Branch (0.1.2 -> 0.2.0)" in output
    assert "refreshed 4 skill link(s)" in output


def test_update_render_human_same_version_says_already_current(capsys: Any) -> None:
    # #974: a successful run that lands the version already installed did not
    # update anything, so it must not say "updated".
    update_mod.render_human(
        {
            "ok": True,
            "check": False,
            "old_version": "0.5.3",
            "new_version": "0.5.3",
            "upgrade_performed": True,
            "skills_relinked_count": 4,
            "errors": [],
        }
    )

    output = capsys.readouterr().out

    assert "Main Branch is already current (0.5.3)." in output
    assert "updated" not in output
    assert "refreshed 4 skill link(s)" in output


def _ahead_of_pypi(monkeypatch: Any, tmp_path: Path, mode: str) -> None:
    """A release-candidate build installed while PyPI's latest is the prior release."""
    monkeypatch.setattr(update_mod, "install_mode", lambda: mode)
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_engine_version", lambda root=None: "0.6.3rc1")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "0.6.2")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start"])
    monkeypatch.setattr("mb.update.shutil.which", lambda name: f"/usr/bin/{name}")


def _assert_ahead_of_pypi(result: dict[str, Any]) -> None:
    assert result["ok"] is True
    assert result["old_version"] == "0.6.3rc1"
    assert result["new_version"] == "0.6.3rc1"
    assert result["latest_version"] == "0.6.2"
    assert result["installed_ahead_of_latest"] is True
    assert result["upgrade_performed"] is False
    assert result["manual_update_command"] == ""
    installers = ("uv tool install", "pipx upgrade", "pipx install", "pip install")
    assert not [a for a in result["next_actions"] if a.startswith(installers)]
    assert any("newer than PyPI's latest release (0.6.2)" in w for w in result["warnings"])


@pytest.mark.parametrize("mode", ["uv", "wheel", "pipx"])
def test_update_check_json_ahead_of_pypi_lists_no_install_command(
    monkeypatch: Any, tmp_path: Path, mode: str
) -> None:
    # #1022: a pre-release or local build newer than PyPI must not be offered
    # an install command that would downgrade it.
    calls: list[list[str]] = []
    _ahead_of_pypi(monkeypatch, tmp_path, mode)
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner(calls))

    cli = runner.invoke(app, ["update", "--repo", str(tmp_path / "biz"), "--check", "--json"])

    assert cli.exit_code == 0
    payload = json.loads(cli.stdout)
    _assert_ahead_of_pypi(payload)
    assert payload["release"]["source"] == "not_newer"
    assert _installer_calls(calls) == []


@pytest.mark.parametrize("mode", ["uv", "wheel", "pipx"])
def test_update_run_ahead_of_pypi_runs_no_installer(
    monkeypatch: Any, tmp_path: Path, mode: str, capsys: Any
) -> None:
    calls: list[list[str]] = []
    _ahead_of_pypi(monkeypatch, tmp_path, mode)
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner(calls))

    def never_prompt(command: str, root: Path | None) -> bool:
        raise AssertionError("must not offer to install an older release")

    result = update_mod.run(repo=tmp_path / "biz", interactive=True, confirm=never_prompt)

    _assert_ahead_of_pypi(result)
    assert _installer_calls(calls) == []
    assert result["skills_relinked_count"] == 1

    update_mod.render_human(result)
    output = capsys.readouterr().out
    assert "Main Branch 0.6.3rc1 is newer than PyPI's latest release (0.6.2)" in output
    assert "updated" not in output


def test_update_check_human_ahead_of_pypi(monkeypatch: Any, tmp_path: Path) -> None:
    _ahead_of_pypi(monkeypatch, tmp_path, "uv")
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner([]))

    cli = runner.invoke(app, ["update", "--repo", str(tmp_path / "biz"), "--check"])

    assert cli.exit_code == 0
    assert "version: 0.6.3rc1 (newer than PyPI's latest, 0.6.2)" in cli.stdout
    assert "next: uv tool install" not in cli.stdout


def test_update_dev_build_of_published_release_is_behind_pypi(
    monkeypatch: Any, tmp_path: Path
) -> None:
    # Versions compare by PEP 440, not by their numeric parts: 0.6.3.dev0
    # sorts before 0.6.3, so the published release is still an upgrade.
    _ahead_of_pypi(monkeypatch, tmp_path, "uv")
    monkeypatch.setattr(update_mod, "_engine_version", lambda root=None: "0.6.3.dev0")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "0.6.3")

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["installed_ahead_of_latest"] is False
    assert result["new_version"] == "0.6.3"
    assert result["manual_update_command"] == update_mod.UV_UPDATE_COMMAND_TEXT
    assert update_mod.UV_UPDATE_COMMAND_TEXT in result["next_actions"]


def test_update_reports_plugin_rail_wired_without_warning(monkeypatch: Any, tmp_path: Path) -> None:
    # Default fixture: repo already on the plugin rail -> no migration warning.
    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start", "mb-status"])

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["plugin_rail"]["wired"] is True
    assert not any("symlink-only skill wiring" in w for w in result["warnings"])
    assert "mb skill link --repo . --plugin --json" not in result["next_actions"]


def test_update_surfaces_plugin_migration_for_symlink_era_repo(
    monkeypatch: Any, tmp_path: Path
) -> None:
    # #931: a repo that predates the plugin default stays on symlinks after
    # `mb update`; the post-update follow-up names the one-command migration.
    monkeypatch.setattr(
        update_mod,
        "plugin_wiring_status",
        lambda repo: {
            "wired": False,
            "marketplace_known": False,
            "plugin_enabled": False,
            "settings_path": str(tmp_path / "biz" / ".claude" / "settings.json"),
        },
    )
    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start", "mb-status"])

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["plugin_rail"]["wired"] is False
    assert any("symlink-only skill wiring" in w for w in result["warnings"])
    assert "mb skill link --repo . --plugin --json" in result["next_actions"]


def test_update_warns_when_installed_claude_plugin_is_stale(
    monkeypatch: Any, tmp_path: Path
) -> None:
    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        if args == ["pipx", "upgrade", "mainbranch"]:
            return _completed(args)
        if args == ["mb", "--version"]:
            return _completed(args, stdout="mb 0.4.2\n")
        if args[:3] == ["mb", "skill", "link"]:
            return _completed(
                args, stdout=json.dumps({"ok": True, "linked": ["mb-start"], "tracked_changes": []})
            )
        if args[:4] == ["mb", "doctor", "repair", "--repo"]:
            return _codex_repair_completed(args)
        return _completed(args)

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(shutil, "which", lambda name: "/opt/homebrew/bin/pipx")
    monkeypatch.setattr(update_mod, "_run_command", fake_run)
    monkeypatch.setattr(
        update_mod,
        "claude_mainbranch_plugin_status",
        lambda *, expected_version=None, timeout=5.0: {
            "checked": True,
            "ok": False,
            "state": "stale",
            "expected_version": expected_version,
            "installed_version": "0.4.1",
            "installed_versions": ["0.4.1"],
            "enabled_versions": ["0.4.1"],
            "entries": [],
            "command": "claude plugin list --json",
            "repair": engine_mod.PLUGIN_INSTALL_COMMAND,
            "summary": "Main Branch Claude Code plugin is enabled at 0.4.1, expected 0.4.2.",
        },
    )

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["new_version"] == "0.4.2"
    assert result["plugin_rail"]["install"]["state"] == "stale"
    assert result["plugin_rail"]["install"]["expected_version"] == "0.4.2"
    assert engine_mod.PLUGIN_INSTALL_COMMAND in result["next_actions"]
    assert any("older Main Branch plugin" in warning for warning in result["warnings"])
    assert any("/reload-plugins" in warning for warning in result["warnings"])


def test_update_check_uses_planned_version_for_plugin_status(
    monkeypatch: Any, tmp_path: Path
) -> None:
    expected_versions: list[str | None] = []

    def fake_status(*, expected_version=None, timeout=5.0) -> dict[str, Any]:
        expected_versions.append(expected_version)
        return {
            "checked": True,
            "ok": False,
            "state": "stale",
            "expected_version": expected_version,
            "installed_version": "0.4.1",
            "installed_versions": ["0.4.1"],
            "enabled_versions": ["0.4.1"],
            "entries": [],
            "command": "claude plugin list --json",
            "repair": engine_mod.PLUGIN_INSTALL_COMMAND,
            "summary": (
                f"Main Branch Claude Code plugin is enabled at 0.4.1, expected {expected_version}."
            ),
        }

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start", "mb-status"])
    monkeypatch.setattr(update_mod, "claude_mainbranch_plugin_status", fake_status)

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert expected_versions == ["9.9.9"]
    assert result["plugin_rail"]["install"]["expected_version"] == "9.9.9"
    assert any("expects 9.9.9" in warning for warning in result["warnings"])
    assert engine_mod.PLUGIN_INSTALL_COMMAND in result["next_actions"]


@pytest.mark.parametrize(
    ("answer", "expected"),
    [("y", True), ("Y", True), ("yes", True), ("", False), ("n", False), ("sure", False)],
)
def test_confirm_uv_update_defaults_to_no(
    monkeypatch: Any, capsys: Any, tmp_path: Path, answer: str, expected: bool
) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": answer)

    approved = update_mod._confirm_uv_update(
        update_mod.UV_UPDATE_COMMAND_TEXT, tmp_path / "_engine"
    )

    assert approved is expected
    out = capsys.readouterr().out
    assert "uv tool install --refresh-package mainbranch mainbranch@latest" in out
    assert str(tmp_path / "_engine") in out


def test_confirm_uv_update_treats_interrupted_input_as_no(monkeypatch: Any) -> None:
    def interrupted(prompt: str = "") -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", interrupted)

    assert update_mod._confirm_uv_update(update_mod.UV_UPDATE_COMMAND_TEXT, None) is False


def test_update_render_human_manual_path_names_the_command(capsys: Any) -> None:
    update_mod.render_human(
        {
            "ok": True,
            "check": False,
            "mode": "uv",
            "old_version": "0.5.2",
            "new_version": "0.6.0",
            "upgrade_performed": False,
            "manual_update_command": update_mod.UV_UPDATE_COMMAND_TEXT,
            "skills_relinked_count": 15,
            "next_actions": [update_mod.UV_UPDATE_COMMAND_TEXT],
            "warnings": ["Main Branch was installed as a uv tool."],
            "errors": [],
        }
    )

    output = capsys.readouterr().out
    assert "install mode: uv" in output
    assert "version: 0.5.2 -> 0.6.0" in output
    assert "Main Branch did not upgrade this install." in output
    assert "refreshed 15 skill link(s)" in output
    assert "next: uv tool install --refresh-package mainbranch mainbranch@latest" in output


def test_update_check_uv_carries_the_manual_command_like_wheel_does(
    monkeypatch: Any, tmp_path: Path
) -> None:
    # The key must not appear and disappear by install mode.
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start"])

    seen = {}
    for mode, command in (
        ("uv", "uv tool install --refresh-package mainbranch mainbranch@latest"),
        ("wheel", "pip install --upgrade mainbranch"),
    ):
        monkeypatch.setattr(update_mod, "install_mode", lambda mode=mode: mode)
        seen[mode] = update_mod.run(repo=tmp_path / "biz", check=True)
        assert seen[mode]["manual_update_command"] == command
        assert seen[mode]["new_version"] == "9.9.9"

    # And `--check` may only promise a relink the real run actually performs.
    assert seen["uv"]["planned_skills_relink_count"] == 1
    assert seen["wheel"]["planned_skills_relink_count"] == 1


def test_update_check_promise_matches_what_the_real_run_does(
    monkeypatch: Any, tmp_path: Path
) -> None:
    # Finding 1: `--check` planned 15 relinks that the real run never performed.
    calls: list[list[str]] = []

    monkeypatch.setattr(update_mod, "install_mode", lambda: "uv")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "9.9.9")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["mb-start"])
    monkeypatch.setattr("mb.update.shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(update_mod, "_run_command", _surface_refresh_runner(calls))

    planned = update_mod.run(repo=tmp_path / "biz", check=True)
    actual = update_mod.run(repo=tmp_path / "biz", interactive=False)

    assert planned["planned_skills_relink_count"] == actual["skills_relinked_count"]
    assert planned["surface_refresh"]["claude"]["command"] in actual["surface_refresh"]["commands"]
    assert _installer_calls(calls) == []


# --- #1012: no tracked-file writes without an interactive terminal ---------


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout


@pytest.fixture
def business_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A committed business repo with stale AGENTS.md and a bare .gitignore."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CODEX_HOME", str(home / ".codex"))
    monkeypatch.setenv("XDG_DATA_HOME", str(home / ".local" / "share"))
    monkeypatch.setenv("MAINBRANCH_CODEX_SKILLS_ROOT", str(home / ".codex" / "skills"))
    monkeypatch.setattr(codex_mod, "readiness", _REAL_CODEX_READINESS)
    monkeypatch.setattr(engine_mod, "_personal_skills_dir", lambda: home / ".claude" / "skills")
    repo = tmp_path / "biz"
    repo.mkdir()
    (repo / "CLAUDE.md").write_text("# Business\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Old guidance\n", encoding="utf-8")
    (repo / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(
        repo,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-q",
        "-m",
        "Start",
    )
    return repo


def _in_process_mb(calls: list[list[str]]) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Run `mb ...` subcommands against this checkout's CLI, in process."""

    def fake_run(
        args: list[str], *, cwd: Path | None = None, timeout: float = 0.0
    ) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        if args and args[0] == "mb":
            invoked = runner.invoke(app, args[1:])
            stderr = repr(invoked.exception) if invoked.exception else ""
            if isinstance(invoked.exception, SystemExit):
                stderr = ""
            return _completed(
                args, stdout=invoked.stdout, stderr=stderr, returncode=invoked.exit_code
            )
        return _completed(args, returncode=1, stderr="unexpected command in test")

    return fake_run


def _wheel_update_env(monkeypatch: pytest.MonkeyPatch, calls: list[list[str]]) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: None)
    monkeypatch.setattr(update_mod, "_run_command", _in_process_mb(calls))


def _tracked_state(repo: Path) -> tuple[str, str, str]:
    return (
        _git(repo, "status", "--porcelain"),
        (repo / "AGENTS.md").read_text(encoding="utf-8"),
        (repo / ".gitignore").read_text(encoding="utf-8"),
    )


def test_update_without_terminal_leaves_tracked_files_and_reports_plan(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path
) -> None:
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    monkeypatch.setattr(update_mod, "_is_interactive_terminal", lambda: False)

    def never_ask(repo: Path, files: list[str]) -> bool:
        raise AssertionError("must not prompt without a terminal")

    monkeypatch.setattr(update_mod, "_confirm_surface_writes", never_ask, raising=False)
    before = _tracked_state(business_repo)

    result = update_mod.run(repo=business_repo)

    assert _tracked_state(business_repo) == before
    assert before[0] == ""
    assert not any("--apply" in args for args in calls)
    assert ["mb", "skill", "link", "--repo", str(business_repo), "--json"] not in calls
    assert result["ok"] is True
    planned = result["surface_refresh"]["planned"]
    assert planned["consent"] == "no_terminal"
    assert planned["tracked_files"] == [".gitignore", "AGENTS.md"]
    apply_commands = [
        f"mb skill link --repo {business_repo}",
        f"mb doctor repair --repo {business_repo} --apply --only codex",
    ]
    assert planned["apply_commands"] == apply_commands
    for command in apply_commands:
        assert command in result["next_actions"]
    assert result["surface_refresh"]["claude"]["applied"] is False
    assert result["surface_refresh"]["claude"]["tracked_writes"] == [".gitignore"]
    assert result["surface_refresh"]["codex"]["applied"] is False
    assert result["surface_refresh"]["codex"]["tracked_writes"] == ["AGENTS.md"]
    assert result["codex_repaired"] is False
    assert any("Left tracked files unchanged" in w for w in result["warnings"])


def test_update_json_never_prompts_for_tracked_files_even_at_a_terminal(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path
) -> None:
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    monkeypatch.setattr(update_mod, "_is_interactive_terminal", lambda: True)

    def never_ask(repo: Path, files: list[str]) -> bool:
        raise AssertionError("--json must not prompt")

    monkeypatch.setattr(update_mod, "_confirm_surface_writes", never_ask, raising=False)
    before = _tracked_state(business_repo)

    invoked = runner.invoke(app, ["update", "--repo", str(business_repo), "--json"])

    assert invoked.exit_code == 0, invoked.stdout
    payload = json.loads(invoked.stdout)
    assert _tracked_state(business_repo) == before
    assert payload["surface_refresh"]["planned"]["consent"] == "no_terminal"
    assert payload["surface_refresh"]["planned"]["tracked_files"] == [".gitignore", "AGENTS.md"]


def test_update_terminal_no_leaves_tracked_files(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path
) -> None:
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    asked: list[list[str]] = []

    def say_no(repo: Path, files: list[str]) -> bool:
        asked.append(files)
        return False

    before = _tracked_state(business_repo)

    result = update_mod.run(repo=business_repo, interactive=True, confirm_surfaces=say_no)

    assert asked == [[".gitignore", "AGENTS.md"]], result["errors"]
    assert _tracked_state(business_repo) == before
    assert result["surface_refresh"]["planned"]["consent"] == "declined"
    assert f"mb doctor repair --repo {business_repo} --apply --only codex" in result["next_actions"]


def test_update_terminal_yes_applies_once_then_unattended_runs_need_no_consent(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path
) -> None:
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    asked: list[list[str]] = []

    def say_yes(repo: Path, files: list[str]) -> bool:
        asked.append(files)
        return True

    result = update_mod.run(repo=business_repo, interactive=True, confirm_surfaces=say_yes)

    assert asked == [[".gitignore", "AGENTS.md"]], result["errors"]
    assert result["ok"] is True, result["errors"]
    assert result["surface_refresh"]["planned"]["consent"] == "approved"
    assert result["surface_refresh"]["planned"]["apply_commands"] == []
    changed = sorted(line[3:] for line in _git(business_repo, "status", "--porcelain").splitlines())
    assert changed == [".gitignore", "AGENTS.md"]
    agents_md = (business_repo / "AGENTS.md").read_text(encoding="utf-8")
    assert agents_md != "# Old guidance\n"
    assert "<!-- mainbranch" in agents_md
    assert (business_repo / ".claude" / "skills" / "mb-start").is_symlink()
    assert result["codex_repaired"] is True

    # Once the tracked files are current, a run without a terminal still
    # refreshes the gitignored links, and asks nothing.
    _git(business_repo, "add", "-A")
    _git(
        business_repo,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-q",
        "-m",
        "Refresh",
    )
    (business_repo / ".claude" / "skills" / "mb-start").unlink()

    def never_ask(repo: Path, files: list[str]) -> bool:
        raise AssertionError("nothing tracked changes, so nothing to ask")

    again = update_mod.run(repo=business_repo, interactive=False, confirm_surfaces=never_ask)

    assert again["ok"] is True, again["errors"]
    assert again["surface_refresh"]["planned"]["consent"] == "not_needed"
    assert again["surface_refresh"]["claude"]["applied"] is True
    assert (business_repo / ".claude" / "skills" / "mb-start").is_symlink()
    assert _git(business_repo, "status", "--porcelain") == ""


def test_plan_link_skills_writes_nothing_and_names_gitignore(business_repo: Path) -> None:
    before = _tracked_state(business_repo)

    plan = engine_mod.plan_link_skills(business_repo)

    assert _tracked_state(business_repo) == before
    assert not (business_repo / ".claude").exists()
    assert plan["ok"] is True
    assert plan["tracked_writes"] == [".gitignore"]
    assert ".claude/skills/mb-start" in plan["linked"]
    assert ".claude/skills/mb-start" in plan["gitignore_add"]


# --- #1008 item 4: always fetch the new version after a release --------------


def test_uv_update_command_refreshes_the_package_index() -> None:
    assert update_mod.UV_UPDATE_COMMAND == [
        "uv",
        "tool",
        "install",
        "--refresh-package",
        "mainbranch",
        "mainbranch@latest",
    ]
    assert " ".join(update_mod.UV_UPDATE_COMMAND) == update_mod.UV_UPDATE_COMMAND_TEXT


def test_emitted_commands_quote_a_repo_path_with_spaces_and_parens(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "My Business (old)"
    repo.mkdir()
    real = str(repo.resolve())

    def fake_run(
        args: list[str], *, cwd: Path | None = None, timeout: float = 0.0
    ) -> subprocess.CompletedProcess[str]:
        if args[:3] == ["mb", "skill", "link"] and "--plan" in args:
            return _completed(
                args,
                stdout=json.dumps(
                    {"ok": True, "tracked_changes": [{"path": ".gitignore", "op": "write"}]}
                ),
            )
        if args[:3] == ["mb", "doctor", "repair"] and "--plan" in args:
            change = {"path": "AGENTS.md", "op": "write"}
            plan = {"ok": True, "actions": [{"id": "codex-agents-md", "tracked_changes": [change]}]}
            return _completed(args, stdout=json.dumps(plan))
        return _completed(args, returncode=1, stderr="must not apply without a terminal")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: None)
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=repo, interactive=False)

    planned = result["surface_refresh"]["planned"]
    assert planned["consent"] == "no_terminal"
    emitted = [
        *planned["apply_commands"],
        *[a for a in result["next_actions"] if a.startswith("mb ") and "--repo" in a],
        result["surface_refresh"]["claude"]["command"],
        result["surface_refresh"]["codex"]["command"],
    ]
    assert len(planned["apply_commands"]) == 2
    assert any("--plan --only codex" in command for command in emitted)
    for command in emitted:
        argv = shlex.split(command)
        assert argv[argv.index("--repo") + 1] == real, command

    update_mod.render_human(result)
    printed = [
        line.removeprefix("next: ")
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("next: mb ") and "--repo" in line
    ]
    assert len(printed) == 3
    for command in printed:
        argv = shlex.split(command)
        assert argv[argv.index("--repo") + 1] == real, command


# --- #1015 review: deletions, aliases and transitional cleanup ---------------


def _commit_all(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(
        repo,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-q",
        "-m",
        message,
    )


def _probe_repo(repo: Path, tmp_path: Path, kind: str) -> str:
    """Set up one review reproduction; return the tracked path it puts at risk."""
    entries, _ = engine_mod._link_gitignore_entries()
    (repo / ".gitignore").write_text("\n".join(entries) + "\n", encoding="utf-8")
    at_risk = ""
    if kind == "legacy_link":
        old = repo / ".claude" / "skills" / "start"
        old.parent.mkdir(parents=True)
        old.symlink_to(tmp_path / "missing-old-engine")
        _git(repo, "add", "-f", ".claude/skills/start")
        at_risk = ".claude/skills/start"
    elif kind == "claude_alias":
        shared = repo / "shared-claude"
        shared.mkdir()
        (shared / "settings.local.json").write_text("{}\n", encoding="utf-8")
        (repo / ".claude").symlink_to(shared, target_is_directory=True)
        at_risk = "shared-claude/settings.local.json"
    elif kind == "codex_alias":
        codex_mod.write_agents_md(repo)
        shared = repo / "shared-codex" / "mb-start"
        shared.mkdir(parents=True)
        (shared / "SKILL.md").write_text("stale\n", encoding="utf-8")
        global_root = codex_mod.global_skill_source_root()
        global_root.mkdir(parents=True, exist_ok=True)
        (global_root / "mb-start").symlink_to(shared, target_is_directory=True)
        at_risk = "shared-codex/mb-start/SKILL.md"
    elif kind == "codex_cleanup":
        legacy = repo / ".agents" / "skills" / "main-branch" / "SKILL.md"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("legacy skill\n", encoding="utf-8")
        at_risk = ".agents/skills/main-branch"
    _commit_all(repo, "Probe setup")
    assert _git(repo, "status", "--porcelain") == ""
    return at_risk


def _changed_tracked(repo: Path) -> list[str]:
    status = _git(repo, "status", "--porcelain", "--untracked-files=no")
    return sorted(line[3:] for line in status.splitlines())


REVIEW_PROBES = ["legacy_link", "claude_alias", "codex_alias", "codex_cleanup"]


@pytest.mark.parametrize("kind", REVIEW_PROBES)
def test_review_probe_unattended_changes_no_tracked_file_and_plans_it(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path, tmp_path: Path, kind: str
) -> None:
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    at_risk = _probe_repo(business_repo, tmp_path, kind)

    result = update_mod.run(repo=business_repo, interactive=False)

    assert _changed_tracked(business_repo) == []
    assert _git(business_repo, "status", "--porcelain") == ""
    planned = result["surface_refresh"]["planned"]
    assert planned["consent"] == "no_terminal", planned
    assert at_risk in planned["tracked_files"], planned
    assert result["ok"] is True, result["errors"]


@pytest.mark.parametrize("kind", REVIEW_PROBES)
def test_review_probe_yes_changes_only_listed_files(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path, tmp_path: Path, kind: str
) -> None:
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    at_risk = _probe_repo(business_repo, tmp_path, kind)
    asked: list[list[str]] = []

    def say_yes(repo: Path, files: list[str]) -> bool:
        asked.append(files)
        return True

    result = update_mod.run(repo=business_repo, interactive=True, confirm_surfaces=say_yes)

    assert len(asked) == 1
    listed = result["surface_refresh"]["planned"]["tracked_files"]
    assert at_risk in listed
    changed = _changed_tracked(business_repo)
    assert changed, "the approved plan should have changed something"
    for path in changed:
        assert any(path == item or path.startswith(item.rstrip("/") + "/") for item in listed), (
            path,
            listed,
        )
    assert result["ok"] is True, result["errors"]


def test_unattended_guard_reports_a_tracked_change_the_plan_missed(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path
) -> None:
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    entries, _ = engine_mod._link_gitignore_entries()
    (business_repo / ".gitignore").write_text("\n".join(entries) + "\n", encoding="utf-8")
    _commit_all(business_repo, "Current gitignore")
    # A deliberately wrong plan: it misses the AGENTS.md write the apply makes.
    monkeypatch.setattr(
        update_mod,
        "_plan_codex_surface",
        lambda repo: ({"ok": True, "actions": []}, []),
    )

    result = update_mod.run(repo=business_repo, interactive=False)

    assert _changed_tracked(business_repo) == ["AGENTS.md"]
    assert result["ok"] is False
    assert result["surface_refresh"]["planned"]["unapproved_changes"] == ["AGENTS.md"]
    assert any("not approved: AGENTS.md" in error for error in result["errors"])


def _case_insensitive(directory: Path) -> bool:
    probe = directory / "case-probe"
    probe.write_text("", encoding="utf-8")
    try:
        return (directory / "CASE-PROBE").exists()
    finally:
        probe.unlink()


def _with_current_gitignore(repo: Path) -> None:
    entries, _ = engine_mod._link_gitignore_entries()
    (repo / ".gitignore").write_text("\n".join(entries) + "\n", encoding="utf-8")


def test_unattended_update_leaves_a_lowercase_agents_md_alone(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path
) -> None:
    if not _case_insensitive(business_repo):
        pytest.skip("needs a case-insensitive filesystem: agents.md and AGENTS.md differ here")
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    _with_current_gitignore(business_repo)
    _git(business_repo, "mv", "AGENTS.md", "intermediate.md")
    _git(business_repo, "mv", "intermediate.md", "agents.md")
    _commit_all(business_repo, "Lowercase agents.md")

    result = update_mod.run(repo=business_repo, interactive=False)

    assert _git(business_repo, "status", "--porcelain") == ""
    assert (business_repo / "agents.md").read_text(encoding="utf-8") == "# Old guidance\n"
    planned = result["surface_refresh"]["planned"]
    assert planned["consent"] == "no_terminal", planned
    assert "agents.md" in planned["tracked_files"], planned
    assert result["ok"] is True, result["errors"]


@pytest.mark.parametrize("holder", ["business", "other"])
def test_unattended_update_never_writes_through_a_hard_link(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path, tmp_path: Path, holder: str
) -> None:
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    _with_current_gitignore(business_repo)
    codex_mod.write_agents_md(business_repo)
    holder_repo = business_repo
    if holder == "other":
        holder_repo = tmp_path / "other"
        holder_repo.mkdir()
        _git(holder_repo, "init", "-q", "-b", "main")
    shared = holder_repo / "shared-skill.md"
    shared.write_text("stale\n", encoding="utf-8")
    global_skill = codex_mod.global_skill_source_root() / "mb-start" / "SKILL.md"
    global_skill.parent.mkdir(parents=True, exist_ok=True)
    os.link(shared, global_skill)
    _commit_all(holder_repo, "Shared skill")
    if holder == "other":
        _commit_all(business_repo, "Current surfaces")

    result = update_mod.run(repo=business_repo, interactive=False)

    assert shared.read_text(encoding="utf-8") == "stale\n"
    assert _git(business_repo, "status", "--porcelain") == ""
    assert _git(holder_repo, "status", "--porcelain") == ""
    planned = result["surface_refresh"]["planned"]
    if holder == "business":
        assert "shared-skill.md" in planned["tracked_files"], planned
    else:
        # Outside the business repo the refresh still runs, into a new file.
        assert global_skill.read_text(encoding="utf-8") != "stale\n"
        assert not os.path.samefile(global_skill, shared)
    assert result["ok"] is True, result["errors"]


def test_planned_personal_backup_is_where_the_link_moves_it(
    monkeypatch: pytest.MonkeyPatch, business_repo: Path, tmp_path: Path
) -> None:
    calls: list[list[str]] = []
    _wheel_update_env(monkeypatch, calls)
    _with_current_gitignore(business_repo)
    codex_mod.write_agents_md(business_repo)
    _commit_all(business_repo, "Current surfaces")
    personal = engine_mod._personal_skills_dir()
    personal.mkdir(parents=True)
    (personal / "mb-start").symlink_to(tmp_path / "missing-engine")

    planned = [
        item["path"]
        for item in engine_mod.plan_link_skills(business_repo)["operations"]
        if item["op"] == "create" and ".mainbranch-backups" in item["path"]
    ]
    result = update_mod.run(repo=business_repo, interactive=False)

    applied = sorted(str(path) for path in (personal / ".mainbranch-backups").rglob("mb-start*"))
    assert planned and applied == planned, (planned, applied)
    assert result["ok"] is True, result["errors"]
