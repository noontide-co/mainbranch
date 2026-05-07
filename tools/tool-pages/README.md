# tool-pages

Stub directory. This Go binary never shipped in the public v0.3.x engine. Current Pages/Sites work lives in `/mb-site` and the packaged Python site/Cloudflare readiness atoms. Treat this folder as historical design material unless a new decision revives it.

## Planned shape

```
tools/tool-pages/
├── cmd/tool-pages/main.go
├── internal/...
├── go.mod
├── go.sum
├── SKILL.md
├── README.md  (this file)
├── RELEASING.md
└── Makefile
```

## Distribution channel

`brew install noontide-co/tap/tool-pages`

## Subcommand triad

Per the discrawl pattern, every tool ships at minimum: `init`, `status`, `doctor`, `--version`.

Global flags: `-c/--config`, `--json`, `--plain`, `-q/--quiet`, `-v/--verbose`, `--no-color`, `--data-dir`.
