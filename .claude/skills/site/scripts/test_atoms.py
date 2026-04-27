"""Atom envelope round-trip + invariant tests.

Run with: `python3 -m pytest .claude/skills/site/scripts/test_atoms.py -v`
or directly:  `python3 .claude/skills/site/scripts/test_atoms.py`

These tests exercise the schema contract — not network calls. Live integration
tests for `domain.py check` are run manually (see issue #93). Live `domain.py
buy` is deferred to the first real-project domain.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _envelope import SCHEMA_VERSION, ProviderRunMetadata, validate_status_consistency
from unittest.mock import patch

import dns as dns_module
import pages as pages_module
from dns import (
    CfResult,
    DnsEnsureData,
    DnsEnsureEnvelope,
    DnsEnsureError,
    PORKBUN_API_BASE,
    _cf_classify_error,
    _detect_registrar,
    _porkbun_update_ns,
)
from domain import (
    DomainBuyData,
    DomainBuyEnvelope,
    DomainBuyError,
    DomainCheckData,
    DomainCheckEnvelope,
    DomainCheckError,
    DomainCheckResult,
)
from pages import (
    PagesSetDomainData,
    PagesSetDomainEnvelope,
    PagesSetDomainError,
    _domain_payload_to_data,
    _map_cf_error,
    _wait_for_domain_active,
)


# ---------------------------------------------------------------------------
# DomainCheckEnvelope
# ---------------------------------------------------------------------------


def test_domain_check_ok_round_trip() -> None:
    env = DomainCheckEnvelope(
        status="ok",
        data=DomainCheckData(
            name="example",
            tlds_checked=["com", "co"],
            results=[
                DomainCheckResult(domain="example.com", available=False, method_used="bootstrap"),
                DomainCheckResult(domain="example.co", available=True, method_used="whois"),
            ],
            available=["example.co"],
        ),
        provenance={
            "domain_check": ProviderRunMetadata(
                status="ok",
                latency_ms=412,
                provider_version="domain-check",
            )
        },
    )
    payload = env.model_dump_json()
    parsed = DomainCheckEnvelope.model_validate_json(payload)
    assert parsed.status == "ok"
    assert parsed.error is None
    assert parsed.data.available == ["example.co"]
    assert parsed.schema_version == SCHEMA_VERSION


def test_domain_check_degraded_requires_error() -> None:
    with pytest.raises(ValidationError, match="status!=.ok. requires a structured error"):
        DomainCheckEnvelope(
            status="degraded",
            data=DomainCheckData(name="x", tlds_checked=[], results=[]),
        )


def test_domain_check_ok_rejects_error() -> None:
    with pytest.raises(ValidationError, match='status="ok" must not include an error'):
        DomainCheckEnvelope(
            status="ok",
            data=DomainCheckData(name="x", tlds_checked=[], results=[]),
            error=DomainCheckError(code="invalid_name", message="x"),
        )


def test_domain_check_error_code_is_closed() -> None:
    """Closed enum: only listed codes accepted."""
    with pytest.raises(ValidationError):
        DomainCheckError(code="not_a_real_code", message="x")  # type: ignore[arg-type]


def test_domain_check_extra_fields_rejected() -> None:
    """extra='forbid' on every model — schema drift is loud."""
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "ok",
        "data": {
            "name": "x",
            "tlds_checked": [],
            "results": [],
            "available": [],
            "surprise_field": "drift",
        },
        "provenance": {},
        "error": None,
    }
    with pytest.raises(ValidationError):
        DomainCheckEnvelope.model_validate(payload)


# ---------------------------------------------------------------------------
# DomainBuyEnvelope
# ---------------------------------------------------------------------------


def test_domain_buy_ok_round_trip() -> None:
    env = DomainBuyEnvelope(
        status="ok",
        data=DomainBuyData(
            domain="example.com",
            registrar="cloudflare",
            price_usd=10.45,
            purchased=True,
            already_owned=False,
            expiry="2027-04-27",
            years=1,
        ),
        provenance={
            "cloudflare_registrar": ProviderRunMetadata(
                status="ok",
                latency_ms=1845,
                provider_version="cf-registrar-beta-2026-04-15",
                cost_incurred=1045,
            )
        },
    )
    parsed = DomainBuyEnvelope.model_validate_json(env.model_dump_json())
    assert parsed.data.purchased is True
    assert parsed.data.registrar == "cloudflare"
    assert parsed.provenance["cloudflare_registrar"].cost_incurred == 1045


def test_domain_buy_already_owned_is_ok_status() -> None:
    """already_owned is a *data field*, not an error — atom is idempotent."""
    env = DomainBuyEnvelope(
        status="ok",
        data=DomainBuyData(
            domain="example.com",
            registrar="cloudflare",
            already_owned=True,
            purchased=False,
            expiry="2027-04-27",
            years=1,
        ),
    )
    assert env.error is None
    assert env.data.already_owned is True


def test_domain_buy_user_declined_is_degraded() -> None:
    env = DomainBuyEnvelope(
        status="degraded",
        data=DomainBuyData(domain="example.com", years=1),
        error=DomainBuyError(
            code="user_declined",
            message="Registration requires --yes confirmation.",
            suggestion="Re-run with --yes",
        ),
    )
    assert env.error is not None
    assert env.error.code == "user_declined"


def test_domain_buy_error_code_is_closed() -> None:
    with pytest.raises(ValidationError):
        DomainBuyError(code="something_not_in_the_enum", message="x")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# validate_status_consistency (shared)
# ---------------------------------------------------------------------------


def test_validate_status_consistency_partial_requires_error() -> None:
    with pytest.raises(ValidationError, match="status!=.ok. requires a structured error"):
        DomainCheckEnvelope(
            status="partial",
            data=DomainCheckData(name="x", tlds_checked=[], results=[]),
        )


def test_provider_run_metadata_is_frozen() -> None:
    """Provenance rows are immutable — no after-the-fact mutation."""
    pr = ProviderRunMetadata(status="ok", latency_ms=100, provider_version="v1")
    with pytest.raises(ValidationError):
        pr.latency_ms = 200  # type: ignore[misc]


# ---------------------------------------------------------------------------
# DnsEnsureEnvelope
# ---------------------------------------------------------------------------


def test_dns_ensure_ok_round_trip() -> None:
    env = DnsEnsureEnvelope(
        status="ok",
        data=DnsEnsureData(
            domain="example.com",
            zone_id="abc123",
            ns_pair=["walt.ns.cloudflare.com", "sara.ns.cloudflare.com"],
            zone_created_now=True,
            registrar="porkbun",
            ns_swap_performed=True,
            propagated=True,
            propagation_seconds=143,
        ),
        provenance={
            "cf_zone_create": ProviderRunMetadata(
                status="ok", latency_ms=512, provider_version="cloudflare-api-v4"
            ),
            "porkbun_update_ns": ProviderRunMetadata(
                status="ok", latency_ms=812, provider_version="porkbun-api-v3"
            ),
            "dns_propagation_poll": ProviderRunMetadata(
                status="ok", latency_ms=143000, provider_version="dig+1.1.1.1"
            ),
        },
    )
    parsed = DnsEnsureEnvelope.model_validate_json(env.model_dump_json())
    assert parsed.data.zone_created_now is True
    assert parsed.data.ns_swap_performed is True
    assert len(parsed.data.ns_pair) == 2
    assert parsed.data.propagation_seconds == 143


def test_dns_ensure_idempotent_no_swap() -> None:
    """Idempotent path: zone already existed, NS already correct, no work performed."""
    env = DnsEnsureEnvelope(
        status="ok",
        data=DnsEnsureData(
            domain="example.com",
            zone_id="abc123",
            ns_pair=["walt.ns.cloudflare.com", "sara.ns.cloudflare.com"],
            zone_created_now=False,
            registrar="cloudflare",
            ns_swap_performed=False,
            propagated=True,
            propagation_seconds=2,
        ),
    )
    assert env.data.zone_created_now is False
    assert env.data.ns_swap_performed is False


def test_dns_ensure_error_codes_closed() -> None:
    with pytest.raises(ValidationError):
        DnsEnsureError(code="not_a_real_dns_code", message="x")  # type: ignore[arg-type]


def test_dns_ensure_invalid_domain_envelope() -> None:
    env = DnsEnsureEnvelope(
        status="degraded",
        data=DnsEnsureData(domain="not a valid domain"),
        error=DnsEnsureError(
            code="invalid_domain",
            message="Domain doesn't look valid.",
            suggestion="Pass a registrable apex.",
        ),
    )
    assert env.error is not None
    assert env.error.code == "invalid_domain"


def test_cf_classify_zone_already_exists() -> None:
    """Code 1097 → zone_already_exists with manual-cleanup suggestion."""
    result = CfResult(ok=False, latency_ms=100, status_code=400, error_code=1097, error_message="zone exists")
    code, suggestion = _cf_classify_error(result)
    assert code == "zone_already_exists"
    assert "another Cloudflare account" in suggestion


def test_cf_classify_unauthenticated_401() -> None:
    result = CfResult(ok=False, latency_ms=50, status_code=401, error_message="bad auth")
    code, suggestion = _cf_classify_error(result)
    assert code == "cf_unauthenticated"
    assert "CLOUDFLARE_API_TOKEN" in suggestion


def test_cf_classify_unauthenticated_by_code() -> None:
    """Code 10000 (auth) → cf_unauthenticated even on http 200."""
    result = CfResult(ok=False, latency_ms=50, status_code=200, error_code=10000, error_message="invalid")
    code, _ = _cf_classify_error(result)
    assert code == "cf_unauthenticated"


def test_cf_classify_rate_limited_429() -> None:
    result = CfResult(ok=False, latency_ms=50, status_code=429, error_message="too many")
    code, suggestion = _cf_classify_error(result)
    assert code == "cf_rate_limited"
    assert "back off" in suggestion.lower()


def test_cf_classify_timeout() -> None:
    result = CfResult(ok=False, latency_ms=30000, status_code=0, error_message="timeout")
    code, _ = _cf_classify_error(result)
    assert code == "network_timeout"


def test_cf_classify_generic_failure() -> None:
    """Unrecognized failure shape → cf_request_failed (not silent ok)."""
    result = CfResult(ok=False, latency_ms=50, status_code=500, error_code=9999, error_message="boom")
    code, suggestion = _cf_classify_error(result)
    assert code == "cf_request_failed"
    assert "9999" in suggestion or "500" in suggestion


# CF auth-error code coverage — all five flavors map to cf_unauthenticated.
# (Verified against Cloudflare's published error codes: 9106/9107 legacy,
# 9109 invalid/revoked, 6003/6111 malformed Authorization header.)
@pytest.mark.parametrize(
    "http_status,cf_code",
    [
        (403, 9109),  # token format OK but invalid/revoked
        (403, 9106),  # missing X-Auth-Email (legacy auth)
        (403, 9107),  # missing X-Auth-Key (legacy auth)
        (400, 6003),  # malformed Authorization header
        (400, 6111),  # malformed Authorization header variant
    ],
)
def test_cf_classify_auth_error_codes(http_status: int, cf_code: int) -> None:
    """All five auth-error code paths map to cf_unauthenticated."""
    result = CfResult(
        ok=False,
        latency_ms=80,
        status_code=http_status,
        error_code=cf_code,
        error_message="auth_problem",
    )
    code, suggestion = _cf_classify_error(result)
    assert code == "cf_unauthenticated", f"http {http_status} + code {cf_code} → {code}"
    assert "CLOUDFLARE_API_TOKEN" in suggestion
    assert "scopes" in suggestion.lower() or "scope" in suggestion.lower()


# ---------------------------------------------------------------------------
# Porkbun host pinned (regression test for the audit-caught bug)
# ---------------------------------------------------------------------------


def test_porkbun_api_base_pinned_to_correct_host() -> None:
    """Regression: Porkbun's documented API host is api.porkbun.com (not porkbun.com).

    porkbun.com/api/json/v3/* returns HTTP 403; api.porkbun.com/api/json/v3/* works.
    Audited live before this test was written.
    """
    assert PORKBUN_API_BASE == "https://api.porkbun.com/api/json/v3"


def test_porkbun_update_ns_url_construction() -> None:
    """The actual HTTP call hits api.porkbun.com, not porkbun.com.

    Mocks `requests.post` at the dns module level and asserts the URL passed.
    Catches a future regression where someone shortens the base back to porkbun.com.
    """
    fake_response = type(
        "FakeResp",
        (),
        {
            "status_code": 200,
            "json": lambda self: {"status": "SUCCESS"},
        },
    )()

    with patch.object(dns_module.requests, "post", return_value=fake_response) as mock_post:
        ok, _, err = _porkbun_update_ns(
            "example.com",
            ["walt.ns.cloudflare.com", "sara.ns.cloudflare.com"],
            "fake_key",
            "fake_secret",
        )
        assert ok is True
        assert err is None
        called_url = mock_post.call_args.args[0] if mock_post.call_args.args else mock_post.call_args.kwargs["url"]
        assert called_url.startswith("https://api.porkbun.com/api/json/v3/"), (
            f"Porkbun URL must start with api.porkbun.com — got {called_url}"
        )
        assert "example.com" in called_url
        assert "domain/updateNs" in called_url


def test_porkbun_update_ns_failure_returns_message() -> None:
    """Porkbun status != SUCCESS surfaces the message verbatim for diagnosis."""
    fake_response = type(
        "FakeResp",
        (),
        {
            "status_code": 200,
            "json": lambda self: {"status": "ERROR", "message": "invalid api key"},
        },
    )()

    with patch.object(dns_module.requests, "post", return_value=fake_response):
        ok, _, err = _porkbun_update_ns("example.com", ["a", "b"], "k", "s")
        assert ok is False
        assert err == "invalid api key"


def test_detect_registrar_explicit_wins() -> None:
    reg, err = _detect_registrar("porkbun")
    assert reg == "porkbun"
    assert err is None


def test_detect_registrar_cf_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CLOUDFLARE_API_TOKEN_REGISTRAR", "fake")
    monkeypatch.delenv("PORKBUN_API_KEY", raising=False)
    monkeypatch.delenv("PORKBUN_SECRET_KEY", raising=False)
    reg, err = _detect_registrar(None)
    assert reg == "cloudflare"
    assert err is None


def test_detect_registrar_porkbun_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN_REGISTRAR", raising=False)
    monkeypatch.setenv("PORKBUN_API_KEY", "k")
    monkeypatch.setenv("PORKBUN_SECRET_KEY", "s")
    reg, err = _detect_registrar(None)
    assert reg == "porkbun"
    assert err is None


def test_detect_registrar_neither_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLOUDFLARE_API_TOKEN_REGISTRAR", raising=False)
    monkeypatch.delenv("PORKBUN_API_KEY", raising=False)
    monkeypatch.delenv("PORKBUN_SECRET_KEY", raising=False)
    reg, err = _detect_registrar(None)
    assert reg is None
    assert err is not None
    assert err.code == "registrar_required"


# ---------------------------------------------------------------------------
# PagesSetDomainEnvelope
# ---------------------------------------------------------------------------


def test_pages_set_domain_ok_round_trip() -> None:
    env = PagesSetDomainEnvelope(
        status="ok",
        data=PagesSetDomainData(
            project_name="thelastbill",
            domain="thelastbill.com",
            domain_id="dom_123",
            status="active",
            certificate_authority="google",
            already_attached=False,
            attached_now=True,
            ssl_active=True,
            poll_seconds=42,
            validation_status="active",
            verification_status="active",
            zone_tag="zone_123",
        ),
        provenance={
            "cf_pages_domain_add": ProviderRunMetadata(
                status="ok", latency_ms=321, provider_version="cloudflare-api-v4"
            ),
            "cf_pages_domain_poll": ProviderRunMetadata(
                status="ok", latency_ms=42000, provider_version="cloudflare-api-v4"
            ),
        },
    )
    parsed = PagesSetDomainEnvelope.model_validate_json(env.model_dump_json())
    assert parsed.status == "ok"
    assert parsed.error is None
    assert parsed.data.attached_now is True
    assert parsed.data.ssl_active is True
    assert parsed.schema_version == SCHEMA_VERSION


def test_pages_set_domain_already_attached_is_ok() -> None:
    env = PagesSetDomainEnvelope(
        status="ok",
        data=PagesSetDomainData(
            project_name="thelastbill",
            domain="thelastbill.com",
            status="active",
            already_attached=True,
            attached_now=False,
            ssl_active=True,
        ),
    )
    assert env.error is None
    assert env.data.already_attached is True
    assert env.data.attached_now is False


def test_pages_set_domain_error_codes_closed() -> None:
    with pytest.raises(ValidationError):
        PagesSetDomainError(code="not_a_real_pages_code", message="x")  # type: ignore[arg-type]


def test_pages_set_domain_degraded_requires_error() -> None:
    with pytest.raises(ValidationError, match="status!=.ok. requires a structured error"):
        PagesSetDomainEnvelope(
            status="degraded",
            data=PagesSetDomainData(project_name="x", domain="example.com"),
        )


def test_pages_set_domain_payload_to_data_extracts_statuses() -> None:
    data = _domain_payload_to_data(
        "thelastbill",
        "thelastbill.com",
        {
            "id": "dom_123",
            "name": "thelastbill.com",
            "status": "active",
            "certificate_authority": "lets_encrypt",
            "validation_data": {"status": "active"},
            "verification_data": {"status": "active"},
            "zone_tag": "zone_123",
        },
        already_attached=True,
        attached_now=False,
        poll_seconds=0,
    )
    assert data.domain_id == "dom_123"
    assert data.certificate_authority == "lets_encrypt"
    assert data.ssl_active is True
    assert data.validation_status == "active"
    assert data.verification_status == "active"


def test_pages_map_cf_error_project_not_found() -> None:
    err = _map_cf_error(
        CfResult(ok=False, latency_ms=10, status_code=404, error_message="not found"),
        project_checked=False,
    )
    assert err.code == "project_not_found"


def test_pages_map_cf_error_auth_reuses_cf_classifier() -> None:
    err = _map_cf_error(
        CfResult(ok=False, latency_ms=10, status_code=403, error_code=9109, error_message="invalid token"),
        project_checked=True,
    )
    assert err.code == "cf_unauthenticated"
    assert "CLOUDFLARE_API_TOKEN" in (err.suggestion or "")


def test_pages_map_cf_error_rate_limit_reuses_cf_classifier() -> None:
    err = _map_cf_error(
        CfResult(ok=False, latency_ms=10, status_code=429, error_message="too many"),
        project_checked=True,
    )
    assert err.code == "cf_rate_limited"


def test_pages_map_cf_error_dns_hint() -> None:
    err = _map_cf_error(
        CfResult(ok=False, latency_ms=10, status_code=400, error_message="DNS validation failed"),
        project_checked=True,
    )
    assert err.code == "dns_misconfigured"


def test_pages_wait_for_domain_active_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = [
        CfResult(
            ok=True,
            latency_ms=10,
            status_code=200,
            payload={
                "id": "dom_123",
                "status": "pending",
                "validation_data": {"status": "pending"},
                "verification_data": {"status": "pending"},
            },
        ),
        CfResult(
            ok=True,
            latency_ms=10,
            status_code=200,
            payload={
                "id": "dom_123",
                "status": "active",
                "validation_data": {"status": "active"},
                "verification_data": {"status": "active"},
            },
        ),
    ]

    def fake_cf_call(*args: object, **kwargs: object) -> CfResult:
        return calls.pop(0)

    monkeypatch.setattr(pages_module, "_cf_call", fake_cf_call)
    monkeypatch.setattr(pages_module.time, "sleep", lambda _seconds: None)
    provenance: dict[str, ProviderRunMetadata] = {}
    payload, elapsed, err = _wait_for_domain_active("acct", "proj", "example.com", "tok", 10, provenance)
    assert err is None
    assert payload is not None
    assert payload["status"] == "active"
    assert elapsed >= 0
    assert "cf_pages_domain_poll" in provenance


def test_pages_wait_for_domain_active_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    result = CfResult(
        ok=True,
        latency_ms=10,
        status_code=200,
        payload={
            "id": "dom_123",
            "status": "pending",
            "validation_data": {"status": "pending"},
            "verification_data": {"status": "pending"},
        },
    )
    monkeypatch.setattr(pages_module, "_cf_call", lambda *args, **kwargs: result)
    monkeypatch.setattr(pages_module.time, "sleep", lambda _seconds: None)

    ticks = iter([0, 2, 5])
    monkeypatch.setattr(pages_module.time, "monotonic", lambda: next(ticks))
    payload, elapsed, err = _wait_for_domain_active("acct", "proj", "example.com", "tok", 3, {})
    assert payload is not None
    assert elapsed == 5
    assert err is not None
    assert err.code == "ssl_provisioning_timeout"


def test_pages_wait_for_domain_active_error_status(monkeypatch: pytest.MonkeyPatch) -> None:
    result = CfResult(
        ok=True,
        latency_ms=10,
        status_code=200,
        payload={
            "id": "dom_123",
            "status": "error",
            "validation_data": {"status": "error", "error_message": "CNAME missing"},
            "verification_data": {"status": "pending"},
        },
    )
    monkeypatch.setattr(pages_module, "_cf_call", lambda *args, **kwargs: result)
    payload, _elapsed, err = _wait_for_domain_active("acct", "proj", "example.com", "tok", 10, {})
    assert payload is None
    assert err is not None
    assert err.code == "dns_misconfigured"
    assert "CNAME missing" in err.message


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
