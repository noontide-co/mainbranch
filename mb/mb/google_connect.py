"""``mb connect google --oauth``: the one-time Google sign-in for a business repo.

Read-only Search Console and GA4. A person runs this, never an agent: it opens
a browser (or, with ``--paste``, reads the redirect URL from a real terminal),
receives the authorization code on ``http://127.0.0.1:<port>``, exchanges it
with PKCE and stores the grant. Nothing here calls Google beyond the token
exchange; checking the grant against the APIs comes with ``mb connect test``
in a later release.

Storage (one credential-store item per slot, refs from ``_secret_ref``):

1. ``oauth_grant``: JSON ``client_id``, ``client_secret`` (when the client has
   one), ``refresh_token`` and ``refresh_token_expires_in`` (when returned).
2. ``access_token``: the token from the exchange, as a placeholder that keeps
   ``stored``, ``list`` and ``identity`` working. It is never refreshed.
3. The repo metadata (``.mb/connect.yaml``, and the user-scope file for a
   user-scope entry): refs, ``search_console_site``, ``ga4_property_id``,
   ``oauth_grants``. Readers only follow refs the metadata records, so on a
   first connect nothing is visible until this last write lands.

Every failure carries fixed text; no code, verifier, client secret or token
reaches an exception message, stdout, stderr, JSON or ``repr``.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import webbrowser
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TextIO

from mb import connect as connect_mod
from mb import google_oauth as go
from mb.credential_store import SecretStore, new_credential_deadline

PROVIDER_ID = "google"
GRANT_SLOT = connect_mod.GOOGLE_OAUTH_GRANT_SLOT
TOKEN_SLOT = "access_token"
CLIENT_JSON_MAX_BYTES = 65536
DEFAULT_TIMEOUT_SECONDS = 300
GRANT_LABEL_NAMES = {"search_console": "Search Console", "ga4": "Analytics (GA4)"}
METADATA_SITE = "search_console_site"
METADATA_PROPERTY = "ga4_property_id"
METADATA_GRANTS = connect_mod.GOOGLE_OAUTH_GRANTS_METADATA

_HOST_LABEL_RE = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)$")
_CLIENT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,254}$")
_PROPERTY_RE = re.compile(r"^[0-9]{1,20}$")

# Test seams. The CLI uses these defaults; tests replace them.
Opener = Callable[[str], bool]
open_browser: Opener = webbrowser.open
token_sender: go.Sender | None = None


class GoogleConnectError(RuntimeError):
    """A bootstrap failure after something may have been written.

    ``state`` is the machine code; ``backend_state`` is set when the credential
    store failed. The message is fixed text that says what is now stored.
    """

    def __init__(
        self, message: str, *, state: str, rule: str = "", backend_state: str = ""
    ) -> None:
        super().__init__(message)
        self.state = state
        self.rule = rule
        self.backend_state = backend_state


@dataclass(frozen=True)
class OAuthClient:
    client_id: str
    client_secret: str = field(default="", repr=False)


# --- Inputs ------------------------------------------------------------------


def parse_client_json(text: str) -> OAuthClient:
    """Read a downloaded Desktop-app OAuth client file (``{"installed": {...}}``)."""

    if len(text.encode("utf-8", "replace")) > CLIENT_JSON_MAX_BYTES:
        connect_mod._refuse(
            "oauth_client_malformed",
            "the OAuth client file is too large to be a Google client file. Nothing was "
            "stored. Download the Desktop app client JSON again from the Google Cloud console.",
        )
    try:
        raw = json.loads(text)
    except ValueError:
        raw = None
    if isinstance(raw, dict) and "installed" not in raw and "web" in raw:
        connect_mod._refuse(
            "oauth_client_not_desktop",
            "the OAuth client file is for a Web application client. Nothing was stored. "
            "Create an OAuth client of type Desktop app and download its JSON.",
        )
    section = raw.get("installed") if isinstance(raw, dict) else None
    client_id = section.get("client_id") if isinstance(section, dict) else None
    client_secret = section.get("client_secret", "") if isinstance(section, dict) else None
    if (
        not isinstance(client_id, str)
        or not _CLIENT_ID_RE.match(client_id)
        or not isinstance(client_secret, str)
    ):
        connect_mod._refuse(
            "oauth_client_malformed",
            "the OAuth client file is not a Google Desktop app client JSON (it needs "
            '"installed" with a "client_id"). Nothing was stored. Download it again from '
            "the Google Cloud console.",
        )
    return OAuthClient(client_id=client_id, client_secret=client_secret)


def read_client_file(path: str) -> str:
    try:
        with open(Path(path).expanduser(), "rb") as handle:
            data = handle.read(CLIENT_JSON_MAX_BYTES + 1)
    except OSError:
        connect_mod._refuse(
            "oauth_client_unreadable",
            "the OAuth client file could not be read. Nothing was stored. Check the path "
            "given to --client-file.",
        )
    return data.decode("utf-8", "replace")


def _valid_host(host: str) -> bool:
    labels = host.split(".")
    return len(labels) >= 2 and all(_HOST_LABEL_RE.match(label) for label in labels)


def normalize_search_console_site(value: str) -> str:
    """``sc-domain:<host>``, or a URL-prefix property ``http(s)://<host>/...`` ending in ``/``."""

    site = value.strip()
    if site.startswith("sc-domain:"):
        host = site.removeprefix("sc-domain:").lower()
        if _valid_host(host):
            return f"sc-domain:{host}"
    else:
        parsed = urllib.parse.urlsplit(site)
        if (
            parsed.scheme in {"http", "https"}
            and parsed.hostname
            and _valid_host(parsed.hostname)
            and not parsed.username
            and not parsed.password
            and not parsed.query
            and not parsed.fragment
            and "?" not in site
            and "#" not in site
            and parsed.path.startswith("/")
            and site.endswith("/")
        ):
            return site
    connect_mod._refuse(
        "search_console_site_format",
        "search_console_site must be a Search Console property: sc-domain:example.com, or a "
        "URL prefix such as https://www.example.com/ (ending in /). Nothing was stored.",
    )


def normalize_ga4_property_id(value: str) -> str:
    """A numeric GA4 property id; ``properties/123`` becomes ``123``."""

    prop = value.strip().removeprefix("properties/")
    if not _PROPERTY_RE.match(prop):
        connect_mod._refuse(
            "ga4_property_id_format",
            "ga4_property_id must be the numeric GA4 property id (for example 123456789 or "
            "properties/123456789), not a measurement id (G-...). Nothing was stored.",
        )
    return prop


def _oauth_metadata(pairs: list[str], existing: dict[str, Any]) -> dict[str, str]:
    given = connect_mod._parse_metadata(pairs)
    if METADATA_GRANTS in given:
        connect_mod._refuse(
            "oauth_metadata_reserved",
            f"{METADATA_GRANTS} is recorded by the Google sign-in itself and cannot be set "
            "with --metadata. Nothing was stored.",
        )
    if METADATA_SITE in given:
        given[METADATA_SITE] = normalize_search_console_site(given[METADATA_SITE])
    if METADATA_PROPERTY in given:
        given[METADATA_PROPERTY] = normalize_ga4_property_id(given[METADATA_PROPERTY])
    merged = {str(key): str(value) for key, value in existing.items() if value not in (None, "")}
    merged.update(given)
    return merged


# --- Existing connection -----------------------------------------------------


@dataclass
class _Existing:
    entry: dict[str, Any]
    grant: dict[str, str]
    token: dict[str, str]

    @property
    def oauth(self) -> bool:
        return bool(self.grant.get("ref"))

    @property
    def has_access_token(self) -> bool:
        return bool(self.token.get("ref"))


def _slot(entry: dict[str, Any], name: str) -> dict[str, str]:
    raw_secrets = entry.get("secrets")
    secrets = raw_secrets if isinstance(raw_secrets, dict) else {}
    raw = secrets.get(name)
    if not isinstance(raw, dict) or not raw.get("ref"):
        return {}
    return {"ref": str(raw["ref"]), "backend": str(raw.get("backend") or "local-file")}


def _existing_entry(config: dict[str, Any], repo_id: str) -> _Existing:
    raw = config["providers"].get(PROVIDER_ID)
    if not isinstance(raw, dict):
        raw = connect_mod._user_scope_provider_entry(repo_id, PROVIDER_ID)
    entry = raw if isinstance(raw, dict) else {}
    return _Existing(entry=entry, grant=_slot(entry, GRANT_SLOT), token=_slot(entry, TOKEN_SLOT))


def entry_is_oauth(entry: dict[str, Any] | None) -> bool:
    return isinstance(entry, dict) and bool(_slot(entry, GRANT_SLOT))


def _refuse_by_mode(existing: _Existing, *, reauth: bool, replace_access_token: bool) -> None:
    if existing.oauth and not reauth:
        connect_mod._refuse(
            "oauth_use_reauth",
            "this repo already has a Google sign-in. Renew it only when status says "
            "reauth_required, with `mb connect google --oauth --reauth`: each sign-in uses "
            "one of Google's 100 refresh tokens per account and OAuth client, and the oldest "
            "is silently revoked. Nothing was changed.",
        )
    if reauth and not existing.oauth:
        connect_mod._refuse(
            "oauth_reauth_without_grant",
            "there is no Google sign-in to renew in this repo. Run `mb connect google --oauth` "
            "without --reauth. Nothing was changed.",
        )
    if existing.has_access_token and not existing.oauth and not replace_access_token:
        connect_mod._refuse(
            "oauth_replaces_access_token",
            "this replaces the stored Google access token; Drive, Docs and Sheets use of this "
            "connection stops working. Re-run with --replace-access-token to proceed. "
            "Nothing was changed.",
        )


def _stored_client(existing: _Existing) -> OAuthClient | None:
    """The client recorded in the current grant, for ``--reauth`` without a client file."""

    try:
        probe = SecretStore(existing.grant["backend"]).probe(existing.grant["ref"])
    except (connect_mod.KeychainError, ValueError):
        return None
    if not probe.present:
        return None
    try:
        raw = json.loads(probe.value)
    except ValueError:
        return None
    if not isinstance(raw, dict):
        return None
    client_id = raw.get("client_id")
    client_secret = raw.get("client_secret") or ""
    if not isinstance(client_id, str) or not client_id or not isinstance(client_secret, str):
        return None
    return OAuthClient(client_id=client_id, client_secret=client_secret)


# --- The sign-in -------------------------------------------------------------


def _stdin_is_tty(stream: TextIO | None) -> bool:
    try:
        return bool((stream if stream is not None else sys.stdin).isatty())
    except (AttributeError, ValueError, OSError):
        return False


def _paste_redirect_uri(port: int) -> str:
    # Nothing listens in paste mode: the browser lands on an unreachable page
    # and the operator copies its URL. Any free-looking port works.
    return go.loopback_redirect_uri(port or 8085)


def _sign_in(
    client: OAuthClient,
    *,
    paste: bool,
    no_browser: bool,
    port: int,
    timeout: float,
    emit: Callable[[str], None],
    opener: Opener,
    stdin: TextIO | None,
    paste_reader: Callable[[str], str] | None,
    sender: go.Sender | None,
) -> go.TokenResponse:
    verifier = go.new_code_verifier()
    state = go.new_state()
    challenge = go.code_challenge(verifier)
    emit("Google sign-in (read-only: Search Console, Analytics)")
    if paste:
        redirect_uri = _paste_redirect_uri(port)
        url = go.build_auth_url(
            client_id=client.client_id,
            redirect_uri=redirect_uri,
            code_challenge=challenge,
            state=state,
        )
        emit("Open this URL in a browser on any machine and allow access:")
        emit(f"  {url}")
        emit(
            "The browser then shows a page that cannot load. Copy that page's whole address "
            "(it starts with http://127.0.0.1) and paste it here. Never paste it into a chat."
        )
        code = go.read_pasted_redirect(state, stdin=stdin, reader=paste_reader)
    else:
        with go.LoopbackReceiver(state, port=port, timeout=timeout) as receiver:
            redirect_uri = receiver.redirect_uri
            url = go.build_auth_url(
                client_id=client.client_id,
                redirect_uri=redirect_uri,
                code_challenge=challenge,
                state=state,
            )
            if no_browser:
                emit(f"Open this URL in a browser that can reach {redirect_uri}:")
                emit(f"  {url}")
            else:
                emit("Opening your browser. If it does not open, visit:")
                emit(f"  {url}")
                # webbrowser, never our own argv subprocess. A failure to open
                # is fine: the URL above is the fallback.
                with suppress(Exception):
                    opener(url)
            minutes = max(1, round(timeout / 60))
            emit(f"Waiting for Google on {redirect_uri} ({minutes} min)...")
            code = receiver.wait()
    return go.exchange_code(
        client_id=client.client_id,
        client_secret=client.client_secret or None,
        code=code,
        code_verifier=verifier,
        redirect_uri=redirect_uri,
        sender=sender,
    )


def _grant_json(client: OAuthClient, tokens: go.TokenResponse) -> str:
    grant: dict[str, Any] = {"client_id": client.client_id}
    if client.client_secret:
        grant["client_secret"] = client.client_secret
    grant["refresh_token"] = tokens["refresh_token"]
    if "refresh_token_expires_in" in tokens:
        grant["refresh_token_expires_in"] = tokens["refresh_token_expires_in"]
    return json.dumps(grant, separators=(",", ":"), sort_keys=True)


# --- Storage and its honest failure messages ---------------------------------


@dataclass
class _Writes:
    """What has been written so far, for the partial-failure message."""

    fresh: bool  # no OAuth grant was recorded before this run
    replaced_access_token: bool  # an access-token-only entry is being upgraded
    grant: bool = False
    token: bool = False


def _partial_message(writes: _Writes, failed: str) -> str:
    if failed == "grant":
        return "Nothing was stored and the repo metadata is unchanged."
    if writes.fresh:
        lead = (
            "The Google grant was written to the credential store but this repo does not "
            "record it, so the connection is not set up; the unrecorded item is unused and "
            "the next sign-in overwrites it."
        )
        if writes.replaced_access_token and writes.token:
            lead += (
                " The previously stored Google access token was already replaced by the new "
                "read-only one, so Drive, Docs and Sheets use of this connection has stopped."
            )
        return lead + " Re-run `mb connect google --oauth` once the store is healthy."
    if failed == "token":
        return (
            "The new Google grant is stored and replaced the old one, but the access-token "
            "placeholder and the repo metadata were not updated. The connection uses the new "
            "grant; run `mb connect test google`."
        )
    return (
        "The new Google grant and access token are stored and replaced the old ones, but the "
        "repo metadata was not updated, so the granted products and the site or property it "
        "shows may be stale. Run `mb connect test google`."
    )


def _store_failure(
    exc: connect_mod.KeychainError, writes: _Writes, failed: str
) -> GoogleConnectError:
    detail = connect_mod._backend_repair(exc.reason)
    return GoogleConnectError(
        f"{detail['summary']} {_partial_message(writes, failed)} {detail['repair']}".strip(),
        state=connect_mod.BACKEND_FAILURE_STATE,
        backend_state=exc.reason,
    )


def bootstrap(
    repo: str | Path = ".",
    *,
    client_json: str | None,
    metadata_pairs: list[str] | None = None,
    reauth: bool = False,
    paste: bool = False,
    no_browser: bool = False,
    port: int = 0,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    replace_access_token: bool = False,
    account_label: str = "",
    scope: str = "repo",
    secret_backend: str | None = None,
    emit: Callable[[str], None] | None = None,
    opener: Opener | None = None,
    sender: go.Sender | None = None,
    stdin: TextIO | None = None,
    paste_reader: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """Run the sign-in and store the grant. Refusals raise ``ConnectRefusal``.

    ``GoogleOAuthError`` (declined, timeout, state mismatch, token endpoint)
    means nothing was stored. ``GoogleConnectError`` means a write failed and
    its message says what is stored now.
    """

    say = emit or (lambda line: print(line, file=sys.stderr))
    provider = connect_mod.normalize_provider(PROVIDER_ID)
    normalized_scope = scope.strip().lower().replace("_", "-") or "repo"
    if normalized_scope not in connect_mod.CONNECT_SCOPES:
        connect_mod._refuse("connect_scope", "--scope must be repo or user. Nothing was changed.")
    target = Path(repo).resolve()
    config = connect_mod._read_config(target)
    repo_id = connect_mod._ensure_repo_id(config, target)
    existing = _existing_entry(config, repo_id)
    _refuse_by_mode(existing, reauth=reauth, replace_access_token=replace_access_token)
    raw_metadata = existing.entry.get("metadata")
    metadata = _oauth_metadata(
        list(metadata_pairs or []), raw_metadata if isinstance(raw_metadata, dict) else {}
    )
    if client_json is not None:
        client = parse_client_json(client_json)
    else:
        stored = _stored_client(existing) if reauth else None
        if stored is None:
            connect_mod._refuse(
                "oauth_client_required",
                "pass the OAuth client with --client-file PATH or --client-stdin"
                + (
                    " (the stored grant could not be read, so its client is unknown)"
                    if reauth
                    else ""
                )
                + ". Nothing was changed.",
            )
        client = stored
    if paste and not _stdin_is_tty(stdin):
        raise go.GoogleOAuthError("paste_needs_tty")
    if existing.entry:
        normalized_scope = str(existing.entry.get("scope") or normalized_scope)

    tokens = _sign_in(
        client,
        paste=paste,
        no_browser=no_browser,
        port=port,
        timeout=timeout,
        emit=say,
        opener=opener or open_browser,
        stdin=stdin,
        paste_reader=paste_reader,
        sender=sender if sender is not None else token_sender,
    )
    if not tokens.get("refresh_token"):
        raise GoogleConnectError(
            "Google returned no refresh token, so Main Branch could not read later without "
            "another sign-in. Nothing was stored. Check that the OAuth client is a Desktop "
            "app client, then sign in again.",
            state="no_refresh_token",
            rule="oauth_no_refresh_token",
        )
    granted = go.granted_labels(str(tokens.get("scope") or ""))
    if not granted:
        raise GoogleConnectError(
            "The sign-in granted neither Search Console nor Analytics read access. Nothing "
            "was stored. Sign in again and tick both read-only boxes.",
            state="grant_missing",
            rule="oauth_no_scope_granted",
        )
    missing = [label for label in GRANT_LABEL_NAMES if label not in granted]
    metadata[METADATA_GRANTS] = ",".join(granted)

    deadline = new_credential_deadline()
    backend = existing.grant.get("backend") or existing.token.get("backend") or secret_backend
    store = SecretStore(backend)
    grant_ref = connect_mod._secret_ref(repo_id, PROVIDER_ID, GRANT_SLOT)
    token_ref = connect_mod._secret_ref(repo_id, PROVIDER_ID, TOKEN_SLOT)
    writes = _Writes(
        fresh=not existing.oauth,
        replaced_access_token=existing.has_access_token and not existing.oauth,
    )
    try:
        store.set(grant_ref, _grant_json(client, tokens), deadline=deadline)
    except connect_mod.KeychainError as exc:
        raise _store_failure(exc, writes, "grant") from None
    writes.grant = True
    try:
        store.set(token_ref, str(tokens["access_token"]), deadline=deadline)
    except connect_mod.KeychainError as exc:
        raise _store_failure(exc, writes, "token") from None
    writes.token = True

    now = connect_mod._now()
    entry = {
        "provider": provider.id,
        "connected": True,
        "scope": normalized_scope,
        "account_label": account_label.strip() or str(existing.entry.get("account_label") or ""),
        "connected_at": now,
        "last_checked_at": now,
        "auth": provider.auth,
        "secrets": {
            TOKEN_SLOT: {"ref": token_ref, "backend": store.backend},
            GRANT_SLOT: {"ref": grant_ref, "backend": store.backend},
        },
        "metadata": metadata,
    }
    config["providers"][provider.id] = entry
    user_scope_path = ""
    try:
        if normalized_scope == "user":
            user_scope_path = str(
                connect_mod._write_user_scope_provider(
                    repo_id,
                    repo_identity=config.get("repo_identity") or {},
                    provider_id=provider.id,
                    entry=entry,
                )
            )
        path = connect_mod._write_config(target, config)
    except (OSError, ValueError):
        raise GoogleConnectError(
            "The repo metadata could not be written. " + _partial_message(writes, "metadata"),
            state="metadata_write_failed",
        ) from None

    status = connect_mod.status_provider(provider.id, target, _credential_deadline=deadline)
    return {
        "ok": not missing and status["state"] not in {"missing_secret", "backend_unavailable"},
        "ready": False,
        "provider": provider.id,
        "credential_mode": "oauth",
        "reauth": reauth,
        "oauth_grants": granted,
        "missing_grants": missing,
        "scope": normalized_scope,
        "config_path": str(path),
        "user_scope_path": user_scope_path,
        "credential_backend": store.backend,
        "credential_boundary": store.boundary(),
        "provider_verified": False,
        "repair_command": "mb connect google --oauth --reauth" if missing else "",
        "safe_to_share": True,
        "status": status,
    }


def render_result(result: dict[str, Any]) -> None:
    granted = ", ".join(GRANT_LABEL_NAMES[label] for label in result["oauth_grants"])
    print(f"Granted (read-only): {granted}")
    for label in result["missing_grants"]:
        print(
            f"Not granted: {GRANT_LABEL_NAMES[label]}. Its reads will refuse until you sign in "
            "again with `mb connect google --oauth --reauth` and tick its box."
        )
    print(f"Stored: yes ({result['credential_boundary']})")
    print(f"metadata: {result['config_path']}")
    if result.get("user_scope_path"):
        print(f"user scope: {result['user_scope_path']}")
    print("Not checked against Google yet: this release stores the sign-in only.")
    print("See it with `mb connect status google`.")
