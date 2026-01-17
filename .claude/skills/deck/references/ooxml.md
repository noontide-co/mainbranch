# Office Open XML Technical Reference

This document provides technical details for working with PowerPoint's OOXML format.

**Full reference**: See [anthropics/skills/pptx/ooxml.md](https://github.com/anthropics/skills/blob/main/skills/pptx/ooxml.md)

## Quick Reference

### File Structure

A .pptx file is a ZIP archive containing:

```
presentation.pptx/
├── [Content_Types].xml      # Content type declarations
├── _rels/
│   └── .rels               # Package relationships
├── docProps/
│   ├── app.xml             # Application properties
│   └── core.xml            # Core metadata
└── ppt/
    ├── presentation.xml    # Main presentation data
    ├── slides/             # Individual slides
    │   ├── slide1.xml
    │   └── slide2.xml
    ├── slideLayouts/       # Layout templates
    ├── slideMasters/       # Master templates
    ├── theme/              # Theme data
    └── media/              # Images and media
```

### Key Operations

**Unpack**: `python ooxml/scripts/unpack.py <file.pptx> <output_dir>`

**Validate**: `python ooxml/scripts/validate.py <dir> --original <file.pptx>`

**Pack**: `python ooxml/scripts/pack.py <input_dir> <output.pptx>`

### Common Tasks

| Task | Approach |
|------|----------|
| Add slide | Create XML, update relationships |
| Edit text | Modify `<a:t>` elements in slide XML |
| Change colors | Update `<a:srgbClr>` values |
| Add image | Copy to media/, add relationship, reference in slide |

---

*For complete OOXML documentation, refer to the Anthropic skills repository.*
