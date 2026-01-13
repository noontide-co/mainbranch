# Compliance Reference

Strategic planning resources for compliant advertising.

---

## How This Differs from Lenses

**Lenses** (in `.claude/lenses/`) check individual ads for violations after they're written.

**Compliance references** (this folder) help decide what TYPE of ads to create BEFORE writing them.

```
PLANNING PHASE                    REVIEW PHASE
─────────────────                 ─────────────
compliance/                       lenses/
├── ftc-scrutiny-categories.md    ├── ftc-compliance.md
├── angle-playbook.md             ├── meta-policy.md
├── testimonial-decision-rubric.md├── copy-quality.md
└── typicality/                   ├── visual-standards.md
                                  ├── voice-authenticity.md
                                  └── substantiation.md
```

---

## Files in This Folder

### Strategic Planning

| File | Purpose | When to Use |
|------|---------|-------------|
| `ftc-scrutiny-categories.md` | Which industries get extra FTC attention | Before starting ANY campaign for a client |
| `angle-playbook.md` | All persuasion angles + rules for each | When planning campaign angles |
| `testimonial-decision-rubric.md` | When outcome testimonials are worth it | Before deciding to use testimonials |

### Client-Specific Data

| Folder | Purpose | When to Use |
|--------|---------|-------------|
| `typicality/` | FTC-required outcome data per client | When using outcome testimonials |
| `typicality/README.md` | How to collect typicality data | When data is missing |
| `typicality/{client}-typicality.md` | Client-specific outcome data | During ad review |

---

## Pre-Campaign Checklist

Before creating ads for a client:

### 1. Check FTC Scrutiny Level
Read `ftc-scrutiny-categories.md`
- Tier 1 (Max scrutiny): Default to non-outcome angles
- Tier 2 (High): Outcome testimonials need proper disclosure
- Tier 3 (Moderate): Standard compliance

### 2. Decide on Angles
Read `angle-playbook.md`
- Which angles fit this offer?
- What are the compliance requirements for each?
- Which angles to avoid?

### 3. If Using Outcome Testimonials
Read `testimonial-decision-rubric.md`
- Score the offer on the rubric
- If score < 5: Use alternative angles
- If score >= 5: Check typicality data

### 4. Check Typicality Data
Look for `typicality/{client}-typicality.md`
- If exists with data: Use for disclosures
- If exists but "DATA NEEDED": Block outcome testimonials
- If doesn't exist: Create file, flag as research task

---

## Adding New Clients

When onboarding a new client:

1. Create `typicality/{client}-typicality.md` using template in `typicality/README.md`
2. Assess FTC scrutiny tier for their industry
3. Document what outcome data exists (if any)
4. Recommend angle strategy based on compliance burden

---

## Quick Reference: Angle by Risk

| Low Compliance Burden | High Compliance Burden |
|-----------------------|------------------------|
| Mechanism | Outcome testimonials |
| Social proof (scale) | Urgency/scarcity |
| Risk reversal | Pain agitation (Meta) |
| Community | |
| Process testimonials | |
| Curiosity | |

When in doubt, use low-burden angles.
