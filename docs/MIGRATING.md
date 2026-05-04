# Migrating Existing Main Branch Repos

Main Branch has two repo shapes in the wild:

- **Legacy shape:** `reference/core/`, `reference/domain/`, `reference/proof/`,
  and `outputs/`.
- **Current shape:** `core/`, `research/`, `decisions/`, `log/`, `campaigns/`,
  and `documents/`, with `reference/` kept as a compatibility layer for
  agent-runtime skills.

Existing repos do not need an urgent file move. The safe path is to update the
engine first, repair skill discovery, and only migrate file layout on a clean
branch when you need the new shape.

## Recommended: Let Claude Walk You Through It

If you are already using Main Branch and do not want to reason about old
symlinks, clone paths, or repo shapes, start Claude Code anywhere and paste this
prompt:

```text
I want to migrate my existing Main Branch setup to the current pipx + /mb-start
workflow.

Please go slowly and do this safely:

1. First run read-only checks only:
   - mb --version
   - mb update --check --json
   - mb skill list
   - find likely business repos under ~/Documents/GitHub that have CLAUDE.md
     plus core/ or reference/core/, research/, or decisions/
2. For each likely business repo, inspect without changing files:
   - mb doctor <repo>
   - mb status <repo>
   - mb skill repair --repo <repo>
   - mb migrate --repo <repo> status
3. Show me the exact commands you recommend before running anything that writes.
4. Do not delete real files. Only use Main Branch repair/apply commands after I
   confirm.
5. If a command says I need to restart Claude, stop and tell me exactly which
   folder to open next and which slash command to run.
```

Claude should end by getting each chosen business repo to this state:

```bash
cd /path/to/your-business
mb update --repo .
mb skill link --repo .
mb skill repair --repo .
mb doctor
mb status
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

## Repair An Existing Business Repo

From the business repo:

```bash
cd /path/to/your-business
mb update --repo .
mb skill link --repo .
mb skill repair --repo .
mb doctor
mb status
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
- Claude Code skills still read compatibility paths under `reference/`.

The only thing legacy users usually need immediately is:

```bash
mb update --repo /path/to/your-business
mb skill link --repo /path/to/your-business
mb skill repair --repo /path/to/your-business
```

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

After apply, `mb validate` may still report old frontmatter schema debt in
research and decision files. That means the layout migration worked but older
markdown files still need field/status cleanup. Repair those in small batches,
then run `mb validate --cross-refs` once frontmatter errors are down to zero.

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
mkdir -p log campaigns documents core/finance
touch log/.gitkeep campaigns/.gitkeep documents/.gitkeep core/finance/.gitkeep
```

Validate before merging the branch:

```bash
mb doctor
mb status
mb validate
mb start --json
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
2. Upgrade Main Branch with `mb update --repo /path/to/repo`; if your install
   is still on `0.1.x`, run `pipx upgrade mainbranch` first.
3. Run `mb skill link --repo /path/to/repo`.
4. Run `mb skill repair --repo /path/to/repo`; use `--apply` only when it says
   a stale Main Branch symlink is safe to move.
5. Run `mb doctor` and `mb status`.
6. Run `mb migrate --check`, read the diff, then run `mb migrate --apply` on a
   clean branch when you are ready.

For personal knowledge repos that do not have `reference/core/`, treat them as
GitHub-native repos that Main Branch can brief, not as fully migrated business
repos yet.
