# Image Index - OpenAI Image Rail Smoke

This fixture-safe record proves the first narrow OpenAI image rail with reviewable Facebook image-ad concepts, safe logical media references, and no generated binaries, secrets, private paths, or provider request credentials committed.

```yaml
schema: mainbranch.image_index.v0
push_slug: 2026-05-13-openai-image-rail-dogfood
docs_checked: '2026-05-13'
output_record_written: true
binary_committed: false
experiment_frame: first_creative_playbook_router_experiment
conversion_language: conversion_informed
batch_plan:
  candidate_count: 9
  target_range: 8-12
  strategy: top playbook candidates with one to two variants each
  provider_validation: official_api_rail_only
  generation_size_override:
    applied_to_all_assets: true
    requested_size: 1024x1536
    reason: Keep the official API dogfood batch consistent while testing creative
      direction before per-placement export.
    boundary: Concept placement metadata remains in `concepts[].placement_details`;
      asset dimensions record the actual provider generation request.
generated_count: 9
best_candidate: null
best_playbook: null
all_rejected: true
overlay_tested: false
main_failure_modes: &id005
- generic_ai_image_feel
- not_native_to_feed
- weak_ad_click_reason
- overlay_not_tested_no_finalist
creative_playbook_ids:
- native_problem_scene
- specific_object_metaphor
- proof_artifact
- myth_vs_fact
- with_without_transformation
- crossed_out_problem_list
- founder_pov
- high_contrast_poster
- simple_chart_comparison
- testimonials_with_artifact
- us_vs_them_split
- simple_list_framework
review_board_question: Which playbook produced the best actual ad candidate?
review_board:
  path: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/review-board.md
  committed: false
  storage: ignored_media_storage
review_rule: Beautiful but no click reason = reject.
external_research_boundary: External creative research is scratch/source signal only;
  raw dumps, screenshots, and unverified claims are not committed.
ad_readiness_gate:
  state: ready
  status: fixture_ready
  required_fields:
  - offer
  - audience
  - campaign_goal
  - claim_proof_boundary
  hard_stop_missing: &id001 []
  hard_stop_missing_fields: *id001
  soft_warning_missing: &id002
  - proof
  - customer_language
  - brand_visual_style
  - prior_outcomes
  - meta_summary
  - reference_images
  soft_warning_missing_fields: *id002
  allowed_actions:
  - intake
  - repo_source_audit
  - ad_strategy_outline
  - missing_info_checklist
  - exploration_concepts
  - api_generation
  - final_ad_package
  allowed_low_context_actions:
  - intake
  - repo_source_audit
  - ad_strategy_outline
  - missing_info_checklist
  - placeholder_concepts_marked_as_placeholders
  blocked_actions: &id003
  - final_ad_package_when_hard_stop_missing
  - provider_image_generation_when_hard_stop_missing
  - campaign_ready_claims_when_hard_stop_missing
  - meta_informed_recommendations_without_approved_summary
  blocked_low_context_actions: *id003
  future_cli_candidate: mb ads readiness --json
  rule: If hard-stop fields are missing, produce an intake/source-bite plan instead
    of final ads.
image_generation_gate:
  required_before_provider_generation: &id004
  - selected_concept
  - prompt_record
  - safe_media_storage
  - image_index_target
  - credential_state
  - operator_approval_for_live_provider_call
  workflow:
  - repo_facts
  - ad_readiness
  - source_bites
  - playbook_router
  - concepts
  - review_genericness_checks
  - prompt_records
  - generation_or_fallback
  - review_board
  - image_index
dashboard_readiness:
  state: readable
  read_only: true
  dashboard_role: visual_map
  logic_owners:
    cli: facts_and_safe_checks
    skills: workflow_and_judgment
    repo_files: memory
    dashboard: visual_map
  safe_sources:
  - mb start --json
  - mb status --json --peek
  - mb ads meta summary --json when operator approved
  - pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
  - mb-media://pushes/2026-05-13-openai-image-rail-dogfood/review-board.md
  - current push files
  record_sections:
    ad_readiness: ad_readiness_gate
    missing_inputs:
    - ad_readiness_gate.hard_stop_missing_fields
    - ad_readiness_gate.soft_warning_missing_fields
    source_bites: selected_source_bites
    playbook_router_choices:
    - concepts[].creative_playbook_id
    - concepts[].router_inputs
    - concepts[].router_reason
    - concepts[].playbook_fit
    image_candidates:
    - concepts[]
    - assets[]
    review_scores:
    - concepts[].review.visual_quality
    - concepts[].review.ad_quality
    - concepts[].review.risk
    winner_or_rejection: visual_calibration_result
    provider_readiness:
    - assets[].credential_state
    - assets[].blocker_code
    - image_generation_gate.required_before_provider_generation
    next_actions: dashboard_readiness.next_actions
  provider_readiness:
    provider: openai
    model: gpt-image-2
    credential_states:
    - configured_env
    blocker_codes: []
    required_before_generation: *id004
  missing_inputs:
    hard_stop: *id001
    soft_warning: *id002
  next_actions:
  - review_hard_stop_offer_audience_campaign_goal_claim_boundary
  - review_source_bites_before_generation
  - revise_prompt_direction_before_next_provider_batch
  - test_with_real_reference_or_ad_native_pattern_inputs
  - avoid_recording_automated_concept_score_as_visual_winner
  boundaries:
  - no_secrets
  - no_raw_provider_payloads
  - no_private_paths
  - no_committed_image_binaries
placement_presets:
  facebook_feed_portrait_4x5: &id006
    aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    recommended_generation_size: 1440x1800
    final_export_size: 1080x1350
    safe_zone:
      top: 10%
      bottom: 10%
      sides: 10%
      notes: Keep focal point and overlay text inside conservative feed margins.
    deterministic_overlay_expected: true
    source_boundary: Aspect ratio checked against public Meta guidance; pixel sizes
      are planning defaults. Verify current Ads Manager specs before launch.
    validation: Preview in Meta Ads Manager before launch.
  facebook_feed_square_1x1: &id007
    aspect_ratio: '1:1'
    nearest_provider_size: 1024x1024
    recommended_generation_size: 1440x1440
    final_export_size: 1080x1080
    safe_zone:
      top: 10%
      bottom: 10%
      sides: 10%
      notes: Keep the focal point centered for mobile feed crop.
    deterministic_overlay_expected: true
    source_boundary: Planning preset for square feed/carousel-style creative. Verify
      current Ads Manager specs before launch.
    validation: Preview in Meta Ads Manager before launch.
  facebook_story_reels_9x16: &id009
    aspect_ratio: '9:16'
    nearest_provider_size: 1024x1792
    recommended_generation_size: 1440x2560
    final_export_size: 1080x1920
    safe_zone:
      top: 14%
      bottom: 35%
      sides: 6%
      notes: Keep critical content inside the center safe band.
    deterministic_overlay_expected: true
    source_boundary: 9:16 vertical guidance checked against public Meta Reels guidance;
      verify current Ads Manager specs before launch.
    validation: Preview Stories/Reels placements before launch.
reference_roles:
- logo
- product_photo
- style_reference
- screenshot_reference
- background
- mask_source
selected_source_bites:
- concept_id: lost-thread-branch-map
  source_file: research/customer-language.md
  source_type: customer_language
  extracted_phrase: I keep losing the thread
  visual_translation: tangled red thread becoming a clean branch map connected to
    one durable business archive
- concept_id: operator-before-after-chaos
  source_file: core/offer.md
  source_type: offer
  extracted_phrase: the business repo is durable business memory
  visual_translation: a private archive object quietly connecting decisions, goals,
    pushes, and proof cards
- concept_id: mobile-safe-progress-path
  source_file: pushes/2026-05-13-openai-image-rail-dogfood/push.md
  source_type: push_brief
  extracted_phrase: what is the next practical move?
  visual_translation: one lit checkpoint emerging from launch notes while the rest
    of the clutter stays out of the safe zone
- concept_id: app-sprawl-native-scene
  source_file: research/customer-language.md
  source_type: customer_language
  extracted_phrase: everything is scattered across too many places
  visual_translation: browser tabs, notes, and invoices crowding a laptop while one
    folder anchors the scene
- concept_id: myth-vs-folder
  source_file: core/audience.md
  source_type: objection
  extracted_phrase: I probably need another app
  visual_translation: a pile of app icons fading behind one durable local folder
- concept_id: with-without-context
  source_file: core/offer.md
  source_type: problem_outcome_contrast
  extracted_phrase: stop re-explaining the business every session
  visual_translation: 'two work surfaces: repeated sticky-note explanations versus
    one connected repo map'
- concept_id: crossed-out-tools
  source_file: research/customer-language.md
  source_type: problem_list
  extracted_phrase: I forgot the decision, the offer, and the next step
  visual_translation: three unlabeled problem cards crossed out beside one branch-map
    card
- concept_id: founder-pov-checkpoint
  source_file: pushes/2026-05-13-openai-image-rail-dogfood/push.md
  source_type: founder_note
  extracted_phrase: what did we decide last time?
  visual_translation: first-person hand opening a checkpoint folder next to yesterday's
    notes
- concept_id: high-contrast-context-poster
  source_file: research/customer-language.md
  source_type: customer_language
  extracted_phrase: starting from zero every Monday
  visual_translation: a stark reset button cracked by a small branch map
post_processing_plan:
  status: skipped_after_all_generated_candidates_rejected
  resize_target: 1080x1350
  overlay_expected: false
  overlay_method: skipped_no_finalist
  export_format: png_source_then_jpeg_or_png_final
  compression_target: future_export_step
  validation: No Meta preview until a base image passes manual ad-quality review.
visual_calibration_result:
  state: all_rejected
  generated_count: 9
  provider: openai
  model: gpt-image-2
  binary_committed: false
  review_board_written: true
  review_board_path: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/review-board.md
  best_candidate: null
  best_playbook: null
  all_rejected: true
  overlay_tested: false
  overlay_required_for_best_1_to_3: false
  main_failure_modes: *id005
  manual_review:
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    verdict: all generated candidates rejected
    notes:
    - The images feel like generic GPT images.
    - They do not feel like ads or native feed creative.
    - No clear best three emerged from the batch.
    - The next batch needs a different creative direction, not overlays on these bases.
  next_prompt_changes:
  - Treat reference or ad-native pattern inputs as required for the next visual-quality test.
  - Push prompts away from polished AI illustration and toward ugly, specific, native-feed artifacts.
  - Do not let pre-generation concept scores select a winner without manual visual review.
  note: Official API generation worked and produced nine fixture-safe candidates, but
    manual visual review rejected the whole batch for generic AI feel and weak ad
    usefulness.
concepts:
- concept_id: lost-thread-branch-map
  status: planned
  prompt_key: lost-thread-branch-map.v1
  creative_playbook:
    id: specific_object_metaphor
    status: candidate
    legacy_label: technical-founder
    use_when:
    - audience speaks in systems, workflows, and operating clarity
    - offer promise is about memory, process, or context continuity
    default_avoid:
    - generic SaaS gradient
    - fake dashboard
    - hologram UI
    - robot assistant
    useful_metaphors:
    - dependency graph
    - broken pipeline
    - incident board
    - branch map
    - lost thread
    risky_metaphors:
    - glowing brain
    - robot assistant
    - generic command center
    prompt_bias:
    - tactile systems
    - real artifacts
    - visible consequence
    - source-bite metaphor
  prompt_strategy: creative_director_brief_first_no_text_base
  prompt_strategy_notes: 'Default production path: brief the visual job first, generate
    a text-free base image, then apply deterministic overlay later.'
  viewer_scroll_context: cold Facebook feed
  source_bite:
    source_file: research/customer-language.md
    source_type: customer_language
    extracted_phrase: I keep losing the thread
    insight: The pain is not generic clutter; the operator loses continuity when decisions
      and tasks scatter across tools.
    visual_translation: tangled red thread becoming a clean branch map connected to
      one durable business archive
  genericness_check:
    could_fit_notion: false
    could_fit_asana: false
    could_fit_quickbooks: false
    could_fit_generic_coaching_offer: false
    could_fit_generic_productivity_app: false
    could_fit_any_coaching_offer: false
    could_fit_accounting_software: false
    specific_to_this_offer: 5
    reason: The thread, branch-map, and archive metaphor expresses the repo-backed
      business memory promise.
  avoidance_strategy:
    avoids:
    - stock-photo business imagery
    - "clean desk productivity clich\xE9"
    - "split-screen chaos/order clich\xE9"
    - website hero composition
    - fake dashboard
    - generic SaaS gradient
    intentionally_uses: []
    reason: Uses a customer-language source-bite metaphor instead of generic productivity
      imagery.
  first_second_read: lost business thread becomes one durable branch map
  audience_state: operator is resuming work after context switching across tools
  visual_job: make continuity loss visible before showing the repo-backed memory fix
  visual_metaphor: tangled red thread resolving into a clean branch map and archive
  composition: feed-native tactile maze of red thread and scattered cards, with one
    clear branch path emerging toward a central archive and upper-right overlay space
  visual_hierarchy:
    primary_focal_point: red thread becoming a branch map
    secondary_focal_point: central archive object
    text_zone: upper right
  camera_language: slight top-down editorial ad composition
  style_strength: specific metaphor, restrained production polish
  emotional_tone: relief after broken continuity
  placement: facebook_feed_portrait_4x5
  placement_details: *id006
  text_overlay_plan: text-free base image; deterministic overlay later, max 4 words
  source_files: &id008
  - core/offer.md
  - core/audience.md
  - core/proof/testimonials.md
  - core/brand/visual-style.md
  - research/customer-language.md
  - pushes/2026-05-13-openai-image-rail-dogfood/push.md
  claim_boundary: do not imply automatic decisions, guaranteed outcomes, or provider
    partnership
  references: []
  reference_trait_extraction: []
  prompt: 'Create a fixture-safe Facebook feed image-ad base for a fictional business

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

    information.'
  negative_constraints:
  - no real Meta UI
  - no real logos
  - no rendered words
  - no revenue screenshots
  - no automatic outcome claim
  - no customer data
  creative_playbook_id: specific_object_metaphor
  router_inputs:
    niche: founder_tool
    offer_type: open_source_business_os
    audience: solo founder or operator
    proof_available: false
    brand_style: tactile, technical, irreverent
    platform: facebook_feed
    source_bite_type: customer_language
  router_reason: The source bite is emotional and abstract, so a specific object metaphor
    is more useful than chart proof.
  playbook_fit:
    source_bite_fit: 5
    offer_fit: 5
    audience_fit: 4
    visual_distinctiveness: 5
    conversion_pattern_fit: 4
  external_pattern_signal:
    source_type: grok_synthesis
    pattern: specific_object_metaphor
    confidence: medium
    primary_source_verified: false
  reference_influence_test:
    mode: none
    effect_on_specificity: 4
    effect_on_native_feed_fit: 4
    effect_on_ai_slop_risk: 2
  reference_influence:
    mode: none
    influence_score: null
    copy_risk: pass
  likely_click_reason: A founder who feels context slipping away recognizes the lost-thread
    problem before reading the overlay.
  review:
    status: accepted
    decision: accept
    one_second_clarity: pass
    visual_hook_strength: pass
    ad_usefulness: pass
    source_bite_fit: pass
    genericness_risk: pass
    avoidance_strategy_fit: pass
    avoidance_risk: pass
    prompt_record_complete: pass
    reference_copy_risk: pass
    export_readiness: pass
    readability: pass
    placement_fit: pass
    brand_fit: pass
    claim_safety: pass
    fake_ui_risk: pass
    policy_risk: pass
    private_data_risk: pass
    ai_generic_risk: pass
    click_reason_fit: pass
    visual_quality:
      composition: 5
      style: 5
      polish_control: 5
    ad_quality:
      thumb_stop: 5
      problem_clarity: 5
      desire_clarity: 5
      curiosity_gap: 5
      offer_relevance: 5
      likely_click_reason: A founder who feels context slipping away recognizes the
        lost-thread problem before reading the overlay.
    risk:
      ai_slop_risk: 1
      genericness_risk: 1
      compliance_risk: pass
    avoidance_check:
      stock_photo_risk: pass
      website_hero_risk: pass
      clean_desk_cliche_risk: pass
      generic_saas_risk: pass
      ai_slop_risk: pass
      overpolished_risk: pass
      native_feed_fit: 5
      too_safe_to_stop_scroll: pass
      notes: []
    scores:
      one_second_clarity: 5
      visual_hook_strength: 5
      specificity: 5
      brand_fit: 5
      source_bite_fit: 5
      specific_to_this_offer: 5
      native_feed_fit: 5
      export_readiness: 5
      ai_generic_risk: 1
    notes: []
- concept_id: operator-before-after-chaos
  status: planned
  prompt_key: durable-memory-archive-map.v1
  prompt_strategy: reference_aware_no_text_base
  prompt_strategy_notes: Use the style reference for mood and composition only; do
    not copy subjects, logos, text, or private details.
  viewer_scroll_context: mobile feed between founder and SaaS posts
  source_bite:
    source_file: core/offer.md
    source_type: offer
    extracted_phrase: the business repo is durable business memory
    insight: The offer is not another dashboard; it is memory the operator owns.
    visual_translation: a private archive object quietly connecting decisions, goals,
      pushes, and proof cards
  genericness_check:
    could_fit_notion: false
    could_fit_asana: false
    could_fit_quickbooks: false
    could_fit_generic_coaching_offer: false
    could_fit_generic_productivity_app: false
    could_fit_any_coaching_offer: false
    could_fit_accounting_software: false
    specific_to_this_offer: 5
    reason: The repo/archive memory metaphor is specific to Main Branch's durable
      business-memory promise.
  avoidance_strategy:
    avoids:
    - fake dashboard
    - generic SaaS gradient
    - hologram dashboard
    - glossy 3D icons
    - website hero composition
    intentionally_uses: []
    reason: Uses a repo/archive metaphor instead of dashboard or SaaS tropes.
  first_second_read: scattered business facts snap into a simple map
  audience_state: operator has business facts scattered across docs and dashboards
  visual_job: make scattered operating memory feel visible and organized
  visual_metaphor: paper fragments forming a simple business map on a wall
  composition: square crop, centered map, clear negative space around the focal point
  visual_hierarchy:
    primary_focal_point: simple business map
    secondary_focal_point: paper fragments
    text_zone: top third
  camera_language: straight-on editorial wall composition
  style_strength: clean but still native to the feed
  emotional_tone: control without hype
  placement: facebook_feed_square_1x1
  placement_details: *id007
  text_overlay_plan: no rendered text; reserve top third for overlay
  source_files: *id008
  claim_boundary: do not promise automatic growth or financial outcomes
  references:
  - id: style-001
    role: style_reference
    path: mb-media://references/style-001.png
    safe_to_share: false
    approval_required: true
    privacy_level: private
    use_for: color mood and simple composition
    do_not_copy: exact subject, logos, text, or private details
  reference_trait_extraction:
  - reference_id: style-001
    traits:
      palette: muted warm neutrals with one grounded accent
      composition: simple focal object with visible surrounding context
      lighting: natural, tactile, not glossy studio light
    do_not_copy: exact subject, text, logos, layout, or private details
  prompt: Create a fixture-safe square Facebook ad base image for a fictional business
    operating system. Show scattered paper fragments forming a clean business map.
    No text, logos, screenshots, private data, or real brands.
  negative_constraints:
  - no real logos
  - no rendered words
  - no private screenshots
  - no guaranteed outcome claim
  creative_playbook_id: native_problem_scene
  router_inputs:
    niche: founder_tool
    offer_type: open_source_business_os
    audience: solo founder or operator
    proof_available: false
    brand_style: tactile, technical, irreverent
    platform: facebook_feed
    source_bite_type: offer
  router_reason: The offer bite is broad, so a native problem scene gives the abstract
    business-memory promise a concrete feed-native setting.
  playbook_fit:
    source_bite_fit: 4
    offer_fit: 5
    audience_fit: 4
    visual_distinctiveness: 3
    conversion_pattern_fit: 4
  external_pattern_signal:
    source_type: grok_synthesis
    pattern: native_problem_scene
    confidence: medium
    primary_source_verified: false
  reference_influence_test:
    mode: text_traits
    effect_on_specificity: 4
    effect_on_native_feed_fit: 4
    effect_on_ai_slop_risk: 2
  reference_influence:
    mode: text_traits
    influence_score: null
    copy_risk: pass
  likely_click_reason: The operator sees scattered business facts becoming a map they
    own.
  creative_playbook:
    id: native_problem_scene
    status: candidate
  review:
    status: accepted
    decision: accept
    one_second_clarity: pass
    visual_hook_strength: pass
    ad_usefulness: pass
    source_bite_fit: pass
    genericness_risk: pass
    avoidance_strategy_fit: pass
    avoidance_risk: pass
    prompt_record_complete: pass
    reference_copy_risk: pass
    export_readiness: pass
    readability: pass
    placement_fit: pass
    brand_fit: pass
    claim_safety: pass
    fake_ui_risk: pass
    policy_risk: pass
    private_data_risk: pass
    ai_generic_risk: pass
    click_reason_fit: pass
    visual_quality:
      composition: 5
      style: 5
      polish_control: 5
    ad_quality:
      thumb_stop: 5
      problem_clarity: 5
      desire_clarity: 5
      curiosity_gap: 5
      offer_relevance: 5
      likely_click_reason: The operator sees scattered business facts becoming a map
        they own.
    risk:
      ai_slop_risk: 1
      genericness_risk: 1
      compliance_risk: pass
    avoidance_check:
      stock_photo_risk: pass
      website_hero_risk: pass
      clean_desk_cliche_risk: pass
      generic_saas_risk: pass
      ai_slop_risk: pass
      overpolished_risk: pass
      native_feed_fit: 5
      too_safe_to_stop_scroll: pass
      notes: []
    scores:
      one_second_clarity: 5
      visual_hook_strength: 5
      specificity: 5
      brand_fit: 5
      source_bite_fit: 5
      specific_to_this_offer: 5
      native_feed_fit: 5
      export_readiness: 5
      ai_generic_risk: 1
    notes: []
- concept_id: mobile-safe-progress-path
  status: planned
  prompt_key: mobile-safe-progress-path.v1
  prompt_strategy: creative_director_brief_first_no_text_base
  prompt_strategy_notes: Plan the vertical composition and text-safe zone before any
    provider call.
  viewer_scroll_context: story or reels vertical placement
  source_bite:
    source_file: pushes/2026-05-13-openai-image-rail-dogfood/push.md
    source_type: push_brief
    extracted_phrase: what is the next practical move?
    insight: The operator wants the system to preserve enough context to make the
      next action obvious.
    visual_translation: one lit checkpoint emerging from launch notes while the rest
      of the clutter stays out of the safe zone
  genericness_check:
    could_fit_notion: false
    could_fit_asana: false
    could_fit_quickbooks: false
    could_fit_generic_coaching_offer: true
    could_fit_generic_productivity_app: false
    could_fit_any_coaching_offer: true
    could_fit_accounting_software: false
    specific_to_this_offer: 4
    reason: The checkpoint is broad, but the launch notes and preserved context keep
      it tied to the Main Branch operator loop.
  avoidance_strategy:
    avoids:
    - centered product on white background
    - generic growth chart
    - website hero composition
    - overly cinematic lighting
    - fake dashboard
    intentionally_uses: []
    reason: Keeps the story placement focused on a concrete next-step metaphor.
  first_second_read: one practical next step appears inside launch clutter
  audience_state: solo operator wants the next practical move from a messy launch
  visual_job: make the next step feel obvious on a phone screen
  visual_metaphor: a narrow lit path through launch notes toward one marked checkpoint
  composition: vertical story crop, focal path inside center 1:1 safe zone
  visual_hierarchy:
    primary_focal_point: lit path and checkpoint
    secondary_focal_point: launch notes
    text_zone: above center
  camera_language: vertical mobile-first scene with centered subject
  style_strength: specific scene, low gloss
  emotional_tone: focused momentum
  placement: facebook_story_reels_9x16
  placement_details: *id009
  text_overlay_plan: text-free base image; overlay after export above center
  source_files: *id008
  claim_boundary: do not imply the software launches or spends money automatically
  references: []
  reference_trait_extraction: []
  prompt: Create a vertical 9:16 Facebook story ad base image for a fictional business
    planning tool. A narrow lit path moves through launch notes toward one simple
    checkpoint. Keep all critical detail in the center safe zone. No text, UI, logos,
    screenshots, account data, or private details.
  negative_constraints:
  - no platform UI
  - no logos
  - no tiny text
  - no account data
  - no unsupported automation claim
  creative_playbook_id: proof_artifact
  router_inputs:
    niche: founder_tool
    offer_type: open_source_business_os
    audience: solo founder or operator
    proof_available: false
    brand_style: tactile, technical, irreverent
    platform: facebook_feed
    source_bite_type: push_brief
  router_reason: The push bite asks for the next practical move, so a proof-artifact
    checkpoint scene can make progress feel inspectable without fake data.
  playbook_fit:
    source_bite_fit: 4
    offer_fit: 4
    audience_fit: 4
    visual_distinctiveness: 3
    conversion_pattern_fit: 3
  external_pattern_signal:
    source_type: grok_synthesis
    pattern: proof_artifact
    confidence: low
    primary_source_verified: false
  reference_influence_test:
    mode: none
    effect_on_specificity: 3
    effect_on_native_feed_fit: 3
    effect_on_ai_slop_risk: 3
  reference_influence:
    mode: none
    influence_score: null
    copy_risk: pass
  likely_click_reason: The image promises a practical next step instead of another
    vague productivity dashboard.
  creative_playbook:
    id: proof_artifact
    status: candidate
  review:
    status: accepted
    decision: accept
    one_second_clarity: pass
    visual_hook_strength: pass
    ad_usefulness: pass
    source_bite_fit: pass
    genericness_risk: pass
    avoidance_strategy_fit: pass
    avoidance_risk: pass
    prompt_record_complete: pass
    reference_copy_risk: pass
    export_readiness: pass
    readability: pass
    placement_fit: pass
    brand_fit: pass
    claim_safety: pass
    fake_ui_risk: pass
    policy_risk: pass
    private_data_risk: pass
    ai_generic_risk: pass
    click_reason_fit: pass
    visual_quality:
      composition: 5
      style: 5
      polish_control: 5
    ad_quality:
      thumb_stop: 5
      problem_clarity: 5
      desire_clarity: 5
      curiosity_gap: 5
      offer_relevance: 5
      likely_click_reason: The image promises a practical next step instead of another
        vague productivity dashboard.
    risk:
      ai_slop_risk: 1
      genericness_risk: 1
      compliance_risk: pass
    avoidance_check:
      stock_photo_risk: pass
      website_hero_risk: pass
      clean_desk_cliche_risk: pass
      generic_saas_risk: pass
      ai_slop_risk: pass
      overpolished_risk: pass
      native_feed_fit: 5
      too_safe_to_stop_scroll: pass
      notes: []
    scores:
      one_second_clarity: 5
      visual_hook_strength: 5
      specificity: 5
      brand_fit: 5
      source_bite_fit: 5
      specific_to_this_offer: 4
      native_feed_fit: 5
      export_readiness: 5
      ai_generic_risk: 1
    notes: []
- status: planned
  prompt_strategy: creative_director_brief_first_no_text_base
  viewer_scroll_context: cold Facebook feed
  placement: facebook_feed_portrait_4x5
  placement_details: *id006
  text_overlay_plan: text-free base image; deterministic overlay later
  source_files: *id008
  references: &id010 []
  reference_trait_extraction: &id011 []
  claim_boundary: do not imply automatic decisions, guaranteed outcomes, or provider
    partnership
  negative_constraints: &id012
  - no real Meta UI
  - no real logos
  - no rendered words
  - no customer data
  - no unsupported outcome claim
  concept_id: app-sprawl-native-scene
  prompt_key: app-sprawl-native-scene.v1
  source_bite:
    source_file: research/customer-language.md
    source_type: customer_language
    extracted_phrase: everything is scattered across too many places
    insight: The problem is visible in the operator's live work surface.
    visual_translation: browser tabs, notes, and invoices crowding a laptop while
      one folder anchors the scene
  genericness_check:
    could_fit_notion: true
    could_fit_asana: true
    could_fit_quickbooks: false
    could_fit_generic_coaching_offer: false
    could_fit_generic_productivity_app: true
    could_fit_any_coaching_offer: false
    could_fit_accounting_software: false
    specific_to_this_offer: 4
    reason: The folder-owned business memory cue narrows a common tab-sprawl scene.
  avoidance_strategy:
    avoids:
    - stock-photo business imagery
    - fake dashboard
    - generic SaaS gradient
    intentionally_uses: []
    reason: Uses a native problem scene instead of a polished product mockup.
  first_second_read: too many open loops, one owned business folder
  audience_state: operator has too many tabs and notes open after a work session
  visual_job: make app sprawl feel familiar and solvable
  visual_metaphor: one physical folder grounding a messy laptop scene
  composition: phone-camera desk scene with laptop tabs, notes, and one labeled-but-unreadable
    folder
  visual_hierarchy:
    primary_focal_point: owned folder beside laptop
    secondary_focal_point: messy tabs and notes
    text_zone: top third
  camera_language: native phone snapshot with natural desk mess
  style_strength: lo-fi and specific, not polished
  emotional_tone: recognition before relief
  prompt: Create a feed-native phone-style Facebook ad base image showing a founder
    desk with too many browser tabs, handwritten notes, and one plain business folder
    anchoring the mess. No readable text, UI, logos, customer data, or private details.
  creative_playbook_id: native_problem_scene
  router_inputs:
    niche: founder_tool
    offer_type: open_source_business_os
    audience: solo founder or operator
    proof_available: false
    brand_style: tactile, technical, irreverent
    platform: facebook_feed
    source_bite_type: customer_language
  router_reason: The source bite describes a native operating problem, so the best
    test is a feed-native scene before abstract proof.
  playbook_fit:
    source_bite_fit: 5
    offer_fit: 4
    audience_fit: 5
    visual_distinctiveness: 4
    conversion_pattern_fit: 4
  external_pattern_signal:
    source_type: grok_synthesis
    pattern: native_problem_scene
    confidence: medium
    primary_source_verified: false
  reference_influence_test:
    mode: none
    effect_on_specificity: 4
    effect_on_native_feed_fit: 5
    effect_on_ai_slop_risk: 2
  reference_influence:
    mode: none
    influence_score: null
    copy_risk: pass
  likely_click_reason: The scene looks like the founder's real tabs-and-notes problem.
  creative_playbook:
    id: native_problem_scene
    status: candidate
  review:
    status: accepted
    decision: accept
    one_second_clarity: pass
    visual_hook_strength: pass
    ad_usefulness: pass
    source_bite_fit: pass
    genericness_risk: pass
    avoidance_strategy_fit: pass
    avoidance_risk: pass
    prompt_record_complete: pass
    reference_copy_risk: pass
    export_readiness: pass
    readability: pass
    placement_fit: pass
    brand_fit: pass
    claim_safety: pass
    fake_ui_risk: pass
    policy_risk: pass
    private_data_risk: pass
    ai_generic_risk: pass
    click_reason_fit: pass
    visual_quality:
      composition: 5
      style: 5
      polish_control: 5
    ad_quality:
      thumb_stop: 5
      problem_clarity: 5
      desire_clarity: 5
      curiosity_gap: 5
      offer_relevance: 5
      likely_click_reason: The scene looks like the founder's real tabs-and-notes
        problem.
    risk:
      ai_slop_risk: 1
      genericness_risk: 1
      compliance_risk: pass
    avoidance_check:
      stock_photo_risk: pass
      website_hero_risk: pass
      clean_desk_cliche_risk: pass
      generic_saas_risk: pass
      ai_slop_risk: pass
      overpolished_risk: pass
      native_feed_fit: 5
      too_safe_to_stop_scroll: pass
      notes: []
    scores:
      one_second_clarity: 5
      visual_hook_strength: 5
      specificity: 5
      brand_fit: 5
      source_bite_fit: 5
      specific_to_this_offer: 4
      native_feed_fit: 5
      export_readiness: 5
      ai_generic_risk: 1
    notes: []
- status: planned
  prompt_strategy: creative_director_brief_first_no_text_base
  viewer_scroll_context: cold Facebook feed
  placement: facebook_feed_portrait_4x5
  placement_details: *id006
  text_overlay_plan: text-free base image; deterministic overlay later
  source_files: *id008
  references: *id010
  reference_trait_extraction: *id011
  claim_boundary: do not imply automatic decisions, guaranteed outcomes, or provider
    partnership
  negative_constraints: *id012
  concept_id: myth-vs-folder
  prompt_key: myth-vs-folder.v1
  source_bite:
    source_file: core/audience.md
    source_type: objection
    extracted_phrase: I probably need another app
    insight: The audience may misdiagnose the memory problem as a software-shopping
      problem.
    visual_translation: a pile of app icons fading behind one durable local folder
  genericness_check:
    could_fit_notion: true
    could_fit_asana: true
    could_fit_quickbooks: false
    could_fit_generic_coaching_offer: false
    could_fit_generic_productivity_app: true
    could_fit_any_coaching_offer: false
    could_fit_accounting_software: false
    specific_to_this_offer: 4
    reason: The local folder and owned-memory frame point back to Main Branch.
  avoidance_strategy:
    avoids:
    - fake app logos
    - generic SaaS gradient
    - website hero composition
    intentionally_uses: []
    reason: Tests an educational split without using real trademarks.
  first_second_read: not another app; one owned folder
  audience_state: operator thinks the fix is buying or configuring another tool
  visual_job: challenge the app-shopping misconception
  visual_metaphor: ghosted generic app tiles behind a plain local folder
  composition: simple split-feel poster with a crossed-out app pile and one tactile
    folder
  visual_hierarchy:
    primary_focal_point: plain folder
    secondary_focal_point: crossed-out generic app pile
    text_zone: upper right
  camera_language: flat editorial poster with tactile paper objects
  style_strength: educational, high contrast, not glossy
  emotional_tone: belief shift
  prompt: Create a text-free Facebook ad base image that visually contrasts a faded
    pile of generic unlabeled app tiles with one tactile local business folder. No
    rendered words, real logos, UI, customer data, or private details.
  creative_playbook_id: myth_vs_fact
  router_inputs:
    niche: founder_tool
    offer_type: open_source_business_os
    audience: solo founder or operator
    proof_available: false
    brand_style: tactile, technical, irreverent
    platform: facebook_feed
    source_bite_type: objection
  router_reason: The source bite is a misconception about needing another app, so
    a myth/fact frame can create a fast belief shift.
  playbook_fit:
    source_bite_fit: 4
    offer_fit: 4
    audience_fit: 4
    visual_distinctiveness: 3
    conversion_pattern_fit: 4
  external_pattern_signal:
    source_type: grok_synthesis
    pattern: myth_vs_fact
    confidence: low
    primary_source_verified: false
  reference_influence_test:
    mode: none
    effect_on_specificity: 3
    effect_on_native_feed_fit: 3
    effect_on_ai_slop_risk: 3
  reference_influence:
    mode: none
    influence_score: null
    copy_risk: pass
  likely_click_reason: The ad challenges the assumption that the fix is another app.
  creative_playbook:
    id: myth_vs_fact
    status: candidate
  review:
    status: accepted
    decision: accept
    one_second_clarity: pass
    visual_hook_strength: pass
    ad_usefulness: pass
    source_bite_fit: pass
    genericness_risk: pass
    avoidance_strategy_fit: pass
    avoidance_risk: pass
    prompt_record_complete: pass
    reference_copy_risk: pass
    export_readiness: pass
    readability: pass
    placement_fit: pass
    brand_fit: pass
    claim_safety: pass
    fake_ui_risk: pass
    policy_risk: pass
    private_data_risk: pass
    ai_generic_risk: pass
    click_reason_fit: pass
    visual_quality:
      composition: 5
      style: 5
      polish_control: 5
    ad_quality:
      thumb_stop: 5
      problem_clarity: 5
      desire_clarity: 5
      curiosity_gap: 5
      offer_relevance: 5
      likely_click_reason: The ad challenges the assumption that the fix is another
        app.
    risk:
      ai_slop_risk: 1
      genericness_risk: 1
      compliance_risk: pass
    avoidance_check:
      stock_photo_risk: pass
      website_hero_risk: pass
      clean_desk_cliche_risk: pass
      generic_saas_risk: pass
      ai_slop_risk: pass
      overpolished_risk: pass
      native_feed_fit: 5
      too_safe_to_stop_scroll: pass
      notes: []
    scores:
      one_second_clarity: 5
      visual_hook_strength: 5
      specificity: 5
      brand_fit: 5
      source_bite_fit: 5
      specific_to_this_offer: 4
      native_feed_fit: 5
      export_readiness: 5
      ai_generic_risk: 1
    notes: []
- status: planned
  prompt_strategy: creative_director_brief_first_no_text_base
  viewer_scroll_context: cold Facebook feed
  placement: facebook_feed_portrait_4x5
  placement_details: *id006
  text_overlay_plan: text-free base image; deterministic overlay later
  source_files: *id008
  references: *id010
  reference_trait_extraction: *id011
  claim_boundary: do not imply automatic decisions, guaranteed outcomes, or provider
    partnership
  negative_constraints: *id012
  concept_id: with-without-context
  prompt_key: with-without-context.v1
  source_bite:
    source_file: core/offer.md
    source_type: problem_outcome_contrast
    extracted_phrase: stop re-explaining the business every session
    insight: The core transformation is from repeated context setup to preserved memory.
    visual_translation: 'two work surfaces: repeated sticky-note explanations versus
      one connected repo map'
  genericness_check:
    could_fit_notion: true
    could_fit_asana: false
    could_fit_quickbooks: false
    could_fit_generic_coaching_offer: false
    could_fit_generic_productivity_app: true
    could_fit_any_coaching_offer: false
    could_fit_accounting_software: false
    specific_to_this_offer: 5
    reason: The repeated re-explanation pain is tied to AI-assisted business memory.
  avoidance_strategy:
    avoids:
    - "split-screen chaos/order clich\xE9"
    - "clean desk productivity clich\xE9"
    intentionally_uses:
    - before/after contrast
    reason: Uses transformation contrast, but grounds it in source-specific re-explanation.
  first_second_read: without memory versus with durable business context
  audience_state: operator keeps rebuilding context before useful work starts
  visual_job: make the cost of re-explaining visible
  visual_metaphor: sticky-note repetition becoming one connected map
  composition: subtle left/right transformation with sticky notes moving into a clean
    branch map
  visual_hierarchy:
    primary_focal_point: connected branch map
    secondary_focal_point: repeated sticky notes
    text_zone: top center
  camera_language: editorial tabletop comparison, not sterile
  style_strength: clear contrast with real paper texture
  emotional_tone: frustration turning into relief
  prompt: 'Create a text-free Facebook feed ad base image showing a before/after operating-memory
    contrast: repeated sticky-note explanations resolving into one connected branch
    map. No readable words, logos, UI, customer data, or private details.'
  creative_playbook_id: with_without_transformation
  router_inputs:
    niche: founder_tool
    offer_type: open_source_business_os
    audience: solo founder or operator
    proof_available: false
    brand_style: tactile, technical, irreverent
    platform: facebook_feed
    source_bite_type: problem_outcome_contrast
  router_reason: The source bite has a before/after operating-state contrast, so a
    with/without transformation can make the promise concrete.
  playbook_fit:
    source_bite_fit: 5
    offer_fit: 5
    audience_fit: 4
    visual_distinctiveness: 4
    conversion_pattern_fit: 4
  external_pattern_signal:
    source_type: grok_synthesis
    pattern: with_without_transformation
    confidence: medium
    primary_source_verified: false
  reference_influence_test:
    mode: text_traits
    effect_on_specificity: 4
    effect_on_native_feed_fit: 4
    effect_on_ai_slop_risk: 2
  reference_influence:
    mode: text_traits
    influence_score: null
    copy_risk: pass
  likely_click_reason: The operator can see the cost of scattered context and the
    relief of a durable operating folder.
  creative_playbook:
    id: with_without_transformation
    status: candidate
  review:
    status: accepted
    decision: accept
    one_second_clarity: pass
    visual_hook_strength: pass
    ad_usefulness: pass
    source_bite_fit: pass
    genericness_risk: pass
    avoidance_strategy_fit: pass
    avoidance_risk: pass
    prompt_record_complete: pass
    reference_copy_risk: pass
    export_readiness: pass
    readability: pass
    placement_fit: pass
    brand_fit: pass
    claim_safety: pass
    fake_ui_risk: pass
    policy_risk: pass
    private_data_risk: pass
    ai_generic_risk: pass
    click_reason_fit: pass
    visual_quality:
      composition: 5
      style: 5
      polish_control: 5
    ad_quality:
      thumb_stop: 5
      problem_clarity: 5
      desire_clarity: 5
      curiosity_gap: 5
      offer_relevance: 5
      likely_click_reason: The operator can see the cost of scattered context and
        the relief of a durable operating folder.
    risk:
      ai_slop_risk: 1
      genericness_risk: 1
      compliance_risk: pass
    avoidance_check:
      stock_photo_risk: pass
      website_hero_risk: pass
      clean_desk_cliche_risk: pass
      generic_saas_risk: pass
      ai_slop_risk: pass
      overpolished_risk: pass
      native_feed_fit: 5
      too_safe_to_stop_scroll: pass
      notes: []
    scores:
      one_second_clarity: 5
      visual_hook_strength: 5
      specificity: 5
      brand_fit: 5
      source_bite_fit: 5
      specific_to_this_offer: 5
      native_feed_fit: 5
      export_readiness: 5
      ai_generic_risk: 1
    notes: []
- status: planned
  prompt_strategy: creative_director_brief_first_no_text_base
  viewer_scroll_context: cold Facebook feed
  placement: facebook_feed_portrait_4x5
  placement_details: *id006
  text_overlay_plan: text-free base image; deterministic overlay later
  source_files: *id008
  references: *id010
  reference_trait_extraction: *id011
  claim_boundary: do not imply automatic decisions, guaranteed outcomes, or provider
    partnership
  negative_constraints: *id012
  concept_id: crossed-out-tools
  prompt_key: crossed-out-tools.v1
  source_bite:
    source_file: research/customer-language.md
    source_type: problem_list
    extracted_phrase: I forgot the decision, the offer, and the next step
    insight: The pain is a cluster of repeated operating-memory failures.
    visual_translation: three unlabeled problem cards crossed out beside one branch-map
      card
  genericness_check:
    could_fit_notion: true
    could_fit_asana: true
    could_fit_quickbooks: false
    could_fit_generic_coaching_offer: true
    could_fit_generic_productivity_app: true
    could_fit_any_coaching_offer: false
    could_fit_accounting_software: false
    specific_to_this_offer: 4
    reason: The decision/offer/next-step trio ties the checklist to the business repo
      model.
  avoidance_strategy:
    avoids:
    - tiny unreadable text
    - generic checklist stock art
    intentionally_uses:
    - crossed-out problem list
    reason: Tests checklist relief while keeping final copy deterministic.
  first_second_read: the recurring memory failures get crossed out
  audience_state: operator loses decisions, offers, and next steps between sessions
  visual_job: make the solution feel like eliminating repeated pains
  visual_metaphor: crossed-out problem cards beside one branch-map card
  composition: bold card layout with three crossed-out icons and one grounded folder
    card
  visual_hierarchy:
    primary_focal_point: crossed-out problem cards
    secondary_focal_point: branch-map card
    text_zone: bottom third
  camera_language: simple poster-card composition
  style_strength: bold, legible, controlled
  emotional_tone: satisfying cleanup
  prompt: Create a text-free Facebook ad base image with three unlabeled problem cards
    crossed out and one clear branch-map card beside them. No readable words, logos,
    UI, customer data, or private details.
  creative_playbook_id: crossed_out_problem_list
  router_inputs:
    niche: founder_tool
    offer_type: open_source_business_os
    audience: solo founder or operator
    proof_available: false
    brand_style: tactile, technical, irreverent
    platform: facebook_feed
    source_bite_type: problem_list
  router_reason: The source bite names multiple repeated pains, so a crossed-out problem
    list can test whether visual checklist relief works.
  playbook_fit:
    source_bite_fit: 4
    offer_fit: 4
    audience_fit: 4
    visual_distinctiveness: 3
    conversion_pattern_fit: 4
  external_pattern_signal:
    source_type: grok_synthesis
    pattern: crossed_out_problem_list
    confidence: medium
    primary_source_verified: false
  reference_influence_test:
    mode: none
    effect_on_specificity: 3
    effect_on_native_feed_fit: 3
    effect_on_ai_slop_risk: 3
  reference_influence:
    mode: none
    influence_score: null
    copy_risk: pass
  likely_click_reason: The operator recognizes three repeated pains at once.
  creative_playbook:
    id: crossed_out_problem_list
    status: candidate
  review:
    status: accepted
    decision: accept
    one_second_clarity: pass
    visual_hook_strength: pass
    ad_usefulness: pass
    source_bite_fit: pass
    genericness_risk: pass
    avoidance_strategy_fit: pass
    avoidance_risk: pass
    prompt_record_complete: pass
    reference_copy_risk: pass
    export_readiness: pass
    readability: pass
    placement_fit: pass
    brand_fit: pass
    claim_safety: pass
    fake_ui_risk: pass
    policy_risk: pass
    private_data_risk: pass
    ai_generic_risk: pass
    click_reason_fit: pass
    visual_quality:
      composition: 5
      style: 5
      polish_control: 5
    ad_quality:
      thumb_stop: 5
      problem_clarity: 5
      desire_clarity: 5
      curiosity_gap: 5
      offer_relevance: 5
      likely_click_reason: The operator recognizes three repeated pains at once.
    risk:
      ai_slop_risk: 1
      genericness_risk: 1
      compliance_risk: pass
    avoidance_check:
      stock_photo_risk: pass
      website_hero_risk: pass
      clean_desk_cliche_risk: pass
      generic_saas_risk: pass
      ai_slop_risk: pass
      overpolished_risk: pass
      native_feed_fit: 5
      too_safe_to_stop_scroll: pass
      notes: []
    scores:
      one_second_clarity: 5
      visual_hook_strength: 5
      specificity: 5
      brand_fit: 5
      source_bite_fit: 5
      specific_to_this_offer: 4
      native_feed_fit: 5
      export_readiness: 5
      ai_generic_risk: 1
    notes: []
- status: planned
  prompt_strategy: creative_director_brief_first_no_text_base
  viewer_scroll_context: cold Facebook feed
  placement: facebook_feed_portrait_4x5
  placement_details: *id006
  text_overlay_plan: text-free base image; deterministic overlay later
  source_files: *id008
  references: *id010
  reference_trait_extraction: *id011
  claim_boundary: do not imply automatic decisions, guaranteed outcomes, or provider
    partnership
  negative_constraints: *id012
  concept_id: founder-pov-checkpoint
  prompt_key: founder-pov-checkpoint.v1
  source_bite:
    source_file: pushes/2026-05-13-openai-image-rail-dogfood/push.md
    source_type: founder_note
    extracted_phrase: what did we decide last time?
    insight: The ad can start from the founder's own return-to-work moment.
    visual_translation: first-person hand opening a checkpoint folder next to yesterday's
      notes
  genericness_check:
    could_fit_notion: true
    could_fit_asana: false
    could_fit_quickbooks: false
    could_fit_generic_coaching_offer: false
    could_fit_generic_productivity_app: true
    could_fit_any_coaching_offer: false
    could_fit_accounting_software: false
    specific_to_this_offer: 4
    reason: The checkpoint and decision-memory language tie the POV to Main Branch.
  avoidance_strategy:
    avoids:
    - stock-photo founder pose
    - fake testimonial
    - polished office
    intentionally_uses:
    - founder point of view
    reason: Keeps the scene first-person and tactile rather than influencer-style.
  first_second_read: opening yesterday's decision checkpoint
  audience_state: founder is resuming after a context gap
  visual_job: make preserved decision memory feel personal
  visual_metaphor: hand opening a checkpoint folder beside yesterday's notes
  composition: first-person phone-camera view of hand, folder, and scattered notes
  visual_hierarchy:
    primary_focal_point: hand opening checkpoint folder
    secondary_focal_point: yesterday notes
    text_zone: upper left
  camera_language: first-person founder POV
  style_strength: native, imperfect, close-range
  emotional_tone: relief on return
  prompt: 'Create a first-person founder POV Facebook ad base image: a hand opens
    a plain checkpoint folder beside yesterday''s messy notes. No readable words,
    face, logos, UI, customer data, or private details.'
  creative_playbook_id: founder_pov
  router_inputs:
    niche: founder_tool
    offer_type: open_source_business_os
    audience: solo founder or operator
    proof_available: false
    brand_style: tactile, technical, irreverent
    platform: facebook_feed
    source_bite_type: founder_note
  router_reason: The source bite is a founder/operator moment, so first-person desk
    perspective is a better test than a polished product scene.
  playbook_fit:
    source_bite_fit: 4
    offer_fit: 4
    audience_fit: 5
    visual_distinctiveness: 4
    conversion_pattern_fit: 3
  external_pattern_signal:
    source_type: grok_synthesis
    pattern: founder_pov
    confidence: low
    primary_source_verified: false
  reference_influence_test:
    mode: text_traits
    effect_on_specificity: 4
    effect_on_native_feed_fit: 5
    effect_on_ai_slop_risk: 2
  reference_influence:
    mode: text_traits
    influence_score: null
    copy_risk: pass
  likely_click_reason: The viewpoint feels like the viewer's own work session.
  creative_playbook:
    id: founder_pov
    status: candidate
  review:
    status: accepted
    decision: accept
    one_second_clarity: pass
    visual_hook_strength: pass
    ad_usefulness: pass
    source_bite_fit: pass
    genericness_risk: pass
    avoidance_strategy_fit: pass
    avoidance_risk: pass
    prompt_record_complete: pass
    reference_copy_risk: pass
    export_readiness: pass
    readability: pass
    placement_fit: pass
    brand_fit: pass
    claim_safety: pass
    fake_ui_risk: pass
    policy_risk: pass
    private_data_risk: pass
    ai_generic_risk: pass
    click_reason_fit: pass
    visual_quality:
      composition: 5
      style: 5
      polish_control: 5
    ad_quality:
      thumb_stop: 5
      problem_clarity: 5
      desire_clarity: 5
      curiosity_gap: 5
      offer_relevance: 5
      likely_click_reason: The viewpoint feels like the viewer's own work session.
    risk:
      ai_slop_risk: 1
      genericness_risk: 1
      compliance_risk: pass
    avoidance_check:
      stock_photo_risk: pass
      website_hero_risk: pass
      clean_desk_cliche_risk: pass
      generic_saas_risk: pass
      ai_slop_risk: pass
      overpolished_risk: pass
      native_feed_fit: 5
      too_safe_to_stop_scroll: pass
      notes: []
    scores:
      one_second_clarity: 5
      visual_hook_strength: 5
      specificity: 5
      brand_fit: 5
      source_bite_fit: 5
      specific_to_this_offer: 4
      native_feed_fit: 5
      export_readiness: 5
      ai_generic_risk: 1
    notes: []
- status: planned
  prompt_strategy: creative_director_brief_first_no_text_base
  viewer_scroll_context: cold Facebook feed
  placement: facebook_feed_portrait_4x5
  placement_details: *id006
  text_overlay_plan: text-free base image; deterministic overlay later
  source_files: *id008
  references: *id010
  reference_trait_extraction: *id011
  claim_boundary: do not imply automatic decisions, guaranteed outcomes, or provider
    partnership
  negative_constraints: *id012
  concept_id: high-contrast-context-poster
  prompt_key: high-contrast-context-poster.v1
  source_bite:
    source_file: research/customer-language.md
    source_type: customer_language
    extracted_phrase: starting from zero every Monday
    insight: The emotional hook is the waste of restarting context.
    visual_translation: a stark reset button cracked by a small branch map
  genericness_check:
    could_fit_notion: true
    could_fit_asana: true
    could_fit_quickbooks: false
    could_fit_generic_coaching_offer: true
    could_fit_generic_productivity_app: true
    could_fit_any_coaching_offer: true
    could_fit_accounting_software: false
    specific_to_this_offer: 4
    reason: The branch-map reset visual narrows a broad restart frustration.
  avoidance_strategy:
    avoids:
    - casual meme template
    - generic motivational poster
    - glossy 3D icon
    intentionally_uses:
    - high contrast poster
    reason: Tests thumb-stop with a poster frame without drifting into meme tone.
  first_second_read: stop starting from zero
  audience_state: operator dreads rebuilding context at the start of the week
  visual_job: create a sharp pattern interrupt around reset fatigue
  visual_metaphor: cracked reset button interrupted by a small branch map
  composition: high-contrast poster object scene, large reset object, branch-map detail
  visual_hierarchy:
    primary_focal_point: cracked reset object
    secondary_focal_point: branch-map detail
    text_zone: top third
  camera_language: bold poster-like still life
  style_strength: high contrast, spare, tactile
  emotional_tone: frustrated pattern interrupt
  prompt: 'Create a text-free high-contrast Facebook ad base image: a stark reset
    button-like object cracked by a small branch-map detail. No rendered words, logos,
    UI, customer data, or private details.'
  creative_playbook_id: high_contrast_poster
  router_inputs:
    niche: founder_tool
    offer_type: open_source_business_os
    audience: solo founder or operator
    proof_available: false
    brand_style: tactile, technical, irreverent
    platform: facebook_feed
    source_bite_type: customer_language
  router_reason: The source bite is emotionally simple, so a high-contrast poster
    tests thumb-stop without leaning into casual meme language.
  playbook_fit:
    source_bite_fit: 4
    offer_fit: 4
    audience_fit: 3
    visual_distinctiveness: 5
    conversion_pattern_fit: 3
  external_pattern_signal:
    source_type: grok_synthesis
    pattern: high_contrast_poster
    confidence: low
    primary_source_verified: false
  reference_influence_test:
    mode: none
    effect_on_specificity: 3
    effect_on_native_feed_fit: 3
    effect_on_ai_slop_risk: 3
  reference_influence:
    mode: none
    influence_score: null
    copy_risk: pass
  likely_click_reason: The stark visual makes the continuity pain impossible to miss.
  creative_playbook:
    id: high_contrast_poster
    status: candidate
  review:
    status: accepted
    decision: accept
    one_second_clarity: pass
    visual_hook_strength: pass
    ad_usefulness: pass
    source_bite_fit: pass
    genericness_risk: pass
    avoidance_strategy_fit: pass
    avoidance_risk: pass
    prompt_record_complete: pass
    reference_copy_risk: pass
    export_readiness: pass
    readability: pass
    placement_fit: pass
    brand_fit: pass
    claim_safety: pass
    fake_ui_risk: pass
    policy_risk: pass
    private_data_risk: pass
    ai_generic_risk: pass
    click_reason_fit: pass
    visual_quality:
      composition: 5
      style: 5
      polish_control: 5
    ad_quality:
      thumb_stop: 5
      problem_clarity: 5
      desire_clarity: 5
      curiosity_gap: 5
      offer_relevance: 5
      likely_click_reason: The stark visual makes the continuity pain impossible to
        miss.
    risk:
      ai_slop_risk: 1
      genericness_risk: 1
      compliance_risk: pass
    avoidance_check:
      stock_photo_risk: pass
      website_hero_risk: pass
      clean_desk_cliche_risk: pass
      generic_saas_risk: pass
      ai_slop_risk: pass
      overpolished_risk: pass
      native_feed_fit: 5
      too_safe_to_stop_scroll: pass
      notes: []
    scores:
      one_second_clarity: 5
      visual_hook_strength: 5
      specificity: 5
      brand_fit: 5
      source_bite_fit: 5
      specific_to_this_offer: 4
      native_feed_fit: 5
      export_readiness: 5
      ai_generic_risk: 1
    notes: []
assets:
- asset_id: fake-openai-image-001
  concept_id: lost-thread-branch-map
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt_key: lost-thread-branch-map.v1
  prompt: 'Create a fixture-safe Facebook feed image-ad base for a fictional business

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

    information.'
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    requested_aspect_ratio: '2:3'
    placement: facebook_feed_portrait_4x5
    placement_aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    final_export_size: 1080x1350
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
    generation_size_override: batch_portrait_override
    generation_size_override_note: >-
      This dogfood batch intentionally used one provider size, 1024x1536,
      for all candidates. Concept placement metadata remains in
      concepts[].placement_details and was not used for per-asset provider sizing.
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/images/fake-openai-image-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: rejected
  review:
    decision: reject
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    reason_codes:
    - generic_ai_image_feel
    - not_native_to_feed
    - weak_ad_click_reason
    notes:
    - Rejected as part of the all-rejected manual batch review.
    - No deterministic overlay was tested because no generated base image passed the ad-quality bar.
  safe_to_share: true
  generated_at: '2026-05-13T22:44:17+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only; keep
    any generated binary in configured private media storage.
- asset_id: operator-before-after-chaos-001
  concept_id: operator-before-after-chaos
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt_key: durable-memory-archive-map.v1
  prompt: Create a fixture-safe square Facebook ad base image for a fictional business
    operating system. Show scattered paper fragments forming a clean business map.
    No text, logos, screenshots, private data, or real brands.
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    requested_aspect_ratio: '2:3'
    placement: facebook_feed_portrait_4x5
    placement_aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    final_export_size: 1080x1350
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
    generation_size_override: batch_portrait_override
    generation_size_override_note: >-
      This dogfood batch intentionally used one provider size, 1024x1536,
      for all candidates. Concept placement metadata remains in
      concepts[].placement_details and was not used for per-asset provider sizing.
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/images/operator-before-after-chaos-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: rejected
  review:
    decision: reject
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    reason_codes:
    - generic_ai_image_feel
    - not_native_to_feed
    - weak_ad_click_reason
    notes:
    - Rejected as part of the all-rejected manual batch review.
    - No deterministic overlay was tested because no generated base image passed the ad-quality bar.
  safe_to_share: true
  generated_at: '2026-05-13T22:44:17+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only; keep
    any generated binary in configured private media storage.
- asset_id: mobile-safe-progress-path-001
  concept_id: mobile-safe-progress-path
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt_key: mobile-safe-progress-path.v1
  prompt: Create a vertical 9:16 Facebook story ad base image for a fictional business
    planning tool. A narrow lit path moves through launch notes toward one simple
    checkpoint. Keep all critical detail in the center safe zone. No text, UI, logos,
    screenshots, account data, or private details.
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    requested_aspect_ratio: '2:3'
    placement: facebook_feed_portrait_4x5
    placement_aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    final_export_size: 1080x1350
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
    generation_size_override: batch_portrait_override
    generation_size_override_note: >-
      This dogfood batch intentionally used one provider size, 1024x1536,
      for all candidates. Concept placement metadata remains in
      concepts[].placement_details and was not used for per-asset provider sizing.
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/images/mobile-safe-progress-path-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: rejected
  review:
    decision: reject
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    reason_codes:
    - generic_ai_image_feel
    - not_native_to_feed
    - weak_ad_click_reason
    notes:
    - Rejected as part of the all-rejected manual batch review.
    - No deterministic overlay was tested because no generated base image passed the ad-quality bar.
  safe_to_share: true
  generated_at: '2026-05-13T22:44:17+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only; keep
    any generated binary in configured private media storage.
- asset_id: app-sprawl-native-scene-001
  concept_id: app-sprawl-native-scene
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt_key: app-sprawl-native-scene.v1
  prompt: Create a feed-native phone-style Facebook ad base image showing a founder
    desk with too many browser tabs, handwritten notes, and one plain business folder
    anchoring the mess. No readable text, UI, logos, customer data, or private details.
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    requested_aspect_ratio: '2:3'
    placement: facebook_feed_portrait_4x5
    placement_aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    final_export_size: 1080x1350
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
    generation_size_override: batch_portrait_override
    generation_size_override_note: >-
      This dogfood batch intentionally used one provider size, 1024x1536,
      for all candidates. Concept placement metadata remains in
      concepts[].placement_details and was not used for per-asset provider sizing.
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/images/app-sprawl-native-scene-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: rejected
  review:
    decision: reject
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    reason_codes:
    - generic_ai_image_feel
    - not_native_to_feed
    - weak_ad_click_reason
    notes:
    - Rejected as part of the all-rejected manual batch review.
    - No deterministic overlay was tested because no generated base image passed the ad-quality bar.
  safe_to_share: true
  generated_at: '2026-05-13T22:44:17+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only; keep
    any generated binary in configured private media storage.
- asset_id: myth-vs-folder-001
  concept_id: myth-vs-folder
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt_key: myth-vs-folder.v1
  prompt: Create a text-free Facebook ad base image that visually contrasts a faded
    pile of generic unlabeled app tiles with one tactile local business folder. No
    rendered words, real logos, UI, customer data, or private details.
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    requested_aspect_ratio: '2:3'
    placement: facebook_feed_portrait_4x5
    placement_aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    final_export_size: 1080x1350
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
    generation_size_override: batch_portrait_override
    generation_size_override_note: >-
      This dogfood batch intentionally used one provider size, 1024x1536,
      for all candidates. Concept placement metadata remains in
      concepts[].placement_details and was not used for per-asset provider sizing.
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/images/myth-vs-folder-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: rejected
  review:
    decision: reject
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    reason_codes:
    - generic_ai_image_feel
    - not_native_to_feed
    - weak_ad_click_reason
    notes:
    - Rejected as part of the all-rejected manual batch review.
    - No deterministic overlay was tested because no generated base image passed the ad-quality bar.
  safe_to_share: true
  generated_at: '2026-05-13T22:44:17+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only; keep
    any generated binary in configured private media storage.
- asset_id: with-without-context-001
  concept_id: with-without-context
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt_key: with-without-context.v1
  prompt: 'Create a text-free Facebook feed ad base image showing a before/after operating-memory
    contrast: repeated sticky-note explanations resolving into one connected branch
    map. No readable words, logos, UI, customer data, or private details.'
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    requested_aspect_ratio: '2:3'
    placement: facebook_feed_portrait_4x5
    placement_aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    final_export_size: 1080x1350
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
    generation_size_override: batch_portrait_override
    generation_size_override_note: >-
      This dogfood batch intentionally used one provider size, 1024x1536,
      for all candidates. Concept placement metadata remains in
      concepts[].placement_details and was not used for per-asset provider sizing.
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/images/with-without-context-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: rejected
  review:
    decision: reject
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    reason_codes:
    - generic_ai_image_feel
    - not_native_to_feed
    - weak_ad_click_reason
    notes:
    - Rejected as part of the all-rejected manual batch review.
    - No deterministic overlay was tested because no generated base image passed the ad-quality bar.
  safe_to_share: true
  generated_at: '2026-05-13T22:44:17+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only; keep
    any generated binary in configured private media storage.
- asset_id: crossed-out-tools-001
  concept_id: crossed-out-tools
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt_key: crossed-out-tools.v1
  prompt: Create a text-free Facebook ad base image with three unlabeled problem cards
    crossed out and one clear branch-map card beside them. No readable words, logos,
    UI, customer data, or private details.
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    requested_aspect_ratio: '2:3'
    placement: facebook_feed_portrait_4x5
    placement_aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    final_export_size: 1080x1350
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
    generation_size_override: batch_portrait_override
    generation_size_override_note: >-
      This dogfood batch intentionally used one provider size, 1024x1536,
      for all candidates. Concept placement metadata remains in
      concepts[].placement_details and was not used for per-asset provider sizing.
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/images/crossed-out-tools-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: rejected
  review:
    decision: reject
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    reason_codes:
    - generic_ai_image_feel
    - not_native_to_feed
    - weak_ad_click_reason
    notes:
    - Rejected as part of the all-rejected manual batch review.
    - No deterministic overlay was tested because no generated base image passed the ad-quality bar.
  safe_to_share: true
  generated_at: '2026-05-13T22:44:17+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only; keep
    any generated binary in configured private media storage.
- asset_id: founder-pov-checkpoint-001
  concept_id: founder-pov-checkpoint
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt_key: founder-pov-checkpoint.v1
  prompt: 'Create a first-person founder POV Facebook ad base image: a hand opens
    a plain checkpoint folder beside yesterday''s messy notes. No readable words,
    face, logos, UI, customer data, or private details.'
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    requested_aspect_ratio: '2:3'
    placement: facebook_feed_portrait_4x5
    placement_aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    final_export_size: 1080x1350
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
    generation_size_override: batch_portrait_override
    generation_size_override_note: >-
      This dogfood batch intentionally used one provider size, 1024x1536,
      for all candidates. Concept placement metadata remains in
      concepts[].placement_details and was not used for per-asset provider sizing.
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/images/founder-pov-checkpoint-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: rejected
  review:
    decision: reject
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    reason_codes:
    - generic_ai_image_feel
    - not_native_to_feed
    - weak_ad_click_reason
    notes:
    - Rejected as part of the all-rejected manual batch review.
    - No deterministic overlay was tested because no generated base image passed the ad-quality bar.
  safe_to_share: true
  generated_at: '2026-05-13T22:44:17+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only; keep
    any generated binary in configured private media storage.
- asset_id: high-contrast-context-poster-001
  concept_id: high-contrast-context-poster
  rail: provider
  provider: openai
  model: gpt-image-2
  model_snapshot: gpt-image-2-2026-04-21
  endpoint: v1/images/generations
  docs_checked: '2026-05-13'
  state: generated
  blocker_code: null
  blocker: null
  credential_ref: openai:image-generation
  credential_state: configured_env
  prompt_key: high-contrast-context-poster.v1
  prompt: 'Create a text-free high-contrast Facebook ad base image: a stark reset
    button-like object cracked by a small branch-map detail. No rendered words, logos,
    UI, customer data, or private details.'
  source_context:
  - path: pushes/2026-05-13-openai-image-rail-dogfood/image-index.md
    role: fake_push_context
    safe_to_share: true
  - path: fixture:fictional-northstar-ledger
    role: source_brief
    safe_to_share: true
  references: []
  dimensions:
    requested_size: 1024x1536
    requested_aspect_ratio: '2:3'
    placement: facebook_feed_portrait_4x5
    placement_aspect_ratio: '4:5'
    nearest_provider_size: 1024x1536
    final_export_size: 1080x1350
    format: png
    quality: medium
    generated_width: 1024
    generated_height: 1536
    generation_size_override: batch_portrait_override
    generation_size_override_note: >-
      This dogfood batch intentionally used one provider size, 1024x1536,
      for all candidates. Concept placement metadata remains in
      concepts[].placement_details and was not used for per-asset provider sizing.
  output_reference: mb-media://pushes/2026-05-13-openai-image-rail-dogfood/images/high-contrast-context-poster-001.png
  storage_backend: mb-media
  committed_binary: false
  retries: 0
  timeout_seconds: 60
  cost:
    estimate: unknown_token_metered
    actual: unknown
    usage: null
  review_status: rejected
  review:
    decision: reject
    reviewer: operator
    reviewed_from: ignored local contact sheet and image folder
    reason_codes:
    - generic_ai_image_feel
    - not_native_to_feed
    - weak_ad_click_reason
    notes:
    - Rejected as part of the all-rejected manual batch review.
    - No deterministic overlay was tested because no generated base image passed the ad-quality bar.
  safe_to_share: true
  generated_at: '2026-05-13T22:44:17+00:00'
  operator_notes: Fixture-safe OpenAI image rail smoke. Commit this record only; keep
    any generated binary in configured private media storage.
```
