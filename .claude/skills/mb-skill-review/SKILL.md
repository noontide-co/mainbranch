---
name: mb-skill-review
tier: skill
calls: []
description: "Pre-publish review / UI pass / design pass / design critique for a brief or copy draft: runs dial-gated Seven Sweeps + auxiliary gates and returns synthesized findings. Use when: the operator asks for a pre-publish review, a UI pass, a design pass, a design critique, or to review a page before publishing. Called by /mb-site at pre-lock and pre-publish; reusable by /mb-ads and sales-video workflows."
loops: [reflect]
---

# skill-review

A composable skill that wraps the Seven Sweeps + auxiliary review gates. /mb-site calls this at pre-lock and pre-publish.

## Inputs

- The artifact under review (brief or copy draft)
- The dial (`convert | story | brand`)
- Reference files (voice.md, audience.md, optional research/*)
- The brief's `do_not_state` list (for archetype-fidelity check)

## Outputs

A synthesized review report:

```
{
  "ok": false,
  "dial": "convert",
  "sweeps_run": [1, 2, 3, 4, 5, 6, 7],
  "findings": [
    {"sweep": "Specificity", "priority": "P1", "line": 12, "note": "..."},
    ...
  ],
  "panel_score": 7.2,
  "blocking": ["specificity", "ai-tells"]
}
```

## Flow

1. **Load the artifact** and the dial.
2. **Pick sweeps** from [`references/review.md`](references/review.md) — dial-gated.
3. **Spawn one foreground subagent per active sweep, in parallel.** Each returns short findings (P1/P2/P3 with line refs).
4. **Run auxiliary gates** in parallel: De-AI'd, Framework-true, Archetype-fidelity.
5. **(Convert dial only)** Run Expert Panel scoring across 3-5 personas.
6. **Synthesize** findings into one report; group by sweep, P-priority, line.
7. **Return** to caller (which surfaces to operator).

## Dial-gated sweeps

| Dial | Sweeps |
|---|---|
| `convert` | 1, 2, 3, 4, 5, 6, 7 + Expert Panel |
| `story` | 1, 2, 3, 5, 6 |
| `brand` | 1, 2, 6 |

## Cross-references

- [references/review.md](references/review.md)
- [references/anti-patterns.md](references/anti-patterns.md)
