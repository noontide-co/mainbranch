# Triage Menu and Routing (Step 3)

Detail for Step 3 of /start: presenting the menu, surfacing announcements, spawning triage agents, and the "while you wait" pattern.

---

## Surfacing Announcements (Before the Menu)

Read `<vip_path>/.claude/announcements.md` and `~/.config/vip/local.yaml:seen_announcements` (a list of slug strings). For each `## <slug>` entry whose:
- `expires` date is today or later, AND
- `<slug>` is NOT in `seen_announcements`

…render a one-line "What's new" banner above the menu. Format:

```
─── What's new ───
[NEW] <title>
<2-line body>
─────────────────
```

If there are 2+ unseen entries, list them stacked (newest first). If there are 0, skip the banner entirely.

**Mark seen** when the user routes to the announced skill, or types "dismiss" / "seen" / "got it". Append the slug to `seen_announcements` in `~/.config/vip/local.yaml` via the safe-write pattern in [config-system.md](config-system.md). The list grows over time; expired entries auto-stop surfacing without needing to be removed.

**Add `[NEW]` badge to menu options.** If an unseen announcement targets a specific skill (`skill: /<skill-name>` in announcements.md), append `  [NEW]` to that menu line.

---

## The Menu

If user is ready to work, ask or infer intent. **Use numbered options:**

### Triage (Option 1 — User-Initiated)

**Triage is option 1 on the menu.** It runs when the user selects it or when intent keywords match. It does NOT run automatically every session. This keeps /start fast and preserves context for actual work.

**Why not always-on:** Three parallel agents burn 50-80K tokens. Running them every session means the user starts at 60%+ context before doing anything. /end gates crystallize behind meaningful activity — /start gates triage behind user choice.

**Present the menu:**

> "What would you like to do?
>
> 1. **What should I focus on?** (triage — analyzes your full state) → see [triage-agent.md](triage-agent.md)
> 2. Enrich the core (research, decide, codify) → `/think`
> 3. Create ads (image or video) → `/ads`
> 4. Write a VSL script → `/vsl`
> 5. Create organic content → `/organic`
> 6. Work on my wiki → `/wiki`
> 7. Build/update a site → `/site`
> 8. Add more context → `/think codify`
> 9. Get help → `/help`
>
> (hit a number, or just tell me what you need)"

**When user picks option 1:** Spawn triage agents. See [triage-agent.md](triage-agent.md) for gating, tiered spawning, agent prompts, and synthesis format.

---

## "While You Wait" Pattern

Set expectations, then give them something to chew on:

> "Spinning up [1/2/3] analysis agents — this takes about **2-3 minutes**. They're reading your full reference, decisions, git history, and soul alignment so I can give you something actually useful.
>
> **Good news:** These run as sub-agents in their own context windows, so they won't eat into your session. You'll still have plenty of room for whatever comes next.
>
> While we wait: [pick ONE at random per session]
> - *The word 'decide' comes from Latin 'decidere' — literally 'to cut off.' Every decision is choosing what to let go of.*
> - *Hemingway rewrote the ending of A Farewell to Arms 47 times. When asked why, he said: 'Getting the words right.'*
> - *The best time to plant a tree was 20 years ago. The second best time is now.*
> - *Your reference files are like compound interest — small deposits now, massive returns later.*
> - *'If you can't explain it simply, you don't understand it well enough.' — Einstein. That's what codifying does.*
> - *Fun fact: the average person mass-produces 50K+ words a day in their head. You're one of the few who actually filters those into something useful.*"

---

## When to Auto-Suggest / Skip Triage

**Auto-suggest option 1 when:**
- Returning user (last commit >3 days ago) and no stated intent
- Readiness is THIN (8-11) — "Option 1 can help you figure out the highest-leverage gap"
- User says "what should I work on", "help me prioritize", "what to do next"

**Skip triage entirely when:**
- Readiness is EMPTY or MINIMAL (0-7) — answer is obvious: `/setup` or `/think`
- User stated clear intent with `/start ads` or similar

If user already stated intent, route directly without asking.
