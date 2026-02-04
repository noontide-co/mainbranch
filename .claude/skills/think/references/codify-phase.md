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
5. **Mark complete** — Update decision status from `accepted` to `codified`
6. **Report changes** — Summary of what was updated

---

## Invoking

```
/think codify decisions/2026-01-17-pricing-strategy.md
```

Or naturally: "/think apply the pricing decision to reference files"

---

## Safety Rules

1. **Always read before writing** — Never overwrite without reading first
2. **Preserve structure** — Keep existing headings and organization
3. **Add, don't replace** — New content supplements, doesn't overwrite
4. **Mark additions** — Use date comments for traceability: `<!-- Added 2026-01-17 -->`
5. **Confirm before large changes** — If changing >30% of a file, ask first
6. **Atomic updates** — Complete all or none

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

When `current_offer` is set (multi-offer mode), audit offer-specific files first, then core files:

| File | Status | Gaps |
|------|--------|------|
| offers/[active]/offer.md | Good | - |
| offers/[active]/audience.md | Thin | Missing objections |
| core/offer.md (brand-level) | Good | - |
| core/audience.md (brand-level) | Good | - |
| core/voice.md | Empty | Needs everything |
| proof/testimonials.md | Thin | Only 1 testimonial |
| proof/angles/ | Empty | No angles documented |

When in single-offer mode (no `offers/` folder), use the standard table:

| File | Status | Gaps |
|------|--------|------|
| core/offer.md | Good | - |
| core/audience.md | Thin | Missing objections |
| core/voice.md | Empty | Needs everything |
| proof/testimonials.md | Thin | Only 1 testimonial |
| proof/angles/ | Empty | No angles documented |

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
| offers/community/offer.md | Added three-tier pricing section |
| core/offer.md | Updated brand thesis to reflect multi-tier positioning |
| core/voice.md | Added 5 phrases, 3 personality markers |
| proof/testimonials.md | Added 3 new testimonials |

**Still missing:** [anything not addressed]
```

**Target resolution:** When `current_offer` is set, offer-specific changes go to `offers/[active]/`. Brand-level changes go to `core/`. If unsure whether a change is offer-specific or brand-level, ask the user.

---

## Content Strategy Updates

When codifying decisions about content pillars, platform selection, cadence, or content performance, update `reference/domain/content-strategy.md`. Sections to update:

| Decision About | Update Section |
|----------------|----------------|
| New pillar discovered | **Content Pillars** — add pillar with sub-topics and three tests (soul, offer, audience) |
| Platform added or removed | **Platform Strategy** — update priority-ordered platform list |
| Winning hook identified | **Hooks Library** — add hook with context and performance |
| New framework extracted | **Framework Library** — add framework with source and transfer notes |
| New benchmark established | **Metrics** — update PRP benchmarks or review cadence |
| Content mix ratio adjusted | **Content Mix** — update ratios based on performance data |
| Cadence changed | **Weekly Cadence** — update day-by-day plan |

**How /think cycles update content-strategy.md:**

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

If `content-strategy.md` does not exist and the user is codifying content-related decisions, suggest creating it: "This looks like content strategy work. Want to create `reference/domain/content-strategy.md` to store this?" See `setup/references/templates.md` for the template, and `help/references/content-strategy-help.md` for user-facing FAQ.

---

## Exit Criteria

Codification is complete when:

- All changes described in the decision have been applied to reference files
- Source decision status changed from `accepted` to `codified`
- User confirms the reference file updates capture the decision
