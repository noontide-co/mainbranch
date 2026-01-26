# Ad Review Workflow

## Phase 0: Pre-Review Git Commit

Before reviewing, commit current state to preserve the original:

```bash
git add outputs/YYYY-MM-DD-{type}-{campaign}/
git commit -m "[output] {type} batch pre-review"
```

This ensures the original version is preserved in git history.

## Phase 1: Gather Input

Identify what's being reviewed:
- Single ad concept (copy + visual description)
- Full campaign batch (multiple ads)
- Specific component (just headlines, just hooks)

## Phase 2: Run Lenses in Parallel

Spawn 6 agents, one per lens. Each agent:

1. Reads its lens file from `.claude/lenses/`
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

## Phase 3: Synthesize Report

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

## Phase 4: Apply Fixes and Log Changes

**Key insight: Reviews UPDATE the source file, not just report issues.**

For each P2/P3 issue:
1. Apply the fix directly to the batch file
2. Log the change to `review-log.md`

**review-log.md format:**

```markdown
## Review: YYYY-MM-DD

**Status:** BLOCKED | REVIEW REQUIRED | CLEAR TO SHIP

### Fixes Applied

| Line | Original | Fixed | Reason |
|------|----------|-------|--------|
| #5 | "tired of juggling..." | "juggling..." | Meta Personal Attributes |
| #22 | "drowning in..." | "overwhelmed by..." | Meta Personal Attributes |

### P1 Issues (Manual Fix Required)

[Any P1 issues that need human decision]
```

For P1 issues:
- Do NOT auto-fix (requires human decision)
- Document in review-log.md
- Status: BLOCKED until P1s resolved

## Phase 5: Post-Review Git Commit

After fixes are applied:

```bash
git add outputs/YYYY-MM-DD-{type}-{campaign}/
git commit -m "[review] {type} batch - N fixes applied"
```

**To see what review changed:** `git diff HEAD~1`

## Context Files

**From engine (vip):**
- `.claude/lenses/` — The 6 review lenses
- `.claude/reference/compliance/` — Shared compliance frameworks

**From business repo:**
- `reference/proof/testimonials.md` — Available testimonials for substantiation check
- `reference/proof/typicality.md` — Outcome data for claim validation
- `reference/core/offer.md` — To verify claims match actual offering

## Quick Review (Single Lens)

If you only need one lens (e.g., "just check FTC compliance"):

1. Read the specific lens file
2. Apply only that checklist
3. Return findings for that domain
