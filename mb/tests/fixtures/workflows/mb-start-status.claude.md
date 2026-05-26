# Generated Claude Shell: Daily Start And Status

Source workflow: `workflows/mb-start-status/workflow.md`
Runtime support: `claude_code: supported_shell`
Approval gates: `updates_repairs_migrations`, `file_writes`, `checkpoint`, `provider_mutation`, `publishing_or_spend`, `customer_contact`, `private_data`, `destructive_operations`, `status_marker`
Public/private boundaries: `no_secrets`, `no_raw_provider_exports`, `no_customer_member_data`, `no_private_runtime_settings`, `no_raw_finance_legal_records`

Use from `/mb-start` or `/mb-status` when the operator starts the day, returns to a repo, asks what changed, or asks what to do next. Preserve fact-first routing, update/repair gates, one clear next route, and business language first.

This snapshot does not replace shipped `.claude/skills` prose.

## Required mb Commands

- `mb status --json --peek`
- `mb start --json`
- `mb doctor repair --plan`

## Required JSON Fact Paths

- `money_path`
- `money_path.objects.proof.quality`
- `content_strategy`
- `ranked_actions`
- `update`
- `readiness`
- `drift.items`
- `runtime.codex_cli`
- `runtime.claude_code`
- `since_last_check`
- `journal`
- `checkpoint`
- `onboarding`
- `integrations`
- `github`
- `vocabulary`

## Routing

1. Start from status facts before raw markdown: readiness, drift, runtime wiring, update state, ranked actions, and since-last-check context.
2. Run hard gates before routing: required updates, runtime mismatch, repair blockers, readiness blockers, private-data boundaries, unsafe provider operations, and destructive-operation requests.
3. Use `ranked_actions`, `since_last_check`, `journal`, `money_path`, `content_strategy`, `onboarding`, `readiness`, `update`, and `drift.items` as cited facts.
4. Present one clear business route and the signal behind it. Mutate the status marker only when the operator explicitly approves recording the daily check-in.
5. Ask before business-file writes, checkpoints, repairs, updates, migrations, provider mutation, publishing, spend, customer contact, destructive operations, or public issue/proposal submission.

## Handoff Shape

```text
Daily state: <ready, needs attention, blocked, or not a Main Branch repo>.
Facts read: <status/start/repair facts used>.
What changed: <since-last-check or journal summary>.
Main signal: <ranked action, readiness, drift, MoneyPath, content strategy, or onboarding fact>.
Recommended route: <one business route and why>.
Approval needed before writes: <yes/no and what action>.
```

Use business language first. Technical commands, runtime wiring, provider refs,
and file paths are receipts after the owner-facing state unless the operator asks
for plumbing.
