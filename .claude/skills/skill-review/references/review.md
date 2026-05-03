# Review — Seven Sweeps (dial-gated)

The skill runs review at two moments: **before locking the brief** and **before publishing the site**. Each sweep spawns a parallel review subagent (foreground) that returns findings; the operator decides what to act on.

The review gate ladder replaced the prior `research-grounded / in-voice / de-AI'd / framework-true` set with the **Seven Sweeps** from Corey Haines's copy-editing skill. Sweeps are dial-gated; not every site needs every sweep.

## The Seven Sweeps

| # | Sweep | What it checks |
|---|---|---|
| 1 | Clarity | Confusing structures, unclear pronouns, jargon, sentence-length cliffs |
| 2 | Voice & Tone | Read aloud — consistent register, matches `voice.md` |
| 3 | So What | Every claim answers "why should I care?" — no orphan features |
| 4 | Prove It | Every claim has evidence (testimonial, metric, demo, screenshot) |
| 5 | Specificity | Vague turned concrete (numbers, names, artifacts, scenes) |
| 6 | Heightened Emotion | Does it move you? — pain named honestly, outcome named concretely |
| 7 | Zero Risk | Every barrier near the CTA addressed (price, refund, terms, time) |

## Dial-gated application

| Dial | Sweeps that run | Why |
|---|---|---|
| `convert` | 1, 2, 3, 4, 5, 6, 7 (all) | A sales-conversion page must clear every gate. |
| `story` | 1, 2, 3, 5, 6 | Resonance and archetype fidelity matter more than evidence; Prove-It and Zero-Risk drop. |
| `brand` | 1, 2, 6 | Clarity, voice, emotion. Drop everything that pressures the copy toward conversion. |

The operator can override; the skill defaults to the dial.

## Auxiliary gates that always run

- **De-AI'd** — runs against [anti-patterns.md](anti-patterns.md) AI-tell list. Hard fail on any banned phrase, em-dash overuse, or overused-verb cluster.
- **Framework-true** — if `copy_framework_tag` is set in the brief, check the structure honors it.
- **Archetype-fidelity** — if `archetype` is set, check no `do_not_state` line was written as a headline.

## How review runs

1. **Identify the moment** (pre-lock, pre-publish).
2. **Read the brief** to learn the dial. Pick the sweeps for that dial.
3. **Spawn one foreground subagent per active sweep, in parallel.** Each returns short structured findings (P1/P2/P3 with line refs).
4. **Run the auxiliary gates** in parallel.
5. **Synthesize** into one combined report.
6. **Surface to operator.** "Here's what review found. Address now or proceed?"
7. **Operator picks.** If addressing: re-run affected sweeps after edits. If proceeding: log skipped findings to `.mainbranch/review-skipped.md`.

## Expert Panel Scoring (convert dial only)

After Seven Sweeps clear, run an Expert Panel scoring pass for `convert`:

- Pick 3-5 personas representative of the audience.
- Score each persona's reaction on a 1-10 scale across: clarity, relevance, persuasion, trust.
- Gate: every persona ≥ 7; panel average ≥ 8.
- If gate fails, name the lowest-scoring dimension and re-write that section.

This pass adds 2-4 minutes per draft. Bypass with `--skip-panel`; logged in brief frontmatter.

## Operator-defined gates

Operators extend with their own sweeps by dropping `.md` files in their business repo:

```
your-business-repo/
└── reference/review/
    ├── compliance-tier-1.md
    └── on-brand-tone.md
```

Each is a prompt for one review subagent. Picked up automatically alongside the defaults.

## Cross-references

- [anti-patterns.md](anti-patterns.md) — the AI-tell list run by the De-AI'd auxiliary gate
- [archetypes.md](archetypes.md) — fidelity checks against `do_not_state`
- [headline-formulas.md](headline-formulas.md) — Specificity sweep gates headlines
- `/ads review` — same multi-lens shape, same synthesis pattern
