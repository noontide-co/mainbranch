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

Cloudflare Pages is the Main Branch deploy rail. Other static hosts exist
(Vercel, Netlify, GitHub Pages, self-hosted), but Main Branch does not
maintain setup guidance or fallback instructions for them. If you
deliberately pick another host, the `/mb-wiki` skill can still help with
content management; you handle deployment yourself.

GitHub Pages in particular couples visibility and hosting in ways that the
Main Branch visibility model deliberately separates — public output does
not require public source. Use Cloudflare Pages so a public wiki can ship
from a private repo when you want it to. The engine docs ship the full
rubric (`repo-visibility-rubric`).

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
