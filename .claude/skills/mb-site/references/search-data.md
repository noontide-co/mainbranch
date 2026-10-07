# Search Console and GA4 numbers

Load this when a question needs real search or visitor numbers: "which queries
and pages bring clicks", "is this page indexed", "are my sitemaps healthy",
"how many sessions or conversions did the site get". Use the typed `mb google`
reads. Never open the Search Console or Analytics websites for the person, and
never call Google through `mb connect exec`.

## Rules

- Run from the business repo. The Search Console site and GA4 property come
  from what the repo recorded when the person signed in. Never pass or guess a
  site or property; there are no flags for them.
- Add `--json` and read the result; quote numbers as Google returned them.
  For a large pull (thousands of rows), add `--out <file>` instead, where
  the file is outside the repo or under a folder git ignores (git must ignore
  the file and `.<name>.mb-out.tmp`), such as `.mb/private/pulls/`. `--out` writes a private file and prints only a short summary; read the
  file with a tool, then summarize. Never commit it, never paste it whole.
- The answers are the business's private data. Share conclusions, not raw rows.

## Which command

| Question | Command |
| --- | --- |
| Which queries or pages bring clicks | `mb google sc query --start YYYY-MM-DD --end YYYY-MM-DD --dimensions query,page --json` |
| Is this page indexed | `mb google sc inspect --url <page> --json`: one page at a time, only pages that matter. Google allows 2,000 a day and 600 a minute per site. Never loop over a sitemap. Read `inspection_result.indexStatusResult`. |
| Are the sitemaps healthy | `mb google sc sitemaps list --json` |
| Sessions, users or conversions | `mb google ga4 report --metrics sessions,activeUsers,keyEvents --dimensions date --start YYYY-MM-DD --end YYYY-MM-DD --json` |

Search Console data trails real life by about two days. Say which dates you read.

## When it does not work

- `not_connected`, `grant_missing` or `reauth_required`: the person signs in
  themselves with `mb connect google --oauth` (the command names the exact next
  step). Agents never run the sign-in and never ask for a token in chat.
- `site_not_recorded` or `property_not_recorded`: the repo does not know the site or
  property yet. Ask the person; they record it with `mb connect google --metadata`.
- Not connected and the person does not want to connect: ask for a manual export (a
  CSV from Search Console or GA4) and read that.
- `quota_exhausted`: stop and say so; do not retry in a loop.
- Requesting indexing has no API. The person does it in Search Console.

More: `docs/google.md` in the engine repo.
