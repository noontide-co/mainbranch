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
DEFAULT_MODEL = "gpt-image-2"
DEFAULT_MODEL_SNAPSHOT = "gpt-image-2-2026-04-21"
DEFAULT_SIZE = "1024x1536"
DEFAULT_QUALITY = "medium"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_PROMPT = """\
Create a fixture-safe static ad concept for a fictional business called
Northstar Ledger. Show an abstract desk scene with a clean notebook, simple
charts, and warm natural light. Do not include real brands, real people,
customer data, logos, screenshots, account details, or private information.
Leave open space near the upper center for a later deterministic text overlay.
"""
DEFAULT_CONCEPT_ID = "clean-ledger-command-center"
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
    ai_generic_risk = "warning" if not references and "generic ai art" in joined else "pass"

    checks = {
        "one_second_clarity": one_second_clarity,
        "visual_hook_strength": visual_hook_strength,
        "ad_usefulness": ad_usefulness,
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

    scores = {
        "one_second_clarity": _review_score(one_second_clarity),
        "visual_hook_strength": _review_score(visual_hook_strength),
        "specificity": _review_score(ad_usefulness),
        "brand_fit": _review_score(brand_fit),
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
        "scores": scores,
        "notes": notes,
    }


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
        f"pushes/{push_slug}/push.md",
    ]
    concepts: list[dict[str, Any]] = [
        {
            "concept_id": DEFAULT_CONCEPT_ID,
            "status": "planned",
            "prompt_strategy": "creative_director_brief_first_no_text_base",
            "prompt_strategy_notes": (
                "Default production path: brief the visual job first, generate "
                "a text-free base image, then apply deterministic overlay later."
            ),
            "viewer_scroll_context": "cold Facebook feed",
            "first_second_read": "messy finance clutter becomes one clean operating system",
            "audience_state": "owner wants calmer bookkeeping without exposing private ledgers",
            "visual_job": (
                "show that finance work becomes easier when the operating system is clear"
            ),
            "visual_metaphor": (
                "messy receipts and notes resolving into one clean desk command center"
            ),
            "composition": (
                "warm desk scene, strong central notebook focal point, open upper-center space"
            ),
            "visual_hierarchy": {
                "primary_focal_point": "clean notebook command center",
                "secondary_focal_point": "scattered receipts and notes",
                "text_zone": "upper center",
            },
            "camera_language": "slight top-down editorial desk scene",
            "style_strength": "subtle, not over-stylized",
            "emotional_tone": "relief after clutter",
            "placement": "facebook_feed_portrait_4x5",
            "placement_details": PLACEMENT_PRESETS["facebook_feed_portrait_4x5"],
            "text_overlay_plan": "text-free base image; deterministic overlay later, max 4 words",
            "source_files": common_sources,
            "claim_boundary": (
                "do not imply guaranteed revenue, tax advice, or provider partnership"
            ),
            "references": [],
            "prompt": DEFAULT_PROMPT.strip(),
            "negative_constraints": [
                "no real Meta UI",
                "no real logos",
                "no tiny text",
                "no revenue screenshots",
                "no before/after income claim",
                "no customer data",
            ],
        },
        {
            "concept_id": "operator-before-after-chaos",
            "status": "planned",
            "prompt_strategy": "reference_aware_no_text_base",
            "prompt_strategy_notes": (
                "Use the style reference for mood and composition only; do not "
                "copy subjects, logos, text, or private details."
            ),
            "viewer_scroll_context": "mobile feed between founder and SaaS posts",
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
            "prompt_strategy": "creative_director_brief_first_no_text_base",
            "prompt_strategy_notes": (
                "Plan the vertical composition and text-safe zone before any provider call."
            ),
            "viewer_scroll_context": "story or reels vertical placement",
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

    record = {
        "schema": "mainbranch.image_index.v0",
        "push_slug": push_slug,
        "docs_checked": docs_checked,
        "output_record_written": True,
        "binary_committed": False,
        "placement_presets": PLACEMENT_PRESETS,
        "reference_roles": list(REFERENCE_ROLES),
        "concepts": fixture_facebook_image_concepts(push_slug),
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
