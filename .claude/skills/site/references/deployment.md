# Deployment — Netlify (Legacy Fallback)

> **Legacy reference.** Cloudflare Pages with git auto-deploy is the V1 default for `/site` (better CLI, better domain integration, deploys triggered by `git push`). This file documents the **legacy Netlify path** for pre-V1 Next.js templates that haven't migrated. Pick Netlify only if you have a specific reason to.
>
> For the current Cloudflare Pages flow, see [`cloudflare-pages-link.md`](cloudflare-pages-link.md) (the GitHub App OAuth handshake) and the per-shape build refs ([`minisite-build.md`](minisite-build.md), [`website-build.md`](website-build.md)).

Netlify setup and deployment reference for `/site` legacy paths. Sites use static export (`next build` → `out/` directory) deployed to Netlify.

---

## First-Time Netlify Setup

One-time dashboard walkthrough. After this, deploys are automatic on `git push`.

### Step 1: Create Netlify Account

Go to [app.netlify.com](https://app.netlify.com). Sign up with GitHub (recommended — simplifies repo connection).

### Step 2: Import Project

1. Click **"Add new site"** in the dashboard
2. Select **"Import an existing project"**
3. Choose **"Deploy with GitHub"**
4. Authorize Netlify to access your GitHub account (if first time)
5. Select your site repository from the list

### Step 3: Configure Build Settings

| Setting | Value |
|---|---|
| **Build command** | `pnpm build` |
| **Publish directory** | `out` |
| **Node version** | Set `NODE_VERSION` to `20` in environment variables |

To set environment variables:
1. Click **"Show advanced"** before deploying
2. Click **"New variable"**
3. Key: `NODE_VERSION`, Value: `20`

### Step 4: Deploy

Click **"Deploy site"**. First build takes 1-3 minutes.

Netlify assigns a random URL like `https://random-name-123.netlify.app`. You can change this or add a custom domain later.

### Step 5: Verify

Visit the deployed URL. Confirm the site loads correctly.

---

## Build Settings Reference

### next.config.ts

The site must use static export:

```typescript
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
}
export default nextConfig
```

### netlify.toml (optional)

If the repo includes a `netlify.toml`, it overrides dashboard settings:

```toml
[build]
  command = "pnpm build"
  publish = "out"

[build.environment]
  NODE_VERSION = "20"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

The redirect rule handles client-side routing for single-page sites.

---

## Auto-Deploy on Git Push

After initial setup, Netlify auto-deploys when you push to the `main` branch:

```
git push origin main → Netlify detects → builds → deploys (~1-2 min)
```

Every push triggers a new deploy. No manual action needed.

### Deploy Previews

Netlify creates preview URLs for pull requests. Useful for reviewing changes before merging to main.

---

## Custom Domain

### Option A: Buy Through Netlify

1. Go to **Site settings → Domain management → Add custom domain**
2. Enter your domain name
3. Click **"Verify"** → Netlify offers to register it
4. Follow purchase flow

### Option B: Connect Existing Domain

1. Go to **Site settings → Domain management → Add custom domain**
2. Enter your domain (e.g., `yourbusiness.com`)
3. Netlify provides DNS records to add at your registrar:
   - **A record:** `75.2.60.5`
   - **CNAME:** `[your-site].netlify.app` (for www subdomain)
4. Add records at your DNS provider (Cloudflare, Namecheap, GoDaddy, etc.)
5. Wait for DNS propagation (5 min to 48 hours)

### SSL Certificate

Netlify provides free SSL (Let's Encrypt) automatically once DNS is verified. No configuration needed.

---

## Manual Deploy (Fallback)

If git-connected deploys aren't working:

1. Build locally: `pnpm build`
2. Go to Netlify dashboard → **Deploys** tab
3. Drag and drop the `out/` folder onto the deploy area
4. Wait for upload to complete

This bypasses the build process entirely.

---

## Monitoring Deploys

### Dashboard

- **Deploys tab** shows all recent deploys with status (Published, Building, Failed)
- Click any deploy to see the full build log
- **Production deploys** (green) are live. Failed deploys (red) don't affect the live site.

### Build Notifications

Set up in **Site settings → Build & deploy → Deploy notifications**:
- Email on deploy success/failure
- Slack webhook
- Outgoing webhook (for custom integrations)

---

## Troubleshooting

### Build fails: "command not found: pnpm"

Netlify doesn't have pnpm by default. Two options:

1. Add to build command: `npm install -g pnpm && pnpm build`
2. Add a `.npmrc` with `shamefully-hoist=true` and use `npx pnpm build`

### Build fails: Node version mismatch

Set `NODE_VERSION=20` in Netlify environment variables (Site settings → Environment variables).

### 404 on page refresh

Add the redirect rule to `netlify.toml`:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Deploy succeeds but site looks wrong

1. Clear Netlify cache: **Deploys → Trigger deploy → Clear cache and deploy site**
2. Check that `publish` directory is `out` (not `.next`)
3. Verify `output: 'export'` in `next.config.ts`

### Slow deploys

Typical build time is 1-2 minutes. If slower:
- Check for unnecessary dependencies in `package.json`
- Ensure images aren't being processed at build time
- Consider adding `node_modules` to `.gitignore` (should already be there)

### Custom domain not working

- DNS propagation can take up to 48 hours
- Verify DNS records match what Netlify shows
- Check that SSL certificate has been provisioned (Site settings → Domain management → HTTPS)

---

## Why Netlify

| Factor | Netlify | Alternatives |
|---|---|---|
| **Next.js support** | Native plugin | Vercel (native), Cloudflare (limited) |
| **Free tier** | 100GB bandwidth/month | Vercel (100GB), Cloudflare (unlimited) |
| **Setup** | Dashboard or CLI | Similar across platforms |
| **Git auto-deploy** | Yes | All support this |
| **Custom domains** | Free SSL included | All support this |

Netlify was chosen because all three existing Noontide sites deploy there. Consistency over optimization.

---

## See Also

- [frontend-design.md](frontend-design.md) — Typography, color, motion, performance targets
- [section-patterns.md](section-patterns.md) — How reference files map to page sections
- [examples-and-troubleshooting.md](examples-and-troubleshooting.md) — Usage examples and common fixes
