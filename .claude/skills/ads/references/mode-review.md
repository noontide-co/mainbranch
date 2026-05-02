# Mode: Review

Review ads through 6 compliance and quality lenses before shipping.

---

## The 6 Lenses

| Lens | Location | What It Checks |
|------|----------|----------------|
| FTC Compliance | `.claude/lenses/ftc-compliance.md` | Federal regulations, earnings claims |
| Meta Policy | `.claude/lenses/meta-policy.md` | Platform triggers, Personal Attributes |
| Copy Quality | `.claude/lenses/copy-quality.md` | Schwartz, Hormozi, Suby frameworks |
| Visual Standards | `.claude/lenses/visual-standards.md` | Safe zones, OCR, prohibited visuals |
| Voice Authenticity | `.claude/lenses/voice-authenticity.md` | AI tells, brand voice |
| Substantiation | `.claude/lenses/substantiation.md` | Claims inventory, proof matching |

---

## Review Process

1. Gather input (single ad, batch, or component)
2. Git commit current state (preserves original): `[output] {type} batch pre-review`
3. Spawn 6 parallel Task agents — one per lens. Use `subagent_type: "general-purpose"`. Each agent:
   - Reads the ad batch/copy being reviewed
   - Reads its assigned lens file from `.claude/lenses/`
   - Evaluates every ad against that lens's checklist
   - Returns P1/P2/P3 findings with specific line references
   - Does NOT fix anything — just reports findings (read-only pattern, no write risk)
4. When all 6 agents return, synthesize findings into a unified P1/P2/P3 report (deduplicate where lenses overlap)
5. Write P2/P3 findings to `proposed-compliance-fixes.json`
6. Run `python -m mb.ads_compliance_gate ...` in dry-run mode and show the proposed diff
7. Ask: "Apply these compliance copy changes? (y/n)"
8. Only if approved, rerun the gate with `--approve --review-log ...`
9. Tell user whether the source copy changed or was left unchanged
10. If approved, ask whether to commit: `[review] {type} batch - N fixes applied`

---

## Severity Levels

| Level | Meaning |
|-------|---------|
| **P1** | Blocks launch (legal/platform risk) |
| **P2** | Fix before launch (reduces performance or risk) |
| **P3** | Nice to have (optimization) |

---

## Status Determination

- **BLOCKED:** Any P1 issues
- **REVIEW REQUIRED:** Multiple P2 or borderline P1
- **CLEAR:** No P1, minimal P2

See [review-workflow.md](review-workflow.md) for full report format.
