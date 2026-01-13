# [Business Name]

Client-specific data for [Business Name]. Uses main-branch-premium as the engine.

---

## Engine Reference

**This repo does NOT contain skills or lenses.**

Skills and lenses live in main-branch-premium (the shared engine). Add main-branch-premium as an additional working directory in Claude Code to access them.

```
Engine: main-branch-premium
Data:   this repo
```

---

## What Lives Here

### Context (The Data That Tunes The Engine)

```
context/
├── offer.md              # What we sell (price, benefits, mechanism)
├── audience.md           # Who we sell to (pains, desires, demographics)
├── proof/
│   ├── testimonials.md   # Customer testimonials with consent status
│   └── data.md           # Statistics, outcomes, numbers
├── angles/               # Messaging entry points
│   └── README.md
└── language-bank.md      # Verbatim customer phrases
```

### Compliance (Client-Specific)

```
compliance/
└── typicality/
    └── [client]-typicality.md   # FTC-required outcome data
```

### Outputs

```
campaigns/
└── outputs/              # Generated ad batches, scripts, etc.
```

---

## How To Use

1. **Clone main-branch-premium** to your local machine
2. **Add it as additional working directory** in Claude Code
3. **Open this repo** as your primary working directory
4. **Run skills** from main-branch-premium - they'll read your context and output here

Example:
```
"Generate an ad batch using the fresh-start angle"
→ Engine reads context/offer.md, context/angles/fresh-start.md
→ Engine outputs to campaigns/outputs/
```

---

## Skills Available (via main-branch-premium)

| Skill | What It Does |
|-------|--------------|
| ad-static | Static image ads with AI image prompts |
| ad-video-scripts | Video ad scripts (hooks, bodies, CTAs) |
| ad-review | Multi-lens compliance review (FTC, Meta, etc.) |
| skool-vsl-scripts | Long-form VSL scripts |

---

## Context Files To Populate

Before running skills, populate these files:

| File | Status | Notes |
|------|--------|-------|
| context/offer.md | ⬜ TODO | Price, benefits, mechanism |
| context/audience.md | ⬜ TODO | Pains, desires, demographics |
| context/proof/testimonials.md | ⬜ TODO | Customer results with consent |
| context/angles/ | ⬜ TODO | At least 3-5 angles |
| compliance/typicality/ | ⬜ TODO | Required for outcome testimonials |
