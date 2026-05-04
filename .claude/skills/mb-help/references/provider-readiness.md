# Provider Readiness

Provider setup should feel like business onboarding, not developer config. Start
with the job the operator is trying to do, then use `mb` facts to name what is
ready or missing.

## First Commands

Run from the business repo:

```bash
mb status --json --peek
mb connect plan
mb connect doctor --json
```

Use `mb status --json --peek` first when the operator asks "what should I do
next?" Use `mb connect plan` when the question is "what should I connect?" Use
`mb connect doctor --json` when something looks broken.

## Numbered Choice Pattern

When a provider is missing, give exactly two or three numbered choices:

> "This action needs [business capability].
>
> 1. Set up [provider] now — `[exact command from mb]`
> 2. Skip for this session — [specific limitation]
> 3. Tell me why — `mb educational provider-readiness`"

Do not ask for tokens in prose unless the CLI repair command already says which
provider is missing. Never ask the operator to commit tokens or paste them into
GitHub.

## Decision Tree

1. **GitHub** - tasks, proposals, reviews, and shipped history.
   - Use when: issue drafts, PRs, review, team visibility, daily task tracking.
   - Check/fix: `mb connect doctor --json`.

2. **Cloudflare** - sites, DNS, Pages, and future Workers.
   - Use when: publish a landing page, attach a domain, or deploy a site.
   - Check/fix: `mb connect status --all --json`.

3. **Google / Workspace** - Drive, Docs, Sheets, Slides, and source material.
   - Use when: a workflow needs existing Google files.
   - Check/fix: `mb connect status --all --json`.

4. **Meta Ads** - ad accounts, campaigns, pixels, and future performance facts.
   - Use when: paid-ad generation, review, or learning needs account context.
   - Check/fix: `mb connect status --all --json`.

5. **Apify** - optional research sidecar for scraping, YouTube, Instagram, and web mining.
   - Use when: research or organic workflows need structured external data.
   - Check/fix: `mb connect status --all --json`.

## Support Boundary

Readiness means `mb` can see local metadata and the safest available credential
check has the reported state. It does not mean every future provider workflow is
implemented. Claude Code is still the only supported runtime today.
