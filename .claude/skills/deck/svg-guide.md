# SVG Generation Guide

Guidelines for generating SVG graphics for Main Branch presentations.

---

## Why This Guide Exists

AI-generated SVGs often have issues:
- Incorrect viewBox dimensions
- Missing xmlns declaration
- Broken paths
- Unsupported features

This guide ensures consistent, valid SVGs.

---

## SVG Template

Always start with this structure:

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 WIDTH HEIGHT"
     width="WIDTH"
     height="HEIGHT">
  <!-- Content here -->
</svg>
```

**Required attributes:**
- `xmlns` — Always include
- `viewBox` — Define coordinate system
- `width/height` — Explicit dimensions

---

## Main Branch SVG Colors

Use brand colors from the style guide:

```xml
<!-- Backgrounds -->
<rect fill="#0a0f0a"/>  <!-- Terminal Black -->
<rect fill="#121212"/>  <!-- Pure Dark -->

<!-- Accents -->
<path fill="#4ade80"/>  <!-- Canopy Green -->
<path fill="#22d3ee"/>  <!-- Cyan Glow -->
<path fill="#f59e0b"/>  <!-- Amber LED -->

<!-- Text -->
<text fill="#f0fdf4"/>  <!-- Soft White -->
<text fill="#86efac"/>  <!-- Muted Green -->
```

---

## Glow Effects

For CRT-style glow, use filters:

```xml
<defs>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
</defs>

<circle cx="50" cy="50" r="10" fill="#22d3ee" filter="url(#glow)"/>
```

---

## Circuit Trace Pattern

For decorative circuit lines:

```xml
<path d="M0 50 L100 50 L100 100"
      stroke="#22d3ee"
      stroke-width="2"
      fill="none"
      stroke-linecap="round"/>

<!-- With nodes (LED points) -->
<circle cx="100" cy="50" r="4" fill="#f59e0b"/>
```

---

## Tree/Branch Shapes

For organic branch shapes:

```xml
<!-- Simplified branch path -->
<path d="M50 100
         Q50 70 40 50
         Q30 30 20 10
         M50 70
         Q60 50 80 40"
      stroke="#4ade80"
      stroke-width="3"
      fill="none"
      stroke-linecap="round"/>
```

---

## Rasterizing SVGs

**Always rasterize SVGs to PNG before using in PowerPoint.**

PowerPoint's SVG support is inconsistent. Rasterize with Sharp:

```javascript
const sharp = require('sharp');

async function svgToPng(svgPath, pngPath, width = 1000) {
  await sharp(svgPath)
    .resize(width)
    .png()
    .toFile(pngPath);
}

// Usage
await svgToPng('circuit-trace.svg', 'circuit-trace.png', 800);
```

---

## Common Issues & Fixes

### Issue: SVG not rendering

**Fix**: Ensure `xmlns` is present:
```xml
<svg xmlns="http://www.w3.org/2000/svg" ...>
```

### Issue: Wrong size in PowerPoint

**Fix**: Set explicit width/height, not just viewBox:
```xml
<svg viewBox="0 0 100 100" width="100" height="100">
```

### Issue: Gradients not showing

**Fix**: Rasterize to PNG. PowerPoint gradient support is limited.

### Issue: Filters not working

**Fix**: Rasterize to PNG. Complex filters don't convert well.

---

## SVG Validation Checklist

Before using an SVG:

- [ ] Has `xmlns="http://www.w3.org/2000/svg"`
- [ ] Has valid `viewBox`
- [ ] Has explicit `width` and `height`
- [ ] All paths are closed or properly stroked
- [ ] Colors use hex format (#rrggbb)
- [ ] No external references (fonts, images)
- [ ] Tested render in browser

---

## When to Use SVG vs PNG

| Use SVG | Use PNG |
|---------|---------|
| Source assets | Final presentation |
| Scalable icons | Complex illustrations |
| Simple shapes | Photos/textures |
| Version control | AI-generated images |

**Rule**: Keep SVG as source, rasterize to PNG for PowerPoint.

---

*Last updated: 2026-01-14*
