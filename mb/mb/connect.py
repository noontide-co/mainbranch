"""Integration registry and credential metadata for ``mb connect``."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
import uuid
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

CONFIG_RELATIVE_PATH = Path(".mb") / "connect.yaml"
SERVICE_NAME = "mainbranch"
SENSITIVE_KEY_PARTS = ("token", "secret", "password", "credential", "api_key", "apikey", "key")


@dataclass(frozen=True)
class Provider:
    """Provider registry entry.

    ``required_secrets`` names are local credential slots, not values. They are
    safe to write into repo metadata because actual secret material is stored
    through ``SecretStore``.
    """

    id: str
    name: str
    category: str
    auth: str
    required_secrets: tuple[str, ...]
    metadata_fields: tuple[str, ...]
    description: str
    env_vars: tuple[str, ...] = ()


PROVIDERS: tuple[Provider, ...] = (
    Provider(
        id="google",
        name="Google",
        category="workspace",
        auth="oauth_or_service_account",
        required_secrets=("access_token",),
        metadata_fields=("account_email", "workspace"),
        description="Google Workspace, Drive, Docs, Sheets, Slides, and future analytics sync.",
        env_vars=("GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_OAUTH_TOKEN"),
    ),
    Provider(
        id="meta",
        name="Meta",
        category="ads",
        auth="access_token",
        required_secrets=("access_token",),
        metadata_fields=("ad_account_id", "business_id"),
        description="Meta ads accounts, campaign review, and future performance sync.",
        env_vars=("META_ACCESS_TOKEN",),
    ),
    Provider(
        id="cloudflare",
        name="Cloudflare",
        category="site",
        auth="api_token",
        required_secrets=("api_token",),
        metadata_fields=("account_id", "zone_id"),
        description="Cloudflare Pages, DNS, Workers, and deployment metadata.",
        env_vars=("CLOUDFLARE_API_TOKEN",),
    ),
    Provider(
        id="postiz",
        name="Postiz",
        category="social",
        auth="api_key",
        required_secrets=("api_key",),
        metadata_fields=("workspace",),
        description="Postiz social scheduling and publishing workflows.",
        env_vars=("POSTIZ_API_KEY",),
    ),
    Provider(
        id="apify",
        name="Apify",
        category="research",
        auth="api_token",
        required_secrets=("api_token",),
        metadata_fields=("default_actor",),
        description="Apify research actors and scrape jobs.",
        env_vars=("APIFY_TOKEN",),
    ),
    Provider(
        id="beancount",
        name="Beancount",
        category="finance",
        auth="local_file",
        required_secrets=(),
        metadata_fields=("ledger_path",),
        description="Local ledger paths and finance workflow metadata.",
    ),
    Provider(
        id="transcription",
        name="Whisper / transcription",
        category="media",
        auth="api_key_or_local",
        required_secrets=("api_key",),
        metadata_fields=("engine", "model"),
        description="Whisper-compatible transcription provider or local transcription engine.",
        env_vars=("OPENAI_API_KEY", "WHISPER_API_KEY"),
    ),
)


def provider_map() -> dict[str, Provider]:
    return {provider.id: provider for provider in PROVIDERS}


def provider_registry() -> list[dict[str, Any]]:
    return [
        {
            "id": provider.id,
            "name": provider.name,
            "category": provider.category,
            "auth": provider.auth,
            "required_secrets": list(provider.required_secrets),
            "metadata_fields": list(provider.metadata_fields),
            "description": provider.description,
            "env_vars": list(provider.env_vars),
        }
        for provider in PROVIDERS
    ]


def normalize_provider(provider_id: str) -> Provider:
    key = provider_id.strip().lower().replace("_", "-")
    aliases = {"whisper": "transcription", "cloudflare-pages": "cloudflare"}
    key = aliases.get(key, key)
    providers = provider_map()
    if key not in providers:
        supported = ", ".join(sorted(providers))
        raise ValueError(f"unknown provider {provider_id!r}; supported providers: {supported}")
    return providers[key]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _home() -> Path:
    return Path(os.environ.get("MAINBRANCH_HOME", Path.home() / ".mainbranch")).expanduser()


def _config_path(repo: Path) -> Path:
    return repo / CONFIG_RELATIVE_PATH


def _empty_config() -> dict[str, Any]:
    return {"version": 1, "repo_id": "", "providers": {}}


def _read_config(repo: Path) -> dict[str, Any]:
    path = _config_path(repo)
    if not path.exists():
        return _empty_config()
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    providers = raw.get("providers")
    if not isinstance(providers, dict):
        providers = {}
    return {
        "version": int(raw.get("version") or 1),
        "repo_id": str(raw.get("repo_id") or ""),
        "providers": providers,
    }


def _ensure_repo_id(config: dict[str, Any]) -> str:
    repo_id = str(config.get("repo_id") or "")
    if repo_id:
        return repo_id
    repo_id = uuid.uuid4().hex
    config["repo_id"] = repo_id
    return repo_id


def _write_config(repo: Path, config: dict[str, Any]) -> Path:
    path = _config_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(config, sort_keys=False)
    path.write_text(text, encoding="utf-8")
    return path


def _secret_ref(repo_id: str, provider_id: str, field: str) -> str:
    digest = hashlib.sha256(f"{repo_id}:{provider_id}:{field}".encode()).hexdigest()[:24]
    return f"mainbranch://{digest}/{provider_id}/{field}"


class SecretStore:
    """Best-effort local secret storage outside the repo."""

    def __init__(self, backend: str | None = None) -> None:
        self.backend = backend or _select_secret_backend()

    def set(self, ref: str, value: str) -> None:
        if self.backend == "macos-keychain":
            try:
                _macos_set(ref, value)
            except (OSError, subprocess.SubprocessError) as exc:
                raise RuntimeError("macOS Keychain credential write failed") from exc
            return
        if self.backend == "keyring":
            module = _keyring_module()
            if module is None:
                raise RuntimeError("Python keyring backend is unavailable")
            try:
                module.set_password(SERVICE_NAME, ref, value)
            except Exception as exc:
                raise RuntimeError("Python keyring credential write failed") from exc
            return
        _local_set(ref, value)

    def get(self, ref: str) -> str:
        if self.backend == "macos-keychain":
            return _macos_get(ref)
        if self.backend == "keyring":
            module = _keyring_module()
            if module is None:
                return ""
            try:
                value = module.get_password(SERVICE_NAME, ref)
            except Exception:
                return ""
            return str(value or "")
        return _local_get(ref)

    def boundary(self) -> str:
        if self.backend == "macos-keychain":
            return "stored in the macOS Keychain"
        if self.backend == "keyring":
            return "stored through the Python keyring backend"
        return f"stored outside the repo in {_local_secret_path()}"


def _select_secret_backend() -> str:
    requested = os.environ.get("MB_CONNECT_SECRET_BACKEND", "auto").strip().lower()
    if requested in {"macos-keychain", "keyring", "local-file"}:
        return requested
    if platform.system() == "Darwin" and shutil.which("security"):
        return "macos-keychain"
    if _keyring_module() is not None:
        return "keyring"
    return "local-file"


def _keyring_module() -> Any | None:
    try:
        return importlib.import_module("keyring")
    except ImportError:
        return None


def _macos_set(ref: str, value: str) -> None:
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-a",
            ref,
            "-s",
            SERVICE_NAME,
            "-w",
            value,
            "-U",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )


def _macos_get(ref: str) -> str:
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-a", ref, "-s", SERVICE_NAME, "-w"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.rstrip("\n")


def _local_secret_path() -> Path:
    return _home() / "secrets" / "connect.json"


def _read_local_secrets() -> dict[str, str]:
    path = _local_secret_path()
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return {str(key): str(value) for key, value in raw.items()}


def _write_local_secrets(data: dict[str, str]) -> None:
    path = _local_secret_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with suppress(OSError):
        path.parent.chmod(0o700)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with suppress(OSError):
        path.chmod(0o600)


def _local_set(ref: str, value: str) -> None:
    data = _read_local_secrets()
    data[ref] = value
    _write_local_secrets(data)


def _local_get(ref: str) -> str:
    return _read_local_secrets().get(ref, "")


def _parse_metadata(pairs: list[str]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"metadata must be key=value, got {pair!r}")
        key, value = pair.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError("metadata keys cannot be empty")
        lowered = key.lower().replace("-", "_")
        if any(part in lowered for part in SENSITIVE_KEY_PARTS):
            raise ValueError(f"metadata key {key!r} looks sensitive; use --token/--token-stdin")
        metadata[key] = value
    return metadata


def connect_provider(
    provider_id: str,
    repo: str | Path = ".",
    *,
    token: str = "",
    account_label: str = "",
    metadata_pairs: list[str] | None = None,
    secret_backend: str | None = None,
) -> dict[str, Any]:
    """Connect a provider by writing repo metadata and local secrets."""

    provider = normalize_provider(provider_id)
    target = Path(repo).resolve()
    config = _read_config(target)
    repo_id = _ensure_repo_id(config)
    metadata = _parse_metadata(metadata_pairs or [])
    store = SecretStore(secret_backend)

    secrets: dict[str, dict[str, str]] = {}
    required = list(provider.required_secrets)
    if required:
        primary = required[0]
        if token:
            ref = _secret_ref(repo_id, provider.id, primary)
            store.set(ref, token)
            secrets[primary] = {"ref": ref, "backend": store.backend}
        else:
            secrets[primary] = {
                "ref": _secret_ref(repo_id, provider.id, primary),
                "backend": store.backend,
            }

    providers = config["providers"]
    providers[provider.id] = {
        "provider": provider.id,
        "connected": True,
        "account_label": account_label.strip(),
        "connected_at": _now(),
        "last_checked_at": _now(),
        "auth": provider.auth,
        "secrets": secrets,
        "metadata": metadata,
    }
    path = _write_config(target, config)
    status = status_provider(provider.id, target)
    return {
        "ok": bool(status["ok"]),
        "provider": provider.id,
        "config_path": str(path),
        "credential_backend": store.backend,
        "credential_boundary": store.boundary(),
        "status": status,
    }


def status_provider(provider_id: str, repo: str | Path = ".") -> dict[str, Any]:
    provider = normalize_provider(provider_id)
    target = Path(repo).resolve()
    config = _read_config(target)
    entry = config["providers"].get(provider.id)
    if not isinstance(entry, dict):
        return {
            "provider": provider.id,
            "name": provider.name,
            "connected": False,
            "ok": False,
            "state": "not_connected",
            "account_label": "",
            "metadata": {},
            "secrets": {},
            "last_checked_at": "",
        }

    secrets: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    stored_secrets = entry.get("secrets") if isinstance(entry.get("secrets"), dict) else {}
    for field in provider.required_secrets:
        raw = stored_secrets.get(field) if isinstance(stored_secrets, dict) else None
        raw = raw if isinstance(raw, dict) else {}
        ref = str(raw.get("ref") or "")
        backend = str(raw.get("backend") or "local-file")
        present = bool(ref and SecretStore(backend).get(ref))
        if not present:
            missing.append(field)
        secrets[field] = {"present": present, "ref": ref, "backend": backend}

    metadata = entry.get("metadata") if isinstance(entry.get("metadata"), dict) else {}
    ok = not missing
    state = "connected" if ok else "missing_secret"
    return {
        "provider": provider.id,
        "name": provider.name,
        "connected": bool(entry.get("connected", False)),
        "ok": ok,
        "state": state,
        "account_label": str(entry.get("account_label") or ""),
        "metadata": metadata,
        "secrets": secrets,
        "last_checked_at": str(entry.get("last_checked_at") or ""),
    }


def status_all(repo: str | Path = ".", *, include_all: bool = False) -> dict[str, Any]:
    target = Path(repo).resolve()
    config = _read_config(target)
    configured = set(config["providers"].keys())
    providers = []
    for provider in PROVIDERS:
        if include_all or provider.id in configured:
            providers.append(status_provider(provider.id, target))
    connected = [item for item in providers if item["connected"]]
    broken = [item for item in connected if not item["ok"]]
    return {
        "ok": not broken,
        "repo": str(target),
        "config_path": str(_config_path(target)),
        "repo_id": str(config.get("repo_id") or ""),
        "providers": providers,
        "summary": {
            "configured": len(connected),
            "healthy": len([item for item in connected if item["ok"]]),
            "needs_repair": len(broken),
        },
    }


def list_providers(repo: str | Path = ".") -> dict[str, Any]:
    status = status_all(repo, include_all=True)
    by_id = {item["provider"]: item for item in status["providers"]}
    providers = []
    for provider in provider_registry():
        state = by_id[provider["id"]]["state"]
        providers.append({**provider, "state": state})
    return {"ok": True, "providers": providers, "config_path": status["config_path"]}


def doctor_check(repo: str | Path = ".") -> dict[str, Any]:
    status = status_all(repo)
    summary = status["summary"]
    if summary["configured"] == 0:
        return {
            "name": "integration-credentials",
            "ok": True,
            "detail": "no providers connected",
            "severity": "info",
        }
    if summary["needs_repair"]:
        return {
            "name": "integration-credentials",
            "ok": False,
            "detail": (
                f"{summary['needs_repair']} of {summary['configured']} connected provider(s) "
                "need credential repair; run `mb connect status`."
            ),
            "severity": "warn",
        }
    return {
        "name": "integration-credentials",
        "ok": True,
        "detail": f"{summary['healthy']} connected provider(s) ready",
        "severity": "ok",
    }


def render_list(result: dict[str, Any]) -> None:
    for provider in result["providers"]:
        print(
            f"{provider['id']:<14} {provider['state']:<14} "
            f"{provider['auth']:<22} {provider['description']}"
        )


def render_status(result: dict[str, Any]) -> None:
    summary = result["summary"]
    print(f"mb connect status  {result['repo']}")
    print(
        f"configured: {summary['configured']}  "
        f"healthy: {summary['healthy']}  needs repair: {summary['needs_repair']}"
    )
    if not result["providers"]:
        print("no providers connected")
        return
    for item in result["providers"]:
        state = "ok" if item["ok"] else "warn"
        label = f" ({item['account_label']})" if item["account_label"] else ""
        print(f"  {state}  {item['provider']}{label}: {item['state']}")


def render_connect_result(result: dict[str, Any]) -> None:
    status = result["status"]
    if result["ok"]:
        print(f"connected {result['provider']}")
    else:
        print(f"connected {result['provider']} metadata; credential still needs repair")
    print(f"metadata: {result['config_path']}")
    print(f"secrets: {result['credential_boundary']}")
    source = result.get("credential_source") or {}
    if source.get("type") == "env" and source.get("env_var"):
        print(f"credential source: env {source['env_var']}")
    if status["state"] != "connected":
        print("next: rerun with --token-stdin or --token to store the required credential")


def read_stdin_token() -> str:
    return sys.stdin.read().strip()
