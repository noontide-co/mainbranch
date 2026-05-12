<!--
  Thanks for contributing to Main Branch.

  See CONTRIBUTING.md for branch + PR shape, concern-based commit
  organization, and pre-push gates. Keep PRs scoped — one logical
  change per PR, ideally 3–5 commits by concern.
-->

## Summary

<!-- 1–2 sentences on the user-visible change. -->

## Linked issue

<!-- Use Closes #N for issues this PR resolves; Refs #N for related context. -->

Closes #

## Why

<!-- Frame the problem before the solution. What pain or gap does this address? -->

## Commits by concern

<!-- One logical change per commit. Use this repo's bracketed vocabulary. -->

- [ ] Each commit body bullet-lists the changes in that commit
- [ ] Reviewer reading `git log --oneline main..HEAD` sees the shape of the work
- [ ] Commit subjects use `[add]`, `[update]`, `[fix]`, `[remove]`, `[refactor]`, `[docs]`, or `[chore]`

## Validation

Pre-push gate from repo root:

```bash
scripts/check.sh
```

Cite each level you ran with the evidence-line shape from
[`docs/release-agent-contract.md`](../docs/release-agent-contract.md):
`Level <N> <surface>: <command> — runtime: <python3/venv path> — exit: <code> — log: <path or excerpt>`.
Say which levels were not required and why.

- [ ] Level 1 static: `scripts/check.sh` passes
- [ ] Level 2 CLI contract: focused Typer/CliRunner tests, exit codes, `--json` behavior, TTY vs non-TTY (if CLI behavior touched)
- [ ] Level 3 package/install smoke (if packaging touched)
- [ ] Level 4 fixture repo (if init/onboard/status/start/update touched)
- [ ] Level 5 runtime smoke / dogfood harness / simulation-tier (if runtime, first-run, skill discovery, or release validation touched)
- [ ] SKILL.md ≤500 lines (if any skill touched)
- [ ] Package-visible release gate evidence before tag/publish (if preparing a release)
- [ ] Supply-chain review (if `.github/workflows/`, `.github/dependabot.yml`, `mb/pyproject.toml` deps, or `id-token`/`permissions` blocks touched — see [docs/supply-chain-policy.md](../docs/supply-chain-policy.md))

## Success metric

<!-- The observable condition that means this PR did its job. -->

## CHANGELOG

- [ ] Updated `CHANGELOG.md` `[Unreleased]` section, OR
- [ ] N/A — change is invisible to users (internal refactor, CI-only, etc.)

## Breaking changes

- [ ] No
- [ ] Yes — migration note below

<!-- If yes, describe what users must do to migrate. -->

## Public / private boundary

<!-- Confirm no private operator strategy, machine-specific paths, or runtime internals were committed.
     See docs/oss-operating-checklist.md if in doubt. -->
