# Business Repo Scaffold

Template for creating a new business/client repo that uses main-branch-premium as the engine.

---

## Quick Start

1. **Copy this entire folder** to create a new repo for your business/client
2. **Rename the folder** to your business name (e.g., `my-business`)
3. **Initialize git:** `git init`
4. **Update CLAUDE.md** with your business name and details
5. **Populate context files** with your offer, audience, proof
6. **Add main-branch-premium** as additional working directory in Claude Code

---

## Folder Structure

```
your-business/
├── CLAUDE.md                    # Instructions + engine reference
│
├── context/                     # EVERGREEN — What skills consume
│   ├── offer.md                 # What you sell
│   ├── audience.md              # Who you sell to
│   ├── proof/                   # Approved testimonials
│   │   └── testimonials.md
│   └── angles/                  # Messaging entry points
│       └── README.md
│
├── research/                    # DATED — Point-in-time exploration
│   └── README.md
│
├── decisions/                   # DATED — Choices with rationale
│   └── README.md
│
└── campaigns/                   # OUTPUT — Generated content
    └── README.md
```

---

## The Engine Model

```
main-branch-premium (ENGINE)     your-business (DATA)
├── skills/                      ├── context/
├── lenses/                      ├── research/
└── frameworks/                  ├── decisions/
         │                       └── campaigns/
         └────────────┬───────────────────┘
                      │
              Skills read context/,
              output to campaigns/
```

---

## Philosophy: Active Context Management

**You learn your business by building your context.**

This is not passive memory. By articulating your offer, your audience, your angles — you understand your business more deeply than you would if a chat just "remembered" things automatically.

The cycle:
1. **Research** → Explore questions, gather information (dated)
2. **Decide** → Make choices with rationale (dated)
3. **Codify** → Update evergreen context
4. **Generate** → Skills consume context, produce outputs
5. **Learn** → Outputs inform new research

---

## Minimum Viable Setup

To start generating ads, you need at minimum:

1. ✅ `context/offer.md` — Price, mechanism, benefits
2. ✅ `context/audience.md` — Pains, desires, who they are
3. ✅ At least one angle in `context/angles/`

Optional but recommended:
- `context/proof/testimonials.md` — For social proof
- `context/proof/typicality.md` — Required for outcome testimonials in regulated industries
- `research/` — Dated research sessions
- `decisions/` — Decision records with rationale

---

## File Conventions

### Naming

| Type | Format | Example |
|------|--------|---------|
| Evergreen context | `slug.md` | `offer.md` |
| Research | `YYYY-MM-DD-slug.md` | `2026-01-13-competitor-analysis.md` |
| Decisions | `YYYY-MM-DD-slug.md` | `2026-01-13-angle-strategy.md` |
| Campaign batches | `YYYY-MM-DD-batch-name/` | `2026-01-13-january-launch/` |

### Frontmatter

All markdown files should have frontmatter:

```yaml
---
type: research | decision | context | campaign
status: draft | active | complete | archived
date: 2026-01-13  # For dated content
linked_decisions: []  # For research files
---
```

---

## Using the Engine

1. Add main-branch-premium as additional working directory in Claude Code
2. Skills become available: `/ad-static`, `/ad-review`, etc.
3. Skills read from your `context/` folder
4. Outputs go to your `campaigns/` folder

See main-branch-premium CLAUDE.md for full skill reference.
