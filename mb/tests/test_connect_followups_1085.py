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
def test_google_mid_write_recovery_keeps_destination_and_repairs_file_first(
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
    commands = [shlex.split(part) for part in summary.split("`")[1::2]]
    command = next(cmd for cmd in commands if cmd[:2] == ["mb", "connect"])
    assert command[command.index("--repo") + 1] == str(repo)
    if reauth:
        assert command[:4] == ["mb", "connect", "test", "google"]
        assert summary.index("writable") < summary.index("mb connect test google")
    else:
        assert command[:4] == ["mb", "connect", "google", "--oauth"]
        assert command[command.index("--scope") + 1] == "user"
    assert_no_sentinel(result.output)
