# Decide Phase

Detailed workflow for decision mode in `/think`.

---

## Workflow

1. **Check for related research** — If found, link in frontmatter. If missing, prompt user.
2. **Present options** — At least 2 options with pros/cons/effort.
3. **Document choice** — Clear decision with rationale.
4. **List consequences** — What becomes easier, harder, what we're accepting.
5. **Generate action items** — Specific reference file updates.
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

## Action Items

Every decision ends with explicit action items for reference files:

```markdown
## Action Items

Reference files to update:
- [ ] Update `reference/core/offer.md` — Add guarantee section
- [ ] Create `reference/proof/angles/risk-reversal.md` — New angle file
- [ ] Update `reference/core/voice.md` — Add "guarantee" to vocabulary

Other actions:
- [ ] Set up Stripe subscription
- [ ] Update sales page copy
```

**Be specific:** "Update offer.md" is bad. "Update offer.md — Add 30-day guarantee section after pricing" is good.

### Claude Tasks for Execution

After listing action items, create Claude tasks to track execution:

```
TaskCreate: "Update offer.md with guarantee section"
TaskCreate: "Create risk-reversal.md angle file"
TaskCreate: "Update voice.md vocabulary"
```

This gives you:
- Spinner showing current work ("Updating offer.md...")
- Progress tracking via `TaskList`
- Clear completion markers

As you complete each item, mark the task complete:
```
TaskUpdate: taskId=1, status=completed
```

---

## Decisions as Task Anchors

For substantial work, **create a decision file early** — even before you've fully decided. The decision file becomes your task tracker.

**How it works:**

1. Start project -> Create `decisions/YYYY-MM-DD-topic.md` with `status: proposed`
2. Research and iterate -> Update the file as you learn
3. Make the call -> Change to `status: accepted`
4. Execute -> Check off action items as you complete them
5. Finish -> Change to `status: codified`

**Why this works:**
- Progress is visible in the file
- Rationale captured as you go
- Next session: check `decisions/` to see where you left off
- No separate task manager needed

**The `## Other actions` section** captures non-reference tasks (set up Stripe, update sales page, etc.).

**For smaller tasks:** Just do them. Decision files are for substantial work where the "why" matters.

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

## Exit Criteria

Decision is complete when:

- [ ] Context documented
- [ ] Options listed with pros/cons
- [ ] Decision stated with rationale
- [ ] Consequences listed (what becomes easier/harder)
- [ ] Action items specify which reference files to update
- [ ] File saved to `decisions/`

---

## Template

See [templates/decision-template.md](templates/decision-template.md) for full file structure.
