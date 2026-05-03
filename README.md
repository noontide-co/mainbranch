# Main Branch

[![Star on GitHub](https://img.shields.io/github/stars/noontide-co/mainbranch?style=social&label=Star)](https://github.com/noontide-co/mainbranch)
[![PyPI version](https://img.shields.io/pypi/v/mainbranch?style=flat&label=PyPI)](https://pypi.org/project/mainbranch/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Run your business as files in git. Stop renting it from someone else's dashboard.**

---

## Why

Every SaaS tool gets better with every model update — and raises its prices. Your stuff should get better on your own computer.

You already feel it. Your offer lives in Notion. Your voice lives in a thousand Loom transcripts. Your audience research is in three Google Docs you can't find. Every chat session with your AI starts from zero — you re-paste, re-explain, re-describe, and the output is still generic. One of our members called it *building on quicksand*. That's the right word.

You're renting your business. Not just the dashboards — the operational memory itself.

The open-source gap closed in 2025. The tools to own your stack exist now. Almost nobody has carved time to migrate, because there's no coherent environment that ties it together.

Main Branch is that environment. Your offer, audience, voice, decisions, research, and campaigns live as markdown files in a git repo you own. The `mb` CLI scaffolds it. The bundled skills read those files and produce work that sounds like you — without re-prompting.

The end state isn't sitting at a terminal all day. It's the opposite — eventually you dump thoughts from your phone, drafts get made, you approve, it executes. We're not all the way there. The work is still real. But the substrate is the right one to build on.

We run businesses on this ourselves. The Skool community wraps Main Branch — you watch us ship offers through `mb` live, on real ad accounts, including the AI-native agency arm we're building on top of it.

Own the work. Rent only the rails.

---

## What it is

Main Branch is the `mb` CLI plus MIT-licensed agent workflows for running business-as-files systems. Today the workflows ship for Claude Code; Codex, Cursor, OpenClaw, Hermes, and local runtimes are next. Your offer, audience, voice, research, decisions, and campaigns live in six folders inside your own git repo — versioned, portable, agent-readable.

---

## Quick start

```bash
pipx install mainbranch
mb onboard --name "My Business" --path my-business
cd my-business
claude
/start
```

That's it. `mb onboard` guides the human setup, creates or connects your business repo, wires Claude Code to the bundled skills, and shows the exact next commands. `mb init` still exists as the quiet scriptable primitive underneath it. `/start` walks you through the rest — gathers your business context (offer, audience, voice), drafts the reference files, and routes you to the right workflow.

After the first session, the daily flow is:

```bash
cd ~/Documents/GitHub/my-business
mb status
claude
/start
```

You'll need a Claude Pro ($20/mo) or Max subscription. Install Claude Code itself from [claude.ai](https://claude.ai) — see [docs/BEGINNER-SETUP.md](docs/BEGINNER-SETUP.md) for a step-by-step.

Tested on macOS and Linux. Windows is experimental; see [docs/compatibility.md](docs/compatibility.md) and track [#137](https://github.com/noontide-co/mainbranch/issues/137).

**New to Claude Code, git, or terminal?** Read [docs/BEGINNER-SETUP.md](docs/BEGINNER-SETUP.md) — it covers everything step-by-step, including common errors.

**Contributors** who want to hack on skills can clone the engine repo directly:

```bash
git clone https://github.com/noontide-co/mainbranch.git
```

---

## What you can do

Once set up, you can:

- Research topics and document decisions
- Generate batches of ad copy in your voice
- Create video scripts for Meta ads
- Generate organic content — Reels, TikTok, carousels — from your reference files and research
- Write VSL scripts for your community
- Review ads for compliance before you run them
- Build and deploy landing pages from your reference files
- Close sessions intentionally with crystallize moments

All of this happens through simple slash commands. No prompting skills required.

---

## How it works

Main Branch is the engine. Your business info is the fuel.

```
ENGINE (mb CLI + skills)    YOUR REPO (fuel)
Has all the skills    +     Has your business info
                      =     Outputs that sound like you
```

You create a separate folder for YOUR business. That's where your offer, audience, voice, and testimonials live. The engine reads those files. Then it generates content specific to you.

After running `mb init`, your business repo looks like this:

```
my-business/
├── CLAUDE.md
├── .gitignore
├── .claude/
│   ├── settings.local.json    (gitignored — wires Claude Code to bundled skills)
│   └── skills/                (gitignored — bridge symlinks)
├── core/
│   ├── offers/
│   └── finance/
├── research/
├── decisions/
├── log/
├── campaigns/
└── documents/
```

You fill in the reference files inside `core/`. Claude reads them when generating.

### Connected accounts live with the business repo

Your business repo carries the boundaries for connected accounts. A repo for
one business can point at one Stripe account, Google Ads customer, ad pixel set,
and MCP server set; a different business repo should point at different ones.
Switching repos should switch the tools that can spend money, publish, email,
or mutate customer accounts.

The repo should keep useful non-secret identifiers where agents can inspect
them: Stripe account/product/price IDs in offer or finance notes, Google Ads
customer and campaign IDs in `campaigns/`, ad pixel IDs beside the site or
campaign files they belong to, and MCP server names/scopes in `CLAUDE.md` or
local setup notes. Do not commit API keys, OAuth refresh tokens,
service-account JSON, webhook secrets, MCP tokens, or bearer tokens. Keep
secrets in a runtime's local config, the OS keychain, 1Password, `.env`, or
`.claude/settings.local.json`, and keep those files gitignored.

---

## The `mb` CLI

The CLI surface for the engine. Built for Claude Code first; runtime-agnostic by design. Most workflows still happen via slash-prompt skills inside Claude Code today — the `mb` CLI is the scaffolder, validator, grapher, updater, and future adapter layer around them.

| Command | What it does |
|---|---|
| `mb onboard` | Human setup flow: create or connect a business repo, explain the substrate, wire Claude Code skills, and show the next `/start` step. |
| `mb init` | Set up a fresh business repo (six folders, CLAUDE.md, git init). |
| `mb status` | Show a local-first daily briefing: repo health, runtime wiring, recent decisions/research/git activity, and GitHub tasks when `gh` is authenticated. |
| `mb doctor` | Check the environment — repo shape, frontmatter sanity, settings on disk. Walks you through fixes. |
| `mb connect` | Register provider credentials and integration metadata without committing secrets. |
| `mb validate` | Frontmatter shape check across `core/`, `research/`, `decisions/`, `log/`, `campaigns/`, `documents/`. Pass/fail per file. |
| `mb graph` | Build a repo graph index from frontmatter links, wikilinks, and entity tags. Emits Graphviz DOT by default, `--json` for agents/dashboards, and `--open` to render a PNG view. |
| `mb think <topic>` | Print the `/think` invocation hint. Run inside Claude Code for the full flow. |
| `mb resolve <key>` | Resolve a reference path (checks free first, then paid). |
| `mb educational <topic>` | Print an educational triage file (powers `mb doctor`'s "tell me more" prompts). |
| `mb skill list` | List the skills bundled with this engine. |
| `mb skill path <name>` | Print the on-disk path to a bundled skill. |
| `mb skill validate <name>` | Validate one bundled skill's frontmatter, local references, and 500-line gate. Use `--all --json` for CI. |
| `mb skill link --repo .` | Repair Claude Code skill discovery in a business repo. |

Full list: `mb --help`.

### Provider Connections

`mb connect` is the local-first foundation for integrations such as Google,
Meta, Cloudflare, Postiz, Apify, Beancount, and transcription providers.

```bash
mb connect list
printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata account_id=...
mb connect meta --from-env
mb connect status --json
```

Secrets are stored outside the business repo, using the macOS Keychain when
available and a local `~/.mainbranch/secrets/connect.json` fallback otherwise.
The business repo only receives non-sensitive metadata in `.mb/connect.yaml`,
such as the provider id, account label, credential backend, and last check time.
Skills and future dashboards should read `mb connect status --json` or
`.mb/connect.yaml`; they should never ask users to commit tokens.
`--from-env` is explicit: `mb connect` does not silently import general-purpose
environment variables.

---

## Skills

Skills are pre-built workflows you invoke with slash prompts. Instead of figuring out how to prompt Claude, you type `/ads` and Claude knows exactly what to do — reads your business files, then generates output that matches your voice.

| Skill | What it does |
|---|---|
| `/start` | Main entry point — figures out what you need and routes you there |
| `/setup` | Set up your business repo (run this first if you're new) |
| `/think` | Research, make decisions, add context, transcribe local recordings, update reference files |
| `/ads` | Create ad copy (static or video) and review for compliance |
| `/vsl` | Write video sales letter scripts (Skool or B2B) |
| `/organic` | Generate organic content — Reels, TikTok, carousels |
| `/site` | Generate and deploy landing pages from your reference files |
| `/wiki` | Personal wiki with atomic notes |
| `/end` | Close session — summary, crystallize, commit |
| `/help` | Get answers, troubleshoot, learn the system |
| `/pull` | Quick update — delegates install-mode refresh to `mb update` and summarizes what's new |

---

## Honest Current State

- **Built for Claude Code today.** `mb` is runtime-agnostic by design, but Claude Code is the only first-class runtime currently supported end to end.
- **The terminal front door is live.** Bare `mb`, `mb onboard`, `mb status`, `mb start`, and `mb update` are in the public package.
- **Schema is v1; will evolve.** Frontmatter shapes covered by `mb validate` are stable for the current major; breaking changes bump the major.
- **Runtime compatibility is still ahead.** Codex, Cursor, OpenClaw, Hermes, and local LLMs are roadmap targets, not supported adapters yet.

The engine v0.1.0 decision lives at [`decisions/2026-04-29-mb-vip-v0-1-0-master.md`](decisions/2026-04-29-mb-vip-v0-1-0-master.md). The business-side master plan is tracked in [`noontide-co/projects#119`](https://github.com/noontide-co/projects/pull/119).

---

## Roadmap

The current package is the CLI + Claude Code first-run foundation. Next work deepens GitHub activity, credential/config foundations, graph/indexing, and runtime compatibility. Direction, not promises.

The proposed long-range product direction is captured in
[`decisions/2026-05-02-github-native-business-os.md`](decisions/2026-05-02-github-native-business-os.md):
Main Branch as a GitHub-native business operating system, with `mb` as the
control plane, GitHub as the team layer, graph/structured data as the
intelligence layer, and agent runtimes as execution.

- `mb books` — BeanCount integration for ledger workflows ([#128](https://github.com/noontide-co/mainbranch/issues/128))
- `mb fulfillment` — agency-arm tooling for delivery ops
- Runtime compatibility — Codex, Cursor, OpenClaw, Hermes, local LLMs
- Deeper `/site` workflows — lander → minisite → website graduation
- Dashboard — visual operating loop for your bets and decisions, ships **free as part of `mb`** when the graph/sync substrate is ready
- Skool → GitHub webhook automation

See [CHANGELOG.md](CHANGELOG.md) for what's in this release. Each release ships a "What this means for you" plain-English section above the technical detail.

---

## Open source vs paid community

Plain English boundary so nobody is surprised:

- **Open-source (free, MIT)**: the `mb` CLI, all bundled skills, the schema, the framework, and the dashboard when it ships. Anyone can install and run — no account, no gating, no upsell wall.
- **Paid community (Skool)**: Want to watch us build companies live with Main Branch? Free for 7 days, $19/mo after.

Main Branch is fully usable on its own. The paid community is the live narration on top.

---

## Updating

- **pipx users (most people)**: `pipx upgrade mainbranch`. Or just run `/pull` inside Claude Code — it figures out which install you have and runs the right thing.
- **Clone (developer mode)**: `git pull origin main` from the engine repo.

The CHANGELOG entry for the new version surfaces as a banner the next time you run `/start`.

---

## FAQ

**Do I need to know how to code?**
No. You invoke skills with slash prompts and answer questions.

**What if I have multiple products under one brand?**
Use one repo with an `offers/` folder. Each offer gets its own `offer.md`. Soul and voice stay shared in `core/`. Run `/setup` or `/think` to add offers.

**What if I have multiple separate businesses?**
Create a separate repo for each brand. If they share the same soul and voice, they can share a repo. If not, separate repos.

**How do I update when new skills come out?**
`pipx upgrade mainbranch`, or run `/pull` inside Claude Code.

If `mb --version` still says `0.1.x`, run `pipx upgrade mainbranch` once before
using `mb update`; old installs now surface this as an in-product
"Update required" alert on the main launch, doctor, status, and start
surfaces. Existing business repos should then run `mb skill link --repo .` and
`mb doctor` from the repo root. See
[docs/MIGRATING.md](docs/MIGRATING.md) for the old-repo path.

**Can I edit the skills?**
You can, but you don't need to. They're designed to work out of the box.

**What makes this different from ChatGPT?**
ChatGPT is a chat surface that resets between sessions. Main Branch is a CLI plus a skill set that reads files Claude can re-read every session — your offer, audience, voice, decisions, research — so outputs stay consistent with your business instead of restarting from zero.

**I'm stuck. What do I do?**
Type `/start` again. It picks up where you left off.

---

## Help

**In the Skool community:** post in the Main Branch group. Tag @Devon for technical questions.

**Not in the Skool community?** Open an issue at [github.com/noontide-co/mainbranch/issues](https://github.com/noontide-co/mainbranch/issues).

For platform support and security reporting, see [SUPPORT.md](SUPPORT.md), [SECURITY.md](SECURITY.md), and [docs/compatibility.md](docs/compatibility.md).

**Common issues:**

- "404 error" or "Repository not found" — verify the URL and your network. The repo is public; no access request needed.
- "Claude doesn't see my files" — make sure you started Claude in your business repo folder and ran `/start`.
- "Skills aren't working" — run `mb skill link --repo .` from your business repo to repair bridge symlinks, then restart Claude. If still broken, run `/setup`.
- "Output sounds generic" — add more detail to your reference files, especially `core/voice.md`.
- "I edited Main Branch but can't push" — that's expected for most users. Main Branch is the shared engine. Your business data goes in YOUR repo.

---

## Technical details

Contributors should start with [AGENTS.md](AGENTS.md) and
[CONTRIBUTING.md](CONTRIBUTING.md). Claude Code-specific repo guidance lives in
[CLAUDE.md](CLAUDE.md). You don't need any of these to get started as a user.

All shipping decisions are dated, versioned, and committed alongside the code that implements them.

---

## Community

[skool.com/main](https://skool.com/main)
