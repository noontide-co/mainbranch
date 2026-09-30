# Meta Behaviours, Build Shapes and Read-Back

What Meta actually did to ads, ad sets and creatives when a live dogfood
business built them in September 2026, with the official `meta-ads` CLI 1.2.0
(Graph v24.0) and in Ads Manager. Use it to plan a build, to write the
operator's checklist, and to read a pack back before anyone publishes.

**Evidence level.** At the time of writing those ads were stored, passed Meta
review and were approved, but had not delivered. Each line below is marked:

- *refused*: Meta returned an error, so the rule is proven;
- *stored*: Meta stored and read back the object this way; delivery not yet seen;
- *reported*: from practitioner reports, not yet reproduced.

Meta changes these behaviours without notice. When a line matters for a
launch, re-check it on the day and update this page if it moved.

Main Branch does not ship a Meta write path. This page informs manual builds
and any future adapter; see [Adapter Rails](#adapter-rails).

---

## Objects That Can't Change

- **Creatives are immutable.** An edit takes only name, status and adlabels
  (#100/1815573). *refused*. To change media, text, tracking or enhancements,
  make a new creative and swap it onto a PAUSED ad.
- **Every Ads Manager save makes a new creative** and sends the ad back to
  review. Take creative ids from the latest read-back, never from an earlier
  note. *stored*
- **Copying an ad duplicates its creative**, and Meta appends a date-hash to
  every creative name. Don't read creative names as pack names. *stored*
- **Names freeze at first publish.** Rename before publishing, never after.

## Defaults That Turn Things On

- **Multi-advertiser ads** are ON for any creative that doesn't send
  `contextual_multi_ads {"enroll_status": "OPT_OUT"}`. Unset means enrolled.
  *stored*
- **Shop destination** ("Shop" personalised destination) was switched on for
  every API-built ad. Turn it off where the business wants its own site.
  *stored*
- **Enhancements come back on** after an edit, a duplicate or a preview.
  *reported*. Set each one explicitly at create and check them all on every
  read-back.
- **Features can change after processing.** A feature set at create can read
  back differently once Meta has processed the creative. One opt-in feature
  set by API on an asset-feed creative was dropped after processing while the
  same feature set in Ads Manager stayed. *stored*. Read back after processing,
  not only right after the call.
- **Customer exclusions can be pre-filled wrongly** on new ad sets. *reported*.
  Check the exclusion list by hand on every new ad set.

## Enhancements (Degrees of Freedom)

- `standard_enhancements` is refused as a bundle (#100/3858504, deprecated).
  *refused*. Set each feature in `degrees_of_freedom_spec.creative_features_spec`
  on its own, OPT_IN or OPT_OUT.
- Which features stay on is the business's decision. Record it in a decision
  file and check every feature against it on read-back. A safe default is
  every feature OPT_OUT, then turn on only what the operator chose.
- Relevant comments (`inline_comment`) set by API may not survive processing
  (above). If the operator wants it on, set it in Ads Manager until a read-back
  after processing shows the API value holding.

## Placements, Text and Media

- **Two-rule placement shape.** One creative carries both ratios through
  `asset_feed_spec.asset_customization_rules`: rule 1 (priority 1) lists the
  Stories and Reels positions with the 9:16 asset; rule 2 (priority 2) is the
  catch-all with the 4:5 asset. *stored*. The easiest correct shape is to read
  a creative Ads Manager already made (`asset_feed_spec`) and swap in new
  hashes and text.
- **A mixed rule is a mistake.** Keep feeds and Stories/Reels positions in
  separate rules, and keep each rule's media at its ratio.
- **One description per placement rule** (#100/1885878). *refused*. Extra
  descriptions never reach the ad. Write description 1 as the one that must
  stand alone.
- **Five bodies and five titles per rule.** Sharing one label across all 5
  bodies and all 5 titles gave each placement all 5, and Meta stored and
  approved it. *stored, not yet delivered.* An earlier Main Branch test
  (issue #808) recorded one body and one title per rule. Until a delivery
  breakdown shows the variants getting impressions, treat 5+5 as unproven and
  check the per-asset breakdown after the first day.
- **Ads Manager keeps one description** on these ads; it has no control to add
  more.
- **The CLI's raw `--bodies` / `--images` form builds a dynamic creative.** Use
  the `asset_feed_spec` shape instead if the business keeps dynamic creative
  off.
- **Swapping media in Ads Manager can keep the old media** in the rule with no
  placements (the fallback), which still serves some positions. After any
  media swap, check every video and image in every rule, the fallback
  included.
- **Identical images de-duplicate.** Re-uploading a pixel-identical still is a
  no-op; a video saved through the UI gets a new id with the same title.

## Product Tags

- Set at creative create in `interactive_components_spec`: one `PRODUCT_TAG`
  per product with the Meta **catalog** product id, never the store's own id.
  *stored*
- Catalog product ids can exceed 2^53. Keep them as strings in any tool that
  parses JSON numbers as doubles.
- A position is required on an image and refused on a video.
- Refused on carousels and on feeds that mix images and videos: one creative
  per media type.
- Instagram shows a tag only once the product is approved for shopping. Read
  `capability_to_review_status`; the top-level `review_status` is an old field
  and can be blank. Approval can flip back when product images change.

## Pace and Hygiene

- **Rate limit.** The ad account counts reads and writes together: error
  80004 (#613) came after about 30 calls in 20 minutes. Pace about one write
  every 20 seconds and one upload every 60; after a hit, wait 15 minutes or
  more, retry at most three times, and log each try. *refused*
- **Deletes.** An image any creative uses can't be deleted, and an image delete
  can answer success and keep the image. A delete counts only when a read shows
  it gone. Plan on images accumulating; they don't deliver.
- **Paths.** Use absolute local paths with no symlinks when uploading.
- **Text by value.** Take text from the slots file by script or paste, never
  retyped; join soft-wrapped lines before they become text.

---

## Read-Back Checklist

Run it after the build, again after any Ads Manager pass, and again after Meta
finishes processing. Every line must pass before the operator publishes.

| Check | Pass |
|-------|------|
| Status | Every campaign, ad set and ad the agent prepared is PAUSED |
| Status after writes | Read status back after **every** write, a creative swap included; a write that reports success can leave an object in a state nobody asked for. If it isn't what was asked, stop and fix it before anything else |
| Names | Match the pack record exactly, ad set renamed to the publish day |
| Text | Every primary, headline and description equals the slots file (compare as sets; rules repeat them); each primary opens with its ad's hook |
| Tracking | `url_tags` equals the house line exactly ([naming-and-utm.md](naming-and-utm.md)) |
| Enhancements | Every feature matches the business's decision; nothing else opted in |
| Multi-advertiser | OPT_OUT |
| Shop destination | Off, unless the business chose it |
| Placement rules | Present; 9:16 on Stories/Reels, 4:5 elsewhere; the fallback rule carries the new media |
| Product tag | The intended catalog product, if the pack uses tags |
| Landing URL | Returns 200 today |
| Exclusions | Match the recorded list on the ad set |

Graph can accept an unknown parameter and still answer success. Never report a
build done from the write's own response; report it from the read-back.

---

## Adapter Rails

Any future `mb` write path for Meta (see the Mutation Boundary in
[meta-ads-integration.md](meta-ads-integration.md)) must keep at least these
rails, which the dogfood business ran on its own private tooling:

- creates are forced PAUSED; the tool refuses any other status and never
  activates;
- no budget, bid or spend-cap change without a separate operator approval, and
  caps enforced in the tool;
- the account id is pinned, and every parent, creative and audience id is
  checked to belong to it;
- dry run by default; nothing is sent without an explicit confirm flag;
- a ledger line is written before each send and a result line after, and
  nothing is sent if the ledger can't be written;
- read-back after every write, with a non-zero exit on any mismatch;
- multi-advertiser OPT_OUT sent on every creative;
- enhancement features checked against an allow list; unknown features refused;
- `url_tags` checked against the house tracking line;
- pacing and retry per the rate limit above.
