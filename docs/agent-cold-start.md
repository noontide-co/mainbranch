# Agent Cold Start

Use this sequence at the start of each Main Branch issue, PR review, or release
task. The goal is fast context with the right source of truth: read the durable
public contract first, then discover only the extra docs the task actually
touches.

This file is public agent guidance. Private maintainer workflow preferences can
point here, but should not duplicate the product contract.

## Always Read First

Read these before editing or reviewing:

1. `AGENTS.md` - repo operating contract, validation ladder, public/private
   boundary, and PR expectations.
2. `README.md` - user-facing promise, command surface, runtime support claim,
   and beginner path.
3. `docs/ethos.md` - product principles and state model.
4. `docs/operator-loops.md` - Sense, Decide, Ship, Reflect taxonomy and daily
   loop language.
5. `docs/roadmap.md` - current direction, anti-scope, and shipped foundation.
6. `docs/system-architecture.md` - current CLI, skill, repo, provider,
   runtime, graph, and release architecture boundaries.
7. `docs/oss-operating-checklist.md` - release, runtime-claim, state-model,
   issue/PR, and public/private review checklist.
8. `docs/agent-writing-style.md` - action-first writing rubric for agent docs,
   PR descriptions, reviews, issue comments, and local preferences.
9. `CHANGELOG.md` - read `[Unreleased]` and the latest shipped version section
   so current tense matches release truth.

Do not paste these docs into issue comments, PR bodies, or local preferences.
Link them and state only the decision the current task needs.

## Then Read The Work Thread

Read the assigned GitHub issue and comments before editing. Main Branch GitHub
issues mirror to Linear. Maintainer and hosted agents with Linear access should
call Linear MCP `get_issue` for the mirrored issue before naming the branch; the
returned `gitBranchName` is the branch name. External contributors without
Linear access can use a GitHub-native branch name and reference the issue in the
PR.

GitHub remains the public durable work thread. Leave public coordination
comments on GitHub by default; the sync carries them to Linear. Use Linear-only
comments only for private logs, local runtime notes, or internal team context
that should not appear in public GitHub.

For old, heavily commented, or previously worked issues:

- read every issue comment oldest to newest;
- read linked PRs when their diff or comments are load-bearing context;
- read one hop of linked issues when the assigned issue depends on them;
- inspect any named file path on current `main` before assuming shape;
- summarize the current contract in a local cold-start note when comments
  changed scope over time.

## Write The Cold Start Note

For substantial branches, write a local cold-start note before editing:

- issue and Linear ID when present;
- priority, status, target release if any;
- operator loop: Sense, Decide, Ship, or Reflect;
- in scope and out of scope;
- validation plan by ladder level;
- whether package, fixture, runtime, or release smoke is required.

Use `.agent/` for repo-local, gitignored agent logs, smoke-test evidence, and
branch-local handoff notes. Some hosted runners may provide their own ignored
scratch space; public examples in this repo use `.agent/`. Scratch space is not
durable product truth. Keep durable facts in public docs, decisions, tests,
fixtures, or GitHub issues.

## Progressive Discovery

After the work thread is clear, read only the extra docs that match the surface
you are changing.

| Trigger | Read |
| --- | --- |
| Product direction, roadmap, workflow shape, dashboard, provider choice, dependency choice, setup policy | `docs/roadmap.md`, `docs/operator-loops.md`, relevant `decisions/`, relevant PRD under `docs/prd/`, `docs/dependency-choices.md` when dependencies or provider rails are in play |
| CLI/runtime boundary, runtime support claim, adapter behavior | `decisions/2026-05-01-mb-cli-vs-agent-workflows-boundary.md`, `docs/compatibility.md`, `docs/claude-code-runtime-dogfood.md` when Claude Code evidence matters |
| Skills or generated runtime guidance | relevant `.claude/skills/<name>/SKILL.md`, its `references/`, generated templates under `templates/`, nearby skill validation tests or fixtures |
| First-run, package install, skill discovery, `mb init`, `mb onboard`, `mb status`, `mb start`, `mb update` | `docs/release-simulations.md`, `docs/release-agent-contract.md`, package/install smoke contract in `AGENTS.md`, relevant CLI tests |
| Release prep, package-visible release, supply-chain or publish workflow | `docs/release-agent-contract.md`, `docs/release-simulations.md`, `docs/supply-chain-policy.md`, current `CHANGELOG.md`, GitHub Release / PyPI / Linear release state |
| Post-release sweep | `docs/post-release-alignment.md`, local release evidence when available, shipped PRs since the last tag |
| Public/private boundary, support, contributor workflow, state model | `docs/oss-operating-checklist.md`, `SUPPORT.md`, `SECURITY.md`, `CONTRIBUTING.md` as relevant |

Do not read every decision file by default. Use the issue, changed files,
`AGENTS.md`, and the trigger table above to pick the few that can change the
answer.

## Branch And Issue Hygiene

- Main Branch issues mirror to Linear. Maintainer and hosted agents with Linear
  access fetch the mirrored Linear issue with Linear MCP `get_issue` and use
  its `gitBranchName` for issue work.
- The normal shape is `<username>/main-<number>-<full-ticket-title-lowercase-with-dashes>`.
- External contributors without Linear access can use
  `<gh-username>/<issue-number>-<short-title>` and reference the GitHub issue in
  the PR.
- If work truly has no issue, use a short descriptive branch and create the
  public GitHub issue first when the work is product-facing.
- Preserve Linear IDs in branch names, commit messages, and PR metadata when
  available so Linear Releases can attach work.
- Use `Closes #N` only when the PR fully resolves the GitHub issue.
- Use `Refs #N` for setup work, partial slices, or related context.
- Leave public status, blocker, scope, and readiness comments on GitHub by
  default. Use Linear-only comments only for private logs or internal context.

## Release Noise Boundary

Most issues are not releases. Do not load release runbooks, PyPI checks, or
release-simulation evidence unless the task touches a release-bearing surface:
packaging, install/update, first-run, skill discovery, runtime claims, publish
workflow, supply chain, or post-release alignment.

When the task is release-bearing, use the release docs exactly. Do not compress
away evidence capture, first-run smoke, PyPI verification, or the distinction
between Claude Code print-mode proxy evidence and interactive TUI smoke.

## Local Preference Split

Local maintainer preferences should stay short and private:

- workspace path and target branch;
- issue, branch, Linear, and PR workflow habits;
- private local repo paths and tool availability;
- reminders learned from recent reviews that do not belong in public docs.

Local preferences should not carry:

- the full Main Branch product contract;
- release truth that belongs in `CHANGELOG.md`, GitHub Releases, and PyPI;
- runtime support claims that belong in `docs/compatibility.md`;
- public/private policy that belongs in `docs/oss-operating-checklist.md`;
- stale issue lists or future-tense product plans.

If a preference would help any contributor, move it into this repo. If it only
helps one maintainer's local workflow, keep it private and brief.
