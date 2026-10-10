"""User-scope refusals and recovery hints; temporary stores, no network."""

# ruff: noqa: F811
from __future__ import annotations

import json
import os
import shlex
import shutil
from pathlib import Path
from typing import Any

import pytest

from mb import connect as connect_mod
from mb import google_connect as gc
from mb.cli import app
from mb.durable import atomic_write_text
from tests.test_connect_followups_1076 import (
    _assert_refusal,
    _assert_untouched,
    _store_snapshot,
    _user_scope_cloudflare,
)
from tests.test_google_connect import (  # noqa: F401
    ACCESS,
    BOTH_SCOPES,
    REFRESH,
    _oauth,
    _signin_args,
    assert_no_sentinel,
    client_file,
    google_env,
    loopback_only_network,
    repo,
    runner,
)
from tests.test_google_probe import _api, _mint


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        gc,
        "_sign_in",
        lambda *a, **kw: {
            "refresh_token": REFRESH,
            "access_token": ACCESS,
            "scope": BOTH_SCOPES,
        },
    )
    _api(monkeypatch)
    _mint(monkeypatch)
    monkeypatch.setattr(
        connect_mod,
        "_run_command",
        lambda *a, **kw: {"ok": True, "returncode": 0, "stdout": "fake-renewal", "stderr": ""},
    )


def _deny_writes(path: Path, cause: str, monkeypatch: pytest.MonkeyPatch) -> None:
    if cause == "mode":
        path.chmod(0o400)
        return
    real_open = os.open
    real_path_open = Path.open
    real_atomic = atomic_write_text

    def denied_open(file: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        if Path(file) == path and flags & (os.O_WRONLY | os.O_RDWR):
            raise PermissionError("synthetic write denial")
        return real_open(file, flags, *args, **kwargs)

    def denied_path_open(file: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if file == path and any(flag in mode for flag in "wa+"):
            raise PermissionError("synthetic write denial")
        return real_path_open(file, mode, *args, **kwargs)

    def denied_atomic(file: Path, *args: Any, **kwargs: Any) -> Any:
        if file == path:
            raise PermissionError("synthetic write denial")
        return real_atomic(file, *args, **kwargs)

    monkeypatch.setattr(os, "open", denied_open)
    monkeypatch.setattr(Path, "open", denied_path_open)
    monkeypatch.setattr(connect_mod, "atomic_write_text", denied_atomic)


@pytest.mark.parametrize("cause", ["mode", "permission"])
@pytest.mark.parametrize("as_json", [False, True])
@pytest.mark.parametrize("operation", ["connect", "metadata", "rotate", "google", "reauth"])
def test_unwritable_user_scope_refuses_before_storing(
    repo: Path,
    client_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    cause: str,
    as_json: bool,
    operation: str,
) -> None:
    _user_scope_cloudflare(repo, source="op://Business/Cloudflare/credential")
    if operation == "reauth":
        assert _oauth(repo, *_signin_args(client_file), "--scope", "user").exit_code == 0
    path = connect_mod._user_scope_path()
    _deny_writes(path, cause, monkeypatch)
    frozen = (path, path.read_bytes(), path.stat().st_ino, path.stat().st_mode & 0o777)
    before = _store_snapshot()
    config_before = (repo / ".mb/connect.yaml").read_bytes()
    if operation in {"google", "reauth"}:
        args = ["google", "--oauth", *_signin_args(client_file), "--scope", "user"]
        if operation == "reauth":
            args.append("--reauth")
    elif operation == "rotate":
        monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")
        args = ["rotate", "cloudflare"]
    elif operation == "metadata":
        args = ["stripe", "--scope", "user", "--metadata", "account_id=example"]
    else:
        args = ["stripe", "--scope", "user", "--token-stdin"]
    result = runner.invoke(
        app,
        ["connect", *args, "--repo", str(repo), *(["--json"] if as_json else [])],
        input="sk_live_SYNTH1085abcdefghij\n",
    )
    _assert_refusal(result, as_json, path)
    assert_no_sentinel(result.output)
    assert "sk_live_SYNTH1085" not in result.output
    assert _store_snapshot() == before
    assert (repo / ".mb/connect.yaml").read_bytes() == config_before
    _assert_untouched(frozen)


@pytest.mark.parametrize("existing", ["metadata", "legacy"])
@pytest.mark.parametrize("interrupt_after", [0, 1])
def test_interrupted_google_retry_keeps_inherited_scope_and_can_finish(
    repo: Path,
    client_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    existing: str,
    interrupt_after: int,
) -> None:
    repo = repo.rename(repo.with_name("business ' $(unused)"))
    connect_mod.connect_provider(
        "google",
        repo=repo,
        scope="user",
        token="fake-legacy" if existing == "legacy" else "",
        metadata_pairs=["search_console_site=sc-domain:example.com"],
    )
    from mb.credential_store import SecretStore

    real_set = SecretStore.set
    calls = 0

    def interrupted(self: Any, *args: Any, **kwargs: Any) -> None:
        nonlocal calls
        if calls == interrupt_after:
            raise KeyboardInterrupt
        calls += 1
        real_set(self, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(SecretStore, "set", interrupted)
        result = _oauth(
            repo,
            *_signin_args(client_file),
            *(["--replace-access-token"] if existing == "legacy" else []),
            "--json",
        )
    assert result.exit_code == 130
    summary = json.loads(result.stdout)["summary"]
    command = next(
        shlex.split(part)
        for part in summary.split("`")[1::2]
        if part.startswith("mb connect google")
    )
    assert command[command.index("--scope") + 1] == "user"
    assert command[command.index("--repo") + 1] == str(repo)
    assert ("--replace-access-token" in command) == (existing == "legacy")
    retried = runner.invoke(app, [*command[1:], *_signin_args(client_file), "--json"])
    assert retried.exit_code == 0
    assert json.loads(retried.stdout)["scope"] == "user"
    assert_no_sentinel(result.output + retried.output)


@pytest.mark.parametrize("provider", ["cloudflare", "google"])
@pytest.mark.parametrize("cause", ["mode", "permission"])
@pytest.mark.parametrize("as_json", [False, True])
def test_check_names_the_file_when_its_result_cannot_be_recorded(
    repo: Path,
    client_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    provider: str,
    cause: str,
    as_json: bool,
) -> None:
    _user_scope_cloudflare(repo)
    if provider == "google":
        assert _oauth(repo, *_signin_args(client_file), "--scope", "user").exit_code == 0
    args = ["connect", "test", provider, "--repo", str(repo)]
    writable = runner.invoke(app, [*args, "--json"])
    path = connect_mod._user_scope_path()
    _deny_writes(path, cause, monkeypatch)
    before = path.read_bytes()
    result = runner.invoke(app, [*args, *(["--json"] if as_json else [])])
    assert result.exit_code == writable.exit_code
    if as_json:
        payload = json.loads(result.stdout)
        assert payload["recorded"] is False
        assert payload["not_recorded_reason"] == "user_scope_read_only"
    else:
        lines = [line for line in result.output.splitlines() if line.startswith("recorded: no")]
        assert len(lines) == 1
        assert "read-only" in lines[0]
        assert path.name in lines[0]
    assert path.read_bytes() == before
    assert_no_sentinel(result.output)


@pytest.mark.parametrize("reauth", [False, True])
@pytest.mark.parametrize("cause", ["mode", "permission", "atomic"])
def test_google_mid_write_read_only_restores_and_repairs_file_first(
    repo: Path,
    client_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    reauth: bool,
    cause: str,
) -> None:
    _user_scope_cloudflare(repo)
    if reauth:
        assert _oauth(repo, *_signin_args(client_file), "--scope", "user").exit_code == 0
    path = connect_mod._user_scope_path()
    store_before = _store_snapshot()
    config_before = (repo / ".mb/connect.yaml").read_bytes()
    real_write = connect_mod._write_user_scope_provider

    def race(*args: Any, **kwargs: Any) -> Path:
        if cause == "atomic":

            def denied(*a: Any, **kw: Any) -> Any:
                raise PermissionError("synthetic replacement denial")

            monkeypatch.setattr(connect_mod, "atomic_write_text", denied)
        else:
            _deny_writes(path, cause, monkeypatch)
        return real_write(*args, **kwargs)

    monkeypatch.setattr(connect_mod, "_write_user_scope_provider", race)
    result = _oauth(
        repo,
        *_signin_args(client_file),
        "--scope",
        "user",
        *(["--reauth"] if reauth else []),
        "--json",
    )
    payload = json.loads(result.stdout)
    assert result.exit_code == 1
    assert payload["state"] == "metadata_write_failed"
    summary = payload["summary"]
    assert path.name in summary
    assert "read-only" in summary
    assert "writable" in summary
    # The sign-in is not kept: what was stored before is put back (#1129).
    assert (
        "The previous Google credentials were restored." in summary
        if reauth
        else "The new sign-in was removed, so nothing was stored." in summary
    )
    assert "The repo metadata is unchanged." in summary
    assert bool(_store_snapshot() == store_before)
    assert (repo / ".mb/connect.yaml").read_bytes() == config_before
    assert_no_sentinel(result.output)


def _deny_late_user_write(path: Path, cause: str, monkeypatch: pytest.MonkeyPatch) -> None:
    real_replace = os.replace
    real_open = os.open
    opens = 0

    def replace(src: Any, dst: Any, *args: Any, **kwargs: Any) -> None:
        if Path(dst) == path:
            raise PermissionError("synthetic replacement denial")
        real_replace(src, dst, *args, **kwargs)

    def opened(file: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        nonlocal opens
        if Path(file) == path and flags & (os.O_WRONLY | os.O_RDWR):
            opens += 1
            if opens > 1:
                raise PermissionError("synthetic late open denial")
        return real_open(file, flags, *args, **kwargs)

    if cause == "atomic":
        monkeypatch.setattr(os, "replace", replace)
    else:
        monkeypatch.setattr(os, "open", opened)


def _late_write_args(operation: str) -> list[str]:
    if operation == "rotate":
        return ["rotate", "cloudflare"]
    provider = "cloudflare" if operation == "reconnect" else "stripe"
    return [provider, "--scope", "user", "--token-stdin"]


@pytest.mark.parametrize("cause", ["atomic", "late_open"])
@pytest.mark.parametrize("as_json", [False, True])
@pytest.mark.parametrize("operation", ["connect", "reconnect", "rotate"])
def test_late_user_scope_denial_restores_credential(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    cause: str,
    as_json: bool,
    operation: str,
) -> None:
    _user_scope_cloudflare(repo, source="op://Business/Cloudflare/credential")
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")
    path = connect_mod._user_scope_path()
    frozen = (path, path.read_bytes(), path.stat().st_ino, path.stat().st_mode & 0o777)
    before = _store_snapshot()
    config_before = (repo / ".mb/connect.yaml").read_bytes()
    _deny_late_user_write(path, cause, monkeypatch)
    result = runner.invoke(
        app,
        [
            "connect",
            *_late_write_args(operation),
            "--repo",
            str(repo),
            *(["--json"] if as_json else []),
        ],
        input="sk_live_" + "X" * 28 + "\n",
    )
    assert "X" * 28 not in result.output
    assert "fake-renewal" not in result.output
    _assert_refusal(result, as_json, path)
    assert "Nothing else was changed." in result.output
    # Compare booleans so a failing assertion never prints credential bytes.
    assert bool(_store_snapshot() == before)
    assert (repo / ".mb/connect.yaml").read_bytes() == config_before
    _assert_untouched(frozen)


@pytest.mark.parametrize("as_json", [False, True])
@pytest.mark.parametrize("operation", ["connect", "rotate"])
def test_failed_credential_rollback_reports_partial_write_and_replayable_recovery(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    as_json: bool,
    operation: str,
) -> None:
    from mb.credential_store import SecretStore

    repo = repo.rename(repo.with_name("business space ' quote"))
    _user_scope_cloudflare(repo, source="op://Business/Cloudflare/credential")
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")
    path = connect_mod._user_scope_path()
    frozen = (path, path.read_bytes(), path.stat().st_ino, path.stat().st_mode & 0o777)
    before = _store_snapshot()
    config_before = (repo / ".mb/connect.yaml").read_bytes()
    real_set = SecretStore.set
    writes = 0

    def set_(self: SecretStore, *args: Any, **kwargs: Any) -> None:
        nonlocal writes
        writes += 1
        if writes > 1:
            raise OSError("synthetic-rollback-sensitive-detail")
        real_set(self, *args, **kwargs)

    def delete(self: SecretStore, ref: str) -> None:
        raise OSError("synthetic-rollback-sensitive-detail")

    with monkeypatch.context() as patch:
        _deny_late_user_write(path, "atomic", patch)
        patch.setattr(SecretStore, "set", set_)
        patch.setattr(SecretStore, "delete", delete)
        result = runner.invoke(
            app,
            [
                "connect",
                *_late_write_args(operation),
                "--repo",
                str(repo),
                *(["--json"] if as_json else []),
            ],
            input="sk_live_" + "X" * 28 + "\n",
        )
    assert result.exit_code == 1
    assert "Nothing else was changed." not in result.output
    assert "synthetic-rollback-sensitive-detail" not in result.output
    assert "X" * 28 not in result.output
    assert "fake-renewal" not in result.output
    summary = result.output
    if as_json:
        payload = json.loads(result.stdout)
        assert payload["state"] == "metadata_write_failed"
        assert payload["ok"] is False
        assert payload["safe_to_share"] is True
        summary = payload["summary"]
    assert path.name in summary
    assert "not recorded" in summary
    assert "writable" in summary
    assert bool(_store_snapshot() != before)
    assert (repo / ".mb/connect.yaml").read_bytes() == config_before
    _assert_untouched(frozen)
    command = next(
        shlex.split(part) for part in summary.split("`")[1::2] if part.startswith("mb connect")
    )
    assert command[command.index("--scope") + 1] == "user"
    assert command[command.index("--repo") + 1] == str(repo)
    assert summary.index("writable") < summary.index("`mb connect")
    retried = runner.invoke(app, [*command[1:], "--json"], input="sk_live_" + "X" * 28 + "\n")
    assert retried.exit_code == 0
    assert json.loads(retried.stdout)["scope"] == "user"
