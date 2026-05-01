# Compatibility

Main Branch v0.1.x is intentionally narrow: `mb` plus bundled Claude Code skills.
This page is the public compatibility contract for that surface.

## Supported matrix

| Surface | v0.1.x status | Notes |
|---|---|---|
| macOS | Supported | Primary development path. Recommended for beginners. |
| Linux | Supported for `mb`; supported when Claude Code is installed | CI runs the Python package on Linux. Claude Code must be installed separately. |
| Windows | Experimental | Not tested in CI for v0.1.x. Track [#151](https://github.com/noontide-co/mainbranch/issues/151). |
| Python | 3.10, 3.11, 3.12 | CI gates all three versions. |
| Install mode | `pipx install mainbranch` | Canonical public install path. |
| Developer mode | Git clone | For contributors who want to edit the engine or skills. |
| Agent runtime | Claude Code | First-class in v0.1.x. |
| Codex, Cursor, Hermes, local LLMs | Roadmap | Cross-agent support is v0.2+. |

**Windows tip — try WSL2.** If you're on Windows and want a working setup today, use [Windows Subsystem for Linux 2 (WSL2)](https://learn.microsoft.com/en-us/windows/wsl/install). Inside WSL2, follow the supported Linux flow. The pipx install path works there.

## What "supported" means

Supported means:

- CI runs the relevant Python gates before merge.
- The documented setup path is expected to work.
- Bugs should be filed as GitHub issues.
- Regressions in the supported path are release-quality problems.

Experimental means:

- The path may work for power users.
- It is not part of the v0.1.x release gate.
- Workarounds are welcome, but breakage is not treated as a launch blocker.

## Recommended setup

For most users:

```bash
pipx install mainbranch
mb init my-business --name "My Business"
cd my-business
claude
/start
```

For contributors:

```bash
git clone https://github.com/noontide-co/mainbranch.git
cd mainbranch
```

Use clone mode only if you are editing the engine, docs, or bundled skills.

## Updating

For `pipx` installs:

```bash
pipx upgrade mainbranch
```

For clone installs:

```bash
git pull origin main
```

Inside Claude Code, `/pull` detects the install mode and runs the appropriate
update path.

## Known v0.1.x limits

- Claude Code is the only first-class agent runtime.
- Windows is experimental.
- Skills are bundled into the installed Python package, so public users update
  skills by upgrading `mainbranch`.
- The CLI scaffolds, validates, graphs, resolves, and links skills. Most
  business workflows still happen through Claude Code slash commands.
