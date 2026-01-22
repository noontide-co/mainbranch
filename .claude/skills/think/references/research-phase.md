# Research Phase

Detailed workflow for research mode in `/think`.

---

## Workflow

1. **Define the question** — What specifically are you trying to learn?
2. **Identify sources** — Codebase, web, user input
3. **Gather findings** — Spawn subagents for parallel research when useful
4. **Synthesize** (required) — Distill findings into actionable insight
5. **Save** — Write to `research/YYYY-MM-DD-topic-[source].md`

---

## Defining Good Questions

**Good research questions:**
- "What pricing tier structure should we use?"
- "Which messaging angle resonates with cold traffic?"
- "Should we add a guarantee? What kind?"

**Bad questions (too vague):**
- "How do I grow?"
- "What should I do next?"

---

## Source Suffixes

| Suffix | Source |
|--------|--------|
| `-gemini.md` | Gemini deep research |
| `-gpt.md` | ChatGPT research |
| `-claude-code.md` | This Claude Code session |
| `-claude-web.md` | Claude.ai web interface |
| `-mining.md` | Data mining (internal: reviews, emails | external: Apify, scrapers) |
| `-audit.md` | Site or system audit |
| (none) | General or mixed sources |

---

## Sources to Check

1. **Codebase** — Existing reference files, past decisions, research
2. **Web** — Competitors, industry benchmarks, expert perspectives
3. **User input** — "What else do you know about this?"

---

## Writing Good Synthesis

Every research output MUST have a synthesis section. This forces distillation.

**The rule:** If you can't synthesize it, you don't understand it.

### One-Sentence Summary

The hardest part. Forces clarity.

**Constraints:**
- **20 words maximum** — Not 21. Not "about 20."
- **One sentence** — Period at the end. No semicolons connecting two thoughts.
- **Actionable insight** — Not a description of what you researched.

**Bad:**
> "We researched competitor pricing strategies and found various approaches."

Problems: Describes research, not finding. Says nothing actionable.

**Good:**
> "Three-tier pricing with free/paid/premium maximizes reach while creating natural upgrade paths."

Why it works: Specific structure, specific benefit, 14 words.

### Key Findings

**Constraints:**
- **5-10 bullets** — Not 4. Not 11.
- **15 words each maximum** — Forces precision.
- **Facts, not opinions** — "Competitors charge $47-147" not "Competitors are reasonable."

Each finding should stand alone. Someone reading just the bullets should understand the research.

**Include:** Data points with numbers, patterns across sources, surprises, direct quotes.
**Exclude:** Background information, methodology details, tangential findings, speculation.

### Implications for Reference Files

Makes research actionable. Without it, research becomes orphaned knowledge.

For each finding, ask: "Does this change anything in my reference files?"

| File | Potential Update |
|------|------------------|
| `reference/core/offer.md` | Add tier structure, update pricing |
| `reference/core/audience.md` | Segment by tier |

**Bad:** "Update offer.md"
**Good:** "Update offer.md — Add three-tier pricing with benefits per tier"

### Open Questions

Research rarely answers everything. Document what you still don't know.

**Good:** "What should the free tier include to create desire for paid?"
**Bad:** "How do we make more money?" (too vague)

Each open question is a potential next research session.

---

## Synthesis Checklist

Before marking research as complete:

- [ ] One-sentence summary is under 20 words
- [ ] Summary states an insight, not a description
- [ ] 5-10 key findings, each under 15 words
- [ ] Findings are facts, not opinions
- [ ] Each finding could stand alone
- [ ] Implications section maps to specific reference files
- [ ] Open questions identify follow-up research needs
- [ ] Someone could read just the synthesis and understand the research

---

## Exit Criteria

Research is complete when:

- [ ] Research question answered
- [ ] Synthesis section completed
- [ ] Key findings extracted (5-10 bullets)
- [ ] Open questions documented
- [ ] File saved to `research/`

---

## Template

See [templates/research-template.md](templates/research-template.md) for full file structure.
