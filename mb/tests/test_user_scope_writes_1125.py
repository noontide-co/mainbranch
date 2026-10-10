"""User-scope record writes beyond connect: `mb connect test` and Google sign-in (#1125).

A full disk or an I/O error while recording a check, signing in to Google in
user scope, or writing back the refresh-token expiry after a read is handled
like #1120's connect path: the true cause, no traceback, nothing left half
changed. Temporary stores, stub token endpoint, no network.
"""

# ruff: noqa: F811
from __future__ import annotations

import errno
import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from mb import connect as connect_mod
from mb import durable
from mb import google_connect as gc
from mb.cli import app
from mb.credential_store import SecretStore
from tests.test_connect_followups_1076 import (
    _assert_untouched,
    _freeze_user_scope,
    _store_snapshot,
    _user_scope_cloudflare,
)
from tests.test_connect_followups_1116 import DETAIL, _doctor_row, _fail_user_write
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
from tests.test_google_mint import _mint_with, _signed_in, _status


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        connect_mod,
        "_run_command",
        lambda *a, **kw: {"ok": True, "returncode": 0, "stdout": "fake-renewal", "stderr": ""},
    )
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")

    def fake_http(url: str, headers: Any = None, **kwargs: Any) -> dict[str, Any]:
        return {
            "ok": True,
            "state": "ready",
            "summary": "Cloudflare credential validated with provider.",
            "safe_to_share": True,
            "upstream": {
                "endpoint_family": kwargs.get("endpoint_family", ""),
                "http_status": 200,
                "response_received": True,
                "error_codes": [],
                "error_messages": [],
                "safe_to_share": True,
            },
        }

    monkeypatch.setattr(connect_mod, "_http_get_json", fake_http)


def _assert_clean(result: Any) -> None:
    for leak in (DETAIL, "Traceback", "unexpected error", "OSError", "errno"):
        assert leak not in result.output, leak


def _test_cloudflare(repo: Path, as_json: bool) -> Any:
    args = ["connect", "test", "cloudflare", "--repo", str(repo)]
    return runner.invoke(app, [*args, *(["--json"] if as_json else [])])


# --- 1. mb connect test -----------------------------------------------------------------


@pytest.mark.parametrize(
    ("how", "code"),
    [
        ("write", errno.ENOSPC),
        ("rename", errno.ENOSPC),
        ("write", errno.EIO),
        ("rename", errno.EIO),
    ],
)
@pytest.mark.parametrize("as_json", [False, True])
def test_a_check_that_cannot_be_written_to_the_user_scope_file_is_not_recorded(
    repo: Path, monkeypatch: pytest.MonkeyPatch, how: str, code: int, as_json: bool
) -> None:
    _user_scope_cloudflare(repo)
    path = connect_mod._user_scope_path()
    before = path.read_bytes()
    ok_run = _test_cloudflare(repo, as_json)
    assert ok_run.exit_code == 0, ok_run.output
    path.write_bytes(before)
    _fail_user_write(path, how, code, monkeypatch)

    result = _test_cloudflare(repo, as_json)

    assert result.exit_code == ok_run.exit_code, result.output
    _assert_clean(result)
    assert path.read_bytes() == before
    assert (repo / ".mb/connect.yaml").exists()
    if as_json:
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["recorded"] is False
        assert payload["not_recorded_reason"] == "user_scope_write_failed"
        assert path.name in payload["not_recorded_detail"]
    else:
        assert "mb connect test cloudflare: ok" in result.output
        assert "recorded: no (the user-scope connect file" in result.output
        assert "could not be written" in result.output
    expected = "the disk is full" if code == errno.ENOSPC else "(EIO)"
    assert expected in result.output


def test_a_failed_restore_of_the_user_scope_file_says_it_may_have_changed(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _user_scope_cloudflare(repo)
    path = connect_mod._user_scope_path()

    real_atomic = durable.atomic_write_text

    def always_fail(file: Path, *args: Any, **kwargs: Any) -> None:
        if file == path:
            raise OSError(errno.EIO, DETAIL)
        real_atomic(file, *args, **kwargs)

    monkeypatch.setattr(connect_mod, "atomic_write_text", always_fail)
    # The restore reads the file back first; make it differ from what was there.
    state = {"calls": 0}
    original_read_bytes = Path.read_bytes

    def drifting(self: Path) -> bytes:
        data = original_read_bytes(self)
        if self == path:
            state["calls"] += 1
            if state["calls"] > 1:
                return data + b"# drift\n"
        return data

    monkeypatch.setattr(Path, "read_bytes", drifting)

    result = _test_cloudflare(repo, True)

    assert result.exit_code == 0, result.output
    _assert_clean(result)
    payload = json.loads(result.stdout)
    assert payload["not_recorded_reason"] == "user_scope_write_failed"
    assert "may have changed" in payload["not_recorded_detail"]


def test_a_read_only_user_scope_file_keeps_its_own_reason(repo: Path) -> None:
    _user_scope_cloudflare(repo)
    frozen = _freeze_user_scope()

    result = _test_cloudflare(repo, True)

    payload = json.loads(result.stdout)
    assert payload["not_recorded_reason"] == "user_scope_read_only"
    assert "not_recorded_detail" not in payload
    _assert_untouched(frozen)


def test_doctor_names_a_user_scope_file_that_could_not_be_written(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert _doctor_row(repo, monkeypatch, "user_scope_write_failed") == (
        "`mb connect test stripe` → ready "
        "(not recorded: the user-scope connect file could not be written)"
    )


# --- 2. mb connect google --oauth --scope user ------------------------------------------


def _google_user_args(client_file: Path) -> list[str]:
    return [*_signin_args(client_file), "--scope", "user"]


def _secrets_equal(before: dict[str, str]) -> bool:
    return bool(_local_secrets() == before)


@pytest.mark.parametrize(
    ("how", "code", "cause"),
    [
        ("write", errno.ENOSPC, "the disk is full"),
        ("rename", errno.ENOSPC, "the disk is full"),
        ("write", errno.EIO, "(EIO)"),
        ("rename", errno.EIO, "(EIO)"),
    ],
)
@pytest.mark.parametrize("as_json", [False, True])
def test_a_first_google_sign_in_that_cannot_be_recorded_stores_nothing(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    how: str,
    code: int,
    cause: str,
    as_json: bool,
) -> None:
    google()
    _user_scope_cloudflare(repo)
    path = connect_mod._user_scope_path()
    user_before = path.read_bytes()
    secrets_before = dict(_local_secrets())
    store_before = _store_snapshot()
    _fail_user_write(path, how, code, monkeypatch)

    result = _oauth(repo, *_google_user_args(client_file), *(["--json"] if as_json else []))

    assert result.exit_code == 1, result.output
    _assert_clean(result)
    text = json.loads(result.stdout)["summary"] if as_json else result.output
    if as_json:
        assert json.loads(result.stdout)["state"] == "metadata_write_failed"
    assert path.name in text
    assert cause in text
    assert "The new sign-in was removed, so nothing was stored" in text
    assert "repo metadata is unchanged" in text
    assert path.read_bytes() == user_before
    assert _secrets_equal(secrets_before)
    assert bool(_store_snapshot() == store_before)
    assert not (repo / ".mb/connect.yaml").exists() or "google" not in (
        _config(repo).get("providers") or {}
    )


@pytest.mark.parametrize("as_json", [False, True])
def test_a_google_reauth_that_cannot_be_recorded_puts_the_old_sign_in_back(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    as_json: bool,
) -> None:
    _signed_in(repo, client_file, google, "--scope", "user")
    path = connect_mod._user_scope_path()
    user_before = path.read_bytes()
    config_before = (repo / ".mb/connect.yaml").read_bytes()
    secrets_before = dict(_local_secrets())
    _fail_user_write(path, "write", errno.ENOSPC, monkeypatch)

    result = _oauth(
        repo, "--reauth", "--client-file", str(client_file), *(["--json"] if as_json else [])
    )

    assert result.exit_code == 1, result.output
    _assert_clean(result)
    text = json.loads(result.stdout)["summary"] if as_json else result.output
    assert "The previous Google credentials were restored" in text
    assert path.read_bytes() == user_before
    assert (repo / ".mb/connect.yaml").read_bytes() == config_before
    assert _secrets_equal(secrets_before)


@pytest.mark.parametrize("as_json", [False, True])
def test_a_google_sign_in_whose_restore_also_fails_gives_a_home_relative_recovery(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    as_json: bool,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    google()
    path = connect_mod._user_scope_path()
    real_set = SecretStore.set
    writes = 0

    def fail_restore(self: SecretStore, *args: Any, **kwargs: Any) -> None:
        nonlocal writes
        writes += 1
        if writes > 2:
            raise OSError(DETAIL)
        real_set(self, *args, **kwargs)

    def delete(self: SecretStore, ref: str) -> None:
        raise OSError(DETAIL)

    monkeypatch.setattr(SecretStore, "set", fail_restore)
    monkeypatch.setattr(SecretStore, "delete", delete)
    _fail_user_write(path, "write", errno.ENOSPC, monkeypatch)

    result = _oauth(repo, *_google_user_args(client_file), *(["--json"] if as_json else []))

    assert result.exit_code == 1, result.output
    _assert_clean(result)
    text = json.loads(result.stdout)["summary"] if as_json else result.output
    assert "could not be restored" in text
    assert "Free some disk space first" in text
    assert "--repo ~/biz" in text
    assert str(tmp_path) not in text


def test_a_google_sign_in_over_a_read_only_user_scope_file_is_unchanged(
    repo: Path, client_file: Path, google: Any
) -> None:
    google()
    _user_scope_cloudflare(repo)
    frozen = _freeze_user_scope()

    result = _oauth(repo, *_google_user_args(client_file), "--json")

    assert result.exit_code != 0
    assert "read-only" in result.output
    _assert_untouched(frozen)


# --- 3. the read-time write-back --------------------------------------------------------


@pytest.mark.parametrize("how", ["write", "rename"])
def test_a_read_that_cannot_record_reauth_required_leaves_the_files_and_says_so(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    how: str,
) -> None:
    _signed_in(repo, client_file, google, "--scope", "user")
    path = connect_mod._user_scope_path()
    user_before = path.read_bytes()
    config_before = (repo / ".mb/connect.yaml").read_bytes()
    _mint_with(monkeypatch, status=400, payload={"error": "invalid_grant"})
    _fail_user_write(path, how, errno.ENOSPC, monkeypatch)

    result = connect_mod.read_token("google", repo)

    assert result["rule"] == "reauth_required"
    assert result["ok"] is False
    assert "the disk is full" in result["not_recorded_note"]
    assert "Traceback" not in result["not_recorded_note"]
    assert DETAIL not in result["not_recorded_note"]
    assert path.read_bytes() == user_before
    assert (repo / ".mb/connect.yaml").read_bytes() == config_before
    assert _status(repo)[1]["state"] != "reauth_required"


def test_mb_connect_test_google_reports_the_unwritten_state(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _signed_in(repo, client_file, google, "--scope", "user")
    path = connect_mod._user_scope_path()
    user_before = path.read_bytes()
    _mint_with(monkeypatch, status=400, payload={"error": "invalid_grant"})
    _fail_user_write(path, "write", errno.ENOSPC, monkeypatch)
    gc.forget_minted()

    result = runner.invoke(app, ["connect", "test", "google", "--repo", str(repo), "--json"])

    _assert_clean(result)
    payload = json.loads(result.stdout)
    assert payload["state"] == "reauth_required"
    assert payload["recorded"] is False
    assert payload["not_recorded_reason"] == "user_scope_write_failed"
    assert path.read_bytes() == user_before


def test_a_successful_read_write_back_has_no_note(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, "--scope", "user")
    _mint_with(monkeypatch, status=400, payload={"error": "invalid_grant"})

    result = connect_mod.read_token("google", repo)

    assert "not_recorded_note" not in result
    assert _status(repo)[1]["state"] == "reauth_required"


# --- EACCES, home-relative paths, and a restore that fails for only one slot -------------


def test_a_check_names_the_user_scope_file_with_a_home_relative_path(
    repo: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    _user_scope_cloudflare(repo)
    _fail_user_write(connect_mod._user_scope_path(), "write", errno.ENOSPC, monkeypatch)

    human = _test_cloudflare(repo, False)
    as_json = _test_cloudflare(repo, True)

    detail = json.loads(as_json.stdout)["not_recorded_detail"]
    assert "~/" in detail
    for output in (human.output, detail):
        assert str(tmp_path) not in output
    assert "~/" in human.output


@pytest.mark.parametrize("how", ["write", "rename"])
@pytest.mark.parametrize("as_json", [False, True])
def test_eacces_over_an_existing_file_is_still_read_only_for_a_check(
    repo: Path, monkeypatch: pytest.MonkeyPatch, how: str, as_json: bool
) -> None:
    _user_scope_cloudflare(repo)
    path = connect_mod._user_scope_path()
    before = path.read_bytes()
    _fail_user_write(path, how, errno.EACCES, monkeypatch)

    result = _test_cloudflare(repo, as_json)

    _assert_clean(result)
    if as_json:
        payload = json.loads(result.stdout)
        assert payload["not_recorded_reason"] == "user_scope_read_only"
        assert "not_recorded_detail" not in payload
    else:
        assert "is read-only" in result.output
    assert path.read_bytes() == before


@pytest.mark.parametrize("how", ["write", "rename"])
@pytest.mark.parametrize("as_json", [False, True])
def test_eacces_with_no_user_scope_file_yet_blocks_a_first_google_sign_in(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    how: str,
    as_json: bool,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    google()
    path = connect_mod._user_scope_path()
    assert not path.exists()
    secrets_before = dict(_local_secrets())
    _fail_user_write(path, how, errno.EACCES, monkeypatch)

    result = _oauth(repo, *_google_user_args(client_file), *(["--json"] if as_json else []))

    assert result.exit_code == 1, result.output
    _assert_clean(result)
    text = json.loads(result.stdout)["summary"] if as_json else result.output
    assert "permission to write in its folder ~/" in text
    assert "Make that folder writable" in text
    assert str(tmp_path) not in text
    assert "The new sign-in was removed, so nothing was stored" in text
    assert _secrets_equal(secrets_before)


@pytest.mark.parametrize("how", ["write", "rename"])
def test_eacces_over_an_existing_file_keeps_the_google_read_only_message(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    how: str,
) -> None:
    google()
    _user_scope_cloudflare(repo)
    path = connect_mod._user_scope_path()
    _fail_user_write(path, how, errno.EACCES, monkeypatch)

    result = _oauth(repo, *_google_user_args(client_file), "--json")

    assert result.exit_code == 1, result.output
    _assert_clean(result)
    summary = json.loads(result.stdout)["summary"]
    assert "is read-only" in summary
    assert "could not be restored" not in summary


def test_one_failed_restore_does_not_skip_the_other_slot(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _signed_in(repo, client_file, google, "--scope", "user")
    path = connect_mod._user_scope_path()
    entry = _config(repo)["providers"]["google"]["secrets"]
    grant_ref = entry["oauth_grant"]["ref"]
    token_ref = entry["access_token"]["ref"]
    # A stored token that differs from the one the sign-in mints next.
    SecretStore("local-file").set(token_ref, "SYNTH-OLD-TOKEN-1125")
    secrets_before = dict(_local_secrets())
    real_set = SecretStore.set
    writes = 0

    def set_(self: SecretStore, ref: str, *args: Any, **kwargs: Any) -> None:
        nonlocal writes
        writes += 1
        # The two sign-in writes land; of the two restores, the grant's fails.
        if writes > 2 and ref == grant_ref:
            raise OSError(DETAIL)
        real_set(self, ref, *args, **kwargs)

    monkeypatch.setattr(SecretStore, "set", set_)
    _fail_user_write(path, "write", errno.ENOSPC, monkeypatch)

    result = _oauth(repo, "--reauth", "--client-file", str(client_file), "--json")

    assert result.exit_code == 1, result.output
    _assert_clean(result)
    assert "could not be restored" in json.loads(result.stdout)["summary"]
    # The grant's restore failed; the token's own restore still ran.
    assert _local_secrets()[token_ref] == "SYNTH-OLD-TOKEN-1125"
    assert bool(secrets_before[token_ref] == "SYNTH-OLD-TOKEN-1125")
