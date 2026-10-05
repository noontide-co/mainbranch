# Ad Names and UTMs

One naming scheme for Meta campaigns, pack ad sets, ads and their media, and
the tracking line every creative carries. Names are lowercase with hyphens.
Record the business's codes (brand prefix, audience and angle codes, format
codes) in a decision file, not in the skill.

## Names

| Object | Pattern | Example |
|--------|---------|---------|
| Campaign | `<brand>-<objective>-<scope>` | `acme-sales-core` |
| Pack ad set | `p<NN>-<audience>-<angle>-<launch yyyy-mm-dd>` | `p01-gift-durable-2026-10-05` |
| Ad | `p<NN>-<audience>-<angle>-<format>-h<N>-<product>` | `p01-gift-durable-img45-h1-classic` |
| Media file | the ad name + `-45` or `-916` | `p01-gift-durable-img45-h1-classic-916.jpg` |

- `<format>` names the ad's primary shape and layout (for example `img45`
  still, `sld916` slideshow); the other ratio is always made too.
- `h<N>` is the hook, so the day-14 read can compare hooks across ads.
- **Names freeze at first publish.** If a pack publishes on a later day than
  its ad set name says, rename the ad set before publishing, never after.
- **An ad keeps its name forever.** When a winner moves to a scaling ad set by
  post ID, it keeps its name, so `utm_content` stays the same.

Batch-level names for static-ad drafts (`001.1_IMG_01`) stay as in
[static-output-template.md](static-output-template.md); give each ad its pack
name when it is built.

## URL Parameters

Set on every creative at creation, as its `url_tags`, and read back exactly:

```text
utm_source=facebook&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}&utm_id={{campaign.id}}
```

- Keep one house line per business in its measurement notes; every creative
  uses it unchanged.
- A dataset set to strip custom parameters stops them reaching Meta, but the
  UTMs still reach the store or site analytics, which is where the stop rules
  read from.
- Get it right at creation. Meta limits creative edits, so plan on a new
  creative for a new line ([meta-api-behaviours.md](meta-api-behaviours.md)).

## Landing URLs

- The page the pack's record names, exactly, and nothing else.
- Check it returns status 200 on build day.
- If the page redirects, check that the UTMs survive the redirect.
