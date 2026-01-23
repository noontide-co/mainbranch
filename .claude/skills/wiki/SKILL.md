---
name: wiki
description: |
  Create and maintain personal wikis using Commune Wiki architecture. Use when:
  (1) Setting up a new wiki from the commune-wiki template
  (2) Personalizing wiki (name, avatar, social links, domain)
  (3) Adding atomic notes with proper frontmatter and WikiLinks
  (4) Publishing changes (git commit + push for auto-deploy)
  (5) Converting Gemini/GPT deep research into wiki format
  (6) Pulling upstream template updates from Devon
  (7) Generating "Recent Updates" notes from Git history

  Triggered by: /wiki, "add a note", "publish wiki", "create wiki", "configure wiki", "personalize wiki"
---

# Wiki Skill

Create and maintain personal wikis with atomic notes, WikiLinks, and auto-deploy.

**Need help?** Type `/help` + your question anytime. If conversation compacts, `/help` reloads fresh context.

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

---

## Where Files Go

**Wiki files go to YOUR WIKI REPO, not your business repo or vip.**

```
your-wiki-repo/              <- Files saved here
├── src/content/notes/       <- Atomic notes (/wiki add)
├── src/content/research/    <- Full research docs (/wiki research)
└── src/content/updates/     <- Auto-generated updates (/wiki recent)

~/.mainbranch/wiki.json      <- Config pointing to wiki repo

vip/ (engine)                <- Never modified by /wiki
└── .claude/skills/wiki/     <- This skill lives here
```

The skill reads `~/.mainbranch/wiki.json` to find your wiki repo location.

---

## Prerequisites

Before using this skill:
1. **GitHub account** with SSH keys configured
2. **Cloudflare account** (free tier works)
3. **Wiki repo** cloned locally (created via `/wiki setup` or manually)

Check for existing config:
```bash
cat ~/.mainbranch/wiki.json 2>/dev/null || echo "No wiki configured yet"
```

---

## Modes

| Mode | What It Does | When to Use |
|------|--------------|-------------|
| `setup` | Clone template, deploy to CF Pages | First time (quick) |
| `configure` | Personalize wiki (name, social, domain, etc.) | After setup |
| `add` | Create atomic note with frontmatter | Daily note-taking |
| `publish` | Git commit + push (auto-deploy) | After any changes |
| `research` | Convert Gemini/GPT research to wiki | After deep research |
| `update` | Pull upstream template changes | When fixes released |
| `recent` | Generate "Recent Updates" from Git | Weekly or on threshold |

---

## Mode: setup

Quick first-time wiki setup. Installs default template and deploys. Run `/wiki configure` after to personalize.

**Steps:**
1. Ask: Repo name? Location?
2. Create GitHub repo: `gh repo create [user]/[wiki] --private --clone`
3. Add upstream: `git remote add upstream https://github.com/noontide-co/commune-wiki.git`
4. Merge template: `git fetch upstream && git merge upstream/main --allow-unrelated-histories`
5. **Update footer link:**
   - Change `src/components/Footer.astro` "Powered by Commune" link
   - To: `https://devonmeadows.com/` (external, target="_blank")
6. Ask: Domain? (use `[project].pages.dev` or custom)
7. Update `astro.config.mjs` with site URL
8. Install and build: `pnpm install && pnpm build`
9. Deploy to Cloudflare Pages — see [references/cloudflare-pages-setup.md](references/cloudflare-pages-setup.md)

   **First-time GitHub app install:** If you've never connected Cloudflare to GitHub, you'll need to install the Cloudflare Pages GitHub app first. See the reference for details.

10. Commit and push: `git add -A && git commit -m "Initial wiki setup" && git push`
11. Save config:
    ```bash
    mkdir -p ~/.mainbranch
    cat > ~/.mainbranch/wiki.json << 'EOF'
    {
      "wiki_repo": "/path/to/wiki",
      "hosting": "cloudflare",
      "domain": "yourdomain.com",
      "cf_project": "your-project-name"
    }
    EOF
    ```

**Exit:** "Wiki deployed! Run `/wiki configure` to personalize (name, avatar, social links, etc.)"

---

## Mode: add

Create a new atomic note following evergreen note principles.

**Usage:** `/wiki add "Note Title"`

**Steps:**
1. Read config: `cat ~/.mainbranch/wiki.json | jq -r '.wiki_repo'`
2. Generate slug: `echo "Note Title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-'`
3. Check existing: `ls "$WIKI_REPO/src/content/notes/$SLUG.md" 2>/dev/null`
4. Create note with frontmatter — see [references/note-template.md](references/note-template.md)
5. Apply evergreen principles: atomic, concept-oriented, densely linked
6. Suggest WikiLinks: `grep -r "concept" "$WIKI_REPO/src/content/notes/" --include="*.md" -l`

**Frontmatter validation:**
- Valid `status` values: `draft`, `live`, `updated`
- Valid `visibility` values: `public`, `private`, `draft`

**Exit:** "Note created. Run `/wiki publish` to deploy, or continue editing."

---

## Mode: publish

Commit changes and push to trigger auto-deploy.

**Usage:** `/wiki publish "commit message"` or `/wiki publish`

**Steps:**
1. Read config, cd to wiki repo
2. Check `git status --short`
3. Generate commit message if not provided (analyze changed files)
4. Commit and push: `git add -A && git commit -m "[type] Message" && git push`

**Exit:** "Pushed to GitHub. Cloudflare Pages will auto-deploy in ~90 seconds. Check status: https://dash.cloudflare.com → Workers & Pages → [project-name]"

---

## Mode: research

Convert Gemini/GPT deep research into wiki format.

**Usage:** `/wiki research [path-to-research-file.md]`

**Steps:**
1. Read research file
2. Create summary note (tripwire) in `notes/` — see [references/research-format.md](references/research-format.md)
3. Create full research in `research/`
4. Format external links with arrow icon
5. Suggest WikiLinks to existing notes

**Exit:** "Created research summary and full research. Run `/wiki publish` to deploy."

---

## Mode: update

Pull upstream template improvements from commune-wiki.

**Usage:** `/wiki update`

**Steps:**
1. Read config, cd to wiki repo
2. Fetch upstream: `git fetch upstream`
3. Show changes: `git log HEAD..upstream/main --oneline`
4. Confirm merge with user
5. Merge: `git merge upstream/main --no-edit`
6. Rebuild: `pnpm install && pnpm build`

**Exit:** "Updated to latest template. Run `/wiki publish` to deploy."

---

## Mode: recent

Generate "Recent Updates" note from Git history.

**Usage:** `/wiki recent`

**Triggers:** Friday + >3 commits this week, >15 commits in single day, or manual.

**Steps:**
1. Get recent commits: `git log --since="1 week ago" --pretty=format:"%h %s" --name-only`
2. Categorize: new notes, updated notes, research added
3. Generate update note — see [references/updates-template.md](references/updates-template.md)
4. Save to `src/content/updates/YYYY-MM-DD.md`

---

## Mode: configure

Personalize your wiki after setup. All customization in one place.

**Usage:** `/wiki configure`

**Prompts:**

| Setting | Required | Default |
|---------|----------|---------|
| Display name | Yes | — |
| Short name (mobile) | No | First word of display name |
| Tagline | No | `{display name}'s Notes` |
| Avatar image | No | drag & drop to replace |
| Twitter/X handle | No | skip |
| GitHub username | No | skip |
| Website URLs | No | skip (comma-separated) |
| Welcome page title | No | `Welcome` |
| Welcome heading | No | `Welcome to my wiki` |
| Welcome intro | No | Based on tagline |
| Custom domain | No | keep current |
| Delete sample notes | No | keep samples |

**Steps:**
1. Read config: `cat ~/.mainbranch/wiki.json`
2. Show current settings, ask what to change
3. Update files based on selections:
   - `src/components/Header.astro` — display name, short name, avatar alt
   - `src/pages/index.astro` — meta author, structured data, tagline
   - `src/pages/notes/[...slug].astro` — author meta
   - `src/pages/research/[...slug].astro` — footer attribution
   - `src/content/notes/my-working-notes.md` — welcome page content
   - `astro.config.mjs` — site URL (if domain changed)
   - Replace any "Devon Meadows" references with user's name

4. **If avatar image provided:**
   - Prompt: "Drag and drop your avatar image here (or paste path):"
   - User drags image into terminal → path is pasted
   - Copy to wiki: `cp "[path]" "$WIKI_REPO/public/avatar.jpg"`
   - Supported formats: .jpg, .png, .webp (rename to avatar.jpg)
   - Recommended: 200x200px square crop

5. **If custom domain requested:**
   - Guide through Cloudflare custom domain setup
   - See [references/cloudflare-pages-setup.md](references/cloudflare-pages-setup.md)
   - Update config with new domain

6. **If delete sample notes:**
   ```bash
   rm -f src/content/notes/*.md
   rm -f src/content/updates/*.md
   ```
   Then create fresh `my-working-notes.md` with user's welcome content.

7. Rebuild and push: `pnpm build && git add -A && git commit -m "[configure] Personalize wiki" && git push`

**Exit:** "Wiki personalized! Changes will deploy in ~90 seconds."

See [references/customization.md](references/customization.md) for manual edits.

---

## Config File

`~/.mainbranch/wiki.json`:

```json
{
  "wiki_repo": "/Users/you/wiki",
  "hosting": "cloudflare",
  "domain": "yourdomain.com",
  "cf_project": "your-wiki"
}
```

**Why file-based:** Skill reads at invocation — no need to add wiki as working directory.

---

## When NOT to Use

- General note-taking outside wiki repos — use your notes app
- Business reference files — those go in your business repo, not wiki
- Quick scratch notes — wiki is for evergreen, linked knowledge

---

## Examples

### Example 1: Add a Note

```
User: /wiki add "Compounding Knowledge"

Claude: Reading wiki config...
Creating note at src/content/notes/compounding-knowledge.md

[Writes note with frontmatter, suggests WikiLinks to existing notes]

Note created. Run `/wiki publish` to deploy, or continue editing.
```

### Example 2: Publish Research

```
User: /wiki research ~/Downloads/gemini-pricing-research.md

Claude: Reading research file (8,400 words)...

Creating:
1. Summary note: notes/research-pricing-strategy.md (tripwire)
2. Full research: research/pricing-strategy-full.md

[Formats links, suggests WikiLinks]

Created research summary and full research. Run `/wiki publish` to deploy.
```

### Example 3: Publish Changes

```
User: /wiki publish

Claude: Reading wiki config...
3 files changed:
  A  src/content/notes/compounding-knowledge.md
  M  src/content/notes/active-reference.md
  A  src/content/research/pricing-strategy-full.md

Generating commit message: "[add] Compounding knowledge note, pricing research"

[Commits and pushes]

Pushed to GitHub. Cloudflare Pages will auto-deploy in ~90 seconds.
Live at: https://yourdomain.com
```

---

## References

- [references/cloudflare-pages-setup.md](references/cloudflare-pages-setup.md) — Dashboard walkthrough
- [references/customization.md](references/customization.md) — Update avatar, name, social links after setup
- [references/hosting-recommendation.md](references/hosting-recommendation.md) — Why Cloudflare
- [references/note-template.md](references/note-template.md) — Atomic note guidelines
- [references/research-format.md](references/research-format.md) — Deep research conversion
- [references/updates-template.md](references/updates-template.md) — Weekly updates format

---

## Troubleshooting

**"No wiki configured"**
Run `/wiki setup` first.

**Build failing**
- Check build command is `pnpm build` (not `npm run build`)
- Check output directory is `dist`

**Merge conflicts on update**
- Template files: Claude helps resolve
- Content files: Shouldn't conflict — content is in separate directories

**Stuck on CF Pages dashboard?**
Drag a screenshot into chat for help.
