# Config System

Three-file system: personal settings, team settings, and API keys — each in the right place.

---

## File Locations

| File | Location | Purpose | Git-tracked? |
|------|----------|---------|--------------|
| `local.yaml` | `~/.config/vip/` | User identity + which repo is default | No |
| `env.sh` | `~/.config/vip/` | API keys for optional research tools | No |
| `config.yaml` | `[repo]/.vip/` | Team/business settings, MCP requirements | Yes |

**Key split:**
- **Local** = "Who am I? What repo do I want?" (per-person, per-machine)
- **Env** = "What API keys do I have?" (per-person, sourced by shell)
- **Repo** = "How does this business/team operate?" (shared)

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
default_repo: ~/Documents/GitHub/my-business
recent_repos:
  - ~/Documents/GitHub/my-business
  - ~/Documents/GitHub/client-project

# User identity lives here, NOT in repo config
# Allows multiple people to work on same business repo
user:
  name: "Devon"
  experience: advanced  # beginner | intermediate | advanced
```

---

## Business Repo Config (Team Settings)

```bash
cat [repo]/.vip/config.yaml 2>/dev/null
```

Key fields:
- `session.auto_load_reference` → Load core/ automatically
- `session.show_context_tips` → Team default for tips
- `mcps` → Required MCP servers for this business
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

---

## When Skills Write Config

| Trigger | What's Written | Where |
|---------|----------------|-------|
| `/setup` first run | Full local.yaml + repo config | Both files |
| User selects repo in `/start` | `default_repo`, `recent_repos` | local.yaml |
| User says "I'm advanced" | `user.experience` | local.yaml |
| User says "save as default" | Skill preference | repo config `skills.*` |
| User connects infrastructure | `infrastructure.*` | repo config |

**Rule:** Never write silently. Confirm changes that affect future sessions.

---

## Fallback Chain

Config is always optional. Skills work without it.

```
1. Try local.yaml → missing? → discovery
2. Try repo config → missing? → use defaults
3. Path invalid? → clear config, rediscover
4. Parse error? → warn, clear, rediscover
```

**Principle:** Config is a speed optimization, not a requirement.

---

## User Must Always Have Choice

**Even with valid saved config, `/start` must ask:**

> "Found saved repo:
>
> 1. [saved-repo-name] (saved)
> 2. Switch to different repo
>
> (hit a number)"

Replace `[saved-repo-name]` with the actual folder name from config.

**Never auto-proceed without asking.** Users may have multiple repos:
- Their own business
- Client projects
- Test repos

The saved default is a **suggestion**, not a lock-in. One question takes 1 second; being stuck in the wrong repo wastes minutes.
