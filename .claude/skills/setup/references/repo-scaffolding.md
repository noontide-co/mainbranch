# Repo Scaffolding Reference

Detailed instructions for creating the business repo's configuration files, environment setup, and gitignore.

## API Key Environment (Progressive Setup)

Create the env.sh template for optional research tools. This lives outside git repos for security.

```bash
mkdir -p ~/.config/vip
cat > ~/.config/vip/env.sh << 'EOF'
# Main Branch API Keys
# This file is sourced by your shell. Keep it outside git repos.

# === OPTIONAL RESEARCH TOOLS ===
# These unlock additional capabilities. Add as needed.

# Gemini - Deep web research + Nano Banana image generation (free tier available)
# Get from: https://aistudio.google.com/apikey
# export GOOGLE_API_KEY=""

# xAI/Grok - X/Twitter sentiment analysis
# Get from: https://console.x.ai
# export XAI_API_KEY=""
EOF
```

Add source line to shell config (detects zsh vs bash):

```bash
# Detect shell and add source line
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ]; then
  grep -q 'source.*vip/env.sh' ~/.zshrc 2>/dev/null || \
    echo '[ -f "$HOME/.config/vip/env.sh" ] && source "$HOME/.config/vip/env.sh"' >> ~/.zshrc
else
  grep -q 'source.*vip/env.sh' ~/.bashrc 2>/dev/null || \
    echo '[ -f "$HOME/.config/vip/env.sh" ] && source "$HOME/.config/vip/env.sh"' >> ~/.bashrc
fi
```

**Explain to user:**
> "Created `~/.config/vip/env.sh` for API keys. It's outside git repos (security) and sourced on shell startup.
>
> You don't need keys now -- Apify handles most research. Add Gemini/Grok later if you want deep research capabilities."

**Progressive disclosure:** Don't overwhelm beginners with API setup. The env.sh exists but stays empty until they need it.

## Create Initial Config

Create `.vip/config.yaml` with team/business settings:

```yaml
# .vip/config.yaml
# VIP configuration for this business
# Git-tracked, shared by all collaborators
# NOTE: User identity (name, experience) is in ~/.config/vip/local.yaml

version: 1

# === SESSION (Team Defaults) ===
session:
  auto_load_reference: true
  show_context_tips: true  # Context management tips for beginners
  warn_at_context_pct: 75

# === INFRASTRUCTURE ===
# Populated when services are connected
infrastructure:
  railway:
    project_id: null
  postiz:
    api_url: null
    api_key_ref: null  # keychain:vip/postiz or env:POSTIZ_API_KEY
  r2:
    bucket: null
    public_url: null

# === MCP SERVERS ===
# Track which MCPs this business needs
# /start verifies these are installed, prompts setup if missing
mcps:
  apify:
    required_for: [organic, think]  # Handles web scraping AND YouTube transcripts
    setup_guide: ".claude/skills/organic/references/apify-setup.md"

# === CONTENT ===
content:
  default_channels: []
  require_review: true

# === SKILL PREFERENCES ===
skills:
  ads:
    default_format: static
  think:
    auto_create_tasks: false
```

## Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Secrets
.env
*.env.local

# Machine-local settings (absolute paths, not shared)
.claude/settings.local.json

# Session state (not shared between machines)
.vip/local.yaml

# OS
.DS_Store

# Editor
.vscode/
.idea/
EOF
```

**Why `.claude/settings.local.json` is git-ignored:** Claude Code auto-ignores this file, but we add it explicitly for safety. It contains machine-specific absolute paths to vip (`additionalDirectories`) that differ per computer.

**Why `.vip/local.yaml` is git-ignored:** It stores session state like `current_offer` -- which offer you're working on right now. This is per-machine, per-session. The git-tracked `.vip/config.yaml` holds team/business settings that should be shared.
