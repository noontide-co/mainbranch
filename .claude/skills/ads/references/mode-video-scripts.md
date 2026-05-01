# Mode: Video Scripts

Create diverse spoken-word scripts for camera delivery.

---

## 6-Step Process

1. **Core Outcome:** Single result every buyer achieves
2. **Avatars:** 3-4 buyer personas with situation, frustration, desires
3. **Angles Per Avatar:** Map angles from project context
4. **Generate Ads:** 15-30 scripts across all avatars
5. **Optimize for Spoken:** ~5th grade reading level, contractions, fragments
6. Ask for campaign name (required)

Each batch file should start with:
```yaml
---
type: output
format: video-ad-script
date: YYYY-MM-DD
status: draft
platform: meta
---
```

7. **Save Output:** `outputs/YYYY-MM-DD-video-ads-[offer]-{campaign}/video-ads-batch-001.md` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode)
8. Tell user: "Video scripts saved. Running automatic post-generation pipeline..."
9. Run the **Automatic Post-Generation Pipeline** (see SKILL.md). This handles git commit and compliance review automatically. (No image generation for video scripts.)

---

## Script Structure

**Hook** (1-2 sentences): Lead with pain, desire, or belief. Create curiosity.

**Body** (4-8 sentences): Why problem exists. Position offer. Include proof.

**CTA** (2-3 sentences): Clear instruction. What happens after click.

**CRITICAL**: Each ad = fundamentally different reason to buy.

---

## Spoken Delivery Optimization

- Contractions: you're, don't, can't, won't
- Fragments: "Not theory. Patterns."
- Simple words: "use" not "utilize"

See [video-templates-hooks.md](video-templates-hooks.md) for templates and hook bank.
