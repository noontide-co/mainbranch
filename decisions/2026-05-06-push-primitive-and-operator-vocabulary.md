---
type: decision
date: 2026-05-06
status: accepted
topic: Push primitive, operator vocabulary, and campaign compatibility
linked_issues:
  - https://github.com/noontide-co/mainbranch/issues/329
  - https://github.com/noontide-co/mainbranch/issues/323
  - https://github.com/noontide-co/mainbranch/issues/324
linked_decisions:
  - decisions/2026-05-06-campaign-primitive-and-architecture-model.md
  - decisions/2026-05-06-main-branch-operating-spine.md
  - decisions/2026-05-06-campaigns-refuse-list.md
  - decisions/2026-05-05-operator-loops-taxonomy.md
tags: [v0-3, push, vocabulary, schema, compatibility, foundation]
---

# Push Primitive, Operator Vocabulary, And Campaign Compatibility

## Decision

The canonical engine primitive is **`push`**. The operator's business
calls it whatever it wants — *drop*, *launch*, *challenge*, *promo*,
*play*, *round*, *wave*, *campaign* — and the engine speaks the
operator's word back. Storage is canonical; language is personalized.

This decision turns the operating-spine principle "operator owns the
vocabulary, engine owns the taste" into a public product contract. It
covers four answers a future agent must be able to read off without
guessing:

1. What the engine calls the primitive.
2. What lives on disk.
3. What Claude says to the operator.
4. How existing `campaigns/` records keep working.

It is decision-only. Deterministic implementation lives in
[#323](https://github.com/noontide-co/mainbranch/issues/323).
Skill / runtime / migration code lives in
[#324](https://github.com/noontide-co/mainbranch/issues/324).

## 1. Canonical Engine Primitive

| Surface | Canonical name |
| --- | --- |
| Folder | `pushes/<YYYY-MM-DD-slug>/push.md` |
| Frontmatter `type:` | `push` |
| Link fields on other primitives | `linked_pushes` |
| `mb status` / `mb graph` JSON keys | `pushes`, `active_pushes`, `push_count`, etc. |
| CLI command surface | `mb push new`, `mb push close`, `mb push list`, `mb push open` |
| Bounded `kind:` enum | `launch \| drop \| challenge \| promo \| nurture \| outreach \| event \| announcement \| round \| wave` |

The folder uses **day** precision (`YYYY-MM-DD-slug`) to match every
other dated primitive in the repo (`decisions/`, `research/`, `bets/`,
`log/`). The merged campaign primitive decision's example used month
precision; the canonical shape going forward is day.

`kind:` is a frontmatter field, bounded, and engine-controlled. It
describes the *shape* of the push (a launch is multi-phase; a drop is
single-shot; a nurture is sequential). It is not the operator's
display word; that belongs in operator vocabulary (§3).

## 2. Legacy `campaigns/` Compatibility

`mb` continues to **read** every committed `campaigns/<slug>/campaign.md`
record. Specifically:

- `mb validate` accepts `campaigns/*/campaign.md` against the campaign
  schema and lifecycle from
  [decisions/2026-05-06-campaign-primitive-and-architecture-model.md](2026-05-06-campaign-primitive-and-architecture-model.md).
- `mb graph` and `mb status` index `campaigns/` records and surface them
  in the same shape as `pushes/`.
- `type: campaign` is a recognized alias of `type: push` on read.
- `linked_campaigns` is a recognized alias of `linked_pushes` on read.
- `campaign_path` and any committed examples that name campaign-shaped
  paths continue to resolve.

`mb` **writes** new records as `pushes/`. New skills, scaffolding, and
docs use the canonical push shape. There is no silent rewrite of
existing private repos — every migration is operator-initiated and
preview-first (§5).

This is a compatibility contract, not a permanent dual life. The
write-side support for `campaigns/` will sunset after the migration
command lands and at least one minor release of co-existence has
shipped. The read-side support stays until the engine ships a
deprecation that names a removal release.

## 3. Operator Vocabulary At `core/vocabulary.md`

The operator's preferred words live in **`core/vocabulary.md`**.
Tracked business truth in the business repo — not `.mb/`, not Claude
memory, not `CLAUDE.md`, not `core/voice.md`. The file is optional;
absent the file, the engine speaks its canonical words.

`core/voice.md` answers *how this business sounds* (cadence, register,
forbidden phrases, signature moves).
`core/vocabulary.md` answers *what this business calls operating
primitives* (the noun for a coordinated push, the synonym for a
status, the phrase for a channel).

These are two separate concerns and live in two separate files.

### Shape

```yaml
---
type: vocabulary
---
push: drop
status:
  active: live
  completed: shipped
channels:
  paid: paid traffic
  organic: content
kind:
  launch: launch
  drop: drop
  challenge: challenge
```

Bounded keys only — `push`, `status`, `channels`, `kind`. Anything
outside that set is ignored or warned by the validator. Per-key values
are display words; they replace the canonical word in operator-facing
copy without changing the underlying engine state.

### What vocabulary affects

- Skill prompts (e.g. `/mb-push new` says "want to open a drop?" when
  `push: drop` is set).
- `mb status` conversational output ("Your active drop: Workshop
  waitlist. Day 14.").
- Error messages aimed at operators.
- Narration drafts (the operator's word goes in published artifacts).

### What vocabulary does not affect

- Frontmatter on disk (`type: push`, `kind: launch`).
- Link fields (`linked_pushes`).
- Folder names (`pushes/`).
- JSON output keys (`pushes`, `active_pushes`).
- `mb validate` rules and enums.
- AGENTS.md, contributor docs, command reference, troubleshooting.

The rule from the operating spine applies: canonical storage is boring
and consistent; operator-facing language is personalized and consistent.
**Folder names, frontmatter types, JSON keys, and prose labels do not
mix casually.**

### Default and fallback

- No `core/vocabulary.md` → engine speaks canonical words (`push`,
  `active`, `completed`).
- Partial `core/vocabulary.md` → engine speaks operator's word where
  defined, falls back to canonical otherwise.
- Unknown keys in `core/vocabulary.md` → validator warns; engine
  ignores.

## 4. `git push` And `mb push`

The two coexist. The product command surface (`mb push <subcommand>`)
disambiguates.

- Documentation says `git push` when referring to the git operation.
- Documentation says `mb push new`, `mb push close`, etc. when referring
  to the engine command.
- Beginner and operator-facing copy that would otherwise say a bare
  "push" instead uses the operator's vocabulary word from
  `core/vocabulary.md` when one is set, or the canonical noun
  (a *push*) when none is set.
- Command reference and contributor docs may say "push" when the surface
  is unambiguous.

This is consistent with the operating-spine voice contract: avoid
unexplained internal jargon in beginner copy, but command reference
and technical material may name exact commands when precision matters.

## 5. Migration Policy

The implementation lives in #324; the **policy** lands here.

- **No silent migration.** Engine never rewrites a private repo without
  operator approval.
- **Preview before writes.** `mb doctor --include-migration` or
  `mb migrate` produces a plan and exits. The operator inspects the
  plan and re-runs with an explicit apply flag to land the moves.
- **Compatibility reads survive.** `campaigns/` records remain
  validatable and indexable for at least one minor release after the
  migration command ships.
- **One coordinated pass per repo.** The migration moves a repo from
  `campaigns/` to `pushes/`, renames `linked_campaigns` to
  `linked_pushes`, and leaves a record of the move in `log/`. It does
  not partially migrate; it does not interleave with unrelated changes.
- **Public examples and fixtures lead.** Engine-bundled fixtures and
  doc examples adopt `pushes/` first; private repos follow on the
  operator's schedule.
- **Public release notes name the deprecation.** When the engine
  schedules removal of write-side `campaigns/` support, the release
  notes say so explicitly with a version target.

## What This Decision Supersedes

This decision supersedes only the **canonical storage shape** from
[decisions/2026-05-06-campaign-primitive-and-architecture-model.md](2026-05-06-campaign-primitive-and-architecture-model.md).
That decision said the canonical primitive folder was `campaigns/`,
the frontmatter was `type: campaign`, and the link field was
`linked_campaigns`. Those are now compatibility reads. The canonical
shape is `push`.

It **does not** supersede the campaign primitive decision's other
contributions:

- The definition of a coordinated push (a named, bounded effort with
  a goal, audience, channels, timeline, and outcome) stands.
- The relationship model (*strategy → bet → offer → push → provider
  data → reflection*) stands.
- The lifecycle (`draft, planned, active, paused, completed, canceled,
  archived`) stands and is the lifecycle for `pushes/` records.
- The non-campaign artifact routing (`research/`, `documents/`,
  `log/`, etc.) stands.
- The architecture-doc work in `docs/system-architecture.md` stands;
  that doc gets a pointer to this decision and its primitive section
  updates the canonical name.

The campaigns refuse-list decision continues to apply unchanged. The
refused fields on `campaign.md` are refused on `push.md`.

## Consequences

- New business repos created after this decision lands write to
  `pushes/`. Existing repos with `campaigns/` keep validating; their
  operators choose when to migrate.
- `core/vocabulary.md` is a new optional reference file in the business
  repo. The scaffolding work to ship it (template, doctor check,
  validator schema, example) lives in #324.
- `mb status` JSON gains canonical `pushes` keys; legacy callers that
  read `campaigns` keys are supported for at least one minor release.
- Bundled skills (`/mb-ads`, `/mb-organic`, `/mb-site`, `/mb-vsl`,
  `/mb-bet`, `/mb-start`) are not rewritten in this branch. Their
  next material change adopts the canonical push surface and reads
  `core/vocabulary.md` if it exists. (Owned by #324.)
- Public docs that previously named `campaigns/` as the canonical
  primitive get updates in this branch's PR (`system-architecture.md`)
  or shortly after (README, AGENTS.md, contributor docs) as part of
  #324's coordinated pass.
- The merge into #323's deterministic engine work is unblocked: it can
  add `pushes/` schemas, dual-read campaign records, and ship the
  vocabulary validator without further architectural debate.

## Design Rule

Canonical storage is boring and consistent. Operator-facing language
is personalized and consistent. Folder names, frontmatter types, JSON
keys, and prose labels do not mix casually.

If a future PR ships `pushes/` writes while leaving `linked_campaigns`
in scaffolding, or `type: push` while skill prose still says
"campaign," that PR is incomplete and gets sent back. The migration
either moves cleanly or is held until it can.

## Sources

This decision applies the operating-spine principle that the operator
owns the vocabulary while the engine owns the taste. It draws on
common compatibility patterns from product database migrations
(canonical writes; aliased reads; preview-then-apply migrations) and
on operator-language research showing that real coaches, creators,
and community operators reach for *drop*, *launch*, *challenge*, and
*play* far more than *campaign* — while the word *campaign* already
means a Meta Ads object inside their tools.

The durable artifacts are this decision and the public docs that
will point at it.
