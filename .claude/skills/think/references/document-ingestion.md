# Document Ingestion Pipeline

How /think handles non-markdown files: PDFs, DOCX, PPTX, and other documents.

---

## Core Principle

The repo is a precision instrument, not a dumping ground. Documents get **converted to markdown** during /think — the originals stay where they are. Only the extracted, synthesized knowledge enters the repo.

---

## Detection

When a user provides a file path or mentions a document:

| Extension | Route | Tool |
|-----------|-------|------|
| `.pdf` | Convert to markdown | markitdown (primary), marker (complex/scanned) |
| `.docx` | Convert to markdown | pandoc (primary), markitdown (fallback) |
| `.pptx` | Convert to markdown | markitdown |
| `.csv`, `.xlsx` | Convert to markdown | markitdown |
| `.mp4`, `.m4a`, `.wav`, `.mov` | Existing whisper pipeline | whisper-cpp |
| `.md`, `.txt` | Read directly | Claude Code Read tool |
| `.png`, `.jpg`, `.psd`, `.ai` | Push back — media stays external | N/A |

---

## Size and Complexity Check

Before converting, assess the file:

| Condition | Action |
|-----------|--------|
| DOCX/PPTX under 10MB | Convert directly |
| PDF under 5MB, likely digital (not scanned) | Convert with markitdown |
| PDF over 5MB or appears scanned | Warn user, try markitdown first, fall back to marker with `--force_ocr` |
| Any file over 20MB | Push back: "This is too large. Extract the sections you need, or split the document." |
| Primarily images, minimal text | Push back: "This document is mostly images. What specific content do you need extracted?" |

---

## Conversion Commands

### Primary: markitdown (all formats)

```bash
# Install (one-time)
pip install 'markitdown[all]'

# Convert any supported format
markitdown input.pdf -o output.md
markitdown input.docx -o output.md
markitdown input.pptx -o output.md
```

### DOCX (best quality): pandoc

```bash
# Install (one-time)
brew install pandoc

# Convert DOCX with best structure preservation
pandoc -t gfm -s input.docx -o output.md
```

### Complex/Scanned PDFs: marker

```bash
# Install (one-time — downloads ~3GB of ML models on first run)
pip install marker-pdf

# Convert with OCR
marker_single input.pdf --output_format markdown --output_dir ./output --force_ocr
```

### Quick text extraction: pdftotext

```bash
# Install (one-time)
brew install poppler

# Extract raw text (no formatting)
pdftotext input.pdf output.txt
```

---

## Output Format

Converted documents save to research/ with extraction metadata:

```yaml
---
type: research
date: YYYY-MM-DD
source: doc-extraction
original_file: filename.pdf
original_size: 1.9MB
topics: [extracted-topic]
status: complete
---
```

Filename: `research/YYYY-MM-DD-topic-doc-extraction.md`

---

## After Conversion

1. **Synthesize** — Don't just dump the raw extraction. Extract key findings, implications for reference files, open questions.
2. **Explain** — Tell user: "Extracted to markdown. Original stays where it is — the repo only holds markdown."
3. **Route** — Ask: "Ready to make a decision from this, or need more research?"

---

## Push Back Rules

| Situation | Response |
|-----------|----------|
| File over 20MB | "Too large. Extract the sections you need or split it." |
| Mostly images, no text | "This is mostly visual. What specific ideas do you need captured?" |
| Password-protected | "Can't read this. Remove the password and try again." |
| Scanned with bad quality | "Scan quality is too low for reliable extraction. Can you get a digital version?" |
| User wants original in repo | "The repo holds markdown only. Keep the original in Google Drive or local files. We extract what matters." |

---

## Why Not Just Use Claude Code's Read Tool?

Claude Code's Read tool has a 25,000 token internal limit per read. PDFs are expensive because every page gets rasterized as an image AND text-extracted (1,500-3,000 tokens per page). A 1.9MB PDF with embedded images easily exceeds this. There's also a known bug where the "PDF too large" error becomes sticky and blocks all subsequent inputs.

External conversion tools (markitdown, pandoc, marker) produce clean markdown that Claude Code reads efficiently — no token bloat, no image processing overhead, no sticky errors.

---

## Tool Detection

Check `.vip/config.yaml` tools section. If conversion tools aren't detected:

```bash
which markitdown 2>/dev/null && echo "MARKITDOWN=1" || echo "MARKITDOWN=0"
which pandoc 2>/dev/null && echo "PANDOC=1" || echo "PANDOC=0"
which marker_single 2>/dev/null && echo "MARKER=1" || echo "MARKER=0"
```

If no tools available, offer setup:
> "Document conversion needs markitdown. Install now? `pip install 'markitdown[all]'`"

If user declines, fall back to Claude Code's Read tool with a warning about size limits.

---

## See Also

- `think/SKILL.md` — Routes to this pipeline when file paths detected
- `think/references/local-transcription.md` — Parallel pipeline for video/audio files
- `think/references/research-phase.md` — Where extracted documents feed into
- `start/references/config-system.md` — Media path configuration in local.yaml
