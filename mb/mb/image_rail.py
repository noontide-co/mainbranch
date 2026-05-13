"""Fixture-safe image rail smoke helpers."""

from __future__ import annotations

import base64
import importlib
import importlib.util
import os
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import yaml

DEFAULT_PUSH_SLUG = "2026-05-13-openai-image-rail-smoke"
DEFAULT_ASSET_ID = "fake-openai-image-001"
DEFAULT_PROMPT_KEY = "lost-thread-branch-map.v1"
DEFAULT_MODEL = "gpt-image-2"
DEFAULT_MODEL_SNAPSHOT = "gpt-image-2-2026-04-21"
DEFAULT_SIZE = "1024x1536"
DEFAULT_QUALITY = "medium"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_PROMPT = """\
Create a fixture-safe Facebook feed image-ad base for a fictional business
operating system called Northstar Ledger. Visualize the customer phrase
"I keep losing the thread": tangled red thread winds through scattered decision
cards, invoices, launch notes, and half-finished task lists, then resolves into
a clean branch-map made of labeled-but-unreadable cards connected to one central
archive object. Make the transformation readable in one second, with stronger
ad-like contrast than a neutral desk scene. Avoid a clean desk, split-screen
chaos/order layout, website hero composition, fake dashboard, gradient SaaS
background, and professional photoshoot look. Keep the upper-right area clean
for a later deterministic headline overlay. No rendered words, real brands,
real people, customer data, logos, screenshots, account details, or private
information.
"""
DEFAULT_CONCEPT_ID = "lost-thread-branch-map"
REFERENCE_ROLES = (
    "logo",
    "product_photo",
    "style_reference",
    "screenshot_reference",
    "background",
    "mask_source",
)
PLACEMENT_PRESETS: dict[str, dict[str, Any]] = {
    "facebook_feed_portrait_4x5": {
        "aspect_ratio": "4:5",
        "nearest_provider_size": "1024x1536",
        "recommended_generation_size": "1440x1800",
        "final_export_size": "1080x1350",
        "safe_zone": {
            "top": "10%",
            "bottom": "10%",
            "sides": "10%",
            "notes": "Keep focal point and overlay text inside conservative feed margins.",
        },
        "deterministic_overlay_expected": True,
        "source_boundary": (
            "Aspect ratio checked against public Meta guidance; pixel sizes are "
            "planning defaults. Verify current Ads Manager specs before launch."
        ),
        "validation": "Preview in Meta Ads Manager before launch.",
    },
    "facebook_feed_square_1x1": {
        "aspect_ratio": "1:1",
        "nearest_provider_size": "1024x1024",
        "recommended_generation_size": "1440x1440",
        "final_export_size": "1080x1080",
        "safe_zone": {
            "top": "10%",
            "bottom": "10%",
            "sides": "10%",
            "notes": "Keep the focal point centered for mobile feed crop.",
        },
        "deterministic_overlay_expected": True,
        "source_boundary": (
            "Planning preset for square feed/carousel-style creative. Verify current "
            "Ads Manager specs before launch."
        ),
        "validation": "Preview in Meta Ads Manager before launch.",
    },
    "facebook_story_reels_9x16": {
        "aspect_ratio": "9:16",
        "nearest_provider_size": "1024x1792",
        "recommended_generation_size": "1440x2560",
        "final_export_size": "1080x1920",
        "safe_zone": {
            "top": "14%",
            "bottom": "35%",
            "sides": "6%",
            "notes": "Keep critical content inside the center safe band.",
        },
        "deterministic_overlay_expected": True,
        "source_boundary": (
            "9:16 vertical guidance checked against public Meta Reels guidance; "
            "verify current Ads Manager specs before launch."
        ),
        "validation": "Preview Stories/Reels placements before launch.",
    },
}

SmokeState = Literal["generated", "blocked"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _logical_output(push_slug: str, asset_id: str, extension: str = "png") -> str:
    return f"mb-media://pushes/{push_slug}/images/{asset_id}.{extension}"


def _repo_relative(path: Path, repo: Path) -> str:
    return path.resolve().relative_to(repo.resolve()).as_posix()


def _media_path(repo: Path, media_root: str, push_slug: str, asset_id: str) -> Path:
    root = Path(media_root).expanduser()
    if not root.is_absolute():
        root = repo / root
    return root / "pushes" / push_slug / "images" / f"{asset_id}.png"


def _provider_blocker(generate: bool) -> tuple[str, str]:
    if not generate:
        return (
            "generation_not_approved",
            (
                "Provider generation was not requested. Re-run with --generate only after "
                "the operator approves the provider call and local credential boundary."
            ),
        )
    if not os.environ.get("OPENAI_API_KEY"):
        return (
            "missing_openai_api_key",
            (
                "OPENAI_API_KEY is not set in the local runtime. Do not paste provider "
                "keys into chat or committed repo files."
            ),
        )
    if importlib.util.find_spec("openai") is None:
        return (
            "missing_openai_package",
            "The optional openai Python package is not installed in the local runtime.",
        )
    return "", ""


def _generate_openai_image(prompt: str, *, model: str, size: str, quality: str) -> bytes:
    openai_mod: Any = importlib.import_module("openai")
    client = openai_mod.OpenAI()

    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )
    encoded = response.data[0].b64_json
    if not encoded:
        raise RuntimeError("OpenAI image response did not include b64_json output")
    return base64.b64decode(encoded)


def _png_dimensions(image_bytes: bytes) -> dict[str, int] | None:
    if len(image_bytes) < 24:
        return None
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    if image_bytes[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", image_bytes[16:24])
    return {"width": width, "height": height}


def review_concept(concept: dict[str, Any]) -> dict[str, Any]:
    """Return a structured creative review for a planned or generated concept."""

    joined = " ".join(
        str(concept.get(key, ""))
        for key in (
            "visual_job",
            "visual_metaphor",
            "composition",
            "text_overlay_plan",
            "claim_boundary",
            "prompt",
        )
    ).lower()
    source_files = concept.get("source_files")
    references = concept.get("references")
    source_bite_value = concept.get("source_bite")
    source_bite: dict[str, Any] = source_bite_value if isinstance(source_bite_value, dict) else {}
    genericness_value = concept.get("genericness_check")
    genericness: dict[str, Any] = genericness_value if isinstance(genericness_value, dict) else {}
    placement = str(concept.get("placement", ""))
    text_overlay_plan = str(concept.get("text_overlay_plan", "")).lower()
    negative_constraints = [str(item).lower() for item in concept.get("negative_constraints", [])]

    fake_ui_terms = ("real meta ui", "ads manager", "dashboard screenshot", "fake ui")
    private_terms = ("customer data", "account id", "private screenshot", "token")
    unsupported_claim_terms = (
        "guaranteed revenue",
        "guaranteed profit",
        "meta partnership",
        "before/after income",
    )
    negative_text = " ".join(negative_constraints)

    fake_ui_risk = (
        "fail"
        if any(term in joined for term in fake_ui_terms)
        and not any(
            "no real meta ui" in item or "avoid fake ui" in item for item in negative_constraints
        )
        else "pass"
    )
    unsafe_private_data = False
    for term in private_terms:
        if term not in joined:
            continue
        if f"no {term}" in negative_text:
            continue
        if "do not include" in joined and term in joined:
            continue
        unsafe_private_data = True
    private_data_risk = "fail" if unsafe_private_data else "pass"
    unsupported_claim = False
    for term in unsupported_claim_terms:
        if term not in joined:
            continue
        if f"do not imply {term}" in joined or f"do not promise {term}" in joined:
            continue
        if "do not imply" in joined and term in joined:
            continue
        if "do not promise" in joined and term in joined:
            continue
        if f"no {term}" in negative_text:
            continue
        unsupported_claim = True
    claim_safety = "fail" if unsupported_claim else "pass"
    readability = (
        "warning"
        if "text-in-image" in text_overlay_plan or "render text" in joined or "tiny text" in joined
        else "pass"
    )
    placement_fit = "pass" if placement in PLACEMENT_PRESETS else "warning"
    brand_fit = "pass" if source_files else "warning"
    visual_hook_strength = "pass" if concept.get("visual_metaphor") else "warning"
    one_second_clarity = "pass" if concept.get("visual_job") else "warning"
    ad_usefulness = "pass" if concept.get("audience_state") else "warning"
    avoidance_strategy_fit = _avoidance_strategy_fit(concept)
    avoidance_check = _avoidance_check(joined, concept)
    avoidance_risk = _avoidance_risk(avoidance_check)
    prompt_record_complete = (
        "pass" if concept.get("prompt_key") and concept.get("prompt") else "fail"
    )
    reference_copy_risk = _reference_copy_risk(concept)
    export_readiness = (
        "pass" if placement in PLACEMENT_PRESETS and concept.get("text_overlay_plan") else "warning"
    )
    source_bite_fit = (
        "pass"
        if source_bite.get("source_file")
        and source_bite.get("extracted_phrase")
        and source_bite.get("visual_translation")
        else "fail"
    )
    specific_to_offer = genericness.get("specific_to_this_offer")
    genericness_risk = (
        "pass" if isinstance(specific_to_offer, int) and specific_to_offer >= 4 else "fail"
    )
    ai_generic_risk = "warning" if not references and "generic ai art" in joined else "pass"

    checks = {
        "one_second_clarity": one_second_clarity,
        "visual_hook_strength": visual_hook_strength,
        "ad_usefulness": ad_usefulness,
        "source_bite_fit": source_bite_fit,
        "genericness_risk": genericness_risk,
        "avoidance_strategy_fit": avoidance_strategy_fit,
        "avoidance_risk": avoidance_risk,
        "prompt_record_complete": prompt_record_complete,
        "reference_copy_risk": reference_copy_risk,
        "export_readiness": export_readiness,
        "readability": readability,
        "placement_fit": placement_fit,
        "brand_fit": brand_fit,
        "claim_safety": claim_safety,
        "fake_ui_risk": fake_ui_risk,
        "policy_risk": "pass" if claim_safety == "pass" else "fail",
        "private_data_risk": private_data_risk,
        "ai_generic_risk": ai_generic_risk,
    }
    notes = []
    if fake_ui_risk == "fail":
        notes.append("Remove dashboard or Ads Manager UI cues before generation.")
    if readability == "warning":
        notes.append("Prefer a text-free base image and deterministic overlay later.")
    if brand_fit == "warning":
        notes.append("Add source files or references before approving generation.")
    if placement_fit == "warning":
        notes.append("Use one of the supported Facebook placement presets.")
    if claim_safety == "fail":
        notes.append("Remove unsupported revenue, partnership, or before/after claims.")
    if private_data_risk == "fail":
        notes.append("Remove private data, account identifiers, and screenshots.")
    if source_bite_fit == "fail":
        notes.append("Add a source_bite before turning the concept into a prompt.")
    if genericness_risk == "fail":
        notes.append("Do not generate unless the concept is specific to this offer.")
    if avoidance_strategy_fit == "fail":
        notes.append("Add an avoidance_strategy with soft-avoid rules before generation.")
    if avoidance_risk != "pass":
        notes.append("Revise the concept against the avoidance_check before generation.")
    if prompt_record_complete == "fail":
        notes.append("Record prompt_key and prompt before provider generation.")
    if reference_copy_risk != "pass":
        notes.append("Reference traits must say what to borrow and what not to copy.")
    if export_readiness != "pass":
        notes.append("Add placement and post-processing expectations before export.")

    scores = {
        "one_second_clarity": _review_score(one_second_clarity),
        "visual_hook_strength": _review_score(visual_hook_strength),
        "specificity": _review_score(ad_usefulness),
        "brand_fit": _review_score(brand_fit),
        "source_bite_fit": _review_score(source_bite_fit),
        "specific_to_this_offer": (specific_to_offer if isinstance(specific_to_offer, int) else 1),
        "native_feed_fit": avoidance_check["native_feed_fit"],
        "export_readiness": _review_score(export_readiness),
        "ai_generic_risk": _review_score(ai_generic_risk, risk=True),
    }

    status = "accepted"
    if "fail" in checks.values():
        status = "rejected"
    elif "warning" in checks.values():
        status = "needs_revision"
    decision = {
        "accepted": "accept",
        "needs_revision": "revise",
        "rejected": "reject",
    }[status]

    return {
        "status": status,
        "decision": decision,
        **checks,
        "avoidance_check": avoidance_check,
        "scores": scores,
        "notes": notes,
    }


def _avoidance_strategy_fit(concept: dict[str, Any]) -> str:
    strategy = concept.get("avoidance_strategy")
    if not isinstance(strategy, dict):
        return "fail"
    avoids = strategy.get("avoids")
    if isinstance(avoids, list) and avoids and strategy.get("reason"):
        return "pass"
    return "fail"


def _avoidance_check(joined: str, concept: dict[str, Any]) -> dict[str, Any]:
    strategy = concept.get("avoidance_strategy")
    intentionally_uses = []
    if isinstance(strategy, dict) and isinstance(strategy.get("intentionally_uses"), list):
        intentionally_uses = [str(item).lower() for item in strategy["intentionally_uses"]]

    def intentional(*terms: str) -> bool:
        return any(any(term in item for term in terms) for item in intentionally_uses)

    def soft_check(*terms: str) -> str:
        matched = False
        for term in terms:
            index = joined.find(term)
            if index == -1:
                continue
            previous = joined[max(0, index - 220) : index]
            if "avoid" in previous or "no " in previous or "not " in previous:
                continue
            matched = True
        if not matched:
            return "pass"
        return "pass" if intentional(*terms) else "warning"

    stock_photo_risk = soft_check(
        "stock photo",
        "professional photoshoot",
        "business people",
        "modern office",
    )
    website_hero_risk = soft_check(
        "website hero",
        "gradient background",
        "empty wall",
        "centered product",
    )
    clean_desk_cliche_risk = soft_check(
        "clean desk",
        "coffee",
        "notebook",
        "plant",
        "productivity desk",
    )
    generic_saas_risk = soft_check(
        "saas gradient",
        "hologram dashboard",
        "glossy 3d icon",
        "growth chart",
        "fake dashboard",
    )
    ai_slop_risk = "warning" if "generic ai art" in joined else "pass"
    overpolished_risk = soft_check(
        "high-end commercial",
        "premium luxury",
        "modern minimalist",
        "cinematic lighting",
        "professional photoshoot",
    )

    warnings = [
        stock_photo_risk,
        website_hero_risk,
        clean_desk_cliche_risk,
        generic_saas_risk,
        ai_slop_risk,
        overpolished_risk,
    ].count("warning")
    native_feed_fit = max(1, 5 - warnings)
    too_safe_to_stop_scroll = "warning" if native_feed_fit < 4 else "pass"
    notes = []
    if stock_photo_risk != "pass":
        notes.append("Avoid stock-photo business imagery unless intentionally justified.")
    if website_hero_risk != "pass":
        notes.append("Avoid website-hero composition for feed creative.")
    if clean_desk_cliche_risk != "pass":
        notes.append("Replace clean desk productivity cliches with a source-bite metaphor.")
    if generic_saas_risk != "pass":
        notes.append("Avoid generic SaaS gradients, fake dashboards, and growth-chart tropes.")
    if ai_slop_risk != "pass":
        notes.append("Add source specificity and real-world texture before generation.")
    if overpolished_risk != "pass":
        notes.append("Avoid overpolished prompt language unless the brand requires it.")
    if too_safe_to_stop_scroll != "pass":
        notes.append("The concept is likely too safe to stop the scroll.")

    return {
        "stock_photo_risk": stock_photo_risk,
        "website_hero_risk": website_hero_risk,
        "clean_desk_cliche_risk": clean_desk_cliche_risk,
        "generic_saas_risk": generic_saas_risk,
        "ai_slop_risk": ai_slop_risk,
        "overpolished_risk": overpolished_risk,
        "native_feed_fit": native_feed_fit,
        "too_safe_to_stop_scroll": too_safe_to_stop_scroll,
        "notes": notes,
    }


def _avoidance_risk(avoidance_check: dict[str, Any]) -> str:
    values = [
        value
        for key, value in avoidance_check.items()
        if key.endswith("_risk") or key == "too_safe_to_stop_scroll"
    ]
    if "fail" in values:
        return "fail"
    if "warning" in values:
        return "warning"
    return "pass"


def _reference_copy_risk(concept: dict[str, Any]) -> str:
    references = concept.get("references")
    if not references:
        return "pass"
    if not isinstance(references, list):
        return "warning"
    for reference in references:
        if not isinstance(reference, dict):
            return "warning"
        if not reference.get("use_for") or not reference.get("do_not_copy"):
            return "warning"
    return "pass"


def _review_score(value: str, *, risk: bool = False) -> int:
    if value == "pass":
        return 5 if not risk else 1
    if value == "warning":
        return 3
    return 1 if not risk else 5


def fixture_facebook_image_concepts(push_slug: str) -> list[dict[str, Any]]:
    """Build reviewable fixture concepts for the smoke image index."""

    common_sources = [
        "core/offer.md",
        "core/audience.md",
        "core/proof/testimonials.md",
        "core/brand/visual-style.md",
        "research/customer-language.md",
        f"pushes/{push_slug}/push.md",
    ]
    concepts: list[dict[str, Any]] = [
        {
            "concept_id": DEFAULT_CONCEPT_ID,
            "status": "planned",
            "prompt_key": DEFAULT_PROMPT_KEY,
            "creative_playbook": {
                "id": "technical-founder",
                "status": "suggested",
                "use_when": [
                    "audience speaks in systems, workflows, and operating clarity",
                    "offer promise is about memory, process, or context continuity",
                ],
                "default_avoid": [
                    "generic SaaS gradient",
                    "fake dashboard",
                    "hologram UI",
                    "robot assistant",
                ],
                "useful_metaphors": [
                    "dependency graph",
                    "broken pipeline",
                    "incident board",
                    "branch map",
                    "lost thread",
                ],
                "risky_metaphors": [
                    "glowing brain",
                    "robot assistant",
                    "generic command center",
                ],
                "prompt_bias": [
                    "tactile systems",
                    "real artifacts",
                    "visible consequence",
                    "source-bite metaphor",
                ],
            },
            "prompt_strategy": "creative_director_brief_first_no_text_base",
            "prompt_strategy_notes": (
                "Default production path: brief the visual job first, generate "
                "a text-free base image, then apply deterministic overlay later."
            ),
            "viewer_scroll_context": "cold Facebook feed",
            "source_bite": {
                "source_file": "research/customer-language.md",
                "source_type": "customer_language",
                "extracted_phrase": "I keep losing the thread",
                "insight": (
                    "The pain is not generic clutter; the operator loses continuity "
                    "when decisions and tasks scatter across tools."
                ),
                "visual_translation": (
                    "tangled red thread becoming a clean branch map connected to "
                    "one durable business archive"
                ),
            },
            "genericness_check": {
                "could_fit_notion": False,
                "could_fit_asana": False,
                "could_fit_quickbooks": False,
                "could_fit_generic_coaching_offer": False,
                "could_fit_generic_productivity_app": False,
                "could_fit_any_coaching_offer": False,
                "could_fit_accounting_software": False,
                "specific_to_this_offer": 5,
                "reason": (
                    "The thread, branch-map, and archive metaphor expresses the "
                    "repo-backed business memory promise."
                ),
            },
            "avoidance_strategy": {
                "avoids": [
                    "stock-photo business imagery",
                    "clean desk productivity cliché",
                    "split-screen chaos/order cliché",
                    "website hero composition",
                    "fake dashboard",
                    "generic SaaS gradient",
                ],
                "intentionally_uses": [],
                "reason": (
                    "Uses a customer-language source-bite metaphor instead of "
                    "generic productivity imagery."
                ),
            },
            "first_second_read": "lost business thread becomes one durable branch map",
            "audience_state": "operator is resuming work after context switching across tools",
            "visual_job": (
                "make continuity loss visible before showing the repo-backed memory fix"
            ),
            "visual_metaphor": ("tangled red thread resolving into a clean branch map and archive"),
            "composition": (
                "feed-native tactile maze of red thread and scattered cards, with one "
                "clear branch path emerging toward a central archive and upper-right "
                "overlay space"
            ),
            "visual_hierarchy": {
                "primary_focal_point": "red thread becoming a branch map",
                "secondary_focal_point": "central archive object",
                "text_zone": "upper right",
            },
            "camera_language": "slight top-down editorial ad composition",
            "style_strength": "specific metaphor, restrained production polish",
            "emotional_tone": "relief after broken continuity",
            "placement": "facebook_feed_portrait_4x5",
            "placement_details": PLACEMENT_PRESETS["facebook_feed_portrait_4x5"],
            "text_overlay_plan": "text-free base image; deterministic overlay later, max 4 words",
            "source_files": common_sources,
            "claim_boundary": (
                "do not imply automatic decisions, guaranteed outcomes, or provider partnership"
            ),
            "references": [],
            "reference_trait_extraction": [],
            "prompt": DEFAULT_PROMPT.strip(),
            "negative_constraints": [
                "no real Meta UI",
                "no real logos",
                "no rendered words",
                "no revenue screenshots",
                "no automatic outcome claim",
                "no customer data",
            ],
        },
        {
            "concept_id": "operator-before-after-chaos",
            "status": "planned",
            "prompt_key": "durable-memory-archive-map.v1",
            "prompt_strategy": "reference_aware_no_text_base",
            "prompt_strategy_notes": (
                "Use the style reference for mood and composition only; do not "
                "copy subjects, logos, text, or private details."
            ),
            "viewer_scroll_context": "mobile feed between founder and SaaS posts",
            "source_bite": {
                "source_file": "core/offer.md",
                "source_type": "offer",
                "extracted_phrase": "the business repo is durable business memory",
                "insight": ("The offer is not another dashboard; it is memory the operator owns."),
                "visual_translation": (
                    "a private archive object quietly connecting decisions, goals, "
                    "pushes, and proof cards"
                ),
            },
            "genericness_check": {
                "could_fit_notion": False,
                "could_fit_asana": False,
                "could_fit_quickbooks": False,
                "could_fit_generic_coaching_offer": False,
                "could_fit_generic_productivity_app": False,
                "could_fit_any_coaching_offer": False,
                "could_fit_accounting_software": False,
                "specific_to_this_offer": 5,
                "reason": (
                    "The repo/archive memory metaphor is specific to Main Branch's "
                    "durable business-memory promise."
                ),
            },
            "avoidance_strategy": {
                "avoids": [
                    "fake dashboard",
                    "generic SaaS gradient",
                    "hologram dashboard",
                    "glossy 3D icons",
                    "website hero composition",
                ],
                "intentionally_uses": [],
                "reason": "Uses a repo/archive metaphor instead of dashboard or SaaS tropes.",
            },
            "first_second_read": "scattered business facts snap into a simple map",
            "audience_state": "operator has business facts scattered across docs and dashboards",
            "visual_job": "make scattered operating memory feel visible and organized",
            "visual_metaphor": "paper fragments forming a simple business map on a wall",
            "composition": "square crop, centered map, clear negative space around the focal point",
            "visual_hierarchy": {
                "primary_focal_point": "simple business map",
                "secondary_focal_point": "paper fragments",
                "text_zone": "top third",
            },
            "camera_language": "straight-on editorial wall composition",
            "style_strength": "clean but still native to the feed",
            "emotional_tone": "control without hype",
            "placement": "facebook_feed_square_1x1",
            "placement_details": PLACEMENT_PRESETS["facebook_feed_square_1x1"],
            "text_overlay_plan": "no rendered text; reserve top third for overlay",
            "source_files": common_sources,
            "claim_boundary": "do not promise automatic growth or financial outcomes",
            "references": [
                {
                    "id": "style-001",
                    "role": "style_reference",
                    "path": "mb-media://references/style-001.png",
                    "safe_to_share": False,
                    "approval_required": True,
                    "privacy_level": "private",
                    "use_for": "color mood and simple composition",
                    "do_not_copy": "exact subject, logos, text, or private details",
                }
            ],
            "reference_trait_extraction": [
                {
                    "reference_id": "style-001",
                    "traits": {
                        "palette": "muted warm neutrals with one grounded accent",
                        "composition": "simple focal object with visible surrounding context",
                        "lighting": "natural, tactile, not glossy studio light",
                    },
                    "do_not_copy": "exact subject, text, logos, layout, or private details",
                }
            ],
            "prompt": (
                "Create a fixture-safe square Facebook ad base image for a "
                "fictional business operating system. Show scattered paper "
                "fragments forming a clean business map. No text, logos, "
                "screenshots, private data, or real brands."
            ),
            "negative_constraints": [
                "no real logos",
                "no rendered words",
                "no private screenshots",
                "no guaranteed outcome claim",
            ],
        },
        {
            "concept_id": "mobile-safe-progress-path",
            "status": "planned",
            "prompt_key": "mobile-safe-progress-path.v1",
            "prompt_strategy": "creative_director_brief_first_no_text_base",
            "prompt_strategy_notes": (
                "Plan the vertical composition and text-safe zone before any provider call."
            ),
            "viewer_scroll_context": "story or reels vertical placement",
            "source_bite": {
                "source_file": f"pushes/{push_slug}/push.md",
                "source_type": "push_brief",
                "extracted_phrase": "what is the next practical move?",
                "insight": (
                    "The operator wants the system to preserve enough context to make "
                    "the next action obvious."
                ),
                "visual_translation": (
                    "one lit checkpoint emerging from launch notes while the rest of "
                    "the clutter stays out of the safe zone"
                ),
            },
            "genericness_check": {
                "could_fit_notion": False,
                "could_fit_asana": False,
                "could_fit_quickbooks": False,
                "could_fit_generic_coaching_offer": True,
                "could_fit_generic_productivity_app": False,
                "could_fit_any_coaching_offer": True,
                "could_fit_accounting_software": False,
                "specific_to_this_offer": 4,
                "reason": (
                    "The checkpoint is broad, but the launch notes and preserved context "
                    "keep it tied to the Main Branch operator loop."
                ),
            },
            "avoidance_strategy": {
                "avoids": [
                    "centered product on white background",
                    "generic growth chart",
                    "website hero composition",
                    "overly cinematic lighting",
                    "fake dashboard",
                ],
                "intentionally_uses": [],
                "reason": "Keeps the story placement focused on a concrete next-step metaphor.",
            },
            "first_second_read": "one practical next step appears inside launch clutter",
            "audience_state": "solo operator wants the next practical move from a messy launch",
            "visual_job": "make the next step feel obvious on a phone screen",
            "visual_metaphor": (
                "a narrow lit path through launch notes toward one marked checkpoint"
            ),
            "composition": "vertical story crop, focal path inside center 1:1 safe zone",
            "visual_hierarchy": {
                "primary_focal_point": "lit path and checkpoint",
                "secondary_focal_point": "launch notes",
                "text_zone": "above center",
            },
            "camera_language": "vertical mobile-first scene with centered subject",
            "style_strength": "specific scene, low gloss",
            "emotional_tone": "focused momentum",
            "placement": "facebook_story_reels_9x16",
            "placement_details": PLACEMENT_PRESETS["facebook_story_reels_9x16"],
            "text_overlay_plan": "text-free base image; overlay after export above center",
            "source_files": common_sources,
            "claim_boundary": "do not imply the software launches or spends money automatically",
            "references": [],
            "reference_trait_extraction": [],
            "prompt": (
                "Create a vertical 9:16 Facebook story ad base image for a "
                "fictional business planning tool. A narrow lit path moves "
                "through launch notes toward one simple checkpoint. Keep all "
                "critical detail in the center safe zone. No text, UI, logos, "
                "screenshots, account data, or private details."
            ),
            "negative_constraints": [
                "no platform UI",
                "no logos",
                "no tiny text",
                "no account data",
                "no unsupported automation claim",
            ],
        },
    ]
    for concept in concepts:
        concept["review"] = review_concept(concept)
    return concepts


def _selected_source_bites(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bites = []
    for concept in concepts:
        source_bite = concept.get("source_bite")
        if not isinstance(source_bite, dict):
            continue
        bites.append(
            {
                "concept_id": concept.get("concept_id"),
                "source_file": source_bite.get("source_file"),
                "source_type": source_bite.get("source_type"),
                "extracted_phrase": source_bite.get("extracted_phrase"),
                "visual_translation": source_bite.get("visual_translation"),
            }
        )
    return bites


def _post_processing_plan() -> dict[str, Any]:
    return {
        "status": "planned_not_implemented",
        "resize_target": PLACEMENT_PRESETS["facebook_feed_portrait_4x5"]["final_export_size"],
        "overlay_expected": True,
        "overlay_method": "future_deterministic_overlay_step",
        "export_format": "png_source_then_jpeg_or_png_final",
        "compression_target": "future_export_step",
        "validation": "Preview in Meta Ads Manager before launch.",
    }


def _asset_record(
    *,
    push_slug: str,
    asset_id: str,
    concept_id: str,
    docs_checked: str,
    generated_at: str,
    state: SmokeState,
    blocker_code: str,
    blocker: str,
    credential_state: str,
    output_reference: str,
    prompt: str,
    prompt_key: str,
    model: str,
    size: str,
    quality: str,
    generated_dimensions: dict[str, int] | None,
) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "concept_id": concept_id,
        "rail": "provider",
        "provider": "openai",
        "model": model,
        "model_snapshot": DEFAULT_MODEL_SNAPSHOT,
        "endpoint": "v1/images/generations",
        "docs_checked": docs_checked,
        "state": state,
        "blocker_code": blocker_code or None,
        "blocker": blocker or None,
        "credential_ref": "openai:image-generation",
        "credential_state": credential_state,
        "prompt_key": prompt_key,
        "prompt": prompt.strip(),
        "source_context": [
            {
                "path": f"pushes/{push_slug}/image-index.md",
                "role": "fake_push_context",
                "safe_to_share": True,
            },
            {
                "path": "fixture:fictional-northstar-ledger",
                "role": "source_brief",
                "safe_to_share": True,
            },
        ],
        "references": [],
        "dimensions": {
            "requested_size": size,
            "requested_aspect_ratio": "2:3",
            "placement": "facebook_feed_portrait_4x5",
            "placement_aspect_ratio": PLACEMENT_PRESETS["facebook_feed_portrait_4x5"][
                "aspect_ratio"
            ],
            "nearest_provider_size": PLACEMENT_PRESETS["facebook_feed_portrait_4x5"][
                "nearest_provider_size"
            ],
            "final_export_size": PLACEMENT_PRESETS["facebook_feed_portrait_4x5"][
                "final_export_size"
            ],
            "format": "png",
            "quality": quality,
            "generated_width": (
                generated_dimensions["width"] if generated_dimensions is not None else None
            ),
            "generated_height": (
                generated_dimensions["height"] if generated_dimensions is not None else None
            ),
        },
        "output_reference": output_reference,
        "storage_backend": "mb-media",
        "committed_binary": False,
        "retries": 0,
        "timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
        "cost": {
            "estimate": "unknown_token_metered",
            "actual": "unknown",
            "usage": None,
        },
        "review_status": "unreviewed",
        "safe_to_share": True,
        "generated_at": generated_at,
        "operator_notes": (
            "Fixture-safe OpenAI image rail smoke. Commit this record only; keep any "
            "generated binary in configured private media storage."
        ),
    }


def _render_index(record: dict[str, Any]) -> str:
    yaml_text = yaml.safe_dump(record, sort_keys=False, allow_unicode=False)
    return (
        "# Image Index - OpenAI Image Rail Smoke\n\n"
        "This fixture-safe record proves the first narrow OpenAI image rail "
        "with reviewable Facebook image-ad concepts, safe logical media "
        "references, and no generated binaries, secrets, private paths, or "
        "provider request credentials committed.\n\n"
        "```yaml\n"
        f"{yaml_text}"
        "```\n"
    )


def smoke_openai(
    *,
    repo: str,
    push_slug: str = DEFAULT_PUSH_SLUG,
    docs_checked: str,
    media_root: str = ".mb/media",
    generate: bool = False,
) -> dict[str, Any]:
    """Run or block the narrow OpenAI image rail smoke and write an asset record."""

    repo_path = Path(repo).resolve()
    push_dir = repo_path / "pushes" / push_slug
    push_dir.mkdir(parents=True, exist_ok=True)

    index_path = push_dir / "image-index.md"
    generated_at = _utc_now()
    output_reference = _logical_output(push_slug, DEFAULT_ASSET_ID)

    blocker_code, blocker = _provider_blocker(generate)
    credential_state = "configured_env" if os.environ.get("OPENAI_API_KEY") else "missing_env"
    state: SmokeState = "blocked" if blocker_code else "generated"

    binary_written = False
    generated_dimensions: dict[str, int] | None = None
    if state == "generated":
        out_path = _media_path(repo_path, media_root, push_slug, DEFAULT_ASSET_ID)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            image_bytes = _generate_openai_image(
                DEFAULT_PROMPT,
                model=DEFAULT_MODEL,
                size=DEFAULT_SIZE,
                quality=DEFAULT_QUALITY,
            )
        except Exception as exc:  # noqa: BLE001 - provider errors must become sanitized records.
            state = "blocked"
            blocker_code = "provider_request_failed"
            blocker = (
                f"OpenAI image generation failed before a usable image was written "
                f"({exc.__class__.__name__}). Check the local provider account, "
                f"organization verification, quota, model access, and network state."
            )
        else:
            generated_dimensions = _png_dimensions(image_bytes)
            out_path.write_bytes(image_bytes)
            binary_written = True

    concepts = fixture_facebook_image_concepts(push_slug)
    record = {
        "schema": "mainbranch.image_index.v0",
        "push_slug": push_slug,
        "docs_checked": docs_checked,
        "output_record_written": True,
        "binary_committed": False,
        "placement_presets": PLACEMENT_PRESETS,
        "reference_roles": list(REFERENCE_ROLES),
        "selected_source_bites": _selected_source_bites(concepts),
        "post_processing_plan": _post_processing_plan(),
        "concepts": concepts,
        "assets": [
            _asset_record(
                push_slug=push_slug,
                asset_id=DEFAULT_ASSET_ID,
                concept_id=DEFAULT_CONCEPT_ID,
                docs_checked=docs_checked,
                generated_at=generated_at,
                state=state,
                blocker_code=blocker_code,
                blocker=blocker,
                credential_state=credential_state,
                output_reference=output_reference,
                prompt=DEFAULT_PROMPT,
                prompt_key=DEFAULT_PROMPT_KEY,
                model=DEFAULT_MODEL,
                size=DEFAULT_SIZE,
                quality=DEFAULT_QUALITY,
                generated_dimensions=generated_dimensions,
            )
        ],
    }
    index_path.write_text(_render_index(record), encoding="utf-8")

    return {
        "ok": True,
        "provider": "openai",
        "model": DEFAULT_MODEL,
        "state": state,
        "blocker_code": blocker_code or None,
        "output_record_written": True,
        "record_path": _repo_relative(index_path, repo_path),
        "output_reference": output_reference,
        "storage_backend": "mb-media",
        "dimensions": {
            "requested_size": DEFAULT_SIZE,
            "requested_aspect_ratio": "2:3",
            "placement": "facebook_feed_portrait_4x5",
            "placement_aspect_ratio": PLACEMENT_PRESETS["facebook_feed_portrait_4x5"][
                "aspect_ratio"
            ],
            "format": "png",
            "quality": DEFAULT_QUALITY,
        },
        "generated_dimensions": generated_dimensions,
        "binary_written": binary_written,
        "binary_committed": False,
        "safe_to_share": True,
        "docs_checked": docs_checked,
    }
