---
name: setup
description: |
  Get a new user fully set up with Claude Code + Main Branch. Use when:
  (1) New user needs Claude Code environment configured
  (2) User says "set up my repo", "get me started", "initialize my business"
  (3) User is new to Main Branch and needs the full onboarding
  (4) Migrating existing business context into the Main Branch structure

  Sets up: Chrome extension, two-repo model, business repo with full structure.
  Gathers context aggressively until complete. Applies domain rubrics by business type.
---

# Repo Setup

Get a new user fully configured with Claude Code and their business repo.

---

## The Two-Repo Model

```
ENGINE (vip)     +     DATA (your business repo)
├── Skills                             ├── reference/
├── Lenses                             ├── research/
├── Domain rubrics                     ├── decisions/
└── You PULL updates                   └── You OWN and EDIT this
```

**vip** = The engine. You clone it, pull updates, but never edit it.

**your-business-repo** = Your data. You create it, own it, commit to it. This is where YOUR business context lives.

**How they connect:** In Claude Code, add vip as an "additional working directory." Skills from the engine read your business repo's `reference/` and output to your `outputs/`.

---

## Philosophy: The Core Loop

**This is the heart of Main Branch.** Everything else exists to support this cycle:

```
┌─────────────────────────────────────────────────────┐
│  YOUR BUSINESS REPO (not vip)       │
│                                                     │
│  RESEARCH → DECIDE → CODIFY → GENERATE → LEARN ────┘
│      │          │        │         │
│      ▼          ▼        ▼         ▼
│  research/  decisions/ reference/ outputs/
│
│  Use /think to run this cycle.
│
└─────────────────────────────────────────────────────
```

**Why this matters:**
- **Research** = Investigate before committing (dated, exploratory)
- **Decide** = Make choices with rationale (dated, links to research)
- **Codify** = Update evergreen reference (what skills consume)
- **Generate** = Skills produce outputs from reference
- **Learn** = Outputs inform new research

**All of this happens in YOUR business repo.** Main-branch-premium is the engine — you pull updates but never edit it. Your repo is your data — you own it, commit to it, and evolve it.

**Reference files are living documents.** Not set-it-and-forget-it. Markets shift, you learn, the reference evolves.

After setup, teach users: "Use `/think` to research topics and make decisions. Your reference files get smarter over time."

---

## Workflow

### Pull Latest Updates (Always)

**Before anything else, ensure vip is up to date:**

```bash
# If vip is an added directory or we can find it
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue.
If offline or already current: continue silently.

---

### CRITICAL: Check Location First

**Before doing ANYTHING, verify we're NOT in the vip (engine) repository:**

```bash
# If this succeeds, we're in vip — STOP
ls .claude/skills/setup/SKILL.md 2>/dev/null
```

**If we're in vip, STOP and tell the user:**

> "Hold on — you're in the **vip** repository. That's the engine, not your business repo.
>
> I cannot create your business files here because:
> 1. You only have read-only access to vip (you can't push changes)
> 2. Your business data needs its own separate repository
>
> **Here's what to do:**
>
> 1. Create a folder for your business:
>    ```bash
>    mkdir ~/my-business-name
>    cd ~/my-business-name
>    git init
>    ```
>
> 2. Start Claude in that folder:
>    ```bash
>    claude
>    ```
>
> 3. Add vip as an additional directory so you still have skills:
>    ```
>    /add-dir ~/vip
>    ```
>
> 4. Run `/setup` again
>
> Need more help? See `docs/BEGINNER-SETUP.md` in the vip repo."

**Do not proceed if we're in vip.**

---

### 0. Verify Chrome Extension (REQUIRED for Skool)

**Before gathering ANY context, check Chrome extension status:**

> Type `/chrome` to verify you have the Claude in Chrome extension installed.

If not installed:
> "The Chrome extension is fundamental for Main Branch — it lets me read your sales pages, Skool community, and web content directly. Install it now: https://claude.ai/chrome (requires Google Chrome)"

**If user declines:** Proceed with Playwright or manual screenshots, but note this limits what can be gathered automatically.

**Context tip:** If your conversation gets compacted (summarized), you can always re-invoke `/setup` to reload the full skill context.

### 1. Confirm Git + Working Directory

```bash
git status  # Verify we're in a git repo
pwd         # Confirm working directory
```

If not a git repo:
```bash
git init
```

### 2. Ask Business Type

> What type of business is this?

| Type | Domain Rubric |
|------|---------------|
| **Community/Skool** | Classroom, membership, funnel |
| **E-commerce** | Products, fulfillment, materials |
| **Coaching/Services** | Offers, delivery, packages |
| **Agency** | Services, clients, processes |
| **Other** | Core only, no domain-specific |

**IMPORTANT:** If user has a Skool community, choose **Community/Skool** even if they also do coaching, courses, or services outside Skool. The community is the hub — other offerings feed into it.

Read the appropriate rubric from `vip/.claude/reference/domain-rubrics/`.

### 3. Gather Context (Be a Ruthless Journalist)

Your job: extract every fact possible. Don't settle for partial info. Users provide context in batches — keep asking until YOU say "we have enough."

See **[references/context-gathering.md](references/context-gathering.md)** for:
- URL fetching fallback chain (WebFetch → Chrome → Playwright → manual)
- Business-type specific checklists (Skool, E-commerce, Coaching)
- Completeness criteria

**Opening prompt:**
> Dump everything about this business — sales pages, offer details, testimonials, notes, whatever exists. Paste text, share file paths, or give me URLs to fetch. I'll sort it into the right files.

**After each batch, assess gaps:**
> "Got it. I still need [X, Y, Z] to complete your reference files. Can you share those?"

**Only say "we have enough" when you can fill:**
- offer.md (price, mechanism, deliverables, guarantee)
- audience.md (who, pains, desires, objections)
- voice.md (tone, phrases, personality)
- testimonials.md (3-5 with specific outcomes)
- domain/ (business-type specific structure)

### 4. Create Folder Structure

```bash
mkdir -p reference/core reference/brand reference/proof/angles reference/domain
mkdir -p research decisions outputs
```

Full structure:
```
{business-name}/
├── CLAUDE.md              # Always loaded - business brain
├── README.md              # Human-readable overview
│
├── reference/             # Evergreen truth
│   ├── core/              # REQUIRED
│   │   ├── offer.md       # What you sell
│   │   ├── audience.md    # Who buys
│   │   └── voice.md       # How you sound
│   ├── brand/             # Deep brand systems (optional)
│   ├── proof/
│   │   ├── testimonials.md
│   │   └── angles/        # Proven messaging entry points
│   └── domain/            # Business-type specific
│
├── research/              # Dated investigations
│   └── YYYY-MM-DD-topic-[source].md
│
├── decisions/             # Dated choices with rationale
│   └── YYYY-MM-DD-topic.md
│
└── outputs/               # Generated content
    └── YYYY-MM-DD-batch-name/
```

### 5. Sort Content into Files

Use templates from `references/templates.md`.

**Priority order:**
1. `reference/core/offer.md` — What you sell
2. `reference/core/audience.md` — Who buys
3. `reference/core/voice.md` — How you sound
4. `reference/proof/testimonials.md` — Social proof
5. `reference/proof/angles/` — Messaging entry points

### 6. Apply Domain Rubric

Based on business type, create domain-specific folders:

**E-commerce:** `reference/domain/products/`, `reference/domain/fulfillment/`
**Community:** `reference/domain/classroom/`, `reference/domain/membership/`, `reference/domain/funnel/`

See `vip/.claude/reference/domain-rubrics/` for full specifications.

### 7. Draft CLAUDE.md

See `references/claude-md-guide.md` for structure.

**Key sections:**
- One-line description
- Engine reference (vip)
- Folder structure diagram
- Business summary
- Quick reference (audience, voice, offer)
- Key decisions/research index
- Reference tiers

### 8. Create README.md

Simple human-readable overview:
- What the business is
- How to use the repo with vip
- Quick stats

### 9. Initial Commit

```bash
git add -A
git commit -m "$(cat <<'EOF'
[init] Bootstrap business repo with Main Branch structure

- Created reference/core/ (offer, audience, voice)
- Created reference/proof/ (testimonials, angles)
- Created reference/domain/ ([domain-type] specific)
- Drafted CLAUDE.md and README.md

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### 10. Report Gaps

| File | Status |
|------|--------|
| core/offer.md | ✅ Complete / ⚠️ Missing [X] |
| core/audience.md | ✅ Complete / ⚠️ Missing [X] |
| core/voice.md | ✅ Complete / ⚠️ Missing [X] |
| proof/testimonials.md | ✅ Has content / ❌ Empty |
| proof/angles/ | ✅ [N] angles / ⚠️ None yet |
| domain/ | ✅ Populated / ⚠️ Needs [X] |

Ask user for missing pieces or note for later.

---

## Git Workflow

Always use GitHub CLI with descriptive commits:

**Commit message format:**
```
[type] Brief description

- Detail 1
- Detail 2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

**Types:**
- `[init]` — Initial setup
- `[add]` — New files/features
- `[update]` — Changes to existing
- `[fix]` — Bug fixes
- `[refactor]` — Structure changes
- `[docs]` — Documentation only

See `references/git-workflow.md` for full guide.

---

## References

- **Context Gathering:** `references/context-gathering.md` — Checklists by business type, completeness criteria
- **Templates:** `references/templates.md` — All file templates
- **CLAUDE.md Guide:** `references/claude-md-guide.md` — How to draft a good CLAUDE.md
- **Git Workflow:** `references/git-workflow.md` — Commit messages and CLI usage

---

## When to Run Again

Use this skill to merge new context:

- "I just wrote a new sales page, update my reference"
- "Here's feedback from 10 customer calls"
- "This angle crushed it, let's document why"
- "Got 5 new testimonials this month"
- "I changed my pricing, update everything"

The skill merges new content, preserving what exists.
