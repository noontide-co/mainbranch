---
type: decision
date: 2026-07-28
status: proposed
topic: mb estate, an obligation, account, and agency registry
linked_decisions:
  - decisions/2026-05-04-workspace-repo-sensitive-data-boundaries.md
  - decisions/2026-05-08-business-repo-topology-map.md
  - decisions/2026-05-11-mb-books-foundation.md
  - decisions/2026-05-11-data-source-registry.md
tags: [estate, obligations, entities, agencies, compliance, safety, books]
---

# `mb estate`: an obligation, account, and agency registry

## Decision (proposed)

Main Branch should ship `mb estate` as a sibling safety surface to `mb books`.

`mb books` answers "are my numbers right." `mb estate` answers "what do I owe,
to whom, by when, and what have I never checked."

The feature is two things:

1. A **registry**: a declared, per-entity record of legal identity, ownership,
   accounts, agency relationships, recurring obligations, document locations,
   people with authority, and open items.
2. A set of **checks** over that registry that surface what is overdue,
   unfiled, unverified, or unevidenced.

The registry holds references and statuses. It never holds secrets,
credentials, or full identifiers, and it never asserts a legal conclusion. It
records what was observed and when.

This decision is documentation-only. It defines the data model, the command
shape, and the check list that a future implementation slice should build.

## Frame: the gap bookkeeping cannot close

Bookkeeping is transaction-driven. A ledger learns about the world when money
moves. Every accounting tool inherits that shape: the chart of accounts, the
import rules, the reconciliation loop, the close. All of it starts from a row
that already exists.

Obligations are calendar-driven. They exist whether or not money moves, and the
most dangerous ones generate no transaction at all until the moment they become
expensive:

- A flat annual entity tax produces no row until it is paid. An unpaid one
  produces no row ever. The ledger is not wrong; it simply has nothing to say.
- A filing requirement with a zero balance produces no row. Missing it produces
  an agency-issued estimate, which is the first row anyone sees, and by then it
  is not the operator's number.
- A fee tier crossed by revenue growth produces no row until the tier is
  invoiced. The crossing itself is a fact about the ledger that the ledger does
  not compute.
- A credit sitting at an agency produces no row anywhere, because the operator
  never received anything.
- A registered agent renewal, a payroll registration, an insurance certificate,
  and an annual subscription commitment produce rows that look like ordinary
  expenses and carry no encoding of the obligation behind them.

This is a structural gap, not a tooling failure. A perfectly reconciled ledger
with a clean close is fully compatible with two years of unpaid state minimums
and an unfiled return in a jurisdiction the operator forgot they registered in.

The missing artifact is a file that does not exist in any tool the operator
already runs: a declared list of the obligations, accounts, and agency
relationships that exist independent of transactions, with a last-verified date
on each one.

## The failure classes

The proposal comes from one week inside a real multi-entity operation. The
operator runs five entities. During a single reconciliation pass, the following
came to light. All of it is anonymized; the numbers are kept because the
magnitudes are the argument.

**1. Silent unpaid state minimums.** Two entities each carried two years of an
$800 flat annual entity tax, unpaid and unnoticed. No accounting system knew the
obligation existed. A flat annual tax generates no transaction until it is paid,
so there was nothing for a ledger to fail to reconcile.

**2. A fee tier nobody knew about.** One entity crossed a gross-receipts
threshold that triggered an additional annual fee of roughly $900. The crossing
was visible in the books as revenue. The consequence of the crossing was visible
nowhere. No system connected the two.

**3. Estimated assessments from late filings.** A sales-tax agency, receiving no
return for several periods, issued its own estimates. Those estimates ranged
from 1.5x to 7.2x the actual liability. The agency then levied a bank account
for $3,104.86 against $1,828.00 of real tax. The tax was never the problem. The
missing filings were. An operator who files a zero-dollar return on time never
enters this failure class; an operator who owes a small amount and files nothing
gets a number invented for them.

**4. Agency-held credits invisible by design.** The same agency's portal
displays amounts **due**, not amounts **held**. Nearly $1,000 of the operator's
own credits sat unseen because the interface has no screen for them. A refund
warrant issued a year earlier had never been received and had never been chased,
because nothing in the operator's world recorded that it had been issued.

**5. A bank levy on a related entity.** A levy landed on a second entity for a
modest balance. It was reachable because an account funding one business's
operations was registered to a different entity's tax ID. The contract terms
governed the business relationship; the levy followed the registration. Nothing
in the operator's records connected "this account funds Entity B" to "this
account is registered to Entity A."

**6. A return filed without the owner knowing.** The operator's accountant had
already filed an entity return that the operator believed was still pending. The
filing was correct. The operator's model of the world was not. There was no
shared record of who is authorized to file what, or of what has been filed.

**7. Commitment and export gates discovered at the exit.** A subscription turned
out to carry an annual commitment, discovered only when cancellation was
attempted. A separate provider turned out to gate data export behind an active
account, so the operator's history would not survive the cancellation. That one
was caught only because somebody thought to ask before cancelling. Nothing
systematic produced the question.

**8. Provider-side compliance debt.** Payroll registrations, insurance
certificates, and registered-agent renewals were tracked nowhere except the
memory of whoever set them up.

Eight findings in one week, across five entities. Every one of them is a missing
row in a file that does not exist. None of them would have been caught by better
bookkeeping, because none of them was a bookkeeping error.

The pattern that matters for product design: these were all found during one
deliberate sweep, not during normal operation. Normal operation had been running
for years with all eight present.

## What `mb estate` is

Three claims define the surface.

**It is declared, not discovered.** The registry is a repo fact the operator
writes, the same way `core/operations/repo-topology.md` is a repo fact. Main
Branch does not scrape agency portals, does not hold portal credentials, and
does not infer obligations from a ledger. Anything the engine cannot see, the
operator declares, and the checks then hold the operator to the declaration.

**Its unit of value is the last-verified date.** An obligation with a plausible
amount and no verification date is a guess. The registry's most useful field is
not `amount`, it is `last_verified`. Failure classes 3, 4, and 8 above are all
"nobody has looked at this in a long time," and only a stored date makes that
visible.

**It is a nag, not an authority.** The registry records observations. It does
not compute tax, does not decide whether an obligation applies, and does not
substitute for the professional who does. Its `authority` field cites the rule
the operator believes creates the obligation, so that a human can check the
citation. A missing citation is itself a finding.

## Schema

The registry extends the storage model the
[business repo topology map](2026-05-08-business-repo-topology-map.md) already
contemplates. Default location:

```text
core/operations/estate.yaml
```

Suggested placement note: the topology registry uses a Markdown file with YAML
frontmatter (`core/operations/repo-topology.md`). The estate registry is
substantially more structured and has no useful prose body, so a plain
`.yaml` file is suggested. If the maintainer prefers one convention across
`core/operations/`, `core/operations/estate.md` with the same frontmatter is an
acceptable alternative. This is listed in Open Questions.

Schema identifier: `mb.estate.v0`, following the `mb.repo_topology.v0` and
`mb.child_repo.v0` style. v0 means the shape is documented and not yet validated
by the CLI.

### Shape

```yaml
type: estate
status: active
schema: mb.estate.v0
business_display_name: "Example Business"
last_reviewed: 2026-07-28
default_verification_staleness_days: 180

entities:
  - slug: entity-a
    display_name: "Entity A"
    legal_name: "Example Operating LLC"
    entity_type: llc
    jurisdiction: "US-XX"
    formation_date: 2021-03-11
    tax_classification: s_corp
    lifecycle: active
    topology_repo: example
    identifiers:
      - kind: federal_tax_id
        last_four: "4417"
      - kind: state_entity_number
        last_four: "9002"
    registered_agent:
      provider: "Example Agent Co"
      status: active
      renews: 2027-02-01
      last_verified: 2026-07-14

    ownership:
      - holder: owner-1
        percent: 100
        basis: "operating agreement, 2021-03-11"

    accounts:
      - slug: operating-checking
        institution: "Example Bank"
        kind: checking
        last_four: "0182"
        purpose: "Operating account for Entity A"
        registered_to: entity-a
        funds: [entity-a]
        status: open
        statements_through: 2026-06-30
        evidence: "vault:accounts/entity-a/operating-checking/"
      - slug: shared-card
        institution: "Example Bank"
        kind: credit_card
        last_four: "7731"
        purpose: "Card used for Entity B operations"
        registered_to: entity-a
        funds: [entity-b]
        status: open
        note: "Registration and use are on different entities. See open item."
        evidence: "vault:accounts/entity-a/shared-card/"

    agencies:
      - slug: state-entity-tax
        agency: "State entity tax authority"
        portal: "state tax portal"
        account_ref_last_four: "9002"
        access: operator_login
        status: registered
        last_verified: 2026-07-14
        verified_scope: "balance due, open filing periods"
        credits_held:
          known: false
          note: "Portal displays amounts due only. Held credits require a call."
      - slug: state-sales-tax
        agency: "State sales and use tax authority"
        portal: "state sales tax portal"
        account_ref_last_four: "5540"
        access: operator_login
        status: registered
        last_verified: 2026-07-22
        verified_scope: "balance due, held credits, issued warrants"
        credits_held:
          known: true
          as_of: 2026-07-22
          note: "Credits confirmed by phone; not visible in the portal."

    obligations:
      - slug: annual-entity-tax
        name: "Annual flat entity tax"
        agency: state-entity-tax
        amount: 800.00
        currency: USD
        cadence: annual
        next_due: 2027-04-15
        authority: "State tax code, annual tax on registered entities"
        last_satisfied: 2026-04-12
        evidence: "vault:obligations/entity-a/annual-entity-tax/2026/"
      - slug: gross-receipts-fee
        name: "Tiered gross receipts fee"
        agency: state-entity-tax
        amount: variable
        amount_basis: "tiered on prior-year gross receipts"
        threshold_watch:
          driver: "prior-year gross receipts"
          last_checked: 2026-07-14
        cadence: annual
        next_due: 2027-04-15
        authority: "State tax code, tiered fee schedule"
      - slug: sales-tax-return
        name: "Sales and use tax return"
        agency: state-sales-tax
        amount: variable
        cadence: quarterly
        next_due: 2026-10-31
        authority: "State filing requirement, registered sellers"
        nonfiling_consequence: "Agency issues an estimated assessment"
        last_satisfied: 2026-07-30

    records:
      - kind: formation
        location: "vault:entities/entity-a/formation/"
      - kind: tax_return
        period: "2025"
        location: "vault:entities/entity-a/returns/2025/"
        filed_by: accountant-1
        filed_on: 2026-03-02
        acknowledged_by_owner: true

    people:
      - ref: owner-1
        role: owner
      - ref: accountant-1
        role: accountant
        scope: "prepares and files entity returns"
        files_without_notice: true

    providers:
      - slug: payroll
        kind: payroll
        status: active
        commitment: monthly
        export_gate: none
        last_verified: 2026-06-02
      - slug: scheduling-tool
        kind: saas
        status: active
        commitment: annual
        commitment_ends: 2027-01-19
        export_gate: "history exportable only while the subscription is active"
        export_captured: null

    open_items:
      - slug: unlocated-refund-warrant
        opened: 2026-07-21
        summary: "Agency records show a warrant issued in 2025; never received."
        next_step: "Request reissue through the agency's warrant desk."
        owner: owner-1
      - slug: account-registration-mismatch
        opened: 2026-07-23
        summary: "shared-card is registered to entity-a and funds entity-b."
        next_step: "Decide whether to re-register or document the arrangement."
        owner: owner-1
```

### Field notes

- `identifiers` carries **last four only**, and only when the operator wants a
  disambiguation aid. Full federal or state identifiers never enter the file.
  A registry with no `identifiers` block is valid.
- `registered_to` and `funds` are separate fields on purpose. Failure class 5
  exists entirely in the gap between them.
- `amount: variable` is a first-class value. An obligation is worth tracking
  before its amount is known; forcing a number invites a fabricated one.
- `authority` is a plain-language citation of the rule the operator believes
  creates the obligation. It exists so a human can check the claim, and so the
  check list can flag obligations that nobody can source.
- `evidence` values are pointers into a document store, using the same private
  vault convention `mb books` established (`.mb/private/` by default). The
  registry says where evidence lives. It never contains the evidence.
- `last_verified` on an agency means "a human looked at this account on this
  date." It is not the same as `last_satisfied` on an obligation, which means
  "this was paid or filed."
- `credits_held.known: false` is a meaningful declaration. It records that the
  operator has looked and that the portal does not show it, which is exactly the
  state failure class 4 lives in.

## Commands

Three surfaces. Output shape is described here; implementation belongs to the
follow-up slice.

### `mb estate`

Renders the registry. Read-only, offline, no provider calls.

```text
Example Business                              estate.yaml, reviewed 2026-07-28

Entity A       LLC · US-XX · S-corp election · formed 2021-03-11
  Accounts     2 open, 1 registration mismatch
  Agencies     2 registered, both verified within 180 days
  Obligations  3 tracked, 0 overdue, 0 undated
  Records      formation, 1 return (2025)
  Providers    2 active, 1 with an uncaptured export gate
  Open items   2

Entity B       LLC · US-XX · disregarded · formed 2023-08-02
  Accounts     1 open, 0 statements archived
  Agencies     1 registered, never verified
  Obligations  2 tracked, 1 overdue, 1 undated
  Records      formation
  Providers    none declared
  Open items   0

3 findings. Run `mb estate check` for detail.
```

`--entity <slug>` renders one entity in full. `--json` emits the standard result
envelope per [docs/json-output-contract.md](../docs/json-output-contract.md).

### `mb estate check`

Runs the lints. Findings carry `audience` and `operator_summary` per the
[checks and review model](../docs/checks-and-review-model.md). Estate findings
are almost all `operator_decision`, because the fix is a phone call or a filing,
not a file edit. The exception is shape and schema problems, which are
`mechanical`.

```text
mb estate check

Entity B
  overdue        Annual flat entity tax, due 2026-04-15, no evidence of payment
  never-verified State entity tax authority, no last_verified date recorded
  no-statements  operating-checking declared, statements_through not set

Entity A
  export-gate    scheduling-tool gates export behind an active subscription
                 and no export has been captured

3 findings: 1 overdue, 2 unverified.
Nothing here is a legal conclusion. Verify with the agency or your accountant.
```

Exit semantics follow the `mb books check` pattern: `0` clean, `1` findings,
`2` usage or config error.

### `mb estate calendar`

Everything due in the next N days, across all entities, in date order.

```text
mb estate calendar --days 90

2026-08-15   Entity B   Annual flat entity tax          $800.00   overdue 122d
2026-10-31   Entity A   Sales and use tax return        variable
2027-01-19   Entity A   scheduling-tool commitment ends variable  export gate
```

Default window is 90 days. `--json` for scripts and skills. The calendar is a
view over the registry; it does not schedule, remind, or send anything.

`mb status` should eventually carry a one-line estate fact (overdue count,
never-verified count) in the same way it carries books and topology facts. That
line is a pointer, not a report.

## The checks

The v0 check list. Each one exists because a failure class above went unseen
without it.

1. **Undated obligation.** An obligation with no `next_due`. Something is known
   to be owed and nothing knows when.
2. **Overdue without evidence.** `next_due` is in the past and `last_satisfied`
   is absent, older than `next_due`, or has no `evidence` pointer. This is
   failure classes 1 and 3.
3. **Unverified agency.** An agency with no `last_verified`, or with a
   `last_verified` older than the staleness threshold
   (`default_verification_staleness_days`, suggested default 180). Failure
   classes 3, 4, and 8.
4. **Account with no archived statements.** A declared account with no
   `statements_through` date, or a `statements_through` more than one period
   behind today. An account nobody has statements for is an account nobody is
   watching, which is where levies land.
5. **Books close open past deadline.** An entity linked to a books repo or vault
   whose most recent close is open past the operator's declared close deadline.
   This is the one check that reads across to `mb books`, and it reads a status
   fact only, never ledger contents.
6. **Obligation with no authority citation.** `authority` is missing or empty.
   An obligation nobody can source is either wrong or unverifiable, and both are
   worth surfacing.
7. **Export gate with no captured export.** A provider with a non-empty
   `export_gate` and `export_captured: null`. Failure class 7. The finding fires
   while the subscription is active, which is the only time the fix is possible.

### Checks the evidence argues for, deferred to v1

Listed so the follow-up slice has a queue, not shipped in v0:

- **Registration mismatch.** An account whose `registered_to` is not in its
  `funds` list. Failure class 5. Deferred because the correct resolution is
  often "document the arrangement," not "fix the registration," and the check
  needs an acknowledged-exception mechanism before it stops being noise.
- **Stale threshold watch.** An obligation with a `threshold_watch` block whose
  `last_checked` predates the current period. Failure class 2.
- **Unacknowledged third-party filing.** A record with `filed_by` pointing at a
  person other than the owner and `acknowledged_by_owner: false`. Failure class
  6.
- **Known-unknown credits.** An agency with `credits_held.known: false` and no
  open item tracking the question. Failure class 4.

## Boundaries

This section is load-bearing. The registry is a complete map of an operator's
exposure, which makes it more sensitive than its individual fields suggest.

It inherits the Class B rules from
[the workspace, repo, and sensitive-data boundaries decision](2026-05-04-workspace-repo-sensitive-data-boundaries.md)
and sharpens them the way `mb books` did.

**Never in the registry, under any storage mode:**

- portal credentials, passwords, MFA seeds, security answers, API tokens;
- full federal or state tax identifiers, full account or routing numbers, full
  card numbers;
- signature images, identity documents, or scans of anything;
- the evidence itself: statements, returns, notices, correspondence, contracts;
- dollar figures for anything other than a declared obligation amount. The
  registry is not a balance sheet.

**In the registry, deliberately:**

- last-four fragments, and only as a disambiguation aid;
- agency names, portal labels, and registration status;
- obligation names, cadences, due dates, and authority citations;
- verification dates and the scope of what was verified;
- pointers to where evidence lives, expressed as vault-relative locations;
- roles and authority scopes for the people involved.

**Where the file lives.** The registry is safe for a private hub repo with one
operator. It is not automatically safe for a team-visible business repo. The
same rule
[the `mb books` foundation](2026-05-11-mb-books-foundation.md)
applied holds here: GitHub permissions are
repo-level, so a sensitive file inside a widely-shared repo is not private. For
a team, the registry belongs in the restricted `finance` or `legal` child repo
described in the
[topology map](2026-05-08-business-repo-topology-map.md), with only a status
summary reported up to the hub. `mb estate check` should warn when the registry
is tracked in a repo with collaborators, in the same shape as the
GitHub-as-backup warning `mb books status` already prints.

**It declares where evidence lives without containing it.** Every `evidence` and
`location` value is a pointer. The engine should refuse to read through those
pointers during a check, exactly as `mb books check` refuses to read the vault's
contents. A check can assert that a pointer is declared. It should not assert
that the document behind it says anything in particular.

**It never asserts a legal conclusion.** The registry records what was observed
and when. `authority` records what the operator believes the rule is; it is a
citation to check, not a determination. No output of `mb estate` should be
phrased as advice, and every findings surface should carry the reminder that
verification belongs with the agency or the operator's accountant.

**Editable files are not authority.** Per the sensitive-data boundaries
decision, a registry entry saying an obligation is satisfied is a claim, not a
receipt. Authority lives with the agency, the bank, and the filed document. The
registry's job is to make the claim inspectable and dated so a human can check
it.

## Population is the hard part

The honest section.

Writing the schema is a day. Writing a renderer and seven checks is a week.
Filling the file for one real multi-entity operator is the entire project.

Population requires, per entity: pulling formation documents out of wherever
they landed; reconstructing which accounts exist and which entity each is
registered to; logging into every agency portal and recording what it says and
what it structurally cannot say; finding out which returns have been filed and
by whom; reading subscription terms for commitments and export gates; and
tracking down the obligations nobody remembers creating. Most of that
information exists. It exists in a books repo, an email archive, a filing
cabinet, a portal, and one person's memory, and no two of those agree.

Two consequences for the product.

**Agent-assisted population is the onboarding path, not a nice-to-have.** The
realistic first-run shape is `mb estate init` scaffolding an empty registry,
followed by an agent-run population pass: read the business repo and any linked
books repo for entity and account evidence, interview the operator for what only
they know, and draft entries with explicit `unknown` and `unverified` markers
rather than plausible guesses. The agent should be biased toward recording
uncertainty. A registry full of confident wrong dates is worse than an empty
one, because the checks then confirm a fiction.

**The first population is where the value is proven.** In the operating week
this decision comes from, all eight failure classes surfaced during the sweep
that would have been the first population pass. None surfaced during years of
normal operation. That is the product claim to test: not that the registry keeps
things from drifting, which takes a year to demonstrate, but that filling it in
the first time finds things. If a first population on a real multi-entity
operator finds nothing, the feature is not worth building, and that is a cheap
experiment to run before writing the CLI.

## What this is not

- **Not tax advice.** The registry records obligations the operator declares. It
  does not determine whether an obligation applies, what it costs, or how to
  minimize it.
- **Not a filing tool.** It never submits anything to an agency. It has no
  agency integrations, holds no portal credentials, and takes no action on the
  operator's behalf.
- **Not a payment rail.** It never moves money. `mb` has no provider mutation
  authority here; see the
  [provider mutation contract](../docs/provider-mutation-contract.md).
- **Not a replacement for a CPA, an attorney, or a registered agent.** Failure
  class 6 in particular is a communication problem between an operator and their
  accountant. The registry gives them a shared artifact to disagree over. It
  does not replace either party.
- **Not a document store.** Evidence lives in the private vault or the operator's
  existing archive. The registry points.
- **Not a nexus or compliance engine.** It does not determine where an entity
  has registration obligations. It records the ones the operator knows about and
  makes the gaps visible as gaps.

What it is: a map and a nag.

## Validation Contract

For this decision slice:

- Level 0 (docs/decision) review is required: frontmatter, links, no stale
  product claims, no private data;
- `scripts/check.sh` (Level 1) must pass before pushing;
- no CLI tests, because no CLI behavior changes;
- no package/install smoke, because packaging is unchanged;
- no fixture-repo smoke, because scaffolding is unchanged;
- no runtime smoke, because no skill or runtime wiring changes.

A follow-up implementation issue must add focused CLI tests, a fixture-repo
smoke over a fake `estate.yaml`, and a package smoke if the fixture is packaged
into `mb/mb/_data/`. The fixture must use an obviously fake business, fake
jurisdictions, and no real agency names.

## Open Questions

For the maintainer to settle before an implementation slice opens.

1. **Is `estate` the right word?** It collides with the personal-estate and
   inheritance sense, which is a different product. `mb entities`,
   `mb obligations`, and `mb compliance` are the alternatives. `obligations` is
   the most accurate and the least memorable; `compliance` overpromises.
2. **`estate.yaml` or `estate.md` with frontmatter?** The topology registry uses
   Markdown plus frontmatter. The estate registry has no useful prose body. One
   convention across `core/operations/` may be worth more than the better fit.
3. **Hub or restricted repo by default?** Solo operators are fine committing to
   a private hub. Teams are not. Should `mb estate init` ask, the way
   `mb books` asks about storage mode, or should it default to the restricted
   repo and let solo operators opt down?
4. **Does check 5 cross the books boundary?** Reading "is the close open" from a
   books repo means reading a status fact from a private vault. That is a
   narrower read than `mb books exposure` already performs, but it is a read
   across a boundary and should be named explicitly rather than assumed.
5. **What is the right staleness threshold, and is one threshold enough?** An
   annual filing agency and a quarterly one do not deserve the same verification
   cadence. Per-agency `staleness_days` overrides are easy to add and easy to
   leave unset.
6. **Should obligations carry amounts at all?** Amounts drift, and a stale
   amount in a registry reads as authoritative. Cadence, due date, and authority
   may be the whole useful payload, with the amount left to the agency.
7. **Does the calendar need a push surface?** A registry checked only when
   someone remembers to check it has the same failure mode as the memory it
   replaces. A scheduled check is out of scope here and depends on the
   [scheduled data sync pattern](2026-05-11-scheduled-data-sync-pattern.md).
8. **Multi-jurisdiction entities.** An entity registered in more than one state
   multiplies agencies and obligations. The schema handles it by repetition. The
   question is whether that stays legible at four jurisdictions, or whether it
   pulls the feature toward being a nexus engine, which is explicitly a
   non-goal.

## Consequences

- Main Branch gains a safety surface for obligations that are invisible to
  bookkeeping by construction, without adding a second finance database.
- `mb books` keeps its scope. Bookkeeping stays about transactions; the estate
  registry takes the calendar-driven half and does not push back into the
  ledger.
- The registry inherits the existing sensitive-data boundary rather than
  inventing a new one, so a future dashboard view of estate status is already
  governed.
- Failure classes with the worst asymmetry between cost-to-track and
  cost-to-miss (an $800 obligation becoming a levy, a $1,828 liability becoming
  a $3,104.86 assessment) get a named home.
- The engine takes on an obligation of its own: everything `mb estate` prints
  must stay phrased as observation, because the subject matter invites operators
  to read output as advice.
- Population cost is real and front-loaded. If the agent-assisted onboarding
  path does not work, the feature does not ship, and that is a cheaper failure
  than a half-populated registry passing its own checks.

## Review Trigger

Revisit this decision if any of these become true:

- an implementation slice wants `mb estate` to hold a credential, call an agency
  API, or read through an `evidence` pointer;
- a check needs to compute a liability rather than compare declared dates;
- the registry starts carrying dollar figures beyond declared obligation
  amounts;
- a hosted or dashboard surface proposes showing estate status to anyone who
  does not already have access to the private source;
- a first real population pass finds nothing, which retires the proposal;
- `mb books` and `mb estate` need to share a storage mode rather than each
  declaring one.
