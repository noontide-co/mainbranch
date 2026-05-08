# Business Setup Patterns

Use this during setup when a new business repo needs operating context beyond
the core offer, audience, voice, soul, and proof files.

These are setup patterns for business primitives, not a product taxonomy.
Create only the folders that help the operator's current business and access
boundary. Avoid collecting exhaustive operations, finance, customer, or member
data during first pass onboarding.

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

Use the offer/bet/push/proof reference for the main rules:
`.claude/reference/business-primitives/offer-bet-push-proof.md`.

For setup:

- `core/offer.md` becomes the portfolio thesis.
- Each durable offer gets `core/offers/<slug>/offer.md`.
- Create `core/offers/<slug>/audience.md` only when that offer targets a
  distinct audience segment.
- Company-wide proof stays in `core/proof/`.
- Offer-specific proof goes in `core/offers/<slug>/proof/`.
- Use `core/product-ladder.md` when the relationship between offers matters.

Historical engine builds may still contain older business-type setup notes.
Treat copied notes from that era as compatibility context only; do not present
that language as the current Main Branch model.
