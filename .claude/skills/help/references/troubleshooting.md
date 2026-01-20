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

If slash commands like `/start` or `/ad-static` aren't recognized:

**Check 1: Are you in vip?**
```bash
pwd
ls .claude/skills
```

If not in vip, skills won't be available.

**Check 2: Did you add vip?**

If you started in your business repo, add vip:
```
/add-dir ~/Documents/GitHub/vip
```

**Best practice:** Always start in vip, run `/start`. It handles everything.

---

## Context Feels "Off" or Claude Forgot Things

Claude's context decays as conversations get longer. The CLAUDE.md instructions fade.

**Fix:** Run a slash command to reload fresh instructions.

Good commands for refreshing context:
- `/start` - Reloads and routes
- `/think` - For research/decisions
- `/help` - For questions

---

## Business Repo Not Loading Automatically

If `/start` doesn't load your business repo:

**Check ~/.claude/settings.json:**
```json
{
  "business_repo_path": "/Users/yourname/Documents/GitHub/your-business"
}
```

**Common fixes:**

| Problem | Solution |
|---------|----------|
| File doesn't exist | Tell Claude your business repo path when running /start |
| Path is wrong | Update the path in ~/.claude/settings.json |
| Folder was moved | Update to new location |

---

## Git Conflicts in vip

You shouldn't have any uncommitted changes in vip.

If you do:
```bash
cd ~/Documents/GitHub/vip
git status
git checkout .  # Discards local changes
git pull origin main
```

**Note:** vip is read-only. Any changes you made there should move to your business repo.
