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

See **[../../reference/pull-engine-updates.md](../../reference/pull-engine-updates.md)** for the canonical vip-resolution + pull bash block. Run it at the start of every /wiki invocation.

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
1. **GitHub CLI** (`gh`) installed and authenticated
2. **pnpm** installed (`npm install -g pnpm`)
3. **Cloudflare account** (free tier works) — can create during setup

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

Quick first-time wiki setup. Installs default template and deploys via wrangler CLI. Run `/wiki configure` after to personalize.

**Quick gist:** Ask repo name, check `gh auth`, create+clone repo, merge `commune-wiki` template upstream, apply Windows path fixes if needed, `pnpm install && pnpm build`, push to `main`, ensure Cloudflare account, create Pages project via dashboard with Git connect, capture the deployed URL, write site URL into `astro.config.mjs`, push to trigger deploy, save `~/.mainbranch/wiki.json`.

See **[references/setup-mode.md](references/setup-mode.md)** for the full 12-step procedure: every command, the Windows compat fixes, the Cloudflare dashboard click-path, and the exit message.

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
| Avatar image | No | drag & drop to replace |
| Twitter/X handle | No | skip |
| GitHub username | No | skip |
| Website URLs | No | skip (comma-separated) |
| Custom domain | No | keep current |
| Delete sample notes | No | keep samples |

**Steps:**
1. Read config: `cat ~/.mainbranch/wiki.json`
2. Show current settings, ask what to change
3. Update files based on selections:
   - `src/components/Header.astro` — display name, short name, avatar alt
   - `src/components/Footer.astro` — update "Powered by Commune" link to `https://devonmeadows.com/` (external, target="_blank")
   - `src/pages/index.astro` — meta author, structured data
   - `src/pages/notes/[...slug].astro` — author meta
   - `src/pages/research/[...slug].astro` — footer attribution
   - `src/content/notes/my-working-notes.md` — social links
   - `astro.config.mjs` — site URL (if domain changed)
   - Replace any "Devon Meadows" references with user's name

4. **If avatar image provided:**
   - Prompt: "Drag and drop your avatar image here (or paste path):"
   - User drags image into terminal → path is pasted
   - Copy to wiki: `cp "[path]" "$WIKI_REPO/public/avatar.jpg"`
   - Generate favicon from avatar (uses sharp, already a dependency):
     ```bash
     cd "$WIKI_REPO" && node -e "
       const sharp = require('sharp');
       sharp('public/avatar.jpg')
         .resize(32, 32)
         .png()
         .toFile('public/favicon-32x32.png');
     "
     ```
   - Supported formats: .jpg, .png, .webp (rename to avatar.jpg)
   - Recommended: square image (will be cropped/resized)

5. **If custom domain requested:**
   - Guide through Cloudflare custom domain setup
   - See [references/cloudflare-pages-setup.md](references/cloudflare-pages-setup.md)
   - Update config with new domain

6. **If delete sample notes:**
   ```bash
   rm -f src/content/notes/*.md
   rm -f src/content/updates/*.md
   ```
   Then create fresh `my-working-notes.md` with default welcome content and social links.

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

- [../../reference/pull-engine-updates.md](../../reference/pull-engine-updates.md) — Canonical vip-resolution + pull bash block
- [references/setup-mode.md](references/setup-mode.md) — Full 12-step setup mode procedure (commands, Windows fixes, CF dashboard walkthrough, config save)
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

**Build failing on Windows with path error (`C:\C:\Users\...`)**
The `astro.backlinks.ts` file needs a Windows path fix. Add this import:
```javascript
import { fileURLToPath } from 'node:url';
```
And change:
```javascript
// Before
const distPath = path.join(dir.pathname, 'backlinks.json');
// After
const distPath = path.join(fileURLToPath(dir), 'backlinks.json');
```

**Build failing with sitemap "reduce" error**
Temporarily disable sitemap in `astro.config.mjs`:
```javascript
integrations: [
  tailwind({ applyBaseStyles: false }),
  backlinks(),
  // sitemap({ ... }),  // Comment out temporarily
],
```
Re-enable after first successful deploy.

**"Not logged in" with wrangler**
Run `npx wrangler login` — opens browser for Cloudflare OAuth. You can create a free account during this flow.

**Build failing**
- Check build command is `pnpm build` (not `npm run build`)
- Check output directory is `dist`

**Merge conflicts on update**
- Template files: Claude helps resolve
- Content files: Shouldn't conflict — content is in separate directories

**Stuck on CF Pages dashboard?**
Drag a screenshot into chat for help.
