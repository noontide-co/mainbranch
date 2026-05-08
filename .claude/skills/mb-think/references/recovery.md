# Recovery from Compaction

When conversations get long, Claude's memory compresses (called "compaction"). This guide helps resume `/mb-think` sessions after compaction.

---

## For Users

Just type `/mb-think` again and describe where you were:

- "We're in the middle of researching pricing tiers"
- "I was working on my guarantee decision"
- "Pick up where we left off on the VSL structure"
- "Where was I on the guarantee thing?"

That's it. The skill handles the rest.

---

## For Claude

When resuming a `/mb-think` session:

### 1. Check Multiple Sources

**Claude tasks (current session):**
```
TaskList
```
Shows local execution steps from this session.

**Recent files in user's repo:**
```bash
# Recent research files
ls -lt research/*.md 2>/dev/null | head -5

# In-progress decisions
grep -l "status: proposed\|status: accepted" decisions/*.md 2>/dev/null
```

**GitHub issues (when durable work threads are needed):**
```bash
gh issue list --assignee @me --state open --limit 5
```

### 2. Read Relevant File(s)

Once identified, read the file to restore context:

- Research files show what was learned
- Decision files with `status: proposed` hold drafted rationale still being evaluated
- Decision files with `status: accepted` hold chosen rationale that may need codification

### 3. Confirm with User

> "I see you were working on [topic]. You're at [stage]. Want to continue from here?"

### 4. Resume Workflow

Pick up from the appropriate checkpoint:

| File State | Resume Point |
|------------|--------------|
| Research `draft` | Continue gathering or synthesizing |
| Research `complete` | Move to decide phase |
| Decision `proposed` | Continue options analysis |
| Decision `accepted` | Offer to codify |
| Decision `codified` | Rationale integrated into durable truth |

---

## Why Files Are Memory

- **Chat is disposable** — Files persist
- **Decision files preserve rationale maturity** — proposed, accepted, codified
- **Research files capture learning** — Synthesis survives compaction
- **You're never starting from zero** — Always recoverable state

---

## Quick Recovery Commands

User can say any of these after compaction:

| What User Says | What Happens |
|----------------|--------------|
| "/mb-think continue" | Check recent files, resume |
| "/mb-think where was I?" | Scan decisions/ and research/ for in-progress work |
| "/mb-think apply [topic] decision" | Find and codify the decision |
| "/mb-think [any description of work]" | Context clues help locate files |

---

## Offer Context Recovery

Read `.vip/local.yaml` for `current_offer` to restore which offer was being worked on.

If the file doesn't exist or `current_offer` is not set, check recent `research/` and `decisions/` files for offer-specific prefixes (e.g., `research/2026-02-04-community-pricing-analysis.md`).

Confirm with user: "Were you working on [offer]?"

If the repo has `core/offers/` but no `current_offer` is recoverable, ask before proceeding: "Which offer are you working on?" Use legacy `reference/offers/` only when `core/` is absent.

---

## Multiple In-Progress Items

If user has multiple items in progress:

> "I found a few things in progress:
> 1. Research on pricing tiers (draft)
> 2. Decision on guarantee strategy (accepted, not codified)
>
> Which would you like to continue?"

Let user choose rather than assuming.
