# Config System

Two-file system: personal stays local, team settings travel with repo.

---

## File Locations

| File | Location | Purpose | Git-tracked? |
|------|----------|---------|--------------|
| `local.yaml` | `~/.config/vip/` | User identity + which repo is default | No |
| `config.yaml` | `[repo]/.vip/` | Team/business settings, MCP requirements | Yes |

**Key split:**
- **Local** = "Who am I? What repo do I want?" (per-person, per-machine)
- **Repo** = "How does this business/team operate?" (shared)

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
