# The /think Cycle

The heart of Main Branch. Research, decisions, and reference files ARE your project management.

---

## The Cycle

```
RESEARCH → DECIDE → CODIFY → GENERATE → LEARN
    ↑                                      │
    └──────────────────────────────────────┘
```

1. **Research** - Investigate, gather information
2. **Decide** - Choose with documented rationale
3. **Codify** - Update reference files
4. **Generate** - Skills produce outputs
5. **Learn** - Feed results back into research

Each loop makes your reference more accurate, outputs more effective.

---

## How /think Works

```
/think "What pricing tier should we use?"
```

Claude will:
1. Research (web, your files, your context)
2. Synthesize into clear summary
3. Present options with pros/cons
4. Help you decide
5. Save research and decision as files
6. Optionally update reference

---

## What Gets Saved

| Type | Location | Purpose |
|------|----------|---------|
| Research | `research/2026-01-19-topic-claude-code.md` | Dated investigations |
| Decisions | `decisions/2026-01-19-topic.md` | Choices with rationale |
| Reference | `reference/core/offer.md` | Evergreen truth skills consume |

---

## Why Record Everything?

**Context windows are limited.** Hit 85k tokens and things compact. Conversation fades.

**Files persist.** Come back next week, your research is there. Six months later, the decision file explains why you did it that way.

**Knowledge compounds.** Each file builds on the last. Your business thinking becomes institutional memory.

---

## What Counts as Research?

Research is broad:

| Type | Example |
|------|---------|
| Web research | Gemini deep research on platform updates |
| Data mining | Download social media data, parse for insights |
| Transcript analysis | Pull a podcast, extract angles |
| Competitor mining | Study what's working for others |
| Internal audit | Review past campaigns for patterns |

Research = any investigation that informs a decision.

---

## When to Use /think

**Use it for:**
- Pricing, positioning, messaging decisions
- Processing data dumps into insights
- Any "should we...?" question

**Don't need it for:**
- Quick factual questions (just ask)
- Simple file edits (just edit)
- Content generation (use `/ads`, `/content`, `/vsl`, etc.)

---

## The Three Modes

| Mode | What It Does |
|------|--------------|
| `/think "topic"` | Full flow: research → decide → codify |
| `/think research "topic"` | Just investigate, save findings |
| `/think decide "topic"` | Document decision (research already done) |

---

## Synthesis is Required

Every research output must have:
- One-sentence summary (20 words max)
- Key findings (5-10 bullets)
- Implications for reference files
- Open questions

If you can't summarize it, you don't understand it yet.

---

## Example

```
/think "How to migrate my GPT knowledge base to Main Branch"
```

**Research:** What can be exported? What formats? How to organize?

**Decide:** Extraction method, organization structure.

**Codify:** Execute migration, update reference files.

**Result:** Documented process AND knowledge now in Main Branch.

---

## Decisions as Task Anchors

For substantial work, **create a decision file early** — even before you've fully decided.

**How it works:**

| Status | Meaning |
|--------|---------|
| `proposed` | I'm working on this, exploring options |
| `accepted` | Decision made, now executing |
| `codified` | Done — reference files updated |

**The decision file becomes your task tracker:**
- `## Action Items` = Your task list (with checkboxes)
- `## Other actions` = Non-reference tasks
- `## Review Date` = When to revisit

**Example workflow:**

1. Start a big project → Create `decisions/2026-01-21-new-pricing-strategy.md` with `status: proposed`
2. Research, think, iterate → Update the file as you learn
3. Make the call → Change to `status: accepted`, finalize action items
4. Execute → Check off action items as you complete them
5. Finish → Change to `status: codified`

**Why this works:**
- Progress is visible in the file itself
- Rationale is captured as you go
- Next session, check your `decisions/` folder — you know exactly where you left off
- No separate task manager needed

**For smaller tasks:** Just do them. Decision files are for substantial work where the "why" matters.

---

## Task Tracking Options

Different people prefer different approaches. See [task-tracking-options.md](task-tracking-options.md) for the full spectrum:

| Approach | Best For |
|----------|----------|
| **decisions/** as anchors | People who think in choices |
| **GitHub Issues** | Developers, CLI-native users |
| **focus.md** file | People who want one status file |
| **External tools** | Teams, complex workflows |

Pick one and commit. The system adapts.

---

## Next Step

Got a question you've been wrestling with? Run `/think`. The habit of documenting your thinking is what makes this powerful over time.
