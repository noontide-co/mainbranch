# Winning-Ad Research

Use this when the operator wants to research before creating ads, organic
content, or a content strategy. The job belongs in `/mb-think` because the
output is research and codified reference, not immediate generation.

Do not copy prompt libraries, raw threads, scraped comments, customer data, or
long excerpts into committed files. Save concise excerpts when allowed and
original synthesis.

## When To Use

Route here when the user asks for:

- customer language or sales-call mining;
- competitor ad, landing-page, pricing, or mechanism research;
- review mining from Trustpilot, Amazon, G2, Capterra, app stores, Reddit, or
  niche review sites;
- winning ad or competitor script teardown;
- TikTok, YouTube, Instagram, or X comment mining;
- social strategy analysis before deciding whether to post full-value content,
  gated giveaways, build-in-public notes, or a hybrid.

After the research is synthesized and codified, route production to `/mb-ads`,
`/mb-organic`, `/mb-site`, or `/mb-ads` sales-video workflows.

## Research Bundle

Run only the tracks needed for the user's question. For broad "research winning
ads" requests, propose a compact bundle:

| Track | Source Material | Output |
|-------|-----------------|--------|
| Customer language | Sales calls, surveys, support tickets, onboarding forms, cancellation notes | Personas, hot phrases, implied fears, objections |
| Competitor gap map | Competitor ads, landing pages, product pages, pricing, reviews | Positioning, mechanism stories, awareness coverage, gaps |
| Review mining | Reviews with rating/date/platform metadata | Before-state language, transformations, objections, identity statements |
| Script teardown | Own winners or likely competitor winners with transcripts | Hook/body/mechanism/objection/reveal/close blueprint |
| Content/comment mining | TikTok, YouTube, Instagram, X comments and replies | Pain clusters, unaware language, triggers, tool mentions, false beliefs |

## Source Quality

Prefer first-party or high-signal public evidence over vibe checks:

- own ad-account winners when the operator provides them;
- sales-call and survey language with private data removed;
- review exports with platform, rating, date, and source link;
- ad transcripts with runtime, format, and performance if known;
- competitor "likely winners" only when there are signals such as repeated
  variations, durable presence, engagement, or visible spend/duplicate clues.

"Longest running" is not proof that an ad is winning. Mark competitor winners
as inferred unless the operator has performance data.

## Output Schemas

### Customer Language

For each persona:

- name the persona in plain English;
- describe the situation, not just demographics;
- capture voiced pain, implied fear, identity to protect or upgrade;
- list 8-15 verbatim hot phrases with source citations;
- list recurring objections by persona.

Codify to `core/audience.md`, offer-specific `audience.md`,
`core/voice.md`, and `core/proof/angles/`.

### Competitor Gap Map

For each competitor:

- positioning angle;
- mechanism story, including named or branded mechanisms;
- persona target;
- format mix with specific proportions when evidence supports it;
- awareness coverage from unaware to most aware;
- what they test that the operator does not.

Across competitors, identify the top three gaps, mechanism opportunities, and
pricing or distribution vulnerabilities. Codify durable gaps to
`core/proof/angles/`, `core/content-strategy.md`, and relevant offer files.

### Review Mining

Cluster only source-backed language:

- before-state phrases;
- transformation moments;
- objections that proved wrong;
- identity statements;
- negative-review patterns and expectation gaps.

Keep testimonial claims separate from typicality. Put permissioned individual
proof in `core/proof/testimonials.md`. Put aggregate average-case, time-to-
outcome, common failure, and "not typical" context in `core/proof/typicality.md`.

### Winning Script Teardown

Break each transcript into:

- hook, including exact opening line and psychological lever;
- body, including villain, mechanism, and credibility timing;
- objection handling before product reveal;
- product reveal timing and framing;
- close, including urgency, identity, or transformation move.

Then synthesize the cross-ad blueprint. The useful output is structure, not
topic copying.

### Content And Comment Mining

For organic comments, cluster:

- top pain clusters;
- unaware language;
- trigger-event language;
- competitor or tool mentions with sentiment;
- false beliefs or assumptions;
- raw emotional language.

Organic comments are not buyer proof. Treat them as language and demand
signals, then decide what belongs in `core/audience.md`,
`core/content-strategy.md`, or `core/proof/angles/`.

When comments are mostly keyword replies to a giveaway, treat them as evidence
of the funnel mechanic and visible participation, not deep audience language.
Separate keyword participation from substantive objections, pain language,
tool mentions, or false beliefs.

## Social Strategy Read

When analyzing a public social-growth example, classify the strategy:

- **Gated comment giveaway:** public post drives keyword comments, then DM or
  link delivery converts attention into leads.
- **Resource-in-post:** the post, thread, repo link, landing page, or document
  carries the useful resource directly in public.
- **Public reply/link playbook:** public replies point interested users to a
  resource or opt-in path, with execution handled manually or by a tested
  provider outside Main Branch.
- **Full-value public post:** the post itself teaches enough to earn trust,
  saves, shares, follows, stars, or profile visits.
- **Build-in-public:** public process, metrics, decisions, and lessons create
  proof and audience memory.
- **Build-cool-stuff-publicly:** useful artifacts shipped in public create
  proof first, then invite opt-in follow-up through a visible link or repo.
- **Hybrid:** full-value public artifact plus optional opt-in for templates,
  repo links, or deeper implementation.

For Main Branch, prefer a hybrid unless a decision says otherwise: publish
enough value publicly to earn trust and GitHub attention, then offer an
operator-approved next step. For X/Twitter specifically, prefer
resource-in-post, build-in-public, build-cool-stuff-publicly, and manual public
reply/link playbooks over comment-to-DM. Do not recommend automated
comment/DM execution without an accepted provider path and smoke evidence.

### DM And Comment Automation Model

- **Drafting the CTA is allowed:** `/mb-organic` can draft "comment keyword" or
  "DM keyword" CTAs as content strategy.
- **Manual/operator-approved follow-up is allowed:** the operator can fulfill,
  reply, or DM outside Main Branch, or explicitly approve a one-off action in a
  supported provider.
- **X interaction-triggered execution is refused today:** Main Branch should
  not execute comment-to-DM, keyword DM, auto-reply, auto-like, auto-follow,
  bulk DM, follower-gated giveaway, or private inbox workflows through Postiz,
  Typefully, X API, ManyChat-style tools, Apify, or browser automation.
- **Future support requires a real provider path:** official authority where
  possible, consent/platform constraints, approval gates, privacy-safe logs,
  rate-limit handling, tests, docs, and runtime smoke evidence.
- **Durable plans become push playbooks:** save reusable resource-delivery or
  provider setup plans under `pushes/<push>/playbooks/<playbook>.md` with
  `type: playbook`. The file records the plan, approval state, safe provider
  state, validation evidence, and outcomes; it is not automation execution.

## Provider Boundaries

- **Apify:** optional read-only enrichment for public scraping/comment exports
  when configured. Useful for TikTok comments, YouTube comments/transcripts,
  Instagram mining, and bounded public X profile/post/reply samples depending
  on actor reliability and operator-accepted terms. It is not an official X
  integration and does not prove full reply-tree coverage, DM delivery, private
  analytics, or conversion. Never ask for X session cookies or raw private
  account exports. Missing Apify never blocks the workflow.
- **Grok/xAI or web search:** optional X/social sentiment path when configured,
  best for topic-level "what are people saying now?" research; otherwise use
  web search, public embeds, screenshots, or manual exports.
- **Postiz:** planned optional scheduling/publishing rail. Treat it as draft,
  schedule, thread, cross-post, and analytics support only where docs and
  connected-channel smoke evidence exist. The 2026-05-07 API smoke proved
  reachability/auth only, not supported draft or scheduling behavior. Do not
  treat it as Main Branch-supported DM automation.
- **X API:** official mutation path for posts, replies, and DMs requires
  developer approval, OAuth user tokens, explicit operator authority, billing
  and rate-limit handling, tests, docs, and smoke evidence. Main Branch does
  not support this automation today.
- **ManyChat-style tools:** comment-to-DM automation may be valid for platforms
  such as Instagram when configured directly in that provider, but it is not a
  Main Branch-supported provider path yet.

Never ask users to paste provider tokens, customer records, ad account exports,
or private DM data into public files or issue comments.

## Copyright And Privacy

For public research files:

- cite source URLs;
- include only concise excerpts needed to support the analysis;
- summarize prompt structures in your own words;
- keep raw scrapes, full prompt libraries, full comment dumps, and private
  customer data out of committed files;
- store temporary raw evidence in OS temp or `.context/` only when needed for
  agent handoff.

## Exit Criteria

Research is ready to hand off when:

- each selected track has a synthesis section;
- source limitations and inferred-vs-known winner status are explicit;
- implications map to specific reference files;
- provider gaps are phrased as optional or unsupported, not hidden blockers;
- the next production skill is clear.
