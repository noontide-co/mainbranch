# Context Gathering Guide

Be a ruthless journalist. Extract every fact possible. Don't settle for partial information.

---

## URL Fetching Fallback Chain

Try in this order:

1. **WebFetch** — Fast, simple, try first
2. **Chrome Extension** — If WebFetch fails (403, blocked), use `mcp__claude-in-chrome__*` tools
3. **Playwright** — If no Chrome, offer to open with Playwright
4. **Manual paste** — Last resort: ask user to copy/paste content

---

## Skool Community Checklist

For Skool businesses, gather ALL of these before creating files:

| Item | How to Get | Why Needed |
|------|------------|------------|
| About page | URL or screenshot | Offer, positioning, owner story |
| **Plans page** | Auto-fetch `skool.com/{community}/plans` | Pricing tiers, what's included per tier |
| **Dashboard** | Settings → Dashboard screenshots (all 4 tabs) | Business health metrics |
| Classroom structure | Screenshot of classroom tab | Course catalog for domain/ |
| Course modules | Screenshots of individual courses | Curriculum depth |
| **Calendar** | Screenshot + brain dump explanation | Events, calls, rhythm |
| Community feed | Screenshots of high-engagement posts | Voice, topics, engagement |
| Member wins/testimonials | Screenshots from feed | Social proof |
| Video transcripts | Ask for specific videos you see | Teaching style, key phrases |
| Owner bio/credentials | About page | Authority positioning |
| Client calls/emails | Any recordings or threads | Voice, objection handling |

**Auto-fetch the plans page:**
```
https://www.skool.com/{community-slug}/plans
```
This reveals pricing tiers. Single-tier communities may show minimal info, but multi-tier communities expose the full offer stack.

**Prompts to use:**

If videos visible on about page:
> "I see videos on your about page. Do you have transcripts for those? Video content is gold for capturing your teaching style and key phrases."

If no classroom screenshots:
> "Screenshot your Classroom tab — I need the course structure to document your curriculum."

If no calendar:
> "Screenshot your Calendar tab, then brain dump what each event type is for — coaching calls, Q&As, challenges, etc."

If no testimonials yet:
> "Any member wins or testimonials? Screenshots from the community feed work great."

If no dashboard yet:
> "Click the Settings gear icon, then Dashboard. Screenshot the overview, then click each of the 4 metrics (Members, MRR, Conversion, Retention) and screenshot those too. This helps me understand your business health."

**Also valuable:**
- Client call recordings or transcripts
- Email threads with members
- DMs that show common questions/objections
- Anything that captures how you actually talk to members

---

## Open-Ended Discovery Questions

After gathering the structured items, ask these to surface context only the owner knows:

**History & Context:**
> "What's the backstory? Did you have an offer before Skool? How long have you been doing this?"

**Goals:**
> "What are your goals for this community? Revenue targets? Member count? Something else?"

**What makes you different:**
> "What do members get from you that they can't get elsewhere? What's your unfair advantage?"

**Current challenges:**
> "What's working well right now? What's frustrating you or not working?"

**Anything else:**
> "Anything else I should know? Special context, upcoming launches, experiments you're running, changes you're planning?"

These questions often surface the most valuable positioning and messaging insights.

---

## E-commerce Checklist

| Item | How to Get | Why Needed |
|------|------------|------------|
| Product pages | URLs or screenshots | Product details, benefits |
| About/story page | URL | Brand voice, origin story |
| Reviews | Screenshots or exports | Social proof, language |
| Pricing/collections | Screenshots | Product structure |
| Email examples | Forwarded or pasted | Voice, promotions |

---

## Coaching/Services Checklist

| Item | How to Get | Why Needed |
|------|------------|------------|
| Sales page | URL | Offer, transformation |
| Application/intake form | Screenshot | Qualification criteria |
| Case studies | Documents or URLs | Proof, process |
| Call recordings/transcripts | Files | Voice, objection handling |
| Testimonials | Screenshots or text | Social proof |

---

## Completeness Criteria

Only say "we have enough" when you can fill:

| File | Minimum Required |
|------|------------------|
| offer.md | Price, mechanism, deliverables, guarantee |
| audience.md | Who, pains, desires, objections |
| voice.md | Tone, phrases, personality markers |
| testimonials.md | 3-5 testimonials with specific outcomes |
| domain/ | Business-type specific structure |

After each batch of content, assess gaps:
> "Got it. I still need [X, Y, Z] to complete your reference files. Can you share those?"

Keep asking until YOU determine completeness. Users will provide in batches — that's normal.
