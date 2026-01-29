# Nano Banana Setup (Image Generation)

Google's Gemini-powered image generation for creating ad visuals and content images directly from Claude Code.

---

## What It Does

Nano Banana generates images from text prompts using Google's Gemini models. In Main Branch, this means:

- `/ads` can generate actual image creatives (not just text prompts)
- `/organic` can create social media visuals
- Any skill can request image generation when needed

---

## Prerequisites

- Google AI Studio API key (same as Gemini research — `GOOGLE_API_KEY`)
- If you already set up Gemini for `/think`, you're halfway done

---

## Setup (2 minutes)

### 1. Get API Key (skip if you have GOOGLE_API_KEY)

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the key

### 2. Add to Environment

Add to `~/.config/vip/env.sh` (created during `/setup` — see Step 4a in `setup/SKILL.md` for full env setup):

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

If you don't have `env.sh` yet, run `/setup` first or create it manually:

```bash
mkdir -p ~/.config/vip
echo 'export GOOGLE_API_KEY="your-key"' >> ~/.config/vip/env.sh
```

### 3. Add MCP Server

```bash
claude mcp add nano-banana --scope user -- npx nano-banana-mcp
```

### 4. Verify

Restart Claude Code (`/exit` then `claude`), then check:

```bash
/mcp
```

You should see `nano-banana` listed with available tools.

---

## Available MCP Servers

| Server | Install | Best For |
|--------|---------|----------|
| `nano-banana-mcp` (ConechoAI) | `npx nano-banana-mcp` | Simple, reliable |
| `nanobanana-mcp-server` (Python) | `uvx nanobanana-mcp-server@latest` | Python users |
| `nanobanana-mcp` (YCSE) | Most feature-rich | Session consistency, style persistence |

**Recommended:** `nano-banana-mcp` (ConechoAI) for simplicity.

---

## How Skills Use It

| Skill | How It Uses Image Gen |
|-------|----------------------|
| `/ads` | Generate actual ad creatives from image prompts (graphic, lo-fi, interrupt styles) |
| `/organic` | Create social media visuals for reels covers, carousel images, post graphics |
| `/think` | Generate concept visuals during research/ideation |

**Without Nano Banana:** Skills output text image prompts (descriptions of what the image should look like). You paste these into Midjourney, DALL-E, or another tool manually.

**With Nano Banana:** Skills can generate images directly. Text prompts become actual images.

---

## Pricing

Uses Google AI Studio credits (same as Gemini research):

| Model | Cost | Quality |
|-------|------|---------|
| `gemini-2.5-flash-image` (Nano Banana) | ~$0.02/image | Fast, good for drafts and iterations |
| `gemini-3-pro-image-preview` (Nano Banana Pro) | ~$0.05/image | Best quality, 4K, accurate text rendering |

**Imagen 4** (standalone text-to-image, no conversational editing):

| Model | Cost | Quality |
|-------|------|---------|
| Imagen 4 Fast | ~$0.02/image | Quick generation |
| Imagen 4 Standard | ~$0.04/image | Balanced |
| Imagen 4 Ultra | ~$0.06/image | Highest fidelity |

Free tier includes limited image generation. Paid credits scale to hundreds of images.

**Default:** Use `gemini-2.5-flash-image` for drafts, `gemini-3-pro-image-preview` for final creatives.

---

## Troubleshooting

**"MCP not found"** — Run `claude mcp add` command again. Make sure npx is available (`which npx`).

**"Invalid API key"** — Check `echo $GOOGLE_API_KEY`. Verify at [aistudio.google.com](https://aistudio.google.com).

**"Rate limited"** — Free tier has limits. Wait or upgrade to paid credits.

**Images have watermark** — All Nano Banana outputs include SynthID watermark (Google requirement). This is normal and expected.

---

## Resources

- Google AI Studio: https://aistudio.google.com/apikey
- Gemini Image Gen Docs: https://ai.google.dev/gemini-api/docs/image-generation
- ConechoAI MCP: https://github.com/ConechoAI/Nano-Banana-MCP
