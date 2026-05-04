---
name: mb-status
description: "Thin Main Branch status wrapper. Use when the operator asks what changed, what is healthy, what is stale, what to do next, or wants a daily briefing inside Claude Code."
---

# Status

Show the operator the deterministic Main Branch briefing without duplicating
repo-health checks in prose.

## Workflow

1. Confirm you are in the business repo. If not, ask the operator to `cd` into
   the business repo or pass the repo path.
2. Run:

```bash
mb status --json --peek
```

3. Treat the JSON as the source of truth for setup, update, drift, GitHub,
   onboarding, integrations, bets, since-last-check, readiness, and ranked
   actions.
4. Summarize the top `ranked_actions` first. For each one, include:
   - title
   - command or slash command
   - reason
   - cited signal summaries
5. Then summarize only the sections that matter for the operator's question.
   Do not re-run shell probes that duplicate status facts.

## Mutating The Last-Check Marker

`--peek` is the default inside this skill because a conversation may inspect
status before the operator is ready to record a daily check.

If the operator explicitly says this is the daily check-in and wants it
recorded, run:

```bash
mb status --json
```

Use the new report for the answer.

## Privacy

Respect each action and signal's `safe_to_share` field. If `safe_to_share` is
false, keep evidence local to the conversation and do not suggest pasting it
into public GitHub without review.
