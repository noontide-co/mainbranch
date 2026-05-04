"""``mb site`` paid-traffic readiness checks."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()


def _write_conversion(site: Path, payload: dict[str, object]) -> None:
    target = site / ".mainbranch" / "conversion.json"
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_html(
    site: Path, *, gtm_id: str = "GTM-ABC1234", events: list[str] | None = None
) -> None:
    event_lines = "\n".join(
        f'window.dataLayer.push({{event: "{event}", mb_event_id: "test"}});'
        for event in (events or [])
    )
    (site / "index.html").write_text(
        f"""<!doctype html>
<html>
<head>
<script>window.dataLayer = window.dataLayer || [];</script>
<script src="https://www.googletagmanager.com/gtm.js?id={gtm_id}"></script>
<script>{event_lines}</script>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm_id}"></iframe></noscript>
</body>
</html>
""",
        encoding="utf-8",
    )


def test_site_check_reports_ready_for_operator_review(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    business = tmp_path / "business"
    site = tmp_path / "site"
    init_run(path=str(business), name="Acme")
    site.mkdir()
    (business / "core" / "offer.md").write_text(
        (
            "---\n"
            "gtm_container_id: GTM-ABC1234\n"
            "google_ads_customer_id: '0000000000'\n"
            "consent_posture: standard_tag_consent_reviewed\n"
            "privacy_policy_url: https://example.com/privacy\n"
            "---\n\n"
            "# Offer\n"
        ),
        encoding="utf-8",
    )
    _write_conversion(
        site,
        {
            "kind": "lead_form",
            "url": "https://tally.so/r/example",
            "render": "link_out",
            "primary_conversions": ["mb_lead_submit"],
            "secondary_conversions": ["mb_cta_click", "mb_form_start"],
            "metadata": {"provider": "tally"},
        },
    )
    _write_html(site, events=["mb_cta_click", "mb_form_start", "mb_lead_submit"])

    result = runner.invoke(
        app,
        ["site", "check", str(site), "--business-repo", str(business), "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["state"] == "ready_for_operator_review"
    assert payload["facts"]["expected_events"] == [
        "mb_cta_click",
        "mb_form_start",
        "mb_lead_submit",
    ]
    assert payload["facts"]["provider_state"]["google"]["state"] == "not_connected"
    assert not payload["blocked"]
    assert any(item["kind"] == "operator_approval" for item in payload["manual"])


def test_site_check_uses_source_link_when_business_repo_is_omitted(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    business = tmp_path / "business"
    site = tmp_path / "site"
    init_run(path=str(business), name="Acme")
    site.mkdir()
    (business / "core" / "offer.md").write_text(
        (
            "---\n"
            "gtm_container_id: GTM-ABC1234\n"
            "google_ads_customer_id: '0000000000'\n"
            "consent_posture: standard_tag_consent_reviewed\n"
            "privacy_policy_url: https://example.com/privacy\n"
            "---\n\n"
            "# Offer\n"
        ),
        encoding="utf-8",
    )
    _write_conversion(
        site,
        {
            "kind": "lead_form",
            "url": "https://tally.so/r/example",
            "render": "link_out",
            "primary_conversions": ["mb_lead_submit"],
        },
    )
    (site / ".mainbranch" / "source.json").write_text(
        json.dumps(
            {
                "business_repo": str(business),
                "offer_path": "core/offer.md",
                "campaign_path": "campaigns/smoke.md",
            }
        ),
        encoding="utf-8",
    )
    _write_html(site, events=["mb_cta_click", "mb_form_start", "mb_lead_submit"])

    result = runner.invoke(app, ["site", "check", str(site), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["business_repo"] == str(business.resolve())
    assert payload["source"]["offer_path"] == "core/offer.md"
    assert any(item["kind"] == "site_source_link" for item in payload["evidence"])


def test_site_check_blocks_missing_gtm_noscript_event_and_consent(tmp_path: Path) -> None:
    business = tmp_path / "business"
    site = tmp_path / "site"
    init_run(path=str(business), name="Acme")
    site.mkdir()
    (business / "core" / "offer.md").write_text(
        "---\ngtm_container_id: GTM-XXXXXXX\n---\n\n# Offer\n",
        encoding="utf-8",
    )
    _write_conversion(
        site,
        {"kind": "appointment_booking", "url": "https://cal.com/example", "render": "link_out"},
    )
    (site / "index.html").write_text(
        '<script src="https://www.googletagmanager.com/gtm.js?id=GTM-XXXXXXX"></script>',
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["site", "check", str(site), "--business-repo", str(business), "--json"],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["state"] == "blocked"
    blocked_kinds = {item["kind"] for item in payload["blocked"]}
    assert "gtm_container" in blocked_kinds
    assert "static_html" in blocked_kinds
    assert "data_layer_events" in blocked_kinds
    assert "consent_privacy" in blocked_kinds


def test_status_includes_measurement_summary_when_conversion_plan_exists(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr("mb.status._which", lambda name: "")
    repo = tmp_path / "business"
    init_run(path=str(repo), name="Acme")
    (repo / "core" / "offer.md").write_text(
        (
            "---\n"
            "gtm_container_id: GTM-ABC1234\n"
            "google_ads_customer_id: '0000000000'\n"
            "consent_posture: standard_tag_consent_reviewed\n"
            "privacy_policy_url: https://example.com/privacy\n"
            "---\n\n"
            "# Offer\n"
        ),
        encoding="utf-8",
    )
    _write_conversion(
        repo,
        {
            "kind": "lead_form",
            "url": "https://tally.so/r/example",
            "render": "link_out",
            "primary_conversions": ["mb_lead_submit"],
        },
    )
    _write_html(repo, events=["mb_cta_click", "mb_form_start", "mb_lead_submit"])

    result = runner.invoke(app, ["status", str(repo), "--json", "--peek"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["measurement"]["available"] is True
    assert payload["measurement"]["state"] == "ready_for_operator_review"
    assert payload["measurement"]["facts"]["primary_conversions"] == ["mb_lead_submit"]
