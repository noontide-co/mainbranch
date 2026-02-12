---
name: setup
description: Bootstrap a new business repo with Main Branch structure, or migrate an existing single-offer repo to multi-offer. Use when: (1) New user needs Claude Code environment configured (2) User says "set up", "get started", "initialize", "bootstrap", "create my repo", "new business" (3) User is new to Main Branch and needs full onboarding (4) Migrating existing business context into the Main Branch structure (5) User wants to add a second offer to an existing repo. Creates Chrome extension setup, two-repo model, business repo with full structure. Gathers context aggressively until complete. Applies domain rubrics by business type. Teaches concepts during setup.
---

# Repo Setup

Get a new user fully configured with Claude Code and their business repo.

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

### Pull Latest Engine Updates (Always)

**Before anything else, ensure vip is up to date:**

```bash
# Canonical vip resolution (settings.local.json first — no extra deps)
VIP_PATH=$(python3 -c "
import json, os
try:
    with open('.claude/settings.local.json') as f:
        dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
    for d in dirs:
        if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
            print(d); break
except: print('')
" 2>/dev/null)

# Fallback: check ~/.config/vip/local.yaml (needs PyYAML)
if [ -z "$VIP_PATH" ] || [ ! -f "$VIP_PATH/.claude/skills/start/SKILL.md" ]; then
  VIP_PATH=$(python3 -c "
import os
try:
    import yaml
    with open(os.path.expanduser('~/.config/vip/local.yaml')) as f:
        print(yaml.safe_load(f).get('vip_path', ''))
except: print('')
" 2>/dev/null)
fi

# Pull if found and valid
[ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ] && \
  git -C "$VIP_PATH" pull origin main 2>&1
```

If updates pulled: briefly note "Pulled latest engine updates." then continue.
If vip not found: note it — will be configured during setup.
If offline or already current: continue silently.

---

### Check Location and Configure vip (CRITICAL: DO THIS FIRST)

**This must happen BEFORE context gathering.** If the conversation compacts later, the essential config is already saved.

**Detect where we are:**

```bash
# Check CWD for business repo fingerprint
test -d "reference/core" && echo "IS_BUSINESS_REPO"

# Check CWD for vip fingerprint
test -f ".claude/skills/setup/SKILL.md" && echo "IS_VIP"
```

---

#### Case 1: CWD IS the Business Repo (Happy Path)

User started Claude in their business repo. Confirm and configure vip:

> "You're in your business repo — perfect."

1. **Check if vip is already configured:**
   ```bash
   test -f ".claude/settings.local.json" && python3 -c "
   import json, os
   with open('.claude/settings.local.json') as f:
       dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
   for d in dirs:
       if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
           print('VIP_LOADED'); break
   " 2>/dev/null
   ```

2. **If vip NOT loaded:** Ask for vip path and configure:
   > "Where is your vip folder? (usually `~/Documents/GitHub/vip`)"

   Create `.claude/settings.local.json` (auto git-ignored by Claude Code):
   ```json
   {
     "permissions": {
       "additionalDirectories": ["/absolute/path/to/vip"]
     }
   }
   ```

   **Create compatibility symlinks for skill discovery** (without replacing local folders):
   ```bash
   VIP_PATH="/absolute/path/to/vip"
   mkdir -p .claude/skills .claude/lenses .claude/reference

   # Link each vip skill folder only if missing (preserves local custom skills)
   for d in "$VIP_PATH"/.claude/skills/*; do
     [ -d "$d" ] || continue
     n=$(basename "$d")
     [ -e ".claude/skills/$n" ] || ln -s "$d" ".claude/skills/$n"
   done

   # Bridge lenses/reference similarly without overwriting local files
   for p in "$VIP_PATH"/.claude/lenses/* "$VIP_PATH"/.claude/reference/*; do
     [ -e "$p" ] || continue
     base=$(basename "$p")
     parent=$(basename "$(dirname "$p")")
     [ -e ".claude/$parent/$base" ] || ln -s "$p" ".claude/$parent/$base"
   done
   ```

   Update `~/.config/vip/local.yaml` with a **merge** (never overwrite):
   - Read existing file first (if present)
   - Preserve unknown keys
   - Set/update `vip_path`
   - Add this repo to `recent_repos` (prepend + dedupe)
   - Keep `user.*` if present; ask only when missing
   - If `default_repo` is already set to a different repo, ask before changing it

   **Never use:** `cat > ~/.config/vip/local.yaml`

   > "Configured. vip is now linked for file access, and compatibility bridge links are in place for skill discovery."

3. **If vip loaded:** Check compatibility symlinks exist (without clobbering local files):
   ```bash
   # At minimum, /start must be discoverable
   test -e ".claude/skills/start" && echo "START_BRIDGE_OK"
   ```
   If missing, recreate missing links using the loop above. Never replace the entire `.claude/skills` directory.

---

#### Case 2: CWD IS vip (Old Workflow — Migration)

User started Claude in the engine folder. Guide them to the new workflow:

> "You're in vip — that's the engine. The recommended workflow is now to run Claude from your business repo instead. Let me set that up."

1. **Check if business repo exists:**
   ```bash
   cat ~/.config/vip/local.yaml 2>/dev/null
   ```

2. **If repo exists:** Guide user to switch:
   > "Found your repo at [path]. Close this session, then:
   > ```
   > cd [path]
   > claude
   > /start
   > ```
   > Want me to configure vip as an additional directory there first?"

   If yes, write `.claude/settings.local.json` in the business repo AND create compatibility links:
   ```bash
   VIP_PATH="/absolute/path/to/vip"
   REPO_PATH="[repo-path]"
   mkdir -p "$REPO_PATH"/.claude/skills "$REPO_PATH"/.claude/lenses "$REPO_PATH"/.claude/reference
   # settings.local.json (write via tool or bash)
   for d in "$VIP_PATH"/.claude/skills/*; do
     [ -d "$d" ] || continue
     n=$(basename "$d")
     [ -e "$REPO_PATH/.claude/skills/$n" ] || ln -s "$d" "$REPO_PATH/.claude/skills/$n"
   done
   for p in "$VIP_PATH"/.claude/lenses/* "$VIP_PATH"/.claude/reference/*; do
     [ -e "$p" ] || continue
     base=$(basename "$p")
     parent=$(basename "$(dirname "$p")")
     [ -e "$REPO_PATH/.claude/$parent/$base" ] || ln -s "$p" "$REPO_PATH/.claude/$parent/$base"
   done
   ```
   If direct write is blocked by sandbox boundaries, use the write-boundary decision flow above (ask first, then use terminal commands only if user agrees).

3. **If NO repo exists:** Create one:
   > "Let me create your business repo first."

   a. Ask for business name
   b. Create the folder and init git:
      ```bash
      mkdir -p ~/Documents/GitHub/[business-name]
      cd ~/Documents/GitHub/[business-name] && git init
      ```
   c. Create `.claude/settings.local.json` AND compatibility links in the NEW repo:
      ```bash
      VIP_PATH="/absolute/path/to/vip"
      mkdir -p ~/Documents/GitHub/[business-name]/.claude/skills \
               ~/Documents/GitHub/[business-name]/.claude/lenses \
               ~/Documents/GitHub/[business-name]/.claude/reference
      ```
      Write `settings.local.json`:
      ```json
      {
        "permissions": {
          "additionalDirectories": ["/absolute/path/to/vip"]
        }
      }
      ```
      Create compatibility links without replacing local directories:
      ```bash
      REPO_PATH=~/Documents/GitHub/[business-name]
      for d in "$VIP_PATH"/.claude/skills/*; do
        [ -d "$d" ] || continue
        n=$(basename "$d")
        [ -e "$REPO_PATH/.claude/skills/$n" ] || ln -s "$d" "$REPO_PATH/.claude/skills/$n"
      done
      for p in "$VIP_PATH"/.claude/lenses/* "$VIP_PATH"/.claude/reference/*; do
        [ -e "$p" ] || continue
        base=$(basename "$p")
        parent=$(basename "$(dirname "$p")")
        [ -e "$REPO_PATH/.claude/$parent/$base" ] || ln -s "$p" "$REPO_PATH/.claude/$parent/$base"
      done
      ```
   d. Update `~/.config/vip/local.yaml` with a **merge** (never overwrite):
      - Read existing file first
      - Preserve existing/unknown keys
      - Set/update `vip_path`
      - Add new repo to `recent_repos` (prepend + dedupe)
      - Keep `user.*` if present; ask only when missing
      - Ask before changing `default_repo` if one already exists
   e. **Set the business repo as the target for all file writes:**
      From this point forward, write all files to `~/Documents/GitHub/[business-name]/` NOT to the current directory.
      If direct writes are blocked by workspace limits, use explicit terminal commands with full paths (after user approval via the decision flow above).
   f. Confirm:
      > "Created [business-name] and configured vip. Next time:
      > ```
      > cd ~/Documents/GitHub/[business-name]
      > claude
      > /start
      > ```"

4. **Continue with setup** — proceed to Step 0 (Chrome extension) and beyond.

---

#### Case 3: CWD is Neither

User is in some other directory. Ask what they want:

> "This doesn't look like a business repo or vip. Options:
>
> 1. Create a new business repo here
> 2. Tell me where your existing repo is
> 3. Start fresh (`/setup` will create everything)"

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

### 3. Gather Context (Be a Ruthless Journalist)

Your job: extract every fact possible. Don't settle for partial info. Users provide context in batches — keep asking until YOU say "we have enough."

See **[references/context-gathering.md](references/context-gathering.md)** for:
- URL fetching fallback chain (WebFetch → Chrome → Playwright → manual)
- Business-type specific checklists (Skool, E-commerce, Coaching)
- Completeness criteria

**Opening prompt:**
> Dump everything about this business — sales pages, offer details, testimonials, notes, whatever exists.
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
mkdir -p reference/core reference/brand reference/proof/angles reference/domain
mkdir -p research decisions outputs content/drafts content/scheduled content/published
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
├── content/               # Content lifecycle
│   ├── drafts/            # WIP content
│   ├── scheduled/         # Queued for posting
│   └── published/         # Archive
│
└── outputs/               # Generated assets
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

**Educational context for each core file:**

**soul.md** — Present before writing:
> "soul.md is WHY you exist. Not the marketing answer — the real one. Three questions: What do you research when no one's watching? What intersections excite you? What decisions feel like discovery vs obligation? This file is your reconnection fuel — when you're grinding and feel nothing, re-read it."

**offer.md** — Present before writing:
> "offer.md is WHAT you sell. Price, mechanism, deliverables, guarantee. Every ad, script, and piece of content reads this file. The clearer it is, the better everything downstream works."

**audience.md** — Present before writing:
> "audience.md is WHO buys. Not demographics — real people with specific pains, desires, and objections. The words in this file become the words in your ads."

**voice.md** — Present before writing:
> "voice.md is HOW you sound. Tone, vocabulary, phrases you always use, phrases you never say. This is what keeps AI sounding like you instead of generic."

**For multi-offer setups, also explain:**

**offer.md (brand-level)** — When creating the brand thesis:
> "This is your brand-level offer.md — the umbrella story. It covers what your brand stands for across all offers. Each specific offer gets its own file in `offers/[name]/offer.md` with pricing, mechanism, and details."

**product-ladder.md** — When creating:
> "product-ladder.md maps how your offers relate. Which one do people discover first? Where do they go next? This helps us create content and ads that guide people through your world."

**Priority order:**
1. `reference/core/soul.md` — Why you exist (reconnection fuel)
2. `reference/core/offer.md` — What you sell (or brand thesis if multi-offer)
3. `reference/core/audience.md` — Who buys
4. `reference/core/voice.md` — How you sound
5. `reference/proof/testimonials.md` — Social proof
6. `reference/proof/angles/` — Messaging entry points
7. `reference/brand/visual-style.md` — Visual brand identity (colors, typography, mood, image prompt fragments)
8. `reference/domain/content-strategy.md` — Content pillars, platforms, cadence (template for community businesses)
9. `reference/domain/funnel/skool-surfaces.md` — Live Skool about page + pricing card copy (community businesses with Skool)

**Multi-offer additional files (if applicable):**
10. `reference/offers/[name]/offer.md` — Offer-specific details for each offer
11. `reference/offers/[name]/audience.md` — Only if this offer targets a different segment
12. `reference/domain/product-ladder.md` — How offers relate to each other

> **Note:** content-strategy.md and visual-style.md start as templates and get filled through `/think` cycles. Not required at setup — scaffolded with placeholder sections.

**Visual style scaffolding:** After core reference is drafted, ask 3 quick questions to seed `visual-style.md`:
1. "What's your brand's visual mood?" (minimal/bold/editorial/playful/dark)
2. "What are your brand colors?" (hex codes or descriptions)
3. "What photography style fits?" (lifestyle/product/abstract/editorial)

Use answers + audience data to generate a starter `visual-style.md` from the template at `templates/modules/brand-style-template.md` (in vip). This file is consumed by `/ads` (image prompts), `/site` (CSS/design tokens), and `/organic` (visual consistency).

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
| core/soul.md | ✅ Complete / ⚠️ Missing [X] |
| core/offer.md | ✅ Complete / ⚠️ Missing [X] |
| core/audience.md | ✅ Complete / ⚠️ Missing [X] |
| core/voice.md | ✅ Complete / ⚠️ Missing [X] |
| proof/testimonials.md | ✅ Has content / ❌ Empty |
| proof/angles/ | ✅ [N] angles / ⚠️ None yet |
| domain/ | ✅ Populated / ⚠️ Needs [X] |

**Multi-offer additional checks (if applicable):**

| File | Status |
|------|--------|
| offers/[name]/offer.md | ✅ Complete / ⚠️ Thin (< 20 lines) / ❌ Missing |
| domain/product-ladder.md | ✅ Complete / ⚠️ Placeholder |
| .vip/local.yaml | ✅ Set to [offer] / ❌ Missing |

Ask user for missing pieces or note for later.

---

## Git Workflow

Format: `[type] Brief description` with Co-Authored-By line. Types: `[init]`, `[add]`, `[update]`, `[fix]`, `[refactor]`, `[docs]`. See `references/git-workflow.md` for full guide.

---

## References

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
