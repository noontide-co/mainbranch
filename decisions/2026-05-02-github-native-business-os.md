---
title: Main Branch as GitHub-native business operating system
date: 2026-05-02
status: proposed
tags: [product-direction, github, cli, integrations, graph, business-os]
---

# Main Branch as GitHub-Native Business Operating System

## Decision

Main Branch should move from "CLI plus Claude Code skills" toward a
GitHub-native operating system for running a real business with AI.

The core substrate stays the same:

- the business lives in files in a git repo;
- GitHub issues are work items;
- pull requests are conversations and proposals;
- git history is the evolution story;
- agent runtimes execute against that source of truth.

The product shift is that `mb` becomes the control plane that makes this
substrate usable for non-developers while preserving the real primitives for
technical operators.

## Current Reality

The v0.1 architecture made the right foundational calls:

- `mb` is a stateless, scriptable CLI.
- The business repo is the durable state.
- Claude Code skills are the first execution adapter.
- The engine is runtime-agnostic by design.
- Skills and the CLI are packaged together through PyPI.
- GitHub is already the public collaboration and release surface.

But the product experience is still narrow:

- `mb init` is a scaffold, not an adaptive onboarding flow.
- `/start` is a Claude Code skill, not yet a full business briefing.
- `mb graph` is a DOT exporter, not an operator-facing intelligence surface.
- Tool integrations are skill-specific and credential handling is not yet a
  first-class system.
- GitHub activity is still presented as developer activity instead of business
  meaning.
- There is no dashboard/server mode. All state is currently repo state plus
  small local config, and every `mb` invocation starts, acts, and exits.

This is acceptable for v0.1. It should not be the v0.2 shape.

## Product Model

Main Branch should be understood as five layers.

### 1. Narrative Brain

The git repo remains the source of truth:

- `core/` for evergreen reference;
- `research/` for investigations;
- `decisions/` for choices and rationale;
- `campaigns/`, `log/`, `documents/`, and finance files for operating history.

Markdown stays human-readable. Git history stays inspectable. No database
replaces the files.

### 2. GitHub Team Layer

GitHub is the team operating surface:

- issues become tasks, blockers, requests, and follow-ups;
- pull requests become conversations around proposed changes;
- review comments become durable discussion;
- merge history becomes "what shipped";
- mentions, labels, assignees, and milestones become the daily coordination
  feed.

For non-technical users, Main Branch should translate GitHub vocabulary by
default. A PR can be presented as a proposal, review, or shipped change. An
issue can be presented as a task. Technical users should be able to see the raw
GitHub terms.

No Slack is required for the core work loop.

### 3. Graph Layer

The repo should gain an Obsidian-style graph layer over time:

- frontmatter links;
- wikilinks;
- tags for people, companies, offers, channels, competitors, and metrics;
- research-to-decision-to-campaign relationships;
- git history reports for how important files changed over time.

The graph is for both humans and agents. It lets `/start`, `/think`, and future
runtime adapters enrich context quickly without loading the whole repo.

### 4. Structured Data Layer

Main Branch should add a local structured data layer for facts that are bad at
being markdown:

- ads metrics;
- SEO and analytics data;
- social performance;
- P&L and ledger summaries;
- site performance;
- campaign spend;
- goal progress.

SQLite or DuckDB is the right first shape. The database is an index and query
cache, not the source of truth. Rebuildable data can live outside git. Durable
summaries and decisions flow back into markdown.

### 5. Execution Layer

Claude Code skills remain first-class today. Codex, Cursor, OpenClaw, Hermes,
and local runtimes are compatibility targets.

The execution layer should:

- make ads, sites, social posts, plans, and reports;
- review outcomes against rubrics;
- surface hard truths instead of validating weak strategy;
- propose next actions;
- write durable learnings back into the repo.

`mb` should not become a chat client or model host. It should wire runtimes,
check health, sync integrations, expose JSON, and make the repo legible.

## State Model

The earlier "stateless CLI" framing is correct only for the base command
surface. It should not become a religion.

Main Branch needs three kinds of state:

### Canonical State

Canonical state is the business itself and must live in git:

- reference files;
- research;
- decisions;
- plans;
- campaign artifacts;
- durable summaries;
- files changed through PRs.

This state is portable, reviewable, branchable, and mergeable. It is the reason
the system works.

### Local Operational State

Local operational state can live outside git:

- credentials;
- integration connection metadata;
- last sync timestamps;
- local indexes;
- database cache;
- runtime preferences;
- dashboard/server config;
- logs and temporary run records.

This state belongs under a Main Branch home directory such as `~/.mainbranch/`
or a per-instance path. It should be repairable by `mb doctor`, inspectable by
`mb status`, and rebuildable when possible.

### Live Process State

Live process state exists only when the user intentionally starts a running
surface:

- local dashboard;
- background sync;
- local API server;
- watch mode;
- scheduled jobs;
- runtime bridge.

This state is allowed, but it must be explicit. A user should know when they
are running Main Branch as a local service. The default CLI should remain safe,
boring, and scriptable.

## Dashboard Direction

A dashboard is likely necessary if Main Branch becomes the operating surface for
goals, GitHub activity, graph views, metrics, and integrations.

The dashboard should not replace the repo. It should be a local or self-hosted
view over the repo, GitHub, graph index, structured database, and connected
tools.

The likely shape:

- `mb dashboard` or `mb serve` starts a local web UI;
- first run creates a local instance directory;
- the server reads business repos and GitHub activity;
- structured metrics live in the local database/index;
- credentials are read through the credential layer, never from the repo;
- the UI shows business-language views over issues, PRs, goals, spend, graph,
  and recent decisions;
- production/team mode can later point at hosted Postgres or another durable
  backend, but local-first should be the default.

This follows the right lesson from dashboard-first systems like Paperclip: a
dashboard implies a running server and persistent database. Main Branch should
adopt that when the surface earns it, but it should not force a server into the
install path before the repo/CLI/skill loop is solid.

The dashboard's job is observability and control, not canonical memory.

## Onboarding Direction

The biggest immediate product gap is onboarding.

`mb init` should stay as the quiet, scriptable primitive. Add a higher-level
`mb onboard` flow for humans.

Running bare `mb` in an interactive terminal should not feel like a dead help
dump forever. It should become a beautiful launch screen that orients the user:

- "new here?" -> `mb onboard`;
- "already have a repo?" -> connect or open recent repos;
- "daily work?" -> `mb status` / `mb start`;
- "something broken?" -> `mb doctor`;
- "power user?" -> show raw command list.

This launch screen must be TTY-aware. In non-interactive contexts, scripts,
tests, and CI should still get deterministic help/exit behavior. `mb --help`
must always remain the full plain command reference.

The onboarding flow should:

- detect user sophistication with GitHub, terminal, and Claude Code;
- offer beginner, intermediate, and power-user paths;
- create or connect an existing business repo;
- explain why GitHub, git, Cloudflare, and local files are used;
- wire Claude Code skills and verify discovery;
- introduce GitHub language mapping;
- end with the exact daily ritual: open repo, run the runtime, invoke `/start`.

The tone can carry playful trail-style flavor for first-time CLI users, but it
must be skippable and must not slow down technical users.

## Credential and Integration Direction

Environment variables are not durable enough for the target audience.

`mb` should own integration setup:

- `mb connect <provider>` for Google, Meta, Cloudflare, Postiz, Apify, Beancount,
  Whisper/transcription, and future providers;
- OS keychain as primary credential storage;
- encrypted local config as fallback;
- repo-level metadata for connected providers and last sync timestamps;
- `mb doctor` checks for broken or missing integrations;
- skills call `mb` or read standardized integration outputs instead of asking
  users to hand-edit env files.

Credentials never belong in the business repo.

## Daily Briefing Direction

`/start` should become the daily business briefing.

It should eventually summarize:

- recent merged PRs and what they mean for the business;
- open issues that need the operator;
- assigned tasks and blocked work;
- goals by offer;
- ad spend and performance;
- site and SEO signals;
- P&L or ledger summaries;
- recent decisions and stale research;
- recommended actions, scored through rubrics and guardrails.

The briefing should not be a generic digest. It should reframe raw GitHub and
tool data into business meaning.

## Specialized CLIs

`mb` should remain the umbrella control plane.

Specialized CLIs may emerge when a skill becomes a product surface:

- site work may become a Cloudflare-backed CMS/deploy CLI;
- ads work may become an ads analysis and launch CLI;
- books work may become the Beancount/P&L CLI;
- fulfillment work may become the agency delivery CLI.

Do not split early. A new CLI earns its own package only when the domain has
real external users, clear commands, and enough depth that keeping it inside
`mb` makes the umbrella worse.

## What Not To Do

- Do not make `mb` a daemon by default.
- Do not pretend a dashboard can exist without explicit local process state,
  server config, and a database/index.
- Do not make `mb` a chat interface.
- Do not hide GitHub so deeply that power users lose the real primitive.
- Do not put secrets in repo files, `CLAUDE.md`, or frontmatter.
- Do not make a database the canonical brain.
- Do not claim runtime compatibility before adapters are tested.
- Do not add playful onboarding that technical users cannot skip.

## Near-Term Build Order

The detailed v0.2.0 product slice is in
[`docs/prd/v0-2-first-run-daily-briefing.md`](../docs/prd/v0-2-first-run-daily-briefing.md).
The agent workflow, PR review, and runtime eval contract for building that
slice is in
[`docs/prd/v0-2-agent-workflow-and-evals.md`](../docs/prd/v0-2-agent-workflow-and-evals.md).

1. Add `mb onboard` as the human setup flow; leave `mb init` scriptable.
2. Add a TTY-aware bare `mb` launch screen that routes to onboard, status,
   start, doctor, and help without breaking scripts.
3. Add `mb start` as a clean handoff helper that verifies repo wiring and prints
   or launches the configured runtime command.
4. Add `mb status` as the cheap repo health summary for humans and agents.
5. Upgrade `mb graph` toward an interactive graph and entity/tag model.
6. Add `mb connect` foundation with keychain-backed credential storage.
7. Add GitHub briefing primitives: assigned issues, mentions, PRs merged this
   week, blocked work, and business-language reframing.
8. Add structured sync/indexing for one real data source before generalizing.
9. Add an explicit dashboard spike only after `mb status`, graph/indexing, and
   one integration sync have real data to show.

## Success Criteria

The v0.2 product direction is working when a non-technical operator can:

1. install Main Branch;
2. create or connect a business repo;
3. understand why GitHub is the business operating layer;
4. open a daily briefing;
5. see what changed, what matters, and what to do next;
6. run a skill or runtime workflow that acts on that briefing;
7. close the loop with a decision, PR, or updated reference file.

The system should feel continuous, but the continuity should come from the repo,
GitHub activity, graph, database index, and `/start`/`/end` ritual, not from a
fragile long-running CLI process.
