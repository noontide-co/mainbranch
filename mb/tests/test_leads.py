"""`mb leads grade` — deterministic lead-eligibility grading (#889)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb import leads as leads_mod
from mb.cli import app

runner = CliRunner()


def test_grade_lead_eligible_with_email_and_answer() -> None:
    verdict = leads_mod.grade_lead({"email": "owner@acmeroofing.com", "owner_answer": "yes, owner"})
    assert verdict["eligible"] is True
    assert verdict["reasons"] == []


def test_grade_lead_rejects_implausible_and_fake_emails() -> None:
    assert leads_mod.grade_lead({"email": "not-an-email", "owner_answer": "x"})["eligible"] is False
    assert (
        leads_mod.grade_lead({"email": "test@example.com", "owner_answer": "x"})["eligible"]
        is False
    )


def test_grade_lead_requires_owner_answer_by_default() -> None:
    verdict = leads_mod.grade_lead({"email": "real@business.co"})
    assert verdict["eligible"] is False
    assert any("owner" in r for r in verdict["reasons"])
    # ...unless the caller opts out.
    relaxed = leads_mod.grade_lead({"email": "real@business.co"}, require_owner_answer=False)
    assert relaxed["eligible"] is True


def test_grade_lead_url_signal() -> None:
    # require_url makes a missing URL ineligible.
    assert (
        leads_mod.grade_lead({"email": "real@business.co", "owner_answer": "x"}, require_url=True)[
            "eligible"
        ]
        is False
    )
    # A present-but-broken URL is a quality signal even when not required.
    broken = leads_mod.grade_lead(
        {"email": "real@business.co", "owner_answer": "x", "site_url": "not a url"}
    )
    assert broken["eligible"] is False
    assert any("invalid" in r for r in broken["reasons"])
    # A valid URL passes.
    ok = leads_mod.grade_lead(
        {"email": "real@business.co", "owner_answer": "x", "site_url": "https://acme.com"}
    )
    assert ok["eligible"] is True


def test_grade_batch_pairs_raw_and_eligible_cpl() -> None:
    leads = [
        {"email": "owner@acme.co", "owner_answer": "yes"},  # eligible
        {"email": "test@example.com", "owner_answer": "yes"},  # fake email
        {"email": "no-answer@biz.co"},  # no owner answer
        {"email": "real@roofco.com", "owner_answer": "owner here"},  # eligible
    ]
    result = leads_mod.grade_batch(leads, spend=76)
    assert result["total"] == 4
    assert result["eligible"] == 2
    assert result["raw_cpl"] == 19.0  # the seductive lie
    assert result["eligible_cpl"] == 38.0  # the honest number
    assert "email not plausible" in result["ineligible_reasons"]


def test_grade_batch_zero_eligible_warns_not_silent() -> None:
    leads = [{"email": "test@example.com"}, {"email": "bad"}]
    result = leads_mod.grade_batch(leads, spend=40)
    assert result["eligible"] == 0
    assert result["eligible_cpl"] is None
    assert "no lead qualified" in result["summary"].lower()


def test_leads_grade_cli_json(tmp_path: Path) -> None:
    leads_file = tmp_path / "leads.json"
    leads_file.write_text(
        json.dumps([{"email": "owner@acme.co", "owner_answer": "yes"}]), encoding="utf-8"
    )
    result = runner.invoke(
        app, ["leads", "grade", "--file", str(leads_file), "--spend", "50", "--json"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["eligible"] == 1
    assert payload["raw_cpl"] == 50.0


def test_leads_grade_cli_rejects_non_array(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"not": "an array"}), encoding="utf-8")
    result = runner.invoke(app, ["leads", "grade", "--file", str(bad)])
    assert result.exit_code == 2


def test_grade_batch_empty_is_not_raw_cpl_none() -> None:
    result = leads_mod.grade_batch([], spend=40)
    assert result["total"] == 0
    assert result["summary"] == "no leads to grade"
    assert "None" not in result["summary"]


def test_leads_grade_cli_rejects_scalar_item(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([{"email": "a@b.co"}, "oops"]), encoding="utf-8")
    result = runner.invoke(app, ["leads", "grade", "--file", str(bad)])
    assert result.exit_code == 2
    assert "must be a JSON object" in result.stderr


def test_leads_grade_cli_rejects_negative_spend(tmp_path: Path) -> None:
    leads_file = tmp_path / "leads.json"
    leads_file.write_text(json.dumps([{"email": "a@b.co", "owner_answer": "x"}]), encoding="utf-8")
    result = runner.invoke(app, ["leads", "grade", "--file", str(leads_file), "--spend", "-10"])
    assert result.exit_code == 2
    assert "zero-or-positive" in result.stderr


def test_leads_grade_cli_rejects_non_finite_spend(tmp_path: Path) -> None:
    leads_file = tmp_path / "leads.json"
    leads_file.write_text(json.dumps([{"email": "a@b.co", "owner_answer": "x"}]), encoding="utf-8")
    for bad in ("nan", "inf"):
        result = runner.invoke(app, ["leads", "grade", "--file", str(leads_file), "--spend", bad])
        assert result.exit_code == 2, bad
        assert "finite" in result.stderr


def test_grade_batch_non_finite_spend_is_not_emitted() -> None:
    result = leads_mod.grade_batch([{"email": "a@b.co", "owner_answer": "x"}], spend=float("inf"))
    assert result["raw_cpl"] is None
    assert result["eligible_cpl"] is None
    blob = json.dumps(result)
    assert "Infinity" not in blob and "NaN" not in blob
