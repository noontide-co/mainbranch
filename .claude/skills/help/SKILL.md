---
name: help
description: |
  Answer questions about Main Branch and Claude Code. Use when:
  (1) User asks "how do I...", "what is...", "why does...", "explain..."
  (2) User is confused about the two-repo model, /add-dir, or skills
  (3) User encounters errors (command not found, repository not found)
  (4) User says "help", "I'm stuck", "I don't understand"
  (5) User asks about daily workflow or getting started

  Answers questions based on documented curriculum. Routes to other skills when appropriate.
---

# Help

Answer questions about Main Branch based on documented curriculum.

---

## How to Use

1. Read the user's question
2. Find the relevant topic below or in references/
3. Answer clearly and concisely
4. Route to appropriate skill if action is needed

---

## Quick Answers (Most Common Questions)

### "What are the two repos?"

**vip** = the engine (skills, templates, frameworks). Shared with everyone. You don't edit it.

**Your business repo** = your data (offer, audience, voice, proof). Yours alone. You own it.

Same engine + different data = different outputs for each business.

Think of it like Unity (game engine) + your game assets. The engine provides capabilities. Your assets make it yours.

### "What does 'working in vip' mean?"

It means you start Claude there. Why:
1. Skills live in vip. If you start elsewhere, skills may not be available.
2. Updates happen in vip. `/start` auto-pulls the latest.
3. It's the consistent starting point. Always works.

### "Do I need /add-dir every session?"

After the latest update: **No.**

Run `/start` from vip. It remembers your business repo path (stored in ~/.claude/settings.json) and loads it automatically.

One-time setup: Tell Claude your business repo path when you first run `/start`.

### "Why does context decay?"

Claude Code reads CLAUDE.md at session start. That context is strongest at the beginning and fades as the conversation gets longer and compacts.

**Solution:** Use slash commands regularly (`/start`, `/think`, `/ad-static`). Each command reloads fresh skill instructions.

### "What can Claude do?"

Claude can work with ANY file on your computer. Drag files in, share paths, paste text. Possibilities are endless.

For Main Branch, we focus on two folders (vip + your business repo) so skills can reliably use your business context.

---

## Troubleshooting

### "command not found: claude"

Terminal doesn't know where Claude is installed.

**Mac (zsh):**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

**Linux/older Mac (bash):**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

### "Repository not found" / 404 error

You don't have access yet. Share your GitHub username with Devon in Skool and wait for confirmation.

### "Can't push to vip"

Expected. vip is read-only. Your business data goes in your own repo (created via `/setup`).

### Xcode Command Line Tools popup (Mac)

Click Install. Needed for Git operations. The time estimate is wrong (says hours, takes minutes).

To reinstall: `xcode-select --install`

---

## Daily Workflow

```bash
cd ~/Documents/GitHub/vip
claude
/start
```

That's it. `/start` pulls updates, loads your business repo, routes you to the right skill.

---

## Skills Quick Reference

| Skill | What It Does |
|-------|--------------|
| `/start` | Entry point. Loads your business repo, routes to right skill |
| `/setup` | Create business repo from scratch (first-time users) |
| `/enrich` | Add context to existing repo |
| `/think` | Research topics, make decisions, update reference files |
| `/ad-static` | Generate image ad copy |
| `/ad-video-scripts` | Generate video ad scripts |
| `/ad-review` | Check ads for compliance |
| `/help` | Answer questions (this skill) |

---

## Routing

If user needs action, not just answers:

| User Need | Route To |
|-----------|----------|
| "Set up my repo" | `/setup` |
| "Add more context" | `/enrich` |
| "Research something" | `/think` |
| "Create ad copy" | `/ad-static` or `/ad-video-scripts` |
| "Check my ads" | `/ad-review` |

---

## Detailed References

For deeper explanations, see:

- [references/two-repos.md](references/two-repos.md) - Full explanation of engine + data model
- [references/troubleshooting.md](references/troubleshooting.md) - All error fixes
- [references/getting-started.md](references/getting-started.md) - Step-by-step setup guide
