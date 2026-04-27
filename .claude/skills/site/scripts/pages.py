#!/usr/bin/env python3
"""pages.py — Cloudflare Pages operations atom.

Subcommand:
    set-domain  Idempotent: attach a custom domain to an existing Cloudflare
                Pages project, then poll until the custom-domain status is active.

Invocation: `python3 pages.py set-domain <project_name> <domain>`
Output: companyctx-shape envelope JSON on stdout, logs on stderr.
Exit code: 0 on ok|partial, 1 on degraded.
"""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path
from typing import Literal
from urllib.parse import urlencode

import click
from pydantic import BaseModel, ConfigDict, Field, model_validator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _envelope import (  # noqa: E402
    SCHEMA_VERSION,
    EnvelopeStatus,
    ProviderRunMetadata,
    emit,
    log,
    validate_status_consistency,
)
from dns import CfResult, _cf_call, _cf_classify_error  # noqa: E402

_PROJECT_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,57}[a-z0-9]$")
_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$")


PagesSetDomainErrorCode = Literal[
    "invalid_project_name",
    "invalid_domain",
    "cf_account_id_missing",
    "cf_unauthenticated",
    "cf_rate_limited",
    "project_not_found",
    "domain_already_attached",
    "ssl_provisioning_timeout",
    "cf_request_failed",
    "dns_misconfigured",
    "network_timeout",
]


class PagesSetDomainError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: PagesSetDomainErrorCode
    message: str
    suggestion: str | None = None


class PagesSetDomainData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_name: str
    domain: str
    domain_id: str | None = None
    status: str | None = None
    certificate_authority: Literal["google", "lets_encrypt"] | None = None
    already_attached: bool = False
    attached_now: bool = False
    ssl_active: bool = False
    poll_seconds: int | None = None
    validation_status: str | None = None
    validation_error: str | None = None
    verification_status: str | None = None
    verification_error: str | None = None
    zone_tag: str | None = None
    pages_subdomain: str | None = None
    dns_record_id: str | None = None
    dns_record_content: str | None = None
    dns_record_created_now: bool = False


class PagesSetDomainEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["0.1.0"] = SCHEMA_VERSION
    status: EnvelopeStatus
    data: PagesSetDomainData
    provenance: dict[str, ProviderRunMetadata] = Field(default_factory=dict)
    error: PagesSetDomainError | None = None

    @model_validator(mode="after")
    def _v(self) -> PagesSetDomainEnvelope:
        return validate_status_consistency(self)  # type: ignore[return-value]


def _provider_row(result: CfResult) -> ProviderRunMetadata:
    return ProviderRunMetadata(
        status="ok" if result.ok else "failed",
        latency_ms=result.latency_ms,
        error=None if result.ok else (result.error_message or "unknown"),
        provider_version="cloudflare-api-v4",
    )


def _map_cf_error(result: CfResult, *, project_checked: bool = False) -> PagesSetDomainError:
    if result.status_code == 404 and not project_checked:
        return PagesSetDomainError(
            code="project_not_found",
            message=result.error_message or "Cloudflare Pages project not found.",
            suggestion="Create the Pages project in Cloudflare first, then re-run this atom.",
        )

    dns_hint = result.error_message or ""
    if any(term in dns_hint.lower() for term in ("dns", "cname", "zone", "validation")):
        return PagesSetDomainError(
            code="dns_misconfigured",
            message=result.error_message or "Cloudflare could not validate the custom domain.",
            suggestion="Run dns.py ensure for this apex and confirm the zone lives in the same Cloudflare account.",
        )

    code, suggestion = _cf_classify_error(result)
    if code in ("cf_unauthenticated", "cf_rate_limited", "network_timeout"):
        return PagesSetDomainError(
            code=code,  # type: ignore[arg-type]
            message=result.error_message or code,
            suggestion=suggestion,
        )
    return PagesSetDomainError(
        code="cf_request_failed",
        message=result.error_message or "Cloudflare Pages request failed.",
        suggestion=suggestion,
    )


def _domain_payload_to_data(
    project_name: str,
    domain: str,
    payload: dict,
    *,
    already_attached: bool,
    attached_now: bool,
    poll_seconds: int | None,
    pages_subdomain: str | None = None,
    dns_record_id: str | None = None,
    dns_record_content: str | None = None,
    dns_record_created_now: bool = False,
) -> PagesSetDomainData:
    validation = payload.get("validation_data") or {}
    verification = payload.get("verification_data") or {}
    status = payload.get("status")
    return PagesSetDomainData(
        project_name=project_name,
        domain=domain,
        domain_id=payload.get("id") or payload.get("domain_id"),
        status=status,
        certificate_authority=payload.get("certificate_authority"),
        already_attached=already_attached,
        attached_now=attached_now,
        ssl_active=status == "active",
        poll_seconds=poll_seconds,
        validation_status=validation.get("status"),
        validation_error=validation.get("error_message"),
        verification_status=verification.get("status"),
        verification_error=verification.get("error_message"),
        zone_tag=payload.get("zone_tag"),
        pages_subdomain=pages_subdomain,
        dns_record_id=dns_record_id,
        dns_record_content=dns_record_content,
        dns_record_created_now=dns_record_created_now,
    )


def _domain_error_message(payload: dict) -> str | None:
    validation = payload.get("validation_data") or {}
    verification = payload.get("verification_data") or {}
    return (
        validation.get("error_message")
        or verification.get("error_message")
        or payload.get("error_message")
    )


def _is_missing_domain(result: CfResult) -> bool:
    if result.status_code == 404:
        return True
    msg = (result.error_message or "").lower()
    return "not found" in msg and "domain" in msg


def _candidate_zone_names(domain: str) -> list[str]:
    labels = domain.strip(".").split(".")
    return [".".join(labels[idx:]) for idx in range(0, max(0, len(labels) - 1))]


def _lookup_zone_id(
    account_id: str,
    domain: str,
    token: str,
    provenance: dict[str, ProviderRunMetadata],
) -> tuple[str | None, PagesSetDomainError | None]:
    for zone_name in _candidate_zone_names(domain):
        query = urlencode({"name": zone_name, "account.id": account_id})
        result = _cf_call("GET", f"/zones?{query}", token)
        provenance["cf_pages_zone_lookup"] = _provider_row(result)
        if not result.ok:
            return None, _map_cf_error(result, project_checked=True)
        zones = result.payload if isinstance(result.payload, list) else []
        if zones:
            zone_id = zones[0].get("id")
            if isinstance(zone_id, str) and zone_id:
                return zone_id, None
    return None, PagesSetDomainError(
        code="dns_misconfigured",
        message=f"No Cloudflare zone found for {domain!r} in this account.",
        suggestion="Run dns.py ensure for this domain, then retry pages.py set-domain.",
    )


def _record_matches_pages(record: dict, domain: str, pages_subdomain: str) -> bool:
    return (
        record.get("type") == "CNAME"
        and str(record.get("name", "")).rstrip(".").lower() == domain
        and str(record.get("content", "")).rstrip(".").lower() == pages_subdomain
    )


def _ensure_pages_dns_record(
    account_id: str,
    domain: str,
    pages_subdomain: str,
    token: str,
    provenance: dict[str, ProviderRunMetadata],
    *,
    zone_tag: str | None,
) -> tuple[str | None, bool, PagesSetDomainError | None]:
    zone_id = zone_tag
    if not zone_id:
        zone_id, zone_err = _lookup_zone_id(account_id, domain, token, provenance)
        if zone_err is not None:
            return None, False, zone_err

    query = urlencode({"name": domain})
    lookup = _cf_call("GET", f"/zones/{zone_id}/dns_records?{query}", token)
    provenance["cf_pages_dns_record_lookup"] = _provider_row(lookup)
    if not lookup.ok:
        return None, False, _map_cf_error(lookup, project_checked=True)

    records = lookup.payload if isinstance(lookup.payload, list) else []
    for record in records:
        if _record_matches_pages(record, domain, pages_subdomain):
            record_id = record.get("id")
            return (record_id if isinstance(record_id, str) else None), False, None

    if records:
        existing = records[0]
        message = (
            f"DNS record already exists for {domain}: "
            f"{existing.get('type')} {existing.get('content')}"
        )
        return None, False, PagesSetDomainError(
            code="dns_misconfigured",
            message=message,
            suggestion=(
                f"Point {domain} at {pages_subdomain} with a proxied CNAME record, "
                "or remove the conflicting DNS record and retry."
            ),
        )

    create = _cf_call(
        "POST",
        f"/zones/{zone_id}/dns_records",
        token,
        json_body={
            "type": "CNAME",
            "name": domain,
            "content": pages_subdomain,
            "ttl": 1,
            "proxied": True,
            "comment": "Managed by mb-vip pages.py set-domain",
        },
    )
    provenance["cf_pages_dns_record_create"] = _provider_row(create)
    if not create.ok:
        return None, False, _map_cf_error(create, project_checked=True)

    payload = create.payload if isinstance(create.payload, dict) else {}
    record_id = payload.get("id")
    return (record_id if isinstance(record_id, str) else None), True, None


def _wait_for_domain_active(
    account_id: str,
    project_name: str,
    domain: str,
    token: str,
    timeout_seconds: int,
    provenance: dict[str, ProviderRunMetadata],
) -> tuple[dict | None, int, PagesSetDomainError | None]:
    start = time.monotonic()
    attempt = 0
    while True:
        attempt += 1
        result = _cf_call(
            "GET",
            f"/accounts/{account_id}/pages/projects/{project_name}/domains/{domain}",
            token,
        )
        provenance["cf_pages_domain_poll"] = _provider_row(result)
        elapsed = int(time.monotonic() - start)

        if not result.ok:
            return None, elapsed, _map_cf_error(result, project_checked=True)

        payload = result.payload if isinstance(result.payload, dict) else {}
        status = payload.get("status")
        validation_status = (payload.get("validation_data") or {}).get("status")
        verification_status = (payload.get("verification_data") or {}).get("status")

        if status == "active":
            return payload, elapsed, None

        if status in ("blocked", "error", "deactivated") or validation_status == "error" or verification_status == "error":
            message = _domain_error_message(payload) or f"Pages custom domain status is {status!r}."
            return None, elapsed, PagesSetDomainError(
                code="dns_misconfigured",
                message=message,
                suggestion="Confirm the domain is an active Cloudflare zone in this account and retry.",
            )

        if elapsed >= timeout_seconds:
            return payload, elapsed, PagesSetDomainError(
                code="ssl_provisioning_timeout",
                message=f"Pages custom domain did not become active within {timeout_seconds}s.",
                suggestion="Wait a few minutes and re-run; Cloudflare may still be provisioning the certificate.",
            )

        log(
            f"  [{elapsed:>3}s] domain status={status}, "
            f"validation={validation_status}, verification={verification_status}; waiting"
        )
        time.sleep(min(10, max(2, timeout_seconds // 30)))


@click.group()
def cli() -> None:
    """pages.py — Cloudflare Pages operations atom."""


@cli.command("set-domain")
@click.argument("project_name")
@click.argument("domain")
@click.option(
    "--account-id",
    default=None,
    help="Cloudflare account ID. Defaults to CF_ACCOUNT_ID from the environment.",
)
@click.option(
    "--timeout-seconds",
    default=180,
    show_default=True,
    type=int,
    help="Max wait for custom-domain SSL/domain status to become active.",
)
@click.option(
    "--skip-poll",
    is_flag=True,
    help="Attach the domain but skip polling for active SSL/domain status.",
)
def set_domain(
    project_name: str,
    domain: str,
    account_id: str | None,
    timeout_seconds: int,
    skip_poll: bool,
) -> None:
    """Attach DOMAIN to an existing Cloudflare Pages PROJECT_NAME."""
    project_name = project_name.strip().lower()
    domain = domain.strip().lower().rstrip(".")
    provenance: dict[str, ProviderRunMetadata] = {}

    if not _PROJECT_RE.match(project_name):
        env = PagesSetDomainEnvelope(
            status="degraded",
            data=PagesSetDomainData(project_name=project_name, domain=domain),
            error=PagesSetDomainError(
                code="invalid_project_name",
                message=f"Project name {project_name!r} is not a valid Cloudflare Pages project name.",
                suggestion="Pass the exact lowercase Pages project name, e.g. 'thelastbill'.",
            ),
        )
        sys.exit(emit(env))

    if not _DOMAIN_RE.match(domain):
        env = PagesSetDomainEnvelope(
            status="degraded",
            data=PagesSetDomainData(project_name=project_name, domain=domain),
            error=PagesSetDomainError(
                code="invalid_domain",
                message=f"Domain {domain!r} doesn't look like a valid apex or subdomain.",
                suggestion="Pass a domain like 'example.com' with no scheme or path.",
            ),
        )
        sys.exit(emit(env))

    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        env = PagesSetDomainEnvelope(
            status="degraded",
            data=PagesSetDomainData(project_name=project_name, domain=domain),
            error=PagesSetDomainError(
                code="cf_unauthenticated",
                message="CLOUDFLARE_API_TOKEN not set.",
                suggestion="Add CLOUDFLARE_API_TOKEN to ~/.config/vip/env.sh with Cloudflare Pages:Edit.",
            ),
        )
        sys.exit(emit(env))

    account_id = (account_id or os.environ.get("CF_ACCOUNT_ID") or "").strip()
    if not account_id:
        env = PagesSetDomainEnvelope(
            status="degraded",
            data=PagesSetDomainData(project_name=project_name, domain=domain),
            error=PagesSetDomainError(
                code="cf_account_id_missing",
                message="No Cloudflare account ID supplied.",
                suggestion="Pass --account-id or set CF_ACCOUNT_ID in ~/.config/vip/env.sh.",
            ),
        )
        sys.exit(emit(env))

    log(f"Looking up Cloudflare Pages project {project_name}...")
    project = _cf_call("GET", f"/accounts/{account_id}/pages/projects/{project_name}", token)
    provenance["cf_pages_project_lookup"] = _provider_row(project)
    if not project.ok:
        env = PagesSetDomainEnvelope(
            status="degraded",
            data=PagesSetDomainData(project_name=project_name, domain=domain),
            provenance=provenance,
            error=_map_cf_error(project, project_checked=False),
        )
        sys.exit(emit(env))
    project_payload = project.payload if isinstance(project.payload, dict) else {}
    pages_subdomain = project_payload.get("subdomain")
    if not isinstance(pages_subdomain, str) or not pages_subdomain:
        pages_subdomain = f"{project_name}.pages.dev"

    log(f"Checking whether {domain} is already attached...")
    existing = _cf_call(
        "GET",
        f"/accounts/{account_id}/pages/projects/{project_name}/domains/{domain}",
        token,
    )
    provenance["cf_pages_domain_lookup"] = _provider_row(existing)

    already_attached = False
    attached_now = False
    payload: dict | None = None
    dns_record_id: str | None = None
    dns_record_created_now = False

    if existing.ok:
        already_attached = True
        payload = existing.payload if isinstance(existing.payload, dict) else {}
        log(f"Domain already attached: status={payload.get('status')}")
    elif not _is_missing_domain(existing):
        env = PagesSetDomainEnvelope(
            status="degraded",
            data=PagesSetDomainData(project_name=project_name, domain=domain),
            provenance=provenance,
            error=_map_cf_error(existing, project_checked=True),
        )
        sys.exit(emit(env))
    else:
        log(f"Attaching {domain} to Pages project {project_name}...")
        add = _cf_call(
            "POST",
            f"/accounts/{account_id}/pages/projects/{project_name}/domains",
            token,
            json_body={"name": domain},
        )
        provenance["cf_pages_domain_add"] = _provider_row(add)
        if not add.ok:
            err_msg = (add.error_message or "").lower()
            if add.status_code == 409 or "already" in err_msg:
                env = PagesSetDomainEnvelope(
                    status="degraded",
                    data=PagesSetDomainData(project_name=project_name, domain=domain),
                    provenance=provenance,
                    error=PagesSetDomainError(
                        code="domain_already_attached",
                        message=add.error_message or "Domain is already attached to a Pages project.",
                        suggestion="Check the existing Pages custom-domain attachment, then re-run with that project.",
                    ),
                )
                sys.exit(emit(env))
            env = PagesSetDomainEnvelope(
                status="degraded",
                data=PagesSetDomainData(project_name=project_name, domain=domain),
                provenance=provenance,
                error=_map_cf_error(add, project_checked=True),
            )
            sys.exit(emit(env))
        attached_now = True
        payload = add.payload if isinstance(add.payload, dict) else {}

    if (payload or {}).get("status") != "active":
        log(f"Ensuring Cloudflare DNS CNAME {domain} -> {pages_subdomain}...")
        dns_record_id, dns_record_created_now, dns_err = _ensure_pages_dns_record(
            account_id,
            domain,
            pages_subdomain,
            token,
            provenance,
            zone_tag=(payload or {}).get("zone_tag"),
        )
        if dns_err is not None:
            env = PagesSetDomainEnvelope(
                status="degraded",
                data=_domain_payload_to_data(
                    project_name,
                    domain,
                    payload or {},
                    already_attached=already_attached,
                    attached_now=attached_now,
                    poll_seconds=None,
                    pages_subdomain=pages_subdomain,
                    dns_record_id=dns_record_id,
                    dns_record_content=pages_subdomain,
                    dns_record_created_now=dns_record_created_now,
                ),
                provenance=provenance,
                error=dns_err,
            )
            sys.exit(emit(env))

    poll_seconds: int | None = None
    if not skip_poll:
        log(f"Polling Pages custom-domain status for {domain} (timeout {timeout_seconds}s)...")
        payload, poll_seconds, poll_err = _wait_for_domain_active(
            account_id, project_name, domain, token, timeout_seconds, provenance
        )
        if poll_err is not None:
            env = PagesSetDomainEnvelope(
                status="degraded",
                data=_domain_payload_to_data(
                    project_name,
                    domain,
                    payload or {},
                    already_attached=already_attached,
                    attached_now=attached_now,
                    poll_seconds=poll_seconds,
                    pages_subdomain=pages_subdomain,
                    dns_record_id=dns_record_id,
                    dns_record_content=pages_subdomain if dns_record_id else None,
                    dns_record_created_now=dns_record_created_now,
                ),
                provenance=provenance,
                error=poll_err,
            )
            sys.exit(emit(env))

    data = _domain_payload_to_data(
        project_name,
        domain,
        payload or {},
        already_attached=already_attached,
        attached_now=attached_now,
        poll_seconds=poll_seconds,
        pages_subdomain=pages_subdomain,
        dns_record_id=dns_record_id,
        dns_record_content=pages_subdomain if dns_record_id else None,
        dns_record_created_now=dns_record_created_now,
    )
    env = PagesSetDomainEnvelope(status="ok", data=data, provenance=provenance)
    sys.exit(emit(env))


if __name__ == "__main__":
    cli()
