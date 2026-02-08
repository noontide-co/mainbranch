# Cloudflare Pages Setup

Deploy your wiki to Cloudflare Pages with Git-connected auto-deploy.

**Stuck?** Drag a screenshot into chat for help.

---

## Create Git-Connected Project (Recommended)

This method enables auto-deploy — every `git push` automatically deploys.

### 1. Open Cloudflare Dashboard

Go to https://dash.cloudflare.com (create free account if needed)

### 2. Navigate to Workers & Pages

Left sidebar: under **Compute (AI)** section, click **Workers & Pages**

### 3. Create Application

Click **"Create application"** (blue button, top right)

### 4. Choose Pages (NOT Workers!)

⚠️ **IMPORTANT:** The default screen shows Workers. Look for the small link at the **BOTTOM**:

> "Looking to deploy Pages? **Get started**"

Click **"Get started"** to switch to Pages.

### 5. Connect to Git

Select **"Connect to Git"** → **Get started**

### 6. Authorize GitHub

- Click **"Connect GitHub"** if first time
- Authorize Cloudflare to access your GitHub
- Choose **"Only select repositories"** and pick your wiki repo
- Click **"Install & Authorize"**

If already connected, just select your wiki repo and click **"Begin setup"**

### 7. Configure Build Settings

| Field | Value |
|-------|-------|
| Project name | `wiki` (or preferred name) |
| Production branch | `main` |
| Build command | `pnpm build` |
| Build output directory | `dist` |

### 8. Deploy

Click **"Save and Deploy"**

First build takes ~1-2 minutes. Success screen shows your URL (e.g., `wiki-abc.pages.dev`).

---

## After Setup

Every `git push` to main automatically deploys (~90 seconds).

No need for manual deploys or wrangler CLI.

---

## Custom Domain (Optional)

### Domain already on Cloudflare?

1. Workers & Pages → your project → **Custom domains** tab
2. **"Set up a custom domain"**
3. Enter your domain — CF auto-configures DNS

### Domain not on Cloudflare?

*Option 1: Add domain to Cloudflare (recommended)*
1. Account home → Domains → **"Onboard a domain"**
2. Change nameservers at your registrar
3. Wait for DNS propagation (up to 24-48 hours)
4. Then add custom domain above

*Option 2: External domain*
- Add CNAME record at registrar pointing to `[project].pages.dev`

---

## Common Issues

**Created a Worker instead of a Page?**
Delete it (Settings → Delete) and start over. Make sure to click "Pages: Get started" link.

**Repo not showing?**
Click "configure repository access for the Cloudflare Pages app on GitHub" and add your repo.

**Build failing?**
- Build command must be `pnpm build`
- Output directory must be `dist`
- Check for frontmatter errors in notes

**Build failing with path error on Windows?**
The `astro.backlinks.ts` needs a fix. See Troubleshooting in main skill file.
