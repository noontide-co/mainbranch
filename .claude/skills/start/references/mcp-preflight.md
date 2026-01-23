# MCP Pre-Flight Check

Verify required MCPs are installed before routing to skills that need them.

---

## Why This Matters

MCPs install to USER'S machine (`~/.claude.json`), not the repo. When someone clones their business repo on a new machine, MCPs won't be there.

---

## Check Flow

### 1. Read expected MCPs from config

```yaml
# From .vip/config.yaml
mcps:
  apify:
    required_for: [content]
    setup_guide: ".claude/skills/content/references/apify-setup.md"
  youtube-transcript:
    required_for: [content, think]
    setup_guide: null
```

### 2. Check if MCP tools are available

Look for tool presence:
- `mcp__apify__*` tools → Apify loaded
- `mcp__youtube-transcript__*` → YouTube transcript loaded

### 3. Prompt if missing

If routing to skill that needs missing MCP:

> "The content skill works best with Apify. Not set up on this machine.
>
> 1. Set up now (5 min, one-time)
> 2. Skip for now (some features limited)"

If user picks 1 → Show setup guide path, walk through it.

---

## When to Check

- **Always** when routing to skill that needs MCPs
- **Don't block** on optional MCPs — mention limitations
- **Remember** result for session (don't re-check)

---

## Config vs Installation

| What | Where | Portable? |
|------|-------|-----------|
| "What this business needs" | `.vip/config.yaml` | Yes (git) |
| "What this machine has" | `~/.claude.json` | No (local) |

Config documents requirements. Installation state is Claude Code's domain.
