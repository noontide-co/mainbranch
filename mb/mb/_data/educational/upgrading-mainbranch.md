---
type: educational
topic: upgrading-mainbranch
status: stub
last-updated: 2026-05-02
---

# How Main Branch updates work after pipx install

The normal update path is `/mb-update` inside Claude Code, or `mb update` from
the business repo for power users. Main Branch detects pipx vs clone installs
and refreshes skill links for the repo.

Use raw `pipx` only as a bootstrap fallback for very old installs. If
`mb --version` says `0.1.x`, run this once:

```bash
pipx upgrade mainbranch
mb --version
```

`mb update` was added after the earliest public package, so old installs cannot
run it yet. After the pipx upgrade, `/mb-update` and `mb update` become the
normal path.

If you already have a business repo, repair Claude Code skill discovery from
inside that repo:

```bash
cd /path/to/your-business
mb skill link --repo .
mb doctor
mb start
```

Old repos with `reference/core/` do not need an urgent file move. That layout is
still supported while automated migration is pending. Read `docs/MIGRATING.md`
before moving files.
