# Getting Started

Step-by-step guide from zero to working with Main Branch.

---

## Prerequisites

1. **GitHub account** - [github.com/signup](https://github.com/signup)
2. **Repository access** - Share your GitHub username with Devon in Skool, wait for confirmation
3. **Claude subscription** - Pro ($20/mo) or Max ($100-200/mo) at [claude.ai](https://claude.ai)

---

## Setup Steps

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

**Mac users:** If prompted about Xcode Command Line Tools, click Install. The time estimate is wrong.

### 3. Clone vip

In GitHub Desktop:
1. File → Clone Repository
2. GitHub.com tab
3. Select `mainbranch-ai/vip`
4. Clone

### 4. Open Terminal in vip Folder

**Mac:**
1. Open Terminal
2. Type `cd ` (with a space)
3. Drag the vip folder from Finder into Terminal
4. Press Enter

**Windows:**
1. Right-click inside the vip folder
2. "Open in Terminal"

### 5. Start Claude

```bash
claude
```

### 6. Run /start

```
/start
```

Follow the prompts. `/start` will guide you through creating your business repo.

---

## After Setup: Daily Workflow

```bash
cd ~/Documents/GitHub/vip
claude
/start
```

That's it. `/start` remembers your business repo and loads it automatically.

---

## What /start Does

1. Pulls latest vip updates
2. Loads your business repo (from saved path)
3. Checks your setup completeness
4. Routes you to the right skill based on what you need

---

## Adding Your Business Context

Once your business repo exists, dump everything:

- Sales pages
- Offer details
- Testimonials
- Notes about your audience
- How you talk (emails, posts, DMs)
- URLs to your content

Methods:
- Paste text directly
- Drag files into the terminal
- Share URLs (Claude can fetch them)
- Share file paths

Claude will sort everything into the right reference files.

---

## The Reference Files

Your business repo contains:

```
your-business/
├── reference/
│   ├── core/
│   │   ├── offer.md       # What you sell
│   │   ├── audience.md    # Who buys
│   │   └── voice.md       # How you sound
│   ├── proof/
│   │   ├── testimonials.md
│   │   └── angles/        # Proven messaging
│   └── domain/            # Business-type specific
├── research/              # Your investigations
├── decisions/             # Your choices with rationale
└── outputs/               # Generated content
```

Skills read these files to generate content that sounds like you.

---

## Next Steps After Setup

1. **Fill reference files** - The more context, the better outputs
2. **Try a skill** - `/ad-static` for image ads, `/think` for research
3. **Ask questions** - `/help` if you're stuck
4. **Add more context** - `/enrich` when you have new testimonials, angles, etc.
