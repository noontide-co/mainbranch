# Offers, Bets, Pushes, And Proof

Use this reference whenever a workflow needs to decide whether an idea belongs
in an offer file, a bet file, a push record, a proof file, or a decision.

## Short Answer

- **Offer:** what the business sells or may sell repeatedly.
- **Bet:** a time-boxed wager about whether a direction should continue,
  change, graduate, pause, or stop.
- **Push:** the coordinated work that ships something to an audience.
- **Reusable playbook:** an engine-packaged operating recipe many businesses
  can run.
- **Push playbook:** this push's run record: approvals, provider boundary,
  checks, manual steps, evidence, and outcome hooks.
- **Proof:** evidence that a claim is true.
- **Decision:** the rationale for a choice that changes durable truth.

Business-readable explanation:

> The offer is what we might keep selling. The bet is what we are testing. The
> push is the coordinated work that puts the test into the world. A reusable
> playbook is the recipe. A push playbook is this run's approval and evidence
> record. Proof is the evidence we can safely reuse. A decision explains why
> durable truth changed.

## File Map

| Business meaning | Canonical path |
| --- | --- |
| Single-offer truth | `core/offer.md` |
| Multi-offer portfolio thesis | `core/offer.md` |
| Durable per-offer truth | `core/offers/<slug>/offer.md` |
| Optional per-offer audience | `core/offers/<slug>/audience.md` |
| Company-wide proof folder | `core/proof/` |
| Company-wide testimonial proof | `core/proof/testimonials.md` |
| Company-wide typicality proof | `core/proof/typicality.md` |
| Company-wide proof angles | `core/proof/angles/*.md` |
| Offer-specific proof folder | `core/offers/<slug>/proof/` |
| Offer-specific testimonial proof | `core/offers/<slug>/proof/testimonials.md` |
| Time-boxed wager | `bets/YYYY-MM-DD-slug.md` |
| Coordinated work | `pushes/<YYYY-MM-DD-slug>/push.md` |
| Reusable operating recipe | `.claude/playbooks/<name>/` |
| Per-push playbook run | `pushes/<slug>/playbooks/<playbook>.md` |
| Rationale for changing truth | `decisions/YYYY-MM-DD-slug.md` |

Older repos may have `reference/` compatibility bridges or offer-specific files
such as `core/offers/<slug>/testimonials.md`. Read those as legacy context, but
write new proof under `core/proof/` or `core/offers/<slug>/proof/`.

File-canonical proof targets:

- Individual permissioned testimonials go to `testimonials.md`.
- Aggregate outcome context, average-case timelines, caveats, and typicality go
  to `typicality.md`.
- Durable emotional, competitive, or claims angles go under `angles/`.
- Proof that only supports one offer uses the matching files under
  `core/offers/<slug>/proof/`.
- If the proof type is new, create a clearly named file inside the appropriate
  proof folder instead of scattering proof beside offer files.

## Routing Rules

Create or update a **bet** when the operator is testing a direction with a
deadline, appetite, target, evidence, or verdict. Examples: "test Petaluma HVAC
for two weeks," "see if founder calls beat async audits," "try a $49 workshop."

Create or update an **offer** only when the business is ready to preserve what
it sells or may sell repeatedly. Examples: confirmed promise, pricing,
mechanism, deliverables, guarantee, qualification rules, or checkout/fulfillment
details.

Create or update a **push** when there is coordinated execution: a launch,
drop, challenge, promo, content sequence, lander, ads plan, provider setup
playbook, or internal adoption effort.

Use a **reusable playbook** when the operator is running a repeatable Main
Branch operating recipe, such as a Google Ads search launch. The reusable
playbook lives in the engine/package and should be public, sanitized, and
opinionated.

Create or update a **push playbook** when the current push needs a run record:
approval state, provider boundary, manual steps, readiness checks, safe
provider refs, validation evidence, and outcome criteria. A push playbook is
not proof that Main Branch can mutate a provider account.

Create or update **proof** when the new information is evidence: testimonials,
case studies, outcome summaries, typicality notes, screenshots summarized into
public-safe claims, or approved proof angles.

Create a **decision** when the operator chooses to change durable truth, split
or merge offers, graduate a child repo, retire an offer, or make a migration
plan.

## Single-Offer And Multi-Offer

In a single-offer repo, `core/offer.md` is the durable offer truth.

In a multi-offer repo, `core/offer.md` is the portfolio thesis: what the
business sells overall, who the offers are for, and how the offers relate.
Per-offer specifics live in `core/offers/<slug>/offer.md`.

Do not rename, delete, merge, split, or move offer folders just because they
look stale. Ask first and require either:

- an accepted decision,
- a migration plan the operator approves, or
- explicit operator instruction for the destructive move.

Paused, dead, superseded, or graduated offers should remain inspectable until a
decision or migration plan says what happens. Prefer marking status and linking
context over deleting history.

## Live Validation Wagers

An idea can be both a bet and an offer candidate.

Example: "Petaluma HVAC"

- Open a bet in `bets/YYYY-MM-DD-petaluma-hvac.md` to test whether the direction
  has demand, budget, and proof.
- Link existing research, decisions, and pushes as evidence.
- Draft or update `core/offers/petaluma-hvac/offer.md` only when the operator
  wants a durable offer candidate to preserve promise, pricing, mechanism, and
  delivery assumptions.
- Keep the bet as history even if the offer graduates. The bet records what was
  tested and what was learned.

## Graduation

A successful bet can graduate into one or more durable changes:

- update an existing offer;
- create a new per-offer file;
- create a push or playbook;
- instantiate a reusable playbook into a push playbook run;
- update proof, audience, voice, or strategy;
- create an accepted decision;
- justify a linked child repo for a site, offer, client, finance, ops, or
  execution boundary.

The bet remains in `bets/` with its verdict and evidence. The offer becomes the
current durable truth only after the operator accepts that change.

For paid-search or other spend tests, press for outcome criteria before the
push begins: what counts as a win, a useful loss, a bad test, or an
inconclusive test. Start from offer, audience, search intent, lander readiness,
conversion path, budget, and KPI. Do not require historical account data when
the offer is new.

## Active Offer Resolution

Resolve offer context without turning local session state into strategy:

1. Start from `mb status --json --peek` and other CLI facts already gathered.
2. If a current CLI/status field names active offer context, use it.
3. If `core/offers/` exists and no CLI fact resolves the offer, ask which offer
   this work is about, or offer an `all` / brand-level option.
4. Treat the choice as session-scoped unless the operator explicitly asks to
   save local state.
5. Read `.vip/local.yaml` only as a legacy clue. Confirm it before acting and
   never write it without explicit approval.

When in doubt, ask a business question:

> Is this something you want to keep selling, or something you want to test
> before deciding?
