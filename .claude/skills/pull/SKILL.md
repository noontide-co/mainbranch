---
name: pull
description: Quick update Main Branch. Use when user wants to update the engine without running /start, says "pull", "update", or "get latest", wants to see what changed, or after Devon announces features in Skool. Note that /start updates automatically, so skip /pull if running /start next.
---

# Pull

Update the Main Branch engine.

---

## What It Does

Runs `mb update` for the mechanical engine refresh. The CLI detects whether Main Branch was installed with pipx or from a clone, updates that install, and refreshes skill links for the current business repo. This skill keeps ownership of the "what's new" narrative after the CLI step completes.

### Step 1: Resolve VIP Path

For the canonical bash + python3 resolver (settings.local.json first, ~/.config/vip/local.yaml fallback), see **[../../reference/vip-path-resolution.md](../../reference/vip-path-resolution.md)**.

### Step 2: Update Main Branch

```bash
mb update --repo "${REPO_PATH:-.}" --json 2>&1
```

### Step 3: Pull Business Repo (if it has a remote)

```bash
git pull origin main 2>&1
```

### Handling Results

**Main Branch updated:** If the JSON result has `"ok": true`, say "Updated Main Branch and refreshed skill links." — then read the CHANGELOG and surface unread entries (see "What's New from CHANGELOG" below).

**Main Branch current:** If old_version and new_version match, "Engine already up to date." — still surface unread CHANGELOG entries (the user might not have run /start since the last release landed).

**Main Branch path not found:** If the JSON result is not valid or reports an engine-root error, say "Couldn't find Main Branch. Run `mb skill link --repo .`, then restart Claude."

**Business repo updated:** "Also pulled updates for [repo-name]."

**Business repo current or local-only:** Say nothing.

**Error:** "Couldn't update: [error]. Try `mb update --check --repo .` to see which install path Main Branch detects."

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
