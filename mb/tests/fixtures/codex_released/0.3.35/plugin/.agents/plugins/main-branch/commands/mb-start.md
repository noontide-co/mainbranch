---
description: Start Main Branch.
---

# /mb-start

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
- `mb start --json`

Stop before business routing if `runtime.codex_cli.status` is
`runtime_mismatch` or if any drift item is `codex_runtime_mb_mismatch`.

## Route

Summarize the business state, readiness, ranked actions, and one clear next route. Use `mb start --json` when runtime handoff or Codex readiness matters.

Ask before durable writes, checkpoints, updates, repairs, migrations, provider
mutation, publishing, spend, customer contact, destructive operations, or public
issue/proposal submission.
