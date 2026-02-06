# Triage Agent Reference

Complete reference for the smart triage system spawned by `/start` when the user selects option 0 ("Help me figure out what to work on"). Contains agent prompts, anti-patterns, synthesis format, and save behavior.

Modeled on `/end`'s crystallize agent pattern. Where crystallize asks "what did today mean?", triage asks "what should happen next?" Where crystallize is a mirror, triage is a compass.

---

## When to Trigger

**User selects option 0** in the routing list, or says: "what should I work on?", "help me prioritize", "I don't know where to start", "help me figure out what to do."

**Auto-suggest (but don't auto-run) when:**
- User is returning after 3+ days (soul health check context)
- Readiness score is THIN-to-GOOD (8-14) -- enough to analyze, enough gaps to fill
- Soul health check indicated "push" (suggests drift -- triage may reveal the cause)

**Skip when:**
- User states clear intent ("I want to write ads") -- route directly
- Context window already heavy (>60%) -- triage is expensive
- Readiness is EMPTY or MINIMAL (0-7) -- answer is obvious: /setup or /think
- User explicitly asks for a specific skill

---

## Architecture: 3 Parallel Read-Only Agents

Spawn three agents in a single message using the Task tool. Each gets a focused analysis domain. All three are **read-only** -- they return findings to the main conversation, which synthesizes and presents.

### Reuse Readiness Data (Token Efficiency)

The triage agents receive the readiness assessment results (scores, gaps, session state, recent commits) as input context. They do NOT re-scan these. The readiness assessment (Step 0.9) already ran git log, scored files, detected open decisions, and checked for uncodified research. Triage agents go DEEPER -- reading file contents, checking section quality, analyzing patterns across files, and connecting dots between soul alignment and tactical work.

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

### Pre-Gathering (Main Conversation)

Before spawning agents, gather these in the main conversation and pass to each agent as needed:

| Content | How | Passed To |
|---------|-----|-----------|
| Readiness scores (from Step 0.9) | Already computed | All 3 agents |
| Git log (30 days) | `git log --since="30 days ago" --oneline --no-merges` | Agent 2 |
| Git log (reference file changes, 30 days) | `git log --since="30 days ago" --name-only -- reference/` | Agent 1, 3 |
| Open decisions | `grep -rl "status: proposed\|status: accepted" decisions/` | Agent 2 |
| Unlinked research | Research files with `linked_decisions: []` | Agent 2 |
| soul.md (full) | Read tool | Agent 3 |
| content-strategy.md (full) | Read tool (if exists) | Agent 2, 3 |
| Past triage outputs | `research/*-start-triage.md` (if any) | Agent 3 |
| Past crystallize outputs | `research/*-end-of-day-crystallize.md` (if any) | Agent 3 |
| `.vip/local.yaml` | Read for current_offer | All 3 agents |
| Content pipeline state | `ls content/drafts/ content/scheduled/ content/published/ 2>/dev/null` | Agent 2 |
| Recent outputs | `ls -lt outputs/ 2>/dev/null \| head -5` | Agent 2 |

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

[Scores from Step 0.9: soul X/3, offer X/3, audience X/3, voice X/3,
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

=== CONTENT PIPELINE STATE ===

[Contents of content/drafts/, content/scheduled/, content/published/
or "No content/ folder" if missing]

=== RECENT OUTPUTS ===

[Most recent 5 items in outputs/]

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

3. **Content pipeline state:** Anything in drafts? Scheduled? When was last
   content published? Is there a gap between reference readiness and content
   output?

4. **Output recency:** When was the last batch generated? What type?
   Long gap between reference updates and output generation = missed opportunity.

5. **Velocity pattern:** What's the ratio of enrichment work (research/,
   reference/ changes) to output work (outputs/, content/)? All enrichment
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

Use the Task tool to spawn all three agents in a single message:

```
Task(
  subagent_type: "general-purpose",
  description: "Reference Health Analyst: deep section-level analysis of all
    reference files, cross-file consistency, domain rubric compliance,
    staleness detection. Returns ranked gap list with effort estimates."
)

Task(
  subagent_type: "general-purpose",
  description: "Pipeline & Momentum Analyst: git history patterns, open
    decisions, unlinked research, content pipeline state, velocity assessment.
    Returns bottleneck ranking and momentum assessment."
)

Task(
  subagent_type: "general-purpose",
  description: "Soul & Strategy Connector: soul alignment check, unresolved
    crystallize threads, strategic direction assessment. Returns soul-grounded
    recommendations."
)
```

Each agent is **read-only**. Each returns structured findings. The main conversation synthesizes.

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

### 7. Don't Repeat Past Triage

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

| Component | Estimated Tokens |
|-----------|-----------------|
| Pre-gathering (main conversation) | 5-10K |
| Agent 1: Reference Health | 30-50K |
| Agent 2: Pipeline & Momentum | 20-40K |
| Agent 3: Soul & Strategy | 20-30K |
| Synthesis (main conversation) | 5-10K |
| **Total across all agents** | **75-130K** |

On THIN repos (8-11), Agent 1 has less to read, so budget drops. On FULL repos (15-18), Agent 1 has more content but Agents 2 and 3 become the primary value drivers.

---

## What the Triage Agent Is NOT

1. **Not a task list.** It produces a recommendation with reasoning, not a numbered list of everything that needs doing.

2. **Not an audit.** The readiness assessment already scored files. Triage interprets scores in context and recommends action.

3. **Not a summary.** The session state check already surfaced recent activity. Triage looks forward.

4. **Not /think.** It does not execute research or decisions. It recommends where to start. Then the appropriate skill does the work.

---

## See Also

- [../SKILL.md](../SKILL.md) -- The /start flow that offers triage as option 0
- [readiness-assessment.md](readiness-assessment.md) -- Scoring rubric and display format (runs before triage)
- [../../end/references/crystallize-agent.md](../../end/references/crystallize-agent.md) -- The /end crystallize pattern this agent is modeled on
