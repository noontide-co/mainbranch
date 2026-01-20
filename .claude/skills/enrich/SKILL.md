---
name: enrich
description: |
  Add context to an existing business repo. Use when:
  (1) Returning user wants to fill gaps in reference files
  (2) User has new testimonials, angles, or proof to add
  (3) Business has changed and reference files need updating
  (4) User wants to import research findings into reference
  (5) User says "add context", "update my files", "I have new info"

  Audits existing files, identifies gaps, gathers new context, merges without overwriting.
---

# Enrich

Add context to an existing Main Branch business repo.

**Need help?** Type `/help` + your question anytime. If conversation compacts, `/help` reloads fresh context.

---

## When to Use

- User has an existing repo with reference files
- They want to add more context, not start fresh
- They have new testimonials, angles, or business changes
- Reference files exist but are thin or incomplete

**Not for new users** — use `/setup` for first-time setup.

---

## Workflow

### 0. Pull Latest Updates (Always)

```bash
cd ~/vip 2>/dev/null && git pull origin main 2>/dev/null && cd - >/dev/null || true
```

If updates pulled: briefly note "Pulled latest vip updates." then continue silently.

---

### 1. Verify Repo Structure

Check that standard folders exist:

```bash
ls -la reference/core reference/proof reference/domain 2>/dev/null || echo "Missing folders"
```

If missing core structure, suggest `/setup` instead.

### 2. Audit Current State

Read existing reference files and assess completeness:

| File | Check For |
|------|-----------|
| `reference/core/offer.md` | Price, mechanism, deliverables, guarantee |
| `reference/core/audience.md` | Who, pains, desires, objections |
| `reference/core/voice.md` | Tone, phrases, personality markers |
| `reference/proof/testimonials.md` | 3-5 testimonials with specific outcomes |
| `reference/proof/angles/` | At least 2-3 proven messaging angles |
| `reference/domain/` | Business-type specific content |

### 3. Report Gaps

Present a table showing what's missing or thin:

```markdown
## Current State

| File | Status | Gaps |
|------|--------|------|
| core/offer.md | ⚠️ Thin | Missing guarantee, unclear mechanism |
| core/audience.md | ✅ Good | — |
| core/voice.md | ❌ Empty | Needs everything |
| proof/testimonials.md | ⚠️ Thin | Only 1 testimonial, needs outcomes |
| proof/angles/ | ❌ Empty | No angles documented |
| domain/ | ✅ Good | — |

**Priority:** voice.md, angles/, testimonials
```

### 4. Ask What to Enrich

> "I found gaps in [X, Y, Z]. What would you like to add today? You can:
> - Paste text, URLs, or file paths
> - Share screenshots
> - Brain dump and I'll sort it"

### 5. Gather Context

Use the same ruthless journalist approach from setup.

**For URLs:** Try WebFetch → Chrome → Playwright → manual paste

**Key prompts:**
- "What else do you have? Sales pages, testimonials, emails?"
- "Any client calls or DMs that show how you talk?"
- "What's changed since you last updated these files?"

See `../setup/references/context-gathering.md` for full checklists.

### 6. Merge Into Existing Files

**Critical: Preserve existing content.**

When updating files:
1. Read the current file completely
2. Identify what's new vs. what exists
3. Add new content in appropriate sections
4. Never delete existing content unless explicitly asked
5. Use comments to mark additions: `<!-- Added 2026-01-17 -->`

**Merge patterns:**

For `testimonials.md`:
```markdown
## Existing Testimonials
[keep all existing]

## New Testimonials (Added 2026-01-17)
[add new ones here]
```

For `audience.md` (adding new objections):
```markdown
## Objections
[existing objections]
- [new objection from today's context]
```

### 7. Report What Changed

After merging, show a summary:

```markdown
## Changes Made

| File | Changes |
|------|---------|
| core/voice.md | Added 5 phrases, 3 personality markers |
| proof/testimonials.md | Added 3 new testimonials with outcomes |
| proof/angles/risk-reversal.md | Created new angle file |

**Still missing:** [anything not addressed]
```

### 8. Suggest Next Steps

Based on what's still thin:
- "Your angles folder is still empty — want to document some proven hooks?"
- "Voice file could use more examples — got any emails or posts I can mine?"
- "Consider running `/think` to research [topic] before your next campaign"

---

## Merge Safety Rules

1. **Always read before writing** — Never overwrite without reading first
2. **Preserve structure** — Keep existing headings and organization
3. **Add, don't replace** — New content supplements, doesn't overwrite
4. **Mark additions** — Use date comments for traceability
5. **Confirm before large changes** — If changing >30% of a file, ask first

---

## Quick Reference

**Completeness thresholds:**

| File | Minimum for "Good" |
|------|-------------------|
| offer.md | Price + mechanism + deliverables |
| audience.md | Who + 3 pains + 3 desires + 2 objections |
| voice.md | Tone + 5 phrases + personality |
| testimonials.md | 3 testimonials with specific outcomes |
| angles/ | 2-3 documented angles |

**Status icons:**
- ✅ Good — Meets minimum
- ⚠️ Thin — Exists but incomplete
- ❌ Empty — Missing or no content
