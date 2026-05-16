# Beginner Setup Guide

Setup guide for people new to Claude Code, Git, or terminal. Plan on under 30 minutes.

---

## Read This First

If this feels over your head, that's okay. Most of this is one-time setup. After that, you're mostly chatting with Claude in your business repo and getting outputs back.

You need a terminal because Main Branch creates real files on your machine. That's the magic — your business context lives in files Claude reads every session, instead of resetting to zero. Don't let the unfamiliarity stop you. One step at a time.

If you want the "why" while you set up, Main Branch has short educational
topics you can print from the terminal:

```bash
mb educational daily-owner-loop
mb educational why-mainbranch-not-saas
mb educational github-vs-gdocs
mb educational cli-vs-dashboard
mb educational markdown-vs-notion
mb educational git-history-vs-cloud-sync
```

Start with `daily-owner-loop`. The other topics explain the tool philosophy
behind that loop: local files, markdown, git history, GitHub work threads, `mb`
readiness checks, and Claude Code skills.

---

## What You Need

- **A folder on your computer** — this becomes the business brain.
- **Main Branch (`mb`)** — creates and checks that folder.
- **Claude Code** — the first supported chat runtime for Main Branch skills.
- **A Claude plan that includes Claude Code** — pricing and limits can change;
  use Anthropic's current Claude Code plan details as the source of truth.
- **GitHub CLI (`gh`)** — strongly recommended for almost everyone, and
  required when you want GitHub backup, sync, collaboration, or
  `mb onboard --github --push`.

GitHub does not need to cost anything, and it is the highest-leverage
connection after your local folder. It gives you cloud backup, readable saved
history, shared tasks and proposals, and a repo that other AI tools with GitHub
connectors can read as your business brain. Main Branch can start locally
before GitHub is ready, but most users should connect it during first setup.

Before using GitHub-backed setup, install GitHub CLI and confirm it is signed in
to the account you expect:

```bash
gh auth status
gh api user --jq .login
```

If that account is wrong, stop before creating the GitHub-backed setup and run
`gh auth login` or `gh auth switch`.

## Folder-First Bootstrap

If you are starting from an empty folder with Claude Code, Codex CLI, or another
agent-like runtime, open that runtime in the folder where the business brain
should live and paste this prompt:

```text
I want to set up Main Branch for this business in the current folder.

Treat this as setup intent, not as a document to save.

First, check whether `mb` is available. If it is not installed, stop and tell me
the exact install step. If it is installed, inspect the available setup/onboard
command before running it.

Use this folder as the business repo location unless I say otherwise. Before any
write, explain the folder or repo that will be created or modified and ask for
approval.

If I ask for GitHub backup or sync, first check whether GitHub CLI is installed,
authenticated, and signed in to the account I expect. GitHub is strongly
recommended because it gives Main Branch a free cloud backup, shared history,
task/proposal layer, and connector-friendly copy of the business brain. Main
Branch can start locally without GitHub, but GitHub is needed for sync,
collaboration, and `mb onboard --github --push`.

After setup, run the read-only health/status checks, summarize what was created
in business language, and tell me the next safest action.
```

Do not save that prompt as a markdown document. It is the instruction that tells
the agent to start setup.

---

## Step 1: Install the Tools

### Mac

```bash
# 1. Install Claude Code
curl -fsSL https://claude.ai/install.sh | bash

# 2. Install pipx (Python package installer for CLIs)
brew install pipx
pipx ensurepath

# 3. Install Main Branch
pipx install mainbranch

# 4. Strongly recommended, for GitHub backup/sync/collaboration
brew install gh
gh auth login
```

### Linux

Same flow as macOS — use `apt install pipx` (Debian/Ubuntu) or `dnf install
pipx` (Fedora) instead of `brew install pipx`. Then `pipx ensurepath && pipx
install mainbranch`. For GitHub backup/sync/collaboration, install GitHub CLI
from [cli.github.com](https://cli.github.com/) and run
`gh auth login`.

### Windows

> **Windows is experimental.** It may work but isn't tested in CI; expect rough edges. See [compatibility](compatibility.md). Power users should use WSL2 for the closest supported path.

```powershell
# 1. Install Claude Code
irm https://claude.ai/install.ps1 | iex

# 2. Install Git for Windows
# Download from: https://git-scm.com/download/win

# 3. Install pipx
python -m pip install --user pipx
python -m pipx ensurepath

# 4. Install Main Branch
pipx install mainbranch

# 5. Strongly recommended, for GitHub backup/sync/collaboration
# Download GitHub CLI from: https://cli.github.com/
gh auth login
```

After install, verify:

```bash
mb --version    # should print something like "mb X.Y.Z"
claude doctor   # should report Claude Code is healthy
```

---

## Step 2: Create Your Business Repo

Pick a name and a folder. Local-only setup:

```bash
cd ~/Documents/GitHub          # or wherever you keep code
mb onboard --name "My Business" --path my-business
cd my-business
```

GitHub-backed setup, after `gh auth status` shows the expected account:

```bash
mb onboard --name "My Business" --path my-business --github your-gh-username/my-business --github-visibility private --push
cd my-business
```

`mb onboard` walks you through the setup, explains why Main Branch uses local
files, git, and GitHub, scaffolds the business folder taxonomy (`core/`,
`research/`, `decisions/`, `bets/`, `log/`, `pushes/`, `documents/` plus an
optional `core/vocabulary.md` for operator-owned display words), and wires the
bridge files Claude Code needs to find Main Branch's skills.

You may also see a `.mb/` folder. That is normal. It stores Main Branch's local
operational state for that business repo, such as onboarding progress, safe
provider metadata, backups, and issue drafts. You do not need a `.mb-vip/`
folder; that name comes from the old clone-based setup.

### What Gets Saved

- Saving a file writes it on your computer.
- A checkpoint is an approved saved point in the business history.
- GitHub backup/sync means the approved history is also available from GitHub,
  where AI tools with GitHub connectors can read the business brain.
- Main Branch updates change the engine and skills; they do not rewrite your
  business files without an approved repair, migration, or edit.

Use one business repo when brand, team, voice, access, and operating history are
shared. Create a separate business repo for a separate entity or independent
operating history. Use linked child repos for sites, products, finance/legal,
client work, or private ops when access or lifecycle differs. The full model
lives in [system architecture](system-architecture.md#repo-topology).

---

## Step 3: First Session

```bash
claude
```

Then in Claude Code:

```
/mb-start
```

`/mb-start` walks you through the rest. It reads the same status facts as `mb status`, checks for updates or repair needs, and routes you to setup, thinking, shipping, or closing work.

Plain `/mb-start` is the reliable beginner path. Extra text after `/mb-start`
is treated as normal instruction, not as a project-command argument API.
Natural-language requests can route into the skill, but setup docs teach the
explicit slash command because it is easier to recognize and repair. See the
[Claude Code invocation contract](claude-code-invocation-contract.md) for the
runtime details.

That's it. From this point on:

```bash
cd ~/Documents/GitHub/my-business
claude
/mb-start
```

Three lines. That's the daily flow.

`/mb-start` runs the same status facts internally, so you do not need to run
`mb status` before opening Claude Code. Use `mb status` only when you want a
terminal-only briefing.

---

## Provider Readiness

Providers are outside accounts Main Branch can use when a business workflow
needs them. You do not need to connect everything during first setup.

Use the plan command from your business repo:

```bash
mb connect plan
```

It shows numbered choices:

1. **GitHub** — tasks, proposals, reviews, and shipped history.
2. **Cloudflare** — sites, DNS, Pages, and future Workers.
3. **Google / Workspace** — existing Docs, Drive, Sheets, and Slides.
4. **Meta Ads** — ad accounts, campaigns, and pixels.
5. **Apify** — research sidecar for scraping, YouTube, Instagram, and web mining.

If a provider is missing, Main Branch prints the next command. Examples:

```bash
gh auth login
printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata token_type=account --metadata account_id=...
mb connect doctor --json
```

Secrets stay outside your repo. Main Branch stores only safe metadata in
`.mb/connect.yaml`, such as provider name, account label, account-token type,
and last check time. The file is gitignored by default.

If you use disposable checkouts or agent workspaces, store provider setup in
user scope and hydrate each workspace:

```bash
printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --scope user --token-stdin --metadata token_type=account --metadata account_id=...
mb connect hydrate --repo .
```

User scope is keyed by the business repo identity, so another business repo can
use a different Cloudflare account or zone without sharing that connection.

For the longer plain-English explanation, run:

```bash
mb educational provider-readiness
```

Provider-specific education is available when a job needs that rail:

```bash
mb educational cloudflare-pages
mb educational cal-com
mb educational stripe
mb educational hledger
mb educational forgejo
```

For runtime/editor boundaries, use:

```bash
mb educational cursor
```

---

## Updating Main Branch

When new versions drop, use Claude Code:

```text
/mb-update
```

`/mb-update` figures out which install you have and runs the right update path.
`/mb-start` also checks for important updates at the beginning of a session and
will tell you when updating matters. The CHANGELOG entry for the new version
surfaces as a banner the next time you run `/mb-start`.

Power users can run the same product update path from a business repo:

```bash
mb update --repo .
```

If you installed an early `0.1.x` version, `/mb-update` or `mb update` may say
the install is too old to update itself. Ask Claude to help with the bootstrap.
The fallback command is:

```bash
pipx upgrade mainbranch
```

### Already Using The Old Setup?

Read [migrating.md](migrating.md) before repairing old clone-era installs,
`reference/core/` layouts, or stale skill links. You usually do not need to
move files immediately; update Main Branch first, then let Claude run the
confirmation-gated migration prompt from that doc.

Start Claude Code anywhere and paste:

```text
I want to migrate my existing Main Branch setup to the current pipx + /mb-start
workflow. Please run read-only checks first, find my likely business repos,
show me the exact commands you recommend, and ask before running anything that
writes files. If an old `reference/` layout is present, run `mb migrate --check`
first and do not run `mb migrate --apply` until I approve the dry-run. Use
docs/migrating.md as the source of truth.
```

Claude may ask you to restart in a business folder after it repairs skill
discovery. That is normal. Claude Code loads slash commands when a session
starts, so repaired `/mb-start` links usually appear after restart.

---

## Available Skills

| Skill | What it does |
|---|---|
| `/mb-start` | Main entry point — figures out what you need and routes you. |
| `/mb-status` | Claude Code briefing over `mb status --json --peek`, including ranked next actions. |
| `/mb-think` | Research, decide, codify — turns thinking into durable business files. |
| `/mb-bet` | Open, update, close, list, and narrate business bets. |
| `/mb-ads` | Generate ad copy and review for compliance. |
| `/mb-organic` | Generate organic content (Reels, TikTok, carousels). |
| `/mb-site` | Generate and deploy landing pages. |
| `/mb-wiki` | Personal wiki with atomic notes. |
| `/mb-end` | Close session intentionally — summary, crystallize, checkpoint. |
| `/mb-help` | Get answers, troubleshoot. |
| `/mb-update` | Update Main Branch (figures out pipx vs clone). |

---

## The mb CLI

| Command | What it does |
|---|---|
| `mb onboard` | Guided setup for humans. Creates or connects a business repo and shows the next `/mb-start` step. |
| `mb init` | Scaffold a fresh business repo. |
| `mb status` | Show a terminal-only repo/runtime/GitHub briefing. `/mb-start` reads these facts internally. |
| `mb start` | Check runtime handoff readiness and print or launch Claude Code with `--launch`. |
| `mb connect plan` | Show numbered provider setup choices with readiness and exact next commands. |
| `mb issue draft` | Draft a privacy-safe GitHub issue from a bug, confusing step, or feature gap. |
| `mb checkpoint` | Plan or save a business-readable git checkpoint during long work. |
| `mb similar-bets` | Find similar past bets and outcomes before starting a new one. |
| `mb update` | Update Main Branch based on pipx vs clone install mode. |
| `mb doctor` | Check that everything is set up correctly. Walks you through fixes. |
| `mb skill link --repo .` | Repair Claude Code skill discovery if `/mb-start` doesn't show up. |
| `mb skill repair --repo .` | Check for old personal Claude Code skills that can shadow Main Branch. |
| `mb validate` | Check your business files have correct frontmatter. |
| `mb graph` | Visualize or export the graph of files, links, wikilinks, and business entity tags. |
| `mb skill list` | Show which skills your installed Main Branch ships. |

For the full list: `mb --help`.

---

## Common Issues

**`/mb-start` not recognized in Claude Code:**

```bash
mb skill link --repo .
```

Then restart Claude. This re-wires skill discovery in your business repo and
clears known stale Main Branch personal-skill shadows.

The project-local `.claude/skills/mb-start` bridge link is required for
reliable slash-command discovery; `.claude/settings.local.json` alone is not
enough.

If `/mb-start` is still missing after relinking and restarting, run:

```bash
mb skill repair --repo .
```

That inspect-only command reports unresolved personal-skill conflicts so you can
decide whether to move them with `mb skill repair --repo . --apply`.

**I only see `.mb/`, not `.mb-vip/`:** good. `.mb/` is the current folder.
`.mb-vip/` was old setup language and is not required.

**`mb` not found after install:** run `pipx ensurepath`, close your terminal completely, reopen it.

**Output sounds generic:** add more detail to your core files, especially `core/voice.md`. The richer those files, the more specific your outputs.

**You hit a 404:** the repo is public; no access request needed. Double-check the URL spelling.

---

## Help

- **In Claude Code:** type `/mb-help` or describe the issue in plain English.
- **In Skool:** post in the Main Branch group with a screenshot of the exact error. Tag Devon for setup issues.
- **For contributors:** open an issue at [https://github.com/noontide-co/mainbranch/issues](https://github.com/noontide-co/mainbranch/issues).
- **Platform support:** see [compatibility](compatibility.md).

---

## You've Got This

After the install, you're mostly talking to Claude in your business repo. The
important part is that the work does not disappear into chat: status, decisions,
bets, pushes, logs, checkpoints, and outputs persist locally and in git. The
terminal becomes background.

You don't need to memorize anything. The daily flow is three lines:

```bash
cd ~/Documents/GitHub/my-business
claude
/mb-start
```

Keep going.
