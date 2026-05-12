# Docs

This folder holds Main Branch's durable references, contracts, PRDs, evidence,
and examples. It is meant to be skimmable for both business operators and
coding agents.

Public product truth lives here. Per-event narratives live in `decisions/`,
and the changelog lives in `../CHANGELOG.md`.

## Reading routes

Pick the route that matches what you are doing.

### New here (cold start)

- [`ethos.md`](ethos.md) — product principles, source-of-truth model, and runtime stance.
- [`operator-loops.md`](operator-loops.md) — Sense / Decide / Ship / Reflect workflow taxonomy.
- [`roadmap.md`](roadmap.md) — current public direction.
- [`beginner-setup.md`](beginner-setup.md) — human setup walkthrough.

### Setting up a business repo

- [`beginner-setup.md`](beginner-setup.md) — install, first run, first decision.
- [`migrating.md`](migrating.md) — moving an older Main Branch layout forward.
- [`compatibility.md`](compatibility.md) — supported OS, runtime, and adapter matrix.
- [`repo-visibility-rubric.md`](repo-visibility-rubric.md) — public vs private repo guidance.

### Operating the daily loop

- [`operator-loops.md`](operator-loops.md) — how operator work moves through Sense, Decide, Ship, Reflect.
- [`playbooks.md`](playbooks.md) — reusable operating recipes and run records.
- [`books.md`](books.md) — bookkeeping safety, hledger, and the private ledger vault model.
- [`onboarding-progress.md`](onboarding-progress.md) — lifecycle skill resume surface.
- [`business-connections.md`](business-connections.md) — when to use frontmatter links, inline links, tags, data refs, or context.
- [`markdown-link-conventions.md`](markdown-link-conventions.md) — markdown and link rules.
- [`issue-drafting.md`](issue-drafting.md) — privacy-safe `mb issue` flow.

### Schemas and contracts

- [`system-architecture.md`](system-architecture.md) — repo shapes, business primitives, boundaries, and schemas.
- [`json-output-contract.md`](json-output-contract.md) — `mb --json` envelope.
- [`data-source-registry.md`](data-source-registry.md) — `type: data_source` records.
- [`child-repo-descriptors.md`](child-repo-descriptors.md) — `.mainbranch/repo.json`.
- [`checks-and-review-model.md`](checks-and-review-model.md) — local + CI + agent checks.
- [`claude-code-invocation-contract.md`](claude-code-invocation-contract.md) — supported Claude Code path.
- [`release-simulations.md`](release-simulations.md) — release simulation manifest contract.

### Contributing to the engine

- [`agent-cold-start.md`](agent-cold-start.md) — public read order and progressive discovery contract for agents.
- [`oss-operating-checklist.md`](oss-operating-checklist.md) — public release / contributor checklist.
- [`dependency-choices.md`](dependency-choices.md) — adopted rails and dependency policy.
- [`supply-chain-policy.md`](supply-chain-policy.md) — PyPI publishing, GitHub Actions, dependency, and post-compromise rules.
- [`claude-code-runtime-dogfood.md`](claude-code-runtime-dogfood.md) — manual runtime smoke runbook.
- [`release-agent-contract.md`](release-agent-contract.md) — protocol for agents running release-bearing validation.
- [`post-release-alignment.md`](post-release-alignment.md) — post-release sweep, parallel work lanes, AI review ritual.
- [`agent-writing-style.md`](agent-writing-style.md) — writing rubric for agent-facing docs and reviews.
- [`google-ads-gtm-conversion-rubric.md`](google-ads-gtm-conversion-rubric.md) — paid-traffic conversion rubric.
- [`philosophy.md`](philosophy.md) — long-form product writing.

### Planned product shape

- [`prd/`](prd/) — versioned PRDs (`v0-*.md`).

### Evidence

- [`reports/`](reports/) — dated dogfood, smoke, and review reports (`YYYY-MM-DD-*.md`).

### Examples and samples

- [`examples/`](examples/) — example fixtures and samples.

## Naming convention

Under `docs/`:

- Markdown filenames are **lowercase kebab-case** by default.
- Filenames should name the document's job clearly enough that a fresh agent
  can classify it from the path. If a short product noun is ambiguous, make the
  title explicit, for example `Bookkeeping (mb books)`.
- The only all-caps exception under `docs/` is `docs/README.md`.
- Files under `docs/reports/` may begin with `YYYY-MM-DD-` (dated evidence).
- Files under `docs/prd/` use versioned lowercase names like
  `v0-3-agent-checkpoints.md`.
- Files under `docs/examples/` follow the default lowercase kebab-case rule.

Root-level conventional files keep their conventional uppercase form
(`README.md`, `CHANGELOG.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`,
`SUPPORT.md`, `AGENTS.md`, `CLAUDE.md`, `CODE_OF_CONDUCT.md`).

A lightweight check in `scripts/check.sh` fails when a new non-conventional
all-caps Markdown file appears under `docs/`.

## Categories at a glance

| Kind | Location | Example |
|---|---|---|
| Durable reference | `docs/*.md` | `docs/ethos.md` |
| Index | `docs/README.md` | this file |
| Planned product shape | `docs/prd/` | `docs/prd/v0-3-agent-checkpoints.md` |
| Evidence and dogfood | `docs/reports/` | `docs/reports/2026-05-08-v0-3-11-release-transcript-review.md` |
| Examples and samples | `docs/examples/` | `docs/examples/grok-8-researched-brief.md` |
| Per-event narrative | `../decisions/` (outside `docs/`) | `decisions/2026-05-11-repo-setup-visibility-and-checks-model.md` |
| Public release log | `../CHANGELOG.md` | n/a |
