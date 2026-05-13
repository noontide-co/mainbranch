# Image Generation Workflow

Optional image-generation workflow for producing ad images from approved
prompts and provider access. The durable product rail is the prompt, source
context, output index, approval state, and final asset path. Provider support
is run-scoped until `mb` owns detection and smoke evidence.

---

## Provider Choice

Use the provider and model verified for this run. Do not hard-code a private
environment file, assume a provider is configured, or claim Main Branch supports
image generation because this reference exists.

Current provider notes checked 2026-05-13 against Google's official Gemini
image generation docs:
https://ai.google.dev/gemini-api/docs/image-generation

| Provider | Model family | Use |
| --- | --- | --- |
| Google Gemini API | `gemini-3-pro-image-preview` | Professional/high-fidelity image generation when quality matters more than speed. |
| Google Gemini API | `gemini-2.5-flash-image` | Candidate speed/cost rail for draft or iteration use only. Do not treat it as proven ad-grade output until a smoke/test run records provider, model, prompt, output, review notes, and final asset quality. |
| OpenAI Image API / Responses API | GPT Image models | Candidate alternate provider for generation and editing. Use only when configured for the run and record the exact model. |

If model names or pricing matter to the recommendation, check the provider's
current docs before generating and record the docs-checked date in
`image-index.md`.

---

## Detection

At triage, check whether an approved image provider is available. Use
`mb status --json --peek` / `mb connect doctor --json` first for provider
readiness when available. Those commands may not prove a media API key exists;
only check environment variables when the selected mode actually needs image
generation.

```bash
python3 -c "from google import genai; print('google-genai OK')" 2>/dev/null
python3 -c "from openai import OpenAI; print('openai OK')" 2>/dev/null
```

If a provider is available, show the provider/model, estimated cost, output
path, and required approval before generating. If unavailable, output text
prompts only:

> "Image prompts saved. Paste them into your chosen image tool, or configure an
> approved provider before asking Main Branch to generate files directly."

---

## Generation via Python SDK

The `google-genai` Python package is one supported implementation pattern when
Google is selected for the run. MCP servers or another SDK can be used only
when they are configured and the artifact metadata records the provider/model.

```python
import os, base64
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

response = client.models.generate_content(
    model=os.environ.get("MB_IMAGE_MODEL", "gemini-3-pro-image-preview"),
    contents=[prompt_text],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"]
    )
)

# Extract image from response
for part in response.candidates[0].content.parts:
    if part.inline_data is not None:
        data = part.inline_data.data
        image_bytes = data if isinstance(data, bytes) else base64.b64decode(data)
        with open("output.png", "wb") as f:
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

### Provider Watermarking

Record provider watermarking or provenance metadata when known. For Gemini,
current docs say generated images include SynthID watermarking. Do not promise
that other providers have the same behavior.

---

## Format Pair: 1:1 + 9:16

For Meta-first static creative, plan the default pair as **1:1 (square)** and
**9:16 (vertical)**. Treat placement specs as provider-specific; check current
platform requirements before launch.

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

Based on `core/brand/visual-style.md` depth:

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
  Provider/model: Google Gemini / gemini-3-pro-image-preview
  Docs checked: 2026-05-13
  Estimated cost: $X from current provider pricing

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
2. Approved checkpoint pre-review (preserves original)
3. Main conversation writes prompts.json to disk (keyed by target filename)
4. PARALLEL (all agents spawned in a single message):
   a. Compliance agents (5-6 lenses, read-only) → findings report
   b. Image agents (1 per image, if user approved and provider configured):
      - Each agent reads its prompt(s) from prompts.json
      - Reads visual-style.md for brand context
      - Generates 9:16 image via the selected provider/model
      - Post-processes: resize, JPEG compress, center-crop for 1:1
      - Verifies file(s) exist on disk
      - Returns: file path(s) + status (success/fail) + cost
5. Synthesize: collect all image agent results, retry any failures,
   surface P1s, show the P2/P3 proposed diff, apply copy fixes only after
   explicit approval, write review-log.md if approved, and write image-index.md
6. Approved checkpoint post-review (user confirms)
```

---

## Parallel Agent Spawning

Image generation uses **one subagent per image** (or per 2-3 images for large batches). This is faster than sequential generation and aligns with how Claude Code handles independent tasks.

### How It Works

1. **Main conversation prepares `prompts.json`** before spawning any agents. Each key is the target filename, each value contains the prompt text, style (on-brand/freestyle), and brand context.

2. **All agents spawn in a single message** — compliance agents AND image agents together. Use `subagent_type: "general-purpose"` for all.

3. **Each image agent:**
   - Reads its assigned prompt(s) from `prompts.json` (by filename key)
   - Uses the already-configured provider environment for this run
   - Calls the selected provider/model (single image per API call)
   - Post-processes immediately (resize, PNG to JPEG, compress under 300KB)
   - Verifies the final JPEG exists on disk
   - Returns: `{ path: "images/001_01_graphic_vertical.jpg", status: "success", provider: "google", model: "gemini-3-pro-image-preview", cost: 0.05 }` (or `status: "fail"` with error message)

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

Provider setup:
  Use the provider/model selected by the main conversation.
  Do not ask the operator to paste API keys into chat.

Your assigned image(s) from prompts.json at {output_dir}/prompts.json:
  Key(s): {filename_key(s)}

For EACH assigned image:
1. Read the prompt from prompts.json
2. Run Python: generate via the selected provider/model, save raw PNG
3. Run Python: post-process (resize to target dims, JPEG compress under 300KB, delete raw PNG)
4. Verify final JPEG exists: ls {output_dir}/images/{filename}
5. Return the file path, provider, model, cost, and status

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
pushes/YYYY-MM-DD-static-ads-{campaign}/
├── static-ads-batch-001.md        ← Copy (Batch 1)
├── proposed-compliance-fixes.json ← Compliance proposals
├── review-log.md                  ← Compliance changes after approval
├── images/
│   ├── 001_01_graphic_square.jpg
│   ├── 001_01_graphic_vertical.jpg
│   ├── 001_02_lofi_square.jpg
│   ├── 001_02_lofi_vertical.jpg
│   └── ...
└── image-index.md                 ← Maps prompts, provider metadata, and files
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

## Image Index Metadata

Every generated image batch gets an `image-index.md` with:

- provider and model, or `manual`;
- docs-checked date;
- source files read;
- prompt text or prompt file key;
- output dimensions and format;
- post-processing settings;
- cost estimate and actual cost when known;
- failure/retry count;
- final file paths;
- approval state.

## Fallback (No Provider)

If no image provider is configured:

1. Generate text prompts only (structured JSON format)
2. Save prompts to the output batch file
3. Note: "Image prompts saved as text. To generate images, paste these into your chosen image tool or configure an approved provider for a future run."

---

*See also: image-prompt-templates.md for template library, preflight-algorithm.md for readiness scoring.*
