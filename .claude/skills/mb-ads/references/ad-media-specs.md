# Ad Media Specs and Composition

Sizes, safe areas and composition rules for Meta ad images and short videos,
and how to gate them. It applies to generated creative
([image-generation-workflow.md](image-generation-workflow.md)) and to media
made from real photographs. Placement specs are Meta's and change; check
Meta's Ads Guide before a launch and update this page if it moved.

Source: a live ecommerce dogfood business, September 2026, whose 4:5 and 9:16
media were built into placement rules and approved by Meta review.

---

## Two Shapes Per Ad

| Shape | Placement | Minimum | Notes |
|-------|-----------|---------|-------|
| 4:5 | Feeds (Facebook, Instagram, Explore, Marketplace, search, video feeds) | 1440 x 1800 | Takes more of the feed than 1:1 |
| 9:16 | Stories, Status, Reels | 1080 x 1920 | Mind the safe area below |

Every ad ships both. The build puts the 4:5 on Feeds and the 9:16 on Stories
and Reels through placement rules ([meta-api-behaviours.md](meta-api-behaviours.md)).
A 1:1 square is still accepted by Feeds; make one only when a placement or a
reused asset needs it.

**Designing both.** Compose each ratio for its placement rather than cropping
one from the other. When one master must serve both, design the 9:16 with the
product and every word inside the 4:5 centre band, then crop.

## 9:16 Safe Area

Meta's interface covers about the **top 14%** and the **bottom 35%** of a 9:16
frame. The product and every word sit between 14% and 65% of the height (rows
269 to 1248 on 1080 x 1920). Fill the rest with the photo's own background,
carried on, never a flat colour block.

## Composition Rules

A frame that breaks one of these fails the gate:

1. **The whole product stays in frame**, with at least 6% margin. Only a chain,
   strap, cable or similar may leave the frame.
2. **No dead colour slab.** No flat block without words over about 10% of the
   frame. Words sit on a flat area of the photo, or in a band no taller than
   their lines need.
3. **One shoot per frame.** Never stack photos with different light or grade
   in one frame. Two panels only when both come from the same set.
4. **Product size and place.** A closed or packed product spans about 40-75%
   of the frame width; a product laid open side by side may reach about 88% if
   its margin holds. Its centre sits in the middle of the safe area, not small
   and low under empty space.
5. **Judge it in the placement.** Look at every frame in Meta's own preview crop
   for Feed, Stories and Reels at phone size before calling it done. A frame
   that only works as a file doesn't pass.

## Real Pixels for Physical Products

When the ad shows a physical product, the product pixels come from real
photographs: cropped and uniformly scaled, never generated, mirrored,
repainted or upscaled. When a crop runs short, crop less.

- An AI scene (a person or setting no real photo has) is one whole generation
  from real references, not a cut-out pasted onto a generated background, and
  only for products whose detail survives generation. Gate it against the real
  product: part count, shape, closures, size.
- Label AI scenes on the frame and in the file metadata, and follow the AI
  disclosure rules in [compliance/](compliance/README.md).
- No fake or AI-generated customer testimonials or unboxings.

## Short Videos and Slideshows

- **Frame 1 is the hook**, with its caption already on screen. An empty caption
  band on frame 1 reads as a mistake.
- **Caption timing:** each caption stays on screen at least 0.5 s plus 1 s per
  3 words. More than about 5 captions won't fit in 8 seconds.
- **Words sit on flat areas,** never over the product's detail or skin, and read
  with the sound off.
- **Balanced line breaks,** so no word is orphaned on the last line.
- **Encoding:** H.264, yuv420p, 30 fps, faststart; no audio unless the concept
  needs it.
- Cut a first-frame still per video per ratio to use as the thumbnail.

## Files

- Base name = the ad name plus `-45` or `-916`
  ([naming-and-utm.md](naming-and-utm.md)). Meta shows file names in the
  account library, so the second ratio can be found by name.
- Keep media out of git. The push records where files live
  (`media_location`), their sha256 hashes, sources and gate verdicts.
- Words on media come from the pack's words file, copied by value
  ([meta-text-slots.md](meta-text-slots.md#words-on-images)).
- A render that must be repeatable should give the same bytes from the same
  inputs (zero out timestamps in image metadata), so a changed hash means a
  changed input.

## The Gate

A self-check is not a gate. A separate agent that did not make the files judges
them:

- both ratios per ad pass, or the ad doesn't;
- composition rules 1-5, measured from the output pixels, not from the maker's
  notes;
- for real-photo media: every product pixel traces back to a source photo, not
  mirrored or upscaled;
- words match the words file character for character, and shape, size and
  material words match the product's real specs;
- readable at phone size (9:16 at about 390 px wide, 4:5 at about 440);
- output: one `AD <name>: ACCEPT | RETRY <fix> | STOP <reason>` line per ad and
  exactly one `VERDICT:` line for the set.

A second identical hard-gate failure ends that path; switch to real photos or a
different layout. The operator sees one contact sheet: each ad in both ratios,
failing tiles with a zoomed inset and one plain line.

## Media Retro

Each round of media closes with a row: made, accepted, spend on metered
generation, cost per accepted asset, which layouts worked, each distinct failure
mode with a count and an example, and the file each lesson changed.
