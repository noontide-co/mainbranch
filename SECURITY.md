# Security Policy

Main Branch is local-first software. It installs the `mb` CLI, writes files into
business repos you choose, and wires Claude Code to bundled skills. There is no
hosted Main Branch service in the open-source engine.

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |
| Older versions | No |

Security fixes ship in the next patch release when practical.

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability.

Report privately by one of these paths:

- Use GitHub's private vulnerability reporting flow if it is available on this
  repository.
- Email `devon@noontide.co` with the subject `Main Branch security`.

We aim to acknowledge reports within 7 days and ship a fix within 30 days when practical.

Include:

- The affected version (`mb --version`)
- Operating system and install mode (`pipx` or clone)
- Reproduction steps
- Expected impact
- Any logs or screenshots that do not expose private business data

## Scope

In scope:

- Unsafe file writes outside the requested repo
- Unsafe handling of symlinks or bridge links
- Path traversal in `mb init`, `mb skill link`, `mb resolve`, or related CLI
  commands
- Accidental exposure of private business data in generated files or logs
- GitHub Actions, packaging, or release workflow issues that could affect users

Out of scope:

- Bugs in Claude Code or Anthropic accounts
- Bugs in GitHub, pipx, Python, or operating-system package managers
- Prompt-injection reports that require a user to intentionally paste hostile
  content into their own private business repo, unless Main Branch amplifies that
  content into an unsafe action
- Social engineering against maintainers or community members

## Response expectations

Per the commitment near the top of this file: acknowledge within 7 days, fix
within 30 days when practical. For valid reports we coordinate a fix, publish
a patch release when needed, and credit the reporter unless they prefer to
remain anonymous.

There is no paid bug bounty program.
