# Content Strategy Help

Answers to common questions about the layered content strategy model.

---

## What is content-strategy.md?

Your business-level content strategy and index. It defines:
- **What you want to be known or recommended for**
- **Who** the content is for
- **What** you talk about (content pillars)
- **Why** each asset exists (rank, teach, prove, compare, convert, announce, or start a conversation)
- **Where** more detailed distribution, channel, account, and person files live
- **What not to publish**

It is a reference file that skills read when generating content. Without it, skills still work -- they just lack strategic alignment.

---

## Where does it live?

```
core/
├── content-strategy.md
├── marketing/
│   ├── distribution-strategy.md
│   ├── channels/
│   │   └── x.md
│   └── accounts/
│       └── x-devon.md
└── people/
    └── devon.md
```

Start with `core/content-strategy.md` beside `soul.md`, `offer.md`,
`audience.md`, and `voice.md`. Add the `core/marketing/` and `core/people/`
layers only when the business needs them.

**Why top-level core?** The simple file keeps a solo operator from managing a
folder tree before there is real strategy. It connects soul, offer, audience,
voice, proof, recognition target, content jobs, and distribution choices.

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
| content-strategy.md | WHY/WHAT/WHERE | Business-level content strategy and index |
| marketing/distribution-strategy.md | HOW CHANNELS WORK TOGETHER | Blog, wiki, changelog, email, social, communities, partners, paid amplification |
| marketing/channels/*.md | PLATFORM RULES | Norms, timing, content fit, anti-spam rules, update triggers |
| marketing/accounts/*.md | ACCOUNT STRATEGY | Audience, allowed topics, cadence, CTA path, voice source |
| people/*.md | PERSON VOICE SOURCE | Beliefs, stories, experiences, proof, fabrication boundaries |

Content strategy sits downstream of offer clarity. If the offer, audience,
proof, or voice changes, content strategy may need updating too.

---

## How do I build it?

You build content-strategy.md through `/mb-think` cycles, not all at once. The recommended path:

1. **Start with offer clarity and recognition target.** Run `/mb-think` and say "I want to build my content strategy." Claude should check the offer, audience, proof, and what you want to be known for.

2. **Define pillars and asset jobs.** Derive 3-5 pillars from soul, offer, audience, proof, and buyer language. Name what each asset is for: rank, teach, prove, compare, convert, announce, or start a conversation.

3. **Choose distribution layers.** Decide how owned pages, blog, wiki, changelog, email, social, communities, partners, and paid amplification work together. Keep this in `core/content-strategy.md` until it needs `core/marketing/distribution-strategy.md`.

4. **Split only when needed.** Add `channels/`, `accounts/`, and `people/` files when there are multiple platforms, multiple accounts, or founder/person-specific voice sources.

5. **Fill in over time.** Hooks, frameworks, channel notes, weekly patterns, and metrics grow from research, pushes, and logs. They are not filled upfront.

Each step is a `/mb-think` cycle: research, decide, codify into the right strategy file. See `mb-think/references/codify-phase.md` for the codify workflow.

---

## What is the smallest useful set?

| Layer | Minimum |
| --- | --- |
| `core/content-strategy.md` | Recognition target, audience, offer/category, pillars, asset jobs, non-publishing rules. |
| `core/marketing/distribution-strategy.md` | Optional until more than one channel needs coordination. |
| `core/marketing/channels/<channel>.md` | Optional until platform rules, timing, or norms matter. |
| `core/marketing/accounts/<platform>-<account>.md` | Optional until there are multiple accounts or account-specific CTAs. |
| `core/people/<person>.md` | Optional until a founder/person voice should feed several accounts. |

You do not need every layer to start creating content.

---

## How do skills use it?

| Skill | How It Reads content-strategy.md |
|-------|----------------------------------|
| `/mb-organic` | Reads business strategy, channel/account/person context when present, then drafts content into the current push or output path. |
| `/mb-ads` | Uses pillars to inform angle selection. Uses metrics to identify top organic performers for paid amplification. |
| `/mb-site` | Uses strategy to keep owned pages, wiki, blog, changelog, and conversion surfaces pointed at the same offer and recognition target. |
| `/mb-think` | Writes strategy decisions, research implications, and codified updates into the right content, channel, account, person, research, decision, push, or log file. |

If content strategy files do not exist, all skills work exactly as they did before. The integration is additive.

---

## What is the two-pillar value prop?

Main Branch delivers two kinds of value:

1. **Ads and conversion surfaces that convert** -- immediate ROI through `/mb-ads` and `/mb-site`. Reference files make ads and conversion scripts specific, compliant, and high-converting.

2. **Content that compounds** -- long game through content strategy,
   `/mb-organic`, owned pages, email/newsletter planning, social/community
   distribution, and results logs. One strategy can support many channels
   without copying the same plan into every account file.

Both pillars are powered by the same reference files. The better your reference, the better both your ads and your content.

---

## What is the weekly loop?

Weekly planning reads strategy by reference and writes execution into pushes:

```
Read strategy -> plan this week's queue -> draft content -> review before publishing
-> log results -> update strategy/playbooks when the lesson is durable
```

Specific campaigns, launches, announcements, and distribution pushes belong in
`pushes/<YYYY-MM-DD-slug>/`. Results belong in `log/` or the push review log.

---

## Common Questions

**Q: Do I need content-strategy.md to use /mb-organic?**
No. `/mb-organic` works without it. But with it, your content is strategically aligned instead of ad hoc.

**Q: Can I skip straight to content-strategy.md without core files?**
Not recommended. Your pillars derive from soul + offer + audience. Without those, your pillars will be generic. Build core files first.

**Q: How often should I update content strategy?**
- Channel/account files: when platform norms, audience behavior, or CTA paths change.
- Hooks, frameworks, and learnings: when results or research prove something reusable.
- Pillars and recognition target: when the offer, audience, or category target changes.
- Distribution strategy: when you add/drop channels or change how channels support each other.

**Q: What if I only do ads, not content?**
Content-strategy.md is optional. If you only use `/mb-ads` and `/mb-site` for direct conversion work, you do not need it. It becomes valuable when you start doing organic content or a newsletter.

**Q: Is there a bundled newsletter skill yet?**
Not yet. Newsletter infrastructure such as Beehiiv is a future workflow. For
now, use `/mb-think` to build your content strategy and `/mb-organic` to create
social content.
