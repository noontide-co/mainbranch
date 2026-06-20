"""``mb launch`` read-only readiness checks."""

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


def test_launch_check_reports_astro_cloudflare_resend_readiness(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("MB_CONNECT_SECRET_BACKEND", "local-file")
    monkeypatch.setenv("MAINBRANCH_HOME", str(tmp_path / "home"))
    business = tmp_path / "business"
    site = tmp_path / "norcal-style-site"
    init_run(path=str(business), name="NorCal Style")
    (site / "dist").mkdir(parents=True)
    (site / "src" / "pages" / "api").mkdir(parents=True)
    (business / "core" / "offer.md").write_text(
        (
            "---\n"
            "gtm_container_id: GTM-ABC1234\n"
            "ga4_measurement_id: G-ABC123DEF\n"
            "google_ads_customer_id: '0000000000'\n"
            "consent_posture: standard_tag_consent_reviewed\n"
            "privacy_policy_url: https://example.com/privacy\n"
            "---\n\n"
            "# Offer\n"
        ),
        encoding="utf-8",
    )
    (site / "package.json").write_text(
        json.dumps(
            {
                "scripts": {
                    "build": "astro build",
                    "deploy": "wrangler pages deploy dist",
                    "smoke:booking": "node scripts/smoke-booking.mjs",
                },
                "dependencies": {"astro": "^5.0.0", "resend": "^6.0.0"},
                "devDependencies": {"wrangler": "^4.0.0"},
            }
        ),
        encoding="utf-8",
    )
    (site / "astro.config.mjs").write_text("export default {};\n", encoding="utf-8")
    (site / "wrangler.toml").write_text('name = "site"\npages_build_output_dir = "dist"\n')
    (site / "src" / "pages" / "api" / "contact.ts").write_text(
        'import { Resend } from "resend";\nconst key = "RESEND_API_KEY";\n',
        encoding="utf-8",
    )
    _write_conversion(
        site,
        {
            "kind": "appointment_booking",
            "url": "https://calendly.com/acme/demo",
            "render": "link_out",
            "primary_conversions": ["mb_booked_call"],
        },
    )
    (site / "dist" / "index.html").write_text(
        """<!doctype html>
<html>
<head>
<script>window.dataLayer = window.dataLayer || [];</script>
<script src="https://www.googletagmanager.com/gtm.js?id=GTM-ABC1234"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ABC123DEF"></script>
<script>
window.dataLayer.push({event: "mb_calendar_click", mb_event_id: "test"});
window.dataLayer.push({event: "mb_booked_call", mb_event_id: "test"});
</script>
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-ABC1234"></iframe></noscript>
<div class="calendly-inline-widget" data-url="https://calendly.com/acme/demo"></div>
</body>
</html>
""",
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        ["launch", "check", str(site), "--business-repo", str(business), "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["state"] == "ready_for_operator_review"
    assert payload["facts"]["app_stack"]["frameworks"] == ["astro"]
    assert payload["facts"]["deploy"]["cloudflare"] is True
    assert payload["facts"]["email"]["providers"] == ["resend"]
    assert payload["facts"]["measurement"]["state"] == "ready_for_operator_review"
    assert "form-submit or booking-link smoke" in payload["recommended_action"]


def test_launch_check_detects_shopify_without_claiming_provider_automation(
    tmp_path: Path,
) -> None:
    site = tmp_path / "awake-happy-theme"
    (site / "layout").mkdir(parents=True)
    (site / "config").mkdir()
    (site / "layout" / "theme.liquid").write_text(
        '<html><body>{{ content_for_layout }}<script src="https://cdn.shopify.com/shopifycloud/storefront"></script></body></html>',
        encoding="utf-8",
    )
    (site / "config" / "settings_schema.json").write_text("[]", encoding="utf-8")

    result = runner.invoke(app, ["launch", "check", str(site), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    commerce = payload["facts"]["commerce"]
    assert commerce["platforms"] == ["shopify"]
    assert commerce["liquid_file_count"] == 1
    commerce_check = next(item for item in payload["checks"] if item["kind"] == "commerce_rail")
    assert commerce_check["state"] == "passed"
    assert "publish" not in payload["recommended_action"].lower()


def test_launch_check_blocks_missing_site_path(tmp_path: Path) -> None:
    result = runner.invoke(app, ["launch", "check", str(tmp_path / "missing"), "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["state"] == "blocked"
    assert payload["recommended_action"] == "Pass the site repo path to `mb launch check`."


def test_launch_check_human_output_names_one_next_action(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    result = runner.invoke(app, ["launch", "check", str(site)])

    assert result.exit_code == 0
    assert "mb launch check" in result.stdout
    assert "next:" in result.stdout
