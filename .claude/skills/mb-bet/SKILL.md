---
name: mb-bet
description: "Open, update, close, list, and narrate Main Branch business bets from repo truth. Use when the operator wants to frame an operating bet, track progress, capture a verdict, or draft public-safe narration."
loops: [decide, reflect, ship]
---

# Bet

Business bets are hub nodes in `bets/`. They connect decisions, research,
pushes, logs, documents, and outcomes without replacing any of them. Legacy
`campaigns/` records may still be linked for old repos, but new coordinated
work uses `pushes/`.

A bet is not an offer. An offer is a durable thing the business sells. A bet is
a time-boxed operating hypothesis with appetite, target, deadline, evidence,
and a verdict. A successful bet may graduate into an offer, workflow, content
pillar, push, or decision; a failed bet should be closed with learning.
For the full offer/bet/push/proof routing rubric, use
`.claude/reference/business-primitives/offer-bet-push-proof.md`.

Use `/mb-bet` for five modes:

- `new` - open a bet with hypothesis, appetite, metric, target, deadline, and links.
- `update` - add progress and link new evidence.
- `close` - record result, verdict, learning, and follow-up links.
- `list` - summarize active bets and deadlines.
- `narrate` - draft public-safe site, community, or social copy from repo truth.

Do not publish automatically. Narration drafts are files or message drafts only.

## Repo Rules

Work from the business repo. If unsure, confirm that `core/`, `research/`,
`decisions/`, or `bets/` exists in the current directory. If not, ask the
operator to start Claude from the business repo or run `/mb-start`.

**CLI facts first:** Use `mb status --json --peek` for active bets and repo
readiness before direct file reads. Use `mb validate --cross-refs` after
bet/link edits instead of hand-checking relationship health in prose.

Before writing, run:

```bash
mb status --json --peek
```

Use the result to spot active bets and repo readiness. After writing or editing
bet files, run:

```bash
mb validate --cross-refs
```

If validation warns about missing bidirectional bet links, repair the linked
file frontmatter when it is clearly in scope.

## Bet Frontmatter

Every bet file lives at `bets/YYYY-MM-DD-slug.md` and uses this frontmatter:

```yaml
---
status: open
opened: YYYY-MM-DD
deadline: YYYY-MM-DD
appetite: "2 weeks"
hypothesis: "If we do X for Y, Z will happen because..."
metric: "qualified calls booked"
target: "10 qualified calls by deadline"
result: ""
linked_decisions: []
linked_research: []
linked_pushes: []
linked_campaigns: []
linked_outcomes: []
public: false
channels: []
tags: []
---
```

Allowed statuses: `open`, `paused`, `closed`, `canceled`.

Use repo-relative paths in link fields:

- `linked_decisions`: `decisions/*.md`
- `linked_research`: `research/*.md`
- `linked_pushes` (official): `pushes/YYYY-MM-DD-slug/push.md` or push artifacts
- `linked_campaigns` (legacy compatibility, leave as `[]` for new bets):
  `campaigns/*/campaign.md` records on existing repos that have not yet
  migrated. New bets always include both fields with `linked_pushes`
  populated and `linked_campaigns: []`. When the operator is on a legacy
  campaigns/ repo, recommend `mb doctor` and `mb migrate campaigns --plan`
  before creating new push work.
- `linked_outcomes`: `log/*.md`, `documents/*.md`, or outcome artifacts

When linking an existing file to a bet, add the reverse link too:

```yaml
linked_bets:
  - bets/YYYY-MM-DD-slug.md
```

After adding or changing typed `linked_*` frontmatter, add or repair the
body-level `## Related links` mirror with Markdown relative links. If the
mirror is missing or stale, run `mb doctor repair --plan` and ask before
`mb doctor repair --apply`; use the connection decision matrix in
docs/business-connections.md and do not invent relationships from body links.

## Mode: new

Use when the operator says they want to try, launch, test, prove, or make a bet.

1. Ask only for missing essentials: hypothesis, appetite, deadline, metric,
   target, public/private posture, channels, and any known linked files.
2. If the idea also sounds like a new offer, ask whether it is only a wager for
   now or whether the operator wants to preserve a durable offer candidate too.
   Do not create, rename, delete, or move `core/offers/` folders without an
   accepted decision, approved migration plan, or explicit instruction.
3. Create `bets/YYYY-MM-DD-slug.md`.
4. Add reverse `linked_bets` frontmatter to linked decisions, research,
   pushes (or legacy campaigns), and outcome files when those files already
   exist and the edit is clearly safe.
5. End with the file path, deadline, target, and next action.

Body template:

```markdown
# Bet Title

## Why This Bet

[The operating tension or opportunity.]

## Hypothesis

[Same claim as frontmatter, with context.]

## Work Plan

- [ ] [Concrete action]

## Evidence Log

- YYYY-MM-DD - Bet opened.

## Result

Open.

## Narration Notes

[Public-safe angles, claims to avoid, proof needed before sharing.]

## Related links

- [Existing linked file](../decisions/YYYY-MM-DD-example.md)
```

## Mode: update

Use when work happened but the bet is not finished.

1. Read the bet and linked files.
2. Append a dated `Evidence Log` entry.
3. Update `linked_decisions`, `linked_research`, `linked_pushes` (or legacy
   `linked_campaigns`), or `linked_outcomes` if new files now matter.
4. Keep `result` blank unless there is a real result.
5. Repair reverse `linked_bets` fields on newly linked files.

## Mode: close

Use when the deadline passed, the target is hit, or the operator decides to stop.

1. Ask for the actual result if repo evidence is not enough.
2. Set `status: closed` or `status: canceled`.
3. Fill `result` with the measured outcome and verdict.
4. Add a `## Learning` section or update it if present.
5. Link outcome files and add reverse `linked_bets` fields.
6. If the bet changes durable offer truth, suggest a follow-up decision before
   editing `core/offer.md` or `core/offers/<slug>/offer.md`.
7. Graduation options: update an existing offer, create a new offer candidate,
   create a push/playbook, update proof, or justify a linked child repo. Keep
   the closed bet as history.
8. For paused, dead, superseded, or canceled offer ideas, preserve the record
   and mark status/verdict; do not delete offer folders as cleanup.

## Mode: list

Summarize active bets from `mb status --json --peek` and direct file reads:

- deadline
- status
- target
- metric
- public/private posture
- blocked or overdue signals

Keep it short. End with the next bet that needs attention.

## Mode: narrate

Draft public-safe narration from the bet and linked repo truth. Do not invent
results, metrics, claims, testimonials, or publishing channels.

Ask the operator which surface if unclear:

1. site
2. community
3. social

Draft format:

```markdown
# Narration Draft

Surface: [site/community/social]
Source bet: bets/YYYY-MM-DD-slug.md

## Public Angle

[What can be shared safely.]

## Draft

[Post or page copy.]

## Claims To Verify

- [Any metric, result, or proof that needs source confirmation.]

## Source Links

- [repo-relative paths read]
```

If the bet has `public: false`, ask before drafting public copy. Offer a private
internal retrospective instead.

## Exit

Tell the operator what changed, which files were linked, and whether validation
passed. If bet files or linked repo truth changed, run `mb checkpoint --plan
--json`, show the proposed checkpoint and any blockers, validate the chosen
message with `mb checkpoint --validate "..." --json`, and save with
`mb checkpoint --message "..." --yes` only after operator approval.

End with the exact next command:

```bash
mb status
```
