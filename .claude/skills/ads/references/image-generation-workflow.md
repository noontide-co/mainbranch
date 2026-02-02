# Image Generation Workflow

Nano Banana (Google Gemini) integration for generating actual ad images from Claude Code.

---

## Model — EXACT Name (DO NOT HALLUCINATE)

**The ONLY model to use:**

```
gemini-3-pro-image-preview
```

Copy-paste that string exactly. No other model is acceptable — not for drafts, not for testing, not for anything.

**NEVER use these (they will 404 or produce garbage):**
- ~~`gemini-2.0-flash-preview-image-generation`~~ — does not exist
- ~~`gemini-2.5-flash-image`~~ — exists but quality is not ad-grade. NEVER use.
- ~~`gemini-2.5-flash-preview-04-17`~~ — does not exist
- ~~`gemini-pro-image`~~ — incomplete name
- ~~`gemini-flash-image`~~ — incomplete name
- Any model with "flash" in the name — NEVER for image generation

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

## Post-Processing Pipeline (MANDATORY — Never Skip)

**Raw Gemini output is PNG at arbitrary sizes (often 768x1376 or 1024x1024). This is NOT the final deliverable.** You MUST post-process every image immediately after generation. Never save raw PNGs as final output.

### Steps (run on EVERY generated image)

1. **Resize** to target dimensions (LANCZOS resampling)
2. **Convert** PNG → JPEG
3. **Compress** to under 300KB (quality stepping: 85 → 75 → 65 → 55 → 45)
4. **Delete the raw PNG** after both formats are saved
5. **Verify** final JPEG is under 300KB and at correct dimensions

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

## Text-on-Image: Always Post-Process

**NEVER ask Gemini to render text on the image.** Gemini cannot reliably render text longer than ~5 words. All text goes on via Pillow post-processing.

### Workflow

1. **Gemini generates background-only images** — no text in the prompt
2. **Pillow composites text onto the background** — white bold text, drop shadow, centered

### Text Positioning (Critical)

On 9:16 vertical images, the bottom ~25-30% is covered by UI overlays (caption, CTA button, likes bar). Text must sit **above true center** to stay in the safe zone.

```
┌──────────────────┐
│   TOP UI (10%)   │  ← progress bar, account icon
│                  │
│                  │
│   ██ TEXT ██     │  ← Place text at 35-40% from top
│                  │     (above geometric center)
│                  │
│                  │
│  BOTTOM UI (25%) │  ← caption, CTA, likes — AVOID
└──────────────────┘
```

**Pillow positioning:** Set text Y coordinate to `int(height * 0.38)` (38% from top), NOT `height // 2` (50%). This keeps text safely above the bottom UI zone while looking visually centered within the usable area.

### Prompt Pattern for Text-Free Backgrounds

```
"Generate a [style] background image for a Facebook ad.
9:16 aspect ratio (1080x1920px).
NO TEXT on the image. This is a background for text overlay.
Leave generous clean space in the center-upper area for white text.
[scene/mood/brand directives]"
```

---

## Batch Generation Flow

**Order: Copy → Compliance Review + Image Generation (parallel)**

Compliance review and image generation run in PARALLEL after copy is saved, not sequentially. The post-generation pipeline (see SKILL.md → Automatic Post-Generation Pipeline) orchestrates this.

For a typical ad campaign with 5 angles (15 images):

```
1. Copy saved to output file
2. Git commit pre-review (preserves original)
3. Main conversation writes prompts.json to disk (keyed by target filename)
4. PARALLEL (all agents spawned in a single message):
   a. Compliance agents (5-6 lenses, read-only) → findings report
   b. Image agents (1 per image, if user approved):
      - Each agent reads its prompt(s) from prompts.json
      - Reads visual-style.md for brand context
      - Generates 9:16 image via API
      - Post-processes: resize, JPEG compress, center-crop for 1:1
      - Verifies file(s) exist on disk
      - Returns: file path(s) + status (success/fail) + cost
5. Synthesize: collect all image agent results, retry any failures,
   apply P2/P3 fixes, surface P1s, write review-log.md + image-index.md
6. Git commit post-review (user confirms)
```

---

## Parallel Agent Spawning

Image generation uses **one subagent per image** (or per 2-3 images for large batches). This is faster than sequential generation and aligns with how Claude Code handles independent tasks.

### How It Works

1. **Main conversation prepares `prompts.json`** before spawning any agents. Each key is the target filename, each value contains the prompt text, style (on-brand/freestyle), and brand context.

2. **All agents spawn in a single message** — compliance agents AND image agents together. Use `subagent_type: "general-purpose"` for all.

3. **Each image agent:**
   - Reads its assigned prompt(s) from `prompts.json` (by filename key)
   - Sources the API key: `source ~/.config/vip/env.sh`
   - Calls Gemini via Python SDK (single image per API call)
   - Post-processes immediately (resize, PNG to JPEG, compress under 300KB)
   - Verifies the final JPEG exists on disk
   - Returns: `{ path: "images/001_01_graphic_vertical.jpg", status: "success", cost: 0.05 }` (or `status: "fail"` with error message)

4. **Main conversation collects results** from all image agents, retries any failures with fresh single-image agents.

### Batching Strategy

| Image Count | Strategy | Agents Spawned |
|-------------|----------|----------------|
| 1-8 | One agent per image | N agents |
| 9-15 | One agent per image | N agents |
| 16-30 | Batch 2-3 per agent | ~10-15 agents |

### Rate Limiting

Each agent adds a `time.sleep(2)` before its first API call. Natural stagger from agent startup timing provides additional spacing. If an agent receives a 429 (rate limit), it retries once after a 5-second sleep. If the retry also fails, it returns `status: "fail"` and main conversation handles the retry.

### Agent Prompt Template

```
You are an image generation agent. Generate the assigned image(s) and return results.

Environment setup:
  source ~/.config/vip/env.sh

Your assigned image(s) from prompts.json at {output_dir}/prompts.json:
  Key(s): {filename_key(s)}

For EACH assigned image:
1. Read the prompt from prompts.json
2. Run Python: generate via gemini-3-pro-image-preview, save raw PNG
3. Run Python: post-process (resize to target dims, JPEG compress under 300KB, delete raw PNG)
4. Verify final JPEG exists: ls {output_dir}/images/{filename}
5. Return the file path and status

If rate-limited (429): sleep 5 seconds, retry once.
If retry fails: return status "fail" with error message. Do NOT keep retrying.
```

### Failure Handling

- Agent returns `status: "fail"` with error details
- Main conversation spawns a new single-image agent for just that prompt
- One retry per image. If second attempt fails, log the failure in `image-index.md` and note which prompts need manual generation.

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
