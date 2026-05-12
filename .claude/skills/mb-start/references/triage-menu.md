# Triage Menu and Routing (Step 3)

Detail for Step 3 of /mb-start: presenting the menu, surfacing unread CHANGELOG entries, spawning triage agents, and the "while you wait" pattern.

---

## Surfacing CHANGELOG Entries (Before the Menu)

Resolve the Main Branch path with the shared path resolution
reference, then read `$ENGINE_PATH/CHANGELOG.md`. Read `last_seen_version` from
current Main Branch local state when available; if only legacy
`~/.config/vip/local.yaml` exists, use it as a read-only fallback. If the
most-recent versioned heading in CHANGELOG (the first `## [X.Y.Z]` after
`[Unreleased]`) differs from `last_seen_version`, render a one-line "What's
new" banner above the menu. Format:

```
─── What's new in <version> ───
<one-line headline derived from the section's most prominent Added bullet>
<one-line tail derived from the next bullet, trimmed>
────────────────────────────────
```

If `last_seen_version` matches the current version, skip the banner entirely. If `last_seen_version` is empty (new user), surface the banner once and bump it on engagement.

**Mark seen** when:
- The user routes into a skill (any skill — version surface is per-engine, not per-skill)
- The user types "dismiss" / "seen" / "got it"
- The banner has been surfaced this session and the user moves on

Mark the version seen through current Main Branch local state when that surface
exists. Do not write legacy `~/.config/vip/local.yaml`; if there is no current
write path, treat the banner as session-scoped.

**Why version-based, not slug-based:** the prior `seen_announcements` list grew without bound and required per-feature housekeeping. A single `last_seen_version` field auto-clears on every release and never drifts.

---

## The Menu

If user is ready to work, ask or infer intent. Use numbered options only when
this is the single active choice list in the response. If ranked actions were
already numbered or offers are also being shown, use a named route such as
`triage` instead of reusing `1`.

### Triage (User-Initiated)

**Triage is option 1 only on the main route menu.** It runs when the user
selects that route or when intent keywords match. It does NOT run automatically
every session. This keeps /mb-start fast and preserves context for actual work.
Never make `1` mean triage if `1` already means a ranked recommendation or an
offer selection in the same turn.

**Why not always-on:** Three parallel agents burn 50-80K tokens. Running them every session means the user starts at 60%+ context before doing anything. /mb-end gates crystallize behind meaningful activity — /mb-start gates triage behind user choice.

**Present the menu:**

> "What would you like to do?
>
> 1. **What should I focus on?** (triage — analyzes your full state) → see [triage-agent.md](triage-agent.md)
> 2. Enrich the core (research, decide, codify) → `/mb-think`
> 3. Create ads (image or video) → `/mb-ads`
> 4. Build a conversion surface (site or video ad) → `/mb-site` or `/mb-ads`
> 5. Create organic content → `/mb-organic`
> 6. Work on my wiki → `/mb-wiki`
> 7. Build/update a site → `/mb-site`
> 8. Add more context → `/mb-think codify`
> 9. Get help → `/mb-help`
>
> (hit a number, or just tell me what you need)"

**When user picks the triage route:** Spawn triage agents. See
[triage-agent.md](triage-agent.md) for gating, tiered spawning, agent prompts,
and synthesis format.

---

## "While You Wait" Pattern

Set expectations, then keep the operator anchored in current business facts:

> "Spinning up [1/2/3] analysis agents — this takes about **2-3 minutes**. They're reading your full reference, decisions, git history, and soul alignment so I can give you something actually useful.
>
> While that runs, here's the compact state I already trust:
> - [top ranked action or stated intent]
> - [main readiness or repair signal]
> - [one continuity fact from journal/status]"

---

## When to Auto-Suggest / Skip Triage

**Auto-suggest triage when:**
- Returning user (last saved checkpoint or status journal event is older than 3 days) and no stated intent
- Readiness is THIN (8-11) — "Triage can help you figure out the highest-leverage gap"
- User says "what should I work on", "help me prioritize", "what to do next"

**Skip triage entirely when:**
- Readiness is EMPTY or MINIMAL (0-7) — answer is obvious: `/mb-setup` or `/mb-think`
- User stated clear intent with `/mb-start ads` or similar

If user already stated intent, route directly without asking.
