# Meta Pack Loop: Build, Read, Stop, Scale, Close

Use this when the operator runs Meta ads as a steady cadence: a new **pack**
each week, read every day, judged at day 14, and closed with a retro. It is the
operating loop around the copy, media and naming references:

- words: [meta-text-slots.md](meta-text-slots.md)
- media: [ad-media-specs.md](ad-media-specs.md)
- names and tracking: [naming-and-utm.md](naming-and-utm.md)
- what Meta does to objects, and read-back: [meta-api-behaviours.md](meta-api-behaviours.md)

Main Branch's Meta support is read-only. Every step that touches the ad account
is done by the operator in Ads Manager, or by a write tool the operator has
approved for that business. This skill prepares the pack, the checklist and the
read; it does not publish, activate or change budgets. See the Mutation Boundary
in [meta-ads-integration.md](meta-ads-integration.md).

Source: a live ecommerce dogfood business, September 2026. Its first packs were
built, passed Meta review and were approved; delivery results were not in yet.
Treat the loop as a working shape, and the numbers as starting defaults to
re-set from the business's own data.

---

## The Pack

One pack = one PAUSED ad set holding a few ads (about four) for one audience
and one angle.

- **Two hooks per concept, different in kind** (a plain name versus a reveal,
  a ritual versus an outcome), not two phrasings of one idea. Ads are named
  `-h1-` and `-h2-` so the day-14 read can compare hooks.
- **Both ratios on every ad:** 4:5 for Feeds, 9:16 for Stories and Reels.
- **Five text slots** per ad (5 primary texts, 5 headlines, up to 5
  descriptions), written and edited before the build.
- **One record per pack** in the push:
  `pushes/<YYYY-MM-DD-slug>/packs/p<NN>-<slug>.md` with the brief, the text
  slots file, the media list with hashes, the build checklist, the daily log,
  the verdict and the retro.

Pick the ad set's settings once (audience, exclusions, placements, optimisation,
attribution) and record them in the push. Each new pack is built to that record
and diffed against it, so drift is visible.

## The Weekly Loop

1. **Settings check.** Read the recorded settings and compare them with the
   last live ad set. *Done when* there is no difference, or the difference is
   explained and recorded.
2. **Words.** Write the text slots and run the fresh-agent edit
   ([meta-text-slots.md](meta-text-slots.md)). *Done when* the slots file has
   exactly one `VERDICT` line and every edit is applied or declined with a
   reason.
3. **Media.** Make both ratios per ad and have a separate agent gate them
   ([ad-media-specs.md](ad-media-specs.md)). *Done when* each ad has one
   `AD <name>: ACCEPT | RETRY | STOP` line and the set has one `VERDICT`.
4. **Build, PAUSED.** The operator (or an approved write tool) creates the ad
   set, creatives and ads PAUSED, with the names, `url_tags` and enhancement
   settings from the pack record. *Done when* the read-back checklist in
   [meta-api-behaviours.md](meta-api-behaviours.md) passes for every ad.
5. **Review for the operator.** One comment or message: a contact sheet of every
   ad in both ratios, every text slot, the read-back result, the policy
   checklist, and the ad set renamed to the publish day (names freeze at first
   publish). *Done when* the operator has published, and only what they
   published is active.
6. **Daily read** while anything delivers (below). *Done when* the day's
   numbers are logged and every rule that fired has its pause applied and read
   back.
7. **Verdict and retro at day 14** (below). *Done when* every lesson names the
   file or line it changed, or why nothing changed.

---

## Money Numbers

Set these per product from the business's own margins before the first pack.
Keep them in a decision file, not in the skill.

| Number | Meaning |
|--------|---------|
| Contribution per sale | Price minus product cost, fulfilment, payment fees and any per-order cost |
| Break-even cost per sale | All of the contribution |
| Target cost per sale | A share of it (the dogfood business uses half) |
| Minimum cart target | A floor for cheap products, so a rule has room to fire |

Read prices live when you compute these; never from memory.

## Stop Rules (Daily)

Apply them in order, on **cumulative spend that never resets**:

1. **Creative floor.** After 2,000 impressions, link CTR under 0.5%, or for
   video a hook rate (3-second plays / impressions) under 15%, stops the ad.
   Below 2,000 impressions an ad is inconclusive unless a dollar rule fires.
2. **No cart by target.** Spend reaches the target cost per sale with no
   add-to-cart: stop.
3. **No purchase by break-even.** Spend reaches break-even with no qualifying
   purchase: stop. With 3 or more add-to-carts, hold to 1.5x break-even.
4. **Campaign cap.** A set amount of campaign spend with no qualifying purchase
   stops the campaign.
5. **Contribution check.** Past a set spend, total spend above total
   contribution stops the campaign.
6. **Hold band.** A spend level where nothing scales until the operator reviews.

The dollar values in rules 4 to 6 are the operator's call and belong in the
decision file. The creative floor defaults above are a starting point: re-set
them at day 30 from the account's own data and record the change.

A daily pause is the stop, so expect overshoot: Meta may spend up to 75% over
the daily budget on a single day.

**Who presses what.** An agent may prepare the pause list. Pausing is an
account write, so it needs the operator, or a write tool the operator approved
for pauses only. Activation, budget, bid and spend-cap changes are always the
operator's.

## Daily Read

1. Pull yesterday and lifetime per ad: spend, impressions, link CTR, 3-second
   plays, ThruPlays, add-to-carts, purchases, and delivery and review status
   (rejections, "learning limited"). Use `mb ads meta summary` or an approved
   read-only tool when available; otherwise ask the operator for an Ads Manager
   export.
2. Pull store orders credited to Meta (`utm_source=facebook`, last non-direct
   click). Count only **qualifying purchases**: paid, not test orders, not
   cancelled or refunded, and, if the business decides so, first-time buyers
   only. Keep order-level data out of the repo; write counts.
3. Apply the stop rules.
4. Log the numbers, the rules that fired and the pauses, with the time.
5. Say something to the operator only when something changed.

## Weekly Read and Verdicts

- Read the week with an audience-segment breakdown (new, engaged, existing
  customers), so sales from past buyers never count as acquisition.
- **Verdict at day 14 per pack:**
  - **Winner:** a qualifying purchase at or under the target cost.
  - **Exploratory:** carts but no qualifying purchase.
  - **Loser:** everything else.
- A winner moves into a scaling ad set by post ID ("Use existing post"), which
  keeps its social proof and its ad name, so `utm_content` stays the same.
- Scale in rungs the operator sets. Each rung is the operator's press; carts
  alone never unlock a rung.

## Order of Truth

Store orders by channel come first. Meta's own purchase count is a diagnostic.
Below about 10 Meta purchases, attribution differences mean little; don't
re-plan on them.

---

## Retro (Every Pack)

Every pack closes with a retro in its pack file, as a table:
`lesson with evidence | what changed | commit`.

- **Hooks:** which hook carried (numbers) and why we think so.
- **Slots:** which texts took the spend; any Meta never served. At small spend
  the per-asset breakdown is a hint, not a verdict.
- **Media:** made, accepted, cost per accepted asset, and each failure mode.
- **Review and policy:** every line Meta rejected or the editor cut, with the
  rule it broke.
- **Customer words:** new words from comments, messages and reviews, and where
  they now live (`core/` audience or voice files).
- **Changes:** each lesson becomes a commit to the business's playbook,
  `core/` reference, or a decision if a law changed, or it says "no change,
  because ...".

Route codification through `/mb-think`. The retro is done when every lesson has
a change or a reason.
