# Local Video/Audio Transcription

When user has local media files to mine, use whisper.

---

## Prerequisites Check

User needs:
- whisper-cpp (via Homebrew)
- ffmpeg (via Homebrew)
- Base model downloaded (~142MB)

**Quick check:**
```bash
which whisper-cli ffmpeg
ls ~/.whisper/ggml-base.en.bin
```

If missing, see installation instructions below.

---

## With whisper-mcp (Preferred)

If user has whisper-mcp configured in `.mcp.json`:
- Use `transcribe_audio` tool directly
- Handles video-to-audio conversion automatically
- Returns transcript text

**Check for MCP:**
```bash
grep -q "whisper-mcp" ~/.mcp.json 2>/dev/null && echo "whisper-mcp configured"
```

---

## Without MCP (CLI Fallback)

1. Convert to 16kHz WAV:
   ```bash
   ffmpeg -i "video.mp4" -ar 16000 -ac 1 /tmp/audio.wav -y
   ```

2. Transcribe:
   ```bash
   whisper-cli --model ~/.whisper/ggml-base.en.bin --file /tmp/audio.wav --output-txt
   ```

3. Read output and synthesize into research file

---

## When to Use

Trigger phrases:
- "transcribe this video/audio"
- "I have a recording to mine"
- "transcribe my Loom"
- "process this voice memo"
- User drops a local `.mp4`, `.mov`, `.m4a`, `.wav`, `.mp3` file
- User mentions mining their own recordings

---

## Output

Save transcripts to:
- `research/YYYY-MM-DD-[topic]-transcript.txt` (raw)
- Or synthesize directly into `research/YYYY-MM-DD-[topic]-mining.md`

**Always synthesize.** Raw transcripts are rarely useful. Extract:
- Key insights and frameworks
- Quotable moments
- Messaging patterns
- Action items mentioned

---

## Installation Instructions

### Core Tools (Required)

```bash
# Install whisper-cpp and ffmpeg
brew install whisper-cpp ffmpeg

# Download base English model (142MB)
mkdir -p ~/.whisper
curl -o ~/.whisper/ggml-base.en.bin -L \
  'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin'

# Enable Metal acceleration (add to ~/.zshrc)
export GGML_METAL_PATH_RESOURCES="$(brew --prefix whisper-cpp)/share/whisper-cpp"
```

### Optional: whisper-mcp

For users who want Claude to transcribe directly via tool calls:

Add to `~/.mcp.json`:
```json
{
  "mcpServers": {
    "whisper-mcp": {
      "command": "npx",
      "args": ["-y", "whisper-mcp"]
    }
  }
}
```

Then restart Claude Code and run `/mcp` to verify tools are available.

---

## Model Options

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| base.en | 142MB | Fastest | Good | Most recordings |
| small.en | 466MB | Fast | Better | Heavy accents |
| medium.en | 1.5GB | Slower | Best | Technical jargon |

**Start with base.en.** Upgrade only if accuracy is insufficient.

---

## Performance

On Apple Silicon (M1/M2/M3):
- 18-minute video transcribed in ~26 seconds
- 5-12x realtime speed
- Runs completely offline

---

## Troubleshooting

**"Model not found"**
```bash
ls ~/.whisper/
# Should show ggml-base.en.bin
```

**"ffmpeg not found"**
```bash
brew install ffmpeg
```

**Slow transcription**
- Ensure Metal acceleration is enabled (see installation)
- Check model is loading from SSD, not external drive

**whisper-mcp not working**
- Restart Claude Code after adding to .mcp.json
- Run `/mcp` to check tool availability
- Verify whisper-cpp is installed first
