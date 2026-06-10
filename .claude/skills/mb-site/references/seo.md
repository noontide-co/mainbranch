# SEO Doctrine

Load this when the operator asks about ranking, organic traffic, keyword
research, blogging for SEO, backlinks, or AI-search visibility — or when a
site brief includes an organic-traffic goal. This is durable doctrine for any
business the engine serves; it is practitioner-validated for local service
businesses and applies to any offer with a service × audience-segment grid.

SEO is a 6-12 month game. Say so up front. Ads cover the short term; a
complete strategy is SEO + ads + social. Never promise ranking timelines
shorter than that horizon.

---

## The Ranking Unit: Content Silos

**The homepage converts. Silo pages rank.** A homepage cannot rank for every
service and every location, so do not stuff it with keywords trying.

- The ranking unit is one dedicated page per **service × location** (for a
  local business) or **service × segment** (for any other business). Example:
  "kitchen remodel contractors in Sometown, TX" gets its own page.
- Each silo page is a complete, useful page for that exact query: the service,
  the place, proof, and a conversion path. Not a thin doorway page — thin
  programmatic pages with swapped city names are a penalty risk.
- Stack dozens of silo pages. Many small wins assemble the qualified search
  volume a homepage could never capture alone.
- Silo pages are indexable by design. Paid-traffic landers stay `noindex`.
  The two coexist; include silos deliberately in the sitemap and any AI-crawl
  configuration, and keep paid landers out.

## Keyword Selection Math

Pick low-hanging fruit, not heads. **50 searches/mo at 15/100 competition
beats 1,000/mo at 80/100** — the low-competition page actually ranks, and
dozens of them compound into ~1k qualified searches/mo.

1. Enumerate the grid: every service the business sells × every location or
   segment it serves.
2. Score every cell for search volume and competition (data layer below).
3. Build the lowest-competition, non-zero-volume pages first. Re-rank the
   remaining grid as pages land and authority grows.

## PageSpeed Thresholds

Load time is the non-negotiable on-page factor.

- Target **sub-1.5 s load** and **PageSpeed/Lighthouse 90+**. Under 30 means
  the build didn't try.
- The engine's static-first stack (static HTML on Cloudflare Pages) clears
  this naturally. Never trade it away for a page builder or a heavy
  framework — most SEO competitors are stuck at builder-level scores, so
  speed is a standing advantage.

## Blog With Purpose

Blogging builds topical authority **only** when each post targets a
top-searched question. "Don't just blog about anything."

- Source questions from SERP people-also-ask data (data layer below) and from
  the business's own customer questions — support threads, chat transcripts,
  sales calls.
- Structure every post: clear sections, descriptive headers, short
  paragraphs. A post that answers the question in a scannable shape outranks
  a longer unstructured one.
- Case studies are **conversion assets, not ranking assets**. Do not
  keyword-optimize them; they exist to close visitors who are already
  on-site. Spend ranking effort on silos and question posts instead.

## Backlink Cadence

- **5-10 links per month, maximum.** Bulk link buys (Fiverr-class) are
  poison, not a shortcut.
- **Directories first:** EZ Local, Manta, Merchant Circle, Foursquare,
  Yellow Pages, Bing Places — then **local directories**: search
  "<area> business directory" and submit to every legitimate one.
- Community referrals count: answering referral requests in Facebook groups
  with the business's link builds weighted links (engagement matters), and
  recurring community promo threads (e.g. subreddit weekly promo threads)
  are a repeatable link source.
- Guest posts trade content for links but realistically require an
  established writing track record or a partner who has the relationships.
  Treat as a later-stage tactic, not a starting one.

## AI Search

There is no special AI-SEO. AI assistants recommend what traditional SEO
plus reputation signals already surface:

- A silo page that ranks #1 in Google for a query tends to be the AI
  assistant's #1 answer for the same query.
- Reputation inputs the AI reads: Google Business Profile reviews,
  marketplace/aggregator profiles (Home Advisor, Thumbtack, Nextdoor and
  equivalents), and social engagement.
- So the AI-search plan is: the doctrine above, plus a deliberate review and
  profile cadence. Do not buy AI-visibility SaaS to compensate for missing
  silo pages.

---

## The Data Layer (API-first, buy nothing)

Keyword and rank data come from APIs the operator can wire once and automate,
not from consumer-tool subscriptions. Frame each of these as a future
`mb connect` provider (like `provider:cloudflare`): planned rail, not yet
wired — until `mb connect` supports them, the operator holds credentials in
the environment or keychain. Never ask the operator to paste API keys into
chat or public issue text.

**Wire first, in order:**

1. **DataForSEO SERP** — `POST /v3/serp/google/organic/task_post` (standard
   queue, ~$0.0006/SERP at depth 20) plus `task_get/advanced` on a cron. One
   payload parses organic rank, `local_pack`, `people_also_ask`, and
   `ai_overview` — so AI-Overview visibility tracking costs $0 marginal.
2. **Google Ads `KeywordPlanIdeaService.GenerateKeywordIdeas`** — free
   keyword volume/competition for the grid (1 req/s, 15k ops/day on Basic
   access). Backstop with DataForSEO Labs `bulk_keyword_difficulty` (+
   `search_intent`); a 1,000-keyword grid scores for roughly $0.31 one-time.
3. **Google Search Console `searchanalytics.query`** — the free dashboard
   truth layer: clicks, impressions, CTR, and position by query + page, 25k
   rows/request, 16-month history. GSC truth lets paid SERP checks stay
   weekly instead of daily.

**Indicative recurring cost:** weekly top-20 tracking on 100 keywords is
about $0.50/mo per property; monthly people-also-ask mining (50 seeds) adds
well under $1/mo. Even daily tracking stays in single-digit dollars per
property.

**Explicitly skip enterprise tool APIs:** Ahrefs (Enterprise-only API),
Semrush (Business-plan API), Majestic, Serpstat, Ubersuggest (no API).
Skip DataForSEO Backlinks and LLM-mentions products while under their
$100/mo minimums — GSC's free Links report covers backlink truth at small
scale. Revisit only when tracked volume makes the minimum cheap.

---

## The Fulfillment Loop

The repeatable monthly shape, once the grid is scored:

1. **Grid** — enumerate and score service × location keywords; pick the next
   lowest-competition targets.
2. **Silo pages** — build/ship the next batch of silo pages through the
   normal `/mb-site` build flow (brief, build, review, publish).
3. **Weekly rank check** — SERP tasks on tracked keywords; record movement.
4. **Monthly question pass** — mine people-also-ask + the business's own
   customer questions; publish structured blog answers.
5. **Directory pass** — work the 5-10/mo backlink budget: directories first,
   then community referrals.

Report progress in measurable units: "N silo pages live, ranking #X for Y."
Set the 6-12 month expectation at every report until rankings move.
