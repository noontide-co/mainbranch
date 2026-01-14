# Deck Skill Setup Guide

How to use the `/deck` skill for creating Main Branch presentations.

---

## Prerequisites

### 1. Install Dependencies

```bash
# Node.js packages (global)
npm install -g pptxgenjs playwright sharp react react-dom react-icons

# Python packages
pip install "markitdown[pptx]" defusedxml

# System tools (macOS)
brew install libreoffice poppler

# System tools (Linux)
sudo apt-get install libreoffice poppler-utils
```

### 2. Configure Environment (Optional)

For AI image generation with Gemini:

```bash
# Copy the example env file
cp .env.example .env

# Edit and add your Gemini API key
# Get one at: https://makersuite.google.com/app/apikey
```

---

## Usage

### Basic Presentation

```
Create a 5-slide presentation about [topic]
```

The skill will:
1. Read the Main Branch style guide
2. Create HTML slides with brand styling
3. Convert to PowerPoint
4. Generate thumbnails for validation

### With AI Images

```
Create a presentation about [topic] with AI-generated images
```

Requires `GEMINI_API_KEY` in your `.env` file.

### Using a Template

```
Create a presentation using template.pptx as a base
```

---

## Customization

### Brand Assets

Place your assets in `.claude/skills/deck/assets/`:

```
assets/
├── logo/
│   ├── tree-circuit-dark.png
│   ├── tree-circuit-light.png
│   └── tree-mark-only.png
├── textures/
│   ├── crt-scanlines.png
│   └── terminal-grain.png
└── decorative/
    └── circuit-traces.svg
```

### Style Guide

Edit `.claude/skills/deck/main-branch-style.md` to customize:
- Color palette
- Typography
- Layout templates
- Visual elements

---

## Troubleshooting

### "pptxgenjs not found"

```bash
npm install -g pptxgenjs
```

### "LibreOffice not found"

```bash
# macOS
brew install libreoffice

# Linux
sudo apt-get install libreoffice
```

### Colors look wrong

Remember: PptxGenJS requires hex colors WITHOUT the `#` prefix.

```javascript
// ✅ Correct
color: "4ade80"

// ❌ Wrong (causes file corruption)
color: "#4ade80"
```

---

## Resources

- [Main Branch Style Guide](/.claude/skills/deck/main-branch-style.md)
- [Anthropic PPTX Skill](https://github.com/anthropics/skills/tree/main/skills/pptx)
- [PptxGenJS Documentation](https://gitbrent.github.io/PptxGenJS/)

---

*Last updated: 2026-01-14*
