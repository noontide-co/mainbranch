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

**VIP updated:** "Pulled latest engine updates." — then read `<vip_path>/.claude/announcements.md` and surface unseen, non-expired entries (per the format defined in announcements.md). Diff against `~/.config/vip/local.yaml:seen_announcements` so the user only sees what's actually new.

Render format when there are unseen announcements:

```
Pulled latest engine updates.

─── What's new ───
[NEW] <title>
<2-line body>
─────────────────

(Run /start to begin, or run the named skill directly.)
```

If no unseen announcements: just "Pulled latest engine updates." with nothing after.

**VIP current:** "Engine already up to date." — still surface unseen announcements (the user might not have run /start since vip last had a feature land).

**VIP path not found:** "Couldn't find vip. Run `/setup` to configure your vip path, or check `~/.config/vip/local.yaml`."

**Business repo updated:** "Also pulled updates for [repo-name]."

**Business repo current or local-only:** Say nothing.

**Error:** "Couldn't pull: [error]. Try: Open GitHub Desktop → select vip → click 'Fetch origin'."
