---
name: ad-static
description: Create static/image ads with copy and AI image prompts. Use when asked to create image ads, static ads, ad copy, primaries, headlines, or image prompts for Facebook/Instagram/Meta. Creates campaign batches with 5-6 distinct ad concepts, each with 5 primaries, 5 headlines, and 3 image prompts.
---

# Static Ad Creator

Create static/image ads with copy (multiple styles) + AI image prompts.

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

---

## Reference Required

Before creating ads, the business repo must have these files in `reference/`:

| File | What It Contains |
|------|------------------|
| `reference/core/offer.md` | What you sell, price, mechanism, benefits |
| `reference/core/audience.md` | Who buys, their pains, desires, psychographics |
| `reference/proof/testimonials.md` | Testimonials with names and specific outcomes |
| `reference/proof/angles/*.md` | Different messaging entry points/hooks |

If reference files are missing, ask user to create them first. Skills cannot generate good ads without solid reference.

## Terminology

- **Campaign Batch** = 5-6 distinct ad concepts for simultaneous launch
- **Ad Concept** = 1 angle/avatar + 5 primaries + 5 headlines + 3 image prompts
- **Primary** = One copy variation within an ad

## Campaign Batch Structure

Each batch contains 5-6 angles. Each angle has 3 image creatives (graphic, lo-fi, interrupt).

```
Campaign Batch 001 — [Campaign Name]
│
├── Angle 1 (01-03)
│   ├── 001_01 [concept] (graphic)
│   ├── 001_02 [concept] (lo-fi)
│   └── 001_03 [concept] (interrupt)
│
├── Angle 2 (04-06)
├── Angle 3 (07-09)
└── [etc.]
```

## Hook Rules (Non-Negotiable)

**Hook = 123-135 characters.** This is text visible before "See more" on Facebook.

**Rules:**
- No questions (creates binary "no" response)
- No "you/your" in first 3 lines (feels like an ad)
- No emojis
- Pack customer language and triggers into the hook

**Hook Formulas:**

1. **Transformation:** "How [Resonance] go from [Pain 1], [Pain 2] to [Benefit 1], [Benefit 2] using [Unique Approach]"

2. **Even Without:** "Here's how even [Resonance] (without [Challenge]) are [Benefit] using [Unique Approach]"

3. **Eliminates:** "This [Unique Approach] eliminates [Pain 1], [Pain 2], even [Pain 3], without [Challenge]..."

## Workflow

1. Read project context (offer, audience, proof, angles)
2. Select 5-6 angles for the batch
3. **Write ALL image prompts first** (Part 1)
4. **Write ALL ad copy second** (Part 2)
5. Compliance review
6. Save to output file

## Ad Styles

| Style | Best For | Length |
|-------|----------|--------|
| **Deep Ad** | Cold traffic, trust-building | 500-800 words |
| **UGC/Native** | Warm traffic, authenticity | 100-300 words |
| **Direct Response** | Solution-aware, urgency | 100-400 words |
| **Pattern Interrupt** | Scroll-stopping | Under 100 words |
| **Testimonial** | Social proof, skeptics | 200-400 words |

**Each ad uses all 5 styles** across its 5 primaries.

## Image Prompt Categories

| Type | Description | When to Use |
|------|-------------|-------------|
| **Graphic** | Typography-focused, clean design | Framework visuals, bold statements |
| **Lo-fi** | UGC style, iPhone aesthetic | Authenticity, relatable moments |
| **Interrupt** | Unexpected format | Pattern interrupt, stopping scroll |

## Output Format

Save to business repo: `outputs/{date}-{batch-name}/{batch#}_IMG_{campaign-name}.md`

Example: `outputs/2026-01-15-january-launch/001_IMG_overwhelm-relief.md`

See [references/output-template.md](references/output-template.md) for full template.

## Compliance

For health, parenting, finance niches — extra care required.

**Never say:**
- Cures/treats/heals [condition]
- Guaranteed results
- Will eliminate [problem]
- Critical window closing

**Safe to say:**
- Many have found this helpful
- Supports/complements existing approach
- Framework for understanding
- Education and guidance

## Quality Checklist

**Per Ad - Copy:**
- [ ] 5 primaries with different styles
- [ ] 5 headlines with different approaches
- [ ] Specific testimonial in at least 2 primaries
- [ ] All end with CTA URL

**Per Ad - Hooks:**
- [ ] Hook is 123-135 characters
- [ ] Uses hook formula
- [ ] No questions in hook
- [ ] No "you/your" in first 3 lines

**Compliance:**
- [ ] No medical/financial claims
- [ ] No guaranteed results
- [ ] Positioned as education/support
