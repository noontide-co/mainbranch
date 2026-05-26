---
name: mb-maintenance-repair
title: Maintenance Update And Repair
description: Inspect update, doctor, runtime wiring, and repair plans from deterministic facts, then apply only after explicit operator approval.
loops: [sense, decide, ship]
runtime_support:
  claude_code: supported_shell
  codex_cli: owner_loop_shell
  future: planned
runtime_surfaces:
  claude_code: .claude/skills/mb-update/SKILL.md and /mb-start repair routing
  codex_cli: global main-branch mb-update and mb-doctor skills
required_mb_commands:
  - mb --version
  - mb status --json --peek
  - mb start --json
  - mb doctor repair --plan
  - mb doctor repair --plan --json
  - mb update --check --json
json_facts:
  - money_path
  - money_path.objects.proof.quality
  - content_strategy
  - ranked_actions
  - update
  - readiness
  - drift.items
  - runtime.codex_cli
  - runtime.claude_code
  - surface_refresh
  - codex_adapter
  - repair.sections
  - repair.actions
  - repair.actions[].mode
  - repair.actions[].safe_to_apply
  - repair.actions[].writes
  - validation
approval_gates:
  - updates_repairs_migrations
  - file_writes
  - checkpoint
  - provider_mutation
  - publishing_or_spend
  - customer_contact
  - private_data
  - destructive_operations
  - package_update
  - repair_apply
public_private_boundaries:
  - no_secrets
  - no_raw_provider_exports
  - no_customer_member_data
  - no_private_runtime_settings
  - no_raw_finance_legal_records
writes_business_files: false
provider_mutation: false
publishing_or_spend: false
---

# Maintenance Update And Repair

This workflow source is the portable contract for Main Branch maintenance:
inspect update and repair facts, explain the plan in business language, then
apply only after explicit operator approval.

## Intent And Triggers

Use this workflow when the operator asks to update Main Branch, fix setup,
repair Claude Code or Codex wiring, inspect doctor output, resolve stale repo
guidance, handle migration drift, or understand why start/status is blocked.

Do not use this workflow for first-run business setup, broad strategy,
provider account mutation, publishing, spend, customer contact, or automatic
repair applies.

## Required Mb Commands

Run or preserve these deterministic facts before recommending maintenance work:

- `mb --version`
- `mb status --json --peek`
- `mb start --json`
- `mb doctor repair --plan`
- `mb doctor repair --plan --json`
- `mb update --check --json`

`mb update --check --json` supplies update availability and planned surface
refresh. `mb doctor repair --plan --json` supplies sections, actions, write
sets, and safety flags. These commands provide facts and plans; they do not
authorize writes.

## Required JSON Fact Paths

The runtime shell must preserve these paths from the workflow source:

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

Treat these as facts, not permission. The runtime may explain what is stale,
blocked, repairable, skipped, or safe-to-apply, but it must not claim an update,
repair, migration, or validation fix happened unless facts prove it.

## Routing Rules

Hard gates win before maintenance advice: missing `mb`, runtime mismatch,
package update requirement, broken repo wiring, private-data boundaries,
destructive-operation requests, provider mutation, publishing, spend, and
customer contact.

Explain repair/update state in business language first: what is stale, why it
matters, what will be touched, and what the operator must approve. Quote exact
commands second. Package updates are explicit operator actions outside doctor
repair. `mb doctor repair --apply --only claude`, `--only codex`, or reviewed
all-agent repair should match the affected surface. Migration applies require
review of the migration preview and explicit approval.

After an approved update or repair, rerun `mb status --json --peek` before
routing back into business work.

## Read Boundaries

Read deterministic `mb` facts, update checks, repair plans, validation
summaries, and runtime wiring facts. Read generated guidance only when the plan
or validation says it is stale or missing.

Do not inspect secrets, raw provider exports, raw finance/legal records,
customer/member records, local runtime settings beyond generated readiness
facts, private maintainer notes, or credentials.

## Write Boundaries

The workflow may apply writes only after the operator approves the specific
command and scope. Possible write targets include generated repo guidance,
Claude Code project skill links, global Codex skills, `.gitignore`, `.mb/`
operational state, checkpoint hook files, migration outputs, and package
install state.

The workflow source does not authorize provider writes, publishing, spending,
customer contact, raw secret storage, unsupported runtime adapters, or
unreviewed destructive cleanup.

## Approval Gates

Ask before:

- running package updates or package-changing commands;
- applying doctor repair, skill repair, skill link, Codex global skill writes,
  migrations, or setup cleanup;
- creating, editing, moving, deleting, archiving, or untracking files;
- saving a checkpoint after maintenance;
- mutating provider state, publishing, spending money, or contacting customers;
- reading or moving private, restricted, local-only, finance, legal, customer,
  member, credential, or raw provider data.

Never ask the operator to paste secrets into repo files or workflow sources.

## Handoff Format

When handing off a maintenance plan, include a compact repair receipt:

```text
Maintenance state: <current, update available, repair needed, blocked, or applied>.
Facts read: <version/status/start/update/repair facts used>.
Affected surface: <install, Claude wiring, Codex guidance, migration, validation, gitignore, or checkpoint hook>.
Plan: <read-only command, write command, files touched, and safe-to-apply state>.
Owner impact: <why this matters in business language>.
Next safe action: <one command or route>.
Approval needed before writes: <yes/no and what action>.
```

Use business language first. Exact commands and file paths are receipts after
the owner impact unless the operator asks for plumbing.

## Validation Commands

Before changing this workflow or its runtime shells, run:

```bash
cd mb
python -m pytest tests/test_workflows.py tests/test_update.py tests/test_doctor.py -q
```

For repo-level validation, run:

```bash
scripts/check.sh
```

If package update behavior, generated repo guidance, global Codex skills, or
runtime discovery changes, add package/install and runtime/manual smoke
evidence.

## Runtime-Specific Notes

Claude Code may use slash-command-native language for `/mb-update` and repair
routing from `/mb-start`. Preserve exact repair commands, restart guidance, and
the rule that failed updates stop the session until repaired.

Codex uses generated global `mb-update` and `mb-doctor` skills. It should run
read-only facts first, quote exact commands from the plan, ask before any
write/apply command, stop on runtime mismatch, and avoid claiming Claude Code
entrypoints or broader runtime parity.
