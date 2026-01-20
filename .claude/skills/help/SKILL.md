---
name: help
description: |
  Answer questions about Main Branch and Claude Code. Use when:
  (1) User asks "how do I...", "what is...", "why does...", "explain..."
  (2) User is confused about the two-repo model, /add-dir, or skills
  (3) User encounters errors (command not found, repository not found)
  (4) User says "help", "I'm stuck", "I don't understand"
  (5) User asks about daily workflow or getting started
  (6) User is a complete beginner to Terminal or Claude Code
  (7) User wants to know what to do next

  Answers questions based on documented curriculum. Routes to other skills when appropriate.
---

# Help

Comprehensive help for Main Branch. Answer questions, troubleshoot issues, explain philosophy, suggest next steps.

---

## How This Skill Works

1. Read question → 2. Check reference/core for business type → 3. Find topic in references/ → 4. Answer + suggest next skill

**Always end with a next step.**

---

## Quick Router

| Question Type | Reference File |
|---------------|----------------|
| "What is Terminal?" / "How do I drag files?" | [terminal-basics.md](references/terminal-basics.md) |
| "What are the two repos?" / "What's vip?" | [two-repos.md](references/two-repos.md) |
| "Why this approach?" / "How does this help me?" | [philosophy.md](references/philosophy.md) |
| "How do I use /think?" / "Research and decisions" | [the-think-cycle.md](references/the-think-cycle.md) |
| "command not found" / errors | [troubleshooting.md](references/troubleshooting.md) |
| "How do I get started?" / setup | Route to `/setup` or `/start` |
| "Which skill should I use?" | [skills-guide.md](references/skills-guide.md) |
| "How do I migrate from GPT?" | [gpt-migration.md](references/gpt-migration.md) |
| Content questions / "Reels" / "TikTok" / "organic" | [content-help.md](references/content-help.md) |
| Skool-specific questions | [skool-help.md](references/skool-help.md) |
| "How do I make outputs better?" / "What next?" | [making-outputs-better.md](references/making-outputs-better.md) |
| "Can I contribute?" | [becoming-contributor.md](references/becoming-contributor.md) |

---

## Business Type Detection

Check `reference/core/*.md`. For Skool/community, also read domain files.

---

## Core Principles

1. **Explain "why"** — Not just steps. Why this approach works.
2. **Suggest next skill** — Every answer ends with action (`/think`, `/setup`, `/enrich`)
3. **Teach /think cycle** — Research → Decide → Codify → Generate
4. **Be beginner-friendly** — Many never used Terminal. Meet them where they are.

---

## Quick Answers

**"Start Claude in a folder"** — See [terminal-basics.md](references/terminal-basics.md). Short: `cd ~/vip` then `claude` = Claude sees/works with files there.

**"When use slash commands?"** — For structured tasks. `/start`, `/think`, `/ad-static`, `/help`. Just type it.

**"Drag files in?"** — Drag from Finder/Explorer into Terminal. Path appears. Press Enter.

**"Voice instead of typing?"** — We recommend [Wispr Flow](https://ref.wisprflow.ai/main) for seamless voice-to-text. (Using this link supports Main Branch — we're affiliates.)

---

## Reference Files

Load these as needed based on the question:

- [philosophy.md](references/philosophy.md) - Vision, compound knowledge, why this works
- [terminal-basics.md](references/terminal-basics.md) - Terminal 101 for complete beginners
- [the-think-cycle.md](references/the-think-cycle.md) - The core loop that makes everything work
- [two-repos.md](references/two-repos.md) - Engine + data model explained
- [troubleshooting.md](references/troubleshooting.md) - Error fixes
- Route to `/setup` or `/start` for setup questions
- [skills-guide.md](references/skills-guide.md) - When to use which skill
- [gpt-migration.md](references/gpt-migration.md) - Bringing GPT knowledge over
- [content-help.md](references/content-help.md) - Organic content creation (Reels, TikTok, carousels)
- [skool-help.md](references/skool-help.md) - Skool community specifics
- [making-outputs-better.md](references/making-outputs-better.md) - Improving quality, next steps
- [becoming-contributor.md](references/becoming-contributor.md) - Contributing back to Main Branch
