---
name: google-ads-search-launch
description: "Plan a Google Ads search launch playbook."
argument-hint: "[target]"
user-invocable: true
---

# google-ads-search-launch

Support level: `read_only_planning`.

Use this skill when the operator is in a Main Branch business repo and asks to
start the day, inspect status, set up, update, repair, think through a decision,
close a session, get help, or use one of the inventoried Main Branch workflows.

## Routes

- `mb-doctor`: Repair Main Branch setup. (supported)
- `mb-start`: Start Main Branch. (supported)
- `mb-status`: Show Main Branch status. (supported)
- `mb-setup`: Set up Main Branch. (supported)
- `mb-update`: Update Main Branch. (supported)
- `mb-think`: Think through a Main Branch decision. (supported)
- `mb-end`: End and checkpoint work. (supported)
- `mb-help`: Show Main Branch commands. (supported)
- `mb-bet`: Plan and review Main Branch bets. (read_only_planning)
- `mb-ads`: Plan ads and paid creative from Main Branch facts. (read_only_planning)
- `mb-organic`: Plan organic content from Main Branch facts. (read_only_planning)
- `mb-site`: Plan pages and site readiness from Main Branch facts. (read_only_planning)
- `mb-wiki`: Explain wiki support status for Main Branch. (intentionally_unsupported)
- `mb-skill-concept`: Plan a Main Branch skill concept. (intentionally_unsupported)
- `mb-skill-brief-draft`: Draft a Main Branch skill brief. (intentionally_unsupported)
- `mb-skill-review`: Review a Main Branch skill proposal. (intentionally_unsupported)
- `google-ads-search-launch`: Plan a Google Ads search launch playbook. (read_only_planning)
- `ship-bet`: Plan a ship-bet playbook run. (read_only_planning)
- `weekly-review`: Plan a weekly review. (read_only_planning)

Use this as a read-only planning route in Codex. Ground the answer in the facts below, name what Claude Code can do more fully when relevant, and ask before writing files or touching providers.

Use the route names above as product-facing workflow names. Do not introduce
`main-branch-owner-loop`, plugin, adapter, or command-surface vocabulary in
operator-facing answers.

## Grounding

Start in the current repo. Run the read-only facts that fit the route before
advice:

- `mb status --json --peek`
- `mb connect doctor --json`

Run `command -v mb` and `mb --version` first when setup, update, repair, or
runtime readiness is uncertain. If `mb` is missing or reports an unexpected
version, stop and tell the operator to fix the runtime/login-shell PATH before
continuing.

Use `mb status --json --peek` as the default daily briefing source. It names
readiness, drift, onboarding progress, update state, GitHub activity, provider
signals, recent work, MoneyPath, ranked actions, bets, pushes, and checkpoint
state. Use `mb start --json` when runtime handoff or repo-boundary facts matter.

Stop before business routing if `runtime.codex_cli.status` is `runtime_mismatch`
or if any drift item is `codex_runtime_mb_mismatch`.

## Approval

Read-only fact commands can run without asking. Ask before durable writes,
checkpoints, updates, repairs, migrations, provider mutation, publishing, spend,
customer contact, destructive operations, or public issue/proposal submission.

## Boundaries

Codex supports the daily Main Branch routes listed here. Do not claim all Claude
Code skills, provider mutation, ads/site production, publishing, spend, customer
contact, or slash commands are available unless `mb workflow list --runtime
codex --json` and current runtime evidence say so.
