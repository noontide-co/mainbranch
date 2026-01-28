---
name: ads
description: "Create and review Meta/Facebook/Instagram ads. Routes to: static image ads (copy + AI image prompts), video scripts (15-30 spoken-word scripts), one-liners (30 diversified copy lines for static images), or multi-lens compliance review. Use when asked to create ads, ad copy, image prompts, video scripts, or review ads. Say /ads or ask for static ads, video scripts, one-liners, or ad review."
---

# Ads Skill

Create static ads, video scripts, one-liners, or review ads for compliance.

## Triage

Determine mode from user request:

| Mode | Triggers | Output |
|------|----------|--------|
| **Static** | "static ads", "image ads", "primaries", "headlines", "image prompts" | 5-6 concepts, each with 5 primaries + 5 headlines + 3 image prompts |
| **Video** | "video scripts", "ad scripts", "spoken word", "camera scripts" | 15-30 diverse scripts for spoken delivery |
| **One-Liner** | "one-liners", "30 one-liners", "Andromeda", "diversified static copy" | 30 diversified copy lines for static image ads (Andromeda-optimized) |
| **Review** | "review", "check", "audit", "compliance", "before launch" | P1/P2/P3 report across 6 lenses |

If unclear, ask: "Do you want static image ads, video scripts, one-liners, or a compliance review?"

---

## Reference Required (All Modes)

Before creating ads, the business repo must have:

| File | What It Contains | Required |
|------|------------------|----------|
| `reference/core/offer.md` | What you sell, price, mechanism, benefits | Yes |
| `reference/core/audience.md` | Who buys, their pains, desires | Yes |
| `reference/core/origin.md` | Founder backstory, credibility, unique angle | Selective |
| `reference/core/voice.md` | Tone, phrases, personality | Recommended |
| `reference/proof/testimonials.md` | Testimonials with names and outcomes | Yes |
| `reference/proof/angles/*.md` | Different messaging entry points | Yes |

**origin.md usage:** Not every ad needs founder story. See `vip/.claude/skills/origin/references/usage-guide.md` for when to use vs skip.

If required files are missing, ask user to create them first.

---

## Mode: Static Ads

Create campaign batches with image prompts + ad copy.

### Campaign Structure

Each batch = 5-6 angles. Each angle = 3 image creatives (graphic, lo-fi, interrupt).

```
Campaign Batch 001
├── Angle 1: 001_01 (graphic), 001_02 (lo-fi), 001_03 (interrupt)
├── Angle 2: 001_04, 001_05, 001_06
└── [etc.]
```

### Hook Rules (Non-Negotiable)

**Hook = 123-135 characters** (visible before "See more" on Facebook).

- No questions (binary "no" response)
- No "you/your" in first 3 lines
- No emojis
- Pack customer language into the hook

**Hook Formulas:**
1. **Transformation:** "How [Resonance] go from [Pain] to [Benefit] using [Approach]"
2. **Even Without:** "Here's how even [Resonance] (without [Challenge]) are [Benefit]"
3. **Eliminates:** "This [Approach] eliminates [Pain 1], [Pain 2], without [Challenge]"

### Workflow

1. Read project context (offer, audience, proof, angles)
2. Ask for campaign name (required)
3. Select 5-6 angles for the batch
4. **Write ALL image prompts first** (Part 1)
5. **Write ALL ad copy second** (Part 2)
6. Compliance check
7. Save to `outputs/YYYY-MM-DD-static-ads-{campaign}/static-ads-batch-001.md`
8. Tell user: "Saved to `outputs/YYYY-MM-DD-static-ads-{campaign}/static-ads-batch-001.md`. Want me to commit this to git?"

### Ad Styles (5 per concept)

| Style | Length |
|-------|--------|
| Deep Ad | 500-800 words |
| UGC/Native | 100-300 words |
| Direct Response | 100-400 words |
| Pattern Interrupt | Under 100 words |
| Testimonial | 200-400 words |

### Image Prompt Types

| Type | Use Case |
|------|----------|
| Graphic | Typography-focused, frameworks |
| Lo-fi | UGC style, authenticity |
| Interrupt | Pattern interrupt, scroll-stopping |

See [references/static-output-template.md](references/static-output-template.md) for full output format.

---

## Mode: One-Liner

Generate 30 punchy, truly diversified one-liners for static image ads that feed Meta's Andromeda algorithm.

### Why This Mode Exists

Meta's Andromeda algorithm (July 2025) rewards TRUE creative diversification - not surface variations. 30 one-liners = 30 different psychological conversations, each anchored in offer-specific details.

### 6-Step Process

1. **Core Outcome:** Single transformation every buyer achieves
2. **Extract Specifics:** Roles, timelines, niche pains, value props, failed alternatives, proof points
3. **Reasons to Buy:** 15-20 fundamentally different reasons (the protein supplement exercise)
4. **Hook Categories:** Ensure variety across problem agitation, emotional state, transformation, contrarian, identity callout, etc.
5. **Generate:** 30 one-liners, each with at least one specific anchor
6. **Output:** Simple numbered list, ready to copy

### The Anchor Rule (Non-Negotiable)

Every one-liner **MUST** include at least one specific element:
- A specific role, outcome, or company (DevOps Engineer, AWS, 60k)
- A specific niche pain (service desk 2+ years, no CS degree)
- A specific value prop (mock interviews with Principal Engineers)
- A specific timeline or proof point (8 weeks, 500+ community)

**The Specificity Test:** If this one-liner could sell a gym membership, a life coaching program, or a generic course - it fails. Rewrite it.

### Input Modes

| Mode | How to Detect | What to Pull |
|------|---------------|--------------|
| **Has business repo** | Reference files exist | `reference/core/offer.md`, `reference/core/audience.md`, `reference/core/voice.md`, testimonials |
| **No repo** | Nothing found | Ask user for materials |

### Output Format

**Save to file, not chat.** This enables review to edit the file directly.

1. Ask for campaign name (required)
2. Create folder: `outputs/YYYY-MM-DD-one-liners-{campaign}/`
3. Save full generation context + one-liners to: `one-liners-batch-001.md`
4. Tell user: "Saved 30 one-liners to `outputs/YYYY-MM-DD-one-liners-{campaign}/one-liners-batch-001.md`. Want me to commit this to git?"
5. After git (if accepted), offer: "Want me to run `/ads review` to check for compliance issues?"

**one-liners-batch-001.md format:**

```markdown
---
type: output
subtype: one-liners
date: YYYY-MM-DD
status: draft
review_status: null
---

# One-Liners: {Campaign Name}

## Core Outcome

[Single sentence: the transformation every buyer achieves]

## Extracted Specifics

| Category | Specifics |
|----------|-----------|
| **Roles/Outcomes** | [roles, job titles, results] |
| **Timelines** | [how fast results happen] |
| **Niche Pains** | [pains SPECIFIC to this audience] |
| **Value Props** | [what makes THIS offer different] |
| **Failed Alternatives** | [what they've tried] |
| **Proof Points** | [numbers, stats, community size] |

## Reasons to Buy

[Numbered list of 15-20 fundamentally different reasons]

## Hook Categories

[Which categories each one-liner uses - for diversity check]

---

## One-Liners

1. [one-liner]
2. [one-liner]
...
30. [one-liner]
```

**Why save the full context:**
- **Anchor verification:** Reviewers can check each one-liner has a specific from the extraction
- **Resume capability:** Don't re-extract specifics if generating more
- **Understanding:** Why certain hooks were chosen
- **Quality control:** Can verify all reasons to buy are covered

See [references/one-liner-methodology.md](references/one-liner-methodology.md) for the complete 6-step process, hook categories, and quality checklist.

See [references/one-liner-examples.md](references/one-liner-examples.md) for real examples by offer type.

---

## Mode: Video Scripts

Create diverse spoken-word scripts for camera delivery.

### 6-Step Process

1. **Core Outcome:** Single result every buyer achieves
2. **Avatars:** 3-4 buyer personas with situation, frustration, desires
3. **Angles Per Avatar:** Map angles from project context
4. **Generate Ads:** 15-30 scripts across all avatars
5. **Optimize for Spoken:** ~5th grade reading level, contractions, fragments
6. Ask for campaign name (required)
7. **Save Output:** `outputs/YYYY-MM-DD-video-ads-{campaign}/video-ads-batch-001.md`
8. Tell user: "Saved to `outputs/YYYY-MM-DD-video-ads-{campaign}/video-ads-batch-001.md`. Want me to commit this to git?"

### Script Structure

**Hook** (1-2 sentences): Lead with pain, desire, or belief. Create curiosity.

**Body** (4-8 sentences): Why problem exists. Position offer. Include proof.

**CTA** (2-3 sentences): Clear instruction. What happens after click.

**CRITICAL**: Each ad = fundamentally different reason to buy.

### Spoken Delivery Optimization

- Contractions: you're, don't, can't, won't
- Fragments: "Not theory. Patterns."
- Simple words: "use" not "utilize"

See [references/video-templates-hooks.md](references/video-templates-hooks.md) for templates and hook bank.

---

## Mode: Review

Review ads through 6 compliance and quality lenses before shipping.

### The 6 Lenses

| Lens | Location | What It Checks |
|------|----------|----------------|
| FTC Compliance | `.claude/lenses/ftc-compliance.md` | Federal regulations, earnings claims |
| Meta Policy | `.claude/lenses/meta-policy.md` | Platform triggers, Personal Attributes |
| Copy Quality | `.claude/lenses/copy-quality.md` | Schwartz, Hormozi, Suby frameworks |
| Visual Standards | `.claude/lenses/visual-standards.md` | Safe zones, OCR, prohibited visuals |
| Voice Authenticity | `.claude/lenses/voice-authenticity.md` | AI tells, brand voice |
| Substantiation | `.claude/lenses/substantiation.md` | Claims inventory, proof matching |

### Review Process

1. Gather input (single ad, batch, or component)
2. Git commit current state (preserves original): `[output] {type} batch pre-review`
3. Run all 6 lenses in parallel
4. Synthesize into P1/P2/P3 report
5. Apply P2/P3 fixes directly to the batch file
6. Create `review-log.md` documenting what changed
7. Tell user: "Fixes applied. Want me to commit these changes to git?"
8. If yes, commit: `[review] {type} batch - N fixes applied`

### Severity Levels

| Level | Meaning |
|-------|---------|
| **P1** | Blocks launch (legal/platform risk) |
| **P2** | Fix before launch (reduces performance or risk) |
| **P3** | Nice to have (optimization) |

### Status Determination

- **BLOCKED:** Any P1 issues
- **REVIEW REQUIRED:** Multiple P2 or borderline P1
- **CLEAR:** No P1, minimal P2

See [references/review-workflow.md](references/review-workflow.md) for full report format.

---

## Compliance (All Modes)

**Never say:**
- Cures/treats/heals [condition]
- Guaranteed results
- Will eliminate [problem]

**Safe to say:**
- Many have found this helpful
- Supports/complements existing approach
- Framework for understanding
- Education and guidance

---

## Recovery from Compaction

If context was compacted mid-task, check:

1. **What mode?** Static, Video, or Review
2. **What stage?** Planning angles, writing hooks, generating prompts, reviewing
3. **What's done?** Check outputs/ folder for partial work
4. **Resume:** Continue from the last completed step

For static: Did we finish image prompts (Part 1) before copy (Part 2)?
For video: How many of 15-30 scripts are done?
For review: Which lenses completed?

---

## Quick Reference

**Static ads:** 5-6 concepts x 5 primaries x 5 headlines x 3 image prompts
**Video scripts:** 15-30 diverse scripts, spoken-word optimized
**Review:** 6 lenses, P1/P2/P3 report, fix suggestions
