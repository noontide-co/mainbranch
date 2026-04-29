---
type: educational
topic: cloudflare-vs-vercel
status: stub
last-updated: 2026-04-29
---

# Why we ship sites on Cloudflare Pages, not Vercel or Netlify

## Why we don't recommend Vercel or Netlify by default

Vercel and Netlify are excellent products. The reason we don't pick them as the Main Branch default is not quality — it's pricing posture and lock-in.

**Pricing model risk.** Both Vercel and Netlify use a "free tier with metered overage" model. If your site goes viral, you pay for it after the fact, and the bill can be surprising. Vercel's bandwidth overages are billed at $40/TB after the included 100 GB on Hobby; Netlify's are $55/TB after 100 GB. We have seen Main Branch members hit $300 surprise bills from a single Reel that sent 500K visitors to a one-page site. Cloudflare's free Pages tier has unlimited bandwidth — that is not marketing copy, it is the actual policy as of 2026. The bill cannot surprise you because there is no meter.

**Build minutes are a hidden meter.** Vercel includes 6,000 build-execution minutes per month on Pro; if you are deploying every commit on a busy week, you'll see throttling or upgrade prompts. Cloudflare Pages includes 500 builds per month on the free tier, then charges per build (not per minute). The pricing scales linearly and predictably.

**Egress and image-optimization fees.** Vercel's image-optimization and edge-function minutes are separately metered. Each Next.js `<Image>` view counts. For a marketing site this is small, but for any site that grows organically over a year, it compounds. Cloudflare's image resizing and Workers requests are metered too, but the free tier ceiling is meaningfully higher and the per-unit cost is lower at every tier we have benchmarked.

**Build-pipeline lock-in.** Vercel's build pipeline is tightly coupled to their platform. Their Next.js features (ISR, on-demand revalidation, edge middleware) work only on Vercel; the same code on a different host degrades. Cloudflare Pages is build-pipeline-agnostic — it accepts the static output of any framework, and the deploy is just a folder of files. This makes "leave Cloudflare" a one-day project. "Leave Vercel after writing Vercel-specific Next.js features" is a quarter-long project.

**Composability.** Cloudflare Pages, Workers, R2 (object storage), D1 (SQLite at the edge), Queues, and KV are one platform with one bill. The Main Branch stack uses Pages for the static site, Workers for any custom endpoint (e.g., the `mb claim` Skool-membership check), and R2 for ad-hoc artifact storage. On Vercel you'd reach for AWS or a third-party for the equivalents.

## What we recommend instead

Cloudflare Pages, deployed via `wrangler` from a GitHub repo, with a custom domain and SSL provisioned automatically. Builds run in Cloudflare's pipeline; deploys are atomic; rollbacks are one click. For any dynamic surface, Workers sit beside Pages in the same project.

## Setup walkthrough

1. Create a Cloudflare account at https://dash.cloudflare.com/sign-up. Free tier is enough.

2. Install `wrangler` (the Cloudflare CLI):
   ```bash
   npm install -g wrangler
   wrangler login
   ```
   The login command opens a browser tab and authorizes the CLI.

3. Connect a GitHub repo as a Pages project. From the dashboard: `Workers & Pages → Create → Pages → Connect to Git`. Pick the repo, the branch (typically `main`), and the build settings. For a vanilla static site, set the build command to whatever your framework needs (e.g., `npm run build`) and the output directory to `dist/` or `public/`.

4. Set a custom domain. From the project page: `Custom domains → Set up a domain`. Cloudflare will provision an SSL cert automatically if your domain is on Cloudflare DNS. If it's elsewhere, you add a CNAME at your registrar.

5. Verify deploys. Push a commit to `main`. Within ~60 seconds Cloudflare builds and publishes. Open the project URL.

6. Optional but recommended: set up a `wrangler.toml` in the repo so you can `wrangler pages deploy` from your laptop without a GitHub round-trip:
   ```toml
   name = "your-site"
   compatibility_date = "2026-04-29"
   pages_build_output_dir = "dist"
   ```
   Then `wrangler pages deploy dist/` after a local build.

Cost at typical Main Branch scale: $0/month for a marketing site under ~10K daily visitors. You start paying when you cross into Workers Paid ($5/month for 10M requests) or R2 storage above 10 GB.

## Honest limitations

Cloudflare Pages does not have first-class Next.js ISR or React Server Components support the way Vercel does. If you are building a heavy React app with dynamic SSR rendering and per-request edge logic, Vercel's developer experience is better and the lock-in cost may be worth it. For Main Branch sites — which are mostly static marketing surfaces with the occasional Worker for a form submit or a Skool gate — Pages is the right tool.

The Cloudflare dashboard is also denser and less polished than Vercel's. First-time users will need 30 minutes to learn it. After that it's fine.

## Resources

- Cloudflare Pages docs: https://developers.cloudflare.com/pages/
- Wrangler CLI: https://developers.cloudflare.com/workers/wrangler/
- Pricing comparison (Cloudflare): https://developers.cloudflare.com/pages/platform/limits/
- Vercel pricing (for comparison): https://vercel.com/pricing
