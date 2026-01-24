---
name: think
description: "Combined research, decision, and codification workflow. Use when: (1) Exploring a question before committing (2) Making a decision that needs documentation (3) User says research, decide, figure out, explore, codify, enrich, add context (4) Updating reference files based on decisions (5) User wants to add new testimonials, angles, or proof to existing files. Supports modes: full flow, research-only, decide-only, codify."
---

# Think

Research, decide, and codify knowledge into reference files.

---

## Don't Overthink Think

This skill is for: **"I don't know what happens next. I just need to start."**

Something came your way — a video, a voice memo, a vague feeling, a problem to solve. You don't need a plan. Just start. The skill finds the overlap between your interest and your offer.

**Re-invoke often.** Saying `/think` again is normal. It reloads context. Do it after:
- Reading a large transcript (burns tokens)
- Compaction (context window reset)
- Switching focus
- Anytime you feel lost

---

## Two Modes of Work

Before diving in, know which mode you're in:

| Mode | You're doing | Examples |
|------|--------------|----------|
| **Enriching the core** | Pulling insights → reference files | Mining videos, making decisions, updating offer.md |
| **Creating for the world** | Reference files → output | Ads, scripts, courses, code, posts |

`/think` is for **enriching the core**. When you're ready to create, use `/ads`, `/content`, `/vsl`, or just ask.

Both are work. Enriching the core levels up everything downstream.

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

## Active Guidance (Your Job)

**Don't just provide templates. Actively move people through the cycle.**

On every `/think` invocation, detect state and guide the next step:

```bash
# Check for work in progress
ls -lt research/*.md 2>/dev/null | head -3
grep -l "status: proposed\|status: accepted" decisions/*.md 2>/dev/null
```

| If you find... | Then... |
|----------------|---------|
| Recent research, no decision | "You have research on [topic]. Ready to make a decision?" |
| Proposed decision | "Decision [topic] is proposed. Ready to accept it?" |
| Accepted decision, unchecked items | "Decision [topic] has action items. Ready to codify?" |
| Nothing in progress | "What are you trying to figure out?" |

**The goal is reference files.** Research and decisions are waypoints. Keep asking: "What needs to happen to get this into reference?"

---

## Full Flow (Default)

```
Research -> Checkpoint -> Decide -> Checkpoint -> Codify
```

### 1. Define Question

> "What specifically are you trying to figure out?"

### 2. Research

Gather from codebase, web, user input, local recordings. Spawn subagents for parallel research.

**Mining sources:**

| Source | How | Output suffix |
|--------|-----|---------------|
| YouTube videos | Apify transcript MCP | `-mining.md` |
| Local video/audio | whisper-cpp ([local-transcription.md](references/local-transcription.md)) | `-mining.md` |
| Voice memos | whisper-cpp | `-mining.md` |
| Instagram data export | File parsing | `-mining.md` |
| Competitor sites | Browser MCP or web fetch | `-mining.md` |
| Your own emails/DMs | Paste into conversation | `-mining.md` |
| Deep research | Build prompt → Gemini/GPT | `-gemini.md` or `-gpt.md` |
| Codebase exploration | Grep, read, subagents | `-claude-code.md` |

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

### 6. Action Items

List action items in the decision file:

```markdown
## Action Items
- [ ] Update reference/core/offer.md - Add guarantee section
- [ ] Create reference/proof/angles/risk-reversal.md
```

Optionally create Claude tasks for execution tracking. See [decide-phase.md](references/decide-phase.md).

### 7. Checkpoint

> "Ready to update reference files now, or save for later?"

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

| Layer | Scope | Use For |
|-------|-------|---------|
| **Claude tasks** | Session | Execution tracking, spinners |
| **Decision files** | Forever | Rationale, anchor for work |
| **GitHub issues** | Forever | Cross-session, team visibility |

Decision files are the anchor — create early with `status: proposed`, update to `accepted`, then `codified`.

See [decide-phase.md](references/decide-phase.md) for task creation patterns.
See [recovery.md](references/recovery.md) for resuming sessions.

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

---

## Why This Matters

Reference files aren't just documentation. They're how you stay connected to why you do this.

The act of researching, deciding, and codifying forces you to articulate:
- **Why you do this** — Not the marketing reason. The real reason.
- **Who actually benefits** — Not demographics. Real people whose lives change.
- **What transformation you enable** — Not features. The before/after.

Research and decisions go stale. Reference files compound. Every update makes all downstream content better.

If the overlaps between your interests and your offer don't make sense, maybe you have the wrong offer. The think cycle should feel like pull, not push.
