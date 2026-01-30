# Image Generation Workflow

Nano Banana (Google Gemini) integration for generating actual ad images from Claude Code.

---

## Model Selection

**Use `gemini-3-pro-image-preview` ONLY.**

Pro produces significantly better results for ad creative. Flash is not acceptable for ad-grade output. This applies to all image generation — drafts, finals, iterations.

---

## Detection

At triage, check if Nano Banana is available:

```bash
source ~/.config/vip/env.sh 2>/dev/null
python3 -c "from google import genai; print('OK')" 2>/dev/null
```

**If available:** Offer Batch 4 (image generation) after copy + compliance.
**If unavailable:** Output text prompts only. Note: "Image prompts saved. Paste into Gemini or another image tool to generate."

Also check `.vip/config.yaml` → `tools.nano_banana.status` for cached detection result.

---

## Generation via Python SDK

The `google-genai` Python package is the generation interface. MCP servers are an alternative but the SDK provides more control.

```python
import os, base64
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

response = client.models.generate_content(
    model='gemini-3-pro-image-preview',
    contents=[prompt_text],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE']
    )
)

# Extract image from response
for part in response.candidates[0].content.parts:
    if part.inline_data is not None:
        data = part.inline_data.data
        image_bytes = data if isinstance(data, bytes) else base64.b64decode(data)
        with open('output.png', 'wb') as f:
            f.write(image_bytes)
```

---

## Post-Processing Pipeline

Raw Gemini output is PNG at 1024x1024. Ads need JPEG at specific sizes.

### Steps

1. **Resize** to target dimensions (LANCZOS resampling)
2. **Convert** PNG → JPEG
3. **Compress** to under 300KB (quality stepping: 85 → 75 → 65 → 55 → 45)
4. **Strip metadata** (no EXIF data in ad images)

### Target Dimensions

| Format | Dimensions | Use |
|--------|-----------|-----|
| 1:1 (square) | 1920×1920 | Facebook feed, Instagram feed |
| 9:16 (vertical) | 1080×1920 | Stories, Reels, full-screen mobile |

### Python Post-Processing

```python
from PIL import Image
import os

def post_process(input_path, output_path, width, height, max_kb=300):
    img = Image.open(input_path).convert('RGB')
    img = img.resize((width, height), Image.LANCZOS)
    for quality in [85, 75, 65, 55, 45]:
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        if os.path.getsize(output_path) < max_kb * 1024:
            return quality
    return 45  # best effort
```

### No Gemini Watermark from API

API output does NOT include the Gemini watermark visible in the web UI. SynthID (invisible digital watermark) is embedded but does not affect visual quality.

---

## Format Pair: 1:1 + 9:16

Facebook Ads Manager offers exactly two image uploads per ad: **1:1 (square)** and **9:16 (vertical)**. There is no 4:5 option.

### Design Strategy

Design the **9:16 vertical first** with all critical content (hook text, product, key visual) in the **center 1:1 safe zone**:

```
┌──────────────┐
│  TOP MARGIN  │  ← UI overlays (progress bar, account icon)
│              │
│ ┌──────────┐ │
│ │          │ │
│ │  CENTER  │ │  ← All critical content HERE
│ │  1:1     │ │  ← This extracts as the square version
│ │  ZONE    │ │
│ │          │ │
│ └──────────┘ │
│              │
│ BOTTOM MARGIN│  ← UI overlays (caption, CTA, likes)
└──────────────┘
```

**One design → two uploads.** The 9:16 is the full creative. The 1:1 is a center crop. Context or atmosphere fills the top/bottom margins.

### Prompt Strategy for Format Pair

For each concept, generate ONE 9:16 image. Prompt should specify:
- Critical content centered vertically
- Atmospheric/contextual elements at top and bottom margins
- Aspect ratio: `"aspect_ratio": "9:16"` or `"resolution": "1080x1920px"`

Then center-crop to 1:1 in post-processing.

---

## Smart Mix Recommendation

Based on `reference/brand/visual-style.md` depth:

| visual-style.md State | Mix |
|----------------------|-----|
| Rich (80+ lines, hex codes, mood, prompts) | 60% on-brand, 40% freestyle |
| Adequate (20-80 lines) | 50/50 |
| Stub (< 20 lines) | 30% on-brand, 70% freestyle |
| Missing | 100% freestyle. Offer to create. |

**On-brand images** use color palette, typography direction, mood, and prompt fragments from visual-style.md.

**Freestyle images** ignore brand constraints. Pattern interrupts, meme-style, lo-fi, native/ugly ads — these intentionally break from brand to stop scrolling.

---

## Cost Estimation

Before generating, show cost estimate and get approval:

```
Image Generation Estimate:
  5 angles × 3 styles × 1 format = 15 images
  Model: gemini-3-pro-image-preview @ ~$0.05/image
  Estimated cost: ~$0.75

  Proceed? (y/n)
```

Actual cost depends on prompt complexity and retries.

---

## Text-on-Image Guidance

### Reliable Range

Gemini Pro handles short text (3-5 words) reasonably well in images. Beyond ~25 characters, text quality degrades.

### For One-Liners

One-liners often exceed 25 characters. Two approaches:

1. **Test in-image rendering:** Include the one-liner text in the prompt. If Gemini renders it clearly, use it.
2. **Post-processing overlay (recommended):** Generate the background/visual without text, then overlay text using Pillow or external tools. This is the community consensus from X/Twitter practitioners.

### Prompt Pattern for Text-Free Backgrounds

```
"Generate a [style] background image for a Facebook ad.
No text on the image. Leave clean space in the center for text overlay.
[brand/style directives]"
```

---

## Batch Generation Flow

**Order: Copy → Compliance Review + Image Generation (parallel)**

Compliance review and image generation run in PARALLEL after copy is saved, not sequentially. The post-generation pipeline (see SKILL.md → Automatic Post-Generation Pipeline) orchestrates this.

For a typical ad campaign with 5 angles:

```
1. Copy saved to output file
2. Git commit pre-review (preserves original)
3. PARALLEL:
   a. Compliance agents (5-6 lenses, read-only) → findings report
   b. Image agent generates (if user approved):
      - Read visual-style.md for brand context
      - Determine smart mix (on-brand vs freestyle)
      - For each concept:
        - Build JSON-structured prompt from template + brand data
        - Generate 9:16 image via API
        - Post-process: resize, JPEG compress, center-crop for 1:1
        - Save to output folder
      - Return cost summary + file paths
4. Synthesize: apply P2/P3 fixes, surface P1s, write review-log.md + image-index.md
5. Git commit post-review (user confirms)
```

---

## Output Structure

```
outputs/YYYY-MM-DD-static-ads-{campaign}/
├── static-ads-batch-001.md        ← Copy (Batch 1)
├── review-log.md                  ← Compliance (Batch 2)
├── images/
│   ├── 001_01_graphic_square.jpg
│   ├── 001_01_graphic_vertical.jpg
│   ├── 001_02_lofi_square.jpg
│   ├── 001_02_lofi_vertical.jpg
│   └── ...
└── image-index.md                 ← Maps images to concepts
```

### Image Naming Convention

```
{batch}_{sequence}_{style}_{format}.jpg

Examples:
001_01_graphic_square.jpg
001_01_graphic_vertical.jpg
001_02_lofi_square.jpg
001_03_interrupt_square.jpg
001_04_oneliner_square.jpg
```

---

## Fallback (No Nano Banana)

If Nano Banana is not configured:

1. Generate text prompts only (structured JSON format)
2. Save prompts to the output batch file
3. Note: "Image prompts saved as text. To generate images, paste these into Google AI Studio or configure Nano Banana (`/help nano banana setup`)."

---

*See also: image-prompt-templates.md for template library, preflight-algorithm.md for readiness scoring.*
