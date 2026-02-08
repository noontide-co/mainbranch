---
name: wiki
description: |
  Create and maintain personal wikis using Commune Wiki architecture. Use when:
  (1) Setting up a new wiki from the commune-wiki template
  (2) Personalizing wiki via src/config.ts (name, avatar, social links, domain)
  (3) Updating home note (Right Now, Looking For, Ask Me About)
  (4) Adding atomic notes with proper frontmatter and WikiLinks
  (5) Publishing changes (git commit + push for auto-deploy)
  (6) Converting Gemini/GPT deep research into wiki format
  (7) Pulling upstream template updates from Devon
  (8) Generating "Recent Updates" notes from Git history

  Triggered by: /wiki, "add a note", "publish wiki", "create wiki", "configure wiki", "personalize wiki", "update home note"
---

# Wiki Skill

Create and maintain personal wikis with atomic notes, WikiLinks, and auto-deploy.

**Need help?** Type `/help` + your question anytime. If conversation compacts, `/help` reloads fresh context.

## Pull Latest Updates (Always)

```bash
# Pull vip updates (checks common locations)
for d in . ~/Documents/GitHub/vip ~/vip; do [ -d "$d/.claude/skills" ] && git -C "$d" pull origin main 2>/dev/null && break; done || true
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
| `setup` | Clone template, deploy to CF Pages, generate home note | First time (quick) |
| `configure` | Edit `src/config.ts` (name, links, avatar, theme) | After setup or anytime |
| `home` | Update home note (Right Now, Looking For, Ask Me About) | When priorities change |
| `add` | Create atomic note with frontmatter | Daily note-taking |
| `publish` | Git commit + push (auto-deploy) | After any changes |
| `research` | Convert Gemini/GPT research to wiki | After deep research |
| `update` | Pull upstream template changes | When fixes released |
| `recent` | Generate "Recent Updates" from Git | Weekly or on threshold |

---

## Mode: setup

Quick first-time wiki setup. Installs default template and deploys via wrangler CLI. Run `/wiki configure` after to personalize.

**Steps:**

### 1. Ask: Repo name? Location?
Default: `wiki` in home directory (`~/wiki`)

### 2. Check GitHub CLI
```bash
gh auth status
```
If not authenticated, guide user to run `gh auth login`.

### 3. Create GitHub repo and clone
```bash
gh repo create [user]/[wiki] --private --clone
cd [wiki]
```
If repo exists but not cloned: `git clone https://github.com/[user]/[wiki].git`

### 4. Add upstream and merge template
```bash
# TODO: Revert to noontide-co/commune-wiki once PR #1 is merged
git remote add upstream https://github.com/joedef/commune-wiki.git
git fetch upstream
git merge upstream/wiki-mvp-phase1 --allow-unrelated-histories -m "Initial wiki from commune-wiki template"
```

### 5. Install dependencies and build
```bash
pnpm install
pnpm build
```

### 6. Commit and push
```bash
git add -A
git commit -m "Initial wiki setup"
```

**Check branch name** (Git may default to `master`):
```bash
git branch --show-current
```

If branch is `master`, rename to `main`:
```bash
git branch -m master main
```

Then push:
```bash
git push -u origin main
```

### 7. Ensure Cloudflare account exists

If user doesn't have a Cloudflare account, guide them to create one:
1. Go to https://dash.cloudflare.com
2. Click "Sign up" and create free account

### 8. Create Pages project via dashboard (enables auto-deploy)

Guide user through Cloudflare dashboard — this creates a Git-connected project with auto-deploy:

1. Go to https://dash.cloudflare.com
2. Left sidebar: under **Compute (AI)** section, click **Workers & Pages**
3. Click **"Create application"** (blue button, top right)
4. **IMPORTANT:** Click the small link at the bottom: **"Pages: Get started"** (NOT the Worker option)
5. Select **"Connect to Git"**
6. Authorize GitHub if prompted, select the wiki repository
7. Configure build settings:
   - Project name: `wiki` (or preferred name)
   - Production branch: `main`
   - Build command: `pnpm build`
   - Build output directory: `dist`
8. Click **"Save and Deploy"**

First build takes ~1-2 minutes. Watch progress on screen.

### 9. Note the deployed URL

After deploy completes, Cloudflare shows the URL (e.g., `https://wiki-abc.pages.dev`).

Ask user: "What URL did Cloudflare assign? (shown on success screen)"

### 10. Update config.ts with site URL and user info

Edit `src/config.ts` with the actual URL and user's name:
```typescript
export const config: SiteConfig = {
  displayName: "[User's Name]",
  shortName: "[First Name]",
  tagline: "[One-liner about them]",
  siteUrl: "https://[actual-url].pages.dev",
  // ... rest of config
};
```

### 10b. Ask for avatar image

Ask: "Do you have a profile picture to use? Drag and drop the image here, or paste the file path. (Press Enter to skip and use the default)"

If user provides an image:
- Copy to wiki: `cp "[path]" "$WIKI_REPO/public/avatar.jpg"`
- Generate favicon (uses sharp, already a dependency):
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

If skipped, mention they can update later with `/wiki configure`.

Then commit and push — this triggers auto-deploy:
```bash
pnpm build
git add -A && git commit -m "[update] Set site URL and identity" && git push
```

### 11. Save wiki.json config
```bash
mkdir -p ~/.mainbranch
cat > ~/.mainbranch/wiki.json << 'EOF'
{
  "wiki_repo": "/absolute/path/to/wiki",
  "hosting": "cloudflare",
  "domain": "your-url.pages.dev",
  "cf_project": "wiki"
}
EOF
```

### 12. Generate home note (3-question flow)

Ask user if they want to generate their home page now or later (`/wiki home`).

If now, ask 3 questions:

1. **"What are you working on right now?"** → populates `right_now` frontmatter + Right Now body section
2. **"What are you looking for from this community?"** → populates `looking_for` frontmatter + Looking For body section
3. **"What could people ask you about? (3-5 topics)"** → populates `ask_me_about` frontmatter + Ask Me About body section

Generate a complete `src/content/notes/index.md` from the answers:

```yaml
---
title: "[Display Name]'s Working Notes"
created: [today's date]
updated: [today's date]
visibility: public
status: live
tags: [home, welcome]
aliases: ["home", "welcome"]
summary: "[Generated from answers]"
right_now: "[Answer 1]"
looking_for: "[Answer 2]"
ask_me_about: ["topic-1", "topic-2", "topic-3"]
---
```

Body sections: **Right Now**, **Looking For**, **Ask Me About** (with WikiLink suggestions where relevant), **About** (brief default text mentioning Commune and atomic notes).

Show user the generated note for review. Let them edit before saving.

Then commit and push:
```bash
pnpm build && git add -A && git commit -m "[add] Home note" && git push
```

**Exit:** "Wiki live at https://[url].pages.dev! Home page generated. Run `/wiki configure` to update avatar, links, and theme. Run `/wiki home` anytime to update what you're working on."

---

## Mode: add

Create a new atomic note following evergreen note principles, and link it from the home page.

**Usage:** `/wiki add "Note Title"`

**Steps:**
1. Read config: `cat ~/.mainbranch/wiki.json | jq -r '.wiki_repo'`
2. Generate slug: `echo "Note Title" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-'`
3. Check existing: `ls "$WIKI_REPO/src/content/notes/$SLUG.md" 2>/dev/null`
4. Create note with frontmatter — see [references/note-template.md](references/note-template.md)
5. Apply evergreen principles: atomic, concept-oriented, densely linked
6. Suggest WikiLinks: `grep -r "concept" "$WIKI_REPO/src/content/notes/" --include="*.md" -l`
7. **Update home page Recent Updates** — see below

**Frontmatter validation:**
- Valid `status` values: `draft`, `live`, `updated`
- Valid `visibility` values: `public`, `private`, `draft`

**Update the updates collection (step 7):**

After creating the note, add it to the updates collection so the "Recent updates" card on the home page picks it up:

1. Check if `src/content/updates/YYYY-MM-DD.md` exists for today's date
2. **If it exists:** Append the new note as a bullet under the existing content:
   ```markdown
   - [[Note Title]] — summary
   ```
3. **If it doesn't exist:** Create a new update file:
   ```yaml
   ---
   title: "Added: Note Title"
   date: YYYY-MM-DD
   summary: "New note on [topic]."
   aiGenerated: true
   author: "[user's displayName from config.ts]"
   ---

   - [[Note Title]] — summary
   ```
4. If multiple notes are added on the same day, the file accumulates them. Update the title to reflect the count (e.g., "Added 3 notes").

The home page's built-in "Recent updates" card automatically queries this collection and shows the 5 most recent entries.

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
3. Show changes: `git log HEAD..upstream/wiki-mvp-phase1 --oneline`
   (TODO: Revert to `upstream/main` once noontide-co PR #1 is merged)
4. Confirm merge with user
5. Merge: `git merge upstream/wiki-mvp-phase1 --no-edit`
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

Personalize your wiki by editing `src/config.ts` — the single source of truth for all branding.

**Usage:** `/wiki configure`

**Prompts:**

| Setting | Config Key | Required | Default |
|---------|-----------|----------|---------|
| Display name | `displayName` | Yes | "Your Name" |
| Short name (mobile) | `shortName` | No | First word of display name |
| Tagline | `tagline` | No | "A public wiki of ideas in progress" |
| Avatar image | `avatar` | No | `/avatar.jpg` |
| Social links | `links` | No | `[]` (empty) |
| Theme color | `themeColor` | No | `#3b82f6` |
| Footer text/link | `footer` | No | "Powered by Commune" → `/` |
| Plausible analytics | `plausible` | No | disabled |
| Custom domain | `siteUrl` | No | keep current |
| Delete sample notes | — | No | keep samples |

**Steps:**
1. Read config: `cat ~/.mainbranch/wiki.json | jq -r '.wiki_repo'`
2. Read current `src/config.ts`, show current settings
3. Ask what to change
4. Edit `src/config.ts` with new values — this is the **only file** that needs editing for branding. All components import from it.

   ```typescript
   // src/config.ts
   export const config: SiteConfig = {
     displayName: "Jane Smith",
     shortName: "Jane",
     tagline: "Building in public",
     siteUrl: "https://jane-wiki.pages.dev",
     avatar: "/avatar.jpg",
     links: [
       { label: "GitHub", url: "https://github.com/janesmith" },
       { label: "Twitter", url: "https://x.com/janesmith" },
     ],
     themeColor: "#3b82f6",
     footer: { text: "Powered by Commune", url: "/" },
     // plausible: { domain: "jane-wiki.pages.dev" },
   };
   ```

5. **If avatar image provided:**
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

6. **If custom domain requested:**
   - Update `siteUrl` in `config.ts`
   - Guide through Cloudflare custom domain setup
   - See [references/cloudflare-pages-setup.md](references/cloudflare-pages-setup.md)

7. **If delete sample notes:**
   ```bash
   rm -f src/content/notes/*.md
   rm -f src/content/updates/*.md
   ```
   Then create fresh `src/content/notes/index.md` with default home note template (see setup step 12 for structure).

8. Rebuild and push: `pnpm build && git add -A && git commit -m "[configure] Personalize wiki" && git push`

**Exit:** "Wiki personalized! Changes will deploy in ~90 seconds."

See [references/customization.md](references/customization.md) for manual edits.

---

## Mode: home

Quick update to your home note's temporal fields — what you're working on, looking for, and can help with.

**Usage:** `/wiki home`

**Steps:**
1. Read config: `cat ~/.mainbranch/wiki.json | jq -r '.wiki_repo'`
2. Read current `src/content/notes/index.md`
3. Show current values for `right_now`, `looking_for`, `ask_me_about`
4. Ask what to update (can update one or all):
   - "What are you working on right now?"
   - "What are you looking for?"
   - "What could people ask you about?"
5. Update frontmatter fields AND corresponding body sections in `index.md`
6. Update the `updated` date in frontmatter to today
7. Rebuild and push: `pnpm build && git add -A && git commit -m "[update] Home note" && git push`

**Exit:** "Home note updated. Live in ~90 seconds. Your `/api/profile.json` will reflect the changes too."

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

**Build failing on Windows with path error (`C:\C:\Users\...`)**
Fixed in the latest template. Run `/wiki update` to pull the fix. If on an older template version, add `import { fileURLToPath } from 'node:url';` to `astro.backlinks.ts` and change `dir.pathname` to `fileURLToPath(dir)`.

**Build failing with sitemap "reduce" error**
Sitemap is temporarily disabled in the latest template due to an upstream `@astrojs/sitemap` bug. Run `/wiki update` to pull the fix. If on an older template version, comment out the sitemap integration in `astro.config.mjs`.

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
