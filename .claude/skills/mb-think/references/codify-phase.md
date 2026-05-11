# Codify Phase

Apply decisions to reference files. Merges research findings and decisions into evergreen reference.

---

## When to Use

- After a decision with `status: accepted`
- When research findings should update reference files
- When user has new context to add (testimonials, angles, proof)
- When business has changed and reference files need updating

---

## Workflow

1. **Read source** — Decision file or research file
2. **Identify what changes** — Read the `## What Changes` section (or infer from `## Decision` and `## Consequences` if What Changes is missing). Identify which reference files are affected and what the key changes are.
3. **Propose edits** — For each affected reference file, read it, then propose the specific update to the user.
4. **Apply with confirmation** — After user confirms, apply each update. Preserve existing content.
5. **Atomic finalize pass** — In the SAME edit pass as the final reference file update, flip the source decision from `status: accepted` to `status: codified`. This is the most likely dropped step; treat it as part of the final edit unit, never a follow-up.
6. **Verify read-back** — Re-open the source decision file and confirm frontmatter contains exactly one `status:` field and that it is `codified`.
7. **Report changes** — Summary of what was updated

---

## Invoking

```
/mb-think codify decisions/2026-01-17-pricing-strategy.md
```

Or naturally: "/mb-think apply the pricing decision to reference files"

---

## Safety Rules

1. **Always read before writing** — Never overwrite without reading first
2. **Preserve structure** — Keep existing headings and organization
3. **Add, don't replace** — New content supplements, doesn't overwrite
4. **Mark additions** — Use date comments for traceability: `<!-- Added 2026-01-17 -->`
5. **Confirm before large changes** — If changing >30% of a file, ask first
6. **Atomic updates** — Complete all or none. The decision status flip (`accepted` -> `codified`) is part of the same atomic unit as the final reference-file edit.
7. **Write in enduring language** — Reference files should read like they've always been true, not like reactions to specific events. Core beliefs are timeless truths. If a line references a specific tool, session, bug, or conversation — it belongs in an evolution marker or decision file, not in the reference itself. Test: would someone reading this in 6 months with no context understand it? If not, rewrite until they would.
8. **One status field only** — Never add `codified: true` or any parallel lifecycle field. Decision lifecycle state must live only in `status:` using `proposed|accepted|codified`.

---

## Merge Patterns

### Adding Testimonials

```markdown
## Existing Testimonials
[keep all existing]

## New Testimonials (Added 2026-01-17)
[add new ones here]
```

### Adding Objections to Audience

```markdown
## Objections
[existing objections]
- [new objection from today's context]
```

### Updating Offer

```markdown
## Pricing
[existing pricing info]

### Three-Tier Structure (Added 2026-01-17)
[new tier details]
```

---

## Audit Before Codify

When user wants to enrich existing files, audit completeness first.

Use `.claude/reference/business-primitives/offer-bet-push-proof.md` to decide
whether new context updates a bet, offer, push, proof file, or decision. In
multi-offer mode, audit offer-specific files first, then core files:

| File | Status | Gaps |
|------|--------|------|
| core/offers/[active]/offer.md | Good | - |
| core/offers/[active]/audience.md | Thin | Missing objections |
| core/offer.md (brand-level) | Good | - |
| core/audience.md (brand-level) | Good | - |
| core/voice.md | Empty | Needs everything |
| core/proof/testimonials.md | Thin | Only 1 testimonial |
| core/proof/typicality.md | Empty | No aggregate outcome context |
| core/proof/angles/ | Empty | No angles documented |
| core/offers/[active]/proof/ | Empty | No offer-specific proof |

When in single-offer mode (no `offers/` folder), use the standard table:

| File | Status | Gaps |
|------|--------|------|
| core/offer.md | Good | - |
| core/audience.md | Thin | Missing objections |
| core/voice.md | Empty | Needs everything |
| core/proof/testimonials.md | Thin | Only 1 testimonial |
| core/proof/typicality.md | Empty | No aggregate outcome context |
| core/proof/angles/ | Empty | No angles documented |

**Status icons:**
- Good — Meets minimum
- Thin — Exists but incomplete
- Empty — Missing or no content

**Completeness thresholds:**

| File | Minimum for "Good" |
|------|-------------------|
| offer.md | Price + mechanism + deliverables |
| audience.md | Who + 3 pains + 3 desires + 2 objections |
| voice.md | Tone + 5 phrases + personality |
| testimonials.md | 3 testimonials with specific outcomes |
| typicality.md | Average-case outcomes, timelines, caveats, and common failure context |
| angles/ | 2-3 documented angles |

---

## Gathering New Context

When user has new information to add:

**Prompt:** "What would you like to add today? You can:
- Paste text, URLs, or file paths
- Share screenshots
- Brain dump and I'll sort it"

**For URLs:** Try WebFetch, then Chrome, then ask for manual paste.

**Key prompts:**
- "What else do you have? Sales pages, testimonials, emails?"
- "Any client calls or DMs that show how you talk?"
- "What's changed since you last updated these files?"

---

## Change Report

After codifying, show summary. Use offer-qualified paths when in multi-offer mode:

```markdown
## Changes Made

| File | Changes |
|------|---------|
| core/offers/community/offer.md | Added three-tier pricing section |
| core/offer.md | Updated brand thesis to reflect multi-tier positioning |
| core/voice.md | Added 5 phrases, 3 personality markers |
| core/proof/testimonials.md | Added 3 new testimonials |

**Still missing:** [anything not addressed]
```

**Target resolution:** Offer-specific sellable truth goes to
`core/offers/[active]/`. Brand-level truth goes to `core/`. Company-wide proof
uses `core/proof/testimonials.md`, `core/proof/typicality.md`, and
`core/proof/angles/`; offer-specific proof uses matching files under
`core/offers/[active]/proof/`. If the change is still being tested, update or
open a bet instead of rewriting durable offer truth. If unsure, ask the user.

**Compatibility bridges:** In current repos, `reference/core` points at
`core/` and `reference/offers` points at `core/offers/`. These are aliases for
older skill paths, not duplicate files. Write once to the current `core/` or
`core/offers/` target. Only use `reference/core/` or `reference/offers/` as a
legacy fallback when `core/` is absent.

---

## Content Strategy Updates

When codifying decisions about content pillars, platform selection, cadence, or content performance, update `core/content-strategy.md`. Sections to update:

| Decision About | Update Section |
|----------------|----------------|
| New pillar discovered | **Content Pillars** — add pillar with sub-topics and three tests (soul, offer, audience) |
| Platform added or removed | **Platform Strategy** — update priority-ordered platform list |
| Winning hook identified | **Hooks Library** — add hook with context and performance |
| New framework extracted | **Framework Library** — add framework with source and transfer notes |
| New benchmark established | **Metrics** — update PRP benchmarks or review cadence |
| Content mix ratio adjusted | **Content Mix** — update ratios based on performance data |
| Cadence changed | **Weekly Cadence** — update day-by-day plan |
| Named enemy articulated | **Voice.md (Named Enemies section)** — add enemy concept with pillar mapping |
| Saves insight discovered | **Metrics** — weight saves as #1 purchase intent signal above shares/comments |
| New angle or emotional territory found | **core/proof/angles/** — create new angle file. Angles are additive. Check README.md for consistency |

**How /mb-think cycles update content-strategy.md:**

```
Research: "Which platforms does my audience use?"
  → Decide: Platform strategy (Instagram Reels + newsletter)
    → Codify: Update Platform Strategy section in content-strategy.md

Research: "What content themes drive engagement?"
  → Decide: Three pillars (transformation stories, tactical tips, community wins)
    → Codify: Update Content Pillars section in content-strategy.md

Mining: Competitor content analysis
  → Extract: Framework (hook pattern, emotional arc)
    → Codify: Add to Framework Library + Hooks Library in content-strategy.md
```

If `content-strategy.md` does not exist and the user is codifying content-related decisions, suggest creating it: "This looks like content strategy work. Want to create `core/content-strategy.md` to store this?" See `mb-setup/references/templates.md` for the template, and `mb-help/references/content-strategy-help.md` for user-facing FAQ.

---

## Winning-Ad Research Codification

When codifying customer, review, competitor, script, or comment mining, keep the
research source and the evergreen reference separate. Raw extracts stay in
`research/`; only durable conclusions move into `core/`.

| Research Finding | Codify Target |
|------------------|---------------|
| Repeated customer phrases, pains, objections | `core/audience.md` or offer-specific `audience.md` |
| Identity language, named enemies, phrases to use/avoid | `core/voice.md` |
| New emotional entry point or competitor gap | `core/proof/angles/*.md` |
| Permissioned individual testimonial with context | `core/proof/testimonials.md` |
| Average outcomes, typical timelines, caveats, common failures | `core/proof/typicality.md` |
| Proof that applies only to one offer | `core/offers/<slug>/proof/` |
| Hook pattern, content framework, platform cue, comment insight | `core/content-strategy.md` |
| Mechanism story, pricing/distribution vulnerability | `core/offer.md` or offer-specific `offer.md` |
| Live hypothesis, deadline, target, evidence, or verdict | `bets/YYYY-MM-DD-slug.md` |

Do not turn organic comments into proof claims. Comments are demand language
and content signal unless the operator has verified customer outcome evidence.

Do not paste full review exports, call transcripts, scraped comment dumps, or
private customer details into reference files. Use concise source-backed
synthesis and point back to the research file.

---

## Angle Library Updates

When research surfaces a new emotional territory, buyer motivation, or competitive position:

1. Check `core/proof/angles/` for existing angles
2. If the new territory is genuinely distinct from existing angles, create a new angle file
3. Update `core/proof/angles/README.md` to include the new angle in the library index
4. Note: angles are ADDITIVE. New angles supplement existing ones. Never delete or replace angles unless a decision explicitly retires one.

**Common angle emergence patterns:**
- Mining reveals a competitor using an emotional territory you haven't claimed
- Research discovers a named enemy your audience fights but hasn't articulated
- Testimonials reveal a motivation you didn't know existed
- A lifestyle aspiration emerges that doesn't fit existing categories

---

## Named Enemies Updates

When research or decisions identify a named enemy:

1. Check `core/voice.md` for existing Named Enemies section
2. Add the new enemy with its pillar mapping
3. Enemies are ALWAYS concepts, never people or companies
4. Each content pillar should fight one primary enemy
5. Update `core/content-strategy.md` pillar descriptions to reference their enemy

---

## Exit Criteria

Codification is complete when:

- All changes described in the decision have been applied to reference files
- Source decision status changed from `accepted` to `codified`
- Verification read-back confirms frontmatter has exactly one `status:` field and it is `codified`
- User confirms the reference file updates capture the decision
