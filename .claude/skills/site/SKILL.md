---
name: site
description: "Generate and deploy landing pages from business reference files. Use when:
  (1) Setting up a new site from a starter template
  (2) Applying brand identity from reference files
  (3) Building or editing page sections
  (4) Previewing locally
  (5) Publishing to Netlify

  Triggered by: /site, 'build a site', 'landing page', 'deploy site', 'website',
  'update my site', 'publish site', 'I need a site', 'put this online'"
---

# Site

Generate and deploy landing pages from your business reference files.

---

## Re-Invoke Often

Say `/site` again after compaction, context loss, or switching focus. It reloads skill context. Do it whenever the conversation feels stale.

---

## Pull Latest Updates

```bash
# Canonical vip resolution (settings.local.json first — no extra deps)
VIP_PATH=$(python3 -c "
import json, os
try:
    with open('.claude/settings.local.json') as f:
        dirs = json.load(f).get('permissions', {}).get('additionalDirectories', [])
    for d in dirs:
        if os.path.isfile(os.path.join(d, '.claude/skills/start/SKILL.md')):
            print(d); break
except: print('')
" 2>/dev/null)

# Fallback: check ~/.config/vip/local.yaml (needs PyYAML)
if [ -z "$VIP_PATH" ] || [ ! -f "$VIP_PATH/.claude/skills/start/SKILL.md" ]; then
  VIP_PATH=$(python3 -c "
import os
try:
    import yaml
    with open(os.path.expanduser('~/.config/vip/local.yaml')) as f:
        print(yaml.safe_load(f).get('vip_path', ''))
except: print('')
" 2>/dev/null)
fi

# Pull if found and valid
[ -n "$VIP_PATH" ] && [ -f "$VIP_PATH/.claude/skills/start/SKILL.md" ] && \
  git -C "$VIP_PATH" pull origin main 2>&1
```

---

## Where Files Go

```
your-business-repo/          <- Reference files READ from here
├── reference/core/           (offer.md, audience.md, voice.md, soul.md)
├── reference/proof/          (testimonials.md, angles/)
└── reference/domain/         (content-strategy.md)

your-site-repo/              <- Site code WRITTEN here
├── app/                      (layout.tsx, page.tsx, globals.css)
├── components/               (hero.tsx, cta.tsx, etc.)
├── site-config.ts            (all brand-specific content)
└── public/                   (images, favicon)

~/.mainbranch/sites.json     <- Config pointing to repos

vip/ (engine)                <- Never modified by /site
└── .claude/skills/site/
```

The skill reads from the business repo and writes to the site repo. These are separate repos.

---

## Prerequisites

Before first run, verify:

```bash
node --version    # Need 18+
pnpm --version    # Package manager
gh auth status    # GitHub CLI authenticated
```

- **Node.js 18+** — Required for Next.js
- **pnpm** — Package manager (`npm install -g pnpm` if missing)
- **GitHub CLI** — For repo creation (`brew install gh` on Mac)
- **Netlify account** — Free tier works. Created during setup if needed.
- **Business reference files** — At minimum: `offer.md` and `audience.md`

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

**Site config extension:** `~/.mainbranch/sites.json` can include an `offer` field to link a site to a specific offer:

```json
{
  "name": "community-landing",
  "offer": "community",
  "site_repo": "/absolute/path/to/site-repo",
  "business_repo": "/absolute/path/to/business-repo",
  "template": "high-ticket",
  "hosting": "netlify",
  "domain": "community.example.com"
}
```

When a site has an `offer` field, use that as the active offer instead of reading `.vip/local.yaml`.

---

## Reference Required

| File | Path | Required |
|------|------|----------|
| Offer | `offers/[active]/offer.md` or `core/offer.md` (resolved via path resolution) | **Yes** |
| Audience | `offers/[active]/audience.md` or `core/audience.md` (resolved via path resolution) | **Yes** |
| Voice | `reference/core/voice.md` (always core) | Recommended |
| Soul | `reference/core/soul.md` (always core) | Optional |
| Testimonials | `reference/proof/testimonials.md` + `offers/[active]/testimonials.md` (accumulate) | Recommended |
| Angles | `reference/proof/angles/*.md` | Optional |
| Content Strategy | `reference/domain/content-strategy.md` (always brand-level) | Optional |
| Skool Surfaces | `reference/domain/funnel/skool-surfaces.md` | Optional (congruence) |

If required files are missing, stop and route to `/think codify`:

> "Your offer.md is missing. I need it to generate the site. Run `/think` to build your reference files first."

---

## Reference-to-Section Mapping

| Reference File | Produces |
|---------------|----------|
| Resolved `offer.md` | Hero headline/subhead, value prop, pricing, CTA copy |
| Resolved `audience.md` | Pain point sections, objection handling, copy language/tone |
| `voice.md` (always core) | Color palette, font selection, aesthetic mood, copy tone |
| `soul.md` (always core) | About/mission section, founder story, credibility badge |
| `testimonials.md` (accumulated) | Social proof section, stat counters, trust badges |
| `angles/*.md` | Page structure — which angle drives section order |
| `content-strategy.md` (brand-level) | CTA destinations, newsletter signup integration |

Detailed mapping rules: [references/section-patterns.md](references/section-patterns.md)

---

## Modes

| Mode | What It Does | Trigger |
|------|--------------|---------|
| **setup** | Pick template, scaffold repo, install, deploy | First run, "new site" |
| **configure** | Apply brand (colors, fonts, metadata) from reference | After setup, "change brand" |
| **build** | Generate/edit page sections from reference files | "add section", "update hero", "rebuild" |
| **preview** | Start dev server for local preview | "preview", "show me" |
| **publish** | Git commit + push → Netlify auto-deploy | "publish", "deploy", "ship it" |

---

## Mode: setup

First-time setup. Creates a new site repo from a starter template.

### Step 1: Choose Site Shape

Present options. Site shape, not business vertical — vertical is in `offer.md`.

> **What kind of site are you building?**
>
> 1. **Lander** (1 page, all-in-one) — single page: hero + offer + proof + CTA + footer.
>    *V1 status:* pattern defined, generation system prompt not yet written. Use **Minisite** for now if you need single-page-feel — option 2 already covers that case via its `/start/` page.
>
> 2. **Minisite** (~4 pages, static HTML) — home + `how-it-works/` + 2 LLM-picked from `{proof, pricing, start, faq}` + required `privacy/`, `terms/`, `start/thanks/`. Designed fresh per offer by a generation subagent. **Cloudflare Pages by default. V1 chassis target.**
>    Best for: paid-ad minisite tests, single-offer first deploys, deposit-gateway flows.
>    Spec: [`mb-vip/.claude/reference/minisite.md`](../../reference/minisite.md). Skill flow below: see "Minisite Template Branch."
>
> 3. **Website** (full, multi-section, build step likely) — for businesses with content depth (blog, multiple offers, knowledge base, course area).
>    *V1 status:* pattern defined, chassis-shape Website generation not yet wired. Legacy Next.js templates (`saas`, `high-ticket`) work via Steps 2–11 below as starting points; those are pre-chassis examples that fit a few specific verticals. The full Website tier evolves in V2.

**Hosting default:** Cloudflare Pages for all three shapes. Better CLI, better domain integration, git auto-deploy out of the box. Netlify path stays for the legacy `saas` / `high-ticket` templates only — not the chassis target.

**Graduation:** sites can graduate up the shape ladder when an offer earns it. Lander → Minisite (the single-pager pulls traffic that wants more proof, more pages emerge). Minisite → Website (a winning minisite gets deeper content, a blog, multi-offer support, course area). The graduation isn't automatic; it's an operator decision triggered by the offer pulling traffic that wants more content. V1 doesn't ship a graduation tool — manual repo work for now; future skill mode if it becomes recurring.

If `minisite` is chosen, **skip Steps 2–11 below and go to "Minisite Template Branch"** — that flow uses Cloudflare Pages + atoms. Steps 2–11 apply to the legacy `saas` / `high-ticket` Next.js templates only.

### Step 2: Name and Location

Ask:
- Site name (e.g., "my-landing-page")
- Location (default: `~/sites/[name]`)

### Step 3: Check Prerequisites

```bash
node --version && pnpm --version && gh auth status
```

If anything missing, help them install before proceeding.

### Step 4: Create GitHub Repo

```bash
gh repo create [name] --private --clone --directory [location]
cd [location]
```

### Step 5: Add Template as Upstream

```bash
git remote add upstream https://github.com/mainbranch-ai/site-template-[saas|high-ticket].git
git fetch upstream
git merge upstream/main --allow-unrelated-histories -m "Initial template merge"
```

### Step 6: Install Dependencies

```bash
pnpm install
```

Handle common errors:
- Wrong Node version → suggest `nvm use 18`
- pnpm not found → `npm install -g pnpm`

### Step 7: Verify Build

```bash
pnpm build
```

If build fails, troubleshoot before proceeding. Don't deploy a broken build.

### Step 8: Initial Commit and Push

```bash
git add -A
git commit -m "[add] Initial site from template"
git push -u origin main
```

### Step 9: Deploy to Netlify

Walk user through Netlify dashboard. See [references/deployment.md](references/deployment.md) for full walkthrough.

Key settings: Build command = `pnpm build`, Publish directory = `out`, NODE_VERSION = `20`.

### Step 10: Detect Business Repo

Ask: "Where is your business repo with reference files?" Confirm the path has `reference/core/` files.

If the business repo has `reference/offers/`, ask which offer this site is for. Store the offer in the sites.json config (see `offer` field above).

### Step 11: Save Config

Write `~/.mainbranch/sites.json`:

```json
[
  {
    "name": "[site-name]",
    "site_repo": "/absolute/path/to/site-repo",
    "business_repo": "/absolute/path/to/business-repo",
    "template": "saas",
    "hosting": "netlify",
    "domain": "[name].netlify.app"
  }
]
```

Create `~/.mainbranch/` directory if it doesn't exist.

**Exit:**

> "Site deployed at https://[url]. Run `/site configure` to apply your brand, or `/site build` to start customizing sections from your reference files."

---

## Minisite Template Branch

When the operator picked the `minisite` template in Step 1, the setup and build flows are different from the Next.js templates above. Static HTML, no build step, Cloudflare Pages, atom-driven domain + DNS + custom-domain attachment.

### setup (minisite)

**1. Name + project repo.** Ask the operator:
- Site name (e.g., `thelastbill`). Becomes the Pages project name.
- Project repo location (default: sibling of vip — `~/Documents/GitHub/<name>` for solo, `~/Documents/GitHub/noontide-sites/<name>` for Noontide work). Empty repo, no template merge.
- Apex domain. If they don't have one, route to [`references/naming-heuristic.md`](references/naming-heuristic.md) — an 8-step playbook for generating + validating brand-tier names.

**2. Atom-chain prerequisites.** Confirm the credentials are in place via:
```bash
source ~/.config/vip/env.sh
python3 .claude/skills/site/scripts/verify_live.py
```
Expect 3/3 passed (Cloudflare scopes + zone lookup + domain-check CLI). Porkbun skipped is fine for the CF-registered path.

If anything's red, route the operator to `bash .claude/skills/site/scripts/setup_creds.sh` to provision Cloudflare credentials, then re-run.

**3. Domain — buy-new vs. existing.** Ask:
- "Already own the domain?" → skip to step 4 with the domain name
- "Need to buy?" → run `python3 .claude/skills/site/scripts/domain.py check <name> --tlds .com,.co,.io` first to confirm availability + TLD support. If `extension_not_supported_via_api`, fall back to the Cloudflare dashboard (https://dash.cloudflare.com/registrar — confirm the right account before purchase). For API-supported TLDs and after explicit operator Y on price, proceed with `domain.py buy <name>` — *will be wired in a follow-up PR; today the buy is dashboard for the first minisite, then API once `domain.py buy --registrar=cloudflare` lands*.

**4. DNS ensure.** Once the domain is owned (CF Registrar or Porkbun), run:
```bash
python3 .claude/skills/site/scripts/dns.py ensure <domain> --registrar cloudflare --skip-propagation-poll
```
For CF-registered domains the zone is auto-created with NS already at CF — this is an idempotent verification, not a state change. For Porkbun-registered domains, the atom swaps NS to CF nameservers and polls propagation.

**5. GitHub repo + initial scaffold push.** Create the project repo and push a placeholder `index.html` so the Pages project has something to deploy:
```bash
gh repo create <owner>/<name> --public --add-readme
git clone https://github.com/<owner>/<name>.git ~/Documents/GitHub/<name>
cd ~/Documents/GitHub/<name>
echo '<!doctype html><title><name></title><h1>soon</h1>' > index.html
git add -A && git commit -m "[add] placeholder" && git push
```

**6. Cloudflare Pages project.** Create via wrangler (no dashboard click needed):
```bash
wrangler pages project create <name> --production-branch main
wrangler pages deploy . --project-name <name> --branch main
```
This deploys the placeholder to `https://<hash>.<name>.pages.dev`. The git-source connection (auto-deploy on push) is added by `pages.py create-project` once **#98** ships; until then, manual `wrangler pages deploy` after each push, or one-time UI walkthrough at [`references/cloudflare-pages-link.md`](references/cloudflare-pages-link.md).

**7. Custom domain attach + DNS verification.** Run:
```bash
python3 .claude/skills/site/scripts/pages.py set-domain <name> <domain> --timeout-seconds 300
```
The atom attaches the domain, creates the CNAME record in the zone (the step the dashboard hides), and polls until SSL is active. Expect ~3-4 min total. Live-tested end-to-end in PR #97.

**8. Save config.** Same `~/.mainbranch/sites.json` structure as the Next.js path:
```json
{
  "name": "<name>",
  "site_repo": "/absolute/path/to/repo",
  "business_repo": "/absolute/path/to/business-repo",
  "template": "minisite",
  "hosting": "cloudflare",
  "domain": "<full apex>"
}
```

**Exit:**
> "Minisite ready at https://<domain>. Placeholder deployed; run `/site build --one-shot` to generate the actual minisite from your offer + audience specs."

### build --one-shot (minisite)

This is the load-bearing mode — where Claude (the operator's running session) spawns a subagent that generates fresh HTML/CSS/SVG for this offer. No template inheritance. No placeholder tokens. No Anthropic SDK call. The subagent is a Claude Code subagent, spawned via the `Agent` tool.

**1. Resolve offer context.** Use the existing offer-context resolution above (lines 116–145). At minimum: `offer.md` + `audience.md` paths + the active offer slug.

**2. Load the system prompt.** Read [`references/minisite-generation-system.md`](references/minisite-generation-system.md) verbatim. This is the load-bearing artifact — the full hard-constraints + soft-brief framing for the generation subagent. Pass it as the subagent's system prompt unmodified.

**3. Build the user message.** Compose:
- Resolved `offer.md` content
- Resolved `audience.md` content
- Optional `voice.md` snippets (anchor phrases, named enemies, "never say" list)
- Reference URLs — defaults: `https://howdy.md`, `https://thelastbill.com`. Operator can pass `--reference URL` to add or replace
- Project repo absolute path (where the subagent writes via `Write`)
- Soft directive: *"Generate fresh HTML/CSS/SVG for this offer. The reference URLs are taste anchors, not templates — read them for polish level, then design something that fits **this** offer. Surprise me."*

Anti-patterns to avoid in your own framing of the user message: see [`references/anti-patterns.md`](references/anti-patterns.md). The big ones: don't lock typography or colors, don't enumerate available sections, don't ask the subagent to "make it look like the references," don't suppress variance.

**4. Spawn the subagent.** Invoke the `Agent` tool with `subagent_type=general-purpose`, the system prompt from step 2, and the user message from step 3. The subagent has `Write` access; it will write files directly to the project repo path.

**5. Validate the output.** After the subagent returns, run these checks against the project repo:

- **Required files present:** `index.html`, `how-it-works/index.html`, two more page directories with `index.html`, `privacy/index.html`, `terms/index.html`, `_headers`, `_redirects`, `robots.txt`, `sitemap.xml`, `og.svg`, `favicon.svg`. Each missing file = a fix request to the subagent.
- **Footer presence:** `grep -L "Noontide Collective LLC" *.html **/*.html` should return nothing (or only files where `offer.md` declared a different parent entity — check the override).
- **OG render:** `python3 .claude/skills/site/scripts/og_render.py render <repo>/og.svg <repo>/og.png`. Envelope must return `status: ok` with `width: 1200, height: 630`. Failure → fix request to subagent (likely `og.svg` viewBox is wrong).
- **Lighthouse smoke (optional, V1.1):** `npx lighthouse http://localhost:8000 --only-categories=performance --form-factor=mobile` against a local `python3 -m http.server` running in the project repo. Score ≥ 90 = pass.

**6. Commit + push (operator's call).** Once validation is green, summarize for the operator:
- Files written
- Hero artifact picked
- Color palette
- Two page choices
- Suggested commit message: `"[add] one-shot minisite generation for <offer>"`

Operator runs `git add -A && git commit && git push`. Cloudflare auto-deploys (after #98) or operator runs `wrangler pages deploy` manually.

**Variance test (acceptance criterion):** Running `/site build --one-shot` twice on the same offer must produce visually different output. If it doesn't, the soft brief was too prescriptive — re-read [`references/anti-patterns.md`](references/anti-patterns.md).

### What's NOT in the minisite branch

- No `pnpm install`, no `pnpm build`. Static HTML only.
- No `site-config.ts` pattern. Each minisite generates its own one-off structure.
- No section-types menu (the Next.js section catalog at lines 381–399 doesn't apply).
- No `configure` mode separate from `build --one-shot` — the generation subagent reads voice.md / offer.md directly and bakes the brand decisions into the output.
- No Anthropic API key. No `pages_gen.py` Python wrapper. The generation runs inside the operator's Claude Code session via the `Agent` tool.

---

## Mode: configure

Apply brand identity from reference files to the site's visual system.

### What It Reads

- `voice.md` — Aesthetic direction, tone, personality
- `offer.md` — Headline copy, value proposition
- `soul.md` — Mission text, credibility elements

### What It Changes

- `app/globals.css` — CSS custom properties (colors, fonts)
- `app/layout.tsx` — Font imports, metadata
- `site-config.ts` — Brand name, tagline, metadata

### Voice-to-Aesthetic Derivation

| Voice Trait | Design Implication |
|---|---|
| Warm, personal | Rounded corners, warm palette, serif or humanist sans display font |
| Direct, authoritative | Sharp corners, high contrast, geometric sans or strong serif |
| Playful, energetic | Bold colors, larger type scale, bouncy motion, personality fonts |
| Premium, refined | Restrained palette, ample whitespace, thin weights, serif display |
| Technical, expert | Monospace accents, structured grids, muted palette with signal color |

See [references/frontend-design.md](references/frontend-design.md) for font pairings, color systems, and motion guidelines.

### Steps

1. Read `voice.md` — determine aesthetic direction
2. Read `offer.md` — extract headline, tagline, CTA text
3. Choose font pairing based on voice (see frontend-design reference)
4. Choose color palette based on brand positioning
5. Update CSS variables in `globals.css`
6. Update font imports in `layout.tsx`
7. Update metadata (title, description, OG tags) in `layout.tsx`

### Checkpoint

> "Preview the brand changes? Run `/site preview` to see them locally, or continue to `/site build` to generate sections."

---

## Mode: build

The core generation mode. Reads reference files and generates page sections.

### How It Works

1. Resolve offer context (see Offer Context Resolution above) — use offer-specific `offer.md` and `audience.md` when available
2. Read reference files from business repo (resolved paths)
3. Generate or update `site-config.ts` — the single source of all brand-specific content
4. Generate or edit component files in `components/`
5. Update page composition in `app/page.tsx`

### The site-config.ts Pattern

All brand-specific content lives in one file. Components import from it:

```typescript
// site-config.ts
export const siteConfig = {
  brand: {
    name: "Your Business",
    tagline: "Your tagline from offer.md",
    email: "you@example.com",
  },
  hero: {
    eyebrow: "DERIVED FROM AUDIENCE.MD",
    headline: "Derived from offer.md headline",
    subhead: "Derived from offer.md value proposition",
    ctaText: "Derived from offer.md CTA",
    ctaUrl: "#pricing",
  },
  // ... sections populated from reference files
}
```

### Section Types Available

| Section Type | Purpose | Reference Source |
|---|---|---|
| `hero` | Headline, subhead, CTA, badge | offer.md, audience.md |
| `reasons-grid` | Pain point cards | audience.md |
| `process-stepper` | How it works timeline | offer.md (mechanism) |
| `credibility` | Stats, testimonials, trust | testimonials.md |
| `competitive-positioning` | Why you vs alternatives | offer.md, audience.md |
| `objection-handling` | FAQ-style objection reframes | audience.md |
| `faq` | Standard Q&A accordion | offer.md, audience.md |
| `cta-simple` | Headline + button + microcopy | offer.md |
| `cta-application` | Multi-step qualification form | audience.md, offer.md |
| `examples-grid` | Use case cards | offer.md |
| `trust-strip` | Logo bar | testimonials.md |
| `interactive-explorer` | Clickable detail showcase | offer.md (features) |
| `integration-river` | Scrolling logo marquee | offer.md (integrations) |
| `footer` | Brand, contact, legal | brand info |

See [references/section-patterns.md](references/section-patterns.md) for detailed generation rules per section.

### Build Flows

**Full rebuild:** Read all reference files → regenerate `site-config.ts` → regenerate all components

**Add section:** Ask which section type → read relevant reference → generate component → add to `page.tsx`

**Edit section:** Read current component → read relevant reference → update content and copy

### Copy Guidelines

- Pull language directly from reference files. Don't invent marketing speak.
- Headlines from `offer.md` — the transformation, not the feature
- Pain points from `audience.md` — their words, not generic
- Testimonials from `testimonials.md` only — never fabricate
- CTAs from `offer.md` — specific action, not generic "Learn More"
- If site drives traffic to Skool, cross-reference `skool-surfaces.md` for messaging consistency between the landing page and the Skool about page

### Design Guidelines

Follow [references/frontend-design.md](references/frontend-design.md):

- No generic fonts (Inter, Roboto, Arial banned)
- Bold color commitment (not safe grays)
- Hero animation is mandatory (GSAP stagger reveal)
- CTA color is sacred — nothing else shares it
- Mobile-first responsive
- `prefers-reduced-motion` respected

### Checkpoint

> "Section generated. Want to preview it, add another section, or publish?"

---

## Mode: preview

Start local dev server for immediate feedback.

### Steps

1. Read config, get site repo path
2. Start dev server:

```bash
cd [site_repo] && pnpm dev
```

3. Server starts at `http://localhost:3000`
4. User reviews in browser, requests changes

This mode is iterative. User stays in preview until satisfied, then routes to `/site publish`.

### Checkpoint

> "Looking good? Make changes, or publish when ready."

---

## Mode: publish

Ship changes to production.

### Steps

1. Read config, navigate to site repo
2. Verify build passes:

```bash
cd [site_repo] && pnpm build
```

3. If build fails, fix before proceeding.
4. Check git status:

```bash
git status
git diff --stat
```

5. Stage, commit, and push:

```bash
git add -A
git commit -m "[update] Description of changes"
git push origin main
```

6. Netlify auto-deploys on push.

**Exit:**

> "Pushed to GitHub. Netlify will auto-deploy in ~1-2 minutes. Check status at https://app.netlify.com → [project-name]."

---

## Pipeline Position

The site is **infrastructure**, not recurring content. It's the destination that the content pipeline drives traffic to.

```
/think → reference files (the foundation)
     ↓
/site → landing page (conversion endpoint)
     ↓ drives traffic to:
/ads → paid traffic → landing page
/organic → social links → landing page
/newsletter → email CTA → landing page
```

When reference files change significantly (new offer, new pricing), consider rebuilding:

> "Your offer.md was updated since the site was last published. Want to run `/site build` to update your landing page?"

---

## Recovery from Compaction

If conversation compacted or context was lost:

1. **Re-invoke `/site`** to reload skill context
2. **Check config:**

```bash
cat ~/.mainbranch/sites.json 2>/dev/null
```

3. **Check site repo status:**

```bash
cd [site_repo] && git status && git log --oneline -5
```

4. **Detect what mode was active** from git history and file state
5. Resume from last completed step

---

## Scope

- **v1 is single-page only** — multi-page funnels are future
- **Not for:** wikis (`/wiki`), email templates (`/newsletter`), quick mockups without reference files

---

## References

**Minisite branch (static HTML, Cloudflare Pages, atom-driven):**

- [references/minisite-generation-system.md](references/minisite-generation-system.md) — Load-bearing system prompt for the `--one-shot` generation subagent. Hard constraints + soft brief + reference handling rules.
- [references/anti-patterns.md](references/anti-patterns.md) — What NOT to bake into prompts (over-prescription, hex-locked critique, "make it look like X", template tokens). Read before extending the system prompt.
- [references/naming-heuristic.md](references/naming-heuristic.md) — 8-step playbook for picking a brand-tier domain when the operator hits "I need a domain."
- [references/cloudflare-pages-link.md](references/cloudflare-pages-link.md) — Dashboard walkthrough for the one-time CF Pages Git connect (fallback path; default uses `wrangler pages project create`).

**Next.js branch (saas / high-ticket templates):**

- [references/frontend-design.md](references/frontend-design.md) — Typography, color, motion, anti-AI-slop standards
- [references/section-patterns.md](references/section-patterns.md) — How reference files map to page sections
- [references/deployment.md](references/deployment.md) — Netlify setup and troubleshooting
- [references/examples-and-troubleshooting.md](references/examples-and-troubleshooting.md) — Usage examples, common fixes
