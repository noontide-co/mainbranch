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
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

CONFIG_RELATIVE_PATH = Path(".mb") / "connect.yaml"
SERVICE_NAME = "mainbranch"
SENSITIVE_KEY_PARTS = ("token", "secret", "password", "credential", "api_key", "apikey", "key")
SAFE_METADATA_KEYS = {"token_type", "token_scope", "api_token_type"}
VALIDATION_TIMEOUT_SECONDS = 8
CommandRunner = Callable[[list[str], Path | None, float], dict[str, Any]]
Which = Callable[[str], str | None]


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
        auth="meta_cli_pending",
        required_secrets=(),
        metadata_fields=("ad_account_id", "business_id"),
        description=(
            "Meta Ads account access through Meta's official Ads CLI, pending "
            "Main Branch detection and smoke."
        ),
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

PROVIDER_GUIDANCE: dict[str, dict[str, Any]] = {
    "github": {
        "priority": 1,
        "why": (
            "GitHub is the task, proposal, review, and shipped-work layer for the business repo."
        ),
        "use_when": (
            "Use for daily task tracking, public issue drafts, pull requests, reviews, "
            "and team visibility."
        ),
        "defer_when": (
            "You can start solo local setup without it, but issue, proposal, and team "
            "loops will be limited."
        ),
        "status_command": "mb connect doctor --json",
    },
    "cloudflare": {
        "priority": 2,
        "why": (
            "Cloudflare is the default low-lock-in rail for sites, DNS, Pages, and future Workers."
        ),
        "use_when": (
            "Use when the business needs a landing page, custom domain, deploy, or DNS check."
        ),
        "defer_when": "Defer until you are ready to publish or connect a domain.",
        "status_command": "mb connect doctor --json",
    },
    "google": {
        "priority": 3,
        "why": (
            "Google/Workspace is the bridge for existing Docs, Sheets, Drive, and workspace assets."
        ),
        "use_when": (
            "Use when the business has source material in Google Drive or needs "
            "spreadsheet/docs context."
        ),
        "defer_when": (
            "Do not connect it just because a Google account exists; connect it when "
            "a workflow needs it."
        ),
        "status_command": "mb connect doctor --json",
    },
    "meta": {
        "priority": 4,
        "why": (
            "Meta Ads readiness will let ad workflows reason about ad accounts, campaigns, "
            "and pixels through Meta's official Ads CLI path."
        ),
        "use_when": (
            "Use when the business is generating, reviewing, or learning from Meta/Facebook ads. "
            "For now, treat live account access as planned until Main Branch detection "
            "and read-only smoke are wired."
        ),
        "defer_when": (
            "Defer for organic, research, or site work that does not need ad-account facts."
        ),
        "status_command": "mb connect doctor --json",
    },
    "apify": {
        "priority": 5,
        "why": (
            "Apify is the optional research sidecar for scraping, YouTube, Instagram, "
            "and web mining."
        ),
        "use_when": (
            "Use when research or organic workflows need structured external data collection."
        ),
        "defer_when": "Defer for first-pass reference setup or local-only thinking.",
        "status_command": "mb connect doctor --json",
    },
}


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
    return {"version": 1, "repo_id": "", "repo_identity": {}, "providers": {}}


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
    try:
        version = int(raw.get("version") or 1)
    except (TypeError, ValueError):
        version = 1
    return {
        "version": version,
        "repo_id": str(raw.get("repo_id") or ""),
        "repo_identity": raw.get("repo_identity")
        if isinstance(raw.get("repo_identity"), dict)
        else {},
        "providers": providers,
    }


def _git_output(repo: Path, args: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return ""
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def _normalized_remote(value: str) -> str:
    remote = value.strip()
    if remote.startswith("git@") and ":" in remote:
        host, path = remote.removeprefix("git@").split(":", 1)
        return f"https://{host}/{path}".removesuffix(".git")
    parsed = urllib.parse.urlparse(remote)
    if parsed.scheme and parsed.netloc:
        host = parsed.hostname or parsed.netloc
        path = parsed.path.lstrip("/")
        if path:
            return f"https://{host}/{path}".removesuffix(".git")
    return remote.removesuffix(".git")


def _repo_identity(repo: Path) -> dict[str, str]:
    remote = _git_output(repo, ["config", "--get", "remote.origin.url"])
    if remote:
        source = "git_remote"
        basis = _normalized_remote(remote)
    else:
        common_dir = _git_output(repo, ["rev-parse", "--git-common-dir"])
        if common_dir:
            source = "git_common_dir"
            basis = str(
                (repo / common_dir).resolve()
                if not Path(common_dir).is_absolute()
                else Path(common_dir).resolve()
            )
        else:
            source = "path"
            basis = str(repo.resolve())
    digest = hashlib.sha256(f"mainbranch-connect-v2:{source}:{basis}".encode()).hexdigest()
    return {"source": source, "repo_id": digest[:32], "basis_sha256": digest}


def _ensure_repo_id(config: dict[str, Any], repo: Path) -> str:
    identity = _repo_identity(repo)
    existing = str(config.get("repo_id") or "").strip()
    repo_id = existing or identity["repo_id"]
    config["repo_id"] = repo_id
    config["repo_identity"] = {
        "source": identity["source"],
        "basis_sha256": identity["basis_sha256"],
        "repo_id_source": "existing_config" if existing else identity["source"],
    }
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


def _repair(
    provider: Provider,
    state: str,
    missing: list[str] | None = None,
    validation: dict[str, Any] | None = None,
) -> dict[str, str]:
    validation = validation or {}
    validation_repair = str(validation.get("repair") or "")
    validation_repair_command = str(validation.get("repair_command") or "")
    validation_summary = str(validation.get("summary") or "")
    if validation_repair or validation_repair_command:
        return {
            "summary": validation_summary or f"{provider.name} needs metadata repair.",
            "repair": validation_repair,
            "repair_command": validation_repair_command,
        }
    if provider.id == "meta":
        return {
            "summary": ("Meta Ads CLI support is planned but not wired in this mb release."),
            "repair": (
                "Use reference-file ad workflows for now. Do not add third-party "
                "Meta MCP or access-token setup as a fallback; wait for the "
                "official Meta Ads CLI detection/read-only smoke to land."
            ),
            "repair_command": "",
        }
    missing_fields = ", ".join(missing or provider.required_secrets)
    connect_command = f"mb connect {provider.id} --token-stdin"
    if state == "not_connected":
        if provider.required_secrets:
            return {
                "summary": f"{provider.name} is not connected.",
                "repair": f"Run `{connect_command}` to store the credential outside the repo.",
                "repair_command": connect_command,
            }
        return {
            "summary": f"{provider.name} metadata is not connected.",
            "repair": f"Run `mb connect {provider.id}` with the needed metadata.",
            "repair_command": f"mb connect {provider.id}",
        }
    if state == "missing_secret":
        return {
            "summary": f"{provider.name} metadata exists, but local secret material is missing.",
            "repair": (
                f"Run `{connect_command}` to replace the missing credential ({missing_fields})."
            ),
            "repair_command": connect_command,
        }
    if state == "unvalidated":
        return {
            "summary": f"{provider.name} has stored credentials, but they have not been validated.",
            "repair": f"Run `mb connect test {provider.id}`.",
            "repair_command": f"mb connect test {provider.id}",
        }
    if state == "invalid":
        return {
            "summary": f"{provider.name} validation failed without exposing the provider response.",
            "repair": (
                f"Run `{connect_command}` to replace the credential, then "
                f"`mb connect test {provider.id}`."
            ),
            "repair_command": connect_command,
        }
    return {
        "summary": f"{provider.name} is ready.",
        "repair": "",
        "repair_command": "",
    }


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
        if lowered not in SAFE_METADATA_KEYS and any(
            part in lowered for part in SENSITIVE_KEY_PARTS
        ):
            raise ValueError(f"metadata key {key!r} looks sensitive; use --token/--token-stdin")
        metadata[key] = value
    return metadata


def _cloudflare_token_type(metadata: dict[str, Any]) -> str:
    raw = (
        metadata.get("token_type")
        or metadata.get("token_scope")
        or metadata.get("api_token_type")
        or metadata.get("api_scope")
        or ""
    )
    value = str(raw).strip().lower().replace("_", "-")
    if value in {"account", "account-scoped", "account-owned", "account-token"}:
        return "account"
    return "user"


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
    if provider.id == "meta":
        raise ValueError(
            "Meta Ads CLI support is planned but not wired in this mb release; "
            "run `mb connect plan` or `mb educational provider-readiness`."
        )
    target = Path(repo).resolve()
    config = _read_config(target)
    repo_id = _ensure_repo_id(config, target)
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
        "ok": status["state"] != "missing_secret",
        "ready": bool(status["ok"]),
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
    if provider.id == "meta":
        raw_entry = entry if isinstance(entry, dict) else {}
        raw_meta_metadata = raw_entry.get("metadata")
        meta_metadata: dict[str, Any] = (
            raw_meta_metadata if isinstance(raw_meta_metadata, dict) else {}
        )
        raw_meta_validation = raw_entry.get("validation")
        meta_validation: dict[str, Any] = (
            raw_meta_validation if isinstance(raw_meta_validation, dict) else {}
        )
        repair = _repair(provider, "planned", validation=meta_validation)
        return {
            "provider": provider.id,
            "name": provider.name,
            "connected": False,
            "ok": False,
            "state": "planned",
            "summary": repair["summary"],
            "repair": repair["repair"],
            "repair_command": repair["repair_command"],
            "safe_to_share": True,
            "account_label": str(raw_entry.get("account_label") or ""),
            "metadata": meta_metadata,
            "secrets": {},
            "last_checked_at": str(raw_entry.get("last_checked_at") or ""),
            "validation": {
                "state": str(meta_validation.get("state") or "planned"),
                "checked_at": str(meta_validation.get("checked_at") or ""),
                "summary": str(meta_validation.get("summary") or repair["summary"]),
                "safe_to_share": True,
            },
        }
    if not isinstance(entry, dict):
        repair = _repair(provider, "not_connected")
        return {
            "provider": provider.id,
            "name": provider.name,
            "connected": False,
            "ok": False,
            "state": "not_connected",
            "summary": repair["summary"],
            "repair": repair["repair"],
            "repair_command": repair["repair_command"],
            "safe_to_share": True,
            "account_label": "",
            "metadata": {},
            "secrets": {},
            "last_checked_at": "",
            "validation": {"state": "not_connected", "checked_at": "", "summary": ""},
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

    raw_metadata = entry.get("metadata")
    metadata: dict[str, Any] = raw_metadata if isinstance(raw_metadata, dict) else {}
    raw_validation = entry.get("validation")
    validation: dict[str, Any] = raw_validation if isinstance(raw_validation, dict) else {}
    if missing:
        state = "missing_secret"
        ok = False
    elif not provider.required_secrets:
        state = "ready"
        ok = True
    else:
        validation_state = str(validation.get("state") or "unvalidated")
        if validation_state == "ready":
            state = "ready"
            ok = True
        elif validation_state == "invalid":
            state = "invalid"
            ok = False
        else:
            state = "unvalidated"
            ok = False
    repair = _repair(provider, state, missing, validation)
    return {
        "provider": provider.id,
        "name": provider.name,
        "connected": bool(entry.get("connected", False)),
        "ok": ok,
        "state": state,
        "summary": repair["summary"],
        "repair": repair["repair"],
        "repair_command": repair["repair_command"],
        "safe_to_share": True,
        "account_label": str(entry.get("account_label") or ""),
        "metadata": metadata,
        "secrets": secrets,
        "last_checked_at": str(entry.get("last_checked_at") or ""),
        "validation": {
            "state": str(validation.get("state") or state),
            "checked_at": str(validation.get("checked_at") or ""),
            "summary": str(validation.get("summary") or ""),
            "upstream": validation.get("upstream")
            if isinstance(validation.get("upstream"), dict)
            else {},
            "repair": str(validation.get("repair") or ""),
            "repair_command": str(validation.get("repair_command") or ""),
            "safe_to_share": True,
        },
    }


def _stored_secret(provider: Provider, entry: dict[str, Any]) -> str:
    stored_secrets = entry.get("secrets") if isinstance(entry.get("secrets"), dict) else {}
    if not provider.required_secrets:
        return ""
    primary = provider.required_secrets[0]
    raw = stored_secrets.get(primary) if isinstance(stored_secrets, dict) else None
    raw = raw if isinstance(raw, dict) else {}
    ref = str(raw.get("ref") or "")
    backend = str(raw.get("backend") or "local-file")
    return SecretStore(backend).get(ref) if ref else ""


def _provider_error_summary(provider_name: str, upstream: dict[str, Any]) -> str:
    status = upstream.get("http_status")
    messages = [str(item) for item in upstream.get("error_messages", []) if str(item)]
    base = messages[0] if messages else ""
    if status in {400, 401}:
        return f"{provider_name} rejected the credential. Create a fresh token and reconnect it."
    if status == 403:
        return (
            f"{provider_name} accepted the request shape but denied access. "
            "Check token permissions, account binding, and account_id metadata."
        )
    if status == 404:
        return (
            f"{provider_name} could not find the requested account/token resource. "
            "Check account_id metadata and token ownership."
        )
    if status == 429:
        return f"{provider_name} rate-limited validation. Retry `mb connect test` later."
    if isinstance(status, int) and status >= 500:
        return (
            f"{provider_name} validation returned HTTP {status}. Retry after the provider recovers."
        )
    if base:
        return f"{provider_name} validation failed: {base}"
    return f"{provider_name} validation could not complete."


def _extract_upstream_errors(payload: Any) -> tuple[list[str], list[str]]:
    if not isinstance(payload, dict):
        return [], []
    codes: list[str] = []
    messages: list[str] = []
    for field in ("errors", "messages"):
        raw_items = payload.get(field)
        if not isinstance(raw_items, list):
            continue
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            code = item.get("code")
            message = item.get("message")
            if code not in {None, ""}:
                codes.append(str(code))
            if message:
                messages.append(str(message))
    return codes, messages


def _http_get_json(
    url: str,
    headers: dict[str, str] | None = None,
    *,
    provider_name: str = "provider",
    endpoint_family: str = "unknown",
) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers or {})
    upstream: dict[str, Any] = {
        "endpoint_family": endpoint_family,
        "http_status": None,
        "response_received": False,
        "error_codes": [],
        "error_messages": [],
        "safe_to_share": True,
    }
    try:
        with urllib.request.urlopen(request, timeout=VALIDATION_TIMEOUT_SECONDS) as response:
            status = int(getattr(response, "status", 0) or 0)
            body = response.read(8192)
    except urllib.error.HTTPError as exc:
        body = b""
        with suppress(OSError):
            body = exc.read(8192)
        payload: Any = {}
        if body:
            with suppress(json.JSONDecodeError, UnicodeDecodeError):
                payload = json.loads(body.decode("utf-8"))
        codes, messages = _extract_upstream_errors(payload)
        upstream.update(
            {
                "http_status": int(exc.code),
                "response_received": True,
                "error_codes": codes,
                "error_messages": messages,
            }
        )
        state = "invalid" if exc.code in {400, 401, 403, 404} else "unvalidated"
        return {
            "ok": False,
            "state": state,
            "summary": _provider_error_summary(provider_name, upstream),
            "upstream": upstream,
            "safe_to_share": True,
        }
    except (urllib.error.URLError, TimeoutError, OSError):
        return {
            "ok": False,
            "state": "unvalidated",
            "summary": f"{provider_name} validation could not reach the service.",
            "upstream": upstream,
            "safe_to_share": True,
        }
    payload = {}
    if body:
        with suppress(json.JSONDecodeError, UnicodeDecodeError):
            payload = json.loads(body.decode("utf-8"))
    codes, messages = _extract_upstream_errors(payload)
    upstream.update(
        {
            "http_status": status,
            "response_received": True,
            "error_codes": codes,
            "error_messages": messages,
        }
    )
    if status < 200 or status >= 300:
        state = "invalid" if status in {400, 401, 403, 404} else "unvalidated"
        return {
            "ok": False,
            "state": state,
            "summary": _provider_error_summary(provider_name, upstream),
            "upstream": upstream,
            "safe_to_share": True,
        }
    if isinstance(payload, dict) and payload.get("success") is False:
        return {
            "ok": False,
            "state": "invalid",
            "summary": _provider_error_summary(provider_name, upstream),
            "upstream": upstream,
            "safe_to_share": True,
        }
    token_status = ""
    if isinstance(payload, dict) and isinstance(payload.get("result"), dict):
        token_status = str(payload["result"].get("status") or "")
    if token_status and token_status != "active":
        upstream["token_status"] = token_status
        return {
            "ok": False,
            "state": "invalid",
            "summary": f"{provider_name} token is {token_status}; reconnect an active token.",
            "upstream": upstream,
            "safe_to_share": True,
        }
    return {
        "ok": True,
        "state": "ready",
        "summary": f"{provider_name} credential validated with provider.",
        "upstream": upstream,
        "safe_to_share": True,
    }


def _validate_with_provider(
    provider: Provider, secret: str, metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    checked_at = _now()
    metadata = metadata or {}
    if provider.id == "cloudflare":
        token_type = _cloudflare_token_type(metadata)
        if token_type == "account":
            account_id = str(metadata.get("account_id") or "").strip()
            if not account_id:
                return {
                    "ok": False,
                    "state": "unvalidated",
                    "checked_at": checked_at,
                    "summary": (
                        "Cloudflare account-token validation requires non-secret "
                        "`account_id` metadata."
                    ),
                    "repair": (
                        "Run `mb connect cloudflare --metadata token_type=account "
                        "--metadata account_id=<account-id>`, then "
                        "`mb connect test cloudflare`."
                    ),
                    "repair_command": (
                        "mb connect cloudflare --metadata token_type=account "
                        "--metadata account_id=<account-id>"
                    ),
                    "safe_to_share": True,
                    "upstream": {
                        "endpoint_family": "cloudflare_account_token_verify",
                        "http_status": None,
                        "response_received": False,
                        "error_codes": [],
                        "error_messages": [],
                        "safe_to_share": True,
                    },
                }
            url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/tokens/verify"
            endpoint_family = "cloudflare_account_token_verify"
        else:
            url = "https://api.cloudflare.com/client/v4/user/tokens/verify"
            endpoint_family = "cloudflare_user_token_verify"
        result = _http_get_json(
            url,
            {"Authorization": f"Bearer {secret}"},
            provider_name=provider.name,
            endpoint_family=endpoint_family,
        )
        raw_upstream = result.get("upstream")
        upstream: dict[str, Any] = raw_upstream if isinstance(raw_upstream, dict) else {}
        if token_type == "account" and upstream.get("http_status") == 404:
            fallback = _http_get_json(
                f"https://api.cloudflare.com/client/v4/accounts/{account_id}",
                {"Authorization": f"Bearer {secret}"},
                provider_name=provider.name,
                endpoint_family="cloudflare_account_read",
            )
            raw_fallback_upstream = fallback.get("upstream")
            fallback_upstream: dict[str, Any] = (
                raw_fallback_upstream if isinstance(raw_fallback_upstream, dict) else {}
            )
            fallback_upstream["fallback_from"] = endpoint_family
            fallback["upstream"] = fallback_upstream
            if fallback.get("ok"):
                fallback["summary"] = (
                    "Cloudflare account-scoped credential validated with account read fallback."
                )
            result = fallback
    elif provider.id == "apify":
        result = _http_get_json(
            "https://api.apify.com/v2/users/me",
            {"Authorization": f"Bearer {secret}"},
            provider_name=provider.name,
            endpoint_family="apify_user_me",
        )
    else:
        return {
            "ok": True,
            "state": "ready",
            "checked_at": checked_at,
            "summary": (
                f"{provider.name} has no automated safe validation probe yet; "
                "local credential presence was confirmed."
            ),
            "safe_to_share": True,
        }
    return {
        "ok": bool(result["ok"]),
        "state": str(result["state"]),
        "checked_at": checked_at,
        "summary": str(result["summary"]),
        "repair": str(result.get("repair") or ""),
        "repair_command": str(result.get("repair_command") or ""),
        "safe_to_share": True,
        "upstream": result.get("upstream", {}),
    }


def test_provider(provider_id: str, repo: str | Path = ".") -> dict[str, Any]:
    provider = normalize_provider(provider_id)
    target = Path(repo).resolve()
    config = _read_config(target)
    entry = config["providers"].get(provider.id)
    status = status_provider(provider.id, target)
    if provider.id == "meta":
        return {"ok": False, "provider": provider.id, "status": status, "safe_to_share": True}
    if not isinstance(entry, dict) or status["state"] in {"not_connected", "missing_secret"}:
        return {"ok": False, "provider": provider.id, "status": status, "safe_to_share": True}

    if not provider.required_secrets:
        validation = {
            "ok": True,
            "state": "ready",
            "checked_at": _now(),
            "summary": f"{provider.name} uses repo-local metadata and has no secret to validate.",
            "safe_to_share": True,
        }
    else:
        secret = _stored_secret(provider, entry)
        if not secret:
            return {
                "ok": False,
                "provider": provider.id,
                "status": status_provider(provider.id, target),
                "safe_to_share": True,
            }
        raw_metadata = entry.get("metadata")
        metadata = raw_metadata if isinstance(raw_metadata, dict) else {}
        validation = _validate_with_provider(provider, secret, metadata)

    entry["validation"] = {
        "state": validation["state"],
        "checked_at": validation["checked_at"],
        "summary": validation["summary"],
        "safe_to_share": True,
    }
    if validation.get("repair") or validation.get("repair_command"):
        entry["validation"]["repair"] = validation.get("repair", "")
        entry["validation"]["repair_command"] = validation.get("repair_command", "")
    if isinstance(validation.get("upstream"), dict):
        entry["validation"]["upstream"] = validation["upstream"]
    entry["last_checked_at"] = validation["checked_at"]
    config["providers"][provider.id] = entry
    _write_config(target, config)
    status = status_provider(provider.id, target)
    return {
        "ok": bool(validation["ok"]),
        "provider": provider.id,
        "validation": entry["validation"],
        "status": status,
        "safe_to_share": True,
    }


def status_all(
    repo: str | Path = ".",
    *,
    include_all: bool = False,
    github: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target = Path(repo).resolve()
    config = _read_config(target)
    identity = _repo_identity(target)
    configured = set(config["providers"].keys())
    providers = []
    for provider in PROVIDERS:
        if include_all or provider.id in configured:
            providers.append(status_provider(provider.id, target))
    connected = [item for item in providers if item["connected"]]
    broken = [item for item in connected if not item["ok"]]
    unvalidated = [item for item in connected if item["state"] == "unvalidated"]
    return {
        "ok": not broken,
        "repo": str(target),
        "config_path": str(_config_path(target)),
        "repo_id": str(config.get("repo_id") or identity["repo_id"]),
        "providers": providers,
        "github": github or github_context(target),
        "safe_to_share": True,
        "summary": {
            "configured": len(connected),
            "healthy": len([item for item in connected if item["ok"]]),
            "needs_repair": len(broken),
            "unvalidated": len(unvalidated),
        },
    }


def _run_command(args: list[str], cwd: Path | None = None, timeout: float = 5.0) -> dict[str, Any]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"ok": False, "returncode": 127, "stdout": "", "stderr": f"{args[0]} not found"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "returncode": 124, "stdout": "", "stderr": "command timed out"}
    except subprocess.SubprocessError:
        return {"ok": False, "returncode": 1, "stdout": "", "stderr": "command failed"}
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def github_context(
    repo: str | Path = ".",
    *,
    which_func: Which | None = None,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    target = Path(repo).resolve()
    which = which_func or shutil.which
    run = command_runner or _run_command
    if not which("gh"):
        return {
            "ok": False,
            "state": "missing_cli",
            "summary": "GitHub CLI is not installed.",
            "repair": "Install GitHub CLI, then run `gh auth login`.",
            "repair_command": "gh auth login",
            "safe_to_share": True,
        }

    auth = run(["gh", "auth", "status"], target, 5.0)
    if not auth["ok"]:
        return {
            "ok": False,
            "state": "unauthenticated",
            "summary": "GitHub CLI is installed but not authenticated.",
            "repair": "Run `gh auth login`.",
            "repair_command": "gh auth login",
            "safe_to_share": True,
        }

    git = run(["git", "rev-parse", "--is-inside-work-tree"], target, 3.0)
    if not git["ok"] or git["stdout"].strip() != "true":
        return {
            "ok": False,
            "state": "not_git_repo",
            "summary": "This folder is not a git repo.",
            "repair": "Run `git init` if this should be a business repo.",
            "repair_command": "git init",
            "safe_to_share": True,
        }

    remote = run(["git", "config", "--get", "remote.origin.url"], target, 3.0)
    remote_value = remote["stdout"].strip() if remote["ok"] else ""
    if "github.com" not in remote_value:
        return {
            "ok": False,
            "state": "missing_github_remote",
            "summary": "This repo does not have a GitHub origin remote.",
            "repair": "Add a GitHub origin remote before relying on GitHub tasks or proposals.",
            "repair_command": "gh repo create --source . --remote origin --push",
            "safe_to_share": True,
        }

    return {
        "ok": True,
        "state": "ready",
        "summary": "GitHub CLI auth and repo remote are ready.",
        "repair": "",
        "repair_command": "",
        "safe_to_share": True,
    }


def list_providers(repo: str | Path = ".") -> dict[str, Any]:
    status = status_all(repo, include_all=True)
    by_id = {item["provider"]: item for item in status["providers"]}
    providers = []
    for provider in provider_registry():
        state = by_id[provider["id"]]["state"]
        guidance = PROVIDER_GUIDANCE.get(provider["id"], {})
        providers.append({**provider, **guidance, "state": state})
    return {"ok": True, "providers": providers, "config_path": status["config_path"]}


def provider_plan(repo: str | Path = ".") -> dict[str, Any]:
    """Return noob-safe provider setup choices backed by readiness facts."""

    status = status_all(repo, include_all=True)
    by_id = {item["provider"]: item for item in status["providers"]}
    github = status["github"]
    steps: list[dict[str, Any]] = [
        {
            "id": "github",
            "name": "GitHub",
            "category": "work",
            "priority": PROVIDER_GUIDANCE["github"]["priority"],
            "ready": bool(github["ok"]),
            "state": github["state"],
            "summary": github["summary"],
            "why": PROVIDER_GUIDANCE["github"]["why"],
            "use_when": PROVIDER_GUIDANCE["github"]["use_when"],
            "defer_when": PROVIDER_GUIDANCE["github"]["defer_when"],
            "status_command": PROVIDER_GUIDANCE["github"]["status_command"],
            "next_command": github["repair_command"] or "gh auth status",
            "safe_to_share": bool(github.get("safe_to_share", True)),
        }
    ]
    provider_ids = sorted(
        (provider_id for provider_id in PROVIDER_GUIDANCE if provider_id != "github"),
        key=lambda provider_id: int(PROVIDER_GUIDANCE[provider_id]["priority"]),
    )
    for provider_id in provider_ids:
        item = by_id.get(provider_id)
        if item is None:
            continue
        guidance = PROVIDER_GUIDANCE[provider_id]
        steps.append(
            {
                "id": provider_id,
                "name": item["name"],
                "category": normalize_provider(provider_id).category,
                "priority": guidance["priority"],
                "ready": bool(item["ok"]),
                "state": item["state"],
                "summary": item["summary"],
                "why": guidance["why"],
                "use_when": guidance["use_when"],
                "defer_when": guidance["defer_when"],
                "status_command": guidance["status_command"],
                "next_command": (
                    item["repair_command"]
                    or (
                        "mb educational provider-readiness"
                        if item["state"] == "planned"
                        else f"mb connect test {provider_id}"
                    )
                ),
                "safe_to_share": bool(item.get("safe_to_share", True)),
            }
        )
    ready = len([step for step in steps if step["ready"]])
    return {
        "ok": True,
        "readiness_ok": status["ok"],
        "repo": status["repo"],
        "steps": sorted(steps, key=lambda step: int(step["priority"])),
        "summary": {
            "total": len(steps),
            "ready": ready,
            "needs_setup": len(steps) - ready,
        },
        "safe_to_share": True,
    }


def doctor_check(repo: str | Path = ".", *, status: dict[str, Any] | None = None) -> dict[str, Any]:
    status = status or status_all(repo)
    summary = status["summary"]
    if summary["configured"] == 0:
        return {
            "name": "integration-credentials",
            "ok": True,
            "detail": "no providers connected",
            "severity": "info",
            "repair": "",
            "repair_command": "",
            "safe_to_share": True,
        }
    if summary["needs_repair"]:
        repairs = [item for item in status["providers"] if not item["ok"]]
        first = repairs[0] if repairs else {}
        names = ", ".join(item["provider"] for item in repairs[:3])
        return {
            "name": "integration-credentials",
            "ok": False,
            "detail": (
                f"{summary['needs_repair']} of {summary['configured']} connected provider(s) "
                f"need repair ({names}); run `mb connect doctor`."
            ),
            "severity": "warn",
            "repair": str(first.get("repair") or "Run `mb connect doctor`."),
            "repair_command": str(first.get("repair_command") or "mb connect doctor"),
            "safe_to_share": True,
        }
    return {
        "name": "integration-credentials",
        "ok": True,
        "detail": f"{summary['healthy']} connected provider(s) ready",
        "severity": "ok",
        "repair": "",
        "repair_command": "",
        "safe_to_share": True,
    }


def doctor(repo: str | Path = ".") -> dict[str, Any]:
    github = github_context(repo)
    status = status_all(repo, github=github)
    github = status["github"]
    checks = [
        {
            "name": "github-context",
            "ok": bool(github["ok"]),
            "state": github["state"],
            "summary": github["summary"],
            "repair": github["repair"],
            "repair_command": github["repair_command"],
            "safe_to_share": True,
        },
        *[
            {
                "name": f"provider:{item['provider']}",
                "provider": item["provider"],
                "ok": bool(item["ok"]),
                "state": item["state"],
                "summary": item["summary"],
                "repair": item["repair"],
                "repair_command": item["repair_command"],
                "safe_to_share": True,
            }
            for item in status["providers"]
        ],
    ]
    return {
        "ok": all(check["ok"] for check in checks),
        "repo": status["repo"],
        "checks": checks,
        "integrations": status,
        "safe_to_share": True,
    }


def render_list(result: dict[str, Any]) -> None:
    for provider in result["providers"]:
        print(
            f"{provider['id']:<14} {provider['state']:<14} "
            f"{provider['auth']:<22} {provider['description']}"
        )


def render_plan(result: dict[str, Any]) -> None:
    print(f"mb connect plan  {result['repo']}")
    print("Choose the provider that matches the business job in front of you:")
    for index, step in enumerate(result["steps"], start=1):
        state = "ready" if step["ready"] else step["state"]
        print(f"{index}. {step['name']} ({state})")
        print(f"   why: {step['why']}")
        print(f"   use when: {step['use_when']}")
        if not step["ready"]:
            print(f"   next: {step['next_command']}")


def render_status(result: dict[str, Any]) -> None:
    summary = result["summary"]
    print(f"mb connect status  {result['repo']}")
    print(
        f"configured: {summary['configured']}  "
        f"healthy: {summary['healthy']}  needs repair: {summary['needs_repair']}"
    )
    github = result.get("github") or {}
    if github:
        state = "ok" if github.get("ok") else "warn"
        print(f"  {state}  github: {github.get('state')}")
        if github.get("repair_command"):
            print(f"       next: {github['repair_command']}")
    if not result["providers"]:
        print("no providers connected")
        return
    for item in result["providers"]:
        state = "ok" if item["ok"] else "warn"
        label = f" ({item['account_label']})" if item["account_label"] else ""
        print(f"  {state}  {item['provider']}{label}: {item['state']}")
        if item["repair_command"]:
            print(f"       next: {item['repair_command']}")


def render_doctor(result: dict[str, Any]) -> None:
    print(f"mb connect doctor  {result['repo']}")
    for check in result["checks"]:
        state = "ok" if check["ok"] else "warn"
        print(f"  {state}  {check['name']}: {check['state']}")
        if check["repair_command"]:
            print(f"       next: {check['repair_command']}")


def render_test_result(result: dict[str, Any]) -> None:
    status = result["status"]
    state = "ok" if result["ok"] else "warn"
    print(f"mb connect test {result['provider']}: {state} ({status['state']})")
    validation = result.get("validation") or status.get("validation") or {}
    summary = validation.get("summary")
    if summary:
        print(f"summary: {summary}")
    upstream = validation.get("upstream") if isinstance(validation, dict) else {}
    if isinstance(upstream, dict) and upstream.get("endpoint_family"):
        details = [f"endpoint: {upstream['endpoint_family']}"]
        if upstream.get("http_status") is not None:
            details.append(f"http: {upstream['http_status']}")
        codes = upstream.get("error_codes")
        if isinstance(codes, list) and codes:
            details.append(f"codes: {', '.join(str(code) for code in codes[:3])}")
        print("provider: " + "  ".join(details))
    if status.get("repair_command"):
        print(f"next: {status['repair_command']}")


def render_connect_result(result: dict[str, Any]) -> None:
    status = result["status"]
    if status["state"] == "ready":
        print(f"connected {result['provider']} and ready")
    elif status["state"] == "unvalidated":
        print(f"stored {result['provider']} credential; validation still needed")
    elif not result["ok"]:
        print(f"connected {result['provider']} metadata; credential still needs repair")
    else:
        print(f"connected {result['provider']} metadata")
    print(f"metadata: {result['config_path']}")
    print(f"secrets: {result['credential_boundary']}")
    source = result.get("credential_source") or {}
    if source.get("type") == "env" and source.get("env_var"):
        print(f"credential source: env {source['env_var']}")
    if status["repair_command"]:
        print(f"next: {status['repair_command']}")


def read_stdin_token() -> str:
    if sys.stdin.isatty():
        print(
            "Paste the credential, then press Ctrl-D on a new line to finish.",
            file=sys.stderr,
        )
    return sys.stdin.read().strip()
