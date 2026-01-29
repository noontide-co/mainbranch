# Content Strategy Help

Answers to common questions about content-strategy.md and the content pipeline.

---

## What is content-strategy.md?

Your distribution backbone. It defines:
- **What** you talk about (content pillars)
- **Where** you publish (platform strategy)
- **When** you publish (weekly cadence)
- **How much** of each type (content mix ratios)
- **What works** (hooks library, framework library, metrics)

It is a reference file that skills read when generating content. Without it, skills still work -- they just lack strategic alignment.

---

## Where does it live?

```
reference/
└── domain/
    └── content-strategy.md
```

It lives in `reference/domain/`, not `reference/core/`. Core files (soul, offer, audience, voice) are required for every business. Content strategy is domain-level -- it emerges over time through `/think` cycles, not at setup.

**Why domain and not core?** You need to have your core reference solid before a content strategy makes sense. You also need some real content experience (what platforms you like, what topics land, what hooks work) before you can codify a strategy. It is emergent, not foundational.

---

## How does it relate to other reference files?

| File | Answers | Relationship to Content Strategy |
|------|---------|----------------------------------|
| soul.md | WHY you exist | Pillars must connect to your soul (Soul test) |
| offer.md | WHAT you sell | Pillars must lead toward your mechanism (Offer test) |
| audience.md | WHO you serve | Pillars must address what your audience cares about (Audience test) |
| voice.md | HOW you sound | Content tone and personality come from voice |
| content-strategy.md | WHERE and WHEN | Distribution strategy informed by all four core files |

Content strategy sits downstream of all four core files. If your core changes, your content strategy may need updating too.

---

## How do I build it?

You build content-strategy.md through `/think` cycles, not all at once. The recommended path:

1. **Start with pillars.** Run `/think` and say "I want to build my content strategy." Claude will guide you to derive 3-5 pillars from your soul.md + offer.md + audience.md.

2. **Choose platforms.** Research where your audience actually is. Decide which platforms to prioritize. Codify into the Platform Strategy section.

3. **Set a cadence.** Decide how often you publish, on which days, in what formats. Start simple -- you can always add more.

4. **Fill in over time.** The Hooks Library, Framework Library, and Metrics sections grow as you create content and learn what works. They are not filled upfront.

Each step is a `/think` cycle: research, decide, codify into content-strategy.md. See `think/references/codify-phase.md` for the full codify workflow, including the Content Strategy Updates section.

---

## What are the 9 sections?

| Section | What It Contains | When It Gets Filled |
|---------|-----------------|---------------------|
| **Content Pillars** | 3-5 themes with sub-topics | First `/think` cycle |
| **Platform Strategy** | Priority-ordered platforms with format, cadence, purpose | Early -- after choosing platforms |
| **Content Mix** | Ratios: educational / entertaining / community / promotional | Early -- starting suggestion 50/25/15/10 |
| **Weekly Cadence** | Day-by-day plan for what content type and platform | After platforms and pillars are set |
| **Repurposing Flow** | Keystone piece to derivative content flow | After you have a keystone format (usually newsletter) |
| **Content Genotype Defaults** | Preferred formats, durations, hook styles, variables to test | After some content creation experience |
| **Metrics** | PRP benchmarks per platform, review cadence | After 2-4 weeks of publishing |
| **Framework Library** | Proven frameworks extracted via mining | Grows over time from `/organic` mining |
| **Hooks Library** | Hooks that work, organized by type | Grows over time from what performs |

You do not need all 9 sections filled to start creating content. Pillars + Platform Strategy + Content Mix is enough to begin.

---

## How do skills use it?

| Skill | How It Reads content-strategy.md |
|-------|----------------------------------|
| `/organic` | Suggests topics aligned to defined pillars. Uses platform format from Platform Strategy. Pulls hooks from Hooks Library. |
| `/ads` | Uses pillars to inform angle selection. Uses metrics to identify top organic performers for paid amplification. |
| `/newsletter` | Uses pillars for topic selection. Uses Repurposing Flow to map newsletter to derivative content. (Coming soon.) |
| `/think` | Writes to content-strategy.md during the codify phase. This is the primary tool for building and updating the file. |

If content-strategy.md does not exist, all skills work exactly as they did before. The integration is additive -- it improves output quality but is never required. See `organic/SKILL.md` for how `/organic` reads content-strategy.md during script generation.

---

## What is the two-pillar value prop?

Main Branch delivers two kinds of value:

1. **Ads that convert** -- immediate ROI through `/ads` and `/vsl`. Reference files make ads specific, compliant, and high-converting.

2. **Content that runs itself** -- long game through content strategy, `/organic`, and eventually `/newsletter`. One keystone piece (newsletter) gets adapted across platforms automatically.

Both pillars are powered by the same reference files. The better your reference, the better both your ads and your content.

---

## What is the newsletter-first waterfall?

The content pipeline flows from one keystone piece to many derivatives:

```
Newsletter (keystone, weekly)
    |
    v
/organic --> Platform-adapted social content
    |         (Reels, TikTok, carousels, threads)
    v
/ads --> Paid amplification of top performers
    |
    v
/think --> Performance analysis, strategy updates
    |       (what worked? update hooks library, metrics)
    v
Loop back to newsletter
```

**Why newsletter-first?** Writing one thoughtful piece per week is sustainable. AI adapts it for every platform. You never open a social media app to post -- the system handles distribution.

**What if I do not have a newsletter yet?** You can still use `/organic` to create standalone content. The newsletter is the ideal keystone, but it is not required. Use `/think` to build your content strategy now; add the newsletter when you are ready.

---

## Common Questions

**Q: Do I need content-strategy.md to use /organic?**
No. `/organic` works without it. But with it, your content is strategically aligned instead of ad hoc.

**Q: Can I skip straight to content-strategy.md without core reference?**
Not recommended. Your pillars derive from soul + offer + audience. Without those, your pillars will be generic. Build core reference first.

**Q: How often should I update content-strategy.md?**
- Hooks Library and Framework Library: weekly (as you discover what works)
- Metrics: monthly (review performance)
- Pillars: quarterly (or when your offer fundamentally changes)
- Platform Strategy: when you add or drop a platform

**Q: What if I only do ads, not content?**
Content-strategy.md is optional. If you only use `/ads` and `/vsl`, you do not need it. It becomes valuable when you start doing organic content or a newsletter.

**Q: Is /newsletter available yet?**
Not yet. It is coming soon and requires newsletter infrastructure (Beehiiv or similar). For now, use `/think` to build your content strategy and `/organic` to create social content. When `/newsletter` launches, your content-strategy.md will already be ready for it.
