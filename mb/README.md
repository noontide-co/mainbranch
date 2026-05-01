# mainbranch (`mb`)

Engine umbrella for [Main Branch](https://github.com/noontide-co/mainbranch) — scaffolds, validates, and graphs business-as-files repos.

This package is the Python entry point. Skills, playbooks, educational content, and consumer-repo templates ship as bundled package data. The actual day-to-day "do work" surfaces are Claude Code skills (markdown), invoked from inside Claude Code.

The source tree keeps skills and playbooks in one place: repo-root `.claude/skills/` and `.claude/playbooks/`. During sdist/wheel builds, `setup.py` copies those directories into `mb/_data/skills/` and `mb/_data/playbooks/` inside the build artifact so installed wheels can resolve `mb skill list` without a source checkout.

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
| `mb init` | Scaffold a new business repo (six folders, CLAUDE.md, CODEOWNERS, `git init`). One question only: business name. |
| `mb doctor` | Diagnostic. Checks Claude Code, gh auth, network, librsvg. Warns on cloud-backed finance paths and offers educational triage. |
| `mb validate` | Frontmatter shape check across `decisions/`, `core/offers/`, `research/`, `log/`, `campaigns/`, `documents/`. Exit 1 on any fail. |
| `mb graph` | Walk linked_research / linked_decisions / supersedes; emit Graphviz DOT to stdout. `--open` shells to `dot` + `open`. |
| `mb think <topic>` | Print the /think skill invocation hint for Claude Code (or run inside a session). |
| `mb resolve <key>` | Resolve a reference path through the OSS / paid layered lookup. |
| `mb skill path <name>` | Print the on-disk path to a bundled skill. |
| `mb educational <topic>` | Print an educational triage file. Powers `mb doctor`'s "tell me more" prompts. |

## Status

v0.1 is **Built for Claude Code only**. Cross-agent compatibility is a v0.2+ commitment. The schema is v1 and will evolve. The engine decision lives at `decisions/2026-04-29-mb-vip-v0-1-0-master.md`; the business-side master plan is tracked in `noontide-co/projects#119`.

## License

MIT.
