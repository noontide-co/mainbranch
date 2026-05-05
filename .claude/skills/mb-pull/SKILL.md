---
name: mb-pull
description: Legacy alias for /mb-update. Use only when the user explicitly types /mb-pull or says pull latest using old Main Branch language.
loops: [ship]
---

# Pull

`/mb-pull` is kept for existing users. The preferred command is now
`/mb-update`, matching the CLI command `mb update`.

Run the same update command:

```bash
mb update --repo . --json 2>&1
```

Then follow the result handling in `/mb-update`.

If the user asks which command to remember, teach `/mb-update`.
