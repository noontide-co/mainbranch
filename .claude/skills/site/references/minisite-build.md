# Minisite — Build Flow

The minisite shape: ~4 pages of static HTML, no build step, deployed to Cloudflare Pages with git auto-deploy. Designed fresh per offer by a generation subagent — no template inheritance.

V1 target. The default for paid-ad lander tests, single-offer first deploys, and deposit-gateway flows.

The canonical contract for what a minisite *is* (page list, per-page content, post-payment flow, tracking, walkthrough UX) lives at `mb-vip/.claude/reference/minisite.md` (engine-side spec). This file is the **/site skill's implementation flow** — how the skill walks the operator through producing one.

---

## setup (minisite)

**1. Name + project repo.** Ask the operator:
- Site name (e.g., `thelastbill`). Becomes the Pages project name.
- Project repo location (default: sibling of vip — `~/Documents/GitHub/<name>` for solo work, `~/Documents/GitHub/noontide-sites/<name>` for Noontide work). Empty repo, no template merge.
- Apex domain. If they don't have one, route to [`naming-heuristic.md`](naming-heuristic.md) — an 8-step playbook for generating + validating brand-tier names.

**2. Atom-chain prerequisites.** Confirm the credentials are in place:
```bash
source ~/.config/vip/env.sh
python3 .claude/skills/site/scripts/verify_live.py
```
Expect 3/3 passed (Cloudflare scopes + zone lookup + domain-check CLI). Porkbun skipped is fine for the CF-registered path.

If anything's red, route the operator to `bash .claude/skills/site/scripts/setup_creds.sh` to provision Cloudflare credentials, then re-run.

**3. Domain — buy-new vs. existing.** Ask:
- "Already own the domain?" → skip to step 4 with the domain name.
- "Need to buy?" → run `python3 .claude/skills/site/scripts/domain.py check <name> --tlds .com,.co,.io` first to confirm availability + TLD support. If `extension_not_supported_via_api`, fall back to the Cloudflare dashboard at https://dash.cloudflare.com/registrar (confirm the right account before purchase). For API-supported TLDs and after explicit operator Y on price, proceed with `domain.py buy <name>` once that subcommand wires the live API call.

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

**6. Cloudflare Pages project (git-connected).** The atom creates the project with `source.type=github` so every push auto-deploys:
```bash
python3 .claude/skills/site/scripts/pages.py create-project <name> --repo-owner <owner> --repo-name <repo> --branch main
```
Live-tested in PR #102. If you hit `github_app_not_installed`, the envelope's `suggestion` field walks through the dashboard handshake step (Compute → Workers & Pages → Create application → Continue with GitHub → connect any repo → close the tab); see [`cloudflare-pages-link.md`](cloudflare-pages-link.md) for the full path.

**7. Custom domain attach + DNS verification.** Run:
```bash
python3 .claude/skills/site/scripts/pages.py set-domain <name> <domain> --timeout-seconds 300
```
The atom attaches the domain, creates the CNAME record in the zone (the step the dashboard hides), and polls until SSL is active. Expect ~3-4 min total. Live-tested end-to-end in PR #97.

**8. Save config.** Write or extend `~/.mainbranch/sites.json`:
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

**Exit:**
> "Minisite ready at https://<domain>. Placeholder deployed; run `/site build --one-shot` to generate the actual minisite from your offer + audience specs."

---

## build --one-shot (minisite)

The load-bearing mode — where Claude (the operator's running session) spawns a subagent that generates fresh HTML/CSS/SVG for this offer. No template inheritance. No placeholder tokens. No Anthropic SDK call. The subagent is a Claude Code subagent, spawned via the `Agent` tool.

**1. Resolve offer context.** Use the offer-context resolution from `SKILL.md`. At minimum: `offer.md` + `audience.md` paths + the active offer slug.

**2. Load the system prompt.** Read [`minisite-generation-system.md`](minisite-generation-system.md) verbatim. This is the load-bearing artifact — the full hard-constraints + soft-brief framing for the generation subagent. Pass it as the subagent's system prompt unmodified.

**3. Build the user message.** Compose:
- Resolved `offer.md` content
- Resolved `audience.md` content
- Optional `voice.md` snippets (anchor phrases, named enemies, "never say" list)
- Reference URLs — defaults: `https://howdy.md`, `https://thelastbill.com`. Operator can pass `--reference URL` to add or replace.
- Project repo absolute path (where the subagent writes via `Write`)
- Soft directive: *"Generate fresh HTML/CSS/SVG for this offer. The reference URLs are taste anchors, not templates — read them for polish level, then design something that fits **this** offer. Surprise me."*

Anti-patterns to avoid in your own framing of the user message: see [`anti-patterns.md`](anti-patterns.md). The big ones: don't lock typography or colors, don't enumerate available sections, don't ask the subagent to "make it look like the references," don't suppress variance.

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

Operator runs `git add -A && git commit && git push`. Cloudflare auto-deploys (per the git-connected Pages project from step 6 of setup).

**Variance test (acceptance criterion):** Running `/site build --one-shot` twice on the same offer must produce visually different output. If it doesn't, the soft brief was too prescriptive — re-read [`anti-patterns.md`](anti-patterns.md).

---

## What's NOT in the minisite shape

- No `pnpm install`, no `pnpm build`. Static HTML only.
- No `site-config.ts` pattern. Each minisite generates its own one-off structure.
- No section-types menu (the Next.js section catalog from `website-build.md` doesn't apply).
- No `configure` mode separate from `build --one-shot` — the generation subagent reads voice.md / offer.md directly and bakes the brand decisions into the output.
- No Anthropic API key. No `pages_gen.py` Python wrapper. The generation runs inside the operator's Claude Code session via the `Agent` tool.

---

## Iterating after first build

Re-running `/site build --one-shot` produces a fresh design (variance is the feature). For targeted edits, edit the file in the project repo directly and `git push` — Cloudflare auto-deploys.

When the offer pulls more traffic and the minisite needs more pages or content depth, that's the **graduation signal**. See [`graduation.md`](graduation.md) for paths from minisite → website (per-offer full site) or minisite → Website + CMS (Sanity, Contentful, etc.).
