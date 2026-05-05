# Roadmap

This roadmap is direction, not a promise. GitHub issues and release notes are
the detailed execution record. This file explains the product shape so users,
contributors, and agents understand where Main Branch is going.

## Shipped Foundation

Main Branch already ships:

- public PyPI package and MIT-licensed engine;
- `mb onboard`, `mb init`, `mb status`, `mb start`, `mb update`, `mb doctor`,
  `mb graph`, `mb validate`, `mb migrate`, `mb connect`, and skill management
  commands;
- Claude Code skill wiring with `mb-` prefixed bundled skills;
- beginner setup, migration, repair, and update paths;
- local-first provider metadata and secret-safe connection checks;
- graph and status primitives for future dashboard and agent workflows;
- privacy-safe GitHub issue drafting for user friction;
- `bets/` and `/mb-bet` as the first narration primitive;
- public contribution, support, security, compatibility, and agent guidance.
- accepted workspace/repo/sensitive-data boundary guidance and
  GitHub/Obsidian-compatible markdown/link conventions for future dashboard,
  team daily log, bookkeeping, and multi-repo work.
- initial paid-traffic site readiness checks through `mb site check`.

Claude Code is the supported runtime today. Other runtimes are compatibility
targets until adapter code and smoke evidence exist.

## Next: v0.3.0 - Knows What To Do Next

The next major product step is turning `mb status` and `/mb-start` into a
useful daily decision surface.

Shipped scope:

- `mb status` v1 with "since last check", drift detection, and a stable JSON
  schema ([#261](https://github.com/noontide-co/mainbranch/issues/261));
- privacy-safe issue drafting for bugs, missing workflows, confusing errors,
  and feature ideas ([#264](https://github.com/noontide-co/mainbranch/issues/264));
- `bets/` and `/mb-bet` as the first primitive for tracking and narrating
  operator bets ([#266](https://github.com/noontide-co/mainbranch/issues/266)).

Remaining planned scope:

- a deterministic next-action ranker with top-three recommendations and cited
  signals ([#262](https://github.com/noontide-co/mainbranch/issues/262));
- `/mb-start` using the same status and ranker substrate
  ([#262](https://github.com/noontide-co/mainbranch/issues/262));
- `/mb-status` as a thin runtime wrapper over deterministic status facts;
- shared readiness checks so skills call `mb` instead of duplicating probes
  ([#263](https://github.com/noontide-co/mainbranch/issues/263));
- cleaner beginner/provider onboarding that explains the tool philosophy and
  proves GitHub/provider readiness before noob users get stuck
  ([#273](https://github.com/noontide-co/mainbranch/issues/273)).

Anti-scope for v0.3.0:

- no dashboard as source of truth;
- no broad multi-runtime support claims;
- no marketplace;
- no automatic model invocation from `mb`;
- no provider setup that stores secrets in repo files.

## Soon: v0.3.x - Improves Itself In Public

Once Main Branch knows enough to surface next actions, the product should make
friction easier to turn into public improvement.

Planned scope:

- a small read-only local dashboard spike over existing JSON outputs
  ([#189](https://github.com/noontide-co/mainbranch/issues/189));
- sidecar enrichment contract for optional tools such as public company
  context, analytics, bookkeeping, transcription, or deployment helpers
  ([#265](https://github.com/noontide-co/mainbranch/issues/265)).
- agent checkpoints as hidden Git memory so long Claude Code runs can be saved
  throughout execution and resumed by `/mb-start`
  ([#288](https://github.com/noontide-co/mainbranch/issues/288)).
- follow-up implementation work from the workspace/repo boundary decision and
  markdown/link conventions, including dashboard spikes, team daily log
  surfaces, finance/legal warnings, and broader link repair where issues prove
  the need ([#274](https://github.com/noontide-co/mainbranch/issues/274),
  [#275](https://github.com/noontide-co/mainbranch/issues/275)).

## Later: v0.4 - Launches Offers From Bets

The next proof point after the daily decision loop is graduating real business
bets into offers, pages, ads, fulfillment, and public narration.

Planned scope:

- links between bets, decisions, research, campaigns, and outcomes;
- public bets feed generated through site workflows;
- offer launch workflow: keyword gate, lander, ads, and `/mb-start`
  orchestration ([#89](https://github.com/noontide-co/mainbranch/issues/89));
- decisions on Ops surfaces (books, P&L, compliance) and fulfillment scope;
- bookkeeping/P&L primitives that respect finance-data privacy boundaries
  ([#128](https://github.com/noontide-co/mainbranch/issues/128)).

## Longer Range

Longer-range work should preserve the same state model: canonical truth in git,
local operational state outside git, and live process state only when explicit.

Likely directions:

- runtime adapters for Codex, Cursor, OpenClaw, Hermes, Paperclip-adjacent
  orchestration, and local runtimes;
- dashboard/server mode as an optional local or self-hosted view over repo
  truth, graph output, GitHub, and connected tools;
- structured data layer for metrics, ads, analytics, P&L, and ledgers, with
  explicit access boundaries before sensitive financial/legal data is surfaced;
- richer sidecar ecosystem behind narrow JSON contracts;
- deeper Paid, Organic, Pages, and Ops workflows under the four-pillar framing.

## Reading Order

- [ETHOS.md](ETHOS.md) for the product principles.
- [OPERATOR-LOOPS.md](OPERATOR-LOOPS.md) for the Sense -> Decide -> Ship ->
  Reflect loop.
- [compatibility.md](compatibility.md) for runtime support status.
- [CHANGELOG.md](../CHANGELOG.md) for what actually shipped.
- [GitHub issues](https://github.com/noontide-co/mainbranch/issues) for the
  live task list.
