# Beginner Setup Guide

Setup guide for people new to Claude Code, Git, or terminal. Plan on under 30 minutes.

---

## Read This First

If this feels over your head, that's okay. Most of this is one-time setup. After that, you're mostly chatting with Claude in your business repo and getting outputs back.

You need a terminal because Main Branch creates real files on your machine. That's the magic — your business context lives in files Claude reads every session, instead of resetting to zero. Don't let the unfamiliarity stop you. One step at a time.

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

> **Windows is experimental.** It may work but isn't tested in CI; expect rough edges. See [compatibility](compatibility.md) and track [issue #137](https://github.com/noontide-co/mainbranch/issues/137) for status. Power users are welcome to try the steps below.

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
`research/`, `decisions/`, `bets/`, `log/`, `campaigns/`, `documents/`), and wires the
bridge files Claude Code needs to find Main Branch's skills.

---

## Step 3: First Session

```bash
claude
```

Then in Claude Code:

```
/mb-start
```

`/mb-start` walks you through the rest — gathers your business context (offer, audience, voice), drafts the reference files, routes you to the right skill for what you want to do.

That's it. From this point on:

```bash
cd ~/Documents/GitHub/my-business
claude
/mb-start
```

Three lines. That's the daily flow.

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
printf '%s' "$CLOUDFLARE_API_TOKEN" | mb connect cloudflare --token-stdin --metadata account_id=...
mb connect status --all --json
mb connect doctor --json
```

Secrets stay outside your repo. Main Branch stores only safe metadata in
`.mb/connect.yaml`, such as provider name, account label, and last check time.
For the longer plain-English explanation, run:

```bash
mb educational provider-readiness
```

---

## Updating Main Branch

When new versions drop:

```bash
mb update --repo .
```

Or run `/mb-update` inside Claude Code — it figures out which install you have
and runs the right thing. `/mb-start` also checks for important updates at the
beginning of a session and will tell you when an update matters. The CHANGELOG
entry for the new version surfaces as a banner the next time you run
`/mb-start`.

If you installed an early `0.1.x` version, upgrade once with
`pipx upgrade mainbranch` before trying `mb update`. If you already had a
business repo from the old setup, run this from that repo afterward:

```bash
mb skill link --repo .
mb skill repair --repo .
mb doctor
```

For old `reference/core/` repos, read [MIGRATING.md](MIGRATING.md). You usually
do not need to move files immediately.

### Already Using The Old Setup?

You can let Claude walk you through the migration. Start Claude Code anywhere
and paste:

```text
I want to migrate my existing Main Branch setup to the current pipx + /mb-start
workflow. Please run read-only checks first, find my likely business repos,
show me the exact commands you recommend, and ask before running anything that
writes files. Use docs/MIGRATING.md as the source of truth.
```

Claude may ask you to restart in a business repo after it repairs skill
discovery. That is normal — Claude Code loads slash commands when a session
starts, so repaired `/mb-start` links usually appear after restart.

---

## Available Skills

| Skill | What it does |
|---|---|
| `/mb-start` | Main entry point — figures out what you need and routes you. |
| `/mb-think` | Research, decide, codify — turns thinking into reference files. |
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
| `mb status` | Show a daily repo/runtime/GitHub briefing. |
| `mb start` | Check runtime handoff readiness and print or launch Claude Code. |
| `mb connect plan` | Show numbered provider setup choices with readiness and exact next commands. |
| `mb update` | Update Main Branch based on pipx vs clone install mode. |
| `mb doctor` | Check that everything is set up correctly. Walks you through fixes. |
| `mb skill link --repo .` | Repair Claude Code skill discovery if `/mb-start` doesn't show up. |
| `mb skill repair --repo .` | Check for old personal Claude Code skills that can shadow Main Branch. |
| `mb validate` | Check your reference files have correct frontmatter. |
| `mb graph` | Visualize or export the graph of files, links, wikilinks, and business entity tags. |
| `mb skill list` | Show which skills your installed Main Branch ships. |

For the full list: `mb --help`.

---

## Common Issues

**`/mb-start` not recognized in Claude Code:**

```bash
mb skill link --repo .
mb skill repair --repo .
```

Then restart Claude. This re-wires skill discovery in your business repo and
checks whether an old personal skill is taking precedence.

**`mb` not found after install:** run `pipx ensurepath`, close your terminal completely, reopen it.

**Output sounds generic:** add more detail to your reference files, especially `core/voice.md`. The richer those files, the more specific your outputs.

**You hit a 404:** the repo is public; no access request needed. Double-check the URL spelling.

---

## Help

- **In Claude Code:** type `/mb-help` or describe the issue in plain English.
- **In Skool:** post in the Main Branch group with a screenshot of the exact error. Tag Devon for setup issues.
- **For contributors:** open an issue at [https://github.com/noontide-co/mainbranch/issues](https://github.com/noontide-co/mainbranch/issues).
- **Platform support:** see [compatibility](compatibility.md).

---

## You've Got This

After the install, you're mostly just talking to Claude in your business repo and watching it produce outputs that sound like you. The terminal becomes background.

You don't need to memorize anything. The daily flow is three lines:

```bash
cd ~/Documents/GitHub/my-business
claude
/mb-start
```

Keep going.
