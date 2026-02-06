# Readiness Assessment Reference

Complete reference for the readiness assessment run by `/start` at Step 0.9. Contains scoring rubric, session state check, soul health check, routing gates, skill-specific readiness, and display format.

---

## 1. Reference File Scoring

Score each file by reading it directly (fast -- no subagent needed). Use line count as primary signal, section markers as quality signal.

### Scoring Rubric

| File | 0 (Missing) | 1 (Skeleton) | 2 (Developing) | 3 (Strong) |
|------|-------------|---------------|-----------------|-------------|
| `soul.md` | File missing or empty | <30 lines | 30-80 lines | 80+ lines OR has "Beliefs" section |
| `offer.md` | File missing or empty | <20 lines | 20-80 lines | 80+ lines OR has "Price" section |
| `audience.md` | File missing or empty | <30 lines | 30-60 lines | 60+ lines OR has "Pains" section |
| `voice.md` | File missing or empty | <20 lines | 20-50 lines | 50+ lines OR has "Never Say" section |
| `testimonials.md` | File missing or empty | <5 testimonials | 5-10 testimonials | 10+ testimonials |
| `angles/` | 0 files (or missing dir) | 1 file | 2-3 files | 4+ files |

### How to Score

1. **Read each file** with the Read tool. If the read fails or returns empty, score 0.
2. **Count lines** for the primary threshold check.
3. **Check for section markers** (case-insensitive grep for key headings) as a quality override -- a 25-line soul.md with a "Beliefs" section shows intentional work and scores 2, not 1.
4. **For testimonials:** Count occurrences of `###` or `**"` patterns that indicate individual testimonials.
5. **For angles:** Count `.md` files in `reference/proof/angles/`, excluding `README.md`.

### Multi-Offer Scoring

When `.vip/local.yaml` has `current_offer` set:

1. Score `reference/core/soul.md` and `reference/core/voice.md` from core (these are always brand-level).
2. For offer and audience, resolve using the canonical path algorithm:
   - Check `reference/offers/[current_offer]/offer.md` first. If it exists, score it.
   - If it does not exist, score `reference/core/offer.md`.
   - Same for `audience.md`.
3. Testimonials and angles: check both `reference/proof/` (brand-level) and `reference/offers/[current_offer]/` if offer-specific proof exists.

### Composite Score

Sum all six scores. Maximum = 18.

```
composite = soul + offer + audience + voice + testimonials + angles
```

---

## 2. Session State Check

Surface what happened recently so the user sees continuity, not a blank slate.

### Recent Activity

```bash
# What happened in the last few sessions?
git log --since="7 days ago" --oneline --no-merges 2>/dev/null | head -10
```

If commits exist, summarize in one line: "Last session: [topic from most recent commit message]"

If no commits in 7+ days, note the gap -- this feeds into the soul health check (Section 3).

### Open Decisions

```bash
# Decisions with status: proposed or accepted (not yet codified)
grep -rl "status: proposed\|status: accepted" decisions/ 2>/dev/null
```

For each found, read the frontmatter to extract the topic. Present as:

> "You have [N] open decisions ready to codify: [topic 1], [topic 2]."

**Why this matters:** Uncodified decisions are the highest-value pending work. Research goes stale. Decisions capture reasoning at a point in time. Codifying locks insights into reference before they decay.

### Uncodified Research

```bash
# Research files without linked_decisions (simplified check)
for f in research/*.md; do
  if [ -f "$f" ]; then
    grep -q "linked_decisions: \[\]" "$f" && echo "$f"
  fi
done 2>/dev/null
```

If found, note it gently:

> "[N] research files haven't led to decisions yet. May be worth reviewing."

Do not nag. Some research is exploratory and never needs a decision. This is informational.

### Content Strategy Gap

```bash
# Does content-strategy.md exist and have substance?
wc -l reference/domain/content-strategy.md 2>/dev/null
```

If missing or <10 lines, note it -- but only for businesses that would benefit (community, coaching, content-driven). Not relevant for pure e-commerce.

---

## 3. Soul Health Check

Modeled on /end's crystallize pattern. For returning users, reconnection at session open is as important as reflection at session close.

### When to Trigger

**Trigger conditions (ALL must be true):**
1. `reference/core/soul.md` exists and has substance (score 2+)
2. Last commit was >3 days ago (returning after absence)
3. This is not the user's first session ever (config exists with `user.name`)

**Skip conditions (ANY skips this check):**
- First-time user (no config, no commits)
- Active user (committed within last 3 days)
- User explicitly stated intent already (e.g., `/start ads` -- they know what they want)
- Context window is already heavy (>70%)

### How to Check

```bash
# Days since last commit
git log -1 --format="%ar" 2>/dev/null
```

### The Ask

Read `reference/core/soul.md` (first 50 lines is enough to get the WHY). Then ask:

> "Welcome back. Your last session was [N] days ago.
>
> Quick check-in: Is your current work still feeling like pull or push? If things have shifted, we can revisit soul.md."

**Why this language:** "Pull or push" comes directly from soul.md's offer-fit test. Users who have written their soul.md will recognize this language. It is not generic coaching -- it references their own framework.

### If They Say Push/Obligation

This is valuable information. Do not dismiss it.

> "That's worth paying attention to. Some options:
>
> 1. Explore what shifted through /think
> 2. Review soul.md together and see if the offer still fits
> 3. Proceed anyway and revisit later
>
> (hit a number)"

If they choose 1 or 2, route to `/think` with the soul exploration context. If they choose 3, proceed normally but make a mental note -- the crystallize agent at `/end` should revisit this.

### If They Say Pull/Discovery

Brief acknowledgment, then move on:

> "Good. Let's keep building."

No ceremony. Get out of the way.

---

## 4. Smart Routing Gates

The readiness score determines which skills are available. This prevents users from jumping into output skills with thin reference -- the #1 source of bad outputs.

### Score Interpretation

| Composite | Status | Routing Behavior |
|-----------|--------|------------------|
| **0-3** | EMPTY | Route to `/setup`. "No reference files found. Let's set up your business repo." |
| **4-7** | MINIMAL | Block output skills. Route to `/think`. "Reference isn't ready for generating yet. Let's build the core first." |
| **8-11** | THIN | Warn before output skills. "Reference is thin. /ads and /organic work best with richer context. Want to enrich first with /think?" Allow override if user insists. |
| **12-14** | GOOD | All skills available. Note gaps: "Angles could use expansion" or "No content strategy yet." |
| **15-18** | FULL | All skills available. Present full options. |

### What "Block" Means

MINIMAL (4-7) does NOT show output skills in the numbered options list. If the user explicitly asks for /ads, explain why reference needs work first and offer to route to /think instead. They can override -- this is guidance, not enforcement.

### What "Warn" Means

THIN (8-11) shows output skills in the list but adds a note:

> "3. Create ads  /ads (reference is thin -- results will improve with richer context)"

### Open Decisions Override

If open decisions exist (status: proposed or accepted, not codified), surface them regardless of score:

> "You have [N] decisions ready to codify. Codifying locks in insights before they go stale. Want to finish those first?"

This is a suggestion, not a gate. User can proceed to any available skill.

### Content Strategy Nudge

If score is GOOD or FULL but `content-strategy.md` is missing or thin:

> "You have strong reference but no content strategy. When you're ready, /think can help build content-strategy.md -- pillars, platforms, cadence."

One-time mention per session. Do not repeat.

---

## 5. Skill-Specific Readiness

Beyond the composite score, some skills have specific requirements. Check these when routing to a specific skill.

### /ads

| Requirement | Minimum | Why |
|-------------|---------|-----|
| offer.md | Score 2+ | Needs pricing, mechanism, or clear value prop |
| audience.md | Score 2+ | Needs pain points to write hooks |
| voice.md | Score 1+ | Needs at least basic tone direction |
| 1+ angle file | Required | Angles frame the ad creative |

**If missing:** "To generate quality ads, I need [what's missing]. Want to build that through /think first?"

### /organic

| Requirement | Minimum | Why |
|-------------|---------|-----|
| offer.md | Score 2+ | Needs clear positioning |
| audience.md | Score 2+ | Needs to know who content is for |
| voice.md | Score 1+ | Organic content must sound authentic |
| content-strategy.md | Exists | Needs pillars and platform direction |

**If content-strategy.md missing:** "Organic content works best with a content strategy. Want to build one through /think? It defines your pillars, platforms, and cadence."

### /vsl

| Requirement | Minimum | Why |
|-------------|---------|-----|
| offer.md | Score 3 | VSLs need pricing, mechanism, guarantee, full offer stack |
| audience.md | Score 2+ | Needs psychographics for pain/desire framing |

**If offer thin:** "VSL scripts need a complete offer -- pricing, mechanism, guarantee. Your offer.md needs more depth. Route to /think to flesh it out?"

### /site

| Requirement | Minimum | Why |
|-------------|---------|-----|
| offer.md | Score 2+ | Landing pages need clear value prop |
| voice.md | Score 2+ | Site copy must sound right |

**If voice thin:** "Landing page copy needs strong voice direction. Your voice.md could use expansion. /think can help."

### /newsletter

| Requirement | Minimum | Why |
|-------------|---------|-----|
| content-strategy.md | Exists | Newsletter needs pillar framework |
| voice.md | Score 2+ | Long-form writing needs strong voice |

---

## 6. Display Format

How to present the readiness assessment to the user. Adapt by experience level.

### Beginner (experience: beginner)

Show the full breakdown with explanation:

> "**Repo Health: THIN** (score: 9/18)
>
> Here's where your reference files stand:
> - Soul: 2/3 (good start, could go deeper)
> - Offer: 2/3 (has basics, needs pricing detail)
> - Audience: 2/3 (developing)
> - Voice: 1/3 (skeleton -- needs tone and vocabulary)
> - Testimonials: 1/3 (a few captured)
> - Angles: 1/3 (one angle defined)
>
> Your reference files tell the AI about your business. Richer files = better output. Right now, you can use /think to enrich them. Output skills like /ads work best at score 12+."

### Intermediate (experience: intermediate)

Show the score with gaps highlighted:

> "**Repo Health: THIN** (9/18) -- voice and angles need work.
>
> [routing options]"

### Advanced (experience: advanced)

Score only, no explanation:

> "**9/18** -- voice (1), angles (1). Generating will be rough."

### When Score Is Good or Full

Keep it brief regardless of experience level:

> "**Repo Health: GOOD** (13/18). Ready to work."

Nobody needs a detailed breakdown when things are fine.

### Session State Display

If session state items were found, append after the health display:

> "**Since last session:**
> - Last work: [topic from recent commit]
> - [N] open decisions ready to codify
> - [N] research files without decisions"

Only show items that exist. Skip this section entirely if nothing to report.

---

## Anti-Patterns

### 1. Scoring As Audit

The readiness assessment is not a report card. It is a routing tool. Present it as "here's what you can do" not "here's what's wrong." The user should feel oriented, not judged.

### 2. Blocking Too Aggressively

MINIMAL blocks output skills from the numbered list but does not prevent the user from asking for them directly. If a user with a 6/18 score says "I want to run /ads," explain why reference matters and suggest /think -- but if they insist, let them. They will learn from the thin output.

### 3. Over-Explaining to Advanced Users

An advanced user does not need to hear what reference files are. "9/18 -- voice thin" is enough. Respect their time.

### 4. Skipping the Check Entirely

Even when the user states intent clearly ("/start ads"), run the scoring silently. If they are MINIMAL, the gate matters more than speed. If they are GOOD+, route immediately -- the check took 2 seconds and confirmed readiness.

### 5. Nagging About Research

"You have 12 research files without decisions" sounds like debt collection. Frame it as opportunity: "Some research from past sessions could inform decisions when you're ready."

### 6. Making Soul Health Check Feel Like Therapy

"Pull or push?" is a quick calibration, not a therapy session. Ask it. Accept the answer. Move on. If they want to go deeper, they will.

---

## See Also

- [../SKILL.md](../SKILL.md) -- The /start flow that invokes this assessment
- [config-system.md](config-system.md) -- Config reading for experience level and default repo
- [mcp-preflight.md](mcp-preflight.md) -- MCP check that runs before this assessment
- [../../end/references/crystallize-agent.md](../../end/references/crystallize-agent.md) -- The /end soul awareness pattern this assessment draws from
