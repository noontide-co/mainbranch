---
name: deck
description: Create branded presentations from your business context. Use when: (1) Asked to create slides, decks, presentations, or teaching materials (2) User says "presentation", "deck", "slides", "powerpoint", "pptx" (3) Need to visualize a framework or process for teaching (4) Creating pitch decks, workshop materials, or course content. Reads brand guide and assets from your repo, outputs .pptx files matching your visual identity.
---

# Presentation Creator

Create branded PowerPoint presentations using your business context and visual identity.

**Need help?** Type `/help` + your question anytime.

## Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

---

## Where Files Go

**All files are saved to YOUR business repo, not the engine (vip).**

```
your-business-repo/          <- Files saved here
├── reference/brand/         <- Brand context (read from here)
│   ├── visual-style.md
│   └── assets/              <- Logos, textures, decorative elements
└── outputs/decks/           <- Generated presentations

vip/ (engine)                <- Never modified by /deck
└── .claude/skills/deck/     <- This skill lives here
```

---

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

## Workflow

1. **Read brand context**: Read user's `reference/brand/visual-style.md`
2. **Plan content**: Create outline with slide-by-slide breakdown
3. **Choose theme**: Based on user's defined themes (if multiple exist)
4. **Generate assets**: If AI images needed, use Gemini integration
5. **Build slides**: Use html2pptx workflow from base skill
6. **Save output**: Save to `outputs/decks/` in user's repo
7. **Validate**: Generate thumbnails, check brand consistency

See [`references/html2pptx.md`](references/html2pptx.md) for html2pptx details.

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

---

## References

- [`references/html2pptx.md`](references/html2pptx.md) - HTML to PowerPoint conversion
- [`references/ooxml.md`](references/ooxml.md) - OOXML format reference
- [`references/svg-guide.md`](references/svg-guide.md) - SVG handling guide

*Forked from [anthropics/skills/pptx](https://github.com/anthropics/skills/tree/main/skills/pptx)*
