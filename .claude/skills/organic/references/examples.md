# Organic Skill Examples

## Example 1: Context-Aware Start

```
User: /organic

Claude: Found ac-repo. Checking existing work...

Today's mining exists (3 competitors, 10 concepts).
Scripts generated: 2 of 10 concepts used.

1. Generate from remaining 8 concepts
2. Mine new competitors → `/think`
3. Give me a fresh topic

User: 1

Claude: [Shows concepts, user picks, generates with voice.md]
```

## Example 2: Video Only

```
User: /organic video "how I structure my morning routine"

Claude: What framework fits this best?
- Educational (tips and steps)
- Story-based (your journey)
- Transformation (before/after)

User: Story-based

Claude: What should we call this batch? (e.g., "morning-routine", "productivity-series")

User: morning-routine

Claude: [Generates script using story framework]
[Saves to outputs/2026-01-26-organic-morning-routine/organic-batch-001.md]

Saved to outputs/2026-01-26-organic-morning-routine/organic-batch-001.md
Want me to commit this to git?
```

## Example 3: Mining Redirect

```
User: /organic mine

Claude: Mining is research work now — it lives in `/think` so your mined
concepts go to `research/` and can feed your reference files.

Switching you to `/think` for mining. Once you've got concepts, come back
to `/organic` to generate scripts from them.

[Routes to /think]
```

## Recovering from Compaction

When conversations get long, Claude's memory compresses. If mid-/organic and this happens:

**For the user:** Just type `/organic` again and describe where you were:

- "We were mining @competitor1 and @competitor2"
- "I was picking concepts from today's mining"
- "Generate a video script from the morning routine concept"

**For Claude:** When resuming:

1. Check `research/*-competitor-mine.md` for recent mining
2. Check `outputs/*-organic-*/` for existing scripts
3. Confirm with user: "I see today's mining has X concepts. Want to continue generating from those?"
