# Auto-Heal: Bridge Link Recovery

When a user launches Claude in their business repo and skills aren't showing, this file provides the self-repair logic. It's readable via `additionalDirectories` file access even when skills aren't discoverable.

---

## When This Runs

This runs in two places:

1. **Bootstrap path:** business repo `CLAUDE.md` points here when `/start` is missing.
2. **Main `/start` path:** when `/start` is invoked from vip, it resolves a selected business repo and runs this repair against that repo.

---

## Step 0: Set target repo

Always target the business repo explicitly:

```bash
REPO_PATH="[absolute-path-to-business-repo]"
test -d "$REPO_PATH" || echo "BAD_REPO_PATH"
```

If running directly inside the business repo, set:

```bash
REPO_PATH="$PWD"
```

---

## Step 1: Find vip path

```bash
VIP_PATH=$(REPO_PATH="$REPO_PATH" python3 -c "
import json, os
with open(os.path.join(os.environ['REPO_PATH'], '.claude/settings.local.json')) as f:
    dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
for d in dirs:
    if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
        print(d); break
" 2>/dev/null)
echo "VIP_PATH=$VIP_PATH"
```

If empty: `settings.local.json` is missing or doesn't point to vip. Tell the user to run `/setup` from vip, or manually create `REPO_PATH/.claude/settings.local.json`:

```json
{
  "permissions": {
    "additionalDirectories": ["/absolute/path/to/vip"]
  }
}
```

---

## Step 2: Create bridge links

```bash
mkdir -p "$REPO_PATH/.claude/skills" "$REPO_PATH/.claude/lenses" "$REPO_PATH/.claude/reference"

# Per-skill symlinks (preserves local custom skills)
for d in "$VIP_PATH"/.claude/skills/*/; do
  [ -d "$d" ] || continue
  n=$(basename "$d")
  [ -e "$REPO_PATH/.claude/skills/$n" ] || ln -s "$d" "$REPO_PATH/.claude/skills/$n"
done

# Per-entry lenses and reference
for p in "$VIP_PATH"/.claude/lenses/* "$VIP_PATH"/.claude/reference/*; do
  [ -e "$p" ] || continue
  base=$(basename "$p")
  parent=$(basename "$(dirname "$p")")
  [ -e "$REPO_PATH/.claude/$parent/$base" ] || ln -s "$p" "$REPO_PATH/.claude/$parent/$base"
done
```

---

## Step 3: Verify

```bash
test -e "$REPO_PATH/.claude/skills/start" && echo "HEAL_OK" || echo "HEAL_FAILED"
```

---

## Step 4: Tell the user

If HEAL_OK:
> "I've set up the skill bridge links. **Please restart Claude** (Ctrl+C, then `claude`) — skills like `/start` will appear in the dropdown on next launch."

If HEAL_FAILED:
> "Auto-repair failed. Check that vip is cloned locally and the path in `.claude/settings.local.json` is correct."

---

## Why this is needed

`additionalDirectories` in `settings.local.json` grants file access to vip but doesn't reliably trigger skill discovery in Claude Code v2.1.39. Bridge links (symlinks from `.claude/skills/[name]` to vip skill directories) make Claude discover skills as if they're local. This is a compatibility layer — if Anthropic fixes discovery from additional directories, these links become redundant but harmless.

---

## What the links look like

```
business-repo/.claude/
├── settings.local.json                              # Real file (canonical)
├── skills/                                          # Real directory
│   ├── start -> /path/to/vip/.claude/skills/start   # Symlink (bridge)
│   ├── ads -> /path/to/vip/.claude/skills/ads       # Symlink (bridge)
│   ├── my-local-skill/                              # Real dir (preserved)
│   └── ...
├── lenses/                                          # Real directory
│   ├── ftc-compliance.md -> /path/to/vip/...        # Symlink (bridge)
│   └── ...
└── reference/                                       # Real directory
    ├── compliance -> /path/to/vip/...               # Symlink (bridge)
    └── ...
```

Local custom skills are never overwritten — the `[ -e ] || ln -s` guard skips anything that already exists.
