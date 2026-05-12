# Main Branch

[![Star on GitHub](https://img.shields.io/github/stars/noontide-co/mainbranch?style=social&label=Star)](https://github.com/noontide-co/mainbranch)
[![PyPI version](https://img.shields.io/pypi/v/mainbranch?style=flat&label=PyPI)](https://pypi.org/project/mainbranch/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<p align="center">
  <a href="#quickstart"><strong>Quickstart</strong></a> &middot;
  <a href="docs/ethos.md"><strong>Ethos</strong></a> &middot;
  <a href="docs/roadmap.md"><strong>Roadmap</strong></a> &middot;
  <a href="docs/beginner-setup.md"><strong>Beginner setup</strong></a> &middot;
  <a href="https://skool.com/main"><strong>Community</strong></a>
</p>

---

## What is Main Branch?

# Durable operating memory for AI-assisted businesses

**You don't need to know git. You don't need to know terminals. You just need a folder.**

Main Branch is a folder on your computer that holds your business — offer, audience, voice, decisions, research, bets, launches, meeting notes, fulfillment context, lessons. The agent reads that folder before it answers, so the work it gives you sounds like your business instead of generic AI output. The system saves itself between sessions, so you stop re-explaining who you are every time you open Claude.

Open source. Lives on your machine. Bring your own Claude Code plan. That's it.

|        | Step             | What happens                                                                 |
| ------ | ---------------- | ---------------------------------------------------------------------------- |
| **01** | Open the folder  | One business, one folder. Your offer, voice, audience, and history live here.|
| **02** | Talk to the agent| It reads the folder before it speaks. No re-pasting. No re-explaining.       |
| **03** | The work ships   | Drafts, ad copy, landing pages, decisions. You approve. It saves itself.     |

---

<div align="center">
  <em>Works with</em> <strong>Claude Code today</strong>. Codex CLI has an experimental CLI-first adapter for power users; Cursor, OpenClaw, Hermes, and local runtimes remain compatibility targets — see <a href="docs/compatibility.md">compatibility</a>.
</div>

---

## Main Branch is right for you if

- You're a solo founder, small agency owner, course creator, productized-services operator, indie SaaS founder, or small ecom team
- Your offer lives in Notion, your voice lives in Loom transcripts, your research lives in three Google Docs you can't find
- Every chat session with your AI starts from zero and the output sounds generic
- You're paying for SaaS dashboards that get more expensive without getting smarter
- You want the work to live somewhere you own — not on someone else's server
- You want a system that gets better the longer you use it, instead of starting fresh every Monday

---

## What stops you isn't what you think

| What stops you                                          | What's actually true                                                              |
| ------------------------------------------------------- | --------------------------------------------------------------------------------- |
| "I'm not technical enough. I don't know git, terminals, or any of that." | If you can move a file into a folder, the system handles the rest.       |
| "I'll set it up wrong and not know."                    | The system tells you the next command. It can't get lost.                         |
| "I'd mess it up and lose everything."                   | Every change is saved and rewindable. Git remembers. Mistakes don't stick.        |
| "I need a clear plan before I start."                   | Start with the folder. The system explains itself in plain English as you go.     |
| "I need someone to sit down and walk me through it."    | Type `/mb-start` in Claude. The agent explains. You go at your own pace.          |
| "I won't keep up with the maintenance."                 | When something falls out of date, the system tells you the exact next step.       |

---

## What changes vs. just AI

| Just AI                                                 | Main Branch + Claude                                                              |
| ------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Every chat starts from zero. You re-paste your context. | The agent reads your folder before it answers.                                    |
| Output sounds like every other AI.                      | Output sounds like you — because the agent reads your voice files first.          |
| Important decisions live in chat that disappears.       | Decisions live as plain notes you can read on a Tuesday.                          |
| You build the system yourself: prompts, files, glue.    | The rails are built. Your business folder plugs in.                               |
| Another rented subscription. Gets more expensive.       | Claude Code + a folder you own forever. Your stuff still works without us.        |

---

## What you can do today

- Research a topic and turn it into a decision the system remembers
- Open, run, close, and narrate business bets so the lessons stick around
- Plan and run launches, drops, challenges, and promos as repeatable playbooks
- Generate ad copy, video scripts, sales videos/VSLs, organic content (Reels, TikTok, carousels), and page copy in your voice
- Draft and ship landing pages on Cloudflare from your core files and research
- Capture meeting transcripts, source material, and fulfillment notes into durable docs
- Save readable progress points during long agent runs so the next session starts where this one stopped
- Clean up stale folders, broken links, and old settings before they break a session
- Turn errors and confusing steps into clean public GitHub issues without leaking your business data
- Close sessions intentionally with a crystallize moment that updates your durable memory

You don't run any of these commands yourself. You ask the agent. It runs them.

---

## What's underneath

Main Branch v0.3 has three layers:

- **Your folder is the source of truth.** Offer, audience, voice, decisions, research, bets, launches, logs, documents, links to other repos. Plain markdown files you can read on any computer.
- **The CLI is the safety net.** Scaffolds the folder, validates the shape, draws the relationship graph, briefs you on what's changed, walks through repairs, saves readable checkpoints, and checks that connected providers (GitHub, Cloudflare, ads accounts) are wired up safely. The agent runs it. You don't have to learn it.
- **The skills are the judgment layer.** The agent reads your folder, asks you the right questions, drafts work, reviews it, and routes the artifacts back into files.

Agent recommends. You decide what gets shipped, spent, published, or saved.

The longer-arc operating-system model — where multiple business repos, GitHub teams, structured data, and runtime adapters compose into a full team operating system — is direction, not the v0.3 shape. See [`decisions/2026-05-02-github-native-business-os.md`](decisions/2026-05-02-github-native-business-os.md).

---

## What Main Branch is not

|                                  |                                                                                                |
| -------------------------------- | ---------------------------------------------------------------------------------------------- |
| **Not a chat app.**              | The supported chat surface is Claude Code; Codex CLI is experimental. Main Branch gives agents durable context to read from. |
| **Not a SaaS dashboard.**        | Your business doesn't live on our servers. It lives in your folder.                            |
| **Not a connect-every-tool hub.**| We pick boring, inspectable rails: GitHub, Cloudflare, official ads paths. Curated, not sprawl.|
| **Not a model host.**            | We don't run models. We hand the agent the right context so the model you already use is sharper.|
| **Not magic.**                   | The work is still real. The foundation is just the right one to build on.                      |

---

## Direction, not promises

The current package is the daily operating loop: open the folder, ground the agent, get a ranked next action, ship the work, save a readable checkpoint. Next direction tightens the same loop, expands curated provider rails, and prepares an optional local dashboard that reads from your folder instead of replacing it.

Mobile thought capture, team views, finance/fulfillment roll-ups, broader Ops/bookkeeping, an optional dashboard, and any future hosted/model-invocation surface are eventual targets in [docs/roadmap.md](docs/roadmap.md), not current behavior.

---

## Quickstart

```bash
pipx install mainbranch
mb onboard --name "My Business" --path my-business
cd my-business
claude
/mb-start
```

That's it. `mb onboard` creates the folder, wires Claude Code, and shows the next step. `/mb-start` reads the folder and tells you what to do.

After the first session, the daily flow is:

```bash
cd /path/to/my-business
claude
/mb-start
```

You'll need a Claude plan that includes Claude Code. Install Claude Code from [claude.ai](https://claude.ai). Step-by-step beginner walkthrough: [docs/beginner-setup.md](docs/beginner-setup.md).

### Trying Codex CLI

Codex CLI support is experimental and CLI-first. Fresh business folders include
an `AGENTS.md` file that tells Codex how to start from Main Branch facts. Expect
Codex to run `mb status --json --peek`, `mb start --json`, and
`mb doctor repair --plan`, then translate those facts into a useful owner
briefing. Do not expect Claude Code slash commands such as `/mb-start` to work
inside Codex yet.

After installing Codex CLI, test a new repo with:

```bash
mb onboard --yes --name "Codex Smoke Business" --path codex-smoke-business
cd codex-smoke-business
codex
```

Ask Codex to start the business day from read-only `mb` facts and to ask before
writing files.

For a read-only smoke test:

```bash
codex exec --json --ephemeral --sandbox read-only -c 'approval_policy="never"' -C . \
  'Start this Main Branch business day. Run only read-only mb checks and do not edit files.'
git status --short
```

The smoke passes when Codex uses the `mb` fact commands and `git status --short`
stays clean. See [docs/compatibility.md](docs/compatibility.md) for the current
support boundary.

Tested on macOS and Linux. Windows is experimental — use WSL2.

---

## FAQ

**Do I need to know how to code?** No. You invoke skills with slash prompts and answer questions.

**What if I have multiple products under one brand?** Use one folder with `core/offers/` when products share brand, team, voice, and access. Move an offer into its own folder if it grows its own team, accounts, site, finance boundary, or operating history.

**What's a bet vs. an offer?** A bet is a time-boxed hypothesis: what you'll try, why, by when, how you'll know. An offer is a durable thing you sell. A good bet can graduate into an offer.

**What if I have multiple separate businesses?** One folder per brand, legal entity, ad-account boundary, or team-access boundary.

**How do I update?** Type `/mb-update` in Claude. Power users can run `mb update` from the folder.

**Can Claude migrate an old setup for me?** Yes. Start Claude Code anywhere and paste the prompt in [docs/migrating.md](docs/migrating.md#recommended-let-claude-walk-you-through-it).

**Can I edit the skills?** You can. You don't need to.

**What makes this different from ChatGPT?** ChatGPT resets between sessions. Main Branch is a folder Claude can re-read every session — your offer, audience, voice, decisions, research, and bets — so the output stays consistent with your business.

**I'm stuck.** Type `/mb-start` again.

---

## Help

**In the Skool community:** post in the Main Branch group. Tag @Devon for technical questions.

**Not in the Skool community?** Open an issue at [github.com/noontide-co/mainbranch/issues](https://github.com/noontide-co/mainbranch/issues).

For platform support and security reporting, see [SUPPORT.md](SUPPORT.md), [SECURITY.md](SECURITY.md), and [docs/compatibility.md](docs/compatibility.md).

**Common issues:**

- "404" or "Repository not found" — verify the URL. The repo is public; no access request needed.
- "Claude doesn't see my files" — make sure you started Claude in your business folder and ran `/mb-start`.
- "Skills aren't working" — ask Claude to repair the wiring, or run `/mb-setup`.
- "Output sounds generic" — add more detail to your core files, especially `core/voice.md`.
- "I edited Main Branch but can't push" — that's expected. Main Branch is the shared engine. Your business data goes in YOUR folder.

Hit a real problem? Ask the agent to draft a clean public issue for you. It scrubs private context before submitting.

---

## Open source vs paid community

- **Open-source (MIT)**: the `mb` CLI, bundled skills, schema, framework, docs, and any future local dashboard. Usable without joining the paid community.
- **Community ([Skool](https://skool.com/main))**: Watch us build companies live with Main Branch. Live narration, calls, support, and curated examples — not required for the engine.

Main Branch is usable on its own. The community is the live narration on top.

---

## For contributors and power users

The `mb` CLI is the deterministic control plane. The agent runs it for normal users. If you want to inspect, script, or build on it, here's the surface.

| Command                  | What it does |
|---|---|
| `mb onboard`             | Human setup flow: create or connect a business folder, wire Claude Code skills, show next steps. |
| `mb init`                | Quiet scriptable primitive underneath `mb onboard`. |
| `mb status`              | Local-first daily briefing: ranked next actions, since-last-check changes, drift, repo health, runtime wiring, recent activity, GitHub tasks/proposals. `--json` and `--peek` for callers. |
| `mb doctor`              | Check environment, repo shape, frontmatter, settings. `mb doctor repair --plan` / `--apply` walks through guided reconciliation, including migration drift. |
| `mb connect`             | Register provider credentials, test provider health, inspect repair-safe integration status without committing secrets. |
| `mb site check`          | Local paid-traffic measurement readiness for a site folder: GTM install, dataLayer events, consent posture, Google Ads metadata, operator-review gates. |
| `mb issue draft` / `open`| Draft a privacy-scrubbed GitHub issue locally, review it, then submit through `gh`. |
| `mb validate`            | Frontmatter shape check across `core/`, `research/`, `decisions/`, `bets/`, `log/`, `pushes/`, `documents/`. Pass/fail per file. |
| `mb graph`               | Build a folder graph from frontmatter links, wikilinks, and entity tags. Graphviz DOT, JSON, and PNG outputs. |
| `mb suggest links`       | Suggest likely frontmatter, inline, tag, data, and context connections for a file without editing it. |
| `mb checkpoint`          | Plan or save a business-readable git checkpoint during long agent runs. |
| `mb skill list` / `path` / `validate` / `link` / `repair` | Manage and repair the bundled Claude Code skills. |
| `mb update`              | Update Main Branch in place. |

Full list: `mb --help`. JSON output contract: [docs/json-output-contract.md](docs/json-output-contract.md). Provider readiness: [docs/dependency-choices.md](docs/dependency-choices.md).

**Skills:**

| Skill | Loop |
|---|---|
| `/mb-start` | Daily entry point — figure out what you need and route there |
| `/mb-status` | Daily briefing facts and ranked next actions |
| `/mb-setup` | First-time setup |
| `/mb-think` | Research, decide, codify |
| `/mb-bet` | Open, update, close, narrate business bets |
| `/mb-end` | Close the session — summary, crystallize, checkpoint guidance |
| `/mb-help` | Get answers, troubleshoot, learn the system |
| `/mb-update` | Update Main Branch (delegates to `mb update`) |
| `/mb-ads` `/mb-organic` `/mb-site` | Channel skills (Paid / Organic / Pages). Sales videos/VSLs route through the relevant workflow. |
| `/mb-wiki` | Specialty: personal/atomic-notes wiki, not part of the core daily loop |

`/mb-pull` is preserved as a legacy alias for `/mb-update`.

**Reading order:**

- [AGENTS.md](AGENTS.md) — shared operating contract for Codex, Claude Code, and other agents
- [CLAUDE.md](CLAUDE.md) — Claude Code-specific guidance
- [CONTRIBUTING.md](CONTRIBUTING.md) — branch / commit / validation discipline
- [docs/ethos.md](docs/ethos.md) — product principles
- [docs/operator-loops.md](docs/operator-loops.md) — Sense → Decide → Ship → Reflect taxonomy
- [docs/business-connections.md](docs/business-connections.md) — how to connect notes, reports, data, and GitHub history without noisy links
- [docs/roadmap.md](docs/roadmap.md) — release direction
- [docs/compatibility.md](docs/compatibility.md) — runtime support matrix
- [docs/release-simulations.md](docs/release-simulations.md) — release evidence ladder

---

## Community

- [Skool community](https://skool.com/main) — watch us build with Main Branch
- [GitHub Issues](https://github.com/noontide-co/mainbranch/issues) — bugs and feature requests
- [GitHub Discussions](https://github.com/noontide-co/mainbranch/discussions) — ideas

---

## License

[MIT](LICENSE) © 2026 Noontide

<p align="center">
  <sub>Open source. Built for people who want to own their business memory, not rent it.</sub>
</p>
