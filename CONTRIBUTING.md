# Contributing to Main Branch

Main Branch is a public repo. Anyone can read it; not everyone is wired in to the engine cadence. The contributor flow below documents how the work happens, what gates run, and what discipline rules apply.

These rules are **tool-agnostic.** Conductor users, Codex users, Cursor users, and direct CLI contributors all follow the same shape — the rules describe the work, not the editor.

---

## Branch + PR shape

**One workspace = one branch = one PR.** Hard rule. Cross-cutting work that "feels obvious" gets flagged and stopped. Never reuse a branch.

**Branch convention** (current — Linear sync OFF): `<gh-username>/<short-descriptor>`. Descriptor is kebab-case, under 40 chars, no leading verbs (`fix-`, `add-`).

**PR titles** use Conventional Commits: `feat(scope): ...`, `fix(scope): ...`, `docs: ...`, `test: ...`, `refactor: ...`, `chore: ...`, `ci: ...`. Breaking changes append `!` and a `BREAKING CHANGE:` footer.

---

## Multi-commit organization (CONCERN, not chronology)

Each commit body bullet-lists changes in THAT commit. A reviewer reading `git log --oneline main..HEAD` should see the shape of the work.

| Commit type | What goes in it |
|---|---|
| `feat(scope): ...` | Core behavior change |
| `test(scope): ...` | Tests for new behavior (combine with feat if small) |
| `docs: ...` | README, SPEC, SCHEMA, SKILL.md, CHANGELOG, examples |
| `ci: ...` | Workflow edits, gate additions |
| `chore(scope): ...` | Dep bumps, package metadata, mechanical renames |
| `refactor(scope): ...` | Non-behavioral moves |
| `fix(scope): ...` | Bug fixes mid-work |

---

## Pre-push gates (multi-gate, separate)

The Python umbrella (`mb/`) has four distinct gates:

```bash
cd mb
ruff format --check .   # formatter — separate gate
ruff check .            # linter — separate gate
mypy mb                 # type check
pytest -q               # tests
```

`ruff check` (linter) and `ruff format --check` (formatter) are DISTINCT. Local lint passing does NOT imply format is clean.

For Go tools (Phase 2):

```bash
cd tools/tool-<name>
go fmt ./...
go vet ./...
golangci-lint run
go test ./...
```

For skill regression: run `bash ~/.claude/skills/test-skills/test-skills.sh` against your modified skill before pushing.

**No `--no-verify`. No `git commit --no-verify`. No skipping.**

---

## No history rewriting after first push

Never rewrite. Follow-up fixes after review = NEW commits on top. **Never force-push a pushed branch.** Never amend a pushed commit. If a gate fails, fix the root cause and commit the fix as its own commit.

---

## Public/private smell test

Main Branch is a **public repo**. Apply the test on every commit:

> "Would the reader (anyone with internet) be embarrassed or uncomfortable reading this?"

| Answer | Where it goes |
|---|---|
| Yes | Stays in your private repo. Main Branch does not see it. |
| Meh, fine | Main Branch is fine. |
| Not sure | Default private. Sanitize and re-evaluate. |

Specifically:

- Never commit personal-business numbers (MRR, client names, comp data)
- Never commit Skool-member-personal info
- Never commit live Stripe IDs / API keys
- Never commit working URLs to private member resources

---

## Skill changes

Any change to `.claude/skills/*/SKILL.md` or its `references/` should:

1. Run `/skill-creator` review (or equivalent self-review against [the skill-creator guide](https://github.com/anthropics/claude-code/blob/main/docs/skills.md)).
2. Run skill regression: `test-skills` skill (admin-only) verifies the skill-system invariants.
3. Keep `SKILL.md` under 500 lines (CI gates this). If it grows past, split content into `references/<topic>.md`.
4. Add or update frontmatter: `name:`, `tier:` (skill | playbook), `calls:` (list of tool/skill names invoked by this skill).

---

## Cross-cutting flags

If your change touches more than one of: skills + tools + mb umbrella + CI workflows + docs — STOP. Open a tracking issue, narrow scope, ship the smallest coherent slice. Cross-cutting branches are how regressions ship.

---

## Code review format

PR reviews use this shape:

- Numbered findings, each with file + line citation
- Severity tag: HIGH / MEDIUM / LOW
- MUST FIX (blocks merge) vs SUGGESTIONS (nice-to-have, fine as follow-ups) — separated
- Verdict at end: APPROVE / REQUEST CHANGES (with must-fix count) / NEEDS DISCUSSION

---

## How to find the work

The engine v0.1.0 decision is `decisions/2026-04-29-mb-vip-v0-1-0-master.md`. It locks vocabulary, repo shape, ship list, /site upgrade scope, and the conductor preferences encoded above.

The companion business-side master plan is tracked in `noontide-co/projects#119`. Read it when a contribution touches product positioning, public launch sequencing, pricing, the agency arm, or the four CLI pillars.

If you're considering a contribution, read it first.
