---
name: end
description: "Session-closing skill that helps users wrap up intentionally. Use when: user says done, wrapping up, end my day, closing out, call it a day, goodnight, that's it for today, checkpoint, pause. Bookend to /start. Scans git activity, surfaces what happened, spawns a crystallize agent for deep analysis, commits uncommitted work, and closes with a brief summary. Works for end-of-day, end-of-research-batch, end-of-decision-sprint, or mid-work checkpoints."
---

# End

Close your session intentionally. The bookend to `/start`.

**You only run this when you choose to.** It is never auto-invoked.

---

## Philosophy

The end of a session is the highest-leverage reconnection point. All session you were doing -- researching, deciding, generating. Now you step back and see what actually happened. Accumulated doing becomes conscious understanding.

`/end` is not just end-of-day. It closes any significant session:

- **End of day** -- wrapping up, done for today
- **End of a research batch** -- crystallize before deciding
- **End of a decision sprint** -- step back and see what decisions mean together
- **Mid-work checkpoint** -- pause deep work, crystallize, then continue

The crystallize moment does not assume the user is leaving. It assumes the user wants to step back from doing and see what happened.

This is not an audit. It is a thoughtful friend helping you close the session.

---

## The Flow

```
1. Find the business repo
2. Scan today's activity
3. Session summary
4. Final thought capture (optional)
5. Crystallize (spawns dedicated agent if meaningful activity detected)
   5a. Check for meaningful activity
   5b. Gather file contents for the agent
   5c. Spawn crystallize agent (Task tool)
   5d. Present output to user as-is
   5e. If user engages: stay with it (engagement protocol)
   5f. Always save crystallize output as research file
6. Commit & close
```

Step 4 is optional. **Step 5 is NOT optional** -- if meaningful activity happened (decisions, research, reference changes), you MUST spawn the crystallize agent. Do not try to do the crystallize analysis inline. Do not skip it. The subagent gets a fresh context window and spends real tokens reading the day's files. That depth is the whole point.

A quick `/end` (user says "just commit and close") can be steps 1-3 and 6. But if there is meaningful activity and the user did not explicitly skip, always run Step 5.

---

## Step 1: Find the Business Repo

Read `~/.config/vip/local.yaml` for `default_repo` (primary). If not found, optionally check additional working directories as a fallback for a folder containing `reference/core/`.

**If no repo found:** Skip to a simple close. No business repo means no git activity to scan.

**Do not ask the user to pick a repo.** /end is a quick close, not a triage. Use the default. If the user worked in a different repo today, they can say so.

---

## Step 2: Scan Today's Activity

Run these in the user's business repo:

```bash
# What changed today
git log --since="6am" --oneline --no-merges 2>/dev/null

# Uncommitted changes
git status --short 2>/dev/null

# New or modified files today (staged + committed)
git diff --name-only --diff-filter=AM HEAD@{6am}..HEAD 2>/dev/null
```

**Parse what you find into categories:**

| Category | How to Detect |
|----------|---------------|
| Research files created | New files in `research/` |
| Decisions made | New or modified files in `decisions/` |
| Reference files updated | Modified files in `reference/` |
| Outputs generated | New files in `outputs/` or `content/` |
| Uncommitted changes | `git status --short` output |

**Multi-offer detection (skip if no `offers/` folder — single-offer mode, everything reads from `core/`):** If `reference/offers/` exists, note which offers had files changed:
```bash
git diff --name-only HEAD@{midnight}..HEAD -- reference/offers/ 2>/dev/null | head -20
```
Report: "Offers affected: community, newsletter" (or "Brand-level changes only" if only core/ changed)

**If git log fails** (no commits today, repo issues): Fall back to `git status` and `ls -lt` to find recently modified files. Don't block on this.

**If nothing happened today:** Say so briefly. "Quiet day -- no changes detected. Want to close out?" Skip to Step 6.

---

## Step 3: Session Summary

Present a brief, warm summary. Not a report -- a reflection.

**Offer context:** If `.vip/local.yaml` has `current_offer`, include in summary:
"Worked on: **[offer]**"

**Format (adapt to what actually happened):**

> "Here's what happened today:
>
> - Researched [topic] (research file saved)
> - Made a decision on [topic]
> - Updated offer.md with [what changed]
> - Generated a batch of [type] outputs
>
> [1 sentence connecting the dots -- what theme ties today's work together?]"

**Guidelines:**

- Keep it to 3-6 bullet points max. Summarize, don't list every file.
- If reference files were updated, highlight that -- it is the most valuable work.
- If decisions were made but not codified, note it gently: "Decision on [topic] is ready to codify when you're back."
- The connecting sentence should feel like an observation, not a judgment. "Lot of foundation work today" or "Focused session -- pricing is locked in now."

---

## Step 4: Final Thought Capture (Optional)

Ask once:

> "Any final thoughts before we close?"

**If the user shares something:**

- If it is brief (a sentence or two), acknowledge it and note it in the commit message or suggest adding it to an existing research file.
- If it is substantial (a paragraph or more), offer to save it: "Want me to save that as a quick research note? `research/YYYY-MM-DD-end-of-day-thoughts.md`"
- Use today's date. Source suffix: `-end-of-day.md`

**If the user says no, nothing, or skips:** Move on. No friction.

**After Step 4 -- whether the user engaged or not -- proceed to Step 5.** Do not stop here. Do not wait for permission. If meaningful activity happened today, the crystallize agent runs next.

---

## Step 5: Crystallize

**YOU MUST SPAWN A SUBAGENT FOR THIS STEP.** Do not attempt the crystallize analysis in the main conversation. The main conversation has been burning tokens all session. The crystallize agent gets a fresh context window and spends 50-100K tokens reading the actual files from today -- decisions, research, soul.md, reference diffs. That depth is what makes the question good. Without the subagent, you will default to generic questions like "What did you learn?" which is the exact failure this architecture was built to prevent.

A dedicated subagent performs deep analysis of the session's work and generates one crystallize output -- context plus questions that make the user stop and think.

**Core purpose:** Enrich data and help the user fill in the gaps and find the why.

### 5a. Check for Meaningful Activity

Check if decisions, research, or significant reference changes happened today:

```bash
# Decisions created or modified today
git log --since="6am" --name-only --diff-filter=AM -- decisions/ 2>/dev/null

# Research created today
git log --since="6am" --name-only --diff-filter=A -- research/ 2>/dev/null

# Reference changes
git diff --name-only HEAD@{6am}..HEAD -- reference/ 2>/dev/null
```

**When to skip crystallize entirely:**
- No decisions, research, or reference changes (truly nothing happened)
- Context window critically low (under 30K remaining)
- User explicitly asked for a quick close ("just commit and close")

**Light days:** If only minor activity (one small edit, no decisions), the agent still runs but shifts focus to reference gaps. See [references/crystallize-agent.md](references/crystallize-agent.md) for light-day behavior.

### 5b. Gather File Contents

Before spawning the agent, read and collect:

| Content | How | Always/Conditional |
|---------|-----|-------------------|
| Today's git summary | From Step 2 output | Always |
| Today's decision files (full text) | Read each file detected in 5a | Always |
| Today's research files (full text) | Read each file detected in 5a | Always |
| Reference file diffs | `git diff HEAD@{6am}..HEAD -- reference/` | If reference changed |
| `reference/core/soul.md` | Read full file | Always |
| `reference/domain/content-strategy.md` | Read full file | If it exists |
| Past crystallize outputs | Read `research/*-end-of-day-crystallize.md` | If any exist |

**Heavy-day adaptation:** If more than 5 research files exist for today, pass commit messages + file names for all research, but full text only for the 3-5 most recent or most connected to today's decisions.

### 5c. Spawn the Crystallize Agent

Use the Task tool to spawn a dedicated subagent with a full context window:

```
Task(
  subagent_type: "general-purpose",
  description: "Crystallize agent: analyze today's session work and generate
    a crystallize output (context block + questions) that surfaces unnamed
    tensions, connects tactical work to existential purpose, and identifies
    reference gaps."
)
```

**Agent prompt construction:** Build a structured prompt containing all gathered content from 5b, plus the agent instructions. See [references/crystallize-agent.md](references/crystallize-agent.md) for the complete agent prompt template, analysis process, anti-patterns, and question design criteria.

**Pass to crystallize agent:** Include `current_offer` from `.vip/local.yaml` so the agent can analyze offer-specific reference changes and ask offer-relevant questions.

**The agent is read-only.** It reads files and returns findings. It does not write files. The main conversation handles all file writes.

**The agent returns:** A crystallize output block -- 2-4 sentences of context followed by 1-3 questions. The main conversation presents this to the user exactly as returned, without editing or summarizing.

### 5d. Present to User

Show the crystallize output exactly as the agent returned it. Do not summarize, reword, or add commentary.

### 5e. Engagement Protocol

If the user engages with the crystallize question, the main conversation handles the dialogue (the agent's job is done).

**Rules:**

1. **Let them go deep.** Never redirect to "pick this up with /think." If someone is having an insight at session's end, that is the highest-value moment. Stay with it.
2. **Listen and reflect.** Reflect back what they said in one sentence. Give them space to refine their thinking.
3. **Name what they are doing.** If they articulate a new belief: "That sounds like a new entry for soul.md." If they resolve a tension: "That is a decision waiting to be written."
4. **If insight updates reference, offer to do it.** Don't push -- just offer.
5. **Never push.** If they say one sentence and stop, let them stop. The question was planted. The insight might arrive tomorrow.

See [references/crystallize-agent.md](references/crystallize-agent.md) for the full engagement protocol with examples.

### 5f. Always Save the Crystallize Output

**This is not optional.** Every crystallize moment gets saved as a research file. Future crystallize agents read these for temporal pattern recognition.

```markdown
---
type: research
date: YYYY-MM-DD
source: crystallize
status: complete
---
# End-of-Day Crystallize

## Question Asked
[The crystallize question as presented]

## User Response
[What the user said, or "No engagement" if they skipped]

## Insight Captured
[Any insight that emerged, or empty if none]

## Reference Updated
[Which files were updated as a result, or "None"]
```

Save to: `research/YYYY-MM-DD-end-of-day-crystallize.md`

If an insight was substantial enough to update reference directly (soul.md, offer.md, etc.), do so and note it in the crystallize file.

---

## Step 6: Commit & Close

### Check for uncommitted work

```bash
git status --short 2>/dev/null
```

**If there are uncommitted changes:**

> "You have uncommitted changes:
>
> - [list modified/new files, brief]
>
> Want me to commit these?"

If yes:
- Stage the changed files (prefer specific files over `git add -A`)
- Write a descriptive commit message following the `[type] Brief description` convention
- If work was offer-specific, suggest commit message like: `[update] community offer: added pricing tiers and guarantee`
- If the user shared final thoughts in Step 4, incorporate them into the commit message
- Include the crystallize research file in the commit
- Commit

If no: Leave them. Some people prefer to commit at start of next session.

**If no uncommitted changes:** Skip this.

### The Close

End with a brief, warm close. Not a performance review -- a goodbye.

**Pattern:**

> "Good session. [1 sentence summary of the most important thing that happened]. See you next time."

**Examples:**

> "Good session. Pricing is locked in and your offer is stronger for it. See you next time."

> "Good session. Three new angles ready for ads whenever you are. See you next time."

> "Quiet day, but that research on [topic] will pay off when you decide. See you next time."

> "Solid work. Reference files are updated and everything downstream just got better. See you next time."

**Do not:**
- List everything again (the summary was Step 3)
- Suggest what to do tomorrow (that is /start's job)
- Be overly enthusiastic or performative
- Use emojis

---

## Handling Edge Cases

### User says /end but hasn't done anything

> "Nothing to close out -- no changes detected today. See you next time."

### User says /end mid-task

> "You have work in progress -- [describe what's open]. Want to finish that first, or close out and pick it up next time?"

If they want to close: commit what exists, note the state in the commit message.

### Context window is nearly full

Keep it ultra-brief. Scan, commit if needed, close. Skip Steps 4 and 5.

### Multiple repos in session

Only scan the primary business repo (from config). If the user worked across repos, they can mention it.

### No git repo / no business repo

> "No business repo found. If you want session tracking, run `/setup` next time to create one. See you next time."

---

## What /end Is NOT

- **Not a daily standup.** No plans for tomorrow.
- **Not a task manager.** No to-do lists or assignments.
- **Not a journal.** The final thought capture is optional and brief.
- **Not an audit.** The summary is observational, not evaluative.
- **Not /think** -- but if someone is having an insight, stay with it. The crystallize moment can go deep. That is the point.

---

## Tone

Same as the rest of Main Branch: a thoughtful friend. Brief. Warm. Not performative.

The close should feel like the end of a good conversation -- not a report card, not a ceremony. Just: "Here's what happened. Anything else? Good. See you."

---

## References

- [references/crystallize-agent.md](references/crystallize-agent.md) -- Agent prompt template, analysis process, anti-patterns, question design, engagement protocol, examples
