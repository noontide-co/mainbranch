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

## Required Accounts

- **GitHub** — where the code lives. Free signup at [github.com/signup](https://github.com/signup).
- **Anthropic Pro or Max** — your Claude subscription. Required for Claude Code. Sign up at [claude.ai](https://claude.ai). Pro is $20/month.

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
```

### Linux

Same flow as macOS — use `apt install pipx` (Debian/Ubuntu) or `dnf install pipx` (Fedora) instead of `brew install pipx`. Then `pipx ensurepath && pipx install mainbranch`.

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
```

After install, verify:

```bash
mb --version    # should print something like "mb X.Y.Z"
claude doctor   # should report Claude Code is healthy
```

---

## Step 2: Create Your Business Repo

Pick a name and a folder. Then:

```bash
cd ~/Documents/GitHub          # or wherever you keep code
mb onboard --name "My Business" --path my-business
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

If you already had a business repo from the old setup, ask Claude to repair that
repo afterward. The underlying repair commands are:

```bash
mb skill link --repo .
mb skill repair --repo .
mb doctor
```

For old `reference/core/` repos, read [migrating.md](migrating.md). You usually
do not need to move files immediately. When you are ready, run the dry-run first:

```bash
mb migrate --check
```

Only run `mb migrate --apply` after the dry-run shows the old paths, move
targets, backup location, and no conflicts.

### Already Using The Old Setup?

You can let Claude walk you through the migration. Start Claude Code anywhere
and paste:

```text
I want to migrate my existing Main Branch setup to the current pipx + /mb-start
workflow. Please run read-only checks first, find my likely business repos,
show me the exact commands you recommend, and ask before running anything that
writes files. If an old `reference/` layout is present, run `mb migrate --check`
first and do not run `mb migrate --apply` until I approve the dry-run. Use
docs/migrating.md as the source of truth.
```

Claude may ask you to restart in a business repo after it repairs skill
discovery. That is normal — Claude Code loads slash commands when a session
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
| `/mb-vsl` | Write video sales letter scripts. |
| `/mb-organic` | Generate organic content (Reels, TikTok, carousels). |
| `/mb-site` | Generate and deploy landing pages. |
| `/mb-wiki` | Personal wiki with atomic notes. |
| `/mb-end` | Close session intentionally — summary, crystallize, commit. |
| `/mb-help` | Get answers, troubleshoot. |
| `/mb-update` | Update Main Branch (figures out pipx vs clone). |
| `/mb-pull` | Old name for `/mb-update`; still works for existing users. |

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
