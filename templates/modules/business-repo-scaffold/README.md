# Business Repo Scaffold

Template for creating a new business/client repo that uses main-branch-premium as the engine.

---

## How To Use This Template

1. **Copy this entire folder** to create a new repo for your business/client
2. **Rename the folder** to your business name (e.g., `my-business`)
3. **Initialize git:** `git init`
4. **Update CLAUDE.md** with your business name
5. **Populate context files** with your offer, audience, proof
6. **Add main-branch-premium** as additional working directory in Claude Code

---

## Folder Structure

```
your-business/
├── CLAUDE.md                    # Instructions + engine reference
├── context/                     # What skills consume
│   ├── offer.md                 # Summary: what you sell
│   ├── audience.md              # Summary: who you sell to
│   ├── proof/                   # Testimonials
│   ├── angles/                  # Messaging entry points
│   ├── audience/                # Detail: psychographics
│   └── marketing/               # Detail: offer breakdown, angles
├── campaigns/                   # Generated outputs, assets, tracking
├── compliance/                  # FTC typicality data
├── research/                    # Historical research (dated)
└── copy/                        # Ad creation guides, SOPs
```

---

## The Engine Model

```
main-branch-premium (ENGINE)     your-business (DATA)
├── skills/                      ├── context/
├── lenses/                      ├── campaigns/
└── frameworks/                  ├── compliance/
         │                       ├── research/
         │                       └── copy/
         └────────────┬───────────────────┘
                      │
              Skills read context/,
              output to campaigns/
```

---

## Minimum Viable Setup

To start generating ads, you need at minimum:

1. ✅ `context/offer.md` — Price, mechanism, benefits
2. ✅ `context/audience.md` — Pains, desires
3. ✅ At least one angle in `context/angles/`

Optional but recommended:
- `context/proof/testimonials.md` — For social proof
- `compliance/typicality/` — Required for outcome testimonials
- `research/` — Dated research sessions
- `copy/` — Ad creation guides and SOPs
