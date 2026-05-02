"""``mb update`` install-mode contract tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from mb import __version__
from mb import update as update_mod
from mb.cli import app

runner = CliRunner()


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


def test_update_check_pipx_does_not_run_commands(monkeypatch: Any, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        return _completed(args)

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "0.2.0")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["pull", "start"])
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["ok"] is True
    assert result["old_version"] == __version__
    assert result["new_version"] == "0.2.0"
    assert result["skills_relinked_count"] == 2
    assert calls == []


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
                        "linked": [".claude/skills/start"],
                        "copied": [],
                        "skipped": [".claude/skills/pull"],
                        "errors": [],
                    }
                ),
            )
        return _completed(args, returncode=1, stderr="unexpected")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod.shutil, "which", lambda name: "/opt/homebrew/bin/pipx")
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    repo = tmp_path / "biz"
    result = update_mod.run(repo=repo)

    assert result["ok"] is True
    assert result["new_version"] == "0.2.0"
    assert result["skills_relinked_count"] == 2
    assert calls == [
        ["pipx", "upgrade", "mainbranch"],
        ["mb", "--version"],
        ["mb", "skill", "link", "--repo", str(repo.resolve()), "--json"],
    ]


def test_update_check_clone_reads_origin_without_pull(monkeypatch: Any, tmp_path: Path) -> None:
    root = tmp_path / "engine"
    (root / "mb" / "mb").mkdir(parents=True)
    (root / "mb" / "mb" / "__init__.py").write_text('__version__ = "0.1.2"\n')

    monkeypatch.setattr(update_mod, "install_mode", lambda: "clone")
    monkeypatch.setattr(update_mod, "engine_root", lambda: root)
    monkeypatch.setattr(update_mod, "_version_from_git_ref", lambda _root, _ref: "0.2.0")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["pull", "start", "think"])

    result = update_mod.run(repo=tmp_path / "biz", check=True)

    assert result["ok"] is True
    assert result["old_version"] == "0.1.2"
    assert result["new_version"] == "0.2.0"
    assert result["skills_relinked_count"] == 3
    assert "would run `git pull`" in result["actions"][0]


def test_update_clone_pulls_engine_root_then_relinks(monkeypatch: Any, tmp_path: Path) -> None:
    root = tmp_path / "engine"
    (root / "mb" / "mb").mkdir(parents=True)
    init_file = root / "mb" / "mb" / "__init__.py"
    init_file.write_text('__version__ = "0.1.2"\n')
    calls: list[tuple[list[str], Path | None]] = []

    def fake_run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        calls.append((args, cwd))
        if args == ["git", "pull"]:
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
                        "skipped": [".claude/skills/start"],
                        "errors": [],
                    }
                ),
            )
        return _completed(args, returncode=1, stderr="unexpected")

    monkeypatch.setattr(update_mod, "install_mode", lambda: "clone")
    monkeypatch.setattr(update_mod, "engine_root", lambda: root)
    monkeypatch.setattr(update_mod, "_run_command", fake_run)

    result = update_mod.run(repo=tmp_path / "biz")

    assert result["ok"] is True
    assert result["old_version"] == "0.1.2"
    assert result["new_version"] == "0.2.0"
    assert result["skills_relinked_count"] == 1
    assert calls[0] == (["git", "pull"], root)


def test_update_json_cli_envelope(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(update_mod, "install_mode", lambda: "pipx")
    monkeypatch.setattr(update_mod, "engine_root", lambda: tmp_path / "_engine")
    monkeypatch.setattr(update_mod, "_latest_pypi_version", lambda: "0.2.0")
    monkeypatch.setattr(update_mod, "bundled_skills", lambda: ["start"])

    result = runner.invoke(app, ["update", "--repo", str(tmp_path / "biz"), "--check", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["mode"] == "pipx"
    assert payload["old_version"] == __version__
    assert payload["new_version"] == "0.2.0"
    assert payload["skills_relinked_count"] == 1
    assert payload["errors"] == []
