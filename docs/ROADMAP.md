# Roadmap

This roadmap is direction, not a promise. GitHub issues and release notes are
the detailed execution record. This file explains the product shape so users,
contributors, and agents understand where Main Branch is going.

Main Branch is not only a marketing-growth context folder. Growth is the first
high-value wedge because ads, pages, content, and launches expose the memory
problem quickly. The broader product is durable operating memory for
AI-assisted businesses: meetings, fulfillment, bookkeeping summaries, provider
refs, decisions, bets, pushes, logs, and lessons in repos the team owns.

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
- `bets/` and `/mb-bet` as the first Reflect primitive;
- `mb checkpoint` as the first hidden GitOps save layer for long agent runs;
- public contribution, support, security, compatibility, and agent guidance;
- accepted workspace/repo/sensitive-data boundary guidance and
  GitHub/Obsidian-compatible markdown/link conventions for future dashboard,
  team daily log, bookkeeping, and multi-repo work;
- initial paid-traffic site readiness checks through `mb site check`.

Claude Code is the supported runtime today. Other runtimes are compatibility
targets until adapter code and smoke evidence exist.

## Current: v0.3.x - Tighten The Daily Operating Loop

The current product step is tightening `mb status`, `/mb-start`, `/mb-status`,
doctor repair, checkpoints, pushes, provider readiness, and issue drafting into
a reliable daily decision surface.

Shipped scope:

- `mb status` v1 with "since last check", drift detection, and a stable JSON
  schema ([#261](https://github.com/noontide-co/mainbranch/issues/261));
- deterministic next-action ranking with cited status signals;
- `/mb-start` and `/mb-status` reading the same status substrate instead of
  duplicating repo probes;
- shared readiness and repair surfaces through `mb doctor`, `mb doctor repair`,
  `mb update`, `mb start`, and provider readiness JSON;
- privacy-safe issue drafting for bugs, missing workflows, confusing errors,
  and feature ideas ([#264](https://github.com/noontide-co/mainbranch/issues/264));
- `bets/` and `/mb-bet` as the first primitive for tracking and reflecting on
  operator bets ([#266](https://github.com/noontide-co/mainbranch/issues/266));
- `pushes/` as the canonical coordinated-work folder, with `campaigns/`
  retained as compatibility read;
- git checkpoints as business-readable save points during long agent runs.

Active follow-up scope:

- make checkpoint verbs business-readable and consistent
  ([#301](https://github.com/noontide-co/mainbranch/issues/301));
- install business commit validation into repo workflows
  ([#302](https://github.com/noontide-co/mainbranch/issues/302));
- use the business git journal in status and timelines
  ([#303](https://github.com/noontide-co/mainbranch/issues/303));
- define a stable JSON result envelope across `mb` commands
  ([#297](https://github.com/noontide-co/mainbranch/issues/297));
- harden old-layout migration and legacy reference-path repair
  ([#284](https://github.com/noontide-co/mainbranch/issues/284));
- move provider automation behind explicit approval gates
  ([#286](https://github.com/noontide-co/mainbranch/issues/286)).

Anti-scope for v0.3.x:

- no dashboard as source of truth;
- no broad multi-runtime support claims;
- no marketplace;
- no automatic model invocation from `mb`;
- no provider setup that stores secrets in repo files.

## Soon: Dashboard, Sidecars, And Multi-Repo Views

Once the daily operating loop is boring, Main Branch should make the broader
business system easier to see without replacing the repo as source of truth.

Planned scope:

- a small read-only local dashboard over existing JSON outputs;
- visual multi-repo inventory for business repos, site repos, offer repos, and
  sensitive/private repos, with explicit access boundaries;
- a dashboard map of repos, pushes, bets, commits, issues, PRs, checkpoints,
  provider-safe summaries, and sidecar summaries;
- sidecar enrichment contracts for optional tools such as public company
  context, analytics, bookkeeping, transcription, deployment helpers, and
  provider metrics;
- team daily log surfaces built from commits, checkpoints, issues, PRs, and
  explicit `log/` files instead of treating raw chat as source of truth;
- follow-up implementation work from the workspace/repo boundary decision and
  markdown/link conventions, including dashboard spikes, team daily log
  surfaces, finance/legal warnings, and broader link repair where issues prove
  the need ([#274](https://github.com/noontide-co/mainbranch/issues/274),
  [#275](https://github.com/noontide-co/mainbranch/issues/275)).

Anti-scope:

- no dashboard database as canonical business memory;
- no Slack replacement claim before repo truth, GitHub activity, team logs, and
  permission boundaries are proven;
- no finance/legal raw data in shared repos by default;
- no "connect every SaaS" hub. Provider rails are curated, official where
  possible, deterministic, smoke-tested, and optional.

## Later: v0.4 - Bets And Pushes Become Operating Systems

The next proof point after the daily decision loop is graduating real business
bets into offers, pages, ads, fulfillment, and public Ship surfaces.

Planned scope:

- links between bets, decisions, research, pushes, and outcomes;
- public bets feed generated through site workflows;
- offer launch workflow: keyword gate, lander, ads, and `/mb-start`
  orchestration ([#89](https://github.com/noontide-co/mainbranch/issues/89));
- deterministic site/CMS rails over Cloudflare Pages, DNS, GitHub, and
  operator-approved measurement checks;
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
- deeper Paid, Organic, Pages, and Ops workflows under the four-pillar framing;
- optional chat or team-communication surfaces that convert important
  conversation into durable artifacts: issues, proposals, decisions, pushes,
  logs, and commits.

## Reading Order

- [ETHOS.md](ETHOS.md) for the product principles.
- [OPERATOR-LOOPS.md](OPERATOR-LOOPS.md) for the Sense -> Decide -> Ship ->
  Reflect loop.
- [DEPENDENCY-CHOICES.md](DEPENDENCY-CHOICES.md) for dependency, integration,
  sidecar, CLI, MCP server, and provider-adapter judgment.
- [compatibility.md](compatibility.md) for runtime support status.
- [CHANGELOG.md](../CHANGELOG.md) for what actually shipped.
- [GitHub issues](https://github.com/noontide-co/mainbranch/issues) for the
  live task list.
