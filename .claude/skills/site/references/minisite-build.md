# Minisite — Build Flow

The minisite shape: ~4–6 pages of static HTML, no build step, deployed to Cloudflare Pages with git auto-deploy. Designed fresh per offer by a generation subagent — no template inheritance.

V1 target. The default for paid-ad lander tests, single-offer first deploys, lead-form funnels, and conversion-gateway flows.

The canonical contract for what a minisite *is* (page list, per-page content, conversion endpoint, tracking, walkthrough UX) lives at `mb-vip/.claude/reference/minisite.md` (engine-side spec). This file is the **/site skill's implementation flow** — how the skill walks the operator through producing one.

---

## Flow at a glance

The minisite is built in one continuous flow. Brief and site are not separate skills — `/site` walks all of it:

```
1. Research      — parallel subagents in foreground, recording to /think research files
2. Brief draft   — composed from research + reference files
3. Review        — quality gates run in parallel; operator addresses or proceeds
4. Brief lock    — committed to git as the first durable artifact
5. Setup         — domain, DNS, repo, Pages (tool chain)
6. Conversion    — operator picks endpoint kind, URL captured to .mainbranch/conversion.json
7. Concepts      — N home-page variations on localhost (default 2), operator picks
8. Publish raw   — picked concept committed and pushed; Cloudflare auto-deploys
9. Build out     — rest of pages generated with picked concept as seed
10. Pre-publish review
11. Publish updates — git push, iterate
```

Every step that produces durable work commits to git before moving on. Git history is the durable memory; chat compaction can't be trusted.

---

## 1. Research

Spawn parallel research subagents (foreground only — see [`SKILL.md` Operating principles](../SKILL.md#operating-principles)) for the questions the brief needs answered.

Typical research questions:
- What do this offer's customers actually say? (audience-language mining from interviews, reviews, Skool posts)
- What's the best-performing competitor framing for this offer category?
- What proof is available — testimonials with permission, outcome data, founder credentials?
- What conversion-endpoint kind fits this offer (payment / lead / appointment)?

Each subagent records its findings to a dated `research/YYYY-MM-DD-<slug>-claude-code.md` file in the business repo, with frontmatter following the `/think` research pattern:

```yaml
---
type: research
date: YYYY-MM-DD
source: claude-code
topics: [audience-mining, competitor-framing, proof-inventory]
linked_decisions: []
status: complete
---
```

**Why this matters:** when the conversation compacts later, the operator (and the next session) can re-load the research from disk. Without persisted research, brief drafting is amnesia.

---

## 2. Brief draft

The brief is the locked source of truth for the site. It's composed from:
- Resolved `offer.md` (the framing, value prop, pricing, transformation)
- Resolved `audience.md` (pain frame, language, objections)
- `voice.md` (tone, register, named enemies, "never say")
- The research files just produced
- The conversion endpoint kind (operator's pick)

The skill drafts the brief into a single markdown artifact in the business repo: `decisions/YYYY-MM-DD-minisite-brief-<offer-slug>.md` (per the `/think` decision pattern).

### Step 2a — pick the dial

Three values: `convert`, `story`, `brand`.

- `convert` — sales-conversion priority. Full Seven Sweeps + Expert Panel scoring at review.
- `story` — archetype-faithful storytelling. Drops Prove-It and Zero-Risk sweeps.
- `brand` — voice and brand presence. Only Clarity / Voice / Heightened Emotion sweeps.

The dial decides review depth and influences the paired-imagery style. See [`review.md`](review.md) for the dial-gated sweeps.

### Step 2b — pick the archetype (optional but recommended)

Load [`archetypes.md`](archetypes.md) (the index, not all 9 detail files). Operator picks one archetype for the offer; optionally names a second for `audience_current_archetype` (what the audience is trapped in). The skill loads the picked detail file lazily.

The archetype unlocks: paired-imagery template, headline-formula matches, and the `do_not_state` list (conclusions the audience must reach themselves).

### Step 2c — pick headline formulas

Load [`headline-formulas.md`](headline-formulas.md). Pick 2–3 formulas that match the dial and archetype. The brief draft uses these as scaffolding, not final copy.

### Brief schema (v0.1)

```yaml
---
type: brief
date: YYYY-MM-DD
slug: <offer-slug>
status: proposed
dial: convert | story | brand          # required
archetype: wounded-healer              # optional but recommended
audience_current_archetype: victim     # optional
copy_framework_tag: Compact-Landing    # optional, see section-patterns.md
headline_formulas_picked:              # optional, suggested 2-3
  - "outcome-without-pain"
  - "for-audience-who-tried-X"
do_not_state:                          # required when archetype set
  - "Don't give up!"
  - "It's never too late."
four_forces:                           # optional (JTBD)
  push: ""
  pull: ""
  habit: ""
  anxiety: ""
voice_anchor_lines:
  use:
    - ""
    - ""
  avoid:
    - ""
---
```

The brief body still includes:

- **Headline + subhead** (≤2 lines, transformation-anchored, picks one of the chosen formulas)
- **Value prop** (3 short reasons OR one extended argument)
- **Mechanism summary** (for the how-it-works page)
- **Picked supporting pages** (which 2–4 from `proof / pricing / faq` or operator-added)
- **Conversion endpoint** (kind + URL or "to be wired in step 6")
- **Adjacency map** (per Hughes paired-imagery rule — each section's two images named, with a one-line do-not-state for the caption)

### Brief schema migration

Existing minisite briefs created before 2026-04-29 use the older schema (no `dial`, `archetype`, `do_not_state`). The skill tolerates them. New briefs created on or after 2026-04-29 must include the new fields. `mb validate` enforces the date-based check.

---

## 3. Review (pre-lock) — Seven Sweeps

Run [`review.md`](review.md) sweeps in parallel against the brief draft. Sweeps are **dial-gated**:

- `convert` dial — all 7 sweeps + Expert Panel scoring (every persona ≥ 7, panel avg ≥ 8)
- `story` dial — sweeps 1, 2, 3, 5, 6 (drops Prove-It and Zero-Risk)
- `brand` dial — sweeps 1, 2, 6 only (Clarity / Voice / Heightened Emotion)

Auxiliary gates always run:

- **De-AI'd** (against [`anti-patterns.md`](anti-patterns.md) — em-dash rule, banned phrases, overused-verb cluster)
- **Framework-true** (if `copy_framework_tag` set, structure honors it)
- **Archetype-fidelity** (no `do_not_state` line written as a headline)

Synthesize findings; surface to operator. They address or proceed.

---

## 4. Brief lock

Once review is addressed (or skipped with operator awareness), commit the brief to the business repo:

```bash
cd <business_repo>
git add decisions/YYYY-MM-DD-minisite-brief-<slug>.md
git commit -m "[lock] minisite brief — <slug>"
git push
```

The brief is now durable. Move to setup.

---

## 5. Setup (tool chain)

Same as before — infrastructure provisioning. This step doesn't touch the brief; it's purely about getting the empty deploy target ready.

**5a. Name + project repo.** Ask the operator:
- Site name (e.g., `thelastbill`). Becomes the Pages project name.
- Project repo location (default: sibling of vip — `~/Documents/GitHub/<name>` for solo work, `~/Documents/GitHub/noontide-sites/<name>` for Noontide work). Empty repo, no template merge.
- Apex domain. If they don't have one, route to [`naming-heuristic.md`](naming-heuristic.md).

**5b. Atom-chain prerequisites.** Confirm credentials are in place:
```bash
source ~/.config/vip/env.sh
python3 .claude/skills/site/scripts/verify_live.py
```
Expect 3/3 passed (Cloudflare scopes + zone lookup + domain-check CLI).

If anything's red, route to `bash .claude/skills/site/scripts/setup_creds.sh`, then re-run.

**5c. Domain — buy-new vs. existing.** Ask:
- "Already own the domain?" → skip to 5d with the domain name.
- "Need to buy?" → run `python3 .claude/skills/site/scripts/domain.py check <name> --tlds .com,.co,.io` first to confirm availability + TLD support. For API-supported TLDs and after explicit operator Y on price, proceed with `domain.py buy <name>`. For dashboard-only TLDs, fall back to https://dash.cloudflare.com/registrar.

**5d. DNS ensure.** Once the domain is owned:
```bash
python3 .claude/skills/site/scripts/dns.py ensure <domain> --registrar cloudflare --skip-propagation-poll
```

**5e. GitHub repo + initial scaffold push.**
```bash
gh repo create <owner>/<name> --public --add-readme
git clone https://github.com/<owner>/<name>.git ~/Documents/GitHub/<name>
cd ~/Documents/GitHub/<name>
echo '<!doctype html><title><name></title><h1>soon</h1>' > index.html
git add -A && git commit -m "[add] placeholder" && git push
```

**5f. Cloudflare Pages project (git-connected).**
```bash
python3 .claude/skills/site/scripts/pages.py create-project <name> --repo-owner <owner> --repo-name <repo> --branch main
```
If you hit `github_app_not_installed`, the envelope's `suggestion` field walks through the dashboard handshake step; see [`cloudflare-pages-link.md`](cloudflare-pages-link.md).

**5g. Custom domain attach + DNS verification.**
```bash
python3 .claude/skills/site/scripts/pages.py set-domain <name> <domain> --timeout-seconds 300
```
~3-4 min total. Live-tested end-to-end in PR #97.

**5h. Save config.** Write or extend `~/.mainbranch/sites.json`:
```json
{
  "name": "<name>",
  "site_repo": "/absolute/path/to/repo",
  "business_repo": "/absolute/path/to/business-repo",
  "shape": "minisite",
  "hosting": "cloudflare",
  "domain": "<full apex>"
}
```

---

## 6. Conversion endpoint

Operator picks the kind (per the [Conversion endpoint](minisite.md#conversion-endpoint) section of the engine spec):

- **Stripe payment page** → run `stripe.py create-payment-link <offer-slug> --amount <cents> --success-url https://<domain>/start/thanks/`. Capture `payment_link.url` from the envelope.
- **Lead form** → ask: "Where does form data go?" — capture provider + URL (Tally / Typeform / Google Form / native + Formspree / custom backend).
- **Appointment booking** → ask for the booking-link URL (Cal.com / Calendly / SavvyCal).
- **Custom webhook** → ask for the URL.

Write the picked endpoint to `<site_repo>/.mainbranch/conversion.json`. The shape is the same for all kinds; the `metadata` block varies. Examples:

```json
// Stripe payment page
{
  "kind": "stripe_payment_page",
  "url": "https://buy.stripe.com/abc123",
  "render": "link_out",
  "metadata": {
    "amount_usd": 100,
    "currency": "usd",
    "stripe_product_id": "prod_xyz",
    "stripe_payment_link_id": "plink_abc",
    "payment_kind": "deposit"
  }
}

// Lead form
{
  "kind": "lead_form",
  "url": "https://tally.so/r/abc123",
  "render": "link_out",
  "metadata": { "provider": "tally" }
}

// Appointment booking
{
  "kind": "appointment_booking",
  "url": "https://cal.com/devon/intro",
  "render": "link_out",
  "metadata": { "provider": "cal.com" }
}

// Custom webhook
{
  "kind": "custom_webhook",
  "url": "https://operator-domain.com/leads",
  "render": "form_post",
  "metadata": {}
}
```

The generation subagent in step 9 reads `kind` + `render` + `url` and renders the home CTA accordingly (link-out button, embedded form, embedded booking iframe, or form-POST handler).

---

## 7. Concept variations (home page only)

Per [`concept-variations.md`](concept-variations.md): spawn N home-page concepts in parallel (default 2, operator-configurable in `~/.config/vip/local.yaml`).

Each concept gets:
- Locked brief from step 4
- `offer.md`, `audience.md`, `voice.md`, `soul.md`
- Conversion endpoint URL from step 6
- A short "lean" instruction differentiating this concept from the others

Each writes to `<site_repo>/.mainbranch/concepts/concept-<n>/`. The skill starts a localhost preview for each, surfaces URLs to operator, waits for pick.

Operator picks → picked files move to project root, others discarded (optionally archived to `.mainbranch/concepts/discarded/`).

---

## 8. Publish raw

The picked home page is the rawest working version. Commit + push immediately:

```bash
cd <site_repo>
git add -A
git commit -m "[add] picked home concept — <slug>"
git push
```

Cloudflare auto-deploys (per the git-connected Pages project from step 5f). The site is now live with one page. The rest will follow.

---

## 9. Build out remaining pages

Spawn the minisite generation subagent (foreground) with the picked concept as the design seed. The subagent generates the rest of the pages (`how-it-works/`, picked supporting pages, `privacy/`, `terms/`, `start/thanks/`) consistent with the picked concept's design language.

Inputs to the build subagent:
- Picked `index.html` + `styles.css` from step 8 (the design seed)
- Locked brief from step 4
- Conversion endpoint URL from step 6
- `offer.md`, `audience.md`, `voice.md`, optional `soul.md`
- The system prompt from [`minisite-generation-system.md`](minisite-generation-system.md)

Anti-patterns to avoid in the user message: see [`anti-patterns.md`](anti-patterns.md).

**Validation after build-out:**

- **Required files present:** `index.html`, `how-it-works/index.html`, two more page directories with `index.html`, `privacy/index.html`, `terms/index.html`, `start/thanks/index.html`, `_headers`, `_redirects`, `robots.txt`, `sitemap.xml`, `og.svg`, `favicon.svg`. Each missing file = a fix request to the subagent.
- **Footer presence:** `grep -L "Noontide Collective LLC" *.html **/*.html` should return nothing (or only files where `offer.md` declared a different parent entity).
- **OG render:** `python3 .claude/skills/site/scripts/og_render.py render <repo>/og.svg <repo>/og.png`. Envelope must return `status: ok` with `width: 1200, height: 630`.
- **Conversion URL substitution:** every CTA href on every page should match the URL in `<repo>/.mainbranch/conversion.json` (no `https://CONVERSION-PLACEHOLDER` left).

---

## 10. Pre-publish review

Run [`review.md`](review.md) gates in parallel against the full site copy:
- **in-voice**, **de-AI'd**, **framework-true** (research-grounded only re-runs if reference files changed since brief lock).
- Plus operator-defined gates from `<business_repo>/reference/review/*.md` if any.

Synthesize findings; surface to operator. They address or proceed.

---

## 11. Publish updates + iterate

```bash
cd <site_repo>
git add -A
git commit -m "[add] minisite build-out — <slug>"
git push
```

Cloudflare auto-deploys. Verify `https://<domain>/` returns 200 and shows the new pages.

For targeted edits going forward, edit files in the project repo directly and `git push` — Cloudflare auto-deploys.

---

## Variance test (acceptance criterion)

Running the full flow twice on the same offer must produce visually distinct sites — different palettes, hero artifacts, page choices, microcopy. Concept variations enforce this at the home-page level; build-out inherits the picked concept's seed but still has aesthetic latitude in the supporting pages.

If two full runs produce identical output, the brief was over-specified or the concept-variations soft-brief was too prescriptive — re-read [`anti-patterns.md`](anti-patterns.md).

---

## What's NOT in the minisite shape

- No `pnpm install`, no `pnpm build`. Static HTML only.
- No `site-config.ts` pattern. Each minisite generates its own one-off structure.
- No section-types menu (the Next.js section catalog from `website-build.md` doesn't apply).
- No Anthropic API key. The generation runs inside the operator's Claude Code session via the `Agent` tool.
- No multi-endpoint conversion (one minisite, one conversion endpoint — graduate to website shape if you need both).

---

## Iterating after first build

For targeted edits, edit the file in the project repo directly and `git push`. Cloudflare auto-deploys.

For broader regeneration (new brief, new concept), re-run `/site` — it walks the same flow and detects existing state in the project repo.

When the offer pulls more traffic and the minisite needs more pages or content depth, that's the **graduation signal**. See [`graduation.md`](graduation.md) for paths from minisite → website (per-offer full site) or minisite → Website + CMS (Sanity, Contentful, etc.).

---

## Cross-references

- [`SKILL.md`](../SKILL.md) — Operating principles (foreground-only, publish-first, parallel-by-default)
- [`review.md`](review.md) — quality gates run in steps 3 and 10
- [`concept-variations.md`](concept-variations.md) — parallel concept generation in step 7
- [`minisite-generation-system.md`](minisite-generation-system.md) — system prompt for the build-out subagent in step 9
- [`anti-patterns.md`](anti-patterns.md) — what NOT to bake into prompts
- [`naming-heuristic.md`](naming-heuristic.md) — domain naming playbook (used in step 5a if needed)
- [`cloudflare-pages-link.md`](cloudflare-pages-link.md) — CF Pages GitHub App handshake (used in step 5f if needed)
- [`graduation.md`](graduation.md) — when to move beyond minisite shape
- Engine spec: `mb-vip/.claude/reference/minisite.md` — the contract this flow implements
- `/think` — research and decision recording patterns this flow follows
