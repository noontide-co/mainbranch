---
name: help
description: Answer questions about Main Branch and Claude Code. Use when: (1) User asks "how do I...", "what is...", "why does...", "explain..." (2) User is confused about the two-repo model, /add-dir, or skills (3) User encounters errors (command not found, repository not found) (4) User says "help", "I'm stuck", "I don't understand" (5) User asks about daily workflow or getting started (6) User is a complete beginner to Terminal or Claude Code (7) User wants to know what to do next (8) User brain-dumps a question — triage intent and answer or route. Answers questions based on documented curriculum. Routes to other skills when appropriate.
---

# Help

Answer questions, troubleshoot issues, explain philosophy, suggest next steps.

---

## Workflow

1. **Triage** — Parse user's question/brain-dump
2. **Detect business type** — Check `reference/core/*.md` (Skool? Ecommerce?)
3. **Load reference** — Find topic in references/ table below
4. **Answer** — Explain "why" not just "what"
5. **Route** — End with next skill or action

---

## Topic Router

| Keywords | Reference |
|----------|-----------|
| Terminal, drag files, cd, folder | [terminal-basics.md](references/terminal-basics.md) |
| Two repos, vip, engine, data model | [two-repos.md](references/two-repos.md) |
| Philosophy, why, compound, passive memory | [philosophy.md](references/philosophy.md) |
| /think, research, decide, codify | [the-think-cycle.md](references/the-think-cycle.md) |
| Task tracking, where left off, focus | [task-tracking-options.md](references/task-tracking-options.md) |
| Error, command not found, MCP, Apify setup | [troubleshooting.md](references/troubleshooting.md) |
| Getting started, setup | Route to `/setup` or `/start` |
| Which skill, when to use | [skills-guide.md](references/skills-guide.md) |
| Create skill, Notion export, custom | [skills-guide.md](references/skills-guide.md) |
| Migrate from GPT, ChatGPT | [gpt-migration.md](references/gpt-migration.md) |
| Reels, TikTok, organic, /content | [content-help.md](references/content-help.md) |
| Skool, community | [skool-help.md](references/skool-help.md) |
| Better outputs, quality, what next | [making-outputs-better.md](references/making-outputs-better.md) |
| Contribute, contributor | [becoming-contributor.md](references/becoming-contributor.md) |

---

## Principles

- **Explain "why"** — Not just steps
- **End with action** — Suggest next skill (`/think`, `/setup`, `/ads`, `/vsl`)
- **Beginner-friendly** — Many never used Terminal

---

## Quick Answers

| Question | Answer |
|----------|--------|
| Start Claude in a folder? | `cd ~/vip && claude` — Claude sees files in that folder |
| When use slash commands? | For structured tasks: `/start`, `/think`, `/ads`, `/vsl` |
| Drag files in? | Drag from Finder into Terminal, path appears |
| Voice input? | [Wispr Flow](https://ref.wisprflow.ai/main) (affiliate link) |
