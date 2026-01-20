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

Answer questions, troubleshoot, explain philosophy, suggest next steps.

---

## Workflow

1. Read question
2. Detect business type (check reference/core)
3. Load relevant reference file
4. Answer clearly + suggest next skill

**Always end with a next step.**

---

## Quick Router

| Question Type | Reference |
|---------------|-----------|
| Terminal basics, drag files | [terminal-basics.md](references/terminal-basics.md) |
| Two repos, what's vip | [two-repos.md](references/two-repos.md) |
| Why this approach | [philosophy.md](references/philosophy.md) |
| /think, research, decisions | [the-think-cycle.md](references/the-think-cycle.md) |
| Errors, troubleshooting | [troubleshooting.md](references/troubleshooting.md) |
| Getting started, setup | [getting-started.md](references/getting-started.md) |
| Which skill to use | [skills-guide.md](references/skills-guide.md) |
| Migrate from GPT | [gpt-migration.md](references/gpt-migration.md) |
| Content, Reels, TikTok | [content-help.md](references/content-help.md) |
| Skool questions | [skool-help.md](references/skool-help.md) |
| Making outputs better | [making-outputs-better.md](references/making-outputs-better.md) |
| Contributing | [becoming-contributor.md](references/becoming-contributor.md) |

---

## Answering Principles

### 1. Explain Why
- "This matters because..."
- "This compounds because..."

### 2. Suggest Next Skill
- "Try `/think` to research further"
- "Run `/enrich` to add context"

### 3. Teach /think Cycle
Research → Decide → Codify → Generate

Complex questions → suggest `/think`

### 4. Be Beginner-Friendly
Many users have never used Terminal. Meet them where they are.

---

## Quick Answers

**"Start Claude in a folder"?**
Terminal = text interface. `cd ~/path/to/vip` then `claude` = Claude sees those files.

**When use slash commands?**
Anytime you want structured action. `/start`, `/think`, `/ad-static`, `/help`.

**Drag files?**
Drag from Finder/Explorer into Terminal. Path appears. Press Enter.

**Voice instead of typing?**
Mac: Fn twice → speak → Fn again. Or any dictation software.
