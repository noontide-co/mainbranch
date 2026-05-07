# Dependency Choices

Main Branch is public open-source infrastructure. Every dependency,
integration, sidecar, MCP server, CLI, and provider adapter should earn its
place by improving an operator loop while preserving the product boundary:
canonical business truth in git, deterministic `mb` commands, optional
sidecars, safe credentials, and honest runtime claims.

This document explains the default judgment. Specific implementation details
belong in accepted decisions, CLI tests, provider docs, or linked issues.

## Principles

1. **Curate rails instead of connecting everything.** Main Branch should choose
   a small set of boring, inspectable provider paths and make them easy to run
   well. A user may have many SaaS tools; the product does not need to integrate
   all of them.
2. **Prefer official provider surfaces.** Use official CLIs, APIs, MCP servers,
   connectors, or adapter docs when they are stable, documented, and
   smoke-testable.
3. **Prefer narrow deterministic CLIs over broad SDKs.** If the job is
   inspectable, scriptable, exit-coded, and easy to test through a CLI, that is
   usually a better Main Branch surface than importing a large SDK into core.
4. **Keep optional sidecars optional.** Specialized tools can enrich Sense and
   Ship workflows, but a missing sidecar must degrade gracefully instead of
   breaking the core install.
5. **Add dependencies for user loops, not novelty.** A tool earns its place
   when it makes Sense, Decide, Ship, or Reflect better for operators.
6. **Remove redundant or fragile surfaces.** Decline or remove dependencies
   that become redundant, unmaintained, private, fragile, confusing, or
   superseded by an official path.
7. **Keep secrets out of repos.** Credentials belong in the OS keychain,
   runtime-local config, environment variables, 1Password, or another explicit
   secret store. Repo files may hold only safe metadata.
8. **Describe capabilities before vendors.** User-facing copy should say what
   the operator can do. Name a vendor only when the vendor choice affects setup,
   support, credentials, cost, or a provider-specific workflow.
9. **Do not claim support before evidence.** A path is supported only when the
   adapter, docs, and smoke evidence exist. Until then, describe it as planned,
   experimental, or a target.
10. **Leave an exit path.** Every dependency should have a plausible removal,
   replacement, or graceful-degradation story before it becomes product shape.

## Build, Buy, Or Wrap

Main Branch should not absorb every useful tool into the core CLI. The default
choice is:

- **Use an official provider surface** when the provider already has a stable
  CLI, API, MCP server, or connector that can be smoke-tested and explained.
- **Wrap with `mb`** when operators need deterministic readiness checks,
  business-language routing, repair guidance, approval gates, or safe metadata
  around that provider.
- **Use an optional sidecar** when the work needs specialized data capture,
  scraping, analytics, bookkeeping, media generation, or scheduling that would
  make the core package heavy or provider-specific.
- **Build inside `mb`** only when the behavior is part of the common control
  plane: repo shape, validation, graph/status facts, update/repair paths,
  runtime wiring, provider readiness, issue drafting, or guarded checkpoints.
- **Defer** when the path would require unsupported runtime claims, untested
  account mutation, committed secrets, broad browser automation, or a hosted
  state model that has not been accepted.

This keeps the daily loop coherent. Users think in bets, pushes, playbooks,
outcomes, and checkpoints. `mb` checks whether the rails are ready. Provider
tools and sidecars do narrow jobs behind explicit contracts.

## Decision Rubric

Use this rubric before adding, promoting, replacing, or removing a dependency.

| Question | What to look for |
|---|---|
| Which operator loop improves? | Sense, Decide, Ship, or Reflect. Ops is a Ship channel, not a fifth loop. |
| Is there an official provider path? | Prefer official CLIs, APIs, connectors, MCP servers, docs, and account models when they can be tested. |
| Can Main Branch test it? | Local tests, CI tests, read-only smoke, package smoke, fixture repo smoke, or runtime smoke as appropriate. |
| Does it require paid access or hosted setup? | Document account requirements, OAuth/developer-app steps, billing assumptions, and no-account fallback behavior. |
| Where do secrets live? | Credentials must stay outside tracked repos; repo metadata must be safe to share. |
| Does it cross runtime boundaries? | Claude Code is first-class today; other runtimes need adapters and smoke evidence before support claims. |
| Can failures be explained? | `mb doctor`, `mb connect`, `mb status`, or provider docs should tell the user what failed and the next command. |
| Does it mutate external accounts? | Spending, publishing, emailing, deploying, and customer/account mutation need explicit operator action and provider authority. |
| What is the exit plan? | Record the replacement, fallback, deprecation path, or reason the dependency can stay optional. |

## Decision States

Use boring words when recording a choice:

- **Adopted**: part of the supported product surface with validation evidence.
- **Planned**: preferred direction, but not yet supported.
- **Reference**: useful implementation pattern, not required for core use.
- **Optional**: supported or planned enrichment path that must degrade
  gracefully when missing.
- **Removed**: no longer a supported or recommended path.
- **Declined**: considered and intentionally not adopted.
- **Superseded**: replaced by another path; keep the reason visible.

Decisions are revisable. When product direction changes, update the running
choices log or add a dated decision so future contributors do not have to infer
why a tool disappeared.

## Running Choices Log

| Date | Surface | Candidate | Decision | Why | Replacement / next path | Issue |
|---|---|---|---|---|---|---|
| 2026-05-05 | Meta Ads account access | Pipeboard MCP/tools | Removed | A third-party connector should not remain a Main Branch dependency or fallback after the product direction moved to the official Meta path. Keeping it would preserve confusing setup, pricing, and tool-name assumptions. | Use provider-agnostic Meta account-access guidance now; evaluate Meta's official Ads CLI / Ads AI Connectors as the planned path after detection and read-only smoke are wired. | [#304](https://github.com/noontide-co/mainbranch/issues/304) |
| 2026-05-05 | Meta Ads account access | Meta Ads CLI / Ads AI Connectors | Planned | Official provider surfaces are preferred, but Main Branch should not claim live support until setup, detection, and read-only smoke are verified. | Keep Meta readiness planned in `mb connect`; document exact supported commands only after smoke evidence exists. | [#304](https://github.com/noontide-co/mainbranch/issues/304) |
| 2026-05-05 | Google Ads / GTM | Official Google Ads and Tag Manager surfaces | Planned | Paid traffic needs deterministic measurement and conversion checks before spend. Main Branch should prefer official Google paths and local site checks over broad browser automation. | Keep current `mb site check` readiness states; promote Google Ads/GTM automation only behind approval gates and smoke evidence. | [#286](https://github.com/noontide-co/mainbranch/issues/286) |
| 2026-05-04 | Context enrichment | `companyctx` | Reference | Public company/domain context is useful across Sense and Ship workflows, but it should prove the sidecar contract without becoming a required core install. | Use the optional sidecar contract from [the sidecar enrichment decision](../decisions/2026-05-04-sidecar-enrichment-cli-contract.md). | [#265](https://github.com/noontide-co/mainbranch/issues/265) |
| 2026-05-04 | Bookkeeping and P&L | Beancount | Optional future sidecar | Plain-text ledgers are useful, but real finance data has stricter privacy and access boundaries than normal business repo files. | Keep bookkeeping out of core until `mb books` scope is accepted; write approved summaries to shared repos and keep raw ledgers in private sources. | [#128](https://github.com/noontide-co/mainbranch/issues/128) |
| 2026-05-04 | Research enrichment | Apify | Optional provider-readiness path | Scraping and research actors can enrich workflows, but they require explicit provider setup and should not make core install heavy. | Surface readiness through `mb connect plan` / `mb connect status`; promote only workflows with proven value and safe failure behavior. | [#273](https://github.com/noontide-co/mainbranch/issues/273) |
| 2026-05-07 | Public social research | Apify X/TikTok/YouTube actors | Reference optional path | Public social scraping can help Sense workflows and `/mb-think` research, especially comment mining and profile/post analysis, but actor reliability, platform limits, cookies, and terms vary. | Keep as optional read-only research enrichment. Save synthesized findings to `research/`; do not claim private DM access, account mutation, or guaranteed X reply-tree access. | Source context: [#341](https://github.com/noontide-co/mainbranch/issues/341); active follow-up: [#351](https://github.com/noontide-co/mainbranch/issues/351) |
| 2026-05-07 | X social research | Grok/xAI and public web fallbacks | Optional research path | Real-time X sentiment and public post/profile analysis can enrich Sense, but Main Branch should not require X credentials or imply full public reply access without an accepted adapter and smoke evidence. | Use configured Grok/xAI or public web/embeds/screenshots as fallback; route durable findings through `/mb-think` research files. | Source context: [#341](https://github.com/noontide-co/mainbranch/issues/341); active follow-up: [#351](https://github.com/noontide-co/mainbranch/issues/351) |
| 2026-05-07 | X posting, replies, and DMs | Official X API | Planned mutation path | X posting, replies, and DMs require developer approval, OAuth user authority, rate-limit handling, and explicit operator approval. Main Branch has no accepted adapter or smoke evidence today. | Treat as planned only. Do not automate X replies/DMs from Main Branch until provider authority, approval gates, tests, docs, and smoke evidence exist. | Source context: [#341](https://github.com/noontide-co/mainbranch/issues/341); active follow-up: [#351](https://github.com/noontide-co/mainbranch/issues/351) |
| 2026-05-04 | Sites and DNS | Cloudflare CLI/API | Adopted where smoke-tested | Cloudflare is an official provider path for site, DNS, Pages, and future deterministic CMS/site operations when a flow has a safe token boundary and validation evidence. | Keep credentials outside repos; expand only through explicit `mb connect`, site-readiness contracts, GitHub-linked deploy flows, and operator approval gates. | [#89](https://github.com/noontide-co/mainbranch/issues/89) |
| 2026-05-07 | Social scheduling | Postiz | Candidate supported rail after smoke | Social scheduling is a clear Ship rail, and Postiz now has documented MCP/API surfaces plus hosted and self-hosted deployment paths. Main Branch should recommend hosted vs self-hosted vs VPS through opinionated onboarding, not a neutral provider list. | Run a focused Postiz MCP/API scheduling smoke before claiming support; see [the Postiz scheduling rail decision](../decisions/2026-05-07-postiz-scheduling-rail.md). | [#352](https://github.com/noontide-co/mainbranch/issues/352) |
| 2026-05-07 | Growth automation playbooks | Comment-to-DM and resource-delivery providers | Accepted add-on boundary | Comment-keyword and DM-keyword funnels are useful growth playbooks, but provider write actions mutate inboxes and customer conversations. Main Branch should own playbook specs, approval evidence, resources, and outcomes under `pushes/`, while partner tools or official APIs own mutation until tested. | Keep ManyChat-style tools as add-on candidates, not core dependencies. Defer X comment-to-DM execution, LinkedIn write automation, TikTok DM/comment write, and browser-automation mass-DM tools; see [the growth automation playbook decision](../decisions/2026-05-07-growth-automation-playbook-addons.md). | Schema: [#350](https://github.com/noontide-co/mainbranch/issues/350); X boundary: [#351](https://github.com/noontide-co/mainbranch/issues/351); source context: [#341](https://github.com/noontide-co/mainbranch/issues/341) |
| 2026-05-04 | Workspace docs and sheets | Google Workspace | Planned optional provider | Many operators already have Docs, Sheets, and Drive source material. Main Branch should ingest or reference that material without making Google the canonical memory. | Treat Google Workspace as source/input and provider metadata; durable summaries and decisions flow back into the business repo. | Follow-up issue needed |
| 2026-05-04 | GitHub-native task and release flow | GitHub CLI | Adopted core operational dependency | GitHub issues, pull requests, releases, and auth are central public primitives; `gh` is inspectable, scriptable, and already expected by contributor and issue-drafting flows. | Keep browser/manual fallbacks for user-facing issue submission where needed; use `gh` for GitHub truth and mutations in agent workflows. | [#264](https://github.com/noontide-co/mainbranch/issues/264) |

## Related Public Contracts

- [ETHOS.md](ETHOS.md) defines the product principles, state model, runtime
  honesty, and optional-sidecar stance.
- [OPERATOR-LOOPS.md](OPERATOR-LOOPS.md) defines Sense, Decide, Ship, Reflect,
  and the Paid / Organic / Pages / Ops channels.
- [compatibility.md](compatibility.md) defines supported, experimental, and
  roadmap runtime surfaces.
- [Sidecar enrichment CLI contract](../decisions/2026-05-04-sidecar-enrichment-cli-contract.md)
  defines how optional sidecars should integrate.
- [Workspace, repo, and sensitive-data boundaries](../decisions/2026-05-04-workspace-repo-sensitive-data-boundaries.md)
  defines where secrets, finance/legal data, and provider authority belong.
