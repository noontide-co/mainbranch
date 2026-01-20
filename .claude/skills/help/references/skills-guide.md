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

### /enrich - Add More Context
**Use when:** You have new information to add, reference files are thin, business has changed.

**What it does:**
- Audits your existing files
- Shows what's missing or incomplete
- Gathers new context from you
- Merges into existing files (never overwrites)

**Regular use:** Run whenever you have new testimonials, angles, or updates.

---

### /think - Research and Decisions
**Use when:** Exploring a question, making a strategic decision, need to document rationale.

**What it does:**
- Researches topics (web, your files, your input)
- Synthesizes findings
- Helps you make decisions
- Records everything to files
- Updates reference when you codify

**Heavy use:** This is the core skill. Use it for any "should we...?" question.

See [the-think-cycle.md](the-think-cycle.md) for deep dive.

---

### /ad-static - Image Ad Copy
**Use when:** Need copy for static/image ads (Facebook, Instagram, etc.).

**What it does:**
- Reads your reference files
- Generates multiple ad concepts
- Creates primaries (main text), headlines, image prompts
- Outputs organized batches

**Output:** 5-6 distinct concepts, each with variations.

---

### /ad-video-scripts - Video Ad Scripts
**Use when:** Need scripts for video ads (15-60 seconds, UGC style).

**What it does:**
- Reads your reference files
- Generates spoken-word scripts
- Optimizes for camera delivery
- Creates hook variations

**Output:** 15-30+ diverse scripts.

---

### /ad-review - Compliance Check
**Use when:** Before running ads, want to check for issues.

**What it does:**
- Runs multiple review "lenses" in parallel
- Checks FTC compliance
- Checks Meta policy
- Reviews copy quality
- Checks voice authenticity
- Identifies claims that need proof

**Output:** P1/P2/P3 prioritized report of issues.

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
├── Add new context?
│   └── /enrich
│
├── Research or decide something?
│   └── /think
│
├── Create ad copy?
│   ├── Image ads → /ad-static
│   └── Video scripts → /ad-video-scripts
│
├── Check ads before running?
│   └── /ad-review
│
├── Confused or stuck?
│   └── /help
│
└── Skool community tasks?
    └── /skool-manager
```

---

## Skill Combinations

Common workflows:

**New campaign:**
1. `/think` - Research your angle
2. `/ad-static` or `/ad-video-scripts` - Generate copy
3. `/ad-review` - Check before running

**Learning from results:**
1. `/think research` - Document what worked
2. `/enrich` - Add winning angles to reference
3. Next campaign uses updated reference

**Business evolution:**
1. `/think` - Decide on offer change
2. `/enrich` - Update reference with decision
3. Future outputs reflect new offer

---

## When You're Not Sure

If you don't know which skill to use:

1. Run `/start` - It'll detect your state and suggest
2. Ask `/help` - Describe what you want to accomplish
3. Run `/think` - If it's a question worth exploring

Most of the time, `/start` will point you in the right direction.

---

## Creating Your Own Skills

As you use Main Branch, you might want custom skills for your specific workflows. This is possible and encouraged. Ask about becoming a contributor or explore the skill-creator resources.
