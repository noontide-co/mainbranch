---
name: pull
description: Quick pull latest vip updates from GitHub. Use when user wants to update vip without running /start, says "pull", "update", or "get latest", wants to see what changed, or after Devon announces features in Skool. Note that /start pulls automatically, so skip /pull if running /start next.
---

# Pull

Pull latest vip engine updates from GitHub.

---

## What It Does

Resolves the vip path and pulls updates there — NOT from the current working directory (which is your business repo).

### Step 1: Resolve VIP Path

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
```

### Step 2: Pull VIP

```bash
# Pull if found and valid
[ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ] && \
  git -C "$VIP_PATH" pull origin main 2>&1
```

### Step 3: Pull Business Repo (if it has a remote)

```bash
git pull origin main 2>&1
```

### Handling Results

**VIP updated:** "Pulled latest engine updates. Changes: [list]"

**VIP current:** "Engine already up to date."

**VIP path not found:** "Couldn't find vip. Run `/setup` to configure your vip path, or check `~/.config/vip/local.yaml`."

**Business repo updated:** "Also pulled updates for [repo-name]."

**Business repo current or local-only:** Say nothing.

**Error:** "Couldn't pull: [error]. Try: Open GitHub Desktop → select vip → click 'Fetch origin'."
