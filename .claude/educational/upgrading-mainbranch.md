---
type: educational
topic: upgrading-mainbranch
status: stub
last-updated: 2026-05-01
---

# How Main Branch updates work after pipx install

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

If you use the older clone-based setup, updates still come from Git:

```bash
git -C ~/Documents/GitHub/mb-vip pull origin main
```

`/pull` detects the install mode and chooses the right update path.
