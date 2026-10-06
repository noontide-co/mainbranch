---
description: Show Main Branch commands.
---

# /mb-help

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

- `mb workflow list --runtime codex --json`
- `mb status --json --peek`

Stop before business routing if `runtime.codex_cli.status` is
`runtime_mismatch` or if any drift item is `codex_runtime_mb_mismatch`.

## Route

Show the supported, pending, and unsupported Codex workflow surfaces. Do not claim parity for surfaces the inventory does not mark supported.

Ask before durable writes, checkpoints, updates, repairs, migrations, provider
mutation, publishing, spend, customer contact, destructive operations, or public
issue/proposal submission.
