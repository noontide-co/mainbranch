# Skills Guide: When to Use What

Skills are specialized workflows. Each one does something specific. This guide helps you pick the right one.

---

## The Main Skills

### /start - Entry Point
**Use when:** Beginning a session, unsure what to do next, want Claude to figure out your state.

**What it does:**
- Pulls latest vip updates
- Loads your business repo automatically
- Checks your setup completeness
- Routes you to the right skill

**Daily habit:** Always start sessions with `/start`.

---

### /setup - First-Time Setup
**Use when:** New to Main Branch, need to create your business repo.

**What it does:**
- Creates your business folder structure
- Asks about your business type
- Gathers your context (offer, audience, voice)
- Saves everything to reference files

**One-time:** You only run this once per business.

---

### /think - Research, Decisions, and Context
**Use when:** Exploring a question, making a strategic decision, need to document rationale, or adding new context to reference files.

**Two ways to invoke:**
- `/think` — Loads the full skill with routing and mode detection. Best when you're starting a focused thinking session.
- `/think "my question"` — Jumps straight into exploring that question. Best when you already know what you're investigating.

Both are valid. Use whichever fits the moment. Don't overthink which to use.

**What it does:**
- Researches topics (web, your files, your input)
- Synthesizes findings
- Helps you make decisions
- Records everything to files
- Updates reference when you codify
- Adds new context (via codify mode)

**Heavy use:** This is the core skill. Use it for any "should we...?" question.

See [the-think-cycle.md](the-think-cycle.md) for deep dive.

---

### /ads - Ad Generation and Review
**Use when:** Need copy for static ads, video ad scripts, or compliance review.

**Modes:**
- `/ads` or `/ads static` - Image ad copy (primaries, headlines, image prompts)
- `/ads video` - Video ad scripts (15-60 seconds, UGC style)
- `/ads review` - Multi-lens compliance check (FTC, Meta policy, copy quality)

**Output:** Multiple concepts with variations.

---

### /vsl - Video Sales Letters
**Use when:** Need long-form sales video scripts.

**Modes:**
- `/vsl skool` - 18-section framework for Skool communities
- `/vsl b2b` - Haynes 7-step framework for high-ticket B2B

---

### /organic - Organic Content
**Use when:** Generating Reels, TikTok, or carousel content from your reference files and research (not paid ads).

**What it does:**
- Generates scripts in your voice from reference + research
- Supports video, carousel, and static formats
- Uses mined research from `/think` (competitor analysis, framework extraction)

**Modes:**
- `/organic` - Full flow (select concept -> generate)
- `/organic video "topic"` - Generate Reels/TikTok script
- `/organic carousel "topic"` - Generate carousel slides
- `/organic static "topic"` - Generate post caption

**Mining happens in /think:** If you need to mine competitors first, run `/think` to research and save findings, then come back to `/organic` to generate from that research.

**Key difference from /ads video:** Organic uses soft CTAs (save, follow) while ads use hard CTAs (buy, sign up).

---

### /wiki - Personal Wiki
**Use when:** Building a public wiki with atomic notes and WikiLinks.

**What it does:**
- Sets up wiki from Commune Wiki template
- Creates atomic notes with proper frontmatter
- Converts Gemini/GPT research to wiki format
- Auto-deploys to Cloudflare Pages on git push

**Modes:**
- `/wiki setup` - First-time setup (repo, hosting, config)
- `/wiki add "Note Title"` - Create new atomic note
- `/wiki publish` - Commit and push (auto-deploys)
- `/wiki research [file]` - Convert research to wiki format
- `/wiki update` - Pull upstream template fixes
- `/wiki recent` - Generate weekly updates note

**Key difference from business repo:** Wiki is for public evergreen knowledge. Business repo is for private reference files.

---

### /end - Close Session
**Use when:** Done for the day, wrapping up, want to close intentionally.

**What it does:**
- Scans today's git activity (new files, changes)
- Summarizes what happened this session
- Offers a crystallize moment if decisions were made
- Commits uncommitted work
- Closes with a brief summary

**Why it matters:** If you've ever closed a terminal and wondered "did that stick?", `/end` is the answer. It reviews your git activity, surfaces anything that might need crystallizing into reference, and commits uncommitted work. Nothing falls through the cracks.

**Daily habit:** End sessions with `/end` to close intentionally.

---

### /help - Get Answers
**Use when:** Confused, stuck, have questions about Main Branch.

**What it does:**
- Answers questions from documented curriculum
- Troubleshoots errors
- Explains concepts
- Suggests next skills

**You're using it now.**

---

## Decision Tree

```
What do you need?
│
├── Starting a session?
│   └── /start
│
├── First time setup?
│   └── /setup
│
├── Research, decide, or add context?
│   └── /think
│
├── Create ad copy? (paid)
│   └── /ads (static, video, or review mode)
│
├── Write video sales letter?
│   └── /vsl (skool or b2b)
│
├── Create organic content? (free reach)
│   └── /organic (Reels, TikTok, carousels)
│
├── Build a public wiki?
│   └── /wiki
│
├── Done for the day?
│   └── /end
│
└── Confused or stuck?
    └── /help
```

---

## Skill Combinations

Common workflows:

**New campaign:**
1. `/think` - Research your angle
2. `/ads static` or `/ads video` - Generate copy
3. `/ads review` - Check before running

**Learning from results:**
1. `/think research` - Document what worked
2. `/think codify` - Add winning angles to reference
3. Next campaign uses updated reference

**Business evolution:**
1. `/think` - Decide on offer change
2. `/think codify` - Update reference with decision
3. Future outputs reflect new offer

---

## When You're Not Sure

If you don't know which skill to use:

1. Run `/start` - It'll detect your state and suggest
2. Ask `/help` - Describe what you want to accomplish
3. Run `/think` - If it's a question worth exploring
4. Still learning the system? That's expected — context management is a skill that develops over time. The more you use `/think` and `/end`, the more natural it gets.

Most of the time, `/start` will point you in the right direction.

---

## Creating Your Own Skills

Want Notion export? Custom CMS posting? Your unique workflow?

You can create custom skills manually or use Anthropic's `/skill-creator` if you have it installed. You have **two locations** for custom skills:

### Option 1: Business Repo Skills (Project-Specific)

Skills that only make sense for one business/project:

```
your-business-repo/
└── .claude/skills/my-skill/SKILL.md
```

**Use for:** Business-specific workflows like `/notion-export`, `/publish`, `/batch-week`

### Option 2: Global Skills (Work Everywhere)

Skills you want available in **every** Claude Code session, regardless of which project you're in:

```
~/.claude/skills/my-skill/SKILL.md
```

This is your **user-level skills directory** — Claude Code's official location for personal skills that persist across all projects.

**Use for:**
- Personal productivity workflows (`/daily-standup`)
- Cross-project utilities (`/git-cleanup`)
- Admin tools you use everywhere

**Example:**
```
~/.claude/skills/
├── daily-standup/SKILL.md    # Your morning routine
├── git-cleanup/SKILL.md      # Branch maintenance
└── review-pr/SKILL.md        # Your PR checklist
```

### Skill Priority

When the same skill name exists in multiple locations, Claude uses this priority:

1. **Project `.claude/skills/`** (highest priority)
2. **User `~/.claude/skills/`** (global)
3. **vip `.claude/skills/`** (shared engine)

This means you can override vip skills with your own version if needed.

| Location | Scope | Example Use |
|----------|-------|-------------|
| `your-repo/.claude/skills/` | One project | `/notion-export` for this business |
| `~/.claude/skills/` | All projects | `/daily-standup` everywhere |
| `vip/.claude/skills/` | Shared (read-only) | `/ads`, `/think`, `/start` |

See [becoming-contributor.md](becoming-contributor.md) to contribute skills back to vip.
