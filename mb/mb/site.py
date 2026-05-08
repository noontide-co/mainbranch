"""Paid-traffic site readiness checks for ``mb site``."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from mb import connect as connect_mod

CONVERSION_RELATIVE_PATH = Path(".mainbranch") / "conversion.json"
SOURCE_RELATIVE_PATH = Path(".mainbranch") / "source.json"
CHILD_REPO_RELATIVE_PATH = Path(".mainbranch") / "repo.json"
CHILD_REPO_SCHEMA = "mb.child_repo.v0"
HTML_EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".mainbranch",
    ".mb",
    ".next",
    "node_modules",
}
REUSABLE_SOURCE_DIRS = {
    "app",
    "components",
    "layouts",
    "pages",
    "src",
    "templates",
}
PLACEHOLDER_GTM_IDS = {"GTM-XXXXXXX", "GTM-XXXXXX", "GTM-PLACEHOLDER"}
GTM_ID_RE = re.compile(r"\bGTM-[A-Z0-9]{5,}\b")
GA4_ID_RE = re.compile(r"\bG-[A-Z0-9]{6,}\b")
META_PIXEL_RE = re.compile(r"\b\d{10,20}\b")

EVENTS_BY_KIND: dict[str, list[str]] = {
    "stripe_payment_page": ["mb_cta_click", "mb_purchase"],
    "payment_page": ["mb_cta_click", "mb_purchase"],
    "deposit": ["mb_cta_click", "mb_deposit"],
    "lead_form": ["mb_cta_click", "mb_form_start", "mb_lead_submit"],
    "appointment_booking": ["mb_calendar_click", "mb_booked_call"],
    "booking": ["mb_calendar_click", "mb_booked_call"],
    "email_signup": ["mb_cta_click", "mb_email_signup"],
    "custom_webhook": ["mb_cta_click", "mb_lead_submit"],
}


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return {}, "missing"
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f"invalid JSON: {exc}"
    return (parsed, "") if isinstance(parsed, dict) else ({}, "not a JSON object")


def _resolve_source_path(site_repo: Path, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = (site_repo / candidate).resolve()
    return str(candidate)


def _resolve_relative_checkout(child_repo: Path, value: Any) -> tuple[str, str]:
    if not isinstance(value, str) or not value.strip():
        return "", ""
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return "", "parent.local_checkout must be relative, not absolute"
    return str((child_repo / candidate).resolve()), ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _child_repo_descriptor(child_repo: Path) -> tuple[dict[str, Any], str]:
    descriptor, error = _read_json(child_repo / CHILD_REPO_RELATIVE_PATH)
    if error:
        return {}, error

    parent = descriptor.get("parent")
    parent_data: dict[str, Any] = parent if isinstance(parent, dict) else {}
    linked = descriptor.get("linked")
    linked_data: dict[str, Any] = linked if isinstance(linked, dict) else {}
    local_checkout, checkout_error = _resolve_relative_checkout(
        child_repo, parent_data.get("local_checkout")
    )
    if checkout_error:
        return {}, checkout_error

    schema = str(descriptor.get("schema") or "")
    if schema and schema != CHILD_REPO_SCHEMA:
        return {}, f"unsupported schema {schema!r}"

    normalized_parent = {
        "display_name": str(parent_data.get("display_name") or ""),
        "github_owner": str(parent_data.get("github_owner") or ""),
        "repo_name": str(parent_data.get("repo_name") or ""),
        "remote": str(parent_data.get("remote") or ""),
        "local_checkout": str(parent_data.get("local_checkout") or ""),
        "resolved_local_checkout": local_checkout,
    }
    normalized = {
        "schema": schema or CHILD_REPO_SCHEMA,
        "role": str(descriptor.get("role") or ""),
        "display_name": str(descriptor.get("display_name") or ""),
        "github_owner": str(descriptor.get("github_owner") or ""),
        "repo_name": str(descriptor.get("repo_name") or ""),
        "safe_purpose": str(descriptor.get("safe_purpose") or ""),
        "parent": normalized_parent,
        "linked": {
            "offers": _string_list(linked_data.get("offers")),
            "pushes": _string_list(linked_data.get("pushes")),
            "bets": _string_list(linked_data.get("bets")),
            "decisions": _string_list(linked_data.get("decisions")),
        },
        "return_to_hub_command": str(descriptor.get("return_to_hub_command") or ""),
        "safe_to_share": bool(descriptor.get("safe_to_share", True)),
    }
    return normalized, ""


def _site_source(site_repo: Path) -> tuple[dict[str, Any], str]:
    source, error = _read_json(site_repo / SOURCE_RELATIVE_PATH)
    if error:
        return {}, error
    business_repo = _resolve_source_path(site_repo, source.get("business_repo"))
    return {
        "business_repo": business_repo,
        "offer_path": str(source.get("offer_path") or ""),
        "campaign_path": str(source.get("campaign_path") or ""),
        "safe_to_share": True,
    }, ""


def _read_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        parsed = yaml.safe_load(text[3:end].strip()) or {}
    except yaml.YAMLError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _offer_paths(repo: Path) -> list[Path]:
    candidates = [
        repo / "core" / "offer.md",
        repo / "reference" / "core" / "offer.md",
    ]
    for root in (repo / "core" / "offers", repo / "reference" / "offers"):
        if root.exists():
            candidates.extend(sorted(root.glob("*/offer.md")))
    return [path for path in candidates if path.is_file()]


def _merged_offer_metadata(repo: Path | None) -> dict[str, Any]:
    if repo is None:
        return {}
    metadata: dict[str, Any] = {}
    for path in _offer_paths(repo):
        metadata.update(_read_frontmatter(path))
    return metadata


def _string_value(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)
    return ""


def _list_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def _metadata_sources(
    conversion: dict[str, Any],
    offer: dict[str, Any],
    providers: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_conversion_meta = conversion.get("metadata")
    conversion_meta: dict[str, Any] = (
        raw_conversion_meta if isinstance(raw_conversion_meta, dict) else {}
    )
    provider_metadata: dict[str, Any] = {}
    for item in providers:
        raw_metadata = item.get("metadata")
        metadata: dict[str, Any] = raw_metadata if isinstance(raw_metadata, dict) else {}
        for key, value in metadata.items():
            provider_metadata.setdefault(key, value)
    return {
        "gtm_container_id": _string_value(
            conversion.get("gtm_container_id"),
            conversion_meta.get("gtm_container_id"),
            offer.get("gtm_container_id"),
            provider_metadata.get("gtm_container_id"),
        ),
        "ga4_measurement_id": _string_value(
            conversion.get("ga4_measurement_id"),
            conversion_meta.get("ga4_measurement_id"),
            offer.get("ga4_measurement_id"),
            provider_metadata.get("ga4_measurement_id"),
        ),
        "meta_pixel_id": _string_value(
            conversion.get("meta_pixel_id"),
            conversion_meta.get("meta_pixel_id"),
            offer.get("meta_pixel_id"),
            provider_metadata.get("meta_pixel_id"),
        ),
        "google_ads_customer_id": _string_value(
            conversion.get("google_ads_customer_id"),
            conversion_meta.get("google_ads_customer_id"),
            conversion_meta.get("ads_customer_id"),
            offer.get("google_ads_customer_id"),
            offer.get("ads_customer_id"),
            provider_metadata.get("google_ads_customer_id"),
            provider_metadata.get("ads_customer_id"),
        ),
        "consent_posture": _string_value(
            conversion.get("consent_posture"),
            conversion_meta.get("consent_posture"),
            offer.get("consent_posture"),
        ),
        "privacy_policy_url": _string_value(
            conversion.get("privacy_policy_url"),
            conversion_meta.get("privacy_policy_url"),
            offer.get("privacy_policy_url"),
        ),
        "primary_conversions": _list_value(
            conversion.get("primary_conversions") or conversion_meta.get("primary_conversions")
        ),
        "secondary_conversions": _list_value(
            conversion.get("secondary_conversions") or conversion_meta.get("secondary_conversions")
        ),
        "operator_approvals": conversion.get("operator_approvals")
        if isinstance(conversion.get("operator_approvals"), dict)
        else {},
    }


def _is_placeholder_gtm(value: str) -> bool:
    return value.upper() in PLACEHOLDER_GTM_IDS or bool(re.fullmatch(r"GTM-X+", value.upper()))


def _html_files(site_repo: Path) -> list[Path]:
    files: list[Path] = []
    for path in site_repo.rglob("*.html"):
        if any(part in HTML_EXCLUDED_DIRS for part in path.relative_to(site_repo).parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def _relative(site_repo: Path, path: Path) -> str:
    try:
        return path.relative_to(site_repo).as_posix()
    except ValueError:
        return str(path)


def _read_many(paths: list[Path]) -> list[tuple[Path, str]]:
    items: list[tuple[Path, str]] = []
    for path in paths:
        try:
            items.append((path, path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return items


def _has_google_manager_url(text: str, *, script_name: str, gtm_container_id: str) -> bool:
    if not gtm_container_id:
        return False
    pattern = (
        rf"googletagmanager\.com/{re.escape(script_name)}"
        rf"\?[^\"'<>\s]*\bid={re.escape(gtm_container_id)}(?:[&#\"'<>\s]|$)"
    )
    return bool(re.search(pattern, text, flags=re.IGNORECASE))


def _check_html(
    site_repo: Path,
    *,
    gtm_container_id: str,
    expected_events: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    html_files = _html_files(site_repo)
    html_items = _read_many(html_files)
    combined = "\n".join(text for _, text in html_items)
    evidence: list[dict[str, Any]] = []
    details: dict[str, Any] = {
        "html_files": [_relative(site_repo, path) for path in html_files[:25]],
        "html_file_count": len(html_files),
        "missing_events": [],
        "reusable_template_live_gtm_ids": [],
    }

    if not html_files:
        evidence.append(
            {
                "kind": "static_html",
                "state": "blocked",
                "summary": "No built HTML files were found to inspect.",
            }
        )
        return evidence, details

    has_gtm_script = _has_google_manager_url(
        combined, script_name="gtm.js", gtm_container_id=gtm_container_id
    )
    has_gtm_noscript = _has_google_manager_url(
        combined, script_name="ns.html", gtm_container_id=gtm_container_id
    )
    has_sri = bool(
        re.search(
            r"<script[^>]+(?:googletagmanager\.com/(?:gtm|gtag)\.js)[^>]+integrity=",
            combined,
            flags=re.IGNORECASE,
        )
    )
    placeholder_ids = sorted(
        {
            match.group(0)
            for match in GTM_ID_RE.finditer(combined)
            if _is_placeholder_gtm(match.group(0))
        }
    )

    if gtm_container_id:
        if has_gtm_script and has_gtm_noscript:
            state = "passed"
            summary = "GTM loader and noscript fallback found in built HTML."
        else:
            state = "blocked"
            missing = []
            if not has_gtm_script:
                missing.append("head script")
            if not has_gtm_noscript:
                missing.append("body noscript")
            summary = f"GTM is declared, but built HTML is missing {', '.join(missing)}."
    else:
        state = "missing"
        summary = "No GTM container ID is declared for this paid-traffic check."
    evidence.append({"kind": "static_html", "state": state, "summary": summary})

    if placeholder_ids:
        evidence.append(
            {
                "kind": "static_html_placeholders",
                "state": "blocked",
                "summary": "Built HTML still contains placeholder GTM IDs.",
                "evidence": placeholder_ids[:5],
            }
        )
    if has_sri:
        evidence.append(
            {
                "kind": "gtm_loader_sri",
                "state": "blocked",
                "summary": "GTM or Google tag loader has an SRI integrity attribute.",
            }
        )

    missing_events = [event for event in expected_events if event not in combined]
    details["missing_events"] = missing_events
    if expected_events and not missing_events:
        evidence.append(
            {
                "kind": "data_layer_events",
                "state": "passed",
                "summary": "Expected Main Branch dataLayer events were found.",
                "events": expected_events,
            }
        )
    elif expected_events:
        evidence.append(
            {
                "kind": "data_layer_events",
                "state": "blocked",
                "summary": "Expected Main Branch dataLayer events are missing from built HTML.",
                "events": expected_events,
                "missing": missing_events,
            }
        )

    template_live_ids: list[str] = []
    for source_dir in REUSABLE_SOURCE_DIRS:
        root = site_repo / source_dir
        if not root.exists():
            continue
        for source_path in root.rglob("*"):
            if not source_path.is_file():
                continue
            try:
                text = source_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for match in GTM_ID_RE.finditer(text):
                value = match.group(0)
                if value == gtm_container_id and not _is_placeholder_gtm(value):
                    template_live_ids.append(_relative(site_repo, source_path))
                    break
    details["reusable_template_live_gtm_ids"] = sorted(set(template_live_ids))
    if not gtm_container_id:
        pass
    elif template_live_ids:
        evidence.append(
            {
                "kind": "template_gtm_config",
                "state": "blocked",
                "summary": "Reusable source/template files hardcode a live GTM ID.",
                "evidence": sorted(set(template_live_ids))[:10],
            }
        )
    else:
        evidence.append(
            {
                "kind": "template_gtm_config",
                "state": "passed",
                "summary": "No live GTM ID was found in reusable source/template directories.",
            }
        )
    return evidence, details


def _provider_summary(providers: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {item.get("provider"): item for item in providers}
    wanted = ["google", "cloudflare", "meta"]
    return {
        provider_id: {
            "state": str((by_id.get(provider_id) or {}).get("state") or "not_connected"),
            "connected": bool((by_id.get(provider_id) or {}).get("connected")),
            "ok": bool((by_id.get(provider_id) or {}).get("ok")),
            "summary": str((by_id.get(provider_id) or {}).get("summary") or ""),
            "repair_command": str((by_id.get(provider_id) or {}).get("repair_command") or ""),
        }
        for provider_id in wanted
    }


def _state(evidence: list[dict[str, Any]], facts: dict[str, Any]) -> str:
    if any(item["state"] == "blocked" for item in evidence):
        return "blocked"
    if not facts["gtm_container_id"] and not facts["conversion_kind"]:
        return "missing"
    ads_ready = bool(facts["google_ads_customer_id"] and facts["primary_conversions"])
    approvals = facts["operator_approvals"]
    required_approval_keys = [
        "gtm_container_reviewed",
        "conversion_actions_reviewed",
        "consent_posture_reviewed",
    ]
    approvals_ready = all(bool(approvals.get(key)) for key in required_approval_keys)
    if ads_ready and approvals_ready:
        return "ready"
    if ads_ready:
        return "ready_for_operator_review"
    return "ready_for_preview"


def check(
    site_repo: str | Path = ".",
    *,
    business_repo: str | Path | None = None,
) -> dict[str, Any]:
    """Check static paid-traffic measurement readiness without mutating providers."""

    site = Path(site_repo).resolve()
    source, source_error = _site_source(site)
    child_descriptor, child_descriptor_error = _child_repo_descriptor(site)
    raw_source_business = source.get("business_repo") if source else ""
    source_business = raw_source_business if isinstance(raw_source_business, str) else ""
    if not source_business and child_descriptor:
        parent = child_descriptor.get("parent")
        parent_data = parent if isinstance(parent, dict) else {}
        descriptor_business = parent_data.get("resolved_local_checkout")
        if isinstance(descriptor_business, str):
            source_business = descriptor_business
    explicit_business_repo = bool(business_repo)
    business_value = business_repo or source_business
    business = Path(business_value).resolve() if business_value else None
    conversion, conversion_error = _read_json(site / CONVERSION_RELATIVE_PATH)
    offer = _merged_offer_metadata(business)
    provider_status = connect_mod.status_all(business or site, include_all=True)
    providers = provider_status.get("providers") or []
    facts = _metadata_sources(conversion, offer, providers)
    conversion_kind = _string_value(conversion.get("kind"))
    if conversion_kind == "stripe_payment_page":
        payment_kind = _string_value((conversion.get("metadata") or {}).get("payment_kind"))
        if payment_kind == "deposit":
            conversion_kind = "deposit"
    expected_events = EVENTS_BY_KIND.get(
        conversion_kind, ["mb_cta_click"] if conversion_kind else []
    )
    facts.update(
        {
            "conversion_kind": conversion_kind,
            "expected_events": expected_events,
            "conversion_path": CONVERSION_RELATIVE_PATH.as_posix(),
            "provider_state": _provider_summary(providers),
        }
    )

    evidence: list[dict[str, Any]] = []
    if conversion_error:
        state = "missing" if conversion_error == "missing" else "blocked"
        evidence.append(
            {
                "kind": "conversion_plan",
                "state": state,
                "summary": f"{CONVERSION_RELATIVE_PATH.as_posix()} is {conversion_error}.",
            }
        )
    else:
        evidence.append(
            {
                "kind": "conversion_plan",
                "state": "passed",
                "summary": f"Conversion endpoint kind is {conversion_kind or 'unspecified'}.",
            }
        )
    if source_error and source_error != "missing":
        evidence.append(
            {
                "kind": "site_source_link",
                "state": "blocked",
                "summary": f"{SOURCE_RELATIVE_PATH.as_posix()} is {source_error}.",
            }
        )
    elif source:
        source_state = "passed" if source.get("business_repo") else "blocked"
        evidence.append(
            {
                "kind": "site_source_link",
                "state": source_state,
                "summary": "Site repo links back to business context."
                if source_state == "passed"
                else "Site source link is missing business_repo.",
            }
        )
    elif child_descriptor:
        parent = child_descriptor.get("parent")
        parent_data = parent if isinstance(parent, dict) else {}
        source_state = (
            "passed"
            if parent_data.get("resolved_local_checkout") or explicit_business_repo
            else "manual"
        )
        evidence.append(
            {
                "kind": "site_source_link",
                "state": source_state,
                "summary": "Site repo links back to business context through .mainbranch/repo.json."
                if source_state == "passed"
                else (
                    "Child repo descriptor names the hub; pass --business-repo "
                    "with the local hub checkout for local offer metadata."
                ),
            }
        )
    else:
        evidence.append(
            {
                "kind": "site_source_link",
                "state": "missing",
                "summary": f"{SOURCE_RELATIVE_PATH.as_posix()} is missing.",
            }
        )
    if child_descriptor_error and child_descriptor_error != "missing":
        evidence.append(
            {
                "kind": "child_repo_descriptor",
                "state": "blocked",
                "summary": f"{CHILD_REPO_RELATIVE_PATH.as_posix()} is {child_descriptor_error}.",
            }
        )
    elif child_descriptor:
        role = child_descriptor.get("role") or "unspecified"
        evidence.append(
            {
                "kind": "child_repo_descriptor",
                "state": "passed",
                "summary": f"Child repo descriptor declares role {role}.",
            }
        )

    gtm_id = str(facts["gtm_container_id"])
    if gtm_id and _is_placeholder_gtm(gtm_id):
        evidence.append(
            {
                "kind": "gtm_container",
                "state": "blocked",
                "summary": "GTM container ID is still a placeholder.",
            }
        )
    elif gtm_id:
        evidence.append(
            {
                "kind": "gtm_container",
                "state": "passed",
                "summary": "GTM container ID is declared in repo-safe metadata.",
            }
        )
    else:
        evidence.append(
            {
                "kind": "gtm_container",
                "state": "missing",
                "summary": "GTM container ID is not declared.",
            }
        )

    html_evidence, html_details = _check_html(
        site,
        gtm_container_id=gtm_id,
        expected_events=expected_events,
    )
    evidence.extend(html_evidence)

    if facts["consent_posture"] and facts["privacy_policy_url"]:
        evidence.append(
            {
                "kind": "consent_privacy",
                "state": "passed",
                "summary": "Consent posture and privacy policy URL are declared.",
            }
        )
    else:
        missing = []
        if not facts["consent_posture"]:
            missing.append("consent posture")
        if not facts["privacy_policy_url"]:
            missing.append("privacy policy URL")
        evidence.append(
            {
                "kind": "consent_privacy",
                "state": "blocked",
                "summary": f"Missing {', '.join(missing)} for paid-traffic review.",
            }
        )

    ads_missing = []
    if not facts["google_ads_customer_id"]:
        ads_missing.append("Google Ads customer ID")
    if not facts["primary_conversions"]:
        ads_missing.append("primary conversion plan")
    if ads_missing:
        evidence.append(
            {
                "kind": "google_ads_plan",
                "state": "manual",
                "summary": f"Missing {', '.join(ads_missing)} before launch review.",
            }
        )
    else:
        evidence.append(
            {
                "kind": "google_ads_plan",
                "state": "passed",
                "summary": "Google Ads customer and primary conversion plan are declared.",
            }
        )

    approval_keys = [
        "gtm_container_reviewed",
        "conversion_actions_reviewed",
        "consent_posture_reviewed",
    ]
    missing_approvals = [key for key in approval_keys if not facts["operator_approvals"].get(key)]
    if missing_approvals:
        evidence.append(
            {
                "kind": "operator_approval",
                "state": "manual",
                "summary": "Operator review approvals are not fully recorded.",
                "missing": missing_approvals,
            }
        )
    else:
        evidence.append(
            {
                "kind": "operator_approval",
                "state": "passed",
                "summary": "Required operator review approvals are recorded.",
            }
        )

    state = _state(evidence, facts)
    blocked = [item for item in evidence if item["state"] == "blocked"]
    manual = [item for item in evidence if item["state"] in {"manual", "missing"}]
    if state == "blocked":
        summary = "Paid-traffic measurement readiness is blocked by local setup gaps."
        repair = "Fix the blocked evidence items, then rerun `mb site check`."
    elif state == "ready_for_preview":
        summary = "Static instrumentation is ready for preview; provider plan or approvals remain."
        repair = (
            "Run GTM Preview/Tag Assistant, record Google Ads conversion metadata, "
            "then rerun `mb site check`."
        )
    elif state == "ready_for_operator_review":
        summary = "Measurement plan is ready for operator review before any launch."
        repair = (
            "Review GTM publication, conversion actions, consent posture, and "
            "campaign launch manually."
        )
    elif state == "ready":
        summary = "Local readiness checks passed; launch still requires explicit operator action."
        repair = ""
    else:
        summary = "No paid-traffic measurement plan was found."
        repair = "Run `/mb-site` for a paid-traffic minisite and record conversion metadata."

    return {
        "ok": state in {"ready_for_preview", "ready_for_operator_review", "ready"},
        "schema": {
            "name": "mainbranch.site_readiness",
            "version": "1.0",
        },
        "site_repo": str(site),
        "business_repo": str(business) if business else "",
        "source": source,
        "child_descriptor": child_descriptor,
        "state": state,
        "safe_to_share": True,
        "summary": summary,
        "facts": facts,
        "html": html_details,
        "evidence": evidence,
        "blocked": blocked,
        "manual": manual,
        "repair": repair,
        "repair_command": "mb site check",
        "provider_status": {
            "summary": provider_status.get("summary") or {},
            "safe_to_share": True,
        },
    }


def render_check(result: dict[str, Any]) -> None:
    """Render a concise human paid-traffic readiness report."""

    print(f"mb site check  {result['site_repo']}")
    print(f"state: {result['state']}")
    print(result["summary"])
    print("")
    print("facts:")
    facts = result["facts"]
    for key in [
        "conversion_kind",
        "gtm_container_id",
        "google_ads_customer_id",
        "primary_conversions",
        "consent_posture",
        "privacy_policy_url",
    ]:
        value = facts.get(key)
        print(f"  {key}: {value if value else '-'}")
    print("")
    print("evidence:")
    for item in result["evidence"]:
        print(f"  {item['state']:<8} {item['kind']}: {item['summary']}")
    if result.get("repair"):
        print("")
        print(f"next: {result['repair']}")
