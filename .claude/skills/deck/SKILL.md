---
name: deck
description: Create branded presentations from your business context. Use when asked to create slides, decks, presentations, or teaching materials. Reads brand guide and assets from your repo, outputs .pptx files matching your visual identity.
---

# Presentation Creator

Create branded PowerPoint presentations using your business context and visual identity.

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

---

## Overview

This skill is a fork of Anthropic's PPTX skill, enhanced with:
- **Brand-aware generation** — Reads your style guide from `reference/brand/`
- **Asset integration** — Uses your logos, textures, and decorative elements
- **Gemini integration** for AI image generation (optional)

## Context Required

Before creating presentations, the business repo should have:

| File | What It Contains |
|------|------------------|
| `reference/brand/visual-style.md` | Visual identity, color palettes, typography |
| `reference/brand/assets/logo/` | Logo variants for different backgrounds |
| `reference/brand/assets/textures/` | Background textures, overlays |
| `reference/brand/assets/decorative/` | Decorative elements, dividers |

If brand context is missing, ask the user to create it or offer to help define their visual identity.

## Reading Brand Context

**Always read the user's style guide first** before creating any presentation:

```
reference/brand/visual-style.md
```

If no style guide exists, offer to help create one using the template at:
```
templates/modules/brand-style-template.md
```

## Workflows

### Creating a New Presentation

1. **Read brand context**: Read user's `reference/brand/visual-style.md`
2. **Plan content**: Create outline with slide-by-slide breakdown
3. **Choose theme**: Based on user's defined themes (if multiple exist)
4. **Generate assets**: If AI images needed, use Gemini integration
5. **Build slides**: Use html2pptx workflow from base skill
6. **Validate**: Generate thumbnails, check brand consistency

### Using the html2pptx Workflow

See [`references/html2pptx.md`](references/html2pptx.md) for detailed instructions.

**Brand-aware additions:**
- Use colors from user's style guide
- Use brand fonts (fallback to web-safe equivalents)
- Include logo per user's placement guidelines
- Apply textures/overlays as defined in brand

## Design Principles

### Reading User's Palette

Extract colors from `reference/brand/visual-style.md`:
- Background colors (primary, secondary)
- Text colors (primary, muted, accent)
- Accent colors (success, warning, error, links)
- Chart colors (series colors for data viz)

### Typography

**Always use web-safe fonts for PowerPoint compatibility:**
- **Headers**: Arial Black, Impact, Trebuchet MS
- **Body**: Verdana, Tahoma, Arial
- **Code/Data**: Courier New (monospace)

If user specifies custom fonts, note they may not render on all machines.

### Visual Elements

Read from user's brand guide:
- Background textures/overlays
- Decorative elements (dividers, frames)
- Logo placement rules
- Glow/shadow effects

## Gemini Integration (Optional)

For AI-generated images, set `GEMINI_API_KEY` in environment.

See project `.env.example` for setup instructions.

## Dependencies

Same as base PPTX skill:
- markitdown (text extraction)
- pptxgenjs (PowerPoint generation)
- playwright (HTML rendering)
- sharp (image processing)
- LibreOffice (PDF conversion)
- Poppler (PDF to images)

## Base Skill Documentation

For complete PPTX creation, editing, and analysis workflows, see:
- [`references/html2pptx.md`](references/html2pptx.md) - HTML to PowerPoint conversion
- [`references/ooxml.md`](references/ooxml.md) - OOXML format reference
- [`references/svg-guide.md`](references/svg-guide.md) - SVG handling guide

---

*Forked from [anthropics/skills/pptx](https://github.com/anthropics/skills/tree/main/skills/pptx)*
