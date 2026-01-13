# Research

Point-in-time exploration and information gathering. Dated snapshots that inform decisions.

---

## When to Save Research

Save research when you:
- Run Gemini/Claude deep research
- Analyze competitors
- Gather audience insights
- Review testimonials for themes
- Explore new angles or strategies

## File Format

```yaml
---
type: research
date: 2026-01-13
source: gemini | claude | web | expert | internal
topics: [topic1, topic2]
linked_decisions:
  - 2026-01-13-decision-this-informed
status: complete
---
```

## Naming

`YYYY-MM-DD-slug.md`

Example: `2026-01-13-competitor-pricing-analysis.md`

## Linking to Decisions

When research informs a decision, add the decision ID to `linked_decisions` in frontmatter. This creates traceability: Research → Decision → Context.
