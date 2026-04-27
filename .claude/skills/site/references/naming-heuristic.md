# Domain Naming Heuristic

A repeatable playbook for picking a brand-tier domain when the operator hits "I need a domain." Use this when the offer doesn't already have a name. Run via `domain.py check` and validate the top picks with `domain-check --info` before purchase.

The goal is a `.com` (or `.co`, `.app`, `.io`) that reads as a confident standalone brand — not a generic descriptor or a clever-but-forgettable pun. Spend 15 minutes here; the name will outlive the lander by years.

---

## Step 1 — Map the category's existing brand patterns

List the top 5–10 names in the offer's category. Look for naming patterns:

- **Descriptive** ("Quickbooks", "Mailchimp"): tells you what it does
- **Compound noun** ("Notion", "Linear", "Figma"): coined word that sounds like something
- **Action verb** ("Spotify", "Shopify"): does-something-y
- **Object/artifact** ("Slack", "Stripe", "Honey"): a thing in the world
- **Person/place** ("Wendy's", "Asana"): named after someone or somewhere

Note which patterns dominate. Those are saturated; you want a different territory.

## Step 2 — Identify underused naming territories

Among the patterns NOT dominant in the category, which would actually fit the offer's voice? A coaching offer in a sea of "Coach.io" / "TrainerOS" can be named after an object — a knot, a compass, a lantern. A billing tool in a sea of "BillRunner" / "PayPilot" can be named after a moment — `thelastbill`.

The territory should feel surprising-but-right when you say it out loud. If it's just surprising, it'll feel arbitrary. If it's just right, it'll feel like every other brand in the category.

## Step 3 — Pick 4–6 brand directions in those territories

Each direction is a *concept* you'll mine for candidates. Examples:

- **Direction A:** A small, intimate household object (relevant if the offer is about quiet daily practice)
- **Direction B:** A moment in a transformation (relevant if the offer ends a struggle — `thelastbill`, `firstdraft`)
- **Direction C:** A craft or trade verb (relevant if the offer is about workmanship — `forge`, `lathe`)
- **Direction D:** A natural pattern (relevant if the offer is about emergence — `pollen`, `tide`, `bloom`)

Don't workshop the directions to death. 4–6 candidates, 2 minutes each.

## Step 4 — Generate 5–8 candidates per direction

For each direction, ride the concept into adjacent words. If the direction is "small intimate household object," candidates might be: `bell`, `latch`, `pin`, `match`, `wick`, `kettle`, `spoon`, `notebook`. Don't filter yet — quantity over quality at this stage.

End of step 4: ~30 candidate names.

## Step 5 — Run `domain.py check` across multi-TLD

For each candidate, check availability across the relevant TLDs. The default chassis priority:

```bash
python3 .claude/skills/site/scripts/domain.py check <candidate> \
  --tlds .com,.co,.io,.app,.ai,.dev
```

For thematic offers, also try category-specific TLDs:

- Coaching/community → `.coach`, `.club`, `.studio`
- Software/tooling → `.app`, `.dev`, `.tools`
- Editorial/publishing → `.md`, `.press`, `.weekly`
- Local/place → `.us`, `.la`, `.nyc`

Many premium TLDs are dashboard-only at Cloudflare today (`.us`, `.co`, `.io` returned `extension_not_supported_via_api` in earlier probes). Note which require dashboard purchase vs. API.

## Step 6 — Mine the strong root

If a candidate stem is strong but the exact `.com` is taken, try variations:

- **Prefix:** `the-`, `get-`, `use-`, `with-` (`thelastbill`, `getlatch`)
- **Suffix:** `-app`, `-hq`, `-co`, `-studio`, `-club`
- **Compound:** combine two words from your candidate list (`bell` + `forge` = `bellforge`)
- **Slight alteration:** `notebok`, `notebok.io`, `noteboox` (last resort — risks looking misspelled)

Re-run `domain.py check` on variations.

## Step 7 — Retry UNKNOWNs after 30 seconds

`domain-check` occasionally returns transient UNKNOWN states for less-common TLDs. If a candidate you care about returns UNKNOWN, retry once after 30 seconds before assuming it's unavailable. The provider WHOIS path is sometimes rate-limited.

## Step 8 — Validate the final 3 with `domain-check --info`

For your top three candidates, run a richer query that surfaces parked / squatted / offer-for-sale states:

```bash
domain-check <candidate>.com --info
```

Watch for:

- "Parked by speculator with offer-for-sale page" — technically available via aftermarket but at $500–$5000+
- "Active site, content unrelated" — domain is owned but unused; can't acquire without negotiation
- "Truly available" — clean RDAP/WHOIS path, ready for `domain.py buy`

Pick the one with the cleanest history + the strongest fit. Two-name shortlists tend to deadlock; three-name shortlists usually have a clear winner once you read the real WHOIS.

---

## When to skip this heuristic

- The offer already has a brand name in `offer.md` (the operator decided weeks ago; respect that decision)
- The offer is a sub-product under an existing brand (use `<existing-brand>.<sub>.com` or a subdirectory; not a new domain)
- The operator has emotional attachment to a specific name and is past the "ready to consider alternatives" phase

The heuristic exists for the case where the operator is starting fresh and wants a confident answer in 15 minutes. Honor the offer when there's already an answer.
