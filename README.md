# Main Branch Premium

Turn Claude into your personal marketing team. Create ads, scripts, and community content that sounds like YOU.

---

## What You Can Do

Once set up, you can:

- Research topics and document decisions
- Generate batches of ad copy in your voice
- Create video scripts for Meta ads
- Write VSL scripts for your community
- Review ads for compliance before you run them
- Manage Skool community engagement

All of this happens through simple commands. No prompting skills required.

---

## Before You Start

You need three things installed:

| Requirement | What It Is | How to Get It |
|-------------|-----------|---------------|
| Claude Code | The terminal app that runs these skills | [claude.ai/code](https://claude.ai/code) |
| Chrome Extension | Lets Claude see your web pages | [claude.ai/chrome](https://claude.ai/chrome) |
| GitHub Desktop | Keeps your files synced | [desktop.github.com](https://desktop.github.com) |

New to all this? That is okay. Each install takes about 2 minutes.

---

## Quick Start

### Step 1: Clone This Repo

Open GitHub Desktop. Click **File > Clone Repository**.

Paste this URL:
```
https://github.com/mainbranch-ai/vip
```

Choose where to save it. Click **Clone**.

### Step 2: Open Claude Code

Open Claude Code (the terminal app, not the website).

You will see a prompt. Type:
```
/repo-setup
```

This walks you through everything. Just answer the questions.

### Step 3: Tell Claude About Your Business

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

Instead of figuring out how to prompt Claude, you just type a command like `/ad-static` and Claude knows exactly what to do.

**Example:**

You type:
```
/ad-static
```

Claude reads your business files, then generates 5-6 complete ad concepts. Each concept includes headlines, primary text, and image prompts. All in your voice.

No prompt engineering. No explaining what you want. Just type the command.

---

## Available Skills

| Command | What It Does |
|---------|-------------|
| `/repo-setup` | Set up your business repo (run this first) |
| `/think` | Research topics, make decisions, update reference files |
| `/ad-static` | Create static image ad copy for Meta |
| `/ad-video-scripts` | Write 15-60 second video ad scripts |
| `/ad-review` | Check ads for FTC and Meta compliance |
| `/skool-vsl-scripts` | Write video sales letter scripts |
| `/skool-manager` | Respond to Skool community posts |

---

## How It Works

Main Branch Premium is the engine. Your business info is the fuel.

```
THIS REPO (engine)          YOUR REPO (fuel)
Has all the skills    +     Has your business info
                      =     Outputs that sound like you
```

You create a separate folder for YOUR business. That is where your offer, audience, voice, and testimonials live.

The engine reads your files. Then it generates content specific to you.

---

## Your Business Repo Structure

After running `/repo-setup`, your business folder looks like this:

```
your-business/
├── reference/
│   ├── core/
│   │   ├── offer.md       <- What you sell
│   │   ├── audience.md    <- Who buys
│   │   └── voice.md       <- How you sound
│   └── proof/
│       └── testimonials.md <- Social proof
├── research/              <- Your investigations
├── decisions/             <- Your choices
└── outputs/               <- Generated content
```

You fill in the reference files. Claude reads them when generating.

---

## Need Help?

**In the Skool community:**
Post in the Main Branch group. Tag @Devon for technical questions.

**Common issues:**
- "Claude does not see my files" - Make sure you added vip as an additional working directory
- "Skills are not working" - Run `/repo-setup` first to set everything up
- "Output sounds generic" - Add more detail to your reference files, especially voice.md

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

ChatGPT forgets everything between sessions. Main Branch Premium remembers because your business info lives in files that Claude reads every time.

**I am stuck. What do I do?**

Type `/repo-setup` again. It picks up where you left off.

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
