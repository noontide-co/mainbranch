# Content Skill Help

Help for the `/content` skill - mining competitors and generating organic content scripts.

---

## What is /content?

The `/content` skill helps you:

1. **Mine competitor content** - Find what's working for others in your niche
2. **Extract winning concepts** - Identify hooks, structures, and angles that perform
3. **Generate scripts** - Create Reels, TikTok, and carousel content in your voice

It's for **organic content** (free reach), not **paid ads** (use `/ad-video-scripts` for ads).

---

## When to Use /content

Use `/content` when you want to:

- Research what's working for competitors
- Get ideas for Reels or TikTok videos
- Create carousel content
- Write captions for static posts
- Find proven angles to adapt

---

## Modes

### Full Flow: `/content`

The complete workflow:
1. Identify competitors
2. Mine their top content
3. Extract winning concepts
4. Generate scripts in your voice

### Mine Only: `/content mine`

Just research, no script generation:
- Extracts competitor content data
- Identifies top performers
- Saves research to `research/` folder
- Use when you want ideas but will generate later

### Video: `/content video "topic"`

Generate a Reels/TikTok script:
- From a mined concept
- From a topic you provide
- Applies your voice from `reference/core/voice.md`

### Carousel: `/content carousel "topic"`

Generate multi-slide carousel:
- 7-10 slides by default
- Hook slide, value slides, CTA slide
- Ready to design

### Static: `/content static "topic"`

Generate single-post caption:
- Hook line, body, soft CTA
- Matches your voice
- Hashtag suggestions included

---

## How It Differs from /ad-video-scripts

| Aspect | /ad-video-scripts | /content |
|--------|-------------------|----------|
| **Purpose** | Paid traffic conversion | Organic reach |
| **Tone** | Direct response, urgency | Value-first, authentic |
| **CTA** | Hard (buy now, link in bio) | Soft (save, follow, comment) |
| **Framework** | AIDA, PAS | Hook-Retain-Reward |
| **Goal** | Clicks and sales | Views, saves, follows |

**Rule of thumb:**
- Spending money to show it? → `/ad-video-scripts`
- Posting to your feed? → `/content`

---

## Required Reference Files

The skill needs these files in your business repo:

| File | Required? | Purpose |
|------|-----------|---------|
| `reference/core/offer.md` | Yes | Context for CTAs |
| `reference/core/audience.md` | Yes | Who you're creating for |
| `reference/core/voice.md` | Yes | How you sound on camera |
| `reference/competitors/handles.md` | No | List of competitors to mine |

If missing core files, run `/setup` first.

---

## Common Questions

### "How do I know which competitors to mine?"

Look for:
- **Direct competitors** - Same offer, same audience
- **Adjacent creators** - Similar audience, different offer
- **Aspirational accounts** - Bigger creators you admire

You want 3-5 accounts minimum. Save them in `reference/competitors/handles.md`.

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
1. Voice file is too thin → Run `/enrich` to add more
2. Topic is too broad → Be more specific
3. Missing personal examples → Add stories to your reference

### "Can I save winning angles I discover?"

Yes. Route to `/think codify` to add them to `reference/proof/angles/`.

This makes them available for future generations across all skills.

---

## Workflow Example

```
1. /content mine
   → Competitor data extracted
   → Top 15 concepts identified
   → Saved to research/

2. Review concepts with Claude
   → Select 5 to adapt

3. /content video "concept 1"
   → Script generated in your voice
   → Saved to outputs/

4. Repeat for carousel, static as needed

5. (Optional) /think codify
   → Save best angles to reference
```

---

## Troubleshooting

### "Apify isn't working"

The skill can work without Apify. Share:
- Screenshots of top posts
- URLs to content you want to study
- Notes on what you observed

### "Output doesn't sound like me"

Check `reference/core/voice.md`:
- Is it detailed enough?
- Does it have examples of how you talk?
- Does it list phrases to avoid?

Run `/enrich` to add more voice context.

### "I don't know what to create about"

Run `/content mine` first. Let competitor research inspire topics.

Or run `/think research "content ideas for [your niche]"` to brainstorm.

---

## Related Skills

| Skill | When to Use Instead |
|-------|---------------------|
| `/ad-video-scripts` | Paid video ads |
| `/ad-static` | Paid image ads |
| `/think` | Researching content strategy |
| `/enrich` | Adding more voice/context |
