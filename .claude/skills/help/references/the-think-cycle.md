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

## Working After Compaction

When Claude hits the context limit, it compacts — the conversational thread gets summarized and older details fade. This can feel disorienting, but the system is designed for exactly this scenario.

**Your files survive no matter what.** Research files, decision files, reference files — they're on disk, version controlled in git. Compaction loses conversational context, not your repo. If an insight made it into a file, it's safe. If it only existed in conversation, it's gone after compaction. When in doubt, save a research file.

**You can help Claude rebuild context fast.** After compaction (or in a new session), point Claude at recent work:
- "Look at my last 3 decisions"
- "Read the commits from today"
- "Summarize what's in `research/` from this week"

Claude picks up the thread from your files, not from memory.

**`/start` does this automatically.** It scans your folders, checks recent activity, and routes you to the right place. You don't have to manually reconstruct anything — just `/start` and go.

**You can always look yourself.** Open your repo in Cursor, Warp, VS Code, or any text editor. The files are plain markdown. Browse `decisions/` to see where you left off. Read `research/` to remember what you explored. Your repo is readable by humans, not just AI.

**Context management is a skill.** It's nuanced at first — knowing when to save a file, how much to capture, when to update reference vs. leave as research. But it gets easier. After a few sessions, the rhythm becomes natural: think, capture, move on. The system handles the rest.

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
- Content generation (use `/ads`, `/organic`, `/vsl`, etc.)

---

## The Three Modes

| Mode | What It Does |
|------|--------------|
| `/think "topic"` | Inline usage — give it a question directly and it runs the full flow: research → decide → codify. Works great for specific questions. |
| `/think research "topic"` | Just investigate, save findings |
| `/think decide "topic"` | Document decision (research already done) |

**Note:** `/think` by itself (no argument) loads the full skill with routing and mode detection — it'll ask what you want to work on and guide you through the process. Both approaches are valid. Inline is faster when you know the question; bare `/think` is better when you want to explore or aren't sure where to start.

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

**The decision file tracks what changes:**
- `## What Changes` = Which reference files are affected and how
- `## Review Date` = When to revisit (optional)

**Example workflow:**

1. Start a big project → Create `decisions/2026-01-21-new-pricing-strategy.md` with `status: proposed`
2. Research, think, iterate → Update the file as you learn
3. Make the call → Change to `status: accepted`, describe what changes
4. Codify → Apply changes to reference files
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

## Closing the Loop: /end

At the end of a session, `/end` offers a natural crystallize moment. If you made decisions during the day, it asks: "What did you learn?" This is where accumulated doing becomes conscious understanding -- the highest-leverage point in the think cycle. You don't have to engage with it, but when you do, the insights often update reference files in ways that improve everything downstream.

If you're worried about losing work when a session ends, `/end` is your safety net — it reviews everything that happened and makes sure nothing falls through the cracks before you close.

---

## Next Step

Got a question you've been wrestling with? Run `/think`. The habit of documenting your thinking is what makes this powerful over time.
