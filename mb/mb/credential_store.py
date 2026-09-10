"""Bounded, platform-native credential storage for provider connections.

The public CLI talks to this module only. Native APIs run in a short-lived
helper process so a locked or wedged OS store cannot hang unattended work.
Secret values travel over stdin and stdout, never process arguments or error
messages.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any, NamedTuple

from mb.durable import atomic_write_text

SERVICE_NAME = "mainbranch"
CREDENTIAL_HELPER_TIMEOUT_SECONDS = 8
HELPER_OUTPUT_LIMIT = 1024 * 1024
SUPPORTED_BACKENDS = {"auto", "macos-keychain", "secret-service", "keyring", "local-file"}

KEYCHAIN_RESET_WARNING = (
    "Do not reset or delete the login keychain — that destroys every credential "
    "already stored in it."
)
BACKEND_REPAIRS: dict[str, dict[str, str]] = {
    "keychain_locked": {
        "summary": "The macOS login Keychain is locked, so credentials cannot be read or written.",
        "repair": (
            "Unlock it interactively inside the reader's owning user security session, then "
            "rerun the command in that same session. A desktop unlock does not unlock every "
            "already-running remote session. "
            f"{KEYCHAIN_RESET_WARNING}"
        ),
        "repair_command": "security unlock-keychain ~/Library/Keychains/login.keychain-db",
    },
    "keychain_auth_failed": {
        "summary": (
            "The macOS login Keychain rejected credential access, so credentials "
            "cannot be read or written."
        ),
        "repair": (
            "If backend health is ready, approve the installed reader identity in this item's "
            "Access Control or reconnect from that stable installed mb. Otherwise unlock the "
            "login keychain inside the reader's owning security session. "
            f"{KEYCHAIN_RESET_WARNING}"
        ),
        "repair_command": "open -a 'Keychain Access'",
    },
    "keychain_unavailable": {
        "summary": "The macOS Keychain did not answer, so credentials cannot be read or written.",
        "repair": (
            "Run the reader as the logged-in user in its intended GUI launchd security session, "
            "check the login keychain there, then rerun the command. "
            f"{KEYCHAIN_RESET_WARNING}"
        ),
        "repair_command": "open -a 'Keychain Access'",
    },
    "secret_service_locked": {
        "summary": "The Linux Secret Service collection is locked.",
        "repair": (
            "Unlock the existing login collection in the desktop keyring application, then "
            "rerun the command. Main Branch will not open an unlock prompt during unattended work."
        ),
        "repair_command": "",
    },
    "secret_service_unavailable": {
        "summary": "The Linux Secret Service backend is unavailable.",
        "repair": (
            "Start or repair the desktop Secret Service and its existing default collection, "
            "then rerun the command."
        ),
        "repair_command": "",
    },
    "credential_store_timeout": {
        "summary": "The credential store did not answer before the safety deadline.",
        "repair": (
            "Check or unlock the operating-system credential store interactively, then rerun "
            "the command. Main Branch stopped the unattended attempt."
        ),
        "repair_command": "",
    },
    "backend_incompatible": {
        "summary": "The recorded credential backend is incompatible with this operating system.",
        "repair": (
            "Reconnect this provider on the current machine to its native credential store. "
            "Main Branch will not silently switch stores."
        ),
        "repair_command": "",
    },
    "local_file_corrupt": {
        "summary": "The explicit local credential file is malformed or unreadable.",
        "repair": (
            "Repair or restore the local credential file before reconnecting. Main Branch "
            "refused to overwrite it."
        ),
        "repair_command": "",
    },
    "local_file_unavailable": {
        "summary": "The explicit local credential file is unavailable.",
        "repair": "Check its directory and permissions, then rerun the command.",
        "repair_command": "",
    },
}


def backend_repair(reason: str) -> dict[str, str]:
    """Return sanitized operator guidance for one backend reason."""

    return BACKEND_REPAIRS.get(reason, BACKEND_REPAIRS["keychain_unavailable"])


class CredentialStoreError(RuntimeError):
    """A sanitized credential-store failure safe to show to an operator."""

    def __init__(self, reason: str, message: str = "") -> None:
        detail = backend_repair(reason)
        super().__init__(message or f"{detail['summary']} {detail['repair']}")
        self.reason = reason


class SecretProbe(NamedTuple):
    """Result of reading one credential reference."""

    value: str
    present: bool
    backend_ok: bool
    reason: str


def select_secret_backend(requested: str | None = None) -> str:
    """Select one backend without silently falling back to plaintext storage."""

    raw = requested
    if raw is None:
        raw = os.environ.get("MB_CONNECT_SECRET_BACKEND", "auto")
    choice = str(raw).strip().lower()
    if choice not in SUPPORTED_BACKENDS:
        supported = ", ".join(sorted(SUPPORTED_BACKENDS - {"keyring"}))
        raise ValueError(f"unknown credential backend {choice!r}; choose one of: {supported}")
    if choice == "local-file":
        return choice
    system = platform.system()
    if choice == "keyring":
        # Releases before #959 recorded the generic `keyring` name. The native
        # adapters address the same service/account records without retaining
        # keyring's unbounded, backend-dependent runtime behavior.
        if system == "Darwin":
            return "macos-keychain"
        if system == "Linux":
            return "secret-service"
        raise CredentialStoreError("backend_incompatible")
    if choice == "auto":
        if system == "Darwin":
            return "macos-keychain"
        if system == "Linux":
            return "secret-service"
        raise CredentialStoreError("backend_incompatible")
    if choice == "macos-keychain" and system != "Darwin":
        raise CredentialStoreError("backend_incompatible")
    if choice == "secret-service" and system != "Linux":
        raise CredentialStoreError("backend_incompatible")
    return choice


class SecretStore:
    """Credential-store facade used by connect, status, token, and doctor."""

    def __init__(self, backend: str | None = None) -> None:
        self.backend = select_secret_backend(backend)

    def set(self, ref: str, value: str) -> None:
        if self.backend == "local-file":
            _local_set(ref, value)
            return
        result = _run_helper(self.backend, "set", ref=ref, value=value)
        state = str(result.get("state") or "unavailable")
        if state != "ready":
            raise CredentialStoreError(_reason_for(self.backend, state))

    def get(self, ref: str) -> str:
        return self.probe(ref).value

    def probe(self, ref: str) -> SecretProbe:
        if not ref:
            return SecretProbe("", False, True, "")
        if self.backend == "local-file":
            try:
                data = _read_local_secrets()
            except CredentialStoreError as exc:
                return SecretProbe("", False, False, exc.reason)
            if ref not in data:
                return SecretProbe("", False, True, "")
            return SecretProbe(data[ref], True, True, "")
        result = _run_helper(self.backend, "get", ref=ref)
        state = str(result.get("state") or "unavailable")
        if state == "missing":
            return SecretProbe("", False, True, "")
        if state != "ready":
            return SecretProbe("", False, False, _reason_for(self.backend, state))
        value = result.get("value")
        if not isinstance(value, str):
            return SecretProbe("", False, False, _reason_for(self.backend, "unavailable"))
        return SecretProbe(value, True, True, "")

    def health(self) -> dict[str, Any]:
        reason = ""
        if self.backend == "local-file":
            try:
                _read_local_secrets()
            except CredentialStoreError as exc:
                reason = exc.reason
        else:
            result = _run_helper(self.backend, "health")
            state = str(result.get("state") or "unavailable")
            if state != "ready":
                reason = _reason_for(self.backend, state)
        detail = backend_repair(reason) if reason else None
        return {
            "backend": self.backend,
            "ok": not reason,
            "state": reason or "ready",
            "summary": (
                detail["summary"]
                if detail is not None
                else f"Credential backend {self.backend} is ready."
            ),
            "repair": detail["repair"] if detail is not None else "",
            "repair_command": detail["repair_command"] if detail is not None else "",
            "safe_to_share": True,
        }

    def boundary(self) -> str:
        if self.backend == "macos-keychain":
            return "stored in the macOS login Keychain"
        if self.backend == "secret-service":
            return "stored in the Linux Secret Service default collection"
        return f"stored outside the repo in {_local_secret_path()}"

    def delete(self, ref: str) -> None:
        """Delete an exact reference; used for bounded synthetic native smoke cleanup."""

        if self.backend == "local-file":
            data = _read_local_secrets()
            if ref in data:
                del data[ref]
                _write_local_secrets(data)
            return
        result = _run_helper(self.backend, "delete", ref=ref)
        state = str(result.get("state") or "unavailable")
        if state not in {"ready", "missing"}:
            raise CredentialStoreError(_reason_for(self.backend, state))


def _reason_for(backend: str, state: str) -> str:
    if state == "timed-out":
        return "credential_store_timeout"
    if state == "incompatible":
        return "backend_incompatible"
    if backend == "macos-keychain":
        if state == "locked":
            return "keychain_locked"
        if state == "auth-failed":
            return "keychain_auth_failed"
        return "keychain_unavailable"
    if backend == "secret-service":
        if state in {"locked", "auth-failed"}:
            return "secret_service_locked"
        return "secret_service_unavailable"
    return "local_file_unavailable"


def _run_helper(
    backend: str,
    action: str,
    *,
    ref: str = "",
    value: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"ref": ref}
    if value is not None:
        payload["value"] = value
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "mb._credential_helper", backend, action],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            input=json.dumps(payload),
            timeout=CREDENTIAL_HELPER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {"state": "timed-out"}
    except (OSError, subprocess.SubprocessError):
        return {"state": "unavailable"}
    stdout = completed.stdout or ""
    if len(stdout) > HELPER_OUTPUT_LIMIT:
        return {"state": "unavailable"}
    try:
        result = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        return {"state": "unavailable"}
    if not isinstance(result, dict):
        return {"state": "unavailable"}
    state = result.get("state")
    if state not in {"ready", "missing", "locked", "auth-failed", "unavailable"}:
        return {"state": "unavailable"}
    if completed.returncode != (0 if state in {"ready", "missing"} else 1):
        return {"state": "unavailable"}
    return result


def _local_secret_path() -> Path:
    home = Path(os.environ.get("MAINBRANCH_HOME", Path.home() / ".mainbranch")).expanduser()
    return home / "secrets" / "connect.json"


def _read_local_secrets() -> dict[str, str]:
    path = _local_secret_path()
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CredentialStoreError("local_file_corrupt") from exc
    except OSError as exc:
        raise CredentialStoreError("local_file_unavailable") from exc
    if not isinstance(raw, dict) or any(
        not isinstance(key, str) or not isinstance(value, str) for key, value in raw.items()
    ):
        raise CredentialStoreError("local_file_corrupt")
    return dict(raw)


def _write_local_secrets(data: dict[str, str]) -> None:
    path = _local_secret_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with suppress(OSError):
            path.parent.chmod(0o700)
        atomic_write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")
        with suppress(OSError):
            path.chmod(0o600)
    except OSError as exc:
        raise CredentialStoreError("local_file_unavailable") from exc


def _local_set(ref: str, value: str) -> None:
    data = _read_local_secrets()
    data[ref] = value
    _write_local_secrets(data)
