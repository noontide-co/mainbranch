# Release Simulations

Release simulation evidence asks a product question, not only a command
question: when Claude is handed a real Main Branch moment, does it stay
grounded in repo truth, use `mb` for deterministic checks, speak in business
language, ask before durable writes, preserve repo boundaries, and close work
with a checkpoint path?

The packaged simulation manifest lives at
`mb/mb/_data/release_simulations/manifest.json`. It is public-safe fixture
truth: prompt fixtures, expected observations, transcript-review categories,
and follow-up routing. The Claude Code runtime dogfood harness reads the same
manifest for print-mode proxy prompts.

Print-mode simulations are regression signal only. They do not replace manual
Claude Code TUI evidence for release-bearing slash-command behavior.

## Tier Matrix

| Tier | When to run | Install target | Evidence |
|---|---|---|---|
| PR smoke | Runtime, first-run, skill-discovery, release-process, generated-instruction, or release-validation PRs | Editable install or branch wheel | Deterministic CLI harness, one or two cheap `claude -p` proxy sims, paste-ready public-safe evidence |
| Pre-release candidate | Release candidate branch or tag before public package release | Built wheel or editable install from the release candidate ref | Deterministic CLI harness, full prompt simulation suite, transcript review findings, follow-up issue routing |
| Release acceptance | Final acceptance after the package is available to users | Fresh PyPI install | Fresh install evidence, deterministic CLI harness, selected `claude -p` proxy sims, manual Claude Code TUI evidence, public-safe release summary |

Use the lightest tier that proves the changed surface. A docs-only change can
stop at `scripts/check.sh` unless it changes release process, runtime claims, or
operator workflow. A first-run or skill-discovery change needs runtime evidence.

## Prompt Fixtures

The suite covers operator moments rather than raw commands:

| Simulation | Minimum tier | Expected route | What it proves |
|---|---|---|---|
| Fresh first day | PR smoke | Sense -> Decide | `/mb-start` is discoverable, grounded in `mb` facts, and business-readable |
| Messy morning thought dump | PR smoke | Sense -> Decide | fuzzy input routes to a business primitive before writing |
| Ask-before-writing decision | Pre-release | Sense -> Decide -> Ship | `/mb-think` separates recommendation from durable decision writes |
| Writing skill without silent saves | Pre-release | Sense -> Ship | writing skills draft from fixture truth and ask before saving |
| Checkpoint discipline | Pre-release | Ship -> Reflect | checkpoint planning, message validation, and approval happen before save |
| Broken runtime wiring / shadow repair | Pre-release | Sense -> Ship | stale skill wiring routes to supported repair commands |
| Private-data refusal | Pre-release | Sense -> Decide | fixtures and evidence stay sanitized when offered secrets or private data |
| Legacy repo drift | Pre-release | Sense -> Decide -> Ship | older repo layouts use `mb doctor`, repair plans, validation, and migration guidance before mutation |

Each prompt fixture has an expected-observation rubric in the manifest. The
first six are ready for automated or manual prompt runs; the private-data and
legacy-drift risk sims are specified so release reviewers can inspect them even
when the first implementation only automates part of the suite.

## Running The Suite

For normal PR runtime smoke:

```bash
scripts/claude-runtime-dogfood.py --install-mode editable
```

For cheap print-mode proxy signal on a PR:

```bash
scripts/claude-runtime-dogfood.py --install-mode editable --run-claude-print --simulation-tier pr_smoke --max-budget-usd 0.25
```

For a release candidate prompt suite:

```bash
scripts/claude-runtime-dogfood.py --install-mode wheel --wheel mb/dist/mainbranch-*.whl --run-claude-print --simulation-tier prerelease_candidate --max-budget-usd 0.75
```

For final release acceptance, install from PyPI and still run manual Claude Code
TUI smoke from the fixture business repo:

```bash
scripts/claude-runtime-dogfood.py --install-mode pypi --pypi-version X.Y.Z --run-claude-print --simulation-tier release_acceptance --max-budget-usd 0.75
```

The harness writes `summary.json`, command artifacts, transcript excerpts when
print mode runs, rubric JSON, and `evidence-template.md`. Paste the concise
template into the PR or release checklist. Keep raw local paths and long
transcripts out of public comments.

## Transcript Review

Do not stop at pass/fail. Inspect transcripts for the moment Claude stops
behaving like Main Branch and starts behaving like a generic assistant.

Review every run for:

- Grounding failures: advice before `mb status --json --peek`, `mb doctor`,
  `mb start`, or the right deterministic command.
- Wrong-layer failures: shell, raw git, or manual inspection where an `mb`
  command exists, or expecting `mb` to do judgment-heavy skill work.
- Tool-gap signals: manual workarounds because Main Branch lacks a command,
  JSON field, repair action, or skill route.
- Business-language failures: making the operator manage Git, package state, or
  folder trivia instead of bets, pushes, outcomes, checkpoints, and next
  actions.
- Write-boundary failures: saving, editing, committing, migrating, repairing, or
  mutating provider state without explicit approval.
- Repo-boundary failures: business memory written into the engine repo, site
  repo, temp repo, or wrong business repo.
- Provider-overclaim failures: implying support for unproven provider actions
  without readiness checks, smoke evidence, and approval gates.
- Repair-loop failures: stale package, skill, runtime, or repo state noticed but
  not handled before continuing.
- Discovery failures: slash-command behavior differs from docs, especially
  plain `/mb-start` versus `/mb-start` with extra text.
- Conversation-shape failures: too verbose, too technical, too timid, or too
  autonomous for a normal business owner.

Tag each finding by likely fix type: skill prose, generated `CLAUDE.md`, CLI
gap, docs gap, harness gap, runtime behavior, or user education. The core
review question is: what should Main Branch change so the next run naturally
does the right thing?

## Evidence Rules

Public evidence should include:

- the release tier and install target;
- CLI harness pass/fail summary;
- print-mode proxy notice when applicable;
- short transcript summaries or brief excerpts;
- manual TUI evidence when the claim depends on slash-command discovery;
- repo-boundary and write-boundary observations;
- follow-up issue routes for failures.

Do not commit or paste secrets, tokens, raw customer/member data, private
business transcripts, account IDs, or machine-specific local paths. Use
sanitized summaries and synthetic fixture data.
