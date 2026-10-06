---
description: Show Main Branch status.
---

# /mb-status

Use Main Branch from the current repo. This command is a thin Codex route over
deterministic `mb` facts and the repo `AGENTS.md` guidance. Do not duplicate
workflow logic here.

## Preflight

Run first:

- `command -v mb`
- `mb --version`

If `mb` is missing or reports an unexpected version, stop and tell the operator
to fix the runtime/login-shell PATH before continuing.

## Facts

Run the read-only facts that fit this command:

- `mb status --json --peek`

Stop before business routing if `runtime.codex_cli.status` is
`runtime_mismatch` or if any drift item is `codex_runtime_mb_mismatch`.

## Route

Answer from status facts: readiness, drift, recent work, since-last-check, MoneyPath, content strategy, provider signals, and ranked actions.

Ask before durable writes, checkpoints, updates, repairs, migrations, provider
mutation, publishing, spend, customer contact, destructive operations, or public
issue/proposal submission.
