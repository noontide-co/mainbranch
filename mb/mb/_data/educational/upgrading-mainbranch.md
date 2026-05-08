---
type: educational
topic: upgrading-mainbranch
status: draft
last-updated: 2026-05-08
---

# Updating Main Branch without becoming the package manager

Main Branch changes quickly. You should not have to understand Python
packaging, git remotes, or old clone layouts to stay current.

The beginner path is:

```text
/mb-update
```

Run it inside Claude Code from your business repo. It delegates the mechanical
work to `mb update`, explains what changed, and tells you the next command.

## The terminal path

Power users can run:

```bash
mb update --repo .
```

from the business repo.

`/mb-start` also checks whether an important update exists before routing the
session. You do not need to check for updates manually every day.

## If your install is too old

Very early public installs may not have `mb update` yet. If `mb --version`
prints an old version and `/mb-update` cannot run, use the bootstrap command:

```bash
pipx upgrade mainbranch
mb --version
```

After that, return to the business repo and let Main Branch repair skill
discovery if needed:

```bash
cd /path/to/your-business
mb skill link --repo .
mb doctor
```

Those commands are troubleshooting, not the everyday beginner loop.

## Why updates work this way

Most users install Main Branch with:

```bash
pipx install mainbranch
```

That means the CLI and bundled Claude Code skills live inside the installed
Python package. Updates come from PyPI. The business repo stays yours; it is not
the engine repo.

Main Branch keeps those roles separate:

- `mb` updates the engine;
- the business repo stores your durable memory;
- `/mb-start` and `/mb-update` explain what to do next in business-owner
  language.

## Old business repos

If you already have a business repo from an older setup, do not hand-move files
first. Ask Claude to run read-only checks and show the plan:

```text
I want to update my existing Main Branch business repo. Please run read-only
checks first, show me the exact commands you recommend, and ask before doing
anything that writes files.
```

For old folder layouts, use the migration guide:

```bash
mb migrate --check
```

Only run `mb migrate --apply` after the dry-run shows the planned moves,
backup location, and no conflicts.

## What Main Branch does not claim

Updating the engine is not the same as proving a runtime behavior. Claude Code
is the supported runtime today. Other runtimes remain roadmap targets until
adapter code and smoke evidence exist.
