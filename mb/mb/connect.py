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
CommandRunner = Callable[..., dict[str, Any]]
Which = Callable[[str], str | None]


class ConfigBoundaryError(ValueError):
    """Raised when local connect metadata is outside the selected repo boundary."""


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
        auth="meta_ads_cli_read_only",
        required_secrets=("access_token",),
        metadata_fields=("ad_account_id", "business_id"),
        description=(
            "Meta Ads account access through Meta's official Ads CLI, with local "
            "credential storage and read-only account smoke before skills use live facts."
        ),
        env_vars=("ACCESS_TOKEN", "META_ACCESS_TOKEN"),
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
        id="hledger",
        name="hledger",
        category="finance",
        auth="local_file",
        required_secrets=(),
        metadata_fields=("journal_path", "vault_path"),
        description=(
            "Local hledger journal metadata for the private books vault. "
            "`core/finance/books.md` is the source of truth for storage mode; "
            "real ledgers stay outside the tracked business repo."
        ),
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
            "Meta Ads readiness lets ad workflows use account, campaign, insights, "
            "creative, and pixel context through Meta's official Ads CLI."
        ),
        "use_when": (
            "Use when the business is generating, reviewing, or learning from Meta/Facebook ads. "
            "Main Branch stores the token outside the repo and only treats live account "
            "access as ready after read-only CLI smoke passes."
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

META_SETUP_REQUIREMENTS = (
    "Meta Business Portfolio / Business Manager access",
    "An ad account assigned to the user or system user",
    "The Business portfolio ID from Meta business info when available",
    "A Meta developer app selected during token generation",
    "A system user token or individual user token with assigned assets",
    "Possible second-admin approval in stricter Business Manager setups",
)

META_TOKEN_SCOPES = (
    "business_management",
    "ads_management",
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_ads",
    "catalog_management",
    "read_insights",
)

META_READ_SMOKE_COMMANDS: tuple[tuple[str, list[str], bool], ...] = (
    ("adaccount_list", ["meta", "-o", "json", "ads", "adaccount", "list"], False),
    ("campaign_list", ["meta", "-o", "json", "ads", "campaign", "list"], False),
    (
        "insights_get",
        [
            "meta",
            "-o",
            "json",
            "ads",
            "insights",
            "get",
            "--fields",
            "spend,impressions,clicks,ctr,cpc",
        ],
        False,
    ),
    ("dataset_list", ["meta", "-o", "json", "ads", "dataset", "list"], True),
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


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _checked_config_path(repo: Path) -> Path:
    root = repo.resolve()
    path = _config_path(root)
    config_dir = path.parent

    if config_dir.is_symlink() or path.is_symlink():
        raise ConfigBoundaryError(
            "Refusing to use .mb/connect.yaml because the local state path is a symlink."
        )
    if config_dir.exists() and not config_dir.is_dir():
        raise ConfigBoundaryError(
            "Refusing to use .mb/connect.yaml because the local state directory is invalid."
        )

    parent_resolved = config_dir.resolve(strict=False)
    path_resolved = path.resolve(strict=False)
    if not _is_within(parent_resolved, root) or not _is_within(path_resolved, root):
        raise ConfigBoundaryError(
            "Refusing to use .mb/connect.yaml because it is outside the selected repo boundary."
        )
    return path


def _empty_config() -> dict[str, Any]:
    return {"version": 1, "repo_id": "", "repo_identity": {}, "providers": {}}


def _read_config(repo: Path) -> dict[str, Any]:
    path = _checked_config_path(repo)
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
    path = _checked_config_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Re-check after creating .mb so a swapped local-state path cannot escape the repo.
    path = _checked_config_path(repo)
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
        return _meta_repair(state, missing)
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


def _meta_repair(state: str, missing: list[str] | None = None) -> dict[str, str]:
    connect_command = "mb connect meta --token-stdin --metadata ad_account_id=<act_id>"
    install_command = "pipx install --python <python3.12-or-newer> meta-ads"
    if state == "wrong_python":
        return {
            "summary": "Meta Ads CLI requires Python 3.12 or newer.",
            "repair": (
                "Install Python 3.12+, then install Meta's official Ads CLI with "
                f"`{install_command}`."
            ),
            "repair_command": install_command,
        }
    if state == "missing_cli":
        return {
            "summary": "Meta Ads CLI is not installed or `meta --version` failed.",
            "repair": (
                "Install Meta's official Ads CLI with Python 3.12+, then rerun "
                "`mb connect test meta`."
            ),
            "repair_command": install_command,
        }
    if state == "not_connected":
        return {
            "summary": "Meta Ads is not connected.",
            "repair": (
                "Prepare the Meta Business Portfolio, ad account, app, assigned assets, "
                f"and token, then run `{connect_command}`."
            ),
            "repair_command": connect_command,
        }
    if state == "missing_secret":
        missing_fields = ", ".join(missing or ("access_token",))
        return {
            "summary": "Meta Ads metadata exists, but local token material is missing.",
            "repair": (
                f"Run `{connect_command}` to replace the missing credential ({missing_fields})."
            ),
            "repair_command": connect_command,
        }
    if state == "missing_metadata":
        return {
            "summary": "Meta Ads needs non-secret `ad_account_id` metadata before validation.",
            "repair": (
                "Run `mb connect meta --metadata ad_account_id=<act_id>`, then "
                "`mb connect test meta`."
            ),
            "repair_command": "mb connect meta --metadata ad_account_id=<act_id>",
        }
    if state == "unvalidated":
        return {
            "summary": "Meta Ads has local setup metadata, but read-only smoke has not passed.",
            "repair": "Run `mb connect test meta`.",
            "repair_command": "mb connect test meta",
        }
    if state == "waiting_for_admin_approval":
        return {
            "summary": "Meta needs another business admin to approve this connection.",
            "repair": (
                "Meta needs another business admin to approve this connection. "
                "Nothing is broken locally."
            ),
            "repair_command": "",
        }
    if state == "auth_failed":
        return {
            "summary": "Meta Ads auth did not pass.",
            "repair": (
                "Check token scopes, app, system user, assigned assets, and ad account "
                "metadata, then rerun `mb connect test meta`."
            ),
            "repair_command": "mb connect test meta",
        }
    if state == "read_smoke_failed":
        return {
            "summary": "Meta Ads auth passed, but read-only account smoke failed.",
            "repair": (
                "Check ad account access and token scopes, then rerun `mb connect test meta`."
            ),
            "repair_command": "mb connect test meta",
        }
    return {
        "summary": "Meta Ads read-only account context is ready.",
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


def _cloudflare_token_type(metadata: dict[str, Any], secret: str = "") -> str:
    if secret.strip().startswith("cfat_"):
        return "account"
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


def _python_version_ok(value: str) -> bool:
    parts = value.strip().split(".")
    if len(parts) < 2:
        return False
    try:
        major = int(parts[0])
        minor = int(parts[1])
    except ValueError:
        return False
    return (major, minor) >= (3, 12)


def _meta_python_ready(
    *,
    which_func: Which | None = None,
    command_runner: CommandRunner | None = None,
) -> bool:
    if sys.version_info >= (3, 12):
        return True
    which = which_func or shutil.which
    run = command_runner or _run_command
    python312 = which("python3.12")
    if not python312:
        return False
    result = run(
        [
            python312,
            "-c",
            "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
        ],
        None,
        3.0,
    )
    return bool(result.get("ok")) and _python_version_ok(str(result.get("stdout") or ""))


def _meta_prerequisite_state(
    *,
    which_func: Which | None = None,
    command_runner: CommandRunner | None = None,
) -> str:
    which = which_func or shutil.which
    run = command_runner or _run_command
    if which("meta"):
        version = run(["meta", "--version"], None, 5.0)
        if version.get("ok"):
            return ""
        return "missing_cli"
    if not _meta_python_ready(which_func=which, command_runner=run):
        return "wrong_python"
    return "missing_cli"


def _meta_setup() -> dict[str, Any]:
    return {
        "requirements": list(META_SETUP_REQUIREMENTS),
        "token_scopes": list(META_TOKEN_SCOPES),
        "credential_paths": ["--token-stdin", "--from-env", "hidden prompt"],
        "safe_metadata": [
            "ad_account_id (use the act_ ad account ID)",
            "business_id (Meta calls this Business portfolio ID)",
            "account label",
        ],
        "test_command": "mb connect test meta --json",
        "safe_to_share": True,
    }


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
        "setup": _meta_setup() if provider.id == "meta" else {},
        "status": status,
    }


def status_provider(
    provider_id: str,
    repo: str | Path = ".",
    *,
    which_func: Which | None = None,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    provider = normalize_provider(provider_id)
    target = Path(repo).resolve()
    config = _read_config(target)
    entry = config["providers"].get(provider.id)
    if provider.id == "meta":
        prereq_state = _meta_prerequisite_state(
            which_func=which_func,
            command_runner=command_runner,
        )
        raw_entry = entry if isinstance(entry, dict) else {}
        raw_meta_metadata = raw_entry.get("metadata")
        meta_metadata: dict[str, Any] = (
            raw_meta_metadata if isinstance(raw_meta_metadata, dict) else {}
        )
        raw_meta_validation = raw_entry.get("validation")
        meta_validation: dict[str, Any] = (
            raw_meta_validation if isinstance(raw_meta_validation, dict) else {}
        )
        stored_secrets = (
            raw_entry.get("secrets") if isinstance(raw_entry.get("secrets"), dict) else {}
        )
        raw_secret = stored_secrets.get("access_token") if isinstance(stored_secrets, dict) else {}
        raw_secret = raw_secret if isinstance(raw_secret, dict) else {}
        ref = str(raw_secret.get("ref") or "")
        backend = str(raw_secret.get("backend") or "local-file")
        secret_present = bool(ref and SecretStore(backend).get(ref))
        validation_state = str(meta_validation.get("state") or "unvalidated")
        if prereq_state:
            state = prereq_state
            ok = False
        elif not isinstance(entry, dict):
            state = "not_connected"
            ok = False
        elif not secret_present:
            state = "missing_secret"
            ok = False
        elif not str(meta_metadata.get("ad_account_id") or "").strip():
            state = "missing_metadata"
            ok = False
        elif validation_state == "ready":
            state = "ready"
            ok = True
        elif validation_state in {
            "waiting_for_admin_approval",
            "auth_failed",
            "read_smoke_failed",
            "missing_cli",
            "wrong_python",
            "missing_metadata",
        }:
            state = validation_state
            ok = False
        else:
            state = "unvalidated"
            ok = False
        repair = _repair(
            provider, state, ["access_token"] if not secret_present else [], meta_validation
        )
        return {
            "provider": provider.id,
            "name": provider.name,
            "connected": bool(isinstance(entry, dict) and raw_entry.get("connected", False)),
            "ok": ok,
            "state": state,
            "summary": repair["summary"],
            "repair": repair["repair"],
            "repair_command": repair["repair_command"],
            "safe_to_share": True,
            "account_label": str(raw_entry.get("account_label") or ""),
            "metadata": meta_metadata,
            "secrets": {
                "access_token": {"present": secret_present, "ref": ref, "backend": backend}
            },
            "last_checked_at": str(raw_entry.get("last_checked_at") or ""),
            "setup": _meta_setup(),
            "validation": {
                "state": str(meta_validation.get("state") or state),
                "checked_at": str(meta_validation.get("checked_at") or ""),
                "summary": str(meta_validation.get("summary") or ""),
                "upstream": meta_validation.get("upstream")
                if isinstance(meta_validation.get("upstream"), dict)
                else {},
                "repair": str(meta_validation.get("repair") or ""),
                "repair_command": str(meta_validation.get("repair_command") or ""),
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


def _meta_env(secret: str, metadata: dict[str, Any]) -> dict[str, str]:
    keep = ("PATH", "HOME", "LANG", "LC_ALL", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")
    env = {key: os.environ[key] for key in keep if key in os.environ}
    env["ACCESS_TOKEN"] = secret
    env["AD_ACCOUNT_ID"] = str(metadata.get("ad_account_id") or "").strip()
    business_id = str(metadata.get("business_id") or "").strip()
    if business_id:
        env["BUSINESS_ID"] = business_id
    return env


def _safe_command_check(name: str, args: list[str], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "command": " ".join(args),
        "ok": bool(result.get("ok")),
        "returncode": int(result.get("returncode") or 0),
        "stdout_present": bool(str(result.get("stdout") or "")),
        "stderr_present": bool(str(result.get("stderr") or "")),
        "safe_to_share": True,
    }


def _run_meta_command(
    run: CommandRunner,
    args: list[str],
    repo: Path,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        return run(args, repo, VALIDATION_TIMEOUT_SECONDS, env=env)
    except TypeError:
        return run(args, repo, VALIDATION_TIMEOUT_SECONDS)


def _looks_like_admin_approval(result: dict[str, Any]) -> bool:
    text = f"{result.get('stdout') or ''}\n{result.get('stderr') or ''}".lower()
    admin_words = ("admin", "business admin", "administrator")
    approval_words = ("approval", "approve", "pending", "waiting")
    return any(word in text for word in admin_words) and any(
        word in text for word in approval_words
    )


def _meta_validation_result(
    *,
    ok: bool,
    state: str,
    checked_at: str,
    summary: str,
    checks: list[dict[str, Any]],
    repair: str = "",
    repair_command: str = "",
) -> dict[str, Any]:
    return {
        "ok": ok,
        "state": state,
        "checked_at": checked_at,
        "summary": summary,
        "repair": repair,
        "repair_command": repair_command,
        "safe_to_share": True,
        "upstream": {
            "endpoint_family": "meta_ads_cli",
            "checks": checks,
            "safe_to_share": True,
        },
    }


def _validate_meta_with_cli(
    provider: Provider,
    secret: str,
    metadata: dict[str, Any],
    repo: Path,
    *,
    which_func: Which | None = None,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    checked_at = _now()
    checks: list[dict[str, Any]] = []
    prereq_state = _meta_prerequisite_state(
        which_func=which_func,
        command_runner=command_runner,
    )
    if prereq_state:
        repair = _meta_repair(prereq_state)
        checks.append(
            {
                "name": "local_prerequisites",
                "ok": False,
                "state": prereq_state,
                "safe_to_share": True,
            }
        )
        return _meta_validation_result(
            ok=False,
            state=prereq_state,
            checked_at=checked_at,
            summary=repair["summary"],
            checks=checks,
            repair=repair["repair"],
            repair_command=repair["repair_command"],
        )
    if not secret:
        repair = _meta_repair("missing_secret", ["access_token"])
        return _meta_validation_result(
            ok=False,
            state="missing_secret",
            checked_at=checked_at,
            summary=repair["summary"],
            checks=checks,
            repair=repair["repair"],
            repair_command=repair["repair_command"],
        )
    ad_account_id = str(metadata.get("ad_account_id") or "").strip()
    if not ad_account_id:
        repair = _meta_repair("missing_metadata")
        return _meta_validation_result(
            ok=False,
            state="missing_metadata",
            checked_at=checked_at,
            summary=repair["summary"],
            checks=checks,
            repair=repair["repair"],
            repair_command=repair["repair_command"],
        )

    run = command_runner or _run_command
    env = _meta_env(secret, metadata)
    auth_args = ["meta", "auth", "status"]
    auth = _run_meta_command(run, auth_args, repo, env)
    checks.append(_safe_command_check("auth_status", auth_args, auth))
    if not auth.get("ok"):
        state = "waiting_for_admin_approval" if _looks_like_admin_approval(auth) else "auth_failed"
        repair = _meta_repair(state)
        return _meta_validation_result(
            ok=False,
            state=state,
            checked_at=checked_at,
            summary=repair["summary"],
            checks=checks,
            repair=repair["repair"],
            repair_command=repair["repair_command"],
        )

    for name, args, needs_business_id in META_READ_SMOKE_COMMANDS:
        if needs_business_id and not str(metadata.get("business_id") or "").strip():
            checks.append(
                {
                    "name": name,
                    "command": " ".join(args),
                    "ok": True,
                    "skipped": True,
                    "reason": "business_id metadata not set",
                    "safe_to_share": True,
                }
            )
            continue
        result = _run_meta_command(run, args, repo, env)
        checks.append(_safe_command_check(name, args, result))
        if not result.get("ok"):
            state = (
                "waiting_for_admin_approval"
                if _looks_like_admin_approval(result)
                else "read_smoke_failed"
            )
            repair = _meta_repair(state)
            return _meta_validation_result(
                ok=False,
                state=state,
                checked_at=checked_at,
                summary=repair["summary"],
                checks=checks,
                repair=repair["repair"],
                repair_command=repair["repair_command"],
            )

    return _meta_validation_result(
        ok=True,
        state="ready",
        checked_at=checked_at,
        summary=f"{provider.name} read-only account smoke passed.",
        checks=checks,
    )


def _validate_with_provider(
    provider: Provider,
    secret: str,
    metadata: dict[str, Any] | None = None,
    *,
    repo: Path | None = None,
    which_func: Which | None = None,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    checked_at = _now()
    metadata = metadata or {}
    if provider.id == "cloudflare":
        token_type = _cloudflare_token_type(metadata, secret)
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
    elif provider.id == "meta":
        return _validate_meta_with_cli(
            provider,
            secret,
            metadata,
            repo or Path.cwd(),
            which_func=which_func,
            command_runner=command_runner,
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


def test_provider(
    provider_id: str,
    repo: str | Path = ".",
    *,
    which_func: Which | None = None,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    provider = normalize_provider(provider_id)
    target = Path(repo).resolve()
    config = _read_config(target)
    entry = config["providers"].get(provider.id)
    status = status_provider(
        provider.id,
        target,
        which_func=which_func,
        command_runner=command_runner,
    )
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
                "status": status_provider(
                    provider.id,
                    target,
                    which_func=which_func,
                    command_runner=command_runner,
                ),
                "safe_to_share": True,
            }
        raw_metadata = entry.get("metadata")
        metadata = raw_metadata if isinstance(raw_metadata, dict) else {}
        validation = _validate_with_provider(
            provider,
            secret,
            metadata,
            repo=target,
            which_func=which_func,
            command_runner=command_runner,
        )

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
    status = status_provider(
        provider.id,
        target,
        which_func=which_func,
        command_runner=command_runner,
    )
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
        "config_path": str(_checked_config_path(target)),
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


def _run_command(
    args: list[str],
    cwd: Path | None = None,
    timeout: float = 5.0,
    *,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
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
                        if item["state"] in {"planned", "readiness"}
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
    setup = result.get("setup") if result["provider"] == "meta" else {}
    if isinstance(setup, dict) and setup.get("requirements"):
        print("Meta Ads setup requirements:")
        for item in setup["requirements"]:
            print(f"  - {item}")
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
