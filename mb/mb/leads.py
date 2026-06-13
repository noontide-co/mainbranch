"""Deterministic lead-eligibility grading (`mb leads grade`).

A real business we built saw its instant-form set win on raw cost-per-lead
($19) while producing 0/4 eligible leads; the lander set produced the only
real customers. Budget decisions made on raw CPL are decisions made on a lie.

This grades each lead with deterministic, judgment-free checks — a plausible
email, a valid site URL when one is expected, and a non-empty owner/qualifying
answer — and reports ELIGIBLE-lead CPL beside raw CPL so the honest metric is
the default. No business data is stored; the grader is a pure function over a
lead dict, and the CLI reads a leads JSON the operator provides.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

# Plausible-email shape; the value itself never needs to leave the caller.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Obvious non-leads — placeholder/throwaway local parts and example domains.
_FAKE_LOCALPARTS = ("test", "example", "noreply", "no-reply", "none", "asdf")
_FAKE_DOMAINS = ("example.com", "example.org", "test.com", "email.com", "domain.com")


def _email_plausible(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    email = value.strip().lower()
    if not _EMAIL_RE.match(email):
        return False
    local, _, domain = email.partition("@")
    return local not in _FAKE_LOCALPARTS and domain not in _FAKE_DOMAINS


def _url_valid(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _owner_answer_present(lead: dict[str, Any]) -> bool:
    direct = lead.get("owner_answer")
    if isinstance(direct, str) and direct.strip():
        return True
    answers = lead.get("answers")
    if isinstance(answers, dict):
        return any(isinstance(v, str) and v.strip() for v in answers.values())
    return False


def grade_lead(
    lead: dict[str, Any],
    *,
    require_url: bool = False,
    require_owner_answer: bool = True,
) -> dict[str, Any]:
    """Grade one lead. Returns eligibility + which checks failed (no PII)."""
    checks: dict[str, bool] = {"email_plausible": _email_plausible(lead.get("email"))}
    reasons: list[str] = []
    if not checks["email_plausible"]:
        reasons.append("email not plausible")

    if require_owner_answer:
        checks["owner_answer_present"] = _owner_answer_present(lead)
        if not checks["owner_answer_present"]:
            reasons.append("no owner/qualifying answer")

    if require_url:
        checks["url_valid"] = _url_valid(lead.get("site_url"))
        if not checks["url_valid"]:
            reasons.append("site URL missing or invalid")
    elif lead.get("site_url") not in (None, ""):
        # A URL was supplied but malformed — that is a real quality signal.
        checks["url_valid"] = _url_valid(lead.get("site_url"))
        if not checks["url_valid"]:
            reasons.append("site URL present but invalid")

    return {"eligible": not reasons, "reasons": reasons, "checks": checks}


def _round_cents(value: float) -> float:
    return round(value, 2)


def grade_batch(
    leads: list[dict[str, Any]],
    *,
    spend: float | int | None = None,
    require_url: bool = False,
    require_owner_answer: bool = True,
) -> dict[str, Any]:
    """Grade a batch and pair raw CPL with ELIGIBLE-lead CPL (the honest metric)."""
    verdicts = [
        grade_lead(lead, require_url=require_url, require_owner_answer=require_owner_answer)
        for lead in leads
    ]
    total = len(verdicts)
    eligible = sum(1 for v in verdicts if v["eligible"])
    ineligible = total - eligible
    reason_tally: dict[str, int] = {}
    for verdict in verdicts:
        for reason in verdict["reasons"]:
            reason_tally[reason] = reason_tally.get(reason, 0) + 1

    raw_cpl: float | None = None
    eligible_cpl: float | None = None
    if spend is not None and total:
        raw_cpl = _round_cents(float(spend) / total)
    if spend is not None and eligible:
        eligible_cpl = _round_cents(float(spend) / eligible)

    if spend is None:
        summary = f"{eligible}/{total} leads eligible"
    elif eligible == 0:
        summary = (
            f"0/{total} eligible — raw CPL {raw_cpl} hides that NO lead qualified; "
            "do not judge this source on raw CPL"
        )
    else:
        summary = (
            f"{eligible}/{total} eligible — raw CPL {raw_cpl}, ELIGIBLE CPL "
            f"{eligible_cpl} (decide budget on the eligible number)"
        )

    return {
        "ok": True,
        "total": total,
        "eligible": eligible,
        "ineligible": ineligible,
        "raw_cpl": raw_cpl,
        "eligible_cpl": eligible_cpl,
        "ineligible_reasons": reason_tally,
        "verdicts": verdicts,
        "summary": summary,
        "safe_to_share": True,
    }


def render_batch(result: dict[str, Any]) -> None:
    print(result["summary"])
    if result["ineligible_reasons"]:
        print("ineligible reasons:")
        for reason, count in sorted(result["ineligible_reasons"].items()):
            print(f"  {count:>3}  {reason}")
