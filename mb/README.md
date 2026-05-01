# mainbranch (`mb`)

Engine umbrella for [Main Branch](https://github.com/noontide-co/mainbranch) — scaffolds, validates, and graphs business-as-files repos.

This package is the Python entry point. Workflows, playbooks, educational content, and consumer-repo templates ship as bundled package data. In v0.1.x, the day-to-day "do work" surfaces are packaged as Claude Code skills (markdown), invoked from inside Claude Code. The `mb` CLI is runtime-agnostic by design: future adapters should let Codex, Cursor, OpenClaw, Hermes, and local runtimes operate against the same business-as-files repo.

The source tree keeps the engine payload in one place: repo-root `.claude/`. During sdist/wheel builds, `setup.py` copies that tree into `mb/_engine/.claude/` inside the build artifact so installed wheels can resolve skills, playbooks, reference files, lenses, and educational prompts without a source checkout.

## Install

```bash
pipx install mainbranch
```

That puts `mb` on your PATH. Verify:

```bash
mb --version
```

## Subcommands (v0.1)

| Command | What it does |
|---|---|
| `mb init` | Scaffold a new business repo (six folders, CLAUDE.md, CODEOWNERS, `git init`) and wire the bundled Claude Code skill adapter. One question only: business name. |
| `mb doctor` | Diagnostic. Checks Claude Code, gh auth, network, librsvg, runtime wiring, and package freshness. Warns on cloud-backed finance paths and offers educational triage. |
| `mb validate` | Frontmatter shape check across `decisions/`, `core/offers/`, `research/`, `log/`, `campaigns/`, `documents/`. Exit 1 on any fail. |
| `mb graph` | Walk linked_research / linked_decisions / supersedes; emit Graphviz DOT to stdout. `--open` shells to `dot` + `open`. |
| `mb think <topic>` | Print the /think workflow invocation hint for the currently supported runtime. |
| `mb resolve <key>` | Resolve a reference path through the OSS / paid layered lookup. |
| `mb skill path <name>` | Print the on-disk path to a bundled skill. |
| `mb skill link --repo <path>` | Wire or repair Claude Code skill discovery for a business repo. Future runtime adapters should get equivalent wiring commands. |
| `mb educational <topic>` | Print an educational triage file. Powers `mb doctor`'s "tell me more" prompts. |

## Status

v0.1 is **Claude Code first**. Runtime compatibility for Codex, Cursor, OpenClaw, Hermes, and local runtimes is a v0.2+ commitment. The schema is v1 and will evolve. The runtime boundary decision lives at `decisions/2026-05-01-mb-cli-vs-agent-workflows-boundary.md`; the engine master decision lives at `decisions/2026-04-29-mb-vip-v0-1-0-master.md`.

## License

MIT.
