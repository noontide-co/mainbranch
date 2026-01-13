# Commands

Workflow commands that invoke multi-step processes.

## What Commands Are

Commands are slash-invokable workflows that chain together multiple actions. They're shortcuts for common sequences.

## Structure

```markdown
---
name: command-name
description: What this command does
---

# /command-name

## Purpose
[What this accomplishes]

## Steps
1. [First action]
2. [Second action]
3. [Output]

## Usage
```
/command-name [arguments]
```

## Example
[Concrete example with expected output]
```

## Planned Commands

| Command | Domain | Purpose |
|---------|--------|---------|
| /daily-pulse | Ops | Morning status check across tools |
| /ad-batch | Marketing | Generate full ad batch with copy + images |
| /weekly-review | Ops | Summarize week, plan next |

*Commands ship as they're built and tested.*
