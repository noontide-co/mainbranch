# Changelog

All notable changes to `mb-vip` (the Main Branch engine) will be documented in
this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The release tag scheme is `oe-vMAJOR.MINOR.PATCH` ("oe" = open engine) — the
PyPI distribution `mainbranch` tracks the same version sequence.

## [Unreleased]

### What this means for you (plain English)

Since v0.1.0, here's what's changed in your day-to-day if you're a member:

- **Better "what's new" notices.** Instead of a separate announcements
  file that nobody updated, the engine now uses this CHANGELOG. You'll
  see banners in `/start` and `/pull` when there's a real release.
- **More archetype detail in `/site`.** The 5 archetype templates that
  shipped as stubs in v0.1.0 are now full reference files — you'll get
  richer brand-voice guidance when you build a site for a contrarian
  brand, a redemption-arc brand, etc.
- **Quality gates got tighter.** New CI jobs catch packaging mistakes
  before they hit you. You won't notice them unless something breaks
  upstream and we catch it before merge.

OSS / contributor detail below.

### Added

- **CHANGELOG.md** itself (Keep a Changelog format). Replaces the
  `.claude/announcements.md` file as the single source of truth for what's
  new in the engine. `/start` and `/pull` now diff the current version
  against `~/.config/vip/local.yaml:last_seen_version` and surface unread
  entries as a "What's new" banner.
- **`wheel-install-smoke` CI job** (`.github/workflows/ci.yml`). Builds the
  `mainbranch` wheel + sdist, installs into a clean venv, and verifies
  the CLI surfaces `mb --version`, `mb --help`, `mb skill list`, and
  `mb doctor` all run to clean exit, plus `python -c "import mb"` works.
  Catches packaging drift (missing `py.typed`, stale `package-data`,
  entry-point registration gaps) that the editable-install matrix can't
  see. **Note:** the wheel does NOT yet ship populated `mb/_data/skills/`
  in v0.1.0 — `mb skill list` runs cleanly but returns an empty bundle.
  Skill bundling at build time is deferred to a v0.1.x follow-up. Pattern
  borrowed from `companyctx`.
- **70% coverage threshold** in CI (`mb/pyproject.toml` +
  `.github/workflows/ci.yml`). Test-suite blocks merge if `--cov-fail-under=70`
  fails. Minimal smoke tests added to `mb/tests/` to cover `educational`,
  `think`, and CLI entry-point modules that were under-tested.
- **5 archetype detail files promoted from stubs to full** under
  `.claude/skills/site/references/archetypes/`: `victim.md`,
  `tragedy-mindset.md`, `dark-hero.md`, `redemption.md`,
  `tragic-comedy.md`. Each now carries the same shape as the existing
  4 archetypes (wounded-healer, savior, david-goliath, broken-hero):
  definition, when to use, audience-current-trap reframe (where applicable),
  do-not-state list, paired-imagery template, headline formulas (where
  applicable), voice anchor, anti-patterns, brand applications.
  Source: `research/2026-04-29-marketing-site-brief-framework-yt-mining.md`
  (Chase Hughes 9-archetype framework). The `archetypes.md` catalog now
  lists real one-line blurbs instead of `(stub)` tags.
- **Canonical `vip-path-resolution.md` reference** at
  `.claude/reference/vip-path-resolution.md`. Single source of truth for
  the bash + python3 resolver that locates mb-vip via
  `.claude/settings.local.json:additionalDirectories` first, with
  `~/.config/vip/local.yaml:vip_path` as the fallback. Includes failure
  modes and recovery. Replaces inline copies of the resolver across at
  least 5 reference files.

### Changed

- **`/pull` and `/start` now read CHANGELOG entries** instead of
  `.claude/announcements.md`. The "what's new" surface diff'd against the
  user's `last_seen_version` (stored in `~/.config/vip/local.yaml`).
  Behaviour is unchanged from the user's perspective: a banner appears
  the first time they pull a release, gets dismissed when they engage,
  and stops surfacing after the version is marked seen.
- **`.github/workflows/publish-pypi.yml`** now extracts the matching
  CHANGELOG section as the GitHub Release body. Pattern borrowed from
  `companyctx`'s publish workflow.
- **5 reference files** that previously inlined the vip-path resolver
  (`.claude/skills/setup/references/cwd-detection.md`,
  `.claude/skills/help/references/troubleshooting.md` (×2 occurrences),
  `.claude/skills/pull/SKILL.md`,
  `.claude/reference/pull-engine-updates.md`) now point at the canonical
  `vip-path-resolution.md` reference. Resolver semantics are unchanged.

### Removed

- **`.claude/announcements.md`** — superseded by `CHANGELOG.md`. The
  announcements format (per-skill `seen` tracking via slugs) is replaced
  by per-version `last_seen_version` tracking, which compresses to a
  single string in user config.

## [0.1.0] - 2026-04-29 (Phase 2 RC)

First Phase 2 release candidate. The engine is now a real Python package
(`mainbranch` on PyPI, `mb` CLI) with a six-folder business-as-files
taxonomy and a /site shape upgrade that adopts Chase Hughes' 9-archetype
narrative framework as the brief layer. **The CLI surface is smoke-tested
end-to-end; the skill bundle itself does NOT yet ship in the wheel — skills
live in the `mb-vip` engine repo's `.claude/skills/` for v0.1.0 and are
loaded via `additionalDirectories` from the consumer business repo. Wheel-time
skill bundling is a v0.1.x follow-up.**

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
sections below cover what shipped in PRs #114 / #115 / #116 / #117.

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
  Stubs land for 5 of the 9 archetypes (filled out in the next release).
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
  files in the next release (see Unreleased above).
- `tools/` contains stubs for future OSS carve-outs (research-pack pivot
  per `project_d100_research_pack_pivot_20260420.md`).
- `playbooks/` ships skeletons; full playbook content lands incrementally.

## [0.0.x] - pre-2026-04-29

Pre-V1 dev releases. Internal-only. Documented in git history; not
re-summarised here.
