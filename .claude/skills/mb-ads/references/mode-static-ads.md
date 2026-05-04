# Mode: Static Ads

Create campaign batches with image prompts + ad copy.

---

## Campaign Structure

Each batch = 5-6 angles. Each angle = 3 image creatives (graphic, lo-fi, interrupt).

```
Campaign Batch 001
├── Angle 1: 001_01 (graphic), 001_02 (lo-fi), 001_03 (interrupt)
├── Angle 2: 001_04, 001_05, 001_06
└── [etc.]
```

---

## Hook Rules (Non-Negotiable)

**Hook = 123-135 characters** (visible before "See more" on Facebook).

- No questions (binary "no" response)
- No "you/your" in first 3 lines
- No emojis
- Pack customer language into the hook

**Hook Formulas:**
1. **Transformation:** "How [Resonance] go from [Pain] to [Benefit] using [Approach]"
2. **Even Without:** "Here's how even [Resonance] (without [Challenge]) are [Benefit]"
3. **Eliminates:** "This [Approach] eliminates [Pain 1], [Pain 2], without [Challenge]"

---

## Workflow

**Batch 1: Copywriting**

1. Read project context (offer, audience, proof, angles)
2. Ask for campaign name (required)
3. Select 5-6 angles for the batch — **reference `.claude/reference/compliance/angle-playbook.md`** for angle types, compliance burden, and selection matrix
4. **Write ALL image prompts first** (Part 1)
5. **Write ALL ad copy second** (Part 2)
6. **Cold traffic language check:** Every hook must pass the 3-second comprehension test — no insider jargon, no assumed context. Translate community language to customer language. See Joel's cold traffic guidance in [one-liner-methodology.md](one-liner-methodology.md).

Each batch file should start with:
```yaml
---
type: output
format: static-ad
date: YYYY-MM-DD
status: draft
platform: meta
---
```

7. Save to `outputs/YYYY-MM-DD-static-ads-[offer]-{campaign}/static-ads-batch-001.md` (include offer slug in multi-offer mode; omit `[offer]-` in single-offer mode)
8. Tell user: "Copy saved. Running automatic post-generation pipeline..."
9. Run the **Automatic Post-Generation Pipeline** (see SKILL.md). This handles git commit, compliance review, and image generation automatically.

---

## Ad Styles (5 per concept)

| Style | Length |
|-------|--------|
| Deep Ad | 500-800 words |
| UGC/Native | 100-300 words |
| Direct Response | 100-400 words |
| Pattern Interrupt | Under 100 words |
| Testimonial | 200-400 words |

---

## Image Prompt Types

| Type | Use Case |
|------|----------|
| Graphic | Typography-focused, frameworks, authority |
| Lo-fi | UGC style, authenticity, social proof |
| Interrupt | Pattern interrupt, scroll-stopping, contrarian |
| Text Overlay | Background-only for text overlay (used with creative variation copy) |

**Format pair: 1:1 + 9:16** — Facebook Ads Manager accepts exactly these two formats per ad. Design 9:16 first with critical content in center 1:1 safe zone. Center-crop for square. One design → two uploads.

See [static-output-template.md](static-output-template.md) for full output format.
See [image-prompt-templates.md](image-prompt-templates.md) for template library.
See [image-generation-workflow.md](image-generation-workflow.md) for Nano Banana integration.
