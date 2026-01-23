# Cloudflare Pages Setup

One-time setup for auto-deploy. After this, every `git push` deploys automatically.

**Stuck?** Drag a screenshot into chat for help.

---

## What's a CLI?

CLI = Command Line Interface. It's the terminal/command prompt where you type commands.

**UI (dashboard)** = Click buttons in a browser
**CLI (terminal)** = Type commands like `git push`

After this one-time UI setup, you'll work entirely in the CLI. That's where I can help you directly — no more dashboard needed.

---

## Quick Path

```
Workers & Pages → Create application → "Looking to deploy Pages? Get started" (bottom link!)
→ Import an existing Git repository → Select repo → Fill build settings → Save and Deploy
```

---

## Step-by-Step

### 1. Navigate to Pages

Left sidebar: **Build** → **Compute & AI** → **Workers & Pages**

### 2. Create Application

Click **"Create application"** (blue, top right)

---

⚠️ **WARNING: Worker vs Page Confusion**

The default screen is **Workers** (wrong!). You need **Pages**.

Look for the small link at the **BOTTOM** of the page:
> "Looking to deploy Pages? **Get started**"

Click **"Get started"** to switch to the Pages flow.

If you miss this, you'll create a Worker instead of a Page — it won't work and you'll have to delete it and start over.

---

### 3. Choose Import Method

Select: **"Import an existing Git repository"** → **Get started**

### 4. Connect GitHub

⚠️ **First time connecting Cloudflare to GitHub?** You'll need to install the Cloudflare Pages GitHub app:
1. Click **"Connect GitHub"** button
2. Authorize Cloudflare to access your GitHub account
3. Choose **"Only select repositories"** and pick your wiki repo
4. Click **"Install & Authorize"**

**Already connected?** Continue below:

- Make sure you're on the **GitHub** tab (not GitLab)
- Select your GitHub account from dropdown
- Find and click your wiki repo (e.g., `my-wiki`)
- Click **"Begin setup"**

*Repo not showing?* Click "configure repository access for the Cloudflare Pages app on GitHub" to add it.

### 5. Build Settings

| Field | Value |
|-------|-------|
| Project name | (auto-filled from repo) |
| Production branch | `main` |
| Framework preset | `Astro` or `None` |
| **Build command** | `pnpm build` |
| **Build output directory** | `dist` |

Advanced settings (optional, leave defaults):
- Root directory: `/`
- Environment variables: none needed

### 6. Deploy

Click **"Save and Deploy"**

First build takes ~1-2 minutes. Watch progress on screen.

**Build stages you'll see:**
1. Initializing build environment
2. Cloning git repository
3. Building application
4. Deploying to Cloudflare's global network

**Success screen shows:**
- "Your project is deployed to Region: Earth"
- Link to your site: `[project-name].pages.dev`
- Next steps (you can ignore these)

---

## You're Done with the Dashboard!

Once you see the success screen, **you never need to open this dashboard again**.

From now on:
- Edit files locally
- `git add . && git commit -m "message" && git push`
- Cloudflare automatically rebuilds and deploys

I can help you with everything from the terminal now. The dashboard was just the one-time connection step.

---

## Custom Domain (Optional)

Skip this if you're fine with `[project].pages.dev` for now. **You can add a domain later anytime with `/wiki domain-setup`.**

### Check: Is your domain already on Cloudflare?

Go to Account home → Domains. Is your domain listed there?

**YES → Easy path:**
1. Workers & Pages → your project → **Custom domains** tab
2. **"Set up a custom domain"**
3. Enter your domain
4. CF auto-configures DNS — done!

**NO → Two options:**

*Option 1: Add domain to Cloudflare (recommended)*
1. Account home → Domains → **"Onboard a domain"**
2. Enter your domain, follow steps to change nameservers at your registrar
3. Wait for DNS propagation (up to 24-48 hours)
4. Then follow "YES" path above

*Option 2: Keep domain external*
- Manually add CNAME record at your registrar pointing to `[project].pages.dev`
- Less integrated, SSL may have issues

---

## Common Issues

**Created a Worker instead of a Page?**
Symptoms: "Missing entry point" error, or project appears under Workers instead of Pages.
Fix:
1. Go to Workers & Pages → find your project
2. Click it → Settings → scroll to bottom → **Delete**
3. Start over from Step 2, but this time click the **"Pages: Get started"** link at the bottom

**Repo not showing when connecting GitHub?**
Click "configure repository access for the Cloudflare Pages app on GitHub" and add your repo.

**Direct upload project can't add Git?**
Delete project (Settings → Delete), recreate via this flow.

**Build failing?**
- Check Build command is `pnpm build` (not `npm run build`)
- Check Build output directory is `dist` (not `public` or `/`)
- Check for frontmatter errors — `status` must be `draft`, `live`, or `updated`
