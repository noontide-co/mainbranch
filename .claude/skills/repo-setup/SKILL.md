---
name: Repo Setup
description: |
  Bootstrap a new business repo with the complete Main Branch structure. Use when:
  (1) Setting up a new client/business repo from scratch
  (2) User says "set up my repo", "initialize my business", or "create my KB"
  (3) Migrating existing business context into structured reference files
  (4) User asks how to organize their business information for AI

  Creates: CLAUDE.md, README.md, full folder structure, core reference files.
  Applies domain rubrics (e-commerce, community, coaching) based on business type.
  Uses GitHub CLI for proper version control from the start.
---

# Repo Setup

Bootstrap a business repo by gathering context, creating structure, and drafting core files.

---

## The Two-Repo Model

```
ENGINE (main-branch-premium)     +     DATA (your business repo)
├── Skills                             ├── reference/
├── Lenses                             ├── research/
├── Domain rubrics                     ├── decisions/
└── You PULL updates                   └── You OWN and EDIT this
```

**main-branch-premium** = The engine. You clone it, pull updates, but never edit it.

**your-business-repo** = Your data. You create it, own it, commit to it. This is where YOUR business context lives.

**How they connect:** In Claude Code, add main-branch-premium as an "additional working directory." Skills from the engine read your business repo's `reference/` and output to your `outputs/`.

---

## Philosophy

**This is not a one-time setup.** Reference files are living documents.

```
Research → Decide → Codify reference → Generate outputs → Learn → Repeat
```

Start messy. Refine continuously. The system gets smarter because the owner stays present with the business.

---

## Workflow

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
| **E-commerce** | Products, fulfillment, materials |
| **Community/Skool** | Classroom, membership, funnel |
| **Coaching/Services** | Offers, delivery, packages |
| **Agency** | Services, clients, processes |
| **Other** | Core only, no domain-specific |

Read the appropriate rubric from `main-branch-premium/.claude/reference/domain-rubrics/`.

### 3. Request Context Dump

> Dump everything about this business — sales pages, offer details, testimonials, notes, whatever exists. Paste text, share file paths, or give me URLs to fetch. I'll sort it into the right files.

Accept:
- Pasted text
- File paths to read
- URLs to fetch (WebFetch)
- "Read my existing [file]"
- Voice memos transcribed

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

See `main-branch-premium/.claude/reference/domain-rubrics/` for full specifications.

### 7. Draft CLAUDE.md

See `references/claude-md-guide.md` for structure.

**Key sections:**
- One-line description
- Engine reference (main-branch-premium)
- Folder structure diagram
- Business summary
- Quick reference (audience, voice, offer)
- Key decisions/research index
- Reference tiers

### 8. Create README.md

Simple human-readable overview:
- What the business is
- How to use the repo with main-branch-premium
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
