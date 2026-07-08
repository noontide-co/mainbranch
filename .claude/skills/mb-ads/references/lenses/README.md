# Lenses

Quality control reference files for multi-lens ad review.

---

## What Are Lenses?

Lenses are self-contained knowledge bases that define review criteria. Each lens focuses on one domain and provides:

- Core principle (one-sentence philosophy)
- Actionable checklist with ✅/🔴 examples
- Red flags to always catch
- Severity levels (P1/P2/P3)
- Sources for authority

---

## Available Lenses

| Lens | Focus | Key Question |
|------|-------|--------------|
| `ftc-compliance.md` | Federal regulations | Does this violate FTC rules? |
| `meta-policy.md` | Platform enforcement | Will Meta reject this? |
| `copy-quality.md` | Direct response effectiveness | Does this follow proven frameworks? |
| `visual-standards.md` | Visual compliance & impact | Will this pass and stop the scroll? |
| `voice-authenticity.md` | AI detection & brand voice | Does this sound human and on-brand? |
| `substantiation.md` | Claims & proof | Is every claim backed by evidence? |

---

## How Agents Use Lenses

1. **Read the lens file** to understand criteria
2. **Apply checklist** to ad copy/visual
3. **Flag issues** with severity (P1/P2/P3)
4. **Cite specific examples** from the lens
5. **Provide fix suggestions** based on safe alternatives

---

## Severity Definitions

| Level | Meaning | Action |
|-------|---------|--------|
| **P1** | Blocks launch | Must fix before shipping |
| **P2** | Should fix | Fix before launch if possible |
| **P3** | Nice to have | Improve if time allows |

---

## Adding New Lenses

Each lens file should include:

1. **Core Principle** — One sentence philosophy
2. **Key Rules** — Specific, actionable criteria
3. **Checklist** — Pass/fail examples table
4. **Red Flags** — Patterns to always catch
5. **Severity** — P1/P2/P3 definitions for this domain
6. **Sources** — Authority for the rules

---

*Based on Gemini deep research 2026-01-13 and Compound Engineering lens patterns.*
