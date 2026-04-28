# Section Patterns

> **Applies to: Website (Next.js) shape only.** The minisite shape uses LLM-decided sections per [`minisite-generation-system.md`](minisite-generation-system.md) — no fixed section catalog. Use this file when working in the legacy Next.js Website templates (`saas`, `high-ticket`).

How reference files map to page sections. This is the translation layer Claude uses during `/site build` mode for the Website shape.

---

## How It Works

1. Read reference files from business repo
2. Determine which sections the page needs (based on template + business type)
3. For each section, extract data from the relevant reference files
4. Generate `site-config.ts` entries and component code
5. Compose sections in `app/page.tsx`

---

## Section Library

### hero

**Purpose:** Above-the-fold hook. Headline, subhead, CTA, optional badge/proof.

**Reference sources:** offer.md (headline, value prop, CTA), audience.md (eyebrow framing), testimonials.md (stat badge)

**Data to extract:**
- Headline: The primary transformation or outcome from offer.md
- Subhead: Supporting detail — mechanism or key benefit
- Eyebrow: Audience identifier or category label
- CTA text: Specific action from offer.md
- CTA url: `#pricing`, `#application`, or external link
- Badge: Stat or credibility marker (e.g., "200+ clients" from testimonials)

**Component structure:** Full-viewport section with staggered GSAP reveal. Headline uses SplitType word animation. CTA button with accent color.

**Design notes:** Most important section. Gets the most whitespace. Headline font at maximum scale (`--text-hero`).

---

### reasons-grid

**Purpose:** Name the pain points. Make the visitor feel understood.

**Reference sources:** audience.md (pain points, fears, frustrations)

**Data to extract:**
- 3-4 pain point cards, each with: title, description, optional icon/stat
- Language should mirror how the audience describes their problems

**Component structure:** Grid (2-col desktop, 1-col mobile). Cards with stagger-in animation on scroll.

**Design notes:** Keep copy short. These are recognition moments, not explanations.

---

### process-stepper

**Purpose:** Show how it works. Demystify the mechanism.

**Reference sources:** offer.md (mechanism, process, deliverables)

**Data to extract:**
- 3-5 steps, each with: label, description, optional icon
- Steps should follow the actual customer journey

**Component structure:** Horizontal stepper (desktop) / vertical timeline (mobile). Auto-advancing with click override. Animated connection line between steps.

**Design notes:** This section builds confidence. Keep it simple — complexity here creates doubt.

---

### credibility

**Purpose:** Social proof. Stats, testimonials, trust signals.

**Reference sources:** testimonials.md (quotes, stats, scenarios)

**Data to extract:**
- Stats row: 3-4 key numbers (clients served, years, success rate, etc.)
- Testimonial quotes: 2-3 strongest with name and context
- Optional: founder photo, credentials

**Component structure:** Stats with animated counters (GSAP). Quote cards or full-width quotes.

**Design notes:** Real numbers > vague claims. Named testimonials > anonymous. Specific outcomes > general praise.

---

### competitive-positioning

**Purpose:** Why this vs alternatives.

**Reference sources:** offer.md (differentiators), audience.md (what they've tried)

**Data to extract:**
- 3 competitor types (not named competitors — categories like "DIY", "Agencies", "Other tools")
- For each: what they offer vs what you offer

**Component structure:** 3-column comparison cards with stagger reveal.

**Design notes:** Frame as "them vs us" without being negative. Focus on what you DO differently.

---

### objection-handling

**Purpose:** Address fears before the CTA.

**Reference sources:** audience.md (objections, fears, hesitations)

**Data to extract:**
- 4-6 objections with reframes
- Each: the objection (their voice), the reframe (your voice), optional insight

**Component structure:** Accordion with numbered items. Click to expand.

**Design notes:** Use their exact language for the objection. The reframe should feel like a conversation, not a sales pitch.

---

### faq

**Purpose:** Handle remaining questions.

**Reference sources:** offer.md (pricing, logistics), audience.md (common questions)

**Data to extract:**
- 5-8 Q&A pairs covering: pricing, timeline, what's included, who it's for, guarantee

**Component structure:** Accordion. Same pattern as objection-handling but different content.

**Design notes:** FAQ is the last stop before CTA. Answer the dealbreaker questions here.

---

### cta-simple

**Purpose:** Clean call to action with headline + button.

**Reference sources:** offer.md (CTA text, urgency)

**Data to extract:**
- Headline: Action-oriented (e.g., "Ready to stop losing clients?")
- Button text: Specific action
- Microcopy: Optional reassurance ("No credit card required")

**Component structure:** Centered section with headline, button, and microcopy. Background can be dark/accent for contrast.

---

### cta-application

**Purpose:** Multi-step qualification form for high-ticket offers.

**Reference sources:** audience.md (qualification criteria), offer.md (pricing tiers)

**Data to extract:**
- 4-6 qualification questions (revenue, timeline, investment readiness, etc.)
- Qualification logic (which answers qualify)
- Result messages for qualified vs not qualified

**Component structure:** Step-by-step form with progress bar. Branching logic. Final step shows result.

**Design notes:** Only for high-ticket ($3k+). Lower-priced offers use cta-simple.

---

### examples-grid

**Purpose:** Show concrete use cases.

**Reference sources:** offer.md (use cases, features)

**Data to extract:**
- 4 example cards with title and description
- Each shows a specific thing customers build/achieve

**Component structure:** 2x2 card grid with hover effects.

---

### trust-strip

**Purpose:** Logo bar for social proof.

**Reference sources:** testimonials.md (company names, logos)

**Data to extract:**
- 6-12 company/brand names or logos

**Component structure:** Horizontal row of logos or text wordmarks. Optional marquee animation.

---

### interactive-explorer

**Purpose:** Clickable showcase of features or concepts.

**Reference sources:** offer.md (features, capabilities)

**Data to extract:**
- 4-6 items, each with: key, label, description, detail content

**Component structure:** Left panel with selectable items, right panel shows details. Typing animation on select.

**Design notes:** Great for SaaS products. Less relevant for services.

---

### integration-river

**Purpose:** Show tool/platform integrations.

**Reference sources:** offer.md (integrations, tech stack)

**Data to extract:**
- 20-50 integration names organized in 3 rows

**Component structure:** Multi-row marquee with logo pills. Pause on hover.

**Design notes:** SaaS-specific. Requires logo service (Logo.dev) or SVG assets.

---

### footer

**Purpose:** Brand, contact, legal.

**Data to extract:**
- Brand name, tagline, email, location
- Legal links (privacy, terms)
- Copyright year

**Component structure:** Simple flex layout with contact info.

---

## Template Section Orders

### SaaS Template (from Bolt)

```
Hero → Interactive Explorer → Reasons Grid → Process Stepper →
Examples Grid → Integration River → Trust Strip → CTA Simple → Footer
```

### High-Ticket Template (from LaunchGrid)

```
Hero → Credibility → Reasons Grid → Process Stepper →
Competitive Positioning → Objection Handling → FAQ →
CTA Application → Footer
```

---

## Business Type Recommendations

| Business Type | Template | Key Sections |
|---|---|---|
| **SaaS / Product** | SaaS | Interactive explorer, integration river, examples grid |
| **E-commerce** | SaaS | Hero with product, trust strip, process stepper |
| **Coaching / Community (premium)** | High-ticket | Qualification form, credibility, objection handling |
| **Coaching / Community (accessible)** | SaaS | Simple CTA, process stepper, trust strip |
| **Agency / Service** | High-ticket | Competitive positioning, credibility, qualification |
| **Course / Info product** | Either | Process stepper (curriculum preview), credibility, FAQ |

---

## Shared Infrastructure

These components are identical across both templates:

| Component | Purpose |
|---|---|
| `LenisProvider` | Smooth scroll wrapper (client component) |
| `HeadlineReveal` | GSAP + SplitType word-by-word headline animation |
| `useInView` hook | IntersectionObserver wrapper for scroll triggers |
| `useAutoStep` hook | Observer + auto-advancing interval (for steppers) |
| `Accordion` | Expand/collapse for FAQ and objection handling |
| `ProcessStepper` | Horizontal desktop / vertical mobile step timeline |
| `SectionHeader` | Eyebrow + heading + subtext pattern |

---

## The site-config.ts Pattern

All brand-specific content flows through one TypeScript file:

```typescript
export const siteConfig = {
  brand: {
    name: "Business Name",
    tagline: "From offer.md",
    email: "contact@example.com",
    url: "https://example.com",
  },
  metadata: {
    title: "Page Title | Brand",
    description: "Meta description from offer.md",
  },
  hero: {
    eyebrow: "FROM AUDIENCE.MD",
    headline: "From offer.md transformation",
    subhead: "From offer.md mechanism",
    ctaText: "From offer.md CTA",
    ctaUrl: "#pricing",
    badge: { text: "From testimonials stats", dot: true },
  },
  reasons: [
    { title: "From audience.md", description: "Pain point detail" },
    // ...
  ],
  steps: [
    { label: "Step 1", desc: "From offer.md mechanism" },
    // ...
  ],
  testimonials: {
    stats: [
      { value: "200+", label: "Clients" },
      // ...
    ],
    quotes: [
      { text: "From testimonials.md", author: "Name", role: "Title" },
      // ...
    ],
  },
  faqs: [
    { question: "From audience.md", answer: "From offer.md" },
    // ...
  ],
}
```

Components import from this file. During `/site build`, Claude generates this file from reference files, then regenerates components to consume it.

---

## See Also

- [SKILL.md](../SKILL.md) — `/site` operating principles + triage
- [website-build.md](website-build.md) — full Website (Next.js) build flow this catalog supports
- [frontend-design.md](frontend-design.md) — Typography, color, motion, anti-AI-slop standards (Next.js)
- [cloudflare-pages-link.md](cloudflare-pages-link.md) — CF Pages GitHub App OAuth handshake (current default deploy)
- [deployment.md](deployment.md) — Netlify deploy walkthrough (legacy fallback)
- [examples-and-troubleshooting.md](examples-and-troubleshooting.md) — Usage examples and common fixes
