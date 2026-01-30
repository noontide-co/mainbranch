# Static Ad Output Template

Use this structure for campaign batch outputs.

## Contents

- **Part 1: Image Prompts** - Generate all images first (line 25)
- **Part 2: Ad Copy** - Copy for Ads Manager (line 70)
- **Naming Conventions** - File and image naming (line 174)
- **Format Pair: 1:1 + 9:16** - Vertical-first design strategy (line 191)

---

```markdown
# Campaign Batch {number} — {Campaign Name}

Generated: {date}
Target: {Offer name and price}
Destination: {CTA URL}

**Workflow:** Generate all images first (Part 1), then copy ad text (Part 2)

---

# PART 1: IMAGE PROMPTS

Generate all images first. Design 9:16 vertical first, then center-crop for 1:1 square.

---

## Ad 1: {Angle Name} — {batch#}.1

**Angle:** {description}
**Avatar:** {target persona}

---

### {batch#}.1_IMG_01 — {Descriptive Name}

**Vertical (1080×1920) — design this first:**
```text
{Full prompt for 9:16 vertical. Place critical content (headline, product, key visual) in center 1:1 zone. Fill top/bottom margins with atmospheric/contextual elements.}
```

**Square (1920×1920) — center-crop from vertical:**
```text
{Center-crop the vertical to extract the 1:1 safe zone at 1920×1920.}
```

---

### {batch#}.1_IMG_02 — {Descriptive Name}

[Repeat structure]

---

### {batch#}.1_IMG_03 — {Descriptive Name}

[Repeat structure]

---

## Ad 2: {Angle Name} — {batch#}.2

[Repeat full structure for each ad]

---

# PART 2: AD COPY FOR ADS MANAGER

Copy and paste into Ads Manager after images are ready.

---

## Ad 1: {Angle Name} — {batch#}_IMG_01

---

### Primary 1 — Deep Ad (~500 words)

**Hook:** {123-135 chars}

```text
{Full primary text}

{CTA URL}
```

---

### Primary 2 — UGC/Native (~200 words)

**Hook:** {hook}

```text
{Primary text}

{CTA URL}
```

---

### Primary 3 — Direct Response (~300 words)

**Hook:** {hook}

```text
{Primary text}

{CTA URL}
```

---

### Primary 4 — Pattern Interrupt (~80 words)

**Hook:** {hook}

```text
{Primary text}

{CTA URL}
```

---

### Primary 5 — Testimonial (~300 words)

**Hook:** {hook}

```text
{Primary text}

{CTA URL}
```

---

### Headlines — {batch#}_IMG_01

**Headline 1 — Proof-led**
```text
{Headline}
```

**Headline 2 — Mechanism-led**
```text
{Headline}
```

**Headline 3 — Outcome-led**
```text
{Headline}
```

**Headline 4 — Curiosity-led**
```text
{Headline}
```

**Headline 5 — Benefit-led**
```text
{Headline}
```

---

[Repeat for Ad 2, Ad 3, etc.]
```

---

## Naming Conventions

**Folder:** `outputs/YYYY-MM-DD-static-ads-{campaign}/`
- Date: `YYYY-MM-DD`
- Type: `static-ads`
- Campaign name: lowercase with dashes (required)

**Batch file:** `static-ads-batch-{###}.md`
- Example: `static-ads-batch-001.md`

**Full path example:** `outputs/2026-01-15-static-ads-january-launch/static-ads-batch-001.md`

**Review log:** `review-log.md` (same folder)

**Image naming:** `{batch}.{ad#}_IMG_{image#}`
- `001.1_IMG_01` — first image for Ad 1
- `001.1_IMG_02` — second image for Ad 1
- `001.2_IMG_01` — first image for Ad 2

---

## Format Pair: 1:1 + 9:16

Facebook Ads Manager accepts exactly two image uploads per ad: **1:1 (square)** and **9:16 (vertical)**. There is no 4:5 option.

### Design Strategy

Design the **9:16 vertical first** with critical content in the **center 1:1 safe zone**. Then center-crop for the square version. One design → two uploads.

### Prompt Approach

1. **9:16 prompt** (1080×1920) — Full creative with critical content centered
2. **1:1 extraction** — Center-crop the 9:16 to 1920×1920

**Standard 9:16 prompt directive:**
```text
Aspect ratio 9:16, resolution 1080x1920. Place all critical content (headline, product, key visual) in the center 1:1 zone. Fill top and bottom margins with atmospheric/contextual elements. Keep text and important elements centered vertically between 25% and 70% from top to stay within safe zones.
```

### Post-Processing (When Using Nano Banana)

If Nano Banana generated the image:
- Raw output is PNG at 1024x1024
- Resize to 1080×1920 (9:16) and 1920×1920 (1:1 center-crop)
- Convert PNG → JPEG, compress under 300KB
- See `image-generation-workflow.md` for full pipeline

---

## Image Index

When Nano Banana generates actual images, create an `image-index.md` in the batch folder:

```markdown
# Image Index — {Campaign Name}

| File | Angle | Style | Format | Prompt Summary |
|------|-------|-------|--------|----------------|
| 001_01_graphic_square.jpg | Authority | Graphic | 1:1 | Bold framework on dark gradient |
| 001_01_graphic_vertical.jpg | Authority | Graphic | 9:16 | Same, full vertical |
| 001_02_lofi_square.jpg | Social Proof | Lo-fi | 1:1 | Casual phone-style screenshot |
| ... | ... | ... | ... | ... |

Generated: {date}
Model: gemini-3-pro-image-preview
Cost: ~${total}
```
