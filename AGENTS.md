# Agent Instructions

Main Branch is public open-source infrastructure. Treat this file as the
repo-level operating contract for Codex, Claude Code, and any other agent or
human contributor working in this repository.

## Product Shape

Main Branch is a CLI plus agent-runtime skill system for running a business from
markdown files in git.

- `mb` is the deterministic, inspectable, scriptable control plane.
- Agent-runtime skills are the judgment-heavy execution layer.
- GitHub issues are tasks.
- Pull requests are proposals and review conversations.
- Git history is the evolution story.
- A user's business repo is the durable business brain.

Claude Code is the first-class runtime today. Codex, Cursor, OpenClaw, Hermes,
Paperclip-adjacent orchestration, and local runtimes are compatibility targets
only when tested. Do not claim support before there is an adapter or smoke
evidence.

## Quick Start

For normal repo validation:

```bash
scripts/check.sh
```

For focused CLI work:

```bash
cd mb
pytest tests/test_<area>.py -q
```

For package/install changes:

```bash
(cd mb && python -m build)
python -m venv /tmp/mainbranch-smoke
/tmp/mainbranch-smoke/bin/pip install mb/dist/*.whl
/tmp/mainbranch-smoke/bin/mb --version
/tmp/mainbranch-smoke/bin/mb skill list
```

## Repository Layout

```
.
+-- AGENTS.md          # shared instructions for repo agents
+-- CLAUDE.md          # Claude Code adapter instructions
+-- README.md          # public user-facing entrypoint
+-- CHANGELOG.md       # public release truth
+-- CONTRIBUTING.md    # contributor workflow
+-- decisions/         # dated product/architecture decisions
+-- docs/              # setup, compatibility, PRDs, checklists, migration docs
+-- mb/                # Python package, CLI, tests, bundled data
+-- .claude/skills/    # bundled Claude Code skill source
+-- templates/         # files copied into created business repos
+-- tools/             # experimental helper tools
+-- scripts/           # repo-level validation helpers
```

## Repo Surfaces

Changes may affect one or more public surfaces:

- CLI behavior in `mb/mb/` and `mb/tests/`;
- packaged data under `mb/mb/_data/`;
- bundled skills under `.claude/skills/`;
- business-repo scaffolding under `templates/` and `mb/mb/init.py`;
- user docs in `README.md`, `docs/BEGINNER-SETUP.md`, `docs/MIGRATING.md`,
  `SUPPORT.md`, and `docs/compatibility.md`;
- contributor/agent docs in `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and
  `.github/`;
- release surfaces in `CHANGELOG.md`, GitHub Releases, PyPI metadata, and
  Linear Releases.

Do not assume a change is "just docs" when it changes instructions that agents,
skills, users, or release automation follow.

## Public / Private Boundary

This repository is public. Every committed file should be safe for a stranger to
read forever.

Public is appropriate for:

- deterministic CLI behavior;
- runtime-agnostic skill contracts;
- product decisions, PRDs, and release criteria;
- sanitized examples and fixtures;
- open-source support, security, and contribution docs.

Do not commit:

- secrets, tokens, credentials, raw account data, or customer/member data;
- private local paths, personal operating preferences, or machine-specific
  automation details;
- private community operations, launch plans, or partner/customer strategy;
- untested runtime compatibility claims.

Use OS temp for throwaway build artifacts, scratch repos, and smoke-test output.
Use `.context/` only for repo-bound handoff notes such as `cold-start.md` or
branch-specific collaboration state. It is gitignored and is not durable product
truth. Durable truth belongs in code, tests, docs, decisions, fixtures, or GitHub
issues.

## Start Protocol

Before editing:

1. Read this file.
2. Read `README.md`.
3. Read the assigned GitHub/Linear issue and all comments.
4. If the work touches public product shape, release discipline, runtime claims,
   contributor workflow, or public/private boundaries, apply
   `docs/OSS-OPERATING-CHECKLIST.md`.
5. If the work touches v0.2 product direction, read:
   - `decisions/2026-05-02-github-native-business-os.md`
   - `docs/prd/v0-2-first-run-daily-briefing.md`
   - `docs/prd/v0-2-agent-workflow-and-evals.md`
6. If the work touches the CLI/runtime boundary, read:
   - `decisions/2026-05-01-mb-cli-vs-agent-workflows-boundary.md`
   - `docs/compatibility.md`
7. If the work touches skills, inspect the relevant
   `.claude/skills/<name>/SKILL.md` and nearby tests or fixtures.
8. Check open PRs for overlapping files before making broad edits.

For substantial branches, write `.context/cold-start.md` before editing:

```md
# Cold Start

Issue:
Linear ID:
Release:
Priority:
Status:

## Scope

In:

Out:

## Risks

-

## Validation Plan

- Static:
- CLI:
- Package/install:
- Fixture repo:
- Runtime/manual:
```

## Work Shape

Prefer one coherent user loop per branch. Do not broaden scope silently. If you
find adjacent work, open or comment on a follow-up issue instead of burying it in
the current PR.

Good issue slices look like:

- one command surface, such as `mb status`;
- one repair loop, such as `mb update`;
- one validator, such as cross-reference validation;
- one runtime proof, such as Claude Code `/start` discovery from a fresh repo.

Avoid tiny PRs that cost more in cold start, review, CI, and merge overhead than
they return. Large PRs are fine when they have one success metric and
concern-organized commits.

## Branches, Issues, and Releases

If a Linear issue exists, use Linear's official branch name when it is provided
by the issue or task runner. Preserve Linear IDs in branch names, commit
messages, and PR metadata so Linear Releases can attach work correctly.

If no Linear issue exists, use a short concrete branch name such as
`<gh-username>/status-briefing` or `<gh-username>/runtime-smoke`.

GitHub remains the public durable issue thread:

- use `Closes #N` only when the PR fully completes the GitHub issue;
- use `Refs #N` for partial slices or related context;
- comment on issues when scope changes, blockers appear, or a branch is ready
  for review;
- keep target release and priority visible in `.context/cold-start.md` and PR
  bodies for release-bearing work.

## Linear-Hosted Agents

When launched from Linear or assigned a Linear issue:

- treat the Linear issue as the task brief, but verify durable details in this
  repository before editing;
- use the official Linear branch name if the task runner provides it;
- preserve the Linear ID in branch, commit, and PR metadata;
- map Linear status honestly: move to started/in progress only when coding or
  writing actually begins, and do not mark shipped until release verification
  proves users can install it;
- keep GitHub issue closure accurate with `Closes #N` only for fully completed
  GitHub issues;
- comment when scope changes, blockers appear, or validation cannot reach the
  required level;
- open a PR when the hosted-agent workflow expects it, but never merge it unless
  explicitly instructed.

Workspace-level Linear guidance should stay short and point agents back here.
This file is the detailed contract.

## GitHub Workflow

Prefer the GitHub CLI for GitHub truth and mutations:

```bash
gh config set pager cat
gh config set prompt disabled
```

Use `gh issue view`, `gh issue list`, `gh pr view`, `gh pr diff`,
`gh pr checks`, `gh pr create`, and `gh pr edit` when GitHub work is needed.
Do not merge a PR unless the maintainer explicitly asks for merge.

Hosted agents that are assigned an issue may open a PR when their task runner
expects it. Local branch-author agents should follow the current prompt: if it
says to stop before PR creation, push the branch and report that it is ready.

## Commit Discipline

Use concern-based commits. A reviewer should understand the branch from:

```bash
git log --oneline main..HEAD
git diff main..HEAD --stat
```

This repo commonly uses:

- `[add] Brief description`
- `[update] Brief description`
- `[fix] Brief description`
- `[remove] Brief description`
- `[refactor] Brief description`

Do not rewrite pushed history unless the maintainer explicitly asks.

## Validation Ladder

Use the lightest eval that proves the behavior. Do not ship first-run,
runtime-discovery, update, packaging, or skill changes on unit tests alone.

Level 0, docs/decision:

- frontmatter where expected;
- links resolve;
- no stale product claims;
- no private details in public docs.

Level 1, static:

```bash
scripts/check.sh
```

Run this from the repo root before pushing. It mirrors CI's package working
directory; do not substitute root-level `mypy mb` unless you also pass the right
config.

Level 2, CLI contract:

- focused Typer/CliRunner tests;
- exit codes;
- `--json` behavior where present;
- TTY vs non-TTY behavior for launch and onboarding UI;
- no hangs in scripts or CI.

Level 3, package/install smoke:

Run when packaging, entrypoints, bundled data, skill discovery, or update paths
change.

```bash
(cd mb && python -m build)
python -m venv /tmp/mainbranch-smoke
/tmp/mainbranch-smoke/bin/pip install mb/dist/*.whl
/tmp/mainbranch-smoke/bin/mb --version
/tmp/mainbranch-smoke/bin/mb skill list
```

Use `pipx install --force ...` or `pipx upgrade ...` smoke when install/update
behavior changed.

Level 4, fixture repo:

```bash
tmpdir="$(mktemp -d)"
mb onboard --yes --name "Test Business" --path "$tmpdir/test-business"
cd "$tmpdir/test-business"
mb doctor
mb status
mb start --json
mb validate
```

Level 5, runtime smoke:

- create a fresh business repo;
- launch the relevant runtime from that repo;
- verify `/start` or the equivalent runtime entrypoint is discoverable;
- verify the skill reads the business repo and does not write into the engine
  repo;
- record the evidence in the PR.

If a runtime cannot be launched because of auth or UI constraints, say that
explicitly and describe the closest verified fallback. Do not pretend CLI tests
cover runtime discovery.

## Skill Maintenance

Bundled skills are product code even when implemented as Markdown.

When changing `.claude/skills/<name>/`:

- keep each skill directory self-contained;
- reference `references/`, `scripts/`, and `assets/` using paths relative to the
  skill directory;
- do not reference sibling skills with `../` paths or absolute local paths;
- keep shared helper content small enough to duplicate when two skills need it;
- keep `SKILL.md` under the line-count gate and move detail into
  `references/`;
- avoid platform-specific shell interpolation in cross-runtime skill content
  unless there is a documented fallback;
- test behavior with the relevant runtime smoke when discovery or invocation
  changes.

Mechanical Python tests do not prove LLM-facing skill behavior. If the prose or
workflow changed, include a runtime/manual validation note.

## State Model

- Canonical business state stays in git.
- Local operational state stays out of git.
- Secrets stay in the OS keychain, environment, or runtime-specific secret
  stores, never in repo files or frontmatter.
- Dashboard/server/process state must be explicit, local-first, optional, and
  documented before it is added.

## PR Expectations

PR bodies should give reviewers product scope and validation evidence:

- summary of the user loop or product truth changed;
- in-scope and out-of-scope bullets;
- commit list, oldest first;
- release, Linear IDs, `Closes`/`Refs`, and follow-ups;
- success metric;
- validation by ladder level;
- public/private boundary note.

Update `CHANGELOG.md` for user-visible CLI, skill, packaging, compatibility, or
workflow changes. Skip it only for invisible maintenance.

## Review Focus

When reviewing, lead with findings:

- public operating checklist in `docs/OSS-OPERATING-CHECKLIST.md`;
- public/private boundary;
- product direction;
- state model;
- runtime claims;
- CLI contract;
- validation evidence;
- issue/release fit;
- stale language;
- test quality;
- truncated files.

Verdicts should be explicit: approve, request changes, or needs discussion.
