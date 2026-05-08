# Main Branch

[![Star on GitHub](https://img.shields.io/github/stars/noontide-co/mainbranch?style=social&label=Star)](https://github.com/noontide-co/mainbranch)
[![PyPI version](https://img.shields.io/pypi/v/mainbranch?style=flat&label=PyPI)](https://pypi.org/project/mainbranch/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Durable operating memory for AI-assisted businesses. Ship growth and ops work from files you own.**

---

## Why

Every SaaS tool gets better with every model update — and raises its prices. Your stuff should get better on your own computer.

You already feel it. Your offer lives in Notion. Your voice lives in a thousand Loom transcripts. Your audience research is in three Google Docs you can't find. Every chat session with your AI starts from zero — you re-paste, re-explain, re-describe, and the output is still generic. One of our members called it *building on quicksand*. That's the right word.

You're renting your business. Not just the dashboards — the operational memory itself.

The open-source gap closed in 2025. The tools to own your stack exist now. Almost nobody has carved time to migrate, because there is no coherent environment that ties it together.

Main Branch is that environment. Your offer, audience, voice, decisions, research, bets, pushes (launches, drops, challenges, promos — whatever your business calls them), meeting notes, fulfillment context, and operating lessons live as markdown files in a git repo you own. The `mb` CLI scaffolds and checks it. The bundled skills read those files and help ship work from what your business already knows.

The end state isn't sitting at a terminal all day. It's the opposite — eventually you dump thoughts from your phone, drafts get made, finance and fulfillment signals roll up, the team sees what is moving, you approve the risky actions, and the system executes the boring rails. We're not all the way there. The work is still real. But the substrate is the right one to build on.

Every bet you ship leaves a lesson. The lessons update your offer, your audience, your voice. Your business gets smarter every week — without you having to remember. The agent recommends; you make the call.

We run our own businesses on this. Inside our Skool community you watch us do it live: shipping offers through `mb`, running real ad accounts, and building the agency on top of it.

Own the work. Rent only the rails.

---

## What it is

Main Branch is the `mb` CLI plus MIT-licensed agent workflows for running a local-first business operating repo. It's built for operators and small teams running real businesses: solo founders, small agencies, course creators, productized services, indie SaaS, and small ecom teams. Today the workflows ship for Claude Code. Codex, Cursor, OpenClaw, Hermes, and local runtimes are compatibility targets, not supported adapters yet.

The repo is the operating memory: offer, audience, voice, research, decisions, bets, pushes, logs, documents, meeting summaries, fulfillment notes, safe finance summaries, and provider refs. The CLI is the deterministic control plane: setup, status, validation, graph, provider readiness, updates, checkpoints, and repair. The skills are the judgment layer: research, decide, write, review, ship, and reflect.

Main Branch is opinionated about rails. The point is not to connect every SaaS tool a business has accumulated. The point is to choose boring, inspectable paths: GitHub for durable work threads, proposals, and shipped history; Cloudflare for sites and DNS; provider paths such as Google/Workspace and official ads only where smoke-tested; planned optional rails such as Postiz for social scheduling and Beancount-style plain-text finance; and optional sidecars for enrichment. Those paths should be wrapped in deterministic commands agents can call without wasting tokens guessing provider setup.

Read the product frame in [docs/ETHOS.md](docs/ETHOS.md), the four operator loops (Sense → Decide → Ship → Reflect) and the four channels (Paid, Organic, Pages, Ops) in [docs/OPERATOR-LOOPS.md](docs/OPERATOR-LOOPS.md), and the release direction in [docs/ROADMAP.md](docs/ROADMAP.md).
Workspace, repo, dashboard, finance/legal, and team-log boundaries are defined
in
[decisions/2026-05-04-workspace-repo-sensitive-data-boundaries.md](decisions/2026-05-04-workspace-repo-sensitive-data-boundaries.md).
Markdown/link conventions for GitHub and Obsidian live in
[docs/markdown-link-conventions.md](docs/markdown-link-conventions.md).
Dependency, integration, sidecar, and provider-adapter choices are recorded in
[docs/DEPENDENCY-CHOICES.md](docs/DEPENDENCY-CHOICES.md).

---

## Quick start

```bash
pipx install mainbranch
mb onboard --name "My Business" --path my-business
cd my-business
claude
/mb-start
```

That's it. `mb onboard` guides the human setup, creates or connects your business repo, wires Claude Code to the bundled skills, and shows the exact next commands. `mb init` still exists as the quiet scriptable primitive underneath it. `/mb-start` then reads the deterministic status facts, checks whether the repo needs repair or an update, and routes you to setup, thinking, shipping, or closing work.

After the first session, the daily flow is:

```bash
cd ~/Documents/GitHub/my-business
claude
/mb-start
```

`/mb-start` reads `mb status --json --peek` internally, so you do not need to
run `mb status` first. Use `mb status` when you want the same deterministic
briefing in the terminal without opening Claude Code. If you want `mb` to check
handoff readiness and open Claude Code for you, run `mb start --launch` from
the business repo.

The normal day should feel like business work, not GitHub administration:

1. Start in the business repo.
2. Let `/mb-start` ground Claude in `mb` facts: repo health, status, updates,
   graph links, provider readiness, and recent activity.
3. Dump thoughts or pick a next action. Claude should route that input into the
   right Main Branch primitive: a bet, research note, decision, push, playbook,
   outcome, log entry, or checkpoint.
4. Use the skills for judgment-heavy work and `mb` for deterministic checks,
   repair, validation, graph/status facts, provider readiness, and commits.
5. Close with `/mb-end` or `mb checkpoint` guidance so the lesson, decision,
   artifact, or saved work lands in git before the next session.

Under the hood, Main Branch uses issues, branches, pull requests, commits,
graph links, provider refs, and local connection state to preserve and inspect
progress. You can inspect those details when you want them, but the default
language stays closer to the business: bets, goals, offers, pushes, playbooks,
outcomes, and checkpoints.

You'll need a Claude Pro ($20/mo) or Max subscription. Install Claude Code itself from [claude.ai](https://claude.ai) — see [docs/BEGINNER-SETUP.md](docs/BEGINNER-SETUP.md) for a step-by-step.

Tested on macOS and Linux. Windows is experimental and not part of the CI
release gate; see [docs/compatibility.md](docs/compatibility.md). Power users
on Windows should use WSL2 for the closest supported path.

**New to Claude Code, git, or terminal?** Read [docs/BEGINNER-SETUP.md](docs/BEGINNER-SETUP.md) — it covers everything step-by-step, including common errors.

**Contributors** who want to hack on skills can clone the engine repo directly:

```bash
git clone https://github.com/noontide-co/mainbranch.git
```

---

## What you can do

Once set up, you can:

- Research topics and document decisions
- Open, update, close, and narrate business bets
- Generate batches of ad copy in your voice
- Create video scripts for Meta ads
- Generate organic content — Reels, TikTok, carousels — from your core files and research
- Write VSL scripts for your community
- Review ads for compliance before you run them
- Build and deploy Cloudflare-backed landing pages from your core files and research when the repo is connected and readiness checks pass
- Capture meeting transcripts, source material, and fulfillment notes into durable docs, logs, research, or decisions
- Close sessions intentionally with crystallize moments

All of this happens through simple slash commands. No custom prompt engineering required for supported workflows.

---

## How it works

Main Branch has three layers:

- **Your repo is canonical memory.** It holds the durable business truth:
  core files, research, decisions, bets, pushes, logs, documents, and links to
  child repos.
- **`mb` is the deterministic control plane.** It scaffolds, validates, graphs,
  briefs, repairs, checkpoints, updates, and checks provider readiness.
- **Skills are the judgment layer.** Claude Code reads repo truth, asks the
  operator questions, drafts work, reviews it, and routes artifacts back into
  files.

The CLI and skills are meant to work together. Skills should call `mb` for
facts instead of guessing at repo health, provider setup, or update state. The
CLI should stay deterministic and scriptable instead of becoming a chat client
or model host.

You create a separate folder for YOUR business. That's where your offer,
audience, voice, proof, operations, research, decisions, bets, pushes, logs, and
documents live. The engine reads those files. Then it helps produce work and
records what changed so the next session starts from the same memory.

After running `mb init`, your business repo looks like this:

```
my-business/
├── CLAUDE.md
├── .gitignore
├── .github/
│   └── CODEOWNERS
├── .mb/
│   └── schema_version
├── .claude/
│   ├── settings.local.json    (gitignored — wires Claude Code to bundled skills)
│   └── skills/                (gitignored — bridge symlinks)
├── core/
│   ├── vocabulary.md
│   ├── offers/
│   ├── proof/
│   ├── brand/
│   ├── strategy/
│   ├── operations/
│   └── finance/
├── research/
├── decisions/
├── bets/
├── log/
├── pushes/
├── campaigns/                 # legacy compatibility read only
└── documents/
```

You fill in the durable business files inside `core/`. Claude reads them when generating.
Old repos may still have `campaigns/`; `mb` reads it for compatibility, but
new coordinated work belongs in `pushes/`.

As a business grows, related work can graduate into child repos: sites,
products/offers, client fulfillment repos, private finance repos, or ops repos.
The business repo stays the hub. Future dashboard work should map those repos
and their pushes, bets, commits, issues, PRs, checkpoints, provider-safe
summaries, and active decisions. The dashboard is the map, not the source of
truth.

### Connected accounts live with the business repo

Your business repo carries the boundaries for connected accounts. A repo for
one business can point at one Stripe account, Google Ads customer, ad pixel set,
and MCP server set; a different business repo should point at different ones.
Switching repos should switch the tools that can spend money, publish, email,
or mutate customer accounts.

The repo should keep useful non-secret identifiers where agents can inspect
them: Stripe account/product/price IDs in offer or finance notes, Google Ads
customer and campaign IDs (provider's term for their object) in
`pushes/<push>/push.md` `provider_refs:`, ad pixel IDs beside the site or
push files they belong to, and MCP server names/scopes in `CLAUDE.md` or
local setup notes. Do not commit API keys, OAuth refresh tokens,
service-account JSON, webhook secrets, MCP tokens, or bearer tokens. Keep
secrets in a runtime's local config, the OS keychain, 1Password, `.env`, or
`.claude/settings.local.json`, and keep those files gitignored.

---

## The `mb` CLI

The CLI surface for the engine. Built for Claude Code first; runtime-agnostic by design. Most workflows still happen via slash-prompt skills inside Claude Code today — the `mb` CLI is the scaffolder, validator, grapher, updater, and future adapter layer around them.

| Command | What it does |
|---|---|
| `mb onboard` | Human setup flow: create or connect a business repo, explain the substrate, wire Claude Code skills, and show the next `/mb-start` step. |
| `mb onboard status` | Show durable onboarding progress from `.mb/onboarding.json`, including missing core-reference inputs and the next recommended action. |
| `mb init` | Set up a fresh business repo (business folders, CLAUDE.md, git init). |
| `mb status` | Show the local-first briefing in the terminal without opening Claude Code: ranked next actions, since-last-check changes, drift, repo health, runtime wiring, recent decisions/research/bets/git activity, and GitHub tasks/proposals when `gh` is authenticated. Use `--json` for the v1 status schema, `--verbose` for detail, and `--peek` for non-mutating reads. |
| `mb doctor` | Check the environment — repo shape, frontmatter sanity, settings on disk. Use `mb doctor repair --plan` / `--apply` for guided repo reconciliation; add `--include-migration` only after reviewing the migration preview. |
| `mb connect` | Register provider credentials, test provider health, and inspect repair-safe integration status without committing secrets. |
| `mb site check` | Check local paid-traffic measurement readiness for a site repo: GTM installation, Main Branch dataLayer events, consent posture, Google Ads plan metadata, and operator-review gates. |
| `mb issue draft` | Create a local, privacy-scrubbed GitHub issue draft under `.mb/issue-drafts/` for bugs, feature gaps, or questions. |
| `mb issue open` | Submit a reviewed issue draft with `gh issue create`, or print a browser/manual fallback when GitHub CLI is unavailable. |
| `mb validate` | Frontmatter shape check across `core/`, `research/`, `decisions/`, `bets/`, `log/`, `pushes/` (and legacy `campaigns/` as compatibility), `documents/`. Pass/fail per file. |
| `mb graph` | Build a repo graph index from frontmatter links, wikilinks, and entity tags. Emits Graphviz DOT by default, `--json` for agents/dashboards, and `--open` to render a PNG view. |
| `mb similar-bets` | Find similar past bets and offer outcomes from repo truth so new work can learn from old attempts. |
| `mb checkpoint` | Plan or save a business-readable git checkpoint during long agent runs. |
| `mb think <topic>` | Print the `/mb-think` invocation hint. Run inside Claude Code for the full flow. |
| `mb resolve <key>` | Resolve a reference key from the curated library, local core files, or bundled stubs. |
| `mb educational <topic>` | Print an educational triage file (powers `mb doctor`'s "tell me more" prompts). |
| `mb skill list` | List the skills bundled with this engine. |
| `mb skill path <name>` | Print the on-disk path to a bundled skill. |
| `mb skill validate <name>` | Validate one bundled skill's frontmatter, local references, and 500-line gate. Use `--all --json` for CI. |
| `mb skill link --repo .` | Repair Claude Code skill discovery in a business repo and back up stale or broken Main Branch personal symlinks. |
| `mb skill repair --repo .` | Detect personal Claude Code skills that shadow Main Branch and explain safe repair. Use `--apply` only for stale Main Branch symlinks or broken links with Main Branch skill names. |

Full list: `mb --help`.

### Provider Connections

`mb connect` is the local-first foundation for supported, planned, and optional
provider rails such as GitHub, Cloudflare, Google, Meta, Postiz, Apify,
Beancount, and transcription providers.
Use `mb connect plan` when you are not sure what to connect first; it explains
GitHub, Cloudflare, Google/Workspace, Meta Ads, and Apify as numbered business
choices with the current readiness state and exact next command.

```bash
mb connect plan
mb connect list
printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata token_type=account --metadata account_id=...
mb connect test cloudflare
mb connect doctor
mb connect status --json
mb educational provider-readiness
```

Secrets are stored outside the business repo, using the macOS Keychain when
available and a local `~/.mainbranch/secrets/connect.json` fallback otherwise.
The business repo only receives non-sensitive, gitignored metadata in
`.mb/connect.yaml`, such as the provider id, account label, credential backend,
account-token type, and last check time.
Stored credentials start as `unvalidated` until `mb connect test <provider>`
runs the safest available check. Providers with a safe API probe validate
against the provider; providers without one record that local credential
presence was confirmed and that no automated probe exists yet. A secret ref
alone is never reported as healthy.
`mb connect status --json` and `mb connect doctor --json` include safe repair
fields such as `state`, `summary`, `repair`, `repair_command`, and
`safe_to_share` for onboarding agents. Skills and future dashboards should read
those JSON commands or `.mb/connect.yaml`; they should never ask users to commit
tokens.
`--from-env` is explicit: `mb connect` does not silently import general-purpose
environment variables.

---

## Skills

Skills are pre-built workflows you invoke with slash prompts. Instead of figuring out how to prompt Claude, you type `/mb-ads` and Claude knows exactly what to do — reads your business files, then generates output that matches your voice.

The supported Claude Code contract is project-local skill discovery through the
business repo's `.claude/skills/mb-*` bridge links. Plain `/mb-start` is the
daily entrypoint; extra text after it is treated as normal instruction, not a
stable `$ARGUMENTS` command API. See
[docs/claude-code-invocation-contract.md](docs/claude-code-invocation-contract.md).

Some skills ship growth work. Others maintain operating memory. `/mb-start`,
`/mb-status`, `/mb-think`, `/mb-bet`, `/mb-end`, `mb checkpoint`, `mb graph`,
and `mb connect` are as important as the content skills because they keep the
repo understandable, current, and safe to operate from.

| Skill | What it does |
|---|---|
| `/mb-start` | Main entry point — figures out what you need and routes you there |
| `/mb-status` | Thin Claude Code wrapper over `mb status --json --peek` for daily briefing facts and ranked next actions |
| `/mb-setup` | Set up your business repo (run this first if you're new) |
| `/mb-think` | Research, make decisions, add context, transcribe local recordings, update durable business files |
| `/mb-bet` | Open, update, close, list, and narrate business bets |
| `/mb-ads` | Create ad copy (static or video) and review for compliance |
| `/mb-vsl` | Write video sales letter scripts (Skool or B2B) |
| `/mb-organic` | Generate organic content — Reels, TikTok, carousels |
| `/mb-site` | Generate and deploy landing pages from your core files and research |
| `/mb-wiki` | Personal wiki with atomic notes |
| `/mb-end` | Close session — summary, crystallize, approved checkpoint guidance |
| `/mb-help` | Get answers, troubleshoot, learn the system |
| `/mb-update` | Update Main Branch — delegates install-mode refresh to `mb update` and summarizes what's new |
| `/mb-pull` | Legacy alias for `/mb-update` |

---

## Honest Current State

- **Built for Claude Code today.** `mb` is runtime-agnostic by design, but Claude Code is the only first-class runtime currently supported end to end.
- **The terminal front door is live.** Bare `mb`, `mb onboard`, `mb status`, `mb start`, and `mb update` are in the public package.
- **Growth is the strongest shipped wedge.** Ads, organic, VSLs, sites, bets, pushes, status, and checkpoints are the most developed public workflows.
- **Ops is the expansion path.** Meetings, fulfillment, bookkeeping/P&L, team daily logs, repo topology, and dashboard views use the same memory model, but they are less shipped than the growth surfaces.
- **Provider automation is curated and gated.** GitHub and Cloudflare paths are the most concrete today. Google/Workspace, Meta Ads, Google Ads/GTM, Postiz, Apify, Beancount, and transcription are wired as planned or optional provider/sidecar surfaces until each path has smoke evidence.
- **Schema is v1; will evolve.** Frontmatter shapes covered by `mb validate` are stable for the current major; breaking changes bump the major.
- **Runtime compatibility is still ahead.** Codex, Cursor, OpenClaw, Hermes, and local LLMs are roadmap targets, not supported adapters yet.

| Runtime | Status | Notes |
|---|---|---|
| Claude Code | Supported today | First-class adapter with skill wiring, repair, and smoke-tested first-run flow. |
| Codex | Roadmap | Target runtime; no public adapter support claim yet. |
| Cursor | Roadmap | Target runtime; no public adapter support claim yet. |
| OpenClaw | Roadmap | First-tier compatibility target because users operate there; no adapter support claim yet. |
| Hermes / Paperclip-adjacent orchestration | Roadmap | Target orchestration layer; must consume stable repo and JSON contracts. |
| Local runtimes | Roadmap | Long-range endpoint once adapter contracts are proven. |

The engine v0.1.0 decision lives at [`decisions/2026-04-29-mb-vip-v0-1-0-master.md`](decisions/2026-04-29-mb-vip-v0-1-0-master.md). Some historical planning happened in private Noontide repos; public product truth now lives in this repository's decisions, docs, issues, changelog, and releases.

---

## Roadmap

The current package is the CLI + Claude Code first-run foundation plus the first daily operating surfaces: `mb status`, `/mb-status`, next-action ranking, bets, pushes, checkpoints, provider readiness, site checks, and privacy-safe issue drafting. Next work keeps tightening those loops, expands the curated provider rails, and prepares the future dashboard as a map over repo truth rather than a replacement for it. See [docs/ROADMAP.md](docs/ROADMAP.md) for the public roadmap and the current GitHub issue anchors. Direction, not promises.

The proposed long-range product direction is captured in
[`decisions/2026-05-02-github-native-business-os.md`](decisions/2026-05-02-github-native-business-os.md):
Main Branch as a GitHub-native business operating system, with `mb` as the
control plane, GitHub as the team layer, graph/structured data as the
intelligence layer, and agent runtimes as execution.

- **v0.3.x: Tightens the daily operating loop.** Status/ranking, `/mb-start`, `/mb-status`, doctor repair, checkpoints, pushes, provider readiness, and issue drafting keep becoming clearer and more reliable.
- **v0.4: Bets and pushes become operating systems.** Stronger links between bets, offers, pages, ads, outcomes, fulfillment, Ops, and public narration.
- **Longer range.** Runtime adapters, dashboard/server mode, repo topology, structured data, deeper Ops surfaces (meetings, books, P&L, compliance), and richer Paid, Organic, and Pages workflows.

See [CHANGELOG.md](CHANGELOG.md) for what's in this release. Each release ships a "What this means for you" plain-English section above the technical detail.

---

## Open source vs paid community

Plain English boundary so nobody is surprised:

- **Open-source (free, MIT)**: the `mb` CLI, bundled skills, schema, framework, docs, and future local dashboard surface when it ships. The engine is usable without joining the paid community.
- **Paid community (Skool)**: Want to watch us build companies live with Main Branch? Free for 7 days, $19/mo after. The community can include live narration, calls, support, and curated examples that are not required for the open-source engine.

Main Branch is usable on its own. The paid community is the live narration and support layer on top.

---

## Updating

- **Normal user path**: run `/mb-update` inside Claude Code. It figures out
  which install you have and runs the right thing.
- **Power user CLI path**: `mb update --repo .` from your business repo.
- **Clone (developer mode)**: `git pull origin main` from the engine repo.

`/mb-start` checks for important updates at the beginning of a session and will
tell you when updating matters. The CHANGELOG entry for the new version
surfaces as a banner the next time you run `/mb-start`.

---

## FAQ

**Do I need to know how to code?**
No. You invoke skills with slash prompts and answer questions.

**What if I have multiple products under one brand?**
Use one repo with an `offers/` folder when the products share the same brand,
team, voice, and access boundary. Each offer gets its own `offer.md`. If an
offer graduates into its own team, provider accounts, site, finance boundary,
or operating history, move it into its own repo and keep the company repo as a
hub.

**What's a bet vs. an offer?**
A bet is a time-boxed operating hypothesis: what you'll try, why, by when, and how you'll know if it worked. An offer is a durable thing you sell. A good bet can graduate into an offer, push, workflow, content pillar, or decision; a bad bet gets closed with learning.

**What if I have multiple separate businesses?**
Create a separate repo for each brand, legal entity, provider-account boundary,
or team-access boundary. If businesses truly share the same voice, team, and
access rules, they can share a repo. If not, separate repos.

**How do I update when new skills come out?**
Run `/mb-update` inside Claude Code. Power users can run `mb update --repo .`
from the business repo.

If `mb --version` still says `0.1.x`, ask Claude to help bootstrap the update.
The fallback is `pipx upgrade mainbranch` once before using `mb update`; old
installs now surface this as an in-product "Update required" alert on the main
launch, doctor, status, and start surfaces. Existing business repos should then
be repaired with `mb skill link --repo .`, `mb skill repair --repo .`, and
`mb doctor` from the repo root. See [docs/MIGRATING.md](docs/MIGRATING.md) for
the old-repo path.
`/mb-pull` still works as a legacy alias, but new docs teach `/mb-update`.

**Can Claude migrate an old setup for me?**
Yes. Start Claude Code anywhere and paste the prompt in
[docs/MIGRATING.md](docs/MIGRATING.md#recommended-let-claude-walk-you-through-it).
Claude should inspect first, update Main Branch through `/mb-update` or
`mb update`, recommend one repo at a time, and ask before applying repairs or
layout migrations.

**Can I edit the skills?**
You can, but you don't need to. They're designed to work out of the box.

**What makes this different from ChatGPT?**
ChatGPT is a chat surface that resets between sessions. Main Branch is a CLI plus a skill set that reads files Claude can re-read every session — your offer, audience, voice, decisions, research, and bets — so outputs stay consistent with your business instead of restarting from zero.

**I'm stuck. What do I do?**
Type `/mb-start` again. It picks up where you left off.

---

## Help

**In the Skool community:** post in the Main Branch group. Tag @Devon for technical questions.

**Not in the Skool community?** Open an issue at [github.com/noontide-co/mainbranch/issues](https://github.com/noontide-co/mainbranch/issues).

For platform support and security reporting, see [SUPPORT.md](SUPPORT.md), [SECURITY.md](SECURITY.md), and [docs/compatibility.md](docs/compatibility.md).

**Common issues:**

- "404 error" or "Repository not found" — verify the URL and your network. The repo is public; no access request needed.
- "Claude doesn't see my files" — make sure you started Claude in your business repo folder and ran `/mb-start`.
- "Skills aren't working" — run `mb skill link --repo .` from your business repo to repair bridge symlinks and known stale Main Branch shadows, then restart Claude. If still broken, run `mb skill repair --repo .` to inspect unresolved personal-skill conflicts or run `/mb-setup`.
- "Output sounds generic" — add more detail to your core files, especially `core/voice.md`.
- "I edited Main Branch but can't push" — that's expected for most users. Main Branch is the shared engine. Your business data goes in YOUR repo.

**Turn friction into a public issue:** run `mb issue draft bug --command "mb doctor" --what-happened "..."` from your business repo. Review the local draft under `.mb/issue-drafts/`, then run `mb issue open <draft> --yes` when it is safe to submit. See [docs/issue-drafting.md](docs/issue-drafting.md).

---

## Technical details

Contributors should start with [AGENTS.md](AGENTS.md) and
[CONTRIBUTING.md](CONTRIBUTING.md). Claude Code-specific repo guidance lives in
[CLAUDE.md](CLAUDE.md). You don't need any of these to get started as a user.

All shipping decisions are dated, versioned, and committed alongside the code that implements them.

---

## Community

[skool.com/main](https://skool.com/main)
