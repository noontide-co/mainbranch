---
name: think
description: |
  Combined research and decision workflow. Use when:
  (1) Exploring a question before committing to an approach
  (2) Making a decision that needs documentation and rationale
  (3) User says "research", "decide", "figure out", "explore"
  (4) Updating reference files based on a completed decision
  (5) Any time user would open multiple tabs to investigate something

  Supports modes: full flow, research-only, decide-only, codify.
---

# Think

Structured workflow for research, decisions, and codifying knowledge.

**Need help?** Type `/help` + your question anytime. If conversation compacts, `/help` reloads fresh context.

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

---

## When to Use

- Exploring a question before committing to an approach
- Making a decision that needs documentation and rationale
- Updating reference files based on a completed decision
- Any time you'd open multiple tabs to "figure something out"

---

## Where Files Go

**All files are saved to YOUR business repo, not the engine (vip).**

```
your-business-repo/          <- Files saved here
├── research/                 <- /think research output
├── decisions/                <- /think decide output
└── reference/                <- /think codify updates this

vip/ (engine)             <- Never modified by /think
└── .claude/skills/think/     <- This skill lives here
```

Make sure your business repo is the primary working directory.

---

## Modes

### `/think "topic"` (Full Flow - Default)

Research, synthesize, then decide. Context preserved throughout.

```
Research → Synthesize → Decide → (optional) Codify
```

### `/think research "topic"`

Research only. Creates file in `research/`.

### `/think decide "topic"`

Document a decision only. Prompts for related research if none found.

### `/think codify decisions/YYYY-MM-DD-topic.md`

Apply a decision's action items to reference files.

---

## Full Flow Walkthrough

### 1. Define the Question

Start by clarifying what we're exploring:

> "What specifically are you trying to figure out?"

Good research questions:
- "What pricing tier structure should we use?"
- "Which messaging angle resonates with cold traffic?"
- "Should we add a guarantee? What kind?"

Bad questions (too vague):
- "How do I grow?"
- "What should I do next?"

### 2. Gather Information

Sources to check:
1. **Codebase** — Existing reference files, past decisions, research
2. **Web** — Competitors, industry benchmarks, expert perspectives
3. **User input** — "What else do you know about this?"

Spawn subagents for parallel research when investigating multiple sources.

### 3. Synthesize (Required)

Every research output MUST have a synthesis section. This forces distillation.

**Template:**
```markdown
## Synthesis

### One-Sentence Summary (20 words max)
[Distilled insight]

### Key Findings (5-10 bullets, 15 words each)
- [Finding 1]
- [Finding 2]
...

### Implications for Reference Files
| File | Potential Update |
|------|------------------|
| [file] | [what might change] |

### Open Questions
- [What we still don't know]
```

### 4. Checkpoint

> "Ready to make a decision, or need more research?"

Options:
- **Decide now** — Move to decision phase
- **More research** — Continue exploring
- **Save research, decide later** — Create research file, exit

### 5. Document Decision

Walk through options with pros/cons. Document the choice and rationale.

See [references/decision-template.md](references/decision-template.md) for structure.

### 6. Generate Action Items

Every decision ends with explicit action items for reference files:

```markdown
## Action Items

- [ ] Update reference/core/offer.md — Add guarantee section
- [ ] Update reference/proof/angles/risk-reversal.md — Create new angle
- [ ] Update reference/core/voice.md — Add "guarantee" to vocabulary
```

### 7. Checkpoint

> "Ready to update reference files now, or save for later?"

Options:
- **Codify now** — Apply action items immediately
- **Save decision** — Create decision file, codify later with `/think codify`

---

## Research Mode

Use when exploring without committing to a decision.

### Workflow

1. Define research question
2. Identify sources
3. Gather findings
4. Synthesize (required)
5. Save to `research/YYYY-MM-DD-topic-claude-code.md`

### Output Location

```
research/
└── YYYY-MM-DD-topic-claude-code.md
```

### Source Suffixes

| Suffix | Source |
|--------|--------|
| `-gemini.md` | Gemini deep research |
| `-gpt.md` | ChatGPT/GPT-4 |
| `-claude-code.md` | This Claude Code session |
| `-claude-web.md` | Claude.ai web |
| `-mining.md` | Internal data mining |
| `-audit.md` | Site/system audit |
| (none) | General/mixed |

### Exit Criteria

Research is complete when:
- [ ] Research question answered
- [ ] Synthesis section completed
- [ ] Key findings extracted (5-10 bullets)
- [ ] Open questions documented
- [ ] File saved to `research/`

---

## Decide Mode

Use when you've already done research and need to document a decision.

### Workflow

1. Check for related research
   - If found: Link in frontmatter
   - If missing: Prompt user — "Did you do research on this? Want to research first?"
2. Present options with pros/cons
3. Document decision and rationale
4. Generate action items
5. Save to `decisions/YYYY-MM-DD-topic.md`

### Output Location

```
decisions/
└── YYYY-MM-DD-topic.md
```

### Linking Research

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

### Exit Criteria

Decision is complete when:
- [ ] Context documented
- [ ] Options listed with pros/cons
- [ ] Decision stated with rationale
- [ ] Consequences listed (what becomes easier/harder)
- [ ] Action items specify which reference files to update
- [ ] File saved to `decisions/`

---

## Codify Mode

Use to apply a decision's action items to reference files.

### Workflow

1. Read the decision file
2. Extract action items
3. For each action item:
   - Read target reference file
   - Apply the specified update
   - Preserve existing content
4. Mark decision as "codified" in frontmatter

### Invoking

```
/think codify decisions/2026-01-17-pricing-strategy.md
```

### Safety

- **Never delete content** — Add or modify, don't remove
- **Confirm before writing** — "I'm about to update X files. Proceed?"
- **Atomic updates** — Complete all or none

### Exit Criteria

Codification is complete when:
- [ ] All action items from decision applied
- [ ] Reference files updated
- [ ] Decision status changed to "codified"
- [ ] User confirms changes are correct

---

## File Templates

### Research Template

See [references/research-template.md](references/research-template.md)

### Decision Template

See [references/decision-template.md](references/decision-template.md)

---

## Writing Good Synthesis

See [references/synthesis-guide.md](references/synthesis-guide.md)

Key principles:
- Force yourself to distill to one sentence
- If you can't summarize it, you don't understand it
- Explicit mapping to reference files prevents orphan research

---

## Context Preservation

Context flows through files, not memory.

```
Research File → Decision File → Reference Files
     ↑              ↑                ↑
  (created)    (links back)    (updated via codify)
```

**Why files as context:**
- Survives session compaction
- Auditable trail of reasoning
- Machine-readable for future sessions

---

## Decisions as Task Anchors

For substantial work, **create a decision file early** — even before you've fully decided. The decision file becomes your task tracker.

**How it works:**

1. Start project → Create `decisions/YYYY-MM-DD-topic.md` with `status: proposed`
2. Research and iterate → Update the file as you learn
3. Make the call → Change to `status: accepted`
4. Execute → Check off action items as you complete them
5. Finish → Change to `status: codified`

**Why this works:**
- Progress is visible in the file
- Rationale captured as you go
- Next session: check `decisions/` to see where you left off
- No separate task manager needed

**The `## Other actions` section** captures non-reference tasks (set up Stripe, update sales page, etc.).

**For smaller tasks:** Just do them. Decision files are for substantial work where the "why" matters.

---

## When NOT to Use

- Quick factual questions (just ask)
- Simple file edits (just edit)
- Generating content (use specific skills like `/ad-static`)

Use `/think` when the answer requires investigation and the choice needs documentation.

---

## Examples

### Example 1: Pricing Research

```
User: /think "what pricing tier should we use?"

Claude: Let me research pricing tier structures for your business type...
[Gathers information from reference files, web search, competitors]

Claude: ## Synthesis
One-sentence: Freemium with $97/month pro tier matches competitor pricing while preserving premium positioning.

Key findings:
- Competitors range $47-147/month for similar features
- Your audience responds to "investment" framing over "cheap"
...

Ready to make a decision, or need more research?

User: Let's decide

Claude: ## Considered Options

### Option A: Two-tier ($0 / $97/month)
Pros: Simple, clear upgrade path
Cons: May leave money on table from power users

### Option B: Three-tier ($0 / $97 / $297)
...

[Documents decision, creates action items]
```

### Example 2: Research Only

```
User: /think research "competitor messaging angles"

Claude: [Gathers, synthesizes, saves to research/2026-01-17-competitor-messaging-claude-code.md]

Research saved. Run `/think decide` when you're ready to choose your angle strategy.
```

### Example 3: Codify Past Decision

```
User: /think codify decisions/2026-01-15-guarantee-strategy.md

Claude: Reading decision file...

Action items found:
1. Update reference/core/offer.md — Add 30-day guarantee section
2. Update reference/proof/angles/risk-reversal.md — Create file

Proceed with updates? (y/n)

User: y

[Applies updates, marks decision as codified]
```

---

## References

- [references/research-template.md](references/research-template.md) — Template for research output
- [references/decision-template.md](references/decision-template.md) — Template for decision output
- [references/synthesis-guide.md](references/synthesis-guide.md) — How to write good synthesis
