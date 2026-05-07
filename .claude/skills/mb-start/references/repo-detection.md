# Repo Detection (Step 2)

CWD-first detection of the business repo, with config fallback. The user starts Claude in their business repo — check CWD first before falling back to config.

---

## CWD Detection (Primary — Fast Path)

```
1. Check CWD for business repo fingerprint:
   test -d "core" || test -d "reference/core"
   ├── YES → This IS the business repo. Use CWD. Skip to config loading.
   └── NO → Continue to step 2.

2. Check CWD for Main Branch engine fingerprint (old workflow):
   test -f ".claude/skills/mb-start/SKILL.md"
   ├── YES → User is in the engine repo (old workflow). Trigger migration guidance.
   └── NO → Continue to step 3.

3. Fall back to config:
   Read ~/.config/vip/local.yaml → default_repo + recent_repos
   ├── Found valid repo(s)? → Present options (see below)
   └── Nothing valid? → Discovery or /mb-setup
```

### Migration Guidance (Step 2 - User Is in the Engine Repo)

> "It looks like you're running Claude inside the Main Branch engine folder. The recommended workflow is now to run Claude from your business repo instead.
>
> 1. **Quick switch:** Close this session, `cd [their-repo-path]` then `claude` then `/mb-start`
> 2. **Need setup help?** `/mb-setup` will configure everything
> 3. **Continue here anyway** (some features may need manual paths)"
>
> If `~/.config/vip/local.yaml` has `default_repo`, show that path in option 1.

---

## Config Loading

Once business repo is identified (from CWD or config), load settings:

```
1. Read ~/.config/vip/local.yaml
   ├── Found? → Get legacy engine path + default_repo + recent_repos + user identity
   └── Missing? → Acceptable if CWD is the repo; config gets created by /mb-setup

2. Read [repo]/.vip/config.yaml
   ├── Found? → Get team settings, MCP requirements
   └── Missing? → Use defaults, offer to create later
```

---

## Multi-Repo Selection (When CWD Is NOT a Business Repo)

If CWD detection fails (step 3 above), present options from config:

**Validate EVERY path in config before showing it to the user.** Never present a dead path as an option. For each path in `default_repo` and `recent_repos`, check `test -d "[path]/core" || test -d "[path]/reference/core"`. If invalid, attempt recovery (check sibling folders for a renamed repo) and auto-prune dead entries. See [config-system.md](config-system.md) for the full recovery algorithm.

**ALWAYS present numbered options** — even with ONE repo found:

> "I found this business repo:
>
> 1. [repo-name]
> 2. Another one (tell me the path)
> 3. Create new (`/mb-setup`)
> 4. I'm confused (`/mb-help`)
>
> Which one? (hit a number)"

**MULTIPLE found:** List all, then options 2-4 above.

**NONE found:** Ask user for path, or route to `/mb-setup`.

### Discovery Algorithm (When No Config)

Use fallbacks in order:

1. **Scan additionalDirectories** for paths containing `core/` or legacy `reference/core/`
2. **Use bash to find repos** (if step 1 fails)
   ```bash
   find ~/Documents/GitHub -maxdepth 3 -type d \( -name "reference" -o -name "core" \) -print 2>/dev/null
   ```
3. **Ask the user** (if nothing found)

**Verify with Read, not Glob:** Use `Read` on `[path]/core/soul.md` or legacy `[path]/reference/core/soul.md` to confirm it's a business repo. `soul.md` is always canonical in `core/` for current repos.

**Skip the engine repo** - any path containing `.claude/skills/mb-start/SKILL.md` is the engine, not a business repo.

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

**Rule:** All business-repo operations must target `REPO_PATH` (not implicit CWD). This is critical when `/mb-start` is invoked from the engine repo and the selected repo is elsewhere.

If `~/.config/vip/local.yaml` doesn't have this repo saved, offer to save:

> "Want me to save [repo-name] as your default? (faster startup next time)"

If yes, update `~/.config/vip/local.yaml`:

```yaml
vip_path: /path/to/mainbranch
default_repo: /full/path/to/repo
recent_repos:
  - /full/path/to/repo
user:
  name: "[ask if not set]"
  experience: "[ask if not set]"  # beginner | intermediate | advanced
```

**If user.name or user.experience missing:** Ask once, save for future sessions.

---

## Verify Main Branch Is Loaded (Config + Skill Bridge Links)

After detecting the business repo, confirm Main Branch is accessible and `/mb-start` bridge exists in the selected repo (`REPO_PATH`):

```bash
# 1. Resolve engine path from selected repo's settings.local.json
ENGINE_PATH=$(test -f "$REPO_PATH/.claude/settings.local.json" && REPO_PATH="$REPO_PATH" python3 -c "
import json, os
with open(os.path.join(os.environ['REPO_PATH'], '.claude/settings.local.json')) as f:
    dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
for d in dirs:
    if os.path.isfile(os.path.join(d, '.claude/skills/mb-start/SKILL.md')):
        print(d); break
" 2>/dev/null)

# 2. Check /mb-start bridge exists in selected repo
test -e "$REPO_PATH/.claude/skills/mb-start" && echo "START_BRIDGE_OK"
```

**If `additionalDirectories` missing:** run `mb skill link --repo "$REPO_PATH"`, then restart Claude.

**If bridge links missing** (but `additionalDirectories` exists): run the canonical repair from [auto-heal.md](auto-heal.md), targeting `REPO_PATH`.

Tell the user: "Repaired missing Main Branch bridge links in **[repo-name]**. Local custom skills are preserved."

**If `/mb-start` was invoked from the engine repo:** always run this verification block for the selected `REPO_PATH` before routing. This is the migration safety net for existing users.

**Why both are needed:**
- `additionalDirectories` = file access (read reference files, compliance docs)
- Bridge links = slash-command discovery for Main Branch skills
