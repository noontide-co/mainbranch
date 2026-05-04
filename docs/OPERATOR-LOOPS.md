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

- beginner-safe GitHub/provider onboarding with persistent readiness checks;
- domain and public-context enrichment through optional sidecars;
- clearer rules for when one business should become multiple repos or
  workspaces.

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

- richer drift detection for stale context, stale links, and broken wiring;
- provider-readiness signals for GitHub, Cloudflare, Google, Meta, Apify, and
  other optional tools;
- an Obsidian-compatible link/readability pass for markdown repos;
- a local dashboard that visualizes existing repo/GitHub/provider truth without
  becoming the source of truth.

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
- noob-safe prompts to open GitHub issues when the user hits friction;
- decision trees for provider choices, paid-SaaS exceptions, sensitive data, and
  workspace/repo boundaries.

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
- noob-safe connector flows for GitHub, Cloudflare, Google, Meta, and Apify;
- richer site, ads, organic, bookkeeping, and fulfillment loops.

## 5. Narrate

**Question:** What did we learn, and what should others see?

This loop turns shipped work and business outcomes into durable internal memory
and optional public narration.

Current surfaces:

- `CHANGELOG.md`
- decisions and retros;
- `/mb-end`;
- `bets/` and `/mb-bet`;
- GitHub releases;
- public site workflows through `/mb-site`

Next improvements:

- bet-to-offer graduation rules;
- status and dashboard visibility for active bets, deadlines, and outcomes;
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
