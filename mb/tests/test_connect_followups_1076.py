"""Google connect follow-ups from the #1075 review (#1076).

Strict `client_secret` types in a stored grant, user-scope writes that keep
what they do not own, rotate under a locked store, and rotate's step for a
Google entry with a source that is not 1Password. Fake backends and temp
config dirs only.
"""

# The fixtures are imported from test_google_connect, so test parameters
# share their names by design.
# ruff: noqa: F811

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from mb import connect as connect_mod
from mb import credential_store
from mb import google_connect as gc
from mb.cli import app
from tests.test_google_connect import (  # noqa: F401 (fixtures are used by name)
    _google_entry,
    client_file,
    google,
    google_env,
    loopback_only_network,
    repo,
    runner,
)
from tests.test_google_hardening2 import _metadata_only
from tests.test_google_probe import (  # noqa: F401 (fixtures are used by name)
    _api,
    _mint,
    _sign_in,
    _status,
    fixed_day,
)

BASE = {"client_id": "id.example.com", "refresh_token": "r-1"}


def _set_grant(repo: Path, grant: dict[str, Any]) -> None:
    ref = _google_entry(repo)["secrets"]["oauth_grant"]["ref"]
    credential_store.SecretStore("local-file").set(ref, json.dumps(grant))


# --- 1. client_secret types ----------------------------------------------------------


@pytest.mark.parametrize("secret", [[], False, 0, {}, 5, True, 1.5])
def test_a_client_secret_that_is_not_text_is_unreadable(secret: Any) -> None:
    value = json.dumps({**BASE, "client_secret": secret})

    assert gc.client_from_grant(value) is None
    assert gc.grant_repair_command(value) == gc.REAUTH_WITH_CLIENT_COMMAND


@pytest.mark.parametrize("secret", [None, "", "s-1", "missing"])
def test_a_missing_null_empty_or_text_client_secret_is_a_usable_client(secret: Any) -> None:
    grant = dict(BASE)
    if secret != "missing":
        grant["client_secret"] = secret
    value = json.dumps(grant)

    client = gc.client_from_grant(value)

    assert client is not None
    assert client.client_secret == (secret if secret in {"s-1"} else "")
    assert gc.grant_repair_command(value) == ""


@pytest.mark.parametrize("secret", [[], False, 0, {}, 5, True])
def test_every_path_names_the_same_step_for_a_bad_client_secret(
    repo: Path,
    client_file: Path,
    google: Any,
    monkeypatch: pytest.MonkeyPatch,
    secret: Any,
) -> None:
    _sign_in(repo, client_file, google, monkeypatch)
    _set_grant(repo, {**BASE, "client_secret": secret})

    code, status = _status(repo)
    assert status["state"] in {"invalid", "reauth_required"}
    assert status["repair_command"] == gc.REAUTH_WITH_CLIENT_COMMAND
    assert status["secrets"]["oauth_grant"]["usable"] is False
    _mint(monkeypatch)
    _api(monkeypatch)
    for args in (["token", "google", "--print"], ["test", "google", "--json"]):
        result = runner.invoke(app, ["connect", *args, "--repo", str(repo)])
        assert result.exit_code != 0, args
        assert gc.REAUTH_WITH_CLIENT_COMMAND in result.output
    rotated = runner.invoke(app, ["connect", "rotate", "google", "--repo", str(repo), "--json"])
    assert gc.REAUTH_WITH_CLIENT_COMMAND in json.loads(rotated.stdout)["summary"]


# --- 3. user-scope writes ----------------------------------------------------------------


def _user_file() -> Path:
    return connect_mod._user_scope_path()


def test_a_user_scope_write_keeps_other_top_level_keys(repo: Path) -> None:
    path = _user_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump({"version": 1, "note": {"kept": [1, 2]}, "repos": {}}), encoding="utf-8"
    )

    connect_mod.connect_provider(
        "stripe", repo=repo, token="sk_live_SYNTH1076abcdefghij", scope="user"
    )

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["note"] == {"kept": [1, 2]}
    assert data["repos"]


def test_a_read_only_user_scope_file_is_not_replaced_or_changed(repo: Path) -> None:
    path = _user_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"version": 1, "repos": {}}), encoding="utf-8")
    path.chmod(0o400)
    before = path.read_bytes()
    inode = path.stat().st_ino

    with pytest.raises(OSError) as caught:
        connect_mod._write_user_scope({"version": 1, "repos": {"x": {}}})

    assert str(path) in str(caught.value)
    assert "read-only" in str(caught.value)
    assert path.read_bytes() == before
    assert path.stat().st_ino == inode
    assert (path.stat().st_mode & 0o777) == 0o400


def test_a_stale_entry_is_kept_when_the_user_scope_file_is_read_only(repo: Path) -> None:
    connect_mod.connect_provider(
        "google",
        repo=repo,
        metadata_pairs=["search_console_site=sc-domain:example.com"],
        scope="user",
    )
    path = _user_file()
    path.chmod(0o400)
    before = path.read_bytes()
    repo_id = str(connect_mod._read_config(repo)["repo_id"])

    assert connect_mod._drop_user_scope_metadata_only(repo_id, "google") is False

    assert path.read_bytes() == before
    assert (path.stat().st_mode & 0o777) == 0o400


# --- 4. rotate under a locked store ----------------------------------------------------


def test_rotate_over_a_sign_in_under_a_locked_store_names_the_store_repair(
    repo: Path, client_file: Path, google: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _sign_in(repo, client_file, google, monkeypatch)

    def locked(*args: Any, **kwargs: Any) -> credential_store.SecretProbe:
        return credential_store.SecretProbe("", False, False, "keychain_locked")

    monkeypatch.setattr(connect_mod, "_probe_secret_ref", locked)
    status_repair = credential_store.backend_repair("keychain_locked")["repair"]

    result = runner.invoke(app, ["connect", "rotate", "google", "--repo", str(repo), "--json"])

    payload = json.loads(result.stdout)
    assert result.exit_code == 2
    assert payload["rule"] == "rotate_backend_unavailable"
    assert status_repair in payload["summary"]
    assert "--client-file" not in payload["summary"]
    assert "once the store unlocks" in payload["summary"]
    assert connect_mod.status_provider("google", repo)["repair"] == status_repair


# --- 5. rotate_unsupported_source for Google ---------------------------------------------


def test_rotate_over_a_google_entry_with_a_foreign_source_names_the_sign_in(repo: Path) -> None:
    _metadata_only(repo)
    config = connect_mod._read_config(repo)
    config["providers"]["google"]["metadata"]["source"] = "vault://elsewhere/item"
    connect_mod._write_config(repo, config)

    result = runner.invoke(app, ["connect", "rotate", "google", "--repo", str(repo), "--json"])

    payload = json.loads(result.stdout)
    assert payload["rule"] == "rotate_unsupported_source"
    assert f"`{connect_mod.GOOGLE_SIGN_IN_COMMAND}`" in payload["summary"]
    assert "--token-stdin" not in payload["summary"]
