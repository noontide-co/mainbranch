# Cloudflare Pages Setup

Deploy your wiki to Cloudflare Pages using the wrangler CLI.

**Stuck?** Drag a screenshot into chat for help.

---

## CLI Deployment (Default)

### 1. Check wrangler authentication

```bash
npx wrangler whoami
```

**If not logged in:**
```bash
npx wrangler login
```
Opens browser for OAuth. You can create a free Cloudflare account during this flow.

### 2. Create Pages project

```bash
npx wrangler pages project create [project-name] --production-branch main
```

This creates an empty project at `https://[project-name].pages.dev`.

### 3. Deploy

```bash
npx wrangler pages deploy dist --project-name [project-name]
```

Wrangler outputs the URL. Note this for your `astro.config.mjs`.

### 4. Subsequent deploys

After any changes:
```bash
pnpm build
npx wrangler pages deploy dist --project-name [project-name]
```

Or set up auto-deploy (below) so `git push` deploys automatically.

---

## Auto-Deploy Setup (Optional)

Connect GitHub so every `git push` deploys automatically. One-time dashboard setup.

### Quick Path

```
dash.cloudflare.com → Workers & Pages → [your project] → Settings → Builds & deployments → Connect to Git
```

### Step-by-Step

1. Go to https://dash.cloudflare.com
2. Left sidebar: **Workers & Pages**
3. Click your project name
4. **Settings** tab → **Builds & deployments**
5. Click **"Connect to Git"**
6. Authorize GitHub if prompted
7. Select your repository
8. Build settings:
   - Build command: `pnpm build`
   - Build output directory: `dist`
9. **Save**

Now every `git push` triggers automatic deploy.

---

## Custom Domain (Optional)

Skip this if `[project].pages.dev` works for now.

### Check: Is your domain already on Cloudflare?

Go to Account home → Domains.

**YES (domain on Cloudflare) → Easy:**
1. Workers & Pages → your project → **Custom domains** tab
2. **"Set up a custom domain"**
3. Enter your domain
4. CF auto-configures DNS — done!

**NO (domain external) → Two options:**

*Option 1: Add domain to Cloudflare (recommended)*
1. Account home → Domains → **"Onboard a domain"**
2. Change nameservers at your registrar (instructions provided)
3. Wait for DNS propagation (up to 24-48 hours)
4. Then follow "YES" path above

*Option 2: Keep domain external*
- Add CNAME record at your registrar pointing to `[project].pages.dev`
- Less integrated, SSL may have issues

---

## Common Issues

**"Not logged in" error**
Run `npx wrangler login` and complete OAuth in browser.

**Build failing with path error on Windows**
See Troubleshooting in main skill file for `astro.backlinks.ts` fix.

**Build failing with sitemap error**
Temporarily comment out sitemap in `astro.config.mjs`, deploy, then re-enable.

**Build failing in general**
- Check build command is `pnpm build`
- Check output directory is `dist`
- Check for frontmatter errors — `status` must be `draft`, `live`, or `updated`
