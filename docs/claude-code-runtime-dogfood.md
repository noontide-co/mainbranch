# Claude Code Runtime Dogfood

This runbook is the manual production smoke for the supported Claude Code
runtime. It proves the part CI cannot prove: Claude discovers Main Branch
skills from a fresh business repo, reads and writes the business repo instead
of the engine repo, treats `mb` as the control plane, and explains work in
operator language.

Use this when a change touches first-run handoff, Claude Code skill discovery,
slash-command invocation, LLM-facing skill behavior, checkpoint saves, or
release validation. Keep the fixture sanitized and disposable.

## What This Proves

- `mb onboard` creates a fresh business repo with project-local Claude Code
  skill bridge links.
- `mb doctor`, `mb doctor repair --plan`, `mb status --json --peek`, and
  `mb start --json` describe the repo without mutating business files.
- Plain `/mb-start` is discoverable from Claude Code and uses status facts
  before routing.
- `/mb-think` can reason from the fixture business files and writes durable
  output only into the business repo after operator approval.
- A writing skill such as `/mb-organic` can draft from repo truth without
  editing the engine repo.
- Checkpoint behavior goes through `mb checkpoint` planning, validation, and
  explicit operator approval before a commit is saved.

This does not automate Claude Code UI testing, test private business data, or
prove unsupported runtimes.

## Prerequisites

- Claude Code is installed and authenticated.
- Git is installed.
- The GitHub CLI is optional for this runbook; use it only if you want status
  to include authenticated GitHub facts.
- You have an `mb` executable under test. For a release smoke, use the installed
  package. For a PR smoke, use a wheel or editable install from the branch.

For a PR smoke from a local checkout:

```bash
ENGINE_REPO="$(git rev-parse --show-toplevel)"
python3 -m venv /tmp/mainbranch-dogfood-venv
/tmp/mainbranch-dogfood-venv/bin/pip install -e "$ENGINE_REPO/mb"
MB=/tmp/mainbranch-dogfood-venv/bin/mb
"$MB" --version
```

For an already installed release smoke:

```bash
MB="$(command -v mb)"
"$MB" --version
```

## Automated Harness

Use the automated harness when you need repeatable deterministic evidence for a
PR, release candidate, runtime-discovery change, or skill-discovery change:

```bash
scripts/claude-runtime-dogfood.py --install-mode editable
```

The harness creates a disposable sanitized business repo, installs the package
under test into a temp virtual environment, runs the read-only CLI checks below,
checks fixture and engine repo boundaries, and writes a public-safe evidence
folder. The final output prints the evidence path and a paste-ready
`evidence-template.md`.

By default the temp root is kept so you can inspect evidence artifacts. Remove
it after copying anything you need:

```bash
rm -rf /path/printed/by/the/harness
```

Use `--cleanup` for CI or local runs that only need the exit code. If you need
artifacts and cleanup in the same run, pass `--evidence-dir` outside the temp
root before adding `--cleanup`. Explicit `--root` directories are never removed,
and reusing a `--root` requires deleting the existing `dogfood-studio/` fixture
first.

For a wheel smoke:

```bash
(cd mb && python -m build)
scripts/claude-runtime-dogfood.py --install-mode wheel --wheel mb/dist/mainbranch-*.whl
```

For a release smoke against PyPI:

```bash
scripts/claude-runtime-dogfood.py --install-mode pypi --pypi-version 0.3.6
```

The optional print-mode proxy path runs chained `claude -p` prompts and
preserves the returned session id when Claude Code emits one:

```bash
scripts/claude-runtime-dogfood.py --install-mode editable --run-claude-print --max-budget-usd 0.25
```

The print-mode prompt set comes from the packaged
[release simulation manifest](release-simulations.md). Use
`--simulation-tier pr_smoke` for cheap PR signal,
`--simulation-tier prerelease_candidate` for the full prompt suite before a
release, and `--simulation-tier release_acceptance` for selected proxy checks
around a fresh PyPI install.

Print-mode evidence is a proxy. It is useful for repeatable regression signal,
budget/auth failures, transcript excerpts, and rubric scoring, but it is not
the same as interactive Claude Code TUI evidence. Release-bearing runtime
claims still need the manual interactive phase below unless the PR explicitly
documents why the runtime could not be launched.

For the tier matrix, prompt fixtures, expected-observation rubrics, transcript
review categories, fix-type routing, and public evidence rules, see
[Release Simulations](release-simulations.md).

## Phase 1: Fresh Fixture Setup

This phase creates a disposable, sanitized business repo. It is allowed to
write inside the fixture repo only.

```bash
export DOGFOOD_ROOT="$(mktemp -d)"
export DOGFOOD_REPO="$DOGFOOD_ROOT/dogfood-studio"

"$MB" onboard --yes --name "Dogfood Studio" --path "$DOGFOOD_REPO" --json
cd "$DOGFOOD_REPO"
git config user.name "Main Branch Dogfood"
git config user.email "dogfood@example.com"
```

Add enough public-safe business context for Claude to reason from:

```bash
cat > core/offer.md <<'EOF'
# Offer

Dogfood Studio helps solo founders keep offer, audience, voice, and launch
context in files they own so AI sessions stop starting from zero.

Primary offer: a two-week operating-memory setup sprint.
Promise: leave with a working business repo, daily decision flow, and one
shipped growth asset.
EOF

cat > core/audience.md <<'EOF'
# Audience

Solo founders and small service operators who already use AI for marketing and
operations but keep losing context across chats, SaaS tools, and docs.

They are capable but busy. They want exact next steps, not abstract systems
thinking.
EOF

cat > core/voice.md <<'EOF'
# Voice

Direct, specific, calm, and practical. Avoid hype. Explain tradeoffs in plain
English. Prefer business-owner language before tool internals.
EOF

mkdir -p research decisions pushes log documents
cat > research/2026-05-07-ai-context-reset.md <<'EOF'
---
type: research
topic: AI context reset pain
date: 2026-05-07
source: sanitized dogfood fixture
---

# AI Context Reset Pain

Common complaint: every new AI chat requires the founder to re-explain the
offer, audience, proof, and current priority. The opportunity is to turn the
business repo into the durable briefing layer.
EOF

git add .
git commit -m "[added] dogfood fixture context"
```

Record the engine repo status before runtime work if you are validating a local
checkout:

```bash
if [ -n "${ENGINE_REPO:-}" ]; then
  git -C "$ENGINE_REPO" status --short
fi
git status --short
```

Pass condition:

- The fixture repo exists.
- `.claude/skills/mb-start/SKILL.md` exists in the fixture repo.
- The first commit succeeds with the business-readable checkpoint hook active.
- The engine repo status is unchanged except for intentional PR edits.

## Phase 2: Read-Only CLI Checks

These commands should inspect the fixture, not write business content.

```bash
cd "$DOGFOOD_REPO"
"$MB" doctor
"$MB" doctor repair --plan
"$MB" checkpoint --hook-status --json
"$MB" checkpoint --status --json
"$MB" status --json --peek > "$DOGFOOD_ROOT/status.json"
"$MB" start --json > "$DOGFOOD_ROOT/start.json" || true
```

Check the JSON enough to catch obvious handoff failures:

```bash
python3 - <<'PY'
import json, os
root = os.environ["DOGFOOD_ROOT"]
status = json.load(open(os.path.join(root, "status.json"), encoding="utf-8"))
start = json.load(open(os.path.join(root, "start.json"), encoding="utf-8"))
print("status schema:", status.get("schema_version"))
print("skill wiring:", status.get("runtime", {}).get("skill_wiring"))
print("handoff ready:", start.get("handoff_ready"))
print("follow up:", start.get("command", {}).get("follow_up"))
PY
```

Pass condition:

- `mb doctor` exits successfully or gives an actionable, public-safe repair.
- `mb doctor repair --plan` does not apply changes.
- `mb checkpoint --hook-status --json` and `mb checkpoint --status --json`
  emit parseable JSON without creating a commit.
- `mb status --json --peek` emits parseable JSON and includes runtime skill
  wiring facts.
- `mb start --json` emits parseable JSON and names `/mb-start` as the follow-up
  when handoff is available.

## Phase 3: Local Wiring Repair Check

Run this phase only if Phase 2 reports missing or unhealthy skill wiring. It is
allowed to mutate local Claude wiring files under the fixture repo.

```bash
cd "$DOGFOOD_REPO"
"$MB" skill repair --repo .   # inspect personal-skill shadows; no --apply yet
"$MB" skill link --repo .     # rewrite project-local bridge links
"$MB" doctor
"$MB" start --json > "$DOGFOOD_ROOT/start-after-repair.json" || true
```

Pass condition:

- `mb skill repair --repo .` reports shadow findings and the safe `--apply`
  command without moving personal skills. If a real shadow must be cleared,
  rerun with `--apply` only after reviewing the findings.
- `mb skill link --repo .` explains any project-local bridge links it rewrote.
- `.claude/skills/mb-start/SKILL.md` exists after repair.
- `mb start --json` reports the clearest available next command.

## Phase 4: Claude Code Runtime Smoke

Start Claude Code from the fixture business repo, not from the engine repo:

```bash
cd "$DOGFOOD_REPO"
claude
```

Paste these prompts one at a time. Do not batch them; the transcript matters.

```text
/mb-start
```

Expected observations:

- Claude recognizes `/mb-start` as a Main Branch skill, not an unknown command.
- It confirms it is working in `dogfood-studio` or the fixture path.
- It uses `mb status --json --peek` facts before routing.
- It speaks to a business owner and avoids dumping technical internals unless a
  repair is needed.

Then test `/mb-think`:

```text
/mb-think Should Dogfood Studio focus next week's offer angle on async onboarding audits or live founder calls? Decide from the repo context. Ask before writing any durable decision.
```

Expected observations:

- Claude reads `core/offer.md`, `core/audience.md`, `core/voice.md`, and the
  research file.
- It separates research, decision, and codification.
- It asks before writing to `decisions/` or `core/`.
- If it writes, the file lands in the fixture business repo.

Then test one writing skill:

```text
/mb-organic video "Create three short-form scripts for founders who keep losing offer context between AI sessions. Use the fixture voice and ask before saving drafts."
```

Expected observations:

- Claude uses the fixture voice and audience.
- Drafts are business-owner-readable.
- It asks before saving generated artifacts.
- If it saves, it writes under the fixture repo, usually `documents/` or
  `pushes/` depending on whether the work becomes a coordinated push.

Finally test checkpoint behavior:

```text
Show the checkpoint plan for any approved changes, validate the proposed message, and ask me before saving the checkpoint.
```

If you approve the checkpoint, expected observations:

- Claude calls `mb checkpoint --plan --json`.
- Claude validates the proposed subject with `mb checkpoint --validate "..."`
  before saving.
- Claude calls `mb checkpoint --message "..." --yes` only after approval.
- The saved commit subject uses the business-readable verb contract, such as
  `[decided] ...`, `[drafted] ...`, or `[updated] ...`.

If Claude cannot operate the checkpoint command directly, run the same gated
sequence from the fixture repo and record that as fallback evidence:

```bash
cd "$DOGFOOD_REPO"
"$MB" checkpoint --plan --json
"$MB" checkpoint --validate "[drafted] organic context script" --json
"$MB" checkpoint --message "[drafted] organic context script" --yes --json
"$MB" checkpoint --status --json
```

## Phase 5: Post-Run Checks

Exit Claude Code, then inspect both repos:

```bash
cd "$DOGFOOD_REPO"
git status --short
git log --oneline --decorate -5
find decisions research pushes documents core -type f | sort

if [ -n "${ENGINE_REPO:-}" ]; then
  git -C "$ENGINE_REPO" status --short
fi
```

Pass condition:

- New or changed business files are only in the fixture repo.
- Any saved commits are business-readable.
- The engine repo has no unexpected changes from the Claude Code run.
- Failures are specific enough to turn into a GitHub issue.

## Evidence Template

The automated harness writes this shape to `evidence-template.md`. If you run
the manual phases directly, paste this into the PR or issue comment. Include
short excerpts or summaries of Claude behavior; do not paste private business
data, tokens, account IDs, or long transcripts.

```md
## Claude Code Runtime Dogfood Evidence

Date:
Main Branch ref or version:
Claude Code version:
OS:
Fixture repo path: disposable temp path, no private data
GitHub issue / PR:

### CLI Fixture Setup

- `mb onboard --yes --json`:
- Fixture commit:
- `.claude/skills/mb-start/SKILL.md` present:

### Read-Only Checks

- `mb doctor`:
- `mb doctor repair --plan`:
- `mb status --json --peek`:
- `mb start --json`:

### Claude Runtime Transcript Summary

- Simulation tier:
- `/mb-start` discovered:
- `/mb-start` used business repo and status facts:
- `/mb-start` spoke in operator language:
- `/mb-think` read fixture files:
- `/mb-think` asked before durable writes:
- `/mb-organic` or `/mb-ads` used fixture voice/audience:
- Writing skill asked before saving:
- Checkpoint plan/validate/save behavior:

### Repo Boundary Check

- Business repo changed files:
- Business commits created:
- Engine repo unexpected changes:

### Failures / Follow-Up Issues

- Failure:
- Expected:
- Actual:
- Minimal reproduction:
- Proposed GitHub issue title:
```

When reviewing transcripts, classify failures with the categories in
[Release Simulations](release-simulations.md): grounding, wrong layer, tool
gap, business language, write boundary, repo boundary, provider overclaim,
repair loop, discovery, or conversation shape. Tag the likely fix type so the
failure routes to a focused follow-up instead of becoming vague release notes.

## Failure Triage

Turn failures into follow-up issues when they expose a product gap. Good issue
reports include the command or slash prompt, the fixture state, expected
behavior, actual behavior, and whether the failure was read-only, repair,
business-file write, or checkpoint related.

Common failures:

- `Unknown command: /mb-start`: attach `mb start --json`, `mb skill repair
  --repo .`, and whether `.claude/skills/mb-start/SKILL.md` exists.
- Claude reads or writes the engine repo: include the starting directory,
  `pwd`, fixture `git status --short`, and engine `git status --short`.
- Claude ignores `mb` status facts: include the `/mb-start` transcript summary
  and `status.json` keys that should have been used.
- Claude saves without approval: include the prompt, changed files, and commit
  subject.
- Claude speaks mostly in internals: include a short excerpt and the business
  owner wording you expected.
