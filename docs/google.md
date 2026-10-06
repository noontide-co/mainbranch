# `mb google`: read Search Console and GA4

`mb google` reads a business's Search Console site and GA4 property with the
repo's Google sign-in. It never writes anything to Google. There are three
commands:

| Command | What it reads | Google method |
| --- | --- | --- |
| `mb google sc query` | Search performance rows (clicks, impressions, CTR, position) | Search Console `searchAnalytics.query` |
| `mb google sc sitemaps list` | Submitted sitemaps and their status | Search Console `sitemaps.list` |
| `mb google ga4 report` | A GA4 report table | Analytics Data API `properties.runReport` |

Each prints a table by default. Add `--json` to get one result envelope
(`docs/json-output-contract.md`) with the schema name `mb.google.sc.query`,
`mb.google.sc.sitemaps` or `mb.google.ga4.report`. Every command takes
`--repo PATH` (default `.`).

## Before you start

A person signs the repo in once, in a terminal:

```bash
mb connect google --oauth --client-file <Desktop client JSON> \
  --metadata search_console_site=sc-domain:example.com \
  --metadata ga4_property_id=123456789
mb connect test google
```

Setup, the Google Cloud steps and headless sign-in are in
[`connect.md`](connect.md#google-search-console-and-ga4).

The site and the property come only from what the sign-in recorded. There
are no `--site` or `--property` flags. To change either, record it again
with `mb connect google --metadata search_console_site=<site>` or
`--metadata ga4_property_id=<property-id>`.

The Google sign-in can read every property the Google account can see.
These commands read only the recorded ones, but a command run through
`mb connect exec google` is not held to that rule.

The access token is minted inside the `mb` process from the stored sign-in.
It is never printed, returned in JSON, written to disk or passed to another
program.

## `mb google sc query`

```bash
mb google sc query --start 2026-09-01 --end 2026-09-30 --dimensions query,page
mb google sc query --start 2026-09-01 --end 2026-09-30 \
  --dimensions date --filter query:contains:shoes --fresh --json
```

| Option | Meaning |
| --- | --- |
| `--start`, `--end` | Required. `YYYY-MM-DD`, in Pacific Time (`America/Los_Angeles`), as Search Console counts days. Both days are included. |
| `--dimensions` | Group by `query`, `page`, `date`, `country`, `device`, `searchAppearance`. Comma-separated or repeated. None gives one total row. |
| `--type` | `web` (default), `image`, `video`, `news`, `discover`, `googleNews`. |
| `--filter` | `dimension:operator:expression`, repeatable, and every filter must match. Dimensions are `query`, `page`, `country`, `device`, `searchAppearance`. Operators are `equals`, `notEquals`, `contains`, `notContains`, `includingRegex`, `excludingRegex`. The expression may contain `:`. |
| `--row-limit` | 1 to 25,000 (default 1,000). |
| `--start-row` | Zero-based first row, for paging (default 0). |
| `--fresh` | Include data that is not final yet (`dataState: all`). By default only final data is read. |

The JSON result has `site`, `range` (`start`, `end`, `timezone`), `type`,
`dimensions`, `filters`, `row_limit`, `start_row`, `row_count`,
`may_have_more`, `next_start_row`, `rows` (`keys`, `clicks`, `impressions`,
`ctr`, `position`), `response_aggregation_type`, `data_state` and, when
Google sends it, `metadata` (`first_incomplete_date` or
`first_incomplete_hour`).

To page through results, `may_have_more` is true when a full page came back.
Run the command again with `--start-row <next_start_row>`. Google does not
promise to return every row, only the top ones, sorted by clicks.

## `mb google sc sitemaps list`

```bash
mb google sc sitemaps list
mb google sc sitemaps list --sitemap-index https://www.example.com/sitemap_index.xml --json
```

`--sitemap-index URL` lists the sitemaps inside that index instead of the
ones submitted for the site. The JSON result has `site`, `sitemap_count`
and `sitemaps`. Each sitemap keeps Google's documented fields: `path`,
`lastSubmitted`, `lastDownloaded`, `type`, `isPending`, `isSitemapsIndex`,
`warnings`, `errors` and `contents` (`type`, `submitted`). Any other field is
dropped. Strings longer than 2,048 characters are cut and end in `…`.

## `mb google ga4 report`

```bash
mb google ga4 report --metrics activeUsers,sessions \
  --dimensions date,sessionDefaultChannelGroup \
  --start 2026-09-01 --end 2026-09-30 --order-by sessions:desc
```

| Option | Meaning |
| --- | --- |
| `--metrics` | Required. GA4 metric API names, such as `activeUsers` or `sessions`. |
| `--dimensions` | GA4 dimension API names, such as `date` or `sessionDefaultChannelGroup`. |
| `--start`, `--end` | Required. `YYYY-MM-DD`, in the property's reporting time zone. Both days are included. |
| `--limit` | 1 to 250,000 (default 1,000; Google's own default is 10,000). |
| `--offset` | Zero-based first row, for paging (default 0). |
| `--order-by` | One requested metric or dimension, `NAME` or `NAME:desc` (`NAME:asc` also works). Custom names keep their colons: `customEvent:plan` or `customEvent:plan:desc`. |

Names must start with a letter and use only letters, digits, `_` and `:`.
Google checks whether a name exists. An unknown name gets an answer of
`ga4_request_rejected`.

The JSON result has `property_id`, `range`, `dimensions`, `metrics`,
`limit`, `offset`, `row_count`, `total_row_count` (Google's `rowCount`),
`may_have_more`, `next_offset`, `rows` (`dimensions` and `metrics` as
`{name: value}`, with values as the strings Google returns), `order_by` when
given, and `property_quota`.

## Quotas and pacing

Each command sends one request. If the request never reached Google, it is
retried once; nothing else is retried. `mb` never runs two reads at once.

- Search Console, Search Analytics: 1,200 queries per minute per site and per
  user, 30,000,000 per day and 40,000 per minute per Cloud project. There are
  also short-term (10 minutes) and long-term (1 day) load limits. Grouping or
  filtering by `page` or `query` costs the most, both together most of all,
  and longer date ranges cost more. If you hit the load quota, wait 15
  minutes. Do not re-read the same data over and over.
- Search Console, other calls (sitemaps): 20 per second and 200 per minute per
  user.
- GA4, standard property: 200,000 core tokens per day, 40,000 per hour,
  14,000 per hour per Cloud project, 10 requests at once, and 10 server
  errors per hour per project, after which Google blocks the property for
  that project. Every report asks Google for `returnPropertyQuota`, and the
  result's `property_quota` shows `consumed` and `remaining` for
  `tokensPerDay`, `tokensPerHour`, `tokensPerProjectPerHour`,
  `concurrentRequests`, `serverErrorsPerProjectPerHour` and
  `potentiallyThresholdedRequestsPerHour`. Agents should pace their reads by
  these numbers.

Sources: Search Console usage limits
(<https://developers.google.com/webmaster-tools/limits>) and Data API limits
and quotas
(<https://developers.google.com/analytics/devguides/reporting/data/v1/quotas>).

## Exit codes and rules

| Exit | When | `rule` |
| --- | --- | --- |
| 0 | The read worked, even with zero rows. | none |
| 1 | No Google sign-in in this repo (`next: mb connect google --oauth ...`). | `not_connected` |
| 1 | The sign-in did not grant this product (`next: mb connect google --oauth --reauth`). | `grant_missing` |
| 1 | Google refused the stored sign-in, recorded for `mb connect status` (`next: mb connect google --oauth --reauth`). | `reauth_required` |
| 1 | Another token or credential-store problem, with that rule and its repair. | for example `token_unreachable`, `oauth_grant_missing` |
| 1 | Google answered 401. | `search_console_auth_rejected`, `ga4_auth_rejected` |
| 1 | Google answered 403 or 404: the account cannot read the site or property. | `search_console_no_access`, `ga4_no_access` |
| 1 | The API is not enabled in the client's Cloud project. | `search_console_api_disabled`, `ga4_api_disabled` |
| 1 | A quota or rate limit. `quota` names Google's reason when it gives one from a fixed list, such as `RESOURCE_EXHAUSTED`, `quotaExceeded` or `rateLimitExceeded`. | `quota_exhausted` |
| 1 | Another 4xx answer. | `search_console_request_rejected`, `ga4_request_rejected` |
| 1 | A redirect (3xx). It is never followed, so the token never reaches a second URL. | `search_console_unexpected_redirect`, `ga4_unexpected_redirect` |
| 1 | A 5xx answer, which is not retried. | `search_console_server_error`, `ga4_server_error` |
| 1 | Google could not be reached, after one retry. | `search_console_unreachable`, `ga4_unreachable` |
| 1 | An unreadable answer. | `search_console_response_malformed`, `ga4_response_malformed` |
| 2 | No `search_console_site` is recorded. | `site_not_recorded` |
| 2 | No `ga4_property_id` is recorded. | `property_not_recorded` |
| 2 | A date is not `YYYY-MM-DD`, or `--start` is after `--end`. | `bad_date` |
| 2 | `--row-limit` is outside 1-25,000, or `--start-row` is negative. | `row_limit_range` |
| 2 | `--limit` is outside 1-250,000, or `--offset` is negative. | `limit_range` |
| 2 | A Search Console dimension is not in the list, or is repeated. | `unknown_dimension` |
| 2 | A `--filter` is not `dimension:operator:expression` with known values. | `filter_format` |
| 2 | `--type` is not in the list. | `unknown_type` |
| 2 | A GA4 name or `--order-by` is not well formed. | `name_format` |
| 2 | `--order-by` names something that was not requested. | `order_by_unknown` |
| 2 | `--sitemap-index` is not an http(s) URL. | `sitemap_index_format` |
| 2 | `.mb/connect.yaml` could not be used. | `connect_config_refused` |

A refusal (exit 2) calls nothing: no token is minted and Google is not asked.
Failures print `mb google ...: <summary> (<rule>)` and a `next:` line on
stderr. With `--json`, the same failure is also written to stdout as an
envelope with `ok: false`, `state`, `rule`, `summary`, `repair_command` and
`exit_code`. A provider failure adds `http_status` and, for a quota, `quota`.
A read never changes the recorded status, except for `reauth_required`.

## What is never shown

- No token, refresh token or client secret, in any output or `repr`.
- No text from Google's error answers. Only the HTTP status and a fixed list
  of reason codes are used, to pick the rule.
- Row values are data and are returned as Google sent them in `--json`. The
  table view strips ANSI escape sequences and control characters and keeps
  each row on one line, so a hostile search query cannot write to your
  terminal. Wide cells are cut at 80 characters.

## Not here yet

URL inspection (`mb google sc inspect`), a private `--out` file mode and
skill wiring come in later releases. Request indexing has no API; it stays in
the Search Console website.
