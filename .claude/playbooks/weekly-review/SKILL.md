---
name: weekly-review
tier: playbook
calls: [think, end]
status: skeleton
description: "Skeleton playbook (v0.1). Walks the operator through a weekly review: status updates on running offers, decisions to ship, research to commit, log entries to write. v0.2 implementation lands real orchestration."
---

# weekly-review (skeleton)

A playbook that runs every Friday: surface what changed, force a status update on every running offer, commit any draft decisions or research, write the week's log entry.

**v0.1 status: skeleton.** This file documents the intent. Real orchestration in v0.2.

## Intended flow (v0.2 implementation)

```
1. mb validate          — confirm frontmatter is clean
2. mb graph             — print the link graph (changes since last week)
3. /think               — for each running offer, force a status update
4. /end                 — close the session with a log entry
5. log/                 — write weekly-review-YYYY-MM-DD.md
```

## Inputs

- The consumer repo's full state
- Optional: last week's `log/weekly-review-YYYY-MM-DD.md` for diff context

## Outputs

- Updated `core/offers/*/offer.md` files (status enums refreshed)
- A weekly log entry summarizing decisions, research, and shipped work
- Any draft decisions promoted from `proposed` to `accepted` or `rejected`

## Status enum reminder

`proposed | running | scaling | killed | graduated | died`

Every running offer gets a one-line status update during the playbook. Killed and died are first-class states — graduating an offer to `died` is the capture mechanism for "given my past losses, help me decide today."

## Cross-references

- [think/SKILL.md](../../skills/think/SKILL.md)
- [end/SKILL.md](../../skills/end/SKILL.md)
