# Pull Engine Updates

Canonical bash for pulling latest Main Branch updates at the start of any skill invocation. CWD is the business repo — resolve the engine path first. **Do NOT silently swallow failures.** Users on stale code get broken features.

For the canonical resolver (bash + python3, settings.local.json first, ~/.config/vip/local.yaml fallback) see **[vip-path-resolution.md](vip-path-resolution.md)**. Run that snippet, then:

```bash
if [ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ]; then
  if git -C "$VIP_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$VIP_PATH" pull origin main 2>&1
  elif command -v pipx >/dev/null 2>&1 && pipx list --short 2>/dev/null | grep -q '^mainbranch '; then
    pipx upgrade mainbranch 2>&1
    mb skill link --repo "${REPO_PATH:-.}" 2>&1
  else
    echo "NO_UPDATE_MODE"
  fi
else
  echo "NO_ENGINE_PATH"
fi
```

## Handle the Result

| Result | What to say |
|--------|-------------|
| "Already up to date." | Say nothing |
| "upgraded package mainbranch" / "upgraded shared libraries" | "Updated Main Branch and refreshed skill links." |
| "Updating..." / files changed | "Pulled latest engine updates." |
| `NO_UPDATE_MODE` | "Main Branch is linked, but I couldn't tell how to update it. Try `pipx upgrade mainbranch` if you installed with pipx, or pull the engine repo in GitHub Desktop if you cloned it." |
| `NO_ENGINE_PATH` / VIP_PATH empty | "Couldn't find Main Branch. Run `mb skill link --repo .`, then restart Claude." |
| Any error (auth, network) | Show the warning below |

## If Pull Fails — Show This Warning

> "I wasn't able to pull the latest Main Branch updates. This means you may be running on an old version and missing new features.
>
> Common fixes:
> 1. **Installed with pipx?** Run `pipx upgrade mainbranch`, then `mb skill link --repo .`
> 2. **Using a cloned engine repo?** Open GitHub Desktop → select mainbranch → click 'Fetch origin'
> 3. **Network issue?** Check your internet connection
>
> You can continue, but some features may not work as expected."

**Do not skip this warning.** A user running stale vip is the #1 cause of "why doesn't X work" support questions.

---

## Step 0.5: Pull Business Repo Updates (start skill only)

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
