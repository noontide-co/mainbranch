# tool-stripe

Stub directory. This Go binary never shipped in the public v0.3.x engine.
Current provider/payment work should be revived only behind a fresh decision,
explicit approval gates, and secret-safe connection checks. Treat this folder
as historical design material unless a new decision revives it.

## Planned shape

```
tools/tool-stripe/
├── cmd/tool-stripe/main.go
├── internal/...
├── go.mod
├── go.sum
├── SKILL.md
├── README.md  (this file)
├── RELEASING.md
└── Makefile
```

## Distribution channel

`brew install noontide-co/tap/tool-stripe`

## Subcommand triad

Per the discrawl pattern, every tool ships at minimum: `init`, `status`, `doctor`, `--version`.

Global flags: `-c/--config`, `--json`, `--plain`, `-q/--quiet`, `-v/--verbose`, `--no-color`, `--data-dir`.
