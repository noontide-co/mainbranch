# Pull Engine Updates (Step -1)

Pull vip updates. CWD is the business repo — resolve vip path first. **Do NOT silently swallow failures.** Users on stale code get broken features.

```bash
# Canonical vip resolution (settings.local.json first — no extra deps)
VIP_PATH=$(python3 -c "
import json, os
try:
    with open('.claude/settings.local.json') as f:
        dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
    for d in dirs:
        if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
            print(d); break
except: print('')
" 2>/dev/null)

# Fallback: check ~/.config/vip/local.yaml (needs PyYAML)
if [ -z "$VIP_PATH" ] || [ ! -f "$VIP_PATH/.claude/skills/start/SKILL.md" ]; then
  VIP_PATH=$(python3 -c "
import os
try:
    import yaml
    with open(os.path.expanduser('~/.config/vip/local.yaml')) as f:
        print(yaml.safe_load(f).get('vip_path', ''))
except: print('')
" 2>/dev/null)
fi

# Pull if found and valid
[ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ] && \
  git -C "$VIP_PATH" pull origin main 2>&1
```

## Handle the Result

| Result | What to say |
|--------|-------------|
| "Already up to date." | Say nothing |
| "Updating..." / files changed | "Pulled latest engine updates." |
| VIP_PATH empty (not found) | "Couldn't find vip. Run `/setup` to configure, or check `~/.config/vip/local.yaml`." |
| Any error (auth, network) | Show the warning below |

## If Pull Fails — Show This Warning

> "I wasn't able to pull the latest Main Branch updates. This means you may be running on an old version and missing new features.
>
> Common fixes:
> 1. **GitHub Desktop not running?** Open it and make sure you're signed in
> 2. **Subscription inactive?** Check your Main Branch access in Skool
> 3. **Network issue?** Check your internet connection
> 4. **Try manually:** Open GitHub Desktop → select vip → click 'Fetch origin'
>
> You can continue, but some features may not work as expected."

**Do not skip this warning.** A user running stale vip is the #1 cause of "why doesn't X work" support questions.

---

## Step 0.5: Pull Business Repo Updates

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

- Engine (vip) → new skills, playbooks, compliance frameworks
- Business repo → your reference files, decisions, research
