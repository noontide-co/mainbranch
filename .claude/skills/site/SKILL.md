---
name: site
description: "Triage and build any site shape — lander (1 page), minisite (~4 pages), or full website — and graduate between them. Routes to per-shape build flow, reads from business reference files, deploys to Cloudflare Pages with git auto-deploy. Use when:
  (1) Operator says 'I want a site' / 'I want a lander' / 'spin up a one-pager'
  (2) Setting up a new site of any shape from offer + audience material
  (3) Updating / iterating on an existing site
  (4) Graduating a site to a new shape (lander → minisite → website → website + CMS)
  (5) Previewing or publishing changes

  Triggered by: /site, 'build a site', 'landing page', 'lander', 'minisite', 'website', 'I need a site', 'spin up a site', 'put this online', 'publish site', 'deploy site', 'update my site', 'graduate my site', 'add a CMS to my site'"
---

# Site

Pick a site shape, build it from your business reference files, ship it to Cloudflare Pages with git auto-deploy. Graduate up the shape ladder when an offer earns it.

---

## Re-Invoke Often

Say `/site` again after compaction, context loss, or switching focus. It reloads skill context. Do it whenever the conversation feels stale.

---

## Pull Latest Updates

For the canonical vip-resolution + pull bash block (and the failure warning), see [`.claude/reference/pull-engine-updates.md`](../../reference/pull-engine-updates.md). Run it at the start of every invocation.

---

## Operating principles

Four behaviors `/site` uses on every run, not optional:

**1. One flow: brief → site.** The brief and the site live in the same skill. Don't tell the operator "build the brief in X, then come back for the site." `/site` walks: research → brief draft → review → lock → concept variations → publish → iterate. Continuous.

**2. Foreground subagents, always.** When spawning subagents (research, concept generation, review passes), keep them in the foreground. Background subagents have a known file-write bug — files appear written but don't persist. Foreground only. See [`references/concept-variations.md`](references/concept-variations.md) for the spawn pattern.

**3. Parallel by default.** Multiple research questions? Spawn agents in parallel. Multiple concept variations? Spawn in parallel. Multiple review passes? Spawn in parallel. Sequential is the exception, not the rule.

**4. Publish-first, then iterate.** Push the rawest working version of the brief, then the rawest working concept, to GitHub immediately. Git history is the durable memory across context clears. Chat compaction can't be trusted. Iterate on top of committed work, not in-memory state.

When research subagents record findings, they follow the [`/think` research patterns](../think/SKILL.md) — dated `research/YYYY-MM-DD-slug-claude-code.md` files with frontmatter (`linked_decisions: []`), so the research → decision → reference chain stays intact across the brief and the site.

---

## Where Files Go

```
your-business-repo/          <- Reference files READ from here
├── reference/core/           (offer.md, audience.md, voice.md, soul.md)
├── reference/proof/          (testimonials.md, angles/)
└── reference/domain/         (content-strategy.md)

your-site-repo/              <- Site code WRITTEN here
                             (shape-specific layout — see per-shape build refs)

~/.mainbranch/sites.json     <- Config pointing to repos

vip/ (engine)                <- Never modified by /site
└── .claude/skills/site/
```

The skill reads from the business repo and writes to the site repo. These are separate repos.

---

## Prerequisites

Default deploy target is **Cloudflare Pages** (better CLI, better domain integration, git auto-deploy, supports static and build-step sites alike).

| Tool | Required for | Install |
|---|---|---|
| Cloudflare account | All site shapes (default) | https://dash.cloudflare.com (free) |
| `gh` CLI authenticated | Repo creation | `brew install gh` + `gh auth login` |
| Cloudflare API token + account ID + GitHub App install | Atom-driven domain/DNS/Pages flow | One-time: `bash .claude/skills/site/scripts/setup_creds.sh` then [`references/cloudflare-pages-link.md`](references/cloudflare-pages-link.md) for the GitHub App OAuth handshake |
| `offer.md` + `audience.md` | Site generation | Build via `/think` first if missing |
| Node 18+ + pnpm | **Only for Website shape** with Next.js / Astro build step | `brew install node && npm install -g pnpm` |

Verify atom credentials with:
```bash
source ~/.config/vip/env.sh
python3 .claude/skills/site/scripts/verify_live.py
```
Expect 3/3 passed (Cloudflare scopes + zone lookup + domain-check CLI). Porkbun skipped is fine for the CF-registered path.

Netlify is supported as a legacy fallback for pre-V1 Next.js templates only — see [`references/deployment.md`](references/deployment.md). Not the default target.

---

## Config Discovery

On every invocation, check for existing config:

```bash
cat ~/.mainbranch/sites.json 2>/dev/null || echo "NO_CONFIG"
```

- **Config found, one site:** Confirm with user, load site repo path
- **Config found, multiple sites:** Ask which site to work on (numbered list)
- **No config:** Route to setup mode

---

## Offer Context Resolution

Before loading reference files, resolve the active offer:

1. Check `.vip/local.yaml` for `current_offer`
2. If set: load `reference/offers/[current_offer]/offer.md` as the active offer
3. If not set AND `reference/offers/` exists: ask which offer this site is for
4. If no `offers/` folder: use `reference/core/offer.md` (single-offer, backward compatible)

**Always-core files** (never per-offer): `soul.md`, `voice.md`, `content-strategy.md`
**Offer-aware files** (check offers/ first, fall back to core/): `offer.md`, `audience.md`
**Accumulate files** (load both): `testimonials.md` (offer-specific + brand-level)

`~/.mainbranch/sites.json` can include an `offer` field that overrides `.vip/local.yaml`:

```json
{
  "name": "thelastbill",
  "offer": "the-last-bill",
  "site_repo": "/absolute/path/to/site-repo",
  "business_repo": "/absolute/path/to/business-repo",
  "shape": "minisite",
  "hosting": "cloudflare",
  "domain": "thelastbill.com"
}
```

---

## Reference Required

| File | Path | Required |
|---|---|---|
| Offer | `offers/[active]/offer.md` or `core/offer.md` (resolved) | **Yes** |
| Audience | `offers/[active]/audience.md` or `core/audience.md` (resolved) | **Yes** |
| Voice | `reference/core/voice.md` | Recommended |
| Soul | `reference/core/soul.md` | Optional |
| Testimonials | `reference/proof/testimonials.md` (+ offer-specific if exists) | Recommended |
| Angles | `reference/proof/angles/*.md` | Optional |
| Content Strategy | `reference/domain/content-strategy.md` | Optional |
| Skool Surfaces | `reference/domain/funnel/skool-surfaces.md` | Optional (congruence) |

If required files are missing, stop and route to `/think codify`:
> "Your offer.md is missing. I need it to generate the site. Run `/think` to build your reference files first."

---

## Triage — What Are You Building?

Ask the operator. Route based on the answer; don't assume.

> **What are you doing?**
>
> **A. New site from scratch.** Pick a shape:
> - 🟦 **Lander** (1 page, all-in-one) — hero + offer + proof + CTA + footer. Maximum focus, minimum nav.
>   *V1: per-offer lander generation not yet wired. Use **Minisite** for single-page-feel use cases — its home page covers the focused conversion target.* Future spec: [`references/lander-build.md`](references/lander-build.md).
>
> - 🟩 **Minisite** (~4–6 pages, static HTML) — home + how-it-works + 2–4 LLM-picked + privacy/terms/start-thanks. Designed fresh per offer by a generation subagent. **V1 target.**
>   Best for: paid-ad lander tests, single-offer first deploys, payment / lead-form / booking funnels.
>   Flow: [`references/minisite-build.md`](references/minisite-build.md). Engine spec: `mb-vip/.claude/reference/minisite.md`.
>
> - 🟨 **Website** (full, multi-section, build step likely) — depth, blog, multiple offers, knowledge base, course area.
>   *V1 status:* per-offer Website generation pending. Legacy Next.js templates (`saas`, `high-ticket`) work today as starting points.
>   Flow: [`references/website-build.md`](references/website-build.md).
>
> **B. Iterating on an existing site.** Same shape, more content / edits.
> - Editing pages, adding sections, updating copy → go straight to **Mode: build** (per the existing site's shape)
> - Just publishing your work → **Mode: publish**
>
> **C. Graduating to a different shape.** Existing site has earned more.
> - Lander → Minisite (single-pager pulls more content)
> - Minisite → Website (~4–6 pages becoming 10+, blog, multi-offer)
> - Website → Website + CMS (Sanity / Contentful / etc. for non-dev editing)
> - Read [`references/graduation.md`](references/graduation.md) — when to graduate, what changes, manual vs scripted.

If the operator can't articulate which they're doing, ask the predecessor question: *"What goal are you trying to hit? Drive paid traffic to a sale, lead, or booking? Sell a course? Replace your current Squarespace?"* Their answer maps cleanly to a shape.

---

## Modes (cross-shape)

| Mode | What it does | Trigger |
|---|---|---|
| **setup** | First-run for a new site of the chosen shape | "new site", "spin up", "build me a site" |
| **build** | Generate or edit content (shape-specific — see per-shape ref) | "build", "regenerate", "add a section" |
| **preview** | Local server / dev environment (shape-specific) | "preview", "show me locally" |
| **publish** | Stage, commit, push — Cloudflare auto-deploys | "publish", "ship it", "deploy" |

Per-shape detail in the build refs:
- [`references/minisite-build.md`](references/minisite-build.md) — minisite full flow
- [`references/website-build.md`](references/website-build.md) — Next.js website flow
- [`references/lander-build.md`](references/lander-build.md) — lander (V1 stub; mostly delegates to minisite)

The `publish` mode is shape-agnostic when the project is git-connected to Cloudflare Pages: `git push` triggers auto-deploy. For legacy Netlify-deployed projects, see [`references/deployment.md`](references/deployment.md).

---

## Reference-to-Section Mapping

How offer/audience/voice/proof material flows into a generated site:

| Reference File | Produces |
|---|---|
| Resolved `offer.md` | Hero headline/subhead, value prop, pricing, CTA copy |
| Resolved `audience.md` | Pain point sections, objection handling, copy language/tone |
| `voice.md` | Color palette, font selection, aesthetic mood, copy tone |
| `soul.md` | About/mission section, founder story, credibility badge |
| `testimonials.md` | Social proof, stat counters, trust badges |
| `angles/*.md` | Page structure — which angle drives section order |
| `content-strategy.md` | CTA destinations, newsletter signup integration |

Detail per-shape:
- Minisite: [`references/minisite-generation-system.md`](references/minisite-generation-system.md) (the system prompt) + [`references/anti-patterns.md`](references/anti-patterns.md)
- Website (Next.js): [`references/section-patterns.md`](references/section-patterns.md) + [`references/frontend-design.md`](references/frontend-design.md)

---

## Pipeline Position

The site is **infrastructure**, not recurring content. It's the destination the content pipeline drives traffic to.

```
/think → reference files (the foundation)
     ↓
/site → site (conversion endpoint)
     ↓ drives traffic to:
/ads → paid traffic → site
/organic → social links → site
/newsletter → email CTA → site
```

When reference files change significantly (new offer, new pricing), consider re-running build:
> "Your offer.md was updated since the site was last published. Want to run `/site build` to update?"

---

## Recovery from Compaction

If conversation compacted or context was lost:

1. **Re-invoke `/site`** to reload skill context
2. **Check config:** `cat ~/.mainbranch/sites.json 2>/dev/null`
3. **Identify the site shape** from the config's `shape` field; load the corresponding build ref
4. **Check site repo status:** `cd <site_repo> && git status && git log --oneline -5`
5. **Resume from last completed step** based on git history + sites.json state

---

## Brief schema (v0.1)

The brief is the locked source of truth for any /site flow. v0.1 adds these fields on top of the legacy schema:

| Field | Type | Required? | Purpose |
|---|---|---|---|
| `dial` | enum: `convert / story / brand` | required | Routes Seven Sweeps depth at review |
| `archetype` | enum: 9 archetypes | optional but recommended | Drives paired-imagery + headline-formula picks |
| `audience_current_archetype` | string | optional | What the audience is *trapped in*. Reframe target. |
| `do_not_state` | list[string] | required when archetype set | Conclusions the audience must reach themselves |
| `four_forces` | object: `{push, pull, habit, anxiety}` | optional | JTBD frame |
| `voice_anchor_lines` | object: `{use: [], avoid: []}` | required | Per-site voice slice |
| `headline_formulas_picked` | list[string] | optional, suggested 2-3 | Picked from `headline-formulas.md` |
| `copy_framework_tag` | enum (PAS / AIDA / StoryBrand / Compact-Landing / Varied / Enterprise-B2B / Product-Launch / null) | optional | Extends `framework_tag` with Haines page templates |

**Migration:** existing briefs dated before 2026-04-29 use the older schema (no `dial`, `archetype`, `do_not_state`). The skill tolerates them. New briefs created on or after 2026-04-29 must include the new required fields. `mb validate` enforces the date-based check.

---

## Scope

Site shapes `/site` covers: **lander** (1 page), **minisite** (~4–6 pages), **website** (full). Plus graduation paths up the ladder, including bolt-on CMS for the website tier.

**Not for:**
- Wikis (`/wiki`)
- Email templates (`/newsletter`)
- Quick mockups without business reference files
- Apps with auth, dashboards, real-time features (use a separate app skill)

---

## References

**Triage + per-shape build flows:**

- [references/lander-build.md](references/lander-build.md) — 1-page shape (V1 stub)
- [references/minisite-build.md](references/minisite-build.md) — ~4–6 page shape (V1 target)
- [references/website-build.md](references/website-build.md) — full-site shape (Next.js + future per-offer generation)
- [references/graduation.md](references/graduation.md) — paths between shapes + CMS bolt-on (Sanity, Contentful, Notion, etc.)

**Generation + design (used by per-shape flows):**

- [references/minisite-generation-system.md](references/minisite-generation-system.md) — load-bearing system prompt for minisite generation subagent
- [references/concept-variations.md](references/concept-variations.md) — parallel-on-localhost concept generation pattern (default 2)
- [references/review.md](references/review.md) — quality-gate steps the skill runs through before lock and before publish
- [references/anti-patterns.md](references/anti-patterns.md) — what NOT to bake into prompts (AI-tells + generation anti-patterns)
- [references/archetypes.md](references/archetypes.md) — Hughes 9-archetype catalog (picker for the brief)
- [references/archetypes/<slug>.md](references/archetypes/) — per-archetype detail (lazy-loaded)
- [references/headline-formulas.md](references/headline-formulas.md) — 20+ formulas grouped by frame, picked per dial + archetype
- [references/naming-heuristic.md](references/naming-heuristic.md) — 8-step domain naming playbook
- [references/cloudflare-pages-link.md](references/cloudflare-pages-link.md) — CF Pages GitHub App handshake walkthrough
- [references/frontend-design.md](references/frontend-design.md) — typography, color, motion (Next.js-relevant)
- [references/section-patterns.md](references/section-patterns.md) — section catalog (Next.js-relevant)

**Legacy:**

- [references/deployment.md](references/deployment.md) — Netlify deploy walkthrough (legacy fallback)
- [references/examples-and-troubleshooting.md](references/examples-and-troubleshooting.md) — usage examples, common fixes
