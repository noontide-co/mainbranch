# Static Ad Output Template

Use this structure for campaign batch outputs.

## Contents

- **Part 1: Image Prompts** - Generate all images first (line 25)
- **Part 2: Ad Copy** - Copy for Ads Manager (line 70)
- **Naming Conventions** - File and image naming (line 174)
- **Two Sizes Per Image** - Square + vertical prompts (line 191)

---

```markdown
# Campaign Batch {number} — {Campaign Name}

Generated: {date}
Target: {Offer name and price}
Destination: {CTA URL}

**Workflow:** Generate all images first (Part 1), then copy ad text (Part 2)

---

# PART 1: IMAGE PROMPTS

Generate all images first. Each prompt has square and vertical versions.

---

## Ad 1: {Angle Name} — {batch#}.1

**Angle:** {description}
**Avatar:** {target persona}

---

### {batch#}.1_IMG_01 — {Descriptive Name}

**Square (1920×1920):**
```text
{Full prompt for square}
```

**Vertical (1080×1920):**
```text
Now resize to 1080x1920 vertical. Keep all text/important content centered in the middle 50% of the frame.
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

**Batch files:** `{batch#}_IMG_{campaign-name}_{date}.md`
- Batch number: 3 digits (`001`, `002`)
- Format: `IMG`
- Campaign name: lowercase with dashes
- Date: `YYYY-MM-DD`

**Example:** `001_IMG_launch-batch_2026-01-15.md`

**Image naming:** `{batch}.{ad#}_IMG_{image#}`
- `001.1_IMG_01` — first image for Ad 1
- `001.1_IMG_02` — second image for Ad 1
- `001.2_IMG_01` — first image for Ad 2

---

## Two Sizes Per Image Prompt

Every prompt needs square + vertical:

1. **Full square prompt** (1920×1920) — complete with all details
2. **Resize prompt** (1080×1920) — short follow-up

**Standard resize prompt:**
```text
Now resize to 1080x1920 vertical for Reels/Stories. Do NOT change the image content, angle, or composition - only adjust the framing. Keep all text and important elements centered in the middle 45% of the frame vertically (between 25% and 70% from top) to stay within Facebook/Instagram safe zones.
```
