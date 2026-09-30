# Static Ad Output Template

Use this structure for campaign batch outputs.

## Contents

- **Part 1: Image Prompts** - Generate all images first (line 25)
- **Part 2: Ad Copy** - Copy for Ads Manager (line 70)
- **Naming Conventions** - File and image naming (line 174)
- **Format Pair: 4:5 + 9:16** - One composition per placement

---

```markdown
---
type: output
format: static-ad
date: YYYY-MM-DD
status: draft
platform: meta
---

# Campaign Batch {number} — {Campaign Name}

Generated: {date}
Target: {Offer name and price}
Destination: {CTA URL}

**Workflow:** Generate all images first (Part 1), then copy ad text (Part 2)

---

# PART 1: IMAGE PROMPTS

Generate all images first. Make a 4:5 for Feeds and a 9:16 for Stories and Reels, each composed for its placement.

---

## Ad 1: {Angle Name} — {batch#}.1

**Angle:** {description}
**Avatar:** {target persona}

---

### {batch#}.1_IMG_01 — {Descriptive Name}

**Prompt record:**
```yaml
prompt_key: "{descriptive-concept-id}.v1"
prompt_file: "pushes/{push}/prompts/{descriptive-concept-id}.md"
```

**Creative playbook (optional):**
```yaml
creative_playbook_id: "{native_problem_scene | specific_object_metaphor | proof_artifact | myth_vs_fact | with_without_transformation | crossed_out_problem_list | founder_pov | high_contrast_poster | simple_chart_comparison | testimonials_with_artifact | us_vs_them_split | simple_list_framework}"
creative_playbook:
  id: "{same as creative_playbook_id}"
  status: candidate
use_when:
  - "{why this playbook fits the source bite, offer, audience, and brand}"
default_avoid:
  - "{niche-specific cliché to avoid}"
useful_metaphors:
  - "{niche-specific metaphor}"
risky_metaphors:
  - "{niche-specific metaphor to avoid unless intentional}"
prompt_bias:
  - "{style or artifact bias for this niche}"
router_inputs:
  offer_type: "{offer type}"
  audience: "{audience}"
  source_bite_type: "{customer_language | offer | proof | research | founder_note | push_brief}"
  proof_available: false
  brand_style: "{visual style summary}"
  platform: facebook_feed
router_reason: "{why this playbook fits this candidate}"
playbook_fit:
  source_bite_fit: 1
  offer_fit: 1
  audience_fit: 1
  visual_distinctiveness: 1
  conversion_pattern_fit: 1
```

**Source bite:**
```yaml
source_file: research/customer-language.md
source_type: customer_language
extracted_phrase: "{phrase that makes this concept specific}"
insight: "{why this is sharper than generic chaos/order language}"
visual_translation: "{how the phrase becomes a one-second visual}"
```

**Genericness check:**
```yaml
could_fit_notion: false
could_fit_asana: false
could_fit_quickbooks: false
could_fit_generic_coaching_offer: false
could_fit_generic_productivity_app: false
could_fit_any_coaching_offer: false
could_fit_accounting_software: false
specific_to_this_offer: 4
reason: "{why this image could only come from this business context}"
```

**Avoidance strategy:**
```yaml
avoids:
  - stock-photo business imagery
  - clean desk productivity cliché
  - website hero composition
  - fake dashboard
  - generic SaaS gradient
intentionally_uses: []
reason: "{why the concept avoids generic ad imagery or why a soft-avoid pattern is intentional}"
```

**Feed (1440×1800, 4:5):**
```text
{Full prompt for the 4:5 feed image. Whole product in frame with margin; words on a flat area.}
```

**Vertical (1080×1920, 9:16):**
```text
{Full prompt for 9:16 vertical. Product, headline and key visual between 14% and 65% of the height. Fill top/bottom with the scene's own background, not a flat block.}
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

**Hook:** {complete first sentence, 44 chars or fewer}

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

**Folder:** `pushes/YYYY-MM-DD-static-ads-{campaign}/`
- Date: `YYYY-MM-DD`
- Type: `static-ads`
- Campaign name: lowercase with dashes (required)

**Batch file:** `static-ads-batch-{###}.md`
- Example: `static-ads-batch-001.md`

**Full path example:** `pushes/2026-01-15-static-ads-january-launch/static-ads-batch-001.md`

**Review log:** `review-log.md` (same folder)

**Image naming:** `{batch}.{ad#}_IMG_{image#}`
- `001.1_IMG_01` — first image for Ad 1
- `001.1_IMG_02` — second image for Ad 1
- `001.2_IMG_01` — first image for Ad 2

---

## Format Pair: 4:5 + 9:16

For Meta static creative, the default pair is **4:5** (Feeds, 1440×1800
minimum) and **9:16** (Stories and Reels, 1080×1920). Compose each for its
placement rather than cropping one from the other. Keep product, words and
disclosures between 14% and 65% of the 9:16 height. Full specs, composition
rules and the media gate: [ad-media-specs.md](ad-media-specs.md).

### Post-Processing (When Using An Image Provider)

If a provider generated the image:
- Record the raw output dimensions and format
- Resize to 1440×1800 (4:5) and 1080×1920 (9:16); never upscale product detail
- Convert PNG → JPEG, compress under 300KB
- Name files by ad name plus `-45` / `-916` once the ad is named ([naming-and-utm.md](naming-and-utm.md))
- See `image-generation-workflow.md` for full pipeline

---

## Image Index

When planning or generating images, create an `image-index.md` in the batch
folder. It can hold both planned concepts and generated assets. Link assets
back to concepts with `concept_id`.

Also write a local ignored review board/contact sheet under configured media
storage. The board answers: "Which playbook produced the best actual ad
candidate?" Commit only safe `image-index.md` records and distilled findings.

```markdown
# Image Index — {Campaign Name}

Docs checked: {date}
Provider: {provider or manual}
Model: {exact model or n/a}
Source files: {offer.md, audience.md, visual-style.md, ...}
Review board: {ignored local path or not written}
Estimated cost: ${estimate}
Actual cost: ${actual or unknown}
Post-processing: {dimensions, format, compression, crop rules}
Approval state: {draft/reviewed/approved}

## Concepts

| Concept ID | Playbook | Status | Audience State | Visual Job | Likely Click Reason | Review |
|------------|----------|--------|----------------|------------|---------------------|--------|
| clean-system-vs-ad-chaos | native_problem_scene | planned | Overwhelmed operator | Show clarity replacing ad chaos | Recognizes the source-bite problem in one second | accepted |

## Assets

| File | Angle | Style | Format | Prompt Key | Retries | Notes |
|------|-------|-------|--------|------------|---------|-------|
| 001_01_graphic_feed.jpg | Authority | Graphic | 4:5 | 001_01_graphic | 0 | Feed composition |
| 001_01_graphic_vertical.jpg | Authority | Graphic | 9:16 | 001_01_graphic | 0 | Full vertical |
| 001_02_lofi_feed.jpg | Social Proof | Lo-fi | 4:5 | 001_02_lofi | 1 | Manual review needed |
| ... | ... | ... | ... | ... | ... | ... |
```
