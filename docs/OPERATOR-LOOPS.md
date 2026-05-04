# Operator Loops

Main Branch work should be understood through the operator's loop, not only the
implementation surface. A command, skill, issue, or release should make at
least one of these loops better.

## 1. Know

**Question:** What does this business know about itself?

This loop captures the durable context an agent needs before doing serious
work:

- offers, audience, voice, proof, constraints, and pricing;
- research, competitors, insights, and raw notes;
- decisions and why they were made;
- campaigns, logs, documents, and operating history.

Current surfaces:

- `mb onboard`
- `mb init`
- `/mb-start`
- `/mb-think`
- `core/`, `research/`, `decisions/`, `campaigns/`, `log/`, `documents/`

Next improvements:

- resumable onboarding that can span multiple sessions;
- domain and public-context enrichment through optional sidecars;
- better detection of missing or stale reference files.

## 2. See

**Question:** What changed, what is stale, and what is healthy?

This loop turns the repo, local environment, GitHub activity, connected tools,
and graph into a concise briefing.

Current surfaces:

- `mb status`
- `mb doctor`
- `mb graph`
- `mb connect status`
- GitHub issues, pull requests, and release history

Next improvements:

- `mb status` v1 with "since last check";
- drift detection for stale context and broken wiring;
- stable `--json` schemas for agents and dashboards;
- a thin local dashboard once the JSON substrate is useful.

## 3. Decide

**Question:** What should I do next, and why?

This loop ranks possible work without pretending the system owns the business.
Main Branch should cite evidence and let the operator override it.

Current surfaces:

- `/mb-start`
- `/mb-think`
- GitHub issues and priorities
- `mb status`

Next improvements:

- a deterministic next-action ranker;
- top-three recommendations in `mb status` and `/mb-start`;
- explicit pin, skip, and defer controls;
- privacy-safe prompts to open GitHub issues when the user hits friction.

## 4. Execute

**Question:** What work are we shipping?

This loop is where domain workflows live. The domains are not the whole
product, but they are where the product proves itself.

Current surfaces:

- `/mb-ads`
- `/mb-vsl`
- `/mb-organic`
- `/mb-site`
- `/mb-wiki`
- `/mb-end`
- `mb connect`

Execution domains:

- pages and CMS;
- paid ads and compliance;
- organic content;
- research and positioning;
- fulfillment and delivery;
- bookkeeping and P&L;
- integrations and sidecar CLIs.

Next improvements:

- skills leaning more heavily on CLI facts instead of duplicate checks;
- optional provider and sidecar contracts;
- richer site, ads, organic, bookkeeping, and fulfillment loops.

## 5. Narrate

**Question:** What did we learn, and what should others see?

This loop turns shipped work and business outcomes into durable internal memory
and optional public narration.

Current surfaces:

- `CHANGELOG.md`
- decisions and retros;
- `/mb-end`;
- GitHub releases;
- public site workflows through `/mb-site`

Next improvements:

- a `bets/` primitive for public operating bets;
- `/mb-bet` with `new`, `update`, `close`, `list`, and `narrate` modes;
- status integration for active bets and deadlines;
- public bets pages generated from repo truth.

## Applying The Loops

When opening or working an issue, name the loop it improves:

- **Know** for onboarding, reference, research, decisions, and context capture.
- **See** for status, doctor, graph, update, migrations, and integrations.
- **Decide** for ranking, triage, recommendations, issue drafting, and
  operator overrides.
- **Execute** for domain workflows and sidecar tools.
- **Narrate** for bets, retros, release notes, public pages, and community
  updates.

A large branch is acceptable when it improves one coherent loop with one
observable success metric. A tiny branch is not automatically better if it
costs more cold start, review, CI, and release overhead than it returns.
