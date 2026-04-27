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
from dns import (
    CfResult,
    DnsEnsureData,
    DnsEnsureEnvelope,
    DnsEnsureError,
    _cf_classify_error,
    _detect_registrar,
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


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
