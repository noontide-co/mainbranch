---
date: 2026-05-13
status: accepted
tags: [ads, creative, skills, providers, review-board]
---

# Ad Creative Readiness, Playbooks, And Review Board

## Decision

Treat MAIN-374 as the first ad creative production-loop experiment, not a
batch-image factory.

The production loop is:

```text
repo facts -> ad readiness -> source bites -> playbook router -> concepts ->
official API generation or fallback -> scoring -> local review board ->
image-index.md and distilled findings
```

The review question is:

```text
Which playbook produced the best actual ad candidate?
```

Do not reduce the review to:

```text
Which image looked best?
```

## Layer Boundaries

- `mb start` and `mb status` expose deterministic repo, MoneyPath, provider,
  graph, and readiness facts.
- `/mb-ads` owns strategy, source-bite extraction, creative playbook routing,
  prompt records, operator-facing guidance, and human review.
- `mb ads meta summary --json` is optional read-only Meta context only after
  the operator approves it and provider readiness is present.
- `mb image` and future image commands own provider calls, safe JSON, media
  storage boundaries, local review-board writing, and push-local
  `image-index.md` records.
- Local ignored scratch owns raw generated images, contact sheets, and review
  boards.
- Committed repo memory owns safe `image-index.md` records, prompt keys, source
  bites, candidate scores, decisions, and distilled findings.

Raw provider payloads, generated binaries, screenshots, private paths,
credentials, account data, raw Grok dumps, and unverified claims do not belong
in committed records.

## Ad Readiness Gate

Final ad generation requires:

```yaml
ad_readiness:
  state: ready | partial | blocked
  required_fields:
    - offer
    - audience
    - campaign_goal
    - claim_proof_boundary
  hard_stop_missing: []
  soft_warning_missing:
    - proof
    - customer_language
    - brand_visual_style
    - prior_outcomes
    - meta_summary
    - reference_images
  allowed_actions:
    - intake
    - repo_source_audit
    - ad_strategy_outline
    - missing_info_checklist
    - exploration_concepts
    - api_generation
    - final_ad_package
  blocked_actions: []
```

If a hard-stop field is missing, set `state: blocked` or `state: partial`, list
the field in `hard_stop_missing`, and do not generate final ads. Create an
intake or source-bite plan, or generate clearly marked low-confidence
exploration concepts only if the operator approves.

Suggested refusal:

```text
Missing required fields for production ads: [list]. I can create an intake
plan, or generate low-confidence exploration concepts clearly marked as
placeholders.
```

This is a quality gate, not busywork. The system should not invent offer facts,
audience facts, proof, or claim boundaries.

## Source Bites Before Prompts

Every concept needs a source bite before provider generation:

```yaml
source_bite:
  source_file:
  source_type:
  extracted_phrase:
  insight:
  visual_translation:
```

If there is no source bite, mark the concept `source_light: true` and block
provider generation unless the operator explicitly approves broad exploration.

## Playbook Router Metadata

Creative playbooks are emerging router metadata, not a canonized library yet.
MAIN-374 should test which categories actually produce usable ad candidates
before hardening a schema or weights.

Initial IDs:

```text
native_problem_scene
specific_object_metaphor
proof_artifact
myth_vs_fact
with_without_transformation
crossed_out_problem_list
founder_pov
high_contrast_poster
simple_chart_comparison
testimonials_with_artifact
us_vs_them_split
simple_list_framework
```

Use `high_contrast_poster` instead of `bold_meme_poster` so the router does
not bias the system too casual. Treat `native_collage` as part of
`native_problem_scene` until a batch proves it deserves its own playbook.

Each candidate records:

```yaml
candidate_id:
creative_playbook_id:
router_inputs:
  offer_type:
  audience:
  source_bite_type:
  proof_available:
  brand_style:
  platform:
router_reason:
playbook_fit:
  source_bite_fit: 1-5
  offer_fit: 1-5
  audience_fit: 1-5
  visual_distinctiveness: 1-5
  conversion_pattern_fit: 1-5
```

Use `conversion_informed` or "conversion-informed" for patterns unless live
account outcome data proves performance. Do not claim Main Branch generates
high-converting ads.

## Scoring Doctrine

Separate image quality from ad quality:

```yaml
visual_quality:
  composition: 1-5
  style: 1-5
  polish_control: 1-5
ad_quality:
  thumb_stop: 1-5
  problem_clarity: 1-5
  desire_clarity: 1-5
  curiosity_gap: 1-5
  offer_relevance: 1-5
  likely_click_reason: string
risk:
  ai_slop_risk: 1-5
  genericness_risk: 1-5
  compliance_risk: pass | warning | fail
```

Hard reject:

- `ai_slop_risk >= 4`;
- `genericness_risk >= 4`;
- `compliance_risk = fail`;
- beautiful image with no likely click reason.

Rule:

```text
Beautiful but no click reason = reject.
```

## Review Board Boundary

The local review board or contact sheet is ignored scratch. It may include raw
visual comparison and local media references. The committed repo should contain
only safe records:

- source bites;
- prompt keys;
- playbook IDs and router reasons;
- provider/model metadata;
- safe logical media references;
- review scores and decisions;
- distilled findings.

## Future Dashboard Boundary

A future local dashboard should read these records, not own creative or provider
logic:

```text
CLI = facts and safe checks
skills = workflow and judgment
repo files = memory
dashboard = visual map
```

The image-index record should remain structured enough for a read-only local
dashboard to show ad readiness, missing inputs, source bites, playbook router
choices, image candidates, review scores, best candidate or rejection state,
provider readiness, and next actions. It should not require secrets, raw
provider payloads, private paths, or committed image binaries.

Public evidence should be sanitized:

```text
generated_count=8-12
provider=openai
model=gpt-image-2
binary_committed=false
review_board_written=true
best_candidate=<asset_id> or all_rejected=true
best_playbook=<playbook_id> or none
overlay_tested=true/false
```

If the provider call is blocked or not approved, the record must say so instead
of implying visual quality proof:

```text
generated_count=0
best_candidate=null
best_playbook=null
all_rejected=null
overlay_tested=false
main_failure_modes=[provider_generation_not_run, no_visual_quality_proven, overlay_not_tested]
```

## External Research Boundary

Grok, swipe files, ad libraries, Reddit, X threads, and agency blogs can inform
pattern selection, but unverified synthesis is scratch/source signal only:

```yaml
external_pattern_signal:
  source_type: grok_synthesis | swipe_file | ad_library | reddit | x_thread | agency_blog
  pattern:
  confidence: low | medium | high
  primary_source_verified: false
```

Do not commit raw Grok dumps, screenshots, exact competitor ads, or unverified
performance claims.

## Reference Influence Hook

Full reference-image copy prevention is follow-up work. For now, keep the
metadata hook:

```yaml
reference_influence:
  mode: none | text_traits | image_reference
  influence_score: null
  copy_risk: pass | warning | fail
```

When a provider cannot use actual image references, convert approved references
into text traits and record what to borrow and what not to copy.

## Out Of Scope

- Meta publishing or campaign creation.
- Broad model routing.
- Full reference hashing and copy-prevention.
- Weekly creative learning automation.
- Performance feedback into router weights.
- Claims that Main Branch generates high-converting ads.

## Follow-Ups

- Reference image system, influence scoring, and copy-prevention.
- Weekly creative learning loop and ad-library research workflow.
- Full playbook library and router weight tuning.
- Outcome feedback loop from Meta performance into playbook scores.
