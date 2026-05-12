# Business Setup Patterns

Use this during setup when a new business repo needs operating context beyond
the core offer, audience, voice, soul, and proof files.

These are setup patterns for business primitives, not a product taxonomy.
Create only the folders that help the operator's current business and access
boundary. Avoid collecting exhaustive operations, finance, customer, or member
data during first pass onboarding.

Use `.claude/reference/business-primitives/offer-bet-push-proof.md` for the
offer, bet, push, proof, playbook, and decision routing contract.

## Shared File Rules

### Always Core

These files stay brand-level. Do not create per-offer versions unless the
operator is actually splitting into a separate business repo.

| File or folder | Why |
| --- | --- |
| `core/soul.md` | Soul is brand identity. Different souls usually mean different repos. |
| `core/voice.md` | Voice is brand personality. One brand, one voice. |
| `core/content-strategy.md` | Distribution is brand-level. Offers are topics inside pillars, not separate strategies. |
| `core/brand/` | Brand systems, visual identity, and guardrails are unified. |

### Offer-Aware

| File | Single-offer repo | Multi-offer repo |
| --- | --- | --- |
| Offer | `core/offer.md` | `core/offers/<slug>/offer.md`, with `core/offer.md` as portfolio thesis |
| Audience | `core/audience.md` | `core/offers/<slug>/audience.md` when distinct; otherwise `core/audience.md` |

### Proof

Proof folders own the domain; standard files keep the write targets
predictable.

| Proof type | Company-wide target | Offer-specific target |
| --- | --- | --- |
| Individual testimonials | `core/proof/testimonials.md` | `core/offers/<slug>/proof/testimonials.md` |
| Average-case outcome context | `core/proof/typicality.md` | `core/offers/<slug>/proof/typicality.md` |
| Messaging angles | `core/proof/angles/*.md` | `core/offers/<slug>/proof/angles/*.md` |

Older repos may have offer testimonials beside the offer file. Read those as
compatibility context, but write new proof under the proof folders above.

### Resolution Pseudocode

```text
resolve_context(file_type, selected_offer):
  if file_type in [soul, voice, content-strategy, brand]:
    return core/{file_type}

  if file_type in [offer, audience] and selected_offer:
    candidate = core/offers/{selected_offer}/{file_type}.md
    if candidate exists:
      return candidate

  if file_type in [testimonials, typicality, angles] and selected_offer:
    return [
      core/offers/{selected_offer}/proof/{file_type},
      core/proof/{file_type},
      legacy offer-side proof files as read-only context
    ]

  return core/{file_type}.md or core/proof/{file_type}
```

Offer choice is session-scoped unless the operator explicitly approves saving
local state.

## Community Or Membership

Useful folders:

```text
core/operations/classroom/
core/operations/membership/
core/operations/funnel/
core/operations/funnel/skool-surfaces.md
core/content-strategy.md
```

Capture the public-safe surfaces the skills need: about-page positioning,
pricing-card copy, classroom/module structure, onboarding promise, content
cadence, and fulfillment notes. Do not import raw member data.

### Community File Specs

`core/operations/classroom/modules.md` captures curriculum structure:
module name, learning outcome, format, duration, prerequisites, lessons, and
deliverables.

`core/operations/classroom/resources.md` catalogs downloads, templates, tools,
which module they support, and access level.

`core/operations/funnel/stages.md` documents the member journey: awareness,
interest, consideration, conversion, onboarding, engagement, and retention.

`core/operations/funnel/touchpoints.md` documents conversion moments such as
landing pages, email sequences, sales pages, checkout, and onboarding.

`core/operations/funnel/skool-surfaces.md` stores live about-page and pricing
card copy for congruence checks across `/mb-ads`, `/mb-organic`, and `/mb-site`.
Update it when the live about page, pricing tiers, or major
claims change.

`core/operations/membership/pricing.md` captures price points, billing
frequency, trials, tiers, and what is gated versus open.

`core/operations/membership/benefits.md` captures what members get by access
level.

`core/content-strategy.md` captures content pillars, platform strategy,
content mix, weekly cadence, metrics, repurposing flow, framework library, and
hook library. Pillars should pass the soul, offer, and audience tests.

Optional community extensions include `core/operations/events/`,
`core/operations/gamification/`, and `core/operations/affiliates/`.

### Community Analytics And Retention

When mining Skool or membership performance data, prefer summarized metrics
over raw member exports. Useful dashboard facts include members, monthly
recurring revenue, conversion, retention, activity, posts, comments, likes,
cohorts, new members, churn, upgrades, downgrades, and top contributors.

For retention analysis, preserve the operating insight that people often stay
for the founder's point of view, taste, and curation rather than for a growing
feature stack. Skills should look for:

- founder personality and epiphany bridges in the offer and sales video;
- members adopting language, rituals, and named enemies;
- curated paths through content rather than "more modules" as the default fix;
- retention evidence in `core/proof/typicality.md`, case summaries, and
  membership outcome notes.

Curation can be the moat. In community businesses, the value is often the
sequence, selection, and interpretation of content, not raw volume.

## E-Commerce

Useful folders:

```text
core/operations/products/
core/operations/fulfillment/
core/operations/support/
```

Keep `core/offer.md` or `core/offers/<slug>/offer.md` as the sellable promise.
Use operations files for catalog, materials, fulfillment, returns, suppliers,
support patterns, and inventory notes. Do not treat raw exports as durable
truth until they are summarized.

### E-Commerce File Specs

`core/operations/products/catalog.md` captures product name, handle or slug,
price, product type, short description, key features, variants, and collection
or category. A Shopify export can seed it, but the durable file should be a
clean summary.

`core/operations/products/materials.md` captures materials by product type,
sourcing or origin, care instructions, sustainability notes, and customer-facing
quality language.

`core/operations/products/sizing.md` captures size charts, fit notes, and
measurement instructions.

`core/operations/fulfillment/logistics.md` captures production method,
production time, carriers, shipping times, returns, international shipping, and
support constraints.

Optional e-commerce extensions include `core/operations/collections/`,
`core/operations/seasonal/`, and `core/operations/wholesale/`.

## Coaching, Services, Or Agency

Useful folders:

```text
core/operations/delivery/
core/operations/sales/
core/operations/fulfillment/
```

Capture packages, qualification rules, delivery process, sales-call patterns,
client onboarding, and outcome proof. Client-specific confidential work belongs
in a separate linked client repo when access boundaries differ.

## Multi-Offer

Use one repo with `core/offers/` when the products share the same brand, team,
voice, and access boundary. Use separate repos when the products have different
souls, voices, teams, provider accounts, finance boundaries, or operating
histories.

Examples:

| Scenario | Structure |
| --- | --- |
| Coaching community plus digital course | Multi-offer |
| Free group plus paid group under one brand | Multi-offer |
| Coaching practice plus unrelated e-commerce store | Separate repos |
| Agency plus personal brand with distinct voice | Separate repos |

For setup:

- `core/offer.md` becomes the portfolio thesis.
- Each durable offer gets `core/offers/<slug>/offer.md`.
- Create `core/offers/<slug>/audience.md` only when that offer targets a
  distinct audience segment.
- Company-wide proof stays under `core/proof/`.
- Offer-specific proof goes under `core/offers/<slug>/proof/`.
- Use `core/product-ladder.md` when the relationship between offers matters.

### Product Ladder

`core/product-ladder.md` explains how offers relate. Useful sections:

- offer list with type, price, purpose, feeds-from, and feeds-into;
- flow from entry offer to ascension or retention;
- cross-sell and upgrade opportunities;
- notes on which offers are variants versus truly separate products.

### Scaling Guidance

| Offer count | Guidance |
| --- | --- |
| 1 | Single-offer mode. No `core/offers/` folder needed. |
| 2-3 | Multi-offer sweet spot. Clean separation is usually enough. |
| 4-10 | Still workable. Group offers into tiers or families in `core/product-ladder.md`. |
| 10+ | Reconsider architecture. Group families or split repos if souls, audiences, or operations diverge. |

Warning signs that an offer needs a separate repo:

- it needs a different `core/soul.md` or `core/voice.md`;
- it serves a fundamentally different audience with little overlap;
- the brand strategy reads as "for this offer only";
- provider accounts, finance, client access, or operating history need a
  separate boundary.

### Migration Guardrails

Single-offer to multi-offer is a deliberate migration, not cleanup:

1. Current `core/offer.md` becomes the portfolio thesis.
2. Current offer details move to `core/offers/<slug>/offer.md`.
3. `core/product-ladder.md` is created when offer relationships matter.
4. `core/audience.md` remains the shared baseline unless the new offer needs
   `core/offers/<slug>/audience.md`.
5. `core/soul.md`, `core/voice.md`, `core/brand/`, `core/content-strategy.md`,
   and `core/proof/` remain brand-level unless an accepted decision says
   otherwise.

Do not rename, merge, delete, split, or move offer folders without an accepted
decision, approved migration plan, or explicit operator instruction.

Historical engine builds may still contain older business-type setup notes.
Treat copied notes from that era as compatibility context only; do not present
that language as the current Main Branch model.
