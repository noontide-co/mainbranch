# Image Generation Workflow

Optional image-generation workflow for producing ad images from approved
prompts and provider access. The durable product rail is the prompt, source
context, output index, approval state, and safe logical media reference.
Provider support is run-scoped until `mb` owns detection and smoke evidence.

Prompt-only/manual mode is a fallback, not the target. The product direction is
fixture-safe generation/editing plus strong artifact records and storage
boundaries.

---

## Provider Choice

Use the provider and model verified for this run. Do not hard-code a private
environment file, assume a provider is configured, or claim Main Branch supports
image generation because this reference exists.

Current provider notes checked 2026-05-13 against the accepted creative media
generation decision:
`decisions/2026-05-13-creative-media-generation-rails.md`.

| Provider | Model family | Use |
| --- | --- | --- |
| OpenAI Image API / Responses API | `gpt-image-2` | First readiness target for fixture-safe static image generation/editing. Use only when configured for the run and record the exact model/snapshot. |
| Google Gemini API | Nano Banana image-model family | Candidate comparison rail for future work. Do not treat it as proven ad-grade output until a smoke/test run records the current exact model ID, prompt, output, review notes, and final asset quality. |
| BFL FLUX.2 / ComfyUI | FLUX.2 family | Candidate local/private or heavy-reference rail after the OpenAI rail and metadata contract are stable. |
| Manual provider use | `manual` | Safe fallback when no approved provider is configured. Save prompts and asset records for the operator to use manually. |

If model names or pricing matter to the recommendation, check the provider's
current docs before generating and record the docs-checked date in
`image-index.md`.

Do not hard-code exact candidate-provider model IDs from memory. OpenAI
`gpt-image-2` is the first readiness target; other provider/model IDs must be
checked against current primary docs and pinned per run.

---

## Detection

At triage, check whether an approved image provider is available. Use
`mb status --json --peek` / `mb connect doctor --json` first for provider
readiness when available. Those commands may not prove a media API key exists;
only check environment variables when the selected mode actually needs image
generation.

```bash
python3 -c "from openai import OpenAI; print('openai OK')" 2>/dev/null
python3 -c "from google import genai; print('google-genai OK')" 2>/dev/null
```

If a provider is available, show the provider/model, estimated cost, output
path, and required approval before generating. If unavailable, output text
prompts only:

> "Image prompts saved. Paste them into your chosen image tool, or configure an
> approved provider before asking Main Branch to generate files directly."

---

## Media Storage Boundary

Commit the push-local `image-index.md` record by default, not generated image
binaries. Generated or edited media should resolve through configured storage:

- local gitignored media cache, such as `.mb/media/`;
- private operator media folder, such as `~/MainBranchMedia/<business>/`;
- external media folder;
- site repo/public folder only after explicit approval.

Committed records should use safe logical references such as
`mb-media://pushes/2026-05-ad-test/images/hero-001.png`, not private absolute
paths.

Reference images should carry roles:

```yaml
references:
  - id: logo
    role: logo
    path: mb-media://brand/logo.png
    safe_to_share: false
  - id: product
    role: product_photo
    path: mb-media://pushes/2026-05-ad-test/references/product.webp
    safe_to_share: false
```

---

## Generate / Edit / Mask Decision Tree

- No image input: generate.
- Image input plus broad natural-language change: edit.
- Image input plus exact region change: mask edit.
- Many prompts, many variants, or repeated reference combinations: batch later,
  after the single-image rail is stable.

Recommended implementation shape:

```bash
mb image generate --prompt "..." --out mb-media://pushes/2026-05-ad-test/images/hero-001.png
mb image edit --prompt "..." --ref-image mb-media://brand/logo.png --out mb-media://pushes/2026-05-ad-test/images/hero-002.png
mb image edit --prompt "..." --ref-image mb-media://pushes/2026-05-ad-test/references/product.webp --mask mb-media://pushes/2026-05-ad-test/references/mask.png --out mb-media://pushes/2026-05-ad-test/images/hero-003.png
```

This shape is a decision recommendation, not a shipped command claim.

---

## Generation via Python SDK

The OpenAI Python SDK is the first implementation pattern to smoke for
MAIN-362. MCP servers, runtime-native image tools, or another SDK can be used
only when they are configured for the run and the artifact metadata records the
provider/model.

```python
import base64
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.images.generate(
    model=os.environ.get("MB_IMAGE_MODEL", "gpt-image-2"),
    prompt=prompt_text,
    size=os.environ.get("MB_IMAGE_SIZE", "1024x1536"),
    quality=os.environ.get("MB_IMAGE_QUALITY", "medium"),
)

image_bytes = base64.b64decode(response.data[0].b64_json)
with open("output.png", "wb") as f:
    f.write(image_bytes)
```

---

## Post-Processing Pipeline (MANDATORY — Never Skip)

**Raw provider output is not automatically the final deliverable.** Post-process
every ad image immediately after generation. Never save raw provider files as
final output unless the operator explicitly approves that exact file as the
final asset.

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

Record provider watermarking or provenance metadata when known. Do not promise
that all providers expose the same provenance, watermarking, or C2PA behavior.

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
  Provider/model: OpenAI / gpt-image-2
  Docs checked: 2026-05-13
  Estimated cost: $X from current provider pricing
  Storage: mb-media://pushes/2026-05-ad-test/images/
  Record: pushes/2026-05-ad-test/image-index.md

  Proceed? (y/n)
```

Actual cost depends on prompt complexity and retries.

---

## Text-on-Image: Prefer Deterministic Final Overlays

GPT Image 2 is the first rail to smoke partly because current validation
points to strong text rendering. Still, final paid creative often needs exact
copy, exact safe-zone placement, and predictable export sizes. When exact text
matters, generate the background or composition and apply final text with a
deterministic post-processing step such as Pillow.

### Workflow

1. **Provider generates the background or composition**
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
   - Verifies the final JPEG exists in configured media storage
   - Returns: `{ output_reference: "mb-media://pushes/2026-05-ad-test/images/001_01_graphic_vertical.jpg", status: "success", provider: "openai", model: "gpt-image-2", cost_estimate: "$X from current provider pricing" }` (or `status: "fail"` with error message)

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
2. Resolve the assigned `mb-media://...` reference to configured media storage
3. Run Python: generate via the selected provider/model, save raw PNG in configured media storage
4. Run Python: post-process (resize to target dims, JPEG compress under 300KB, delete raw PNG)
5. Verify final JPEG exists in configured media storage and return the safe logical reference
6. Return the logical media reference, provider, model, cost, and status

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
└── image-index.md                 ← Maps prompts, provider metadata, review
                                      state, and mb-media:// references
```

`image-index.md` stores logical media references that resolve to configured
storage, not generated binaries in the push folder:

```yaml
assets:
  - asset_id: 001_01_graphic_vertical
    output_reference: mb-media://pushes/YYYY-MM-DD-static-ads-{campaign}/images/001_01_graphic_vertical.jpg
    storage_backend: mb-media
    committed_binary: false
  - asset_id: 001_02_lofi_vertical
    output_reference: mb-media://pushes/YYYY-MM-DD-static-ads-{campaign}/images/001_02_lofi_vertical.jpg
    storage_backend: mb-media
    committed_binary: false
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
- safe logical media references;
- reference image roles and safe logical reference paths when used;
- storage backend label;
- approval state.

## Fallback (No Provider)

If no image provider is configured:

1. Generate text prompts only (structured JSON format)
2. Save prompts and the intended logical media references to `image-index.md`
3. Note: "Image prompts saved as text. To generate images, paste these into your chosen image tool or configure an approved provider for a future run."

---

*See also: image-prompt-templates.md for template library, preflight-algorithm.md for readiness scoring.*
