"""``mb update`` install-mode contract tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from mb import __version__
from mb import codex as codex_mod
from mb import update as update_mod
from mb.cli import app

runner = CliRunner()


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
                    {"ok": True, "linked": [], "copied": [], "skipped": [], "errors": []}
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
                    {"ok": True, "linked": [], "copied": [], "skipped": [], "errors": []}
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
                    {"ok": True, "linked": [], "copied": [], "skipped": [], "errors": []}
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
                    {"ok": True, "linked": [], "copied": [], "skipped": [], "errors": []}
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
    monkeypatch.setattr(update_mod, "install_mode", lambda: "wheel")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is False
    assert result["mode"] == "wheel"
    assert result["new_version"] == result["old_version"]
    assert "unsupported install mode" in result["errors"][0]


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
    assert result["errors"] == ["mb skill link returned invalid JSON"]


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
