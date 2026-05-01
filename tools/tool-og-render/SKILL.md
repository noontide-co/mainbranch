---
name: tool-og-render
tier: tool
calls: []
description: "Render inline SVG to 1200x630 PNG for OG meta tags. rsvg-convert primary path, cairosvg fallback. Bundled with mainbranch PyPI package."
prerequisites:
  commands: [rsvg-convert]
  optional: [cairosvg]
---

# tool-og-render

Wrapper SKILL.md for the og_render.py implementation living at `.claude/skills/site/scripts/og_render.py`. Live-tested via PR #100 on thelastbill.com.

## Subcommand

```
tool-og-render render <input.svg> [<output.png>]
```

Renders 1200x630, validates dimensions, returns a companyctx-shape envelope on stdout. Exit 0 on ok|partial; 1 on degraded.

## Why this exists as a tool

Site HTML/CSS/SVG generation happens via Claude Code subagents (LLM work). The SVG → PNG render is deterministic external work — shell to a binary, validate output. Closed-enum errors. That's tool-shape.

## See also

- `.claude/skills/site/scripts/og_render.py` — actual implementation
- `tool-og-render/wrapper.py` (planned) — thin Python wrapper exposed via the `mb` umbrella
