# Organic Skill Help

Help for the `/organic` skill -- generating organic content scripts from your reference files and research.

---

## First-Time Setup

Before using `/organic`, you need three files in your business repo:

| File | What It Contains |
|------|------------------|
| `reference/core/voice.md` | How you sound on camera |
| `reference/core/audience.md` | Who watches your content |
| `reference/core/offer.md` | What you do/sell |

**Don't have these?** Run `/setup` first.

**Want to mine competitors first?** Use `/think` to research competitor content. Mining saves to `research/`, then `/organic` generates from that research.

---

## What is /organic?

The `/organic` skill generates organic content scripts from your reference files and any research you've already saved:

1. **Generate scripts** -- Create Reels, TikTok, and carousel content in your voice
2. **Apply winning concepts** -- Use hooks, structures, and angles from research you've done via `/think`
3. **Stay on-brand** -- Every script draws from your voice.md, audience.md, and offer.md

It's for **organic content** (free reach), not **paid ads** (use `/ads` for ads).

**Note:** Mining (competitor analysis, content extraction) happens in `/think`, not `/organic`. Run `/think` first to research competitors, then `/organic` to generate from that research.

---

## When to Use /organic

Use `/organic` when you want to:

- Generate Reels or TikTok video scripts
- Create carousel content
- Write captions for static posts
- Turn research (from `/think`) into ready-to-shoot scripts

---

## Modes

### Full Flow: `/organic`

The complete generation workflow:
1. Review your reference files and any saved research
2. Identify winning concepts and angles
3. Generate scripts in your voice

### Video: `/organic video "topic"`

Generate a Reels/TikTok script:
- From a concept in your saved research
- From a topic you provide
- Applies your voice from `reference/core/voice.md`

### Carousel: `/organic carousel "topic"`

Generate multi-slide carousel:
- 7-10 slides by default
- Hook slide, value slides, CTA slide
- Ready to design

### Static: `/organic static "topic"`

Generate single-post caption:
- Hook line, body, soft CTA
- Matches your voice
- Hashtag suggestions included

---

## How It Differs from /ads video

| Aspect | /ads video | /organic |
|--------|------------|----------|
| **Purpose** | Paid traffic conversion | Organic reach |
| **Tone** | Direct response, urgency | Value-first, authentic |
| **CTA** | Hard (buy now, link in bio) | Soft (save, follow, comment) |
| **Framework** | AIDA, PAS | Hook-Retain-Reward |
| **Goal** | Clicks and sales | Views, saves, follows |

**Rule of thumb:**
- Spending money to show it? → `/ads video`
- Posting to your feed? → `/organic`

---

## Required Reference Files

The skill needs these files in your business repo:

| File | Required? | Purpose |
|------|-----------|---------|
| `reference/core/offer.md` | Yes | Context for CTAs |
| `reference/core/audience.md` | Yes | Who you're creating for |
| `reference/core/voice.md` | Yes | How you sound on camera |
| `research/*.md` | No | Saved research from `/think` (competitor mining, content ideas) |

If missing core files, run `/setup` first.

---

## Common Questions

### "How do I research competitors first?"

Use `/think` to mine competitor content before generating. The research flow:

1. `/think` -- research competitor accounts, extract winning concepts
2. Research saves to `research/` folder
3. `/organic` -- generates scripts informed by that research

Look for 3-5 accounts: direct competitors (same offer, same audience), adjacent creators (similar audience, different offer), and aspirational accounts (bigger creators you admire).

### "What makes content 'top performing'?"

Engagement rate = (likes + comments) / followers

Top 10-20% by engagement rate are "winners" worth studying.

### "Can I use the exact hooks I find?"

No. Adapt the PATTERN, not the words.

**Example:**
- Competitor hook: "3 things I wish I knew before starting my agency"
- Your adaptation: "3 things I wish I knew before my first launch"

Same structure. Different words. Your topic.

### "How is voice applied?"

The skill reads `reference/core/voice.md` and:
- Matches your tone (casual, professional, energetic)
- Uses your vocabulary
- Avoids your "never say" phrases
- Adds your verbal quirks

The more detailed your voice file, the better the output.

### "What if my content feels generic?"

Usually means:
1. Voice file is too thin → Run `/think codify` to add more
2. Topic is too broad → Be more specific
3. Missing personal examples → Add stories to your reference

### "Can I save winning angles I discover?"

Yes. Route to `/think codify` to add them to `reference/proof/angles/`.

This makes them available for future generations across all skills.

---

## Workflow Example

```
1. /think (mine competitors)
   → Competitor data extracted
   → Top 15 concepts identified
   → Saved to research/

2. /organic video "concept from research"
   → Script generated in your voice
   → Saved to outputs/

3. Repeat for carousel, static as needed

4. (Optional) /think codify
   → Save best angles to reference
```

---

## Troubleshooting

### "Apify isn't working"

**Check 1: Is it installed?**
Type `/mcp` - you should see `apify` in the list.

**Check 2: Did you restart Claude?**
MCPs only load at startup. Type `/exit`, then `claude --continue`.

**Check 3: Is your token valid?**
Check apify.com → Settings → API & Integrations.

**Fallback:** Share screenshots manually if Apify won't cooperate.

See `organic/references/apify-setup.md` for full Apify installation and configuration.

### "Mining used a lot of tokens"

Mining happens through `/think`, not `/organic`. Each competitor uses ~3-5k tokens. To reduce:
- Mine fewer competitors (2-3 instead of 5)
- Use "quick scan" (fewer posts per competitor)

### "Output doesn't sound like me"

Check `reference/core/voice.md`:
- Is it detailed enough?
- Does it have examples of how you talk?
- Does it list phrases to avoid?

Run `/think codify` to add more voice context.

### "I don't know what to create about"

Run `/think` first to mine competitors or brainstorm content ideas. Research saves to `research/`, then `/organic` generates from that research.

Or run `/think research "content ideas for [your niche]"` to brainstorm.

---

## Related Skills

| Skill | When to Use Instead |
|-------|---------------------|
| `/ads video` | Paid video ads |
| `/ads static` | Paid image ads |
| `/think` | Researching content strategy |
| `/think codify` | Adding more voice/context (see `think/references/codify-phase.md`) |
