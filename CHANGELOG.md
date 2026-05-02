# Changelog

All notable changes to `mb-vip` (the Main Branch engine) will be documented in
this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The release tag scheme is `oe-vMAJOR.MINOR.PATCH` ("oe" = open engine) — the
PyPI distribution `mainbranch` tracks the same version sequence.

## [Unreleased]

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
