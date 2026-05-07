---
name: mb-status
description: "Thin Main Branch status wrapper. Use when the operator asks what changed, what is healthy, what is stale, what to do next, or wants a daily briefing inside Claude Code."
loops: [sense]
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
   onboarding, integrations, bets, journal activity, since-last-check,
   readiness, and ranked actions.
4. Summarize the top `ranked_actions` first. For each one, include:
   - title
   - command or slash command
   - reason
   - cited signal summaries
5. Then summarize only the sections that matter for the operator's question.
   Do not re-run shell probes that duplicate status facts.
   For "what changed?" or "what happened since last time?", answer from
   `since_last_check.journal` first, then top-level `journal` for recent
   context.
6. If provider readiness is the question, use `integrations.github` and
   `integrations.providers` from status first. If the operator needs choices or
   repair commands, run:

```bash
mb connect plan
mb connect doctor --json
```

Summarize GitHub, Cloudflare, Google/Workspace, Meta Ads, and Apify as numbered
business choices. Use the CLI's `next_command` or `repair_command`; do not ask
the operator to paste tokens into files or public issue text.

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
