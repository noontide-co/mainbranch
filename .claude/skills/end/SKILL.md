---
name: end
description: "Session-closing skill that helps users wrap up intentionally. Use when: user says done, wrapping up, end my day, closing out, call it a day, goodnight, that's it for today. Bookend to /start. Scans git activity, surfaces what happened, offers a crystallize moment for accumulated decisions, commits uncommitted work, and closes with a brief summary."
---

# End

Close your session intentionally. The bookend to `/start`.

**You only run this when you choose to.** It is never auto-invoked.

---

## Philosophy

The end of a session is the highest-leverage reconnection point. All day you were doing -- researching, deciding, generating. Now, for thirty seconds, you step back and see what actually happened. Accumulated doing becomes conscious understanding.

This is not an audit. It is a thoughtful friend helping you close the day.

---

## The Flow

```
1. Find the business repo
2. Scan today's activity
3. Session summary
4. Final thought capture (optional)
5. Crystallize prompt (if decisions were made)
6. Commit & close
```

Progressive disclosure: steps 4 and 5 only happen if the user engages. A quick `/end` can be steps 1-3 and 6 in under a minute.

---

## Step 1: Find the Business Repo

Read `~/.config/vip/local.yaml` for `default_repo`. If not found, check additional working directories for a folder containing `reference/core/`.

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

**If git log fails** (no commits today, repo issues): Fall back to `git status` and `ls -lt` to find recently modified files. Don't block on this.

**If nothing happened today:** Say so briefly. "Quiet day -- no changes detected. Want to close out?" Skip to Step 6.

---

## Step 3: Session Summary

Present a brief, warm summary. Not a report -- a reflection.

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

---

## Step 5: Crystallize Prompt (If Decisions Were Made)

**Only trigger this if decisions were created or accepted today.** Check:

```bash
# Decisions created or modified today
git log --since="6am" --name-only --diff-filter=AM -- decisions/ 2>/dev/null
```

If decisions or research exist, craft ONE genuinely provocative question.

**This is the most important step in /end.** Don't ask generic questions like "What did you learn?" or "What shifted?" Read the actual decisions and research from today. Find the thread that's still pulling -- the unanswered question, the tension between two choices, the implication nobody said out loud yet. Ask THAT.

**How to craft the question:**

1. Read today's decision files and research files (at least skim them)
2. Look for: unresolved tensions, assumptions that weren't tested, implications that weren't followed, connections between separate decisions that nobody drew yet
3. Ask one question that makes them stop and think -- the kind of question a great advisor would ask at the end of a strategy session

**Examples of BAD crystallize questions:**
- "What did you learn today?" (too generic)
- "What shifted in your thinking?" (sounds like therapy homework)
- "You made 3 decisions. Anything to add?" (not a real question)

**Examples of GOOD crystallize questions:**
- "You positioned Main Branch as a thinking system, not a memory tool. But your pricing tiers are structured around feature access. Is the thing you're selling aligned with the thing you're saying?"
- "You built 5 new angles today but your content strategy still has zero content derived from 53 decisions. What's actually blocking the pipeline?"
- "You decided trial members get full access. What happens to the people who downgrade after 7 days but already built reference files with premium skills?"

The question should feel like it came from someone who was paying attention all day. Because you were.

**If the user engages:**

- Let them explore. This is their thinking time. Don't rush to close.
- Listen. Reflect back what they said in one sentence.
- If the insight is substantial, offer to save it -- append to a decision file, update a reference file, or create a quick research note.
- If they surface a pattern across multiple decisions, offer to capture it where it belongs.
- If the exploration goes deep, let it go deep. Don't deflect to "pick it up with /think next session." If someone is having an insight at the end of their day, that's the highest-value moment. Stay with it.

**If the user deflects or says "nothing":** That is fine. Say something like "Fair enough" and move on. Never push.

**If nothing meaningful happened today:** Skip this step. Don't force a crystallize moment on a light session.

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
- If the user shared final thoughts in Step 4, incorporate them into the commit message
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
- **Not /think** — but if someone is having an insight, stay with it. The crystallize moment can go deep. That's the point.

---

## Tone

Same as the rest of Main Branch: a thoughtful friend. Brief. Warm. Not performative.

The close should feel like the end of a good conversation -- not a report card, not a ceremony. Just: "Here's what happened. Anything else? Good. See you."
