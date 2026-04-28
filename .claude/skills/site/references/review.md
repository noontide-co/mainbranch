# Review — Quality Gates for Brief and Site Copy

The skill runs through review steps at two moments: **before locking the brief** and **before publishing the site**. Each gate spawns a parallel review subagent (foreground) that returns findings; the operator decides what to act on. Gates are not blocking — they're guidance, like the lenses `/ads review` runs.

Review is plural. Multiple gates run in parallel and report back. The skill synthesizes the findings into one read-out for the operator.

---

## When review runs

| Moment | What's being reviewed | Gates that apply |
|---|---|---|
| **Before brief lock** | The draft brief (offer framing, headline, value prop, audience-language match) | research-grounded, in-voice, de-AI'd, framework-true |
| **Before publish** | The site copy as it exists in the project repo (home, how-it-works, picked pages) | in-voice, de-AI'd, framework-true (research-grounded re-runs only if reference files changed) |

The `/site` flow stops at each moment, runs review in parallel, surfaces findings, asks the operator: *"Address these, or proceed?"* It's a checkpoint, not a wall.

---

## The default gates

Each gate is a small subagent prompt (a "lens" in the same shape as `.claude/lenses/*.md`). Spawn in parallel; collect findings; render to operator.

### research-grounded

**Question:** Is the brief / copy backed by what real customers say?

**Inputs:** the brief draft (or site copy), `audience.md`, any `research/*.md` files in the business repo.

**Findings:** points where the language sounds invented vs. grounded. Specific lines to swap with audience-quoted phrasing. Or "looks grounded — no action needed."

**Why it matters:** ungrounded copy reads as AI marketing-speak and converts poorly. The fix is usually pulling specific phrases from interviews, reviews, or transcripts the operator has on file.

### in-voice

**Question:** Does the copy match `voice.md`?

**Inputs:** the brief draft (or site copy), `voice.md`.

**Findings:** sentences that violate declared voice traits (e.g., "warm and personal" voice but the copy is corporate-clinical). Suggested rewrites in the right register.

**Why it matters:** off-voice copy breaks brand cohesion and signals the system isn't actually using the operator's reference files.

### de-AI'd

**Question:** Does the copy have AI tells — generic hedging, em-dash overuse, "in today's fast-paced world," empty intensifiers, unnecessary numbered lists?

**Inputs:** the brief draft (or site copy).

**Findings:** specific sentences flagged with the AI-tell pattern (e.g., "this sentence has the 'unleash potential' pattern"). Suggested human rewrites.

**Why it matters:** AI-sounding copy is the #1 signal that nothing custom happened. Even if the system *did* use the reference files, AI cadence destroys trust.

### framework-true

**Question:** If the offer / brief declares a framework (e.g., PAS, AIDA, StoryBrand, founder-letter), does the copy follow it?

**Inputs:** the brief draft (or site copy), `offer.md` (which may declare a framework), the brief's structural plan.

**Findings:** sections that don't fit the declared framework's beats, or are out of order. Suggested restructuring.

**Why it matters:** an operator who picked a framework expects the output to follow it. Drift here is a quiet failure.

---

## Operator-defined gates

Operators can extend with their own gates by dropping `.md` files in their business repo:

```
your-business-repo/
└── reference/
    └── review/                    <- operator's custom gates
        ├── compliance-tier-1.md   <- e.g., FTC outcome-claim check
        └── on-brand-tone.md       <- e.g., specific tone rules
```

Each file is a prompt for one review subagent. The skill picks them up automatically and runs them alongside the defaults.

This is the same shape as `.claude/lenses/` for `/ads review`. Custom gates compose with the defaults — they don't replace them.

---

## How the skill runs review

1. **Identify the moment** (pre-lock, pre-publish).
2. **Collect inputs** the gates will need (brief draft, site copy, reference files).
3. **Spawn one foreground subagent per gate, in parallel.** Each subagent reads its inputs and returns findings as a short markdown report.
4. **Synthesize findings** into one combined report — group by gate, P1 / P2 / P3 priority, with specific line references.
5. **Surface to operator.** "Here's what review surfaced. Address now, or proceed?"
6. **Operator picks.** If they address: re-run the affected gates after edits. If they proceed: log the skipped findings to `.mainbranch/review-skipped.md` (visible in git history) and move on.

---

## Why "review" not "checks"

"Checks" carries GitHub-PR-checks baggage and confuses operators who don't think in those terms. "Review" matches `/ads review` and reads naturally to anyone editing copy.

The plural noun "review" works the same way `/ads review` does — one mode that runs multiple lenses in parallel and combines the output.

---

## Cross-references

- [`/ads review`](../../ads/SKILL.md) — same multi-lens shape, same synthesis pattern
- [`anti-patterns.md`](anti-patterns.md) — the anti-patterns that bypass review (over-prescription, padding, fabrication)
- [`minisite-build.md`](minisite-build.md) — where review fits in the operator walkthrough
- [`/think`](../../think/SKILL.md) — research patterns review depends on (research files, decisions linked to reference)
