# VIP Path Resolution

Canonical resolver for locating the mb-vip engine repo from a Claude Code session running inside a business repo. Used by `/start`, `/pull`, `/setup`, `/help` (troubleshooting), and any reference file that needs to read or pull engine-side files.

**Single source of truth.** Other reference files MUST link here rather than inline the snippet — the resolver semantics (and the order of fallbacks) need to stay in lockstep across the engine, and inline copies drift.

---

## Resolution order

1. **`.claude/settings.local.json` → `permissions.additionalDirectories`** (preferred). The directory passed to Claude Code via `additionalDirectories` is the canonical loading mechanism for vip in Phase 2. No external config needed; pure filesystem.
2. **`~/.config/vip/local.yaml` → `vip_path`** (fallback). For users who haven't yet migrated to `additionalDirectories`, or whose `settings.local.json` is missing / malformed.

The first valid path that contains `.claude/skills/start/SKILL.md` wins.

---

## The canonical bash + python3 snippet

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

After this block, `$VIP_PATH` is either a valid path to the mb-vip checkout or empty.

**Always validate before use:**

```bash
[ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ] && \
  <command using $VIP_PATH>
```

---

## Why two fallbacks (not one)

- **`additionalDirectories`** is the future-canonical mechanism — it requires zero extra config, works without PyYAML, and gives the harness explicit knowledge of the engine path. It's also the only mechanism Conductor / sandboxed environments support cleanly.
- **`~/.config/vip/local.yaml`** is the legacy mechanism that pre-dates `additionalDirectories`. We keep it as a fallback so existing users don't break on engine upgrades; it also serves users whose `settings.local.json` got reset by a tool like Claude Desktop's permission wipe.

The order matters: `settings.local.json` is harness-authoritative, `local.yaml` is best-guess. If both exist and disagree, the harness path wins because that's the path Claude Code is actually authorised to read.

---

## Failure modes and recovery

| Symptom | Likely cause | Recovery |
|---|---|---|
| `$VIP_PATH` is empty | Neither fallback resolved | Run `/setup` to configure, or add the engine path to `~/.config/vip/local.yaml` manually. |
| `$VIP_PATH` set but `.claude/skills/start/SKILL.md` missing | Stale config pointing at a deleted / renamed checkout | Re-run `/setup` to refresh, or update `~/.config/vip/local.yaml` to the current path. |
| `python3` not found | Minimal environment | Document as a setup prerequisite (every Main Branch user needs python3 in `$PATH`). |
| `yaml` import fails (fallback path only) | PyYAML not installed | The fallback is best-effort. Surface the underlying message and fall through to "no engine found" recovery. |
| Resolved path readable but `git pull` fails | Auth / network / locked-file | Surface the warning from `pull-engine-updates.md` ("Common fixes" — GitHub Desktop, Skool subscription, network). |

---

## When to inline vs. when to link

**Inline is correct only when:** the snippet needs a small modification for the local context (e.g., looking up a different skill's SKILL.md as the canary file, or following a different fallback chain).

**Link is correct when:** the snippet would be a verbatim copy. In that case, point at this file and let the caller's bash sub-shell run the snippet.

A reference file that inlines the resolver and *also* customises it should comment the customisation explicitly so it doesn't drift back into the canonical version on a future refactor.

---

## Callers that link to this file

- `.claude/skills/pull/SKILL.md`
- `.claude/skills/setup/references/cwd-detection.md`
- `.claude/skills/help/references/troubleshooting.md` (skills-not-working + git-conflicts sections)
- `.claude/reference/pull-engine-updates.md`

If you add a new caller, link here. Do not copy the snippet inline.
