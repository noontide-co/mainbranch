# Skool Community Help

If you're running a Skool community, Main Branch has specific support for your business type.

---

## Business Type: Community

When you run `/setup` and select "Community/Skool," your repo gets structured for community-based businesses:

```
reference/domain/
├── classroom/       # Course content structure
├── membership/      # Tiers, pricing, access levels
└── funnel/          # How members find and join
```

---

## Skool-Specific Skills

### /skool-manager

Manage community engagement directly from Claude Code.

**What it does:**
- Check your Skool feed for new posts
- Draft responses that match your voice
- Daily community management rounds

**Requires:** Chrome extension connected to your Skool login.

### /skool-vsl-scripts

Write Video Sales Letters for your community.

**What it does:**
- Uses the 18-section VSL framework
- Creates scripts for about page videos
- Optimized for community sales

---

## Classroom Structure

If you have courses in your Skool classroom, document them in:

```
reference/domain/classroom/
├── courses/
│   └── [course-name]/
│       ├── course.md          # Overview
│       └── folders/
│           └── [folder-name]/
│               ├── folder.md
│               └── pages/
│                   └── [page].md
```

This structure mirrors Skool's hierarchy: Course → Folder → Page.

---

## Membership Tiers

Document your membership structure in:

```
reference/domain/membership/
├── tiers.md         # Free, paid, VIP, etc.
├── pricing.md       # What each tier costs
└── access.md        # What each tier gets
```

---

## Funnel Documentation

How do people find and join your community?

```
reference/domain/funnel/
├── traffic.md       # Where members come from
├── landing.md       # Landing page messaging
└── onboarding.md    # First 7 days experience
```

---

## Common Skool Questions

### "How do I sync my classroom content?"

Currently manual. Document your classroom structure in reference/domain/classroom/.

Future: We're building automation to sync classroom content directly.

### "Can Claude post in my community?"

With Chrome extension: Yes, /skool-manager can help draft and post responses.

Without extension: Claude can draft responses, you copy-paste them.

### "How do I use my community content for ads?"

1. Document your best testimonials in reference/proof/testimonials.md
2. Document winning messaging in reference/proof/angles/
3. Run `/ad-static` or `/ad-video-scripts`
4. Skills read your community context automatically

---

## Skool + Main Branch Philosophy

Your community IS your business context.

- Member questions reveal pain points → audience.md
- Success stories become testimonials → testimonials.md
- Popular content shows what resonates → angles/
- Objections in DMs inform → audience.md objections

Feed learnings from your community back into reference files. This is the compound knowledge loop in action.

---

## Browser Automation Note

We're evaluating different browser automation approaches:
- Chrome extension (current)
- Vercel agent-browser (testing)
- Playwright (fallback)

For now, the Chrome extension is the simplest path. Install it at https://claude.ai/chrome

---

## Next Step

If you haven't documented your Skool structure yet, run `/enrich` and tell Claude about your classroom, membership tiers, and funnel.

The more Skool context in your reference files, the better your community-focused outputs will be.
