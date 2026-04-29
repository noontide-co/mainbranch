# mb-vip Conductor Preferences

Last updated: 2026-04-29

Source of truth is the Conductor UI (Repository Settings → Preferences for `mb-vip`).
Update this file when you change preferences in the UI — paste matching blocks into the UI panel so Conductor-spawned agents read the current version, not stale UI copy.

The companion file in `noontide-projects` (`/Users/devonmeadows/conductor/workspaces/noontide-projects/edinburgh-v1/.context/attachments/preferences-v2.md`) defines the cross-repo workflow and Thoth runtime canon. mb-vip is the **engine repo** under that umbrella. The business repo (`noontide-projects`) and the engine repo (`mb-vip`) are paired but distinct: business repo carries soul/offer/audience/voice/proof + research + decisions; engine repo carries skills + playbooks + tools + the `mb` umbrella + educational triage content.

---

## General preferences

```
You are working inside Conductor on Devon's Mac.

## Workspace

Your workspace is {workspace_dir}, a git worktree of /Users/devonmeadows/Documents/GitHub/mb-vip. Each Conductor workspace owns exactly one branch. The target branch for PRs is main.

One workspace = one branch = one issue (when issues exist) = one PR. Never reuse a branch across tickets. Never widen scope into another issue's lane — flag it and stop.

The .context directory (gitignored) is collaboration scratch space only. Durable state lives in the repo itself: SKILL.md files, playbook markdown, tool source, decisions/, research/.

## This Repo

`mb-vip` (also published as `mainbranch-ai/vip` on GitHub) is the **engine** for Main Branch — the public OSS Python umbrella + Go tools + skill markdown + playbook markdown that power Devon's business stack and ship to operators.

The repo is **public, MIT-licensed**. Treat every commit as public forever.

Engine-side scope:

- `mb/` — the Python umbrella package (`pipx install mainbranch`). CLI commands: `mb init`, `mb resolve`, `mb validate`, `mb test`, `mb doctor`, `mb claim`.
- `tools/` — individual Go binaries (`tool-domain`, `tool-dns`, `tool-pages`, `tool-stripe`, `tool-og-render`). One concern per tool. Each ships its own `cmd/`, `SKILL.md`, `README.md`, `RELEASING.md`. Phase 2 deliverable; v0.1.0 ships `mb` umbrella first.
- `.claude/skills/` — markdown skills loaded by Claude Code. Each skill has SKILL.md (≤ 500 lines, frontmatter required) + `references/` folder for deep content. Existing: ads, end, help, organic, pull, setup, site, start, think, vsl, wiki.
- `.claude/playbooks/` — multi-step opinionated workflows. v0.1.0 starters: ship-bet, weekly-review.
- `.claude/educational/` — "tell me more" triage content. Loaded on-demand when skills surface opinionated defaults (Cloudflare > Vercel, Forgejo > GitHub for personal data, etc.).
- `.claude/lenses/`, `.claude/reference/`, `.claude/scripts/` — supporting infrastructure (compliance, voice cards, automation).
- `templates/` — consumer-repo bootstrap templates (`CLAUDE.md.tmpl`, `CODEOWNERS.tmpl`, brand-style-template, etc.).
- `decisions/`, `research/` — engine-specific dated decisions and investigations. Cross-link to `noontide-projects/decisions/` when business and engine concerns chain.

The business repo (`noontide-projects`) is at `/Users/devonmeadows/Documents/GitHub/noontide-projects` and is the **task-source** for cross-repo work — it carries the master decisions that drive engine work, and its `pr-review` skill is the canonical PR review path for engine contributions.

## Locked stack

| Layer | Choice | Why locked |
|---|---|---|
| Distribution | `pipx install mainbranch` (PyPI) | One install command, isolated env, OS-agnostic. |
| Umbrella | Python 3.10+ Typer CLI (`mb`) | Matches companyctx + morning-paper precedent. |
| Tools | Go binaries, one concern each | Single static binary per tool. No Python deps for ops surface. |
| Skill format | Markdown with YAML frontmatter | Claude Code-native. No MCP. |
| Playbook format | Markdown SKILL.md (same shape as skills) | Reusable infrastructure. |
| Cross-agent | Claude Code first-class. Codex/Cursor/Hermes/local-LLMs are v0.2+ targets, NOT v0.1.0 claims. | README sentence locked; do not soften. |

## Key invariants (read before touching anything)

1. **Vocabulary lock — tool / skill / playbook only.** No `atom` / `molecule` / `compound`. The Garry-Tan-style chemistry metaphor was retired in `decisions/2026-04-29-mb-vip-v0-1-0-master.md`. Any PR that reintroduces it is wrong.
2. **No MCP.** Agent discovery is `SKILL.md` + CLI invocation, never an MCP server. Per `feedback_skill_md_over_mcp.md` (Devon memory rule). Never propose MCP. Never reintroduce.
3. **No `mb run` multi-agent runtime.** `mb` is a CLI umbrella, not a runtime. Switzerland-for-runtimes posture: Paperclip is the runtime in the Noontide stack; `mb` does not compete.
4. **Claude Code first-class in v0.1.0.** README sentence locked verbatim: *"Main Branch v0.1.0 is built for Claude Code. Other agents (Codex, Cursor, Hermes, local LLMs) may run individual skills with manual setup, but full-flow compatibility is a v0.2+ goal. We will publish a compatibility matrix when v0.2 ships."* Do not soften. Do not delete.
5. **Anti-SaaS posture.** "Own the work, rent only the rails." No "rent your business" framing in formal docs. Reserve the rhetoric for marketing surfaces (`noontide-projects/outputs/`), not engine README/SKILL.md.
6. **OSS / paid mechanism.** Skill files MIT in this repo. Reference data (compiled voice corpus, etc.) lives in a separate paid private GitHub repo (`noontide-co/curated`) gated by Collaborator membership. Skills resolve reference paths via `mb resolve`; missing-reference returns a public stub plus subscribe banner. **Never bake paid reference paths into MIT skill files.** See master decision § "OSS / Paid — Engine Side".
7. **Schema lock.** Tool / skill / playbook frontmatter MUST include `tier:` and `calls:`. Educational content frontmatter MUST include `type: educational`, `topic:`, `status:`. `mb validate` (when shipped) enforces.
8. **"Tool" word disambiguation.** In this repo, "tool" = the binary CLI (`tool-domain`, `tool-dns`, …). It is NOT the MCP "tool" usage. Preserve clarity in docs — when ambiguous, write "binary tool" or "MCP-style tool" explicitly.
9. **Public/private smell test on every commit.** "Would the reader (anyone with internet) be embarrassed reading this?" If yes, it belongs in `noontide-projects` (private), not here.
10. **Educational triage pattern ("tell me more").** Every opinionated default in any skill offers `[t] Tell me why / [s] Recommended setup / [n] Continue anyway`. Educational content lives at `.claude/educational/<topic>.md`.

## Where to read first (start protocol)

Before doing work, read in this order:

1. `README.md` and `CLAUDE.md` at repo root.
2. `decisions/2026-04-29-mb-vip-v0-1-0-master.md` — the engine master. § "Conductor Preferences for mb-vip", § "OSS / Paid — Engine Side", § "Educational Triage Content", § "Cross-Agent Compatibility (v0.1 honesty)".
3. `noontide-projects/decisions/2026-04-29-main-branch-v0-1-0-master.md` — the business master that drives engine work.
4. The assigned GitHub issue body and **every comment**, oldest to newest. `gh issue view <N> --comments` then `gh api repos/mainbranch-ai/vip/issues/<N>/timeline --paginate` (catches cross-references).
5. Every linked PR: `gh pr view <PR> --comments` and `gh pr diff <PR>` if load-bearing.
6. Every file path mentioned in body or comments — read current state on `main` before assuming shape.

Issue body is a snapshot. Comments contain scope narrowings, blocker discoveries, corrections. Miss a comment, ship against the wrong contract.

Set non-interactive gh CLI before proceeding: `gh config set pager cat && gh config set prompt disabled`.

## Skill workflow contract

This repo IS the skill source. When work touches `.claude/skills/<x>/`, `.claude/playbooks/<x>/`, or `.claude/educational/<x>.md`:

- **Always invoke `/skill-creator` for review** before commit. Frontmatter, description (50–150 words), line count (≤ 500), references folder layout, See Also linking. Skill-creator is the canonical authoring guide.
- **Always run `bash ~/.claude/skills/test-skills/test-skills.sh`** locally before push. Full 162-test regression suite. Pre-push gate; pr-review's Subagent A re-runs it.
- **PR review goes through `/pr-review`** in `noontide-projects/.claude/skills/pr-review/`. That skill is the canonical reviewer flow — admin-only. mb-vip preferences POINT at it; they do NOT duplicate the checklist.

## Two-stage agent flow (mirror companyctx)

| Stage | Trigger | Responsibilities | Forbidden |
|---|---|---|---|
| **Branch-author agent** | Devon assigns issue / opens workspace | Investigate → Write → Validate → Commit → Push to origin → Report. Comment on issue at kickoff, blocker, scope-narrowed, branch-ready, lock/stand-down. | NEVER `gh pr create`. NEVER open draft PR. NEVER auto-open via any tool. |
| **PR-author agent** | Devon clicks Conductor "Merge PR" button | Open PR with conventional-commit title + structured body. Post one-line issue comment with PR URL. Stop. | Don't re-run gates. Don't push new commits. Don't widen scope. Don't fix CI red — that's a new workspace. |

## Two-machine model

mb-vip is **mac-local + GitHub-public**. There is no Thoth deploy step for engine code (skills are loaded by Claude Code locally; CLI is `pipx install` from PyPI). When engine work needs to land on Thoth:

1. Commit and push the engine repo.
2. Publish to PyPI (when relevant — handled by `.github/workflows/publish-pypi.yml`).
3. Thoth's `mb` install picks up the new version via `pipx upgrade mainbranch`.

No `ssh thoth git pull` for skills — they're loaded from the local clone of mb-vip on whichever machine is running Claude Code.

## Reporting

When done, report in this exact shape:

1. **Branch at rest.** Branch name, commit count on top of `main`, one-line summary per commit (`git log --oneline main..HEAD`).
2. **Pushed to origin.** Confirm `git push` succeeded. End with: "Branch `<name>` is ready. Pushed to origin. Ready for the Merge PR button."
3. **Pre-push gates, all green locally.** Per-language gate results (see § "Pre-push checklist"). If a gate is N/A (e.g., docs-only PR), say so and why.
4. **Issue acceptance boxes.** Ticked vs deferred — copy the issue's checklist and mark each box `[x]` delivered or `[ ]` deferred (with reason: blocked-on / Slice-B / out-of-scope).
5. **Follow-ups worth tracking.** Open as new issues, don't bundle into the current work.
6. **Blockers.** Dependencies on other open issues, anything that would widen scope.
```

---

## Setup script

```
python3 -m pip install -e ".[dev]" 2>/dev/null || true
gh config set pager cat
gh config set prompt disabled
mkdir -p .claude
cat > .claude/settings.local.json << 'INNEREOF'
{
  "permissions": {
    "additionalDirectories": [
      "/Users/devonmeadows/Documents/GitHub/noontide-projects"
    ]
  }
}
INNEREOF
exit
```

This wires the engine repo to read `noontide-projects` as an additional directory (the inverse of the noontide-projects setup, which wires it to read mb-vip). Engine work routinely needs to verify it's not breaking the consumer repo's expectations.

---

## Branch rename preferences

```
mb-vip does NOT have Linear sync as of 2026-04-29. Branch convention is the GitHub-username form, matching recent practice on this repo:

    dmthepm/<short-descriptor>

Examples (good):
- dmthepm/mb-vip-codify-2
- dmthepm/og-render-resvg-upgrade
- dmthepm/skill-brief-draft-extract
- dmthepm/educational-anti-cloud-backup

Rules:
- Descriptor is kebab-case, under 40 characters.
- No leading verbs (`fix-`, `add-`, `measure-`, `update-`).
- Describe the thing, not the action.
- One slash only (after username).
- No ticket prefixes (no `cox-` — that's companyctx).

When Linear sync lands (v0.2 candidate), branch convention rolls over to:

    devon/<linear-id-lowercase>-<short-descriptor>

(matches companyctx — Linear's "Copy git branch name" produces this format and the sync hinges on matching it.) Until that lands, do NOT use the Linear form on mb-vip.

Rename procedure:
1. git branch -m dmthepm/<short-descriptor>
2. git push origin -u dmthepm/<short-descriptor> after your first commit.
3. If a placeholder branch was already pushed, delete the remote: git push origin --delete <old-name>.
```

---

## Pre-push checklist (non-negotiable)

The engine repo runs three gates locally before push. Every gate is a separate check; passing one does NOT imply another is clean.

### Gate 1: skill regression suite (always)

```
bash ~/.claude/skills/test-skills/test-skills.sh
```

Full 162-test regression suite. Matches pr-review's Subagent A. If local doesn't match remote, P1 blocker. `test-skills` is admin-only — contributors get the test results back via PR review, not by running it themselves. (For this repo, you ARE running it because you're in Devon's machine; the admin-only constraint applies to external contributors who don't have the skill installed.)

### Gate 2: per-language gates (run what applies)

**Python** (when `mb/` or `tests/` touched — v0.1.0 day-one):

```
python -m ruff format --check .
python -m ruff check .
python -m mypy mb tests
python -m pytest -q
```

`ruff check` (linter) and `ruff format --check` (formatter) are DISTINCT gates. Local `ruff check` passing does NOT imply format is clean.

**Go** (when `tools/<name>/` touched — Phase 2 deliverable):

```
go fmt ./...
go vet ./...
golangci-lint run
go test ./...
```

**Markdown skills/playbooks** (when `.claude/skills/` or `.claude/playbooks/` touched):

```
# line-count enforcement — no SKILL.md > 500 lines
find .claude/skills .claude/playbooks -name SKILL.md -exec wc -l {} \; | awk '$1 > 500 {print "OVER 500:", $0}'
```

Any output = P1. Refactor to references folder.

### Gate 3: skill-creator validation (when skills/playbooks/educational touched)

When any of the following is touched, invoke `/skill-creator` for review BEFORE commit:

- `.claude/skills/<name>/` (new or modified)
- `.claude/playbooks/<name>/` (new or modified)
- `.claude/educational/<topic>.md` (new or modified — the "tell me more" triage pattern)
- Major changes to existing SKILL.md (rename, restructure, frontmatter changes, references folder reshape)

Skill-creator validates: frontmatter check, description discoverability (50–150 words), line count compliance (≤ 500), references folder use, See Also linking.

Workflow: invoke `/skill-creator` → it reviews + suggests edits → operator applies → commit. **Do NOT ship a SKILL.md without /skill-creator review for v0.1.0+.**

### Aspirational vs current gate state

- Skill regression: GREEN, lives in `~/.claude/skills/test-skills/`.
- Python: aspirational for v0.1.0 day-one (`mb` umbrella ships first; gate enforces from then forward).
- Go: aspirational for Phase 2 (when `tools/` ships).
- Markdown: GREEN, applies today.
- Skill-creator: GREEN, applies today.

Document the full gate suite now; enforce per-language as the code lands.

---

## Issue-thread updates

Comment on the GitHub issue at exactly these five moments — and ONLY these. Issue thread is the durable record of decisions that change the meaning of the work. The commit log + PR body are for everything else.

1. **Kickoff** — one comment restating IN-scope / OUT-scope for your slice. Links the branch you created.
2. **Blocker discovered** — dependency on another open issue, missing infrastructure, scope ambiguity. Comment names the blocker and what you're doing about it (stop / narrow / proceed-with-caveat).
3. **Scope narrowed** — if you carved a Slice A out of the issue, comment documents the split BEFORE you push code.
4. **Branch ready for PR** — one comment when the branch is pushed and locally green. Branch name, summary of what's on it. Do NOT open the PR yourself — Devon clicks the Conductor "Merge PR" button.
5. **Lock / stand-down** — if accepted but you're handing off (e.g., a dependency blocks implementation), comment records the stopping point.

**Do NOT comment on every commit.** Do NOT comment per-acceptance-checkbox. Do NOT post "🚀 working on it" updates. Issue comments are for moments that change the contract.

GitHub issues on `mainbranch-ai/vip` are the primitive task store when issues exist. When work is decision-driven (not issue-driven), the master decision in `noontide-projects/decisions/` or `mb-vip/decisions/` is the contract — apply the same comment-discipline to the decision file's PR thread.

---

## Commit + push discipline (STOP BEFORE PR)

You are responsible for commits and pushing the branch. You are NOT responsible for opening the PR. Devon clicks the "Merge PR" button in Conductor when he's ready; that button fires a separate PR-creation agent.

Rules:

- **Conventional Commits required, one logical change per commit.** `feat(scope): ...`, `fix(scope): ...`, `docs: ...`, `test: ...`, `refactor: ...`, `chore: ...`, `ci: ...`. Breaking changes use `!` + a `BREAKING CHANGE:` footer. Do not lump unrelated changes — a reviewer reading `git log --oneline main..HEAD` should see the shape of the work.
- **Push to origin after the branch is green locally.** `git push -u origin dmthepm/<descriptor>`. Push more than once if follow-up commits land — still no PR.
- **Do NOT run `gh pr create`. Do NOT open a draft PR. Do NOT auto-open via any tool.** If the branch already has a PR open from a prior agent, stop and report — don't push to it silently.
- **If a gate fails locally, fix the root cause and commit the fix as its own commit.** Never `--no-verify`. Never amend a pushed commit. Never force-push.
- **When changing skill structure, follow skill-creator's guidance** on file length + references folder layout. Skill-creator review is part of the pre-commit flow, not a post-hoc check.

---

## Multi-commit organization

If the branch touches more than one concern, split into multiple logical commits so a reviewer reading `git log --oneline main..HEAD` sees the shape without opening the diff. One-shot 1M-context sessions routinely produce 50–100+ file diffs across schema, tests, docs, CI, scripts, and skills; a reviewer can't hold that in one head.

Chunk by CONCERN, not chronological order. Common chunks, each its own commit:

| Commit type | What goes in it |
|---|---|
| `feat(scope): ...` | Core behavior change (new skill, new tool, new CLI command, new playbook). |
| `test(scope): ...` | Tests for new behavior. Combine with feat if small (1–2 test files); split when 3+ test files. |
| `docs: ...` | README, CHANGELOG, examples, brief reference updates. Always its own commit unless trivially one-line. |
| `ci: ...` | Workflow edits, dependabot config, pre-push gate additions. Own commit. |
| `chore(scope): ...` | Dep bumps, package metadata (`py.typed`, `__init__.py` re-exports), mechanical renames. |
| `refactor(scope): ...` | Non-behavioral code or doc moves. Own commit so reviewer can skim and trust it. |
| `fix(scope): ...` | Bug fixes surfaced mid-work. Own commit even if tiny. |

### Engine-specific scopes

| Scope | Used when |
|---|---|
| `mb` | Touching the Python umbrella package (`mb/` source, CLI commands, resolver). |
| `tools(<name>)` | Touching a specific Go binary (`tools/tool-domain/`, `tools/tool-dns/`, etc.). |
| `skill(<name>)` | Touching a markdown skill (`.claude/skills/<name>/`). |
| `playbook(<name>)` | Touching a playbook (`.claude/playbooks/<name>/`). |
| `educational(<topic>)` | Touching educational triage content (`.claude/educational/<topic>.md`). |
| `templates` | Touching `templates/` (consumer-repo bootstrap). |
| `docs` | Repo-level docs (README, CLAUDE.md, conductor-preferences.md). No scope. |

Each commit's body bullet-lists the specific changes in THAT commit. Title = verdict, body = inventory.

### Reorganize-at-end pattern

In a 1M-context session, do all the work in one monolithic WIP commit locally. At the end, before push:

1. `git reset HEAD~1` (drop the WIP).
2. `git add -p` (or path-based `git add`) to construct logical commits.
3. `git log --oneline main..HEAD` — verify the shape reads like a changelog.
4. THEN push.

First push, no force-push concern. Once the branch is pushed and visible as a Merge PR candidate, **do NOT rewrite history.** Follow-up fixes after review are NEW commits on top. Never force-push a pushed branch.

One-commit branches are fine when the work genuinely is one concern. Judgment call — if a reviewer would ask "why is this all one commit?", split.

---

## Skill-creator integration

`/skill-creator` is the canonical authoring guide for skills, playbooks, and educational content in this repo. It is mandatory.

### When to invoke

- Creating any new skill in `.claude/skills/<name>/`.
- Creating any new playbook in `.claude/playbooks/<name>/`.
- Creating any new educational topic in `.claude/educational/<topic>.md` (the "tell me more" triage pattern from the v0.1.0 master).
- Major changes to existing SKILL.md: rename, restructure, frontmatter changes, references folder reshape.
- Splitting a SKILL.md that's pushing 500 lines into body + references.

### What it validates

| Check | Pass criterion |
|---|---|
| Frontmatter | `name:` matches folder name. `description:` is 50–150 words. Required fields present. |
| Description discoverability | Contains "use when" language, trigger phrases, synonyms. Long enough to trigger reliably; short enough to not bloat always-on context. |
| Line count | SKILL.md ≤ 500 lines. References files flagged at 400+ lines as candidates for splitting. |
| References folder | If body content > 200 lines, deep content lives in `references/`. SKILL.md links to references; references don't link back unnecessarily. |
| See Also | Reference files > 100 lines have a See Also section linking to canonical sources. |

### Workflow

```
operator drafts skill → /skill-creator review → applies suggested edits → commit
```

Do NOT ship a SKILL.md, playbook, or educational topic without /skill-creator review for v0.1.0+. Pr-review's Step 6 (Skill-Creator Compliance) verifies this on the reviewer side.

---

## test-skills integration

`test-skills` is the regression test runner for `.claude/skills/`. It ships in this repo's test infrastructure.

### Pre-push gate

Every PR that touches `.claude/skills/`, `.claude/playbooks/`, `.claude/educational/`, or any tool/CLI runs:

```
bash ~/.claude/skills/test-skills/test-skills.sh
```

locally before push. Report the test count in the branch-ready issue comment (e.g., "162/162 passed"). Pr-review's Subagent A re-runs it; if local count doesn't match remote count, P1 blocker.

### Admin-only

`test-skills` is admin-only. External contributors don't run it themselves — they get the test results back via PR review. This is intentional. The skill encodes Devon's regression contract; running it requires the admin install.

For Devon's own machines (this repo's primary author and reviewer), `test-skills` runs as part of the pre-push checklist on every push.

---

## pr-review integration

The canonical PR review skill lives at `noontide-projects/.claude/skills/pr-review/SKILL.md`. It is **admin-only**. Reviewers run it.

### mb-vip preferences DO NOT duplicate the review checklist

mb-vip preferences POINT at pr-review and require it for every contribution. **Engine PRs that bypass pr-review are P1 by definition.** If a PR ships without pr-review having run, the next reviewer's first action is to run it.

### What pr-review covers (so this file doesn't have to)

The pr-review flow includes:

| Step | What it checks |
|---|---|
| Subagent A | Regression tests — full 162-test suite. P1 gate. |
| Subagent B | Cross-reference integrity — stale paths, broken markdown links, See Also completeness. |
| Subagent C | File length enforcement — every SKILL.md ≤ 500 lines, large reference files flagged. |
| Step 6 | Skill-creator compliance — frontmatter, description discoverability, references folder use. |
| Steps 7–9 | Cross-cutting concerns (compliance, voice, routing), system comprehension check, skill-or-mode decision. |

### When mb-vip cares

- Any PR touching `.claude/skills/`, `.claude/playbooks/`, `.claude/educational/`, `.github/workflows/`, `mb/`, `tools/`, or top-level docs (README.md, CLAUDE.md, conductor-preferences.md) goes through pr-review.
- Trivial single-line PRs (typo fix, dep bump) MAY skip Subagents A/B/C if the reviewer documents the skip rationale in the PR comment. Default is run-everything.

mb-vip preferences honor the pr-review flow as gospel. If the two ever conflict, pr-review wins.

---

## Cross-cutting concerns (engine-specific)

The list of things that are P1-blocking regardless of what the issue asks for.

### Vocabulary

- **Tool / skill / playbook only.** No `atom` / `molecule` / `compound`. The chemistry metaphor was retired. Any reintroduction is a P1 fix.
- **"Tool" disambiguation.** In this repo, a "tool" is a binary CLI under `tools/<name>/`. It is NOT MCP "tool" usage. When ambiguous, write "binary tool" or "MCP-style tool" explicitly.

### No MCP

- Never propose an MCP server. Never reintroduce one. Agent discovery is `SKILL.md` + CLI invocation.
- This is a Noontide-wide posture, not a v0.1.0-only constraint. See `feedback_skill_md_over_mcp.md`.

### Runtime posture

- **No `mb run` multi-agent runtime.** `mb` is a CLI umbrella. Switzerland-for-runtimes: Paperclip is the runtime in the Noontide stack. Do not build agent orchestration into `mb`.

### Cross-agent compatibility

- **Claude Code is first-class in v0.1.0.** README sentence is locked verbatim. Do not soften, do not delete, do not promise Codex/Cursor/Hermes/local-LLM support before v0.2.
- Operators trying Cursor and discovering skills don't run will churn quietly. We accept this for v0.1.0 and fix in v0.2+.

### Anti-SaaS posture

- "Own the work, rent only the rails." Reserve "rent your business" rhetoric for marketing surfaces (`noontide-projects/outputs/`), NOT engine README/SKILL.md.
- Engine docs read like infrastructure documentation, not pitch decks.

### OSS / paid mechanism

- Skill files MIT, this repo. Reference data (compiled voice corpus, etc.) lives in a separate paid private GitHub repo (`noontide-co/curated`) gated by Collaborator membership.
- Skills resolve reference paths via `mb resolve <key>` (see `mb/mb/resolve.py`). Resolution order: paid → local override → MIT stub.
- **Never bake paid reference paths into MIT skill files.** Skills call the resolver; the resolver picks the path.
- Missing-reference returns the MIT stub plus a banner: `"This is a public stub. To use Devon's compiled voice corpus, subscribe at mainbranch.io/run."`

### Schema lock

- Tool / skill / playbook frontmatter MUST include `tier:` and `calls:`.
- Educational content frontmatter MUST include `type: educational`, `topic:`, `status:`, `last_reviewed:`.
- `mb validate` (when shipped) enforces. Missing fields = P1.

### Educational triage pattern

Every opinionated default in any skill offers three paths:

```
[t] Tell me why    → loads .claude/educational/<topic>.md
[s] Recommended    → walks through the recommended setup
[n] Continue       → skill proceeds with the default
```

- Initial topics (v0.1.0): `anti-cloud-backup.md`, `opinionated-stack-cloudflare-vs-vercel.md`, `github-vs-gdocs.md`.
- Pattern is reusable — any new opinionated default gets a matching educational file.
- Educational files follow the format in the master decision § "Educational Triage Content".

### No vendor commitments before measurement

- Per `feedback_no_vendor_commitments_pre_test.md`: do NOT name specific vendors / APIs in public-facing writing before testing them.
- README, CHANGELOG, accepted ADRs may name a vendor only after a measurement spike.
- Research files and proposed ADRs may list candidates with a "pending spike" banner.

### Public OSS hygiene

- mb-vip is a **public MIT repo**. Treat every commit as public forever.
- Never commit secrets, API keys, OAuth tokens, proxy credentials, 1Password material.
- Never commit Devon-personal numbers (MRR, client names, comp data).
- Never commit Skool-member-personal info (real names, emails outside example.test, contact details).
- Never commit live Stripe / Cloudflare / Cal.com IDs that resolve to real production resources.
- Apply the public/private smell test on every paragraph: *"Would the reader (anyone with internet) be embarrassed?"* If yes, it goes to `noontide-projects` private.

---

## Create PR preferences

This prompt fires when Devon clicks the Conductor "Merge PR" button on a branch that is already pushed to origin and locally green. The branch-author agent committed and pushed; you are the PR-author agent. One job: open the GitHub PR against `main`, post the one-line issue comment, stop.

### Do not

- Do NOT re-run pre-push gates. The branch-author agent reported them; trust the report unless the branch is visibly stale.
- Do NOT push new commits, amend, rebase, or force-push.
- Do NOT widen scope (no drive-by fixes from this prompt; open a new issue instead).
- If the branch has zero commits on top of `main`, is not pushed, or already has an open PR — STOP and report.

### Inputs you can trust

- `git log --oneline main..HEAD` — commits you're wrapping.
- `git diff main..HEAD --stat` — file shape.
- `gh issue view <N> --comments` — acceptance checklist + scope narrowings (when issue-driven).
- Decision file in `decisions/` (when decision-driven, no GitHub issue).

### PR title

Conventional Commits strictly. Examples:

- `feat(skill/site): add archetype-driven minisite flow`
- `fix(mb): clear ruff UP045/B008 in resolver`
- `docs: refresh CLAUDE.md + conductor-preferences for engine v0.1.0`
- `ci(publish): wire PyPI trusted-publisher workflow`
- `chore(skill/site): rename reference/brand → reference/visual-identity`
- `refactor!: vocabulary swap atom/molecule/compound → tool/skill/playbook`

Reference issues in PR bodies by GitHub number (`#N`) so close-on-merge fires. Use `Refs #N` when delivering only a slice; use `Closes #N` only when the PR fully satisfies the issue's acceptance checklist.

When the engine PR is part of a coordinated cross-repo landing (e.g., engine PR #114 + business PR #91), reference the companion PR by URL in the body's "Coordinated chain" section.

### PR body structure

```
## Summary
- 2–5 bullets on what shipped. Behavior change, not file list.

## Commits
- One bullet per commit in `git log --oneline main..HEAD` order (oldest first): `sha — subject`.

## Acceptance (from #N)
Copy the issue's acceptance checklist verbatim. Tick boxes this PR satisfies. Annotate boxes intentionally NOT ticked (e.g., "blocked on #15", "Slice B scope").

## Test plan
- [x] `bash ~/.claude/skills/test-skills/test-skills.sh` — X/Y passed (count from branch-author report)
- [x] `ruff format --check .` clean (when Python touched)
- [x] `ruff check .` clean (when Python touched)
- [x] `mypy mb tests` clean (when Python touched)
- [x] `pytest -q` — X tests passed (when Python touched)
- [x] Skill line counts ≤ 500 (when skills touched)
- [x] /skill-creator review passed (when skills touched)
- [x] Any behavior-specific checks

## Coordinated chain (when applicable)
- Companion PR: <URL> in noontide-projects (or vice versa)
- Master decision: link

## Breaking changes (if any)
- `BREAKING CHANGE:` footer with migration posture. Include `!` in commit title.
```

Keep the body scannable. The reader should know what's in the box and how it was validated without opening it.

### After the PR is open

1. Post a single comment on the GitHub issue (when issue-driven): `PR #<PR-number>: <title>. Branch \`dmthepm/<descriptor>\`.` One line.
2. Report back: PR URL, issue-comment URL, whether CI has picked up the PR. If CI is red on the first run, name the failing job and stop — fix-ups are a new workspace, not this prompt.

---

## Code review preferences

Engine-specific code review checklist. Reads as a tighter companyctx + pr-review hybrid. When in doubt, defer to the canonical `/pr-review` skill in `noontide-projects/.claude/skills/pr-review/`.

Each finding cites file + line where applicable.

1. **SCOPE.** Does this PR stay inside the assigned issue / decision boundary? Flag any file or function that widens scope, adds an MCP server, introduces a vendor SDK not on the issue's list, or starts infrastructure owned by another open issue.

2. **CONTRACT PRESERVATION.**
   - Skill / playbook / tool frontmatter includes `tier:` and `calls:` (schema lock).
   - Educational content frontmatter includes `type: educational`, `topic:`, `status:`, `last_reviewed:`.
   - Vocabulary lock honored — tool / skill / playbook only, no atom/molecule/compound.
   - "Tool" word disambiguated where ambiguous.
   - `mb resolve` is the path the skill takes; no hardcoded paid-reference paths.

3. **SKILL-CREATOR COMPLIANCE.**
   - Did the contributor invoke `/skill-creator`? Frontmatter valid? Description in 50–150 words?
   - SKILL.md ≤ 500 lines? References folder used for deep content? See Also present on long reference files?
   - If a SKILL.md is > 450 lines, flag P3 (near limit).

4. **TEST-SKILLS GREEN.**
   - Branch-author reported test count. PR-review's Subagent A re-runs and confirms.
   - If local count doesn't match remote — P1 blocker.

5. **CROSS-REFERENCE INTEGRITY.**
   - All markdown links resolve.
   - See Also sections present on reference files > 100 lines.
   - No stale paths (`reference/brand/`, `business_repo_path`, `settings.json` for skills, `config/devon`, etc.).
   - New files cross-link to canonical sources.

6. **SECRETS + PRIVACY.**
   - No API keys, tokens, passwords, OAuth credentials, 1Password material, .env files.
   - No Devon-personal numbers (MRR, client names, comp data).
   - No Skool-member-personal info or live production IDs.
   - Public/private smell test passes on every paragraph.

7. **CI GATE COMPATIBILITY.**
   - Python 3.10 compatibility: no `datetime.UTC` (use `timezone.utc`), no 3.11-only stdlib in hot paths.
   - `ruff format --check` will pass (linter-clean is not enough).
   - `mypy` strict on touched modules.
   - `pytest` green; coverage not regressed.
   - For Go (Phase 2): `go fmt`, `go vet`, `golangci-lint`, `go test` clean.

8. **CONVENTIONAL COMMITS.**
   - PR title matches `<type>(<scope>)?: <description>` or `<type>!: ...` for breaking.
   - Breaking changes include `BREAKING CHANGE:` footer with migration posture.
   - Engine-specific scopes used correctly (`mb`, `tools(<name>)`, `skill(<name>)`, `playbook(<name>)`, `educational(<topic>)`, `templates`).

9. **NO MCP.** Never propose. Never reintroduce. P1 if reintroduced. See `feedback_skill_md_over_mcp.md` and the master decision.

10. **PUBLIC OSS HYGIENE.**
    - No vendor commitments without measurement (per `feedback_no_vendor_commitments_pre_test.md`).
    - No partner data leakage (Joel Requena's pipeline, Skool members, etc.).
    - License headers correct on new source files.
    - README and CHANGELOG agree with shipped behavior.

11. **CROSS-AGENT COMPATIBILITY HONESTY.**
    - The locked README sentence (Claude Code first-class, v0.2+ for others) is not softened, deleted, or weakened.
    - No PR claims Codex/Cursor/Hermes/local-LLM support without a v0.2 milestone landing first.

12. **TRUNCATED FILES.** Flag any file that ends abruptly, mid-function, or mid-paragraph.

### Output format

Structured for machine consumption (review is often fed back to the authoring agent for fixes):

- Number each finding (e.g., `[1] SCOPE: mb/cli.py:45 — this PR is the resolver slice; CLI changes belong in #18.`).
- Severity tag on each: `HIGH` / `MEDIUM` / `LOW`.
- Separate findings into MUST FIX (blocks merge) vs SUGGESTIONS (nice-to-have, fine as follow-ups).
- End with a verdict: `APPROVE` / `REQUEST CHANGES` (with count of must-fix items) / `NEEDS DISCUSSION`.

---

## Reporting

When done, report in this exact shape (Devon reads this to decide whether to click the Merge PR button):

1. **Branch at rest.** Branch name (`dmthepm/<descriptor>`), commit count on top of `main`, one-line summary per commit (`git log --oneline main..HEAD`).
2. **Pushed to origin.** Confirm `git push` succeeded. Do NOT name a PR URL — there is no PR yet. End with: `Branch dmthepm/<descriptor> is ready. Pushed to origin. Ready for the Merge PR button.`
3. **Pre-push gates, all green locally.** Name each one that ran:
   - `bash ~/.claude/skills/test-skills/test-skills.sh` — X/Y passed
   - Python: `ruff format --check`, `ruff check`, `mypy mb tests`, `pytest -q` (with test count) — when applicable
   - Go: `go fmt`, `go vet`, `golangci-lint`, `go test` — when applicable
   - Markdown: SKILL.md line counts ≤ 500 — when skills touched
   - `/skill-creator` review — when skills/playbooks/educational touched
   If a gate is N/A (docs-only PR), say so and why.
4. **Issue acceptance boxes.** Ticked vs deferred. Copy the checklist; mark each box `[x]` delivered or `[ ]` deferred with reason.
5. **Follow-ups worth tracking.** New issues to open; don't bundle into current work.
6. **Blockers.** Dependencies on other open issues, anything that would widen scope.

---

## Cross-references

- Engine master decision: `decisions/2026-04-29-mb-vip-v0-1-0-master.md`
- Business master decision: `noontide-projects/decisions/2026-04-29-main-branch-v0-1-0-master.md`
- Canonical PR review skill: `noontide-projects/.claude/skills/pr-review/SKILL.md`
- Test-skills runner: `~/.claude/skills/test-skills/test-skills.sh`
- Skill authoring guide: `/skill-creator` (in available skills)
- Cross-repo conductor preferences: `/Users/devonmeadows/conductor/workspaces/noontide-projects/edinburgh-v1/.context/attachments/preferences-v2.md`

