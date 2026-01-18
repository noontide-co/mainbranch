# Beginner Setup Guide

Complete setup guide for people new to Claude Code, Git, or terminal.

---

## Before You Do Anything Else

### Step 0: Get Repository Access

The vip repository is private. You need access before you can clone it.

**How to get access:**
1. Create a GitHub account if you don't have one: [github.com/signup](https://github.com/signup)
2. Share your GitHub username with Devon in the Skool community
3. Wait for confirmation that you've been added

**Without access, you'll see errors like:**
- "404 Not Found"
- "Repository not found"
- "Could not read Username"

Don't proceed until you have access confirmed.

---

## Required Accounts

| Account | What For | Link |
|---------|----------|------|
| GitHub | Access the vip repository | [github.com/signup](https://github.com/signup) |
| Anthropic (Pro or Max) | Use Claude Code | [claude.ai](https://claude.ai) |

You need a paid Claude subscription (Pro at $20/month or Max at $100-200/month) to use Claude Code.

---

## Install These Tools

### 1. GitHub Desktop (Required)

GitHub Desktop lets you clone repositories and see when updates are available — all without touching the terminal.

**Install:**
- Download from [desktop.github.com](https://desktop.github.com)
- Sign in with your GitHub account

**Why GitHub Desktop:**
- Visual indicator when there are updates to pull
- No need to remember git commands
- Works the same on Mac and Windows

### 2. Claude Code (Required)

Claude Code is the terminal app that runs Main Branch skills.

**Mac:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

After installing, you'll need to authenticate with your Anthropic account the first time you run it.

---

## Setup Steps

### Step 1: Clone the Repository

Open GitHub Desktop and clone the vip repository.

1. Open GitHub Desktop
2. Click **File → Clone Repository**
3. Click the **URL** tab
4. Paste: `https://github.com/mainbranch-ai/vip`
5. Choose where to save it (remember this location!)
6. Click **Clone**

**If you get an error:** You probably don't have access yet. Go back to Step 0.

### Step 2: Open Terminal in the vip Folder

**Mac:**
1. Open Terminal (Applications → Utilities → Terminal)
2. Type `cd ` (with a space after it)
3. Drag the vip folder from Finder into the Terminal window
4. Press Enter

Or if you cloned to your home folder:
```bash
cd ~/vip
```

**Windows:**
1. Open the folder where you cloned vip in File Explorer
2. Right-click inside the folder
3. Select "Open in Terminal" or "Git Bash Here"

Or in Git Bash:
```bash
cd /c/Users/YourName/path/to/vip
```

### Step 3: Start Claude Code

In your terminal, type:
```bash
claude
```

The first time, you'll be asked to authenticate. Follow the prompts.

### Step 4: Run the Start Command

Once Claude is running, type:
```
/start
```

Claude will guide you from here. It will:
1. Check if you have a business repo set up
2. If not, guide you through `/setup` to create one
3. Help you add your business context

---

## Understanding the Two Repos

This is the most important concept to understand.

### vip (The Engine)

- Contains skills, lenses, compliance frameworks
- You **PULL** updates from this — never edit it
- You have **read-only access** on GitHub
- Even if you edit files locally, you cannot push changes

### Your Business Repo (Your Data)

- Contains your offer, audience, voice, testimonials
- You **create this** via the `/setup` command
- You **own and edit** this
- You can push changes to your own GitHub

```
vip/                          your-business/
├── .claude/skills/           ├── reference/
├── .claude/lenses/           │   ├── core/
├── .claude/reference/        │   ├── proof/
└── (DO NOT EDIT)             │   └── domain/
                              ├── research/
                              ├── decisions/
                              └── outputs/
                              (YOU OWN THIS)
```

**The two work together:** vip provides the skills. Your business repo provides the data. Skills read your data and generate outputs.

---

## Keeping vip Updated

Devon will update the vip repository with new skills and improvements. Here's how to get those updates:

### Using GitHub Desktop

1. Open GitHub Desktop
2. Select the **vip** repository from the dropdown
3. Look for **Fetch origin** or **Pull origin** button
4. If there's a number badge or arrow, updates are available
5. Click **Pull** to get them

**Check weekly** or when Devon announces updates in Skool.

### What Updates Look Like

In GitHub Desktop, you'll see:
- An arrow icon indicating changes available
- "Pull origin" button becomes active
- The number of commits behind

---

## Common Errors and Fixes

| Error | What Happened | Fix |
|-------|---------------|-----|
| "404 error" or "Repository not found" | No access to the repo | Share your GitHub username with Devon |
| "Could not read Username" | Git can't authenticate | Sign into GitHub Desktop first |
| "command not found: claude" | Claude Code not installed | Run the install command again |
| "Skills not working" | Not in the vip folder | Make sure you ran `claude` from inside the vip folder |
| Made changes to vip but can't push | You only have read access | This is expected — vip is read-only. Your business data goes in YOUR repo |

---

## What NOT to Do

### Don't Enter GitHub URLs into Claude

Claude Code doesn't fetch repositories. If you paste a GitHub URL into Claude, you'll get a 404 error.

**Wrong:**
```
> https://github.com/mainbranch-ai/vip
Error: Request failed status code 404
```

**Right:**
1. Clone the repo using GitHub Desktop first
2. Open terminal in that folder
3. Run `claude`
4. Type `/start`

### Don't Edit the vip Repository

Even though you can edit files locally, you:
- Cannot push changes (read-only access)
- Will create conflicts when you try to pull updates
- Should put all your business data in YOUR separate repo

If Claude ever tries to write to the vip folder, something went wrong.

### Don't Use Claude Desktop App or Cowork for Main Branch

These are great tools, but they don't support the two-directory workflow that Main Branch requires.

| Tool | Works for Main Branch? | Why |
|------|----------------------|-----|
| Claude Code (Terminal) | Yes | Supports `/add-dir` for multiple directories |
| Claude Desktop App | No | Designed for single-repo workflows |
| Cowork | No | Sandboxed to one folder |

---

## Adding Your Business Repo (After Initial Setup)

Once you've created your business repo with `/setup`, you'll want Claude to see both repos.

### Option 1: Add vip as Additional Directory

Work from your business repo, add vip:

```bash
cd ~/your-business-repo
claude
```

Then in Claude:
```
/add-dir ~/vip
```

### Option 2: Add Your Business Repo to vip

Work from vip, add your business repo:

```bash
cd ~/vip
claude
```

Then in Claude:
```
/add-dir ~/your-business-repo
```

Either way works. The point is Claude needs to see both directories.

---

## IDE Integration (Skip for Now)

Claude Code can integrate with VS Code and other editors. This is useful but adds complexity.

**Skip this until you're comfortable with the basics.**

Once you've successfully:
1. Cloned vip
2. Run `/start`
3. Created your business repo
4. Generated some outputs

Then consider adding IDE integration. We'll cover that in a separate guide.

---

## Getting Help

**In the Skool community:**
- Post in the Main Branch group
- Tag @Devon for technical questions
- Share screenshots of errors

**Before asking for help, check:**
1. Do you have repository access? (Step 0)
2. Are you in the right folder? (run `pwd` to check)
3. Is Claude Code installed? (run `claude --version`)

---

## Quick Reference

### First-Time Setup (Do Once)
```
1. Get GitHub access from Devon
2. Install GitHub Desktop
3. Install Claude Code
4. Clone vip via GitHub Desktop
5. cd into vip folder
6. Run: claude
7. Type: /start
```

### Daily Workflow
```
1. Open terminal
2. cd ~/vip (or your business repo)
3. Run: claude
4. Use /add-dir to add the other repo
5. Use skills like /ad-static, /think, etc.
```

### Getting Updates
```
1. Open GitHub Desktop
2. Select vip repository
3. Click "Pull origin" if updates available
```
