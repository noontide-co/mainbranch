---
name: ad-video-scripts
description: Write high-converting video ad scripts for Meta ads. Use when asked to create ad scripts, video scripts, or ad copy for Facebook/Instagram/Meta campaigns. Generates 15-30+ diverse scripts optimized for spoken-word camera delivery.
---

# Ad Video Script Writer

Creates diverse video ad scripts using a systematic 6-step process.

## Context Required

Business repo must have these files in `context/`:

| File | What It Contains |
|------|------------------|
| `context/offer.md` | What you sell, price, mechanism, benefits |
| `context/audience.md` | Who buys, their pains, desires |
| `context/proof/testimonials.md` | Testimonials with names and outcomes |
| `context/angles/*.md` | Different messaging entry points |

If context files are missing, ask user to create them first.

## 6-Step Process

### Step 1: Core Outcome
Identify the single result every buyer achieves.

### Step 2: Avatars
Define 3-4 buyer personas: situation, frustration, what they've tried, what they want.

### Step 3: Angles Per Avatar
Map angles from project context. Each angle = different entry point.

### Step 4: Generate Ads
Produce 15-30 ads across all avatars:

**Hook** (1-2 sentences): Lead with pain, desire, or belief. Create curiosity.

**Body** (4-8 sentences): Why problem exists. Position offer. Include proof.

**CTA** (2-3 sentences): Clear instruction. What happens after click.

**CRITICAL**: Each ad = fundamentally different reason to buy.

### Step 5: Optimize for Spoken Delivery
Simplify to ~5th grade reading level:
- Contractions: you're, don't, can't, won't
- Fragments for emphasis: "Not theory. Patterns."
- Simple words: "use" not "utilize"

### Step 6: Save Output
Save to business repo: `campaigns/{date}-{batch-name}/{batch#}_VID_{angle}.md`

Example: `campaigns/2026-01-15-january-launch/001_VID_transformation.md`

## Templates & Hooks

See [references/templates-hooks.md](references/templates-hooks.md) for:
- Problem-Solution template
- Testimonial-Led template
- Empathy-First template
- Hook bank by category

## Compliance

**Never:** cure/fix claims, guaranteed results, replaces professional service

**Safe:** many found helpful, supports approach, education and guidance

## Output Format

```markdown
# Batch {number} — {Angle} Video Scripts

Generated: {date}
Offer: {name} ({price})
CTA: {URL}

---

## Avatar 1: {Name}

### Script 1: {batch#}_VID_{trigger}-01

HOOK:
{text}

BODY:
{text}

CTA:
{text}

---
```

## Quality Check

1. No two ads same core reason to buy
2. Read aloud sounds natural
3. No claims or guarantees
4. True diversification
