# Beginner Setup Guide

Complete setup guide for people new to Claude Code, Git, or terminal.

---

## Read This First

**If this feels over your head, that's okay.** You're not alone.

This guide involves some technical stuff — terminal commands, GitHub, cloning repos. If you've never done any of this before, it might feel foreign. But here's what I want you to know:

**This is one of the biggest opportunities I've ever seen.** And whether you're technical or not, it is absolutely worth the small effort it's going to take you — probably under an hour — to get through this setup.

Here's the thing: **most of this is one-time setup.** You're not going to be typing terminal commands every day. You're not going to need to memorize any of this. Once you're set up, you're mostly just chatting with Claude like normal.

**So why do we need the terminal at all?**

Because this tool needs to create and edit files on your computer. That's what makes it so powerful. Instead of Claude forgetting everything between conversations, your business context lives in actual files that Claude reads every time. That's the magic — and the terminal is just the door that lets Claude do this work for you.

**You can do this.** Even if Git and GitHub feel weird right now, you'll start to get familiar with it over time. Don't let the unfamiliarity stop you. Just focus on one step at a time.

Let's go.

---

## Before You Do Anything Else

### Step 0: Get Repository Access

The vip repository is private. You need access before anything else will work.

**How to get access:**
1. Create a GitHub account if you don't have one: [github.com/signup](https://github.com/signup)
2. Share your GitHub username with Devon in the Skool community
3. Wait for confirmation that you've been added

**Without access, you'll see errors like:**
- "404 Not Found"
- "Repository not found"
- "Could not read Username"

Don't move forward until Devon confirms you have access.

---

## Required Accounts

| Account | What It's For | Link |
|---------|---------------|------|
| GitHub | This is where the code lives. Think of it like a shared folder in the cloud. | [github.com/signup](https://github.com/signup) |
| Anthropic (Pro or Max) | Your Claude subscription. You need a paid plan to use Claude Code. | [claude.ai](https://claude.ai) |

Claude Code requires Pro ($20/month) or Max ($100-200/month).

---

## Install These Tools

### 1. GitHub Desktop (Strongly Recommended)

GitHub Desktop is a visual app that makes Git easy. No commands to remember — just buttons to click.

**Install:**
- Download from [desktop.github.com](https://desktop.github.com)
- Sign in with your GitHub account

**Why you'll love it:**
- Shows you when updates are available (little badge appears)
- Lets you see exactly what changed
- No need to remember Git commands

**Already comfortable with Git?** You can skip this and use terminal commands. But for most people, GitHub Desktop removes a lot of headaches.

### 2. Claude Code (Required)

Claude Code is a terminal app. "Terminal" is just a text-based way to talk to your computer — you type commands, it does things.

**To install on Mac:**

1. Open Terminal (find it in Applications → Utilities → Terminal)
2. Copy and paste this entire line, then press Enter:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**To install on Windows:**

1. Open PowerShell (search for "PowerShell" in your Start menu)
2. Copy and paste this entire line, then press Enter:

```powershell
irm https://claude.ai/install.ps1 | iex
```

That's it. The installer does the rest.

---

## Setup Steps

Don't overthink this. Just follow each step.

### Step 1: Clone the Repository

"Cloning" just means downloading a copy of the files to your computer.

1. Open GitHub Desktop
2. Click **File → Clone Repository**
3. Click the **GitHub.com** tab (not URL)
4. You should see `mainbranch-ai/vip` in the list. Select it.
5. Choose where to save it. Your Documents folder is fine. **Remember this location!**
6. Click **Clone**

**If you don't see `mainbranch-ai/vip` in the list:**
- You're either not logged in, or not logged into the right account
- Go to **GitHub Desktop → Preferences → Accounts**
- Sign in with the GitHub account you gave Devon
- Try again

**Alternate method (URL tab):**
If for some reason the GitHub.com tab doesn't work, you can use the URL tab instead:
1. Click the **URL** tab
2. Paste: `https://github.com/mainbranch-ai/vip`
3. Click Clone

But the GitHub.com tab is easier because if the repo shows up, you know you're logged in correctly.

### Step 2: Open Terminal in the vip Folder

Now you need to open your terminal "inside" the folder you just downloaded. This tells Claude Code where to look for files.

**On Mac:**

Option A (easiest):
1. Open Terminal (Applications → Utilities → Terminal)
2. Type `cd ` (that's "cd" followed by a space)
3. Open Finder, find the vip folder, and drag it into the Terminal window
4. Press Enter

Option B (if you know where you saved it):
```bash
cd ~/Documents/vip
```

**On Windows:**

1. Open File Explorer and navigate to the vip folder
2. Right-click inside the folder (not on a file)
3. Click "Open in Terminal" or "Git Bash Here"

**What does "cd" mean?** It stands for "change directory." It's just telling your computer "go to this folder."

### Step 3: Start Claude Code

Now, in that same terminal window, type:

```bash
claude
```

And press Enter.

The first time you do this, Claude will ask you to log in. Just follow the prompts — it'll open a browser window.

### Step 4: Run the Start Command

Once Claude is running, you'll see a prompt where you can type. Type:

```
/start
```

And press Enter.

**That's it.** From here, Claude takes over and guides you through everything else. You're just chatting now.

---

## Once Claude is Running, Just Ask

Here's the thing most people don't realize at first:

**Claude can help you with everything.** You don't need to memorize commands. You don't need to follow this guide perfectly. Once Claude is running, you can just... ask.

Stuck on something? Just type:
- "I'm confused about the two repo thing, can you explain?"
- "Help me connect my git"
- "What should I do next?"
- "I got an error, here's what it says..."

**Skills vs. Just Chatting:**
- Skills like `/start`, `/ad-static`, `/think` are carefully built workflows that guide you through specific tasks
- But you can also just have a normal conversation — ask questions, get help, troubleshoot

**Pro tip:** If you're ever stuck and this guide isn't helping, paste the whole thing into your Claude conversation and say "I'm stuck at step X, help me." Claude can read it and help you through.

The reason this guide exists isn't so you memorize it — it's so Claude (and you) have a reference. Use it however helps you most.

---

## Understanding the Two Repos

This is the key concept. Once you get this, everything else makes sense.

### vip (The Engine)

This is the shared system that everyone uses. It contains all the skills, templates, and frameworks.

- You **download updates** from this — you never edit it
- You have **read-only access** (you can look but not change the original)
- Think of it like software you install — you use it, you don't rewrite it

### Your Business Repo (Your Data)

This is YOUR personal folder. It contains everything about YOUR business — your offer, your audience, how you talk, your testimonials.

- You **create this** when you run `/setup`
- You **own and control** everything in it
- This is what makes your outputs sound like YOU

```
vip/                          your-business/
├── Skills                    ├── Your offer
├── Templates                 ├── Your audience
├── Frameworks                ├── Your voice
└── (shared, read-only)       └── (yours, you own it)
```

**How they work together:** The engine (vip) reads your business data and generates content that sounds like you. Same engine, different data = different outputs for each business.

---

## Keeping vip Updated

Devon regularly adds new skills and improvements. Here's the good news:

### Updates Happen Automatically

**You don't need to do anything.** Every time you use a skill (`/start`, `/ad-static`, etc.), it automatically checks for updates and pulls them. If there were updates, Claude will briefly mention it and keep going.

### GitHub Desktop (If You're Curious)

Want to see what changed? Open GitHub Desktop:
- A number badge means updates are available
- Click **Pull origin** to get them
- Click on commits in the History tab to see exactly what's new

But again — you don't need to do this. Skills auto-update.

---

## Common Errors and Fixes

Everyone hits these at some point. Here's what they mean:

| What You See | What Happened | How to Fix It |
|--------------|---------------|---------------|
| "We couldn't find that repository" | You don't have access yet | Share your GitHub username with Devon and wait for confirmation |
| "404 error" or "Repository not found" | You don't have access yet | Share your GitHub username with Devon and wait for confirmation |
| "Could not read Username" | Git isn't logged in | Open GitHub Desktop and make sure you're signed in |
| "command not found: claude" | Claude Code isn't installed | Run the install command again (Step 2 of Install) |
| "Skills not working" | You're not in the right folder | Make sure you ran `claude` from inside the vip folder |
| Made changes but can't push | vip is read-only (this is normal!) | Your business data goes in YOUR repo, not vip |

### "We couldn't find that repository" — The Most Common Issue

This error means GitHub can't access the vip repo. 99% of the time it's one of these:

**1. You don't have access yet (most likely)**
- The vip repo is private — you must be invited
- Share your GitHub username with Devon
- Wait for confirmation before trying again

**2. You're not logged into GitHub Desktop**
- Open GitHub Desktop
- Go to GitHub Desktop → Preferences → Accounts
- Make sure you're signed into GitHub.com with the account Devon added

**3. You're logged into the wrong GitHub account**
- Some people have multiple GitHub accounts
- Check which account you gave Devon — that's the one you need to be signed into

### Duplicate App Icons in Dock

If you see two GitHub Desktop icons (or restored an app from Trash):

1. Quit GitHub Desktop completely (Cmd+Q)
2. Open Trash → delete the GitHub Desktop items permanently
3. Check Applications folder — is GitHub Desktop there?
4. If not, download fresh from [desktop.github.com](https://desktop.github.com)
5. Open the fresh install and sign in again

---

## What NOT to Do

### Don't Paste GitHub URLs into Claude

Claude Code works with files on your computer. It can't fetch things from the internet.

**This won't work:**
```
> https://github.com/mainbranch-ai/vip
Error: Request failed status code 404
```

**Do this instead:**
1. Clone the repo first (GitHub Desktop)
2. Open terminal in that folder
3. Run `claude`
4. Type `/start`

### Don't Edit the vip Folder

Even if you accidentally edit something in vip:
- You can't push those changes (it's read-only)
- It might cause problems when you try to update

All your business stuff goes in YOUR separate repo. Claude will guide you to set that up.

### Don't Use Claude Desktop App or Cowork for Main Branch

Those are great tools, but they work differently. Main Branch needs the terminal version because it works with two folders at once (vip + your business).

---

## After Initial Setup

Once you've created your business repo with `/setup`, you'll want Claude to see both folders.

This is easy. In Claude, just type:

```
/add-dir ~/path/to/other/folder
```

For example, if you're working in vip and want to add your business repo:
```
/add-dir ~/Documents/my-business
```

Or if you're in your business repo and want to add vip:
```
/add-dir ~/Documents/vip
```

Now Claude can see both and use the skills to work with your data.

---

## Skip IDE Integration For Now

You might hear about VS Code integration or other fancy setups. Ignore all that for now.

Get the basics working first:
1. Clone vip ✓
2. Run `/start` ✓
3. Create your business repo ✓
4. Generate some outputs ✓

Once you're comfortable, we can talk about other tools. But honestly? Many people never need them.

---

## Getting Help

**Stuck? Post in the Skool community.**
- Tag @Devon for technical questions
- Share a screenshot of the error — it helps a lot

**Quick checks before asking:**
1. Do you have repository access? (Devon confirmed?)
2. Did you run `claude` from inside the vip folder?
3. Is Claude Code installed? (Try typing `claude --version` in terminal)

---

## Quick Reference

### First-Time Setup (Do Once)
```
1. Get GitHub access from Devon
2. Install GitHub Desktop
3. Install Claude Code
4. Clone vip using GitHub Desktop
5. Open terminal in the vip folder
6. Type: claude
7. Type: /start
8. Follow the prompts
```

### Daily Use (After Setup)
```
1. Open terminal
2. Go to your business folder: cd ~/my-business
3. Type: claude
4. Chat, use skills, or just ask for help
```

That's it. Once Claude is running, you can ask it to help you with the rest — including adding vip if you forgot.

---

## You've Got This

Seriously. If you made it through this guide, the hard part is over.

From here on out, you're just having conversations with Claude — except now Claude actually knows your business, remembers everything, and can create real files and outputs for you.

**And remember:** If you ever get stuck, just ask Claude. It's read all these docs. It knows the system. It can help you troubleshoot, explain concepts, or guide you through whatever you're trying to do.

That's the power of this system. And you just unlocked it.

Let's go build something.
