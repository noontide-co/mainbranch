---
name: skool-vsl-scripts
description: Write high-converting Video Sales Letter scripts for Skool communities and membership businesses using an 18-section framework. Use when: (1) Creating VSL scripts for Skool about pages or community launches (2) Writing sales videos for membership or community offers (3) User says "VSL", "video sales letter", "about page video", "sales video" (4) Need the 18-section structure: Hook, Epiphany Bridge, Social Proof Stacking, Risk Reversal, CTAs (5) Selling lower-ticket memberships or communities ($47-$497/month). For high-ticket B2B offers ($3K-$50K+), use /b2b-killer-vsl instead. Produces camera-ready scripts optimized for spoken delivery.
---

# Skool VSL Script Writer

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

---

## Reference Required

| File | Purpose |
|------|---------|
| `reference/core/offer.md` | Community name, price, inclusions, guarantee |
| `reference/core/audience.md` | Target transformation, objections, doubts |
| `reference/proof/testimonials.md` | Member success stories with specifics |

**Optional but helpful:** Personal origin story (for epiphany bridge), `reference/proof/angles/*.md`

If missing, ask user to provide or run `/enrich` first.

## The 18-Section Framework

See [references/vsl-framework.md](references/vsl-framework.md) for complete templates and examples per section.

**Quick overview:** Hook → Epiphany Bridge → Peek Plan → Features/Soft CTA → The Plan → Answer Questions → Stack Proof → Change Tone → Zoom Out → Price Anchor → Low Effort/High Reward → Recap Obstacles → Address Objections → Roadmap → Worst/Best Case → Hard CTA → Risk Reversal → Final CTA

## Process

### 1. Gather Context

Confirm you have:
- Target audience and primary pain
- Core transformation offered
- Personal origin story (for epiphany bridge)
- 3-5 member success stories with specifics
- Top 3-5 objections
- Pricing and guarantee details

### 2. Write Sections

Follow the 18-section framework. Key principles:
- **Hook**: Specific pain, create recognition
- **Epiphany Bridge**: Empathy, catalyst, results
- **Social Proof**: Diverse backgrounds, specific outcomes
- **CTAs**: Soft asks build to hard ask
- **Risk Reversal**: Joining feels safer than not joining

### 3. Optimize for Spoken Delivery

- Contractions: you're, don't, can't
- Short sentences, rhetorical questions
- Flow with commas (one long sentence with pauses)
- ~5th grade reading level

### 4. Output Format

```markdown
# VSL Script: {Community Name}

**Target Audience**: {description}
**Core Transformation**: {outcome}
**Runtime Estimate**: {X minutes}

---

## 1. HOOK
{hook text}

## 2. EPIPHANY BRIDGE
{bridge text}

[Continue through all 18 sections...]

---

## DELIVERY NOTES
- Energy tips
- Pacing guidance
- Key emphasis points
```

## Quality Checklist

Before delivery, verify:
- [ ] Hook creates pain recognition
- [ ] Epiphany bridge feels authentic
- [ ] Social proof covers diverse situations
- [ ] All major objections addressed
- [ ] CTA progression: soft → hard
- [ ] Reads naturally aloud
- [ ] Joining feels safer than not joining
