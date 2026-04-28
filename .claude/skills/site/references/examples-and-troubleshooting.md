# Examples & Troubleshooting

Usage examples and common issue fixes for `/site`.

---

## Examples

### Example 1: New minisite for a coaching offer

**User:** "I need a landing page for my coaching business."

**Claude:** "/site walks brief → site as one flow. Pick a shape:
1. **Lander** (1 page, all-in-one) — V1 stub; use minisite for now.
2. **Minisite** (~4–6 pages, static HTML) — V1 default. Best for paid-ad funnels and single-offer first deploys.
3. **Website** (full multi-section, build step) — bigger surface, blog/courses/etc.

Coaching usually fits #2."

**User:** "Yeah, minisite."

**Claude:** [Walks the 11-step flow:]
1. Spawns parallel research subagents (foreground) for audience-language mining + competitor framing + proof inventory. Records findings to `research/YYYY-MM-DD-*-claude-code.md` files.
2. Drafts the brief into `decisions/YYYY-MM-DD-minisite-brief-coaching.md`.
3. Runs review gates in parallel (research-grounded, in-voice, de-AI'd, framework-true). Surfaces findings.
4. Operator addresses or proceeds → `git commit` locks the brief.
5. Atom-chain setup: `domain.py check / buy`, `dns.py ensure`, `gh repo create`, `pages.py create-project --source github`, `pages.py set-domain`.
6. **Conversion endpoint pick.** "What's the conversion goal? Stripe payment, lead form, appointment booking, or custom webhook?" — operator picks; URL captured to `<repo>/.mainbranch/conversion.json`.
7. Spawns 2 home-page concept subagents in parallel on localhost (default `default_concepts: 2` from `~/.config/vip/local.yaml`). Surfaces URLs.
8. Operator picks one; picked concept committed and pushed → Cloudflare auto-deploys.
9. Build out the rest of the pages with the picked concept as design seed.
10. Pre-publish review.
11. Final push.

"Live at https://your-domain.com. The home CTA links to your conversion endpoint. Reference files are in `<business_repo>/`. Edit pages directly and `git push` to iterate — Cloudflare auto-deploys."

### Example 2: Iterating on hero copy

**User:** "/site — update the hero on my existing minisite"

**Claude:** [Reads sites.json + the picked offer's reference files]

"Your minisite is at /Users/.../thelastbill. Reading offer.md, audience.md, voice.md...

Current hero copy:
- Headline: 'Stop losing clients to scope creep.'
- Subhead: 'The project management system that keeps creative agencies profitable.'

Want me to regenerate from updated reference files, or hand-edit a specific line?"

### Example 3: Publish changes

**User:** "/site publish"

**Claude:** [Runs pre-publish review gates, checks git status]

"Pre-publish review surfaced:
- ✓ in-voice: copy matches voice.md
- ✓ de-AI'd: no AI tells flagged
- ⚠ research-grounded: hero subhead doesn't match audience.md language verbatim — minor

Address the warning, or proceed?"

**User:** "Proceed."

**Claude:** [Commits + pushes]

"Pushed to GitHub. Cloudflare Pages will auto-deploy in ~1-2 minutes. Live at https://thelastbill.com."

---

## Troubleshooting

### "No site configured"

Run `/site` and pick "new site from scratch." The skill walks setup, then writes `~/.mainbranch/sites.json` so future invocations know where your site repo is.

### Cloudflare Pages: `github_app_not_installed` error

The Cloudflare Pages GitHub App OAuth handshake hasn't been completed for your account. Walk through it once at https://dash.cloudflare.com → Workers & Pages → Create application → Continue with GitHub → connect any repo → close the tab. After that, `pages.py create-project --source github` works.

See [`cloudflare-pages-link.md`](cloudflare-pages-link.md) for the full walkthrough.

### `verify_live.py` fails

```bash
source ~/.config/vip/env.sh
python3 .claude/skills/site/scripts/verify_live.py
```

Expect 3/3 passed (Cloudflare scopes + zone lookup + domain-check CLI). If anything's red, route to `bash .claude/skills/site/scripts/setup_creds.sh`. Porkbun skipped is fine for the CF-registered path.

### Build failing (Website shape with build step)

```bash
cd [site_repo] && node --version && pnpm install && pnpm build
```

Common causes: wrong Node version (need 18+), missing dependencies, TypeScript errors. The minisite shape is static HTML and doesn't have a build step — if you're getting build errors on a minisite, something is wrong with the project repo configuration.

### Styles not applying

Minisite: each generation produces self-contained HTML/CSS, so the issue is usually a stale browser cache or a missing file (e.g., `og.svg` typo'd as `og.svg.png`). Hard-refresh the browser; check `_headers` if cache-control is being aggressive.

Website (Next.js): check `globals.css` for correct CSS variable names. Check `layout.tsx` for font imports. Run `pnpm dev` locally to debug.

### "Reference files not found"

Check `~/.mainbranch/sites.json` — the `business_repo` path must point to your business repo with `reference/core/` files (or `reference/offers/<active>/` for multi-offer setups).

### Site looks generic / like AI

Run `/site` again and trigger the review gates. The "de-AI'd" gate flags AI tells. The "in-voice" gate checks against `voice.md`. If voice.md is thin, that's the upstream fix — strengthen via `/think codify`.

For the Website (Next.js) shape: read [frontend-design.md](frontend-design.md) — the anti-AI-slop standards exist specifically to prevent generic output.

### Conversion endpoint URL not wired

Check `<site_repo>/.mainbranch/conversion.json`. The generation subagent reads `kind` + `url` + `render` and substitutes the URL into every CTA href. If the file is missing or has `https://CONVERSION-PLACEHOLDER`, run `/site` again and re-run the conversion-endpoint phase.

### Netlify (legacy)

If you're on a pre-V1 Next.js template still deploying to Netlify, see [`deployment.md`](deployment.md) for legacy fallback troubleshooting.

---

## See Also

- [SKILL.md](../SKILL.md) — operating principles, triage, modes
- [minisite-build.md](minisite-build.md) — full 11-step minisite flow
- [review.md](review.md) — quality-gate steps
- [concept-variations.md](concept-variations.md) — parallel-on-localhost concept pattern
- [cloudflare-pages-link.md](cloudflare-pages-link.md) — CF Pages GitHub App OAuth handshake
- [deployment.md](deployment.md) — Netlify deploy walkthrough (legacy fallback)
