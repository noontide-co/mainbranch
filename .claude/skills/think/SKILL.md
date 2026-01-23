---
name: think
description: Combined research, decision, and codification workflow. Use when: (1) Exploring a question before committing (2) Making a decision that needs documentation (3) User says "research", "decide", "figure out", "explore", "codify", "enrich", "add context" (4) Updating reference files based on decisions (5) User wants to add new testimonials, angles, or proof to existing files. Supports modes: full flow, research-only, decide-only, codify.
---

# Think

Research, decide, and codify knowledge into reference files.

---

## Pull Latest Updates

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

---

## Where Files Go

All files save to YOUR business repo, not the engine (vip).

```
your-business-repo/          <- Files saved here
├── research/                 <- Research output
├── decisions/                <- Decision output
└── reference/                <- Codify updates this

vip/ (engine)                 <- Never modified
```

---

## Route by Intent

Detect mode from user's natural language:

| User Says | Mode | Reference |
|-----------|------|-----------|
| "figure out", "explore", "I'm trying to..." | Full Flow | - |
| "research", "investigate", "what do we know about" | Research | [research-phase.md](references/research-phase.md) |
| "decide", "we chose", "document decision" | Decide | [decide-phase.md](references/decide-phase.md) |
| "codify", "apply", "update reference files" | Codify | [codify-phase.md](references/codify-phase.md) |
| "add context", "enrich", "I have new info" | Codify | [codify-phase.md](references/codify-phase.md) |
| "where was I", "continue", "pick up" | Recovery | [recovery.md](references/recovery.md) |

If unclear, ask: "Are you exploring a question, documenting a decision, or updating reference files?"

---

## Full Flow (Default)

```
Research -> Checkpoint -> Decide -> Checkpoint -> Codify
```

### 1. Define Question

> "What specifically are you trying to figure out?"

### 2. Research

Gather from codebase, web, user input. Spawn subagents for parallel research.

### 3. Synthesize (Required)

Every research output needs:
- One-sentence summary (20 words max)
- Key findings (5-10 bullets)
- Implications for reference files
- Open questions

### 4. Checkpoint

> "Ready to make a decision, or need more research?"

### 5. Decide

Present options with pros/cons. Document choice and rationale.

### 6. Action Items + Tasks

List action items in the decision file AND create Claude tasks:

```markdown
## Action Items
- [ ] Update reference/core/offer.md - Add guarantee section
- [ ] Create reference/proof/angles/risk-reversal.md
```

**Create tasks for execution tracking:**
```
TaskCreate: "Update offer.md with guarantee section"
TaskCreate: "Create risk-reversal.md angle file"
```

Tasks provide:
- Spinner showing current work
- Dependencies between items
- Session-level progress tracking

### 7. Checkpoint

> "Ready to update reference files now, or save for later?"
>
> "I've created tasks for each action item. Want to work through them now?"

### 8. Codify

Apply action items to reference files. Mark decision as codified.

---

## Research Mode

```
/think research "topic"
```

Output: `research/YYYY-MM-DD-topic-claude-code.md`

See [references/research-phase.md](references/research-phase.md) for full workflow.

---

## Decide Mode

```
/think decide "topic"
```

Output: `decisions/YYYY-MM-DD-topic.md`

See [references/decide-phase.md](references/decide-phase.md) for full workflow.

---

## Codify Mode

```
/think codify decisions/YYYY-MM-DD-topic.md
```

Or: "/think add new testimonials to my files"

See [references/codify-phase.md](references/codify-phase.md) for full workflow.

---

## Task Tracking Layers

Three levels of task tracking, each with a purpose:

| Layer | Scope | Persists | Use For |
|-------|-------|----------|---------|
| **Claude tasks** | Current session | Session | Execution tracking, spinners |
| **Decision files** | Project | Forever | Rationale, anchor for work |
| **GitHub issues** | Roadmap | Forever | Cross-session, team visibility |

### Decision Files as Anchors

For substantial work, create decision file early with `status: proposed`:

1. `proposed` - Drafted, exploring
2. `accepted` - Decision made
3. `codified` - Applied to reference files

### Claude Tasks for Execution

When a decision has action items, create Claude tasks:
- Use `TaskCreate` for each action item
- Use `TaskUpdate` to mark progress
- Use `TaskList` to see what's left

### GitHub Issues for Roadmap

For work that spans sessions or needs team visibility:
- Create issue: `gh issue create --repo [repo] --title "..." --body "..."`
- Link to decision file in issue body
- Close issue when decision is codified

Check `decisions/` and `TaskList` to see where you left off.

---

## Recovery

If conversation compacted, check multiple sources:

**1. Claude tasks (current session):**
```
TaskList
```

**2. Recent files:**
```bash
ls -lt research/*.md 2>/dev/null | head -5
grep -l "status: proposed\|status: accepted" decisions/*.md 2>/dev/null
```

**3. GitHub issues (if using):**
```bash
gh issue list --assignee @me --state open
```

Then confirm: "I see you were working on [topic]. Continue from here?"

See [references/recovery.md](references/recovery.md) for details.

---

## Templates

- [references/templates/research-template.md](references/templates/research-template.md)
- [references/templates/decision-template.md](references/templates/decision-template.md)

---

## When NOT to Use

- Quick factual questions (just ask)
- Simple file edits (just edit)
- Generating content (use `/ads`, `/vsl`, `/content`)

Use `/think` when the answer requires investigation and the choice needs documentation.
