# Router and Language Contract

`/mb-start` is the business router. It should feel like the operator opened the
business and the system remembered where they are, what changed, and what kind
of work their current words imply.

Use this reference after `mb status --json --peek` is available and before
presenting a menu.

This operationalizes the repo-wide contract in `AGENTS.md`, generated business
repo guidance in `templates/`, and `mb educational git-history-vs-cloud-sync`:
git remains the durable memory layer, but the operator hears business language
first.

---

## Routing Order

1. If the user stated a live intent, route that intent before showing generic
   ranked actions. Ranked actions are for open-ended starts such as "what should
   I do next?", not for overriding "set up bookkeeping" or "save this."
2. Apply hard gates first: required Main Branch update, broken repo wiring,
   missing business repo, provider danger, private-data boundary, or destructive
   operation.
3. Use status facts as evidence: `ranked_actions`, `update`, `readiness`,
   `onboarding`, `drift`, `integrations`, `github`, `brain`, `checkpoint`,
   `since_last_check`, `journal`, and `money_path`.
4. Choose the smallest useful next workflow. Do not present the full route menu
   when a clear intent maps to one route.
5. If two routes are plausible, ask one business question that separates them.
   Example: "Is this bookkeeping setup, or are you trying to decide the tool?"

---

## First Screen Shape

For a normal returning session, answer in this order:

1. Working context: business name and the plain-language sync state.
2. Update posture: strongly recommend updates when available, especially when
   the user's stated intent touches a feature added after their installed
   version.
3. Where we left off: 1 to 3 business-readable facts from status, without raw
   hashes or branch names.
4. Current route: the inferred workflow or one compact choice list.

Avoid "Something else" as the main escape hatch. Use "tell me what you came here
to do" only after showing the likely business routes.

---

## Save and Sync Vocabulary

Use business words first. Keep technical terms available only when they are the
exact command, validation evidence, or the operator asks for git details.

| Technical state | Default operator language |
| --- | --- |
| commit | saved checkpoint |
| uncommitted changes | unsaved local work |
| dirty files | local files with unsaved changes |
| push | sync saved checkpoint to the shared repo |
| pull/fetch | catch up with the shared repo |
| rebase | reconcile local saved work with newer shared work |
| ahead | saved locally but not synced |
| behind | newer saved work exists in the shared repo |
| diverged | both your local repo and the shared repo have newer saved work |
| branch/worktree | workspace |
| conflict | the same file changed in two places |
| hash/SHA | checkpoint id |

Do not print checkpoint ids, branch names, `origin`, `ahead`, `behind`,
`diverged`, `rebase`, or `commit` in the first response unless they are inside a
command the user must run or the user asked for technical detail.

Good pattern:

> "Your bookkeeping setup is saved locally. The shared repo also has one newer
> saved change, so reconcile before syncing."

Avoid:

> "Local and origin have diverged. Run `git pull --rebase` before pushing."

---

## Update Posture

When `status.update.severity` is `recommended` or `required`, name the installed
and latest versions if present and say how many version steps are behind when
the numbers are obvious.

If the status report includes release highlights or ranked update actions, use
those highlights. If not, say the user may be missing recent routing, repair,
or skill fixes; do not invent exact release notes.

Use direct language:

> "Update strongly recommended: mb 0.3.15 -> 0.3.17. You are two versions behind,
> and this session touches routing/bookkeeping behavior that has been changing.
> Run `mb update` before we continue."

If the update is required, run or route to the cited update command before
business work.

---

## Intent Clusters

### Save, checkpoint, wrap, sync, publish

Signals: save, saved, checkpoint, wrap up, closing out, end my day, sync,
publish my saved work, share for review, pull request, PR, proposal, catch up,
reconcile, shared repo, newer work.

Route:

- If ending the session, use `/mb-end`.
- If saving progress midstream, run `mb checkpoint --plan --json`, then validate
  and save after approval.
- If local/shared repo state is involved, explain it with the save/sync
  vocabulary above. Do not prescribe a rebase in first response; say reconcile
  unless technical detail is needed.
- If the user asks to publish, open a PR, or share work for review, use status
  `git.workflow_mode`, `git.summary`, and GitHub facts to explain whether this
  is a saved checkpoint, a sync, or a proposal/review path. The planned
  `mb publish --plan` and packaged publish skill are not shipped yet;
  do not pretend they exist or load ad hoc PR-instruction attachments.

### Bookkeeping, books, finance, accounting

Signals: bookkeeping, books, finance, accounting, chart of accounts, P&L,
ledger, bank statements, restricted finance child repo, restricted repo topology,
hledger, receipts, tax, payroll, revenue report.

Route:

- Run `mb books check --repo "$REPO_PATH" --json` before inventing structure.
- Keep raw ledgers, statements, credentials, account numbers, payroll rows, tax
  IDs, and exact private numbers out of the public/team-safe business repo.
- Preserve public topology terms: hub repo, child repo, hub registry
  `core/operations/repo-topology.md`, child descriptor `.mainbranch/repo.json`,
  role `finance`, and visibility `restricted` or `local_only`.
- Use the books contract fields, especially `storage_mode`, and the repo
  topology role `finance` with visibility `restricted` or `local_only` to
  decide where raw books belong. The hub repo should keep only safe summaries,
  decisions, and links.
- If the user is deciding tooling, route to `/mb-think` after the books check.
- If the user is setting up the safe repo contract, draft or update the safe
  finance files named by the books check. Do not create generic finance files
  that bypass the contract.

### Provider and tool setup

Signals: connect, provider, Cloudflare, GitHub, Google, Workspace, Meta Ads,
Stripe, hledger, Apify, Postiz, Cal.com, token, API key, deployment, DNS,
calendar, booking.

Route:

- Read `status.integrations` first.
- Run `mb connect plan` or `mb connect doctor --json` when status says a
  provider is missing, degraded, or needed for the stated route.
- Explain the business capability first, then the command.
- Never ask the user to paste secrets into repo files or chat.

### Repair, update, drift

Signals: broken, not showing up, stale, migration, old layout, warnings, validate
noise, repair, update, missing links, cross refs.

Route:

- Required update or stale skill wiring comes before output work.
- Use `mb doctor repair --plan --json` for repo drift.
- Use `mb validate --cross-refs` only when relationship/link health is the
  stated task or status points there.

### Decide, codify, research

Signals: think, decide, figure out, explore, research, compare, tool decision,
strategy, positioning, offer, audience, voice, soul check, vendor choice.

Route to `/mb-think`, with `codify` when the task is to turn known context into
durable repo truth.

### Bets, pushes, sites, ads, organic, wiki

Signals and routes:

- bet, wager, deadline, metric, result, outcome: `/mb-bet`
- launch, push, playbook, offer launch: launch orchestration, then `/mb-think`,
  `/mb-site`, `/mb-ads`, or checkpoint as the current step requires
- content strategy, distribution strategy, channel strategy, account strategy,
  founder voice, weekly content plan: `/mb-think` to codify the strategy layer,
  then `/mb-organic`, `/mb-site`, or `/mb-ads` for output
- site, landing page, lander, minisite, publish: `/mb-site`
- ads, Google Ads, Meta Ads, video ad, compliance: `/mb-ads`
- organic, reels, TikTok, LinkedIn, carousel, repurpose: `/mb-organic`
- wiki, notes, public knowledge base, atomic notes: `/mb-wiki`
- confused, help, explain the system: `/mb-help`

---

## Dead-End Avoidance

- Do not let generic "set up" override the specific noun. "Set up
  bookkeeping" routes through books; "set up Cloudflare" routes through
  provider checks; "set up the repo" routes to `/mb-setup`.
- Do not turn every returning session into triage. Triage is for open-ended
  prioritization or explicit deep review.
- Do not show raw recent checkpoint ids as proof of continuity. Use journal
  summaries and file/topic names.
- Do not blindly catch up the business repo from the shared remote. First
  explain the sync state and ask before changing local saved work.
