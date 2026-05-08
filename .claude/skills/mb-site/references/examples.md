# Examples

Usage examples for `/mb-site`. Load this only when examples would help the current operator step.

## Example 1: New Minisite For A Coaching Offer

**User:** "I need a landing page for my coaching business."

**Claude:** "/mb-site walks brief to site as one flow. Pick a shape:

1. Lander: 1 page, all-in-one. V1 stub; use minisite for now.
2. Minisite: ~4-6 pages, static HTML. V1 default. Best for paid-ad funnels and single-offer first deploys.
3. Website: full multi-section site with a build step. Bigger surface, blog/courses/etc.

Coaching usually fits minisite."

**User:** "Yeah, minisite."

**Claude:** Walks the minisite flow:

1. Spawns foreground research subagents in parallel for audience-language mining, competitor framing, and proof inventory. Records findings to `research/YYYY-MM-DD-*-claude-code.md`.
2. Drafts the brief into `decisions/YYYY-MM-DD-minisite-brief-coaching.md`.
3. Runs review gates in parallel. Surfaces findings.
4. Operator addresses or proceeds, then the brief is committed.
5. Runs setup: domain, DNS, GitHub repo, Cloudflare Pages, source links.
6. Asks for conversion goal: Stripe payment, lead form, appointment booking, or custom webhook. Captures URL to `<repo>/.mainbranch/conversion.json`.
7. Spawns 2 home-page concept subagents in parallel on localhost and surfaces URLs.
8. Operator picks one; picked concept is committed and pushed.
9. Builds out the rest of the pages with the picked concept as design seed.
10. Runs pre-publish review.
11. Pushes final updates.

**Exit:** "Live at https://your-domain.com. The home CTA links to your conversion endpoint. Business context is in `<business_repo>/core/`. Edit pages directly and `git push` to iterate; Cloudflare auto-deploys."

## Example 2: Iterating On Hero Copy

**User:** "/mb-site - update the hero on my existing minisite"

**Claude:** Reads `.mainbranch/repo.json` or legacy `.mainbranch/source.json`, the picked offer, and current site files.

**Claude:** "Your minisite is at `<site_repo>`. Reading offer.md, audience.md, and voice.md.

Current hero copy:

- Headline: 'Stop losing clients to scope creep.'
- Subhead: 'The project management system that keeps creative agencies profitable.'

Want me to regenerate from updated core files, or hand-edit a specific line?"

## Example 3: Publish Changes

**User:** "/mb-site publish"

**Claude:** Runs pre-publish review gates and checks git status.

**Claude:** "Pre-publish review surfaced:

- in-voice: copy matches voice.md.
- de-AI'd: no AI tells flagged.
- research-grounded: hero subhead does not match audience.md language verbatim; minor.

Address the warning, or proceed?"

**User:** "Proceed."

**Claude:** Commits and pushes.

**Exit:** "Pushed to GitHub. Cloudflare Pages will auto-deploy in roughly 1-2 minutes. Live at https://thelastbill.com."

## See Also

- [`minisite-build.md`](minisite-build.md) - minisite step router.
- [`minisite-iterate.md`](minisite-iterate.md) - targeted edits and regeneration.
- [`troubleshooting.md`](troubleshooting.md) - common fixes.
