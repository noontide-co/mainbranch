# Legacy Config Cleanup

Main Branch now treats `.vip/*.yaml` as legacy cleanup/audit input. Runtime
skills should prefer CWD-first repo detection, `mb status --json --peek`,
`mb connect`, `mb onboard`, and current repo files over `.vip` YAML.

---

## File Locations

| File | Location | Purpose | Git-tracked? |
|------|----------|---------|--------------|
| `settings.local.json` | `[repo]/.claude/` | Grants Claude Code file access to the active Main Branch engine | No (auto git-ignored by Claude Code) |
| `local.yaml` | `~/.config/vip/` | Legacy machine-local fallback for user identity, engine path, and default repo | No |
| `env.sh` | `~/.config/vip/` | API keys for optional research tools | No |
| `config.yaml` | `[repo]/.vip/` | Legacy mixed repo config that must be audited before reuse | Maybe old repos tracked it |

**Key split:**
- **Settings** = "Where is Main Branch?" (per-repo, per-machine — `.claude/settings.local.json`)
- **Local** = "Who am I? What repo do I want?" legacy fallback (per-person, per-machine)
- **Env** = "What API keys do I have?" (per-person, sourced by shell)
- **Repo** = current business truth in `core/`, `research/`, `decisions/`,
  `bets/`, `pushes/`, `log/`, `documents/`, `.mb/connect.yaml`, and generated
  repo instructions. Do not use `.vip/config.yaml` as the current shared
  settings surface.

### .claude/settings.local.json (Main Branch linkage)

Created by `mb skill link` and `/mb-setup`. Tells Claude Code to load Main Branch as a read-only additional directory:

```json
{
  "permissions": {
    "additionalDirectories": ["/absolute/path/to/mainbranch"]
  }
}
```

**Auto git-ignored** by Claude Code (like `.claude/settings.local.json` is always local). Contains machine-specific absolute paths — never commit this.

### .claude/ bridge links (slash-command discovery)

`additionalDirectories` grants file access to Main Branch, but project-local
`.claude/skills/mb-*` bridge links are the supported slash-command discovery
surface. Runtime smoke on Claude Code 2.1.126 returned `Unknown command:
/mb-start` when the project-local `.claude/skills/mb-start` bridge was missing,
even though `settings.local.json` still pointed at the engine.

```
business-repo/.claude/
├── settings.local.json       # real file (auto git-ignored)
├── skills/                   # real local folder (for project custom skills)
│   ├── mb-start -> /path/to/mainbranch/.claude/skills/mb-start
│   ├── mb-ads   -> /path/to/mainbranch/.claude/skills/mb-ads
│   └── ... (only missing entries linked)
```

Created by `mb skill link` and `/mb-setup`. `/mb-start` can auto-repair missing
links. Old clone-based repos may also have `.claude/lenses/` or
`.claude/reference/` symlinks; those are legacy link dirs that `mb doctor
repair` can move to backup when they point at stale engine clones.

**Both are needed:**
- `additionalDirectories` = file access (reading reference files across repos)
- Bridge links = slash-command discovery for Main Branch skills

---

## Environment Variables (~/.config/vip/env.sh)

API keys for optional research tools. Created during `/mb-setup`, sourced by shell on startup.

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

**Created by:** `/mb-setup` when optional API-key setup is needed. Tool-specific setup guides also reference this file: `mb-think/references/gemini-setup.md`, `mb-think/references/grok-setup.md`, `mb-setup/references/nano-banana-setup.md`.

**Shell integration:** `/mb-setup` adds this line to `~/.zshrc` or `~/.bashrc`:
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
# /mb-start writes absolute paths automatically when saving config.
vip_path: /absolute/path/to/mainbranch  # legacy key name; points at Main Branch
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
# /mb-site uses default_concepts to set how many home-page concepts
# get generated in parallel. Default 2; raise to 3 or 5 if you're
# OK spending more tokens for more variation.
default_concepts: 2

# CHANGELOG version tracking (managed by /mb-start and /mb-update)
# Last engine version the user has seen the "what's new" banner for.
# Diff'd against the most recent versioned heading in
# the active engine's `CHANGELOG.md` to decide whether to surface unread entries.
# Bumped when the user routes to any skill or types "dismiss".
last_seen_version: "0.1.0"
```

**CRITICAL: Always use absolute paths, never `~`.** The Glob and Read tools do not expand `~`, causing silent failures (0 results when files exist). When writing to `local.yaml`, always expand `~` to the full absolute path first. If `local.yaml` already contains `~`, auto-upgrade it to absolute during path validation.

**Media paths** are machine-specific (contain usernames, sync folder locations). They belong in local.yaml, not repo config. Skills resolve media paths with a fallback chain: `media.{type}` → `media.root/{type}/` → ask user and save.

---

## Legacy Business Repo Config Audit

```bash
mb doctor repair --plan --json
```

Older repos may have `[repo]/.vip/config.yaml` with mixed key families:
business facts, MCP requirements, tool snapshots, infrastructure refs, content
defaults, skill defaults, client repo pointers, and old reference-structure
notes.

Do not load it as current truth. The doctor repair plan classifies keys without
printing raw values so private paths, provider notes, client context, and
credentials are not copied into chat or durable files. Move only still-current,
non-private facts into the appropriate current surface after operator review.

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
3. If yes: create or update `~/.config/vip/local.yaml` with that repo path, preserving existing keys.

---

## Missing Legacy Config

If repo has `core/` or legacy `reference/core/` but no `.vip/config.yaml`:

Do not create it. Use `mb status --json --peek`, `mb onboard status --json`,
`mb connect plan`, and current repo files instead.

---

## Migration Table

| Scenario | Behavior |
|----------|----------|
| New user, no repo | Route to `/mb-setup` |
| Existing user, no config | Discovery works, offer upgrade |
| Existing user, accepts | Fast path going forward |
| Existing user, declines | Works exactly as before |

---

## When Skills Read Config

| Skill | Reads | Purpose |
|-------|-------|---------|
| `/mb-start` | legacy local.yaml only when CWD/config discovery fails | Find default/recent repos as fallback |
| `/mb-start` | `mb status --json --peek`, `mb connect`, `mb onboard` | Check readiness, repairs, onboarding, provider state |
| `/mb-help` | legacy local.yaml only as optional fallback | Adjust verbosity based on experience |
| `/mb-ads`, `/mb-think` | local.yaml `media.*` | Resolve where non-markdown outputs go |

---

## When Skills Write Config

| Trigger | What's Written | Where |
|---------|----------------|-------|
| `/mb-setup` first run | Current repo files, `.claude/settings.local.json`, skill links, `.mb/` state | Business repo |
| User selects repo in `/mb-start` | `default_repo`, `recent_repos` only if legacy fallback is still being used and user confirms | local.yaml |
| User says "I'm advanced" | `user.experience` | local.yaml |
| User says "save as default" | Prefer current skill/workflow inputs; do not write `.vip/config.yaml` | n/a (no write) |
| User connects infrastructure | Provider metadata through `mb connect`; secrets stay local | `.mb/connect.yaml` and local secret stores |
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
2. Use `mb status --json --peek`, `mb connect`, and repo files for current facts
3. Path invalid? → attempt recovery, then clear and rediscover
4. Parse error? → warn, clear, rediscover
```

**Principle:** Config is a speed optimization, not a requirement.

---

## Config Hygiene (Stale Path Handling)

Users rename folders, move repos, or clone to new locations. Config paths go stale. `/mb-start` must handle this gracefully — a normie user won't know to say "fix my config."

### Validation Rule

**Before presenting ANY repo as a numbered option, verify the path exists:**

```bash
if test -d "[path]/core" || test -d "[path]/reference/core"; then echo "valid"; else echo "invalid"; fi
```

Never show a dead path. Never load a dead path and show "0/18 EMPTY" for a repo that simply moved.

### Recovery Algorithm

When a config path is invalid:

1. **Check parent directory** — if the parent exists, the folder was likely renamed
2. **Scan siblings** — look for `core/` or legacy `reference/core/` in adjacent folders
3. **If match found** — tell the user: "Looks like **[old-name]** moved to **[new-name]**. Updating your config."
4. **If no match** — silently drop the stale entry from the list

### Auto-Prune

After validation, if any paths were removed or updated, write the cleaned `local.yaml` immediately. Removing dead paths is housekeeping — no confirmation needed. Adding or changing the default repo still requires user confirmation.

### Common Scenarios

| What Happened | What User Sees | What /mb-start Does |
|---------------|---------------|-------------------|
| Folder renamed | Nothing broken | Detects new name, updates config, presents correct option |
| Folder deleted | Fewer options | Prunes dead entry, shows only valid repos |
| Folder moved to new parent | "Switch to different repo" | Can't auto-detect across parents — user provides new path, config updates |
| Clone to new machine | Empty config | Normal discovery flow — no stale paths to worry about |

---

## User Must Always Have Choice

**Even with valid saved config, `/mb-start` must list ALL validated repos from `recent_repos`:**

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
