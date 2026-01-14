# HTML to PowerPoint Guide

Convert HTML slides to PowerPoint presentations with accurate positioning.

**Full reference**: See [anthropics/skills/pptx/html2pptx.md](https://github.com/anthropics/skills/blob/main/skills/pptx/html2pptx.md)

---

## Quick Start

### 1. Create HTML Slide

```html
<!DOCTYPE html>
<html>
<head>
<style>
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background: #121212;  /* Use brand background color */
  font-family: Verdana, sans-serif;
  color: #f0f0f0;       /* Use brand text color */
  display: flex;
}
h1 { color: #4ade80; font-size: 48pt; }  /* Use brand accent */
</style>
</head>
<body>
  <div style="margin: 40pt;">
    <h1>Slide Title</h1>
    <p>Content goes here</p>
  </div>
</body>
</html>
```

### 2. Convert to PowerPoint

```javascript
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_16x9';

const { slide } = await html2pptx('slide1.html', pptx);
await pptx.writeFile('output.pptx');
```

---

## Using Brand Colors

Read colors from the user's `context/brand/visual-style.md` and create a colors object:

```javascript
// Example: Extract from user's style guide
const BRAND_COLORS = {
  bgPrimary: "0a0f0a",    // From style guide
  bgSecondary: "121212",
  textPrimary: "f0fdf4",
  textMuted: "86efac",
  accent1: "4ade80",
  accent2: "22d3ee",
  accent3: "f59e0b",
  warning: "f87171"
};
```

**CRITICAL**: No `#` prefix in PptxGenJS colors!

### Chart Colors

```javascript
// Single series - use primary accent
chartColors: ["4ade80"]

// Multiple series - use accent palette
chartColors: ["4ade80", "22d3ee", "f59e0b", "f87171"]
```

### Web-Safe Fonts

```javascript
// Headers
fontFace: "Impact"  // or "Arial Black", "Trebuchet MS"

// Body
fontFace: "Verdana"  // or "Tahoma", "Arial"

// Code/Data
fontFace: "Courier New"
```

---

## Critical Rules

### Text Must Be in Tags

- ✅ `<div><p>Text</p></div>`
- ❌ `<div>Text</div>` — Text will NOT appear

### No Manual Bullets

- ✅ Use `<ul>` and `<ol>`
- ❌ Never use •, -, * symbols

### Web-Safe Fonts Only

- ✅ Arial, Verdana, Georgia, Courier New, Impact
- ❌ Segoe UI, Roboto, SF Pro

### Colors Without Hash

- ✅ `color: "4ade80"`
- ❌ `color: "#4ade80"` — Causes corruption

---

## Workflow

1. **Read user's style guide** from `context/brand/visual-style.md`
2. **Create HTML slides** with brand colors/fonts
3. **Rasterize gradients/icons** to PNG using Sharp FIRST
4. **Convert with html2pptx**
5. **Add charts/tables** using PptxGenJS
6. **Generate thumbnails** to validate
7. **Iterate** until visually correct

---

## Dependencies

```bash
# Required
npm install -g pptxgenjs playwright sharp

# For text extraction
pip install "markitdown[pptx]"

# For PDF conversion
brew install libreoffice poppler  # macOS
```

---

*See full documentation at [anthropics/skills](https://github.com/anthropics/skills)*
