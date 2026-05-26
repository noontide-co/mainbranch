# Generated Codex Workflow Guidance: Maintenance Update And Repair

Source workflow: `workflows/mb-maintenance-repair/workflow.md`
Runtime support: `codex_cli: owner_loop_shell`
Approval gates: `updates_repairs_migrations`, `file_writes`, `checkpoint`, `provider_mutation`, `publishing_or_spend`, `customer_contact`, `private_data`, `destructive_operations`, `package_update`, `repair_apply`
Public/private boundaries: `no_secrets`, `no_raw_provider_exports`, `no_customer_member_data`, `no_private_runtime_settings`, `no_raw_finance_legal_records`

Codex is first-class for the proven owner loop only. This guidance is generated
from the engine workflow source for business-repo `AGENTS.md`; the business repo
does not need to contain `workflows/mb-maintenance-repair/workflow.md`. Treat this rendered
route as the Codex shell for natural-language daily operating tasks. It does not
claim Claude Code runtime entrypoints work inside Codex or that all Main Branch
workflows are available in Codex.

## Required mb Commands

- `mb --version`
- `mb status --json --peek`
- `mb start --json`
- `mb doctor repair --plan`
- `mb doctor repair --plan --json`
- `mb update --check --json`

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
- `surface_refresh`
- `codex_adapter`
- `repair.sections`
- `repair.actions`
- `repair.actions[].mode`
- `repair.actions[].safe_to_apply`
- `repair.actions[].writes`
- `validation`

## Codex Route

1. Inspect update and repair state before advice: version, status, start, update check, and repair plan facts.
2. Stop on runtime mismatch or missing `mb` before business routing.
3. Explain what is stale, why it matters, affected surface, write set, and safe-to-apply state before exact commands.
4. Package updates are explicit operator actions. Repair applies, migrations, global skill writes, skill links, gitignore changes, and untracking require approval.
5. After an approved update or repair, rerun `mb status --json --peek` before routing back into business work.

## Handoff Shape

```text
Maintenance state: <current, update available, repair needed, blocked, or applied>.
Facts read: <version/status/start/update/repair facts used>.
Affected surface: <install, Claude wiring, Codex guidance, migration,
validation, gitignore, or checkpoint hook>.
Plan: <read-only command, write command, files touched, and safe-to-apply state>.
Owner impact: <why this matters in business language>.
Next safe action: <one command or route>.
Approval needed before writes: <yes/no and what action>.
```

Use business language first. Technical commands, runtime wiring, provider refs,
and file paths are receipts after the owner-facing state unless the operator asks
for plumbing. Do not tell Codex users to run Claude Code entrypoints. Runtime
smoke is required before docs say this selected workflow is supported in Codex.
