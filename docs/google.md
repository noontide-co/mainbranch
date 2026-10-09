# `mb google`: read Search Console and GA4

`mb google` reads a business's Search Console site and GA4 property with the
repo's Google sign-in. It never writes anything to Google. There are four
commands:

| Command | What it reads | Google method |
| --- | --- | --- |
| `mb google sc query` | Search performance rows (clicks, impressions, CTR, position) | Search Console `searchAnalytics.query` |
| `mb google sc sitemaps list` | Submitted sitemaps and their status | Search Console `sitemaps.list` |
| `mb google sc inspect` | The index status of one URL | Search Console `urlInspection.index.inspect` |
| `mb google ga4 report` | A GA4 report table | Analytics Data API `properties.runReport` |

Each prints a table by default. Add `--json` to get one result envelope
(`docs/json-output-contract.md`) with the schema name `mb.google.sc.query`,
`mb.google.sc.sitemaps`, `mb.google.sc.inspect` or `mb.google.ga4.report`. Every command takes
`--repo PATH` (default `.`).

## Who uses these reads

The `mb-site` skill (queries, indexing, sitemaps, sessions) and the `mb-ads`
skill (GA4 sessions and conversions) call these commands with `--json`, or
`--out` for large pulls, and read the site and property only from the repo's
recorded sign-in. When the repo is not signed in, they tell the person to run
`mb connect google --oauth` themselves (an agent never runs the sign-in) and
fall back to asking for a manual export. Codex reaches the same commands
through the generated `AGENTS.md` routing rules. Inspect one page at a time:
never loop over a sitemap.

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
`--metadata ga4_property_id=<property-id>`. An empty value
(`--metadata search_console_site=`) removes it, and the reads then refuse
with `site_not_recorded` or `property_not_recorded`.

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

## `mb google sc inspect`

```bash
mb google sc inspect --url https://www.example.com/shoes/
mb google sc inspect --url https://www.example.com/shoes/ --json
```

This shows the status of the version in Google's index only. The API has
no live test, and requesting indexing has no API either; both stay in the
Search Console website.

`--url` must be a full `http` or `https` URL under the recorded site. It
cannot contain a user name or password, a `#fragment`, spaces, control
characters, `\`, or `.` or `..` path segments. For a domain site
(`sc-domain:example.com`), the URL's host must be that domain or one of its
subdomains. For a URL-prefix site (`https://www.example.com/blog/`), the
URL must start with the prefix: the scheme and host are compared in lower
case and the path is compared exactly. Any other URL is refused with
`url_outside_site`, and nothing is sent to Google. Use the host's punycode
form (`xn--...`) with no trailing dot, as Search Console records it; a
Unicode or trailing-dot host is refused with `url_format`, and the message
says so. The request sends the
recorded site as `siteUrl`, so there is no flag to change it.

The JSON result has `site`, `inspection_url` and `inspection_result`, which
keeps only Google's documented fields:

- `indexStatusResult`: `verdict`, `coverageState`, `robotsTxtState`,
  `indexingState`, `lastCrawlTime`, `pageFetchState`, `googleCanonical`,
  `userCanonical`, `crawledAs`, `sitemap` and `referringUrls`.
- `ampResult`: `verdict`, `ampUrl`, `robotsTxtState`, `indexingState`,
  `ampIndexStatusVerdict`, `lastCrawlTime`, `pageFetchState` and `issues`
  (`issueMessage`, `severity`).
- `mobileUsabilityResult` (deprecated by Google): `verdict` and `issues`
  (`issueType`, `severity`, `message`).
- `richResultsResult`: `verdict` and `detectedItems` (`richResultType`, and
  `items` with `name` and `issues`).
- `inspectionResultLink`, but only when it is a
  `https://search.google.com/` link with no space, control, bidi or line
  separator character in it.

Any other field is dropped. Strings longer than 2,048 characters are cut and
end in `…`, and each list keeps at most 32 entries. The default output is a
short summary: the verdict and coverage state, robots.txt, indexing and page
fetch states, the last crawl, the canonicals, and counts.

URL Inspection has its own, much smaller quota: 2,000 inspections a day
and 600 a minute per site. Inspect the pages you need, not the whole site.

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
Spaces around a name are trimmed; a newline, tab or other character in a
name is refused with `name_format`.
They may end in `[event_name]`, the form GA4 uses for custom definitions
registered before October 2020, such as `customEvent:level[level_up]`.

If you request both `X` and `X:desc` (for example `keyEvents` and a key
event named `desc`), `--order-by X:desc` could mean either, so it is refused
with `order_by_ambiguous`. Write `X:desc:asc` or `X:desc:desc` to sort by
`X:desc`, or `--order-by X` to sort by `X` ascending.
Google checks whether a name exists. An unknown name gets an answer of
`ga4_request_rejected`.

The JSON result has `property_id`, `range`, `dimensions`, `metrics`,
`limit`, `offset`, `row_count`, `total_row_count` (Google's `rowCount`),
`may_have_more`, `next_offset`, `rows` (`dimensions` and `metrics` as
`{name: value}`, with values as the strings Google returns), `order_by` when
given, and `property_quota`.

## `--out`: keep a large pull in a private file

Every read takes `--out PATH`. It writes the same JSON that `--json` prints
(the envelope, never a token or grant) to PATH with mode 0600, created in one
step, and prints only a short summary: the path, the row count and
`may_have_more`. With `--json` the summary is JSON (`mb.google.out`). A path
under your home folder is shown as `~/...`, so the summary never prints your
username, and `safe_to_share: true` holds; there is no absolute-path field, so
an agent opens the file by the path it passed to `--out` (expand `~` to the
home folder). Add
`--force` to replace an existing file.

```bash
mb google sc query --start 2026-09-01 --end 2026-09-30 --dimensions query,page \
  --row-limit 25000 --out ~/pulls/queries-2026-09.json
```

A pull is the business's private data, so `--out` is judged before anything is
read from Google (a refused path costs no quota) and refuses with exit 2:

| `rule` | When |
| --- | --- |
| `out_path_in_repo` | PATH is inside a git checkout, the business repo included, and git does not report it ignored (a tracked file, or one `git add` would pick up). `--force` never lifts this. When `GIT_DIR` or `GIT_WORK_TREE` is exported (even as an empty value, which git also counts as set and refuses to run with), the path is judged a second time with them, and refused unless both answers allow it; a refusal from that second judgment says it comes from the checkout those variables name. |
| `out_temp_not_ignored` | PATH is in a git checkout and git ignores the file, but not its temporary file `.<name>.mb-out.tmp` in the same folder (for example `.gitignore` lists only `report.json` or `*.json`, or `dir/*` followed by `!dir/*.tmp`). The report is written to that temporary file first, so git must ignore both paths; a negation that re-includes the temporary file is refused. |
| `out_path_git_unknown` | PATH is inside a checkout and git could not answer, or `mb` could not place the path in the checkout (for example `BIZ/` for `Biz/` on a case-insensitive disk), so it cannot check the ignore rule. Also when an exported `GIT_DIR` or `GIT_WORK_TREE` names a repository git cannot use, or a work tree `mb` cannot examine (it is never counted as outside), and when the checkout sets `core.ignorecase` to false on a disk that does not tell case apart and a folder in PATH is spelled differently from the one on disk (git's rules would be matched against one spelling while the file lands in the other). The path is refused and nothing is read; the message says which. |
| `out_path_exists` | The file exists and `--force` was not given. |
| `out_path_not_file` | PATH exists and is not a plain file (a folder, for example). |
| `out_parent_missing` | The folder does not exist. `mb` never creates folders. |
| `out_path_link` | PATH itself is a link, even a dangling one. |
| `out_path_invalid` | PATH is empty or has no file name. |
| `out_force_without_out` | `--force` was given without `--out`. |

Folders above the file may be links (macOS keeps `/tmp` behind one): the
folder is resolved first and the checks run on where it really is, so a link
into a repo is refused by the git rule. An exported `GIT_WORK_TREE` spelled
with another case, or through a link or firmlink, is matched to the real
folder by file identity, so its ignored folders are allowed when PATH spells
its folders as they are on disk.

A refusal shows PATH as you gave it, except that an absolute path under your
home folder is shown as `~/...`, so a refusal (also marked `safe_to_share:
true` with `--json`) never prints your username. A relative PATH is judged by
where it leads from the folder you run the command in: under your home folder
it is shown as `~/...` too (with home `/Users/alex`, `alex/pulls/x.json` typed
in `/Users` shows as `~/pulls/x.json`); anywhere else it is shown as typed. A relative PATH is relative to the
folder you run the command from, not `--repo`. A failed read writes nothing. If
the read worked but the file cannot be written, the command exits 1 with
`out_write_failed` (with `--json`, the failure envelope is also on stdout, like the read failures). If `mb` cannot remove its own temporary file after a failed write, the message names it and says to remove it; "nothing was left behind" is only printed when that is true. If the file was written but the temporary copy could not be removed, the command still exits 0 and the summary adds a `warning:` line (with `--json`, an entry in `warnings`) naming `.<name>.mb-out.tmp`, a second copy of the report to remove yourself. The report goes through `.<name>.mb-out.tmp` beside the
file, created exclusively: if that name already exists (a run killed mid-write,
or two runs at once) nothing is written, the existing file is left as it is and
the message names it so you can remove it.

Put the file outside the repo (for example `~/pulls/`), or under a folder git
ignores. The rule is path-exact: git must ignore the file and its
`.<name>.mb-out.tmp`, both. `mb init` repos ignore `.mb/private/`, so
`.mb/private/pulls/` works once that folder exists; `.mb/` itself is not
ignored (a folder like `.mb/pulls/` is refused). Never commit it: the rows are
private business data.

## Quotas and pacing

Each command sends one request. If Google could not be reached, or no answer
came back, the request is retried once; nothing else is retried. A request
that timed out may still have reached Google, but every read is read-only,
so sending it twice changes nothing (it does count against the quota). `mb` never runs two reads at once.

- Search Console, Search Analytics: 1,200 queries per minute per site and per
  user, 30,000,000 per day and 40,000 per minute per Cloud project. There are
  also short-term (10 minutes) and long-term (1 day) load limits. Grouping or
  filtering by `page` or `query` costs the most, both together most of all,
  and longer date ranges cost more. If you hit the load quota, wait 15
  minutes. Do not re-read the same data over and over.
- Search Console, URL Inspection: 2,000 queries per day and 600 per minute
  per site, and 10,000,000 per day and 15,000 per minute per Cloud project.
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

## Sources

Google's API reference pages for each method:

- `searchAnalytics.query`:
  <https://developers.google.com/webmaster-tools/v1/searchanalytics/query>
- `sitemaps.list`: <https://developers.google.com/webmaster-tools/v1/sitemaps/list>
  and the Sitemap resource, <https://developers.google.com/webmaster-tools/v1/sitemaps>
- `urlInspection.index.inspect`:
  <https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect>
  and its result fields,
  <https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult>
- `properties.runReport`:
  <https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport>
  and the API names,
  <https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema>

Quotas: Search Console usage limits
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
| 1 | Google could not be reached, or no answer came back, after one retry. | `search_console_unreachable`, `ga4_unreachable` |
| 1 | An unreadable answer, or an inspection whose `inspectionResult` is not an object. | `search_console_response_malformed`, `ga4_response_malformed` |
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
| 2 | `--order-by X:desc` (or `X:asc`) when both `X` and `X:desc` were requested. | `order_by_ambiguous` |
| 2 | `--url` is not a plain http(s) URL. | `url_format` |
| 2 | `--url` is not under the recorded Search Console site. | `url_outside_site` |
| 2 | `--sitemap-index` is not an http(s) URL. | `sitemap_index_format` |
| 2 | `.mb/connect.yaml` could not be used. | `connect_config_refused` |
| 2 | `--out` refused (see `--out`; nothing was read). | `out_*` |
| 1 | The read worked but the `--out` file could not be written. | `out_write_failed` |

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
  terminal. It also removes bidi controls (U+202A-202E, U+2066-2069,
  U+200E, U+200F, U+061C) and turns line separators (U+2028, U+2029) into
  spaces. Wide cells are cut at 80 characters.

## Not here yet

Request indexing has no API; it stays in the Search Console website.
