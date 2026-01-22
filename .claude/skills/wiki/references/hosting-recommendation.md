# Why Cloudflare Pages?

We recommend **Cloudflare Pages** for hosting your wiki. Here's why:

## The Short Version

Cloudflare Pages is free, fast, and we've done the work to make setup smooth. Other hosts work but require more manual configuration.

## Why Cloudflare

| Benefit | Details |
|---------|---------|
| **Free forever** | No bandwidth limits, no build limits that matter |
| **Auto-deploy** | Push to GitHub → site updates automatically |
| **Fast globally** | CDN edge network, your wiki loads fast everywhere |
| **CLI + Dashboard** | Work from terminal, check dashboard when needed |
| **Custom domains** | Free SSL, easy DNS if domain already on CF |
| **We've tested it** | This skill has step-by-step instructions with exact button names |

## What About Other Hosts?

Other static site hosts work fine:
- **Vercel** — Good, 100GB/mo bandwidth limit
- **Netlify** — Good, 100GB/mo bandwidth limit
- **GitHub Pages** — Free but requires public repo (or Pro plan)
- **Self-hosted** — Full control, more setup work

If you prefer these, the `/wiki` skill can still help with content management. You'll just handle deployment yourself.

## CLI Consideration

Cloudflare's `wrangler` CLI is excellent:
- One-time login (`wrangler login`)
- Deploy from terminal (`wrangler pages deploy`)
- Check status without opening browser

Other hosts have CLIs too (Vercel, Netlify), but we've optimized this skill for Cloudflare.

## The One-Time Dashboard Dance

Cloudflare requires a one-time setup in their dashboard to connect your GitHub repo. After that, everything is CLI:

1. **Dashboard (one-time):** Connect GitHub repo, set build settings
2. **CLI (forever after):** `git push` and your wiki auto-deploys

We guide you through the dashboard step-by-step with exact button names. Takes ~5 minutes, then you never need it again.

## Bottom Line

Use Cloudflare unless you have a specific reason not to. It's what we support best.
