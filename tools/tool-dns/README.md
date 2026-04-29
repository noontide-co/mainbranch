# tool-dns

Stub directory. The Go binary lands in v0.1.0 Phase 2 (the build week per the master decision).

## Planned shape

```
tools/tool-dns/
├── cmd/tool-dns/main.go
├── internal/...
├── go.mod
├── go.sum
├── SKILL.md
├── README.md  (this file)
├── RELEASING.md
└── Makefile
```

## Distribution channel

`brew install noontide-co/tap/tool-dns`

## Subcommand triad

Per the discrawl pattern, every tool ships at minimum: `init`, `status`, `doctor`, `--version`.

Global flags: `-c/--config`, `--json`, `--plain`, `-q/--quiet`, `-v/--verbose`, `--no-color`, `--data-dir`.
