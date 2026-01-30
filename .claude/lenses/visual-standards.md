# Visual Standards Lens

Review ad visuals for platform compliance and thumb-stopping effectiveness.

---

## Core Principle

**Visuals are the first point of rejection.** Meta's algorithm analyzes text via OCR and visual content via computer vision before humans see the ad.

---

## Safe Zones (9:16 Reels/Stories)

The 9:16 format (1080x1920) has UI elements that cover content.

```
┌─────────────────────┐
│   TOP 14% DANGER    │  ← Progress bar, account icon
│                     │
│ ┌─────────────────┐ │
│ │  CENTER 1:1     │ │  ← All hooks and disclosures HERE
│ │  SAFE ZONE      │ │  ← This area extracts as the square version
│ └─────────────────┘ │
│                     │
│  BOTTOM 35% DANGER  │  ← Caption, CTA button, likes
└─────────────────────┘
```

**Compliance implication:** Disclosures at bottom are "avoidable" = non-compliant.

### Format Pair: 1:1 + 9:16

Facebook Ads Manager accepts exactly two image uploads per ad: **1:1 (square)** and **9:16 (vertical)**. There is no 4:5 upload option.

**Design strategy:** Design 9:16 first, keep critical content in center 1:1 zone, center-crop for square version. One design → two uploads.

### Technical Specs

- **Square:** 1920×1920 (1:1) — Facebook feed, Instagram feed
- **Vertical:** 1080×1920 (9:16) — Stories, Reels, full-screen mobile
- **Safe margin:** 250px from top and bottom edges on 9:16
- **Critical text:** Must be in center 1:1 zone (visible in both formats)

---

## OCR Triggers

Meta reads text on images. Banned claims in image text trigger rejection.

| Safe Image Text | Flagged Image Text |
|-----------------|-------------------|
| "New Strategy Revealed" | "Lose 20lbs Fast" |
| "Framework Breakdown" | "Make $10k/month" |
| "Free Training" | "Financial Freedom" |

---

## Visual Patterns (2025)

### Pattern Interrupts

- **Glitch/Flash:** High-contrast, rapid changes. Effect must be smooth (excessive = "Disruptive" flag).
- **Lo-fi aesthetic:** Native-looking content outperforms polished ads for many audiences.

### Fake Podcast Aesthetic

Popular trend: "Podcast clip" framing builds authority.

**Compliance check:** If guest makes a claim ("I made $1M"), that's an endorsement. Requires superimposed disclaimer *during* that sentence: "Results not typical. Average revenue is $0."

### Green Screen Commentary

Creator talking over screenshot/chart.

**Compliance check:**
- Background must be truthful (no faked bank statements)
- No unauthorized logos (CNN, Fox = trademark violation)
- Source must be visible if showing news article

---

## Prohibited Visual Patterns

| Pattern | Why Banned | Alternative |
|---------|-----------|-------------|
| Before/after (weight loss) | Explicitly banned | Result-state lifestyle image |
| Zoomed body parts | Health policy | Full body in context |
| Bank account screenshots | "Unrealistic outcomes" | Abstract success imagery |
| Fake play buttons | Circumventing systems | Real video or static design |
| Fake UI elements | Deceptive | Clear design language |

---

## Checklist

| Check | Pass | Fail |
|-------|------|------|
| **Safe Zones** | Text centered, 250px buffer | Text at edges, covered by UI |
| **OCR Claims** | Generic text, no promises | Banned phrases in image |
| **Body Focus** | Full body in context | Zoomed abs, belly, acne |
| **Button Fakes** | Real video or static | Fake play/download button |
| **UGC Authenticity** | Real screenshots with source | Doctored images, fake logos |

---

## Disclosure Placement

For endorsements or claims in video:

- **Position:** Superimposed, not in caption
- **Timing:** Appears during the claim, not after
- **Size:** Readable, not fine print
- **Duration:** On screen long enough to read

---

## Red Flags (Always Flag)

- Any before/after structure
- Text in danger zones (top 14%, bottom 35%)
- Banned phrases visible in image
- Fake UI elements anywhere
- Zoomed body parts
- Screenshots without visible source

---

## Severity

| Level | Criteria | Action |
|-------|----------|--------|
| **P1 - Blocks** | Before/after, fake UI, OCR banned phrases | Cannot ship |
| **P2 - Fix** | Disclosure placement, safe zone violations | Fix before launch |
| **P3 - Note** | Could be more thumb-stopping | Improve if time |

---

*Source: Meta Ad Specs 2025, Jon Loomer Safe Zone Templates, usevisuals.com*
