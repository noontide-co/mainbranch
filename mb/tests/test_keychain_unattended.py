"""No unattended credential read may wait on a macOS keychain dialog (#1005).

Unit tests run everywhere. The integration test runs only on macOS with
``MB_KEYCHAIN_INTEGRATION=1``; it creates a throwaway keychain under the temp
directory, never touches the login keychain, and leaves the user keychain
search list exactly as it found it.
"""

from __future__ import annotations

import ast
import ctypes
import json
import os
import platform
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import yaml

from mb import _credential_helper as helper_mod
from mb import connect as connect_mod
from mb import credential_store as store_mod
from mb import fleet as fleet_mod

MB_PACKAGE = Path(connect_mod.__file__).resolve().parent


def _keychain_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A repo whose Cloudflare and Resend refs are recorded in the macOS Keychain."""

    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    repo = tmp_path / "business"
    repo.mkdir()
    connect_mod.connect_provider(
        "cloudflare", repo, token="fixture-cloudflare", metadata_pairs=["account_id=acct-1"]
    )
    connect_mod.connect_provider("resend", repo, token="re_fixture")
    path = repo / ".mb" / "connect.yaml"
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    for provider, field in (("cloudflare", "api_token"), ("resend", "api_key")):
        config["providers"][provider]["secrets"][field]["backend"] = "macos-keychain"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "macos-keychain")
    monkeypatch.setattr(store_mod.platform, "system", lambda: "Darwin")  # type: ignore[attr-defined]
    return repo


class _RecordingHelper:
    """Stands in for the helper subprocess and records every payload."""

    def __init__(self, get_state: str = "ready") -> None:
        self.get_state = get_state
        self.calls: list[dict[str, Any]] = []

    def run(self, args: list[str], **kwargs: Any) -> SimpleNamespace:
        action = args[-1]
        payload = json.loads(kwargs["input"])
        self.calls.append({"action": action, "payload": payload, "timeout": kwargs["timeout"]})
        if action == "get":
            state = self.get_state
            if state == "prompt-pending" and payload.get("interactive") is True:
                state = "ready"
            if state == "ready":
                return SimpleNamespace(returncode=0, stdout='{"state":"ready","value":"fixture"}')
            return SimpleNamespace(returncode=1, stdout=json.dumps({"state": state}))
        return SimpleNamespace(returncode=0, stdout='{"state":"ready"}')

    def install(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake = SimpleNamespace(
            run=self.run,
            PIPE=subprocess.PIPE,
            DEVNULL=subprocess.DEVNULL,
            TimeoutExpired=subprocess.TimeoutExpired,
            SubprocessError=subprocess.SubprocessError,
        )
        monkeypatch.setattr(store_mod, "subprocess", fake)


def test_every_unattended_caller_reads_with_interaction_off(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _keychain_repo(tmp_path, monkeypatch)
    helper = _RecordingHelper()
    helper.install(monkeypatch)
    monkeypatch.setattr(
        connect_mod,
        "_validate_with_provider",
        lambda provider, secret, metadata=None, **kwargs: {
            "ok": True,
            "state": "ready",
            "checked_at": "2026-01-01T00:00:00Z",
            "provider_verified": True,
            "summary": "fixture",
        },
    )

    connect_mod.connect_provider("resend", repo, token="re_rotated")
    connect_mod.status_provider("cloudflare", repo)
    connect_mod.status_all(repo)
    connect_mod.test_provider("cloudflare", repo)
    connect_mod.read_token("cloudflare", repo)
    connect_mod.exec_with_secret(
        "cloudflare",
        ["true"],
        repo,
        runner=lambda *args, **kwargs: subprocess.CompletedProcess(args, 0),
    )
    connect_mod.doctor(repo)
    token, account_id, error = fleet_mod._cloudflare_credentials("cloudflare", repo, "hub-a")

    assert (token, account_id, error) == ("fixture", "acct-1", "")
    actions = {call["action"] for call in helper.calls}
    assert {"get", "set"} <= actions
    for call in helper.calls:
        assert call["payload"]["interactive"] is False, call["action"]
        assert call["timeout"] <= store_mod.CREDENTIAL_HELPER_TIMEOUT_SECONDS


def test_only_the_keychain_repair_passes_interactive_true() -> None:
    """A source guard: a new interactive caller must be a deliberate choice."""

    offenders: list[str] = []
    for path in sorted(MB_PACKAGE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            for call in ast.walk(node):
                if not isinstance(call, ast.Call):
                    continue
                for keyword in call.keywords:
                    if (
                        keyword.arg == "interactive"
                        and isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is True
                    ):
                        offenders.append(f"{path.name}:{node.name}")
    assert sorted(set(offenders)) == ["cli.py:connect_cmd", "connect.py:repair_keychain"]


def test_denied_read_on_unlocked_keychain_is_prompt_pending() -> None:
    assert (
        helper_mod._denied_state(helper_mod.ERR_SEC_AUTH_FAILED, health="ready") == "prompt-pending"
    )
    assert (
        helper_mod._denied_state(helper_mod.ERR_SEC_INTERACTION_NOT_ALLOWED, health="ready")
        == "prompt-pending"
    )
    assert helper_mod._denied_state(helper_mod.ERR_SEC_ITEM_NOT_FOUND, health="ready") == "missing"
    assert (
        helper_mod._denied_state(helper_mod.ERR_SEC_AUTH_FAILED, health="locked") == "auth-failed"
    )


def test_adapter_get_checks_lock_first_and_never_reads_a_locked_keychain() -> None:
    reads: list[int] = []
    adapter: Any = object.__new__(helper_mod._MacSecurity)
    adapter.health = lambda: "locked"

    def query(ref: str, return_data: bool = False) -> tuple[int, list[int]]:
        reads.append(1)
        return 0, []

    adapter._query = query

    assert adapter.get("fixture-ref") == ("locked", None)
    assert reads == []


def test_adapter_get_maps_untrusted_read_to_prompt_pending() -> None:
    adapter: Any = object.__new__(helper_mod._MacSecurity)
    adapter.health = lambda: "ready"
    adapter._query = lambda ref, return_data=False: (7, [])
    adapter._release_all = lambda values: None
    adapter.security = SimpleNamespace(
        SecItemCopyMatching=lambda query, result: helper_mod.ERR_SEC_AUTH_FAILED
    )
    adapter.core = SimpleNamespace(CFRelease=lambda value: None)

    assert adapter.get("fixture-ref") == ("prompt-pending", None)


class _FakeLibrary:
    """Accepts ctypes argtypes/restype assignments and records calls."""

    def __init__(self, log: list[tuple[str, tuple[Any, ...]]]) -> None:
        object.__setattr__(self, "_log", log)

    def __getattr__(self, name: str) -> Any:
        log = self._log

        def call(*args: Any) -> int:
            log.append((name, args))
            return 0

        fn: Any = call
        object.__setattr__(self, name, fn)
        return fn


@pytest.mark.parametrize(("interactive", "disabled"), [(False, True), (True, False)])
def test_adapter_disables_interaction_unless_explicitly_interactive(
    monkeypatch: pytest.MonkeyPatch, interactive: bool, disabled: bool
) -> None:
    monkeypatch.delenv(helper_mod.TEST_KEYCHAIN_ENV, raising=False)
    log: list[tuple[str, tuple[Any, ...]]] = []
    monkeypatch.setattr(ctypes, "CDLL", lambda path: _FakeLibrary(log))

    helper_mod._MacSecurity(interactive=interactive)

    assert (("SecKeychainSetUserInteractionAllowed", (False,)) in log) is disabled


def test_helper_payload_without_explicit_true_stays_non_interactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[bool] = []

    class Adapter:
        def __init__(self, *, interactive: bool = False) -> None:
            seen.append(interactive)

        def health(self) -> str:
            return "ready"

    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(helper_mod, "_MacSecurity", Adapter)
    for payload in ({}, {"interactive": "true"}, {"interactive": 1}, {"interactive": True}):
        helper_mod._macos("health", payload)

    assert seen == [False, False, False, True]


def test_prompt_pending_fails_fast_with_named_repair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _keychain_repo(tmp_path, monkeypatch)
    _RecordingHelper(get_state="prompt-pending").install(monkeypatch)

    started = time.monotonic()
    status = connect_mod.status_provider("cloudflare", repo)
    token = connect_mod.read_token("cloudflare", repo)
    elapsed = time.monotonic() - started

    assert elapsed < 1.0
    assert status["state"] == connect_mod.BACKEND_FAILURE_STATE
    assert status["secrets"]["api_token"]["backend_state"] == "keychain_prompt_pending"
    assert "Cloudflare" in status["summary"]
    assert "keychain prompt pending" in status["summary"]
    assert status["repair_command"] == "mb connect repair --keychain"
    assert "mb connect repair --keychain" in status["repair"]
    assert "timeout" not in status["summary"].lower()
    assert token["error"] == "Cloudflare credential: keychain prompt pending"
    assert token["repair_command"] == "mb connect repair --keychain"


def test_fleet_warning_names_hub_provider_and_repair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _keychain_repo(tmp_path, monkeypatch)
    _RecordingHelper(get_state="prompt-pending").install(monkeypatch)

    _, _, error = fleet_mod._cloudflare_credentials("cloudflare", repo, "hub-a")

    assert error == (
        "cloudflare connection 'cloudflare': keychain prompt pending; "
        "run mb connect repair --keychain in hub-a"
    )


def test_keychain_repair_asks_only_for_pending_items(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _keychain_repo(tmp_path, monkeypatch)
    helper = _RecordingHelper(get_state="prompt-pending")
    helper.install(monkeypatch)

    result = connect_mod.repair_keychain(repo, interactive=True)

    assert result["ok"] is True
    assert [(item["provider"], item["state"]) for item in result["items"]] == [
        ("cloudflare", "ready"),
        ("resend", "ready"),
    ]
    interactive = [call for call in helper.calls if call["payload"]["interactive"]]
    assert len(interactive) == 2
    assert all(
        call["timeout"] == store_mod.INTERACTIVE_CREDENTIAL_TIMEOUT_SECONDS for call in interactive
    )
    assert "fixture" not in json.dumps(result)


def test_keychain_repair_without_consent_never_asks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _keychain_repo(tmp_path, monkeypatch)
    helper = _RecordingHelper(get_state="prompt-pending")
    helper.install(monkeypatch)

    result = connect_mod.repair_keychain(repo)

    assert result["ok"] is False
    assert result["pending"] == 2
    assert all(call["payload"]["interactive"] is False for call in helper.calls)


def test_cli_keychain_repair_refuses_without_a_terminal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from typer.testing import CliRunner

    from mb.cli import app

    repo = _keychain_repo(tmp_path, monkeypatch)
    helper = _RecordingHelper(get_state="prompt-pending")
    helper.install(monkeypatch)

    result = CliRunner().invoke(app, ["connect", "repair", "--keychain", "--repo", str(repo)])
    assert result.exit_code == 2
    assert "terminal" in result.stderr
    assert helper.calls == []

    missing_flag = CliRunner().invoke(app, ["connect", "repair", "--repo", str(repo)])
    assert missing_flag.exit_code == 2
    assert helper.calls == []


@pytest.mark.parametrize(
    "name",
    ["login.keychain-db", "mbtest-x.keychain", "other.keychain-db"],
)
def test_test_keychain_seam_refuses_anything_but_a_throwaway_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    path = tmp_path / name
    path.write_text("", encoding="utf-8")
    monkeypatch.setenv(helper_mod.TEST_KEYCHAIN_ENV, str(path))

    with pytest.raises(RuntimeError):
        helper_mod._test_keychain_path()


def test_test_keychain_seam_refuses_the_user_keychains_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    keychains = tmp_path / "Library" / "Keychains"
    keychains.mkdir(parents=True)
    path = keychains / "mbtest-x.keychain-db"
    path.write_text("", encoding="utf-8")
    monkeypatch.setenv(helper_mod.TEST_KEYCHAIN_ENV, str(path))

    with pytest.raises(RuntimeError):
        helper_mod._test_keychain_path()


# ---------------------------------------------------------------------------
# macOS integration: throwaway keychain only.
# ---------------------------------------------------------------------------

SECURITY = "/usr/bin/security"
integration = pytest.mark.skipif(
    platform.system() != "Darwin" or os.environ.get("MB_KEYCHAIN_INTEGRATION") != "1",
    reason="macOS keychain integration runs only with MB_KEYCHAIN_INTEGRATION=1 on macOS",
)


def _search_list() -> str:
    return subprocess.run(
        [SECURITY, "list-keychains", "-d", "user"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout


@pytest.fixture
def throwaway_keychain(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
    before = _search_list()
    path = tmp_path / f"mbtest-{secrets.token_hex(4)}.keychain-db"
    password = secrets.token_hex(16)
    try:
        subprocess.run(
            [SECURITY, "create-keychain", "-p", password, str(path)],
            check=True,
            capture_output=True,
            timeout=10,
        )
        # Never leave the throwaway keychain in the user's search list.
        if _search_list() != before:
            listed = [line.strip().strip('"') for line in before.splitlines() if line.strip()]
            subprocess.run(
                [SECURITY, "list-keychains", "-d", "user", "-s", *listed],
                check=True,
                capture_output=True,
                timeout=10,
            )
        subprocess.run(
            [SECURITY, "unlock-keychain", "-p", password, str(path)],
            check=True,
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            [SECURITY, "set-keychain-settings", str(path)],
            check=True,
            capture_output=True,
            timeout=10,
        )
        monkeypatch.setenv(helper_mod.TEST_KEYCHAIN_ENV, str(path))
        yield path
    finally:
        subprocess.run(
            [SECURITY, "delete-keychain", str(path)], capture_output=True, timeout=10, check=False
        )
        assert _search_list() == before


def _require_seam(path: Path) -> None:
    """Refuse to touch any keychain unless the seam names the throwaway one."""

    assert os.environ.get(helper_mod.TEST_KEYCHAIN_ENV) == str(path)
    assert helper_mod._test_keychain_path() == str(path.resolve())


def _foreign_python(tmp_path: Path) -> list[str]:
    """An interpreter the keychain sees as a different app (new code hash)."""

    copy = tmp_path / "foreign-python"
    shutil.copy2(Path(sys.executable).resolve(), copy)
    subprocess.run(
        ["/usr/bin/codesign", "--force", "--sign", "-", str(copy)],
        check=True,
        capture_output=True,
        timeout=60,
    )
    return [str(copy)]


def _helper_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONHOME"] = sys.base_prefix
    env["PYTHONPATH"] = str(MB_PACKAGE.parent)
    return env


@integration
def test_macos_item_from_another_python_reports_prompt_pending_fast(
    tmp_path: Path, throwaway_keychain: Path
) -> None:
    _require_seam(throwaway_keychain)
    ref = "mbtest-ref-foreign"
    created = subprocess.run(
        [*_foreign_python(tmp_path), "-m", "mb._credential_helper", "macos-keychain", "set"],
        input=json.dumps({"ref": ref, "value": "dummy-not-a-secret"}),
        capture_output=True,
        text=True,
        env=_helper_env(),
        timeout=30,
        check=False,
    )
    assert json.loads(created.stdout) == {"state": "ready"}

    store = store_mod.SecretStore("macos-keychain")
    started = time.monotonic()
    probe = store.probe(ref)
    elapsed = time.monotonic() - started

    assert probe.reason == "keychain_prompt_pending"
    assert probe.value == ""
    assert elapsed < 1.0


@integration
def test_macos_item_from_this_python_still_reads(throwaway_keychain: Path) -> None:
    _require_seam(throwaway_keychain)
    store = store_mod.SecretStore("macos-keychain")
    assert store.health()["ok"] is True

    store.set("mbtest-ref-own", "dummy-not-a-secret")

    assert store.probe("mbtest-ref-own") == store_mod.SecretProbe(
        "dummy-not-a-secret", True, True, ""
    )
    store.delete("mbtest-ref-own")
    assert store.probe("mbtest-ref-own").present is False
