# Creative ledger — what's actually working

One row per creative asset. The agent appends rows from recorded facts
(push logs, the funnel collector, `mb leads grade` output) and proposes a
verdict; you approve it. Code never invents a verdict.

## The one doctrine

An asset is **not working until it produces an ELIGIBLE lead, not a cheap
one.** A low raw CPL on junk leads is a trap (a real business we built had a
$19 raw-CPL set that produced zero eligible customers). Drive KEEP/KILL off
`eligible_cpl` and the `downstream_event`, never off `raw_cpl` or CTR alone.

- **KEEP** — eligible_cpl is at or under target AND a downstream event fired.
- **KILL** — spend is past the test budget with no eligible lead.
- **WATCH** — not enough spend yet to judge; keep it running to a decision.

## The row shape

| asset_id | angle_lever | source | date | spend | ctr | raw_cpl | eligible_cpl | downstream_event | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| example-01 | pain-led / urgency | meta | 2026-06-13 | 120 | 1.8% | 19.00 | (none yet) | 0 booked | WATCH |

Column meanings:

- **asset_id** — stable id for the creative (slug or provider id).
- **angle_lever** — the angle or persuasion lever being tested.
- **source** — the channel/account it ran on (meta, google, organic).
- **date** — when the row's numbers were last trued up (UTC).
- **spend** — spend attributed to this asset for the window.
- **ctr** — click-through rate (diagnostic only, never a verdict driver).
- **raw_cpl** — spend / all leads. The seductive number; do not decide on it.
- **eligible_cpl** — spend / ELIGIBLE leads (`mb leads grade`). The honest one.
- **downstream_event** — the money-path event (booked, paid, replied).
- **verdict** — KEEP / KILL / WATCH, driven by eligible_cpl + downstream.

## Graduating past markdown

This table is v1. When an offer passes ~50 assets, move the same columns to
the owned contact+event spine (`mb spine init --owned`) so the ledger is
queryable with SQL instead of scanned by eye. The columns do not change; only
the store does.
