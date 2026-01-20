# Main Branch VIP

Turn Claude into your marketing team. Create ads, scripts, content that sounds like YOU.

---

## New to Claude Code?

**Complete beginner?** Read [docs/BEGINNER-SETUP.md](docs/BEGINNER-SETUP.md) first.

**Comfortable with terminal?** Keep reading.

---

## What You Can Do

- Research topics, document decisions
- Generate ad copy batches in your voice
- Write video scripts for Meta ads
- Mine competitors, create Reels/TikTok/carousels
- Write VSL scripts
- Review ads for compliance
- Manage Skool community

---

## Before You Start

### 1. Get Repository Access

Private repo. Share GitHub username with Devon in Skool. Wait for confirmation.

### 2. Install Tools

**GitHub Desktop** (recommended): [desktop.github.com](https://desktop.github.com)

**Claude Code** (required):
```bash
# Mac
curl -fsSL https://claude.ai/install.sh | bash

# Windows (PowerShell)
irm https://claude.ai/install.ps1 | iex
```

Requires Claude Pro ($20/mo) or Max subscription.

---

## Quick Start

1. **Clone**: GitHub Desktop → File → Clone → `https://github.com/mainbranch-ai/vip`
2. **Terminal**: `cd ~/path/to/vip`
3. **Run**: `claude`
4. **Start**: `/start`

Answer the questions. Share your offer, audience, voice, testimonials.

Done.

---

## Skills

| Command | What |
|---------|------|
| `/start` | Entry point — routes you where needed |
| `/pull` | Pull latest updates |
| `/setup` | Set up business repo (first time) |
| `/enrich` | Add context, fill gaps |
| `/think` | Research → decide → codify |
| `/ad-static` | Static image ad copy |
| `/ad-video-scripts` | Video ad scripts |
| `/ad-review` | Compliance review |
| `/content` | Mine competitors, organic scripts |
| `/skool-vsl-scripts` | VSL scripts |
| `/skool-manager` | Skool community posts |

---

## How It Works

```
vip (engine)     +     your-repo (data)     =     outputs in your voice
```

Engine reads your files. Generates content specific to you.

---

## Your Business Repo

```
your-business/
├── reference/
│   ├── core/          # offer.md, audience.md, voice.md
│   ├── brand/         # Deep brand systems
│   ├── proof/         # testimonials, angles
│   └── domain/        # Business-type specific
├── research/          # Investigations
├── decisions/         # Choices with rationale
└── outputs/           # Generated content
```

---

## Updates

Automatic. Skills pull latest before running.

Manual: GitHub Desktop → Pull origin.

---

## Need Help?

**Skool**: Post in Main Branch group. Tag @Devon.

**Common issues:**
- "404/not found" → Need access first
- "Claude doesn't see files" → `/add-dir` vip as working directory
- "Skills not working" → Run `claude` from inside vip, then `/start`
- "Output sounds generic" → Add detail to reference files

---

## FAQ

**Need to code?** No.

**Multiple businesses?** Separate repo each.

**Update skills?** GitHub Desktop → Fetch → Pull.

**Can I edit skills?** Yes, but unnecessary.

**Different from ChatGPT?** Claude reads your files every time. No forgetting.

**Stuck?** `/start` again.

---

## Technical Details

See [CLAUDE.md](CLAUDE.md) for full system docs.
