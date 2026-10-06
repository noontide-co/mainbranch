---
description: Answer Main Branch support questions from runtime inventory.
---

# /mb-help

Use the Main Branch owner-loop skill and the business repo `AGENTS.md` guidance.
This command is a thin Codex shim, not a separate workflow source.

## Route

Workflow discovery

## Required Facts

First run `command -v mb` and `mb --version`. This command shim was generated
by Main Branch `0.3.30`. If runtime `mb` is older or different, stop
before running status/repair commands and surface the PATH repair.

Run the direct `mb` facts that fit this request:

- `mb status --json --peek`
- `mb start --json`
- `mb workflow list --runtime codex --json`

Do not shell-wrap `mb` JSON through `jq`, temp files, redirects, or Python parsers.

## Task

Answer from the generated owner-loop skill, workflow inventory, and mb facts. Name unsupported provider/publishing/spend/customer-contact boundaries plainly.

## Boundaries

Ask before durable writes, checkpoints, updates, repairs, migrations, provider
mutation, publishing, spend, customer contact, destructive operations,
raw private-source reads, or public issue/proposal submission.

Do not claim Claude Code skill parity, all-skill parity, ads/site production,
provider mutation support, publishing support, spend support, or customer-contact
support in Codex.
