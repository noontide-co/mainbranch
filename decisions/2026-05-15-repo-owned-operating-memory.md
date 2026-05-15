---
type: decision
date: 2026-05-15
status: accepted
topic: Repo-owned operating memory and current product language
linked_decisions:
  - decisions/2026-05-01-mb-cli-vs-agent-workflows-boundary.md
  - decisions/2026-05-04-workspace-repo-sensitive-data-boundaries.md
  - decisions/2026-05-05-operator-loops-taxonomy.md
  - decisions/2026-05-06-main-branch-operating-spine.md
  - decisions/2026-05-07-work-continuity-hidden-technical-memory.md
  - decisions/2026-05-11-repo-setup-visibility-and-checks-model.md
  - decisions/2026-05-13-provider-cli-api-wrapper-boundary.md
supersedes:
  - decisions/2026-05-02-github-native-business-os.md
tags: [product-direction, architecture, language, state-model, providers]
---

# Repo-Owned Operating Memory

## Decision

Main Branch is repo-owned operating memory for AI-assisted businesses.

The current product shape is:

1. The business folder is the durable memory.
2. `mb` is the fact, safety, repair, update, and connected-account readiness
   layer.
3. Agent runtimes and skills are the judgment and workflow layer.
4. Git and GitHub are the hidden technical memory layer.
5. Provider rails, sidecars, Obsidian, and future dashboards are inputs or
   views, not source of truth.

This supersedes the older "GitHub-native business operating system" proposal as
the current direction anchor. The old proposal was directionally useful, but it
was written before the daily loop, push primitive, hidden GitOps layer, provider
connection model, and experimental Codex adapter had settled.

## Current Architecture

The business repo owns durable business truth:

- `core/` for evergreen offer, audience, voice, proof, strategy, operations,
  finance policy, and connected-account boundaries;
- `research/`, `decisions/`, `bets/`, `pushes/`, `log/`, and `documents/` for
  operating memory;
- safe connected-account refs, data-source records, and approved summaries when
  they are useful to future work;
- git history, checkpoints, GitHub issues, and pull requests as inspectable
  history and coordination.

`mb` owns deterministic facts and safe mechanics:

- repo shape, validation, graph, status, start, doctor/repair, migration,
  update, connected-account readiness, skill wiring, and checkpoint planning;
- stable JSON and exit codes for agents, CI, dashboards, and power users;
- privacy and secret boundaries for local state, provider connections, and
  public issue drafting.

Skills and runtimes own judgment:

- routing messy operator requests into business primitives;
- asking the missing question;
- drafting, reviewing, and improving work;
- translating `mb` facts into business-owner language;
- asking before durable writes, publishing, spend, provider mutation, or
  customer contact.

## Provider And Secret Model

Durable safe refs live in git. Secrets do not.

Provider setup has three layers:

- tracked repo files can hold non-secret intent, account labels,
  connected-account refs, public-safe ids, and approved summaries;
- local ignored workspace state can hold hydration markers, repair evidence,
  and caches;
- user-scoped or provider-native secret stores hold tokens, refresh tokens,
  service-account material, and private account access.

`mb connect` may own credential routing, readiness checks, safe metadata, and
workspace hydration. The OS keychain, environment, provider-native auth store,
or GitHub Actions secrets own the secret values.

Disposable workspaces should hydrate from user/local state when the repo identity
matches. A different business repo must not inherit another repo's provider
credentials simply because it shares a machine.

Provider mutation is not a blanket product capability. A rail can mutate
external systems only when that specific workflow has preview behavior,
operator approval, readiness checks, tests, and smoke evidence.

## Language Contract

Normal operators should not have to reason in git or schema terms.

Use business language first:

- task, blocker, follow-up, proposal, saved checkpoint, connected account,
  business map, proof, offer, push, playbook, outcome, and what changed;
- "the system checked..." before raw command names;
- "saved progress" before "commit";
- "proposal" before "pull request";
- "connected account" before "provider readiness";
- "public site from private source" before GitHub/Cloudflare mechanics.

Keep technical language available where it belongs:

- contributor docs;
- command references;
- JSON contracts;
- troubleshooting;
- architecture and decision records.

The rule is not to hide the machinery. The rule is to let the user meet the
business outcome before the machinery.

## Dashboard And Sidecar Stance

Dashboards, Obsidian, scheduled sync, local databases, and sidecars are useful
only when they make repo truth easier to see or safe external facts easier to
use.

They must not become the canonical business memory. A future dashboard may have
state, indexes, and server process state, but that state is explicit local or
self-hosted operational state. It reads from business repos, GitHub, `mb` JSON,
provider-safe summaries, and approved sidecars.

No dashboard is required for the current daily loop.

## Consequences

- README and roadmap should link this decision for the current long-arc model.
- Historical v0.1/v0.2 planning decisions remain useful context, but they are
  not current product truth when they conflict with README, AGENTS, roadmap,
  architecture, compatibility, or this decision.
- Provider and workspace docs should say that `mb` owns routing and readiness,
  while secret stores own secret values.
- Operator-facing copy should keep improving away from unexplained terms such
  as provider refs, sidecars, topology, schema, runtime adapter, and smoke
  evidence unless the user is in a technical or contributor context.

## Review Trigger

Revisit this decision if Main Branch ships any of these:

- a dashboard that writes durable business truth;
- provider mutation without a specific accepted rail;
- a supported non-Claude runtime;
- a hosted service that changes the repo-owned memory model;
- background sync or scheduled jobs that become default rather than explicit.

## Related links

- [The mb CLI vs Portable Agent Workflows](2026-05-01-mb-cli-vs-agent-workflows-boundary.md)
- [Workspace, Repo, and Sensitive Data Boundaries](2026-05-04-workspace-repo-sensitive-data-boundaries.md)
- [Operator Loops Taxonomy](2026-05-05-operator-loops-taxonomy.md)
- [Main Branch Operating Spine](2026-05-06-main-branch-operating-spine.md)
- [Work Continuity and Hidden Technical Memory](2026-05-07-work-continuity-hidden-technical-memory.md)
- [Repo Setup, Visibility, and Checks Model](2026-05-11-repo-setup-visibility-and-checks-model.md)
- [Provider CLI/API and mb Wrapper Boundary](2026-05-13-provider-cli-api-wrapper-boundary.md)
- [Superseded: GitHub-Native Business Operating System](2026-05-02-github-native-business-os.md)
