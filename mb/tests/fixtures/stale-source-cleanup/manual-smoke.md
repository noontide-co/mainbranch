# Stale-Source Cleanup Manual Smoke

This is a sanitized fixture path for MAIN-393 / #630. It uses generic offer
language only.

## Setup

Create a temporary business repo with these files:

```text
core/offer.md
core/audience.md
core/offers/workshop/offer.md
core/proof/angles/legacy-speed-angle.md
research/2026-05-01-old-source-import.md
```

Seed the stale phrase in each file:

```text
legacy same-day guarantee
```

The research file should say the source came from an older import. The active
truth files should treat the phrase as current before cleanup.

## Operator Prompt

```text
That old source is stale. We no longer offer the legacy same-day guarantee.
Retire that claim everywhere and keep the current offer conservative.
```

## Expected Workflow

1. Run `mb status --json --peek`.
2. Search active and source files for `legacy same-day guarantee`.
3. Report downstream usage without asking the operator to inspect a git diff.
4. Add a stale note to `research/2026-05-01-old-source-import.md`.
5. Create `decisions/YYYY-MM-DD-retire-legacy-same-day-guarantee.md` with
   `status: accepted` and `## What Changes` naming the active files.
6. Remove the stale claim from:
   - `core/offer.md`
   - `core/audience.md`
   - `core/offers/workshop/offer.md`
7. Mark `core/proof/angles/legacy-speed-angle.md` as retired instead of deleting it.
8. Flip the cleanup decision from `status: accepted` to `status: codified`.
9. Re-open edited files and confirm the stale phrase no longer appears in
   active current-truth sections.
10. Re-open the decision and confirm it has exactly one `status:` field set to
    `codified`.
11. Run `mb checkpoint --plan --json`.
12. Propose a business-readable checkpoint message such as
   `[updated] offer truth after stale-source cleanup`.

## Pass Condition

The cleanup passes when current truth no longer uses the obsolete claim, the
source remains auditable with a stale note, the codified decision explains what
changed, and the checkpoint proposal is business-readable.
