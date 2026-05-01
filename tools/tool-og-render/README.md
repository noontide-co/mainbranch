# tool-og-render

Python wrapper around `.claude/skills/site/scripts/og_render.py` (live-tested on `thelastbill.com` via PR #100). Renders inline SVG → 1200x630 PNG via `rsvg-convert` (primary) with `cairosvg` fallback (CI/Linux).

## Distribution

Bundled with the `mainbranch` PyPI package. System dep: `librsvg`.

```bash
brew install librsvg          # macOS
apt install librsvg2-bin      # Linux
pipx install mainbranch       # gets the wrapper
```

## Why not Node/Puppeteer

Pressure-tested 2026-04-29. The static SVG (hero text + signature visual + wordmark; no JS, no network, no web fonts) is purpose-built for SVG rasterizers, NOT headless browsers. 200MB Chromium dep is overkill. `rsvg + cairosvg` matches every constraint and is already production-proven.

## v0.2+ upgrade path

`resvg` (Rust). Single static <3MB binary, sub-10ms render, identical macOS/Linux output, no system deps. Drop-in replacement via `brew install resvg`. Gate the swap on (a) one real failure mode in `rsvg-convert` that resvg fixes, OR (b) v0.2 release window opening.

## Implementation

The actual code is at `.claude/skills/site/scripts/og_render.py`. This directory is the wrapper / packaging surface; do NOT duplicate the renderer.
