# Site Context

Load this when `/mb-site` needs prerequisites, active offer resolution, required business context, or section mapping.

## Prerequisites

Default deploy target is Cloudflare Pages. Netlify is supported only as a legacy fallback for pre-V1 Next.js templates; see [`deployment.md`](deployment.md).

| Tool | Required for | Install |
|---|---|---|
| Cloudflare account | All site shapes by default | https://dash.cloudflare.com |
| `gh` CLI authenticated | Repo creation | `brew install gh` then `gh auth login` |
| Cloudflare API token, account ID, GitHub App install | Domain/DNS/Pages flow | `mb connect cloudflare --token-stdin --metadata token_type=account --metadata account_id=...`, then [`cloudflare-pages-link.md`](cloudflare-pages-link.md) |
| `offer.md` and `audience.md` | Site generation | Build via `/mb-think` first if missing |
| Node 18+ and pnpm | Website shape with Next.js or Astro build step | `brew install node && npm install -g pnpm` |

Hard-gate Cloudflare-dependent work with:

```bash
mb connect doctor --json
```

If `provider:cloudflare` is not `ready`, do not run domain buy, DNS, Pages,
custom-domain, or deploy tools. Offer the operator: connect now with
`printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata token_type=account --metadata account_id=... && mb connect test cloudflare`;
continue read-only for availability checks, naming, brief, and research only;
or skip for now and record the blocker. User API tokens remain supported by
omitting `token_type=account`, but account-scoped tokens are preferred for
multi-business operators.

`verify_live.py` remains a deeper manual smoke after `mb connect` says
Cloudflare is ready. Expect Cloudflare scopes, zone lookup, and domain-check CLI
to pass. Porkbun skipped is fine for the Cloudflare-registered path.

## Active Offer Resolution

Before loading business context, resolve the active offer:

1. If a future `mb` JSON field exposes active offer state, use it; otherwise read `.vip/local.yaml` only as a legacy fallback.
2. If set, load `core/offers/[current_offer]/offer.md` as the active offer.
3. If not set and `core/offers/` exists, ask which offer this site is for.
4. If no `core/offers/` folder exists, use `core/offer.md` for a single-offer repo.

Always-core files, never per-offer: `soul.md`, `voice.md`, `content-strategy.md`.

Offer-aware files, check `core/offers/` first and fall back to `core/`: `offer.md`, `audience.md`.

Accumulate files: testimonials and proof can come from both offer-specific context and brand-level `core/proof/`.

## Required Business Context

| File | Path | Required |
|---|---|---|
| Offer | `core/offers/[active]/offer.md` or `core/offer.md` | Yes |
| Audience | `core/offers/[active]/audience.md` or `core/audience.md` | Yes |
| Voice | `core/voice.md` | Recommended |
| Soul | `core/soul.md` | Optional |
| Testimonials | `core/proof/testimonials.md` plus offer-specific proof if present | Recommended |
| Angles | `core/proof/angles/*.md` | Optional |
| Content Strategy | `core/content-strategy.md` | Optional |
| Skool Surfaces | `core/operations/funnel/skool-surfaces.md` | Optional for congruence |

Legacy `reference/*` paths are compatibility fallback only. Do not write new evergreen business truth there.

If required files are missing, stop and route to `/mb-think codify`:

> "Your offer.md is missing. I need it to generate the site. Run `/mb-think` to build your core business files first."

## Reference-To-Section Mapping

How business context flows into a generated site:

| Business context | Produces |
|---|---|
| Resolved `offer.md` | Hero headline/subhead, value prop, pricing, CTA copy |
| Resolved `audience.md` | Pain sections, objection handling, copy language/tone |
| `voice.md` | Palette, font selection, aesthetic mood, copy tone |
| `soul.md` | About/mission section, founder story, credibility badge |
| `core/proof/testimonials.md` | Social proof, stat counters, trust badges |
| `core/proof/angles/*.md` | Page structure and section order |
| `core/content-strategy.md` | CTA destinations and newsletter/signup integration |

Detail per shape:

- Minisite: [`minisite-generation-system.md`](minisite-generation-system.md) and [`anti-patterns.md`](anti-patterns.md).
- Website: [`section-patterns.md`](section-patterns.md) and [`frontend-design.md`](frontend-design.md).

## Pipeline Position

The site is infrastructure, not recurring content. It is the destination the content pipeline drives traffic to.

```text
/mb-think -> core business files
     |
/mb-site -> site conversion endpoint
     |
/mb-ads, /mb-organic, email/newsletter content -> traffic to site
```

When core business files change significantly, such as new offer or pricing, consider re-running build:

> "Your offer.md was updated since the site was last published. Want to run `/mb-site build` to update?"
