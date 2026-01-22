---
name: ads
description: Create and review Meta/Facebook/Instagram ads. Routes to static image ads (copy + AI image prompts), video scripts (15-30 spoken-word scripts), or multi-lens compliance review. Use when asked to create ads, write ad copy, generate image prompts, write video scripts, or review ads for compliance. Say "/ads" or ask for "static ads", "video scripts", or "ad review".
---

# Ads Skill

Create static ads, video scripts, or review ads for compliance.

## Triage

Determine mode from user request:

| Mode | Triggers | Output |
|------|----------|--------|
| **Static** | "static ads", "image ads", "primaries", "headlines", "image prompts" | 5-6 concepts, each with 5 primaries + 5 headlines + 3 image prompts |
| **Video** | "video scripts", "ad scripts", "spoken word", "camera scripts" | 15-30 diverse scripts for spoken delivery |
| **Review** | "review", "check", "audit", "compliance", "before launch" | P1/P2/P3 report across 6 lenses |

If unclear, ask: "Do you want static image ads, video scripts, or a compliance review?"

---

## Reference Required (All Modes)

Before creating ads, the business repo must have:

| File | What It Contains |
|------|------------------|
| `reference/core/offer.md` | What you sell, price, mechanism, benefits |
| `reference/core/audience.md` | Who buys, their pains, desires |
| `reference/proof/testimonials.md` | Testimonials with names and outcomes |
| `reference/proof/angles/*.md` | Different messaging entry points |

If reference files are missing, ask user to create them first.

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
2. Select 5-6 angles for the batch
3. **Write ALL image prompts first** (Part 1)
4. **Write ALL ad copy second** (Part 2)
5. Compliance check
6. Save to `outputs/{date}-{batch-name}/{batch#}_IMG_{campaign-name}.md`

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

## Mode: Video Scripts

Create diverse spoken-word scripts for camera delivery.

### 6-Step Process

1. **Core Outcome:** Single result every buyer achieves
2. **Avatars:** 3-4 buyer personas with situation, frustration, desires
3. **Angles Per Avatar:** Map angles from project context
4. **Generate Ads:** 15-30 scripts across all avatars
5. **Optimize for Spoken:** ~5th grade reading level, contractions, fragments
6. **Save Output:** `outputs/{date}-{batch-name}/{batch#}_VID_{angle}.md`

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
2. Run all 6 lenses in parallel
3. Synthesize into P1/P2/P3 report
4. Provide fix suggestions for each issue
5. Save to `outputs/{batch-folder}/review-{date}.md`

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
