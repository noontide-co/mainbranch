# Decision Template

Copy this template when documenting decisions.

Based on Architecture Decision Records (ADR) best practices.

---

## Filename Convention

```
decisions/YYYY-MM-DD-topic.md
```

Use lowercase, hyphens between words. Be specific in the topic name.

Good: `2026-01-17-pricing-tier-strategy.md`
Bad: `2026-01-17-pricing.md` (too vague)

---

## Template

```markdown
---
type: decision
date: YYYY-MM-DD
status: proposed
linked_research:
  - research/YYYY-MM-DD-topic-source.md
supersedes: null
---

# Decision: [Clear Title]

## Context

[Why we needed to make this decision. What situation prompted it.]

## Research Summary

[Key findings from linked research. Don't duplicate — synthesize.]

See: [linked research files]

## Options

### Option A: [Name]

[Brief description]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

### Option B: [Name]

[Brief description]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

## Decision

**We chose: Option [X]**

[2-3 sentences explaining WHY this option. What made it the right choice given our situation, constraints, and goals.]

## Consequences

### What Becomes Easier
- [Consequence 1]
- [Consequence 2]

### What Becomes Harder
- [Trade-off 1]
- [Trade-off 2]

### What We're Accepting
- [Risk or limitation we're knowingly accepting]

## What Changes

[Describe which reference files are affected and what the key changes are. This is what codify reads to know what to update.]

[Example: offer.md gets a new pricing tier section. audience.md needs segments for each tier. A new angle file for upgrade messaging.]

## Review Date (Optional)

[When to revisit — a date or trigger. Example: "Revisit after 100 new members"]
```

---

## Status Values

| Status | Meaning |
|--------|---------|
| `proposed` | Decision drafted, not yet accepted |
| `accepted` | Decision made and committed to |
| `codified` | Changes applied to reference files |

---

## Linking Research

Always link to research that informed the decision:

```yaml
linked_research:
  - research/2026-01-15-pricing-analysis-gemini.md
  - research/2026-01-16-competitor-review-claude-code.md
```

This creates an audit trail: decision -> research -> findings.

---

## Superseding Previous Decisions

When a new decision replaces an old one:

**In the new decision:**
```yaml
supersedes: decisions/2025-12-01-original-pricing.md
```

**In the old decision:**
Add a note at the top (keep status as `accepted` or `codified`):
```markdown
> **Superseded by:** decisions/2026-01-17-pricing-tier-strategy.md
```

---

## Quality Checklist

Before marking decision as `accepted`:

- [ ] Context explains why this decision was needed
- [ ] At least 2 options considered
- [ ] Each option has clear pros/cons
- [ ] Decision states the choice AND the reasoning
- [ ] Consequences acknowledge trade-offs
- [ ] What Changes describes affected files and key changes

---

## What Changes Format

Be specific about which files are affected and what changes:

**Good:**
```markdown
## What Changes

offer.md gets a "30-day guarantee" section after pricing. voice.md adds "risk-free" to approved vocabulary. A new angle file (risk-reversal.md) captures the guarantee-as-differentiator messaging.
```

**Bad:**
```markdown
## What Changes

Update offer and voice files.
```

---

## Example: Completed Decision

```markdown
---
type: decision
date: 2026-01-17
status: accepted
linked_research:
  - research/2026-01-15-pricing-tier-analysis-gemini.md
  - research/2026-01-16-competitor-audit-claude-code.md
supersedes: decisions/2025-09-01-single-tier-pricing.md
---

# Decision: Three-Tier Pricing Structure

## Context

Currently offering one tier at $97/month. Growth has plateaued at 150 members. Need to decide whether to add tiers to capture more of the market. Three members asked about "advanced" content in the same week.

## Research Summary

- Competitors use 2-3 tiers, range $47-197/month
- Free tiers convert 5-15% to paid within 60 days
- Three-tier pricing captures both budget and power users
- Our audience responds to "investment" framing

See: research/2026-01-15-pricing-tier-analysis-gemini.md

## Options

### Option A: Keep Single Tier

Stay at $97/month, focus on value.

**Pros:**
- Simple, no confusion
- Premium positioning maintained

**Cons:**
- Missing free-tier lead generation
- Leaving money on table from power users

### Option B: Two-Tier (Free + Paid)

Add free tier with limited content.

**Pros:**
- Lead generation at scale
- Lower barrier to entry

**Cons:**
- Dilutes community quality
- Support burden from free members

### Option C: Three-Tier (Free + $97 + $297)

Full tier structure with free, standard, and premium.

**Pros:**
- Maximum market capture
- Natural upgrade path
- Premium tier for power users

**Cons:**
- More complex to manage
- Potential confusion
- Must clearly differentiate tiers

## Decision

**We chose: Option C (Three-Tier)**

The research shows three tiers maximizes both reach and revenue. Our audience values "investment" framing, so premium tier won't cannibalize base tier. The member requests for "advanced" content validate demand for premium.

## Consequences

### What Becomes Easier
- Lead generation through free tier
- Upselling committed members to premium
- Revenue growth without member count growth

### What Becomes Harder
- Content planning (must differentiate tiers)
- Community management (three member segments)
- Messaging (explaining tier differences)

### What We're Accepting
- Free tier members may be lower quality
- Premium tier needs exclusive content we haven't created yet
- 30-60 days to see if this works

## What Changes

offer.md gets a three-tier pricing structure with benefits per tier (Free, $97 Core, $297 Premium). audience.md adds three segments: Free Seeker, Core Member, Power User — each with distinct psychographics and buying triggers. A new angle file (tier-comparison.md) captures upgrade messaging. domain/membership/tiers.md gets the full tier specification.

Outside reference: create free tier content curriculum, define premium-only cadence, configure Skool tiers.

## Review Date (Optional)

Review on 2026-03-17 (60 days) — free-to-paid conversion rate, premium tier uptake, churn by tier.
```
