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

<!-- One logical change per commit. Conventional commit prefixes. -->

- [ ] Each commit body bullet-lists the changes in that commit
- [ ] Reviewer reading `git log --oneline main..HEAD` sees the shape of the work
- [ ] Conventional Commits format: `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`, `ci:`

## Test plan

Pre-push gates from `mb/`:

```bash
cd mb
ruff format --check .
ruff check .
mypy mb
pytest -q --cov=mb --cov-fail-under=70
```

- [ ] `ruff format --check` passes
- [ ] `ruff check` passes
- [ ] `mypy mb` passes
- [ ] `pytest -q --cov=mb --cov-fail-under=70` passes
- [ ] Wheel install smoke (if packaging touched)
- [ ] SKILL.md ≤500 lines (if any skill touched)

## CHANGELOG

- [ ] Updated `CHANGELOG.md` `[Unreleased]` section, OR
- [ ] N/A — change is invisible to users (internal refactor, CI-only, etc.)

## Breaking changes

- [ ] No
- [ ] Yes — migration note below

<!-- If yes, describe what users must do to migrate. -->
