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
from mb.durable import atomic_write_text
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
NON_UTF8 = b"version: 1\nrepos: {}\n# \xff\xfe\n"
# Invalid YAML and invalid UTF-8 are both a corrupt file.
BAD_FILES = {"yaml": CORRUPT.encode(), "non_utf8": NON_UTF8}


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


def _corrupt_before_write(
    monkeypatch: pytest.MonkeyPatch, content: bytes = BAD_FILES["yaml"]
) -> None:
    real = connect_mod._write_user_scope_provider

    def corrupt(*args: Any, **kwargs: Any) -> Path:
        connect_mod._user_scope_path().write_bytes(content)
        return real(*args, **kwargs)

    monkeypatch.setattr(connect_mod, "_write_user_scope_provider", corrupt)


def _assert_clean(output: str, tmp_path: Path, secrets: dict[str, Any]) -> None:
    assert str(tmp_path) not in output and "Traceback" not in output
    assert "UnicodeDecodeError" not in output and "codec" not in output
    for value in secrets.values():
        assert not isinstance(value, str) or value not in output


@pytest.mark.parametrize("kind", list(BAD_FILES))
@pytest.mark.parametrize("fresh", [True, False])
def test_signin_with_an_unreadable_user_scope_file_restores_both_slots(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    fresh: bool,
    kind: str,
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
    _corrupt_before_write(monkeypatch, BAD_FILES[kind])

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
    assert connect_mod._user_scope_path().read_bytes() == BAD_FILES[kind]
    assert _tmp_files(tmp_path) == []
    _assert_clean(result.output, tmp_path, dict(secrets_before))


# --- 3. corrupt user-scope file read after the repo metadata was written ------------------


@pytest.mark.parametrize("kind", list(BAD_FILES))
def test_corrupt_user_scope_file_after_the_repo_write_leaves_no_half_update(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    kind: str,
) -> None:
    path = _expired(repo, client_file, google, monkeypatch, tmp_path)
    config_path = repo / ".mb" / "connect.yaml"
    config_before = config_path.read_bytes()
    real = connect_mod._write_config

    def write_then_corrupt(*args: Any, **kwargs: Any) -> Path:
        out = real(*args, **kwargs)
        path.write_bytes(BAD_FILES[kind])
        return out

    monkeypatch.setattr(connect_mod, "_write_config", write_then_corrupt)
    result = connect_mod.read_token("google", repo)

    assert result["ok"] is False and result["rule"] == "reauth_required"
    assert "unreadable or invalid YAML" in result["not_recorded_note"]
    _assert_clean(result["not_recorded_note"], tmp_path, {})
    assert config_path.read_bytes() == config_before
    assert path.read_bytes() == BAD_FILES[kind]
    assert _tmp_files(tmp_path) == []


@pytest.mark.parametrize("kind", list(BAD_FILES))
def test_read_with_a_user_scope_file_bad_from_the_start_is_not_recorded(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    kind: str,
) -> None:
    path = _expired(repo, client_file, google, monkeypatch, tmp_path)
    config_path = repo / ".mb" / "connect.yaml"
    config_before = config_path.read_bytes()
    secrets = dict(_local_secrets())
    path.write_bytes(BAD_FILES[kind])

    result = connect_mod.read_token("google", repo)

    assert result["ok"] is False and result["rule"] == "reauth_required"
    assert result["not_recorded_reason"] == "user_scope_write_failed"
    assert "unreadable or invalid YAML" in result["not_recorded_note"]
    assert "could not be put back" not in result["not_recorded_note"]
    _assert_clean(json.dumps(result), tmp_path, secrets)
    assert config_path.read_bytes() == config_before
    assert path.read_bytes() == BAD_FILES[kind]
    assert dict(_local_secrets()) == secrets
    assert _tmp_files(tmp_path) == []


def test_signin_with_a_user_scope_file_bad_from_the_start_stores_nothing(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    google()
    _user_scope_cloudflare(repo)
    path = connect_mod._user_scope_path()
    config_path = repo / ".mb" / "connect.yaml"
    secrets_before = dict(_local_secrets())
    config_before = config_path.read_bytes()
    args = [*_signin_args(client_file), "--scope", "user", "--json"]
    messages = {}
    for kind, content in BAD_FILES.items():
        path.write_bytes(content)
        result = _oauth(repo, *args)
        assert result.exit_code != 0, result.output
        messages[kind] = json.loads(result.stdout)
        _assert_clean(result.output, tmp_path, secrets_before)
        assert dict(_local_secrets()) == secrets_before
        assert config_path.read_bytes() == config_before
        assert path.read_bytes() == content
        assert _tmp_files(tmp_path) == []

    # A file that is not UTF-8 gets the message invalid YAML gets.
    assert messages["non_utf8"] == messages["yaml"]
    assert "unreadable or invalid YAML" in json.dumps(messages["yaml"])


# --- 3b. a check never half-records ----------------------------------------------------


@pytest.mark.parametrize("as_json", [False, True])
@pytest.mark.parametrize("kind", list(BAD_FILES))
def test_connect_test_with_a_corrupt_user_scope_file_never_half_records(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    kind: str,
    as_json: bool,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    _user_scope_cloudflare(repo)
    path = connect_mod._user_scope_path()
    config_path = repo / ".mb" / "connect.yaml"
    config_before = config_path.read_bytes()
    secrets = dict(_local_secrets())
    monkeypatch.setattr(
        connect_mod,
        "_validate_with_provider",
        lambda provider, secret, *a, **k: {
            "ok": True,
            "state": "ready",
            "checked_at": "2026-10-10T00:00:00Z",
            "provider_verified": True,
            "summary": "stubbed check",
        },
    )
    real = connect_mod._write_config

    def write_then_corrupt(*args: Any, **kwargs: Any) -> Path:
        out = real(*args, **kwargs)
        path.write_bytes(BAD_FILES[kind])
        return out

    monkeypatch.setattr(connect_mod, "_write_config", write_then_corrupt)
    cli = ["connect", "test", "cloudflare", "--repo", str(repo), *(["--json"] if as_json else [])]

    result = runner.invoke(app, cli)

    _assert_clean(result.output, tmp_path, secrets)
    assert "unreadable or invalid YAML" in result.output
    assert "recorded: no" in result.output or '"recorded": false' in result.output
    if as_json:
        payload = json.loads(result.stdout)
        assert payload["recorded"] is False
        assert payload["not_recorded_reason"] == "user_scope_write_failed"
        assert "put back" not in payload["not_recorded_detail"]
    assert config_path.read_bytes() == config_before
    assert path.read_bytes() == BAD_FILES[kind]
    assert dict(_local_secrets()) == secrets
    assert _tmp_files(tmp_path) == []


def test_connect_test_says_so_when_the_repo_metadata_cannot_be_put_back(
    repo: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    _user_scope_cloudflare(repo)
    path = connect_mod._user_scope_path()
    monkeypatch.setattr(
        connect_mod,
        "_validate_with_provider",
        lambda provider, secret, *a, **k: {
            "ok": True,
            "state": "ready",
            "checked_at": "2026-10-10T00:00:00Z",
            "provider_verified": True,
            "summary": "stubbed check",
        },
    )
    real_write = connect_mod._write_config
    real_atomic = atomic_write_text
    broken = {"on": False}

    def write_then_corrupt(*args: Any, **kwargs: Any) -> Path:
        out = real_write(*args, **kwargs)
        path.write_bytes(NON_UTF8)
        broken["on"] = True
        return out

    def atomic(file: Path, *args: Any, **kwargs: Any) -> None:
        if broken["on"] and file.name == "connect.yaml":
            raise OSError(errno.EIO, "synthetic")
        real_atomic(file, *args, **kwargs)

    monkeypatch.setattr(connect_mod, "_write_config", write_then_corrupt)
    monkeypatch.setattr(connect_mod, "atomic_write_text", atomic)

    result = runner.invoke(app, ["connect", "test", "cloudflare", "--repo", str(repo), "--json"])

    payload = json.loads(result.stdout)
    assert payload["recorded"] is False
    assert "could not be put back either" in payload["not_recorded_detail"]
    _assert_clean(result.output, tmp_path, {})
    assert "synthetic" not in result.output


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
