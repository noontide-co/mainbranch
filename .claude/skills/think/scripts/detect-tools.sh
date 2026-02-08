#!/usr/bin/env bash
# detect-tools.sh — DEPRECATED: Detection now happens inline in /think SKILL.md
#
# This script is kept for reference but detection logic has moved to the main skill.
# Why: Claude can detect tools AND update config in one step using Read/Edit tools.
# The bash script could only report — it couldn't reliably write YAML.
#
# New flow (in SKILL.md):
# 1. Read .vip/config.yaml
# 2. Check status values (true/false/null)
# 3. Probe unknowns using bash or tool presence checks
# 4. Update config with Edit tool (status + last_checked timestamp)
# 5. Report once based on user experience level
#
# See: .claude/skills/think/SKILL.md "Tool Detection (Config-First)" section

echo "NOTE: detect-tools.sh is deprecated. Tool detection now happens inline in /think."
echo "The skill reads config, probes unknowns, and updates config directly."
echo ""
echo "For manual checking, here's what tools exist on this machine:"
echo ""

# Source env file if it exists
[ -f "$HOME/.config/vip/env.sh" ] && source "$HOME/.config/vip/env.sh"

echo "Research tools:"

# Apify - MCP-based (can't reliably detect via bash, skill checks mcp__apify__* tools)
APIFY_STATUS="unknown (check MCP tool presence in Claude session)"
echo "  ? Apify — $APIFY_STATUS"

# Gemini - env var
if [ -n "$GOOGLE_API_KEY" ]; then
  GEMINI_STATUS="available"
  echo "  ✓ Gemini (GOOGLE_API_KEY set)"
else
  GEMINI_STATUS="unavailable"
  echo "  ✗ Gemini (GOOGLE_API_KEY not set)"
fi

# Grok - env var + SDK
if [ -n "$XAI_API_KEY" ] && python3 -c "import xai_sdk" 2>/dev/null; then
  GROK_STATUS="available"
  echo "  ✓ Grok (XAI_API_KEY + xai_sdk)"
elif [ -n "$XAI_API_KEY" ]; then
  GROK_STATUS="partial"
  echo "  ~ Grok (XAI_API_KEY set but xai_sdk package missing)"
else
  GROK_STATUS="unavailable"
  echo "  ✗ Grok (XAI_API_KEY not set)"
fi

# whisper - CLI (check mlx_whisper first, then whisper-cli)
if which mlx_whisper >/dev/null 2>&1; then
  WHISPER_STATUS="available"
  echo "  ✓ whisper (mlx_whisper found)"
elif which whisper-cli >/dev/null 2>&1; then
  WHISPER_STATUS="available"
  echo "  ✓ whisper (whisper-cli found)"
else
  WHISPER_STATUS="unavailable"
  echo "  ✗ whisper (no variant found — try: pip3 install mlx-whisper)"
fi

# Nano Banana - image generation (requires Gemini/GOOGLE_API_KEY)
if [ "$GEMINI_STATUS" = "available" ]; then
  NANOBANANA_STATUS="available"
  echo "  ✓ Nano Banana (GOOGLE_API_KEY set)"
else
  NANOBANANA_STATUS="unavailable"
  echo "  ✗ Nano Banana (needs GOOGLE_API_KEY)"
fi

echo ""
echo "Document tools:"

# markitdown
which markitdown >/dev/null 2>&1 \
  && echo "  ✓ markitdown" \
  || echo "  ✗ markitdown"

# pandoc
which pandoc >/dev/null 2>&1 \
  && echo "  ✓ pandoc" \
  || echo "  ✗ pandoc"

# marker
which marker_single >/dev/null 2>&1 \
  && echo "  ✓ marker (marker_single)" \
  || echo "  ✗ marker"

echo ""
echo "To update your config, edit .vip/config.yaml directly or let /think handle it."
