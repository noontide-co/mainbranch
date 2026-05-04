# Changelog

All notable changes to `mb-vip` (the Main Branch engine) will be documented in
this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The release tag scheme is `oe-vMAJOR.MINOR.PATCH` ("oe" = open engine) — the
PyPI distribution `mainbranch` tracks the same version sequence.

## [Unreleased]

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
  anchor to the Know -> See -> Decide -> Execute -> Narrate loop and the
  current v0.3/v0.4 release direction.
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
  business repo, explains the local files / git / GitHub substrate, wires the
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
  deterministic CLI substrate and agent skills as the judgment layer.
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
- **`mb` stays the stable substrate.** It owns repo shape, validation, status,
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
