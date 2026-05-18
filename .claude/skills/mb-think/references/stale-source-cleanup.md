# Stale-Source Cleanup

Use this when the operator says old source material, a claim, an offer detail,
a testimonial usage, or a messaging angle is stale, obsolete, retired, no
longer true, or should stop being used.

The goal is not to erase history. The goal is to reconcile current business
truth so future sessions do not keep using the stale material.

Scope boundary: this workflow starts after a specific stale item is named. If
the operator needs to inventory or ingest transcripts, authenticated community
content, cloud-drive uploads, provider recordings, or mixed private sources,
route to the ingestion/privacy rail first; do not expand stale-source cleanup
into transcript ingestion, provider connectors, newsletter implementation, or
dashboard work.

## Trigger Phrases

- "That source is old."
- "This claim is not true anymore."
- "We do not sell that offer now."
- "Retire this angle."
- "Stop using that proof."
- "This was tested and did not work."
- "The file came from an old SOP."

## Workflow

1. **Name the stale item.** Ask for the smallest exact claim, source, angle,
   offer detail, or file path that should stop guiding future work.
2. **Name the replacement truth.** Ask what should be true now. If the operator
   only knows "not that," record that and keep replacement wording conservative.
3. **Read facts first.** Run `mb status --json --peek`. If save state matters,
   run `mb checkpoint --plan --json` before proposing a saved checkpoint.
4. **Find downstream usage.** Search exact phrases and nearby terms across
   `core/`, `research/`, `decisions/`, `bets/`, `pushes/`, `log/`, and
   `documents/`. Read the files before editing.
5. **Map impact.** Group findings as current truth, source/evidence,
   generated output, decision history, or stale artifact. Current truth lives
   in `core/` and active offer files; source/evidence may stay for audit with
   a stale note.
6. **Propose reconciliation.** Tell the operator which files should change and
   which files should stay as historical evidence.
7. **Record a decision when truth changes.** Use
   `decisions/YYYY-MM-DD-retire-<slug>.md` with `status: accepted` after the
   operator confirms. `## What Changes` must name every affected `core/` or
   per-offer file and describe the removal, replacement, or retirement.
8. **Codify after approval.** Update current truth files. Mark retired angles,
   proof usage, or claims as retired instead of deleting them unless the
   operator explicitly asks for deletion and destructive-operation guardrails
   have been read.
9. **Mark the decision codified.** In the same cleanup pass, flip the cleanup
   decision from `status: accepted` to `status: codified` after the current
   truth files are updated.
10. **Verify read-back.** Re-open edited files and the cleanup decision. Confirm
   the stale phrasing no longer appears in active current-truth sections and
   the decision has exactly one `status:` field set to `codified`.
11. **Checkpoint.** Run `mb checkpoint --plan --json`, show the proposed
   business-readable message, validate it, and save only after approval.

## File Handling

| Finding | Default handling |
| --- | --- |
| Stale claim in `core/offer.md` | Replace or remove from current offer truth. |
| Stale offer detail in `core/offers/<slug>/offer.md` | Update the offer-specific file and any brand-level summary it affected. |
| Retired audience language in `core/audience.md` | Remove from current audience truth or move to "Do not use" language. |
| Retired angle in `core/proof/angles/` | Mark as retired with reason, date, and replacement angle if known. |
| Source research that caused the mistake | Keep it as historical source and add a stale note. |
| Generated push/ad/site copy using the stale claim | Mark for revision; do not publish or reuse until updated. |
| Prior accepted decision now superseded | Add a new decision that supersedes it instead of rewriting history. |

## Decision Shape

```markdown
---
type: decision
date: YYYY-MM-DD
status: accepted
supersedes:
  - decisions/YYYY-MM-DD-older-decision.md
---

# Retire old offer detail

## Decision

We are retiring the old offer detail from current business truth.

## Why

The source was from an older version of the business and no longer matches what
we sell.

## What Changes

Reference files affected:
- `core/offer.md` - remove the old detail and replace it with the current
  promise.
- `core/offers/workshop/offer.md` - update the deliverables section.
- `core/proof/angles/old-angle.md` - mark the angle retired and point to the
  replacement angle.

Outside reference: revise any draft campaign or page copy before publishing.
```

After approved reconciliation, update the same decision to `status: codified`.

## Operator-Facing Summary

Use this shape after reconciliation:

```text
I found the stale claim in three places.

Current truth updated:
- core/offer.md
- core/offers/workshop/offer.md

Historical source kept with a stale note:
- research/YYYY-MM-DD-old-source.md

Decision recorded:
- decisions/YYYY-MM-DD-retire-old-offer-detail.md

Next checkpoint proposal:
- [updated] offer truth after stale-source cleanup
```

Do not require the operator to inspect a git diff. Offer the exact files and
plain-language changes first; technical detail can be shown on request.

## Manual Smoke Path

The sanitized fixture path is `mb/tests/fixtures/stale-source-cleanup/manual-smoke.md`.
It covers obsolete source material, downstream active truth cleanup, an accepted
decision, and a checkpoint message proposal.
