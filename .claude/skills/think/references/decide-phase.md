# Decide Phase

Detailed workflow for decision mode in `/think`.

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

**Be specific:** "Update offer" is bad. "offer.md gets a 30-day guarantee section after pricing" is good. Name the files and describe the changes — but as prose, not checkboxes.

---

## Decisions as Task Anchors

For substantial work, **create a decision file early** — even before you've fully decided. The decision file becomes your task tracker.

**How it works:**

1. Start project -> Create `decisions/YYYY-MM-DD-topic.md` with `status: proposed`
2. Research and iterate -> Update the file as you learn
3. Make the call -> Change to `status: accepted`
4. Codify -> Apply changes described in `## What Changes` to reference files
5. Finish -> Change to `status: codified`

**Why this works:**
- Progress is visible in the file (proposed -> accepted -> codified)
- Rationale captured as you go
- Next session: check `decisions/` to see where you left off
- No separate task manager needed

**Non-reference tasks** (set up Stripe, update sales page, etc.) go in `## What Changes` under "Outside reference."

**For smaller tasks:** Just do them. Decision files are for substantial work where the "why" matters.

---

## Status Values

| Status | Meaning |
|--------|---------|
| `proposed` | Decision drafted, not yet accepted |
| `accepted` | Decision made and committed to |
| `codified` | Changes applied to reference files |

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
