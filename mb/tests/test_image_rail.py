from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import yaml
from typer.testing import CliRunner

from mb import image_rail as image_rail_mod
from mb.cli import app

runner = CliRunner()


def _record_from_index(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    _, fenced = text.split("```yaml\n", 1)
    yaml_text, _ = fenced.split("\n```", 1)
    return cast(dict[str, Any], yaml.safe_load(yaml_text))


def test_openai_image_smoke_writes_safe_blocked_record(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(
        app,
        [
            "image",
            "smoke-openai",
            "--repo",
            str(repo),
            "--push-slug",
            "2026-05-13-fake-openai-smoke",
            "--docs-checked",
            "2026-05-13",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["provider"] == "openai"
    assert payload["model"] == "gpt-image-2"
    assert payload["state"] == "blocked"
    assert payload["blocker_code"] == "generation_not_approved"
    assert payload["candidate_count"] == 9
    assert payload["generated_count"] == 0
    assert payload["best_candidate"] is None
    assert payload["best_playbook"] is None
    assert payload["all_rejected"] is None
    assert payload["overlay_tested"] is False
    assert "no_visual_quality_proven" in payload["main_failure_modes"]
    assert payload["output_record_written"] is True
    assert payload["review_board_written"] is True
    assert payload["binary_committed"] is False

    index_path = repo / "pushes" / "2026-05-13-fake-openai-smoke" / "image-index.md"
    review_board_path = (
        repo / ".mb" / "media" / "pushes" / "2026-05-13-fake-openai-smoke" / "review-board.md"
    )
    assert index_path.exists()
    assert review_board_path.exists()
    record = _record_from_index(index_path)
    asset = record["assets"][0]
    concepts = record["concepts"]

    assert record["schema"] == "mainbranch.image_index.v0"
    assert record["experiment_frame"] == "first_creative_playbook_router_experiment"
    assert record["conversion_language"] == "conversion_informed"
    assert record["batch_plan"]["candidate_count"] == 9
    assert record["generated_count"] == 0
    assert record["best_candidate"] is None
    assert record["best_playbook"] is None
    assert record["all_rejected"] is None
    assert record["overlay_tested"] is False
    assert "provider_generation_not_run" in record["main_failure_modes"]
    assert record["visual_calibration_result"]["state"] == "blocked"
    assert record["visual_calibration_result"]["generated_count"] == 0
    assert record["visual_calibration_result"]["best_candidate"] is None
    assert record["visual_calibration_result"]["best_playbook"] is None
    assert record["visual_calibration_result"]["all_rejected"] is None
    assert record["visual_calibration_result"]["overlay_tested"] is False
    assert "no_visual_quality_proven" in record["visual_calibration_result"]["main_failure_modes"]
    assert record["dashboard_readiness"]["state"] == "readable"
    assert record["dashboard_readiness"]["read_only"] is True
    assert record["dashboard_readiness"]["dashboard_role"] == "visual_map"
    assert record["dashboard_readiness"]["logic_owners"]["cli"] == "facts_and_safe_checks"
    assert "mb start --json" in record["dashboard_readiness"]["safe_sources"]
    assert (
        record["dashboard_readiness"]["record_sections"]["winner_or_rejection"]
        == "visual_calibration_result"
    )
    assert "confirm_openai_image_credential_state" in record["dashboard_readiness"]["next_actions"]
    assert "no_secrets" in record["dashboard_readiness"]["boundaries"]
    assert (
        record["review_board_question"] == "Which playbook produced the best actual ad candidate?"
    )
    assert record["review_rule"] == "Beautiful but no click reason = reject."
    assert record["review_board"]["committed"] is False
    assert "high_contrast_poster" in record["creative_playbook_ids"]
    assert "bold_meme_poster" not in record["creative_playbook_ids"]
    assert "native_collage" not in record["creative_playbook_ids"]
    assert len(concepts) == 9
    assert len(record["assets"]) == 9
    assert "facebook_feed_portrait_4x5" in record["placement_presets"]
    assert "style_reference" in record["reference_roles"]
    assert record["ad_readiness_gate"]["state"] == "ready"
    assert record["ad_readiness_gate"]["required_fields"] == [
        "offer",
        "audience",
        "campaign_goal",
        "claim_proof_boundary",
    ]
    assert record["ad_readiness_gate"]["hard_stop_missing_fields"] == []
    assert "api_generation" in record["ad_readiness_gate"]["allowed_actions"]
    assert "final_ad_package" in record["ad_readiness_gate"]["allowed_actions"]
    assert (
        "operator_approval_for_live_provider_call"
        in record["image_generation_gate"]["required_before_provider_generation"]
    )
    assert record["selected_source_bites"][0]["concept_id"] == concepts[0]["concept_id"]
    assert record["selected_source_bites"][0]["extracted_phrase"] == "I keep losing the thread"
    assert record["post_processing_plan"]["status"] == "planned_not_implemented"
    assert record["post_processing_plan"]["overlay_expected"] is True
    assert concepts[0]["concept_id"] == asset["concept_id"]
    assert concepts[0]["prompt_key"] == image_rail_mod.DEFAULT_PROMPT_KEY
    assert concepts[0]["creative_playbook_id"] == "specific_object_metaphor"
    assert concepts[0]["creative_playbook"]["id"] == "specific_object_metaphor"
    assert concepts[0]["creative_playbook"]["legacy_label"] == "technical-founder"
    assert concepts[0]["creative_playbook"]["status"] == "candidate"
    assert concepts[0]["router_inputs"]["offer_type"] == "open_source_business_os"
    assert concepts[0]["router_inputs"]["source_bite_type"] == "customer_language"
    assert concepts[0]["router_reason"]
    assert concepts[0]["playbook_fit"]["conversion_pattern_fit"] == 4
    assert concepts[0]["external_pattern_signal"]["source_type"] == "grok_synthesis"
    assert concepts[0]["external_pattern_signal"]["primary_source_verified"] is False
    assert concepts[0]["reference_influence_test"]["mode"] == "none"
    assert concepts[0]["reference_influence"]["mode"] == "none"
    assert concepts[0]["reference_influence"]["influence_score"] is None
    assert concepts[0]["reference_influence"]["copy_risk"] == "pass"
    assert "branch map" in concepts[0]["creative_playbook"]["useful_metaphors"]
    assert concepts[0]["prompt_strategy"] == "creative_director_brief_first_no_text_base"
    assert concepts[1]["prompt_strategy"] == "reference_aware_no_text_base"
    assert concepts[0]["viewer_scroll_context"] == "cold Facebook feed"
    assert concepts[0]["first_second_read"]
    assert concepts[0]["source_bite"]["source_type"] == "customer_language"
    assert concepts[0]["source_bite"]["extracted_phrase"] == "I keep losing the thread"
    assert "thread" in concepts[0]["source_bite"]["visual_translation"]
    assert concepts[0]["genericness_check"]["specific_to_this_offer"] == 5
    assert concepts[0]["genericness_check"]["could_fit_notion"] is False
    assert concepts[0]["genericness_check"]["could_fit_asana"] is False
    assert concepts[0]["genericness_check"]["could_fit_quickbooks"] is False
    assert concepts[0]["genericness_check"]["could_fit_generic_coaching_offer"] is False
    assert concepts[0]["genericness_check"]["could_fit_generic_productivity_app"] is False
    assert "clean desk productivity cliché" in concepts[0]["avoidance_strategy"]["avoids"]
    assert concepts[0]["avoidance_strategy"]["intentionally_uses"] == []
    assert concepts[0]["visual_hierarchy"]["text_zone"] == "upper right"
    assert concepts[0]["placement"] == "facebook_feed_portrait_4x5"
    assert concepts[0]["source_files"]
    assert concepts[0]["claim_boundary"]
    assert concepts[0]["references"] == []
    assert concepts[1]["references"][0]["role"] == "style_reference"
    assert concepts[1]["references"][0]["approval_required"] is True
    assert concepts[1]["references"][0]["privacy_level"] == "private"
    assert concepts[1]["references"][0]["use_for"]
    assert concepts[1]["references"][0]["do_not_copy"]
    assert concepts[1]["reference_trait_extraction"][0]["reference_id"] == "style-001"
    assert "private" not in concepts[1]["reference_trait_extraction"][0]["traits"]["composition"]
    assert concepts[0]["review"]["one_second_clarity"] == "pass"
    assert concepts[0]["review"]["source_bite_fit"] == "pass"
    assert concepts[0]["review"]["genericness_risk"] == "pass"
    assert concepts[0]["review"]["avoidance_strategy_fit"] == "pass"
    assert concepts[0]["review"]["avoidance_risk"] == "pass"
    assert concepts[0]["review"]["prompt_record_complete"] == "pass"
    assert concepts[0]["review"]["reference_copy_risk"] == "pass"
    assert concepts[0]["review"]["export_readiness"] == "pass"
    assert concepts[0]["review"]["click_reason_fit"] == "pass"
    assert concepts[0]["review"]["avoidance_check"]["native_feed_fit"] == 5
    assert concepts[0]["review"]["avoidance_check"]["clean_desk_cliche_risk"] == "pass"
    assert concepts[0]["review"]["visual_quality"]["composition"] == 5
    assert concepts[0]["review"]["ad_quality"]["thumb_stop"] == 5
    assert concepts[0]["review"]["ad_quality"]["likely_click_reason"]
    assert concepts[0]["review"]["risk"]["ai_slop_risk"] == 1
    assert concepts[0]["review"]["risk"]["compliance_risk"] == "pass"
    assert concepts[0]["review"]["scores"]["one_second_clarity"] == 5
    assert concepts[0]["review"]["scores"]["specific_to_this_offer"] == 5
    assert concepts[0]["review"]["scores"]["native_feed_fit"] == 5
    assert concepts[0]["review"]["decision"] == "accept"
    assert asset["provider"] == "openai"
    assert asset["model"] == "gpt-image-2"
    assert asset["model_snapshot"] == "gpt-image-2-2026-04-21"
    assert asset["credential_state"] == "missing_env"
    assert asset["prompt_key"] == image_rail_mod.DEFAULT_PROMPT_KEY
    assert asset["output_reference"].startswith("mb-media://pushes/")
    assert asset["storage_backend"] == "mb-media"
    assert asset["committed_binary"] is False
    assert asset["safe_to_share"] is True

    text = index_path.read_text(encoding="utf-8")
    board_text = review_board_path.read_text(encoding="utf-8")
    assert str(tmp_path) not in text
    assert str(tmp_path) not in board_text
    assert "Which playbook produced the best actual ad candidate?" in board_text
    assert "Beautiful but no click reason = reject." in board_text
    assert "OPENAI_API_KEY=" not in text
    assert not list((repo / ".mb" / "media").rglob("*.png"))
    assert not list((repo / "pushes").rglob("*.png"))


def test_openai_image_smoke_generate_without_key_records_missing_key(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(
        app,
        [
            "image",
            "smoke-openai",
            "--repo",
            str(repo),
            "--push-slug",
            "2026-05-13-fake-openai-smoke",
            "--docs-checked",
            "2026-05-13",
            "--generate",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["state"] == "blocked"
    assert payload["blocker_code"] == "missing_openai_api_key"
    assert payload["best_candidate"] is None
    assert payload["best_playbook"] is None
    assert payload["all_rejected"] is None
    assert payload["overlay_tested"] is False

    index_path = repo / "pushes" / "2026-05-13-fake-openai-smoke" / "image-index.md"
    record = _record_from_index(index_path)
    asset = record["assets"][0]
    assert asset["blocker_code"] == "missing_openai_api_key"
    assert "Do not paste provider keys" in asset["blocker"]
    assert record["concepts"][0]["status"] == "planned"
    assert record["concepts"][0]["review"]["status"] == "accepted"
    assert record["concepts"][0]["review"]["source_bite_fit"] == "pass"
    assert record["concepts"][0]["review"]["genericness_risk"] == "pass"
    assert record["concepts"][0]["review"]["avoidance_strategy_fit"] == "pass"
    assert record["concepts"][0]["review"]["prompt_record_complete"] == "pass"
    assert record["concepts"][0]["review"]["scores"]["ai_generic_risk"] == 1
    assert record["visual_calibration_result"]["state"] == "blocked"
    assert record["visual_calibration_result"]["overlay_tested"] is False
    assert asset["concept_id"] == image_rail_mod.DEFAULT_CONCEPT_ID


def test_openai_image_smoke_generated_path_keeps_binary_in_media_cache(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-written")
    monkeypatch.setattr(image_rail_mod, "_provider_blocker", lambda generate: ("", ""))
    monkeypatch.setattr(
        image_rail_mod,
        "_generate_openai_image",
        lambda prompt, *, model, size, quality: (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x04\x00\x00\x00\x06\x00fake-png-tail"
        ),
    )

    result = runner.invoke(
        app,
        [
            "image",
            "smoke-openai",
            "--repo",
            str(repo),
            "--push-slug",
            "2026-05-13-fake-openai-smoke",
            "--docs-checked",
            "2026-05-13",
            "--generate",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["state"] == "generated"
    assert payload["candidate_count"] == 9
    assert payload["generated_count"] == 9
    assert payload["best_candidate"] == image_rail_mod.DEFAULT_ASSET_ID
    assert payload["best_playbook"] == "specific_object_metaphor"
    assert payload["all_rejected"] is False
    assert payload["overlay_tested"] is False
    assert payload["main_failure_modes"] == []
    assert payload["generated_dimensions"] == {"width": 1024, "height": 1536}
    assert payload["binary_written"] is True
    assert payload["binary_written_count"] == 9
    assert payload["binary_committed"] is False

    media_path = (
        repo
        / ".mb"
        / "media"
        / "pushes"
        / "2026-05-13-fake-openai-smoke"
        / "images"
        / "fake-openai-image-001.png"
    )
    assert media_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    index_path = repo / "pushes" / "2026-05-13-fake-openai-smoke" / "image-index.md"
    record = _record_from_index(index_path)
    dimensions = record["assets"][0]["dimensions"]
    assert record["generated_count"] == 9
    assert record["best_candidate"] == image_rail_mod.DEFAULT_ASSET_ID
    assert record["best_playbook"] == "specific_object_metaphor"
    assert record["all_rejected"] is False
    assert record["overlay_tested"] is False
    assert record["main_failure_modes"] == []
    assert record["visual_calibration_result"]["state"] == "creative_review_winner_selected"
    assert record["visual_calibration_result"]["best_candidate"] == image_rail_mod.DEFAULT_ASSET_ID
    assert record["visual_calibration_result"]["best_playbook"] == "specific_object_metaphor"
    assert record["visual_calibration_result"]["overlay_tested"] is False
    assert (
        "test_deterministic_overlay_on_best_one_to_three_candidates"
        in record["dashboard_readiness"]["next_actions"]
    )
    assert all(asset["state"] == "generated" for asset in record["assets"])
    assert dimensions["generated_width"] == 1024
    assert dimensions["generated_height"] == 1536
    assert record["assets"][0]["prompt_key"] == image_rail_mod.DEFAULT_PROMPT_KEY
    assert record["selected_source_bites"]
    assert record["review_board"]["path"].endswith("review-board.md")
    assert record["post_processing_plan"]["resize_target"] == "1080x1350"
    text = index_path.read_text(encoding="utf-8")
    assert str(media_path) not in text
    assert "test-key-not-written" not in text


def test_openai_image_smoke_allows_absolute_media_root(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    repo = tmp_path / "biz"
    repo.mkdir()
    media_root = tmp_path / "private-media"

    result = image_rail_mod.smoke_openai(
        repo=str(repo),
        push_slug="2026-05-13-fake-openai-smoke",
        docs_checked="2026-05-13",
        media_root=str(media_root),
        generate=False,
    )

    assert result["state"] == "blocked"
    assert result["blocker_code"] == "generation_not_approved"
    assert result["review_board_written"] is True
    assert (
        result["review_board_path"]
        == "mb-media://pushes/2026-05-13-fake-openai-smoke/review-board.md"
    )

    review_board_path = media_root / "pushes" / "2026-05-13-fake-openai-smoke" / "review-board.md"
    assert review_board_path.exists()

    index_path = repo / "pushes" / "2026-05-13-fake-openai-smoke" / "image-index.md"
    index_text = index_path.read_text(encoding="utf-8")
    record = _record_from_index(index_path)
    assert (
        record["review_board"]["path"]
        == "mb-media://pushes/2026-05-13-fake-openai-smoke/review-board.md"
    )
    assert str(media_root) not in index_text


def test_openai_image_smoke_provider_failure_writes_sanitized_blocker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-written")
    monkeypatch.setattr(image_rail_mod, "_provider_blocker", lambda generate: ("", ""))

    def fail_generation(prompt: str, *, model: str, size: str, quality: str) -> bytes:
        raise RuntimeError("secret-bearing provider details should not be recorded")

    monkeypatch.setattr(image_rail_mod, "_generate_openai_image", fail_generation)

    result = runner.invoke(
        app,
        [
            "image",
            "smoke-openai",
            "--repo",
            str(repo),
            "--push-slug",
            "2026-05-13-fake-openai-smoke",
            "--docs-checked",
            "2026-05-13",
            "--generate",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["state"] == "blocked"
    assert payload["blocker_code"] == "provider_request_failed"
    assert payload["generated_count"] == 0
    assert payload["best_candidate"] is None
    assert payload["best_playbook"] is None
    assert payload["all_rejected"] is None
    assert payload["overlay_tested"] is False
    assert "no_visual_quality_proven" in payload["main_failure_modes"]

    index_path = repo / "pushes" / "2026-05-13-fake-openai-smoke" / "image-index.md"
    record = _record_from_index(index_path)
    assert all(asset["blocker_code"] == "provider_request_failed" for asset in record["assets"])
    assert record["visual_calibration_result"]["state"] == "blocked"
    assert record["visual_calibration_result"]["best_candidate"] is None
    text = index_path.read_text(encoding="utf-8")
    assert "RuntimeError" in text
    assert "secret-bearing provider details" not in text
    assert "test-key-not-written" not in text


def test_image_concept_review_catches_unsafe_fixture_case() -> None:
    concept = {
        "concept_id": "unsafe-meta-dashboard",
        "audience_state": "operator wants proof that ads are working",
        "visual_job": "show guaranteed revenue from ads",
        "visual_metaphor": "dashboard screenshot with Meta Ads Manager results",
        "composition": "real Meta UI with account ID in the corner",
        "emotional_tone": "hype",
        "placement": "unsupported_feed_banner",
        "text_overlay_plan": "render text-in-image with tiny claim",
        "source_files": [],
        "claim_boundary": "guaranteed revenue after launch",
        "references": [],
        "prompt": "Use customer data and a dashboard screenshot with guaranteed profit.",
        "negative_constraints": [],
    }

    review = image_rail_mod.review_concept(concept)

    assert review["status"] == "rejected"
    assert review["fake_ui_risk"] == "fail"
    assert review["claim_safety"] == "fail"
    assert review["private_data_risk"] == "fail"
    assert review["source_bite_fit"] == "fail"
    assert review["genericness_risk"] == "fail"
    assert review["avoidance_strategy_fit"] == "fail"
    assert review["placement_fit"] == "warning"
    assert review["readability"] == "warning"
    assert review["scores"]["specificity"] == 5
    assert review["scores"]["ai_generic_risk"] == 1


def test_image_concept_review_rejects_generic_source_light_concept() -> None:
    concept = {
        "concept_id": "generic-clean-desk",
        "audience_state": "owner wants a calmer workday",
        "visual_job": "show business work becoming organized",
        "visual_metaphor": "messy desk becoming a clean desk",
        "composition": "warm desk scene with empty wall for text",
        "emotional_tone": "calm",
        "placement": "facebook_feed_portrait_4x5",
        "text_overlay_plan": "text-free base image",
        "source_files": ["core/offer.md"],
        "claim_boundary": "do not promise outcomes",
        "references": [],
        "source_bite": {
            "source_file": "core/offer.md",
            "source_type": "offer",
            "extracted_phrase": "organized work",
            "insight": "The operator wants less clutter.",
            "visual_translation": "a clean desk",
        },
        "genericness_check": {
            "could_fit_notion": True,
            "could_fit_asana": True,
            "could_fit_quickbooks": True,
            "could_fit_generic_coaching_offer": True,
            "could_fit_generic_productivity_app": True,
            "could_fit_any_coaching_offer": True,
            "could_fit_accounting_software": True,
            "specific_to_this_offer": 2,
            "reason": "This could fit almost any productivity or accounting product.",
        },
        "avoidance_strategy": {
            "avoids": [
                "clean desk productivity cliché",
                "website hero composition",
                "stock-photo business imagery",
            ],
            "intentionally_uses": [],
            "reason": "This fixture should be revised instead of generated.",
        },
        "prompt": "Create a clean desk ad image with warm light.",
        "negative_constraints": ["no real logos", "no customer data"],
    }

    review = image_rail_mod.review_concept(concept)

    assert review["status"] == "rejected"
    assert review["source_bite_fit"] == "pass"
    assert review["genericness_risk"] == "fail"
    assert review["avoidance_strategy_fit"] == "pass"
    assert review["avoidance_risk"] == "warning"
    assert review["avoidance_check"]["clean_desk_cliche_risk"] == "warning"
    assert review["avoidance_check"]["too_safe_to_stop_scroll"] == "warning"
    assert "specific to this offer" in " ".join(review["notes"])
    assert review["scores"]["specific_to_this_offer"] == 2
    assert review["scores"]["native_feed_fit"] < 4


def test_init_gitignore_keeps_media_cache_out_of_git(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path / "biz"), "--name", "Acme"])

    assert result.exit_code == 0
    gitignore = (tmp_path / "biz" / ".gitignore").read_text(encoding="utf-8")
    assert ".mb/media/" in gitignore
