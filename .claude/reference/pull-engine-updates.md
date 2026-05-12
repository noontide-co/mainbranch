# Main Branch Update Check

Canonical command for checking or applying Main Branch updates at the start of
any skill invocation. CWD is the business folder. **Do not silently swallow
failures.** Users on stale code get broken features.

`mb update` owns the install-mode mechanics. It detects pipx vs source
checkouts, runs the correct update command, and refreshes skill links for the
business folder.

```bash
mb update --repo "${REPO_PATH:-.}" --json 2>&1
```

## Handle the Result

| Result | What to say |
|--------|-------------|
| JSON `"ok": true`, old_version == new_version | Say nothing |
| JSON `"ok": true`, old_version != new_version | "Updated Main Branch and refreshed skill links." |
| Invalid JSON or missing engine root | "Couldn't find Main Branch. Run `mb skill link --repo .`, then restart Claude." |
| JSON `"ok": false` or command failure | Show the warning below |

## If Update Fails - Show This Warning

> "I wasn't able to update Main Branch. This means you may be running on an old version and missing new features.
>
> Common fixes:
> 1. Run `mb update --check --repo .` to see which install path Main Branch detects
> 2. Run `mb update --repo .` again after fixing the reported error
> 3. **Network issue?** Check your internet connection
>
> You can continue, but some features may not work as expected."

**Do not skip this warning.** A user running stale Main Branch is the #1 cause of "why doesn't X work" support questions.

---

## Business Folder Remote Check (start skill only)

Once the business folder is confirmed, check whether it has remote updates from
`REPO_PATH`:

```bash
if git -C "$REPO_PATH" remote get-url origin >/dev/null 2>&1; then
  git -C "$REPO_PATH" pull origin main 2>&1
else
  echo "NO_REMOTE"
fi
```

### Handle the Result

| Result | What to say |
|--------|-------------|
| "Already up to date." | Say nothing |
| "Updating..." / files changed | "Updated local business files from GitHub for [folder-name]." |
| "NO_REMOTE" | Say nothing — local-only repo, no remote configured |
| Any other error | Show the warning below |

### If The Remote Check Fails

> "Couldn't check GitHub updates for [folder-name]. You may be working on older reference files.
>
> Try: Open GitHub Desktop -> select [folder-name] -> click 'Fetch origin'"

### Why This Check Exists

- `mb update` keeps the installed CLI and skills current.
- The business folder remote check keeps the operator's own business files current.
