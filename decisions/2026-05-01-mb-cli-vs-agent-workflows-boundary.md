---
type: decision
date: 2026-05-01
status: accepted
topic: The mb CLI vs portable agent workflows product boundary
linked_decisions:
  - decisions/2026-04-29-mb-vip-v0-1-0-master.md
participants: [Devon, Codex]
tags: [v0-2, cli, workflows, runtimes, product-boundary, decision]
---

# The mb CLI vs Portable Agent Workflows

## Decision

`mb` is the deterministic, inspectable, scriptable substrate for a
business-as-files repo. It owns repo shape, validation, migration, status,
updates, graphing, and runtime wiring.

Agent workflows are the judgment-heavy layer. They read from and write to the
same business repo, but they run inside whatever agent runtime hosts them.
Claude Code is the first fully supported adapter in v0.1.x. Codex, Cursor,
OpenClaw, Hermes, and local LLM runtimes are v0.2+ compatibility targets.

The boundary is hard:

- `mb` does not invoke a model.
- `mb` does not hold a conversation.
- `mb` does not become a chat client, daemon, scheduler, artifact generator, or
  vector store.
- Agent workflows do not own structural invariants like schema, migration, or
  repo health.

Main Branch is runtime-agnostic by design. `mb` writes and verifies files;
whichever runtime hosts the workflow reads those files.

## Why This Matters

v0.1.1 made the public install path real: `pipx install mainbranch`, `mb init`,
Claude Code wiring, and `mb doctor` all work. That makes the next product
question urgent: is `mb` just a helper for Claude Code, or is it the durable
surface of Main Branch?

This decision makes the answer explicit. `mb` is the stable operating surface.
Claude Code is the first client. Future runtimes should be able to consume the
same repo shape and workflow definitions without forking the product.

## What `mb` Owns

- **`mb init`** - scaffold a business repo, write templates, initialize git, and
  wire configured runtimes.
- **`mb doctor`** - diagnose repo shape, install mode, runtime discovery, auth,
  and common local environment problems.
- **`mb validate`** - enforce deterministic frontmatter and schema rules across
  business files.
- **`mb graph`** - emit a parseable graph from research, decisions, supersession,
  and cross-links.
- **`mb update`** - perform install-mode-aware engine refreshes: pipx upgrade,
  git pull, package-data refresh, and runtime-link repair.
- **`mb skill list/path/link`** - inspect and wire the currently packaged
  Claude Code skill adapter.
- **`mb migrate`** - run dry-run-able, diff-visible schema and path migrations.
- **`mb status`** - provide a cheap health summary for operators, agents,
  dashboards, and CI.
- **Runtime adapter wiring** - eventually support configured adapters such as
  `claude`, `codex`, `cursor`, `openclaw`, `hermes`, and local runtime endpoints.

Every `mb` verb should be one-shot, exit-coded, and eventually `--json`
parseable. The CLI's value is its contract, not its intelligence.

## What Agent Workflows Own

- Research, decide, codify loops.
- Content generation: ads, VSLs, organic posts, sites, decks, wiki work.
- Session bookends and intent routing: start, end, help, pull narration.
- Any task whose output depends on judgment, voice, synthesis, or conversation.

In v0.1.x these workflows are packaged as Claude Code skills. That packaging is
an adapter, not the permanent architecture.

## Runtime Posture

### Claude Code

First-class in v0.1.x. `mb init` writes `.claude/settings.local.json` and bridge
links. `mb doctor` validates Claude Code discovery. The bundled workflow package
ships as Claude Code skills.

### Codex, Cursor, Hermes

First-tier v0.2+ compatibility targets. They should consume the same business
repo and workflow definitions through their own adapter layer.

### OpenClaw

OpenClaw remains a first-tier public compatibility target because adoption in
the wider market matters. Devon's internal Noontide preference may be Hermes +
Paperclip, but that preference does not decide the public engine's runtime
surface. Main Branch should meet users where they already operate.

### Paperclip

Paperclip is better understood as an orchestration or supervision layer than as
the workflow runtime itself. Main Branch should expose stable repo and JSON
contracts that Paperclip can supervise later, without making `mb` a Paperclip
subsystem.

### Local LLMs

Local models are a long-term endpoint. The same boundary holds: `mb` keeps the
repo legible and portable; the local runtime hosts the model interaction.

## What This Means For v0.2

The clean v0.2 CLI issues are:

1. `mb status` - repo health summary.
2. `mb update` - install-mode-aware engine refresh.
3. `mb migrate` - schema and path migration helpers.
4. `mb skill validate <name>` - validate the current Claude Code skill package.

The risky issue is `mb workflow run <name>`. It should not ship as "shell out to
Claude" with runtime support bolted on later. The right v0.2 work is to design
the runtime adapter contract first. If `workflow run` cannot stay
non-conversational and runtime-agnostic across Claude Code plus at least one
other runtime, close the issue and document per-runtime launch commands instead.

## Non-Features

`mb` deliberately does not:

- call Anthropic, OpenAI, local LLMs, or any model provider;
- own conversation state;
- stream a chat UI;
- run a background daemon;
- schedule jobs;
- generate ads, sites, decks, or copy;
- store embeddings or run a vector database.

Those are valid products. They are not the `mb` product.

## Review Trigger

Revisit this decision if more than 30 percent of v0.2 milestone work proposes
verbs that invoke models, manage conversation state, or require persistent
service behavior. That is product-boundary drift, not normal implementation
detail.
