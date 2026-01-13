---
name: ad-review
description: Multi-lens compliance and quality review for ads before shipping. Use when asked to review ads, check compliance, audit copy, or verify ads are ready to launch. Runs 6 parallel review lenses (FTC, Meta, Copy, Visual, Voice, Substantiation) and produces a P1/P2/P3 report.
---

# Ad Review (Multi-Lens)

Review ads through 6 compliance and quality lenses before shipping.

## When to Use

- Before launching a new ad batch
- When ads are getting rejected and you need to identify why
- To audit existing campaigns for compliance risks
- Anytime you want systematic review, not just gut check

## The 6 Lenses

| Lens | File | What It Checks |
|------|------|----------------|
| FTC Compliance | `lenses/ftc-compliance.md` | Federal regulations, earnings claims, disclosures |
| Meta Policy | `lenses/meta-policy.md` | Platform triggers, Personal Attributes, bans |
| Copy Quality | `lenses/copy-quality.md` | Schwartz, Hormozi, Suby frameworks |
| Visual Standards | `lenses/visual-standards.md` | Safe zones, OCR, prohibited visuals |
| Voice Authenticity | `lenses/voice-authenticity.md` | AI tells, brand voice consistency |
| Substantiation | `lenses/substantiation.md` | Claims inventory, proof matching |

## Workflow

### Phase 1: Gather Input

Identify what's being reviewed:
- Single ad concept (copy + visual description)
- Full campaign batch (multiple ads)
- Specific component (just headlines, just hooks)

### Phase 2: Run Lenses in Parallel

Spawn 6 agents, one per lens. Each agent:

1. Reads its lens file from `lenses/`
2. Applies the checklist to the ad content
3. Returns findings with severity (P1/P2/P3)

**Parallel execution prompt for each lens:**

```
You are reviewing ad copy through the [LENS NAME] lens.

Read: [path to lens file]

Review this content:
[AD CONTENT]

For each checklist item in the lens:
1. Evaluate: Pass or Fail?
2. If Fail, cite the specific violation
3. Assign severity: P1 (blocks), P2 (fix before launch), P3 (improve if time)
4. Suggest specific fix based on "Safe" examples in the lens

Return findings as:
- Issue: [what's wrong]
- Severity: P1/P2/P3
- Evidence: [specific text that violates]
- Fix: [how to correct it]
```

### Phase 3: Synthesize Report

Combine all lens findings into a single review report:

```markdown
# Ad Review Report

**Date:** YYYY-MM-DD
**Reviewed:** [Campaign/Ad name]
**Status:** [BLOCKED / REVIEW REQUIRED / CLEAR]

---

## Summary

| Lens | P1 | P2 | P3 |
|------|----|----|----|
| FTC Compliance | X | X | X |
| Meta Policy | X | X | X |
| Copy Quality | X | X | X |
| Visual Standards | X | X | X |
| Voice Authenticity | X | X | X |
| Substantiation | X | X | X |
| **Total** | X | X | X |

---

## P1 Issues (Must Fix Before Launch)

### [Issue Title]
**Lens:** [Which lens caught this]
**Evidence:** [Specific text/visual]
**Why it's P1:** [Explanation from lens]
**Fix:** [Specific correction]

---

## P2 Issues (Should Fix)

[Same format]

---

## P3 Issues (Nice to Have)

[Same format]

---

## What's Working Well

[Positive findings from lenses]
```

### Phase 4: Provide Fix Suggestions

For each P1/P2 issue, provide:
- The problematic text
- Why it fails (cite lens rule)
- The corrected version (using safe alternatives from lens)

## Severity Definitions

| Level | Meaning | Examples |
|-------|---------|----------|
| **P1** | Blocks launch — legal/platform risk | Unsubstantiated income claim, "Are you struggling with..." |
| **P2** | Should fix — reduces performance or creates risk | Missing disclosure, AI vocabulary tells |
| **P3** | Nice to have — optimization opportunity | Could be more specific, hook could be stronger |

## Status Determination

- **BLOCKED:** Any P1 issues present
- **REVIEW REQUIRED:** Multiple P2 issues or borderline P1
- **CLEAR:** No P1, minimal P2

## Output Location

Save review reports to: `artifacts/reviews/{date}-{campaign-name}-review.md`

## Quick Review (Single Lens)

If you only need one lens (e.g., "just check FTC compliance"):

1. Read the specific lens file
2. Apply only that checklist
3. Return findings for that domain

## Context Files

The skill may reference:
- `context/compliance/` — Niche-specific rules beyond standard lenses
- `context/proof/` — Available testimonials for substantiation check
- `context/language-bank.md` — Customer phrases for voice check

## Example Review Flow

**User:** "Review this ad batch before I launch"

**Claude:**
1. Reads the ad content
2. Spawns 6 Task agents (one per lens) in parallel
3. Each agent reads its lens and reviews the content
4. Synthesizes findings into report
5. Flags BLOCKED if any P1, provides fixes
6. Saves report to artifacts/reviews/

---

*This skill implements the "Multi-Lens Ad Review Architecture" from the system architecture plan.*
