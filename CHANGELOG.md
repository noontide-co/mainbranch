# Changelog

All notable changes to Main Branch (`mainbranch` / `mb`) will be documented in
this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The release tag scheme is `oe-vMAJOR.MINOR.PATCH` ("oe" = open engine) — the
PyPI distribution `mainbranch` tracks the same version sequence.

## [Unreleased]

### Added

- Accepted decision
  `decisions/2026-05-11-mb-books-foundation.md` choosing **hledger** as
  the bookkeeping engine for `mb books`. The hledger journal is the
  only authoritative ledger; CSV/SQLite stay as import staging,
  snapshots, caches, or report outputs, not the books. hledger is
  optional for base `mb` installs (the base CLI must run without it)
  but is the chosen engine when using `mb books`. `mb` core never
  imports hledger libraries; deeper validation shells out to
  `hledger ... -O json` and reads structured output, never scrapes
  terminal text. Defined a **private books vault** storage model with
  three modes: solo local (default — real books live at
  `.mb/private/books/` with their own local git history and no
  GitHub remote), team private repo (separate restricted-access repo
  for finance/admin users with PR review), and advanced
  encrypted/off-platform vault. Operator-facing language is "private
  books vault," not `.gitignore`; `mb` creates and enforces the
  ignore rules. The team-visible business repo commits only safe
  metadata (`core/finance/books.md`,
  `core/finance/chart-of-accounts.md`, optional
  `core/finance/import-rules/` and `docs/reports/finance/` when free
  of Class B data). A GitHub-as-backup warning is required whenever
  real books are tracked on GitHub. Named the first surface
  `mb books check` plus sibling `mb books status` and `mb books doctor`
  shapes for the follow-up implementation. Added `docs/books.md`,
  `docs/reports/2026-05-11-hledger-vs-beancount-fit.md` (primary-source
  comparison; Beancount v3, Ledger CLI, and CSV/SQLite considered and
  not chosen), and `docs/examples/books/acme-fixture.journal` plus
  sample policy/chart-of-accounts files. Existing Beancount-flavoured
  surfaces (`mb connect` provider, educational doc, ethos /
  system-architecture / dependency-choices / operator-loops /
  beginner-setup copy, gitignore template — adding `*.journal`,
  `*.hledger`, and `.mb/private/`) are named in the decision as
  migration follow-ups so the foundation PR does not also become a
  CLI refactor. No CLI behaviour change in this slice. Updated the
  bookkeeping row in `docs/dependency-choices.md` to reflect the
  hledger choice. Refs MAIN-320, #483, #128.
- Added deterministic operator vocabulary facts from optional
  `core/vocabulary.md` to `mb status --json --peek` and `mb start --json`.
  The new `vocabulary` block exposes bounded display terms while keeping
  canonical folders, frontmatter types, validators, JSON keys, and command
  names unchanged. Refs MAIN-281, #407.
- Added `audience` and `operator_summary` fields to findings emitted by
  `mb doctor` (every repair action), `mb validate` (each validation category
  in `validation_categories`, plus `top_audience` and `top_operator_summary`
  at the root), and `mb status` ranked actions. `audience` classifies each
  finding as `mechanical` (Main Branch can apply safely), `operator_decision`
  (a human must decide), or `informational` (read-only signal). The existing
  `safe_to_apply` boolean on doctor actions remains the safety gate;
  `audience` is the routing signal skills and agents read to translate facts
  into business-language next steps. Schemas are additive; no version bump
  required. Refs MAIN-310, #463.
- Added workflow awareness to `mb status`'s existing `git` block:
  `workflow_mode` (one of `solo-on-main`, `branch`, `worktree`,
  `detached`), `default_branch` (detected from `origin/HEAD` with
  fallbacks to `main` and `master`), `upstream`, `ahead`, `behind`,
  `worktree_root`, and an operator-facing `summary` one-liner. Gives
  skills and agents a single place to decide whether to recommend
  save-on-main, branch-and-PR, or worktree-aware flows without their own
  git wrappers. `workflow_mode` describes local git shape only — not
  pre-repo setup state, actor permissions, or check-enforcement choices.
  Refs MAIN-310, #463.
- Accepted decision
  `decisions/2026-05-11-operator-facing-gitops-and-migration-planning.md`
  locking the operator-facing GitOps contract: finding classification,
  workflow awareness, the deferred `mb commit --plan` / `mb publish --plan`
  primitives, a packaged `/mb-publish` skill, and `mb migrate plan`
  non-standard folder scanning. Implementation lands in staged slices that
  each cite this decision. Refs MAIN-310, #463.
- Added `mb suggest links <file>` as a read-only command that ranks candidate
  frontmatter, inline Markdown, entity tag, data/report metadata, nearby
  context, and ignore decisions with JSON reasons for skills and future UI.
  Refs #469.
- Added warning-only Related links mirror checks to `mb validate --cross-refs`
  and a safe `mb doctor repair --plan` / `--apply` path that creates or
  updates `## Related links` body mirrors from frontmatter `linked_*`
  frontmatter without making body links authoritative. Refs #454.
- Added `docs/business-connections.md` and an accepted decision explaining
  when to use typed frontmatter links, inline Markdown links, entity tags,
  data/report references, GitHub history links, nearby context, or no link.
  Refs #468.
- Opened a follow-up implementation issue for scheduled provider data sync.
  Refs #471.
- Added the first record type in a future registry of portable business
  facts: `type: data_source` records at `data/<provider>/source.md`.
  `mb validate` recognizes the schema and checks provider id, owner,
  privacy enum, cadence (warning), freshness date, storage mapping,
  reports list, useful-query shape, and secret leakage. `mb graph` and
  `mb validate --cross-refs` understand the new typed relationship
  `linked_data_sources`. `mb suggest links` carries the typed field hint
  when the candidate is a registry record. Documented in
  `docs/data-source-registry.md` with an accepted decision and sanitized
  Google Ads and Stripe fixture examples. The doc frames `data_source` as
  the first record type and leaves room for sibling types
  (`provider_config`, `secret_handle`, `integration_account`) without
  binding them to SQL/storage assumptions. Refs #470.

### Changed

- Replaced off-brand infrastructure jargon across public docs and generated
  guidance, and softened user-facing "canonical" language toward "source of
  truth", "official", "current", or "the version `mb` trusts" where precision
  allows. Refs #468.
- Cleaned stale future-tense language across public docs and accepted
  decisions so they describe `mb suggest links` (MAIN-313 / #473), the
  `type: data_source` / `linked_data_sources` registry (MAIN-314 / #475),
  and the operator-facing GitOps primitives `audience`, `operator_summary`,
  and `mb status` workflow awareness (MAIN-310 / #476) as shipped, while
  keeping scheduled provider data sync (#471) and the deferred
  `mb commit --plan` / `mb publish --plan` / `/mb-publish` /
  `mb migrate plan` surfaces as the remaining follow-ups. Also removed
  GitHub Pages from a hosting comparison in the bundled `/mb-wiki` skill
  reference so it does not read as a normal Main Branch fallback. Docs-only;
  no CLI, validator, schema, or runtime behavior changes. Refs MAIN-318,
  #478.
- Clarified graph-link authoring guidance across markdown conventions,
  generated business-repo instructions, and bundled authoring skills:
  frontmatter remains the source of truth, body mirrors are repairable viewer output,
  and agents should not invent relationships without evidence. Refs #454.
- Decided that Obsidian is a first-class optional viewer over the same
  markdown files `mb` validates, not a dependency or second source of
  truth. `mb` keeps the typed business graph and validation; Obsidian
  owns clickable browsing, Backlinks, and Graph view. `docs/markdown-link-conventions.md`
  is restructured around three layered rules (frontmatter edges in
  frontmatter; body mirrors are note-level only; Markdown relative links
  for interop) and documents the cross-tool section-anchor trap and
  authoring hazards. Generated business-repo agent guidance
  (`CLAUDE.md.tmpl`, `AGENTS.md.tmpl`) gains a brief Linking section so
  Claude Code and Codex agents emit the body-mirror + frontmatter pair
  consistently. No CLI behavior, frontmatter contract, or fixture
  changes. Refs #455.

## [0.3.15] - 2026-05-09

v0.3.15 ships the migration and repair hardening that landed after v0.3.14 as
an installable patch release. Large validation reports now group findings by
repair category, `mb status` and `mb doctor repair --plan` surface the top
repair cluster, legacy `outputs/` directories get archive-oriented migration
guidance, and onboarding recognizes canonical `core/proof/` evidence without
requiring compatibility shims.

### What this means for you (plain English)

- **Repair lists are easier to act on.** `mb validate`, `mb status`, and
  `mb doctor repair --plan` now show validation categories and top repair
  guidance so a messy migrated repo points at the biggest useful fix first.
- **Migration advice is less destructive.** Old top-level `outputs/` folders
  are treated as historical generated work that should be archived or reviewed
  by hand, not bulk-promoted into pushes or legacy campaigns.
- **Daily startup sees current repo shapes.** `mb onboard` recognizes populated
  `core/proof/` directories, relationship health accepts push-side
  `linked_bets`, and proposed topology rename records can exist without
  weakening validation for live repo entries.

### Added

- Added validation category summaries to `mb validate --json`, `mb status`,
  and `mb doctor repair --plan --json` so large repair reports identify the
  highest-leverage debt cluster first. Refs #460.
- Added migration drift coverage for legacy top-level `outputs/` with
  archive-oriented guidance that avoids fabricating retroactive pushes or
  campaigns. Refs #460.

### Changed

- `mb validate` now accepts `--repo PATH` as an alias for the positional path,
  push schema failures surface the required `goal` mapping shape in the first
  pass, and proposed topology rename entries can carry a pre-rename remote
  mismatch without weakening validation for live entries. Refs #460.
- Relationship health now treats push-side `linked_bets` as a valid active
  bet-to-push relationship and gives clearer reverse-link guidance for
  bet/push and offer/push gaps. Refs #460.
- Onboarding progress now recognizes canonical `core/proof/` content as proof
  instead of requiring legacy single-file proof shims. Refs #460.
- Agent guidance now centralizes slug conventions and destructive-operation
  approval rules for setup/start routing. Refs #460.

### Fixed

- `mb doctor repair --include-migration` errors and help now show the required
  `--apply --include-migration` combination, and checkpoint hook install
  summaries distinguish newly installed hooks from already-verified hooks.
  Refs #460.

## [0.3.14] - 2026-05-09

v0.3.14 ships the first experimental Codex CLI-first adapter slice and the
push playbook health surface that landed after v0.3.13 as an installable
patch release. Fresh business repos now get a tracked `AGENTS.md` Codex
entrypoint; `mb status`, `mb start`, and `mb doctor repair` expose and
refresh Codex readiness facts; and `mb status --json --peek` flags push
playbook health gaps without rewriting your repo. Public philosophy and
architecture docs were also realigned to the current v0.3 story so unshipped
surfaces are not mistaken for current behavior. Claude Code remains the
supported runtime; Codex support is experimental and gated by future dogfood
work.

### What this means for you (plain English)

- **Codex gets a real first-run path.** New `mb onboard` repos include a
  tracked `AGENTS.md` so Codex (and any other AGENTS.md-aware runtime) has a
  documented entrypoint. `mb status --json` and `mb start --json` now expose
  a Codex readiness section, and `mb doctor repair --plan` / `--apply` can
  report and refresh stale Codex instructions. This is an experimental slice;
  Claude Code is still the supported runtime.
- **Push playbook health is visible in `mb status`.** `mb status --json
  --peek` adds push playbook health facts plus concise human and
  ranked-action signals when active pushes are missing run records, playbook
  approval/status is pending, completed pushes lack outcome links, or
  provider boundaries remain plan/manual work. Nothing is rewritten for you;
  the gaps are surfaced so you can act.
- **Public docs match what ships.** `docs/philosophy.md` and
  `docs/system-architecture.md` were realigned to the v0.3 public story so
  unshipped surfaces (mobile, team dashboard, finance/bookkeeping features,
  provider mutation, hosted model invocation) cannot be mistaken for current
  behavior. Durable contracts (repo shape, topology roles, push and playbook
  frontmatter, artifact routing) are preserved.

### Added

- Added the first experimental Codex CLI-first adapter slice: fresh business
  repos now get a tracked `AGENTS.md` Codex entrypoint, `mb start --json` and
  `mb status --json` expose Codex readiness facts, and
  `mb doctor repair --plan` / `--apply` can report and refresh stale Codex
  instructions. This does not claim Codex slash-command or workflow parity.
  Refs #405.
- Added push playbook health facts to `mb status --json --peek`, plus concise
  human and ranked-action signals when active pushes are missing run records,
  playbook approval/status is pending, completed pushes lack outcome links, or
  provider boundaries remain plan/manual work. Refs #446.

### Changed

- Realigned `docs/philosophy.md` and `docs/system-architecture.md` to the v0.3
  public story: dropped speculative surface copy, collapsed sections that
  duplicated `docs/ETHOS.md`, `docs/OPERATOR-LOOPS.md`, and `docs/ROADMAP.md`,
  consolidated legacy/compatibility names under a single Superseded Names
  section, and stated the no-provider-mutation invariant up front. Durable
  contracts (business repo shape, repo topology role table, push and playbook
  frontmatter, artifact routing, state boundaries) are preserved. Refs #444.

## [0.3.13] - 2026-05-08

v0.3.13 ships the repo-topology work that landed after v0.3.12 as an
installable patch release. `mb status`, `mb graph`, and `mb doctor` now expose
topology facts; `mb validate` enforces the new repo descriptor and topology
record schemas; migration drift now surfaces as actionable warnings; and
reusable playbooks plus agent-facing routing docs were refreshed to match the
current push topology.

### What this means for you (plain English)

- **`mb` can now show you your repo topology.** `mb status --json` adds a
  `topology` section and a business-readable "Business map" line so you can
  see hub/child relationships without hand-tracing them. `mb graph --json`
  gains `repo` nodes and deterministic hub/child edges with playbook-run
  resolution.
- **Migration drift gets named, not hidden.** `mb validate` and
  `mb doctor repair --plan --json` warn on stale generated guidance, legacy
  active-write folders, stale Claude settings, wrong push/playbook paths, and
  legacy bet campaign links — without rewriting anything for you.
- **Child repos get a real, role-neutral descriptor.** The new
  `.mainbranch/repo.json` contract covers site, offer, product, client,
  finance, legal, ops, integration sidecar, experiment, and archive repos,
  while keeping existing `.mainbranch/source.json` site behavior compatible.
- **Topology records are validated before they go stale.** `mb validate`
  reads `core/operations/repo-topology.md` `type: repo_topology` entries with
  topology vocabularies, safe repo-link checks, and finance/legal/provider
  boundary warnings.
- **Reusable playbooks and routing docs match the current push model.**
  `ship-bet` and `weekly-review` route run evidence into
  `pushes/<push>/playbooks/`, outcomes, logs, and checkpoints; agent-facing
  routing docs and the public product story have been refreshed to match.

### Added

- Added privacy-safe business repo migration drift warnings through
  `mb validate`, `mb doctor`, and `mb doctor repair --plan --json` for stale
  generated guidance, legacy active-write folders, stale Claude settings,
  wrong push/playbook paths, and legacy bet campaign links. Refs #432, #436.
- Added the role-neutral `.mainbranch/repo.json` child repo descriptor contract
  for site, offer, product, client, finance, legal, ops, integration sidecar,
  experiment, and archive repos, while keeping existing site
  `.mainbranch/source.json` behavior compatible. Refs #417.
- Added `mb validate` coverage for `core/operations/repo-topology.md`
  `type: repo_topology` records, including topology role/lifecycle/visibility
  vocabularies, safe repo-link checks, and finance/legal/provider-boundary
  warnings. Refs #416.
- Exposed repo topology facts in `mb status --json`, `mb graph --json`, and
  `mb doctor repair --plan --json` through a shared role-neutral
  `mb.topology` reader. Status gains an additive `topology` section and a
  business-readable "Business map" line; graph gains `repo` nodes and
  deterministic hub/child relationship edges (with `linked_playbook_runs`
  resolving to push playbook run files and `INDEX_VERSION` bumped to 2);
  doctor gains a preview-only `topology-drift` section that warns on unsafe
  metadata, descriptor/registry handle mismatch, descriptor/role mismatch,
  or orphaned child descriptors without renaming, deleting, or rewriting
  any repos. Public-safe topology payload and local-machine facts
  (e.g. clone path) stay in separate fields. Refs #418.

### Changed

- `mb validate` now accepts current bets that use `linked_pushes` without
  requiring legacy `linked_campaigns`, keeps `linked_campaigns` compatible for
  old bets, and treats `research/README.md` as folder documentation instead of
  a research artifact. Refs #432.
- Updated generated business `CLAUDE.md`, `/mb-site`, and `/mb-help` guidance
  so agents distinguish hub work from child-repo work and avoid committed
  absolute paths, secrets, raw provider caches, finance/legal source data, or
  permission claims in repo descriptors. Refs #417.
- Refreshed reusable playbook skeletons against the current push topology:
  `ship-bet` and `weekly-review` now route concrete run evidence to
  `pushes/<push>/playbooks/`, outcomes, logs, and checkpoints instead of legacy
  `campaigns/`, and the Google Ads Search launch playbook is labeled as a
  usable draft recipe rather than a non-executable skeleton. Refs #425.
- Refreshed agent-facing routing docs to match the current daily loop,
  topology vocabulary, and migration guardrails. Refs #437.
- Refreshed the public story around the shipped v0.3.12 work so README,
  docs, and roadmap language match what users can install today. Refs #440.

## [0.3.12] - 2026-05-08

v0.3.12 is a quick follow-up release for the Google Ads launch playbook rails
merged after v0.3.11. It moves the post-release playbook changelog entries out
of the already-published v0.3.11 section and ships them as their own patch.

### What this means for you (plain English)

- **Google Ads Search launch plans get more reviewable.** `/mb-ads
  launch-plan` now has clearer rails for researched campaign settings, assets,
  skipped asset rationale, approval gates, and proposed durable `core/`
  updates without mutating Google Ads.
- **Reusable playbooks and per-push run records are easier to separate.** The
  docs now distinguish platform rules, attributed playbook opinion, fork
  points, and one-off push execution records.

### Added

- Added a playbook concept guide that separates official platform rules,
  global platform guidance, attributed playbook opinion, fork points, and
  per-push run records. Refs #427.
- Added playbook memory guidance so paid-search discoveries can become durable
  `research/`, `core/`, proof, strategy, or decision updates instead of staying
  trapped inside one campaign run record. Refs #427.
- Added Google Ads campaign-settings and asset research rails for
  `/mb-ads launch-plan`, including market-intent research, geography and
  conversion-path choices, RSA rationale, sitelinks, callouts, structured
  snippets, skipped assets, URL options, and playbook fork records. Refs #427.

## [0.3.11] - 2026-05-08

v0.3.11 tightens the daily loop after v0.3.10: startup and
migration guidance is less ambiguous, legacy `.vip` YAML state is audit-only,
business primitives and repo topology are clearer, release simulations run from
materialized fixtures, and Google Ads Search launch work has a plan-only
playbook path.

This release also records a Codex adapter plan, but it does not promote Codex
or any other non-Claude runtime to supported status. Claude Code remains the
supported runtime; print-mode simulations remain proxy evidence rather than
interactive TUI slash-command proof.

### What this means for you (plain English)

- **Startup should make fewer bad guesses.** `/mb-start` now avoids reusing the
  same menu numbers for different choices and treats active-offer picks as
  session context unless you explicitly save state.
- **Old `.vip` YAML is no longer treated as current truth.** `mb doctor repair
  --plan --json` can classify legacy `.vip/local.yaml` and `.vip/config.yaml`
  without printing raw values, but it does not delete or migrate them for you.
- **Offers, bets, proof, pushes, and child repos are easier to reason about.**
  Skills and generated instructions now share clearer business primitives and
  topology language.
- **Google Ads launch planning has safer rails.** The new Search playbook helps
  build reviewable plans and run records without claiming Main Branch can
  publish campaigns or mutate ad accounts.
- **Release evidence is more concrete.** Print-mode simulations now run from
  materialized fixture repos and label permission-distorted runs as proxy
  evidence with deterministic fallback facts.

### Added

- Added a proposed Codex adapter plan that preserves Claude Code as the
  supported runtime today, defines staged support levels, and names the first
  smoke-gated implementation slices without claiming Codex runtime support.
  Refs #401.
- Added materialized release-simulation fixture profiles to the Claude runtime
  dogfood harness. Print-mode simulations now run from per-simulation fixture
  repos for launch-readiness gaps, dirty checkpoint planning, broken skill
  wiring, synthetic private-data refusal, and legacy drift, with evidence for
  applied mutations, read-only `mb` facts, permission denials, and grounding
  verdicts. Refs #402.
- Added a shared business-primitives reference for offers, bets, pushes,
  reusable playbooks, push playbooks, proof, and decisions, including
  live-validation, graduation, proof-placement, and ask-before-destructive-offer
  rules. Refs #411.
- Added a `mb doctor repair --plan --json` audit section for legacy
  `.vip/local.yaml` and `.vip/config.yaml` YAML state. The plan classifies key
  families without printing raw values, separates local/session state from
  durable business/provider facts, and keeps deletion/migration manual. Refs
  #413.
- Added an accepted business repo topology decision that defines hub and child
  repo roles, relationship types, GitHub owner/repo and local-folder naming,
  lifecycle language, reusable-vs-run playbook boundaries, safe metadata
  placement, finance/legal boundaries, slug rules, and follow-up surfaces for
  status, graph, doctor, generated instructions, and future dashboard maps.
  Refs #406.
- Added a release-simulation fixture for the `/mb-start` ambiguous-choice
  failure where an operator replies `1` for the top recommendation in a rich
  multi-offer repo, so release review checks that offer selection cannot
  silently win over onboarding or recommendation routing. Refs #410.
- Added a rich-migration `/mb-start` triage fixture that requires agents to map
  durable business truth, active bets, execution work, proof, legacy
  compatibility files, and linked operating-boundary repos before routing or
  spawning agents. Refs #410.
- Added Google Ads campaign-plan guidance for `/mb-ads`, including
  offer/policy-fit routing, existing-campaign rescue decisions, account-history
  inputs, `mb connect`/provider-tool boundary checks, keyword and negative-list
  planning, site/conversion readiness, approval gates, and a sanitized
  plan-only push playbook fixture. Refs #414.
- Added the first reusable Google Ads Search launch playbook skeleton under
  `.claude/playbooks/`, with Noontide's paid-search proof-run approach and a
  push-playbook run template. Refs #414.
- Added B2B local-services Google Ads field notes to the reusable Search launch
  playbook, covering GA4/GTM/Ads import order, Search-only campaign defaults,
  UI gotchas, negative-keyword categories, manual gates, and validation-window
  calibration. Refs #422.
- Expanded the Google Ads Search launch playbook with measurement-chain gotchas
  from the related operator repo launch notes: explicit form-success events,
  GTM Preview verification, GA4 Realtime/admin lag, and Google Ads conversion
  import UI variants. Refs #414, #422.

### Changed

- Aligned bundled skill guidance, generated business `CLAUDE.md`, and public
  architecture docs around the bet-vs-offer rubric, `core/offer.md` as
  single-offer truth or multi-offer portfolio thesis, and
  `core/offers/<slug>/proof/` for offer-specific proof. Refs #411.
- Retired LLM-facing "domain rubric" setup language in favor of business
  primitives and setup patterns, carried forward the operational community,
  e-commerce, and multi-offer setup guidance, and added skill validation
  warnings for new uses of the old phrase outside historical compatibility
  notes. Refs #411.
- Retired `.vip/config.yaml` as active path/provider/tool config in current
  CLI and skill guidance. New setup no longer creates it, and offer-aware
  skills ask for explicit session context instead of silently routing from
  `.vip/local.yaml`. Refs #413.
- Expanded `mb doctor repair --plan --json` migration guidance with an
  offer-topology section that surfaces legacy `.vip/local.yaml` active-offer
  state, offer folder/frontmatter slug drift, and multi-offer review needs
  without auto-renaming or rewriting strategy files. Refs #410.
- Tightened `/mb-start` and multi-offer skill guidance so one prompt cannot
  reuse the same number for recommendations, offers, and routes; offer choices
  are session-scoped unless the operator explicitly confirms saving local
  active-offer state. Refs #410.

## [0.3.10] - 2026-05-08

v0.3.10 makes the release process prove itself while adding new owner-facing
daily-loop paths: richer launch orchestration, beginner education, cheaper
large-repo status checks, and the first release gate that requires simulation
evidence plus manual transcript review.

### What this means for you (plain English)

- **Launch work has a clearer path.** `/mb-start` can now route an offer launch
  through research, push, lander, ads-plan, approval, and checkpoint steps
  without pretending Main Branch mutates provider accounts for you.
- **Beginner education is easier to find.** `mb educational` now has a catalog
  for common setup, ownership, provider, and tool-choice topics.
- **Status scales better.** Relationship-health checks are cheaper on larger
  business repos.
- **Releases have stronger proof.** Package-visible releases now run release
  simulations and require manual transcript review before release claims are
  treated as evidence.

### Added

- Added bundled skill guidance for a guided offer-launch path: `/mb-start`
  can route an operator from active offer to keyword-gate research, canonical
  launch push, one-page lander, provider-safe ad launch plan/check, and
  checkpointed approval records without claiming live provider mutation. Refs
  #89.
- Added a beginner education catalog for `mb educational`, including the
  daily owner loop, Main Branch anti-SaaS why, CLI/dashboard, markdown/Notion,
  git/cloud-sync, Cloudflare Pages, Cal.com, Beancount, Forgejo, Cursor, and
  Stripe topics. Refs #144.
- Added an opt-in `grok-8` researched-brief format for `/mb-think`, including a
  reusable eight-category research reference, downstream guidance for
  `/mb-ads`, `/mb-site`, `/mb-organic`, and push-playbook use, plus a
  public-safe example brief. Refs #147.
- Added release-acceptance simulation coverage for the `/mb-start launch
  <offer>` path so release reviewers can check keyword-gate, push, lander,
  ads-plan, approval, and checkpoint routing before treating the release as
  ready. Refs #400.

### Changed

- Refreshed the existing educational topics so setup, provider readiness,
  updates, GitHub/Docs, Cloudflare/Vercel, and sensitive-data guidance teach
  normal business owners through exact Main Branch commands without claiming
  unshipped provider or runtime support. Refs #144.
- Tightened release simulation guidance so package-visible releases run
  pre-tag release candidate and release acceptance simulations whenever
  feasible, require manual transcript review beyond heuristic rubrics, and
  record whether Claude Code print-mode actually executed read-only `mb`
  grounding commands or fell back because of permissions. Refs #394.
- Reduced `mb status` relationship-health work on large repos by reusing graph
  relationship facts instead of reparsing the same file bodies repeatedly.
  Refs #358, #396.

## [0.3.9] - 2026-05-08

v0.3.9 makes the daily operating loop more inspectable. Main Branch now exposes
business relationship gaps in `mb status`, validates push playbooks as durable
business commitments, gives JSON consumers a shared result envelope, and
documents the packaged runtime boundary for non-Claude callers.

### What this means for you (plain English)

- **Status can explain missing business links.** `mb status` can now surface
  disconnected bets, pushes, offers, and outcomes instead of only reporting file
  and repo health.
- **Playbooks become checkable plans.** Push playbooks now have a v1 schema so
  provider work, approval gates, resources, outcomes, and safe state can be
  reviewed before anyone mutates an external account.
- **Agents get steadier JSON.** High-value `mb --json` commands now share a
  non-colliding result envelope while preserving their command-specific payloads.
- **Runtime claims stay scoped.** Packaged callers can use deterministic `mb`
  subprocess calls today, while non-Claude slash/runtime adapters remain roadmap
  targets until they have their own evidence.

### Added

- Added `mb status` relationship-health JSON and human briefing signals for
  disconnected bets, pushes, offers, and outcomes so daily status can surface
  business-loop gaps from graph facts. Refs #358.
- Added v1 `type: playbook` validation for
  `pushes/<push>/playbooks/<playbook>.md`, including required push linkage,
  provider-boundary, trigger, resource, approval, safe state, validation, and
  outcome-link fields, plus bundled skill guidance that treats playbooks as
  plans and approval records rather than provider execution. Refs #350.

### Changed

- Added a shared additive v1 JSON result envelope to high-value `mb --json`
  surfaces: `mb status`, `mb start`, `mb checkpoint`, `mb issue`, `mb doctor`,
  and `mb onboard`. Existing command-specific payload keys remain top-level for
  compatibility while shared metadata (`result_envelope_version`,
  `result_schema`, `mb_command`, `ok`, `result_status`, `errors`, `warnings`,
  and `actions`) gives skills, harnesses, and future dashboards one
  failure-handling convention. Refs #297.
- Documented the packaged `mb` invocation contract, runtime repo-path discovery
  rules, and adapter/readiness map for Codex, Cursor, OpenClaw, Hermes,
  Paperclip-adjacent orchestration, and local runtimes without claiming
  non-Claude runtime support. Refs #129.

## [0.3.8] - 2026-05-08

v0.3.8 tightens the daily operating loop after the 0.3.7 release discipline
landed. Main Branch now has a shared relationship registry for graph and
cross-reference validation, safer runtime route checks, and clearer provider
boundaries for Postiz and X-style resource delivery.

### What this means for you (plain English)

- **The business graph is more useful.** `mb graph --json` and
  `mb validate --cross-refs` now agree on relationship fields, Markdown links,
  push-to-offer links, and safe provider references.
- **Claude gets fewer fake routes.** User-facing runtime guidance now points to
  shipped Main Branch slash commands or clearly marks future commands as
  unshipped.
- **Provider claims stay honest.** Postiz remains a candidate scheduling rail
  until connected-channel smoke exists, and Main Branch refuses X comment/DM
  automation until an accepted provider path is proven.
- **Release reviews are sharper.** Claude transcript reviews now have a public
  rubric and sample so reviewers can turn simulation misses into product work.

### Changed

- Aligned bundled skill and public docs language with the accepted work-continuity
  model: decisions are rationale artifacts, GitHub issues are durable work
  threads when needed, `/mb-start` regenerates the current view from facts, and
  `/mb-end` remains closure/checkpointing rather than tomorrow planning. Refs
  #377.
- Accepted the X resource-delivery boundary: Main Branch may draft public
  resource/link playbooks and future scheduling/provider smoke, but refuses
  comment-to-DM, keyword DM, auto-reply, auto-like, auto-follow, bulk DM, and
  browser-automation execution on X until a later decision accepts an official
  tested provider path. Refs #351.
- Recorded a public-safe partial Postiz scheduling smoke: the REST API endpoint
  and auth path worked, but the tested setup had no connected channels, so
  Postiz remains a candidate rail rather than supported scheduling behavior.
  Refs #352.
- Expanded Claude release simulation transcript review guidance with a
  severity rubric, public-safe sample review, and harness evidence-template
  pointer so release reviewers distinguish heuristic scoring from manual
  production-behavior review. Refs #379.
- Added a shared relationship registry to `mb graph --json` and
  `mb validate --cross-refs`, including normalized relationship types, safe
  Markdown body-link parsing, push-to-offer checks, and provider-ref graph nodes
  that expose provider/ref kinds without raw account values. Refs #357.
- Removed ghost runtime routes from bundled skill and public docs language:
  newsletter/email intent now routes to `/mb-think` and `/mb-organic`, the
  unshipped `/mb-start launch <offer>` form is labeled as future/deferred, and
  `mb skill validate` now fails obvious references to unbundled Main Branch
  slash commands. Refs #356.

## [0.3.7] - 2026-05-07

v0.3.7 turns the new release discipline into something Main Branch can
practice. Claude Code runtime dogfood now has an automated harness, release
simulations turn real operator moments into reviewable evidence, generated
business `CLAUDE.md` files push agents back through the CLI, and old-layout
migration guidance is safer before it writes.

### What this means for you (plain English)

- **Claude gets stronger startup instructions.** Fresh business repos now tell
  Claude Code to inspect `mb` facts before giving setup or repair advice.
- **Releases have better evidence.** Main Branch can run a sanitized dogfood
  harness and prompt simulation suite before claiming runtime behavior works.
- **Migration is less surprising.** Old `reference/` and `campaigns/` guidance
  has been swept toward the current folder model, and migration dry-runs now
  show backups, conflicts, and safe next commands before apply.
- **Provider choices are clearer.** The docs now explain when Main Branch
  should wrap an existing CLI, call an MCP/server API, or build its own tool.

### Added

- Added `scripts/claude-runtime-dogfood.py`, a repeatable Claude Code dogfood
  harness that creates a sanitized fixture business repo, runs deterministic
  CLI/runtime-handoff checks, captures public-safe evidence artifacts, and can
  optionally run a labeled `claude -p` print-mode proxy smoke. Refs #364.
- Added a release simulation suite manifest, prompt fixtures, expected-behavior
  rubrics, transcript-review categories, and release-tier documentation for
  PR smoke, pre-release candidate, and release acceptance evidence. Refs #368.
- Added a public Claude Code runtime dogfood runbook for release-bearing manual
  smoke evidence, including sanitized fixture setup, read-only CLI checks,
  `/mb-start`, `/mb-think`, `/mb-organic`, checkpoint behavior, repo-boundary
  checks, and a paste-back evidence template. Refs #355.

### Changed

- Fresh business repo `CLAUDE.md` files now make the bootstrap CLI-first:
  Claude Code is told to read `mb` status/start/doctor facts before setup or
  repair advice, separate read-only checks from write/apply repairs, and return
  technical repair results in business-owner language. Refs #353.
- Hardened old-layout migration output so dry-runs show safe next commands,
  planned backup location, and source-to-target conflict context before apply;
  bumped the migration JSON envelope schema to v2 for the new per-action
  `backup` and `next` fields; refreshed docs and bundled skill guidance away
  from current `reference/` and `campaigns/` write targets. Refs #284.
- Documented the public build-vs-wrap-vs-sidecar boundary for provider CLIs,
  MCP servers, hosted workflows, and future sidecars, with concrete guidance
  for Cloudflare, Postiz, Apify/X research, Vercel-style platforms,
  Beancount-style bookkeeping, and Google Ads/GTM readiness. Refs #366.

## [0.3.6] - 2026-05-07

v0.3.6 makes Main Branch more disciplined about how business work gets saved,
remembered, and resumed. Checkpoint verbs are now business-readable, fresh
business repos install commit-message validation, `mb status` includes a
provisional git journal, and growth research guidance is broader without
pretending untested provider automation is shipped.

### What this means for you (plain English)

- **Your commits read like business progress.** Main Branch now accepts
  checkpoint subjects such as `[added] market.md` and blocks vague raw commit
  messages in business repos.
- **`mb status` can remember what happened.** Status and start output now
  include recent business-readable commit history so Claude can answer "what
  changed since last time?" from repo facts.
- **Growth research has a stronger path.** `/mb-think` now has winning-ad
  research guidance for customer language, competitor gaps, review mining,
  script teardown, and social comment mining.
- **Provider boundaries stay honest.** Postiz, X/Grok, Apify, and
  comment-to-DM/resource-delivery ideas are framed as researched or candidate
  rails until smoke evidence proves support.
- **The public framing is cleaner.** README, roadmap, architecture, ethos, and
  contributor docs now describe Main Branch as durable operating memory for a
  business, not just a growth-file scaffold.

### Added

- Documented the proven Claude Code invocation contract for `/mb-start`,
  including extra-text behavior, natural-language routing, the required
  project-local `.claude/skills/mb-*` bridge links, and the repair path when
  Claude Code reports `Unknown command: /mb-start`. Refs #354.
- `mb checkpoint` now uses the accepted business-readable checkpoint verb
  contract, proposes subjects such as `[added] market.md`, validates checkpoint
  messages with `--validate` or stdin, and exposes parsed verb/loop/channel
  metadata for future status and timeline consumers. Refs #301.
- Accepted decisions now capture Postiz as the candidate social scheduling rail
  to smoke next, plus the growth-automation playbook boundary for future
  comment-to-DM and resource-delivery add-ons. Refs #341.
- Fresh business repos now install a repo-local Main Branch `commit-msg` hook
  that validates manual git commits through `mb checkpoint --validate -`,
  skips Git-generated merge/revert/fixup/squash/amend subjects, records the
  active `mb` executable for minimal-PATH Git clients, and includes checkpoint
  hook status, install, and uninstall controls on `mb checkpoint`. Refs #302.
- `mb status` and `mb start` now expose a provisional git `journal` timeline
  that groups business-readable commits by operator loop, preserves legacy
  `[checkpoint]` history, and parses `Refs:` links to bets, pushes, decisions,
  legacy campaigns, and GitHub issues. Refs #303.
- README, roadmap, architecture, ethos, dependency choices, support, security,
  and contributor docs now frame Main Branch around durable operating memory,
  current Claude Code support, optional rails, and lower-maintenance roadmap
  buckets instead of issue-by-issue release lists. Refs #340, #346.

### Changed

- Package builds now use SPDX-style MIT license metadata and the CI/local
  quality gates type-check tests, raise the coverage floor to 79%, and keep
  Windows as an explicit experimental, non-CI-gated platform. Refs #135.
- Added `/mb-think` winning-ad research guidance for customer language,
  competitor gap maps, review mining, script teardown, and social comment
  mining, with `/mb-ads` routing pointers and provider-boundary notes for
  Apify, X/Grok, Postiz, X API, and ManyChat-style automation. Follow-up
  guidance now distinguishes Apify public X post/profile/reply mining from
  Grok topic sentiment, and clarifies that DM/comment-keyword CTAs are draft
  strategy, not supported automation. Refs #341.
- `mb doctor` and `mb doctor repair` now report, repair, and preserve
  business checkpoint hook wiring, and shipped skills use approved
  `mb checkpoint` planning/validation/save calls instead of raw git commit
  instructions. Refs #302.
- `/mb-start` and `/mb-status` now treat status journal facts as the source of
  truth for "what happened since last time?" instead of re-probing raw git logs.
  Refs #303.
- Legacy campaign paths are now described as compatibility aliases while the
  current working-folder model keeps `pushes/` as the active growth work home.
  Refs #345.

## [0.3.5] - 2026-05-06

v0.3.5 tightens the Cloudflare account-token repair from v0.3.4. Main Branch
now recognizes `cfat_` Cloudflare Account API tokens automatically when
`account_id` metadata is present, and `/mb-site` setup docs show the safer
account-token command shape.

### What this means for you (plain English)

- **Cloudflare account tokens need less ceremony.** A stored token beginning
  with `cfat_` now routes to the account-token validation path automatically
  when account metadata is present.
- **The docs match the safer path.** `/mb-site` setup guidance now teaches the
  account-scoped token command with `account_id` metadata instead of implying
  every operator should use a personal user token.

### Fixed

- `mb connect test cloudflare` now auto-detects `cfat_` account tokens and uses
  the account-token validation path when `account_id` metadata is present,
  without requiring `token_type=account`. Refs #335.
- `/mb-site` setup guidance, `setup_creds.sh`, and the Cloudflare Pages
  reference now show the `mb connect cloudflare --token-stdin --metadata ...`
  command shape for account-scoped Cloudflare tokens. Refs #335.

## [0.3.4] - 2026-05-06

v0.3.4 repairs the Cloudflare setup path used by `/mb-site`. Account-scoped
Cloudflare tokens can now validate cleanly, provider failures include safer
diagnostics, and site workflows stop before Cloudflare-dependent work when the
repo is not connected yet.

### What this means for you (plain English)

- **Cloudflare setup is less brittle.** Main Branch can validate account-scoped
  Cloudflare tokens as well as the older user-token path.
- **Credential errors are easier to fix.** `mb connect test cloudflare --json`
  now reports safe endpoint-family, HTTP status, and provider error details
  instead of hiding every failure behind a generic rejection.
- **Worktrees share the right identity.** New connect metadata derives
  credential identity from stable git facts so parallel worktrees do not split
  keychain entries for the same business repo.
- **`/mb-site` stops earlier.** Domain, DNS, Pages, custom-domain, and deploy
  work now gate on Cloudflare readiness instead of failing halfway through.

### Changed

- `/mb-site` now hard-gates Cloudflare-dependent domain, DNS, Pages, custom
  domain, and deploy work on `mb connect doctor --json` readiness. The skill
  offers connect-now, read-only, and skip-for-now paths instead of discovering
  missing Cloudflare credentials halfway through setup. Refs #335.

### Fixed

- `mb connect test cloudflare` now supports Cloudflare account-scoped token
  validation via `--metadata token_type=account --metadata account_id=...`
  while preserving the existing user-token verify path. Failed provider checks
  include safe upstream diagnostics such as endpoint family, HTTP status, and
  provider error codes/messages in JSON. Account-token validation falls back to
  a read-only account probe if Cloudflare returns 404 for the token verify path,
  so valid credentials are not immediately classified as bad solely because the
  verify endpoint shape changed. Refs #335.
- `mb connect` now derives repo-scoped credential identity from stable git
  remote/common-dir facts for new connect metadata before falling back to the
  local path, avoiding separate keychain refs for parallel worktrees of the same
  business repo. Existing non-empty `repo_id` values are preserved so previously
  stored keychain refs are not orphaned. Refs #335.
- New and repaired business repos now gitignore `.mb/connect.yaml` by default,
  and doctor repair untracks an already-committed `.mb/connect.yaml` while
  leaving the file on disk. Interactive `mb connect <provider> --token-stdin`
  prints paste/EOF instructions before reading from a TTY. Refs #335.
- `/mb-site` no longer tells operators to use `domain.py buy` for live domain
  purchases; the command remains a structured unavailable placeholder until
  registrar support lands behind explicit guardrails. Refs #335.

## [0.3.3] - 2026-05-06

v0.3.3 turns the campaign architecture work into the clearer push primitive.
It adds canonical `pushes/` scaffolding and validation, keeps legacy
`campaigns/` readable during migration, and splits `/mb-site` into smaller
runtime-loadable references.

### What this means for you (plain English)

- **Your business can use its own words.** Main Branch stores the canonical
  primitive as a `push`, while `core/vocabulary.md` lets an operator call that
  work a launch, drop, challenge, promo, campaign, or another local term.
- **New repos start in the new shape.** `mb init` and `mb onboard` now scaffold
  `pushes/`; existing `campaigns/` records still read as compatibility input.
- **Push records are checkable.** `mb validate`, `mb status --json --peek`,
  `mb start --json`, and `mb graph --json` now expose canonical push facts and
  schema errors.
- **Site work loads less context.** `/mb-site` is now a compact router with
  focused minisite references instead of one large skill document.

### Added (MAIN-248 / #323)

- `mb validate` now enforces the canonical `pushes/<YYYY-MM-DD-slug>/push.md`
  schema: `type: push`, bounded `kind:`, lifecycle `status:`, separate
  `health:`, structured `goal: { metric, target, by }`, `owner`, `audience`,
  `offer`, and short `promise`. Legacy `campaigns/*/campaign.md` records
  remain readable as compatibility input. Refs #323.
- `mb status --json --peek`, `mb start --json`, and `mb graph --json` now expose
  canonical push facts (`pushes`, `active_pushes`, `push_count`) plus explicit
  legacy campaign compatibility keys and deprecation markers during the
  compatibility window. Refs #323.
- Bundled write-heavy skills now show the minimum valid `push.md`
  frontmatter required by `mb validate`, so runtime-generated push records
  are less likely to drift from the deterministic schema. Refs #323.

### Added (MAIN-249 / #324)

- `mb init` and `mb onboard` now scaffold the canonical `pushes/` folder
  instead of legacy `campaigns/`, and bundle an optional
  `core/vocabulary.md` template so a business can name what it calls a
  push (drop, launch, challenge, promo, campaign, etc.) without changing
  any engine internals. Existing repos with `campaigns/` keep working as
  compatibility reads. Refs #324.
- `mb validate` and `mb graph` accept canonical `pushes/<YYYY-MM-DD-slug>/push.md`
  records and the `linked_pushes` link field alongside legacy campaigns;
  `mb status` indexes `pushes/` and surfaces legacy `campaigns/` count
  as a parenthetical drift signal. Full kind/health/structured-goal
  schema is left to #323. Refs #324, refs #323.
- `mb doctor` warns when a repo still has legacy `campaigns/` records
  ("Legacy campaigns folder detected. Main Branch now writes pushes/.
  Run `mb migrate campaigns --plan` to preview a safe move.") and
  exposes a structured `legacy_campaigns_to_pushes` repair item via
  `mb doctor repair --plan --json`. Refs #324.
- `mb migrate campaigns --plan` (read-only) prints a per-record plan
  classifying each `campaigns/<slug>/campaign.md` record as a move
  (deterministic destination), ambiguous (route to operator review),
  or blocker (cannot infer a safe move). The apply path is explicitly
  deferred to a follow-up PR with backups and explicit operator
  approval. Implements the Migration Rubric from the issue body. Refs
  #324.
- Top-priority bundled skills (`/mb-ads`, `/mb-organic`, `/mb-vsl`,
  `/mb-site`, `/mb-bet`, `/mb-start`) carry a new "Output destinations
  and operator vocabulary" section telling them to write to `pushes/`,
  read `core/vocabulary.md` when present, and recommend `mb doctor` /
  `mb migrate campaigns --plan` on legacy repos. `linked_pushes` is
  added to bet frontmatter alongside legacy `linked_campaigns`. Refs
  #324.

### Fixed

- `mb validate` now checks `campaigns/*/campaign.md` `status:` against the
  campaign lifecycle (`draft, planned, active, paused, completed, canceled,
  archived`) defined in
  [decisions/2026-05-06-campaign-primitive-and-architecture-model.md](decisions/2026-05-06-campaign-primitive-and-architecture-model.md).
  The previous implementation reused the offer enum, so a campaign written
  to the merged decision (`status: active`) failed validation. Refs #328.
- Corrected the `linked_bets:` example in the campaign primitive decision
  and supporting docs to use the dated `bets/2026-05-06-workshop-waitlist.md`
  shape, matching every other primitive's path convention. Refs #328.

### Added

- New decision
  [decisions/2026-05-06-campaigns-refuse-list.md](decisions/2026-05-06-campaigns-refuse-list.md)
  publishes the fields the engine refuses to add to `campaign.md` (epic,
  numeric priority, multi-assignee, story points, kpi_dashboard, linked_okrs,
  free-text description, and others). The product is judged by what it
  refuses; the refuse list is now the public default and a clear path to
  changing it. Refs #328.
- New decision
  [decisions/2026-05-06-main-branch-operating-spine.md](decisions/2026-05-06-main-branch-operating-spine.md)
  codifies Main Branch's operating philosophy as a durable product
  decision: the system speaks Linear-quiet, the operator runs
  Hormozi-volume, and the bets layer carries Robbins identity. Includes
  ten cross-cutting principles, a voice/tone profile for operator-facing
  surfaces, and the principle that the operator owns the vocabulary
  (campaigns can be called *drops*, *launches*, *challenges*, *promos*
  in operator-facing surfaces). Refs #328.
- New decision
  [decisions/2026-05-06-push-primitive-and-operator-vocabulary.md](decisions/2026-05-06-push-primitive-and-operator-vocabulary.md)
  makes `push` the canonical engine primitive (folder `pushes/`,
  `type: push`, `linked_pushes`, push-shaped JSON keys, bounded `kind:`
  enum) while preserving existing `campaigns/` records as compatibility
  reads. Operator vocabulary lives in a new optional `core/vocabulary.md`
  — committed business truth, not `.mb/` or Claude memory — so the
  operator's business calls a push whatever it wants (*drop*, *launch*,
  *challenge*, *campaign*) while canonical storage stays consistent.
  Migration is preview-then-apply; deterministic implementation lives in
  #323 and skill/runtime/migration code lives in #324. Refs #329.

### Changed

- Defined `campaigns/` as the first coordinated-push model, refreshed the
  system architecture model around current business-repo folders, and blessed
  `documents/transcripts/`, `documents/prototypes/`, and `documents/archive/`
  for non-campaign artifacts before the later `pushes/` decision superseded the
  storage name in part. Refs #321.
- Refactored `/mb-site` into a compact router with progressively loadable
  minisite step references, and split examples from troubleshooting so agents
  can load only the detail needed for the current site step. Refs #107 and
  #110.
- The campaign primitive decision
  ([decisions/2026-05-06-campaign-primitive-and-architecture-model.md](decisions/2026-05-06-campaign-primitive-and-architecture-model.md))
  is superseded **in part**: the canonical storage shape moves to `push`,
  but the relationship model, definition of a coordinated push, lifecycle
  states, and non-campaign artifact routing stand. The system architecture
  doc now points at `pushes/` as the canonical primitive while documenting
  `campaigns/` as a compatibility read. Refs #329.

## [0.3.2] - 2026-05-06

v0.3.2 makes Main Branch safer to repair and clearer about where business
memory lives. It adds guided doctor repair, retires the old committed
`reference/` folder model for new repos, and tightens migration/runtime
guidance from real dogfood.

### What this means for you (plain English)

- **Doctor can now help repair a repo.** `mb doctor repair --plan` explains
  what is stale or unsafe before anything writes, and `--apply` can fix safe
  wiring/local-state issues.
- **New business repos use `core/` as the business brain.** Legacy
  `reference/*` paths are compatibility fallbacks, not places where new truth
  should be written.
- **Migration guidance is less confusing.** Claude-led updates now start with
  Main Branch update/repair, use read-only checks by default, and pause before
  git decisions that normal users should not have to judge alone.

### Added

- Added `mb doctor repair --plan/--apply` as a guided repo reconciliation
  surface with read-only planning, JSON output, safe wiring/local-state repairs,
  optional `--include-migration` migration apply after preview review,
  validation and graph summaries, git review guidance, and explicit runtime
  smoke reminders. Refs #314.

### Changed

- Clarified quick start and beginner docs so daily users run `claude` then
  `/mb-start` without a separate `mb status` step. `mb status` is now framed as
  the terminal-only briefing that `/mb-start` reads internally.
- Clarified migration, beginner, README, educational, and skill guidance so
  Claude treats Main Branch updates as the required first fix through
  `/mb-update` / `mb update`, repairs one repo at a time, and explains any git
  branch as a safe draft instead of leaving beginners to decide what to merge.
- Tightened migration read-only checks to use `mb status --peek` and clarified
  that `.mb/last-status-seen.json` is local operational state, not migration
  work to commit.
- Clarified that Claude-led migration should pause after branch summaries so
  users and maintainers can review git decisions instead of having Claude push,
  open, merge, rebase, or delete branches by default.
- Added migration dogfood guidance that distinguishes structural checks from
  runtime smoke, documents command mutability, and recommends one-repo-at-a-time
  migration with `--peek` / `--check` discovery.
- Added migration guidance for static runtime-smoke fallbacks and for detecting
  old clone-path `.claude/lenses/` or `.claude/reference/` symlinks that
  skill-link repair does not yet own.
- Updated generated repo scaffolds, `mb skill link`, and checkpoint safety so
  Claude Code app `.claude/worktrees/` state is treated as local runtime output,
  not business repo work to commit.
- Clarified migration runtime smoke language so agents distinguish slash-command
  discovery and read-only core access from a full `/mb-think` workflow.
- Updated bundled skill guidance to treat `core/` and `core/offers/` as the
  canonical write paths, with `reference/core` and `reference/offers` only as
  legacy compatibility bridges, and added skill validation warnings for stale
  direct legacy path guidance.
- Retired committed business-repo `reference/` scaffolding in favor of
  canonical `core/` subfolders for proof, brand, strategy, and operations;
  expanded migration and skill validation to treat legacy `reference/*` paths
  as compatibility-only. Refs #318.

## [0.3.1] - 2026-05-05

v0.3.1 tightens the v0.3 product frame after the first public release. It
locks the operator loop language, adds checkpoint primitives for long agent
runs, removes stale third-party Meta Ads connector assumptions, and documents
how Main Branch chooses dependencies.

### What this means for you (plain English)

- **Long agent sessions can checkpoint work.** `mb checkpoint` can inspect
  dirty business repos, propose readable checkpoint messages, and save approved
  commits.
- **The product language is more stable.** Public docs and skills now use the
  Sense -> Decide -> Ship -> Reflect loop taxonomy.
- **Meta Ads setup is less misleading.** Main Branch no longer presents
  Pipeboard as the Meta Ads path and keeps official Meta support planned until
  detection and read-only smoke are wired.
- **Dependency choices are public.** Contributors can see why a dependency,
  sidecar, CLI, MCP server, or provider adapter is adopted, planned, removed,
  or declined.

### Added

- Added `docs/DEPENDENCY-CHOICES.md` to make dependency, integration, sidecar,
  CLI, MCP server, and provider-adapter judgment public, including the
  Pipeboard removal / official Meta Ads CLI planned path as the first running
  choices-log example. Closes #305.
- Added an accepted operator-readable git history decision that defines the
  business commit verb contract, Sense / Decide / Ship / Reflect loop mapping,
  checkpoint trailer guidance, and follow-up implementation slices. Closes
  #300.
- Added planning-only `mb checkpoint --plan --json` so agents can inspect
  dirty business repos, classify changed files, run safety gates, and propose
  readable checkpoint messages before commit execution ships. Refs #290.
- Added guarded `mb checkpoint --message ... --yes` execution so approved
  checkpoint plans can become readable git commits without exposing raw git
  mechanics to beginners. Refs #291.
- Added checkpoint resume facts to `mb start --json` and wired `/mb-start`,
  `/mb-end`, and `/mb-think` toward `mb checkpoint` so checkpointing can happen
  throughout long agent sessions instead of only at end-of-day. Refs #292.
- Locked the operator-loop taxonomy at four loops -- Sense, Decide, Ship,
  Reflect -- with full reasoning, alternatives considered, and the
  skills-vs-loops principle in the new decision file. Closes #306.

### Changed

- Updated Meta Ads provider readiness and bundled ad/research skills to remove
  third-party connector setup language and treat Meta's official Ads AI
  Connectors CLI path as planned until Main Branch detection and read-only
  smoke are wired. Refs #304.
- Aligned the operator-readable git history contract with the four-loop
  taxonomy from the operator-loop decision: Sense, Decide, Ship, and Reflect.
  Refs #300 and #306.
- Rewrote `docs/OPERATOR-LOOPS.md` to the four-loop taxonomy
  (Sense -> Decide -> Ship -> Reflect) with examples, anti-examples, loop
  chains, the skills-vs-loops principle, and the channels-vs-loops separation
  (Paid, Organic, Pages, Ops). Refs #306.
- Updated `docs/ETHOS.md` to the four-loop framing and renamed Principle 3
  from "Operator Sovereignty" to "The Operator Decides" so the principle
  reads in operator language without philosophy-grad-school framing. Refs
  #306.
- Aligned the four-channel framing (Paid, Organic, Pages, Ops) across
  README, ROADMAP, and OPERATOR-LOOPS, and clarified the audience as
  operators and small teams running real businesses (solo founders, small
  agencies, course creators, productized services, indie SaaS, small ecom
  teams). Refs #306.
- Updated bundled lifecycle and output skills to lean on deterministic
  `mb status --json --peek`, `mb connect plan`, `mb connect doctor --json`,
  and `mb update --repo .` facts instead of duplicating repo-health,
  provider-readiness, and update probes in skill prose. Added a `loops:` field
  to the SKILL.md frontmatter schema and extended `mb skill validate` to require
  it on every bundled skill. Skill authors maintaining third-party skills must
  backfill the `loops:` field before upgrading; existing installations with
  skills lacking the field will fail `mb skill validate`. Refs #263 and #306.
- Clarified beginner, migration, and `/mb-help` docs that `.mb/` is the current
  repo-local Main Branch state folder and `.mb-vip/` is not required. Refs
  #296.
- Added release-truth rules to the agent contract and OSS checklist so docs do
  not describe a version as shipped until CHANGELOG, GitHub Release, and PyPI
  state agree. Closes #295.

## [0.3.0] - 2026-05-04

v0.3.0 makes Main Branch better at telling a user what matters next. It adds
the first public product frame, status/ranker improvements, bets, issue
drafting, provider setup planning, and paid-traffic site readiness checks.

### What this means for you (plain English)

- **`mb status` is more useful.** It can now show deterministic drift signals,
  recent changes, ranked next actions, active bets, and paid-traffic measurement
  readiness.
- **Main Branch can capture friction.** If something is confusing or broken,
  `mb issue draft` can create a privacy-scrubbed local GitHub issue draft before
  you decide to submit it.
- **Paid site launch checks are safer.** `/mb-site`, `/mb-ads`, and
  `mb site check` now route Google Ads/GTM advice through a local readiness
  checklist instead of pretending to launch or mutate provider accounts.
- **The product direction is public.** The ethos, operator loops, roadmap,
  markdown conventions, and runtime boundary are now documented for agents and
  contributors.

### Added

- Added an accepted workspace/repo/sensitive-data boundary decision covering
  business repos, workspaces, repo/workspace/private dashboards, team daily
  logs, finance/legal data, future `mb books` behavior, and why editable files
  cannot be admin authority. Closes #274; refs #120 and #128.
- Added GitHub/Obsidian-compatible markdown and link conventions for
  frontmatter paths, body links, wikilinks, entity tags, cross-repo references,
  and optional Obsidian usage. Closes #275.
- Added `bets/` as a first-class business-repo primitive with validation,
  graph links, `mb status` active-deadline reporting, and the new `/mb-bet`
  Claude Code workflow for `new`, `update`, `close`, `list`, and `narrate`.
- Added `mb issue draft` and `mb issue open` so users can turn confusing
  Main Branch friction into privacy-scrubbed local GitHub issue drafts before
  explicitly submitting with `gh issue create`.
- Added issue-drafting docs and `/mb-help` troubleshooting guidance for when
  skills should suggest a bug, feature, or question draft without submitting on
  the operator's behalf.
- Added public ethos, operator-loop, and roadmap docs so future product work can
  anchor to the Sense -> Decide -> Ship -> Reflect loop and the current
  v0.3/v0.4 release direction.
- Added a proposed skill-to-CLI and runtime adapter contract covering lifecycle
  and production skill boundaries, Claude Code as the reference adapter,
  support levels, runtime-aware invocation hints, workflow launcher gates, and
  onboarding resume state. Refs #220.
- Added `mb status` schema v1.0 with repo-local since-last-check state,
  deterministic drift signals, `--peek` non-mutating reads, `--verbose` detail
  output, and `--no-color` human output. Refs #261.
- Added deterministic `mb status` ranked next actions with cited signals,
  confidence, and `safe_to_share` fields, plus top-three human rendering. Refs
  #262.
- Added `/mb-status` as a thin Claude Code wrapper over
  `mb status --json --peek`.
- Added `mb similar-bets <thesis>` for deterministic bets memory over
  `bets/*.md` plus graduated/dead offer context, with JSON shaped for agent,
  ranker, and future consumers. Refs #143.
- Added `mb connect plan` and `mb educational provider-readiness` so provider
  setup is presented as numbered business choices with readiness states and
  exact next commands. Refs #273.
- Added the Google Ads, GTM, and conversion tracking rubric for paid-traffic
  landers/sites, including event naming, conversion action naming, consent
  guardrails, Cloudflare Pages instrumentation, verification gates, and future
  provider-readiness states. Refs #279.
- Added `mb site check` for local paid-traffic measurement readiness checks
  covering GTM installation, `mb_*` dataLayer events, consent/privacy posture,
  Google Ads plan metadata, provider readiness summary, and manual operator
  approval gates. Refs #283.

### Changed

- Updated the README and agent instructions to point contributors and agents at
  the public product frame before making roadmap, runtime, or workflow changes.
- Clarified compatibility docs so non-Claude runtimes remain roadmap surfaces
  until each has a documented adapter and fresh-repo smoke evidence.
- Updated `/mb-start` to read deterministic status/ranker facts before asking
  setup or routing questions. Refs #263.
- Extended `mb validate --cross-refs` to warn on missing or ambiguous
  Obsidian-style wikilinks while keeping wikilink checks out of default
  validation.
- Updated beginner setup and provider docs to teach GitHub, Cloudflare,
  Google/Workspace, Meta Ads, and Apify readiness without claiming unsupported
  provider workflows. Refs #273 and #144.
- Updated `/mb-site`, `/mb-ads`, and `/mb-start` guidance to route
  paid-traffic launch advice through the Google Ads/GTM rubric and
  deterministic `mb site check` facts before recommending any launch step. Refs
  #283.
- Clarified `/mb-site` business-repo mode versus site-repo mode, including
  `.mainbranch/source.json` source links and a progressive `/mb-help` answer
  for where to start Claude during site work. Refs #283.

## [0.2.6] - 2026-05-04

v0.2.6 adds `/mb-update` as the beginner-facing Claude Code update command
while keeping `/mb-pull` as a compatibility alias for existing users.

### What this means for you (plain English)

- **Use `/mb-update` going forward.** It matches the terminal command
  `mb update`, so new users only need to remember one word.
- **Old `/mb-pull` still works.** Existing users can keep using it while docs
  and onboarding copy move to `/mb-update`.

### Added

- Added `/mb-update` as the preferred Claude Code update skill so the slash
  command matches the CLI command `mb update`.

### Changed

- Kept `/mb-pull` as a legacy alias for existing users while public docs now
  teach `/mb-update`.

## [0.2.5] - 2026-05-04

v0.2.5 finishes the noob-safe migration loop for past users with broken
personal Claude Code skill symlinks from older Main Branch setups.

### What this means for you (plain English)

- **Old broken `/start`-style symlinks are cleaned up automatically.** Running
  `mb skill link --repo .` now backs up broken personal symlinks with Main
  Branch skill names before wiring the current `/mb-start` skill set.
- **Real personal or third-party skills are still protected.** Main Branch only
  moves stale Main Branch links and broken symlinks with Main Branch current or
  legacy names; directories, real files, and live third-party links are
  reported but not moved.

### Fixed

- `mb skill link --repo .` and `mb skill repair --repo . --apply` now move
  broken personal Claude Code symlinks with Main Branch current or legacy skill
  names to timestamped backups instead of leaving old `/start`, `/think`, and
  similar traps in place. User-authored directories, real files, and live
  third-party skill links remain report-only.

## [0.2.4] - 2026-05-04

v0.2.4 is the noob-safe migration and provider-trust release. It moves bundled
Claude Code skills to collision-resistant `mb-` names, adds repair tools for
legacy global skill wiring, makes legacy migration checks privacy-safe by
default, and stops treating stored provider credentials as healthy until they
are validated.

### What this means for you (plain English)

- **Skill commands are now prefixed.** New and repaired repos use `/mb-start`,
  `/mb-think`, `/mb-ads`, and the rest of the `mb-` skill set so Main Branch is
  less likely to collide with personal or third-party Claude Code skills.
- **Old installs have a safer repair path.** `mb skill repair --repo .`,
  `mb skill link --repo .`, `mb doctor`, and `mb start --json` can explain and
  repair stale wiring without deleting unrelated user-authored skills.
- **Migration checks are private by default.** Legacy repo migration plans show
  path/action summaries unless you explicitly ask for full diffs.
- **Connected accounts must prove they work.** `mb connect test <provider>` and
  `mb connect doctor` distinguish missing, unvalidated, invalid, and ready
  credentials without printing secrets.

### Added

- `mb skill repair --repo .` detects personal Claude Code skills that shadow
  Main Branch's project-local wiring, reports each entry's resolved target, and
  moves only provably stale Main Branch symlinks to a timestamped backup when
  run with `--apply`.
- Bundled Claude Code skills now use collision-resistant `mb-` names such as
  `/mb-start`, `/mb-think`, `/mb-ads`, and `/mb-pull`; fresh business repos only
  wire the prefixed names.
- Bundled skill validation now fails if an engine-bundled skill lacks the
  `mb-` vendor prefix, so `scripts/check.sh` and CI catch future regressions.
- Added a Claude Code plugin prototype manifest at `.claude-plugin/plugin.json`
  with the `mainbranch` namespace and the current `.claude/skills/` payload.
  This does not replace `mb skill link` yet; runtime smoke still decides when
  plugin packaging becomes default.
- `mb migrate --check` now defaults to a privacy-safe path/action summary;
  use `--diff` explicitly to print full unified diffs that may include private
  legacy business content. JSON output also omits full diff text unless
  `--diff` is present.
- Added `mb connect test <provider>` and `mb connect doctor` so users and
  onboarding agents can distinguish missing, unvalidated, invalid, and ready
  provider credentials without printing secret values or raw provider
  responses. Providers without a safe API probe can complete the test with an
  explicit "no automated probe yet" summary instead of looping forever. The
  JSON output now includes safe repair fields such as `state`, `summary`,
  `repair`, `repair_command`, and `safe_to_share`.
- Decision doc `decisions/2026-05-03-skill-distribution-and-migration.md`
  records the proposed skill distribution and migration model: keep
  project-local symlink wiring as the v0.2 supported adapter, ship stale
  global skill detection and migration first, and target Claude Code plugin
  packaging as the durable destination because the bundled skill names are
  generic enough that plugin namespacing (not symlink hygiene) is the only
  collision-proof escape. Includes evidence drawn from public Claude
  Code skill repos (Every.to's `compound-engineering-plugin` enforces a
  `ce-` prefix in CI; `mattpocock-skills` ships unprefixed and would
  collide with bundled Main Branch skill names today). Adds a follow-up
  to decide whether to rename bundled skills to a `mb-` prefix before
  the plugin spike lands. Refs #236 and #234.

### Changed

- `mb migrate --repo <repo> status` now honors the root `--repo` option, matching
  `mb migrate status --repo <repo>`.
- `mb skill link --repo .` removes stale Main Branch/VIP-era engine paths from
  `.claude/settings.local.json` when it rewrites the active engine path.
- Bundled migration/setup copy now routes old users through `mb skill link`,
  `mb skill repair`, `mb doctor`, and `mb start --json` instead of old clone-era
  manual setup instructions.
- `mb connect status --json`, `mb doctor`, and `mb status` no longer treat a
  stored secret ref as provider health. Stored credentials report
  `unvalidated` until `mb connect test <provider>` succeeds, and repair output
  names the affected provider plus the next command.
- Transient provider validation failures, such as rate limits, network errors,
  and 5xx responses, remain `unvalidated` instead of being reported as invalid
  credentials that need rotation.
- GitHub integration health now distinguishes missing `gh`, unauthenticated
  `gh`, missing GitHub remotes, non-git folders, and ready GitHub repo context
  in secret-safe status and doctor output.

### Fixed

- v0.1-to-v0.2 path migration now ignores local OS metadata such as `.DS_Store`,
  `Thumbs.db`, `Desktop.ini`, and AppleDouble `._*` files.
- `mb validate` now adds a legacy frontmatter repair explanation after migrated
  repos fail current schema checks, distinguishing content-schema debt from
  layout migration failure.

## [0.2.3] - 2026-05-03

v0.2.3 makes Main Branch easier to resume after an interrupted first run and
turns `mb graph` into a useful deterministic index for future dashboard,
status, and agent-workflow work.

### What this means for you (plain English)

- **Onboarding can survive multiple sessions.** `mb onboard` now writes a
  lightweight local progress file so agents can tell what setup inputs are
  still missing without relying on the previous chat transcript.
- **`mb status` and `mb doctor` know about onboarding gaps.** They can point a
  beginner or agent back to the next setup step instead of silently treating an
  empty repo as ready.
- **`mb graph --json` now exposes real structure.** Files, frontmatter links,
  wikilinks, and business entities become a machine-readable graph index.
- **The public operating contract is clearer.** Contributors and agents now
  have a public checklist for release readiness, runtime claims, issue/PR
  discipline, and public/private boundaries.

### Added

- Added `.mb/onboarding.json` as the lightweight onboarding progress contract,
  plus `mb onboard status` and `mb onboard plan` for human and JSON resume
  surfaces.
- Added `mb graph --json` as a deterministic repo graph index for files,
  frontmatter links, wikilinks, and first-class people, companies, offers,
  channels, competitors, and metrics entity nodes while keeping DOT output as
  the default scriptable view.
- Added `docs/OSS-OPERATING-CHECKLIST.md` as a public checklist for
  Main Branch product-boundary, release-readiness, runtime-claim,
  public/private, state-model, and issue/PR discipline, and linked it from
  agent and contributor docs.
- Added a public-safe `mb connect` dogfood report documenting credential storage
  behavior, beginner-facing repair gaps, and follow-up integration issues.

### Changed

- `mb status` and `mb doctor` now surface incomplete onboarding progress so
  agents can resume setup without relying on the previous chat transcript.
- New and repaired business repos now gitignore `.mb/onboarding.json`; use
  `--path` for scripted `mb onboard` repo paths now that `onboard` also has
  `status` and `plan` subcommands.

## [0.2.2] - 2026-05-03

v0.2.2 turns the v0.2 command surface into a better operating foundation. It
adds the first credential/integration registry, validates bundled skills as
product code, and clarifies how per-repo connected accounts should stay tied to
the active business repo.

### What this means for you (plain English)

- **`mb connect` now has a foundation.** You can list known providers, check
  connected status, and import credentials explicitly from environment
  variables into local storage without committing secrets.
- **Skill packaging is checked before release.** `mb skill validate --all`
  verifies bundled skills are self-contained, have valid frontmatter, and stay
  under the line-count gate.
- **`mb doctor` can catch more broken installs.** Doctor and CI now run bundled
  skill validation, so missing skill references surface before users hit them.
- **Connected tools stay repo-tethered.** Main Branch docs and generated
  `CLAUDE.md` now tell users to keep ads, Stripe, pixels, MCP tools, and other
  accounts connected to the active business repo instead of treating them as
  global magic.

### Added

- Added `mb skill validate <name>` and `mb skill validate --all` to check
  bundled skill frontmatter, self-contained local references, and the 500-line
  `SKILL.md` gate with JSON output for agents and CI.
- Added `mb connect` with a provider registry, `list` and `status` views,
  explicit `--from-env` credential import, local secret storage outside git,
  repo-safe `.mb/connect.yaml` metadata, and doctor/status integration health
  reporting.

### Changed

- Documented per-repo connected-account boundaries in the generated business
  `CLAUDE.md`, README, `mb init`, and `mb onboard` output so users keep Stripe,
  ads, pixels, and MCP tool access tethered to the active business repo without
  committing secrets.
- `mb doctor` and CI now run bundled skill validation so broken skills are
  caught before release.

## [0.2.1] - 2026-05-02

v0.2.1 is the first post-0.2 durability release. It makes the new CLI front
door safer for existing users, gives `mb` better GitHub-native briefing data,
adds schema migration machinery for old business repos, and gates `/ads`
compliance rewrites behind explicit approval.

### What this means for you (plain English)

- **Old installs now get a clear update warning.** If your Main Branch install
  is too old for the current setup and skill-link flow, `mb`, `mb doctor`,
  `mb status`, and `mb start` tell you to run `pipx upgrade mainbranch`, then
  `mb skill link --repo .` and `mb doctor`.
- **Existing repos have a migration path.** `mb migrate status`,
  `mb migrate --check`, and `mb migrate --apply` can move legacy
  `reference/core` and `reference/offers` layouts into the current `core`
  layout with a repo-local backup and compatibility links.
- **`mb status` knows more about GitHub work.** When `gh` is available and
  authenticated, the briefing now separates assigned tasks, attention requests,
  open proposals, shipped proposals this week, recently closed tasks, and
  blocked/stale tasks.
- **`mb validate` can catch stale links before they spread.** Use
  `mb validate --cross-refs` to warn on missing local frontmatter references
  and orphan offer directories; add `--strict` when CI should fail on those
  warnings.
- **`/ads` review no longer silently rewrites copy.** Compliance findings are
  rendered as proposed diffs first and only applied after explicit approval.

### Added

- Added shared package freshness metadata and beginner-safe update alerts for
  stale installs.
- Added `mb migrate` with `status`, `--check`, `--apply`, JSON envelopes,
  unified diffs, backups under `.mb/backups/`, schema markers, and v0.1-to-v0.2
  path migration support.
- Added schema-drift detection to `mb doctor`.
- Added GitHub activity collection primitives backed by `gh` for richer
  `mb status` output and downstream dashboard/runtime consumers.
- Added `mb validate --cross-refs` and `--strict` for known local
  frontmatter references and offer-directory checks.
- Added an internal `/ads` compliance gate helper that dry-runs proposed copy
  fixes, skips ambiguous replacements, and writes changes only after approval.

### Changed

- `mb status` now reports business-language GitHub sections instead of only raw
  assigned issues, review requests, and merged PRs.
- `mb doctor`, `mb status`, and `mb start` now expose stable update metadata in
  JSON for agent and future dashboard consumers.
- New `mb init` repos now include `.mb/schema_version` and ignore
  `.mb/backups/`.
- `docs/MIGRATING.md` now points existing users at the automated migration
  command before the manual fallback.

### Fixed

- `/ads` compliance review now proposes P2/P3 copy edits as a diff and keeps
  source copy unchanged unless the user approves.
- Compliance copy replacement refuses repeated ambiguous evidence and avoids
  compounding replacements against already-proposed text.

## [0.2.0] - 2026-05-02

v0.2.0 makes `mb` feel like the front door to Main Branch. The release stays
terminal-first and Claude-Code-first, but the CLI now owns first-run setup,
daily repo briefing, runtime handoff, and install-mode-aware updates.

### What this means for you (plain English)

- **Running `mb` now gives you a starting point.** In an interactive terminal,
  bare `mb` shows a short launch screen with the main trails: onboard, status,
  start, doctor, and full help.
- **New users get a guided setup path.** `mb onboard` creates or connects a
  business repo, explains the local files / git / GitHub model, wires the
  bundled Claude Code skills, and prints the next `/start` step.
- **Daily work has a model-free briefing.** `mb status` summarizes repo shape,
  git state, runtime wiring, recent decisions/research, and GitHub task context
  when `gh` is available.
- **Runtime handoff is explicit and repairable.** `mb start` checks whether the
  business repo, git work tree, Claude Code executable, and `/start` skill wiring
  are ready, then prints the exact command to run or launches Claude Code with
  `--launch`.
- **Updates are install-mode aware.** `mb update` handles pipx installs and
  clone/source installs without pretending every user has a git checkout.

### Added

- Added a TTY-aware bare `mb` launch screen. Non-interactive callers and
  `mb --plain` still receive normal Typer command help.
- Added `mb onboard` for human first-run setup. It supports interactive use,
  `--yes` for scripted setup, `--json` for smoke tests, and guarded connect mode
  for existing Main Branch repos.
- Added `mb status` as the first daily briefing primitive. It reports repo
  readiness, runtime/skill wiring, git activity, local brain files, validation
  stats, and GitHub issue/PR context when authenticated.
- Added `mb start` as the runtime handoff helper. It emits structured JSON,
  blocks unsafe `--json --launch` combinations, and keeps Claude Code launch
  opt-in.
- Added `mb update` for install-mode-aware engine refreshes. It detects pipx vs
  clone installs, supports `--check` dry-runs, emits `--json` result envelopes,
  and refreshes skill links after updates.
- Added Linear release sync after successful PyPI publish so Linear release
  completion tracks package availability rather than merge state.
- Added release-path wheel smokes for bare `mb`, `mb --plain`, `mb onboard`,
  `mb status`, `mb start`, `mb update --check --json`, and Claude Code skill
  wiring from the built wheel.

### Changed

- Reframed the README around the operating thesis before the command list:
  Main Branch is a GitHub-native business operating system, with `mb` as the
  deterministic CLI layer and agent skills as the judgment layer.
- Updated `/pull` so the skill delegates mechanical update work to `mb update`
  and keeps ownership of the human-readable changelog summary.
- Updated the v0.2 first-run PRD so the merged launch-loop issues are marked
  closed/merged and remaining dashboard/connect/graph work stays deferred.

### Fixed

- `mb onboard --mode connect` no longer mutates arbitrary uninitialized
  directories before rejecting them.
- `mb start --json --launch` now exits with a structured error instead of
  launching Claude Code and contaminating JSON output.

## [0.1.2] - 2026-05-01

v0.1.2 is a public framing and package-metadata release. It does not change
installed behavior; it makes the repo, PyPI metadata, and decision history
match the accepted runtime-agnostic product boundary.

### What this means for you (plain English)

- **Claude Code is still the supported v0.1 runtime.** Nothing changes for
  existing members or new `pipx install mainbranch` users.
- **Main Branch is not Claude-Code-only forever.** The public engine now
  states the intended runtime posture clearly: Claude Code first, with Codex,
  Cursor, OpenClaw, Hermes, and local runtimes targeted later.
- **`mb` stays the stable control layer.** It owns repo shape, validation, status,
  migration, updates, graphing, and runtime wiring. Agent runtimes own
  judgment-heavy workflows.

### Changed

- Added the accepted decision
  `decisions/2026-05-01-mb-cli-vs-agent-workflows-boundary.md`.
- Updated README, compatibility docs, package description, and PyPI long
  description language around runtime-agnostic positioning.
- Amended the v0.1 master decision so its historical runtime list points to the
  accepted runtime-agnostic boundary and includes OpenClaw as a first-tier
  public compatibility target.

## [0.1.1] - 2026-05-01

v0.1.1 makes the public `pipx install mainbranch` path work end-to-end
for Claude Code users. v0.1.0 published the package and bundled skills;
this patch wires those bundled skills into new business repos so `/start`,
`/think`, `/ads`, and the rest are discoverable without cloning the
engine repo.

### What this means for you (plain English)

- **New members can use the simple install path.** Run
  `pipx install mainbranch`, then `mb init`, then start Claude in the new
  business repo and run `/start`.
- **Existing clone-based members are not broken.** If your business repos
  already link to a local Main Branch checkout, that flow still works.
- **Updates now match your install type.** pipx users upgrade with
  `pipx upgrade mainbranch`; clone users still pull the engine repo.
  `/pull` now explains and runs the right path.
- **`mb doctor` catches broken skill wiring.** If `/start` is not
  discoverable, it tells you to run `mb skill link --repo .`.

### Fixed

- **`mb init` now writes Claude Code wiring.** It creates
  `.claude/settings.local.json`, points `additionalDirectories` at the
  active Main Branch engine root, and creates per-skill bridge links under
  `.claude/skills/`.
- **Wheel layout now preserves the full engine shape.** Build artifacts
  copy repo-root `.claude/` into `mb/_engine/.claude/`, including
  `skills/`, `playbooks/`, `reference/`, `lenses/`, `educational/`, and
  `scripts/`. Relative skill links such as `../../reference/...` now work
  from an installed wheel.
- **`mb skill list` and `mb skill path` use the active engine root.** They
  work against the packaged wheel layout and the source checkout layout.
- **`/pull` is install-mode aware.** Clone-based installs still run
  `git pull`; pipx installs run `pipx upgrade mainbranch` and refresh
  skill links with `mb skill link --repo .`.
- **Bridge links are gitignored.** `mb init` and `mb skill link` add
  machine-local `.claude/settings.local.json` plus per-skill bridge links
  to `.gitignore`.

### Added

- **`mb skill link --repo <path>`** to repair or refresh Claude Code skill
  discovery for an existing business repo.
- **`mb educational upgrading-mainbranch`** with the short explanation for
  pipx upgrades and clone-based updates.
- **Release-path wheel smoke coverage** for the installed engine root,
  reference files, `mb init` settings, and bridge-link discovery.

## [0.1.0] - 2026-05-01

First public engine release. The engine is now a real Python package
(`mainbranch` on PyPI, `mb` CLI) with a six-folder business-as-files
taxonomy and a /site shape upgrade that adopts Chase Hughes' 9-archetype
narrative framework as the brief layer. The CLI surface is smoke-tested
end-to-end, and the release wheel now bundles skills and playbooks as
package data so `mb skill list` works without a source checkout.

Locked under `decisions/2026-04-29-mb-vip-v0-1-0-master.md` (the engine
master) and the matching noontide-projects business master at
`decisions/2026-04-29-main-branch-v0-1-0-master.md`.

### What this means for you (plain English)

If you're a Main Branch member, here's what changes in your day-to-day:

- **Nothing breaks.** Your existing setup keeps working. The skills you
  already use (`/start`, `/think`, `/site`, `/ads`, etc.) are in the same
  place and still get pulled into your business repo.
- **You'll see a one-time "what's new" banner** the next time you run
  `/start` or `/pull`. After that, things go quiet again until v0.2.
- **`/site` got smarter about brand voice and storytelling.** When you
  build a marketing site, it now asks you to pick a story archetype
  (like "wounded healer" or "David vs Goliath") and writes copy that
  fits that frame instead of generic SaaS-speak. There's a new review
  pass that catches the most common AI-writing tells (em-dashes,
  "in today's fast-paced world," that kind of thing).
- **A new `mb` command-line tool exists** but you don't need to install
  it to use Main Branch. It's the start of an installable engine
  (`pipx install mainbranch`) for people who want to run mb without
  cloning the repo manually. Optional today; canonical later.
- **The repo is now versioned like a product.** This release is `0.1.0`.
  Future releases get visible version numbers, a CHANGELOG (this file),
  and a "what's new" banner so you don't have to read commit logs to
  know what changed.

If you're an OSS contributor or you want the technical detail, the
sections below cover what shipped in PRs #114 / #115 / #116 / #117 /
#153 / #160 / #161.

### Added — final public release prep (PRs #153 / #160 / #161)

- **MIT LICENSE** at repo root for the public release.
- **Public repo metadata and docs** moved to `noontide-co/mainbranch`.
  README, beginner setup, package URLs, publish workflow comments, and
  template docs now point at the new public repo path.
- **PyPI trusted-publisher target** locked to
  `owner=noontide-co, repo=mainbranch, workflow=publish-pypi.yml, env=pypi`.
- **Wheel-time skill/playbook bundling.** `setup.py` copies
  repo-root `.claude/skills/` and `.claude/playbooks/` into
  `mb/_data/skills/` and `mb/_data/playbooks/` during sdist/wheel builds.
  Source stays single-copy in `.claude/`; generated copies are not
  committed.
- **Wheel smoke now asserts a populated skill bundle.** CI checks for
  `mb/_data/skills/start/SKILL.md`, `mb/_data/playbooks/ship-bet/SKILL.md`,
  and verifies fresh wheel installs print `start` and `think` from
  `mb skill list`.
- **Public VSL example cleanup.** Real names, hard dollar claims, MRR
  proof, and Ads Lab-specific proof claims were replaced with clearly
  fictionalized composite examples and guidance to use only approved
  testimonials.

### Added — V1 translation (PR #116)

- **`mb` umbrella package** (PyPI: `mainbranch`). Typer CLI with
  subcommands `init`, `doctor`, `validate`, `graph`, `think`, `resolve`,
  `educational`, `skill list`, `skill path`. Replaces ad-hoc bootstrap
  scripts.
- **/site skill upgrade** to the one-flow shape: brief → review → lock →
  setup → conversion endpoint → 2 home concepts on localhost → pick →
  publish raw → build out → publish. Brief now requires explicit
  archetype + audience-current-archetype selection (Hughes 9-archetype
  framework). Paired-imagery rule replaces "what does this section say"
  with "what two things does this section put next to each other."
  Stubs land for 5 of the 9 archetypes (to be filled out in a future release).
- **Seven Sweeps review pass** (`.claude/skills/site/references/review.md`).
  Anti-pattern catalogue for AI-generated marketing copy with the
  "AI tells" reference (`ai-tells.md`).
- **Repo reorg**: `mb/` (Python package), `tools/` (auxiliary CLIs and
  stubs), `templates/` (scaffolding payloads), `experimental/`,
  `playbooks/` skeletons, `.claude/educational/` for diagnostic prompts.
- **CI matrix** across Python 3.10/3.11/3.12 with ruff format check, ruff
  lint, mypy strict, pytest with coverage, plus a SKILL.md ≤ 500-line gate.
- **PyPI publish workflow** (`.github/workflows/publish-pypi.yml`).
  Trusted-publisher OIDC, gated on a `pypi` GitHub Environment with
  required reviewer. Triggered by GitHub Release on `oe-v*` tags.
- **5 SKILL.md refactors** to keep every skill under the 500-line gate:
  `/start`, `/setup`, `/think`, `/end`, `/wiki`, `/site`, `/ads`.
  Long content moved to `references/` files loaded lazily.

### Added — Codify batch 1 (PR #114)

- `reference/visual-identity/` reference set (covered in detail by PR #115).
- 3 educational stubs at `.claude/educational/` —
  `anti-cloud-backup.md`, `cloudflare-vs-vercel.md`,
  `github-vs-gdocs.md`. Powers the `mb doctor` "tell me more" prompts.

### Added — Visual-identity sweep (PR #115)

- Full visual-identity reference build under
  `reference/visual-identity/` for the consumer repo template. Image
  generation prompts, type pairing, palette tokens, paired-imagery
  recipes per archetype.

### Changed

- **Engine repo renamed `vip` → `mb-vip`** to match the `mb` CLI binary.
  The PyPI package is `mainbranch`.
- **`additionalDirectories` is now the canonical loading mechanism** for
  vip; bridge symlinks in business repos are a compatibility fallback
  for skill discovery.
- **Decision file `2026-04-29-mb-vip-v0-1-0-master.md` mirrors
  noontide-projects #89.** The two masters are paired contracts: business
  thesis + naming + pricing on one side, engine surface + ship gates on
  the other.

### Notes / follow-ups

- The 5 archetype stubs (victim, tragedy-mindset, dark-hero, redemption,
  tragic-comedy) ship as `status: stub` and are promoted to full detail
  files in a future release.
- `tools/` contains stubs for future OSS carve-outs (research-pack pivot
  per `project_d100_research_pack_pivot_20260420.md`).
- `playbooks/` ships skeletons; full playbook content lands incrementally.

## [0.0.x] - pre-2026-04-29

Pre-V1 dev releases. Internal-only. Documented in git history; not
re-summarised here.
