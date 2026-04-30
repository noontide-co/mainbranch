# File Education (Teach Why Each File Matters)

When sorting content into files during setup, teach WHY each file matters as you create it. Don't just scaffold — explain. This is the user's first encounter with the system. The act of writing these files IS the learning.

---

## Core File Educational Context

Present each blurb before writing the corresponding file.

### soul.md
> "soul.md is WHY you exist. Not the marketing answer — the real one. Three questions: What do you research when no one's watching? What intersections excite you? What decisions feel like discovery vs obligation? This file is your reconnection fuel — when you're grinding and feel nothing, re-read it."

### offer.md
> "offer.md is WHAT you sell. Price, mechanism, deliverables, guarantee. Every ad, script, and piece of content reads this file. The clearer it is, the better everything downstream works."

### audience.md
> "audience.md is WHO buys. Not demographics — real people with specific pains, desires, and objections. The words in this file become the words in your ads."

### voice.md
> "voice.md is HOW you sound. Tone, vocabulary, phrases you always use, phrases you never say. This is what keeps AI sounding like you instead of generic."

---

## Multi-Offer Additions

For multi-offer setups, also explain:

### offer.md (brand-level)
> "This is your brand-level offer.md — the umbrella story. It covers what your brand stands for across all offers. Each specific offer gets its own file in `offers/[name]/offer.md` with pricing, mechanism, and details."

### product-ladder.md
> "product-ladder.md maps how your offers relate. Which one do people discover first? Where do they go next? This helps us create content and ads that guide people through your world."

---

## Priority Order (Single-Offer)

1. `reference/core/soul.md` — Why you exist (reconnection fuel)
2. `reference/core/offer.md` — What you sell (or brand thesis if multi-offer)
3. `reference/core/audience.md` — Who buys
4. `reference/core/voice.md` — How you sound
5. `reference/proof/testimonials.md` — Social proof
6. `reference/proof/angles/` — Messaging entry points
7. `reference/visual-identity/visual-style.md` — Visual brand identity (colors, typography, mood, image prompt fragments)
8. `reference/domain/content-strategy.md` — Content pillars, platforms, cadence (template for community businesses)
9. `reference/domain/funnel/skool-surfaces.md` — Live Skool about page + pricing card copy (community businesses with Skool)

### Multi-Offer Additional Files (if applicable)

10. `reference/offers/[name]/offer.md` — Offer-specific details for each offer
11. `reference/offers/[name]/audience.md` — Only if this offer targets a different segment
12. `reference/domain/product-ladder.md` — How offers relate to each other

> **Note:** content-strategy.md and visual-style.md start as templates and get filled through `/think` cycles. Not required at setup — scaffolded with placeholder sections.

---

## Visual Style Scaffolding

After core reference is drafted, ask 3 quick questions to seed `visual-style.md`:

1. "What's your brand's visual mood?" (minimal/bold/editorial/playful/dark)
2. "What are your brand colors?" (hex codes or descriptions)
3. "What photography style fits?" (lifestyle/product/abstract/editorial)

Use answers + audience data to generate a starter `visual-style.md` from the template at `templates/modules/brand-style-template.md` (in vip). This file is consumed by `/ads` (image prompts), `/site` (CSS/design tokens), and `/organic` (visual consistency).
