# Main Branch VIP

Turn Claude into your personal marketing team. Create ads, scripts, and community content that sounds like YOU.

---

## First Time? Start Here

**New to Claude Code, Git, or terminal?** Read the complete beginner guide:

**[docs/BEGINNER-SETUP.md](docs/BEGINNER-SETUP.md)**

It covers everything step-by-step, including common errors and how to fix them.

**Already comfortable with terminal and git?** Keep reading below.

---

## What You Can Do

Once set up, you can:

- Research topics and document decisions
- Generate batches of ad copy in your voice
- Create video scripts for Meta ads
- Mine competitor content and create organic Reels/TikTok/carousels
- Write VSL scripts for your community
- Review ads for compliance before you run them
- Manage Skool community engagement

All of this happens through simple commands. No prompting skills required.

---

## Before You Start

### 1. Get Repository Access (Required First)

This is a private repository. You need access before you can clone it.

**Share your GitHub username with Devon in the Skool community.** Wait for confirmation before proceeding.

### 2. Install These Tools

#### GitHub Desktop (Strongly Recommended)

GitHub Desktop is a visual app that makes Git easy. No commands to remember — just buttons to click.

- Download from [desktop.github.com](https://desktop.github.com)
- Sign in with your GitHub account

**Why you'll love it:**
- Shows you when updates are available (little badge appears)
- Lets you see exactly what changed
- No need to remember Git commands

*Already comfortable with Git? You can skip this and use terminal commands instead.*

#### Claude Code (Required)

Claude Code is a terminal app that runs skills.

| Requirement | What It Is | How to Get It |
|-------------|-----------|---------------|
| Claude Code | Terminal app that runs skills | See install commands below |
| Chrome Extension | Lets Claude see your web pages (optional) | [claude.ai/chrome](https://claude.ai/chrome) |

**Install Claude Code:**

Mac:
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows (PowerShell):
```powershell
irm https://claude.ai/install.ps1 | iex
```

You need a Claude Pro ($20/mo) or Max subscription to use Claude Code.

---

## Quick Start

### Step 1: Clone This Repo

Open GitHub Desktop. Click **File > Clone Repository**.

Paste this URL:
```
https://github.com/mainbranch-ai/vip
```

Choose where to save it (remember the location!). Click **Clone**.

### Step 2: Open Terminal in the vip Folder

**Mac:**
```bash
cd ~/path/to/vip
```

**Windows (Git Bash):**
```bash
cd /c/Users/YourName/path/to/vip
```

### Step 3: Run Claude Code

In your terminal, type:
```bash
claude
```

The first time, you will authenticate with your Anthropic account.

### Step 4: Start Setup

Once Claude is running, type:
```
/start
```

This walks you through everything. Just answer the questions.

### Step 5: Tell Claude About Your Business

Claude will ask you to share:
- Your offer (what you sell)
- Your audience (who buys)
- Your voice (how you sound)
- Testimonials (proof it works)

You can paste text, share URLs, or upload files. Claude organizes it all for you.

That is it. You are ready to generate.

---

## What Are Skills?

Skills are pre-built commands that do specific jobs.

Instead of figuring out how to prompt Claude, you just type a command like `/ads` and Claude knows exactly what to do.

**Example:**

You type:
```
/ads
```

Claude reads your business files, then generates 5-6 complete ad concepts. Each concept includes headlines, primary text, and image prompts. All in your voice.

No prompt engineering. No explaining what you want. Just type the command.

---

## Available Skills

| Command | What It Does |
|---------|-------------|
| `/start` | Main entry point — figures out what you need and routes you there |
| `/pull` | Quick update — pulls latest skills from GitHub |
| `/setup` | Set up your business repo (run this first if you're new) |
| `/think` | Research, make decisions, add context, transcribe local recordings, update reference files |
| `/ads` | Create ad copy (static or video) and review for compliance |
| `/vsl` | Write video sales letter scripts (Skool or B2B) |
| `/content` | Mine competitors, create Reels/TikTok/carousel scripts |
| `/skool-manager` | Respond to Skool community posts |

---

## How It Works

Main Branch is the engine. Your business info is the fuel.

```
THIS REPO (engine)          YOUR REPO (fuel)
Has all the skills    +     Has your business info
                      =     Outputs that sound like you
```

You create a separate folder for YOUR business. That is where your offer, audience, voice, and testimonials live.

The engine reads your files. Then it generates content specific to you.

---

## Your Business Repo Structure

After running `/start`, your business folder looks like this:

```
your-business/
├── reference/
│   ├── core/
│   │   ├── offer.md       <- What you sell
│   │   ├── audience.md    <- Who buys
│   │   └── voice.md       <- How you sound
│   ├── brand/             <- Deep brand systems
│   │   ├── voice-system.md
│   │   └── guardrails.md
│   ├── proof/
│   │   ├── testimonials.md <- Social proof
│   │   └── angles/        <- Proven messaging angles
│   └── domain/            <- Business-type specific
│       └── [see domain rubrics]
├── research/              <- Your investigations
├── decisions/             <- Your choices
└── outputs/               <- Generated content
```

You fill in the reference files. Claude reads them when generating.

---

## Keeping vip Updated

Devon updates the vip repository with new skills and improvements.

**Updates happen automatically.** Every skill pulls the latest changes before running. You don't need to do anything.

**GitHub Desktop (optional):** If you want to see what changed or pull updates manually, open GitHub Desktop, select vip, and click Pull origin. The History tab shows exactly what changed in each update.

---

## Need Help?

**In the Skool community:**
Post in the Main Branch group. Tag @Devon for technical questions.

**Common issues:**
- "404 error" or "Repository not found" — You need access first. Share your GitHub username with Devon.
- "Claude does not see my files" — Make sure you added vip as an additional working directory using `/add-dir`
- "Skills are not working" — Make sure you ran `claude` from inside the vip folder, then run `/start`
- "Output sounds generic" — Add more detail to your reference files, especially voice.md
- "I edited vip but can't push" — That's expected. vip is read-only. Your business data goes in YOUR repo.

---

## FAQ

**Do I need to know how to code?**

No. You just type commands and answer questions.

**What if I have multiple businesses?**

Create a separate repo for each one. The engine (this repo) stays the same.

**How do I update when new skills come out?**

Open GitHub Desktop. Click **Fetch origin**, then **Pull**. Done.

**Can I edit the skills?**

You can, but you do not need to. The skills are designed to work out of the box.

**What makes this different from ChatGPT?**

ChatGPT forgets everything between sessions. Main Branch remembers because your business info lives in files that Claude reads every time.

**I am stuck. What do I do?**

Type `/start` again. It picks up where you left off.

---

## Technical Details

Looking for the full system documentation? See [CLAUDE.md](CLAUDE.md).

That file has:
- Complete folder structure
- File naming conventions
- Domain rubrics by business type
- Compliance frameworks
- Git commit conventions

You do not need to read it to get started. But it is there when you want to go deeper.

---

## Community

[skool.com/main-branch](https://skool.com/main-branch)
