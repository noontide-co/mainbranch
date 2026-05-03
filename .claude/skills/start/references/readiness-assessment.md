# Readiness Assessment Reference

Complete reference for the readiness assessment run by `/start` at Step 6. Contains scoring rubric, session state check, soul health check, routing gates, skill-specific readiness, and display format.

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

### Key Section Markers by File

When checking section markers, search for these headings (case-insensitive). These are the quality signals that distinguish skeleton files from intentional work:

| File | Key Sections to Detect |
|------|----------------------|
| `soul.md` | "Beliefs", "Anti-patterns", "Evolution Markers", "The Test", "The Parts" |
| `offer.md` | "Price" / "Pricing", "Mechanism", "Guarantee", "Value Stack", "Objections", "Deliverables" |
| `audience.md` | "Pains", "Desires", "Psychographics", "Language", "Objections", "Segments" |
| `voice.md` | "Never Say", "Vocabulary", "Rhythm", "Examples", "Tone", "Phrases" |
| `testimonials.md` | Count `###` or `**"` patterns (each indicates one testimonial) |

**How to use:** When a file scores 1 or 2 by line count, check for these markers to identify WHICH sections are missing. This drives the specific gap language in Section 7 and prevents hand-wavy gap messages like "voice.md is thin" when the real issue is "voice.md has no Never Say section."

### How to Score

**CRITICAL: Use absolute paths for ALL file reads and searches.** The repo path from Step 2 is an absolute path (e.g., `/Users/devon/Documents/GitHub/my-business`). Always use it — never use `~` or relative paths. The Glob and Read tools do not expand `~`, so `~/Documents/GitHub/repo/reference/proof` will silently return 0 results even when files exist.

1. **Read each file** with the Read tool using the absolute repo path (e.g., `[repo-path]/reference/core/soul.md`). If the read fails or returns empty, score 0.
2. **Count lines** for the primary threshold check.
3. **Check for section markers** (case-insensitive grep for key headings from the table above) as a quality override -- a 25-line soul.md with a "Beliefs" section shows intentional work and scores 2, not 1. Use specific markers to identify exactly what's missing.
4. **For testimonials:** Read `[repo-path]/reference/proof/testimonials.md`. Count occurrences of `###` or `**"` patterns (each indicates one testimonial).
5. **For angles:** Glob `[repo-path]/reference/proof/angles/*.md` to count files, excluding `README.md`.

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
# Decisions with frontmatter status: proposed or accepted (anchored parse)
for f in [repo-path]/decisions/*.md; do
  [ -f "$f" ] || continue
  status=$(awk 'NR==1&&$0=="---"{fm=1;next} fm&&$0=="---"{exit} fm&&/^status:[[:space:]]*/{val=$0; sub(/^status:[[:space:]]*/, "", val); gsub(/[[:space:]]+$/, "", val); print val; exit}' "$f")
  case "$status" in
    proposed|accepted) echo "$f" ;;
  esac
done 2>/dev/null
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

## 3. Health Flags

Lightweight metadata checks that catch common decay without reading full file contents. Run AFTER structural scoring (Section 1) and session state (Section 2). Adds 4-5 tool calls.

**Principle:** If you can detect it from metadata, frontmatter, or file stats — it belongs here. If you need to read and compare file *contents* — it belongs in triage.

### Check A: Frontmatter Status Scan (1 call)

```bash
grep -l "status: draft" [repo-path]/reference/core/*.md 2>/dev/null
```

Flag any file that scored 3/3 structurally but has `status: draft` in frontmatter. Highest-signal check — the user explicitly declared this file unfinished.

**Flag:** `! status: draft` (inline next to file)

### Check B: Staleness Detection (1 call)

```bash
git log --format="%ai" -1 -- [repo-path]/reference/core/soul.md [repo-path]/reference/core/offer.md [repo-path]/reference/core/audience.md [repo-path]/reference/core/voice.md
```

Flag any core file not modified in 30+ days. Not a score penalty — an observation.

**Flag:** `! stale (Xd)` (inline next to file)

### Check C: Angle Count Mismatch (1 call)

```bash
ls [repo-path]/reference/proof/angles/*.md 2>/dev/null
```

Compare actual .md file count (excluding README.md) against angles README if it exists. Flag if counts differ.

**Flag:** `! 3 files vs 5 in README` (inline next to angles row)

### Check D: Decision Lifecycle Audit (shared script)

```bash
# Resolve vip script path (settings.local.json first, then ~/.config/vip/local.yaml)
AUDIT_SCRIPT=$(python3 -c "
import json, os
path = '.claude/settings.local.json'
target = ''
try:
    with open(path) as f:
        dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
    for d in dirs:
        candidate = os.path.join(d, '.claude/scripts/decision_lifecycle_audit.sh')
        if os.path.isfile(candidate):
            target = candidate
            break
except Exception:
    pass
print(target)
" 2>/dev/null)

if [ -z "$AUDIT_SCRIPT" ] && [ -f "$HOME/.config/vip/local.yaml" ]; then
  vip_path=$(awk -F': *' '/^vip_path:/ {print $2; exit}' "$HOME/.config/vip/local.yaml" | tr -d '"')
  [ -n "$vip_path" ] && AUDIT_SCRIPT="$vip_path/.claude/scripts/decision_lifecycle_audit.sh"
fi

if [ -n "$AUDIT_SCRIPT" ] && [ -f "$AUDIT_SCRIPT" ] && bash "$AUDIT_SCRIPT" --repo "[repo-path]" --format text; then
  : # Shared script output includes machine-friendly summary + human bucket lines
else
  echo "Decision lifecycle audit unavailable; falling back to strict frontmatter counts."
  codified=0
  accepted=0
  invalid_or_missing=0

  for f in [repo-path]/decisions/*.md; do
    [ -f "$f" ] || continue
    status=$(awk 'NR==1&&$0=="---"{fm=1;next} fm&&$0=="---"{exit} fm&&/^status:[[:space:]]*/{val=$0; sub(/^status:[[:space:]]*/, "", val); gsub(/[[:space:]]+$/, "", val); print val; exit}' "$f")
    case "$status" in
      codified) codified=$((codified + 1)) ;;
      accepted) accepted=$((accepted + 1)) ;;
      proposed) ;;
      *) invalid_or_missing=$((invalid_or_missing + 1)) ;;
    esac
  done

  printf "Decisions: %s codified, %s accepted\n" "$codified" "$accepted"
  [ "$invalid_or_missing" -gt 0 ] && printf "Decisions with invalid/missing status: %s\n" "$invalid_or_missing"
fi
```

Use `.claude/scripts/decision_lifecycle_audit.sh` as the single source of truth for lifecycle classification in both `/start` and `/end`.
The script parses frontmatter only (between `---` delimiters), ignores body `status:` text, classifies accepted decisions into `needs_review|action_needed|stale_orphaned`, and reports invalid/missing status explicitly.
Never auto-flip statuses from evidence alone. Status changes remain manual-confirmed.

**Flag:** `Decisions: X codified, Y accepted` (below file scores)
**Flag:** `Needs review: N` (accepted with implementation evidence)
**Flag:** `Action needed: A` (accepted with no evidence and not stale)
**Flag:** `Stale/orphaned: S` (accepted, stale threshold crossed, weak/no evidence)
**Flag:** `Decisions with invalid/missing status: I` (only when `I > 0`)

### Check E: Naming Convention Spot-Check (1 call)

```bash
ls [repo-path]/research/ [repo-path]/decisions/ 2>/dev/null
```

Pattern-match filenames against `YYYY-MM-DD-slug.md`. Only flag if >20% violations.

**Flag:** `Naming: X% violations in research/` (below file scores)

### Display Rules

- Maximum 5 flags total
- File-level flags (A, B, C) appear inline next to the relevant file score
- Pipeline flags (D, E) appear as a separate line below file scores
- No "WARNING" or "ISSUE" language — factual observations only
- If any flags exist, append: "Pick option 1 for deeper analysis"
- Flags inform; they do NOT gate routing or change the structural score

---

## 4. Soul Health Check

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

## 5. Smart Routing Gates

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

## 6. Skill-Specific Readiness

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

**If voice thin:** "Landing page copy needs strong voice direction. `/site` walks brief→site as one flow and will pull from your `voice.md` — but if it's thin, the output will be too. You can keep going (`/site` has its own brief phase) or strengthen voice first via `/think`."

### /newsletter

| Requirement | Minimum | Why |
|-------------|---------|-----|
| content-strategy.md | Exists | Newsletter needs pillar framework |
| voice.md | Score 2+ | Long-form writing needs strong voice |

---

## 7. Display Format

How to present the readiness assessment to the user. Adapt by experience level.

**Core principle: Every gap must be actionable.** The formula for any file scoring below 3:

```
[Specific missing section/file] + [What it unlocks downstream] + [Concrete offer to fix it now]
```

### Gap Display Rules

1. **For ANY score below 18:** Identify exactly which files scored below 3.
2. **For each gap:** Say what specific section or content is missing, what filling it would unlock for downstream skills, and offer to fix it right there.
3. **Use the per-file gap tables from Section 8** to determine the specific gap language for each file at each score level.
4. **Group gaps under a "Gaps:" heading** after the score line.

### Beginner (experience: beginner)

Show the score, then list each gap with full actionable detail:

> "**Repo Health: THIN** (score: 9/18)
>
> Your reference files tell the AI about your business. Richer files = better output. Output skills like /ads work best at score 12+.
>
> **Gaps:**
> - **voice.md** (1/3): Missing "Never Say" section -- this is the #1 guard rail for authentic output. Want me to ask you 3 questions to build it? (~5 min)
> - **testimonials.md** (1/3): Only 2 testimonials. More proof = better ads. Have screenshots or messages to add?
> - **angles/** (1/3): 1 angle file. Angles frame every ad and organic piece -- 3+ gives /ads real variety. Want to explore a new angle through /think?
> - **audience.md** (2/3): Missing "Objections" section -- /ads hooks work best when they preempt resistance. What do people say right before they decide NOT to buy?"

### Intermediate (experience: intermediate)

Show the score, then list gaps with brief actionable detail:

> "**Repo Health: THIN** (9/18)
>
> **Gaps:**
> - **voice.md** (1/3): No "Never Say" section -- guard rail for authentic output. 3 questions to build it? (~5 min)
> - **testimonials.md** (1/3): 2 testimonials. 10+ unlocks stronger ad proof. Have recent wins?
> - **angles/** (1/3): 1 angle. 3+ prevents ad fatigue. Build one through /think?"

### Advanced (experience: advanced)

Score with gap specifics, no explanation. **One line, always -- even at GOOD/FULL.** Advanced users don't need gap tables or explanation blocks.

> "**9/18** -- voice (1, no Never Say), testimonials (1, only 2), angles (1, single angle)."

**At GOOD/FULL, same one-line format:**

> "**16/18** -- testimonials (2), angles (1). Have recent wins to add? Need 2 more angles for ad variety."

> "**13/18** -- testimonials (2, 7 captured), angles (1, single angle). Gaps: recent wins? New angle through /think?"

### When Score Is GOOD (12-14)

Still show gaps -- this is where the old format failed. Users at 13/18 need to know what the missing 5 points are. **Beginner/intermediate get the full gap display below. Advanced users get the one-line format above.**

> "**Repo Health: GOOD** (13/18)
>
> **Gaps:**
> - **testimonials.md** (2/3): 7 testimonials captured. 10+ unlocks stronger ad proof. Have any recent wins to add?
> - **angles/** (1/3): 1 angle file. 4+ gives /ads real variety. Want to explore a new angle through /think?"

### When Score Is FULL (15-18) But Not Perfect

Still show what would reach 18. **Beginner/intermediate get the gap display below. Advanced users get the one-line format above.**

> "**Repo Health: FULL** (16/18)
>
> **Gaps:**
> - **testimonials.md** (2/3): 7 testimonials. 10+ gives /ads and /vsl more proof options. Have any recent wins?
> - **angles/** (1/3): 1 angle file. 4+ lets you test different emotional entry points in ads. Want to build another?"

### When Score Is 18/18

No structural gaps to show, but don't claim perfection — triage finds deeper issues:

> "**Repo Health: FULL** (18/18). All reference files present and substantive. For deeper analysis (staleness, cross-file consistency, pipeline health), pick option 1."

**Do NOT say:** "locked", "mature", "production-ready", or "all set." 18/18 means structure is complete, not that content is perfect. Triage handles quality.

### Flag Display

Health flags from Section 3 appear alongside structural scores. File-level flags (status, staleness, count mismatch) go inline. Pipeline flags (codification rate, naming) go below.

**Beginner/Intermediate — flags after gaps:**

> "**Repo Health: FULL** (18/18)
>
> **Flags:**
> - soul.md — status: draft (you marked this unfinished)
> - audience.md — stale (41d since last update)
> - Decisions: 8 codified, 55 accepted
> - Needs review: 4
> - Action needed: 2
> - Stale/orphaned: 1
>
> Pick option 1 for deeper analysis."

**Advanced — flags on one line:**

> "**18/18** — flags: soul.md draft, audience.md stale (41d), 8 codified + 55 accepted, 4 need review, 2 action needed, 1 stale/orphaned. Option 1 for details."

**When GOOD/FULL with both gaps AND flags:**

> "**Repo Health: GOOD** (13/18)
>
> **Gaps:**
> - **testimonials.md** (2/3): 7 testimonials. 10+ unlocks stronger proof. Have recent wins?
>
> **Flags:**
> - offer.md — stale (35d)
> - Decisions: 3 codified, 9 accepted
> - Needs review: 2
> - Action needed: 1
> - Stale/orphaned: 1
>
> Pick option 1 for deeper analysis."

**When no flags fire:** Don't show the Flags section at all. No "Flags: none" or "0 flags" — just omit it.

### Session State Display

If session state items were found, append after the health display:

> "**Since last session:**
> - Last work: [topic from recent commit]
> - [N] open decisions ready to codify
> - [N] research files without decisions"

Only show items that exist. Skip this section entirely if nothing to report.

---

## 8. Per-File Gap Tables

Use these tables to determine the specific gap language for each file at each score level. The formula is always: **[Specific missing section/file] + [What it unlocks downstream] + [Concrete question or offer to fix it now]**.

### soul.md

| Score | What's Missing | Actionable Gap | Question to Ask |
|-------|---------------|----------------|-----------------|
| 0 | File doesn't exist | "No soul.md yet. This is the foundation -- your WHY. Let me ask you 3 questions to draft it." | "What do you research when no one's watching? What intersections excite you? What work feels like discovery vs obligation?" |
| 1 | <30 lines, skeleton | "soul.md exists but is thin. Missing: Beliefs section, Anti-patterns, Evolution Markers." | "What do you believe about [domain] that most people get wrong? What patterns make you lose energy?" |
| 2 | 30-80 lines, developing | "soul.md has substance but is missing [specific section: Evolution Markers or Anti-patterns or The Parts]." | Depends on missing section: "When did your thinking about this shift? What was the before/after?" (Evolution Markers) |
| 3 | Strong | At 3, only surface if qualitative issues exist: "soul.md is strong. Last updated [date] -- still resonates?" | No question unless returning after long absence (soul health check handles this) |

### offer.md

| Score | What's Missing | Actionable Gap | Question to Ask |
|-------|---------------|----------------|-----------------|
| 0 | File doesn't exist | "No offer.md. /ads, /vsl, and /site can't generate without knowing what you sell." | "What do you sell? What transformation does the buyer get? What does it cost?" |
| 1 | <20 lines | "offer.md exists but is missing: [check for Pricing, Mechanism, Guarantee, Value Stack sections]." | "Your offer mentions [what exists] but I don't see [missing section]. What's your guarantee? What makes your mechanism unique?" |
| 2 | 20-80 lines, developing | "offer.md is developing. [Specific weak area: e.g., 'Mechanism section is one sentence -- this is what makes /vsl scripts compelling.']" | "Walk me through HOW your product/service actually works. What's the step-by-step transformation?" |
| 3 | Strong | "offer.md is strong. Ready for /ads and /vsl." | No question. Note if Price section hasn't been updated in 60+ days. |

### audience.md

| Score | What's Missing | Actionable Gap | Question to Ask |
|-------|---------------|----------------|-----------------|
| 0 | File doesn't exist | "No audience.md. Hooks and ad copy will be generic without knowing who you're talking to." | "Who are the 2-3 people you've helped most? What was their life like before?" |
| 1 | <30 lines | "audience.md is a skeleton. Missing: [Pains section, Desires section, Psychographics]." | "What keeps your audience up at 2am? Not their stated problem -- their actual fear." |
| 2 | 30-60 lines, developing | "audience.md has [what exists] but is missing [specific section: e.g., 'No Objections section -- /ads hooks work best when they preempt resistance.']" | "What do people say right before they decide NOT to buy? What's their go-to excuse?" |
| 3 | Strong | "audience.md is strong." | No question. Note if segments could be refined for multi-offer routing. |

### voice.md

| Score | What's Missing | Actionable Gap | Question to Ask |
|-------|---------------|----------------|-----------------|
| 0 | File doesn't exist | "No voice.md. Generated content will sound like generic AI until voice is defined." | "Send me 3 pieces of content you've written that sound most like you. I'll extract the patterns." |
| 1 | <20 lines | "voice.md exists but is missing: [check for Never Say, Vocabulary, Rhythm sections]." | "What phrases do you NEVER want to see in your content? What words feel wrong for your brand?" |
| 2 | 20-50 lines, developing | "voice.md has tone direction but is missing [specific: e.g., 'No Never Say section -- this is the most important guard rail for authentic-sounding output.']" | "Read this draft [show example output] -- what sounds wrong? What would you change?" |
| 3 | Strong | "voice.md is strong." | No question. Could note: "Last voice calibration was [date]. Want to run a quick test with a sample output?" |

### testimonials.md

| Score | What's Missing | Actionable Gap | Question to Ask |
|-------|---------------|----------------|-----------------|
| 0 | File doesn't exist | "No testimonials. /ads and /vsl are dramatically weaker without proof." | "Do you have any testimonials, screenshots, DMs, or reviews? Even 2-3 is a strong start." |
| 1 | <5 testimonials | "[N] testimonials. More variety = more angles for ads." | "Any testimonials that specifically mention [the transformation from offer.md]? Those are highest value." |
| 2 | 5-10 testimonials | "Good proof base. Consider: are there testimonials that support each angle in proof/angles/?" | "Which of your testimonials surprises you most? Which one do people respond to when you share it?" |
| 3 | Strong (10+) | "Strong proof base." | No question unless typicality.md is missing: "You have strong testimonials but no typicality data. For FTC-safe outcome claims, we'd need average results." |

### angles/ (proof/angles/)

| Score | What's Missing | Actionable Gap | Question to Ask |
|-------|---------------|----------------|-----------------|
| 0 | No angle files | "No angles defined. Angles are messaging entry points -- each one frames your offer differently for different motivations." | "Why do your best customers buy? Not the feature -- the emotional trigger. Is it fear? Status? Relief? Curiosity?" |
| 1 | 1 angle | "One angle defined ([name]). Ads and organic content need variety -- 3+ angles prevent fatigue." | "You have [existing angle]. What's the SECOND most common reason people buy? Different motivation = different angle." |
| 2 | 2-3 angles | "Decent angle variety. Review: do angles cover different emotional territories? (e.g., if all three are fear-based, missing opportunity-based.)" | "Look at your angles: [list names]. Are there buyer motivations not covered? What about [suggest missing emotional territory]?" |
| 3 | 4+ angles | "Strong angle library." | No question. Could note: "Which angles have been tested in ads? Performance data would inform prioritization." |

### content-strategy.md (domain, not in composite but checked)

| State | Actionable Gap | Question to Ask |
|-------|----------------|-----------------|
| Missing | "No content strategy yet. Content generated by /organic and /ads works better with pillars, platform strategy, and cadence defined." | "Want to build content-strategy.md through /think? It derives pillars from your soul + offer + audience." |
| Exists but thin (<20 lines) | "content-strategy.md is a skeleton. Missing: [check for Pillars, Platform Strategy, Content Mix, Cadence sections]." | "Your content strategy needs [specific section]. Start with pillars -- what 3-5 themes connect your soul to your audience?" |
| Exists but incomplete | "content-strategy.md has [what exists] but is missing [Hooks Library / Framework Library / Metrics]." | "Your pillars and platform are set. Want to populate the hooks library? Every hook pattern you capture makes /organic output better." |
| Complete | "Content strategy is solid." | Note last updated date. If >30 days, suggest review. |

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
- `/end` crystallize-agent pattern -- The soul awareness pattern this assessment draws from
