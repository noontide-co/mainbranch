---
description: Summarize current business state and what changed.
---

# /mb-status

Use the Main Branch owner-loop skill and the business repo `AGENTS.md` guidance.
This command is a thin Codex shim, not a separate workflow source.

## Route

Start/status/setup/update/doctor

## Required Facts

First run `command -v mb` and `mb --version`. This command shim was generated
by Main Branch `0.3.33`. If runtime `mb` is older or different, stop
before running status/repair commands and surface the PATH repair.

After `mb status --json --peek` or `mb start --json`, stop if `runtime.codex_cli.status` is `runtime_mismatch` or any `drift.items[].id` equals `codex_runtime_mb_mismatch`. Treat that as a runtime `mb` mismatch: tell the operator to fix the runtime/login-shell PATH and rerun read-only checks before owner-loop advice, repair planning, or writes.

Run the direct `mb` facts that fit this request:

- `mb status --json --peek`
- `mb start --json`

Do not shell-wrap `mb` JSON through `jq`, temp files, redirects, or Python parsers.

## Task

Summarize ranked actions, since-last-check changes, readiness, drift, MoneyPath, content strategy, integrations, bets, pushes, vocabulary, and checkpoint state from the JSON facts.

## Boundaries

Ask before durable writes, checkpoints, updates, repairs, migrations, provider
mutation, publishing, spend, customer contact, destructive operations,
raw private-source reads, or public issue/proposal submission.

Do not claim Claude Code skill parity, all-skill parity, ads/site production,
provider mutation support, publishing support, spend support, or customer-contact
support in Codex.
