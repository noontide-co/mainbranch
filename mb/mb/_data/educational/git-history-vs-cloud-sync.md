---
type: educational
topic: git-history-vs-cloud-sync
status: draft
last-updated: 2026-05-08
---

# Git history vs. cloud sync: why checkpoints matter

Cloud sync answers "is this file on another device?" Git history answers "what
changed, who changed it, and why did we preserve it?"

Main Branch needs the second answer.

## The beginner version

A git commit is a saved checkpoint. It is not developer ceremony. It is the
business saying:

"This change matters enough to remember."

When Main Branch talks about checkpoints, it means readable saved business
progress: a decision accepted, a push drafted, an offer updated, a repair
completed, or a lesson recorded.

## Why cloud sync is not enough

**Sync copies state.** It does not explain the business reason for the change.

**Sync can spread mistakes quickly.** If a file is wrong, deleted, or conflicted,
the sync tool may faithfully copy the problem.

**Sync history is not a work thread.** GitHub issues can hold tasks, blockers,
requests, and follow-ups. Pull requests can hold proposals and review
conversations. Git commits hold the saved evolution story.

**Agents need inspectable history.** An agent can read git history and answer
questions such as "what changed since yesterday?" or "which decision updated
the offer?" Cloud sync usually cannot provide that chain in a scriptable way.

## What Main Branch gives you

- `mb status` shows current facts and recent activity.
- `/mb-start` grounds Claude Code in those facts before advice.
- `mb checkpoint` plans or saves business-readable checkpoints.
- `/mb-end` helps close the session and preserve what changed.
- GitHub can share the task/proposal layer with a team.

## What Main Branch does not claim

Main Branch does not ask beginners to hand-manage branches, diffs, and merges
as the normal day. Those primitives are the hidden save system underneath the
business loop.

If something breaks, use `mb doctor`, `/mb-start`, or the exact command Main
Branch prints. Do not guess your way through git internals.
