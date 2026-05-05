# Main Branch Ethos

Main Branch is public open-source infrastructure for running a business from
markdown files in git.

The product is not another place to paste prompts. The product is a durable
operating substrate:

- the business repo is the business brain;
- `mb` is the deterministic control plane;
- agent-runtime skills are the judgment-heavy execution layer;
- GitHub issues are tasks and requests;
- pull requests are proposals and review conversations;
- git history is the evolution story.
- checkpoints make long agent runs durable before chat context is lost.

The promise is simple: own the work, rent only the rails.

## What We Are Building

Main Branch should help an operator move through five loops:

1. **Know the business** - capture offers, audience, voice, proof, research,
   decisions, and context in files the operator owns.
2. **See what is happening** - summarize repo health, recent changes, stale
   context, connected tools, GitHub tasks, and local setup state.
3. **Decide what matters** - surface the next best actions with clear evidence,
   while leaving the operator in charge.
4. **Execute the work** - run focused workflows for pages, ads, organic
   content, research, fulfillment, bookkeeping, and other business domains.
5. **Narrate and learn** - turn bets, outcomes, changelogs, decisions, and
   retros into public or private operating memory.

Those loops are described in detail in [OPERATOR-LOOPS.md](OPERATOR-LOOPS.md).

## Product Principles

### 1. Files First

Canonical business truth belongs in git: reference files, research, decisions,
campaigns, plans, public artifacts, durable summaries, and proposal changes.
Rebuildable indexes, local caches, credentials, runtime preferences, and live
process state can exist outside git, but they must not replace the repo.

### 2. Thin CLI, Fat Workflows

`mb` should stay deterministic, inspectable, scriptable, and exit-coded. It
owns repo shape, validation, migration, status, updates, graphing, integration
metadata, skill wiring, and runtime adapter contracts.

Agent-runtime skills own synthesis, writing, review, routing, and judgment. A
skill may call `mb` for facts. It should not reimplement repo-health probes or
structural invariants in prose.

### 3. Operator Sovereignty

Main Branch should recommend, not seize control. The system can tell the
operator what looks stale, risky, blocked, or important. It should cite the
signals behind that recommendation and make override paths explicit.

Publishing, spending money, contacting customers, mutating accounts, and
shipping public-facing work should remain intentional operator actions unless a
future decision explicitly changes that boundary.

### 4. Beginner-Safe, Power-User-Honest

The product is for non-developers, but it should not hide the real primitives.
GitHub issues can be described as tasks. Pull requests can be described as
proposals. Git history can be described as shipped work. The underlying terms
should remain available when the user needs them.

Beginner flows should end with exact commands. Power users should always have a
quiet, scriptable path.

### 5. Runtime Honesty

Claude Code is the first supported runtime today. Codex, Cursor, OpenClaw,
Hermes, Paperclip-adjacent orchestration, and local runtimes are compatibility
targets only when adapter code and smoke evidence exist.

Main Branch should meet operators where they already work, but it should not
claim support before support is proven.

### 6. Improve Through Friction

If a user hits an error, missing workflow, confusing step, or repeated manual
repair, Main Branch should make it easy to turn that friction into a clean
GitHub issue. That loop is part of the product. The public issue tracker is how
operator usage becomes shared infrastructure.

Issue drafting must be privacy-safe by default. Business context, customer
data, tokens, local paths, and account details must not be sent without an
explicit operator decision.

### 7. Sidecars Are Optional

Specialized tools can make Main Branch stronger when they do one narrow job
well and return structured output. Examples include public company context,
ads metrics, bookkeeping, transcription, analytics, or deployment helpers.

Sidecars should be optional providers behind stable contracts, not hard
dependencies of the core engine.

### 8. Evidence Beats Vibes

Do not ship runtime claims, migration paths, packaging changes, or first-run
flows without evidence. Use the validation ladder in [AGENTS.md](../AGENTS.md):
static checks, CLI tests, package smoke, fixture repo smoke, and runtime smoke
when the behavior depends on a real runtime.

The product should feel alive, but the substrate should stay boring enough to
debug.

### 9. Git Is The Hidden App

Main Branch should use git as the invisible save system for business work.
Operators should not need to understand branches, diffs, or commits to benefit
from them. Agents should checkpoint meaningful work throughout a run so future
sessions can reconstruct what changed, what was decided, and what remains open
from repo history.

Checkpointing is not noisy autosave. It is durable business memory: readable
commits at meaningful boundaries, with privacy and secret-safety gates before
anything is recorded.

## What We Are Not Building Yet

Main Branch is not a hosted SaaS dashboard, chat client, background daemon,
model host, vector database, scheduler, or marketplace today.

Those may become useful surfaces later. They earn their way in by preserving
the same source of truth: the business repo, GitHub, git history, deterministic
CLI contracts, and explicit runtime adapters.
