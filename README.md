# Main Branch

**Run your business as files in git. Stop renting it from someone else's dashboard.**

Main Branch is the `mb` CLI plus a set of MIT-licensed Claude Code skills for running business-as-files workflows. Your offer, audience, voice, research, decisions, and campaigns live in a six-folder taxonomy in your own git repo — versioned, portable, agent-readable. Built for Claude Code first; cross-agent at v0.2+.


## Install

```bash
pipx install mainbranch
```

That puts the `mb` CLI on your PATH. Run `mb --help` to see subcommands. (PyPI publish is the next launch step — until then, install in developer mode below.)

For developer mode (cloning the engine repo to hack on skills):

```bash
git clone https://github.com/noontide-co/mainbranch.git
```

See [CHANGELOG.md](CHANGELOG.md) for what's in this release.

---

## Honest current state (v0.1)

- **Built for Claude Code.** Cross-platform skill support is a v0.2+ commitment.
- **Schema is v1; will evolve.** Frontmatter shapes covered by `mb validate` are stable for v0.1.x; breaking changes bump the major.
- **Cross-agent compatibility matrix lands at v0.2.** Codex, Cursor, Hermes, local LLMs are not first-class targets in v0.1.

The engine v0.1.0 decision lives at [`decisions/2026-04-29-mb-vip-v0-1-0-master.md`](decisions/2026-04-29-mb-vip-v0-1-0-master.md).

The business-side master plan is tracked in [`noontide-co/projects#119`](https://github.com/noontide-co/projects/pull/119), which amends the launch direction around a CLI-first public product, Skool as the paid wrapper, and the four v0.1 pillars: ads, books, pages, and fulfillment.

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
- Generate organic content — Reels, TikTok, carousels — from your reference files and research
- Write VSL scripts for your community
- Review ads for compliance before you run them
- Build and deploy landing pages from your reference files
- Close sessions intentionally with crystallize moments

All of this happens through simple commands. No prompting skills required.

---

## Before You Start

### 1. Install These Tools

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
https://github.com/noontide-co/mainbranch
```

Choose where to save it (remember the location!). Click **Clone**.

### Step 2: First Session (Run From mainbranch)

Open a terminal in the **mainbranch** folder you just cloned:

**Mac:**
```bash
cd ~/Documents/GitHub/mainbranch
```

**Windows (Git Bash):**
```bash
cd /c/Users/YourName/Documents/GitHub/mainbranch
```

Run Claude and type `/setup`:
```bash
claude
```

`/setup` creates your business repo and configures everything. The first time, you will also authenticate with your Anthropic account.

### Step 3: Complete /setup (Share Business Context)

During `/setup`, Claude will ask you to share:
- Your offer (what you sell)
- Your audience (who buys)
- Your voice (how you sound)
- Testimonials (proof it works)

You can paste text, share URLs, or upload files. Claude organizes it all for you.

### Step 4: Daily Workflow (After Setup)

After setup, work from your **business repo** (not the Main Branch engine repo):
```bash
cd ~/Documents/GitHub/[your-business]
claude
/start
```

### Step 5: Start Generating

Use `/start` to route to the right workflow (`/think`, `/ads`, `/organic`, etc.).

That is it. You are ready to generate.

---

## What Are Skills?

Skills are pre-built workflows you invoke with slash prompts (for example, `/start`, `/ads`, `/think`).

Instead of figuring out how to prompt Claude, you invoke a skill with a slash prompt like `/ads` and Claude knows exactly what to do.

**Example:**

You type:
```
/ads
```

Claude reads your business files, then generates 5-6 complete ad concepts. Each concept includes headlines, primary text, and image prompts. All in your voice.

No prompt engineering. No explaining what you want. Just run the skill.

---

## Available Skills

| Skill | What It Does |
|---------|-------------|
| `/start` | Main entry point — figures out what you need and routes you there |
| `/setup` | Set up your business repo (run this first if you're new) |
| `/think` | Research, make decisions, add context, transcribe local recordings, update reference files |
| `/ads` | Create ad copy (static or video) and review for compliance |
| `/vsl` | Write video sales letter scripts (Skool or B2B) |
| `/organic` | Generate organic content — Reels, TikTok, carousels |
| `/site` | Generate and deploy landing pages from your reference files |
| `/wiki` | Personal wiki with atomic notes |
| `/end` | Close session — summary, crystallize, commit |
| `/help` | Get answers, troubleshoot, learn the system |
| `/pull` | Quick update — pulls latest skills from GitHub |
| `/newsletter` | Generate weekly newsletter from thinking work (coming soon) |

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
├── CLAUDE.md              <- Always loaded by Claude Code
├── .vip/                  <- Session config
│   ├── config.yaml        <- User preferences (git-tracked)
│   └── local.yaml         <- Session offer state (git-ignored)
├── reference/
│   ├── core/
│   │   ├── soul.md        <- WHY you exist
│   │   ├── offer.md       <- Brand-level thesis (or single offer)
│   │   ├── audience.md    <- WHO buys
│   │   └── voice.md       <- HOW you sound
│   ├── offers/            <- Per-offer context (multi-offer only)
│   │   └── [offer-name]/
│   │       ├── offer.md   <- Offer-specific transformation
│   │       └── audience.md <- Offer-specific audience (optional)
│   ├── visual-identity/   <- Image gen prompts, palette, type, paired imagery
│   ├── proof/
│   │   ├── testimonials.md <- Social proof
│   │   └── angles/        <- Proven messaging angles
│   └── domain/
│       ├── product-ladder.md  <- How offers relate (multi-offer)
│       └── content-strategy.md <- Pillars, platforms, cadence
├── research/              <- Your investigations
├── decisions/             <- Your choices
└── campaigns/             <- All generated content (lifecycle via frontmatter status)
```

You fill in the reference files. Claude reads them when generating.

---

## Keeping Main Branch Updated

Devon updates the Main Branch repository with new skills and improvements.

**Updates happen automatically when you run `/start`.** You can also run `/pull` anytime to get the latest.

**GitHub Desktop (optional):** If you want to see what changed or pull updates manually, open GitHub Desktop, select `mainbranch`, and click Pull origin. The History tab shows exactly what changed in each update.

---

## Need Help?

**In the Skool community:**
Post in the Main Branch group. Tag @Devon for technical questions.

**Common issues:**
- "404 error" or "Repository not found" — Verify the URL and your network. The repo is public; no access request needed.
- "Claude does not see my files" — Make sure you started Claude in your business repo folder and ran `/start`
- "Skills are not working" — Check that `.claude/settings.local.json` exists and run `/start` once to auto-repair missing bridge links. If still broken, run `/setup`.
- "Output sounds generic" — Add more detail to your reference files, especially voice.md
- "I edited Main Branch but can't push" — That's expected for most users. Main Branch is the shared engine. Your business data goes in YOUR repo.

---

## FAQ

**Do I need to know how to code?**

No. You invoke skills with slash prompts and answer questions.

**What if I have multiple products under one brand?**

Use one repo with an `offers/` folder. Each offer gets its own `offer.md`. Soul and voice stay shared in `core/`. Run `/setup` or `/think` to add offers.

**What if I have multiple separate businesses?**

Create a separate repo for each brand. If they share the same soul and voice, they can share a repo. If not, separate repos.

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
