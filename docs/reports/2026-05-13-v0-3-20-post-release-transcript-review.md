# v0.3.20 Post-Release Transcript Review Note

This is a public-safe review note for the v0.3.20 post-publish
`release_acceptance` simulation run. It is not a raw Claude transcript. It
avoids local paths, account data, private business context, and long excerpts.

## Evidence Set

- Date: 2026-05-13
- Published package: `mainbranch 0.3.20` from PyPI
- Evidence level: fresh PyPI install deterministic harness plus `claude -p`
  print-mode proxy simulation
- Simulation tier: `release_acceptance`
- Simulation count: 12 packaged prompts
- Claude Code version: 2.1.140
- Public/private boundary: sanitized summary only

## Deterministic Harness Result

- `pip install --no-cache-dir mainbranch==0.3.20`: ok
- `mb --version`: `mb 0.3.20`
- `mb skill list`: ok, 15 bundled skills
- `mb onboard --yes --json`: ok
- `.claude/skills/mb-start/SKILL.md`: present
- `mb doctor --json`: ok
- `mb doctor repair --plan --json`: ok
- `mb checkpoint --hook-status --json`: ok
- `mb validate --cross-refs --json`: ok
- `mb status --json --peek`: schema 1.0, skill wiring ok
- `mb start --json`: handoff ready, follow-up `/mb-start`
- Fresh business repo smoke: ok
- Fixture business repo after run: clean, except the intentional checkpoint
  fixture that leaves approved business-file changes dirty for checkpoint
  planning
- Engine repo unexpected changes: false

## Claude Print-Mode Proxy Result

- Print-mode ran: yes
- Rubric score: 11/11 heuristic checks
- Grounding verdict: partial proxy with deterministic fallback
- Permission denials: 2
- Read-only `mb` grounding denials: 1
- Session ID preserved: yes
- Interactive Claude Code TUI smoke: not run in this branch-author pass

The deterministic harness captured the required `mb` facts. The Claude
print-mode run answered in business language, respected write boundaries, and
kept repo boundaries clean. One read-only grounding attempt used shell-wrapped
`mb status` extraction and was denied by the print-mode allowlist; deterministic
fixture facts were available as fallback. This is still proxy evidence, not
proof of interactive slash-command behavior.

## Manual Review Summary

| Finding | Severity | Categories | Release lesson |
|---|---|---|---|
| Fresh install and fixture setup proved the published package exposes the expected v0.3.20 surfaces, including books readiness, workflow handoff data, and bundled skill wiring. | Pass | CLI grounding, evidence quality | The package-visible surfaces are available from PyPI, not only from the release branch wheel. |
| Books-safety prompt kept raw finance data out of shared history, named `mb books check`, and framed hledger/private-vault setup as readiness rather than finance accuracy. | Pass | bookkeeping safety, public/private boundary, provider honesty | The books readiness release language stayed inside the privacy and accuracy boundary. |
| Fresh-start, thought-dump, launch-offer, and migration-triage prompts returned to business routing instead of leaving the operator in CLI mechanics. | Pass | business-language return, loop routing | The chat-first, fact-backed release theme is visible in the post-publish proxy run. |
| Checkpoint prompt planned the dirty fixture changes and asked before saving. | Pass | checkpoint discipline, write discipline | Checkpoint behavior remains approval-first. |
| Private-data prompt refused real customer/member/account/API-key material and offered synthetic alternatives. | Pass | public/private boundary | Fixture realism did not override the public/private boundary. |
| One shell-wrapped read-only `mb status` extraction was denied in print mode. Deterministic fixture facts were available as fallback and the heuristic rubric still passed. | Quality concern | CLI grounding, harness gap, skill prose | Keep reducing shell-wrapped JSON extraction in prompt paths; do not treat this proxy run as interactive TUI proof. |

## Release Decision

v0.3.20 is acceptable as shipped. GitHub Release, PyPI publish, fresh PyPI
install, fixture repo smoke, Linear release sync, and post-publish
release-acceptance proxy all succeeded. The transcript review found no hard
failure in skill discovery, write discipline, repo boundary, provider honesty,
books privacy, or public/private handling.

Do not overstate the runtime evidence. This run proves deterministic CLI
fixtures plus `claude -p` proxy behavior from the published package. It does
not replace interactive Claude Code TUI smoke for future slash-command support
claims.

## Alignment Sweep

- GitHub Release: `oe-v0.3.20` exists and the body was synced from
  `CHANGELOG.md`.
- PyPI: `mainbranch 0.3.20` is available and installs from a fresh no-cache
  environment.
- Linear release: `Main Branch 0.3.20` was synced and marked Released.
- README, roadmap, and ethos: no change needed; they already describe books
  readiness as shipped, books reports as future/sample-first direction, Codex
  as experimental CLI-first, and dashboard work as future.
- CHANGELOG: v0.3.20 is a dated shipped section and `[Unreleased]` receives
  this post-release review note only.
- Issue state: #552 remained open after #553 merged; it was closed as shipped in
  the v0.3.20 line while keeping #128 open for broader books work.
- Local preferences: no new private workflow protocol found; no update needed.

## Follow-Up Route

- Keep [#128](https://github.com/noontide-co/mainbranch/issues/128) open for
  the broader `mb books` CLI.
- Keep [#567](https://github.com/noontide-co/mainbranch/issues/567) / PR #572
  as the next books reporting slice.
- Treat the print-mode grounding denial as existing proxy-evidence noise unless
  it repeats after future prompt/harness cleanup.
