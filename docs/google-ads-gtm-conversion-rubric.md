# Google Ads, GTM, and Conversion Tracking Rubric

This is the implementation rubric for Main Branch-generated landers and sites
that are meant to run paid traffic. It answers which GTM container to use,
which conversion actions exist, which events fire, where config belongs, how to
verify the setup, and what the operator must approve before launch.

Linked decision:
[decisions/2026-05-04-google-ads-gtm-conversion-rubric.md](../decisions/2026-05-04-google-ads-gtm-conversion-rubric.md).

## Product Boundary

Main Branch recommends and verifies measurement readiness. It does not seize
control of Google accounts.

`mb` owns deterministic facts:

- repo-safe connection metadata;
- local credential presence and provider probes when implemented;
- static site instrumentation checks;
- browser smoke results;
- safe repair commands and JSON readiness states.

Skills own judgment:

- explaining setup to the operator;
- deciding whether paid traffic is blocked;
- drafting GTM/Ads naming and conversion plans;
- asking for explicit approval before publishing, uploading, or spending.

Google Ads, GTM, Cloudflare, consent tools, booking tools, Stripe, and CRMs own
provider state. Main Branch records the durable plan and evidence, but it does
not become the provider.

## Default Stack

| Layer | Default | When to choose another path |
|---|---|---|
| Tag manager | GTM web container | gtag-only is acceptable for a content-only or analytics-only site with no paid traffic and no near-term third-party tags. |
| Ads conversion tags | Google Ads conversion tags in GTM | GA4-imported conversions can be secondary diagnostics, but paid campaigns should have explicit Google Ads conversion actions for primary goals. |
| Click attribution | Conversion Linker or equivalent Google tag behavior in GTM | Do not omit click attribution on paid landers. |
| First-party transport | Cloudflare Google Tag Gateway when the domain is already on Cloudflare | Standard GTM is acceptable when Cloudflare is not in use. Server-side GTM is a later upgrade. |
| Consent | Consent Mode-compatible banner/CMP when EEA/UK or personalization is in scope | A simple US-only informational banner can be acceptable for non-personalized measurement, but the operator owns legal compliance. |

GTM is required once the operator chooses paid traffic, retargeting, enhanced
conversions, analytics-driven iteration, or multiple tags. It is optional for a
plain content site.

## Beginner Setup Path

For a first paid lander, the beginner-safe setup path is:

1. Create or choose the Google account that owns this business.
2. Create the Google Ads account for this business, or choose the existing
   account. Use a manager account only when the operator manages more than one
   Ads account.
3. Create a GTM web container for the production site.
4. Install the GTM container on the generated site through `/mb-site`
   instrumentation.
5. In GTM, add the Google tag, Conversion Linker when needed, consent defaults
   and updates, and event triggers for the selected `mb_*` events.
6. In Google Ads, create conversion actions using the naming and goal rules in
   this rubric.
7. In GTM, map `mb_*` dataLayer events to Google Ads conversion tags.
8. Use GTM Preview/Tag Assistant and a browser smoke to verify that tags fire.
9. Publish the GTM container only after the operator reviews it.
10. Launch paid traffic only after the operator approves consent/privacy,
    conversion actions, billing, budgets, and campaign launch.

Agents may draft the checklist and configuration plan. The operator creates
accounts, accepts terms, publishes GTM, and launches campaigns.

## Business and Account Granularity

Use these boundaries:

- one business repo per business/account boundary;
- one Google Ads conversion customer per business unless the operator has a
  manager-account structure;
- one GTM account per business when possible;
- one GTM web container per site and environment;
- one production conversion action set per offer goal.

Do not share a GTM container or Google Ads conversion action across unrelated
business repos. Do not send preview/staging traffic into production conversion
actions.

Suggested GTM container name:

```text
<business>-<site>-<environment>
```

Example:

```text
acme-diagnostic-prod
```

## State and Storage Rules

### Safe in an Access-Controlled Business Repo

These values are not credentials. They can be stored in a private or
access-controlled business repo when they help operators and agents inspect the
launch plan. If a business repo is public, use placeholders or local/provider
metadata instead.

- GTM container ID, such as `GTM-XXXXXXX`;
- GA4 measurement ID, such as `G-XXXXXXXXXX`;
- Google Ads customer ID;
- Google Ads conversion action resource names or human labels;
- Cloudflare zone/site/project names;
- site domain and environment;
- selected conversion events;
- consent posture and policy links;
- sanitized offline import schema;
- verification checklist results that do not expose customer data.

Today `/mb-site` can read opt-in tracking fields from resolved `offer.md`
frontmatter, such as:

```yaml
gtm_container_id: GTM-XXXXXXX
ga4_measurement_id: G-XXXXXXXXXX
meta_pixel_id: "000000000000000"
```

Those fields are acceptable in a private business repo when the operator wants
agents to inspect the plan. They are not sufficient proof of readiness. Future
provider work should prefer `.mb/connect.yaml` for repo-safe connection
metadata and build-time environment variables for site deployment values.

### Public Examples Must Use Placeholders

Committed public docs, templates, and fixtures must never contain real account
IDs, conversion labels, customer data, conversion values, API responses, or
private URLs. Use placeholder IDs such as `GTM-XXXXXXX`, `AW-XXXXXXXXX`, and
`customers/0000000000/conversionActions/111111111`.

### Never Commit

Never commit:

- API tokens, OAuth refresh tokens, service-account JSON, client secrets, or
  Google Ads developer tokens;
- raw leads, CRM exports, customer lists, booking records, conversion uploads,
  or enhanced-conversion user identifiers;
- email, phone, name, address, or hashed PII;
- conversion values tied to individual customers;
- unpublished GTM export files if they expose private account details;
- local browser traces, HAR files, or screenshots with account/customer data.

Use the OS keychain, runtime-specific secret storage, environment variables,
1Password, `.env.local`, `.claude/settings.local.json`, or
`~/.mainbranch/secrets/` for local-only secrets and raw provider data.

## Site Instrumentation

When GTM is enabled, generated static HTML must include:

- the GTM script as high in `<head>` as the generator can place it;
- the GTM noscript iframe immediately after the opening `<body>` tag;
- the dataLayer initialization before the GTM loader when page-level metadata
  is needed by initial tags;
- no Subresource Integrity attribute on Google tag/GTM loaders;
- CSP support through nonces when the site uses a strict CSP.

The committed site source should not hardcode a live GTM ID in reusable
templates. Prefer build-time configuration:

```env
PUBLIC_GTM_CONTAINER_ID=GTM-XXXXXXX
PUBLIC_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
```

For pure static sites, use a build step that replaces placeholders with
environment variables before deploy. For framework sites, use the framework's
public environment-variable convention.

Cloudflare Pages production and preview environments must use separate
measurement values when preview traffic should not count as production
conversions.

If a generated one-off private site repo inlines the GTM ID during early
implementation, that is a compatibility bridge, not the long-term template
contract. Public templates and reusable examples must keep placeholders or env
variables.

## DataLayer Contract

Generated sites should push Main Branch events to `window.dataLayer`.

Base payload:

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "mb_lead_submit",
  mb_site_id: "diagnostic-lander",
  mb_offer_id: "diagnostic-call",
  mb_event_id: "01J00000000000000000000000",
  mb_conversion_kind: "lead_submit",
  mb_destination: "lead_form",
  value_basis: "configured_in_ads"
});
```

Payload rules:

- `event` is required.
- `mb_event_id` should be unique per event occurrence when the site can
  generate one.
- `mb_offer_id` should match the offer slug used by the business repo.
- `mb_site_id` should be stable for the site/environment.
- `mb_conversion_kind` should mirror the event family.
- `mb_destination` should describe the destination without exposing private
  data.
- `currency` is allowed only for confirmed purchase/deposit events.
- `value` is allowed only when the operator has chosen value-based reporting
  and the value is not sensitive in the repo or browser context.

Do not push email, phone, full name, address, raw CRM notes, booking notes,
customer IDs, or hashed user identifiers by default.

## Event Vocabulary

Use these event names exactly:

| Event | Trigger | Default Ads role |
|---|---|---|
| `mb_cta_click` | User clicks a meaningful CTA. | Secondary |
| `mb_form_start` | User starts a lead/signup form. | Secondary |
| `mb_lead_submit` | Lead form succeeds. | Primary for lead-gen |
| `mb_calendar_click` | User clicks an outbound calendar/booking URL. | Secondary unless no booking confirmation exists |
| `mb_booked_call` | Booking is confirmed by provider callback or thank-you page. | Primary for call funnels |
| `mb_email_signup` | Email/newsletter signup is confirmed. | Primary for signup funnels |
| `mb_purchase` | Purchase is confirmed. | Primary for checkout funnels |
| `mb_deposit` | Deposit/application fee is confirmed. | Primary for deposit funnels |
| `mb_offline_conversion_ready` | Offline conversion record is staged for operator review. | Diagnostic; uploaded offline action is primary when used |

Events are intentionally generic enough for `/mb-site`, `/mb-ads`, and future
sidecars to share. GTM maps these events to provider-specific tags, triggers,
and conversion labels.

## Google Ads Conversion Actions

Name conversion actions:

```text
MB - <Offer> - <Action> - <Environment>
```

Use title case for the human-facing action:

- `Lead Submit`
- `Calendar Click`
- `Booked Call`
- `Email Signup`
- `Purchase`
- `Deposit`
- `Offline Qualified Lead`
- `Offline Sale`

Recommended mapping:

| Site goal | Primary conversion action | Secondary conversion actions |
|---|---|---|
| Lead form | `MB - <Offer> - Lead Submit - Prod` | Form Start, CTA Click |
| Booked call | `MB - <Offer> - Booked Call - Prod` | Calendar Click, Lead Submit |
| Purchase | `MB - <Offer> - Purchase - Prod` | CTA Click, Form Start |
| Deposit/application | `MB - <Offer> - Deposit - Prod` | CTA Click, Form Start |
| Email signup | `MB - <Offer> - Email Signup - Prod` | CTA Click |
| Offline sale | `MB - <Offer> - Offline Sale - Prod` | Lead Submit, Booked Call, Offline Conversion Ready |

Use production conversion actions for production traffic only. Preview and
staging environments should either use separate conversion actions or block
Google Ads conversion tags entirely.

Recommended Google Ads settings:

| Setting | Lead/call funnels | Purchase/deposit funnels |
|---|---|---|
| Optimization role | Exactly one primary conversion when possible | Exactly one primary conversion when possible |
| Count | One | Every |
| Attribution | Data-driven when available | Data-driven when available |
| Click-through window | 30 days by default; 60-90 only for longer sales cycles | 7-30 days depending on buying cycle |
| View-through window | Conservative; document if changed | Conservative; document if changed |
| Value | Use configured static value only when meaningful | Use actual value only when privacy-safe and approved |

Secondary events are diagnostics, not optimization goals. Do not optimize a new
campaign against every micro-event just because the site can fire them.

## Click Identifiers

Google Ads auto-tagging appends click identifiers such as `gclid`, `gbraid`,
and `wbraid`. Paid landers should preserve attribution through the Google tag
or Conversion Linker. If a future site implementation captures click
identifiers for offline conversion staging, it must:

- store them only in local/browser or gitignored operational state;
- preserve the landing-page timestamp and consent status;
- avoid committing raw click identifiers to public docs, templates, fixtures, or
  durable markdown;
- include `gclid` when available for offline imports, with `gbraid`/`wbraid`
  support where Google Ads requires it;
- avoid custom conversion variables when the selected identifier type does not
  support them.

Click IDs are not API secrets, but they are user/session attribution data and
should be treated as private operational data.

## Offline Conversions

Offline conversion support starts as staging and review, not automatic upload.

Durable committed files can describe:

- the conversion action name/resource placeholder;
- required columns;
- consent requirements;
- source system;
- review checklist;
- upload history summary without customer rows.

Raw rows belong outside git. A future local path such as
`.mb/offline-conversions/` should be gitignored and should contain only
operator-reviewed staging files.

Minimum staged fields for a future importer:

| Field | Required | Notes |
|---|---|---|
| `conversion_action` | Yes | Google Ads conversion action resource or configured alias. |
| `conversion_date_time` | Yes | Include timezone. |
| `order_id` | Strongly recommended | Helps deduplicate and adjust conversions. |
| `gclid`, `gbraid`, or `wbraid` | Recommended when present | Captured from click URLs or session storage. |
| `user_identifiers` | Optional, approval-gated | Must be normalized/hashed per Google rules and consent-gated. |
| `conversion_value` | Optional | Do not commit customer-level values. |
| `currency_code` | Required when value is present | ISO currency code. |
| `ad_user_data_consent` | Required for EEA/UK user data uploads | Preserve consent status. |

An agent may draft the schema and remind the operator how to upload. It must
not upload offline conversions until a future connector has explicit approval
and smoke evidence.

## Consent and Enhanced Conversions

Consent posture is a launch gate, not an afterthought.

Minimum decisions before paid traffic:

- target geography: US-only, EEA/UK, mixed, or unknown;
- whether remarketing or ad personalization is used;
- whether enhanced conversions are used;
- whether offline conversions or customer lists are uploaded;
- which privacy policy and cookie/consent UI apply.

For EEA/UK or mixed traffic, the setup must support Google Consent Mode signals:

- `ad_storage`
- `analytics_storage`
- `ad_user_data`
- `ad_personalization`

Enhanced conversions require:

- explicit operator approval;
- customer data terms accepted in Google Ads;
- first-party data collected directly from the user;
- consent status preserved when required;
- no committed raw or hashed PII.

If those requirements are not met, enhanced conversions are blocked. The site
can still use standard tag-based conversion tracking where lawful and approved.

## Cloudflare Pages and Tag Gateway

Cloudflare Pages remains the default deploy target for `/mb-site`.

For Cloudflare-hosted paid landers:

1. inject GTM through build-time environment configuration;
2. use Cloudflare Pages environment separation for production vs preview;
3. enable Cloudflare Google Tag Gateway only after the operator approves
   Cloudflare/Google account linking or API configuration;
4. record the endpoint path and measurement ID as local/provider metadata;
5. verify that the deployed page still loads tags and pushes `mb_*` events.

Cloudflare Google Tag Gateway is the preferred lightweight first-party
transport when available. Server-side GTM should wait until one of these is
true:

- monthly paid spend is high enough that signal recovery is economically
  meaningful;
- EEA/UK traffic share makes consent and first-party measurement quality a
  central constraint;
- the operator needs server-side deduplication for Meta CAPI, TikTok Events
  API, or another non-Google server event system;
- an analyst or technical operator can maintain the server container.

## Verification Checklist

A future implementation should produce evidence at these levels.

### Level 0: Repo Plan

- Business repo declares site, offer, environment, GTM container, Google Ads
  conversion customer, and conversion action plan.
- Privacy/consent posture is explicit.
- No secrets or customer rows are committed.

### Level 1: Static Build

- Built HTML includes GTM head script and body noscript when GTM is enabled.
- Built HTML does not include placeholder IDs.
- Reusable templates do not commit live IDs.
- CSP is absent, compatible, or nonce-aware.
- No SRI attribute is attached to GTM/gtag loaders.

### Level 2: Network Probe

- `https://www.googletagmanager.com/gtm.js?id=<GTM_ID>` returns a successful
  response.
- If Cloudflare Google Tag Gateway is enabled, the configured first-party
  endpoint responds for the deployed domain.

### Level 3: Browser Smoke

- A Playwright or equivalent browser run triggers the expected user actions.
- `window.dataLayer` receives the expected `mb_*` events.
- Network logs show GTM/Google tag requests after consent state allows them.
- Preview/staging does not fire production conversion actions.

### Level 4: Provider Preview

- GTM Preview/Tag Assistant confirms expected triggers and tags fire.
- GTM workspace/container version is reviewed before publication.
- Google Ads conversion actions exist and match the primary/secondary plan.

### Level 5: Post-Launch Diagnostics

- Google Ads diagnostics do not report missing tags or consent blockers.
- Delayed conversion reporting is checked after the provider's normal latency.
- Any discrepancy becomes a GitHub issue or campaign decision with sanitized
  evidence.

There is no reliable provider-independent CLI today that proves a deployed page
fires a Google Ads conversion and that Google Ads attributes it immediately.
Static, browser, Tag Assistant, and delayed provider diagnostics are separate
evidence types.

## Future `mb connect` Readiness Shape

Future Google/GTM readiness should follow the existing provider-readiness
contract: a secret reference alone is never healthy.

Core `mb connect` should validate only generic provider connectivity and
repo-safe metadata: a Google credential exists, the account can be reached when
safe probes exist, and the declared metadata is parseable. A future Google Ads
or GTM sidecar should own deeper domain probes such as container contents,
conversion action listing, GTM workspace state, Tag Assistant-adjacent checks,
and Ads diagnostics. `/mb-site` owns local static/browser instrumentation
checks against generated pages.

Sketch JSON:

```json
{
  "provider": "google_ads",
  "state": "ready_for_operator_review",
  "safe_to_share": true,
  "summary": "Google Ads metadata and GTM site instrumentation are present; operator must review GTM publication and consent before launch.",
  "metadata": {
    "ads_customer_id_present": true,
    "gtm_container_id_present": true,
    "site_environment": "prod",
    "primary_conversions": ["mb_booked_call"],
    "secondary_conversions": ["mb_calendar_click", "mb_lead_submit"]
  },
  "evidence": [
    {
      "kind": "static_html",
      "state": "passed",
      "summary": "GTM loader and noscript fallback found in built HTML."
    },
    {
      "kind": "browser_data_layer",
      "state": "passed",
      "summary": "Expected mb_calendar_click and mb_lead_submit events observed."
    },
    {
      "kind": "operator_approval",
      "state": "blocked",
      "summary": "GTM publish and enhanced conversions approval not recorded."
    }
  ],
  "repair": "Review GTM Preview, publish the container if correct, record consent/enhanced-conversion approvals, then rerun the readiness check.",
  "repair_command": "mb connect test google-ads"
}
```

Recommended states:

| State | Meaning |
|---|---|
| `missing` | No relevant metadata or credential path. |
| `declared` | Repo-safe metadata exists, but no provider/local checks have run. |
| `unvalidated` | Credentials or metadata exist, but provider checks are unavailable or inconclusive. |
| `ready_for_preview` | Site instrumentation and container resolution pass. |
| `ready_for_operator_review` | Provider state and conversion plan are present; approval remains. |
| `ready` | Deterministic checks pass and required approvals are recorded. |
| `blocked` | A missing account, consent, publication, or verification issue prevents launch. |

`mb status --json` should summarize this readiness. `mb doctor --json` should
provide the next repair command. Skills should read the JSON instead of
duplicating provider probes.

## Operator Approval Checklist

Before an agent recommends paid launch, the operator must explicitly approve:

- GTM container selection;
- GTM workspace publication to Live;
- Google Ads conversion action selection and primary/secondary status;
- Consent banner/CMP and privacy policy posture;
- Cloudflare Google Tag Gateway or server-side routing if used;
- enhanced conversions if used;
- offline conversion upload if used;
- campaign launch, budget, billing, and spend.

No approval, no launch recommendation.

## Official References

- Google Tag Manager installation:
  <https://support.google.com/tagmanager/answer/14847097>
- Google Tag Manager data layer:
  <https://developers.google.com/tag-platform/tag-manager/datalayer>
- Google Tag Manager with CSP:
  <https://developers.google.com/tag-platform/security/guides/csp>
- Google Consent Mode:
  <https://support.google.com/google-ads/answer/10000067>
- Google Consent Mode reference:
  <https://support.google.com/google-ads/answer/13802165>
- Google enhanced conversions:
  <https://support.google.com/google-ads/answer/9888656>
- Google customer data policies:
  <https://support.google.com/google-ads/answer/7475709>
- Google Ads API offline conversions:
  <https://developers.google.com/google-ads/api/docs/conversions/upload-offline>
- Cloudflare Google Tag Gateway:
  <https://developers.cloudflare.com/google-tag-gateway/>
- Cloudflare Google Tag Gateway API:
  <https://developers.cloudflare.com/api/go/resources/google_tag_gateway/>
