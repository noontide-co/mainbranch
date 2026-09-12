"""Integration registry and credential metadata for ``mb connect``."""

from __future__ import annotations

import hashlib
import json
import os
import re
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

from mb.credential_store import (
    CredentialStoreError,
    SecretProbe,
    SecretStore,
    backend_repair,
    new_credential_deadline,
    select_secret_backend,
)
from mb.durable import atomic_write_text

CONFIG_RELATIVE_PATH = Path(".mb") / "connect.yaml"
USER_SCOPE_RELATIVE_PATH = Path("connect") / "user-scope.yaml"
SENSITIVE_KEY_PARTS = ("token", "secret", "password", "credential", "api_key", "apikey", "key")
SAFE_METADATA_KEYS = {"token_type", "token_scope", "api_token_type"}
CONNECT_SCOPES = {"repo", "user"}
VALIDATION_TIMEOUT_SECONDS = 8
SECRET_REPLACEMENT = "<redacted>"
CommandRunner = Callable[..., dict[str, Any]]
Which = Callable[[str], str | None]

SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b"
    r"(api[_ -]?key|access[_ -]?token|refresh[_ -]?token|token|secret|password|"
    r"credential|authorization)"
    r"([ \t]*[:=][ \t]*)(bearer[ \t]+)?([^\s,;]+)"
)
SECRET_PHRASE_RE = re.compile(
    r"(?i)\b"
    r"((?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|authorization)[ \t]+)"
    r"(bearer[ \t]+)?([A-Za-z0-9._~+/=-]{12,})"
)
BEARER_SECRET_RE = re.compile(r"(?i)\bbearer[ \t]+[^\s,;]+")

BACKEND_FAILURE_STATE = "backend_unavailable"
# A credential is stored and readable, but no provider call has ever confirmed
# it works. Distinct from `unvalidated` ("`mb connect test` has not been run"):
# running the test again cannot clear this state when the provider has no probe.
UNVERIFIED_STATE = "stored_unverified"


# Providers with a real read-only probe in `_validate_with_provider`. Kept as
# one named set because the exit-code contract turns on it: a provider with a
# probe can be verified by running `mb connect test`, and one without cannot be
# verified by anything the operator runs.
# `test_probe_provider_set_matches_validate_with_provider` guards the drift.
PROBE_PROVIDERS: frozenset[str] = frozenset({"cloudflare", "apify", "meta"})


def has_provider_probe(provider_id: str) -> bool:
    """Can Main Branch confirm this provider's credential by calling it?"""
    return provider_id in PROBE_PROVIDERS


def provider_needs_action(item: dict[str, Any]) -> bool:
    """Is there something the operator can actually do about this provider?

    Process exit codes answer this question rather than "is everything
    verified". A red that nobody can clear gets ignored, and a probe-less
    provider can never turn green until a probe exists upstream, so it warns
    without failing. Everything else that is not `ok` is actionable: run the
    test, replace the credential, or fix the backend.
    """
    if item.get("ok"):
        return False
    if item.get("state") == UNVERIFIED_STATE:
        return has_provider_probe(str(item.get("provider") or ""))
    return True


def _provider_verified(validation: dict[str, Any]) -> bool:
    """Read the "a provider call confirmed this credential" fact, failing closed.

    Releases through 0.5.2 recorded ``state: ready`` for providers that were
    never probed, so an absent ``provider_verified`` key is not evidence of a
    successful provider call. Absent reads as unverified until `mb connect test`
    records the fact, which costs one re-test and never overclaims readiness.
    """
    return validation.get("provider_verified") is True


def _verified_at(validation: dict[str, Any]) -> str:
    """Timestamp of the last *successful* provider call, or "" if never.

    Preserved across a later failure: it records when the credential last
    worked, which stays true even when the current check fails.
    """
    return str(validation.get("verified_at") or "")


def _backend_repair(reason: str) -> dict[str, str]:
    """Sanitized summary/repair for a credential-backend reason code."""

    return backend_repair(reason)


KeychainError = CredentialStoreError
_select_secret_backend = select_secret_backend


class ConfigBoundaryError(ValueError):
    """Raised when local connect metadata is outside the selected repo boundary."""


class ConfigCorruptError(ValueError):
    """Raised when local connect metadata cannot be parsed safely."""


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
    # Expected prefixes for the primary secret. Empty = no shape check.
    # Used to refuse malformed credentials at intake without ever echoing
    # the value itself.
    key_prefixes: tuple[str, ...] = ()


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
        metadata_fields=("ad_account_id", "business_id", "page_id", "pixel_id"),
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
        id="stripe",
        name="Stripe",
        category="payments",
        auth="api_key",
        required_secrets=("api_key",),
        metadata_fields=("account_id", "mode"),
        description=(
            "Stripe payments: checkout, products, customers, and webhook "
            "configuration. Store the secret or restricted key locally; keys "
            "never enter chat or committed repo files. Record `mode` metadata "
            "(test or live) so agents can verify the key matches the intent."
        ),
        env_vars=("STRIPE_SECRET_KEY", "STRIPE_API_KEY"),
        key_prefixes=("sk_", "rk_"),
    ),
    Provider(
        id="resend",
        name="Resend",
        category="email",
        auth="api_key",
        required_secrets=("api_key",),
        metadata_fields=("sender_domain", "audience_id"),
        description=(
            "Resend transactional and lifecycle email: sending, domains, and "
            "audiences. The sender domain lives in metadata so agents read "
            "identity from recorded facts instead of live provider state."
        ),
        env_vars=("RESEND_API_KEY",),
        key_prefixes=("re_",),
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


CUSTOM_PROVIDER_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,30}$")
CUSTOM_IDENTITY_METADATA_ORDER = (
    "role",
    "access_level",
    "data_domain",
    "auth_state",
    "environment",
    "source_system",
    "account_ref",
    "workspace",
    "tenant_id",
)


def _custom_provider(provider_id: str) -> Provider:
    """Synthesize a registry entry for an operator-named provider.

    Custom providers ride every existing rail (SecretStore, user scope,
    `mb connect token`, status) with a single `api_key` secret slot.
    """
    return Provider(
        id=provider_id,
        name=provider_id,
        category="custom",
        auth="api_key",
        required_secrets=("api_key",),
        metadata_fields=(),
        description="Operator-defined custom provider.",
    )


def normalize_provider(provider_id: str, *, allow_custom: bool = False) -> Provider:
    key = provider_id.strip().lower().replace("_", "-")
    aliases = {"whisper": "transcription", "cloudflare-pages": "cloudflare"}
    key = aliases.get(key, key)
    providers = provider_map()
    if key in providers:
        return providers[key]
    if allow_custom:
        if not CUSTOM_PROVIDER_RE.fullmatch(key):
            raise ValueError(
                f"custom provider id {provider_id!r} must be 2-31 chars of "
                "lowercase letters, digits, and hyphens"
            )
        return _custom_provider(key)
    supported = ", ".join(sorted(providers))
    raise ValueError(
        f"unknown provider {provider_id!r}; supported providers: {supported}. "
        "For an operator-defined provider, rerun with --custom."
    )


def _is_custom_provider_id(provider_id: str) -> bool:
    key = provider_id.strip().lower().replace("_", "-")
    return key not in provider_map() and bool(CUSTOM_PROVIDER_RE.fullmatch(key))


def _connect_command(provider: Provider, *, token_stdin: bool = False) -> str:
    custom_flag = " --custom" if provider.category == "custom" else ""
    token_flag = " --token-stdin" if token_stdin else ""
    return f"mb connect {provider.id}{custom_flag}{token_flag}"


def _safe_identity_metadata(metadata: dict[str, Any]) -> dict[str, str]:
    """Return custom-provider metadata safe enough for identity diagnostics.

    The output is still operator-facing (`safe_to_share: false`), but this
    avoids echoing hand-edited secret-like metadata keys if a repo config is
    malformed.
    """

    recorded: dict[str, str] = {}
    for key in CUSTOM_IDENTITY_METADATA_ORDER:
        value = metadata.get(key)
        if value is not None and value != "":
            recorded[key] = str(value)
    for raw_key, value in metadata.items():
        key = str(raw_key)
        lowered = key.lower().replace("-", "_")
        if key in recorded or value is None or value == "":
            continue
        if lowered not in SAFE_METADATA_KEYS and any(
            part in lowered for part in SENSITIVE_KEY_PARTS
        ):
            continue
        recorded[key] = str(value)
    return recorded


def _metadata_key_looks_sensitive(key: str) -> bool:
    lowered = key.lower().replace("-", "_")
    return lowered not in SAFE_METADATA_KEYS and any(
        part in lowered for part in SENSITIVE_KEY_PARTS
    )


def _safe_status_metadata(metadata: dict[str, Any]) -> dict[str, str]:
    """Filter hand-edited metadata before it enters safe-to-share status JSON."""
    recorded: dict[str, str] = {}
    for raw_key, raw_value in metadata.items():
        key = str(raw_key)
        if raw_value is None or raw_value == "":
            continue
        value = str(raw_value)
        flagged, _reason = _classify_credential_value(key, value)
        if flagged or _metadata_key_looks_sensitive(key):
            continue
        recorded[key] = value
    return recorded


def _safe_status_label(value: Any) -> str:
    label = str(value or "")
    flagged, _reason = _classify_credential_value("account_label", label)
    return SECRET_REPLACEMENT if flagged else label


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
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigCorruptError(
            "Refusing to update .mb/connect.yaml because it is unreadable or invalid YAML. "
            "Fix or move the file, then rerun the command."
        ) from exc
    if not isinstance(raw, dict):
        raise ConfigCorruptError(
            "Refusing to update .mb/connect.yaml because it does not contain a YAML object. "
            "Fix or move the file, then rerun the command."
        )
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


def _github_repo_full_name(remote: str) -> str:
    normalized = _normalized_remote(remote)
    parsed = urllib.parse.urlparse(normalized)
    if parsed.hostname != "github.com":
        return ""
    path = parsed.path.strip("/")
    if path.count("/") < 1:
        return ""
    owner, repo_name, *_ = path.split("/")
    return f"{owner}/{repo_name.removesuffix('.git')}" if owner and repo_name else ""


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
    atomic_write_text(path, text)
    return path


def _user_scope_path() -> Path:
    return _home() / USER_SCOPE_RELATIVE_PATH


def _empty_user_scope() -> dict[str, Any]:
    return {"version": 1, "repos": {}}


def _read_user_scope() -> dict[str, Any]:
    path = _user_scope_path()
    if not path.exists():
        return _empty_user_scope()
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigCorruptError(
            "Refusing to update connect user-scope metadata because it is unreadable or "
            "invalid YAML. Fix or move the file, then rerun the command."
        ) from exc
    if not isinstance(raw, dict):
        raise ConfigCorruptError(
            "Refusing to update connect user-scope metadata because it does not contain a YAML "
            "object. Fix or move the file, then rerun the command."
        )
    repos = raw.get("repos")
    if not isinstance(repos, dict):
        repos = {}
    try:
        version = int(raw.get("version") or 1)
    except (TypeError, ValueError):
        version = 1
    return {"version": version, "repos": repos}


def _write_user_scope(data: dict[str, Any]) -> Path:
    path = _user_scope_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with suppress(OSError):
        path.parent.chmod(0o700)
    atomic_write_text(path, yaml.safe_dump(data, sort_keys=False))
    with suppress(OSError):
        path.chmod(0o600)
    return path


def _user_scope_provider_entry(repo_id: str, provider_id: str) -> dict[str, Any] | None:
    data = _read_user_scope()
    raw_repo = data["repos"].get(repo_id)
    repo_entry = raw_repo if isinstance(raw_repo, dict) else {}
    providers = repo_entry.get("providers") if isinstance(repo_entry.get("providers"), dict) else {}
    raw_entry = providers.get(provider_id) if isinstance(providers, dict) else None
    return raw_entry if isinstance(raw_entry, dict) else None


def _write_user_scope_provider(
    repo_id: str,
    *,
    repo_identity: dict[str, Any],
    provider_id: str,
    entry: dict[str, Any],
) -> Path:
    data = _read_user_scope()
    raw_repos = data.get("repos")
    repos: dict[str, Any] = raw_repos if isinstance(raw_repos, dict) else {}
    data["repos"] = repos
    raw_repo = repos.get(repo_id)
    repo_entry = raw_repo if isinstance(raw_repo, dict) else {}
    raw_providers = repo_entry.get("providers")
    providers: dict[str, Any] = raw_providers if isinstance(raw_providers, dict) else {}
    repo_entry["repo_identity"] = repo_identity
    repo_entry["updated_at"] = _now()
    repo_entry["providers"] = providers
    providers[provider_id] = entry
    repos[repo_id] = repo_entry
    return _write_user_scope(data)


def _secret_ref(repo_id: str, provider_id: str, field: str) -> str:
    digest = hashlib.sha256(f"{repo_id}:{provider_id}:{field}".encode()).hexdigest()[:24]
    return f"mainbranch://{digest}/{provider_id}/{field}"


def _unverified_repair(provider: Provider) -> dict[str, str]:
    """Guidance for a stored credential no provider call has confirmed.

    Split on whether a probe exists, so guidance matches the exit code: a
    provider that exits 1 always names something to run, and a provider that
    exits 0 never sends the operator after a fix that cannot work.
    """
    if has_provider_probe(provider.id):
        # Reachable through metadata that recorded readiness without recording
        # a provider call. Running the probe is a real next step.
        return {
            "summary": (
                f"{provider.name} has a stored credential whose readiness was recorded "
                "without a provider call."
            ),
            "repair": f"Run `mb connect test {provider.id}` to confirm it with the provider.",
            "repair_command": f"mb connect test {provider.id}",
        }
    # No probe exists, so rerunning `mb connect test` would record the same
    # unverified result. Pointing at it would be busywork dressed as a fix.
    return {
        "summary": (
            f"{provider.name} has a stored credential, but Main Branch has no "
            "automated way to confirm it works with the provider."
        ),
        "repair": (
            f"Confirm the {provider.name} credential in the provider's own dashboard, "
            "or treat the first real workflow run as the check."
        ),
        "repair_command": "",
    }


def _repair(
    provider: Provider,
    state: str,
    missing: list[str] | None = None,
    validation: dict[str, Any] | None = None,
    backend_reason: str = "",
) -> dict[str, str]:
    if state == BACKEND_FAILURE_STATE:
        # Wins over every provider-level repair: reconnecting a provider
        # cannot succeed while the credential backend itself is unhealthy.
        detail = _backend_repair(backend_reason)
        return {
            "summary": (
                f"{provider.name} credentials cannot be read. {detail['summary']} "
                "The stored metadata is intact."
            ),
            "repair": detail["repair"],
            "repair_command": detail["repair_command"],
        }
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
    if state == UNVERIFIED_STATE:
        # Ahead of the Meta special-case: `_meta_repair` has no answer for this
        # state, and `_unverified_repair` is already probe-aware, so Meta gets
        # "run `mb connect test meta`" rather than a generic fallback.
        return _unverified_repair(provider)
    if provider.id == "meta":
        return _meta_repair(state, missing)
    missing_fields = ", ".join(missing or provider.required_secrets)
    connect_command = _connect_command(provider, token_stdin=True)
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


def _validate_key_shape(provider: Provider, token: str, metadata: dict[str, str]) -> None:
    """Refuse malformed credentials at intake.

    Error messages must never echo the credential value — only its expected
    shape and, for Stripe, whether it is a test or live key.
    """
    if not token or not provider.key_prefixes:
        return
    if not token.startswith(provider.key_prefixes):
        shapes = ", ".join(f"{prefix}…" for prefix in provider.key_prefixes)
        slot = provider.required_secrets[0] if provider.required_secrets else "credential"
        raise ValueError(
            f"the {provider.name} {slot} does not match the expected key shape "
            f"({shapes}). Nothing was stored; check the value and reconnect."
        )
    if provider.id == "stripe":
        mode = str(metadata.get("mode") or "").strip().lower()
        if mode == "live" and token.startswith(("sk_test_", "rk_test_")):
            raise ValueError(
                "metadata says mode=live but the key is a Stripe TEST key. "
                "Nothing was stored; fix the mode or the key and reconnect."
            )
        if mode == "test" and token.startswith(("sk_live_", "rk_live_")):
            raise ValueError(
                "metadata says mode=test but the key is a Stripe LIVE key. "
                "Nothing was stored; fix the mode or the key and reconnect."
            )


def connect_provider(
    provider_id: str,
    repo: str | Path = ".",
    *,
    token: str = "",
    account_label: str = "",
    metadata_pairs: list[str] | None = None,
    secret_backend: str | None = None,
    scope: str = "repo",
    custom: bool = False,
) -> dict[str, Any]:
    """Connect a provider by writing repo metadata and local secrets."""

    if custom:
        provider = normalize_provider(provider_id, allow_custom=True)
    else:
        # Reconnecting an existing custom provider works without the flag.
        provider = resolve_provider(provider_id, repo)
    normalized_scope = scope.strip().lower().replace("_", "-") or "repo"
    if normalized_scope not in CONNECT_SCOPES:
        raise ValueError("scope must be repo or user")
    target = Path(repo).resolve()
    metadata = _parse_metadata(metadata_pairs or [])
    _validate_key_shape(provider, token, metadata)
    config = _read_config(target)
    repo_id = _ensure_repo_id(config, target)
    credential_deadline = new_credential_deadline()
    providers = config["providers"]
    raw_existing_entry = providers.get(provider.id)
    if not token and provider.id not in providers:
        raw_existing_entry = _user_scope_provider_entry(repo_id, provider.id)
    existing_entry = raw_existing_entry if isinstance(raw_existing_entry, dict) else {}

    secrets: dict[str, dict[str, str]] = {}
    required = list(provider.required_secrets)
    if required:
        primary = required[0]
        if token:
            store = SecretStore(secret_backend)
            ref = _secret_ref(repo_id, provider.id, primary)
            try:
                store.set(ref, token, deadline=credential_deadline)
            except KeychainError as exc:
                # Fail before any metadata is written, so a backend outage
                # cannot leave `connected: true` next to an unstored secret.
                detail = _backend_repair(exc.reason)
                raise KeychainError(
                    exc.reason,
                    f"{detail['summary']} Nothing was stored and the repo metadata is "
                    f"unchanged. {detail['repair']}",
                ) from exc
            secrets[primary] = {"ref": ref, "backend": store.backend}
        else:
            raw_existing_secrets = existing_entry.get("secrets")
            existing_secrets = (
                raw_existing_secrets if isinstance(raw_existing_secrets, dict) else {}
            )
            raw_primary = existing_secrets.get(primary)
            existing_primary = raw_primary if isinstance(raw_primary, dict) else {}
            existing_ref = str(existing_primary.get("ref") or "")
            if existing_ref:
                existing_backend = str(existing_primary.get("backend") or "local-file")
                # Tokenless reconnects may update safe metadata or scope, but
                # they cannot migrate a secret. Validate and retain the exact
                # recorded store/ref instead of orphaning the existing value.
                store = SecretStore(existing_backend)
                secrets = {
                    str(field): {
                        str(key): str(value)
                        for key, value in raw_secret.items()
                        if key in {"ref", "backend"}
                    }
                    for field, raw_secret in existing_secrets.items()
                    if isinstance(raw_secret, dict)
                }
            else:
                store = SecretStore(secret_backend)
                secrets[primary] = {
                    "ref": _secret_ref(repo_id, provider.id, primary),
                    "backend": store.backend,
                }
    else:
        store = SecretStore(secret_backend)

    providers[provider.id] = {
        "provider": provider.id,
        "connected": True,
        "scope": normalized_scope,
        "account_label": account_label.strip(),
        "connected_at": _now(),
        "last_checked_at": _now(),
        "auth": provider.auth,
        "secrets": secrets,
        "metadata": metadata,
    }
    user_scope_path = ""
    if normalized_scope == "user":
        user_scope_path = str(
            _write_user_scope_provider(
                repo_id,
                repo_identity=config.get("repo_identity") or {},
                provider_id=provider.id,
                entry=providers[provider.id],
            )
        )
    path = _write_config(target, config)
    status = status_provider(
        provider.id,
        target,
        _credential_deadline=credential_deadline,
    )
    return {
        "ok": status["state"] not in {"missing_secret", BACKEND_FAILURE_STATE},
        "ready": bool(status["ok"]),
        "provider": provider.id,
        "scope": normalized_scope,
        "config_path": str(path),
        "user_scope_path": user_scope_path,
        "hydrated": normalized_scope == "user",
        "credential_backend": store.backend,
        "credential_boundary": store.boundary(),
        # Kept as empty compatibility fields for callers from earlier releases.
        # Credentials are repo_id-scoped and must never rotate another business.
        "rotated_sibling_refs": [],
        "stale_sibling_refs": [],
        "setup": _meta_setup() if provider.id == "meta" else {},
        "status": status,
    }


def _secret_statuses(
    provider: Provider,
    entry: dict[str, Any],
    *,
    deadline: float | None = None,
    probes: dict[str, SecretProbe] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    secrets: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    stored_secrets = entry.get("secrets") if isinstance(entry.get("secrets"), dict) else {}
    for field in provider.required_secrets:
        raw = stored_secrets.get(field) if isinstance(stored_secrets, dict) else None
        raw = raw if isinstance(raw, dict) else {}
        ref = str(raw.get("ref") or "")
        backend = str(raw.get("backend") or "local-file")
        probe = probes.get(field) if probes is not None else None
        if probe is None:
            probe = _probe_secret_ref(backend, ref, deadline=deadline)
        if not probe.present:
            missing.append(field)
        secrets[field] = {
            "present": probe.present,
            "ref": ref,
            "backend": backend,
            "backend_ok": probe.backend_ok,
            "backend_state": probe.reason or "ready",
        }
    return secrets, missing


def _probe_secret_ref(backend: str, ref: str, *, deadline: float | None = None) -> SecretProbe:
    """Probe stored metadata without letting a foreign backend crash status."""

    try:
        return SecretStore(backend).probe(ref, deadline=deadline)
    except (CredentialStoreError, ValueError):
        return SecretProbe("", False, False, "backend_incompatible")


def _backend_failure_reason(secrets: dict[str, Any]) -> str:
    """First backend reason code across a provider's secrets, else ``""``."""

    for raw in secrets.values():
        entry = raw if isinstance(raw, dict) else {}
        if not entry.get("backend_ok", True):
            return str(entry.get("backend_state") or "keychain_unavailable")
    return ""


def _unhydrated_status(
    provider: Provider, entry: dict[str, Any], *, deadline: float | None = None
) -> dict[str, Any]:
    secrets, missing = _secret_statuses(provider, entry, deadline=deadline)
    raw_metadata = entry.get("metadata")
    metadata: dict[str, Any] = raw_metadata if isinstance(raw_metadata, dict) else {}
    backend_reason = _backend_failure_reason(secrets)
    if backend_reason:
        state = BACKEND_FAILURE_STATE
        repair = _repair(provider, state, missing, None, backend_reason)
        ok = False
    elif missing:
        repair = _repair(provider, "missing_secret", missing)
        state = "missing_secret"
        ok = False
    else:
        repair = {
            "summary": (
                f"{provider.name} exists in user scope, but this workspace is not hydrated."
            ),
            "repair": "Run `mb connect hydrate --repo .` from this workspace.",
            "repair_command": "mb connect hydrate --repo .",
        }
        state = "needs_hydration"
        ok = False
    raw_validation = entry.get("validation")
    stored_validation: dict[str, Any] = raw_validation if isinstance(raw_validation, dict) else {}
    return {
        "provider": provider.id,
        "name": provider.name,
        "connected": True,
        "ok": ok,
        "state": state,
        "stored": bool(provider.required_secrets) and not missing and not backend_reason,
        "has_probe": has_provider_probe(provider.id),
        "provider_verified": _provider_verified(stored_validation),
        "verified_at": _verified_at(stored_validation),
        "summary": repair["summary"],
        "repair": repair["repair"],
        "repair_command": repair["repair_command"],
        "safe_to_share": True,
        "account_label": _safe_status_label(entry.get("account_label")),
        "metadata": _safe_status_metadata(metadata),
        "secrets": secrets,
        "last_checked_at": str(entry.get("last_checked_at") or ""),
        "scope": "user",
        "user_scope_available": True,
        "hydrated": False,
        "validation": {
            "state": state,
            "checked_at": "",
            "provider_verified": _provider_verified(stored_validation),
            "verified_at": _verified_at(stored_validation),
            "summary": repair["summary"],
        },
    }


def resolve_provider(provider_id: str, repo: str | Path = ".") -> Provider:
    """Resolve a provider id against the registry, then connected customs.

    Read paths (status, token, test, hydrate) use this so an already
    connected custom provider keeps working without re-passing --custom.
    """
    try:
        return normalize_provider(provider_id)
    except ValueError:
        key = provider_id.strip().lower().replace("_", "-")
        if CUSTOM_PROVIDER_RE.fullmatch(key):
            target = Path(repo).resolve()
            config = _read_config(target)
            if isinstance(config["providers"].get(key), dict):
                return _custom_provider(key)
            repo_id = str(config.get("repo_id") or _repo_identity(target)["repo_id"])
            if _user_scope_provider_entry(repo_id, key) is not None:
                return _custom_provider(key)
        raise


def status_provider(
    provider_id: str,
    repo: str | Path = ".",
    *,
    which_func: Which | None = None,
    command_runner: CommandRunner | None = None,
    _credential_deadline: float | None = None,
    _secret_probes: dict[str, SecretProbe] | None = None,
) -> dict[str, Any]:
    provider = resolve_provider(provider_id, repo)
    target = Path(repo).resolve()
    config = _read_config(target)
    identity = _repo_identity(target)
    repo_id = str(config.get("repo_id") or identity["repo_id"])
    entry = config["providers"].get(provider.id)
    if not isinstance(entry, dict):
        user_entry = _user_scope_provider_entry(repo_id, provider.id)
        if user_entry is not None:
            return _unhydrated_status(provider, user_entry, deadline=_credential_deadline)
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
        probe = _secret_probes.get("access_token") if _secret_probes is not None else None
        if probe is None:
            probe = _probe_secret_ref(backend, ref, deadline=_credential_deadline)
        secret_present = probe.present
        meta_backend_reason = "" if probe.backend_ok else (probe.reason or "keychain_unavailable")
        meta_stored = bool(secret_present and not meta_backend_reason)
        validation_state = str(meta_validation.get("state") or "unvalidated")
        if prereq_state:
            state = prereq_state
            ok = False
        elif not isinstance(entry, dict):
            state = "not_connected"
            ok = False
        elif meta_backend_reason:
            state = BACKEND_FAILURE_STATE
            ok = False
        elif not secret_present:
            state = "missing_secret"
            ok = False
        elif not str(meta_metadata.get("ad_account_id") or "").strip():
            state = "missing_metadata"
            ok = False
        elif validation_state == "ready" and _provider_verified(meta_validation):
            state = "ready"
            ok = True
        elif validation_state == "ready":
            # Recorded ready without a recorded provider call (pre-0.5.3).
            state = UNVERIFIED_STATE
            ok = False
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
            provider,
            state,
            ["access_token"] if not secret_present else [],
            meta_validation,
            meta_backend_reason,
        )
        return {
            "provider": provider.id,
            "name": provider.name,
            "connected": bool(isinstance(entry, dict) and raw_entry.get("connected", False)),
            "ok": ok,
            "state": state,
            "stored": meta_stored,
            "has_probe": has_provider_probe(provider.id),
            "provider_verified": _provider_verified(meta_validation),
            "verified_at": _verified_at(meta_validation),
            "summary": repair["summary"],
            "repair": repair["repair"],
            "repair_command": repair["repair_command"],
            "safe_to_share": True,
            "account_label": _safe_status_label(raw_entry.get("account_label")),
            "metadata": _safe_status_metadata(meta_metadata),
            "secrets": {
                "access_token": {
                    "present": secret_present,
                    "ref": ref,
                    "backend": backend,
                    "backend_ok": probe.backend_ok,
                    "backend_state": probe.reason or "ready",
                }
            },
            "last_checked_at": str(raw_entry.get("last_checked_at") or ""),
            "scope": str(raw_entry.get("scope") or "repo"),
            "user_scope_available": bool(raw_entry.get("scope") == "user"),
            "hydrated": bool(raw_entry.get("scope") == "user"),
            "setup": _meta_setup(),
            "validation": {
                "state": str(meta_validation.get("state") or state),
                "checked_at": str(meta_validation.get("checked_at") or ""),
                "provider_verified": _provider_verified(meta_validation),
                "verified_at": _verified_at(meta_validation),
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
            "stored": False,
            "has_probe": has_provider_probe(provider.id),
            "provider_verified": False,
            "verified_at": "",
            "summary": repair["summary"],
            "repair": repair["repair"],
            "repair_command": repair["repair_command"],
            "safe_to_share": True,
            "account_label": "",
            "metadata": {},
            "secrets": {},
            "last_checked_at": "",
            "scope": "repo",
            "user_scope_available": False,
            "hydrated": False,
            "validation": {
                "state": "not_connected",
                "checked_at": "",
                "provider_verified": False,
                "verified_at": "",
                "summary": "",
            },
        }

    secrets, missing = _secret_statuses(
        provider,
        entry,
        deadline=_credential_deadline,
        probes=_secret_probes,
    )

    raw_metadata = entry.get("metadata")
    metadata: dict[str, Any] = raw_metadata if isinstance(raw_metadata, dict) else {}
    raw_validation = entry.get("validation")
    validation: dict[str, Any] = raw_validation if isinstance(raw_validation, dict) else {}
    backend_reason = _backend_failure_reason(secrets)
    # "stored" is about credential material only: a provider that needs no
    # secret (hledger) has nothing stored, even though it can still be ready.
    stored = bool(provider.required_secrets) and not missing and not backend_reason
    if backend_reason:
        state = BACKEND_FAILURE_STATE
        ok = False
    elif missing:
        state = "missing_secret"
        ok = False
    elif not provider.required_secrets:
        state = "ready"
        ok = True
    else:
        validation_state = str(validation.get("state") or "unvalidated")
        if validation_state == "invalid":
            state = "invalid"
            ok = False
        elif _provider_verified(validation):
            state = "ready"
            ok = True
        elif validation_state in {"ready", UNVERIFIED_STATE}:
            # A check ran but never confirmed the credential with the provider.
            # Pre-0.5.3 metadata reaches here too: it recorded "ready" without
            # recording a provider call, so it is read as unverified.
            state = UNVERIFIED_STATE
            ok = False
        else:
            state = "unvalidated"
            ok = False
    repair = _repair(provider, state, missing, validation, backend_reason)
    return {
        "provider": provider.id,
        "name": provider.name,
        "connected": bool(entry.get("connected", False)),
        "ok": ok,
        "state": state,
        "stored": stored,
        "has_probe": has_provider_probe(provider.id),
        "provider_verified": _provider_verified(validation),
        "verified_at": _verified_at(validation),
        "summary": repair["summary"],
        "repair": repair["repair"],
        "repair_command": repair["repair_command"],
        "safe_to_share": True,
        "account_label": _safe_status_label(entry.get("account_label")),
        "metadata": _safe_status_metadata(metadata),
        "secrets": secrets,
        "last_checked_at": str(entry.get("last_checked_at") or ""),
        "scope": str(entry.get("scope") or "repo"),
        "user_scope_available": bool(entry.get("scope") == "user"),
        "hydrated": bool(entry.get("scope") == "user"),
        "validation": {
            "state": str(validation.get("state") or state),
            "checked_at": str(validation.get("checked_at") or ""),
            "provider_verified": _provider_verified(validation),
            "verified_at": _verified_at(validation),
            "summary": str(validation.get("summary") or ""),
            "upstream": validation.get("upstream")
            if isinstance(validation.get("upstream"), dict)
            else {},
            "repair": str(validation.get("repair") or ""),
            "repair_command": str(validation.get("repair_command") or ""),
            "safe_to_share": True,
        },
    }


def hydrate(
    repo: str | Path = ".",
    *,
    provider_id: str = "",
) -> dict[str, Any]:
    """Materialize ignored repo-local provider metadata from user scope."""

    target = Path(repo).resolve()
    config = _read_config(target)
    repo_id = _ensure_repo_id(config, target)
    data = _read_user_scope()
    raw_repo = data["repos"].get(repo_id)
    repo_entry = raw_repo if isinstance(raw_repo, dict) else {}
    raw_providers = repo_entry.get("providers")
    providers = raw_providers if isinstance(raw_providers, dict) else {}
    selected_ids: list[str]
    if provider_id:
        provider = resolve_provider(provider_id, repo)
        selected_ids = [provider.id]
    else:
        selected_ids = sorted(str(key) for key in providers)

    hydrated: list[str] = []
    missing: list[str] = []
    for selected in selected_ids:
        raw_entry = providers.get(selected)
        if not isinstance(raw_entry, dict):
            missing.append(selected)
            continue
        config["providers"][selected] = raw_entry
        hydrated.append(selected)

    path = ""
    if hydrated:
        path = str(_write_config(target, config))

    statuses = [status_provider(provider, target) for provider in hydrated]
    return {
        "ok": bool(hydrated) and not missing,
        "repo": str(target),
        "repo_id": repo_id,
        "config_path": path or str(_checked_config_path(target)),
        "user_scope_path": str(_user_scope_path()),
        "hydrated": hydrated,
        "missing": missing,
        "statuses": statuses,
        "safe_to_share": True,
        "repair_command": ""
        if hydrated
        else "mb connect <provider> --scope user --token-stdin --repo .",
    }


def _entry_secret_probe(
    entry: dict[str, Any], field: str, *, deadline: float | None = None
) -> SecretProbe:
    stored_secrets = entry.get("secrets") if isinstance(entry.get("secrets"), dict) else {}
    raw = stored_secrets.get(field) if isinstance(stored_secrets, dict) else None
    raw = raw if isinstance(raw, dict) else {}
    ref = str(raw.get("ref") or "")
    backend = str(raw.get("backend") or "local-file")
    return _probe_secret_ref(backend, ref, deadline=deadline)


def _entry_secret_probes(
    provider: Provider, entry: dict[str, Any], *, deadline: float | None = None
) -> dict[str, SecretProbe]:
    return {
        field: _entry_secret_probe(entry, field, deadline=deadline)
        for field in provider.required_secrets
    }


def _entry_secret_value(entry: dict[str, Any], field: str) -> str:
    return _entry_secret_probe(entry, field).value


def _stored_secret(provider: Provider, entry: dict[str, Any]) -> str:
    if not provider.required_secrets:
        return ""
    return _entry_secret_value(entry, provider.required_secrets[0])


def read_token(provider_id: str, repo: str | Path = ".") -> dict[str, Any]:
    """Resolve the stored primary credential for scripted consumers.

    The returned ``token`` exists to be written to stdout exactly once;
    callers must never log it, persist it, or embed it in shareable output.
    Falls back to user scope when the repo config has no entry, so worktrees
    and scheduled tasks resolve the same credential as the primary checkout.
    """
    provider = resolve_provider(provider_id, repo)
    if not provider.required_secrets:
        raise ValueError(f"provider {provider.id!r} stores no secrets")
    field = provider.required_secrets[0]
    target = Path(repo).resolve()
    config = _read_config(target)
    identity = _repo_identity(target)
    repo_id = str(config.get("repo_id") or identity["repo_id"])
    entry = config["providers"].get(provider.id)
    source = "repo"
    if not isinstance(entry, dict):
        entry = _user_scope_provider_entry(repo_id, provider.id)
        source = "user"
    if not isinstance(entry, dict):
        repair_command = _connect_command(provider, token_stdin=True)
        return {
            "ok": False,
            "provider": provider.id,
            "field": field,
            "source": "",
            "token": "",
            "state": "not_connected",
            "backend_state": "",
            "error": f"{provider.name} is not connected",
            "repair_command": repair_command,
        }
    probe = _entry_secret_probe(entry, field)
    if not probe.backend_ok:
        detail = _backend_repair(probe.reason)
        return {
            "ok": False,
            "provider": provider.id,
            "field": field,
            "source": source,
            "token": "",
            "state": BACKEND_FAILURE_STATE,
            "backend_state": probe.reason,
            "error": detail["summary"],
            "repair_command": detail["repair_command"],
        }
    if not probe.present:
        repair_command = _connect_command(provider, token_stdin=True)
        return {
            "ok": False,
            "provider": provider.id,
            "field": field,
            "source": source,
            "token": "",
            "state": "missing_secret",
            "backend_state": "ready",
            "error": f"{provider.name} credential is missing from the secret store",
            "repair_command": repair_command,
        }
    return {
        "ok": True,
        "provider": provider.id,
        "field": field,
        "source": source,
        "token": probe.value,
        "state": "ready",
        "backend_state": "ready",
        "error": "",
        "repair_command": "",
    }


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


def _header_secret_candidates(headers: dict[str, str] | None) -> list[str]:
    if not headers:
        return []
    candidates: list[str] = []
    for key, value in headers.items():
        key_text = str(key).lower()
        value_text = str(value)
        if not value_text:
            continue
        if key_text == "authorization":
            candidates.append(value_text)
            parts = value_text.split()
            if len(parts) >= 2 and parts[0].lower() == "bearer":
                candidates.append(parts[1])
        elif any(part in key_text for part in SENSITIVE_KEY_PARTS):
            candidates.append(value_text)
    return candidates


def _redact_sensitive_text(value: Any, secret_values: tuple[str, ...] = ()) -> str:
    text = str(value)
    for secret in sorted(set(secret_values), key=len, reverse=True):
        if len(secret) >= 4:
            text = text.replace(secret, SECRET_REPLACEMENT)
    text = BEARER_SECRET_RE.sub(f"Bearer {SECRET_REPLACEMENT}", text)
    text = SECRET_ASSIGNMENT_RE.sub(
        lambda match: f"{match.group(1)}{match.group(2)}{match.group(3) or ''}{SECRET_REPLACEMENT}",
        text,
    )
    text = SECRET_PHRASE_RE.sub(
        lambda match: f"{match.group(1)}{match.group(2) or ''}{SECRET_REPLACEMENT}",
        text,
    )
    return text


def _extract_upstream_errors(
    payload: Any, secret_values: tuple[str, ...] = ()
) -> tuple[list[str], list[str]]:
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
                messages.append(_redact_sensitive_text(message, secret_values))
    return codes, messages


def _http_get_json(
    url: str,
    headers: dict[str, str] | None = None,
    *,
    provider_name: str = "provider",
    endpoint_family: str = "unknown",
) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers or {})
    secret_values = tuple(_header_secret_candidates(headers))
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
        codes, messages = _extract_upstream_errors(payload, secret_values)
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
    codes, messages = _extract_upstream_errors(payload, secret_values)
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
        # Meta's only success path is a passing read-only account smoke, which
        # is a real provider call.
        "provider_verified": ok,
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
        # No safe read-only probe exists for this provider, so the only fact
        # available is that a credential is stored. Saying "ready" here would
        # claim a provider call that never happened.
        return {
            "ok": False,
            "state": UNVERIFIED_STATE,
            "checked_at": checked_at,
            "provider_verified": False,
            "summary": (
                f"{provider.name} has a stored credential, but Main Branch has no "
                "automated way to confirm it works with the provider."
            ),
            "repair": _unverified_repair(provider)["repair"],
            "safe_to_share": True,
        }
    return {
        "ok": bool(result["ok"]),
        "state": str(result["state"]),
        "checked_at": checked_at,
        "provider_verified": bool(result["ok"]),
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
    provider = resolve_provider(provider_id, repo)
    target = Path(repo).resolve()
    config = _read_config(target)
    entry = config["providers"].get(provider.id)
    deadline = new_credential_deadline()
    probes = (
        _entry_secret_probes(provider, entry, deadline=deadline) if isinstance(entry, dict) else {}
    )
    status = status_provider(
        provider.id,
        target,
        which_func=which_func,
        command_runner=command_runner,
        _credential_deadline=deadline,
        _secret_probes=probes,
    )
    if not isinstance(entry, dict) or status["state"] in {
        "not_connected",
        "missing_secret",
        BACKEND_FAILURE_STATE,
    }:
        return {
            "ok": False,
            "provider": provider.id,
            "stored": bool(status.get("stored")),
            "provider_verified": bool(status.get("provider_verified")),
            "verified_at": str(status.get("verified_at") or ""),
            "status": status,
            "safe_to_share": True,
        }

    if not provider.required_secrets:
        # Nothing is stored and nothing can be verified with a provider: this
        # readiness is about repo-local metadata, so it never sets
        # `provider_verified`.
        validation = {
            "ok": True,
            "state": "ready",
            "checked_at": _now(),
            "provider_verified": False,
            "summary": f"{provider.name} uses repo-local metadata and has no secret to validate.",
            "safe_to_share": True,
        }
    else:
        secret = probes[provider.required_secrets[0]].value
        if not secret:
            return {
                "ok": False,
                "provider": provider.id,
                "stored": bool(status.get("stored")),
                "provider_verified": bool(status.get("provider_verified")),
                "verified_at": str(status.get("verified_at") or ""),
                "status": status,
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

    raw_previous = entry.get("validation")
    previous: dict[str, Any] = raw_previous if isinstance(raw_previous, dict) else {}
    provider_verified = bool(validation.get("provider_verified"))
    verified_at = validation["checked_at"] if provider_verified else _verified_at(previous)
    entry["validation"] = {
        "state": validation["state"],
        "checked_at": validation["checked_at"],
        "provider_verified": provider_verified,
        "verified_at": verified_at,
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
    if entry.get("scope") == "user":
        identity = {
            "source": str(config.get("repo_identity", {}).get("source") or ""),
            "basis_sha256": str(config.get("repo_identity", {}).get("basis_sha256") or ""),
            "repo_id_source": str(config.get("repo_identity", {}).get("repo_id_source") or ""),
        }
        _write_user_scope_provider(
            str(config.get("repo_id") or _repo_identity(target)["repo_id"]),
            repo_identity=identity,
            provider_id=provider.id,
            entry=entry,
        )
    status = status_provider(
        provider.id,
        target,
        which_func=which_func,
        command_runner=command_runner,
        _credential_deadline=deadline,
        _secret_probes=probes,
    )
    return {
        "ok": bool(validation["ok"]),
        "provider": provider.id,
        "stored": bool(status.get("stored")),
        "provider_verified": provider_verified,
        "verified_at": verified_at,
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
    deadline = new_credential_deadline()
    config = _read_config(target)
    identity = _repo_identity(target)
    repo_id = str(config.get("repo_id") or identity["repo_id"])
    user_repo = _read_user_scope()["repos"].get(repo_id)
    user_repo = user_repo if isinstance(user_repo, dict) else {}
    user_providers = user_repo.get("providers")
    configured = {
        str(key).strip().lower().replace("_", "-")
        for key in config["providers"]
        if str(key).strip()
    }
    if isinstance(user_providers, dict):
        configured.update(
            str(key).strip().lower().replace("_", "-") for key in user_providers if str(key).strip()
        )
    providers = []
    for provider in PROVIDERS:
        if include_all or provider.id in configured:
            providers.append(status_provider(provider.id, target, _credential_deadline=deadline))
    custom_ids = sorted(
        provider_id for provider_id in configured if _is_custom_provider_id(provider_id)
    )
    for provider_id in custom_ids:
        providers.append(status_provider(provider_id, target, _credential_deadline=deadline))
    connected = [item for item in providers if item["connected"]]
    unverified = [item for item in connected if item["state"] == UNVERIFIED_STATE]
    # A stored-but-unverified provider is not broken: nothing is known to be
    # wrong with it and no repair command would change that. Counting it
    # separately keeps `needs_repair` meaning "there is something to fix",
    # while `ok` still refuses to call the repo fully healthy.
    broken = [item for item in connected if not item["ok"] and item["state"] != UNVERIFIED_STATE]
    unvalidated = [item for item in connected if item["state"] == "unvalidated"]
    return {
        "ok": not broken and not unverified,
        "repo": str(target),
        "config_path": str(_checked_config_path(target)),
        "repo_id": repo_id,
        "user_scope_path": str(_user_scope_path()),
        "providers": providers,
        "github": github or github_context(target),
        "safe_to_share": True,
        "summary": {
            "configured": len(connected),
            "healthy": len([item for item in connected if item["ok"]]),
            "needs_repair": len(broken),
            "unvalidated": len(unvalidated),
            "unverified": len(unverified),
            "actionable": len([item for item in connected if provider_needs_action(item)]),
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

    auth = run(["gh", "auth", "status"], target, 5.0)
    if not auth["ok"]:
        full_name = _github_repo_full_name(remote_value)
        reachable = (
            run(["gh", "repo", "view", full_name, "--json", "nameWithOwner"], target, 5.0)
            if full_name
            else {"ok": False, "stdout": "", "stderr": ""}
        )
        if reachable["ok"]:
            return {
                "ok": True,
                "state": "ready_reachable",
                "summary": (
                    "GitHub repo is reachable even though `gh auth status` reports stale "
                    "auth metadata."
                ),
                "repair": "",
                "repair_command": "",
                "repo": full_name,
                "auth_status_ok": False,
                "repo_view_ok": True,
                "safe_to_share": True,
            }
        return {
            "ok": False,
            "state": "unauthenticated",
            "summary": "GitHub CLI is installed but not authenticated.",
            "repair": "Run `gh auth login`.",
            "repair_command": "gh auth login",
            "safe_to_share": True,
        }

    return {
        "ok": True,
        "state": "ready",
        "summary": "GitHub CLI auth and repo remote are ready.",
        "repair": "",
        "repair_command": "",
        "repo": _github_repo_full_name(remote_value),
        "auth_status_ok": True,
        "repo_view_ok": False,
        "safe_to_share": True,
    }


def list_providers(repo: str | Path = ".") -> dict[str, Any]:
    status = status_all(repo, include_all=True)
    by_id = {item["provider"]: item for item in status["providers"]}
    providers = []
    for registry_entry in provider_registry():
        state = by_id[registry_entry["id"]]["state"]
        guidance = PROVIDER_GUIDANCE.get(registry_entry["id"], {})
        providers.append({**registry_entry, **guidance, "state": state, "custom": False})
    custom_providers = []
    for item in status["providers"]:
        if not _is_custom_provider_id(item["provider"]):
            continue
        custom_provider = _custom_provider(item["provider"])
        custom = {
            "id": custom_provider.id,
            "name": custom_provider.name,
            "category": custom_provider.category,
            "auth": custom_provider.auth,
            "required_secrets": list(custom_provider.required_secrets),
            "metadata_fields": list(custom_provider.metadata_fields),
            "description": custom_provider.description,
            "env_vars": list(custom_provider.env_vars),
            "state": item["state"],
            "custom": True,
            "connected": bool(item["connected"]),
            "ready": bool(item["ok"]),
            "account_label": item.get("account_label", ""),
            "scope": item.get("scope", "repo"),
            "repair_command": item.get("repair_command", ""),
        }
        providers.append(custom)
        custom_providers.append(custom)
    return {
        "ok": True,
        "providers": providers,
        "custom_providers": custom_providers,
        "config_path": status["config_path"],
    }


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
        # A broken credential backend explains every other provider failure,
        # so it leads the briefing instead of a per-provider reconnect.
        repairs.sort(key=lambda item: item["state"] != BACKEND_FAILURE_STATE)
        first = repairs[0] if repairs else {}
        names = ", ".join(item["provider"] for item in repairs[:3])
        backend_broken = first.get("state") == BACKEND_FAILURE_STATE
        detail = (
            f"{summary['needs_repair']} of {summary['configured']} connected provider(s) "
            f"need repair ({names}); run `mb connect doctor`."
        )
        if backend_broken:
            detail = (
                f"credential backend is unhealthy, so {summary['needs_repair']} of "
                f"{summary['configured']} connected provider(s) cannot be read ({names}); "
                "run `mb connect doctor`."
            )
        return {
            "name": "integration-credentials",
            "ok": False,
            "detail": detail,
            "severity": "warn",
            "repair": str(first.get("repair") or "Run `mb connect doctor`."),
            "repair_command": str(first.get("repair_command") or "mb connect doctor"),
            "safe_to_share": True,
        }
    if summary.get("unverified"):
        unverified = [item for item in status["providers"] if item["state"] == UNVERIFIED_STATE]
        names = ", ".join(item["provider"] for item in unverified[:3])
        first = unverified[0] if unverified else {}
        return {
            "name": "integration-credentials",
            "ok": False,
            "detail": (
                f"{summary['unverified']} of {summary['configured']} connected provider(s) "
                f"have a stored credential Main Branch cannot verify ({names})."
            ),
            "severity": "warn",
            "repair": str(first.get("repair") or ""),
            "repair_command": str(first.get("repair_command") or ""),
            "safe_to_share": True,
        }
    return {
        "name": "integration-credentials",
        "ok": True,
        "detail": f"{summary['healthy']} connected provider(s) verified ready",
        "severity": "ok",
        "repair": "",
        "repair_command": "",
        "safe_to_share": True,
    }


def credential_backend_health(backend: str | None = None) -> dict[str, Any]:
    """Read-only health probe of the local credential backend."""

    try:
        return SecretStore(backend).health()
    except (CredentialStoreError, ValueError) as exc:
        reason = exc.reason if isinstance(exc, CredentialStoreError) else "backend_incompatible"
        detail = _backend_repair(reason)
        return {
            "backend": str(backend or "auto"),
            "ok": False,
            "state": reason,
            "summary": detail["summary"],
            "repair": detail["repair"],
            "repair_command": detail["repair_command"],
            "safe_to_share": True,
        }


def _configured_credential_backends(status: dict[str, Any]) -> list[str]:
    backends: set[str] = set()
    raw_providers = status.get("providers")
    providers = raw_providers if isinstance(raw_providers, list) else []
    for raw_provider in providers:
        provider = raw_provider if isinstance(raw_provider, dict) else {}
        raw_secrets = provider.get("secrets")
        secrets = raw_secrets if isinstance(raw_secrets, dict) else {}
        for raw_secret in secrets.values():
            secret = raw_secret if isinstance(raw_secret, dict) else {}
            backend = str(secret.get("backend") or "")
            if backend:
                backends.add(backend)
    return sorted(backends)


def _configured_backend_health(status: dict[str, Any]) -> dict[str, Any] | None:
    backends = _configured_credential_backends(status)
    if not backends:
        return None
    raw_providers = status.get("providers")
    providers = raw_providers if isinstance(raw_providers, list) else []
    for raw_provider in providers:
        provider = raw_provider if isinstance(raw_provider, dict) else {}
        raw_secrets = provider.get("secrets")
        secrets = raw_secrets if isinstance(raw_secrets, dict) else {}
        for raw_secret in secrets.values():
            secret = raw_secret if isinstance(raw_secret, dict) else {}
            if secret.get("backend_ok", True):
                continue
            reason = str(secret.get("backend_state") or "keychain_unavailable")
            detail = _backend_repair(reason)
            return {
                "backend": str(secret.get("backend") or "unknown"),
                "ok": False,
                "state": reason,
                "summary": detail["summary"],
                "repair": detail["repair"],
                "repair_command": detail["repair_command"],
                "safe_to_share": True,
            }
    # The per-provider probes already proved each configured backend answered.
    # Re-probing here would multiply the command's native-store deadline.
    names = ", ".join(backends)
    return {
        "backend": names,
        "ok": True,
        "state": "ready",
        "summary": f"Configured credential backend(s) are ready: {names}.",
        "repair": "",
        "repair_command": "",
        "safe_to_share": True,
    }


def _probe_gap(status: dict[str, Any]) -> dict[str, Any]:
    """Connected providers Main Branch has no way to verify.

    Surfaced so a permanent `stored, unverified` reads as a known upstream gap
    that someone can close by writing a probe, rather than as a mystery the
    operator keeps trying to fix locally.
    """
    providers = sorted(
        str(item.get("provider") or "")
        for item in status.get("providers") or []
        if item.get("connected") and item.get("secrets") and not item.get("has_probe")
    )
    if not providers:
        return {"providers": [], "summary": "", "safe_to_share": True}
    return {
        "providers": providers,
        "summary": (
            f"{len(providers)} connected provider(s) have no automated probe "
            f"({', '.join(providers[:3])}); Main Branch cannot verify them until one "
            "exists upstream, so they warn without failing."
        ),
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
    ]
    # Backend health is checked before any provider repair is suggested: a
    # locked Keychain makes "reconnect the provider" advice unfollowable. Only
    # when a provider is actually connected, so a fresh repo does not warn
    # about a backend nothing depends on yet.
    backend = _configured_backend_health(status)
    if backend is not None:
        checks.append(
            {
                "name": "credential-backend",
                "ok": bool(backend["ok"]),
                "state": backend["state"],
                "summary": backend["summary"],
                "repair": backend["repair"],
                "repair_command": backend["repair_command"],
                "safe_to_share": True,
            }
        )
    checks += [
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
    ]
    # `ok` stays truthful: it is false whenever anything is unverified. The
    # exit code is a separate question — see `provider_needs_action`.
    needs_action = any(
        not check["ok"] for check in checks if not str(check["name"]).startswith("provider:")
    ) or any(provider_needs_action(item) for item in status["providers"])
    return {
        "ok": all(check["ok"] for check in checks),
        "needs_action": needs_action,
        "probe_gap": _probe_gap(status),
        "repo": status["repo"],
        "checks": checks,
        "integrations": status,
        "safe_to_share": True,
    }


# --- Credential hygiene (mb connect hygiene) -------------------------------
#
# Read-only scan of known agent-config surfaces for PLAINTEXT credentials that
# violate the agent-access-dossier never-print doctrine. The scan reports the
# surface, the dotted location, and a length-only mask — it NEVER emits the
# secret value itself. Findings carry a one-line keychain/env remediation.

# Value-shape prefixes that betray a real credential regardless of key name.
CREDENTIAL_VALUE_PREFIXES: tuple[str, ...] = (
    "sk_",
    "rk_",
    "re_",
    "sk-",
    "fal-",
    "AIza",
    "ghp_",
    "gho_",
    "github_pat_",
    "xoxb-",
    "xoxp-",
    "glpat-",
    "AKIA",
)
_HYGIENE_SECRET_KEY_RE = re.compile(
    r"(?i)(token|api[_-]?key|secret|password|passwd|bearer|authorization|"
    r"access[_-]?key|developer[_-]?token|client[_-]?secret|private[_-]?key)"
)
# A value that is wholly or partly an env reference (${VAR}, $VAR) is correctly
# externalized — not a plaintext leak.
_ENV_REFERENCE_RE = re.compile(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?")
# A value is "externalized" only if it is WHOLLY env reference(s) (optionally a
# Bearer prefix) — not a literal secret with an env ref tacked on. Matching a
# bare .search() let "${ENV}sk-realsecret" pass as safe (false negative).
_ENV_REFERENCE_FULL_RE = re.compile(r"(?i)^(bearer\s+)?(\$\{?[A-Za-z_][A-Za-z0-9_]*\}?)+$")
_PLACEHOLDER_VALUES = frozenset(
    {"", "changeme", "change-me", "todo", "none", "null", "example", "redacted"}
)
# An ISO-8601 date or timestamp is not a secret. Housekeeping fields like
# `claudeCodeFirstTokenDate` match the secret-named-key heuristic ("Token")
# but hold a date string — excluding the shape keeps the count honest.
_ISO_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?)?$"
)

# JSON config surfaces scanned by default. TOML surfaces (e.g. ~/.codex/
# config.toml) are a follow-up slice (tomllib is 3.11+; the matrix includes
# 3.10), tracked on the hygiene issue.
HYGIENE_HOME_SURFACES: tuple[str, ...] = (".claude.json",)
HYGIENE_REPO_SURFACES: tuple[str, ...] = (
    ".mcp.json",
    ".claude/settings.json",
    ".claude/settings.local.json",
)


def _looks_like_env_reference(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    # Safe only if the WHOLE value is env reference(s) (e.g. "Bearer ${FAL_KEY}").
    # A literal secret mixed with an env ref is NOT safe.
    return bool(_ENV_REFERENCE_FULL_RE.match(stripped))


def _looks_like_iso_datetime(value: str) -> bool:
    return bool(_ISO_DATETIME_RE.match(value.strip()))


def _looks_like_placeholder(value: str) -> bool:
    stripped = value.strip()
    lowered = stripped.lower()
    if lowered in _PLACEHOLDER_VALUES:
        return True
    if stripped.startswith("<") and stripped.endswith(">"):
        return True
    if lowered.startswith(("your_", "your-", "<your", "xxx")):
        return True
    return bool(stripped and set(stripped) <= {"x", "X", "*", "•", "."})


def _credential_value_prefix(value: str) -> str:
    candidate = value.strip()
    if candidate.lower().startswith("bearer "):
        candidate = candidate[7:].strip()
    for prefix in CREDENTIAL_VALUE_PREFIXES:
        if candidate.startswith(prefix):
            return prefix
    return ""


def _classify_credential_value(key: str, value: str) -> tuple[bool, str]:
    """Return (flagged, reason) without ever surfacing the value."""
    if not isinstance(value, str):
        return False, ""
    if (
        _looks_like_env_reference(value)
        or _looks_like_placeholder(value)
        or _looks_like_iso_datetime(value)
    ):
        return False, ""
    prefix = _credential_value_prefix(value)
    if prefix:
        return True, f"value carries the `{prefix}` credential prefix"
    # A secret-named key holding a non-referenced, non-placeholder literal with
    # some entropy (a digit or mixed case) reads as a real plaintext credential.
    if (
        _HYGIENE_SECRET_KEY_RE.search(key)
        and len(value.strip()) >= 12
        and (any(ch.isdigit() for ch in value) or not value.islower())
    ):
        return True, f"secret-named key `{key}` holds a plaintext value"
    return False, ""


def _walk_json_for_secrets(
    node: Any, path: str, surface: str, findings: list[dict[str, Any]]
) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            child_path = f"{path}.{key}" if path else str(key)
            if isinstance(value, str):
                flagged, reason = _classify_credential_value(str(key), value)
                if flagged:
                    findings.append(
                        {
                            "surface": surface,
                            "location": child_path,
                            "key": str(key),
                            "reason": reason,
                            "mask": f"••• ({len(value)} chars)",
                            "remediation": (
                                "move the value into the OS keychain "
                                "(`mb connect <provider> --token-stdin`) or a gitignored "
                                "env.sh, then reference it as ${ENV_VAR} in this config"
                            ),
                            "safe_to_share": True,
                        }
                    )
            else:
                _walk_json_for_secrets(value, child_path, surface, findings)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _walk_json_for_secrets(value, f"{path}[{index}]", surface, findings)


def _scan_surface(path: Path, label: str) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Scan one JSON surface. Returns (findings, skip_record_or_None)."""
    if not path.exists():
        return [], None
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return [], {"surface": label, "reason": "unreadable"}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return [], {"surface": label, "reason": "not valid JSON"}
    findings: list[dict[str, Any]] = []
    _walk_json_for_secrets(data, "", label, findings)
    return findings, None


def scan_credential_hygiene(
    repo: str | Path = ".", *, home: str | Path | None = None
) -> dict[str, Any]:
    """Flag plaintext credentials in known agent-config surfaces (read-only).

    Never emits a secret value — findings carry the surface, dotted location,
    a length-only mask, and a keychain/env remediation. ``home`` overrides the
    home directory (tests, alternate profiles).
    """
    repo_path = Path(repo).expanduser().resolve()
    # Agent configs (~/.claude.json) live in the real home directory, not the
    # mainbranch secret-store home (_home()).
    home_path = Path(home).expanduser().resolve() if home is not None else Path.home()

    findings: list[dict[str, Any]] = []
    scanned: list[str] = []
    skipped: list[dict[str, Any]] = []

    surfaces: list[tuple[Path, str]] = [
        (home_path / name, f"~/{name}") for name in HYGIENE_HOME_SURFACES
    ]
    surfaces += [(repo_path / name, name) for name in HYGIENE_REPO_SURFACES]

    for path, label in surfaces:
        if not path.exists():
            continue
        surface_findings, skip = _scan_surface(path, label)
        if skip is not None:
            skipped.append(skip)
            continue
        scanned.append(label)
        findings.extend(surface_findings)

    # A surface that could not be scanned was NOT proven clean — it must not
    # yield a clean machine verdict (gates/automation read ok + the exit code).
    ok = not findings and not skipped
    if not findings:
        summary = f"no plaintext credentials found across {len(scanned)} scanned config surface(s)"
    else:
        summary = (
            f"{len(findings)} plaintext credential(s) in agent config — move them "
            "to the keychain/env and reference via ${ENV_VAR}"
        )
    # Surface unscannable files loudly — a config that could not be parsed was
    # NOT proven clean; silence there would be a false all-clear.
    if skipped:
        labels = ", ".join(str(item["surface"]) for item in skipped)
        summary += (
            f" — WARNING: {len(skipped)} surface(s) could not be scanned "
            f"(not proven clean): {labels}"
        )
    return {
        "ok": ok,
        "repo": str(repo_path),
        "home": str(home_path),
        "surfaces_scanned": scanned,
        "surfaces_skipped": skipped,
        "findings": findings,
        "summary": summary,
        "safe_to_share": True,
    }


def render_credential_hygiene(result: dict[str, Any]) -> None:
    print(f"mb connect hygiene  {result['repo']}")
    print(result["summary"])
    for finding in result["findings"]:
        print(f"  warn  {finding['surface']} → {finding['location']}")
        print(f"        {finding['reason']} {finding['mask']}")
        print(f"        next: {finding['remediation']}")
    for skip in result["surfaces_skipped"]:
        print(f"  skip  {skip['surface']}: {skip['reason']}")
    if result["ok"]:
        print("  ok    every scanned surface references secrets indirectly")


# --- Canonical business identity (mb connect identity) ---------------------
#
# Agents must read identity (ad account, pixel, page, sender domain, Stripe
# account/mode) from RECORDED facts, never infer it from live provider state
# (mining friction #1). Each provider's registry metadata_fields IS the
# canonical identity schema; this surface aggregates the recorded values and
# names what's still unrecorded. Output carries business identifiers, so it is
# operator-facing (safe_to_share=False) — never paste into public artifacts.


def business_identity(repo: str | Path = ".") -> dict[str, Any]:
    """Aggregate recorded business-identity metadata across connected providers."""
    target = Path(repo).resolve()
    status = status_all(target)
    pmap = provider_map()
    providers_out: list[dict[str, Any]] = []
    for item in status["providers"]:
        if not item["connected"]:
            continue
        provider = pmap.get(item["provider"])
        metadata = item.get("metadata") or {}
        metadata = metadata if isinstance(metadata, dict) else {}
        if provider:
            fields = provider.metadata_fields
            if not fields:
                continue
            recorded = {field: str(metadata.get(field, "")) for field in fields}
            missing = [field for field in fields if not recorded[field]]
            schema = "registry"
        elif _is_custom_provider_id(str(item["provider"])):
            recorded = _safe_identity_metadata(metadata)
            if not recorded:
                continue
            missing = []
            schema = "custom_metadata"
        else:
            continue
        providers_out.append(
            {
                "provider": item["provider"],
                "name": item["name"],
                "custom": provider is None,
                "identity_schema": schema,
                "identity": recorded,
                "missing_fields": missing,
                "complete": not missing,
            }
        )
    total_missing = sum(len(item["missing_fields"]) for item in providers_out)
    if not providers_out:
        summary = "no connected providers carry identity metadata yet"
    elif total_missing == 0:
        summary = f"all {len(providers_out)} connected provider(s) have complete recorded identity"
    else:
        summary = (
            f"{total_missing} identity field(s) unrecorded across "
            f"{len(providers_out)} connected provider(s) — record them with "
            "`mb connect <provider> --metadata <field>=<value>` so agents read "
            "facts, not live state"
        )
    return {
        "ok": True,
        "repo": str(target),
        "providers": providers_out,
        "summary": summary,
        # Carries ad account / pixel / page / sender-domain identifiers.
        "safe_to_share": False,
    }


def render_identity(result: dict[str, Any]) -> None:
    print(f"mb connect identity  {result['repo']}")
    print(result["summary"])
    for item in result["providers"]:
        mark = "ok" if item["complete"] else "warn"
        print(f"  {mark}  {item['provider']}")
        for field, value in item["identity"].items():
            shown = value if value else "(unrecorded)"
            print(f"        {field}: {shown}")


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


def state_label(state: str) -> str:
    """Human phrasing for a provider state. JSON keeps the machine value."""
    return "stored, unverified" if state == UNVERIFIED_STATE else state


def render_status(result: dict[str, Any]) -> None:
    summary = result["summary"]
    print(f"mb connect status  {result['repo']}")
    line = (
        f"configured: {summary['configured']}  "
        f"healthy: {summary['healthy']}  needs repair: {summary['needs_repair']}"
    )
    if summary.get("unverified"):
        line += f"  unverified: {summary['unverified']}"
    print(line)
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
        print(f"  {state}  {item['provider']}{label}: {state_label(item['state'])}")
        if item["repair_command"]:
            print(f"       next: {item['repair_command']}")


def render_provider_status(result: dict[str, Any]) -> None:
    state = "ok" if result["ok"] else "warn"
    label = f" ({result['account_label']})" if result["account_label"] else ""
    print(
        f"mb connect status {result['provider']}{label}: {state} ({state_label(result['state'])})"
    )
    if result.get("summary"):
        print(f"summary: {result['summary']}")
    if result.get("repair_command"):
        print(f"next: {result['repair_command']}")


def render_doctor(result: dict[str, Any]) -> None:
    print(f"mb connect doctor  {result['repo']}")
    for check in result["checks"]:
        state = "ok" if check["ok"] else "warn"
        print(f"  {state}  {check['name']}: {state_label(check['state'])}")
        if check["repair_command"]:
            print(f"       next: {check['repair_command']}")
    probe_gap = result.get("probe_gap") or {}
    if probe_gap.get("providers"):
        print(f"  note  no provider probe: {', '.join(probe_gap['providers'])}")
        print(f"       {probe_gap['summary']}")


def render_test_result(result: dict[str, Any]) -> None:
    status = result["status"]
    state = "ok" if result["ok"] else "warn"
    print(f"mb connect test {result['provider']}: {state} ({state_label(status['state'])})")
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


def render_hydrate_result(result: dict[str, Any]) -> None:
    print(f"mb connect hydrate  {result['repo']}")
    if result["hydrated"]:
        print(f"hydrated: {', '.join(result['hydrated'])}")
        print(f"metadata: {result['config_path']}")
    else:
        print("no user-scoped provider metadata found for this repo")
    if result["missing"]:
        print(f"missing: {', '.join(result['missing'])}")
    if result.get("repair_command"):
        print(f"next: {result['repair_command']}")


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
    elif status["state"] == BACKEND_FAILURE_STATE:
        print(f"connected {result['provider']} metadata; credential backend is unhealthy")
        print(f"summary: {status['summary']}")
        print(f"repair: {status['repair']}")
    elif not result["ok"]:
        print(f"connected {result['provider']} metadata; credential still needs repair")
    else:
        print(f"connected {result['provider']} metadata")
    print(f"metadata: {result['config_path']}")
    if result.get("scope") == "user":
        print(f"user scope: {result['user_scope_path']}")
    print(f"secrets: {result['credential_boundary']}")
    rotated = result.get("rotated_sibling_refs") or []
    if rotated:
        print(
            f"rotated {len(rotated)} sibling ref(s) to the new credential (other repos/worktrees)"
        )
    stale = result.get("stale_sibling_refs") or []
    if stale:
        print(
            f"WARNING: {len(stale)} sibling ref(s) could not be updated "
            "and still hold the OLD credential:"
        )
        for ref in stale:
            print(f"  - {ref}")
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
    value = sys.stdin.read()
    # Treat one final line ending as the stdin transport delimiter. Preserve
    # every other leading, trailing, and embedded character exactly.
    if value.endswith("\r\n"):
        return value[:-2]
    if value.endswith("\n"):
        return value[:-1]
    return value
