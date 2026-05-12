# Organic Skill Help

Help for the `/mb-organic` skill -- generating organic content scripts from your reference files and research.

---

## First-Time Setup

Before using `/mb-organic`, you need three files in your business repo:

| File | What It Contains |
|------|------------------|
| `core/voice.md` | How you sound on camera |
| `core/audience.md` | Who watches your content |
| `core/offer.md` | What you do/sell |

**Don't have these?** Run `/mb-setup` first.

Recommended when available:

| File | What It Adds |
|------|--------------|
| `core/content-strategy.md` | Recognition target, pillars, asset jobs, and non-publishing rules |
| `core/marketing/channels/<channel>.md` | Platform norms, timing, content fit, and update triggers |
| `core/marketing/accounts/<platform>-<account>.md` | Account-specific audience, CTA path, cadence, and allowed topics |
| `core/people/<person>.md` | Founder/person beliefs, stories, voice source material, and fabrication boundaries |

**Want to mine competitors first?** Use `/mb-think` to research competitor content. Mining saves to `research/`, then `/mb-organic` generates from that research.

---

## What is /mb-organic?

The `/mb-organic` skill generates organic content scripts from your reference files and any research you've already saved:

1. **Generate scripts** -- Create Reels, TikTok, and carousel content in your voice
2. **Apply winning concepts** -- Use hooks, structures, and angles from research you've done via `/mb-think`
3. **Stay on-brand** -- Every script draws from your voice.md, audience.md, and offer.md

It's for **organic content** (free reach), not **paid ads** (use `/mb-ads` for ads).

**Note:** Mining (competitor analysis, content extraction) happens in `/mb-think`, not `/mb-organic`. Run `/mb-think` first to research competitors, then `/mb-organic` to generate from that research.

---

## When to Use /mb-organic

Use `/mb-organic` when you want to:

- Generate Reels or TikTok video scripts
- Create carousel content
- Write captions for static posts
- Turn research (from `/mb-think`) into ready-to-shoot scripts

---

## Modes

### Full Flow: `/mb-organic`

The complete generation workflow:
1. Review your reference files and any saved research
2. Identify winning concepts and angles
3. Generate scripts in your voice

### Video: `/mb-organic video "topic"`

Generate a Reels/TikTok script:
- From a concept in your saved research
- From a topic you provide
- Applies your voice from `core/voice.md`

### Carousel: `/mb-organic carousel "topic"`

Generate multi-slide carousel:
- 7-10 slides by default
- Hook slide, value slides, CTA slide
- Ready to design

### Static: `/mb-organic static "topic"`

Generate single-post caption:
- Hook line, body, soft CTA
- Matches your voice
- Hashtag suggestions included

---

## How It Differs from /mb-ads video

| Aspect | /mb-ads video | /mb-organic |
|--------|------------|----------|
| **Purpose** | Paid traffic conversion | Organic reach |
| **Tone** | Direct response, urgency | Value-first, authentic |
| **CTA** | Hard (buy now, link in bio) | Soft (save, follow, comment) |
| **Framework** | AIDA, PAS | Hook-Retain-Reward |
| **Goal** | Clicks and sales | Views, saves, follows |

**Rule of thumb:**
- Spending money to show it? → `/mb-ads video`
- Posting to your feed? → `/mb-organic`

---

## Required Reference Files

The skill needs these files in your business repo:

| File | Required? | Purpose |
|------|-----------|---------|
| `core/offer.md` | Yes | Context for CTAs |
| `core/audience.md` | Yes | Who you're creating for |
| `core/voice.md` | Yes | How you sound on camera |
| `research/*.md` | No | Saved research from `/mb-think` (competitor mining, content ideas) |

If missing core files, run `/mb-setup` first.

---

## Common Questions

### "How do I research competitors first?"

Use `/mb-think` to mine competitor content before generating. The research flow:

1. `/mb-think` -- research competitor accounts, extract winning concepts
2. Research saves to `research/` folder
3. `/mb-organic` -- generates scripts informed by that research

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

The skill reads `core/voice.md` and:
- Matches your tone (casual, professional, energetic)
- Uses your vocabulary
- Avoids your "never say" phrases
- Adds your verbal quirks

The more detailed your voice file, the better the output.

### "What if my content feels generic?"

Usually means:
1. Voice file is too thin → Run `/mb-think codify` to add more
2. Topic is too broad → Be more specific
3. Missing personal examples → Add stories to your reference

### "Can I save winning angles I discover?"

Yes. Route to `/mb-think codify` to add them to `core/proof/angles/`.

This makes them available for future generations across all skills.

---

## Workflow Example

```
1. /mb-think (mine competitors)
   → Competitor data extracted
   → Top 15 concepts identified
   → Saved to research/

2. /mb-organic video "concept from research"
   → Script generated in your voice
   → Saved to pushes/

3. Repeat for carousel, static as needed

4. (Optional) /mb-think codify
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

Mining happens through `/mb-think`, not `/mb-organic`. Each competitor uses ~3-5k tokens. To reduce:
- Mine fewer competitors (2-3 instead of 5)
- Use "quick scan" (fewer posts per competitor)

### "Output doesn't sound like me"

Check `core/voice.md`:
- Is it detailed enough?
- Does it have examples of how you talk?
- Does it list phrases to avoid?

Run `/mb-think codify` to add more voice context.

### "I don't know what to create about"

Run `/mb-think` first to mine competitors or brainstorm content ideas. Research saves to `research/`, then `/mb-organic` generates from that research.

Or run `/mb-think research "content ideas for [your niche]"` to brainstorm.

---

## Related Skills

| Skill | When to Use Instead |
|-------|---------------------|
| `/mb-ads video` | Paid video ads |
| `/mb-ads static` | Paid image ads |
| `/mb-think` | Researching content, distribution, channel, account, or person voice strategy |
| `/mb-think codify` | Adding more voice/context (see `mb-think/references/codify-phase.md`) |
