"""Credential pre-read deadline regressions, using only a temporary file store."""

# ruff: noqa: F811
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

import pytest

from mb import credential_store as credential_store
from mb.cli import app
from tests.test_google_connect import google_env, repo, runner  # noqa: F401


@pytest.mark.parametrize("scope", ["repo", "user"])
def test_slow_working_backend_keeps_connect_success(
    repo: Path, monkeypatch: pytest.MonkeyPatch, scope: str
) -> None:
    actions: list[str] = []

    def invoke(args: list[str], stdin: str, timeout: float) -> tuple[int, str]:
        action = args[-1]
        payload = json.loads(stdin)
        actions.append(action)
        if timeout < 3:
            time.sleep(timeout)
            raise subprocess.TimeoutExpired(args, timeout)
        time.sleep(3)
        ref = payload["ref"]
        if action == "get":
            stored = credential_store._read_local_secrets()
            response = (
                {"state": "ready", "value": stored[ref]} if ref in stored else {"state": "missing"}
            )
        elif action == "set":
            credential_store._local_set(ref, payload["value"])
            response = {"state": "ready"}
        else:
            raise AssertionError("unexpected helper operation")
        return 0, json.dumps(response)

    monkeypatch.setattr(credential_store, "_invoke_helper", invoke)
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "macos-keychain")
    token = "synthetic-credential-deadline"
    result = runner.invoke(
        app,
        ["connect", "cloudflare", "--scope", scope, "--token-stdin", "--repo", str(repo), "--json"],
        input=token + "\n",
    )
    assert token not in result.output
    payload = json.loads(result.stdout)
    assert result.exit_code == 0
    assert payload["ok"] is True
    assert payload["status"]["state"] == "unvalidated"
    assert actions == (["get", "set", "get"] if scope == "user" else ["set", "get"])
    assert token in credential_store._read_local_secrets().values()


def test_timed_out_user_preread_refuses_before_storing(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    actions: list[str] = []

    def invoke(args: list[str], stdin: str, timeout: float) -> tuple[int, str]:
        actions.append(args[-1])
        raise subprocess.TimeoutExpired(args, timeout)

    monkeypatch.setattr(credential_store, "_invoke_helper", invoke)
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "macos-keychain")
    token = "synthetic-credential-timeout"
    before = credential_store._read_local_secrets()
    result = runner.invoke(
        app,
        [
            "connect",
            "cloudflare",
            "--scope",
            "user",
            "--token-stdin",
            "--repo",
            str(repo),
            "--json",
        ],
        input=token + "\n",
    )
    assert token not in result.output
    payload: dict[str, Any] = json.loads(result.stdout)
    assert result.exit_code == 1
    assert payload["ok"] is False
    assert "Nothing was stored" in payload["summary"]
    assert actions == ["get"]
    assert credential_store._read_local_secrets() == before
    assert not (repo / ".mb/connect.yaml").exists()
