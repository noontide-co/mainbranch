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

**Trigger:** [The specific event or question that started this]

---

## Research Summary

[Key findings from linked research. Don't duplicate — synthesize.]

See: [linked research files]

---

## Considered Options

### Option A: [Name]

[Brief description]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

**Effort:** [Low/Medium/High]

---

### Option B: [Name]

[Brief description]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

**Effort:** [Low/Medium/High]

---

### Option C: [Name] (if applicable)

[Same structure]

---

## Decision

**We chose: Option [X]**

[2-3 sentences explaining WHY this option. What made it the right choice given our situation, constraints, and goals.]

---

## Consequences

### What Becomes Easier

- [Consequence 1]
- [Consequence 2]

### What Becomes Harder

- [Trade-off 1]
- [Trade-off 2]

### What We're Accepting

- [Risk or limitation we're knowingly accepting]

---

## Action Items

Reference files to update:

- [ ] Update `reference/core/offer.md` — [Specific change]
- [ ] Update `reference/core/audience.md` — [Specific change]
- [ ] Create `reference/proof/angles/[new-angle].md` — [Description]
- [ ] Update `CLAUDE.md` — [Specific change]

Other actions:

- [ ] [Non-reference action]
- [ ] [Non-reference action]

---

## Review Date

[When should we revisit this decision? Set a specific date or trigger.]

Example: "Revisit after 100 new members" or "Review on 2026-04-01"
```

---

## Status Values

| Status | Meaning |
|--------|---------|
| `proposed` | Decision drafted, not yet accepted |
| `accepted` | Decision made and committed to |
| `codified` | Action items applied to reference files |
| `superseded` | Replaced by a newer decision |
| `deprecated` | No longer relevant |

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
Update status to `superseded` and add note:
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
- [ ] Action items are specific (file + change)
- [ ] Review date is set

---

## Action Item Format

Be specific about what changes in which file:

**Good:**
```markdown
- [ ] Update `reference/core/offer.md` — Add "30-day guarantee" section after pricing
- [ ] Update `reference/core/voice.md` — Add "risk-free" to approved vocabulary
```

**Bad:**
```markdown
- [ ] Update offer
- [ ] Fix voice file
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

Currently offering one tier at $97/month. Growth has plateaued at 150 members. Need to decide whether to add tiers to capture more of the market.

**Trigger:** Three members asked about "advanced" content in the same week.

---

## Research Summary

- Competitors use 2-3 tiers, range $47-197/month
- Free tiers convert 5-15% to paid within 60 days
- Three-tier pricing captures both budget and power users
- Our audience responds to "investment" framing

See: research/2026-01-15-pricing-tier-analysis-gemini.md

---

## Considered Options

### Option A: Keep Single Tier

Stay at $97/month, focus on value.

**Pros:**
- Simple, no confusion
- Premium positioning maintained

**Cons:**
- Missing free-tier lead generation
- Leaving money on table from power users

**Effort:** None

---

### Option B: Two-Tier (Free + Paid)

Add free tier with limited content.

**Pros:**
- Lead generation at scale
- Lower barrier to entry

**Cons:**
- Dilutes community quality
- Support burden from free members

**Effort:** Medium

---

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

**Effort:** High

---

## Decision

**We chose: Option C (Three-Tier)**

The research shows three tiers maximizes both reach and revenue. Our audience values "investment" framing, so premium tier won't cannibalize base tier. The member requests for "advanced" content validate demand for premium.

---

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

---

## Action Items

Reference files to update:

- [ ] Update `reference/core/offer.md` — Add three-tier pricing structure with benefits per tier
- [ ] Update `reference/core/audience.md` — Add segments for Free Seeker, Core Member, Power User
- [ ] Create `reference/proof/angles/tier-comparison.md` — Angle for upgrade messaging
- [ ] Update `reference/domain/membership/tiers.md` — Full tier specification

Other actions:

- [ ] Create free tier content curriculum
- [ ] Define premium-only content cadence
- [ ] Set up Skool tier configuration

---

## Review Date

Review on 2026-03-17 (60 days) with data on:
- Free-to-paid conversion rate
- Premium tier uptake
- Churn by tier
```
