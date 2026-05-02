# Compatibility

Main Branch is intentionally narrow today: `mb` plus bundled Claude Code skills as the first adapter for portable agent workflows.
This page is the public compatibility contract for that surface.

## Supported matrix

| Surface | Current status | Notes |
|---|---|---|
| macOS | Supported | Primary development path. Recommended for beginners. |
| Linux | Supported for `mb`; supported when Claude Code is installed | CI runs the Python package on Linux. Claude Code must be installed separately. |
| Windows | Experimental | Not tested in CI. Track [#137](https://github.com/noontide-co/mainbranch/issues/137). |
| Python | 3.10, 3.11, 3.12 | CI gates all three versions. |
| Install mode | `pipx install mainbranch` | Canonical public install path. |
| Developer mode | Git clone | For contributors who want to edit the engine or skills. |
| Agent runtime | Claude Code | First-class today. |
| Codex, Cursor, OpenClaw, Hermes, local LLMs | Roadmap | `mb` is runtime-agnostic by design, but these adapters are not supported yet. |

**Windows tip — try WSL2.** If you're on Windows and want a working setup today, use [Windows Subsystem for Linux 2 (WSL2)](https://learn.microsoft.com/en-us/windows/wsl/install). Inside WSL2, follow the supported Linux flow. The pipx install path works there.

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

Use the CLI update contract from inside your business repo:

```bash
mb update
```

`mb update` detects whether the engine is a `pipx` install or clone checkout,
runs the appropriate update path, and refreshes skill links. Use
`mb update --check` for a dry-run and `mb update --json` for automation.
Inside Claude Code, `/pull` calls `mb update` for this mechanical step and keeps
ownership of the human-readable "what's new" summary.

## Known Limits

- Claude Code is the only first-class agent runtime today.
- Windows is experimental.
- Skills are bundled into the installed Python package, so public users update
  skills by upgrading `mainbranch`.
- The CLI scaffolds, validates, graphs, resolves, and links the current Claude
  Code skill adapter. Most business workflows still happen through Claude Code
  slash commands.
