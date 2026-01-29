#!/usr/bin/env bash
# detect-tools.sh — Probe research tools not yet tracked in .vip/config.yaml
# Called once per /think session. Results should be written back to config.yaml.

CONFIG=".vip/config.yaml"

if [ -f "$CONFIG" ]; then
  # Parse known tool statuses (simple grep — not a full yaml parser)
  APIFY_STATUS=$(grep -A1 "^  apify:" "$CONFIG" | grep "status:" | awk '{print $2}')
  GEMINI_STATUS=$(grep -A1 "^  gemini:" "$CONFIG" | grep "status:" | awk '{print $2}')
  GROK_STATUS=$(grep -A1 "^  grok:" "$CONFIG" | grep "status:" | awk '{print $2}')
  WHISPER_STATUS=$(grep -A1 "^  whisper:" "$CONFIG" | grep "status:" | awk '{print $2}')
else
  # No config — probe everything
  APIFY_STATUS="null"
  GEMINI_STATUS="null"
  GROK_STATUS="null"
  WHISPER_STATUS="null"
fi

echo "Research tools:"

# Only probe tools with unknown status
[ "$APIFY_STATUS" = "true" ] && echo "  ✓ Apify (YouTube, Instagram mining)"
[ "$APIFY_STATUS" = "null" ] && {
  ([ -n "$APIFY_TOKEN" ] || type mcp__apify__search-actors >/dev/null 2>&1) \
    && echo "  ✓ Apify (detected — updating config)" \
    || echo "  ✗ Apify (not found)"
}

[ "$GEMINI_STATUS" = "true" ] && echo "  ✓ Gemini (deep research)"
[ "$GEMINI_STATUS" = "null" ] && {
  [ -n "$GOOGLE_API_KEY" ] \
    && echo "  ✓ Gemini (detected — updating config)" \
    || echo "  ✗ Gemini (not found)"
}

[ "$GROK_STATUS" = "true" ] && echo "  ✓ Grok (X/Twitter sentiment via SDK)"
[ "$GROK_STATUS" = "null" ] && {
  # Source env file if key not in environment but file exists
  [ -z "$XAI_API_KEY" ] && [ -f "$HOME/.config/devon/env.sh" ] && source "$HOME/.config/devon/env.sh"
  ([ -n "$XAI_API_KEY" ] && python3 -c "import xai_sdk" 2>/dev/null) \
    && echo "  ✓ Grok (detected — updating config)" \
    || echo "  ✗ Grok (not found)"
}

[ "$WHISPER_STATUS" = "true" ] && echo "  ✓ whisper (local transcription)"
[ "$WHISPER_STATUS" = "null" ] && {
  which whisper-cli >/dev/null 2>&1 \
    && echo "  ✓ whisper (detected — updating config)" \
    || echo "  ✗ whisper (not found)"
}
