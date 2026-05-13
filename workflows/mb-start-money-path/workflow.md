---
name: mb-start-money-path
title: Start To MoneyPath Think Handoff
description: Ground daily start path-to-money prompts in deterministic MoneyPath facts before handing off to thinking or codification work.
loops: [sense, decide, ship]
runtime_support:
  claude_code: supported_shell
  codex_cli: experimental_shell
  future: planned
required_mb_commands:
  - mb status --json --peek
  - mb start --json
  - mb doctor repair --plan
json_facts:
  - money_path
  - money_path.objects.offer
  - money_path.objects.proof
  - money_path.objects.proof.quality
  - money_path.objects.product_ladder
  - money_path.objects.cta_path
  - money_path.objects.channel_strategy
  - money_path.objects.active_push
  - money_path.objects.outcome_feedback_loop
  - money_path.ranked_actions
  - content_strategy
  - ranked_actions
  - update
  - readiness
  - drift.items
writes_business_files: true
provider_mutation: false
publishing_or_spend: false
---

# Start To MoneyPath Think Handoff

This workflow source is the portable contract for daily start prompts where the
operator asks about revenue, offer readiness, the next dollar, or the path to
money. It exists to keep Claude Code and Codex shells aligned without changing
shipped runtime behavior in this prototype.

## Intent And Triggers

Use this workflow when the operator starts or returns to a business repo and
asks what matters for revenue, what sells, what blocks the next paid step, or
whether the offer, proof, CTA, channel, push, page, or feedback loop is ready.

Trigger phrases include path to money, revenue, make money, next dollar, what
sells, paid step, CTA, offer readiness, product ladder, proof, launch readiness,
and sales path.

Do not use this workflow for a full research run, a full `/mb-think` port, a
site build, provider setup, publishing, spend, customer contact, or direct model
execution from `mb`.

## Required Mb Commands

Run or preserve these deterministic facts before interpreting business files:

- `mb status --json --peek`
- `mb start --json`
- `mb doctor repair --plan`

`mb status --json --peek` is the normal first read. `mb start --json` is the
daily-start contract for runtime bootstraps that need a compact owner briefing.
`mb doctor repair --plan` supplies repair blockers when status reports drift or
broken wiring.

## Required JSON Fact Paths

The runtime shell must preserve these paths from the workflow source:

- `money_path`
- `money_path.objects.offer`
- `money_path.objects.proof`
- `money_path.objects.proof.quality`
- `money_path.objects.product_ladder`
- `money_path.objects.cta_path`
- `money_path.objects.channel_strategy`
- `money_path.objects.active_push`
- `money_path.objects.outcome_feedback_loop`
- `money_path.ranked_actions`
- `content_strategy`
- `ranked_actions`
- `update`
- `readiness`
- `drift.items`

Treat these as facts, not strategy. The CLI reports legibility, connection, and
instrumentation. The runtime may recommend a route, but it must not claim that
an offer will or will not convert.

## Routing Rules

Hard gates win before MoneyPath interpretation: required updates, broken repo
wiring, repair blockers, validation blockers, relationship-health blockers,
unsafe provider operations, private-data boundaries, and destructive-operation
requests.

When hard gates are clear, start from `money_path.overall_level`,
`money_path.overall_label`, the required object paths above, and
`money_path.ranked_actions`. Compare the top-level `ranked_actions` with the
MoneyPath bottleneck. If they disagree, name which gate or route takes priority.

Read supporting offer, proof, product ladder, decision, research, finance
summary, push, or channel files only after the deterministic facts identify why
that file can help.

Route to the thinking/codification workflow only when the next useful move is
to clarify, decide, research, or write durable business truth. Do not hand off
to a production workflow when the missing fact is a decision, CTA, proof
quality, paid entry step, or outcome feedback loop.

## Read Boundaries

Read deterministic `mb` facts before raw markdown. After the fact pass, read
only the business files needed for the stated bottleneck or handoff:

- `core/offer.md` or `core/offers/<slug>/offer.md`
- `core/proof/` or offer-specific proof files
- `core/product-ladder.md` or current product-ladder equivalent
- `core/content-strategy.md` and indexed content strategy layers
- relevant `decisions/`, `research/`, `pushes/`, and safe finance summaries

Do not inspect secrets, raw provider exports, raw finance/legal records,
customer/member records, local runtime settings, or private maintainer notes.

## Write Boundaries

The workflow may hand off to a route that writes business files only after the
operator agrees to codify, decide, research, or save a checkpoint. Valid write
targets live in the business repo, such as `research/`, `decisions/`, `core/`,
`bets/`, `pushes/`, `log/`, and `documents/`.

The workflow source itself does not authorize writes to shipped runtime files,
generated repo guidance, provider accounts, public sites, ad accounts, customer
systems, or release surfaces.

## Approval Gates

Ask before:

- applying updates, repairs, or migrations;
- creating, editing, moving, deleting, or archiving business files;
- saving a checkpoint;
- publishing a site, opening a public issue, submitting a proposal, spending
  money, mutating provider state, or contacting customers;
- reading or moving private, restricted, local-only, finance, legal, customer,
  member, credential, or raw provider data.

Never ask the operator to paste secrets into repo files or workflow sources.

## Handoff Format

When handing off to thinking or codification, include a compact snapshot:

```text
MoneyPath snapshot: overall <level> / <label>.
Bottleneck: <object or gate>.
Proof: <generic/specific/offer-linked/typicality/outcome-feedback facts>.
Offer and ladder: <structured facts and missing fields>.
CTA/channel/push: <connection facts>.
Outcome feedback: <instrumentation facts>.
Ranked actions: <agreement or disagreement with MoneyPath bottleneck>.
Recommended route: use the thinking/codification workflow to <decision or write target>.
Approval needed before writes: yes.
```

Use business language. Avoid subjective conversion judgment such as "your offer
is bad," "this will convert," or "this will not convert."

## Validation Commands

Minimum validation for this prototype:

- focused workflow schema tests;
- generated Claude and Codex shell snapshot tests;
- drift tests that fail when a supported shell omits a required `mb` command or
  JSON fact path;
- public/private boundary review;
- `scripts/check.sh`.

Runtime smoke is required before generated shell output replaces shipped
Claude Code skill prose or before docs claim selected Codex workflow support.

## Runtime-Specific Notes

### Claude Code

Claude Code remains the supported runtime. Rendered Claude shell snapshots must
preserve slash-command-native language, `/mb-start` to `/mb-think` handoff
shape, MoneyPath-first routing, hard gates before MoneyPath interpretation, and
no subjective conversion judgment.

This prototype does not replace `.claude/skills/mb-start/SKILL.md` or
`.claude/skills/mb-think/SKILL.md`. Replacing shipped Claude prose requires
skill validation and runtime evidence.

### Codex CLI

Codex remains experimental and CLI-first. Rendered Codex shell snapshots must
start from generated `AGENTS.md` style grounding and deterministic `mb` facts.

Do not say `/mb-start` works inside Codex. Do not claim selected Codex workflow
support until a fresh fixture repo and read-only `codex exec --json --ephemeral
--sandbox read-only -C <repo>` smoke prove the generated shell is actually
used.
