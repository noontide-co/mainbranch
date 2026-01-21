# The /think Cycle: The Core Loop

This is the heart of Main Branch. Everything else exists to support this cycle.

**"/think is my project management solution for running anything now."** - It's not just for marketing. It's how you manage decisions across all your businesses.

---

## The Cycle

```
RESEARCH → DECIDE → CODIFY → GENERATE → LEARN
    ↑                                      │
    └──────────────────────────────────────┘
```

1. **Research** - Investigate a question, gather information
2. **Decide** - Make a choice with documented rationale
3. **Codify** - Update your reference files with the decision
4. **Generate** - Use skills to create outputs from reference
5. **Learn** - See what works, feed back into research

This cycle is why Main Branch gets better over time. Each loop makes your reference more accurate, your outputs more effective.

---

## How /think Works

Run `/think` with a topic:
```
/think "What pricing tier should we use?"
```

Claude will:
1. Research the topic (web search, your existing files, your context)
2. Synthesize findings into a clear summary
3. Present options with pros/cons
4. Help you make a decision
5. Save the research and decision as files
6. Optionally update your reference files

---

## What Gets Saved

**Research files** go to `research/`:
```
research/2026-01-19-pricing-analysis-claude-code.md
```

These are dated investigations. They capture what you learned and when.

**Decision files** go to `decisions/`:
```
decisions/2026-01-19-pricing-strategy.md
```

These document the choice you made and why. They link back to research.

**Reference files** get updated:
```
reference/core/offer.md (updated with new pricing)
```

This is where decisions become evergreen truth that skills consume.

---

## Why Record Everything?

### 1. Context Windows Are Limited

Claude has a context window. When you hit 85k tokens, things start getting compacted. The conversation fades.

**This is why we're leaving a paper trail.** The files persist even when the conversation doesn't.

### 2. Context Survives Sessions

Claude's memory fades. Files don't. When you come back next week, your research and decisions are still there.

### 3. Rationale is Preserved

Six months from now, you'll wonder "why did we do it this way?" The decision file tells you.

### 4. Knowledge Compounds

Each research file adds to your understanding. Each decision builds on the last. Over time, you have a comprehensive record of your business thinking.

### 5. Reference Stays Current

When decisions update reference files, your outputs immediately reflect the new reality. No stale information.

### 6. Cross-Tool Portability

Files saved to your repo can be accessed from:
- Claude Code on desktop
- Claude on your phone
- ChatGPT with GitHub connected
- Any future tool

The conversation is temporary. The files are yours forever.

---

## What Counts as "Research"?

Research is broad. It's not just web search:

| Research Type | Example |
|---------------|---------|
| Web research | Gemini deep research on platform updates |
| Data mining | Download your social media data, parse it for insights |
| Transcript analysis | Pull a podcast transcript, extract angles |
| Competitor mining | Study what's working for others |
| Internal audit | Review your own past campaigns for patterns |
| Document review | Analyze a contract, policy, or guide |

Research = any investigation that informs a decision.

---

## When to Use /think

**Perfect for:**
- Pricing decisions
- Positioning questions
- Messaging angle exploration
- Offer structure changes
- Audience refinement
- Any "should we...?" question
- Processing data dumps into insights
- Making sense of platform changes

**Not needed for:**
- Quick factual questions (just ask)
- Simple file edits (just edit)
- Content generation (use `/ad-static`, etc.)

Use `/think` when the answer requires investigation and the choice needs documentation.

---

## Example: GPT Knowledge Base Migration

Christian asked: "How do I dump my GPT knowledge base into Claude?"

This is a perfect /think question.

```
/think "How to extract and migrate my GPT knowledge base to Main Branch"
```

**Research phase:**
- What data can be exported from GPT?
- What formats are available?
- What's the best way to organize it for Main Branch?

**Decision phase:**
- Decide on extraction method
- Decide on organization structure
- Document the approach

**Codify phase:**
- Execute the migration
- Update reference files with the imported content

**Result:** Christian has a documented process AND his knowledge is now in Main Branch.

---

## The Three Modes

### `/think "topic"` (Full Flow)
Research → Synthesize → Decide → Codify (optional)

### `/think research "topic"` (Research Only)
Just investigate and save findings. Decide later.

### `/think decide "topic"` (Decision Only)
You've already researched. Just document the decision.

---

## Synthesis is Required

Every research output must have a synthesis section:
- One-sentence summary (20 words max)
- Key findings (5-10 bullets)
- Implications for reference files
- Open questions

This forces distillation. If you can't summarize it, you don't understand it yet.

---

## Next Step

Got a question you've been wrestling with? Run `/think` on it. Even if you don't complete the full cycle, the research alone will clarify your thinking.

The habit of documenting your thinking is what makes Main Branch powerful over time.
