# Pull Engine Updates

Canonical command for pulling latest Main Branch updates at the start of any skill invocation. CWD is the business repo. **Do NOT silently swallow failures.** Users on stale code get broken features.

`mb update` owns the install-mode mechanics. It detects pipx vs clone installs, runs the correct update command, and refreshes skill links for the business repo.

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

## If Pull Fails — Show This Warning

> "I wasn't able to pull the latest Main Branch updates. This means you may be running on an old version and missing new features.
>
> Common fixes:
> 1. Run `mb update --check --repo .` to see which install path Main Branch detects
> 2. Run `mb update --repo .` again after fixing the reported error
> 3. **Network issue?** Check your internet connection
>
> You can continue, but some features may not work as expected."

**Do not skip this warning.** A user running stale vip is the #1 cause of "why doesn't X work" support questions.

---

## Pull Business Repo Updates (start skill only)

Once business repo is confirmed, pull its latest updates from `REPO_PATH`:

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
| "Updating..." / files changed | "Pulled latest updates for [repo-name]." |
| "NO_REMOTE" | Say nothing — local-only repo, no remote configured |
| Any other error | Show the warning below |

### If Pull Fails (and Repo Has a Remote)

> "Couldn't pull updates for [repo-name]. You may be working on older reference files.
>
> Try: Open GitHub Desktop → select [repo-name] → click 'Fetch origin'"

### Why Both Repos

- Main Branch engine → new skills, playbooks, compliance frameworks
- Business repo → your reference files, decisions, research
