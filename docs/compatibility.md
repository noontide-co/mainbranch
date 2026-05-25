# Compatibility

Main Branch is intentionally narrow today: `mb`, bundled Claude Code skills,
and global Codex `mb-*` skills. This page is the public compatibility contract
for those surfaces.

## Supported matrix

| Surface | Current status | Notes |
|---|---|---|
| macOS | Supported | Primary development path. Recommended for beginners. |
| Linux | Supported for `mb`; supported when Claude Code is installed | CI runs the Python package on Linux. Claude Code must be installed separately. |
| Windows | Experimental | Not tested in CI. Use WSL2 for the closest supported path. |
| Python | 3.10, 3.11, 3.12 | CI gates all three versions. |
| Install mode | `pipx install mainbranch` | Official public install path. |
| Developer mode | Git clone | For contributors who want to edit the engine or skills. |
| Agent runtime | Claude Code | Supported through project-local slash skills. |
| Codex CLI | Supported | Fresh business repos include `AGENTS.md`; global Main Branch `mb-*` skills install once per user under `~/.codex/skills` and route through deterministic `mb` facts. `mb workflow list --runtime codex` exposes supported, pending, and unsupported workflow surfaces. |
| Cursor, OpenClaw, Hermes, Paperclip-adjacent orchestration, local LLMs | Roadmap | `mb` is runtime-agnostic by design, but these adapters are not supported yet. |

**Windows tip — try WSL2.** If you're on Windows and want a working setup today, use [Windows Subsystem for Linux 2 (WSL2)](https://learn.microsoft.com/en-us/windows/wsl/install). Inside WSL2, follow the supported Linux flow. The pipx install path works there.

Main Branch intentionally does not run a `windows-latest` CI gate while Windows
is experimental. Windows bugs are useful signal, but release quality is gated on
the supported macOS/Linux path and the Linux Python CI matrix.

## What "supported" means

Supported means:

- CI runs the relevant Python gates before merge.
- The documented setup path is expected to work.
- Bugs should be filed as GitHub issues.
- Regressions in the supported path are release-quality problems.

Experimental means:

- The path may work for power users.
- It is not part of the release gate.
- Workarounds are welcome, but breakage is not treated as a launch blocker.

Roadmap means:

- The surface is a product target, not a support claim.
- There is no supported adapter yet.
- Public docs should not tell users to rely on it.

For agent runtimes, support requires the runtime adapter contract in
[decisions/2026-05-04-skill-cli-runtime-adapter-contract.md](../decisions/2026-05-04-skill-cli-runtime-adapter-contract.md):
discovery rules, install/update behavior, generated-file and state rules,
`mb doctor` / `mb status` / `mb start` expectations, and fresh-repo runtime
smoke evidence. Claude Code is the reference adapter today.

For release-bearing Claude Code smoke evidence, use the
[Claude Code runtime dogfood runbook](claude-code-runtime-dogfood.md).

For the exact supported Claude Code slash-command behavior, including
`/mb-start`, extra text after the slash command, natural-language routing, and
skill-link repair, see
[Claude Code Invocation Contract](claude-code-invocation-contract.md).

## Packaged CLI invocation

`mb` is a normal console command in the `mainbranch` Python package:

```bash
pipx install mainbranch
mb --version
```

If the package is installed in an environment where the console script is not
on `PATH`, `python3 -m mb --version` exercises the same package entrypoint.

Automation callers do not need to run inside Claude Code to use deterministic
CLI facts. A Paperclip-style routine, local script, CI job, or future runtime
adapter should treat `mb` as a subprocess with an explicit business repo:

```bash
repo="/absolute/path/to/business-repo"
mb status "$repo" --json --peek
mb start --repo "$repo" --json
mb validate "$repo" --json
mb graph "$repo" --json
mb connect status --repo "$repo" --json
```

Use the command's exit code, stdout JSON, and stderr output as the automation
contract. Do not scrape human Rich output when a `--json` form exists. Do not
require Claude Code environment variables, Claude-specific local settings, or a
human terminal session for these CLI checks.

Common shipped automation-safe commands include:

| Need | Command shape |
|---|---|
| Package/version check | `mb --version` |
| Daily repo facts | `mb status "$repo" --json --peek` |
| Runtime handoff metadata | `mb start --repo "$repo" --json` |
| Repo health | `mb doctor "$repo" --json` |
| Repair preview | `mb doctor repair --repo "$repo" --plan --json` |
| Agent-surface repair preview | `mb doctor repair --repo "$repo" --plan --only claude`, `--only codex`, or `--all-agents` |
| Frontmatter/schema validation | `mb validate "$repo" --json` |
| Graph/index facts | `mb graph "$repo" --json` |
| Provider readiness | `mb connect status --repo "$repo" --json` |
| Checkpoint preview | `mb checkpoint --repo "$repo" --plan --json` |
| Update dry-run | `mb update --repo "$repo" --check --json` |
| Bundled skill inventory | `mb skill list` |
| Bundled skill validation | `mb skill validate --all --json` |
| Claude Code start wiring repair preview | `mb doctor repair --repo "$repo" --plan --json` |
| Claude Code skill-link repair preview | `mb skill repair --repo "$repo" --json` |

Some current commands are runtime handoff hints, not workflow execution. For
example, `mb think <topic>` prints the `/mb-think` hint for Claude Code today;
it does not run a model and does not yet expose a stable JSON workflow launcher.
Future commands such as bookkeeping reconciliation or packaged workflow runners
should be documented only after the command and JSON contract exist.

## Runtime path discovery

Non-Claude callers must discover the business repo path from their own runtime
or orchestration config, then pass it to `mb` or run with that repo as the
working directory. Safe discovery sources include:

- an explicit runtime setting such as `MAINBRANCH_REPO` or an equivalent
  project config field;
- the current working directory when the runtime was launched from a business
  repo;
- a user-selected workspace/project folder;
- a caller-owned manifest that stores repo paths outside public docs and avoids
  credentials.

Docs, adapters, and examples should not hardcode maintainer-specific home
directory paths. If a sample needs a path, use placeholders like
`/absolute/path/to/business-repo` or shell variables such as `$repo`.

Runtime config may point at a business repo, an engine install, and optional
provider tools. Credentials, OAuth tokens, API keys, raw exports, and local
machine preferences must stay outside tracked business files. Business
memory remains in the repo's tracked `core/`, `research/`,
`decisions/`, `bets/`, `pushes/`, `log/`, and `documents/` files.

## Connector and provider readiness

Connector availability is runtime-specific. A Claude.ai web connector does not
prove that Claude Code, Codex, Conductor, or another agent runtime can use the
same tool. Each surface needs its own visible tool list or deterministic CLI
check, restart behavior, OAuth/scope refresh path, and read-only smoke before
docs or skills should rely on it.

Use `mb connect status --repo "$repo" --json` for Main Branch provider rails.
Use the runtime's own tool surface for Claude.ai, Claude Code, Codex, Conductor,
or future adapters. For the decision table that separates `mb connect`,
Claude.ai connectors, Claude Code bridged tools/MCP/plugins,
Codex/Conductor tools, local CLI/API-key paths, and unsupported providers, run:

```bash
mb educational provider-readiness
```

## Runtime adapter readiness map

This map compares runtime surfaces without claiming support before adapters and
smoke evidence exist.

| Runtime surface | Status | Invocation | Skill/workflow discovery | Routing and automation | Observability and packaging |
|---|---|---|---|---|---|
| Claude Code | Supported | `mb start --repo "$repo"` prints the `claude` handoff; `mb start --launch` may launch after readiness checks. | `mb skill link --repo "$repo"` writes project-local `.claude/skills/mb-*` bridge links and `.claude/settings.local.json`. | Slash commands such as `/mb-start` and `/mb-think` own conversation and judgment; they call deterministic `mb` commands for facts. | `mb doctor`, `mb status --json`, `mb start --json`, `mb skill repair`, and runtime dogfood evidence gate release claims. Skills ship inside the Python package today. |
| Codex CLI | Supported | Can call deterministic `mb` commands as a subprocess when pointed at a business repo. `AGENTS.md` gives Codex the repo bootstrap, and global Main Branch skills give Codex `mb-*` workflow routes. | Fresh `mb onboard` repos include tracked `AGENTS.md`. `mb doctor repair --plan --only codex` / `--apply --only codex` refresh repo guidance and install or repair the global Codex skill bundle. Use `--all-agents` only after reviewing both Claude and Codex surface writes. | Codex `mb-*` skills run `mb status --json --peek`, `mb start --json`, `mb doctor repair --plan --json`, `mb checkpoint --plan --json`, `mb validate --json`, and `mb workflow list --runtime codex --json` as needed, translate facts into business language, and ask before writes. | `mb doctor`, `mb status --json`, `mb start --json`, and `mb workflow list` expose Codex readiness and workflow support. Codex support covers start/status/setup/update/doctor, think/codify, end/checkpoint/save, validate, and workflow discovery. Ads, organic, site, bet, and playbook routes are installed for discovery but remain read-only planning unless their support level says otherwise. |
| Cursor | Roadmap | Can call deterministic `mb` commands from terminal/tasks when pointed at a business repo. | No supported Cursor rules/package adapter yet. | No supported Main Branch routing contract. | Needs adapter docs, install/update rules, conflict handling, and smoke evidence. |
| OpenClaw | Roadmap | Target public runtime surface. It should call `mb` through stable CLI/JSON commands rather than clone-era paths. | No supported OpenClaw adapter yet. | Main Branch should coexist with OpenClaw as the business repo/GitHub memory layer, not replace it. | Needs explicit adapter shape, migration notes, generated-file rules, and smoke evidence. |
| Hermes | Roadmap | Target runtime/memory surface. It may supervise or host workflows that call packaged `mb` commands. | No supported Hermes adapter yet. | Hermes-specific routing belongs in the Hermes adapter, while `mb` remains deterministic and non-conversational. | Docs may describe internal-package expectations generically, but not as the only blessed public path. Smoke evidence is required before support claims. |
| Paperclip-adjacent orchestration | Roadmap | Best understood as orchestration or supervision. A routine can run `mb status`, `mb validate`, `mb graph`, `mb connect status`, or other shipped deterministic commands against an explicit repo path. | Paperclip should not assume Claude Code skills are available unless a separate runtime adapter provides that discovery layer. | Paperclip may sequence deterministic checks and handoffs; model conversation, retries, and judgment stay in the hosted runtime/workflow layer. | Needs package install contract, repo-path config, log/exit-code handling, and smoke evidence before experimental/support status. |
| Local runtimes | Roadmap | Can call deterministic `mb` commands as subprocesses when pointed at a business repo. | No supported local-runtime adapter yet. | No supported workflow routing, prompt packaging, or model invocation through `mb`. | Needs endpoint/runtime discovery, generated-file and secret rules, and fresh-repo smoke evidence. |

## Workflow coverage today

The CLI/repo contract and the slash-skill workflow contract have different
support levels:

Shared workflow sources under `workflows/` are runtime-agnostic contracts.
Runtime shells, Claude Code skills, generated `AGENTS.md`, Codex command
plugins, and future adapter packages should stay thin over those sources. A
checked shared workflow source does not by itself make every runtime supported;
support still requires an adapter and smoke evidence for that runtime.

| Surface | Claude Code | Other runtimes and orchestrators |
|---|---|---|
| Deterministic CLI facts (`mb status --json`, `mb validate --json`, `mb graph --json`, `mb connect status --json`) | Supported when `mb` is installed and pointed at a business repo. | Callable as packaged CLI subprocesses, but this does not make the hosting runtime supported. |
| Runtime handoff (`mb start --json`, `mb start --launch`) | Supported for Claude Code handoff and launch readiness. | Codex CLI handoff metadata is supported for global skill readiness: `mb start --json` reports Codex executable, `AGENTS.md`, global skills, and runtime `mb` readiness. `mb` does not launch Codex. |
| Lifecycle slash skills (`/mb-start`, `/mb-status`, `/mb-setup`, `/mb-update`, `/mb-end`, `/mb-help`) | Supported through Claude Code project-local skill discovery. | Codex supports matching global skills (`mb-start`, `mb-status`, `mb-setup`, `mb-update`, `mb-doctor`, `mb-end`, `mb-help`) grounded in deterministic `mb` facts. |
| Production slash skills (`/mb-think`, `/mb-ads`, `/mb-organic`, `/mb-site`, `/mb-wiki`, `/mb-bet`) | Supported through Claude Code skills, subject to each skill's provider and workflow limits. Conversion scripts route through the owning workflow instead of a standalone primitive or skill. | Codex supports `mb-think` through `workflows/mb-think/workflow.md` and global skills. Ads, organic/newsletter, site, bet, and shipped playbook names are installed for inventory and read-only planning. Wiki and skill-authoring workflows are intentionally unsupported for the current Codex target. |
| Automation routines | May call CLI commands before handing judgment work to Claude Code. | May call shipped deterministic CLI commands against an explicit repo path. Conversation, retries, routing, and model invocation belong to the runtime adapter, not `mb`. |

## Adapter checklist

Before a non-Claude surface moves out of roadmap status, its PR or decision must
document:

- runtime executable, plugin, endpoint, or package discovery;
- install, update, restart, and repair commands;
- workflow discovery and human invocation syntax;
- generated files, tracked-vs-gitignored rules, and secret handling;
- `mb doctor`, `mb status --json`, and `mb start --json` readiness behavior;
- exact fresh-repo smoke evidence and known limitations.

That evidence should prove the runtime reads the business repo and does not
write runtime state, credentials, or raw account data into tracked files.

For the Codex staging plan, see
[Codex Adapter Plan](../decisions/2026-05-08-codex-adapter-plan.md). The current
implementation is the daily Main Branch slice: generated `AGENTS.md`, global
Main Branch Codex skills, deterministic readiness facts, doctor repair coverage,
`mb workflow list`, and
compact workflow discovery for start/status/setup/update/doctor, think/codify,
end/checkpoint/save, validate, and workflow inventory. The think route is checked against
`workflows/mb-think/workflow.md` as the first official shared workflow source
pattern, and fresh read-only Codex smoke covers the supported skill surface from a
business repo. It does not claim all-skill parity, copied Claude skill parity,
provider/publishing workflow support, spend, or customer-contact support.
Codex plugin slash commands are not the readiness path until runtime smoke proves
they load in Codex Desktop.

## Recommended setup

For most users:

```bash
pipx install mainbranch
mb onboard --name "My Business" --path my-business
cd my-business
mb start --launch
```

Use `mb init my-business --name "My Business"` when you need the quiet,
scriptable scaffold primitive without the human setup flow.

For contributors:

```bash
git clone https://github.com/noontide-co/mainbranch.git
cd mainbranch
```

Use clone mode only if you are editing the engine, docs, or bundled skills.

## Updating

For normal Claude Code users, run:

```text
/mb-update
```

For CLI automation and power users, use the update contract from inside your
business repo:

```bash
mb update
```

`mb update` detects whether Main Branch is a `pipx` install or source checkout,
runs the appropriate update path, and then runs the explicit surface-refresh
path by default: Claude Code skill links/guidance plus Codex global skills and
repo `AGENTS.md` from the upgraded `mb` executable. Use `mb update --check` for
a dry-run, `mb update --json` for automation, and `--no-refresh-surfaces` only
when deliberately updating the package without touching runtime surfaces.
Inside Claude Code, `/mb-update` calls `mb update` for this mechanical step and keeps
ownership of the human-readable "what's new" summary. Codex users should open a
fresh Codex thread after an update so refreshed global skills are loaded.

Early `0.1.x` installs do not have `mb update` yet. If `mb`, `mb doctor`,
`mb status`, or `mb start` says "Update required", run this once first:

```bash
pipx upgrade mainbranch
```

Then run these from your business repo:

```bash
mb skill link --repo .
mb skill repair --repo .
mb doctor
```

## Known Limits

- Claude Code is supported through project-local slash skills.
- Codex CLI is supported through global Main Branch `mb-*` skills and
  deterministic `mb` facts. Main Branch does not claim all-skill parity, copied Claude skill
  parity, provider writes, publishing, spend, or customer-contact workflows.
- Windows is experimental.
- Skills are bundled into the installed Python package, so public users update
  skills by upgrading `mainbranch`.
- The CLI scaffolds, validates, graphs, resolves, and links the current Claude
  Code skill adapter. Most business workflows still happen through Claude Code
  slash commands.
- Claude Code slash-command discovery depends on project-local
  `.claude/skills/mb-*` bridge links in the business repo. The
  `.claude/settings.local.json` `additionalDirectories` entry grants engine
  file access, but it is not enough by itself for reliable `/mb-start`
  discovery.
- Cursor, OpenClaw, Hermes, Paperclip-adjacent orchestration, and local
  runtimes remain roadmap surfaces until each has a documented adapter and
  smoke evidence. Codex support is limited to the skill surface above.
