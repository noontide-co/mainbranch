# Mode: setup (Detailed Steps)

Quick first-time wiki setup. Installs default template and deploys via wrangler CLI. Run `/wiki configure` after to personalize.

---

## 1. Ask: Repo Name? Location?
Default: `wiki` in home directory (`~/wiki`)

## 2. Check GitHub CLI
```bash
gh auth status
```
If not authenticated, guide user to run `gh auth login`.

## 3. Create GitHub Repo and Clone
```bash
gh repo create [user]/[wiki] --private --clone
cd [wiki]
```
If repo exists but not cloned: `git clone https://github.com/[user]/[wiki].git`

## 4. Add Upstream and Merge Template
```bash
git remote add upstream https://github.com/noontide-co/commune-wiki.git
git fetch upstream
git merge upstream/main --allow-unrelated-histories -m "Initial wiki from commune-wiki template"
```

## 5. Apply Windows Compatibility Fixes (Windows only)
On Windows, fix path handling in `astro.backlinks.ts`:

```bash
# Add fileURLToPath import
sed -i "s/import path from 'node:path';/import path from 'node:path';\nimport { fileURLToPath } from 'node:url';/" astro.backlinks.ts

# Fix the dist path line
sed -i "s/path.join(dir.pathname,/path.join(fileURLToPath(dir),/" astro.backlinks.ts
```

Or manually edit `astro.backlinks.ts`:
- Add import: `import { fileURLToPath } from 'node:url';`
- Change: `path.join(dir.pathname, 'backlinks.json')` → `path.join(fileURLToPath(dir), 'backlinks.json')`

## 6. Install Dependencies and Build
```bash
pnpm install
pnpm build
```

**If build fails with sitemap error:** Temporarily comment out the sitemap integration in `astro.config.mjs`, rebuild, then uncomment after first deploy.

## 7. Commit and Push
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

## 8. Ensure Cloudflare Account Exists

If user doesn't have a Cloudflare account, guide them to create one:
1. Go to https://dash.cloudflare.com
2. Click "Sign up" and create free account

## 9. Create Pages Project via Dashboard (Enables Auto-Deploy)

Guide user through Cloudflare dashboard — this creates a Git-connected project with auto-deploy:

1. Go to https://dash.cloudflare.com
2. Left sidebar: **Workers & Pages**
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

## 10. Note the Deployed URL

After deploy completes, Cloudflare shows the URL (e.g., `https://wiki-abc.pages.dev`).

Ask user: "What URL did Cloudflare assign? (shown on success screen)"

## 11. Update Site URL and Push

Edit `astro.config.mjs` with the actual URL:
```javascript
site: 'https://[actual-url].pages.dev',
```

Then commit and push — this triggers auto-deploy:
```bash
pnpm build
git add -A && git commit -m "[update] Set site URL" && git push
```

## 12. Save Config
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

**Exit:** "Wiki deployed at https://[url].pages.dev with auto-deploy enabled! Every `git push` will automatically deploy. Run `/wiki configure` to personalize (name, avatar, social links, etc.)"
