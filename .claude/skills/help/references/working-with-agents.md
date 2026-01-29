# Working with Agents

Claude can spawn parallel workers (subagents) to handle tasks simultaneously. You don't need to do anything special — skills invoke this automatically when it helps.

---

## What Are Subagents?

When Claude faces a task that benefits from parallel execution, it spawns Task agents — each gets its own context window, works independently, and returns results to the main conversation.

Think of it like delegating. Instead of Claude doing three research tasks sequentially (filling up your context window with raw content), it sends three workers out at once. Each comes back with a summary. Claude synthesizes across all of them.

---

## When They Help

**Multi-source research** (`/think`)
- Researching a topic across YouTube + X/Twitter + web simultaneously
- Each agent handles one source, saves its own research file, returns a 5-bullet summary
- Main conversation stays clean for synthesis

**Compliance review** (`/ads review`)
- Six lenses need to evaluate the same ad batch
- Each agent reads one lens file + the ad copy, returns P1/P2/P3 findings
- Main conversation merges all six into a unified report

**Batch generation** (future)
- Generating content across multiple angles or platforms simultaneously
- Each agent handles one angle/platform, returns output

---

## When They Don't Help

- **Iterative conversation** — When you're going back and forth refining something, subagents add overhead
- **Small tasks** — Quick edits, single-source research, simple questions
- **Tasks needing user input mid-stream** — Subagents can't ask you questions while running
- **Sequential dependencies** — When step 2 depends on step 1's output

---

## When File Writes Fail

Occasionally a subagent will report that it saved a file, but the file doesn't appear on disk. This is a known Claude Code bug — not a permissions issue. The agent's Write tool succeeds in its context but doesn't persist to the filesystem.

**What happens:** Claude detects the missing file and writes it from the agent's returned content. You may see: "Agent reported writing [file] but it doesn't exist. Writing from returned content now."

**This is automatic.** Skills instruct agents to verify their writes and return fallback content. You don't need to do anything.

---

## What You See

When Claude spawns subagents, you'll see something like:

> "Spawning 3 research agents: YouTube transcript, X sentiment, web search..."

Then results come back:

> "All 3 agents returned. Synthesizing across sources..."

You don't manage this. Claude decides when parallel execution is worth it based on the task.

---

## Context Management Tips

**Why context matters:** Claude has a finite context window per conversation. Long transcripts, mined posts, and raw research eat through it fast.

**Subagents help because:**
- Heavy content (a 90-minute YouTube transcript) lives in the subagent's window, not yours
- Only the distilled summary (5-10 bullets) returns to your main conversation
- Your main conversation stays clean for decision-making and synthesis

**Other context strategies:**
- Re-invoke skills (`/think`, `/ads`) after compaction to reload context
- Break long sessions by topic — finish one research thread before starting another
- Use `/start` to begin fresh sessions when context is heavy
- Reference files are your persistent memory — context windows are temporary

---

## How It Connects

| Skill | Uses Agents For |
|-------|----------------|
| `/think` | Multi-source research (YouTube + web + X simultaneously) |
| `/ads review` | 6 compliance lenses in parallel |
| `/help` | This page (you're reading it now) |

Skills handle the orchestration. You focus on the questions and decisions.
