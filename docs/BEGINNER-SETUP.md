# Beginner Setup Guide

Quick setup for Claude Code + Main Branch. For the full curriculum with videos and detailed walkthroughs, see the Skool classroom.

---

## Prerequisites

1. **GitHub account** - [github.com/signup](https://github.com/signup)
2. **Repository access** - Share your GitHub username with Devon in Skool, wait for confirmation
3. **Claude subscription** - Pro ($20/mo) or Max ($100-200/mo) at [claude.ai](https://claude.ai)

---

## Quick Setup (5 Steps)

### 1. Install GitHub Desktop

Download from [desktop.github.com](https://desktop.github.com). Sign in with your GitHub account.

### 2. Install Claude Code

**Mac:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://claude.ai/install.ps1 | iex
```

### 3. Clone vip

In GitHub Desktop: **File → Clone Repository → GitHub.com tab → select `mainbranch-ai/vip`**

### 4. Open Terminal in vip Folder

**Mac:** Open Terminal, type `cd `, drag the vip folder from Finder into Terminal, press Enter.

**Windows:** Right-click inside the vip folder → "Open in Terminal"

### 5. Start Claude

```bash
claude
```

Then type `/start` and follow the prompts.

---

## Daily Workflow (After Setup)

Every time you use Main Branch:

```bash
cd ~/Documents/GitHub/vip
claude
/start
```

That's it. `/start` loads your business repo and routes you to the right skill.

---

## Common Issues

### "command not found: claude"

Your terminal doesn't know where Claude is installed. Run:

**Mac:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

**Linux/older Mac:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

### "Repository not found" / 404

You don't have access yet. Share your GitHub username with Devon and wait for confirmation.

### Xcode Command Line Tools (Mac)

If you see a popup about developer tools, click Install. You'll need it for Git operations. The time estimate is usually wrong (says hours, takes minutes).

To reinstall if you canceled: `xcode-select --install`

### Can't push to vip

Expected. vip is read-only. Your business data goes in your own repo (created via `/setup`).

---

## The Two Repos

```
vip/                    your-business/
├── Skills              ├── Your offer
├── Templates           ├── Your audience
├── Frameworks          ├── Your voice
└── (engine, shared)    └── (your data)
```

Same engine + different data = outputs tailored to each business.

**Important:** Your business repo is a precision instrument, not a dumping ground. Every file should earn its place by improving what AI can do for you. PDFs, images, and media stay outside the repo — only markdown reference files go in.

---

## What You Can Do

Once set up, type these commands:

- `/think` - Research, make decisions, add context
- `/ads` - Generate image ads, video scripts, or review for compliance
- `/vsl` - Write video sales letters (Skool or B2B)
- `/organic` - Mine competitors, create Reels/TikTok/carousels
- `/site` - Build and deploy landing pages from your reference files
- `/help` - Get answers to any question

---

## Getting Help

- **Stuck?** Post in Skool with a screenshot. Tag @Devon.
- **Full curriculum** with videos: See the classroom in Skool.
