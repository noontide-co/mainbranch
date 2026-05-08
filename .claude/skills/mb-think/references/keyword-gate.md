# Keyword Gate Research

Use this for buyer-intent search demand validation before building or funding a
launch push.

Triggers:

- "keyword gate this offer"
- "kill or build this offer"
- "is there search demand for this"
- "what keywords should the lander/ad plan use"
- "validate buyer intent before paid traffic"

## Source Of Truth

Start from the active offer and audience:

- `core/offers/<offer>/offer.md` and `core/offers/<offer>/audience.md`, when
  multi-offer mode is active;
- otherwise `core/offer.md` and `core/audience.md`;
- accumulated proof and voice files when they clarify pain, promise, and
  forbidden claims.

If a launch push already exists, link the research to it. If no push exists,
write the research so `/mb-start` and `/mb-site` can create one later.

## Tool Order

Use progressive enhancement. Never block the workflow on an optional provider.

1. `mb status --json --peek` and `mb connect doctor --json` for provider facts.
2. Apify/search-sidecar SERP and autocomplete data when configured.
3. Google Keyword Planner CSV when the operator provides a file path.
4. Web search fallback for SERP inspection and adjacent terms.
5. Operator-provided customer language, Ads Manager screenshots, or exports.

Do not ask the operator to paste provider tokens, OAuth secrets, raw customer
data, or account exports into chat.

## Seed Terms

Generate 8-15 seeds:

- offer name and category;
- problem-aware phrases from audience pain;
- solution-aware phrases and synonyms;
- comparison phrases: `vs`, `alternative`, `reviews`;
- commercial phrases: `cost`, `price`, `consultant`, `service`, `software`,
  `agency`, `near me` only when local intent is actually relevant;
- audience qualifiers such as role, industry, stage, or geography.

## Buckets

Rank terms into:

- `ready_to_buy`: high commercial intent, provider/service/software searches,
  price/cost/comparison terms, or branded alternatives.
- `comparison`: competitors, alternatives, best-of, reviews, category
  evaluation.
- `research`: informational searches that may inform page copy but should not
  lead paid traffic by default.
- `negative_seed`: free, template, PDF, definition, jobs, salary, DIY, examples,
  and any irrelevant adjacent meanings.

## Verdict

Use an opinionated but overrideable verdict:

- **Build:** at least three ready-to-buy terms with credible demand and a page
  angle the offer can honestly satisfy.
- **Build with caution:** one or two ready-to-buy terms, weak volume/CPC signal,
  or heavy dependency on comparison/research terms.
- **Kill:** no credible ready-to-buy terms, unclear buyer, or likely policy/
  tracking risk that must be resolved first.

Explain confidence based on source quality. Web-only or screenshot-only
research is lower confidence than exported planner/provider data.

## Output File

Write:

```text
research/YYYY-MM-DD-keyword-gate-<offer-or-push>.md
```

Frontmatter:

```yaml
---
type: research
date: YYYY-MM-DD
topic: keyword gate for offer-slug
source: claude-code
status: completed
entities: [offer-slug]
linked_pushes: []
linked_offers:
  - core/offers/<offer>/offer.md
---
```

Body sections:

- `## Verdict`
- `## Source Quality`
- `## Ready-To-Buy Terms`
- `## Comparison Terms`
- `## Research Terms`
- `## Negative Keyword Seeds`
- `## Recommended Lander Cluster`
- `## Ad Plan Inputs`
- `## What Changes`

`Recommended Lander Cluster` should name the primary 2-4 terms for hero,
meta/title, and section headings. `Ad Plan Inputs` should list ready-to-buy
targets and negative seeds for `/mb-ads` launch-plan mode.

## Stop Conditions

Stop and ask before moving to lander/ad work when:

- verdict is `Kill`;
- search demand depends on unsupported provider mutation;
- claims would trigger medical, financial, employment, housing, credit, or
  other regulated policy review;
- the offer/audience files are too thin to judge intent.
