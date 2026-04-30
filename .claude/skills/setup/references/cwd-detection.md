# CWD Detection and vip Configuration

Detailed flow for detecting the user's current working directory and configuring vip during `/setup`. This is the critical first step — must happen BEFORE context gathering so essential config is saved if conversation compacts.

---

## Pull Latest Engine Updates (Always)

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

## Detect Where We Are

```bash
# Check CWD for business repo fingerprint
test -d "reference/core" && echo "IS_BUSINESS_REPO"

# Check CWD for vip fingerprint
test -f ".claude/skills/setup/SKILL.md" && echo "IS_VIP"
```

---

## Case 1: CWD IS the Business Repo (Happy Path)

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

   Then update `.gitignore` to exclude bridge links (see `auto-heal.md` Step 2.5 for the canonical script — marker-based, per-skill entries, idempotent).

   > "Configured. vip is now linked for file access, and compatibility bridge links are in place for skill discovery."

3. **If vip loaded:** Check compatibility symlinks exist (without clobbering local files):
   ```bash
   # At minimum, /start must be discoverable
   test -e ".claude/skills/start" && echo "START_BRIDGE_OK"
   ```
   If missing, recreate missing links using the loop above. Never replace the entire `.claude/skills` directory.

---

## Case 2: CWD IS vip (Old Workflow — Migration)

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
   Then update `.gitignore` in the business repo to exclude bridge links (see `auto-heal.md` Step 2.5 for the canonical script).

   If direct write is blocked by sandbox boundaries, use the write-boundary decision flow from SKILL.md (ask first, then use terminal commands only if user agrees).

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
   d. Update `.gitignore` in the new repo to exclude bridge links (see `auto-heal.md` Step 2.5 for the canonical script).
   e. Update `~/.config/vip/local.yaml` with a **merge** (never overwrite):
      - Read existing file first
      - Preserve existing/unknown keys
      - Set/update `vip_path`
      - Add new repo to `recent_repos` (prepend + dedupe)
      - Keep `user.*` if present; ask only when missing
      - Ask before changing `default_repo` if one already exists
   f. **Set the business repo as the target for all file writes:**
      From this point forward, write all files to `~/Documents/GitHub/[business-name]/` NOT to the current directory.
      If direct writes are blocked by workspace limits, use explicit terminal commands with full paths (after user approval via the decision flow above).
   g. Confirm:
      > "Created [business-name] and configured vip. Next time:
      > ```
      > cd ~/Documents/GitHub/[business-name]
      > claude
      > /start
      > ```"

4. **Continue with setup** — proceed to Step 0 (Chrome extension) and beyond.

---

## Case 3: CWD is Neither

User is in some other directory. Ask what they want:

> "This doesn't look like a business repo or vip. Options:
>
> 1. Create a new business repo here
> 2. Tell me where your existing repo is
> 3. Start fresh (`/setup` will create everything)"
