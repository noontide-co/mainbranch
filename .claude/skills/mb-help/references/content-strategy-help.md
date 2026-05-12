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
core/
└── content-strategy.md
```

It lives at top-level `core/content-strategy.md` beside `soul.md`,
`offer.md`, `audience.md`, and `voice.md`.

**Why top-level core?** Content strategy is brand-level evergreen strategy. It
connects the business's soul, offer, audience, and voice to distribution
choices: pillars, platforms, cadence, hooks, and metrics. It is not an
operations file. Use `core/operations/` for delivery systems like classroom,
membership, funnel, and fulfillment.

You still need enough core file context before a content strategy makes sense.
The file usually emerges through `/mb-think` cycles after the operator has
some real content experience: what platforms they like, what topics land, and
what hooks work.

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

You build content-strategy.md through `/mb-think` cycles, not all at once. The recommended path:

1. **Start with pillars.** Run `/mb-think` and say "I want to build my content strategy." Claude will guide you to derive 3-5 pillars from your soul.md + offer.md + audience.md.

2. **Choose platforms.** Research where your audience actually is. Decide which platforms to prioritize. Codify into the Platform Strategy section.

3. **Set a cadence.** Decide how often you publish, on which days, in what formats. Start simple -- you can always add more.

4. **Fill in over time.** The Hooks Library, Framework Library, and Metrics sections grow as you create content and learn what works. They are not filled upfront.

Each step is a `/mb-think` cycle: research, decide, codify into content-strategy.md. See `mb-think/references/codify-phase.md` for the full codify workflow, including the Content Strategy Updates section.

---

## What are the 9 sections?

| Section | What It Contains | When It Gets Filled |
|---------|-----------------|---------------------|
| **Content Pillars** | 3-5 themes with sub-topics | First `/mb-think` cycle |
| **Platform Strategy** | Priority-ordered platforms with format, cadence, purpose | Early -- after choosing platforms |
| **Content Mix** | Ratios: educational / entertaining / community / promotional | Early -- starting suggestion 50/25/15/10 |
| **Weekly Cadence** | Day-by-day plan for what content type and platform | After platforms and pillars are set |
| **Repurposing Flow** | Keystone piece to derivative content flow | After you have a keystone format (usually newsletter) |
| **Content Genotype Defaults** | Preferred formats, durations, hook styles, variables to test | After some content creation experience |
| **Metrics** | PRP benchmarks per platform, review cadence | After 2-4 weeks of publishing |
| **Framework Library** | Proven frameworks extracted via mining | Grows over time from `/mb-organic` mining |
| **Hooks Library** | Hooks that work, organized by type | Grows over time from what performs |

You do not need all 9 sections filled to start creating content. Pillars + Platform Strategy + Content Mix is enough to begin.

---

## How do skills use it?

| Skill | How It Reads content-strategy.md |
|-------|----------------------------------|
| `/mb-organic` | Suggests topics aligned to defined pillars. Uses platform format from Platform Strategy. Pulls hooks from Hooks Library. |
| `/mb-ads` | Uses pillars to inform angle selection. Uses metrics to identify top organic performers for paid amplification. |
| Planned newsletter workflow | Would use pillars for topic selection and the Repurposing Flow to map the email to derivative content. Today, use `/mb-think` to plan it and `/mb-organic` to repurpose it. |
| `/mb-think` | Writes to content-strategy.md during the codify phase. This is the primary tool for building and updating the file. |

If content-strategy.md does not exist, all skills work exactly as they did before. The integration is additive -- it improves output quality but is never required. See `organic/SKILL.md` for how `/mb-organic` reads content-strategy.md during script generation.

---

## What is the two-pillar value prop?

Main Branch delivers two kinds of value:

1. **Ads and conversion surfaces that convert** -- immediate ROI through `/mb-ads` and `/mb-site`, with `/mb-vsl` kept only as a compatibility router. Reference files make ads and sales videos specific, compliant, and high-converting.

2. **Content that runs itself** -- long game through content strategy, `/mb-organic`, and planned newsletter workflows. One keystone piece gets adapted across platforms automatically.

Both pillars are powered by the same reference files. The better your reference, the better both your ads and your content.

---

## What is the keystone-first waterfall?

The content pipeline flows from one keystone piece to many derivatives:

```
Keystone piece (email, article, or long-form note)
    |
    v
/mb-organic --> Platform-adapted social content
    |         (Reels, TikTok, carousels, threads)
    v
/mb-ads --> Paid amplification of top performers
    |
    v
/mb-think --> Performance analysis, strategy updates
    |       (what worked? update hooks library, metrics)
    v
Loop back to the next keystone piece
```

**Why keystone-first?** Writing one thoughtful piece per week is sustainable.
AI adapts it for every platform. You never open a social media app to post --
the system handles distribution.

**What if I do not have an email list yet?** You can still use `/mb-organic`
to create standalone content. An email or newsletter can become the keystone
later, but it is not required. Use `/mb-think` to build your content strategy
now.

---

## Common Questions

**Q: Do I need content-strategy.md to use /mb-organic?**
No. `/mb-organic` works without it. But with it, your content is strategically aligned instead of ad hoc.

**Q: Can I skip straight to content-strategy.md without core files?**
Not recommended. Your pillars derive from soul + offer + audience. Without those, your pillars will be generic. Build core files first.

**Q: How often should I update content-strategy.md?**
- Hooks Library and Framework Library: weekly (as you discover what works)
- Metrics: monthly (review performance)
- Pillars: quarterly (or when your offer fundamentally changes)
- Platform Strategy: when you add or drop a platform

**Q: What if I only do ads, not content?**
Content-strategy.md is optional. If you only use `/mb-ads` and `/mb-site` for direct conversion work, you do not need it. It becomes valuable when you start doing organic content or a newsletter.

**Q: Is there a bundled newsletter skill yet?**
Not yet. Newsletter infrastructure such as Beehiiv is a future workflow. For
now, use `/mb-think` to build your content strategy and `/mb-organic` to create
social content.
