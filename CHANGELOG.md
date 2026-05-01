# Changelog

All notable changes to `mb-vip` (the Main Branch engine) will be documented in
this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The release tag scheme is `oe-vMAJOR.MINOR.PATCH` ("oe" = open engine) — the
PyPI distribution `mainbranch` tracks the same version sequence.

## [Unreleased]

No unreleased changes yet.

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
