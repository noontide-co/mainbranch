---
type: decision
date: 2026-05-07
status: accepted
topic: Growth automation playbook add-ons
linked_decisions:
  - decisions/2026-05-01-mb-cli-vs-agent-workflows-boundary.md
  - decisions/2026-05-04-sidecar-enrichment-cli-contract.md
  - decisions/2026-05-07-postiz-scheduling-rail.md
linked_issues: []
participants: [Devon, Codex]
tags: [v0-3, playbooks, growth, social, integrations, provider-boundary]
---

# Growth Automation Playbook Add-ons

## Decision

Main Branch should model growth automation as playbooks attached to pushes, not
as hidden core automation. The product should own the durable plan, approvals,
resources, copy, validation evidence, and outcomes. Provider tools should own
external account mutation until Main Branch has accepted adapters, approval
gates, tests, docs, and smoke evidence.

The default playbook path should be:

```text
pushes/<push>/playbooks/<playbook>.md
```

This keeps social-growth experiments close to the business work they serve and
lets `mb status`, future dashboards, bets, issues, and team logs reason about
what was planned, approved, activated, paused, or retired.

## Architectural Split

The durable split is read versus write:

- **Read adapters** enrich Sense. Examples: Apify public scraping, provider read
  APIs, YouTube transcripts, public X/profile/post/comment samples, and account
  analytics when credentials are configured.
- **Write adapters** mutate external accounts. Examples: publishing, replying,
  DMing, emailing, scheduling, auto-following, auto-liking, and lead capture.

Read adapters can become first-class earlier because they can degrade
gracefully and do not speak to customers. Write adapters require stricter
provider authority, approval gates, rate-limit handling, privacy-safe logs,
tests, docs, and smoke evidence.

## Playbook Contract

A v1 playbook should capture:

```yaml
type: playbook
status: draft
push: ../push.md
platform: instagram
provider: manual
trigger:
  kind: comment_keyword
  keyword: TEMPLATE
resource:
  kind: url
  value: https://example.com/resource
approval:
  required: true
  approved_by:
  approved_at:
state:
  provider_object_id:
  activated_at:
  retired_at:
validation:
  dry_run:
  smoke_evidence:
  notes:
```

The exact schema can evolve, but it should preserve:

- inputs: platform, post, trigger, keyword, resource, message copy;
- provider: `manual`, `manychat`, `linkdm`, `postiz`, `x-api`, or another
  accepted provider id;
- approval: explicit human approval for any external account mutation;
- state: safe provider ids only, no tokens;
- validation: dry-run, smoke evidence, and failure/retire criteria;
- outcome: metrics or lessons linked back to the push and bet.

## v1 Product Boundary

Main Branch may:

- draft comment-keyword, DM-keyword, reply, link, and resource-delivery
  playbooks;
- validate that the playbook has an approval state, resource, copy, and
  provider boundary;
- generate provider-specific setup instructions or recipes;
- record public-safe smoke evidence and outcomes;
- route raw provider exports or scrape dumps out of committed files.

Main Branch must not:

- auto-DM, auto-reply, auto-like, auto-follow, scrape private inboxes, or mutate
  social accounts by default;
- recommend browser-automation mass-DM tools as a safe default;
- claim support for a provider before API/MCP/docs and smoke evidence exist;
- commit raw DMs, customer records, full comment dumps, provider tokens, or
  private account analytics;
- treat "a tool exists" as the same thing as a Main Branch-supported rail.

## Platform Read

Comment-to-DM is not a universal cross-platform primitive.

| Platform | v1 stance | Reason |
|---|---|---|
| Instagram | Draft/validate playbooks first; execute through manual or partner tool until a provider path is accepted | Comment-keyword to DM is a common provider-supported growth pattern, but it mutates inboxes |
| WhatsApp | Candidate for later because official business messaging exists | Requires opt-in, templates, account setup, and privacy handling |
| X/Twitter | Research and defer; do not support comment-to-DM in v1 | Automation policy, DM opt-in requirements, API cost/friction, and account-risk concerns |
| LinkedIn | Do not touch write automation in v1 | High suspension and policy risk |
| TikTok | Draft/research only | DM/comment write surfaces are not a clear Main Branch path |
| YouTube | Reply/link playbooks only, no DM | YouTube has comments, not DMs |
| Threads | Reply/link playbooks only until messaging support is official and tested | Reply surfaces are different from inbox automation |

## X/Twitter Research Queue

The current research context is useful and should not be discarded. It suggests
there is operator interest in X "comment to DM" or interaction-triggered
resource delivery, and that current market tools include creator-growth
products, browser-extension tools, X-focused schedulers, unofficial DM tools,
and automation runners.

Candidate names observed in research context include:

- TweetHunter;
- Hypefury;
- Typefully;
- DM Dad;
- Hivoe;
- Drippi;
- PhantomBuster;
- BooSend;
- DMpro;
- xAutoDM;
- MKT X;
- Zapier, Make, Pipedream, Activepieces, and n8n as automation runners.

These names are a research queue, not an endorsement. Before any public
recommendation, verify current pricing, API/MCP/CLI availability, official
provider status, policy risk, account safety, and whether the tool can be used
without committing secrets or depending on fragile browser automation.

For X specifically, the likely future shape is:

- use Typefully or Postiz for scheduling/drafting if their APIs/MCP surfaces are
  smoke-tested;
- use Apify/Grok/web/manual exports for read-only public research;
- prefer public reply/link/resource playbooks over auto-DM;
- consider official X API mutation only with explicit user opt-in, opt-out,
  approval gates, rate limits, tests, docs, and runtime smoke evidence;
- keep unofficial browser automation and high-volume DM tools outside Main
  Branch-supported guidance unless a later decision accepts the risk explicitly.

## Eliminated Or Deferred

These are intentionally not v1 core dependencies:

- ManyChat as a core dependency. It may be a partner/add-on provider for
  Instagram experiments, but Main Branch should not depend on it.
- n8n, Make, Zapier, Pipedream, and Activepieces as default runtimes. Main
  Branch may emit recipes later, but the engine should not require them.
- X comment-to-DM execution.
- LinkedIn write automation.
- TikTok DM/comment write automation.
- YouTube DM automation.
- Browser-automation mass-DM tools as product guidance.
- Generic "growth bot" marketplaces.

## Next Steps

1. Land this decision so the research is not lost.
2. Smoke Postiz MCP/API scheduling separately.
3. Draft a playbook schema fixture under `pushes/` only after the decision and
   Postiz smoke clarify provider boundaries.
4. Open a follow-up research issue for X interaction-triggered resource
   delivery tools, with explicit policy/API verification as acceptance criteria.

## Sources

- X automation rules: https://help.x.com/articles/76915-automation-rules-and-best-practices
- X developer guidelines: https://docs.x.com/developer-guidelines
- Typefully API overview: https://support.typefully.com/en/articles/8718287-typefully-api
- ManyChat Quick Automations: https://help.manychat.com/hc/en-us/articles/16654065283100-Manychat-Quick-Automations
- Postiz MCP introduction: https://docs.postiz.com/mcp/introduction
