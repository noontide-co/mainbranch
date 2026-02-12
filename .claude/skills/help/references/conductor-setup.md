# Conductor Setup

How to get Main Branch skills working in Conductor workspaces.

---

## Why Skills Don't Show Up in Conductor

Conductor creates isolated workspaces. Each workspace is its own folder — it doesn't automatically know where vip lives on your machine.

Main Branch skills live in the **vip repo** (the engine). For Claude to discover them in a Conductor workspace, two things need to exist:

1. **`settings.local.json`** — tells Claude where vip is (file access)
2. **Bridge symlinks** — make Claude discover skills as if they're local (skill dropdown)

Without these, Claude opens in your workspace and sees no skills. No `/start`, no `/ads`, nothing.

---

## The Fix: Pre-Agent (PA) Config Script

Conductor has a **Pre-Agent config** — a script that runs before Claude starts in a workspace. This is where you set up the vip connection.

### The Script

```bash
for skill in ads end help organic pull setup site start think vsl wiki; do
  target="/absolute/path/to/vip/.claude/skills/$skill"
  link=".claude/skills/$skill"
  [ -d "$target" ] && [ ! -e "$link" ] && ln -s "$target" "$link" || true
done
mkdir -p .claude
cat > .claude/settings.local.json << 'EOF'
{
  "permissions": {
    "additionalDirectories": [
      "/absolute/path/to/vip"
    ]
  }
}
EOF
exit
```

**Replace `/absolute/path/to/vip`** with the actual path to your vip clone. Common locations:

| OS | Typical Path |
|----|-------------|
| Mac (GitHub Desktop) | `~/Documents/GitHub/mb-vip` or `~/Documents/GitHub/vip` |
| Mac (manual clone) | `~/projects/vip` or wherever you cloned it |
| Linux | `~/repos/vip` or `~/Documents/GitHub/vip` |

### What Each Part Does

1. **The `for` loop** — Creates symlinks from the workspace's `.claude/skills/` to each vip skill directory. The `[ ! -e "$link" ]` guard means it won't overwrite existing local skills.

2. **`settings.local.json`** — Tells Claude that vip is an additional directory it can read from. This gives Claude access to lenses, compliance docs, and reference files inside vip.

3. **`exit`** — Closes the Claude session so it restarts fresh with skills loaded. Skills are only discovered at startup — adding symlinks mid-session doesn't make them appear.

### Finding Your vip Path

If you're not sure where vip is:

```bash
# Check if you cloned it with GitHub Desktop
ls ~/Documents/GitHub/mb-vip 2>/dev/null && echo "Found: ~/Documents/GitHub/mb-vip"
ls ~/Documents/GitHub/vip 2>/dev/null && echo "Found: ~/Documents/GitHub/vip"

# Or search for it
find ~/ -name "CLAUDE.md" -path "*/vip/*" -maxdepth 4 2>/dev/null
```

---

## Setting Up the PA Config

### Step by Step

1. **Open Conductor**
2. **Create or select a workspace** for your business repo
3. **Find the PA (Pre-Agent) config** for that workspace
4. **Paste the script above** (with your actual vip path)
5. **Start the agent** — the script runs first, creates the links, then exits
6. **Start the agent again** — now skills show up in the dropdown

### Per-Workspace

The PA config is per-workspace. If you create a new workspace, you need to add the script there too. Same script, same vip path.

---

## Troubleshooting

### Skills still don't appear after running the script

1. **Did Claude restart?** The script ends with `exit`. Start a new session — skills only load at startup.
2. **Is the vip path correct?** Check that the path in the script actually contains `.claude/skills/start/SKILL.md`.
3. **Are symlinks created?** Run `ls -la .claude/skills/` — you should see arrows (`->`) pointing to vip.

### "Cannot edit files outside allowed directories"

This is Conductor's sandbox. The PA script handles this by using `ln -s` (which creates links inside the workspace). The `settings.local.json` grants read access to vip. If you still hit this error during a session, it means you're trying to write to a path outside the workspace — which is expected. Your business files should be inside the workspace.

### Symlinks show as broken

The vip path in the script doesn't match where vip actually lives. Verify:

```bash
ls /absolute/path/to/vip/.claude/skills/start/SKILL.md
```

If that file doesn't exist, your path is wrong.

### New skills added to vip don't appear

When Devon adds new skills to vip, your PA script's skill list may be outdated. Update the `for skill in ...` line to include the new skill name. Or replace it with a dynamic version:

```bash
for d in /absolute/path/to/vip/.claude/skills/*/; do
  [ -d "$d" ] || continue
  skill=$(basename "$d")
  link=".claude/skills/$skill"
  [ -e "$link" ] || ln -s "$d" "$link"
done
```

This automatically picks up any new skills from vip.

---

## Why Not Just Use Terminal?

You can. Running `cd ~/Documents/GitHub/my-business && claude` in a regular terminal works perfectly — `/setup` and `/start` handle all the vip linkage automatically.

Conductor adds value when you want to run **multiple agents in parallel** on different tasks. The tradeoff is the one-time PA config setup per workspace.

---

## Quick Reference

| What | Where |
|------|-------|
| PA config script | Conductor workspace settings |
| vip path | Your local vip clone (e.g., `~/Documents/GitHub/mb-vip`) |
| Bridge links | `.claude/skills/` in the workspace (symlinks to vip) |
| File access | `.claude/settings.local.json` → `additionalDirectories` |
| Skills load | Only at Claude startup (not mid-session) |
