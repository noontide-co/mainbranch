"""A read-only or corrupt user-scope file never leaves a sign-in half-changed (#1129).

Temporary stores, stub token endpoint, no network.
"""

# ruff: noqa: F811
from __future__ import annotations

import errno
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest

from mb import connect as connect_mod
from mb import google_connect as gc
from mb.cli import app
from tests.test_connect_followups_1076 import _user_scope_cloudflare
from tests.test_connect_followups_1116 import _fail_user_write
from tests.test_google_connect import (  # noqa: F401 (fixtures are used by name)
    _config,
    _local_secrets,
    _oauth,
    _signin_args,
    client_file,
    google,
    google_env,
    loopback_only_network,
    repo,
    runner,
)
from tests.test_google_mint import _mint_with, _signed_in, _token

CORRUPT = ":\n  - [unclosed"


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")


def _expired(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Path:
    monkeypatch.setenv("HOME", str(tmp_path))
    _signed_in(repo, client_file, google, "--scope", "user")
    _mint_with(monkeypatch, status=400, payload={"error": "invalid_grant"})
    gc.forget_minted()
    return connect_mod._user_scope_path()


def _tmp_files(folder: Path) -> list[str]:
    return sorted(p.name for p in folder.rglob("*.tmp"))


# --- 1. read-only file during the read write-back ----------------------------------------


@pytest.mark.parametrize("how", ["frozen", "eacces_writable_folder"])
def test_read_writeback_on_a_read_only_file_puts_the_metadata_back(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    how: str,
) -> None:
    path = _expired(repo, client_file, google, monkeypatch, tmp_path)
    config_path = repo / ".mb" / "connect.yaml"
    config_before = config_path.read_bytes()
    user_before = path.read_bytes()
    if how == "frozen":
        os.chmod(path, 0o400)
    else:
        _fail_user_write(path, "write", errno.EACCES, monkeypatch)
    try:
        result = connect_mod.read_token("google", repo)
    finally:
        os.chmod(path, 0o600)

    assert result["ok"] is False and result["rule"] == "reauth_required"
    note = result["not_recorded_note"]
    assert "read-only" in note and "could not be put back" not in note
    assert "~/" in note and str(tmp_path) not in note
    assert config_path.read_bytes() == config_before
    assert path.read_bytes() == user_before
    assert _tmp_files(tmp_path) == []


# --- 2. corrupt user-scope file during Google sign-in ------------------------------------


def _corrupt_before_write(monkeypatch: pytest.MonkeyPatch) -> None:
    real = connect_mod._write_user_scope_provider

    def corrupt(*args: Any, **kwargs: Any) -> Path:
        connect_mod._user_scope_path().write_text(CORRUPT)
        return real(*args, **kwargs)

    monkeypatch.setattr(connect_mod, "_write_user_scope_provider", corrupt)


@pytest.mark.parametrize("fresh", [True, False])
def test_signin_with_an_unreadable_user_scope_file_restores_both_slots(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    fresh: bool,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    google()
    if fresh:
        _user_scope_cloudflare(repo)
        args = [*_signin_args(client_file), "--scope", "user"]
        secrets_before = dict(_local_secrets())
    else:
        _signed_in(repo, client_file, google, "--scope", "user")
        args = ["--reauth", "--client-file", str(client_file)]
        secrets_before = dict(_local_secrets())
    config_path = repo / ".mb" / "connect.yaml"
    config_before = config_path.read_bytes()
    _corrupt_before_write(monkeypatch)

    result = _oauth(repo, *args, "--json")

    assert result.exit_code == 1, result.output
    payload = json.loads(result.stdout)
    assert payload["state"] == "metadata_write_failed"
    summary = payload["summary"]
    assert "user-scope connect file ~/" in summary
    assert "unreadable or invalid YAML" in summary and "Fix or move that file" in summary
    assert "repo metadata could not be written" not in summary
    assert ("restored" in summary) == (not fresh)
    assert dict(_local_secrets()) == secrets_before
    assert config_path.read_bytes() == config_before
    assert str(tmp_path) not in result.output and "Traceback" not in result.output


# --- 3. corrupt user-scope file read after the repo metadata was written ------------------


def test_corrupt_user_scope_file_after_the_repo_write_leaves_no_half_update(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = _expired(repo, client_file, google, monkeypatch, tmp_path)
    config_path = repo / ".mb" / "connect.yaml"
    config_before = config_path.read_bytes()
    real = connect_mod._write_config

    def write_then_corrupt(*args: Any, **kwargs: Any) -> Path:
        out = real(*args, **kwargs)
        path.write_text(CORRUPT)
        return out

    monkeypatch.setattr(connect_mod, "_write_config", write_then_corrupt)
    result = connect_mod.read_token("google", repo)

    assert result["ok"] is False and result["rule"] == "reauth_required"
    assert "unreadable or invalid YAML" in result["not_recorded_note"]
    assert str(tmp_path) not in result["not_recorded_note"]
    assert config_path.read_bytes() == config_before
    assert _tmp_files(tmp_path) == []


# --- 4. note position -----------------------------------------------------------------


def test_token_and_exec_print_the_note_after_their_error_line(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = _expired(repo, client_file, google, monkeypatch, tmp_path)
    _fail_user_write(path, "write", errno.ENOSPC, monkeypatch)
    token = _token(repo)
    gc.forget_minted()
    exec_ = runner.invoke(
        app, ["connect", "exec", "google", "--repo", str(repo), "--", sys.executable, "-c", "pass"]
    )

    for name, out in (("token", token.stderr), ("exec", exec_.stderr)):
        lines = out.splitlines()
        error = next(
            i
            for i, line in enumerate(lines)
            if line.startswith(f"mb connect {name}: ") and "recorded: no" not in line
        )
        note = next(i for i, line in enumerate(lines) if "recorded: no" in line)
        assert error < note, (name, out)


# --- `mb connect test google` after a read-only write-back ------------------------------


def test_connect_test_google_calls_a_read_only_file_read_only(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = _expired(repo, client_file, google, monkeypatch, tmp_path)
    config_before = (repo / ".mb" / "connect.yaml").read_bytes()
    os.chmod(path, 0o400)
    try:
        as_json = runner.invoke(app, ["connect", "test", "google", "--repo", str(repo), "--json"])
        gc.forget_minted()
        human = runner.invoke(app, ["connect", "test", "google", "--repo", str(repo)])
    finally:
        os.chmod(path, 0o600)

    payload = json.loads(as_json.stdout)
    assert payload["recorded"] is False
    assert payload["not_recorded_reason"] == "user_scope_read_only"
    assert "read-only" in payload["not_recorded_detail"]
    assert "could not be written" not in as_json.output
    assert "recorded: no (the user-scope connect file ~/" in human.output
    assert "is read-only" in human.output
    assert str(tmp_path) not in as_json.output + human.output
    assert (repo / ".mb" / "connect.yaml").read_bytes() == config_before
