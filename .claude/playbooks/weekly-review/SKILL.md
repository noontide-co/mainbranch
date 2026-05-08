---
name: weekly-review
tier: playbook
calls: [start, think, end]
status: skeleton
description: "Reusable skeleton playbook. Walks the operator through a weekly review across bets, offers, pushes, playbook runs, outcomes, decisions, logs, and checkpoints. Not yet a single executable orchestrator."
---

# weekly-review (skeleton)

This is a reusable operating recipe, not a one-off weekly review file. Use it to
surface what changed, decide what needs attention, record outcomes from active
pushes and playbook runs, promote approved research or decisions, and save a
checkpoint.

**Current status: skeleton.** This file documents the intended review chain and
artifact routing. It is not yet executable as one coherent workflow with a
single progress surface, automatic diffs, or cross-skill data passing. Run the
checks and skills manually today.

## Playbook Versus Run

This file is the reusable engine recipe under `.claude/playbooks/weekly-review/`.
The concrete review belongs in the business repo. Use:

- `log/weekly-review-YYYY-MM-DD.md` for the week-level chronology, decisions,
  blockers, and handoff notes;
- `pushes/<push>/playbooks/<playbook>.md` when reviewing one push playbook run's
  approvals, forks, validation evidence, manual steps, or linked outcomes;
- `pushes/<push>/review-log.md`, `pushes/<push>/reviews/`, or outcome/log links
  when the review changes the push state;
- `research/`, `core/`, `decisions/`, or `bets/` only when the operator
  approves durable memory updates.

Do not write new work under `campaigns/`; that folder is legacy compatibility
read only.

## Intended Flow

```text
1. /mb-start or mb status --json --peek
   Read repo health, updates, provider readiness, active bets, pushes, and
   recent activity.
2. mb validate
   Confirm frontmatter and links are clean enough to trust the review.
3. mb graph
   Inspect relationship drift across bets, offers, pushes, decisions, outcomes,
   and legacy compatibility records.
4. Active bets and offers
   Identify bets needing a verdict, offers needing a status note, and proposed
   core updates that require operator approval.
5. Pushes and playbook runs
   Review active or recently completed pushes, including
   pushes/<push>/playbooks/<playbook>.md run records, provider-boundary notes,
   validation evidence, manual steps, and linked outcomes.
6. /mb-think
   Codify approved lessons into research, core files, decisions, bet verdicts,
   or proposed updates.
7. /mb-end
   Close with a weekly log entry and checkpoint plan.
8. mb checkpoint
   Save accepted artifacts after operator approval.
```

## Inputs

- The business repo's full state
- Optional: last week's `log/weekly-review-YYYY-MM-DD.md` for diff context
- Active and recently completed `pushes/`
- Push playbook run records under `pushes/<push>/playbooks/`
- Open bet verdicts, proposed decisions, research drafts, and outcome files

## Outputs

- A weekly log entry at `log/weekly-review-YYYY-MM-DD.md`.
- Updated bet verdicts, push reviews, playbook run records, or outcome links
  when the operator approves the change.
- Approved updates to `core/offers/*/offer.md`, `core/audience.md`,
  `core/proof/`, research, or strategy files when the week changes durable
  business truth.
- Draft decisions promoted from `proposed` to `accepted` or `rejected` only
  after an explicit operator decision.
- A checkpoint plan and operator-approved checkpoint for accepted artifacts.

## Review Boundaries

- Preserve primitive boundaries:
  - bets answer "what are we trying to learn?";
  - offers answer "what do we sell repeatedly?";
  - pushes answer "what coordinated work is shipping?";
  - push playbooks answer "what happened in this run?";
  - logs answer "what happened this week?"
- Do not delete, rename, or collapse bets, offer folders, pushes, or child repos
  during review. Link forward when work graduates, is superseded, or needs a
  follow-up.
- Keep provider/account data safe. Do not commit tokens, raw exports, customer
  records, screenshots with private account details, session secrets, or local
  absolute paths.

## Skeleton Caveats

- Each step runs as its own command today.
- No automatic weekly diff or progress UI exists yet.
- Status updates should follow the current validators for the file being edited;
  do not invent new enum values in reusable prose.
- Provider mutation remains manual or provider-native unless a future accepted
  adapter ships with approval gates and smoke evidence.

## Cross-references

- [start/SKILL.md](../../skills/mb-start/SKILL.md)
- [think/SKILL.md](../../skills/mb-think/SKILL.md)
- [end/SKILL.md](../../skills/mb-end/SKILL.md)
