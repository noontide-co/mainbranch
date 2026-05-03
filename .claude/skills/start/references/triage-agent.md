# Triage Agent Reference

Complete reference for the smart triage system in `/start`. Runs when the user selects **option 1** ("What should I focus on?") from the /start menu. Contains agent prompts, pre-gathering, gating, synthesis format, anti-patterns, and save behavior.

Modeled on `/end`'s crystallize agent pattern. Where crystallize asks "what did today mean?", triage asks "what should happen next?" Where crystallize is a mirror, triage is a compass.

---

## When to Run

**Triage runs when the user chooses it.** It's option 1 on the /start menu — the recommended default most sessions. But the user can always skip it and pick a skill directly.

**Why not always-on:** Three parallel agents burn 50-80K tokens. Running them every session means the user hits 60%+ context before doing any actual work. /end gates crystallize behind meaningful activity — /start gates triage behind user choice. Agents eat the heavy context in their own windows, keeping main lean for whatever comes next.

**Auto-suggest option 1 when:**
- Returning user (last commit >3 days ago) and no stated intent
- Readiness is THIN (8-11) — "Option 1 can help you figure out the highest-leverage gap"
- User says "what should I work on", "help me prioritize", "what to do next"

**Skip triage entirely when:**
- Readiness is EMPTY or MINIMAL (0-7) — answer is obvious: `/setup` or `/think`
- User stated clear intent with `/start ads` or similar

---

## Gating (Like /end's Crystallize)

Before spawning agents, check these gates (modeled on /end Step 5a):

| Gate | Check | If fails |
|------|-------|----------|
| Context budget | Is main context < 50%? | Warn user: "Context is at X%. Triage uses significant tokens. Run it anyway?" |
| Readiness tier | Is score ≥ 8 (THIN or above)? | Skip triage — not enough reference to analyze. Route to `/think` |
| Meaningful state | Does repo have commits, decisions, or research? | If brand new repo with just setup scaffolding, skip deep triage — suggest `/think` instead |

### Tiered Spawning

Not every session needs 3 agents. Match agent count to context:

| Condition | Agents | Why |
|-----------|--------|-----|
| THIN (8-11), few commits | **1 agent** (Reference Health only) | Not enough content for pipeline or soul analysis |
| GOOD (12-14), active repo | **2 agents** (Reference Health + Pipeline) | Soul analysis adds value when there's meaningful work history |
| FULL (15-18), active repo | **3 agents** (all three) | Full analysis justified |
| User says "deep triage" | **3 agents** regardless | Explicit request overrides tiering |

---

## Architecture: 3 Parallel Read-Only Agents

Spawn three agents in a single message using the Task tool. Each gets a focused analysis domain. All three are **read-only** -- they return findings to the main conversation, which synthesizes and presents.

### Reuse Readiness Data (Token Efficiency)

The triage agents receive the readiness assessment results (scores, gaps, session state, recent commits) as input context. They do NOT re-scan these. The readiness assessment (Step 6) already ran git log, scored files, detected open decisions, and checked for uncodified research. Triage agents go DEEPER -- reading file contents, checking section quality, analyzing patterns across files, and connecting dots between soul alignment and tactical work.

**What readiness already computed (pass as context, do not recompute):**
- Per-file scores (soul, offer, audience, voice, testimonials, angles)
- Composite score and status tier (EMPTY/MINIMAL/THIN/GOOD/FULL)
- Recent commits summary
- Open decision count and topics
- Uncodified research count
- Session gaps and last activity date

**What triage agents add (their unique value):**
- Agent 1: Section-level analysis of file contents, cross-file consistency, domain rubric compliance
- Agent 2: Work pattern analysis, velocity assessment, pipeline bottlenecks
- Agent 3: Soul-strategy alignment, unresolved threads, temporal patterns

### Pre-Gathering (Main Conversation — Keep It Lean)

**The goal is to pass COMPACT data to agents, not load everything into main.** Main gathers lightweight metadata (scores, file lists, git summaries). Agents do the heavy reading (full file contents, cross-file analysis) in their own context windows.

Gather these in main and pass as structured text in each agent's prompt:

| Content | How | Size | Passed To |
|---------|-----|------|-----------|
| Readiness scores (from Step 6) | Already computed | ~20 lines | All 3 agents |
| Absolute repo path | From Step 2 | 1 line | All 3 agents (agents use this to Read files themselves) |
| Git log (30 days) | `git log --since="30 days ago" --oneline --no-merges` | ~30 lines | Agent 2 |
| Reference file change list (30 days) | `git log --since="30 days ago" --name-only -- reference/` | ~20 lines | Agent 1, 3 |
| Open decision file names | `grep -rl "status: proposed\|status: accepted" decisions/ 2>/dev/null` | ~10 lines | Agent 2 |
| Unlinked research count | `grep -rl "linked_decisions: \[\]" research/ 2>/dev/null \| wc -l` | 1 line | Agent 2 |
| Past triage file names | `ls research/*-start-triage.md 2>/dev/null` | ~5 lines | Agent 3 |
| Past crystallize file names | `ls research/*-end-of-day-crystallize.md 2>/dev/null` | ~5 lines | Agent 3 |
| `current_offer` | From `.vip/local.yaml` | 1 line | All 3 agents |
| Output lifecycle listing | `grep -rl "status: draft\|status: scheduled" outputs/ 2>/dev/null` | ~10 lines | Agent 2 |

**What agents read themselves (in their own context, NOT in main):**
- soul.md, offer.md, audience.md, voice.md — Agent 1 reads all, Agent 3 reads soul
- content-strategy.md — Agent 2, 3
- Full decision files (agents pick which ones to read based on file names)
- Full past triage/crystallize outputs (agents pick based on file names)
- testimonials.md, angles/* — Agent 1

**This keeps main at ~5K tokens of pre-gathering** while agents spend 20-50K each reading full files.

---

## Agent 1: Reference Health Analyst

### Prompt Template

```
=== REFERENCE HEALTH ANALYST ===

You analyze reference file health at section level -- not just line count, but
what specific sections exist, what's missing, and what filling each gap would
unlock for downstream skills (/ads, /vsl, /organic, /site).

You are NOT an auditor. You are identifying the highest-leverage gaps.

=== ANTI-PATTERNS (read first) ===

[Include Anti-Patterns section from this file]

=== READINESS SCORES ===

[Scores from Step 6: soul X/3, offer X/3, audience X/3, voice X/3,
testimonials X/3, angles X/3. Composite X/18.]

=== CURRENT OFFER ===

[current_offer from .vip/local.yaml, or "single-offer mode"]

=== REFERENCE FILES ===

[Full text of each reference file in core/, offers/[active]/ if multi-offer,
proof/testimonials.md, proof/angles/*.md, domain/content-strategy.md,
domain/product-ladder.md if multi-offer, domain/funnel/skool-surfaces.md if exists]

=== DOMAIN RUBRIC ===

[The relevant domain rubric from vip: community.md, ecommerce.md, or multi-offer.md.
Determine which by checking reference/domain/ contents.]

=== REFERENCE FILE CHANGE HISTORY (30 DAYS) ===

[Git log output for reference/ changes]

=== YOUR TASK ===

1. For each reference file scoring below 3: identify the SPECIFIC sections that
   are missing or thin. Use the file content, not just line count.

2. For each gap found: state what downstream skill it weakens and what question
   would fill it (~5 min effort).

3. Check cross-file consistency:
   - Does audience.md pain language match the angles in proof/angles/?
   - Does offer.md mechanism match what testimonials describe?
   - Do voice.md guardrails align with actual output tone?

4. Check domain rubric compliance: what domain-specific files are missing?
   (e.g., community business without skool-surfaces.md, e-commerce without products/)

5. Check staleness: which files haven't been updated in 30+ days?
   Only flag if the file is actively used by downstream skills.

6. If multi-offer: are all offer files comparable in depth? Is product-ladder.md
   connecting them?

Return a RANKED list of reference improvements. Rank by compound impact
(what unlocks the most downstream value). For each item include:
- File and section
- What's missing or weak
- What filling it unlocks
- Suggested question to fill it
- Effort estimate (quick = ~5 min, moderate = ~15 min, deep = needs /think)
```

**Token budget:** ~30-50K (reads all reference files, domain rubric, produces structured analysis)

---

## Agent 2: Pipeline & Momentum Analyst

### Prompt Template

```
=== PIPELINE & MOMENTUM ANALYST ===

You analyze work patterns, pipeline health, and momentum. You look at what's
been done, what's pending, and where energy is going. You identify bottlenecks
and the highest-value pending work.

You are NOT a task manager. You identify patterns and bottlenecks.

=== ANTI-PATTERNS (read first) ===

[Include Anti-Patterns section from this file]

=== GIT LOG (30 DAYS) ===

[Git log output -- commits, what changed, when]

=== OPEN DECISIONS ===

[List of decisions with status: proposed or accepted. Include frontmatter
and first 10 lines of each.]

=== UNLINKED RESEARCH ===

[Research files with linked_decisions: []. Include filename and date.]

=== OUTPUT LIFECYCLE STATE ===

[Files in outputs/ grouped by frontmatter status: draft, scheduled, published, final.
Use: grep -rl "status: draft" outputs/ 2>/dev/null
or "No outputs with lifecycle status" if none have status field.
Also list most recent 5 items in outputs/.]

=== CONTENT STRATEGY ===

[Full text of content-strategy.md, or "Not yet created."]

=== READINESS SCORES ===

[Composite score and per-file scores]

=== YOUR TASK ===

Analyze these dimensions:

1. **Open decisions:** How many? What topics? How old? Decisions accumulating
   without codification = the highest-value pending work. Research goes stale.
   Decisions capture reasoning at a point in time.

2. **Unlinked research:** Research without linked_decisions. Note it gently --
   some research is exploratory. But research older than 14 days without a
   decision may be going stale.

3. **Output lifecycle state:** Any outputs with status: draft? Scheduled?
   When was the last output published? Is there a gap between reference
   readiness and output generation?

4. **Output recency:** When was the last batch generated? What type?
   Long gap between reference updates and output generation = missed opportunity.

5. **Velocity pattern:** What's the ratio of enrichment work (research/,
   reference/ changes) to output work (outputs/)? All enrichment
   with no output = stuck in thinking. All output with no enrichment =
   running on stale context.

6. **Content strategy health:** Does content-strategy.md have populated pillars?
   Hooks library? Framework library? Metrics section? Or is it a skeleton?

Return:
- Pipeline health summary (2-3 sentences)
- Top 3 bottlenecks ranked by impact
- Momentum assessment: "building", "stalled", "execution-heavy", or "enrichment-heavy"
- Highest-value pending work item with reasoning
```

**Token budget:** ~20-40K (reads git logs, scans file frontmatter, analyzes patterns)

---

## Agent 3: Soul & Strategy Connector

### Prompt Template

```
=== SOUL & STRATEGY CONNECTOR ===

You connect the user's existential purpose (soul.md) to their tactical work
patterns. You look for alignment and drift. You check whether recent work
reflects what matters or has become mechanical execution.

You are NOT a therapist or coach. You are a strategic compass.

=== ANTI-PATTERNS (read first) ===

[Include Anti-Patterns section from this file]

=== SOUL.MD ===

[Full text of soul.md]

=== CONTENT STRATEGY ===

[Full text of content-strategy.md, or "Not yet created."]

=== PAST TRIAGE OUTPUTS ===

[Contents of research/*-start-triage.md, if any.
If none: "First triage session. No prior outputs."]

=== PAST CRYSTALLIZE OUTPUTS ===

[Contents of research/*-end-of-day-crystallize.md, most recent 3.
If none: "No crystallize history."]

=== RECENT DECISIONS (LAST 5) ===

[Full text of 5 most recent decision files]

=== REFERENCE FILE CHANGE HISTORY (30 DAYS) ===

[Git log output for reference/ changes]

=== READINESS SCORES ===

[Composite score and per-file scores]

=== YOUR TASK ===

Analyze these dimensions:

1. **Soul-offer alignment:** Does the recent work pattern reflect soul.md
   interests? Are decisions connecting to the WHY or just optimizing tactics?

2. **Unresolved crystallize threads:** Past crystallize questions where the user
   engaged but nothing was codified into reference. These are insights that
   were acknowledged but not captured.

3. **Past triage follow-through:** If previous triage recommended something,
   did it happen? If not, is it still relevant or has the situation changed?

4. **Strategic gaps:** What big questions is the user circling without landing?
   Look at decision topics -- are multiple decisions orbiting the same
   unresolved tension?

5. **Temporal patterns:** Is the user stuck in a loop (same type of work every
   session)? Or making progress across the system?

6. **Content strategy to soul alignment:** Do the pillars in content-strategy.md
   actually connect to soul.md interests? Or are they purely tactical?

Return:
- Strategic direction assessment (2-3 sentences)
- 1-2 observations about where the user's energy and attention should go next
  (based on soul alignment, not just tactical gaps)
- Any unresolved threads from past crystallize/triage that deserve attention
```

**Token budget:** ~20-30K (reads soul, strategy files, past crystallize/triage outputs)

---

## Spawning Pattern

**Spawn all three agents in a single message using the Task tool.** This sends them to parallel context windows. Each agent's prompt includes the pre-gathered metadata PLUS instructions to read specific files themselves using the absolute repo path.

```
Task(
  subagent_type: "general-purpose",
  description: "Reference Health Analyst: read all reference files at [repo-path],
    analyze section-level quality, cross-file consistency, domain rubric compliance,
    staleness detection. Return ranked gap list with effort estimates.",
  prompt: "[Pre-gathered metadata + Agent 1 prompt template + absolute repo path]"
)

Task(
  subagent_type: "general-purpose",
  description: "Pipeline & Momentum Analyst: analyze git patterns, open decisions,
    unlinked research, content pipeline state, velocity. Return bottleneck ranking
    and momentum assessment.",
  prompt: "[Pre-gathered metadata + Agent 2 prompt template + absolute repo path]"
)

Task(
  subagent_type: "general-purpose",
  description: "Soul & Strategy Connector: read soul.md at [repo-path], check
    alignment with recent work, review past crystallize/triage outputs. Return
    soul-grounded recommendations.",
  prompt: "[Pre-gathered metadata + Agent 3 prompt template + absolute repo path]"
)
```

Each agent is **read-only**. Each reads files in its own context window. Main conversation stays lean.

**Set `max_turns: 20` on each Task call** to prevent runaway agents. 20 turns is enough for full file reads + analysis but caps cost if something loops.

### After Spawning: Wait for Agents

**The user already chose triage (option 1). They're waiting for results.** Show a brief message: "Analyzing your business state..." while agents work.

### When Agents Return: Present the Synthesis

When all agents complete, synthesize their findings (see Synthesis Format below) and present to the user. Then ask: "Want to go with [primary recommendation]? Or does something else feel right?"

The user can pick the recommendation, ask follow-up questions, or choose a different path entirely. Triage is guidance, not enforcement.

---

## Synthesis Format

After all three agents return, synthesize into this format:

```
=== TRIAGE ANALYSIS ===

[2-3 sentences of context -- what the agents found, what patterns emerged.
This shows the user you read their whole business state, not just surface scores.]

## Recommended Focus

**Primary:** [The one thing that would have the highest compound impact]
[1-2 sentences: why this, what it unlocks, how it connects to their purpose]

**Also ready:** [1-2 other high-value options]
[Brief reasoning for each]

## Quick Fixes Available

- [Specific gap]: [What question to ask to fill it] -- ~5 min
- [Specific gap]: [What question to ask to fill it] -- ~5 min

## What I'd Skip Today

[1 thing the user might instinctively do that the analysis suggests isn't
the highest value right now. This is the highest-leverage part of the
recommendation -- telling someone what NOT to do.]
[Brief reasoning]
```

**After presenting:** Ask "Want to go with [primary recommendation]? Or does something else feel right?"

If user picks the primary recommendation, route to the appropriate skill. If they pick something else, respect it -- triage is guidance, not enforcement.

---

## Thin Repo Mode (THIN 8-11 or GOOD 12-14 with gaps)

**When reference is still building, triage becomes the most valuable thing in the system.** This is where users most need direction. The synthesis should inspire, not audit.

### Shift the Energy

- **Don't say:** "You're missing voice.md, testimonials, and 3 angles."
- **Do say:** "Your offer and audience are solid. Adding a Never Say section to voice.md would immediately sharpen every ad hook. I can ask you 3 questions right now and we'll have it in 5 minutes."

### Show What Unlocks

Every gap recommendation must connect to a specific downstream outcome the user cares about:

| Gap | What Unlocks | How to Say It |
|-----|-------------|---------------|
| No voice.md | Ads sound generic | "Once voice.md has a Never Say section, /ads stops using phrases that don't sound like you" |
| Thin audience.md | Hooks don't land | "Adding 3-5 pain points to audience.md means /ads writes hooks your audience actually recognizes" |
| No angles | Ad fatigue | "One angle = one ad direction. Three angles = three completely different emotional entry points. More angles = more creative variety before fatigue" |
| No testimonials | Can't use social proof | "Even 2-3 testimonials unlock proof-based ads. Got any screenshots of wins, DMs, or reviews?" |
| No content-strategy | No distribution plan | "Your reference is ready to generate content, but without content-strategy.md there's no plan for where it goes. 15 min with /think can build the skeleton" |

### Make It Easy

**Always offer to do it right now.** The #1 reason thin repos stay thin is the user doesn't know it's a 5-minute fix:

> "Want me to ask you the 3 questions that would build your voice.md right now? Takes about 5 minutes and immediately improves every output."

### Synthesis Format for Thin Repos

```
=== TRIAGE ANALYSIS ===

[Acknowledge what they HAVE built — celebrate progress, not just gaps]

## Your Biggest Unlock Right Now

**[One thing]:** [What adding it unlocks, in terms the user cares about]
[Offer to do it right now with specific questions — make it feel like 5 minutes, not a project]

## What's Already Working

- [File] is [specific strength] — this means [downstream benefit]
- [File] has [good section] — [what it enables]

## After That

[1-2 next-level items for when they're ready — don't overwhelm, just show the path]
```

**Key difference from full synthesis:** Lead with the unlock, not the gaps. Show what's working first. Make the recommendation feel like leveling up, not fixing problems.

---

## Anti-Patterns

Include these in each agent's prompt (adapted from /end's crystallize anti-patterns).

### 1. Don't List Everything That's Wrong

"You're missing 12 things" is debt collection, not guidance. Pick the highest-leverage gaps. The user should feel oriented, not overwhelmed.

### 2. Don't Prescribe Without Reasoning

"Update voice.md" is a command. "Your ads will sound generic until voice.md has a Never Say section -- want me to ask you 3 questions to build it?" is guidance. Every recommendation needs a WHY connected to downstream impact.

### 3. Don't Ignore Soul

If the user's recent work is all execution with no enrichment, the recommendation should notice that -- not just suggest more execution. If the soul health check indicated "push," the triage must honor that.

### 4. Don't Be Generic

"You should work on your reference files" could be said to anyone. Name the specific file, section, and what filling it would unlock. Reference actual content from the files you read.

### 5. Don't Overwhelm

Three parallel agents produce a LOT of findings. Synthesis must ruthlessly prioritize. One primary recommendation. One or two secondary options. Quick fixes. What to skip. Done. Not a 20-item action plan.

### 6. Don't Ignore What the User Just Told You

If the soul health check revealed "this feels like push," the triage recommendation must honor that. If the user mentioned a specific concern during /start, incorporate it.

### 7. Don't Make Thin Repos Feel Broken

"You're missing 5 files" makes the user feel behind. "Your offer is clear and your audience is developing -- adding a Never Say section to voice.md would immediately sharpen your ads. Want me to ask you 3 questions?" makes them feel like they're building something. Thin repos are not broken. They're early. The triage should feel like unlocking the next level, not auditing what's missing.

### 8. Don't Repeat Past Triage

If a previous triage recommended voice.md work and it still hasn't happened, don't just repeat the recommendation. Ask whether the gap is actually blocking anything, or whether the user has implicitly decided it's low priority.

---

## Saving Triage Output

Like crystallize, triage output is saved for future temporal awareness.

**Save to:** `research/YYYY-MM-DD-start-triage.md`

```markdown
---
type: research
date: YYYY-MM-DD
source: triage
status: complete
---
# Start-of-Session Triage

## Recommendation Given
[The primary recommendation as presented]

## Secondary Options
[The also-ready options]

## Quick Fixes Identified
[Gaps that could be filled in ~5 min]

## What Was Skipped
[The "what I'd skip today" item]

## User Choice
[What the user actually chose to do]

## Follow-Up
[Whether the recommendation was followed -- updated at /end if possible]
```

**Why save:** Future triage agents read these for temporal pattern recognition. "Last time we recommended voice.md work and you chose /ads instead -- did that work out?" Prevents repetitive recommendations and enables the system to learn user preferences.

---

## Token Budget

### By Tier

| Tier | Agents | Main Cost | Agent Cost | Total |
|------|--------|-----------|------------|-------|
| Light (1 agent) | Reference Health only | 5-10K | 30-50K | 35-60K |
| Standard (2 agents) | Health + Pipeline | 5-10K | 50-90K | 55-100K |
| Full (3 agents) | All three | 5-10K | 70-120K | 75-130K |

### Per Agent

| Component | Estimated Tokens |
|-----------|-----------------|
| Pre-gathering (main conversation) | 5-10K |
| Agent 1: Reference Health | 30-50K |
| Agent 2: Pipeline & Momentum | 20-40K |
| Agent 3: Soul & Strategy | 20-30K |
| Synthesis (main conversation) | 5-10K |

**Main context impact:** Only pre-gathering (~5-10K) and synthesis (~5-10K) hit main. Agent tokens are in their own windows. This means triage costs main ~10-20K total, regardless of tier.

---

## What the Triage Agent Is NOT

1. **Not a task list.** It produces a recommendation with reasoning, not a numbered list of everything that needs doing.

2. **Not an audit.** The readiness assessment already scored files. Triage interprets scores in context and recommends action.

3. **Not a summary.** The session state check already surfaced recent activity. Triage looks forward.

4. **Not /think.** It does not execute research or decisions. It recommends where to start. Then the appropriate skill does the work.

---

## See Also

- [../SKILL.md](../SKILL.md) -- The /start flow where triage is option 1 on the menu
- [readiness-assessment.md](readiness-assessment.md) -- Scoring rubric and display format (runs before triage, provides scores to agents)
- `/end` crystallize-agent pattern -- The model for this agent's gating, tiering, and token budget
