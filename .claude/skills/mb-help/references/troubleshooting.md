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

Use the public Main Branch engine repo:

**Fix:**
1. Open `https://github.com/noontide-co/mainbranch` in your browser
2. Confirm the URL is typed exactly in GitHub Desktop or terminal
3. Try cloning again

**Note:** The engine repo is public. A 404 usually means the old URL is being used or the URL was mistyped.

---

## "Can't push to Main Branch" / Permission Denied

This is expected behavior, not an error.

**Main Branch is read-only for most users.** You can pull updates but cannot push changes.

Your business data goes in YOUR OWN repo (created by `mb onboard` or `/mb-setup`). That repo you can push to.

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

Same as the 404 error above. Use the public repo URL:

```text
https://github.com/noontide-co/mainbranch
```

---

## Skills Not Working

If skill prompts like `/mb-start` or `/mb-ads` aren't showing in the dropdown:

**Check 1: Does the local bridge exist?**
```bash
test -e .claude/skills/mb-start && echo "START_BRIDGE_OK"
```

If missing, run the noob-safe repair path from the business repo:

```bash
mb skill link --repo .
mb skill repair --repo .
mb doctor
```

If the `mb` CLI is unavailable and you are repairing an old clone-based setup by hand, add skill compatibility links without replacing local folders. First resolve `$ENGINE_PATH` per **[vip-path-resolution.md](vip-path-resolution.md)**, then:

```bash
# Create bridge links only for missing entries
mkdir -p .claude/skills
for d in "$ENGINE_PATH"/.claude/skills/*; do
  [ -d "$d" ] || continue
  n=$(basename "$d")
  [ -e ".claude/skills/$n" ] || ln -s "$d" ".claude/skills/$n"
done
```

**Why this bridge?** It preserves project-local custom skills in `.claude/skills/` while adding missing Main Branch entries when discovery is inconsistent.

Old clone-based repos may also have `.claude/lenses/` or `.claude/reference/`
symlinks. Treat those as legacy link dirs; `mb doctor repair` can move stale
ones into `.mb/backups/`.

**Check 2: Is Main Branch loaded as an additional directory?**
```bash
cat .claude/settings.local.json
```

You should see the active Main Branch engine path listed under `permissions.additionalDirectories`. If not, run `mb skill link --repo .`.

**Check 3: Did you start in your business repo?**

```bash
cd ~/Documents/GitHub/[your-business]
claude
/mb-start
```

**Check 4: None of the above?** Run `/mb-setup` — it creates `settings.local.json` and missing bridge links.

**After fixing:** Close and reopen Claude (`Ctrl+C`, then `claude`) for skill changes to take effect.

---

## Conductor: Skills Not Showing

Conductor workspaces are isolated; Claude doesn't know where Main Branch is unless you tell it.

**The fix:** Run `mb skill link --repo .` in the workspace when possible. If you need a Pre-Agent (PA) config script, use one that creates the bridge links plus `settings.local.json` before Claude starts.

See [conductor-setup.md](conductor-setup.md) for the full script and setup walkthrough.

**Quick version:**
1. Find your Main Branch engine path
2. Add the PA config script to your Conductor workspace
3. The script creates symlinks + settings, then exits
4. Start the agent again — skills appear

**After fixing:** Skills only load at startup. If you added bridge links mid-session, you need to restart Claude.

---

## "Cannot edit files outside allowed directories"

This is common in sandboxed tools (like Conductor workspaces). It means Claude can only edit files inside the current workspace folder.

**What this means in plain English:** Claude is working in one folder "bubble" and can't directly write to files outside that bubble with the normal write tool.

**Important context:** In a regular terminal Claude session (not sandboxed by an IDE/workspace tool), Claude will often prompt for permission and continue. This error is most common in stricter sandboxed environments.

**Fix options:**
1. **Best:** Start Claude in the repo you want to edit (or switch workspace to that repo)
2. **Fallback:** Use terminal commands to write files in the target path

**Recommended for beginners:** Use option 1 whenever possible. It's easier to review and less error-prone.

**If you're in Conductor:** open a workspace rooted at the target repo, then re-run `/mb-setup` or `/mb-start`.

---

## Context Feels "Off" or Claude Forgot Things

Claude's context decays as conversations get longer. The CLAUDE.md instructions fade.

**Fix:** Run a slash command to reload fresh instructions.

Good commands for refreshing context:
- `/mb-start` - Reloads and routes
- `/mb-think` - For research/decisions
- `/mb-help` - For questions

---

## Turn Friction Into a GitHub Issue

If a Main Branch command, skill, setup step, or doc gap is reproducibly confusing
after the repair path above, help the operator create a privacy-safe public issue
draft. Do not submit it for them.

**Bug:**
```bash
mb issue draft bug --command "mb doctor" --what-happened "..." --expected "..."
```

**Feature gap:**
```bash
mb issue draft feature --problem "..." --proposal "..."
```

**Question:**
```bash
mb issue draft question --question "..." --context "..." --tried "..."
```

Drafts go under `.mb/issue-drafts/` and are gitignored. Tell the operator to
review the draft for private business data, customer/member details, secrets,
account IDs, screenshots, and local-only paths before running:

```bash
mb issue open .mb/issue-drafts/[draft].md --yes
```

Use this only for Main Branch product friction that belongs in the public issue
tracker. Operator-specific business strategy belongs in the community or their
private repo, not public GitHub.

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

If `/mb-start` doesn't load your business repo:

**Check legacy machine-local config:**
```bash
cat ~/.config/vip/local.yaml
```

Should show:
```yaml
vip_path: /Users/yourname/Documents/GitHub/mainbranch
default_repo: /Users/yourname/Documents/GitHub/your-business
recent_repos:
  - /Users/yourname/Documents/GitHub/your-business
user:
  name: "Your Name"
  experience: intermediate  # beginner | intermediate | advanced
```

**Audit legacy repo config/state if present:**
```bash
mb doctor repair --repo /path/to/your/repo --plan --json
```

**Common fixes:**

| Problem | Solution |
|---------|----------|
| No `~/.config/vip/local.yaml` | Run `/mb-start` — it will discover your repo and can save the path |
| Path is wrong | Run `/mb-start` and select your repo when prompted, say "yes" to save |
| Folder was moved | Delete `~/.config/vip/local.yaml` and run `/mb-start` again |
| `.vip/config.yaml` exists | Audit it with `mb doctor repair --plan --json`; do not treat it as current team settings |

**Migration from old system:**
If you have an old `~/.claude/settings.json` with `business_repo_path`, run `mb skill link --repo .`, then `mb start --json`. The current architecture uses `.claude/settings.local.json` in your business repo to load the active Main Branch engine as an additional directory.

---

## Config System Explained

See `mb-start/references/config-system.md` for the current legacy-config cleanup guidance.

**Legacy files, different purposes:**

| File | Location | What's In It | Git-tracked? |
|------|----------|--------------|--------------|
| `local.yaml` | `~/.config/vip/` | Default repo, your name, your experience level | No (personal) |
| `config.yaml` | `[repo]/.vip/` | Old mixed config/state that needs audit before reuse | Maybe old repos tracked it |

**Why the split?**
- Multiple people can work on the same business repo
- Alice can be "advanced" while Bob is "beginner"
- Current provider/readiness metadata should come from `mb connect`, generated
  repo instructions, and durable business files, not `.vip/config.yaml`
- Personal settings stay on your machine

**To reset everything:**
```bash
rm ~/.config/vip/local.yaml
# Then run /mb-start — it will rediscover and let you reconfigure
```

---

## Git Conflicts in an Old Engine Clone

Most users should update through `/mb-update` or `mb update`; raw package
commands are only bootstrap fallbacks for old installs where `mb update` is not
available. If you still have an old clone-based engine install, keep business
work out of that clone.

From the business repo, prefer:

```bash
mb update --repo .
mb skill link --repo .
mb doctor
```

If you deliberately maintain a clone-based engine install, resolve `$ENGINE_PATH` per **[vip-path-resolution.md](vip-path-resolution.md)** and inspect it manually before pulling:

```bash
if [ -n "$ENGINE_PATH" ] && [ -f "$ENGINE_PATH/.claude/skills/mb-start/SKILL.md" ]; then
  git -C "$ENGINE_PATH" status --short
  git -C "$ENGINE_PATH" pull origin main
fi
```

If `git status --short` shows local changes, do not discard them blindly. Move business content to your business repo, or keep engine contribution work on its own branch.
