# Decide Phase

Detailed workflow for decision mode in `/mb-think`.

---

## Workflow

1. **Check for related research** — If found, link in frontmatter. If missing, prompt user.
2. **Present options** — At least 2 options with pros/cons/effort.
3. **Document choice** — Clear decision with rationale.
4. **List consequences** — What becomes easier, harder, what we're accepting.
5. **Describe what changes** — Which reference files are affected and what the key changes are.
6. **Save** — Write to `decisions/YYYY-MM-DD-topic.md`

---

## Linking Research

Decisions link to research via frontmatter:

```yaml
---
type: decision
date: 2026-01-17
status: accepted
linked_research:
  - research/2026-01-15-pricing-analysis-gemini.md
  - research/2026-01-16-competitor-review-claude-code.md
---
```

If no research exists, prompt: "Did you do research on this? Want to research first?"

---

## Options Format

Present at least 2 options. For each:

```markdown
### Option A: [Name]

[Brief description]

**Pros:**
- [Pro 1]
- [Pro 2]

**Cons:**
- [Con 1]
- [Con 2]

**Effort:** [Low/Medium/High]
```

---

## Decision Statement

Clear statement of choice plus rationale:

```markdown
## Decision

**We chose: Option [X]**

[2-3 sentences explaining WHY. What made it right given situation, constraints, goals.]
```

---

## Consequences

Honest assessment of trade-offs:

```markdown
## Consequences

### What Becomes Easier
- [Benefit 1]

### What Becomes Harder
- [Trade-off 1]

### What We're Accepting
- [Risk or limitation we knowingly accept]
```

---

## What Changes

Every decision ends with a narrative description of what reference files are affected and what the key changes are. This is what codify reads.

```markdown
## What Changes

offer.md gets a "30-day guarantee" section after pricing. voice.md adds "guarantee" and "risk-free" to approved vocabulary. A new angle file (risk-reversal.md) captures the guarantee-as-differentiator messaging.

Outside reference: set up Stripe subscription, update sales page copy.
```

**In multi-offer mode, use offer-qualified paths:**

```markdown
## What Changes

Reference files affected:
- `core/offers/community/offer.md` — updated pricing section
- `core/offer.md` — updated brand thesis
- `core/product-ladder.md` — updated ascension logic

Outside reference: update Skool pricing cards.
```

**Be specific:** "Update offer" is bad. "`core/offers/community/offer.md` gets a 30-day guarantee section after pricing" is good. Name the files and describe the changes — but as prose, not checkboxes.

### Decision Scope

When documenting a decision, note which offer it affects:
- **Offer-specific:** affects one offer's files (e.g., `core/offers/community/offer.md`)
- **Brand-level:** affects core/ files (e.g., `core/voice.md`, `core/offer.md` brand thesis)
- **Cross-offer:** affects `core/product-ladder.md` or multiple offers simultaneously

---

## Decisions as Rationale Anchors

For substantial choices, **create a decision file early** -- even before you've
fully decided. The decision file keeps the rationale, options, trade-offs, and
intended changes visible. It is not a generic task tracker.

**How it works:**

1. Draft direction -> Create `decisions/YYYY-MM-DD-topic.md` with `status: proposed`
2. Research and iterate -> Update the file as you learn
3. Make the call -> Change to `status: accepted`
4. Codify rationale -> Apply approved changes described in `## What Changes`
   to durable business or engine truth
5. Mark integrated -> Change to `status: codified`

**Why this works:**
- Decision maturity is visible in the file (`proposed` -> `accepted` -> `codified`)
- Rationale is captured as you go
- Next session: `/mb-start` can recover the current view from files, git,
  GitHub facts, graph links, and checkpoints
- Follow-up work routes into a push, playbook, checkpoint, log entry, or
  GitHub issue when it needs durability

**Non-reference consequences** (set up Stripe, update sales page, etc.) can be
named in `## What Changes` under "Outside reference." If they need a durable
thread across sessions or people, suggest a GitHub issue instead of using the
decision as a work board.

**For smaller work:** Just do it. Decision files are for substantial choices
where the "why" matters.

---

## Status Values

| Status | Meaning |
|--------|---------|
| `proposed` | Direction drafted, still being evaluated |
| `accepted` | Operator chose the direction |
| `codified` | Rationale integrated into durable business or engine truth |

---

## Exit Criteria

Decision is complete when:

- Context documented
- Options listed with pros/cons
- Decision stated with rationale
- Consequences listed (what becomes easier/harder)
- What Changes describes affected reference files and key changes
- File saved to `decisions/`

---

## Template

See [templates/decision-template.md](templates/decision-template.md) for full file structure.
