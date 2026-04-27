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


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
