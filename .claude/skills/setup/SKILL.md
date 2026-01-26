---
name: setup
description: Bootstrap a new business repo with Main Branch structure. Use when: (1) New user needs Claude Code environment configured (2) User says "set up", "get started", "initialize", "bootstrap", "create my repo", "new business" (3) User is new to Main Branch and needs full onboarding (4) Migrating existing business context into the Main Branch structure. Creates Chrome extension setup, two-repo model, business repo with full structure. Gathers context aggressively until complete. Applies domain rubrics by business type.
---

# Repo Setup

Get a new user fully configured with Claude Code and their business repo.

---

## Before We Begin

**Need help?** Type `/help` + your question anytime. If conversation compacts (gets summarized), `/help` reloads fresh context.

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

### Check Location — Create Business Repo if Needed (CRITICAL: DO THIS FIRST)

**This must happen BEFORE context gathering.** If the conversation compacts later, the essential config is already saved.

**Check if we're in the vip (engine) repository:**

```bash
# If this succeeds, we're in vip
ls .claude/skills/setup/SKILL.md 2>/dev/null
```

**If we're in vip, CREATE the business repo for them:**

> "You're in vip — that's the engine. Let me create your business repo."

1. **Ask for business name:**
   > "What do you want to call your business folder? (e.g., 'my-agency', 'acme-coaching')"

2. **Create the folder and init git:**
   ```bash
   mkdir -p ~/Documents/GitHub/[business-name]
   cd ~/Documents/GitHub/[business-name] && git init
   ```

3. **IMMEDIATELY save to machine-local settings:**

   This ensures `/start` can find the business repo in future sessions.

   Create/update `~/.config/vip/local.yaml`:
   ```bash
   mkdir -p ~/.config/vip
   ```

   ```yaml
   # ~/.config/vip/local.yaml
   # Machine AND user specific — NOT git-tracked
   default_repo: /Users/[username]/Documents/GitHub/[business-name]
   recent_repos:
     - /Users/[username]/Documents/GitHub/[business-name]

   # User identity lives here (allows multi-user on same repo)
   user:
     name: "[User's name]"
     experience: beginner  # beginner | intermediate | advanced
   ```

   Use the actual expanded path (not ~). Ask user for their name and experience level.

4. **Add it as a working directory:**
   ```
   /add-dir ~/Documents/GitHub/[business-name]
   ```

5. **Set the business repo as the target for all file writes:**
   From this point forward, write all files to `~/Documents/GitHub/[business-name]/` NOT to the current directory.

6. **Confirm the setup is saved:**
   > "Created [business-name] and saved the path. From now on, just run `/start` in vip and it'll load your business repo automatically.
   >
   > **Reminder:** If you ever get confused or the conversation compacts, type `/help` + your question. It has comprehensive answers about how everything works."

7. **Continue with setup** — proceed to Step 0 (Chrome extension) and beyond.

**If NOT in vip:** You're already in the user's business repo. Check if vip path is configured, continue normally.

---

### 0. Verify Chrome Extension (REQUIRED for Skool)

**Before gathering ANY context, check Chrome extension status:**

> Type `/chrome` to verify you have the Claude in Chrome extension installed.

If not installed:
> "The Chrome extension is fundamental for Main Branch — it lets me read your sales pages, Skool community, and web content directly. Install it now: https://claude.ai/chrome (requires Google Chrome)"

**If user declines:** Proceed with Playwright or manual screenshots, but note this limits what can be gathered automatically.

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
which whisper-cli ffmpeg
```

If missing, note for later:
> "Optional: For transcribing your own videos/voice memos, you'll want whisper-cpp. We can set that up later with `/think`."

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

Read the appropriate rubric from `vip/.claude/reference/domain-rubrics/`.

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
mkdir -p .vip
mkdir -p reference/core reference/brand reference/proof/angles reference/domain
mkdir -p research decisions outputs content/drafts content/scheduled content/published
```

Full structure:
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

### 4a. API Key Environment (Progressive Setup)

Create the env.sh template for optional research tools. This lives outside git repos for security.

```bash
mkdir -p ~/.config/vip
cat > ~/.config/vip/env.sh << 'EOF'
# Main Branch API Keys
# This file is sourced by your shell. Keep it outside git repos.

# === OPTIONAL RESEARCH TOOLS ===
# These unlock additional capabilities. Add as needed.

# Gemini - Deep web research (free tier available)
# Get from: https://aistudio.google.com/apikey
# export GOOGLE_API_KEY=""

# xAI/Grok - X/Twitter sentiment analysis
# Get from: https://console.x.ai
# export XAI_API_KEY=""
EOF
```

Add source line to shell config (detects zsh vs bash):

```bash
# Detect shell and add source line
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ]; then
  grep -q 'source.*vip/env.sh' ~/.zshrc 2>/dev/null || \
    echo '[ -f "$HOME/.config/vip/env.sh" ] && source "$HOME/.config/vip/env.sh"' >> ~/.zshrc
else
  grep -q 'source.*vip/env.sh' ~/.bashrc 2>/dev/null || \
    echo '[ -f "$HOME/.config/vip/env.sh" ] && source "$HOME/.config/vip/env.sh"' >> ~/.bashrc
fi
```

**Explain to user:**
> "Created `~/.config/vip/env.sh` for API keys. It's outside git repos (security) and sourced on shell startup.
>
> You don't need keys now — Apify handles most research. Add Gemini/Grok later if you want deep research capabilities."

**Progressive disclosure:** Don't overwhelm beginners with API setup. The env.sh exists but stays empty until they need it.

### 4b. Create Initial Config

Create `.vip/config.yaml` with team/business settings:

```yaml
# .vip/config.yaml
# VIP configuration for this business
# Git-tracked, shared by all collaborators
# NOTE: User identity (name, experience) is in ~/.config/vip/local.yaml

version: 1

# === SESSION (Team Defaults) ===
session:
  auto_load_reference: true
  show_context_tips: true  # Context management tips for beginners
  warn_at_context_pct: 75

# === INFRASTRUCTURE ===
# Populated when services are connected
infrastructure:
  railway:
    project_id: null
  postiz:
    api_url: null
    api_key_ref: null  # keychain:vip/postiz or env:POSTIZ_API_KEY
  r2:
    bucket: null
    public_url: null

# === MCP SERVERS ===
# Track which MCPs this business needs
# /start verifies these are installed, prompts setup if missing
mcps:
  apify:
    required_for: [organic, think]  # Handles web scraping AND YouTube transcripts
    setup_guide: ".claude/skills/organic/references/apify-setup.md"

# === CONTENT ===
content:
  default_channels: []
  require_review: true

# === SKILL PREFERENCES ===
skills:
  ads:
    default_format: static
  think:
    auto_create_tasks: false
```

### 4c. Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Secrets
.env
*.env.local

# OS
.DS_Store

# Editor
.vscode/
.idea/
EOF
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

## After Setup: What's Next

Once setup is complete, tell the user:

> "Your business repo is ready! Here's what to do next:
>
> **Daily workflow:**
> ```
> cd ~/Documents/GitHub/vip
> claude
> /start
> ```
>
> **Key skills to try:**
> - `/think` — Research topics, make decisions, update reference
> - `/ads` — Generate image ads, video scripts, or review for compliance
> - `/vsl` — Write video sales letters (Skool or B2B)
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
