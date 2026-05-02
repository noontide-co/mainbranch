---
type: educational
topic: upgrading-mainbranch
status: stub
last-updated: 2026-05-01
---

# How Main Branch updates work after pipx install

## If `mb --version` says `0.1.x`

Run the bootstrap upgrade once:

```bash
pipx upgrade mainbranch
mb --version
```

`mb update` was added after the earliest public package, so old installs cannot
run it yet. After the pipx upgrade, `mb update` and `/pull` become the normal
path.

## If you already have a business repo

Repair Claude Code skill discovery from inside that repo:

```bash
cd /path/to/your-business
mb skill link --repo .
mb doctor
mb start
```

This rewrites `.claude/settings.local.json` and the local skill links so Claude
Code sees the bundled skills from the installed package.

## Why this changed

If you installed Main Branch with `pipx install mainbranch`, your skills live
inside the installed Python package. That is good for clean setup: there is no
engine repo to clone, and `mb init` can link Claude Code directly to the
packaged skills.

It also means updates come through PyPI. When Devon ships a new version, run:

```bash
pipx upgrade mainbranch
```

Then re-link your business repo if needed:

```bash
mb skill link --repo /path/to/your-business
```

For old repos with `reference/core/`, do not move files first. That legacy
layout is still supported while the automated `mb migrate` command is pending.
Read `docs/MIGRATING.md` in the engine repo before doing any layout migration.

If you use the older clone-based setup, updates still come from Git:

```bash
git -C ~/Documents/GitHub/mb-vip pull origin main
```

`/pull` detects the install mode and chooses the right update path.
