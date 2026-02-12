# Troubleshooting

Common issues and fixes for Claude Code + Main Branch.

---

## "command not found: claude"

Terminal doesn't know where Claude is installed. Add it to your PATH.

**Mac (zsh - default on modern Macs):**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

**Linux or older Mac (bash):**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

**Verify it worked:**
```bash
claude --version
```

---

## "Repository not found" / 404 Error

You don't have access to the vip repository yet.

**Fix:**
1. Share your GitHub username with Devon in Skool
2. Wait for confirmation that access was granted
3. Try cloning again

**Note:** Access is granted manually. Give it time.

---

## "Can't push to vip" / Permission Denied

This is expected behavior, not an error.

**vip is read-only.** You can pull updates but cannot push changes.

Your business data goes in YOUR OWN repo (created via `/setup`). That repo you can push to.

---

## Xcode Command Line Tools Popup (Mac)

If you see a popup about downloading "developer tools" or "Xcode Command Line Tools":

1. **Click Install** - You need these for Git operations
2. **Ignore the time estimate** - It says hours but usually takes minutes
3. **Wait for completion** - Don't cancel

**If you accidentally canceled:**
```bash
xcode-select --install
```

---

## GitHub Desktop: "Repository not found"

Same as the 404 error above. You need access first.

1. Share your GitHub username with Devon
2. Wait for confirmation
3. Try again in GitHub Desktop

---

## Skills Not Working

If skill prompts like `/start` or `/ads` aren't showing in the dropdown:

**Check 1: Does the local bridge exist?**
```bash
test -e .claude/skills/start && echo "START_BRIDGE_OK"
```

If missing, add compatibility links (without replacing local folders):
```bash
# Get vip path from settings
VIP_PATH=$(python3 -c "
import json, os
with open('.claude/settings.local.json') as f:
    dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
for d in dirs:
    if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
        print(d); break
")

# Create bridge links only for missing entries
mkdir -p .claude/skills .claude/lenses .claude/reference
for d in "$VIP_PATH"/.claude/skills/*; do
  [ -d "$d" ] || continue
  n=$(basename "$d")
  [ -e ".claude/skills/$n" ] || ln -s "$d" ".claude/skills/$n"
done
for p in "$VIP_PATH"/.claude/lenses/* "$VIP_PATH"/.claude/reference/*; do
  [ -e "$p" ] || continue
  base=$(basename "$p")
  parent=$(basename "$(dirname "$p")")
  [ -e ".claude/$parent/$base" ] || ln -s "$p" ".claude/$parent/$base"
done
```

**Why this bridge?** It preserves project-local custom skills in `.claude/skills/` while adding missing vip entries when discovery is inconsistent.

**Check 2: Is vip loaded as an additional directory?**
```bash
cat .claude/settings.local.json
```

You should see vip listed under `permissions.additionalDirectories`. If not, run `/setup`.

**Check 3: Did you start in your business repo?**

```bash
cd ~/Documents/GitHub/[your-business]
claude
/start
```

**Check 4: None of the above?** Run `/setup` — it creates `settings.local.json` and missing bridge links.

**After fixing:** Close and reopen Claude (`Ctrl+C`, then `claude`) for skill changes to take effect.

---

## "Cannot edit files outside allowed directories"

This is common in sandboxed tools (like Conductor workspaces). It means Claude can only edit files inside the current workspace folder.

**What this means in plain English:** Claude is working in one folder "bubble" and can't directly write to files outside that bubble with the normal write tool.

**Important context:** In a regular terminal Claude session (not sandboxed by an IDE/workspace tool), Claude will often prompt for permission and continue. This error is most common in stricter sandboxed environments.

**Fix options:**
1. **Best:** Start Claude in the repo you want to edit (or switch workspace to that repo)
2. **Fallback:** Use terminal commands to write files in the target path

**Recommended for beginners:** Use option 1 whenever possible. It's easier to review and less error-prone.

**If you're in Conductor:** open a workspace rooted at the target repo, then re-run `/setup` or `/start`.

---

## Context Feels "Off" or Claude Forgot Things

Claude's context decays as conversations get longer. The CLAUDE.md instructions fade.

**Fix:** Run a slash command to reload fresh instructions.

Good commands for refreshing context:
- `/start` - Reloads and routes
- `/think` - For research/decisions
- `/help` - For questions

---

## MCP Not Working (Apify, etc.)

### "apify not found" in /mcp

MCP wasn't installed correctly. Re-run the setup:

```bash
claude mcp add apify -e APIFY_TOKEN=your_token_here --scope user -- npx -y @apify/actors-mcp-server
```

**Important:** Use `--scope user` so it's saved globally.

### "Invalid token" errors

Check your token at apify.com → Settings → API & Integrations. Copy the default token (don't create a new one).

### MCP installed but not showing

MCPs only load at startup. Restart Claude:

```bash
/exit
claude --continue
```

Then type `/mcp` to verify it appears.

### Permission prompts every time

When Claude first uses an MCP, hit `2` to "always allow" instead of `1` for one-time.

---

## Resuming a Session

If you closed Terminal or need to pick up where you left off:

```bash
claude --continue
```

This resumes your previous conversation with full context.

---

## Business Repo Not Loading Automatically

If `/start` doesn't load your business repo:

**Check machine-local config:**
```bash
cat ~/.config/vip/local.yaml
```

Should show:
```yaml
vip_path: /Users/yourname/Documents/GitHub/vip
default_repo: /Users/yourname/Documents/GitHub/your-business
recent_repos:
  - /Users/yourname/Documents/GitHub/your-business
user:
  name: "Your Name"
  experience: intermediate  # beginner | intermediate | advanced
```

**Check repo config (team settings):**
```bash
cat /path/to/your/repo/.vip/config.yaml
```

**Common fixes:**

| Problem | Solution |
|---------|----------|
| No `~/.config/vip/local.yaml` | Run `/start` — it will discover your repo and offer to save the path |
| Path is wrong | Run `/start` and select your repo when prompted, say "yes" to save |
| Folder was moved | Delete `~/.config/vip/local.yaml` and run `/start` again |
| No `.vip/config.yaml` in repo | Run `/start` — it will offer to create config for faster startups |

**Migration from old system:**
If you have an old `~/.claude/settings.json` with `business_repo_path`, `/start` will detect it and offer to migrate to the new config system. The new architecture uses `.claude/settings.local.json` (in your business repo) to load vip as an additional directory.

---

## Config System Explained

See `start/references/config-system.md` for the full canonical reference on the config system.

**Two files, different purposes:**

| File | Location | What's In It | Git-tracked? |
|------|----------|--------------|--------------|
| `local.yaml` | `~/.config/vip/` | Default repo, your name, your experience level | No (personal) |
| `config.yaml` | `[repo]/.vip/` | Team settings, MCP requirements, skill defaults | Yes (shared) |

**Why the split?**
- Multiple people can work on the same business repo
- Alice can be "advanced" while Bob is "beginner"
- Team settings (infrastructure, MCPs) travel with the repo
- Personal settings stay on your machine

**To reset everything:**
```bash
rm ~/.config/vip/local.yaml
# Then run /start — it will rediscover and let you reconfigure
```

---

## Git Conflicts in vip

You shouldn't have any uncommitted changes in vip.

If you do, resolve them using the canonical VIP resolution to find your vip path:
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

# Then clean and pull (WARNING: discards any local changes in vip)
if [ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ]; then
  git -C "$VIP_PATH" checkout .
  git -C "$VIP_PATH" pull origin main
fi
```

**Warning:** `git checkout .` discards all uncommitted changes in vip. This is safe because vip is read-only — you shouldn't have local changes there. If you do, move them to your business repo first.
