# Changelog

All notable changes to Main Branch (`mainbranch` / `mb`) will be documented in
this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The release tag scheme is `oe-vMAJOR.MINOR.PATCH` ("oe" = open engine) — the
PyPI distribution `mainbranch` tracks the same version sequence.

## [Unreleased]

### Added

- Added a `tighten_bet_exit_criteria` ranked action so active bets without
  predeclared kill/double-down criteria surface as an owner-facing next move in
  `mb status --json --peek` instead of staying buried in raw `brain.bets` facts.
  Routes to `/mb-bet` and keeps writes approval-gated. Closes #789.

### Changed

- Changed daily start/status JSON to separate repo/runtime readiness from
  business-memory completeness, align `mb start --json` next actions with
  status-ranked owner actions when runtime handoff is ready, clarify Codex
  workflow inventory shape, and frame read-only repair plans with findings as
  usable plans. Closes #788.

## [0.3.41] - 2026-05-28

v0.3.41 packages the fact-grounded, owner-facing next-action intelligence train.
It makes `mb status` / `mb start` and the core lifecycle routes better at
surfacing one useful next move from deterministic facts without widening into
repo profiles, provider mutation, scraping, export, or collaborator handoff.

### Added

- Added deterministic repo-boundary helper facts to `mb status --json --peek`,
  `mb start --json`, and onboarding status so agents can guide same-repo,
  separate-business-repo, or child/lightweight-repo setup decisions without
  inventing repo profiles. Closes #631.
- Added MoneyPath appetite-threshold and active-bet exposure facts to
  `mb status --json --peek`, with safe aggregate routing for missing
  thresholds, unanchored bets, and over-cap bets. Closes #645.
- Added optional safe MoneyPath threshold inputs to `mb onboard` and
  `mb onboard plan`, preserving interim answers in gitignored
  `.mb/onboarding.json` and writing confirmed policy to `core/finance/books.md`.
  Closes #646.
- Added a public-safe MoneyPath archetype dogfood report covering solo
  founder/creator, agency/service, and product/SaaS repos. The report records
  MoneyPath levels, top actions, recommendation interpretation, false
  positives, false negatives, and follow-up calibration notes. Closes #532.

### Changed

- Changed daily start/status guidance to preserve `brain.bets.*` trigger facts
  for active, overdue, due-soon, missing-exit, failure-signal, and
  double-down-signal routing. Closes #763.
- Changed `mb-think` guidance to use the current `runtime.codex_cli` fact path
  instead of the stale `runtime.codex` path. Closes #763.

### Fixed

- Added a guided `pipx install --force mainbranch==<latest>` recovery step when
  `mb update` detects that `pipx upgrade mainbranch` failed because pipx could
  not parse a saved local wheel/package spec. Closes #778.
- Fixed Claude `/mb-end` crystallize guidance so durable write language remains
  approval-gated. Closes #763.

## [0.3.40] - 2026-05-27

v0.3.40 packages the shared workflow migration batch for the daily Main Branch
routes and the first canonical Google Ads launch playbook source.

### Added

- Added a public business-file contract spec and the first reusable
  file-contract engine slice. `mb validate --json` and `mb status --json
  --peek` now expose offer-shape findings with owner-facing messages and
  guided routes to existing Main Branch workflows. Refs MAIN-459, #756.

### Changed

- Migrated `mb-ads` to a shared workflow source with checked Claude and Codex
  shells, preserving read-only Codex boundaries for paid creative planning,
  Google Ads launch planning, provider mutation, uploads, publishing, spend,
  account changes, GTM publishes, conversion uploads, and customer contact.
  Closes #750.
- Tightened core lifecycle skill guidance so `mb-think` uses the real
  `runtime.codex_cli` fact path, daily start/status preserves explicit bet
  trigger facts, and `/mb-end` crystallize writes remain approval-gated.
  Closes #767.
- Migrated `mb-site` to a shared workflow source with checked Claude and Codex
  shells, preserving read-only Codex boundaries for site writes, builds,
  deploys, publishing, domain/DNS changes, provider mutation, account changes,
  spend, and customer contact. Closes #749.
- Migrated `mb-organic` to a shared workflow source with checked Claude and
  Codex shells, preserving read-only Codex boundaries for planning, source
  privacy, publishing, account mutation, and customer-contact gates. Closes
  #752.
- Migrated the mb-bet lifecycle to a shared workflow source with checked Claude
  and Codex shells, preserving read-only Codex boundaries until runtime smoke
  proves write support. Closes #751.
- Purged retired folder-taxonomy vocabulary from current agent-facing guidance
  and generated business-repo instructions, keeping old `reference/*`,
  `campaigns/`, and `outputs/` handling in explicit migration/repair contexts.
  Refs MAIN-460, #759.

### Fixed

- Packaged root reusable playbook sources into the wheel `_engine` payload so
  `mb workflow list --runtime codex --json` source paths resolve for installed
  `mainbranch` users. Refs #750.

### Removed

- Retired the provisional `ship-bet` and `weekly-review` skeletons from bundled
  reusable playbook packaging while preserving marker-driven cleanup for stale
  generated Codex global skill directories. The concepts remain future workflow
  candidates, not rejected product ideas. Refs MAIN-458, #753.

## [0.3.39] - 2026-05-26

### Changed

- Changed `mb workflow list --json` to classify business workflow and playbook
  surfaces with explicit reason and next-issue metadata, while hiding
  provisional playbooks from default user-facing Codex global skills. Refs
  MAIN-452, #743.
- Changed daily start/status, setup, update, and repair Codex routes to use
  canonical shared workflow sources, with checked Claude and Codex shell
  snapshots and workflow inventory entries naming the source files. Refs
  MAIN-451, #742.
- Changed `mb-end` to use a canonical shared closeout workflow source, with
  checked Claude and Codex shell snapshots covering status scan, checkpoint
  planning, final thought capture, crystallize, owner-facing save states, and
  approval-gated saves. Refs MAIN-448, #739.
- Changed generated Codex global skills for shared-source routes to render from
  the canonical workflow source, with inventory fields distinguishing shared
  sources, Claude shells, Codex global skills, read-only planning, and pending
  migrations. Refs MAIN-449, #740.
- Changed `mb workflow list --json` to expose the canonical workflow
  architecture and a source-of-truth status for each Codex route, distinguishing
  shared workflow sources, temporary source-skill mirrors, pending migrations,
  and intentionally unsupported surfaces. Refs MAIN-447, #738.
- Changed generated Codex `AGENTS.md` freshness to use hidden schema/template
  metadata instead of a visible exact package version sentence, reducing
  business-repo diffs for patch releases that do not change the guidance
  content. Refs #736.

### Fixed

- Fixed `mb workflow list` human output so workflow status labels render
  visibly, and made retired Codex playbook skill cleanup remove only generated
  Main Branch skill directories. Refs MAIN-452, #743.

## [0.3.38] - 2026-05-25

### Fixed

- Fixed Codex guidance freshness checks so `mb doctor repair --plan --only
  codex` detects stale generated `AGENTS.md` version markers and refreshes the
  repo guidance after package updates. Refs #731.

## [0.3.37] - 2026-05-25

### Changed

- Made `mb doctor repair` agent-surface writes explicit: operators can plan or
  apply Claude-only, Codex-only, or reviewed all-agent repairs, and JSON reports
  now include detected surfaces, touched files, receipts, skipped surfaces, and
  refresh notes. Refs MAIN-440, #722.
- Clarified `mb update` surface refresh behavior and added an explicit
  `--no-refresh-surfaces` escape hatch for package-only updates. Refs MAIN-440,
  #722.

## [0.3.36] - 2026-05-24

v0.3.36 corrects the Codex support surface after v0.3.35. Codex now follows the
plain global skill bundle model under the Codex skills root instead of treating
plugin slash commands as readiness.

### Fixed

- Corrected Codex support to install a global Main Branch skill bundle under
  the Codex skills root, with one generated skill/playbook folder per supported
  or inventoried workflow. Codex readiness now requires current global skills,
  current repo `AGENTS.md`, and the current runtime `mb`; plugin command state
  is no longer part of readiness. Refs MAIN-439, #721.

## [0.3.35] - 2026-05-24

### Changed

- Added a clean global Codex `/mb-*` command surface for Main Branch: repair now
  generates command files under the global plugin, removes the old visible
  `main-branch-owner-loop` skill/plugin source, and readiness only passes when
  the command files are current and the plugin is installed/enabled. Refs
  MAIN-437, #717.
- Updated `mb update` so package/source updates refresh Claude Code skill links
  and then run the Codex command-surface repair from the upgraded `mb`
  executable; Codex users still restart Codex to reload `/mb-*` commands.

## [0.3.34] - 2026-05-23

v0.3.34 packages the Codex live workflow surface after v0.3.33. Codex starts
from generated Main Branch guidance, the global Codex plugin, and deterministic
`mb` facts; fresh onboarding now points users at that supported path directly.

### Changed

- Clarified the supported Codex path as generated Main Branch guidance delivered
  by the global Codex plugin and grounded in deterministic `mb` facts. Refs
  MAIN-434, #709.
- Removed unproven Codex command-file shims from the generated global plugin;
  Codex support now starts from the plugin guidance and deterministic `mb`
  facts. Refs MAIN-434, #709.
- Updated fresh business-repo onboarding and README guidance so Codex users are
  told to ask Codex for a read-only `mb`-fact start instead of running
  unsupported `/mb-start` slash commands. Refs MAIN-435, #712.
- Extended the Codex workflow inventory to account for every bundled Claude
  `mb-*` skill source, keeping full workflow parity as an explicit routing
  ledger instead of an implied owner-loop subset. Refs MAIN-433, #707.

### Fixed

- Fixed Codex-only doctor repair so a missing global Main Branch Codex plugin is
  still installed when repo guidance is current but the Codex runtime PATH has a
  warning. Refs MAIN-436, #714.

## [0.3.33] - 2026-05-23

v0.3.33 packages the global-only Codex owner-loop plugin model after v0.3.32.
It retires the brief repo-local Codex plugin default so users install one global
Main Branch plugin while business repos keep lightweight `AGENTS.md` guidance.

### Changed

- Pivoted Codex owner-loop slash commands to a global Main Branch plugin install
  model: business repos keep lightweight `AGENTS.md` guidance, while
  `mb doctor repair --only codex` installs or repairs the global plugin source
  and Codex marketplace registration. Refs MAIN-431, #703.

## [0.3.32] - 2026-05-23

v0.3.32 packages the Codex readiness truth cleanup after v0.3.31. It keeps the
proven Codex owner-loop handoff native and treats installed/enabled Codex plugin
slash commands as part of readiness, so `mb` no longer reports ready while
`/mb-*` commands are absent.

### Changed

- Made `mb start --json` top-level next actions prefer Codex-facing handoff
  and smoke commands when Codex owner-loop readiness is present, while keeping
  Claude launch details in the Claude command section. Refs MAIN-428, #697.
- Made Codex plugin install state part of Codex readiness so status, start,
  doctor repair, and update follow-ups distinguish current adapter files from
  installed/enabled `/mb-*` slash commands. Refs MAIN-430, #700.

## [0.3.31] - 2026-05-23

v0.3.31 packages the post-v0.3.30 Codex readiness follow-ups. It tightens
generated Codex guidance around runtime `mb` mismatches and tunes release
simulation scoring so future release acceptance runs flag real routing misses
instead of acceptable business-language routing.

### Changed

- Tightened generated Codex owner-loop guidance so runtime `mb` mismatches
  reported by `mb status` or `mb start` stop the session before additional
  owner-loop checks, and added Codex-specific start handoff next actions.
  Refs MAIN-426, #692.
- Tuned the release-simulation `loop_routing` rubric so release acceptance
  recognizes clear business-language routing while generic no-routing answers
  still fail. Refs MAIN-425, #691.

## [0.3.30] - 2026-05-22

v0.3.30 packages the Codex runtime readiness follow-up after v0.3.29. It
keeps the supported Codex owner loop honest when a login shell would resolve a
different `mb` binary, and it narrows Codex repair guidance to the scoped
adapter path when only Codex wiring needs repair.

### Added

- Added Codex runtime `mb` path/version diagnostics so status, start, and doctor
  can warn when the login-shell runtime would execute a stale Main Branch
  binary even though generated Codex adapter files are current. Refs MAIN-424,
  #688.

### Changed

- Scoped Codex adapter repair through `mb doctor repair --only codex` and
  updated `mb update` plus generated Codex guidance to point operators at the
  focused repair and runtime `mb --version` preflight. Refs MAIN-424, #688.

## [0.3.29] - 2026-05-22

v0.3.29 packages the owner-loop hardening batch after v0.3.28. It tightens
release dogfood grounding, checkpoint subject semantics, public-safe team
member context, and the repo-scoped Codex plugin/guidance surface
while keeping broader Codex slash-command parity, all-skill parity,
provider-write, publishing, spend, and customer-contact workflows out of scope.

### Added

- Added a public-safe `core/team/<slug>.md` team member primitive, onboarding
  scaffold, validation for normalized and duplicate GitHub handles, and status
  GitHub activity handle resolution so business repos can name known team
  contributors. Refs MAIN-396, #633.
- Added a repo-scoped Codex plugin marketplace, plugin manifest, generated
  guidance, and command files for the supported Main Branch owner loop while
  keeping deterministic `mb` facts and shared workflow sources as the source of
  truth. Refs MAIN-423, #682.

### Changed

- Tightened `mb checkpoint` around finite bracketed checkpoint subjects such as
  `[updated] offer.md -- clarified guarantee`, keeping saved business history
  scannable while improving validation, hook guidance, journal facts, and
  `/mb-site` business-repo save guidance. Refs MAIN-403, #648.

### Fixed

- Tightened Claude print-mode release dogfood prompts so agents can use
  harness-captured fixture facts instead of shell-wrapping `mb status --json`
  through pipes, redirects, temp files, or Python parsers. Refs MAIN-419, #672.

## [0.3.28] - 2026-05-19

v0.3.28 packages the Codex owner-loop runtime release after v0.3.27. It makes
Codex first-class for the proven Main Branch owner loop by adding generated
Codex guidance, workflow inventory, repair/status readiness, and release
evidence while keeping slash-command, all-skills, provider-write, publishing,
spend, and customer-contact parity out of scope.

### Added

- Added generated Codex guidance at `.agents/skills/main-branch-owner-loop`, a
  generated workflow inventory, and
  `mb workflow list --runtime codex` so Codex can discover supported,
  pending, and intentionally unsupported Main Branch workflow surfaces. Refs
  MAIN-421, #676.
- Added source-ingestion privacy rails for transcripts, authenticated
  community/provider sources, mixed-account manifests, skip filters, proof
  permission gates, and `/mb-think` routing. Refs MAIN-409, #657.

### Changed

- Promoted Codex narrowly from experimental CLI-first guidance to first-class
  owner-loop support for start/status/setup/update/doctor, think/codify,
  end/checkpoint/save, validate, and workflow discovery while keeping
  slash-command, provider-write, publishing, spend, customer-contact, and
  copied Claude skill parity out of scope. Refs MAIN-421, #676.
- Tightened generated Codex `AGENTS.md` thinking-route guidance so fresh
  business repos treat the rendered route as the Codex shell for the
  `mb-think` shared workflow source instead of chasing engine-only workflow
  paths. Refs MAIN-418, #671.
- Clarified connector and provider readiness guidance so Claude.ai connectors,
  Claude Code bridged tools/MCP/plugins, Codex/Conductor tools, `mb connect`
  rails, local CLI/API-key paths, and unsupported providers have separate
  restart, OAuth/scope, and read-only smoke expectations. Refs MAIN-411, #654.

## [0.3.27] - 2026-05-18

v0.3.27 packages the shared-workflow and customer-call cleanup batch after
v0.3.26. It makes `/mb-think` the first official runtime-agnostic workflow
source, adds Codex-aligned generated guidance for that workflow, tightens
Claude Code worktree repair and provider smoke privacy, and adds MoneyPath bet
exit/exposure facts plus a second public-safe session excavation report.

### Added

- Added the second sanitized member session excavation report, with public
  follow-up routing for Claude worktree skill discovery, provider mutation
  gates, secret-safe smoke checks, transcript/source-ingestion privacy,
  connector readiness, dashboard direction, repo boundaries, and stale-source
  cleanup. Refs MAIN-408, #653.
- Added a `/mb-think` stale-source cleanup workflow for retiring obsolete
  source material, claims, offer details, proof usage, or messaging angles;
  `/mb-start` now routes stale-source cleanup requests into the reconcile,
  decision, codify, and checkpoint loop. Refs MAIN-393, #630.
- Added bet MoneyPath metadata, appetite-tier, kill-rubric, and double-down
  validation warnings plus `mb status --json` exit-signal facts for declared
  active bet rubrics. Refs MAIN-399, #644.
- Added `mb books exposure --repo . --bet ... --json` and
  `mb books exposure --repo . --active --json` for privacy-bounded hledger bet
  exposure totals without raw ledger rows, payees, account names, account
  numbers, private vault paths, or transaction memos. Refs MAIN-399, #644.

### Changed

- Made `workflows/mb-think/workflow.md` the first official shared workflow
  source pattern by adding checked runtime surfaces, approval gates,
  public/private boundary metadata, generated shell drift checks, and Codex
  `AGENTS.md` alignment while keeping Codex support experimental and
  CLI-first. Refs MAIN-397, #636.
- Aligned public agent, compatibility, and release-sweep docs around shared
  workflow sources, thin runtime shells, pre-release alignment gates, and
  Claude/Codex support boundaries. Refs MAIN-416, #664.

### Fixed

- Redacted provider upstream error messages before storing or printing
  `mb connect test` validation results, and tightened setup references so
  provider smoke evidence records readiness without printing credential values.
  Refs MAIN-413, #658.
- Tightened Claude Code worktree repair so missing project-local `/mb-start`
  wiring is reported as missing Main Branch start wiring, `mb start --json`
  points to `mb doctor repair --plan` / `--apply`, and doctor repair restores
  the bridge in a fresh worktree fixture. Refs MAIN-410, #655.

## [0.3.26] - 2026-05-16

v0.3.26 packages the first-run trust batch after v0.3.25. It tightens setup,
save, sync, status, checkpoint, Codex lifecycle discovery, and proof permission
paths so a real founder setup can stay grounded in deterministic Main Branch
facts without exposing private setup evidence.

### Added

- Added a public session excavation workflow for turning customer calls, chat
  exports, agent logs, and generated repo history into prioritized,
  privacy-safe follow-ups. Refs MAIN-386, #622.
- Added the first sanitized session excavation report from a real customer
  setup, with public follow-up routing for setup, onboarding, checkpoint,
  status, proof, stale-source, repo-boundary, and beginner-explanation issues.
  Refs MAIN-386, #622.

### Changed

- Added compact Codex lifecycle workflow discovery to generated business-repo
  `AGENTS.md`, covering start, status, and thinking/codification routes while
  keeping `.agents/skills`, plugin packaging, site/ads/provider workflows, and
  slash-command parity out of scope. Refs MAIN-387, #624.
- Added a folder-first first-run setup contract across beginner docs, README,
  generated runtime guidance, and `/mb-setup`: pasted setup guides now route to
  deterministic `mb onboard` setup intent instead of document creation, with
  plain-language save/checkpoint/update/runtime boundaries and strongly
  recommended GitHub backup, sync, connector, and account-check guidance. Refs
  MAIN-388, #625; MAIN-395, #632; MAIN-394, #631.
- Added public-marketing proof permission readiness to MoneyPath status facts
  and tightened start/ads/site/think guidance so specific internal proof routes
  to permission collection before proof-backed public campaigns. Refs MAIN-392,
  #629.

### Fixed

- Fixed `mb status --json --peek` so date-valued status facts serialize as ISO
  strings and status failures return the shared JSON error envelope instead of
  leaking Python tracebacks. Refs MAIN-391, #628.
- Fixed `mb onboard --github <owner/repo> --push` so first-run GitHub backup
  includes generated `.mb/schema_version` state in the saved baseline instead
  of stranding the operator at manual cleanup. The push path now records
  GitHub CLI auth/account preflight facts before creating the repo. Refs
  MAIN-389, #626.
- Added a checkpoint review gate for suspicious scratch files, prompt drafts,
  conflict/editor leftovers, and empty accidental notes so `mb checkpoint` does
  not save them without explicit operator approval. Refs MAIN-390, #627.

## [0.3.25] - 2026-05-16

v0.3.25 packages the post-v0.3.24 release-simulation language fix. It makes
checkpoint suggestions more specific and keeps release-acceptance transcripts
stricter about business-owner wording before git/GitHub details.

### Fixed

- Tightened post-v0.3.24 release-simulation guidance and scoring so final
  answers avoid parenthetical git/GitHub restatements, flag
  `Connected GitHub backup: none surfaced` as owner-language leakage, and use
  more specific checkpoint proposals such as `[updated] offer and founder-call
  research` instead of broad buckets. Refs MAIN-385, #619.

## [0.3.24] - 2026-05-15

v0.3.24 packages the release freshness context and owner-language hardening
that landed after v0.3.23. It helps agents explain update availability from
fresh facts and keeps normal business-owner answers from leading with
git/GitHub mechanics.

### Changed

- Added release-note context and freshness evidence to update checks:
  `mb status --json --peek` now names the fresh check command, latest-version
  source, check timestamp, and release notes URL, while `mb update --check`
  reports GitHub Release metadata in JSON and human output when available.
  Refs MAIN-384, #616.

### Fixed

- Tightened release-simulation owner-language scoring and prompt guidance so
  punctuation variants like `working tree: clean`, `branch: main`, and vague
  checkpoint examples such as `[drafted] files` are caught unless the final
  answer translates the matching business meaning first. Generated business-repo
  Claude/Codex guidance now carries the same default translations. Refs
  MAIN-377, #604.
- Labeled unavailable update release-note URLs as expected fallback URLs in
  `mb update --check` human output instead of presenting them as authoritative
  release notes. Refs MAIN-384, #616.

## [0.3.23] - 2026-05-14

v0.3.23 packages the owner-ready first-run GitHub setup path and
user-scoped provider hydration for disposable workspaces. Together they make a
fresh business repo easier to set up, save, sync, and rehydrate from agent
workspaces without re-entering provider tokens.

### Added

- Added a first-run setup completion envelope and optional `mb onboard --github
  ... --push` path so fresh business repos can be scaffolded, saved, connected
  to a private/public GitHub repo, pushed, and reported in owner-facing
  language. Fresh business repos now include a small tracked `README.md`.
  Refs MAIN-378, #606.
- Added user-scoped provider connection metadata and `mb connect hydrate` so
  disposable workspaces can materialize ignored local provider readiness from a
  repo-id keyed user store without re-entering provider tokens. Refs MAIN-379,
  #608.

### Changed

- Improved stale Claude wiring diagnostics to show the current `mb` path and
  version, stale wired engine path, multiple-install signal, and repair command.
  GitHub readiness now treats successful `gh repo view owner/repo` reachability
  as stronger evidence than stale `gh auth status` metadata. Refs MAIN-378,
  #606.

## [0.3.22] - 2026-05-14

v0.3.22 packages the first fixture-safe OpenAI GPT Image 2 smoke rail, the
ad-creative review-board and creative playbook hardening from dogfood,
post-v0.3.21 roadmap/bookkeeping alignment, and tighter owner-language
release-simulation guidance.

### Added

- Added `mb image smoke-openai` as the first fixture-safe OpenAI GPT Image 2
  rail smoke: it writes a push-local `image-index.md`, records generated or
  sanitized blocked state, stores binaries only in configured media storage
  when `--generate` is approved, and keeps `.mb/media/` gitignored by default.
  The package now depends on the official OpenAI Python SDK for that direct
  rail. Refs MAIN-370, #587.

### Changed

- Updated `/mb-ads` image-generation guidance to route the first real provider
  proof through `mb image smoke-openai`, including the approved-generation and
  no-secrets credential boundary. Refs MAIN-370, #587.
- Aligned post-v0.3.21 roadmap and bookkeeping docs so the sample monthly books
  report and Meta Ads read-only summary are described as shipped, while
  private-vault reporting, imports, reconciliation, and provider mutation remain
  deferred. Refs #590.
- Updated `/mb-ads` image-generation guidance and the OpenAI image rail smoke
  record so push-local `image-index.md` files can hold reviewable Facebook
  image-ad concepts, source-bite anchors, genericness checks, placement
  presets, optional creative playbook metadata, prompt records, reference
  roles, avoidance strategy checks, planned post-processing metadata,
  structured creative review findings, and concept-to-asset links before
  optional provider generation. Refs MAIN-373, #595.
- Expanded the `/mb-ads` image production loop as the first creative
  playbook/router experiment: ad readiness gates, source-bite-first prompting,
  conversion-informed playbook metadata, separate visual/ad/risk scoring,
  local ignored review boards, official API batch smoke records, and safe
  `image-index.md` evidence distinguish actual ad candidates from merely
  attractive images. Refs MAIN-374, #596.
- Recorded the MAIN-376 OpenAI image rail dogfood result: official API
  generation produced nine fixture-safe candidates, binaries stayed ignored,
  and manual review rejected the full batch for generic AI image feel, weak
  native-feed fit, and no clear Facebook ad click reason. Refs MAIN-376, #600.
- Tightened release-simulation owner-language guidance, scoring, and `/mb-start`
  wording so normal final answers translate git/GitHub/checkpoint state before
  technical terms and use specific saved-checkpoint examples. Refs MAIN-372,
  #591.

## [0.3.21] - 2026-05-13

v0.3.21 packages the first compact read-only Meta Ads readiness and summary
rail, the hledger-backed sample monthly books report, shared `/mb-think`
workflow shells for Claude and Codex, provider wrapper boundary guidance, and
release-simulation owner-language hardening.

### Added

- Added an accepted creative media generation rails decision for MAIN-282,
  classifying static image providers, deterministic motion/export rails, AI
  video providers, and platform creative tools as recommended, candidate, or
  refused while keeping provider support claims behind setup detection,
  approval gates, smoke evidence, and artifact metadata. Refs #409.
- Added a durable provider CLI/API vs `mb` wrapper boundary decision, including
  `mb connect`, skill/playbook UX, SecretStore/Keychain, privacy/redaction,
  JSON envelope, support-claim, Meta Ads, and image-generation guidance for
  provider cold starts. Refs MAIN-369, #585.
- Added `mb ads meta summary --repo <BUSINESS_REPO> --window 7d --json` for
  compact read-only Meta Ads account summaries after `mb connect` readiness,
  with bounded windows, redacted account/business IDs, coarse spend by default,
  current-run flags for campaign names and exact spend, and no raw payload or
  cache writes. Refs MAIN-367, #582, MAIN-366, #581, MAIN-352, #550.
- Added a MAIN-366 design for the first compact read-only Meta Ads account
  summary surface, keeping `mb connect` as the readiness rail and routing the
  next paid-channel summary shape toward `mb ads meta summary --json` with raw
  payloads, account IDs, tracked caches, and mutations out of scope. Refs
  MAIN-366, #581.
- Added an accepted shared workflow source and runtime shells decision, plus a
  `/mb-think` shared workflow source with generated Claude/Codex shell snapshots
  and drift tests for required `mb` facts, research-depth guidance,
  public/private boundaries, approval gates, and Codex overclaim language. Refs
  MAIN-368, #583.
- Added release-simulation operator-language rubric warnings for visible
  technical leakage in Claude final answers, plus docs and tests for
  translating git/GitHub/checkpoint mechanics into normal owner language first.
  Refs MAIN-363, #573.
- Added Meta Ads read-only `mb connect` readiness wiring: `mb connect meta`
  now stores tokens through `SecretStore`, keeps safe account metadata in
  `.mb/connect.yaml`, and `mb connect test meta --json` models Python/CLI,
  secret, metadata, admin-approval, auth, read-smoke, and ready states for
  `/mb-ads` and status consumers. Refs MAIN-352, #550.
- Added the first hledger-backed `mb books report monthly --sample --month
  YYYY-MM` surface, including packaged fake journal data, stable JSON envelope
  output, beginner-safe human output, missing-hledger guidance, invalid month
  handling, and privacy-boundary tests. Refs MAIN-360, #567, #560.
- Added a MAIN-362 refresh to the creative media generation rails decision,
  making OpenAI GPT Image 2 the first static-image readiness target while
  keeping Google Gemini / Nano Banana, BFL FLUX.2, xAI Imagine, ComfyUI, and
  raw video providers as candidate rails behind separate smoke evidence. Refs
  #569, #409.

### Changed

- Refreshed always-read cold-start docs after v0.3.20 so README, roadmap,
  ethos, and operator-loop language stay aligned with package-visible books
  readiness while leaving sample reporting under `[Unreleased]`, and use
  saved-checkpoint language where normal owner copy should avoid raw git
  wording. Refs MAIN-365, #577.
- Updated release-simulation scoring and `/mb-start` owner-language guidance so
  normal answers translate raw git/GitHub status phrases before speaking, while
  allowing ordinary phrasing such as "only commit summaries." Refs MAIN-364,
  #575.
- Updated `/mb-ads` Meta account guidance so agents ask before pulling a
  compact read-only account summary, continue from repo files, screenshots, or
  manual Ads Manager notes when Meta is not ready, and avoid implying raw
  performance imports or account mutation. Refs MAIN-366, #581.
- Updated `/mb-ads` image-generation guidance and dependency choices to use
  provider-neutral prompt/output records, push-local image indexes, direct
  OpenAI GPT Image 2 as the first smoke target, configurable media storage
  with safe logical media URIs, reference-image roles, and prompt-only fallback
  when no approved provider is configured. Refs MAIN-362, #569.
- Added verified MAIN-362 implementation research patterns to the creative
  media decision, including a GitHub reference-repo pattern table,
  OpenAI-first ad-volume cost math, and a deterministic video/motion CLI
  boundary that keeps raw generative video out of the first rail. Refs
  MAIN-362, #569.
- Updated `/mb-ads` image-generation guidance to stop hard-coding a single
  Gemini model or private local environment path, require provider/model
  metadata in image indexes, and fall back to saved prompts when no approved
  image provider is configured. Refs MAIN-282, #409.

## [0.3.20] - 2026-05-13

v0.3.20 packages the chat-first, fact-backed daily operating loop. It adds
privacy-safe books readiness facts for status and start, introduces the first
shared workflow source prototype for the daily start -> MoneyPath handoff,
deepens `/mb-think` research-depth guidance, hardens release and local-state
boundaries, and refreshes the public narrative around agents using
deterministic `mb` facts internally while operators see plain business
guidance.

### Added

- Added a `/mb-think` research-depth ladder for offer, audience, proof,
  product-ladder, CTA, content strategy, ads/page launch, market positioning,
  and influence/playbook work, including enough-signal thresholds, stop rules,
  parallel research file contracts, synthesis and promotion rules, MoneyPath
  readiness language, and an MCP-first optional Apify research-provider
  boundary. Refs MAIN-344, #529.
- Added a MAIN-357 design sprint report set for the hledger-backed `mb books`
  reporting path, recommending a fake packaged sample monthly report before
  private-vault reporting and documenting hledger command families, chat-first
  UX, JSON shape, privacy boundaries, and follow-up implementation slices. Refs
  #560, #128.
- Added compact, privacy-safe books readiness facts to `mb status --json --peek`
  and `mb start --json`, so daily-loop agents can see bookkeeping setup,
  hledger availability, vault/ignore safety, unsafe artifact counts, and the
  next safe books route without reading ledger contents or exposing private
  paths. Refs MAIN-355, #555, #510, #553, #128.
- Added an accepted decision for agentic security review sidecars: DeepSec may
  be used as an optional local pre-release review aid for security-sensitive
  branches, while Greptile remains a hosted PR-review candidate pending a
  separate privacy/setup evaluation. Release and post-release docs now route
  sidecar evidence through targeted pre-release checks and sanitized
  post-release follow-up, and contributor/release-agent docs cover sidecar
  evidence capture. Refs #554.
- Added the first narrow MAIN-128 `mb books` setup slice: `mb books status`
  now reports hledger availability, sanitized private-books-vault setup, ignore
  protections, and check health; `mb books doctor --plan` now gives a
  non-mutating repair plan for safe bookkeeping setup gaps without reading or
  mutating real ledger contents. Refs #552, #128.
- Added the MAIN-332 post-#553 bookkeeping dogfood report covering `mb books
  check`, `mb books status`, `mb books doctor --plan`, skill routing, status
  gaps, and privacy boundary findings. Refs #510, #555.
- Added the first shared workflow source prototype for the daily start ->
  MoneyPath `/mb-think` handoff, with generated Claude/Codex shell snapshots
  and drift tests that require shared `mb` commands and JSON facts to stay
  present. Refs MAIN-351, #549.
- Added a public-safe Codex Stage 1 dogfood report documenting the experimental
  CLI-first support boundary, generated `AGENTS.md` grounding, deterministic
  `mb` fact usage, and follow-up route for native workflow decisions without
  claiming Codex slash-command parity. Refs MAIN-304, #453.
- Added a proposed shared workflow corpus and native runtime renderer decision
  that names `workflows/<workflow>/` as the portable source for selected
  workflow semantics, keeps Claude Code and Codex runtime shells native, and
  chooses the daily start -> MoneyPath `/mb-think` handoff as the first
  workflow family to prototype. Refs MAIN-302, #451.
- Added a public-safe v0.3.19 post-release transcript review report that records
  PyPI release-acceptance evidence, print-mode proxy limits, post-release docs
  alignment, and the #539 path-to-money follow-up route. Refs #538, #539.

### Changed

- Refreshed the README, roadmap, and ethos around the chat-first, CLI-backed
  operating loop: repo truth feeds deterministic `mb` facts, skills/agents
  explain and route in chat, operators approve sensitive action, and accepted
  lessons become durable repo memory. Refs MAIN-358, #562.
- Updated `/mb-start` routing guidance so path-to-money, revenue, next-dollar,
  and offer-readiness prompts start from deterministic `money_path` facts, carry
  the MoneyPath snapshot into `/mb-think` handoffs, and avoid normal-path
  `head` / `sed` status JSON chunking. Refs MAIN-349, #539.
- Promoted Meta Ads provider guidance from `planned` to `readiness`: Main
  Branch now names Meta's official `meta-ads` / `meta` CLI path, documents the
  setup and read-only command surface, and keeps live account checks out of
  scope until `mb` owns detection and sanitized read-only smoke. Refs MAIN-350,
  #542.

### Fixed

- Fixed post-#553 bookkeeping dogfood gaps: `/mb-start` now routes bookkeeping
  checks through the shipped positional `mb books check "$REPO_PATH" --json`
  syntax, and `mb books status` / `mb books doctor --plan` now warn when
  non-local books storage is selected without a safe private vault label. Refs
  MAIN-332, #510.

### Security

- Tightened package release workflow tag validation, release-notes extraction,
  and release-action pinning; tightened `.mb/connect.yaml` local-state boundary
  handling so provider metadata paths stay inside the selected repo. Refs
  MAIN-356, #558.

## [0.3.19] - 2026-05-12

v0.3.19 makes daily status more business-aware: MoneyPath, proof-quality, and
layered content-strategy facts now surface through deterministic CLI JSON so
`/mb-start`, bundled skills, and future dashboard views can reason from the same
repo-backed truth without turning the CLI into a strategist. The release also
makes recommended Main Branch updates pause `/mb-start` business routing before
ranked actions.

### Added

- Added deterministic MoneyPath offer guardrail detail and proof-quality facts
  under `money_path.objects.offer` and `money_path.objects.proof`, including
  generic vs. specific testimonials, offer-linked proof, typicality signals,
  unsupported-claim warnings, outcome-feedback signals, and an instrumentation
  gate that requires outcome feedback. Refs MAIN-341, #523.
- Added layered content strategy validation and normalized `content_strategy`
  status facts for simple, layered, disconnected, unindexed, and stale strategy
  files, including `content_strategy_unindexed_layer` findings for unindexed
  layers, so future dashboard views can read CLI facts instead of parsing
  markdown. Refs MAIN-346, #536.
- Added a layered content strategy model for business repos covering
  business-level content strategy, distribution strategy, channel strategy,
  account strategy, founder/person voice files, content playbook freshness,
  pushes, logs, and skill routing. Refs MAIN-337, #517.
- Added MoneyPath readiness facts to `mb status --json --peek`, giving skills
  and scripts a read-only, gated view of customer progress, offer, audience,
  proof, product ladder, CTA, channel, push, playbook, page readiness, and
  outcome feedback. The CLI reports legibility, support, connection, and
  instrumentation; skills and operators still own conversion judgment. Refs
  MAIN-343, #528.
- Added clearer release dogfood print-mode evidence handling: per-simulation
  fresh sessions, categorized permission-denial summaries, direct read-only
  `mb books check` / `mb educational` allowlist coverage, and prompt
  guardrails against shell-wrapped parsing in proxy runs. Refs MAIN-342, #526.
- Added explicit two-layer transcript review guidance so release audits check
  deterministic proof first, then mine the agent transcript for product
  opportunities, repair gaps, and avoidable operator friction. Refs MAIN-342,
  #526.
- Added a Mermaid-powered Main Branch system map with source-of-truth tables
  for architecture boundaries, provider rails, private data, validation, and
  runtime stance. Refs MAIN-339, #519.
- Added an offer-sharpening guide and shared conversion reference so `/mb-think`,
  `/mb-site`, `/mb-ads`, `/mb-organic`, sales-video routing, and launch
  orchestration use the same offer rubric, style spectrum, evidence boundary,
  and stop conditions before scaling pages, ads, videos, or launch work. Refs
  MAIN-336, #516.
- Added a public-safe v0.3.18 post-release transcript review report that records
  the PyPI release-acceptance evidence, print-mode proxy limits, and follow-up
  harness gap, and linked it from the release simulation transcript-review
  guidance. Refs MAIN-340, #521, #526.

### Changed

- Documented MoneyPath proof-quality facts for docs, bundled skills, generated
  repo guidance, and future dashboard badges so agents cite factual proof
  signals instead of subjective proof scores. Refs MAIN-347, #537.
- Updated `/mb-start` and generated repo guidance so recommended Main Branch
  updates pause business routing, ask the operator whether to update first, and
  avoid burying update prompts under ranked actions. Refs MAIN-345, #532.

## [0.3.18] - 2026-05-12

v0.3.18 is a package-visible skill and operator-loop patch. It strengthens
agent cold-start guidance, makes `/mb-start` a stronger business router,
aligns setup guidance around checkpoint-first saves, and moves high-impact
bundled skills toward a CLI-first contract while retiring stale compatibility
aliases.

### Added

- Added `docs/agent-cold-start.md` as the public source for agent read order,
  progressive discovery, release-doc boundaries, and the local preference split,
  so maintainer-local preferences can stay short and private. Refs MAIN-330,
  #507.
- Added an explicit `/mb-start` router and language contract covering live
  intent routing, bookkeeping/books setup, provider setup, save/sync wording,
  stronger update posture, and the rule that generic "set up" must not override
  the user's specific business noun. Refs MAIN-333, #511.

### Changed

- Added `docs/system-architecture.md` and `docs/agent-writing-style.md` to the
  public cold-start always-read set, and tightened the release-agent contract
  with a cheap release-file preflight before expensive validation gates. Refs
  MAIN-340, #521.
- Reframed `/mb-start`, `mb status` git summaries, `mb start` readiness repair,
  and `mb books check` operator summaries around saved checkpoints, unsaved
  local work, catching up, syncing, and reconciliation instead of defaulting to
  raw commit/rebase/ahead/behind language. Refs MAIN-333, #511.
- Aligned `/mb-setup` save and review guidance with the shipped
  checkpoint-first business-repo contract, replacing stale raw save examples
  and default AI attribution trailers with `mb checkpoint` planning,
  validation, and approval language. Refs MAIN-334, #513.
- Added a CLI-first contract to high-impact bundled skills so agents start from
  shipped `mb` facts for status, setup, provider readiness, site checks, books,
  validation, and checkpoints before interpreting or writing workflow prose.
  Refs MAIN-338, #518.

### Removed

- Removed the `/mb-vsl` compatibility router. Sales-video and VSL prompts now
  route directly through `/mb-site`, `/mb-ads`, `/mb-think`, or `/mb-organic`
  by surface and intent. Refs MAIN-338, #518.
- Removed the `/mb-pull` compatibility alias now that `/mb-update` and
  `mb update` own the update flow. Refs MAIN-338, #518.

## [0.3.17] - 2026-05-12

v0.3.17 is a release-tightening patch after the first `mb books` release. It
aligns the active bookkeeping surface on hledger, proves `mb books check`
through an installed-package dogfood run, routes VSL knowledge through the
broader conversion workflows, and hardens the release process with supply-chain
gates plus post-release simulation-audit coverage.

### Changed

- Replaced the active Beancount-era `mb connect` and `mb educational`
  bookkeeping surfaces with hledger, matching the accepted `mb books`
  foundation decision. Default generated `.gitignore` files now protect
  `.mb/private/`, `*.journal`, `*.hledger`, and `*.ledger` alongside the
  defensive `*.beancount` pattern.
- Dogfooded `mb books check` through the installed package and a fresh business
  repo after the hledger cleanup, recorded the evidence in
  [`docs/reports/2026-05-12-books-check-dogfood.md`](docs/reports/2026-05-12-books-check-dogfood.md),
  and updated bundled skill archetype examples that still used Beancount as an
  active bookkeeping example.
- Tightened the post-release alignment playbook so release simulation
  transcript audits are a named post-release step, clarified GitHub/Linear
  evidence routing, and added a packaged release simulation for hledger-backed
  bookkeeping safety handoffs. Refs MAIN-328, #502.
- Repositioned VSLs as reusable conversion knowledge inside `/mb-think`,
  `/mb-site`, `/mb-ads`, and `/mb-organic` workflows instead of a standalone
  business primitive. `/mb-vsl` remains as a compatibility router for existing
  users, the Skool and B2B VSL frameworks moved to shared conversion
  references, and release simulations now cover natural sales-video prompt
  routing. Refs MAIN-285, #412.

### Security

- Locked Main Branch's supply-chain posture in
  [`decisions/2026-05-11-supply-chain-security-gates.md`](decisions/2026-05-11-supply-chain-security-gates.md)
  and documented the durable rules in
  [`docs/supply-chain-policy.md`](docs/supply-chain-policy.md): trusted-publishing
  OIDC only, `id-token: write` scoped to one job in `publish-pypi.yml`, `pypi`
  GitHub Environment with a human approver, single-build artifact reused at
  publish, dependency review in isolation, release-time supply-chain checks,
  and a public-safe post-compromise response path.
- `.github/workflows/publish-pypi.yml` now carries a defensive `if:` guard so
  the `publish` job only runs when the release tag matches `oe-v*`, on top of
  the trusted-publishing binding and the `pypi` environment approval gate.
- `.github/dependabot.yml` now groups pip + GitHub Actions updates, labels
  them for supply-chain review, and applies a release-age `cooldown` so
  freshly-published versions are not proposed the same hour they land.

## [0.3.16] - 2026-05-11

v0.3.16 lands the first concrete `mb books` command surface alongside the
hledger + private books vault foundation, accepts the scheduled data sync
pattern for business repos, exposes operator vocabulary facts in `mb status`
and `mb start`, and locks the operator-facing GitOps primitives (`audience` /
`operator_summary` on findings, workflow awareness on `mb status`). Several
docs and conventions slices land in the same release: graph link authoring
guidance, Related links mirror validation and repair, the `mb suggest links`
command, the first record type in the data-source registry, the business
connections decision, and a docs architecture / language cleanup pass.

### What this means for you (plain English)

- **First safe books surface.** `mb books check` inspects whether your
  finance metadata is wired up, warns if ledger or statement files look like
  they leaked into the team-visible repo, and (with `--fixture`) round-trips
  a packaged fake hledger journal so you can confirm hledger works on your
  machine without ever touching real numbers.
- **Books storage is a clear contract.** hledger is the chosen engine, and
  real books live in a private books vault — solo-local under
  `.mb/private/books/` by default, or a separate team-private repo —
  never in the team-visible business repo.
- **Scheduled data sync has a documented pattern.** The accepted pattern is
  operator-owned cron (or `launchd` / Task Scheduler) writing into the
  existing `data/<provider>/` registry layout, with `mb status` and
  `mb doctor` reporting freshness from the registry record. No CLI
  behavior change yet — the foundation is named and follow-ups are tracked.
- **`mb status` and `mb start` know more about your repo shape.** A
  `vocabulary` block surfaces optional `core/vocabulary.md` display terms,
  and the `git` block now carries `workflow_mode`, `default_branch`,
  `upstream`, `ahead`, `behind`, `worktree_root`, and a one-liner
  `summary`. Skills and agents can decide save-on-main vs branch-and-PR
  vs worktree-aware flows without their own git wrappers.
- **Findings tell you who acts on them.** `mb doctor`, `mb validate`, and
  `mb status` actions now carry `audience`
  (`mechanical` / `operator_decision` / `informational`) plus an
  `operator_summary` so agents can route a fact into business-language
  next steps. `mb validate` also exposes per-category summaries and a top
  cluster so messy migrated repos point at the biggest useful fix first.
- **Link conventions are clearer.** `mb suggest links <file>` ranks
  candidate relationships with JSON reasons; `mb validate --cross-refs`
  and `mb doctor repair --plan` keep `## Related links` body mirrors in
  sync with frontmatter without making body links authoritative; the
  `type: data_source` record at `data/<provider>/source.md` is the first
  portable business-facts record and ships with a `linked_data_sources`
  typed link.

### Added

- Shipped the first `mb books` surface, `mb books check`, implementing the
  contract from `decisions/2026-05-11-mb-books-foundation.md`. The command
  is read-only and never reads real ledger contents. It detects whether
  `core/finance/books.md` exists and parses its `storage_mode`, detects
  whether `core/finance/chart-of-accounts.md` exists, verifies the
  configured storage mode's ignore rule (`.mb/private/` for solo-local
  mode), and warns when tracked files with ledger-shaped extensions
  (`.journal`, `.hledger`, `.ledger`, `.beancount`) or statement-shaped
  extensions (`.csv`, `.ofx`, `.qfx`, `.qbo`, `.qif`) appear in the
  business repo (likely Class B leak). The unsafe-path finding is
  `warn`, not a hard fail, because non-finance CSVs are legitimate;
  files carrying an explicit fixture marker (`MB-FIXTURE`,
  `SAMPLE FIXTURE`, or `NOT A REAL LEDGER`, case-insensitive, in the
  first 1024 bytes) are exempted. Unknown or typo'd `storage_mode`
  values fail closed — they are treated as `solo-local` for vault
  enforcement so a misconfigured policy cannot silently allow a leak.
  Opt in with `--fixture` to validate a packaged fake hledger fixture
  by shelling out to `hledger -f <fixture> check`; if hledger is not
  installed, the check prints a clean informational finding and the
  base install keeps working. `--json` emits the standard Main Branch
  result envelope; every finding carries `audience` and
  `operator_summary` per the operator-facing GitOps contract from
  MAIN-310. Sibling `mb books status` and `mb books doctor` shapes
  remain deferred. The fake fixture from
  `docs/examples/books/acme-fixture.journal` is mirrored into
  `mb/mb/_data/books/acme-fixture.journal` so it is reachable from the
  installed wheel. Refs MAIN-321, #486.
- Accepted decision
  `decisions/2026-05-11-scheduled-data-sync-pattern.md` defining the first
  scheduled data sync pattern for business repos. The default shape is
  **operator-owned cron** (or `launchd` / Task Scheduler) running a
  one-shot per-provider script that writes SQLite plus dated CSV
  snapshots into the existing `data/<provider>/` data-source registry
  layout and updates `source.md` `freshness` and `storage.snapshots`.
  Operational state (last-run JSON summary, raw logs) lives under
  `.mb/private/sync/`, which the pattern requires operators to add to
  `.gitignore` themselves until the deferred books follow-up patches
  `mb/mb/_data/templates/.gitignore.tmpl`. The decision and the
  operator doc state the gap explicitly so no one assumes Main Branch
  already enforces the ignore.
  Credentials stay in the OS keychain, the runtime environment, or
  GitHub Actions secrets — never in repo files, frontmatter, or run
  logs. `mb status` / `mb doctor` surface staleness by reading
  `cadence`/`freshness` from the registry record and the optional
  last-run JSON; Main Branch reports what is stale, it does not claim
  to have run the sync. **GitHub Actions** is named as an explicit
  alternative when the operator already trusts GitHub for secrets; a
  local background service stays out of scope. The pattern reuses the
  shipped `linked_data_sources` typed link plus inline snapshot links
  so decisions, pushes, and outcomes still link the record (not the
  log file). Marketing/ads/analytics/CRM/email data is fine to sync
  into `data/<provider>/`; bank/processor/payroll/tax data remains
  Class B per the `mb books` foundation and belongs in the private
  books vault, not in the team-visible registry. Added
  `docs/scheduled-data-sync.md` as the operator-facing companion.
  No CLI behaviour change in this slice; `mb data sync`,
  `mb data status`, a `mb doctor` freshness check, provider-specific
  scripts, a sidecar envelope, and `mb books import` are named as
  follow-up issues. Closes #471. Refs MAIN-315.
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
