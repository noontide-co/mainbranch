---
type: decision
date: 2026-04-29
status: proposed
topic: mb-vip v0.1.0 — engine-side master decision (skill composition, repo shape, PyPI packaging, /site upgrade, conductor preferences)
mirrors: noontide-projects/decisions/2026-04-29-main-branch-v0-1-0-master.md
linked_research:
  - noontide-projects/research/2026-04-29-marketing-site-brief-framework-yt-mining.md
  - noontide-projects/research/2026-04-29-marketing-skills-repo-mining.md
  - noontide-projects/research/2026-04-29-cli-agent-infra-repos-mining.md
  - noontide-projects/research/2026-04-29-plan-critique-5-devex-multi-team.md
  - noontide-projects/research/2026-04-29-v0-2-roadmap-and-conductor-patterns.md
participants: [Devon, Claude]
tags: [v0-1-0, mb-vip, engine, /site, pypi, conductor-preferences]
---

# mb-vip v0.1.0 — Engine Master Decision

## Context

This file is the engine-side mirror of the noontide-projects master decision (`noontide-projects/decisions/2026-04-29-main-branch-v0-1-0-master.md`). The noontide-projects master sets the business-level locks: vocabulary (tool/skill/playbook), folder shape, OSS-vs-paid mechanism, pricing, dashboard commitment, and the 8-item v0.1.0 ship list at the conceptual level. This file lands the same locks on the **engine repo (`mb-vip`)** with concrete file paths, package shape, and per-skill change lists.

It exists because Devon already acked the noontide-projects master on 2026-04-29 ("agree, lets update everythg, clean move on, 89 merge") and the open commitment in that master was: *"The matching `mb-vip` decision (skill changes, /site dial rename, brand-as-3rd-position, archetype field) gets its own file in that repo."* This is that file.

There is no relitigation here. Vocabulary, folder shape, dial naming, archetype catalog, OSS/paid mechanism, PyPI commitment, and conductor-preferences-for-mb-vip are all decided in the noontide-projects master or in the linked research files. This file translates them into engine-repo execution.

The decision is `status: proposed` because it has not yet been opened as a PR. It graduates to `status: accepted` when Devon merges the v0.1.0-rc1 PR on this branch.

---

## Relationship to the noontide-projects master decision

The noontide-projects master decision is the **business** master: it covers thesis, pricing, persona, bets-in-public, dashboard commitment, OSS-vs-paid mechanism at the business level, and the launch phasing. This file is the **engine** master: it covers the code that ships, the file paths that move, the package on PyPI, the `/site` skill upgrade, and the conductor preferences for working in the `mb-vip` repo itself.

| Concern | noontide-projects master | this file (mb-vip master) |
|---|---|---|
| Pricing tiers ($19/$99/$199/$4K+) | Source of truth | Not covered |
| Bets-in-public mechanic + redaction policy | Source of truth | Not covered |
| Dashboard timeline commitment (v0.2 by July 2026) | Source of truth | Not covered |
| Six data primitives (`core/`, `research/`, `decisions/`, `log/`, `campaigns/`, `documents/`) | Source of truth (lives in *consumer* business repos) | Inherits; `mb init` scaffolds them |
| Vocabulary lock (tool/skill/playbook) | Source of truth | Inherits + applies to file paths |
| Status enum (`proposed/running/scaling/killed/graduated/died`) | Source of truth | `mb validate` enforces frontmatter shape |
| OSS/paid one-line rule (MIT ships shapes; paid ships contents) | Source of truth | Engine-side resolution: how skills find paid reference, what stub returns when missing |
| PyPI distribution commitment | Source of truth (decision to ship) | Source of truth (package shape, entry points, install path) |
| Conductor preferences for mb-vip | Names the commitment | Source of truth (full template) |
| `/site` skill upgrade (brand dial, 9 archetypes, Seven Sweeps, AI-tells, paired imagery) | Names the commitment | Source of truth (file-by-file change list) |
| Repo reorg of `mb-vip` itself (skills flat, playbooks flat, no molecules/compounds dirs) | Names the lock | Source of truth (path-by-path migration) |
| Tools repo layout (`tools/<name>/`, `mb/`) | Names the lock | Source of truth (per-tool implementation language, build path) |
| Educational triage content (`.claude/educational/`) | Names the pattern | Source of truth (initial topic list, file format) |
| Phase 1 / Phase 2 launch sequencing | Source of truth | Inherits; this file's "What Changes" list is the engine-side codification queue for Phase 1 |

If a fact about *what* ships is in conflict, the noontide-projects master wins. If a fact about *how* it lands in the engine repo is in conflict, this file wins.

---

## Vocabulary Locks

Inherited from the noontide-projects master, restated here so the engine repo never relitigates:

| Old (PR #82 chemistry metaphor) | New (locked) | Implementation |
|---|---|---|
| `atom` | `tool` | CLI binaries under `tools/<name>/` and dispatched by `mb` umbrella |
| `molecule` | `skill` | `.claude/skills/<name>/SKILL.md` — flat layout, no `molecules/` subdir |
| `compound` | `playbook` | `.claude/playbooks/<name>/SKILL.md` — flat layout, no `compounds/` subdir |
| "vibe" (third /site dial) | `brand` | The third value of the `dial:` brief field, alongside `convert` and `story` |
| `core/brand/` (consumer-repo path) | `core/visual-identity/` | (Resolved in noontide-projects master; engine references it as the path skills read) |

**There is no `atom-*` binary in v0.1.0 ship**, only `tool-*`. Aliases for 30 days are nice but engine-side defaults must be `tool-` from day one.

**The chemistry metaphor is dead.** Plain English. A `playbook` IS what `compound` was naming. A `skill` IS what `molecule` was naming. A `tool` IS what `atom` was naming. Same role, honest noun, no chemistry. Legacy mentions of `atom`/`molecule`/`compound` survive only inside dated research files (banner-noted, not relitigated) per the master.

---

## Repo Reorg Plan

### Current shape (as of 2026-04-29 on `dmthepm/mb-vip-v0-1-0`)

```
mb-vip/
├── CLAUDE.md
├── CONTRIBUTING.md
├── README.md
├── decisions/
├── docs/
├── experimental/
├── templates/
└── .claude/
    ├── announcements.md
    ├── lenses/
    ├── reference/
    ├── scripts/
    ├── settings.local.json
    └── skills/
        ├── ads/
        ├── end/
        ├── help/
        ├── organic/
        ├── pull/
        ├── setup/
        ├── site/                  # the heavy one — gets upgraded
        ├── start/
        ├── think/
        ├── vsl/
        └── wiki/
```

PR #82 implied a future shape with `.claude/skills/<x>/molecules/` and `.claude/skills/<x>/compounds/` nested folders. Both are dropped. PR #82 also implied a `tools/` directory at the repo root for the CLI binaries; that lock survives the rename (`atom-*` → `tool-*`).

### Locked v0.1.0 shape

```
mb-vip/
├── CLAUDE.md                      # engine-repo CLAUDE.md (not consumer repo's)
├── CONTRIBUTING.md
├── README.md                      # honesty: "Built for Claude Code; cross-platform v0.2+"
├── pyproject.toml                 # NEW — PyPI package metadata
├── conductor-preferences.md       # NEW — adapted from companyctx
├── CODEOWNERS                     # NEW — engine-repo ownership
├── decisions/
│   └── 2026-04-29-mb-vip-v0-1-0-master.md   # this file
├── docs/
├── experimental/
├── templates/                     # consumer-repo templates (CLAUDE.md, .github/CODEOWNERS, etc.)
│   └── consumer/
│       ├── CLAUDE.md.tmpl
│       ├── CODEOWNERS.tmpl
│       └── .gitignore.tmpl
├── tools/                         # NEW top-level — CLI source for tool-* binaries
│   ├── tool-domain/               # Go (per critique #5; aligns w/ discrawl pattern)
│   ├── tool-dns/                  # Go
│   ├── tool-pages/                # Go
│   ├── tool-stripe/               # Go
│   └── tool-og-render/            # Python wrapper around rsvg-convert + cairosvg (PR #100, live-tested)
├── mb/                            # NEW top-level — Python umbrella dispatcher
│   ├── mb/                        # Python package (the `mb` entry point)
│   │   ├── __init__.py
│   │   ├── __main__.py            # `python -m mb` works
│   │   ├── cli.py                 # Click/Typer CLI
│   │   ├── init.py                # `mb init` scaffolder
│   │   ├── doctor.py              # `mb doctor` checks
│   │   ├── validate.py            # `mb validate` frontmatter checker
│   │   ├── graph.py               # `mb graph` DOT emitter
│   │   ├── educational.py         # "tell me more" loader for opinionated defaults
│   │   └── resolve.py             # paid-reference path resolution + missing-ref stub
│   ├── tests/
│   ├── pyproject.toml             # PyPI: mainbranch
│   └── README.md
├── .claude/
│   ├── announcements.md
│   ├── settings.local.json
│   ├── lenses/                    # unchanged
│   ├── scripts/                   # unchanged
│   ├── reference/                 # engine-side reference (e.g., minisite spec)
│   ├── skills/                    # FLAT — no nested molecules/
│   │   ├── ads/
│   │   ├── end/
│   │   ├── help/
│   │   ├── organic/
│   │   ├── pull/
│   │   ├── setup/
│   │   ├── site/                  # heavy upgrade — see /site section below
│   │   ├── start/
│   │   ├── think/
│   │   ├── vsl/
│   │   ├── wiki/
│   │   ├── skill-brief-draft/     # NEW — composable skill called by /site
│   │   ├── skill-concept/         # NEW — composable skill
│   │   └── skill-review/          # NEW — composable skill (Seven Sweeps)
│   ├── playbooks/                 # NEW top-level — flat, no compounds/
│   │   ├── ship-bet/              # NEW v0.1 (skeleton; full impl v0.2)
│   │   └── weekly-review/         # NEW v0.1 (skeleton; full impl v0.2)
│   └── educational/               # NEW — "tell me more" content for opinionated defaults
│       ├── anti-cloud-backup.md
│       ├── opinionated-stack-cloudflare-vs-vercel.md
│       └── github-vs-gdocs.md
└── .github/
    ├── workflows/
    │   ├── publish-pypi.yml       # NEW — trusted publisher (companyctx template)
    │   ├── lint.yml
    │   └── test.yml
    └── CODEOWNERS
```

### Path-by-path move list (Phase 1)

| What | From | To | Action |
|---|---|---|---|
| Engine README honesty pass | `README.md` | `README.md` | Edit: add "Built for Claude Code; cross-platform v0.2+; PyPI as `pipx install mainbranch`" |
| Skill files (10 existing) | `.claude/skills/<name>/` | `.claude/skills/<name>/` | Stay flat. Lock: no nested `molecules/` or `compounds/` subdirs ever introduced. |
| Composable skills (3 new) | — | `.claude/skills/skill-{brief-draft,concept,review}/` | Create. /site calls these via depth-3 chain. |
| Playbooks dir (new) | — | `.claude/playbooks/` | Create with two skeletons (`ship-bet/`, `weekly-review/`). Real impl deferred. |
| Educational triage dir | — | `.claude/educational/` | Create with three initial topic files. |
| Tools source (5) | (currently nowhere or in `experimental/`) | `tools/tool-{domain,dns,pages,stripe,og-render}/` | Create or move. Each gets its own `SKILL.md` next to its binary per discrawl/paperclip pattern lifted from `cli-agent-infra-repos-mining.md`. |
| `mb` umbrella source | — | `mb/mb/` | Create as Python package; entry point `mb` via `pyproject.toml`. |
| Consumer-repo template | (templates not yet structured) | `templates/consumer/` | Create. `mb init` reads from here. |
| Conductor preferences | — | `conductor-preferences.md` (repo root) | Create. Adapted from `companyctx`. |
| Repo CODEOWNERS | — | `.github/CODEOWNERS` | Create. Devon owns all in v0.1; multi-owner pattern doc'd in CONTRIBUTING. |
| PyPI workflow | — | `.github/workflows/publish-pypi.yml` | Create. Trusted-publisher per companyctx template. |

### What does NOT move

- `.claude/lenses/`, `.claude/scripts/`, `.claude/reference/`, `.claude/announcements.md`, `.claude/settings.local.json` — unchanged in v0.1.0.
- `docs/`, `experimental/` — left as-is. `experimental/` is a sandbox; do not promote to canon in v0.1.
- `decisions/` — unchanged structure; this file is the first entry on the engine side.

### Why flat (no `molecules/`, no `compounds/`)

The chemistry metaphor died because the metaphor stopped pulling weight when the third leg (`compound`) was added. Once the metaphor is gone, the directory hierarchy that *enforced* the metaphor (`.claude/skills/<x>/molecules/`, `.claude/skills/<x>/compounds/`) becomes load-bearing only for the metaphor. Drop both. Skills are skills, playbooks are playbooks, both flat under `.claude/`. The depth-3 escape hatch (`playbook → skill → skill → tool`) handles composition; no folder nesting is required to express it.

---

## What Ships in v0.1.0 (the 8-item list, engine-side specifics)

The noontide-projects master locked the 8-item conceptual ship list. This section names the engine-side implementation specifics.

### 1. `mb init` — non-interactive scaffold

| Spec | Value |
|---|---|
| Implementation file | `mb/mb/init.py` |
| Language | Python 3.10+ |
| Templates source | `templates/consumer/` |
| What it creates | `core/`, `research/`, `decisions/`, `log/`, `campaigns/`, `documents/`, `CLAUDE.md`, `.github/CODEOWNERS`, `.gitignore`, runs `git init` |
| User questions | One only: business name. No path-config questions in v0.1. No business-type questions. |
| Idempotent? | Yes. Re-running on existing repo says "already initialized" and exits 0. |
| Output modes | Default human; `--json` for machine callers (per discrawl convention) |
| Required env | None on happy path. Detects `gh auth status`, Claude Code install. |

### 2. `mb doctor` — diagnostic

| Spec | Value |
|---|---|
| Implementation file | `mb/mb/doctor.py` |
| Checks | Claude Code installed; `gh` authed; skills on disk (resolves `vip_path` from `~/.config/vip/local.yaml` first, then `.claude/settings.local.json`); Skool token if present in env; repo writable; network reachable to GH/Cloudflare |
| Anti-cloud-backup detection | Walks `core/finance/` and warns if any file lives under `~/Library/Mobile Documents/` (iCloud), Google Drive, Dropbox sync paths. Triggers educational triage `[t]` "tell me more" → loads `.claude/educational/anti-cloud-backup.md` |
| Output | Human (default) with green checks / red Xs and remediation lines; `--json` for CI |
| Exit code | 0 if all green; 1 if any red |

### 3. `mb validate` — frontmatter shape

| Spec | Value |
|---|---|
| Implementation file | `mb/mb/validate.py` |
| Scope (v0.1) | Frontmatter shape only. No cross-reference validation. No content rules. |
| Hard-coded schema | `decisions/*.md` requires `date`, `status` ∈ {proposed, accepted, rejected, superseded}, `owner`. `core/offers/*/offer.md` requires `slug`, `status` ∈ {proposed, running, scaling, killed, graduated, died}, `owner`. `research/*.md` requires `date`, `topic`, `source`, `status`. |
| Output | Per-file pass/fail, `--verbose` lists missing keys; exit code 1 on any fail |
| Code size estimate | 200–400 LOC Python (yaml.safe_load + path walking) |

### 4. `mb graph` — DOT emitter

| Spec | Value |
|---|---|
| Implementation file | `mb/mb/graph.py` |
| Scope (v0.1) | Walk frontmatter for `linked_research:`, `supersedes:`, `linked_decisions:`. Build adjacency list. Emit Graphviz DOT to stdout. |
| `--open` flag | Shells to `dot -Tpng` then `open` (macOS) / `xdg-open` (Linux). Refuses on Windows in v0.1. |
| Not in v0.1 | HTML rendering; click-to-jump; filter flags; `--serve`. Those are v0.2. |

### 5. CODEOWNERS template

| Spec | Value |
|---|---|
| Source | `templates/consumer/CODEOWNERS.tmpl` |
| Default content | Single-owner default (`* @<gh-username>`). Multi-owner instructions in CLAUDE.md template. |
| Generation | Written by `mb init` with the GH username from `gh auth status` |

### 6. README honesty

| Spec | Value |
|---|---|
| File | `mb-vip/README.md` |
| Required content | "Built for Claude Code. Cross-platform skill support is v0.2+." / "Schema is v1; will evolve." / "Install: `pipx install mainbranch` (recommended) or `git clone github.com/mainbranch-ai/mb-vip` (developer mode)." / Link to compatibility matrix (TBD in v0.2 release notes). |

### 7. End-to-end working flow (Stripe-style hello-world)

| Spec | Value |
|---|---|
| Sequence | `mb init` → `mb think audience` (invokes `/think` skill in Claude Code) → `core/audience.md` is committed |
| Time target | Under 5 minutes on a fresh machine with Claude Code already installed |
| Test | Engine repo CI runs this on a clean container weekly post-launch (v0.2 work; v0.1 is manually verified) |

### 8. PyPI distribution as `pipx install`

| Spec | Value |
|---|---|
| Package name | `mainbranch` (see "PyPI Package Shape" section below for full rationale) |
| Install path | `pipx install mainbranch` |
| Entry point | `mb` (defined via `[project.scripts]` in `pyproject.toml`) |
| Skills shipped | All 13 skills (10 existing + 3 new composables) packaged as data files inside the Python wheel |
| Tools shipped | `tool-*` Go binaries (`tool-domain`, `tool-dns`, `tool-pages`, `tool-stripe`) ship via Homebrew tap (`noontide-co/tap`). `tool-og-render` is bundled with `mainbranch` itself (Python wrapper around `rsvg-convert` + `cairosvg` fallback from PR #100). System dep `librsvg` checked by `mb doctor`. |
| Trusted publisher | GitHub Actions → PyPI per `companyctx` template (`.github/workflows/publish-pypi.yml`) |
| Versioning | Semver. v0.1.0 at launch. Schema-breaking changes bump major. |

---

## What Does NOT Ship in v0.1.0 (engine-side deferred)

Mirrors the noontide-projects master deferral list, with engine-specific items:

| Feature | Why deferred | Target |
|---|---|---|
| `.claude/skills/<x>/molecules/` and `<x>/compounds/` directories | Vocabulary dead. Don't introduce. | Never |
| `mb migrate` (auto) | Manual for first 10 users. `--dry-run` only in v0.1. | v0.2 |
| `mb graph --serve` (HTML UI) | DOT output is fine. UI is downstream. | v0.2 |
| Cross-reference validation in `mb validate` | Frontmatter shape only in v0.1. | v0.2 |
| Schema plugins / custom rules | Hard-coded schema in v0.1. | v1.0 |
| Cross-agent skill execution (Codex/Cursor/Hermes/local LLMs) | Claude Code only in v0.1. | v0.2+ |
| `mb run` (multi-agent runtime) | Switzerland-for-runtimes; Paperclip is the runtime. | Never (intentional) |
| `mb books` (BeanCount CLI) | Templates partial in `devon/finance/`; narrow CLI not built. | v0.2+ |
| `mb access-log <member>` (support tooling) | After webhook ships. | v0.3 |
| Playbook UX wrapper (single progress surface) | v0.1 fan-out is acceptable; polish v0.2. | v0.2 |
| `mb` runnable inside Paperclip routine | Hermes/Paperclip integration is its own packaging surface. | v0.2 |
| Path-config flexibility (renaming `core/` → `brain/` etc.) | Confusion-as-a-Service. Locked. | v0.2 |
| MCP support | Per `feedback_skill_md_over_mcp.md`. CLI + SKILL.md only. | Never |
| Local LLM compatibility claims | Don't make them. Test against Claude Code only. | Never (as a claim) |
| Auto-install of missing tools by skills | Magical; breaks user trust. Print install command, let them choose. | Never (intentional) |
| `tool-*` aliased to `atom-*` for 30 days | Marketing copy mentions it; engine ships `tool-*` only from day one. | Marketing-side only |

---

## PyPI Package Shape

This section is the source of truth for the PyPI package. The noontide-projects master committed to PyPI distribution at v0.1.0 launch; this section names the specifics.

### Package name

**`mainbranch`.**

| Candidate | Pros | Cons | Verdict |
|---|---|---|---|
| `mainbranch-vip` | Brand-aligned w/ "Main Branch" product name | Conflicts with `mainbranch.io` lander; brand-vs-engine collision | Reject |
| `mb-vip` | Matches repo name; short | Too generic for PyPI; `mb` already ambiguous on PyPI | Reject |
| `mainbranch` | Cleanest brand | "Main Branch" is the *product*, not the *engine*; engine is a Noontide artifact | Reject |
| `mainbranch` | Owned by Noontide org (parent), names the engine clearly, hyphenation parses well | Slightly long | **Accept** |

`mainbranch` makes parent-org ownership obvious, leaves room for sibling packages (`noontide-companyctx`, `noontide-morning-paper`), and doesn't conflict with the `mainbranch.io` consumer lander.

### Entry points

```toml
# mb/pyproject.toml
[project]
name = "mainbranch"
version = "0.1.0"

[project.scripts]
mb = "mb.cli:main"
```

`pipx install mainbranch` puts `mb` on PATH. That is the only Python-installed binary.

### What `pipx install` gives the user

| Component | Where it lives after install | How |
|---|---|---|
| `mb` umbrella CLI | `~/.local/bin/mb` (pipx-managed) | Python entry point |
| Skill files (markdown) | `<site-packages>/mb/_data/skills/` | Bundled as package data |
| Playbook files (markdown) | `<site-packages>/mb/_data/playbooks/` | Bundled as package data |
| Educational triage files | `<site-packages>/mb/_data/educational/` | Bundled as package data |
| Consumer-repo templates | `<site-packages>/mb/_data/templates/` | Bundled as package data |
| `tool-*` binaries | NOT installed by pipx | `mb doctor` reports missing; user installs via Homebrew (`brew install noontide-co/tap/tool-domain`) |

`mb init --link-skills` symlinks the bundled skill markdown into `~/.claude/skills/` (or wherever Claude Code looks). `mb init` without that flag scaffolds the consumer repo only and relies on the user's existing `vip` setup.

### How skills are packaged (data files vs Python modules)

Skills stay markdown. Skills are NOT Python modules. The Python package's only job is to:

1. Install `mb` on PATH.
2. Carry skill markdown as **package data** (read-only, bundled in the wheel).
3. Expose `mb skill path <name>` so other tools can find skill files on disk.

The flow when Claude Code invokes `/site`:
- Claude Code looks in its own skills resolution order (`~/.claude/skills/site/SKILL.md` first; `vip_path/.claude/skills/site/SKILL.md` fallback).
- After `pipx install`, the user runs `mb init --link-skills` once which symlinks the bundled skills into the user's Claude Code skills dir.
- Editing the bundled skills is read-only (they live in site-packages); to customize, the user copies the skill into their own `~/.claude/skills/<name>/` and Claude Code's resolution order picks up the override.

This keeps skills as plain markdown (no Python wrapper around them) while still making `pipx install` the single install command.

### Tools (Go binaries) distribution

Per `cli-agent-infra-repos-mining.md`, the discrawl pattern (Homebrew tap + go install) is the right shape for Go CLIs. v0.1.0 distribution:

| Tool | Language | Channel |
|---|---|---|
| `tool-domain` | Go | `brew install noontide-co/tap/tool-domain` |
| `tool-dns` | Go | `brew install noontide-co/tap/tool-dns` |
| `tool-pages` | Go | `brew install noontide-co/tap/tool-pages` |
| `tool-stripe` | Go | `brew install noontide-co/tap/tool-stripe` |
| `tool-og-render` | Python (wrapper around `rsvg-convert` + `cairosvg`) | Bundled with `mainbranch`. System dep: `brew install librsvg` (macOS) or `apt install librsvg2-bin` (Linux). |

Rationale: all four DNS/domain/pages/stripe tools are HTTP/networking workhorses. Go gives single-binary distribution, fast cold-start, no runtime dependency.

`tool-og-render` is the only **non-network** tool — it converts inline SVG to PNG at 1200x630 for OG meta tags. The static SVG (hero text + signature visual + wordmark; no JS, no network, no web fonts) is purpose-built for SVG rasterizers, NOT headless browsers. PR #100 already ships `rsvg-convert` (primary) + `cairosvg` (fallback) — live-tested at `thelastbill.com`. **v0.1.0 keeps that engine.** A code-review agent originally recommended Node/Puppeteer; pressure-tested via Grok 2026-04-29 and confirmed wrong (200MB Chromium dep is overkill for static SVG → PNG; rsvg+cairosvg matches every constraint and is already production-proven). **v0.2+ upgrade path: switch primary to `resvg` (Rust, <3MB binary, sub-10ms render, identical macOS/Linux output)** — Grok's recommended evolution, low-risk drop-in via `brew install resvg`. See "Open Threads" #3 for the upgrade gate.

The `mb` umbrella does NOT bundle these. `mb doctor` reports which are missing and prints the install command. Users install only what they need.

### Version policy

- v0.1.0 at launch.
- Schema changes that break consumer repos bump major (v1.0.0 is the v1 schema lock).
- Bug fixes bump patch (v0.1.1, v0.1.2).
- New skills/playbooks bump minor (v0.2.0, v0.3.0).
- Skill markdown lives at the same version as the Python package (single-version package; skills do not version independently in v0.1).
- Tool binaries (`tool-*`) version independently per the discrawl pattern; `mb doctor` warns on tool-version skew.

### Dependency strategy

Lean. The Python package depends on:
- `click` or `typer` (CLI framework) — pick one, lock version
- `pyyaml` (frontmatter parsing)
- `rich` (TUI output, optional)

Nothing else. No `requests`, no `httpx` in v0.1 (the umbrella does not make network calls — that's tool territory). No async runtime. No DB driver. The umbrella is a thin dispatcher.

### Migration story for current users

Users on the current `git clone mb-vip` setup can transition by:

1. `pipx install mainbranch`
2. `mb init --link-skills` (creates symlinks; safe to run on existing setup)
3. Optionally: `git clone mb-vip` is no longer needed for skills, but stays useful for engine contributors.

Engine contributors (Devon, Joel) keep cloning the repo for development — `pipx install -e .` from the cloned repo lets them edit skills in-place and have changes reflected.

---

## /site Skill Upgrade

This is the single largest engine-side change in v0.1.0. The /site skill goes from a brief-flow target to a brief-flow target *anchored on Hughes' archetype framework + Corey Haines' review gates + the AI-tell anti-pattern list*. All three were locked by the linked research files; this section names the file changes.

### File-by-file change list under `.claude/skills/site/`

| File | Change | Source of content |
|---|---|---|
| `SKILL.md` | Edit. Add brief schema additions section. Reference new files. | This decision |
| `references/minisite-build.md` | Edit Step 2 (Brief draft) → dial pick → archetype pick → adjacency map → four-forces fill. | Hughes yt-mining + Haines mining |
| `references/minisite-generation-system.md` | Edit. Add paired-imagery rule (Hughes). Add OG image formula (Haines image skill). Add "AI hallucinates UI; capture real screenshots" rule. | Haines image skill mining |
| `references/review.md` | Replace gate list with **Seven Sweeps** (dial-gated). | Haines copy-editing skill |
| `references/anti-patterns.md` | Replace/augment with **AI-tell list** verbatim from seo-audit/ai-writing-detection. | Haines seo-audit mining |
| `references/section-patterns.md` | Edit. Add page-structure templates (Compact Landing / Varied / Enterprise / Product Launch). | Haines copy-frameworks |
| `references/archetypes.md` | **NEW.** Catalog of 9 archetypes with one-line blurbs and click-through to per-archetype detail. | Hughes yt-mining |
| `references/archetypes/<slug>.md` (×9) | **NEW.** One file per archetype with: when-to-invoke, audience-current-trap match, do-not-state list, paired-imagery template, headline-formula matches. | Hughes + Haines combined |
| `references/headline-formulas.md` | **NEW.** 20+ headline formulas grouped by frame (outcome / problem / audience / differentiation / proof). Brief draft step picks 2–3 per draft. | Haines copy-frameworks |
| `references/conversion-psychology.md` | **NEW (optional).** Subset of marketing-psychology mapped to dial: `convert` (Anchoring, Loss Aversion, Hick's Law); `story` (Pratfall, Liking, Unity); `brand` (Mere Exposure, Lindy, Peak-End). | Haines marketing-psychology |
| `references/lander-build.md` | Edit. Add "Compact Landing" skeleton from Haines page-structure templates. | Haines copy-frameworks |
| `references/website-build.md` | Edit. Add Site Type Templates (Small Business + Hybrid SaaS) from Haines site-architecture. | Haines site-architecture |
| `references/concept-variations.md` | Unchanged in v0.1 (foreground-subagent rule still load-bearing). | — |
| `references/cloudflare-pages-link.md` | Unchanged. | — |
| `references/deployment.md` | Unchanged. | — |
| `references/examples-and-troubleshooting.md` | Unchanged. | — |
| `references/frontend-design.md` | Unchanged. | — |
| `references/graduation.md` | Unchanged. | — |
| `references/naming-heuristic.md` | Unchanged. | — |

### The 9-archetype catalog (one-line blurbs)

`references/archetypes.md` is the index. Each entry is a one-liner; click through to the per-archetype detail file for when-to-invoke, do-not-state list, paired imagery, and headline formulas.

| Archetype | One-line blurb | Detail file |
|---|---|---|
| Wounded Healer | Person who suffered, healed, now guides others. Coach/teacher/practitioner offers; founders with origin pain. | `archetypes/wounded-healer.md` |
| Savior | Outside force arrives to rescue. Tools/products that "do it for you." | `archetypes/savior.md` |
| Victim | Pure suffering, no agency yet. **Don't position your buyer here on a sales page** — this is what they're escaping. | `archetypes/victim.md` |
| Tragedy Mindset | Nothing can change, fate is sealed. Use to describe the status quo your offer breaks. | `archetypes/tragedy-mindset.md` |
| Broken Hero | Hero who's fallen and must rise again. Comeback / second-chance audiences. | `archetypes/broken-hero.md` |
| Dark Hero | Anti-hero, breaks rules to do right. Contrarian positioning, "the industry hates this." | `archetypes/dark-hero.md` |
| David & Goliath | Small, righteous underdog vs. large, indifferent giant. Challenger brands, anti-establishment offers. | `archetypes/david-goliath.md` |
| Redemption | Bad guy goes to jail / wrong gets righted. Transformation offers — but **don't promise this ending**. | `archetypes/redemption.md` |
| Tragic Comedy | We thought we were in redemption, actually we're in farce. Reframe device when audience expectation is wrong. | `archetypes/tragic-comedy.md` |

**Progressive disclosure rule:** the brief draft step shows `archetypes.md` (the one-line index) by default. Operator picks one, skill loads the per-archetype detail file lazily. /site never loads all 9 detail files at once.

### Brief schema additions

Existing brief schema (in `decisions/YYYY-MM-DD-minisite-brief-<slug>.md`):
- `headline` + `subhead`
- `value_prop`
- `mechanism_summary`
- `picked_supporting_pages`
- `conversion_endpoint`
- `voice_anchor_lines`
- `framework_tag`

**v0.1.0 additions:**

| New field | Type | Required? | Purpose |
|---|---|---|---|
| `dial` | enum: `convert / story / brand` | required | Routes which review sweeps run (see Seven Sweeps below) |
| `archetype` | enum: 9 archetypes (or `null`) | optional but recommended | Drives paired-imagery + headline-formula picks |
| `audience_current_archetype` | string | optional | What audience is *trapped in* (victim/tragedy-mindset). Reframe target for the offer's archetype. |
| `do_not_state` | list[string] | required when archetype set | Conclusions the audience must reach themselves; skill never writes these as headlines |
| `four_forces` | object: `{push, pull, habit, anxiety}` | optional | JTBD frame from Haines product-marketing-context. Useful for `convert` and `story` dials. |
| `voice_anchor_lines` | object: `{use: [], avoid: []}` | already partial; expand to use/avoid pair | Per-site slice from voice.md |
| `headline_formulas_picked` | list[string] | optional, suggested 2–3 | Picked from `headline-formulas.md` |
| `copy_framework_tag` | enum: `PAS / AIDA / StoryBrand / Compact-Landing / Varied / Enterprise-B2B / Product-Launch / null` | optional | Extends existing `framework_tag` with Haines page templates |

**Migration policy:** existing minisite briefs in `noontide-projects/decisions/` use the old schema. Do **not** auto-migrate. New briefs (created after v0.1.0 lands) use the new schema. The `mb validate` schema check tolerates the old schema for files dated before 2026-04-29; flags missing required new fields for files dated 2026-04-29 or later. Old briefs may be hand-upgraded if Devon wants, but no automated migration ships in v0.1.0.

### Seven Sweeps review (dial-gated)

`references/review.md` replaces its current gate list with the Seven Sweeps from Haines copy-editing, dial-gated:

| Sweep | What | `convert` | `story` | `brand` |
|---|---|---|---|---|
| 1. Clarity | Confusing structures, unclear pronouns, jargon | yes | yes | yes |
| 2. Voice & Tone | Read aloud, consistent formality | yes | yes | yes |
| 3. So What | Every claim answers "why should I care?" | yes | yes | no |
| 4. Prove It | Every claim has evidence | yes | no | no |
| 5. Specificity | Vague → concrete | yes | yes | no |
| 6. Heightened Emotion | Does it move you? | yes | yes | yes |
| 7. Zero Risk | Every barrier near CTA addressed | yes | no | no |

- **`convert` dial:** all 7 sweeps. Plus the Expert Panel Scoring rubric (1–10 across 3–5 personas, all ≥7, panel avg ≥8). Brief proceeds only when gate clears.
- **`story` dial:** sweeps 1, 2, 3, 5, 6. Drops Prove-It and Zero-Risk (resonance + archetype-fidelity matter more than evidence).
- **`brand` dial:** sweeps 1, 2, 6 only. Clarity, voice, emotion. Drops everything that pressures the copy toward conversion.

Seven Sweeps replaces the existing `research-grounded / in-voice / de-AI'd / framework-true` gate list. Those gates fold in:
- "research-grounded" → Sweep 4 Prove It (when dial includes it).
- "in-voice" → Sweep 2 Voice & Tone.
- "de-AI'd" → runs as a separate gate alongside Seven Sweeps, sourced from `anti-patterns.md`.
- "framework-true" → runs as a separate gate; checks the `copy_framework_tag` is honored.

### AI-tell anti-pattern list (verbatim from seo-audit/ai-writing-detection)

`references/anti-patterns.md` adopts the seo-audit AI-writing-detection content verbatim:

**Em-dash rule (primary AI tell):** Em-dash is the primary AI tell. Replace with commas, colons, parentheses. **More than 1 em-dash per page = revise.**

**Overused verbs (cut or replace):** delve, leverage, optimize, utilize, facilitate, foster, bolster, underscore, unveil, navigate, streamline, enhance.

**Overused adjectives (cut or replace):** robust, comprehensive, pivotal, crucial, vital, transformative, cutting-edge, groundbreaking, innovative, seamless, intricate, nuanced, multifaceted, holistic.

**AI-flag opening phrases (banned):**
- "In today's fast-paced world,"
- "In the realm of,"
- "It's important to note,"
- "Let's delve into,"
- "Imagine a world where."

**AI-flag transitional phrases (banned):**
- "That being said,"
- "With that in mind,"
- "It's worth mentioning,"
- "At its core,"
- "To put it simply,"
- "In essence,"
- "This begs the question."

**AI-flag concluding phrases (banned):**
- "In conclusion,"
- "To sum up,"
- "By [doing X], you can [achieve Y],"
- "At the end of the day."

**AI-flag structural patterns (banned):**
- "Whether you're a [X], [Y], or [Z]…"
- "It's not just [X], it's also [Y]…"
- Sentences starting with "By [gerund]…"

**Plain English alternatives (Haines plain-english-alternatives.md):** Utilize → Use, Implement → Set up, Leverage → Use, Facilitate → Help, Innovative → New, Robust → Strong, Seamless → Smooth, Cutting-edge → New/Modern.

**Cut these words:** Very, really, extremely, incredibly, just, actually, basically, in order to, that, things, stuff.

The de-AI gate runs as a hard fail: if the draft has more than one em-dash, OR contains any AI-flag phrase, OR uses 3+ overused verbs/adjectives, the gate fails. Operator addresses or proceeds with explicit `--ignore-ai-tells` flag (logged in the brief frontmatter).

### Paired-imagery rule (Hughes)

`references/minisite-generation-system.md` adds the paired-imagery rule. Every visual block is a **pair**, not a single image:

- **Hero:** artifact (the offer made tangible) + status-quo/anomaly pair (the world it disrupts). Reader's eye does the snapping.
- **Features:** old-way scene + new-way scene, no caption gluing them.
- **Testimonial section:** before-state quote + after-state quote, no narrator.
- **OG image:** paired scene rendered in the 1200×630 OG meta-tag block (Haines image skill formula): `[Subject] + [Setting/context] + [Visual style] + [Lighting] + [Composition] + [Technical specs]`.

The image-prompt template is dial-aware:
- `convert` dial → high-clarity, photorealistic, "shot on Canon EOS R5," shallow DoF.
- `story` dial → cinematic, golden hour, archetype-faithful (David imagery vs. Goliath imagery, etc.).
- `brand` dial → minimal, geometric, brand-color-locked, "flowing gradient" / "particle effects."

**Hard rule:** AI hallucinates UI. Never use AI-generated imagery for product UI screenshots. Capture real screenshots, frame in browser/device mockups, annotate with code overlays.

---

## Conductor Preferences for mb-vip

This section is the source of truth for the `conductor-preferences.md` file at the repo root. Adapted from `companyctx`'s preferences (the most fully-developed conductor pattern in Devon's stack), with engine-repo adjustments.

### Branch convention

**Format (when Linear sync is on):** `<linear-username>/<linear-id-lowercase>-<short-descriptor>`
**Format (Linear sync OFF — current state):** `<gh-username>/<short-descriptor>` (e.g., `dmthepm/mb-vip-v0-1-0`).

Engine-repo note: mb-vip does **not** have Linear sync as of 2026-04-29. The current branch (`dmthepm/mb-vip-v0-1-0`) follows the GH-username convention. When Linear sync lands (v0.2 candidate), branch convention rolls over to the companyctx pattern.

Rules (carry over from companyctx):
- Descriptor is kebab-case, under 40 chars.
- No leading verbs (`fix-`, `add-`, `measure-`).
- One slash only.

### One workspace = one branch = one PR

Hard rule. Cross-cutting work that "feels obvious" gets flagged and stopped. Never reuse a branch.

### Two-stage agent flow

| Stage | Trigger | Responsibilities | Forbidden |
|---|---|---|---|
| **Branch-author agent** | Devon assigns issue / opens workspace | Investigate → Write → Validate → Commit → Push to origin → Report. Comment on issue at kickoff, blockers, scope-narrowings, branch-ready, lock/stand-down. | NEVER `gh pr create`. NEVER open draft PR. NEVER auto-open via any tool. |
| **PR-author agent** | Devon clicks Conductor "Merge PR" button | Open PR with conventional-commit title + structured body (Summary / Commits / Acceptance / Test plan). Post one-line issue comment with PR URL. Stop. | Don't re-run gates. Don't push new commits. Don't widen scope. Don't fix CI red — that's a new workspace. |

### Conventional Commits

`feat(scope): ...`, `fix(scope): ...`, `docs: ...`, `test: ...`, `refactor: ...`, `chore: ...`, `ci: ...`. Breaking changes: `!` + `BREAKING CHANGE:` footer.

### Pre-push gate suite (multi-gate, separate)

Engine-repo Python:

```
python -m ruff format --check .   # formatter — separate gate
python -m ruff check .            # linter — separate gate
python -m mypy mb tests           # type check
python -m pytest -q               # tests
```

Engine-repo Go (per tool):

```
go fmt ./...                      # formatter
go vet ./...                      # vet (linter)
golangci-lint run                 # full lint
go test ./...                     # tests
```

**Critical:** `ruff check` (linter) and `ruff format --check` (formatter) are DISTINCT gates. Local `ruff check` passing does NOT imply format is clean.

### Issue thread discipline

Comment on the issue at five specific moments — and ONLY these:
1. Kickoff — restate IN-scope / OUT-scope, link the branch
2. Blocker discovered — name dependency, state stop/narrow/proceed-with-caveat
3. Scope narrowed — document the Slice A / Slice B split before pushing code
4. Branch ready for PR — branch name, summary; Devon clicks Merge PR
5. Lock / stand-down — record stopping point if handing off

**Do NOT comment on every commit.** Commit log + PR body are for that. Issue comments are for decisions that *change the meaning of the work*.

### Multi-commit organization (CONCERN, not chronology)

| Commit type | What goes in it |
|---|---|
| `feat(scope): ...` | Core behavior change |
| `test(scope): ...` | Tests for new behavior (combine with feat if small) |
| `docs: ...` | README, SPEC, SCHEMA, SKILL.md, CHANGELOG, examples |
| `ci: ...` | Workflow edits, gate additions |
| `chore(scope): ...` | Dep bumps, package metadata, mechanical renames |
| `refactor(scope): ...` | Non-behavioral moves |
| `fix(scope): ...` | Bug fixes mid-work |

`git log --oneline main..HEAD` should read like a changelog of the work.

### Reorganize-at-end pattern

In a 1M-context session: do work in one monolithic WIP commit locally. At end:
1. `git reset HEAD~1` (drop WIP)
2. `git add -p` to construct logical commits
3. `git log --oneline main..HEAD` — verify shape
4. THEN push

First push, no force-push concern. Keeps agent fast during work, history clean for reviewers.

### No history rewriting after push

Never rewrite. Follow-up fixes after review = NEW commits on top. **Never force-push a pushed branch.** Never amend a pushed commit. Never `--no-verify`. If a gate fails, fix the root cause and commit the fix as its own commit.

### Public/private smell test

mb-vip is a **public repo**. Apply the test on every commit:

> "Would the reader (anyone with internet) be embarrassed or uncomfortable reading this?"

| Answer | Where it goes |
|---|---|
| Yes | Stays in `noontide-projects` (private). Engine repo does not see it. |
| Meh, fine | mb-vip is fine. |
| Not sure | Default private. Sanitize and re-evaluate. |

Specifically: never commit Devon-personal numbers (MRR, client names, comp data), never commit Skool-member-personal info, never commit live Stripe IDs / API keys, never commit working URLs to private member resources.

### Code review format

- Numbered findings, each with file + line citation
- Severity tag: HIGH / MEDIUM / LOW
- MUST FIX (blocks merge) vs SUGGESTIONS (nice-to-have, fine as follow-ups) — separated
- Verdict at end: APPROVE / REQUEST CHANGES (with must-fix count) / NEEDS DISCUSSION

Output is structured for machine consumption — review is often fed back to authoring agent for fixes.

### Issue body + acceptance checklist as the contract

Before starting any work:
- `gh issue view <N> --comments` — read every comment, oldest to newest
- `gh api repos/<owner>/<repo>/issues/<N>/timeline --paginate` — catches cross-references
- For every linked PR: `gh pr view <PR> --comments` and `gh pr diff <PR>` if load-bearing
- For every linked issue: one-hop recursive read; do not go deeper
- For every file path mentioned: read current state on `main` before assuming shape

**Issue body is a snapshot.** Comments contain scope changes and corrections. Miss a comment, ship against the wrong contract.

---

## OSS / Paid — Engine Side

The noontide-projects master locked the one-line rule: **MIT ships the *shapes*. Paid ships the *contents*.** This section names the engine-side resolution.

### How skills find paid reference

Skills resolve reference paths through `mb`'s resolution logic (`mb/mb/resolve.py`):

```
# Resolution order for `mb resolve voice` (or any reference key):
1. ~/curated/voice/                    # paid private repo (collaborator-gated)
2. <consumer-repo>/core/voice.md       # local override the user wrote
3. <site-packages>/mb/_data/stubs/voice.md   # MIT shipped stub
```

When a skill calls `mb resolve voice`:
- If the paid path resolves, return its content. Skill works fully.
- If only the local path resolves, return its content. Skill works fully.
- If only the MIT stub resolves, return the stub content **plus a banner**: `"This is a public stub. To use Devon's compiled voice corpus, subscribe at mainbranch.io/run."` Skill still runs but produces visibly stub-grade output.

### Missing-reference stub behavior

The stub files in `<site-packages>/mb/_data/stubs/` are short markdown files that:
1. Identify themselves clearly (`# Voice — public stub`).
2. Show the SHAPE of what a voice.md looks like (frontmatter, sections).
3. Tell the user where to get the real one (`Subscribe at mainbranch.io/run for the curated reference.`).
4. Include 2–3 generic example anchor lines that won't conflict with any real brand (fake-business "Acme Brewing" voice, etc.).

This means: an OSS user (free, no subscription) can `pipx install mainbranch`, run `/site` in Claude Code, and get a fully-functional walkthrough that produces a generic-looking site. It works. It just doesn't sound like Devon (or like the user's own brand) until reference is filled in.

### Test mode for OSS users without paid reference

`mb test --skill site` runs the /site skill against a fixture business (`<site-packages>/mb/_data/fixtures/acme-brewing/`) with stub references and asserts the skill produces *something*. This is the v0.1.0 OSS contract: skills are runnable end-to-end against fixtures, even without paid reference.

CI runs `mb test --all` on every PR. If a skill breaks against the fixture, the PR fails.

### v0.1.0 manual collaborator adds

Per the noontide-projects master: first ~10 paid Run/VIP members are added manually to `noontide-co/curated` as outside collaborators. Engine-side, `mb claim --email <email>` is the user-facing fallback that hits a Noontide endpoint, validates Skool membership, and returns the curated repo invite link. Endpoint runs on Cloudflare Worker (per critique #5 deploy-environment recommendation). Implementation is a v0.1.0 Phase 2 deliverable; the engine repo carries the CLI-side glue.

---

## Educational Triage Content (`.claude/educational/`)

The "tell me more" pattern from the noontide-projects master needs an engine-side home. Files live at `.claude/educational/<topic>.md` and are loaded on-demand by `mb` and by skills that enforce opinionated defaults.

### Format

```
---
type: educational
topic: <slug>
status: stable | provisional
last_reviewed: YYYY-MM-DD
---

# <Topic Title>

## Why we recommend this

<short rationale, 2–4 paragraphs>

## What we recommend

<concrete setup>

## Trade-offs

<honest list of what you give up>

## Setup walkthrough

<numbered steps, copy-pasteable>

## Further reading

<links>
```

### Initial topics (v0.1.0)

| File | Triggered by | Subject |
|---|---|---|
| `anti-cloud-backup.md` | `mb doctor` finding `core/finance/` files in iCloud / Drive / Dropbox | Why financial records shouldn't sit in cloud-default backup. Forgejo + Backblaze + restic stack. Subpoena exposure. Encryption-at-rest. |
| `opinionated-stack-cloudflare-vs-vercel.md` | `/site` skill default to Cloudflare Pages | Why Cloudflare Pages over Vercel for Main Branch sites. Pricing. Cold-start. Edge defaults. Lock-in posture. |
| `github-vs-gdocs.md` | First-run `mb init` user comes from a Google-Docs background | Why Markdown-in-git beats Google Docs for business reference. Versioning. Diff. Multi-agent compatibility. The "your business is a tree of files" framing. |

### Pattern reuse

Any skill that enforces an opinionated default (Cloudflare > Vercel, Cal.com > Calendly, BeanCount > QuickBooks, Forgejo > GitHub for personal data) gets a matching `educational/<topic>.md` file. Skills present three options at the warning step: `[t]` Tell me why → loads the file. `[s]` Recommended setup → walks through it. `[n]` Continue anyway → skill proceeds with default.

This pattern is reusable beyond `mb doctor`. It's the standard shape for any opinion the engine bakes in.

---

## Cross-Agent Compatibility (v0.1 honesty)

**Claude Code is the only first-class target in v0.1.0.** README must say so.

| Agent | v0.1.0 status | v0.2+ target |
|---|---|---|
| Claude Code | Fully supported. Skills run end-to-end. Tools called by skills work. | Stays first-class |
| Codex | Skills are not a Codex concept. Manual port required (1–2 days per skill). Not supported. | v0.3 stretch — port `/think` and `/site` |
| Cursor | Cursor Rules can load SKILL.md as guidance but tool routing doesn't work. Manual paste possible. Not supported. | v0.3 stretch |
| Hermes / Paperclip | Skills don't load. `mb` CLI doesn't run inside Paperclip routine. Not supported. | v0.2 — `mb` runnable inside Paperclip routine; migration docs from OpenClaw |
| Local LLMs (llama.cpp, Ollama) | Tool-use protocol parity uneven. Fat skills with 5+ tool calls fail mid-flow on weaker models. Not supported and **no claim made**. | Never (as a default claim). v0.4+ stretch if local tool-use stabilizes. |

### What IS portable in v0.1.0

The schema (`core/`, frontmatter conventions, `mb validate`) and the CLIs (`tool-domain`, `tool-dns`, etc.) run anywhere a shell runs. Engine-side pitch: **"Schema and CLIs portable everywhere; skills work in Claude Code."**

README sentence (verbatim, locked): *"Main Branch v0.1.0 is built for Claude Code. Other agents (Codex, Cursor, Hermes, local LLMs) may run individual skills with manual setup, but full-flow compatibility is a v0.2+ goal. We will publish a compatibility matrix when v0.2 ships."*

Operators who try Cursor and discover skills don't run will churn quietly. We accept this for v0.1.0 and fix in v0.2+.

---

## Risks / Honest Limitations

Eight bullets. Read out loud before merging.

1. **PyPI distribution shape is unproven for skill-bundled packages.** `companyctx` and `morning-paper` are precedent for Python CLIs on PyPI, but neither bundles markdown-as-data the way mb-vip needs to. The `--link-skills` symlink dance is novel; may break on Windows; may confuse users who expect `pipx install` to be self-contained. Mitigation: tested manual fallback (clone-the-engine still works). Failure mode: users grumble about a two-step install.

2. **The 9-archetype catalog is a content-write deliverable, not a code deliverable.** `archetypes.md` plus 9 detail files is roughly 3 days of careful prose. If Devon is the bottleneck, /site upgrade slips. Mitigation: ship index + 3 most-used archetypes (David-Goliath, Wounded-Healer, Broken-Hero) at v0.1.0; ship remaining 6 in v0.1.1 dot release.

3. **Seven Sweeps + Expert Panel Scoring is heavyweight for `convert` dial.** Five-persona scoring per draft adds 2–4 minutes to every brief. Operators may bypass with `--skip-review`. Bypass becomes default. Mitigation: log bypass count in skill telemetry (v0.2 work); if more than 50% of `convert` runs bypass, the gate is wrong-sized.

4. **Brief schema migration policy is "don't auto-migrate."** Existing minisite briefs in noontide-projects will lack `dial`, `archetype`, `do_not_state`, etc. /site will work on them (old schema is tolerated for files dated before 2026-04-29) but will not gate them on the new fields. This is intentional but creates drift: Devon's old briefs and his new briefs are not directly comparable. Mitigation: `mb validate --upgrade-brief <file>` in v0.2 walks an interactive upgrade.

5. **Paired-imagery rule depends on `librsvg` being installed.** OG image generation is the load-bearing part of the rule. `tool-og-render` ships bundled with `mainbranch` but shells out to `rsvg-convert` (system dep) with `cairosvg` Python fallback. If neither is present, /site falls back to single-image OG with a warning. Mitigation: `mb doctor` calls it out clearly; `brew install librsvg` is one-line.

6. **Conductor preferences file is brand-new at the engine repo and untested in workflow.** companyctx-derived preferences are mature in companyctx; pasting them onto a multi-language repo (Python umbrella + Go tools + Node og-render + Markdown skills) may surface gate-suite mismatches we haven't seen. Mitigation: pre-push gate suite ships per-language (Python ruff/mypy/pytest + Go fmt/vet/test + Node lint/test); first PR run will surface anything that's wrong.

7. **No `mb` integration test in v0.1.0 ships against a real consumer repo.** Hello-world flow (`mb init` → `mb think audience`) is verified manually. CI runs `mb test --skill site` against a fixture, but no end-to-end "fresh machine, install pipx, run flow" automation exists. Failure mode: a regression in `mb init` ships and is found by user #1. Mitigation: weekly manual smoke test post-launch; v0.2 work to harness this in CI.

8. **`tool-og-render` shells out to a system dep (`librsvg`).** We can't ship a fully-self-contained binary in v0.1; users need `brew install librsvg` (macOS) or `apt install librsvg2-bin` (Linux). Mitigation: `mb doctor` checks for it and prints the install command. v0.2+ upgrade to `resvg` (single static <3MB Rust binary, no system deps) removes this risk entirely; Grok's pressure-test 2026-04-29 confirmed the upgrade path is low-risk and well-supported.

---

## What Changes (file/path/operational)

Concrete bullet list of file moves, renames, new files. The codification queue for Phase 1.

### File / path moves (within mb-vip)

- New file: `decisions/2026-04-29-mb-vip-v0-1-0-master.md` (this file)
- New file: `conductor-preferences.md` (repo root) — contents per "Conductor Preferences for mb-vip" section
- New file: `pyproject.toml` at repo root (or `mb/pyproject.toml` if the umbrella is a sub-dir package)
- New file: `CODEOWNERS` at `.github/CODEOWNERS`
- New file: `.github/workflows/publish-pypi.yml` (trusted publisher, companyctx template)
- New dir: `tools/` with `tool-{domain,dns,pages,stripe,og-render}/` subdirs (each contains `cmd/`, `SKILL.md`, `README.md`, `RELEASING.md`, lang-appropriate build config)
- New dir: `mb/` with Python package source (`mb/`, `tests/`, `pyproject.toml`, `README.md`)
- New dir: `.claude/playbooks/` with `ship-bet/SKILL.md` and `weekly-review/SKILL.md` skeletons
- New dir: `.claude/educational/` with three initial topic files (`anti-cloud-backup.md`, `opinionated-stack-cloudflare-vs-vercel.md`, `github-vs-gdocs.md`)
- New dir: `.claude/skills/skill-brief-draft/` (composable skill — depth-3 escape hatch)
- New dir: `.claude/skills/skill-concept/` (composable skill)
- New dir: `.claude/skills/skill-review/` (composable skill — wraps Seven Sweeps)
- New dir: `templates/consumer/` with `CLAUDE.md.tmpl`, `CODEOWNERS.tmpl`, `.gitignore.tmpl`

### /site skill file changes (under `.claude/skills/site/`)

- Edit: `SKILL.md` — add brief schema additions section, link new ref files
- Edit: `references/minisite-build.md` — Step 2 dial pick → archetype pick → adjacency map
- Edit: `references/minisite-generation-system.md` — paired-imagery rule, OG formula, "no AI for UI" rule
- Edit: `references/review.md` — replace gate list with dial-gated Seven Sweeps
- Edit: `references/anti-patterns.md` — verbatim AI-tell list from seo-audit
- Edit: `references/section-patterns.md` — add Haines page-structure templates
- Edit: `references/lander-build.md` — add Compact Landing skeleton
- Edit: `references/website-build.md` — add Site Type Templates (Small Business + Hybrid SaaS)
- New: `references/archetypes.md` — index of 9 with one-line blurbs
- New: `references/archetypes/<slug>.md` × 9 — per-archetype detail files (ship 3 at v0.1.0, remaining 6 at v0.1.1)
- New: `references/headline-formulas.md` — 20+ formulas grouped by frame
- New: `references/conversion-psychology.md` — dial-mapped psych principles (optional ref)

### Tool-side changes

- Rename (engine-side): any in-flight `atom-*` references → `tool-*`. v0.1.0 ships `tool-*` only; no aliases on the engine side. (Marketing copy may carry aliases for 30 days per noontide master; engine ships clean.)
- Each tool ships its own `SKILL.md` next to its binary (paperclip/discrawl Pattern A+B hybrid). Frontmatter includes `prerequisites.commands: [tool-<x>]`.
- Each tool ships `init`, `status`, `doctor`, `--version` subcommands minimum (the discrawl triad).
- Each tool ships `-c/--config`, `--json`, `--plain`, `-q/--quiet`, `-v/--verbose`, `--no-color`, `--data-dir` global flags.
- Each tool ships a 1-page `RELEASING.md` (discrawl pattern).
- Coordinated release: all 5 tools tagged at v0.1.0 simultaneously. CHANGELOGs use the discrawl 0.1.0 shape.

### `mb` umbrella behavior

- `mb` Python umbrella dispatches to tools by name (`mb domain ...` → `tool-domain ...` exec).
- `mb` does not bundle tool binaries; calls them via PATH. `mb doctor` reports missing.
- `mb` is the only Python-installed binary. Skills are markdown data inside the wheel.
- `mb skill path <name>` returns the on-disk path to a skill markdown (for Claude Code resolution + user editing).

### Consumer-repo template (`templates/consumer/`)

- `CLAUDE.md.tmpl` — engine-aware CLAUDE.md with placeholder slots for business name, GH username, model preference. Includes link back to mb-vip docs.
- `CODEOWNERS.tmpl` — single-owner default w/ multi-owner instructions in CLAUDE.md.
- `.gitignore.tmpl` — opinionated ignores: `.env`, `*.beancount` (Class B per anti-cloud-backup philosophy), `.DS_Store`, `node_modules/`, `__pycache__/`, `.mypy_cache/`, `.ruff_cache/`.

---

## Phase 1 vs Phase 2

Mirrors the noontide-projects master.

### Phase 1 — `oe-v0.1.0-rc1` — internal, this week (2026-04-29 → 2026-05-06)

Engine-side ships:

- This decision file lands as `decisions/2026-04-29-mb-vip-v0-1-0-master.md`, status `proposed` → `accepted` on merge.
- Repo reorg: skills stay flat, playbooks dir created flat, educational dir created.
- Vocabulary sweep (any remaining `atom-*` / `molecule` / `compound` mentions in skill files → `tool-*` / `skill` / `playbook`).
- /site skill upgrade *outline only*: brief schema doc'd in `SKILL.md`, `archetypes.md` index file lands, 3 archetype detail files land, Seven Sweeps lands in `review.md`, AI-tells lands in `anti-patterns.md`. Remaining 6 archetypes are `status: stub` placeholders that load but say "detail coming v0.1.1."
- Conductor preferences file lands at `conductor-preferences.md`.
- `pyproject.toml` lands; `mb` umbrella package compiles and installs in dev mode (`pipx install -e ./mb`); `mb --version` works.
- Tool source skeletons land in `tools/` (`tool-*/SKILL.md`, `tool-*/cmd/main.go` or equivalent — does not need to compile to ship Phase 1).

No tweet. No Skool announcement. No PyPI publish. Devon migrates his own consumer repo, runs `mb init` against a sandbox dir, fixes drift. Tag `oe-v0.1.0-rc1`.

### Phase 2 — `oe-v0.1.0` — public, 7–10 days later (2026-05-06 → 2026-05-15)

Adds:

- All tool binaries actually compile and pass tests.
- `mb` umbrella publishes to PyPI (`mainbranch` v0.1.0). Trusted-publisher workflow.
- Tools publish to Homebrew tap (`noontide-co/tap`) and `tool-og-render` to npm.
- README.md updates with `pipx install mainbranch` as the recommended path; `git clone` as developer path.
- Compatibility matrix doc lands at `docs/compatibility.md`.
- `mb test --skill site --fixture acme-brewing` ships green.
- /site skill upgrade *full*: remaining 6 archetype detail files ship.

Tag `oe-v0.1.0`. Public.

---

## Review Date

**2026-05-29 (30 days)**, or sooner if:

- PyPI distribution slips past Phase 2 (re-open this file).
- /site brief schema migration breaks more than 2 in-flight Devon briefs (re-open).
- More than 3 of the 9 archetype detail files slip past v0.1.1 (re-open).
- `mb doctor` false-positive rate on anti-cloud-backup detection above 10% (re-open `educational/` design).
- Conductor preferences gate suite causes more than 1 hour of agent rework per PR (re-open the gate scoping).

---

## Open Threads (not blocking acceptance)

Priority-ordered. Devon picks these up after v0.1.0 ships, or punts them with intent.

1. **PyPI package name confirmation.** This file proposes `mainbranch`. If Devon prefers `mainbranch-vip` or `mainbranch` for marketing reasons, the package name changes. Engine-internal is name-agnostic; only the README install line and the `pyproject.toml` name field move. (Priority: high; resolve before Phase 2 PyPI publish.)

2. **Linear sync for mb-vip.** Branch convention rolls over to `<linear-username>/<linear-id-lowercase>-<descriptor>` once Linear sync is on. Cheap to flip; not blocking v0.1.0. (Priority: medium; v0.2 candidate.)

3. **`tool-og-render` engine upgrade to resvg (v0.2+).** v0.1.0 ships `rsvg-convert` + `cairosvg` fallback (PR #100, live-tested). Grok pressure-test 2026-04-29 recommended `resvg` (Rust) as the upgrade path — single static binary <3MB, sub-10ms render, identical macOS/Linux output, no system deps. Drop-in replacement via `brew install resvg`. Gate the swap on: (a) one real failure mode emerging in `rsvg-convert` that resvg fixes, OR (b) v0.2 release window opening. Priority: low; the existing engine works.

4. **Composable skills (`skill-brief-draft`, `skill-concept`, `skill-review`) ownership.** They're new in v0.1.0 and called by /site. If /vsl, /ads, /organic want to call them too, that's a refactor at v0.2. Pre-emptively design for it now, or punt? Punt unless concrete reuse is asked for. (Priority: low.)

5. **Engine-repo Skill folder for `tool-*` SKILL.md files vs co-located in `tools/`.** Currently the plan is co-located: `tools/tool-domain/SKILL.md` lives next to the binary source. Alternative: `.claude/skills/tool-domain/SKILL.md` mirrors. Co-located is cleaner (one ecosystem, single source of truth for the tool's docs); mirror is more discoverable for skills that compose. Pick co-located for v0.1.0; mirror via symlink in v0.2 if discovery becomes a problem. (Priority: low.)

6. **Brief schema migration tooling (`mb validate --upgrade-brief`).** Per Risk #4, the "don't auto-migrate" policy creates drift. v0.2 commitment. Specific shape: walks the operator through each missing required field, suggests defaults from existing fields. (Priority: medium; v0.2.)

7. **Educational triage content beyond the initial three.** As more opinionated defaults land, more `educational/<topic>.md` files are needed. Catalog what's missing: `cal-com-vs-calendly.md`, `beancount-vs-quickbooks.md`, `forgejo-vs-github-personal.md`, `claude-code-vs-cursor.md`, etc. (Priority: medium; rolling.)

8. **The "given my past losses, help me decide today" skill.** Capture mechanism is in place (status: died offers in consumer repos). Skill itself is v0.2+ build. Engine-side: read `core/offers/<slug>/` files where status is `died`, surface the post-mortem rationale during `/think` calls that look similar. (Priority: low; nice-to-have.)
