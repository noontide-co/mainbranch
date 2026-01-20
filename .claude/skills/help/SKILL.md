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

1. Read the user's question
2. Detect their business type (if relevant) by checking reference/core files
3. Find the relevant topic in references/
4. Answer clearly, explain the "why", suggest next skill

**Always end with a next step.** Don't just answer - empower them to take action.

---

## Quick Router

| Question Type | Reference File |
|---------------|----------------|
| "What is Terminal?" / "How do I drag files?" | [terminal-basics.md](references/terminal-basics.md) |
| "What are the two repos?" / "What's vip?" | [two-repos.md](references/two-repos.md) |
| "Why this approach?" / "How does this help me?" | [philosophy.md](references/philosophy.md) |
| "How do I use /think?" / "Research and decisions" | [the-think-cycle.md](references/the-think-cycle.md) |
| "command not found" / errors | [troubleshooting.md](references/troubleshooting.md) |
| "How do I get started?" / setup | [getting-started.md](references/getting-started.md) |
| "Which skill should I use?" | [skills-guide.md](references/skills-guide.md) |
| "How do I migrate from GPT?" | [gpt-migration.md](references/gpt-migration.md) |
| Content questions / "Reels" / "TikTok" / "organic" | [content-help.md](references/content-help.md) |
| Skool-specific questions | [skool-help.md](references/skool-help.md) |
| "How do I make outputs better?" / "What next?" | [making-outputs-better.md](references/making-outputs-better.md) |
| "Can I contribute?" | [becoming-contributor.md](references/becoming-contributor.md) |

---

## Business Type Detection

Some questions need business-type context. Check if reference/core exists:

```bash
ls reference/core/*.md 2>/dev/null
```

If Skool/community business, also read relevant domain files for context before answering Skool-specific questions.

---

## Core Principles When Answering

### 1. Explain the "Why"

Don't just give steps. Explain why this approach works:
- "This matters because..."
- "The benefit of recording this is..."
- "This compounds over time because..."

### 2. Always Suggest a Skill

Every answer should end with a next action:
- "Try running `/think` to research this further"
- "Use `/setup` to get your repo created"
- "Run `/enrich` to add this new context"

### 3. Teach the /think Cycle

Many questions are actually opportunities to teach the core loop:
- Research → Investigate the question
- Decide → Make a choice with rationale
- Codify → Update reference files
- Generate → Create outputs from reference

When someone asks a complex "how do I..." question, suggest they run `/think` to work through it properly.

### 4. Be Beginner-Friendly

Assume nothing. Many users:
- Have never used Terminal
- Don't know what "cd" means
- Don't understand file paths
- Are used to ChatGPT's passive memory

Meet them where they are.

---

## Quick Answers (Most Common)

### "What does 'start Claude in a folder' mean?"

See [terminal-basics.md](references/terminal-basics.md) for full explanation.

Short version: Terminal is a text-based way to interact with your computer. When you type `cd ~/Documents/GitHub/vip` and then `claude`, you're telling Claude to start "in" that folder - meaning it can see and work with files there.

### "When do I use slash commands?"

Anytime you want Claude to do something structured. Slash commands load specialized instructions.

Examples:
- `/start` - Begin a session, load your business repo
- `/think` - Research a topic, make a decision
- `/ad-static` - Generate ad copy
- `/help` - Get answers (you're using it now)

Just type the command. Claude will take it from there.

### "How do I drag files in?"

Literally drag a file from Finder (Mac) or Explorer (Windows) into the Terminal window. The file path appears. Press Enter.

You can also drag folders to add them as working directories.

### "Can I use voice instead of typing?"

Yes. Mac has built-in dictation:
1. Press Fn twice (or the mic key on newer Macs)
2. Speak
3. Press Fn again to stop

Or use any dictation software that types text.

---

## Reference Files

Load these as needed based on the question:

- [philosophy.md](references/philosophy.md) - Vision, compound knowledge, why this works
- [terminal-basics.md](references/terminal-basics.md) - Terminal 101 for complete beginners
- [the-think-cycle.md](references/the-think-cycle.md) - The core loop that makes everything work
- [two-repos.md](references/two-repos.md) - Engine + data model explained
- [troubleshooting.md](references/troubleshooting.md) - Error fixes
- [getting-started.md](references/getting-started.md) - Setup guide
- [skills-guide.md](references/skills-guide.md) - When to use which skill
- [gpt-migration.md](references/gpt-migration.md) - Bringing GPT knowledge over
- [content-help.md](references/content-help.md) - Organic content creation (Reels, TikTok, carousels)
- [skool-help.md](references/skool-help.md) - Skool community specifics
- [making-outputs-better.md](references/making-outputs-better.md) - Improving quality, next steps
- [becoming-contributor.md](references/becoming-contributor.md) - Contributing back to Main Branch
