# Minisite Research

Load this for step 1 of the minisite flow.

## Goal

Research answers the questions the brief needs before site copy or structure is drafted. It also persists those answers so the next session can recover after compaction.

## Run Research In Parallel

Spawn parallel research subagents in the foreground. See [`../SKILL.md`](../SKILL.md) for the foreground-only rule.

Typical research questions:

- What do this offer's customers actually say? Mine interviews, reviews, community posts, approved notes, or other safe source material.
- What competitor framing is common in this offer category?
- What proof is available: testimonials with permission, outcome data, founder credentials, demos, screenshots?
- Which conversion endpoint fits this offer: payment, lead form, appointment booking, or custom webhook?

## Persist Findings

Each subagent records findings to a dated research file in the business repo:

```text
research/YYYY-MM-DD-<slug>-claude-code.md
```

Use the `/mb-think` research frontmatter pattern:

```yaml
---
type: research
date: YYYY-MM-DD
source: claude-code
topics: [audience-mining, competitor-framing, proof-inventory]
linked_decisions: []
status: complete
---
```

Keep private raw customer/member data, credentials, and unapproved account exports out of public repos. Summarize safely or keep raw material outside the repo when it is not public-safe.

For broad site or launch research, prefer the `/mb-think --brief-format=grok-8`
shape. It covers business/offering, ICP, customer journey, competitive
landscape, brand story, technical requirements, content/assets, and
metrics/constraints before the brief is drafted.

## Exit Criteria

Research is ready to feed the brief when:

- audience language has concrete phrases or objections;
- competitor framing is summarized without copying a competitor's site;
- proof has been inventoried with approval status;
- the likely conversion endpoint kind is named, even if the URL is not wired yet.

Then load [`minisite-brief.md`](minisite-brief.md).
