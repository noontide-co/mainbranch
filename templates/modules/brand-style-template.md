# Visual Style Guide Template

**Usage**: Copy this file to your business repo at `reference/brand/visual-style.md` and customize for your brand.

This template is populated with Main Branch's style as an example. Replace all sections with your own brand details.

---

## Brand Overview

> **Replace this section with your brand info**

**[Brand Name]** — [What you do in one line]

**Positioning**: "[Your tagline]"

**Core metaphor**: [What visual metaphor represents your brand?]

**Voice**: [Describe your brand voice]

---

## Style Identity

> **Replace with your style description**

Give your style a name and describe it as a fusion of influences.

**Example (Main Branch):**

*Style: "Terminal Forest"* — A fusion of retro terminal aesthetics, organic growth imagery, and modern dark mode.

---

## Two Themes

| Theme | Background | Accent | Use Case |
|-------|------------|--------|----------|
| **Editorial/Dark** | #0a0f0a (near-black green) | Cyan glow, green highlights | Brand storytelling, launches |
| **Teaching/Neutral** | #1a1a2e (dark navy) | Amber LEDs, warm accents | Curriculum, tutorials |

---

## Color Palette

### Primary Colors

```
DARK BACKGROUNDS
├── #0a0f0a  "Terminal Black"    Primary background (green-tinted black)
├── #121212  "Pure Dark"         Alternative background
├── #1a1a2e  "Navy Dark"         Teaching theme background
└── #0d1117  "GitHub Dark"       Code block backgrounds

LIGHT TEXT
├── #f0fdf4  "Soft White"        Primary text (slight green tint)
├── #e2e8f0  "Cool Gray"         Secondary text
├── #86efac  "Muted Green"       Tertiary text, labels
└── #64748b  "Slate"             Disabled, placeholder text
```

### Accent Colors

```
GREENS (Tree Canopy)
├── #4ade80  "Canopy Green"      Primary accent, success states
├── #22c55e  "Terminal Green"    Active states, highlights
├── #16a34a  "Forest Green"      Darker green for contrast
└── #166534  "Deep Forest"       Shadows, depth

AMBERS (Circuit LEDs)
├── #f59e0b  "Amber LED"         Warning, attention, nodes
├── #fbbf24  "Bright Amber"      Hover states
├── #d97706  "Dark Amber"        Pressed states
└── #92400e  "Burnt Amber"       Shadows

CYANS (Terminal Glow)
├── #22d3ee  "Cyan Glow"         Links, interactive elements
├── #06b6d4  "Bright Cyan"       Hover states
├── #0891b2  "Dark Cyan"         Pressed states
└── #155e75  "Deep Cyan"         Shadows

REDS (Errors/Emphasis)
├── #f87171  "Coral Red"         Errors, warnings, emphasis
├── #ef4444  "Bright Red"        Critical alerts
└── #dc2626  "Dark Red"          Pressed states
```

### Semantic Colors

```
SUCCESS     #4ade80  Canopy Green
WARNING     #f59e0b  Amber LED
ERROR       #f87171  Coral Red
INFO        #22d3ee  Cyan Glow
LINK        #22d3ee  Cyan Glow
ACTIVE      #22c55e  Terminal Green
MUTED       #64748b  Slate
```

---

## Typography

### Font Stack (Web-Safe Only)

```
DISPLAY/HEADERS
├── Primary:    "Impact" or "Arial Black"
├── Fallback:   "Trebuchet MS", "Helvetica", sans-serif
└── Use:        Slide titles, section headers

BODY TEXT
├── Primary:    "Verdana" or "Tahoma"
├── Fallback:   "Arial", "Helvetica", sans-serif
└── Use:        Paragraphs, lists, descriptions

MONOSPACE (Code/Data)
├── Primary:    "Courier New"
├── Fallback:   "Lucida Console", monospace
└── Use:        Code snippets, file paths, technical data, stats
```

### Type Scale

```
SLIDE TITLES       48-64pt    Impact/Arial Black, bold
SECTION HEADERS    32-40pt    Trebuchet MS, bold
SUBHEADERS         24-28pt    Verdana, bold
BODY LARGE         18-20pt    Verdana, regular
BODY STANDARD      14-16pt    Verdana, regular
CAPTIONS           11-12pt    Verdana, regular
CODE               14pt       Courier New, regular
```

### Typography Rules

1. **Never use more than 2 fonts per slide**
2. **Headers always bold**, body rarely bold
3. **Monospace for any technical content** (paths, code, commands)
4. **High contrast**: Light text on dark backgrounds only
5. **Letter spacing**: Slightly increased for headers (+0.5-1pt)

---

## Visual Elements

### The Logo

Three variants available:

| Variant | File | Use Case |
|---------|------|----------|
| **Full Dark** | `tree-circuit-dark.png` | Dark backgrounds, primary use |
| **Full Light** | `tree-circuit-light.png` | Light backgrounds (rare) |
| **Mark Only** | `tree-mark-only.png` | Favicons, small spaces |

**Logo anatomy:**
- Lush green tree canopy (organic, alive)
- White/cyan circuit traces for trunk and roots (structure, system)
- Amber/orange LED nodes at branch points (activity, data flow)
- Soft cyan glow halo (CRT aesthetic)

**Logo placement:**
- Title slides: Centered, large
- Content slides: Bottom-right corner, small
- Teaching slides: Top-left corner, small

### CRT Texture Overlay

Apply subtle scanline texture for terminal aesthetic:
- Horizontal lines at 2-3px intervals
- 5-10% opacity (very subtle)
- Use on hero slides and section dividers
- Skip on content-heavy slides for readability

### Circuit Traces

Decorative lines suggesting data flow:
- Use as section dividers
- Connect related concepts visually
- Animate in videos (optional)
- Colors: Cyan (#22d3ee) or white at 30-50% opacity

### Glow Effects

Terminal-style glow on key elements:
- Apply to logo
- Apply to important numbers/stats
- Use box-shadow with blur: `0 0 20px rgba(34, 211, 238, 0.3)`
- Don't overuse — 1-2 glowing elements per slide max

---

## Slide Layouts

### Title Slide

```
┌─────────────────────────────────────────┐
│                                         │
│              [LOGO]                     │
│                                         │
│         PRESENTATION TITLE              │
│           Subtitle text                 │
│                                         │
│                                         │
│   ══════════════════════════════════    │  ← circuit trace divider
│                                         │
└─────────────────────────────────────────┘
Background: #0a0f0a with subtle CRT texture
```

### Section Divider

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│                                         │
│          SECTION TITLE                  │
│      ────────────────────               │
│                                         │
│                                         │
│                                    [MB] │  ← small logo
└─────────────────────────────────────────┘
Background: #0a0f0a
Accent: Cyan glow on title
```

### Content Slide (Two-Column)

```
┌─────────────────────────────────────────┐
│  SLIDE TITLE                            │
│  ═══════════════════════════════════    │
│                                         │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │              │  │                  │ │
│  │   TEXT       │  │    VISUAL        │ │
│  │   CONTENT    │  │    (chart/image) │ │
│  │              │  │                  │ │
│  └──────────────┘  └──────────────────┘ │
│                                    [MB] │
└─────────────────────────────────────────┘
Split: 40% text / 60% visual
```

### Quote Slide

```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│     "Quote text goes here in large      │
│      italic type with quotes."          │
│                                         │
│                    — Attribution        │
│                                         │
│                                         │
│                                    [MB] │
└─────────────────────────────────────────┘
Quote color: #4ade80 (Canopy Green)
Attribution: #86efac (Muted Green)
```

### Data/Stats Slide

```
┌─────────────────────────────────────────┐
│  SLIDE TITLE                            │
│  ═══════════════════════════════════    │
│                                         │
│   ┌─────┐   ┌─────┐   ┌─────┐          │
│   │ 20  │   │  2  │   │ 10x │          │
│   │hours│   │hours│   │ ROI │          │
│   └─────┘   └─────┘   └─────┘          │
│    Before    After    Result            │
│                                         │
│                                    [MB] │
└─────────────────────────────────────────┘
Numbers: Large (48-64pt), Monospace, Cyan glow
Labels: Small (14pt), Muted Green
```

---

## Chart Styling

### Colors for Charts

```javascript
// Single series
chartColors: ["4ade80"]  // Canopy Green

// Multiple series
chartColors: ["4ade80", "22d3ee", "f59e0b", "f87171"]
// Green, Cyan, Amber, Coral

// Pie charts
chartColors: ["4ade80", "22d3ee", "f59e0b", "86efac", "0891b2"]
```

### Chart Rules

1. **Dark background for chart area** (#121212 or transparent)
2. **Light gridlines** at 10-20% opacity
3. **No 3D effects** — flat design only
4. **Axis labels in Muted Green** (#86efac)
5. **Data labels in Soft White** (#f0fdf4)

---

## Image Guidelines

### AI Image Prompts (for Gemini/Midjourney)

When generating images for Main Branch materials:

**Style keywords:**
- "dark background, near-black"
- "terminal aesthetic, CRT glow"
- "organic and digital fusion"
- "circuit board traces"
- "bonsai tree, pine tree"
- "soft cyan and green glow"
- "retro futurism"

**Avoid:**
- Bright backgrounds
- Corporate stock photo style
- Geometric patterns (use organic shapes)
- Pure white elements

### Screenshot Treatment

When including screenshots:
1. Add subtle border (#22d3ee at 50% opacity)
2. Apply slight corner radius (8-12px)
3. Add drop shadow for depth
4. Consider CRT texture overlay on decorative screenshots

---

## Animation Guidelines (for Video)

### Transitions

- **Preferred**: Fade, dissolve (0.3-0.5s)
- **Accent**: Slide from left (data flow direction)
- **Avoid**: Spin, flip, bounce, or playful transitions

### Element Animation

- **Text**: Fade in, slight upward motion
- **Charts**: Draw on, bars grow upward
- **Circuit traces**: Draw along path (like data flowing)
- **Logo**: Fade in with subtle glow pulse

---

## Do's and Don'ts

### Do

- ✅ Use dark backgrounds consistently
- ✅ Apply CRT texture on hero/divider slides
- ✅ Use monospace for technical content
- ✅ Include logo on every slide (small, corner)
- ✅ Use high contrast (light on dark)
- ✅ Apply glow effects sparingly

### Don't

- ❌ Use light/white backgrounds
- ❌ Use more than 2 fonts per slide
- ❌ Overuse glow effects (max 1-2 per slide)
- ❌ Use geometric patterns (stay organic)
- ❌ Use corporate stock imagery
- ❌ Use low contrast text

---

## Assets Checklist

Before creating a presentation, ensure you have:

- [ ] Logo variants (dark, light, mark)
- [ ] CRT scanline texture
- [ ] Circuit trace SVG/PNG
- [ ] Brand color hex codes
- [ ] Font files (if custom, otherwise web-safe)

---

*Last updated: 2026-01-14*
*Style version: 1.0*
