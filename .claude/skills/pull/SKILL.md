---
name: pull
description: Quick update Main Branch. Use when user wants to update the engine without running /start, says "pull", "update", or "get latest", wants to see what changed, or after Devon announces features in Skool. Note that /start updates automatically, so skip /pull if running /start next.
---

# Pull

Update the Main Branch engine.

---

## What It Does

Resolves the Main Branch engine path and updates that install — NOT from the current working directory (which is your business repo). pipx installs upgrade the `mainbranch` package; clone-based installs run `git pull`.

### Step 1: Resolve VIP Path

For the canonical bash + python3 resolver (settings.local.json first, ~/.config/vip/local.yaml fallback), see **[../../reference/vip-path-resolution.md](../../reference/vip-path-resolution.md)**.

### Step 2: Update Main Branch

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

### Step 3: Pull Business Repo (if it has a remote)

```bash
git pull origin main 2>&1
```

### Handling Results

**Main Branch updated:** "Updated Main Branch and refreshed skill links." — then read the CHANGELOG and surface unread entries (see "What's New from CHANGELOG" below).

**Main Branch current:** "Engine already up to date." — still surface unread CHANGELOG entries (the user might not have run /start since the last release landed).

**Main Branch path not found:** "Couldn't find Main Branch. Run `mb skill link --repo .`, then restart Claude."

**Business repo updated:** "Also pulled updates for [repo-name]."

**Business repo current or local-only:** Say nothing.

**Error:** "Couldn't update: [error]. If you installed with pipx, try `pipx upgrade mainbranch`. If you cloned the engine repo, open GitHub Desktop → select mainbranch → click 'Fetch origin'."

---

## What's New from CHANGELOG

After a successful pull, surface unread CHANGELOG entries so the user knows what landed.

### Read the current engine version

```bash
ENGINE_VERSION=$(python3 -c "
import re, sys
try:
    body = open('$VIP_PATH/CHANGELOG.md').read()
    # First versioned heading after the [Unreleased] block
    m = re.search(r'^## \[(\d+\.\d+\.\d+[^\]]*)\]', body, re.M)
    print(m.group(1) if m else '')
except Exception:
    print('')
" 2>/dev/null)
```

### Read the user's last seen version

```bash
LAST_SEEN=$(python3 -c "
import os
try:
    import yaml
    with open(os.path.expanduser('~/.config/vip/local.yaml')) as f:
        cfg = yaml.safe_load(f) or {}
    print(cfg.get('last_seen_version', '') or '')
except Exception:
    print('')
" 2>/dev/null)
```

### Compare and surface unread entries

If `ENGINE_VERSION` is set and `LAST_SEEN != ENGINE_VERSION`, extract the matching CHANGELOG section (and any newer ones between `LAST_SEEN` and `ENGINE_VERSION`) and render as a banner:

```
Pulled latest engine updates.

─── What's new in <ENGINE_VERSION> ───
<First 4-6 lines of the matching section's most prominent bullets,
trimmed for screen. Skip "Notes / follow-ups" sub-sections.>
──────────────────────────────────────

(Run /start to begin, or run a named skill directly.)
```

If no unread entries (`LAST_SEEN == ENGINE_VERSION` or both empty): just print "Pulled latest engine updates." with nothing after.

### Mark as seen

After display, update `~/.config/vip/local.yaml`:

```bash
python3 -c "
import os, yaml
path = os.path.expanduser('~/.config/vip/local.yaml')
os.makedirs(os.path.dirname(path), exist_ok=True)
try:
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
except FileNotFoundError:
    cfg = {}
cfg['last_seen_version'] = '$ENGINE_VERSION'
with open(path, 'w') as f:
    yaml.safe_dump(cfg, f)
"
```

The user's `last_seen_version` is also bumped automatically when `/start` surfaces the same banner — only one of the two needs to fire per pull.

### Honour user dismiss

If the user types "dismiss" / "seen" / "got it" after the banner appears, also bump `last_seen_version` to the current engine version. The banner stops surfacing on subsequent runs until a new release lands.

---

## References

- [../../reference/vip-path-resolution.md](../../reference/vip-path-resolution.md) — canonical vip-path resolver
- [../../../CHANGELOG.md](../../../CHANGELOG.md) — release notes (the source surfaced as "what's new")
