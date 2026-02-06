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
# Pull vip updates (checks common locations)
for d in . ~/Documents/GitHub/vip ~/vip; do [ -d "$d/.claude/skills" ] && git -C "$d" pull origin main 2>/dev/null && break; done || true
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

### Step 1: Choose Template

Present options:

> **Which template fits your business?**
>
> 1. **SaaS / Product** — Hero → Demo → Value Prop → Workflow → Examples → Integrations → CTA
>    Best for: software, e-commerce, product companies
>
> 2. **High-Ticket Services** — Hero → Solution → Pain → Process → Competitive → Objections → Proof → Qualification → FAQ → CTA
>    Best for: coaching, consulting, agencies, $3k+ services

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

- [references/frontend-design.md](references/frontend-design.md) — Typography, color, motion, anti-AI-slop standards
- [references/section-patterns.md](references/section-patterns.md) — How reference files map to page sections
- [references/deployment.md](references/deployment.md) — Netlify setup and troubleshooting
- [references/examples-and-troubleshooting.md](references/examples-and-troubleshooting.md) — Usage examples, common fixes
