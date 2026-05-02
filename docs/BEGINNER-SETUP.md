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
files, git, and GitHub, scaffolds the six-folder taxonomy (`core/`,
`research/`, `decisions/`, `log/`, `campaigns/`, `documents/`), and wires the
bridge files Claude Code needs to find Main Branch's skills.

---

## Step 3: First Session

```bash
claude
```

Then in Claude Code:

```
/start
```

`/start` walks you through the rest — gathers your business context (offer, audience, voice), drafts the reference files, routes you to the right skill for what you want to do.

That's it. From this point on:

```bash
cd ~/Documents/GitHub/my-business
claude
/start
```

Three lines. That's the daily flow.

---

## Updating Main Branch

When new versions drop:

```bash
pipx upgrade mainbranch
```

Or just run `/pull` inside Claude Code — it figures out which install you have and runs the right thing. The CHANGELOG entry for the new version surfaces as a banner the next time you run `/start`.

If you installed an early `0.1.x` version, upgrade once with
`pipx upgrade mainbranch` before trying `mb update`. If you already had a
business repo from the old setup, run this from that repo afterward:

```bash
mb skill link --repo .
mb doctor
```

For old `reference/core/` repos, read [MIGRATING.md](MIGRATING.md). You usually
do not need to move files immediately.

---

## Available Skills

| Skill | What it does |
|---|---|
| `/start` | Main entry point — figures out what you need and routes you. |
| `/think` | Research, decide, codify — turns thinking into reference files. |
| `/ads` | Generate ad copy and review for compliance. |
| `/vsl` | Write video sales letter scripts. |
| `/organic` | Generate organic content (Reels, TikTok, carousels). |
| `/site` | Generate and deploy landing pages. |
| `/wiki` | Personal wiki with atomic notes. |
| `/end` | Close session intentionally — summary, crystallize, commit. |
| `/help` | Get answers, troubleshoot. |
| `/pull` | Update Main Branch (figures out pipx vs clone). |

---

## The mb CLI

| Command | What it does |
|---|---|
| `mb onboard` | Guided setup for humans. Creates or connects a business repo and shows the next `/start` step. |
| `mb init` | Scaffold a fresh business repo. |
| `mb status` | Show a daily repo/runtime/GitHub briefing. |
| `mb start` | Check runtime handoff readiness and print or launch Claude Code. |
| `mb update` | Update Main Branch based on pipx vs clone install mode. |
| `mb doctor` | Check that everything is set up correctly. Walks you through fixes. |
| `mb skill link --repo .` | Repair Claude Code skill discovery if `/start` doesn't show up. |
| `mb validate` | Check your reference files have correct frontmatter. |
| `mb graph` | Visualize the link graph between research and decisions. |
| `mb skill list` | Show which skills your installed Main Branch ships. |

For the full list: `mb --help`.

---

## Common Issues

**`/start` not recognized in Claude Code:**

```bash
mb skill link --repo .
```

Then restart Claude. This re-wires skill discovery in your business repo.

**`mb` not found after install:** run `pipx ensurepath`, close your terminal completely, reopen it.

**Output sounds generic:** add more detail to your reference files, especially `core/voice.md`. The richer those files, the more specific your outputs.

**You hit a 404:** the repo is public; no access request needed. Double-check the URL spelling.

---

## Help

- **In Claude Code:** type `/help` or describe the issue in plain English.
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
/start
```

Keep going.
