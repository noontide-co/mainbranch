# mainbranch (`mb`)

Engine umbrella for [Main Branch](https://github.com/noontide-co/mainbranch) — scaffolds, validates, and graphs business-as-files repos.

This package is the Python entry point. Workflows, playbooks, educational content, and consumer-repo templates ship as bundled package data. Today, the day-to-day "do work" surfaces are packaged as Claude Code skills (markdown), invoked from inside Claude Code. The `mb` CLI is runtime-agnostic by design: future adapters should let Codex, Cursor, OpenClaw, Hermes, and local runtimes operate against the same business-as-files repo.

The source tree keeps the engine payload in one place: repo-root `.claude/`. During sdist/wheel builds, `setup.py` copies that tree into `mb/_engine/.claude/` inside the build artifact so installed wheels can resolve skills, playbooks, reference files, lenses, and educational prompts without a source checkout.

## Install

```bash
pipx install mainbranch
```

That puts `mb` on your PATH. Verify:

```bash
mb --version
```

## Subcommands

| Command | What it does |
|---|---|
| `mb onboard` | Human setup flow. Creates or connects a business repo, explains the local files/git/GitHub substrate, wires Claude Code skills, verifies discovery, and prints the next `/start` step. Supports `--yes` and `--json` for smoke tests. |
| `mb init` | Scaffold a new business repo (six folders, CLAUDE.md, CODEOWNERS, `git init`) and wire the bundled Claude Code skill adapter. One question only: business name. |
| `mb doctor` | Diagnostic. Checks Claude Code, gh auth, network, librsvg, runtime wiring, and package freshness. Warns on cloud-backed finance paths and offers educational triage. |
| `mb status` | Daily briefing. Summarizes repo shape, install/runtime readiness, recent brain files, recent git activity, and GitHub tasks when `gh` is authenticated. Supports `--json`. |
| `mb start` | Runtime handoff. Verifies the current business repo, git, Claude Code, and `/start` skill wiring, then prints the exact `claude` command or launches it with `--launch`. Supports `--json`. |
| `mb validate` | Frontmatter shape check across `decisions/`, `core/offers/`, `research/`, `log/`, `campaigns/`, `documents/`. Exit 1 on any fail. |
| `mb graph` | Walk linked_research / linked_decisions / supersedes; emit Graphviz DOT to stdout. `--open` shells to `dot` + `open`. |
| `mb update` | Refresh the Main Branch engine according to install mode (`pipx` upgrade or clone `git pull`) and repair skill links. `--check` dry-runs; `--json` emits an envelope. |
| `mb think <topic>` | Print the /think workflow invocation hint for the currently supported runtime. |
| `mb resolve <key>` | Resolve a reference path (checks free first, then paid). |
| `mb skill path <name>` | Print the on-disk path to a bundled skill. |
| `mb skill link --repo <path>` | Wire or repair Claude Code skill discovery for a business repo. Future runtime adapters should get equivalent wiring commands. |
| `mb educational <topic>` | Print an educational triage file. Powers `mb doctor`'s "tell me more" prompts. |

## Status

Main Branch is **Claude Code first** with a strong CLI front door: `mb onboard`, `mb status`, `mb start`, and `mb update` are public package surfaces. Runtime compatibility for Codex, Cursor, OpenClaw, Hermes, and local runtimes remains roadmap work. The schema is v1 and will evolve. The runtime boundary decision lives at `decisions/2026-05-01-mb-cli-vs-agent-workflows-boundary.md`; the engine master decision lives at `decisions/2026-04-29-mb-vip-v0-1-0-master.md`.

## License

MIT.
