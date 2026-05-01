# Repo Detection (Step 0)

CWD-first detection of the business repo, with config fallback. The user starts Claude in their business repo — check CWD first before falling back to config.

---

## CWD Detection (Primary — Fast Path)

```
1. Check CWD for business repo fingerprint:
   test -d "reference/core" || test -d "core"
   ├── YES → This IS the business repo. Use CWD. Skip to config loading.
   └── NO → Continue to step 2.

2. Check CWD for vip fingerprint (old workflow):
   test -f ".claude/skills/start/SKILL.md"
   ├── YES → User is in vip (old workflow). Trigger migration guidance.
   └── NO → Continue to step 3.

3. Fall back to config:
   Read ~/.config/vip/local.yaml → default_repo + recent_repos
   ├── Found valid repo(s)? → Present options (see below)
   └── Nothing valid? → Discovery or /setup
```

### Migration Guidance (Step 2 — User Is in vip)

> "It looks like you're running Claude inside the vip engine folder. The recommended workflow is now to run Claude from your business repo instead.
>
> 1. **Quick switch:** Close this session, `cd [their-repo-path]` then `claude` then `/start`
> 2. **Need setup help?** `/setup` will configure everything
> 3. **Continue here anyway** (some features may need manual paths)"
>
> If `~/.config/vip/local.yaml` has `default_repo`, show that path in option 1.

---

## Config Loading

Once business repo is identified (from CWD or config), load settings:

```
1. Read ~/.config/vip/local.yaml
   ├── Found? → Get vip_path + default_repo + recent_repos + user identity
   └── Missing? → Acceptable if CWD is the repo; config gets created by /setup

2. Read [repo]/.vip/config.yaml
   ├── Found? → Get team settings, MCP requirements
   └── Missing? → Use defaults, offer to create later
```

---

## Multi-Repo Selection (When CWD Is NOT a Business Repo)

If CWD detection fails (step 3 above), present options from config:

**Validate EVERY path in config before showing it to the user.** Never present a dead path as an option. For each path in `default_repo` and `recent_repos`, check `test -d "[path]/reference/core" || test -d "[path]/core"`. If invalid, attempt recovery (check sibling folders for a renamed repo) and auto-prune dead entries. See [config-system.md](config-system.md) for the full recovery algorithm.

**ALWAYS present numbered options** — even with ONE repo found:

> "I found this business repo:
>
> 1. [repo-name]
> 2. Another one (tell me the path)
> 3. Create new (`/setup`)
> 4. I'm confused (`/help`)
>
> Which one? (hit a number)"

**MULTIPLE found:** List all, then options 2-4 above.

**NONE found:** Ask user for path, or route to `/setup`.

### Discovery Algorithm (When No Config)

Use fallbacks in order:

1. **Scan additionalDirectories** for paths containing `reference/core/` or `core/`
2. **Use bash to find repos** (if step 1 fails)
   ```bash
   find ~/Documents/GitHub -maxdepth 3 -type d \( -name "reference" -o -name "core" \) -print 2>/dev/null
   ```
3. **Ask the user** (if nothing found)

**Verify with Read, not Glob:** Use `Read` on `[path]/reference/core/soul.md` or `[path]/core/soul.md` to confirm it's a business repo. `soul.md` is always in `core/` (even multi-offer repos).

**Skip vip** — any path containing `.claude/skills/start/SKILL.md` is the engine, not a business repo.

---

## When CWD IS the Business Repo (Happy Path)

No repo selection needed. Confirm briefly and move on:

> "Working in **[repo-name]**."

---

## Canonical Repo Variable (Required)

After repo detection/selection, set one canonical variable and use it everywhere:

```bash
REPO_PATH="[absolute-path-to-selected-business-repo]"
```

**Rule:** All business-repo operations must target `REPO_PATH` (not implicit CWD). This is critical when `/start` is invoked from vip and the selected repo is elsewhere.

If `~/.config/vip/local.yaml` doesn't have this repo saved, offer to save:

> "Want me to save [repo-name] as your default? (faster startup next time)"

If yes, update `~/.config/vip/local.yaml`:

```yaml
vip_path: /path/to/vip
default_repo: /full/path/to/repo
recent_repos:
  - /full/path/to/repo
user:
  name: "[ask if not set]"
  experience: "[ask if not set]"  # beginner | intermediate | advanced
```

**If user.name or user.experience missing:** Ask once, save for future sessions.

---

## Verify vip Is Loaded (Config + Compatibility Links)

After detecting the business repo, confirm vip is accessible and `/start` bridge exists in the selected repo (`REPO_PATH`):

```bash
# 1. Resolve vip path from selected repo's settings.local.json
VIP_PATH=$(test -f "$REPO_PATH/.claude/settings.local.json" && REPO_PATH="$REPO_PATH" python3 -c "
import json, os
with open(os.path.join(os.environ['REPO_PATH'], '.claude/settings.local.json')) as f:
    dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
for d in dirs:
    if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
        print(d); break
" 2>/dev/null)

# 2. Check /start bridge exists in selected repo
test -e "$REPO_PATH/.claude/skills/start" && echo "START_BRIDGE_OK"
```

**If `additionalDirectories` missing:** Run `/setup` to configure.

**If bridge links missing** (but `additionalDirectories` exists): run the canonical repair from [auto-heal.md](auto-heal.md), targeting `REPO_PATH`.

Tell the user: "Repaired missing vip bridge links in **[repo-name]**. Local custom skills are preserved."

**If `/start` was invoked from vip:** always run this verification block for the selected `REPO_PATH` before routing. This is the migration safety net for existing users.

**Why both are needed:**
- `additionalDirectories` = file access (read reference files, compliance docs)
- Bridge links = compatibility fallback for skill discovery in environments where settings-based discovery is inconsistent
