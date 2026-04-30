# Mode: Hook Library (Creative Variations)

Generate punchy, truly diversified creative variations for static image ads that feed Meta's Andromeda algorithm. Users can request any quantity -- "give me 5" or "give me 50" -- not fixed batches.

Also called "one-liners" -- same methodology, same pipeline. Both trigger words route here.

---

## Why This Mode Exists

Meta's Andromeda algorithm (July 2025) rewards TRUE creative diversification - not surface variations. Each creative variation is a different psychological conversation, anchored in offer-specific details.

---

## 6-Step Process

1. **Core Outcome:** Single transformation every buyer achieves
2. **Extract Specifics:** Roles, timelines, niche pains, value props, failed alternatives, proof points
3. **Reasons to Buy:** 15-20 fundamentally different reasons (the protein supplement exercise)
4. **Hook Categories:** Ensure variety across problem agitation, emotional state, transformation, contrarian, identity callout, etc.
5. **Generate:** 30 creative variations, each with at least one specific anchor
6. **Output:** Simple numbered list, ready to copy

---

## The Anchor Rule (Non-Negotiable)

Every variation **MUST** include at least one specific element:
- A specific role, outcome, or company (DevOps Engineer, AWS, 60k)
- A specific niche pain (service desk 2+ years, no CS degree)
- A specific value prop (mock interviews with Principal Engineers)
- A specific timeline or proof point (8 weeks, 500+ community)

**The Specificity Test:** If this variation could sell a gym membership, a life coaching program, or a generic course - it fails. Rewrite it.

---

## Input Modes

| Mode | How to Detect | What to Pull |
|------|---------------|--------------|
| **Has business repo** | Reference files exist | Resolved `offer.md`, resolved `audience.md`, `reference/core/voice.md`, testimonials |
| **No repo** | Nothing found | Ask user for materials |

---

## Output Format

**Save to file, not chat.** This enables review to edit the file directly.

1. Ask for campaign name (required)
2. Confirm quantity: "How many? A few to test (5-10) or a full batch (30+)?" -- or use the number they already specified
3. Create folder: `outputs/YYYY-MM-DD-creative-variations-[offer]-{campaign}/` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode)
4. Save full generation context + creative variations to: `creative-variations-batch-001.md`
5. Tell user: "Saved {N} creative variations. Running automatic post-generation pipeline..."
6. Run the **Automatic Post-Generation Pipeline** (see SKILL.md). This handles git commit, compliance review, and image generation automatically.

**creative-variations-batch-001.md format:**

```markdown
---
type: output
format: creative-variations
date: YYYY-MM-DD
status: draft
platform: meta
---

# Creative Variations: {Campaign Name}

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

[Which categories each variation uses - for diversity check]

---

## Creative Variations

1. [variation]
2. [variation]
...
{N}. [variation]
```

**Why save the full context:**
- **Anchor verification:** Reviewers can check each variation has a specific from the extraction
- **Resume capability:** Don't re-extract specifics if generating more
- **Understanding:** Why certain hooks were chosen
- **Quality control:** Can verify all reasons to buy are covered

See [one-liner-methodology.md](one-liner-methodology.md) for the complete 6-step process, hook categories, and quality checklist.

See [one-liner-examples.md](one-liner-examples.md) for real examples by offer type.
