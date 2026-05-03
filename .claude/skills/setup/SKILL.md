---
name: setup
description: "Bootstrap a new business repo with Main Branch structure, or migrate an existing single-offer repo to multi-offer. Use when: (1) New user needs Claude Code environment configured (2) User says \"set up\", \"get started\", \"initialize\", \"bootstrap\", \"create my repo\", \"new business\" (3) User is new to Main Branch and needs full onboarding (4) Migrating existing business context into the Main Branch structure (5) User wants to add a second offer to an existing repo. Creates Chrome extension setup, two-repo model, business repo with full structure. Gathers context aggressively until complete. Applies domain rubrics by business type. Teaches concepts during setup."
---

# Repo Setup

Get a new user fully configured with Claude Code and their business repo. Use
`mb onboard status --json` and `mb onboard plan` as the durable progress
contract; do not keep onboarding state only in chat prose.

---

## Before We Begin

**Need help?** Type `/help` + your question anytime. If conversation compacts (gets summarized), `/help` reloads fresh context.

---

## Workflow

### CRITICAL: Write Boundaries in Sandboxed Environments

Some tools (especially workspace-isolated apps, like Conductor workspaces) may only allow direct file writes inside the current workspace folder. If you see:

> "Cannot edit files outside allowed directories"

In a regular terminal `claude` session, this is less common because Claude can often request permission and continue. In restricted workspace tools, limits are usually stricter.

Do **not** silently switch strategies. Ask the user first, in beginner language:

> "This app is only letting me edit files in this one workspace folder.
>
> Since this is first-time setup, switching workspaces mid-chat can be confusing. The easiest options are:
> 1. Continue here and I use terminal commands to create/update files in your target repo path
> 2. Stop here, open Terminal in the target repo folder, run `claude`, then run `/setup` again
>
> If you already have a workspace open for that repo, we can use that too. Which option do you want?"

For first-time setup, do not default to "switch workspace now." Prefer option 1 or 2 unless the user already has the target repo workspace ready.

### Pull Latest Engine Updates and Detect CWD (FIRST)

**Pull vip + detect CWD before context gathering.** Three cases: CWD is the business repo (happy path), CWD is vip (migration), or CWD is neither (ask user).

See **[references/cwd-detection.md](references/cwd-detection.md)** for the full pull script and all three cases (Case 1 happy path, Case 2 vip migration, Case 3 ask). This must happen BEFORE any context gathering — if conversation compacts later, the essential config is already saved.

---

### 0. Check Chrome Extension (Optional, Helpful for Skool)

**Before gathering context, mention the Chrome extension:**

> "The Claude in Chrome extension lets me read your sales pages, Skool community, and web content directly. It's optional but helpful.
>
> To check if it's installed: open Chrome, go to `chrome://extensions`, and look for 'Claude'. If you don't have it: https://claude.ai/chrome"

**If not installed or user declines:** Proceed with URL fetching, Playwright, or manual screenshots. The extension is convenient but not required.

### 1. Confirm Git + Working Directory

```bash
git status  # Verify we're in a git repo
pwd         # Confirm working directory
```

If not a git repo:
```bash
git init
```

### 1a. Check Optional Tools (Inform, Don't Block)

**Local transcription (for mining your own recordings):**
```bash
which mlx_whisper 2>/dev/null || which whisper-cli 2>/dev/null; which ffmpeg
```

If missing, note for later:
> "Optional: For transcribing your own videos/voice memos, you'll want a whisper variant. `pip3 install mlx-whisper` is fastest on Apple Silicon. We can set that up later with `/think`."

Don't block setup on this. Continue and mention it at the end.

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

Read the appropriate rubric from `.claude/reference/domain-rubrics/ (in vip)`.

### 2.5: Offer Structure

After business type, determine offer structure:

> "How many distinct products or services do you sell?"

**If one:** "Single offer — clean and simple. All your details go in `reference/core/`. Most people start here."

**If multiple:** "Multiple offers under one brand. You share the same soul and voice, but each offer has its own specifics."
- Ask: "What should we call each offer? Short slugs work best (e.g., 'community', 'newsletter', 'done-for-you')"
- Ask: "How do these relate? Is there a natural progression — like a free tier that feeds into a paid one?" (This builds `product-ladder.md`)
- Store offer names for Step 4 folder creation
- Note: The multi-offer rubric lives at `.claude/reference/domain-rubrics/multi-offer.md` (in vip) — read it if the user has multiple offers

**Multi-business check (brief, not interrogating):**
> "Are any other business repos relevant right now? If you run completely separate brands, they each get their own repo. We're setting up this one."

This check is simple and non-intrusive. If they say yes, note it and move on — they can run `/setup` again in the other repo later.

### 3. Gather Bounded Context

Your job is to collect enough to create a useful core reference, not every fact
possible. Users provide context in batches. Keep the first pass bounded by
`mb onboard status --json` and its missing inputs.

Before asking for data, run:

```bash
mb onboard status --repo "$REPO_PATH" --json
```

If business type, team size, success stage, or desired outcome are missing, ask
briefly and save them:

```bash
mb onboard plan --repo "$REPO_PATH" --team-size solo --success-stage working
```

Do not ask for full finances, credentials, raw customer/member exports, or
exhaustive operations details during first-pass onboarding.

See **[references/context-gathering.md](references/context-gathering.md)** for:
- URL fetching fallback chain (WebFetch → Chrome → Playwright → manual)
- Business-type specific checklists (Skool, E-commerce, Coaching)
- Completeness criteria

**Opening prompt:**
> Share the essentials for the core reference: what you sell, who it helps, why
> it works, proof you can share, and a few voice samples.
>
> **Pro tip:** You can drag screenshots directly into this terminal window and I'll read them. If you have a Skool community, screenshot your about page, classroom, pricing — drag them all in. Fastest way to get me up to speed.
>
> Paste text, share file paths, give me URLs to fetch, or drag in images. I'll sort it all into the right files.

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
# Always create:
mkdir -p .vip
mkdir -p reference/core reference/visual-identity reference/proof/angles reference/domain
mkdir -p research decisions campaigns documents
```

**Multi-offer only (if user has multiple offers from Step 2.5):**

```bash
# Create offer folders for each offer
for offer in [offer-names]; do
  mkdir -p "reference/offers/$offer"
done

# Write initial current_offer
echo "current_offer: [first-offer]" > .vip/local.yaml

# Ensure .vip/local.yaml is git-ignored (session state, not shared)
grep -q ".vip/local.yaml" .gitignore 2>/dev/null || echo ".vip/local.yaml" >> .gitignore

# Create product-ladder.md placeholder
mkdir -p reference/domain
```

Full structure (single-offer):
```
{business-name}/
├── CLAUDE.md              # Always loaded - business brain
├── README.md              # Human-readable overview
├── .env                   # Secrets (gitignored)
├── .gitignore             # Include .env
│
├── .vip/                  # VIP configuration (git-tracked)
│   └── config.yaml        # User preferences, infrastructure refs
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
│       └── content-strategy.md  # Content pillars, platforms, cadence
│
├── research/              # Dated investigations
│   └── YYYY-MM-DD-topic-[source].md
│
├── decisions/             # Dated choices with rationale
│   └── YYYY-MM-DD-topic.md
│
└── outputs/               # All generated content (lifecycle via frontmatter status)
    └── YYYY-MM-DD-batch-name/
```

Full structure (multi-offer — adds `offers/` and `product-ladder.md`):
```
{business-name}/
├── ...                    # Same as above, plus:
├── reference/
│   ├── core/              # Brand-level (shared)
│   │   ├── soul.md        # ALWAYS core — brand identity
│   │   ├── offer.md       # Brand thesis (high-level)
│   │   ├── audience.md    # Shared audience
│   │   └── voice.md       # ALWAYS core — brand voice
│   ├── offers/            # Offer-specific overrides
│   │   ├── community/
│   │   │   └── offer.md   # Offer-specific details
│   │   └── course/
│   │       └── offer.md
│   └── domain/
│       ├── product-ladder.md      # How offers relate
│       └── content-strategy.md
└── .vip/
    ├── config.yaml        # Git-tracked team settings
    └── local.yaml         # Git-IGNORED session state (current_offer)
```

### 4a. API Key Environment, Config, and .gitignore

See **[references/repo-scaffolding.md](references/repo-scaffolding.md)** for:
- API key environment setup (`~/.config/vip/env.sh`)
- Initial `.vip/config.yaml` template (includes `mcps:` section for MCP server tracking)
- `.gitignore` creation

Run these steps in order: create env.sh, add shell source line, create config.yaml, create .gitignore.

### 5. Sort Content into Files

**The repo is a precision instrument, not a dumping ground.** Not everything the user provides makes it into reference files. Filter for what helps LLMs produce great outputs.

Use templates from `references/templates.md`.

**Teach WHY each file matters as you create it.** Don't just scaffold — explain. This is the user's first encounter with the system. The act of writing these files IS the learning.

See **[references/file-education.md](references/file-education.md)** for the educational blurbs to present before writing each core file (soul, offer, audience, voice, multi-offer additions), the priority order, and the visual style scaffolding questions.

### 6. Apply Domain Rubric

Based on business type, create domain-specific folders:

**E-commerce:** `reference/domain/products/`, `reference/domain/fulfillment/`
**Community:** `reference/domain/classroom/`, `reference/domain/membership/`, `reference/domain/funnel/`, `reference/domain/content-strategy.md`, `reference/domain/funnel/skool-surfaces.md`

See `.claude/reference/domain-rubrics/ (in vip)` for full specifications.

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
| core/soul.md | [OK] Complete / [WARN] Missing [X] |
| core/offer.md | [OK] Complete / [WARN] Missing [X] |
| core/audience.md | [OK] Complete / [WARN] Missing [X] |
| core/voice.md | [OK] Complete / [WARN] Missing [X] |
| proof/testimonials.md | [OK] Has content / [FAIL] Empty |
| proof/angles/ | [OK] [N] angles / [WARN] None yet |
| domain/ | [OK] Populated / [WARN] Needs [X] |

**Multi-offer additional checks (if applicable):**

| File | Status |
|------|--------|
| offers/[name]/offer.md | [OK] Complete / [WARN] Thin (< 20 lines) / [FAIL] Missing |
| domain/product-ladder.md | [OK] Complete / [WARN] Placeholder |
| .vip/local.yaml | [OK] Set to [offer] / [FAIL] Missing |

Ask user for missing pieces or note for later.

---

## Git Workflow

Format: `[type] Brief description` with Co-Authored-By line. Types: `[init]`, `[add]`, `[update]`, `[fix]`, `[refactor]`, `[docs]`. See `references/git-workflow.md` for full guide.

---

## References

- **CWD Detection:** `references/cwd-detection.md` — Pull engine updates + Case 1/2/3 flows for detecting where the user is
- **File Education:** `references/file-education.md` — What to teach the user about each core file, priority order, visual style scaffolding
- **Context Gathering:** `references/context-gathering.md` — Checklists by business type, completeness criteria
- **Templates:** `references/templates.md` — All file templates
- **CLAUDE.md Guide:** `references/claude-md-guide.md` — How to draft a good CLAUDE.md
- **Git Workflow:** `references/git-workflow.md` — Commit messages and CLI usage
- **Repo Scaffolding:** `references/repo-scaffolding.md` — API keys, config.yaml, .gitignore
- **Multi-Offer Migration:** `references/migration-multi-offer.md` — Single to multi-offer migration

---

## Recovering from Compaction

If conversation compacts mid-setup:

**For the user:** Type `/setup` again and describe where you were:
- "We're in the middle of gathering context for my Skool community"
- "I was giving you screenshots, you hadn't created files yet"
- "You created the folder structure but we haven't sorted content"

**For Claude:** When resuming:
1. Check if business repo exists (look for `reference/core/`)
2. If exists, check which files are populated vs empty
3. Resume from the appropriate step based on what's done
4. Confirm with user: "I see [business-name] with [X] files. Looks like we're at step [N]. Continue?"

---

## Migration: Single-Offer to Multi-Offer

When an existing user wants to add another offer (says "I want to add another offer", "I have a second product", or similar), follow the migration guide.

See **[references/migration-multi-offer.md](references/migration-multi-offer.md)** for the complete migration flow: detection, naming, atomic execution, brand-level offer.md creation, product-ladder.md, and commit.

---

## After Setup: What's Next

Once setup is complete, tell the user:

> "Your business repo is ready! Here's what to do next:
>
> **Daily workflow:**
> ```
> cd ~/Documents/GitHub/[business-name]
> claude
> /start
> ```
> vip linkage is managed by setup (`settings.local.json` + compatibility bridge links) — no need to touch the vip folder.
>
> **Key skills to try:**
> - `/think` — Research topics, make decisions, update reference
> - `/think` — Build your content strategy (pillars, platforms, cadence) — start here after core reference is solid
> - `/ads` — Generate image ads, video scripts, or review for compliance
> - `/vsl` — Write video sales letters (Skool or B2B)
> - `/organic` — Create social content aligned to your content pillars
> - `/help` — Get answers anytime you're stuck
>
> **The core loop:** Use `/think` regularly. Research → Decide → Codify. This is how your reference files get smarter over time.
>
> **Remember:** Type `/help` + your question anytime. It has comprehensive answers about Terminal basics, the two-repo model, skills, troubleshooting, and more."

**If whisper-cpp was missing during setup:**

> "One more thing: To transcribe your own videos and voice memos, install whisper-cpp:
> ```bash
> brew install whisper-cpp ffmpeg
> mkdir -p ~/.whisper
> curl -o ~/.whisper/ggml-base.en.bin -L \
>   'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin'
> ```
> Then `/think` can mine your recordings directly."

**If the user wants image generation:**

> "Want to generate actual images for ads and content? See `references/nano-banana-setup.md` for Nano Banana setup (uses your existing Google API key)."
