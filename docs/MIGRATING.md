# Migrating Existing Main Branch Repos

Main Branch has two repo shapes in the wild:

- **Legacy shape:** `reference/core/`, `reference/domain/`,
  `reference/proof/`, `reference/visual-identity/`, and `outputs/`.
- **Current shape:** `core/`, `research/`, `decisions/`, `bets/`, `log/`,
  `campaigns/`, and `documents/`. `reference/` is compatibility-only for old
  repos and old readers.

Existing repos do not need an urgent file move. The safe path is to update the
engine first, repair skill discovery, and only migrate file layout on a clean
branch when you need the new shape.

The update is urgent. Do not continue a migration against a stale Main Branch
engine when a newer package is available. Update first, then repair repos. The
update changes the installed Main Branch tool, not the user's business files.

## `.mb` Is The Current Folder

If you see a `.mb/` folder in your business repo, that is expected. `.mb/` is
Main Branch's repo-local operational state: onboarding progress, provider
metadata, backups, issue drafts, schema markers, and other rebuildable helper
files.

You do **not** need a `.mb-vip/` folder. That name belongs to old clone-based
setup language and the former internal repo name. The current pipx setup does
not require a local engine clone inside your business repo.

Open Claude Code in the business repo folder, not in an engine clone. If slash
commands are missing, ask Claude to repair the skill wiring instead of creating
a `.mb-vip/` folder. These are the underlying commands Claude or a power user
may run:

```bash
mb update --repo .
mb skill link --repo .
mb skill repair --repo .
mb doctor
mb status --peek
```

## Recommended: Let Claude Walk You Through It

If you are already using Main Branch and do not want to reason about old
symlinks, clone paths, or repo shapes, start Claude Code anywhere and paste this
prompt:

```text
I want to migrate my existing Main Branch setup to the current pipx + /mb-start
workflow.

Please go slowly, but treat the Main Branch update as required before repo
repair. I may be new to Terminal, Git, branches, and GitHub.

1. First run read-only checks only:
   - mb --version
   - mb update --check --json
   - mb skill list
   - find likely business repos under ~/Documents/GitHub that have CLAUDE.md
     plus core/ or reference/core/, research/, or decisions/
   Treat every command as a possible writer until its help or docs prove
   otherwise. Use `--peek`, `--check`, or equivalent dry-run flags where they
   exist.
2. If Main Branch is outdated, stop repo work and tell me in plain English:
   "Main Branch needs to update before we touch your business folders. This
   updates the tool installed on your computer, not your business files. Should
   I run the update now?"
3. After I confirm, update Main Branch immediately through the Main Branch
   update path. If `/mb-update` is available, use it. Otherwise run
   `mb update --repo <repo>` from the business repo. Only mention raw package
   commands like `pipx upgrade mainbranch` if `mb update` is unavailable because
   the installed version is too old.
   Do not present the update as an optional phase.
4. Then inspect likely business repos without changing files:
   - mb doctor <repo>
   - mb status <repo> --json --peek
   - mb skill repair --repo <repo>
   - mb migrate --repo <repo> status
5. Recommend one repo to repair first, not a whole multi-repo project plan.
6. Show me the one next write action you recommend before running it.
7. Do not delete real files. Only use Main Branch repair/apply commands after I
   confirm.
8. If you create or switch to a git branch, explain that it is a safe draft copy
   of the work. Do not merge, delete, or rename branches unless I explicitly
   confirm.
9. If a command says I need to restart Claude, stop and tell me exactly which
   folder to open next and which slash command to run.
10. Do not end by giving me a list of internal mb commands to choose from. End
   with the exact folder to open, the exact `claude` command, and `/mb-start`.
```

After the user confirms the update and one repo repair, Claude should get the
chosen business repo to this state. This is implementation detail for Claude and
power users, not a beginner checklist:

```bash
cd /path/to/your-business
mb update --repo .
mb skill link --repo .
mb skill repair --repo .
mb doctor
mb status --peek
mb start
```

Then restart Claude Code from that business repo and run:

```text
/mb-start
```

This flow is intentionally confirmation-gated. `mb skill link` and
`mb skill repair --apply` only move stale Main Branch symlinks and broken links
with Main Branch skill names into timestamped backups. They do not delete
user-authored skill folders, real files, or live third-party skill links.

## If Claude Creates A Branch

Claude Code or `mb migrate --apply` may create or use a git branch before
changing files. That is good: a branch is a safe draft area, not finished work.
Do not leave a beginner wondering whether they should merge it.

When a migration or repair run leaves the user on a branch, Claude should end
with:

- the branch name;
- whether files changed;
- what checks passed or still need attention;
- the exact next folder and `/mb-start` command if the repo is ready;
- whether the branch should be kept as a draft, opened as a GitHub proposal, or
  reviewed by someone more technical before merging.

That final choice belongs to the user. Claude should explain what it thinks the
next git step is and why, then stop. Do not push, open a pull request, merge,
delete, rename, rebase, or force-push unless the user explicitly asks for that
git operation after seeing the branch summary. During migration dogfood or
support, this pause is useful product evidence: the maintainer can see whether
Claude understood branches, commits, review, and merge risk.

Use business language first:

- **branch** = a safe draft copy of the work;
- **pull request** = a proposal for review;
- **merge** = make the draft the main version.

If the user is unsure, the safe answer is to keep the branch local and ask for
review.

Before recommending merge, Claude should separate structural verification from
runtime verification. `mb doctor`, `mb validate`, rename detection, and line
counts prove the filesystem shape. They do not prove Claude Code skills behave
correctly through compatibility symlinks. On the first migration for a user or
repo family, prefer a small runtime smoke before merge:

1. Open Claude Code from the migrated business repo.
2. Run `/mb-start`.
3. Run a bundled skill smoke and label what it proved:
   - Discovery smoke: ask a read-only factual question such as
     `/mb-think what is the soul of this production?`. Pass means Claude Code
     recognized the slash command and read migrated core context from the
     business repo. It does not prove the full `/mb-think` workflow.
   - Full flow smoke: ask for a real research/decide/codify task and explicitly
     say to pause before writing files. Pass means the skill follows its normal
     workflow, writes only to the business repo after approval, and does not
     write into the Main Branch engine.
4. Confirm no skill writes into the engine repo.
5. Then summarize whether the branch is ready to push, review, or merge.

If an interactive Claude Code runtime smoke is not possible from the current
session, say that plainly. A static fallback can inspect `mb start`, skill
symlinks, `settings.local.json`, and referenced files, but it is not runtime
smoke. Label it as static fallback and list exactly what it does not prove.

During either static fallback or runtime smoke, inspect `.claude/` for old
clone-path symlinks outside the `mb-*` skill directories, especially
`.claude/lenses/` and `.claude/reference/`. `mb skill link` and
`mb skill repair` currently own Main Branch skill names; they may not repair
older lens/reference symlinks from clone-based setups. If those symlinks still
point at an old engine clone, report them as follow-up work and do not claim
the clone-to-pipx migration is fully complete until runtime behavior has been
observed without relying on the clone.

Claude Code app sessions may create `.claude/worktrees/` while you test a repo.
That directory is local runtime state, not migration work. Current `mb init` and
`mb skill link` add `.claude/worktrees/` to `.gitignore`; if an older repo shows
it in `git status`, run `mb skill link --repo .` before judging the migration
diff.

If Claude accidentally dirties an existing branch during discovery, stop before
running layout migration. Move the already-written Main Branch repair work onto
a branch, keep user-authored files separate, and do not commit local status
markers:

1. Show `git status --short` for the repo.
2. If only Main Branch repair files changed, create a branch such as
   `mainbranch-repair`.
3. Commit durable repair files such as `.gitignore` changes.
4. Do not commit `.mb/last-status-seen.json`; it is local operational state and
   should be gitignored.
5. Do not commit `.claude/worktrees/`; it is local Claude Code app state and
   should be gitignored.
6. If the repo already had unrelated dirty or untracked user files, leave that
   repo out of batch migration until the user reviews it.

## Command Mutability During Migration

Migration work should be one repo at a time. Do not batch `mb update`,
`mb skill link`, `mb status`, or `mb migrate --apply` across many business repos
unless the user explicitly asks for batch writes after seeing the risk.

Useful defaults:

- `mb status` writes `.mb/last-status-seen.json`; use `mb status --peek` for
  read-only discovery.
- `mb update` can update the installed engine and refresh repo-local skill
  links; treat it as a write.
- `mb skill link` writes Claude Code wiring and `.gitignore` repair entries;
  treat it as a write.
- `.claude/worktrees/` is Claude Code app local state. It should be ignored, not
  committed.
- `mb skill repair` without `--apply` reports personal-skill conflicts;
  `--apply` moves stale Main Branch symlinks to backups.
- `mb migrate status` and `mb migrate --check` inspect; `mb migrate --apply`
  writes the layout migration.

Check command help before assuming flag shape. Some commands take a positional
repo path, while others use `--repo`.

## If You Are On `mb 0.1.x`

Old `mb` versions do not have `mb update` yet. Run the bootstrap upgrade once:

```bash
pipx upgrade mainbranch
mb --version
```

After that, use the current update path:

```bash
mb update --repo /path/to/your-business
```

or, from inside Claude Code:

```text
/mb-update
```

`/mb-pull` still works as a legacy alias for existing users.

## Power User: Repair An Existing Business Repo

From the business repo:

```bash
cd /path/to/your-business
mb update --repo .
mb skill link --repo .
mb skill repair --repo .
mb doctor
mb status --peek
mb start
```

`mb skill link --repo .` rewrites the local Claude Code wiring so `/mb-start`,
`/mb-think`, `/mb-ads`, and the other bundled skills point at the installed
Main Branch package instead of an old clone path. It also removes stale
Main Branch engine paths from `.claude/settings.local.json` so Claude Code does
not keep access to two engine copies after a clone-to-pipx migration. During
that link step, Main Branch also moves provably stale or broken personal
symlinks with Main Branch skill names into a timestamped backup.

`mb skill repair --repo .` checks your personal `~/.claude/skills/` directory
for entries that can beat the project-local Main Branch skills in Claude Code.
It reports the resolved target for each finding. If the entry is a provably
stale Main Branch symlink or a broken symlink using one of Main Branch's current
or legacy skill names, run:

```bash
mb skill repair --repo . --apply
```

That moves the symlink itself to a timestamped backup under
`~/.claude/skills/.mainbranch-backups/`. It does not delete or move
user-authored directories, real files, or live third-party skill links.

## Do Not Start By Moving Files

If your repo has `reference/core/`, leave it alone until the setup works again.
Current Main Branch commands understand that legacy shape:

- `mb status` counts `reference/core/`.
- `mb start` treats a repo with `reference/core/`, `research/`, and
  `decisions/` as a business repo.
- Claude Code skills can read compatibility paths under `reference/` when
  `core/` is absent.

After migration, `reference/core` and `reference/offers` are compatibility
links back to `core/` and `core/offers/`. They are not duplicate files. Agents
should write once to the canonical `core/` or `core/offers/` path and should
not ask users to edit both a canonical path and its `reference/` bridge.

The only thing legacy users usually need immediately is:

```bash
mb update --repo /path/to/your-business
mb skill link --repo /path/to/your-business
mb skill repair --repo /path/to/your-business
```

For beginners, Claude should run that sequence after confirmation and translate
the result into the simple restart flow: open the business folder, run
`claude`, then type `/mb-start`.

## Automated Layout Migration

Use `mb migrate` on a clean branch when you are ready to move a legacy v0.1 repo
from `reference/core/` and `reference/offers/` into the current v0.2 paths.

Inspect the current schema state:

```bash
mb migrate status
```

You can put `--repo` before or after `status`; both inspect the same repo:

```bash
mb migrate --repo /path/to/your-business status
mb migrate status --repo /path/to/your-business
```

Preview the filesystem changes:

```bash
mb migrate --check
mb migrate --check --json
```

By default, `--check` is privacy-safe: it prints path/action summaries and JSON
counts without embedding full file bodies from your legacy reference files.
Those files can contain private strategy, proof, offer details, or customer
language. Only print the full unified diff when it will stay local:

```bash
mb migrate --check --diff
mb migrate --check --diff --json
```

`--check` exits non-zero when migrations are pending so scripts and agents can
detect drift without writing files. The path migration ignores local OS metadata
such as `.DS_Store`, `Thumbs.db`, `Desktop.ini`, and AppleDouble `._*` files.

Apply only after reading the diff:

```bash
mb migrate --apply
```

`--apply` creates a repo-local backup under `.mb/backups/` before changing files,
moves legacy core files into `core/`, moves legacy offer files into
`core/offers/`, leaves compatibility links under `reference/`, updates stale
`CLAUDE.md` path references, writes a migration decision artifact, and stamps
`.mb/schema_version`.

Those compatibility links exist so older readers keep working. Current skills
and agents should treat `core/` and `core/offers/` as the write targets.

After apply, `mb validate` may still report old frontmatter schema debt in
research and decision files. That means the layout migration worked but older
markdown files still need field/status cleanup. Repair those in small batches,
then run `mb validate --cross-refs` once frontmatter errors are down to zero.

Before merge, inspect git's own view of the migration:

```bash
git diff --stat --find-renames main..HEAD
git status --short
```

Git-reported `100%` renames are stronger evidence than line-count comparisons.
If the first migrated repo is the pilot for a larger set, let the branch sit
until `/mb-start` and at least one bundled skill discovery smoke have been run
from that repo. Require a full skill-flow smoke only when the migration changes
skill behavior, write paths, or runtime discovery.

## Manual Layout Migration

The automated command above is preferred. Keep this manual process only as a
fallback when you need to inspect or repair a repo by hand.

Only do this on a clean branch with everything committed:

```bash
cd /path/to/your-business
git status --short
git switch -c migrate-mainbranch-layout
```

For repos with `reference/core/`, move the core files to the current root
`core/` folder and leave a compatibility link behind:

```bash
mkdir -p core
git mv reference/core/* core/
rmdir reference/core
ln -s ../core reference/core
```

For repos with `reference/offers/`, do the same for offer-specific files:

```bash
mkdir -p core/offers
git mv reference/offers/* core/offers/
rmdir reference/offers
ln -s ../core/offers reference/offers
```

Then add the current empty working folders:

```bash
mkdir -p bets log campaigns documents core/finance
touch bets/.gitkeep log/.gitkeep campaigns/.gitkeep documents/.gitkeep core/finance/.gitkeep
```

Validate before merging the branch:

```bash
mb doctor
mb status --peek
mb validate
mb start --json
git diff --stat --find-renames
git diff --stat
```

If anything looks wrong, stop and keep the legacy layout.

## What About `.vip/config.yaml` and `~/.config/vip/local.yaml`?

Keep them for now.

- `~/.config/vip/local.yaml` is machine-local memory: default repo, recent
  repos, experience level, and last-seen changelog version.
- `.vip/config.yaml` is repo-local configuration used by older skills and
  future path/config work.

Do not delete either file as part of a layout migration. `mb skill link` writes
Claude Code discovery into `.claude/settings.local.json`; it does not replace
the old config files yet.

## Current Recommendation

For old business repos:

1. Start with the Claude-led migration prompt above if you want guidance.
2. Update Main Branch through `/mb-update` in Claude Code, or
   `mb update --repo /path/to/repo` for the power-user CLI path. Use
   `pipx upgrade mainbranch` only if the install is still on `0.1.x` and
   `mb update` is unavailable.
3. Run `mb skill link --repo /path/to/repo`.
4. Run `mb skill repair --repo /path/to/repo`; use `--apply` only when it says
   a stale Main Branch symlink is safe to move.
5. Run `mb doctor` and `mb status --peek`.
6. Run `mb migrate --check`, read the diff, then run `mb migrate --apply` on a
   clean branch when you are ready.

For personal knowledge repos that do not have `reference/core/`, treat them as
GitHub-native repos that Main Branch can brief, not as fully migrated business
repos yet.
