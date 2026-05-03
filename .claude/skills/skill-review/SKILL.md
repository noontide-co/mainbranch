---
name: skill-review
tier: skill
calls: []
description: "Run dial-gated Seven Sweeps + auxiliary gates against a brief or copy draft. Returns synthesized findings to the operator. Used by /site at pre-lock and pre-publish moments. Reusable by /vsl, /ads in v0.2."
---

# skill-review

A composable skill that wraps the Seven Sweeps + auxiliary review gates. /site calls this at pre-lock and pre-publish.

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
