# Config System

Two-file system for fast startups and portable preferences.

---

## File Locations

| File | Location | Purpose | Git-tracked? |
|------|----------|---------|--------------|
| `local.yaml` | `~/.config/vip/` | Which repo is default on THIS machine | No |
| `config.yaml` | `[repo]/.vip/` | User preferences, MCP requirements | Yes |

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
```

---

## Business Repo Config

```bash
cat [repo]/.vip/config.yaml 2>/dev/null
```

Key fields:
- `user.experience` → beginner | intermediate | advanced
- `session.auto_load_reference` → Load core/ automatically
- `session.show_context_tips` → Teach context management
- `mcps` → Required MCP servers for this business

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
