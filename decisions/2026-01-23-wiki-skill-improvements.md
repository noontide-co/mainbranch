---
type: decision
date: 2026-01-23
status: proposed
linked_research: ["2026-01-23-wiki-skill-improvements-mining.md"]
github_issue: 39
---

# Decision: Wiki Skill Setup Improvements

## Context

GitHub Issue #39 identifies friction in the `/wiki setup` flow based on first-run testing. This decision captures the approved changes to address those issues.

## Research

See `research/2026-01-23-wiki-skill-improvements-mining.md` for full analysis of:
- Mined transcripts from contributor testing
- Devon's skill-creator guidelines
- Current skill architecture

## Decision

Implement Phase 1 and Phase 2 improvements to the wiki skill setup flow.

### Approved Changes

#### 1. Add Personalization Prompts to Setup

After template merge, prompt user:
- **Display name** (required) — Used in site header, meta tags, footer
- **Short name** (optional) — For mobile display, defaults to first name

Update these files with user's identity:
- `astro.config.mjs` — site title
- `src/components/Header.astro` — brand name
- `src/pages/index.astro` — meta author, structured data
- Any hardcoded "Devon Meadows" references

#### 2. Add Clean Install Option

After template merge, ask:
> "Include sample notes? (recommended for first-time wiki users) [Y/n]"

If user declines:
```bash
rm -f src/content/notes/*.md
rm -f src/content/updates/*.md
# Keep research/ empty by default
```

#### 3. Improve Cloudflare Pages Guidance

Update `references/cloudflare-pages-setup.md`:

**A) Add first-time GitHub app installation step:**
- Before "Connect GitHub", add explicit section for first-time users
- Steps: Install Cloudflare Pages GitHub app → Authorize → Select repositories
- Move this from troubleshooting footnote to primary flow

**B) Add Worker vs Page warning:**
- Add explicit **WARNING** callout about Worker vs Page confusion
- Clarify "GitHub tab" selection step (user saw GitHub in multiple places)
- Add troubleshooting entry: "Created a Worker instead of a Page? Delete and recreate."

Update SKILL.md setup mode:
- Add inline warning before CF dashboard step
- Reference the "Get started" link at bottom explicitly
- Note that first-time users need to install GitHub app

#### 4. Add Frontmatter Validation Note

In `add` mode, mention valid status values:
- Valid: `seed`, `growing`, `evergreen`
- Invalid: `draft` (causes build failure)

#### 5. Add `/wiki domain-setup` Mode

New mode for adding custom domain after initial setup:
- Reads existing config
- Guides user through Cloudflare custom domain setup
- Updates config and astro.config.mjs with new domain
- References existing cloudflare-pages-setup.md for dashboard steps

### Deferred

- **Avatar customization** — Adds complexity, users can manually edit
- **Deployment verification** — `wrangler` CLI dependency not worth it
- **Plausible analytics** — Comment out in template, separate concern

## Rationale

1. **Personalization prompts** — Users expect wiki to feel like theirs immediately
2. **Clean install** — Power users want blank slate; beginners benefit from examples (default: include)
3. **CF guidance** — The Worker vs Page confusion is the #1 setup failure
4. **Frontmatter validation** — Prevents cryptic Astro build errors

All changes align with skill-creator guidelines:
- Keep SKILL.md under 500 lines (currently 291, adding ~50)
- Focused improvements, not feature bloat
- Reference files handle detailed documentation

## Action Items

- [ ] Update `.claude/skills/wiki/SKILL.md` setup mode with personalization prompts
- [ ] Update `.claude/skills/wiki/SKILL.md` setup mode with clean install option
- [ ] Update `.claude/skills/wiki/SKILL.md` setup mode with CF warning
- [ ] Update `.claude/skills/wiki/SKILL.md` add mode with frontmatter note
- [x] Add `.claude/skills/wiki/SKILL.md` domain-setup mode
- [ ] Update `.claude/skills/wiki/references/cloudflare-pages-setup.md` with stronger warnings
- [x] Add note to CF reference about `/wiki domain-setup`
- [ ] Test full setup flow after changes

## Approval

Awaiting user approval before implementation.
