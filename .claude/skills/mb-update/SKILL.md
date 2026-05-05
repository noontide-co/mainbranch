---
name: mb-update
description: Update Main Branch. Use when the user says update, upgrade, pull latest, get latest Main Branch, asks whether they are current, or after Devon announces a new release. Preferred over legacy /mb-pull.
loops: [ship]
---

# Update

Update the Main Branch engine and refresh this business repo's skill links.

Use this instead of asking the user to remember whether they installed with
pipx or an old clone. The CLI owns the mechanics. Do not suggest raw package
commands such as `pipx upgrade mainbranch` as the first update path; only use
that as the bootstrap fallback when `mb update` is unavailable or the installed
version is `0.1.x`.

---

## Step 1: Update Main Branch

Run from the business repo:

```bash
mb update --repo . --json 2>&1
```

Handle the JSON result:

| Result | What to say |
|---|---|
| `"ok": true`, `old_version != new_version` | "Updated Main Branch and refreshed skill links." |
| `"ok": true`, `old_version == new_version` | "Main Branch is already up to date." |
| `"ok": false` | Show the first error and the repair copy below. |
| Invalid JSON | Run `mb update --check --repo .` yourself if possible; if not, ask the user for that output. |

If the result includes warnings, show them after the main status.

---

## Step 2: If Update Fails

Tell the user:

> "I wasn't able to update Main Branch. This can leave you on old skills or old
> migration behavior.
>
> Try these from your business repo:
>
> ```bash
> mb update --check --repo .
> mb doctor
> ```
>
> If `mb --version` says `0.1.x`, run this once first:
>
> ```bash
> pipx upgrade mainbranch
> ```"

Do not continue as if the update worked.

---

## Step 3: Restart If Skill Links Changed

If `skills_relinked_count` is greater than zero, tell the user:

> "Skill links were refreshed. If a slash command does not appear in Claude
> Code, restart Claude from this repo and run `/mb-start`."

Claude Code loads slash commands at session start, so a restart can be required
after repairing links.

---

## Step 4: What Changed

After a successful update, read `CHANGELOG.md` from the active Main Branch
engine if available and summarize only the most recent "What this means for
you" section. Keep it short: 3-5 bullets max.

If no changelog is available, do not guess. Say:

> "Update complete. I couldn't find the local changelog, so run `mb --version`
> to confirm the installed version."
