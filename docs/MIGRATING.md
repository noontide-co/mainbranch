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
/pull
```

## Repair An Existing Business Repo

From the business repo:

```bash
cd /path/to/your-business
mb skill link --repo .
mb doctor
mb status
mb start
```

`mb skill link --repo .` rewrites the local Claude Code wiring so `/start`,
`/think`, `/ads`, and the other bundled skills point at the installed
Main Branch package instead of an old clone path.

## Do Not Start By Moving Files

If your repo has `reference/core/`, leave it alone until the setup works again.
Current Main Branch commands understand that legacy shape:

- `mb status` counts `reference/core/`.
- `mb start` treats a repo with `reference/core/`, `research/`, and
  `decisions/` as a business repo.
- Claude Code skills still read compatibility paths under `reference/`.

The only thing legacy users usually need immediately is:

```bash
pipx upgrade mainbranch
mb skill link --repo /path/to/your-business
```

## Optional Manual Layout Migration

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

If anything looks wrong, stop and keep the legacy layout. Legacy layout support
is intentional while `mb migrate` is still manual.

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

For old repos such as `noontide-projects`:

1. Upgrade Main Branch with `pipx upgrade mainbranch`.
2. Run `mb skill link --repo /path/to/repo`.
3. Run `mb doctor` and `mb status`.
4. Keep `reference/core/` until an automated `mb migrate --check` exists or
   you intentionally run the manual branch process above.

For personal knowledge repos that do not have `reference/core/`, treat them as
GitHub-native repos that Main Branch can brief, not as fully migrated business
repos yet.
