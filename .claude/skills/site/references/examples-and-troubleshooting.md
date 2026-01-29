# Examples & Troubleshooting

Usage examples and common issue fixes for `/site`.

---

## Examples

### Example 1: New Site Setup

**User:** "I need a landing page for my coaching business"

**Claude:** "Let me set up a site for you. Which template fits better?

1. **SaaS / Product** — product-focused, demo-driven
2. **High-Ticket Services** — qualification-focused, trust-driven

Since you said coaching, I'd recommend #2."

**User:** "Yeah, high-ticket"

**Claude:** [Runs setup flow — scaffold, install, deploy, save config]

"Site deployed at https://your-site.netlify.app. It's the default template right now. Run `/site configure` to apply your brand, then `/site build` to generate sections from your reference files."

### Example 2: Build Hero From Reference

**User:** "/site build — update the hero"

**Claude:** [Reads offer.md, audience.md, voice.md]

"Based on your reference files:
- **Headline:** 'Stop losing clients to scope creep.' (from audience pain point)
- **Subhead:** 'The project management system that keeps creative agencies profitable.' (from offer mechanism)
- **CTA:** 'Start Free Trial' (from offer CTA)
- **Badge:** '200+ agencies, 98% retention' (from testimonials stats)

I'll generate the hero component with these. Want to adjust anything before I build?"

### Example 3: Publish Changes

**User:** "/site publish"

**Claude:** [Runs build, checks git status]

"Build passed. Changes:
- Updated hero headline and subhead
- Added credibility section with 3 testimonials
- New color palette (deep navy + coral accent)

Committing as: `[update] Hero copy and credibility section from reference files`"

[Commits and pushes]

"Pushed. Netlify will deploy in ~1-2 minutes."

---

## Troubleshooting

### "No site configured"

Run `/site setup` first. The skill needs `~/.mainbranch/sites.json` to know where your site repo is.

### Build failing

```bash
cd [site_repo] && node --version && pnpm install && pnpm build
```

Common causes: wrong Node version (need 18+), missing dependencies, TypeScript errors.

### Netlify deploy failing

Check Netlify dashboard → Deploys → click failed deploy → read build log. Common causes:
- Build command wrong (should be `pnpm build`)
- Publish directory wrong (should be `out` for static export)
- Node version mismatch (set `NODE_VERSION=20` in Netlify env vars)

### Styles not applying

Check `globals.css` for correct CSS variable names. Check `layout.tsx` for font imports. Run `pnpm dev` locally to debug.

### Static export errors

Verify `next.config.ts` has `output: "export"`. Remove any server-side features (API routes, dynamic server rendering).

### "Reference files not found"

Check `~/.mainbranch/sites.json` — the `business_repo` path must point to your business repo with `reference/core/` files.

### Template merge conflicts

During setup, if `git merge upstream/main` has conflicts, resolve them manually. The template should merge cleanly on first setup.

### Site looks generic / like AI

Read [frontend-design.md](frontend-design.md). Run `/site configure` to apply brand from voice.md. The anti-AI-slop standards exist specifically to prevent this.

---

## See Also

- [frontend-design.md](frontend-design.md) — Typography, color, motion, anti-AI-slop standards
- [section-patterns.md](section-patterns.md) — How reference files map to page sections
- [deployment.md](deployment.md) — Netlify setup and troubleshooting
