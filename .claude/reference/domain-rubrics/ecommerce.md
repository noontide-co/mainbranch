---
type: reference
status: active
domain: e-commerce
date: 2026-01-16
---

# E-commerce Domain Rubric

Guide for structuring `reference/domain/` folder for e-commerce businesses.

---

## Required Domain Structure

```
reference/
└── domain/
    ├── products/
    │   ├── catalog.md        # Full product catalog (from Shopify/platform)
    │   ├── materials.md      # Materials, sourcing, care instructions
    │   └── sizing.md         # Size guides, fit information
    │
    └── fulfillment/
        └── logistics.md      # Shipping, returns, production method
```

---

## File Specifications

### products/catalog.md

**Purpose:** Complete product inventory for AI reference and content generation.

**Required fields per product:**
- Product name
- Handle/slug
- Price
- Product type/category
- Description (short)
- Key features
- Available variants (sizes, colors)

**Source:** Export from Shopify Admin → Products → Export

**Example structure:**
```markdown
## [Product Name]

- **Handle:** product-handle
- **Price:** $39.00
- **Type:** T-Shirt
- **Description:** Brief product description
- **Variants:** S, M, L, XL | Black, White
```

---

### products/materials.md

**Purpose:** Material details for product descriptions, care instructions, and customer questions.

**Required sections:**
- Primary materials by product type
- Sourcing/origin (if relevant)
- Care instructions
- Sustainability notes (if applicable)

**Example:**
```markdown
## T-Shirts
- **Material:** 100% Airlume combed and ring-spun cotton
- **Weight:** 4.2 oz
- **Feel:** Soft, retail fit
- **Care:** Machine wash cold, tumble dry low

## Hoodies
- **Material:** 52% Airlume cotton, 48% poly fleece
- **Weight:** 8.0 oz
- **Feel:** Ultra-soft fleece interior
- **Care:** Machine wash cold, tumble dry low
```

---

### products/sizing.md

**Purpose:** Size guides and fit information for customer support and product pages.

**Required:**
- Size chart by product type
- Fit notes (runs small/large, etc.)
- Measurement instructions

---

### fulfillment/logistics.md

**Purpose:** Operational details for customer communication and AI responses.

**Required sections:**
- Production method (made-to-order, inventory, etc.)
- Production time
- Shipping carriers and times
- Return policy
- International shipping (if applicable)

---

## Optional Extensions

Depending on your e-commerce niche, you may add:

| Folder | Use Case |
|--------|----------|
| `collections/` | Curated collection descriptions |
| `seasonal/` | Holiday/seasonal product info |
| `wholesale/` | B2B pricing and terms |

---

## Integration with Core Reference

E-commerce domain files work alongside universal reference:

| Universal (reference/) | E-commerce Specific (reference/domain/) |
|------------------------|----------------------------------------|
| `core/offer.md` | `products/catalog.md` |
| `core/audience.md` | — |
| `core/voice.md` | — |
| `brand/voice-system.md` | — |
| `proof/testimonials.md` | — |
| `proof/angles/` | — |

**The relationship:** `core/offer.md` summarizes what you sell. `domain/products/catalog.md` has the full inventory.

---

## Skills That Use This Domain

| Skill | What It Reads |
|-------|---------------|
| `/ad-static` | `products/catalog.md` for product details |
| `/ad-video-scripts` | `products/catalog.md`, `products/materials.md` |
| Product descriptions | `products/catalog.md`, `products/materials.md`, `products/sizing.md` |

---

*Rubric version: 1.0*
*Last updated: 2026-01-16*
