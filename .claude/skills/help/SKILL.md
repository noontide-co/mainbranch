---
name: help
description: "Answer questions about Main Branch and Claude Code. Use when: user asks how/what/why questions, is confused about two-repo model or skills, encounters errors, says help or stuck, asks about workflow, is a beginner, or wants to know what to do next."
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
| Reels, TikTok, organic, /organic | [organic-help.md](references/organic-help.md) |
| Skool, community | [skool-help.md](references/skool-help.md) |
| Wiki, atomic notes, publish, WikiLinks | Route to `/wiki` |
| Done, wrapping up, closing, end session, end of day | Route to `/end` |
| Better outputs, quality, what next | [making-outputs-better.md](references/making-outputs-better.md) |
| Content strategy, pillars, platforms, newsletter, content plan | [content-strategy-help.md](references/content-strategy-help.md) |
| Subagents, parallel, agents, context window, tokens | [working-with-agents.md](references/working-with-agents.md) |
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
| What is content-strategy.md? | Your distribution backbone -- pillars, platforms, cadence. Built through `/think`, consumed by `/organic` and `/ads`. Lives in `reference/domain/`. |
| How do I build a content strategy? | Run `/think`. Start by deriving 3-5 pillars from your soul.md + offer.md + audience.md. Then choose platforms, set cadence, and fill in over time. |
| How do pillars work? | Each pillar is a content theme that passes three tests: Soul test (connects to why), Offer test (leads to mechanism), Audience test (they care). 3-5 pillars cover your content universe. |
| What's the content pipeline? | Newsletter-first: write one keystone piece weekly, then `/organic` adapts it for social platforms, `/ads` amplifies top performers. One idea, many formats. |
| What are subagents? | Claude can spawn parallel agents to research or review simultaneously. You'll see it happen automatically in `/think` (multi-source research) and `/ads review` (6 compliance lenses). Each agent gets its own context window so your main conversation stays clean. |
| How do I manage context/tokens? | When context gets heavy, break work into parallel subagents. Heavy research (transcripts, mining) runs in subagents so raw content stays out of your main conversation. Synthesized summaries come back instead. Re-invoke `/think` after compaction to reload context. |
| How do I close a session? | Run `/end`. It summarizes what happened, asks if you have final thoughts, offers a crystallize moment if you made decisions, commits uncommitted work, and says goodbye. Bookend to `/start`. |
