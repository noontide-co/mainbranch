# Decisions

Records of choices made with rationale. Links to research that informed them.

---

## When to Create a Decision

Create a decision file when you're making a choice that:
- Affects your marketing strategy
- Has multiple valid options
- Would benefit from documented rationale
- You might want to revisit later

## File Format

```markdown
---
type: decision
date: 2026-01-13
status: active
---
# Decision Title

## Situation
[What's happening, what prompted this decision]

## Research
### research-name
**Date:** YYYY-MM-DD
**Source:** source
[Summary]
See: `research/YYYY-MM-DD-slug.md`

## Options

### Option A (selected)
**Pros:** ...
**Cons:** ...

### Option B (rejected)
**Pros:** ...
**Cons:** ...

## Decision
[The actual choice with rationale]

## Action Items
- [ ] Update context/offer.md
- [ ] Create new campaign
```

## Naming

`YYYY-MM-DD-slug.md`

Example: `2026-01-13-primary-angle-selection.md`
