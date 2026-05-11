---
name: mb-site
description: "Triage and build any site shape -- lander (1 page), minisite (~4 pages), or full website -- and graduate between them. Routes to per-shape build flow, reads from business context files, deploys to Cloudflare Pages with git auto-deploy. Use when:
  (1) Operator says 'I want a site' / 'I want a lander' / 'spin up a one-pager'
  (2) Setting up a new site of any shape from offer + audience material
  (3) Updating / iterating on an existing site
  (4) Graduating a site to a new shape (lander -> minisite -> website -> website + CMS)
  (5) Previewing or publishing changes

  Triggered by: /mb-site, 'build a site', 'landing page', 'lander', 'minisite', 'website', 'I need a site', 'spin up a site', 'put this online', 'publish site', 'deploy site', 'update my site', 'graduate my site', 'add a CMS to my site'"
loops: [ship]
---

# Site

Pick a site shape, build it from business context, and ship it through a linked site repo. Cloudflare Pages with git auto-deploy is the default deploy path.

## Output destinations and operator vocabulary

Site/lander records that wrap a coordinated push (a launch, drop, or
challenge with a goal and timeline) live under `pushes/<YYYY-MM-DD-slug>/`
on the business-repo side; the wrapping record is `push.md` (`type: push`),
and the site record is typically `pushes/<YYYY-MM-DD-slug>/site.md`. Site
files themselves live in the linked site repo (Cloudflare Pages, etc.) and
are not duplicated in the business repo.

Reverse references from the site repo should use the role-neutral
`.mainbranch/repo.json` descriptor with engine push paths
(`linked.pushes: ["pushes/<...>/push.md"]`). Existing site repos may still use
`.mainbranch/source.json`; its `campaign_path` compatibility key should point
at the current push record when possible. Legacy repos that still have
`campaigns/` continue to resolve via compatibility read.

If `core/vocabulary.md` defines display words (e.g. `terms.push.singular:
launch`), speak the operator's word in conversation while still writing
engine files. If the repo still has legacy `campaigns/` records,
recommend `mb doctor` and `mb migrate campaigns --plan` before creating
new push work.

When creating `push.md`, include the validator-required frontmatter and fill
the values from repo truth or operator answers:

```yaml
---
type: push
slug: YYYY-MM-DD-slug
kind: launch
status: planned
health: unknown
goal: { metric: "", target: "", by: YYYY-MM-DD }
owner: ""
audience: ""
offer: core/offers/<offer>/offer.md
promise: ""
---
```

If the push or site record is tied to a bet, decision, research file,
playbook, or outcome, add the appropriate typed frontmatter link
(`linked_bets`, `linked_decisions`, `linked_research`,
`linked_playbooks`, `linked_outcomes`). Mirror frontmatter links in
`## Related links` with Markdown relative links, or preview
`mb doctor repair --plan` and ask before applying the repair. Use the
connection decision matrix in docs/business-connections.md before adding
typed links. Do not infer frontmatter links from body-only references.

## Re-Invoke Often

Say `/mb-site` again after compaction, context loss, or switching focus. It reloads skill context. Do it whenever the conversation feels stale.

## Start Every Run

1. Load [`references/pull-engine-updates.md`](references/pull-engine-updates.md) and run the standard update check.
2. Detect business repo mode vs site repo mode. Load [`references/site-repo-workflow.md`](references/site-repo-workflow.md) for repo boundaries, source links, and reverse site records.
3. When a business repo is known, run `mb status --json --peek` and use its `readiness`, `drift.items`, `integrations`, `measurement`, and `ranked_actions` facts before inventing setup, provider, or launch-readiness checks in prose.
4. Before any domain purchase, DNS, Cloudflare Pages project, custom-domain attach, or deploy work, run `mb connect doctor --json` from the business repo and check `provider:cloudflare`.
   - If Cloudflare is not `ready`, stop before dispatching site tools and present exactly three choices:
     - **connect now:** `printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata token_type=account --metadata account_id=... && mb connect test cloudflare`
     - **continue read-only:** availability checks, naming, brief, and research only; no buy, DNS, Pages, custom-domain, or deploy calls.
     - **skip for now:** record the blocker in the push/site notes and stage a follow-up task.
   - `cfat_` account tokens route automatically when `account_id` is present; keep `token_type=account` in examples because it is explicit and works on older `mb` versions. User API tokens remain supported as a fallback by omitting `token_type=account`.
5. Resolve the active offer and required business context with [`references/site-context.md`](references/site-context.md).
6. Ask what the operator is building, then load only the shape reference needed next.

## Operating Principles

Four behaviors `/mb-site` uses on every run:

1. **One flow: brief to site.** Do not route the operator to a separate brief skill and then ask them to come back. `/mb-site` walks research, brief draft, review, lock, concept variations, publish, and iteration as one flow.
2. **Foreground subagents.** Research, concept, and review subagents run in the foreground. Background subagents can appear to write files that do not persist.
3. **Parallel by default.** Multiple research questions, concepts, or review passes should run in parallel.
4. **Publish-first, then iterate.** Commit the rawest durable brief and rawest working concept before iterating. Git history is the memory across context clears.

When research subagents record findings, they follow the `/mb-think` research pattern: dated `research/YYYY-MM-DD-slug-claude-code.md` files with frontmatter and `linked_decisions: []`.
When the operator needs a broad researched brief before the site brief, run or
reuse `/mb-think --brief-format=grok-8`. Its eight categories feed the site
flow directly: offering, ICP, journey, competitive landscape, brand story,
technical requirements, assets, and metrics/constraints. Keep the `grok-8`
brief in `research/`; the locked site brief still belongs in `decisions/`.

## Invocation Mode

Use [`references/site-repo-workflow.md`](references/site-repo-workflow.md).

- **Business repo mode:** CWD has `core/` or legacy `reference/core/`. Say: "I'm reading business context here and will create or select a site repo."
- **Site repo mode:** CWD has `.mainbranch/repo.json` or legacy `.mainbranch/source.json`. Say: "I'm editing the site here and reading business context from the linked business repo."

Business repo mode plans, researches, drafts the brief, picks an offer, records push/site state, and creates or selects the site repo. Site repo mode edits code, reviews pages, previews, deploys, and runs `mb site check`.

## Triage

Ask the operator. Do not assume.

> **What are you doing?**
>
> **A. New site from scratch.** Pick a shape.
> - **Lander** (1 page, all-in-one). Use for focused one-off offer tests, retargeting, or paid-traffic landers. Load [`references/lander-build.md`](references/lander-build.md).
> - **Minisite** (~4-6 pages, static HTML). V1 default for paid-ad lander tests, single-offer first deploys, payment, lead-form, and booking funnels. Load [`references/minisite-build.md`](references/minisite-build.md).
> - **Website** (full site, usually with build step). Legacy Next.js templates work today. Load [`references/website-build.md`](references/website-build.md).
>
> **B. Iterating on an existing site.**
> - Editing pages, adding sections, updating copy: load the current shape build reference.
> - Publishing existing work: load the shape publish section or [`references/deployment.md`](references/deployment.md) for legacy Netlify.
>
> **C. Graduating to a different shape.**
> - Lander -> minisite, minisite -> website, website -> website + CMS. Load [`references/graduation.md`](references/graduation.md).

If the operator cannot articulate the shape, ask: "What goal are you trying to hit? Drive paid traffic to a sale, lead, or booking? Sell a course? Replace your current Squarespace?" Their answer maps to the shape.

## Modes

| Mode | What it does | Load |
|---|---|---|
| setup | First-run for a new site | Shape build ref, then setup step |
| build | Generate or edit content | Current shape build ref |
| preview | Local server/dev environment | Current shape preview step |
| publish | Stage, commit, push | Current shape publish step |
| check | Paid-traffic readiness | [`references/site-measurement.md`](references/site-measurement.md) |
| recover | Resume after compaction | [`references/site-recovery.md`](references/site-recovery.md) |

## Reference Map

**Repo + context**

- [`references/site-repo-workflow.md`](references/site-repo-workflow.md) - business repo mode vs site repo mode, source links, reverse records.
- [`references/site-context.md`](references/site-context.md) - prerequisites, active offer resolution, required `core/...` files, and section mapping.
- [`references/site-measurement.md`](references/site-measurement.md) - `mb site check` and paid-traffic readiness states.
- [`references/site-recovery.md`](references/site-recovery.md) - compaction recovery and scope boundaries.

**Shape flows**

- [`references/lander-build.md`](references/lander-build.md) - 1-page shape stub.
- [`references/minisite-build.md`](references/minisite-build.md) - minisite step router.
- [`references/website-build.md`](references/website-build.md) - legacy Next.js website flow.
- [`references/graduation.md`](references/graduation.md) - paths between shapes and CMS bolt-on.

**Minisite step detail**

- [`references/minisite-research.md`](references/minisite-research.md) - research subagents and persisted findings.
- [`references/minisite-brief.md`](references/minisite-brief.md) - brief draft, dial, archetype, schema, review, and lock.
- [`references/minisite-setup.md`](references/minisite-setup.md) - domain, repo, DNS, and Cloudflare Pages setup.
- [`references/minisite-conversion.md`](references/minisite-conversion.md) - conversion endpoint selection and `.mainbranch/conversion.json`.
- [`references/concept-variations.md`](references/concept-variations.md) - parallel home-page concepts.
- [`references/minisite-buildout.md`](references/minisite-buildout.md) - remaining pages and build validation.
- [`references/minisite-publish.md`](references/minisite-publish.md) - raw publish, pre-publish review, final push.
- [`references/minisite-iterate.md`](references/minisite-iterate.md) - post-build edits, regeneration, and graduation signals.

**Generation + design**

- [`references/minisite-generation-system.md`](references/minisite-generation-system.md) - load-bearing system prompt for minisite generation.
- [`references/lander-generation-system.md`](references/lander-generation-system.md) - one-page lander generation profile.
- [`references/review.md`](references/review.md) - dial-gated quality gates.
- [`references/anti-patterns.md`](references/anti-patterns.md) - AI tells and generation anti-patterns.
- [`references/archetypes.md`](references/archetypes.md) - 9-archetype picker. Load picked detail lazily.
- [`references/headline-formulas.md`](references/headline-formulas.md) - formulas grouped by frame.
- [`references/frontend-design.md`](references/frontend-design.md) - website typography, color, motion.
- [`references/section-patterns.md`](references/section-patterns.md) - website section catalog.

**Visibility, hosting, and checks**

- Site repos default to **private**. Before creating a public site repo,
  ask one visibility question — see the engine docs
  (repo-visibility-rubric) for the rule and exact wording.
- Cloudflare is the deploy rail. GitHub Pages is not part of normal Main
  Branch setup; the checks-and-review model in the engine docs explains
  how local `mb` checks, GitHub Actions, and branch protection layer.

**Setup, examples, help**

- [`references/naming-heuristic.md`](references/naming-heuristic.md) - domain naming playbook.
- [`references/cloudflare-pages-link.md`](references/cloudflare-pages-link.md) - Cloudflare Pages GitHub App handshake.
- [`references/deployment.md`](references/deployment.md) - legacy Netlify fallback.
- [`references/examples.md`](references/examples.md) - usage examples.
- [`references/troubleshooting.md`](references/troubleshooting.md) - common fixes.
