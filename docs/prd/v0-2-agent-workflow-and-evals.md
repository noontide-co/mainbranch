---
title: "PRD: v0.2 Agent Workflow + Runtime Evals"
status: draft
date: 2026-05-02
release: v0.2.0
linked_decision: decisions/2026-05-02-github-native-business-os.md
linked_prd: docs/prd/v0-2-first-run-daily-briefing.md
---

# PRD: v0.2 Agent Workflow + Runtime Evals

## Summary

Main Branch is being built by agents inside branch-per-issue workspaces. The
development process should match the product thesis:

- repo files are durable context;
- issues define work;
- PRs carry proposals and evidence;
- checks prove the deterministic layer;
- runtime evals prove the human/agent loop.

This PRD defines the cold-start template, PR review template, and evaluation
ladder for v0.2 work. It is written for Devon's Conductor setup, but the
contract is runtime-agnostic. Any agent runtime should be able to follow it.

## Problem

The v0.2 product direction is larger than a normal CLI feature set. It touches
first-run UX, GitHub briefing, skill wiring, runtime handoff, graph primitives,
and eventually dashboard state.

If every agent starts from chat context, the system drifts:

- one agent optimizes for CLI mechanics while another optimizes for business
  positioning;
- stale issue labels survive after priorities change;
- PRs pass unit tests but fail the actual Claude Code first-run loop;
- decisions stay in conversation instead of becoming durable repo context;
- future agents relearn the same product boundary.

The fix is a durable operating loop: cold start from repo truth, work one issue
per branch, validate with both code checks and runtime smoke tests, then update
issues and PRs with evidence.

## Goals

- Give every Conductor-spawned agent the same starting shape.
- Preserve one issue per branch and one PR per concern.
- Make PR review check product direction, not only syntax.
- Add runtime evals that exercise Claude Code and skills, not only `mb`.
- Keep evals staged so agents can move quickly without pretending every change
  needs a full manual smoke.
- Capture learnings back into docs, issues, tests, or decisions.
- Support future runtimes without rewriting the workflow.

## Non-Goals

- No hosted CI for interactive Claude Code in v0.2.0.
- No fake automation that claims to test an authenticated runtime without
  actually launching it.
- No giant mandatory context dump for every agent.
- No issue epics. Work is sorted by priority, status, and release.
- No model invocation from `mb` itself.

## Conductor Cold Start Template

Use this as the default pre-PR template for Main Branch workspaces.

```md
You are working inside Conductor on Devon's Mac.

## Workspace

Workspace: {workspace_dir}
Target branch: main
Branch naming: dmthepm/<short-specific-name>

One branch owns one issue or one tightly scoped PR. Do not broaden scope
silently. If you find adjacent work, open or comment on a follow-up issue.

## Start Here

1. Read `CLAUDE.md`.
2. Read `decisions/2026-05-02-github-native-business-os.md`.
3. Read `docs/prd/v0-2-first-run-daily-briefing.md`.
4. Read `docs/prd/v0-2-agent-workflow-and-evals.md`.
5. Read the assigned GitHub issue and all comments.
6. Check open PRs that may touch the same files.

## North Star

Main Branch is a GitHub-native business operating system. `mb` is the
deterministic control plane. Agent-runtime skills are the judgment layer. GitHub
issues are tasks. PRs are proposals/conversations. The repo is the durable
business brain.

## Scope

Before editing, write a short scope note in `.context/cold-start.md`:

- issue / PR link;
- intended release;
- priority and status;
- in-scope files;
- explicit non-goals;
- validation plan;
- whether runtime smoke is required.

## Workflow

1. Investigate from source files and issue context.
2. Make the smallest coherent change.
3. Validate deterministically.
4. Run runtime/manual evals when the user-facing loop changed.
5. Update docs/issues when the work changes product truth.
6. Open or update the PR with evidence.

## Evidence Rules

No "done" without evidence.

Preferred evidence order:

1. local test output;
2. CLI smoke output;
3. runtime smoke evidence;
4. GitHub issue/PR/check state;
5. source-code references;
6. screenshots only when a visual or runtime UI matters.
```

## Per-Branch Cold Start File

Every substantial branch should create a gitignored note at
`.context/cold-start.md`. This is not the final artifact, but it keeps agents
honest during the run.

Suggested shape:

```md
# Cold Start

Issue:
Release:
Priority:
Status:

## Read

- [ ] CLAUDE.md
- [ ] Business OS decision
- [ ] v0.2 PRD
- [ ] Assigned issue/comments
- [ ] Existing tests near touched code

## Scope

In:

Out:

## Risks

- 

## Validation Plan

- Static:
- CLI:
- Fixture repo:
- Runtime/manual:

## Evidence Log

- 
```

The final PR should not rely on `.context/`. Anything durable belongs in docs,
tests, decisions, or issue comments.

## PR Creation Template

Every PR should tell reviewers what is in the box without requiring them to
reconstruct the branch.

```md
## Scope

- 

## Product Fit

- Which decision / PRD / issue this implements:
- What user loop changes:
- What stays out of scope:

## Changes

- 

## Validation

- Static:
- CLI:
- Fixture repo:
- Runtime/manual:

## Issue Updates

- Closes:
- Follow-ups opened:

## Risk

- 
```

For decision or PRD-only PRs, replace "Validation" with "Review Focus" and list
the product questions the reviewer should resolve.

## Code Review Template

Reviewers and review agents should lead with findings. Summaries come after
risks.

```md
## Must Fix

1. 

## Suggestions

1. 

## Product Alignment

- Matches the Business OS direction?
- Preserves `mb` as deterministic control plane?
- Keeps skills as runtime/judgment layer?
- Does not overclaim runtime compatibility?
- Uses GitHub language in a way non-developers can understand?

## State Model

- Canonical state stays in git?
- Local operational state stays out of git?
- Live process state is explicit?
- Secrets are never committed?

## Validation Review

- Static checks are present?
- CLI behavior tested in TTY and non-TTY modes when relevant?
- `--json` / exit-code behavior tested when relevant?
- Fixture business repo smoke included when repo shape changes?
- Claude Code/runtime smoke included when skill discovery or first-run flow
  changes?

## Verdict

APPROVE / REQUEST CHANGES / NEEDS DISCUSSION
```

## Evaluation Ladder

Use the lightest eval that proves the changed behavior. Do not run heavy manual
checks for documentation-only branches, but do not let user-facing runtime work
ship on unit tests alone.

### Level 0: Docs and Decision Checks

Use for docs, PRDs, issue cleanup, roadmap, and decision files.

Required:

- frontmatter present where the repo expects it;
- links resolve or are obviously future references;
- no stale product claims;
- no secrets;
- issue/PR state matches the document.

### Level 1: Static Code Checks

Use for any Python, packaging, workflow, or template change.

Required:

```bash
ruff format --check
ruff check
mypy mb
pytest -q --cov
```

Add narrower tests when the touched area has a faster focused target.

### Level 2: CLI Contract Tests

Use for any `mb` command, output, prompt, or exit-code change.

Required:

- unit tests below the Typer command layer;
- `CliRunner` tests for command output;
- non-interactive behavior tested;
- JSON output tested when present;
- exit codes tested for success and expected user-fixable failure.

TTY-aware commands must test both paths:

- interactive TTY shows the product surface;
- non-TTY / `--help` stays deterministic and scriptable.

### Level 3: Package and Install Smoke

Use for packaging, bundled skills, update, skill-linking, or first-run changes.

Required:

```bash
python -m build
python -m venv /tmp/mainbranch-smoke
/tmp/mainbranch-smoke/bin/pip install dist/*.whl
/tmp/mainbranch-smoke/bin/mb --version
/tmp/mainbranch-smoke/bin/mb skill list
```

For pipx-sensitive changes, run a real pipx smoke when practical:

```bash
pipx install --force dist/*.whl
mb --version
mb doctor
```

### Level 4: Business Repo Fixture Smoke

Use for onboarding, init, doctor, validate, graph, status, update, and start
changes.

Required flow in a temp directory:

```bash
mb init test-business
cd test-business
mb doctor
mb status
mb validate
```

Expected evidence:

- repo tree created correctly;
- `.claude/` skill wiring exists when expected;
- `mb doctor` reports repairable issues clearly;
- dirty git state is expected and explained;
- no command writes outside the requested repo except allowed local config.

### Level 5: Agent Runtime Smoke

Use when first-run, skill discovery, `/start`, `/pull`, `/think`, or runtime
handoff behavior changes.

This is manual or semi-automated in v0.2.0. Do not pretend it is covered by
unit tests.

Claude Code smoke:

```bash
tmpdir="$(mktemp -d)"
cd "$tmpdir"
mb init test-business
cd test-business
mb doctor
claude
# inside Claude Code:
# /start
```

Record evidence in the PR:

- Claude Code opened in the business repo, not the engine repo;
- `/start` was discoverable;
- skill had access to expected repo context;
- failure or missing auth path was clear if the runtime could not be launched.

Future runtime smokes should follow the same contract for Codex, Cursor,
OpenClaw, Hermes, or local LLM adapters:

- runtime opens against the business repo;
- skill/workflow discovery works;
- the runtime can read canonical repo files;
- output writes to the expected repo paths;
- `mb` remains the deterministic setup/status layer.

## Self-Improving Loop

Every issue branch should leave the system easier for the next agent.

When a branch reveals a repeated failure, choose one durable fix:

- add or update a test;
- add a fixture;
- improve `mb doctor`;
- clarify an error message;
- update a PRD or decision;
- open a follow-up issue with priority, status, and release;
- update Conductor preferences if the workflow rule belongs at agent startup.

Do not keep operational truth only in chat. Chat can decide; the repo must
remember.

## Issue Hygiene Rules

Issues should be maintained with simple fields:

- priority: Urgent, High, Medium, Low;
- status: Backlog, To Do, In Progress, Canceled, Duplicate;
- release: v0.1.x, v0.2.0, v0.2.1, v0.2.2, v0.3+.

No epics are required. If a body says "epic", rename it to a decision,
direction, or umbrella issue only when it still carries real coordination value.

Cold start should check for stale work:

- `In Progress` issue with no PR or comment should be nudged or moved back;
- shipped work should be closed with a release/link comment;
- duplicated work should be marked duplicate rather than left open;
- future ideas should sit in Backlog with a release guess, not pretend to be
  active.

## What This Means For v0.2.0

The first-run/daily-briefing release is not done until both layers pass:

- deterministic CLI checks prove `mb` can scaffold, inspect, update, and hand
  off reliably;
- runtime smoke proves a human can actually enter Claude Code and use `/start`
  from the generated business repo.

That is the product promise. Unit tests alone are necessary but insufficient.
