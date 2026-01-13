# Agents

Specialized AI agents for specific tasks.

## What Agents Are

Agents are focused personas Claude can adopt for specialized work. Each agent has:
- A specific domain expertise
- Defined behavior patterns
- Clear scope boundaries

## Structure

```markdown
---
name: agent-name
description: What this agent does and when to use it
---

# Agent Name

## Role
[What this agent is responsible for]

## Behavior
[How this agent approaches tasks]

## Scope
- Does: [list]
- Does not: [list]
```

## Planned Agents

| Agent | Domain | Purpose |
|-------|--------|---------|
| ad-reviewer | Marketing | Review ad performance, suggest iterations |
| content-strategist | Marketing | Plan content calendars, repurposing |
| ops-auditor | System Ops | Review workflows, find inefficiencies |

*Agents ship as they're built and tested.*
