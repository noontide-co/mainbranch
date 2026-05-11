---
type: decision
date: 2026-05-11
status: accepted
topic: Operator-facing GitOps and major migration planning
linked_issues:
  - https://github.com/noontide-co/mainbranch/issues/463
linked_decisions:
  - decisions/2026-05-01-mb-cli-vs-agent-workflows-boundary.md
  - decisions/2026-05-02-github-native-business-os.md
  - decisions/2026-05-05-operator-loops-taxonomy.md
  - decisions/2026-05-05-operator-readable-git-history.md
  - decisions/2026-05-06-main-branch-operating-spine.md
  - decisions/2026-05-08-business-repo-topology-map.md
linked_docs:
  - AGENTS.md
  - docs/OPERATOR-LOOPS.md
  - docs/ROADMAP.md
tags: [v0-3, gitops, migration, status, doctor, validate, checkpoint, publish]
---

# Operator-Facing GitOps and Major Migration Planning

## Decision

Main Branch separates **deterministic facts** (CLI JSON) from **operator-facing
guidance** (skill prose) by adding three primitives to the engine and deferring
three command surfaces to follow-up issues.

Land in this slice:

1. **`audience` classification** on every finding emitted by `mb doctor`,
   `mb validate`, and `mb status` ranked actions. Values: `mechanical`,
   `operator_decision`, `informational`.
2. **`operator_summary`** plain-language one-liner on top-level findings, so a
   business owner can read the next step without parsing schema language.
3. **Workflow awareness** in `mb status` — extend the existing `git` block to
   name the workflow mode (`solo-on-main`, `branch`, `worktree`, `detached`),
   detect the default branch, and report ahead/behind counts so skills can
   route save and publish guidance without their own git wrappers.

Defer to follow-up issues, with contracts named here so future work can land
without re-litigating the design:

4. **`mb commit --plan` / `mb publish --plan`** — planned save and publish
   primitives that read the workflow mode and route to the right git operation.
5. **Packaged `/mb-publish` skill** — replaces per-session
   `.context/attachments/PR instructions` files with a bundled skill that reads
   `mb publish --plan` and walks the operator through it.
6. **`mb migrate plan` non-standard folder scanner** — extends today's
   `mb migrate` with a planner that surfaces non-standard top-level folders,
   path substitution maps, and preservation guarantees before any move.

## Why

Dogfooding a Noontide business-repo migration after v0.3.10–v0.3.15 showed two
gaps:

- `mb doctor` and `mb validate` produce useful facts, but they still speak
  schema and Git language. A business owner reads the JSON and does not know
  which findings are safe to auto-repair and which need a human call.
- Publishing changes is currently a per-session `.context/attachments/PR
  instructions` file. That is a maintainer workaround. The engine should know
  how to save and publish without a paste-in.

This decision draws a single boundary: **the CLI exposes structured facts;
runtime skills translate them into business language.** That boundary is in
`decisions/2026-05-01-mb-cli-vs-agent-workflows-boundary.md`, but the current
finding shapes do not carry enough information for skills to do that
translation without re-deriving it every time. The three primitives in this
slice give skills the routing signals they need.

The deferred surfaces (commit-plan, publish-plan, migration planner) all depend
on these primitives, so locking the primitives first lets each follow-up issue
ship in its own PR with its own validation evidence.

## Classification Taxonomy

Every finding emitted by `mb doctor`, `mb validate`, and `mb status` ranked
actions carries an `audience` field. Values are stable, additive, and small:

- **`mechanical`** — Main Branch can apply the fix safely without operator
  judgment. The repair is a renamed field, a missing mirror link, a stale
  cache, or any change with a deterministic correct answer. Today this maps to
  doctor actions with `safe_to_apply: true` and `mode: "write"`, validate
  findings with categories in the deterministic-repair set, and status actions
  whose recommended command is a `--apply`-style flag.
- **`operator_decision`** — A human must decide. The repair is a content
  change, a destructive move, a frontmatter shape that depends on what the
  operator meant, or a workflow choice. Today this maps to doctor actions with
  `safe_to_apply: false`, validate findings with operator-judgment categories
  (status enum, missing slug, missing reverse link, broken cross-ref), and
  status actions that recommend writing or editing repo files.
- **`informational`** — The finding is a signal, not a fix. Used for read-only
  checks, ranked actions that surface state without recommending mutation, and
  doctor actions with `mode: "read"`.

The existing `safe_to_apply` boolean on doctor actions stays as the safety
gate. `audience` is the routing primitive for skills and agents; it is not a
new safety mechanism.

### Mapping rules (this slice)

- `mb doctor` actions
  - `mode == "read"` → `informational`
  - `mode == "write"` and `safe_to_apply` → `mechanical`
  - `mode == "write"` and not `safe_to_apply` → `operator_decision`
- `mb validate` finding categories
  - `missing_related_link_mirror`, `migration_drift` → `mechanical`
  - `yaml_error`, `schema_shape_error`, `no_frontmatter` → `operator_decision`
    (the file is broken; a human reads and fixes)
  - `missing_slug`, `missing_required_key`, `status_enum_mismatch`,
    `enum_mismatch`, `missing_cross_ref_target`, `missing_reverse_link` →
    `operator_decision`
  - `other_error`, `other_warning` → `operator_decision`
- `mb status` ranked actions inherit `audience` from their underlying signal
  when present; otherwise they default to `operator_decision` (status's job is
  to prompt judgment, not silently repair).

These rules live in code, not docs. Skills and agents should read the
`audience` field, not re-derive from `safe_to_apply` or category names.

## Operator-Facing Summary

`operator_summary` is a plain-language one-liner on top-level findings:

- `mb doctor` repair sections grow an `operator_summary` per section.
- `mb validate` validation categories already carry a `repair` string;
  `operator_summary` is added alongside as the human-facing phrasing, and
  `repair` remains the action-oriented phrasing (the two can be the same
  string when no separate operator framing is useful).
- `mb status` ranked actions grow an `operator_summary` field built from their
  existing `reason` plus a verb prefix.

The summary is in plain business language, never references schema field
names, and never assumes the operator knows what Git or YAML is.

## Workflow Awareness in `mb status`

`mb status`'s `git` block today emits:

```text
git.available, git.inside_work_tree, git.branch, git.commit,
git.dirty, git.dirty_count, git.dirty_files, git.remote, git.error
```

This slice adds, in the same block, as additive optional fields:

- **`workflow`** — string, one of:
  - `solo-on-main` — current branch is the default branch and there is no
    branch-and-PR workflow expected today.
  - `branch` — current branch is not the default branch, and the repo is a
    plain clone or main worktree.
  - `worktree` — current checkout is a linked git worktree (Conductor
    workspaces, manual `git worktree add`).
  - `detached` — `HEAD` is detached. No save or publish operations should be
    proposed without operator action.
- **`default_branch`** — string, the repo's default branch when known.
  Detected via `git symbolic-ref refs/remotes/origin/HEAD`, falling back to
  `main` and then `master` for repos without a remote.
- **`ahead`** — integer count of commits ahead of the upstream, or `null` when
  unknown (no upstream tracking).
- **`behind`** — integer count of commits behind the upstream, or `null`.
- **`upstream`** — string name of the upstream ref, or empty.
- **`worktree_root`** — absolute path of the worktree root when `workflow` is
  `worktree`; empty otherwise.
- **`summary`** — short operator-facing one-liner describing the workflow
  state ("On main with no pending changes", "On branch `<name>` with N
  uncommitted files", "In a worktree off `main`, branch `<name>`").

All additions are additive. `STATUS_SCHEMA_VERSION` stays at `"1.0"`. Consumers
that do not read the new fields keep working.

## Deferred Surfaces (Contracts Locked Here, Implementation in Follow-Ups)

### `mb commit --plan` / `mb publish --plan`

A planned save and publish layer that reads `git.workflow` and routes:

- `solo-on-main` and `worktree` → `mb commit --plan` produces concern-clustered
  commit groups (using `mb checkpoint --plan` machinery) and recommends
  `git push` when the operator confirms.
- `branch` and `worktree` with a non-default branch → `mb publish --plan`
  produces the commit groups plus a PR plan: title, body skeleton built from
  the branch's commit log, closing-issues parsed from commit messages, base
  branch, and the `gh pr create` command the operator can run.

Both commands emit structured JSON with the same shape as `mb checkpoint
--plan` today, plus a top-level `audience` and `operator_summary`. They write
nothing without `--yes`. They are read-only by default.

Follow-up issue: track separately. Validation evidence required: fixture repo
covering each workflow mode, plus a CLI smoke that exercises plan-only.

### Packaged `/mb-publish` skill

Replaces the per-session `.context/attachments/PR instructions` files. The
skill calls `mb publish --plan --json`, renders the plan in business language,
asks the operator to confirm, and shells out to `git push` and `gh pr create`.
The skill never reimplements PR-body generation; it reads the plan.

Follow-up issue: track separately. Validation: runtime smoke from a fresh
business repo on a feature branch.

### `mb migrate plan`

Extends today's `mb migrate` with a planner mode that scans non-standard
top-level folders (`outputs/`, `reference/`, `briefs/`, `content/`, `staging/`,
`skills/`, `ops/`, and any custom folder not covered by the topology map),
produces a path substitution map showing where each tree would land in the
current topology, preserves git history via `git mv`, and refuses to apply
ambiguous moves without operator confirmation. Each move carries an
`audience` field (`mechanical` for a topology-recognized rename;
`operator_decision` for an ambiguous move).

Follow-up issue: track separately. Validation: fixture repo with at least one
non-standard folder and a snapshot test of the plan output.

## Consequences

- `mb status`, `mb doctor`, and `mb validate` JSON gains additive fields.
  Tests assert presence and shape; tests do not assert absence of other fields,
  to keep this slice composable with future work.
- Skills can route on `audience` and render `operator_summary` without their
  own git wrappers or schema-to-prose translation.
- Future work (`mb commit --plan`, `mb publish --plan`, `/mb-publish`,
  `mb migrate plan`) lands in its own issue and PR. Each one cites this
  decision as the contract.
- Per-session `.context/attachments/PR instructions` files become unnecessary
  once `/mb-publish` ships. Until then, they remain a maintainer-only
  workaround and should not be referenced from public docs.
- `docs/ROADMAP.md` v0.3 line gains a sub-bullet for this work; the deferred
  surfaces land under v0.3 or v0.4 depending on sequencing.

## Review Trigger

Revisit if any of these turn out to be wrong:

- A finding category needs a fourth `audience` value (for example, a "blocked"
  state where the system cannot classify safety). If so, extend the enum;
  do not silently expand existing values.
- The workflow detection logic misclassifies a real repo Devon or a public
  contributor uses. Update the detection rules in `mb/mb/status.py` and the
  fixture set.
- A skill needs information the `operator_summary` field cannot carry. Add a
  second field (`operator_explanation`?) rather than overloading
  `operator_summary`.

## Related links

- [GitOps issue #463](https://github.com/noontide-co/mainbranch/issues/463)
- [CLI vs agent workflows boundary](2026-05-01-mb-cli-vs-agent-workflows-boundary.md)
- [Operator loops taxonomy](2026-05-05-operator-loops-taxonomy.md)
- [Operator-readable git history](2026-05-05-operator-readable-git-history.md)
- [Business repo topology map](2026-05-08-business-repo-topology-map.md)
