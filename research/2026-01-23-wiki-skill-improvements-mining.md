---
type: research
date: 2026-01-23
source: mining
status: complete
linked_decisions: ["2026-01-23-wiki-skill-improvements.md"]
---

# Wiki Skill Improvements Research

Mining first-run testing feedback and contributor guidance to identify wiki skill improvements.

## Sources Mined

1. **GitHub Issue #39** — Detailed problem statement from @joedef after first-run testing
2. **Devon's contributor guidance transcript** — How to approach skill modifications using /think and skill-creator guidelines
3. **Joe's test drive transcript** — 1-hour raw session showing setup friction points in real time

---

## Key Findings

### 1. GitHub → Cloudflare Connection Unclear

**Problem:** Two distinct issues caused setup friction:

**A) First-time GitHub app installation not called out**

User had never connected Cloudflare to GitHub before. The setup assumes the Cloudflare Pages GitHub app is already installed, but first-time users must:
1. Install the Cloudflare Pages GitHub app on their GitHub account
2. Authorize it
3. Select which repositories it can access (all or specific)

**Current state:** The reference buries this as a troubleshooting footnote: "*Repo not showing? Click 'configure repository access'*" — but this is a REQUIRED first-time step, not an edge case.

**B) Worker vs Page confusion**

User accidentally created a Worker instead of a Page because Cloudflare dashboard defaults to Workers.

**Evidence from Joe's transcript:**
> "Missing Entry Point to Worker Script or to Assets Directory. This means that CloudFlare created a Workers Project instead of a Pages Project. It's a common mistake, the UI defaults to Workers."

**Current state:** The `cloudflare-pages-setup.md` reference does mention this but it's easy to miss during setup.

**Proposed fix:**
- Add explicit "First time? Install the Cloudflare Pages GitHub app" step BEFORE selecting repo
- Add explicit warning about Worker vs Page, make the distinction impossible to miss

---

### 2. Branding Not Customized During Setup

**Problem:** Site deploys with Devon's name and likeness. User had to manually request changes.

**Evidence from Joe's transcript:**
> "On deployment, the site was still customized with Devin's name and likeness had to manually request, request changes for rebrand"
> "not super clear to me right now that I'm working on my local repository... it has your name as the site"
> "maybe this is part of, the setup process. You know, let them, let them customize. Or that could be another skill, wiki, customize."

**Current state:** Setup flow does NOT prompt for user identity. Template ships with Devon's branding.

**Proposed fix:** Add personalization prompts during setup — display name, short name for mobile, then auto-update:
- `src/components/Header.astro` — brand name, avatar alt text
- `src/pages/index.astro` — meta tags, structured data, author
- `src/pages/notes/[...slug].astro` — author meta
- `src/pages/research/[...slug].astro` — footer attribution
- `src/pages/updates/*.astro` — site name
- `public/robots.txt` — domain reference
- `astro.config.mjs` — site URL

---

### 3. No Clean Installation Option

**Problem:** Sample notes included by default with no option to start fresh.

**Evidence from Joe's transcript:**
> "It also installed with a good amount of existing notes and pages, which were very interesting. But I would also like the option to have a clean installation."

**Current state:** Template merges all sample content automatically.

**Proposed fix:** After merging template, ask:
> "Include sample notes? (recommended for first-time users) [Y/n]"

If declined:
```bash
rm -f src/content/notes/*.md
rm -f src/content/updates/*.md
```

---

### 4. Deployment Status Unclear

**Problem:** Skill says "live" before Cloudflare actually finishes deploying.

**Evidence from Joe's transcript:**
> "it says it's live, right? But it's not live yet, right? It's just kicking off the job to deploy"
> "Definitely we need to ping, I think, CloudFlare. If, if there is a deployment problem, we need to know about it. And we shouldn't say that it's live, like, until it's actually live."

**Current state:** `publish` mode says "Cloudflare Pages will auto-deploy in ~90 seconds" without verification.

**Proposed fix:** Either:
- A) Add caveat: "Deployment triggered. Check Cloudflare dashboard if issues."
- B) Add optional verification step using `wrangler` CLI (more complex)

Given skill-creator guidelines favoring simplicity, option A is preferred.

---

### 5. Frontmatter Validation Gap

**Problem:** Joe's note had `draft` in frontmatter where it needed `seed` — caused Cloudflare build failure.

**Evidence from Joe's transcript:**
> "deployment failed. invalid content entry... invalid enum value and it has to do with I guess this atomic note... Seed versus draft."

**Current state:** `add` mode doesn't validate frontmatter values against Astro collection schema.

**Proposed fix:** Add validation note to `add` mode:
- Valid status values: `seed`, `growing`, `evergreen`
- Invalid: `draft` (common mistake)

---

### 6. Windows Path Bugs

**Evidence from Joe's transcript:**
> "Windows Path Bug. Alright, so just so the transcript catches this, we want to open an issue that includes, uh, but there's a Windows Path Bug in Astro.Backlinks."

**Assessment:** This is a template/Astro issue, not a skill issue. Should be tracked separately in commune-wiki repo.

---

## Skill-Creator Guidelines to Apply

From Devon's contributor guidance:
> "make sure to invoke the official Anthropic skill creator skill prior to adding to the skills. Because it, it defines, like, how skills should be, and it has all these suggestions about, like, how, how long they are, how to make reference files, what to put where, router stuff, brevity."

Key guidelines from research:

1. **Brevity under 500 lines** — Current SKILL.md is 291 lines, room for additions
2. **Light-touch integration** — Don't bloat; keep changes focused
3. **Natural language invocation** — Already good
4. **Progressive context loading** — Reference files already separated
5. **Recovery patterns** — Consider adding if setup fails mid-way

---

## Implementation Assessment

### Phase 1: Quick Wins (High Priority)

| Change | Effort | Impact |
|--------|--------|--------|
| Add Workers vs Pages warning to setup | Low | High |
| Add personalization prompts to setup | Medium | High |
| Update CF setup reference with clearer steps | Low | Medium |
| Add frontmatter validation note to `add` mode | Low | Low |

### Phase 2: Clean Install (Medium Priority)

| Change | Effort | Impact |
|--------|--------|--------|
| Add sample notes prompt | Low | Medium |
| Implement content deletion when declined | Low | Medium |

### Phase 3: Polish (Low Priority)

| Change | Effort | Impact |
|--------|--------|--------|
| Avatar customization option | Medium | Low |
| Deployment verification | High | Low |
| Handle Plausible analytics domain | Low | Low |

---

## Proposed Updated Setup Flow

1. Check prerequisites (gh auth, pnpm)
2. Ask: Repo name? Location?
3. Create GitHub repo and clone
4. Add upstream, fetch, merge template
5. **NEW:** Ask: Include sample notes? [Y/n]
6. **NEW:** Ask: Your display name? Short name (mobile)?
7. **NEW:** Update branding in template files
8. Ask: Domain type? (pages.dev or custom)
9. Update astro.config.mjs with site URL
10. pnpm install && pnpm build (verify locally)
11. **IMPROVED:** Guide through CF Pages with stronger Worker vs Page warnings
12. Save config
13. First push to trigger deploy

---

## Files to Modify

| File | Changes |
|------|---------|
| `.claude/skills/wiki/SKILL.md` | Add personalization prompts, clean install option, frontmatter validation |
| `.claude/skills/wiki/references/cloudflare-pages-setup.md` | Strengthen Workers vs Pages warning, clarify GitHub tab selection |

---

## Open Questions

1. **Avatar handling** — Should we prompt for avatar upload/URL, or leave for manual customization?
   - **Recommendation:** Skip for now. Add `/wiki customize` skill later if demand exists.

2. **Plausible analytics** — Template hardcodes `devonmeadows.com`. Remove or prompt?
   - **Recommendation:** Comment out by default, add note to customize manually.

3. **Deployment verification** — Should we use `wrangler pages deployment list` to verify?
   - **Recommendation:** No, adds complexity. Just improve messaging.

---

## Summary

The wiki skill works but has setup friction that can be resolved through:
1. Better Cloudflare guidance (Worker vs Page warning)
2. Personalization prompts (display name, clean install option)
3. Minor validation improvements (frontmatter status values)

Changes align with skill-creator guidelines: focused, brief additions that improve UX without bloating the skill.
