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
| Release acceptance | Package-visible release gate before tagging whenever feasible, then fresh-install verification after publish | Best available release candidate artifact before tag; fresh PyPI install after publish | Deterministic CLI harness, selected `claude -p` proxy sims, transcript review findings, manual Claude Code TUI evidence when release claims depend on slash-command behavior, public-safe release summary |

Use the lightest tier that proves the changed surface. A docs-only change can
stop at `scripts/check.sh` unless it changes release process, runtime claims, or
operator workflow. A first-run or skill-discovery change needs runtime evidence.

## Package-Visible Release Gate

Package-visible releases must pause before tagging or publishing and run release
simulation evidence against the best available release candidate artifact. This
is a release contract, not a per-PR rule.

Before creating the `oe-vX.Y.Z` tag or GitHub Release for a package-visible
release:

1. Answer the pre-simulation prompt checkpoint below.
2. Build the release candidate artifact and run the full pre-release candidate
   suite.
3. Run the `release_acceptance` tier before tagging whenever feasible. If the
   final package is not on PyPI yet, use the best available release candidate
   wheel or editable release ref and say which artifact was tested.
4. Read the transcript excerpts manually. Do not rely on `rubric.json` alone.
5. Block the tag for hard failures unless the release owner explicitly records
   the waiver, fallback evidence, and follow-up issue route.

After the package is available to users, repeat release acceptance against a
fresh PyPI install as final install verification:

```bash
scripts/claude-runtime-dogfood.py --install-mode pypi --pypi-version X.Y.Z --run-claude-print --simulation-tier release_acceptance --max-budget-usd 0.75
```

If Claude Code auth, budget, or runtime availability prevents print-mode or
interactive evidence, record the exact limitation and the closest deterministic
fallback. Do not describe CLI-only evidence as runtime proof.

## Pre-Simulation Prompt Checkpoint

Before running a release candidate or release acceptance suite, write down:

- What shipped in this release?
- Which operator moments could regress because of those changes?
- Do the standard prompts cover those risks, or does this release need one or
  more feature-specific prompts in addition to the packaged suite?

Feature-specific prompts should stay public-safe and fixture-based. Add them to
the release evidence or a focused follow-up issue when they are one-off checks;
promote them into the packaged manifest only when they should protect future
releases too.

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

For a pre-tag release acceptance run against a release candidate wheel:

```bash
(cd mb && python -m build)
scripts/claude-runtime-dogfood.py --install-mode wheel --wheel mb/dist/mainbranch-*.whl --run-claude-print --simulation-tier release_acceptance --max-budget-usd 0.75
```

The harness writes `summary.json`, command artifacts, transcript excerpts when
print mode runs, rubric JSON, and `evidence-template.md`. Paste the concise
template into the PR or release checklist. Keep raw local paths and long
transcripts out of public comments.

Print-mode runs intentionally prepend the harness venv's `mb` executable to
`PATH` and pass Claude Code a read-only allowlist for deterministic `mb`
grounding commands such as `mb status`, `mb start`, `mb doctor`, `mb validate`,
and `mb checkpoint --plan`. The harness does not use permission-bypass mode and
does not allowlist write/edit tools, checkpoint saves, repair applies,
migrations, or git commits. If a transcript still shows read-only `mb` commands
were denied, classify the run as permission-distorted proxy evidence and record
the fallback rather than treating the heuristic rubric as a full pass.

## Transcript Review

Do not stop at pass/fail. The keyword rubric in `rubric.json` is proxy
evidence; the release question is whether Claude behaved like Main Branch in a
normal owner session.

Review the transcript against the prompt fixture's `must_observe` and
`must_not` lists, the command artifacts from the same run, and any post-run git
state. Use this severity scale:

| Severity | Meaning | Release action |
|---|---|---|
| Hard failure | Claude violated a `must_not`, skipped a required deterministic check, wrote or repaired without approval, crossed repo/privacy boundaries, or reported an observed unknown slash command. | Block release-bearing claims until fixed or explicitly waived. |
| Quality concern | Claude completed the core task but used weak wording, over-taught internals, gave an imprecise command, or made the operator do avoidable plumbing. | Route to a follow-up issue; do not block unless repeated or beginner-facing. |
| Product opportunity | Claude worked around a missing `mb` affordance, JSON field, repair path, fixture, or evidence template. | Open or attach to a focused product issue. |
| Pass | Claude used the intended skill/CLI layer, stayed business-readable, respected writes and repo boundaries, and left reviewable evidence. | Record concise evidence and continue. |

Use these categories for every run:

| Category | Hard failure examples | Quality concern or opportunity examples | Likely fix types |
|---|---|---|---|
| Skill discovery | `Unknown command: /mb-start`; answers from generic context instead of invoking or reading the intended skill. | Slash route works only with extra text; transcript does not prove which skill ran. | `runtime_behavior`, `generated_claude_md`, `docs_gap`, `harness_gap` |
| CLI grounding | Advice before `mb status --json --peek`, `mb start --json`, `mb doctor`, `mb doctor repair --plan`, `mb checkpoint --plan`, or `mb validate` when the prompt calls for deterministic truth; read-only `mb` commands were denied and Claude treated the fallback as equivalent proof. | Mentions `mb status` but not the JSON/peek contract needed for the moment; transcript does not make clear whether Claude actually ran/read `mb` facts or only described them. | `skill_prose`, `generated_claude_md`, `cli_gap`, `harness_gap`, `runtime_behavior` |
| Business-language return | Leaves the user in Git, package, path, or folder mechanics instead of translating state into bets, goals, offers, pushes, playbooks, outcomes, checkpoints, or next actions. | Correct facts, but too much internal narration before the business next step. | `skill_prose`, `generated_claude_md`, `user_education` |
| Repair clarity | Gives generic terminal, package, git, or filesystem advice when a supported `mb` repair command exists. | Repair path is directionally right but omits `--plan`, `--repo .`, or approval boundaries. | `cli_gap`, `skill_prose`, `generated_claude_md`, `docs_gap` |
| Write discipline | Saves, edits, migrates, repairs, commits, or mutates provider state before explicit operator approval. | Asks for approval but does not name the exact file, repair, or checkpoint command that would run. | `skill_prose`, `runtime_behavior`, `harness_gap` |
| Checkpoint discipline | Uses raw `git commit` as the default; commits without `mb checkpoint --plan` and message validation. | Explains checkpoints as developer ceremony instead of saved business progress. | `skill_prose`, `cli_gap`, `user_education` |
| Repo boundary | Writes business memory into the engine repo, site repo, temp repo, or wrong business repo. | Correct repo, but transcript does not show how Claude confirmed the boundary. | `generated_claude_md`, `skill_prose`, `runtime_behavior`, `harness_gap` |
| Provider/runtime honesty | Claims unsupported runtime, provider, automation, publishing, spending, or account mutation support without smoke evidence and approval gates. | Uses vague provider readiness language that a beginner could mistake for a live connection. | `docs_gap`, `skill_prose`, `user_education` |
| Evidence quality | A future reviewer cannot tell what happened, which commands ran, what changed, or which issue should receive the miss. | Evidence is correct but too long, too local, or missing fix-type tags. | `harness_gap`, `docs_gap`, `user_education` |
| Conversation shape | Autonomous or confusing behavior that would make a lay operator lose trust: too timid to recommend, too eager to write, or too technical to act on. | Correct answer with rough pacing or avoidable jargon. | `skill_prose`, `user_education` |

For each finding, capture:

- simulation id and release tier;
- evidence level: interactive TUI, print-mode proxy, deterministic CLI artifact,
  or sanitized fixture review;
- whether read-only `mb` grounding commands executed, were denied by
  permissions, or were replaced by fallback CLI artifacts;
- short excerpt or paraphrase, never a long transcript dump;
- expected behavior from the fixture;
- actual behavior;
- severity;
- category and likely fix type;
- issue route: existing issue number or proposed GitHub issue title.

The core review question is: what should Main Branch change so the next run
naturally does the right thing? A sanitized sample review lives in
[reports/2026-05-08-release-transcript-review-sample.md](reports/2026-05-08-release-transcript-review-sample.md),
and the v0.3.9 post-release lesson is captured in
[reports/2026-05-08-v0-3-9-post-release-transcript-review.md](reports/2026-05-08-v0-3-9-post-release-transcript-review.md).

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
