---
name: skill-concept
tier: skill
calls: []
description: "Generate N concept variations of a site / asset on localhost in parallel, foreground subagents. Default 2. Operator picks one to publish. Used by /site as the concept-generation step."
---

# skill-concept

A composable skill for generating concept variations. /site calls this after the brief is locked, before the first publish.

## Inputs

- The locked brief (path provided in the user message)
- Reference URLs (taste anchors, not templates)
- Conversion endpoint config (`.mainbranch/conversion.json`)

## Outputs

- N localhost-runnable HTML variations, each in its own subdir of the project repo (e.g., `concepts/v1/`, `concepts/v2/`)
- A short comparison summary for the operator: hero artifact, palette, voice variant for each
- Operator picks one; that variation is promoted to the project root

## Flow

1. **Spawn N foreground subagents** (default 2). Each gets the same brief + reference URLs but is asked to make different decisions.
2. **Each subagent writes its variation.** Foreground only — background writes are known to silently fail.
3. **Validate** each variation: footer present, OG.svg under 1200×630, no AI tells in the copy.
4. **Render preview.** `python3 -m http.server` from each subdir; open in browser.
5. **Operator picks.** One concept → promoted to repo root; others archived under `concepts/`.

## Foreground rule

Subagents MUST be foreground. The known background-subagent file-write bug means files appear written but don't persist. Foreground only. See [`site/references/concept-variations.md`](../site/references/concept-variations.md) for the spawn pattern.

## Cross-references

- [site/references/concept-variations.md](../site/references/concept-variations.md)
- [site/references/minisite-generation-system.md](../site/references/minisite-generation-system.md)
