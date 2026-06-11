# LOOP-STATE — the Main Branch development loop

The continuity file for the all-day `/loop` session that builds the engine.
Each iteration reads this first, does the next smallest correct slice, and
updates this file in the same PR. Devon steers by editing the **Steering**
section; the loop never overrides it.

Canon (read on first iteration of a fresh session):
- The architecture lock: `noontide` hub → `decisions/2026-06-11-mb-three-layer-architecture-and-pulse.md`
  (three layers; data flows down only; patterns graduate up only when proven).
- The graduation queue: issues #803–#808 + #812–#820 on noontide-co/mainbranch.

## Steering (Devon edits this; loop obeys)

- Mission: improve and fix Main Branch's current issues. Work the priority
  order below. Small slices, release discipline.
- Check-in cadence: Devon reviews every few hours. Park anything ambiguous
  in **Flagged for Devon** instead of guessing.

## Priority order (from the 2026-06-11 decision)

1. **#812 `mb connect token <provider>`** — smallest slice; unblocks every
   collector; de-fragiles the live BOR brief. START HERE.
2. **#804 worktree skills bug** — critical-tagged; silently breaks /mb-* in
   worktrees; blocks community usability.
3. **BOR brief → collector refactor** (pulse v0): split the 4 sources of
   `~/.claude/scheduled-tasks/bor-daily-operator-brief/SKILL.md` into
   deterministic collectors (morning-brief contract), definition versioned in
   the noontide hub. Proves the shape on a live business.
4. **#813 `mb pulse init` + /mb-pulse** — generalize step 3.
5. **#815 delivery-truth doctrine page** (pure docs, cheap), **#814 mb spine
   init/query**, **#816 mb canary init**, **#817 dossier + mb doctor**,
   **#820 operating-principles graduation**, **#803/#805/#806/#808** as specced.
6. **Hub hygiene** (interleave ≤1 small PR per few iterations): the kill/merge
   lists in the 2026-06-11 decision (stale CLAUDE.md lines, proposed-decision
   graveyard, product-ladder missing the live money path).

## Hard guardrails

- PR-only to every protected main (mainbranch main IS protected). Small PRs.
- READ-ONLY on all business data (D1/KV/Resend/Meta/Stripe/Shopify). No
  spend, no publish, no send, no contact mutations, no credential writes.
- Credentials via mb connect keychain / env.sh; never print a token.
- Graduate PROVEN patterns only; no new abstractions (operating-principles §10).
- Validate substantive work with fresh-context agents against LIVE state (§11).
- Never rule on Devon-only calls (Joel lane, bet-doctrine fork, offer-board,
  pulse-into-status question) — park in Flagged for Devon.

## Flagged for Devon

- (10 open questions live in the 2026-06-11 decision; loop appends new ones here)

## Shipped

- 2026-06-11: decision merged (noontide#173); issues #812–#820 filed; spine
  send-truth (bookedoutroofers#99) + privacy chat disclosure (#98) live;
  unattended-cron allow rules set in ~/.claude/settings.json.

## Next intent

- Spec + implement #812 `mb connect token` as the first PR.
