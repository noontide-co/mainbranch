"""User-scope write failures other than read-only, and doctor's not-recorded label (#1116).

A full disk, an I/O error or a failed rename while writing the user-scope
record restores the credential like the read-only case does; `mb doctor`
names the real reason a check was not recorded. Temporary stores, no network.
"""

# ruff: noqa: F811
from __future__ import annotations

import errno
import json
import os
import shutil
from pathlib import Path
from typing import Any

import pytest

from mb import connect as connect_mod
from mb import doctor as doctor_mod
from mb.cli import app
from mb.durable import atomic_write_text
from tests.test_connect_followups_1076 import (
    _assert_untouched,
    _freeze_user_scope,
    _store_snapshot,
    _user_scope_cloudflare,
)
from tests.test_connect_followups_1085 import _late_write_args
from tests.test_google_connect import (  # noqa: F401 (fixtures are used by name)
    google_env,
    loopback_only_network,
    repo,
    runner,
)
from tests.test_google_hardening3 import _dossier

TOKEN = "sk_live_" + "Q" * 28
DETAIL = "synthetic-backend-detail-1116"


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        connect_mod,
        "_run_command",
        lambda *a, **kw: {"ok": True, "returncode": 0, "stdout": "fake-renewal", "stderr": ""},
    )
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")


def _fail_user_write(path: Path, how: str, code: int, monkeypatch: Any) -> None:
    """Make writing the user-scope file fail with ``code``, never read-only."""

    if how == "rename":
        real_replace = os.replace

        def replace(src: Any, dst: Any, *args: Any, **kwargs: Any) -> None:
            if Path(dst) == path:
                raise OSError(code, DETAIL)
            real_replace(src, dst, *args, **kwargs)

        monkeypatch.setattr(os, "replace", replace)
        return
    real_atomic = atomic_write_text

    def atomic(file: Path, *args: Any, **kwargs: Any) -> None:
        if file == path:
            raise OSError(code, DETAIL)
        real_atomic(file, *args, **kwargs)

    monkeypatch.setattr(connect_mod, "atomic_write_text", atomic)


def _run(repo: Path, operation: str, as_json: bool) -> Any:
    args = ["connect", *_late_write_args(operation), "--repo", str(repo)]
    return runner.invoke(app, [*args, *(["--json"] if as_json else [])], input=TOKEN + "\n")


def _summary(result: Any, as_json: bool) -> str:
    if not as_json:
        return str(result.output)
    payload = json.loads(result.stdout)
    assert payload["state"] == "metadata_write_failed"
    assert payload["ok"] is False
    return str(payload["summary"])


def _assert_clean(result: Any) -> None:
    for leak in (DETAIL, "Q" * 28, "fake-renewal", "Traceback", "unexpected error", "OSError"):
        assert leak not in result.output, leak


@pytest.mark.parametrize(
    ("how", "code", "cause"),
    [
        ("write", errno.ENOSPC, "the disk is full"),
        ("rename", errno.ENOSPC, "the disk is full"),
        ("write", errno.EIO, "(EIO)"),
        ("rename", errno.EXDEV, "(EXDEV)"),
    ],
)
@pytest.mark.parametrize("operation", ["connect", "reconnect", "rotate"])
@pytest.mark.parametrize("as_json", [False, True])
def test_a_failed_user_scope_write_restores_the_credential(
    repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    how: str,
    code: int,
    cause: str,
    operation: str,
    as_json: bool,
) -> None:
    _user_scope_cloudflare(repo, source="op://Business/Cloudflare/credential")
    path = connect_mod._user_scope_path()
    frozen = (path, path.read_bytes(), path.stat().st_ino, path.stat().st_mode & 0o777)
    before = _store_snapshot()
    config_before = (repo / ".mb/connect.yaml").read_bytes()
    _fail_user_write(path, how, code, monkeypatch)

    result = _run(repo, operation, as_json)

    assert result.exit_code == 1, result.output
    _assert_clean(result)
    summary = _summary(result, as_json)
    assert path.name in summary
    assert "not recorded" in summary
    assert cause in summary
    assert "repo metadata is unchanged" in summary
    # A first connect had no credential to put back; the others replaced one.
    if operation == "connect":
        assert "The new credential was removed" in summary
    else:
        assert "The previous credential was restored" in summary
    # Compare booleans so a failing assertion never prints credential bytes.
    assert bool(_store_snapshot() == before)
    assert (repo / ".mb/connect.yaml").read_bytes() == config_before
    _assert_untouched(frozen)


@pytest.mark.parametrize("as_json", [False, True])
@pytest.mark.parametrize("operation", ["connect", "reconnect"])
def test_a_failed_restore_after_a_full_disk_gives_the_sanitized_recovery(
    repo: Path, monkeypatch: pytest.MonkeyPatch, as_json: bool, operation: str
) -> None:
    from mb.credential_store import SecretStore

    _user_scope_cloudflare(repo)
    path = connect_mod._user_scope_path()
    before = _store_snapshot()
    real_set = SecretStore.set
    writes = 0

    def set_(self: SecretStore, *args: Any, **kwargs: Any) -> None:
        nonlocal writes
        writes += 1
        if writes > 1:
            raise OSError(DETAIL)
        real_set(self, *args, **kwargs)

    def delete(self: SecretStore, ref: str) -> None:
        raise OSError(DETAIL)

    with monkeypatch.context() as patch:
        _fail_user_write(path, "write", errno.ENOSPC, patch)
        patch.setattr(SecretStore, "set", set_)
        patch.setattr(SecretStore, "delete", delete)
        result = _run(repo, operation, as_json)

    assert result.exit_code == 1, result.output
    _assert_clean(result)
    summary = _summary(result, as_json)
    assert path.name in summary
    assert "the disk is full" in summary
    assert "could not be restored" in summary
    assert "Free some disk space first" in summary
    assert "`mb connect " in summary
    assert bool(_store_snapshot() != before)


@pytest.mark.parametrize("as_json", [False, True])
def test_a_user_scope_file_that_no_longer_parses_stores_nothing(repo: Path, as_json: bool) -> None:
    # Another credential first, so the store already exists.
    connect_mod.connect_provider("apify", repo=repo, token="apify-fixture-token")
    path = connect_mod._user_scope_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("repos: [unclosed\n", encoding="utf-8")
    before = _store_snapshot()
    data = path.read_bytes()

    result = _run(repo, "connect", as_json)

    assert result.exit_code == 2, result.output
    _assert_clean(result)
    assert "invalid YAML" in result.output
    assert bool(_store_snapshot() == before)
    assert path.read_bytes() == data


# --- mb doctor: the not-recorded label follows the reason ---------------------------------


def _doctor_row(repo: Path, monkeypatch: pytest.MonkeyPatch, reason: str) -> str:
    result = {
        "ok": True,
        "state": "ready",
        "recorded": False,
        "not_recorded_reason": reason,
        "status": {"state": "invalid"},
    }
    monkeypatch.setattr(connect_mod, "test_provider", lambda *a, **kw: result)
    _dossier(repo, "Stripe", "stripe")
    return str(doctor_mod._dossier_verify_section(repo)["checks"][0]["summary"])


def test_doctor_names_a_tracked_connect_yaml(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert _doctor_row(repo, monkeypatch, "connect_yaml_tracked") == (
        "`mb connect test stripe` → ready (not recorded: .mb/connect.yaml is tracked by git)"
    )


def test_doctor_names_a_read_only_user_scope_file(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert _doctor_row(repo, monkeypatch, "user_scope_read_only") == (
        "`mb connect test stripe` → ready (not recorded: the user-scope connect file is read-only)"
    )


def test_doctor_guesses_no_cause_for_another_reason(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    row = _doctor_row(repo, monkeypatch, "a_future_reason")

    assert row == "`mb connect test stripe` → ready (not recorded)"


def test_doctor_row_over_a_real_read_only_user_scope_file(repo: Path) -> None:
    _user_scope_cloudflare(repo)
    frozen = _freeze_user_scope()
    _dossier(repo, "Cloudflare", "cloudflare")

    row = doctor_mod._dossier_verify_section(repo)["checks"][0]

    assert row["summary"].endswith("(not recorded: the user-scope connect file is read-only)")
    assert ".mb/connect.yaml is tracked" not in row["summary"]
    _assert_untouched(frozen)
