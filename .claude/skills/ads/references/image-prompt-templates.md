# Image Prompt Templates

Four template types for ad image generation. Each template outputs a JSON-structured prompt with placeholders filled from business reference files.

---

## Template Architecture

All templates follow the same JSON structure. Placeholders are filled at generation time from `visual-style.md`, `offer.md`, `audience.md`, and the copy concept.

```json
{
  "campaign_metadata": {
    "brand": "{{brand_name}}",
    "campaign": "{{campaign_name}}",
    "angle": "{{angle_name}}",
    "style": "{{template_type}}"
  },
  "image_spec": {
    "aspect_ratio": "9:16",
    "resolution": "1080x1920px",
    "format": "photograph | illustration | graphic design"
  },
  "scene": "{{scene_description}}",
  "color_grading": {
    "overall_tone": "{{mood}}",
    "primary_color": "{{primary_hex}}",
    "secondary_color": "{{secondary_hex}}",
    "temperature": "warm | cool | neutral",
    "contrast": "high | medium | low",
    "saturation": "vivid | muted | desaturated"
  },
  "composition": {
    "critical_content_zone": "center 1:1 area",
    "text_overlay_space": "{{where to leave space for text}}",
    "key_elements": ["{{element_1}}", "{{element_2}}"]
  },
  "style_directives": "{{prompt_fragments_from_visual_style}}"
}
```

### Placeholder Sources

| Placeholder | Source |
|-------------|--------|
| `{{brand_name}}` | `reference/core/offer.md` → business name |
| `{{campaign_name}}` | User input at triage |
| `{{angle_name}}` | Selected angle from Batch 1 |
| `{{template_type}}` | graphic, lofi, interrupt, or textoverlay |
| `{{mood}}` | `reference/brand/visual-style.md` → mood descriptors |
| `{{primary_hex}}` | `reference/brand/visual-style.md` → primary color |
| `{{secondary_hex}}` | `reference/brand/visual-style.md` → secondary/accent color |
| `{{prompt_fragments}}` | `reference/brand/visual-style.md` → AI image prompt fragments |
| `{{scene_description}}` | Generated from concept + audience context |

**If visual-style.md is missing:** Omit color_grading and style_directives sections. Use freestyle defaults.

---

## Template 1: Graphic

Typography-focused, clean design. Frameworks, lists, bold statements.

**Use for:** Authority angles, mechanism breakdowns, list-style ads.

```
Scene: Clean graphic design with bold typography on a solid or gradient background.
Central element: {{headline_or_framework}} displayed as large, readable text.
Style: Modern editorial design, magazine-quality layout.
Background: {{primary_color}} to {{secondary_color}} gradient or solid.
Text treatment: High contrast, sans-serif feel, professional.
Composition: Text centered in the 1:1 safe zone. Supporting graphic elements
in top and bottom margins. No clutter — let the text breathe.
Color grading: {{mood}}, {{temperature}}, high contrast.
{{style_directives}}
```

**Note:** For graphic templates, text IS the image. Use Gemini's text rendering for short headlines (under 25 characters). For longer text, generate the background and note overlay needed.

---

## Template 2: Lo-Fi

UGC-style, authentic, raw. Screenshots, casual photos, phone-quality aesthetic.

**Use for:** Social proof angles, testimonial angles, "real person" positioning.

```
Scene: Casual, authentic-looking image as if taken on a phone.
Style: Lo-fi aesthetic, slightly imperfect, natural lighting.
No professional studio look. Think: someone shared this on social media.
Subject: {{subject_description}} in a natural, everyday setting.
Color grading: Slightly warm, natural tones. NOT filtered or over-processed.
If brand colors apply: subtle presence only (clothing, background element).
Composition: Subject in center 1:1 zone. Context fills margins.
Leave clean space for text overlay: {{text_space_location}}.
Mood: Approachable, relatable, trustworthy.
```

**Key:** Lo-fi intentionally breaks from brand polish. This is a freestyle style even for on-brand campaigns. The "imperfection" IS the strategy.

---

## Template 3: Interrupt

Pattern interrupt, scroll-stopping. Bold colors, unusual compositions, provocative visuals.

**Use for:** Contrarian angles, curiosity gap, reframe angles.

```
Scene: Visually striking, unexpected image that stops mid-scroll.
Style: Bold, high-contrast, intentionally attention-grabbing.
NOT polished corporate. Think: billboard art meets meme culture.
Key element: {{interrupt_element}} — the thing that makes someone pause.
Color grading: High saturation, dramatic contrast.
Colors: {{accent_color}} dominant, dark background for maximum pop.
Composition: Key element fills the 1:1 center zone aggressively.
Minimal negative space. The visual should feel almost too close.
Text overlay space: Small area — interrupt images rely on visual, not text.
Mood: Provocative, surprising, impossible to ignore.
```

**Key:** Interrupts intentionally clash with the feed. Native/ugly beats polished by ~40% in Meta testing. This style should feel different from everything else in the campaign.

---

## Template 4: Text Overlay

Background-only image designed for text overlay. The copy text is added in post-processing.

**Use for:** Creative variation copy lines (from `/ads` hook library output).

```
Scene: {{scene_type}} background image for a Facebook ad.
NO TEXT on the image. This image will have text overlaid in post-processing.
Leave generous clean space in the center for a single line of large text.
Style: {{background_style}} — supports readability of overlaid white or light text.
Color grading: {{mood}}, darker tones preferred for text contrast.
Primary background color: {{primary_color}} or complementary dark tone.
Composition: Simple, uncluttered. The background supports the text, not competes.
Center 1:1 zone should be especially clean — this is where the text overlay will go.
Subtle visual interest in margins (texture, gradient, atmospheric elements).
```

### Scene Types for Text Overlays

| Scene Type | Description | Best For |
|------------|-------------|----------|
| `abstract` | Color gradients, geometric shapes, textures | Brand-forward, professional |
| `atmospheric` | Moody lighting, depth, bokeh | Emotional angles, transformation |
| `lifestyle` | Blurred/out-of-focus lifestyle context | Aspirational, identity angles |
| `dark_solid` | Near-solid dark background with subtle texture | Maximum text readability |
| `split` | Two-tone or split composition | Comparison, before/after framing |

---

## Vibe Preservation for Variants

When generating multiple images for the same campaign, use the vibe preservation pattern from X/Twitter practitioners:

> "Generate a new image with SIGNIFICANTLY different composition, objects, and color palette compared to the previous image. CRITICAL: Strictly preserve the original 'vibe', 'aesthetic', and 'mood'."

This produces diverse-but-cohesive ad sets that satisfy Andromeda's need for genuine visual variety while maintaining campaign coherence.

---

## Brand vs Freestyle Selection

For each concept in the batch, assign brand or freestyle based on the smart mix:

```
5 concepts, 60/40 mix:
  Concept 1 (authority)    → on-brand graphic
  Concept 2 (social proof) → freestyle lo-fi
  Concept 3 (mechanism)    → on-brand graphic
  Concept 4 (curiosity)    → freestyle interrupt
  Concept 5 (pain agitate) → on-brand text overlay
```

**On-brand:** Fill all color_grading and style_directives from visual-style.md.
**Freestyle:** Omit brand-specific directives. Let the template style + concept drive the visual.

---

## Reference Image Support (Future)

The JSON structure supports a `reference_images` array for uploading brand photos, product shots, or style references:

```json
{
  "reference_images": [
    { "type": "PRODUCT", "description": "Main product photo" },
    { "type": "STYLE", "description": "Brand style reference" }
  ]
}
```

This is not yet implemented in the API workflow but the template structure supports it for when reference image uploads become available.

---

*See also: image-generation-workflow.md for API integration, static-output-template.md for batch output format.*
