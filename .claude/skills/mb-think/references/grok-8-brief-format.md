# Grok-8 Researched Brief Format

Use this format when the operator asks for a researched brief, site brief,
offer launch brief, or research that must feed `/mb-ads`, `/mb-site`, organic
content, or a push playbook.

The format is adapted from a private source attachment. Keep only the reusable
structure in public repos. Do not copy private examples, client details, raw
customer/member data, credentials, or long excerpts into committed files.

## Invocation

```text
/mb-think --brief-format=grok-8 <research question>
```

`grok-8` is not the default yet. Use it only when requested, when a site or
launch brief needs broad source coverage, or when the operator agrees that the
research should become a downstream production brief.

## Frontmatter

```yaml
---
type: research
date: YYYY-MM-DD
source: claude-code
model: opus-4.5
status: complete
brief_format: grok-8
linked_decisions: []
linked_pushes: []
---
```

Use `linked_pushes` only when the research is tied to a coordinated push.

## The 8 Categories

### 1. Business And Offering Deep Dive

Capture what the business sells, how it delivers, why it is different, pricing
or package shape, the current brand story, goals, and the strongest objections
or hesitations.

Feeds:
- `core/offer.md` or `core/offers/<offer>/offer.md`
- `/mb-ads` offer promise, objections, and angle selection
- `/mb-site` hero, mechanism, pricing, and proof sections

### 2. ICP And Deep Audience Insights

Capture the ideal customer profile, situation, values, fears, aspirations,
desired transformation, buying triggers, online hangouts, and exact language
the audience uses.

Feeds:
- `core/audience.md` or `core/offers/<offer>/audience.md`
- `core/voice.md`
- ad hooks, organic angles, and page section language

### 3. Customer Journey And Story Mapping

Map awareness, consideration, decision, onboarding, retention, and advocacy.
Name friction points, drop-offs, emotional states, and what the site, ad, or
playbook must do at each stage.

Feeds:
- site flow and CTA hierarchy
- push playbook stage gates
- ad funnel intent and retargeting notes

### 4. Competitive And Market Landscape

Summarize direct and indirect competitors, positioning, messaging, tone,
category norms, market shifts, strengths, gaps, and what appears to be working.
Mark inferred winners as inferred unless the operator has performance data.

Feeds:
- `core/proof/angles/`
- competitor gap maps for `/mb-ads`
- differentiation and proof placement for `/mb-site`

### 5. Brand Archetype And Story Discovery

Name the brand personality, customer role, story frame, emotional benefits,
functional benefits, proof stories, and what the brand stands against. The
operator chooses final positioning.

Feeds:
- `/mb-site` dial, archetype, voice, and do-not-state guidance
- `core/voice.md`
- creative review gates for ads and organic content

### 6. Technical, Functional, And Experience Requirements

Capture must-have features, forms, booking, payments, community login,
integrations, SEO priorities, performance, mobile, accessibility, compliance,
analytics, and tracking goals.

Feeds:
- `/mb-site` repo setup, conversion endpoint, and `mb site check`
- provider-readiness notes from `mb connect`
- playbook approval gates where external tools are involved

### 7. Content And Asset Audit

Inventory existing content, missing content, visual assets, videos, voice
guidelines, testimonials, case studies, proof points, and approval status.

Feeds:
- ad proof, image prompts, and video scripts
- site page assets and proof sections
- `core/proof/testimonials.md` and `core/proof/typicality.md`

### 8. Success Metrics And Constraints

Name primary KPIs, secondary signals, timeline, budget, non-negotiables, red
lines, and known risks.

Feeds:
- push goals and health checks
- ad review criteria
- site launch readiness and follow-up measurement

## Output Shape

Use this section order after the standard question, methodology, sources, and
excerpts sections:

```markdown
## Grok-8 Researched Brief

### 1. Business And Offering Deep Dive
### 2. ICP And Deep Audience Insights
### 3. Customer Journey And Story Mapping
### 4. Competitive And Market Landscape
### 5. Brand Archetype And Story Discovery
### 6. Technical, Functional, And Experience Requirements
### 7. Content And Asset Audit
### 8. Success Metrics And Constraints
```

Then include the standard synthesis:

- one-sentence summary;
- key findings;
- implications for reference files;
- downstream handoff;
- open questions;
- citations.

## Downstream Handoff

End every `grok-8` brief with a compact handoff table:

| Next Surface | Ready Input | Missing Or Risky |
|---|---|---|
| `/mb-ads` | Angles, objections, audience language, proof | What still needs operator confirmation |
| `/mb-site` | Offer, audience, story, requirements, assets, metrics | What blocks the brief or launch |
| Push playbook | Trigger, resource, approval gate, provider boundary, outcome hook | What must stay manual or unsupported |
| Reference files | Exact files that should be updated | What should not be codified yet |

If a resource-delivery or provider workflow emerges, create or recommend a
`pushes/<push>/playbooks/<playbook>.md` plan only. Do not execute provider
mutation, publishing, DM/reply automation, spend, or account changes unless a
shipped provider path and explicit operator approval support it.

## Quality Bar

- Each category has either source-backed findings or an explicit "unknown".
- Private data is summarized safely or left outside tracked files.
- Source limitations are clear.
- Provider-readiness language comes from `mb status` or `mb connect` facts
  when available.
- The brief can feed production without rereading raw sources.
