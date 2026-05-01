# Config System

Four-file system: vip linkage, personal settings, team settings, and API keys — each in the right place.

---

## File Locations

| File | Location | Purpose | Git-tracked? |
|------|----------|---------|--------------|
| `settings.local.json` | `[repo]/.claude/` | Links vip as additionalDirectory | No (auto git-ignored by Claude Code) |
| `local.yaml` | `~/.config/vip/` | User identity + vip_path + default repo | No |
| `env.sh` | `~/.config/vip/` | API keys for optional research tools | No |
| `config.yaml` | `[repo]/.vip/` | Team/business settings, MCP requirements | Yes |

**Key split:**
- **Settings** = "Where is vip?" (per-repo, per-machine — `.claude/settings.local.json`)
- **Local** = "Who am I? What repo do I want?" (per-person, per-machine)
- **Env** = "What API keys do I have?" (per-person, sourced by shell)
- **Repo** = "How does this business/team operate?" (shared)

### .claude/settings.local.json (vip linkage)

Created by `/setup`. Tells Claude Code to load vip as a read-only additional directory:

```json
{
  "permissions": {
    "additionalDirectories": ["/absolute/path/to/vip"]
  }
}
```

**Auto git-ignored** by Claude Code (like `.claude/settings.local.json` is always local). Contains machine-specific absolute paths — never commit this.

### .claude/ bridge links (compatibility fallback)

`additionalDirectories` is the canonical config for loading vip. In some environments/versions, skill discovery can still be inconsistent. Compatibility links in local `.claude/` provide a fallback without changing user workflow.

```
business-repo/.claude/
├── settings.local.json       # real file (auto git-ignored)
├── skills/                   # real local folder (for project custom skills)
│   ├── start -> /path/to/vip/.claude/skills/start
│   ├── ads   -> /path/to/vip/.claude/skills/ads
│   └── ... (only missing entries linked)
├── lenses/                   # real local folder; missing vip entries linked
└── reference/                # real local folder; missing vip entries linked
```

Created by `/setup` as a compatibility layer. `/start` can auto-repair missing links.

**Both are needed:**
- `additionalDirectories` = file access (reading reference files across repos)
- Bridge links = compatibility fallback for skill discovery in affected environments

---

## Environment Variables (~/.config/vip/env.sh)

API keys for optional research tools. Created during `/setup`, sourced by shell on startup.

```bash
cat ~/.config/vip/env.sh 2>/dev/null
```

```bash
# Main Branch API Keys
# This file is sourced by your shell. Keep it outside git repos.

# === OPTIONAL RESEARCH TOOLS ===

# Gemini - Deep web research (free tier available)
# Get from: https://aistudio.google.com/apikey
# export GOOGLE_API_KEY=""

# xAI/Grok - X/Twitter sentiment analysis
# Get from: https://console.x.ai
# export XAI_API_KEY=""
```

| Variable | Tool | Purpose | How to Get |
|----------|------|---------|------------|
| `GOOGLE_API_KEY` | Gemini | Deep web research, multi-source synthesis | https://aistudio.google.com/apikey |
| `XAI_API_KEY` | Grok | X/Twitter sentiment, real-time social | https://console.x.ai |
| `APIFY_TOKEN` | Apify | (Usually in MCP config, not env.sh) | https://console.apify.com |

**Why this file exists:**
- Outside git repos (security — keys never committed)
- Sourced on shell startup (always available)
- Optional — system works without it (Apify handles most research)
- Progressive — add keys when you need them, not before

**Created by:** `setup/SKILL.md` Step 4a. Tool-specific setup guides also reference this file: `think/references/gemini-setup.md`, `think/references/grok-setup.md`, `setup/references/nano-banana-setup.md`.

**Shell integration:** `/setup` adds this line to `~/.zshrc` or `~/.bashrc`:
```bash
[ -f "$HOME/.config/vip/env.sh" ] && source "$HOME/.config/vip/env.sh"
```

**After adding a key:** Restart terminal or run `source ~/.config/vip/env.sh`.

---

## Machine-Local Settings

```bash
cat ~/.config/vip/local.yaml 2>/dev/null
```

```yaml
# NOTE: All paths MUST be absolute. Never use ~ (tools don't expand it).
# /start writes absolute paths automatically when saving config.
vip_path: /absolute/path/to/vip
default_repo: /absolute/path/to/my-business
recent_repos:
  - /absolute/path/to/my-business
  - /absolute/path/to/client-project

# User identity lives here, NOT in repo config
# Allows multiple people to work on same business repo
user:
  name: "Your Name"
  experience: advanced  # beginner | intermediate | advanced

# Media output configuration
# Where non-markdown outputs land (images, videos, exports)
# Machine-specific paths — different per computer
media:
  root: /absolute/path/to/Main Branch
  # Per-type overrides (optional — defaults to {root}/{type}/)
  # images: /absolute/path/to/ad-images
  # videos: /absolute/path/to/ad-videos

# Per-skill defaults (optional)
# /site uses default_concepts to set how many home-page concepts
# get generated in parallel. Default 2; raise to 3 or 5 if you're
# OK spending more tokens for more variation.
default_concepts: 2

# CHANGELOG version tracking (managed by /start and /pull)
# Last engine version the user has seen the "what's new" banner for.
# Diff'd against the most recent versioned heading in
# `<vip_path>/CHANGELOG.md` to decide whether to surface unread entries.
# Bumped when the user routes to any skill or types "dismiss".
last_seen_version: "0.1.0"
```

**CRITICAL: Always use absolute paths, never `~`.** The Glob and Read tools do not expand `~`, causing silent failures (0 results when files exist). When writing to `local.yaml`, always expand `~` to the full absolute path first. If `local.yaml` already contains `~`, auto-upgrade it to absolute during path validation.

**Media paths** are machine-specific (contain usernames, sync folder locations). They belong in local.yaml, not repo config. Skills resolve media paths with a fallback chain: `media.{type}` → `media.root/{type}/` → ask user and save.

---

## Business Repo Config (Team Settings)

```bash
cat [repo]/.vip/config.yaml 2>/dev/null
```

Key fields:
- `session.auto_load_reference` → Load core/ automatically
- `session.show_context_tips` → Team default for tips
- `mcps` → Required MCP servers for this business
- `tools` → Cached tool status (`status`, `notes`, `last_checked`) for self-healing detection in `/start` and `/think`
- `infrastructure` → Shared team resources (Railway, Postiz, etc.)
- `skills` → Team defaults for skill behavior

**Note:** `user.name` and `user.experience` are NOT here — they're in local.yaml.

---

## Migration from Old Settings

Existing users may have `~/.claude/settings.json` with `business_repo_path`.

**Detection:**
```bash
cat ~/.claude/settings.json 2>/dev/null | grep business_repo_path
```

**If found:**
1. Extract the path
2. Offer migration: "Found your repo in old settings. Migrate to new config?"
3. If yes: Create `~/.config/vip/local.yaml` with that path

---

## Creating Missing Config

If repo has `reference/core/` but no `.vip/config.yaml`:

> "Your repo exists but doesn't have VIP config. Create it?
> Benefits: faster startups, synced preferences, MCP tracking."

If yes → Create `.vip/config.yaml` with defaults from `/setup`.

---

## Migration Table

| Scenario | Behavior |
|----------|----------|
| New user, no repo | Route to /setup |
| Existing user, no config | Discovery works, offer upgrade |
| Existing user, accepts | Fast path going forward |
| Existing user, declines | Works exactly as before |

---

## When Skills Read Config

| Skill | Reads | Purpose |
|-------|-------|---------|
| `/start` | local.yaml | Find default repo, get user experience level |
| `/start` | repo config | Check MCP requirements, session preferences |
| `/help` | local.yaml | Adjust verbosity based on experience |
| Any skill | repo config `skills.*` | Get skill-specific preferences |
| `/ads`, `/think` | local.yaml `media.*` | Resolve where non-markdown outputs go |

---

## When Skills Write Config

| Trigger | What's Written | Where |
|---------|----------------|-------|
| `/setup` first run | Full local.yaml + repo config | Both files |
| User selects repo in `/start` | `default_repo`, `recent_repos` | local.yaml |
| User says "I'm advanced" | `user.experience` | local.yaml |
| User says "save as default" | Skill preference | repo config `skills.*` |
| User connects infrastructure | `infrastructure.*` | repo config |
| User configures media path | `media.root` or `media.{type}` | local.yaml |

**Rule:** Never write silently. Confirm changes that affect future sessions.

### Safe Write Pattern (CRITICAL)

When updating `~/.config/vip/local.yaml`:

1. Read the existing file first
2. Merge changes into existing keys (do not replace whole file)
3. Preserve unknown keys for forward compatibility
4. Ask before changing `default_repo` if one already exists
5. Write the merged result

**Never use full-file overwrite commands like:**
```bash
cat > ~/.config/vip/local.yaml
```

That pattern can silently delete fields (like `user.*`, `vip_path`, or future keys).

---

## Fallback Chain

Config is always optional. Skills work without it.

```
1. Try local.yaml → missing? → discovery
2. Try repo config → missing? → use defaults
3. Path invalid? → attempt recovery, then clear and rediscover
4. Parse error? → warn, clear, rediscover
```

**Principle:** Config is a speed optimization, not a requirement.

---

## Config Hygiene (Stale Path Handling)

Users rename folders, move repos, or clone to new locations. Config paths go stale. `/start` must handle this gracefully — a normie user won't know to say "fix my config."

### Validation Rule

**Before presenting ANY repo as a numbered option, verify the path exists:**

```bash
test -d "[path]/reference/core" && echo "valid" || echo "invalid"
```

Never show a dead path. Never load a dead path and show "0/18 EMPTY" for a repo that simply moved.

### Recovery Algorithm

When a config path is invalid:

1. **Check parent directory** — if the parent exists, the folder was likely renamed
2. **Scan siblings** — look for `reference/core/` in adjacent folders
3. **If match found** — tell the user: "Looks like **[old-name]** moved to **[new-name]**. Updating your config."
4. **If no match** — silently drop the stale entry from the list

### Auto-Prune

After validation, if any paths were removed or updated, write the cleaned `local.yaml` immediately. Removing dead paths is housekeeping — no confirmation needed. Adding or changing the default repo still requires user confirmation.

### Common Scenarios

| What Happened | What User Sees | What /start Does |
|---------------|---------------|-------------------|
| Folder renamed | Nothing broken | Detects new name, updates config, presents correct option |
| Folder deleted | Fewer options | Prunes dead entry, shows only valid repos |
| Folder moved to new parent | "Switch to different repo" | Can't auto-detect across parents — user provides new path, config updates |
| Clone to new machine | Empty config | Normal discovery flow — no stale paths to worry about |

---

## User Must Always Have Choice

**Even with valid saved config, `/start` must list ALL validated repos from `recent_repos`:**

> "Found your repos:
>
> 1. [default-repo-name] (saved default)
> 2. [other-repo-name]
> 3. Switch to different repo
>
> (hit a number)"

If only one repo: show it plus "Switch to different repo."

**After switching:** Ask "Want me to save [repo-name] as your default?" If yes, update `default_repo`.

**Never auto-proceed without asking.** The saved default is a suggestion, not a lock-in.
