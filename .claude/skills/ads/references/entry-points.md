# Flexible Entry Points

Replace rigid 4-mode triage with intent detection. Users say what they want in natural language, the skill detects intent and routes internally.

---

## Why Flexible Entry Points

The old 4-mode triage (static / video / one-liners / review) forced users into boxes that didn't match how they actually work. Real workflows are messier:

- "I have images, just need copy" -- not a mode
- "Give me 5 variations of this" -- not a mode
- "What's working in my account?" -- not a mode
- "I shot a video, help me turn it into ads" -- spans multiple modes

The skill now detects INTENT and assembles the right pipeline from modular components.

---

## Entry Point Detection

### User-Says Table

| User Says | Intent | Components Assembled | Pipeboard? |
|-----------|--------|---------------------|------------|
| "I want ideas for an ad" | Ideation | Account check (if available) + research + concept generation | Read-only |
| "I'm repurposing a video" | Video Repurpose | Transcribe + extract hooks + copy variants | No |
| "I already have images, just need copy" | Copy Only | Skip image gen, primaries + headlines | No |
| "Just need images for existing copy" | Image Only | Nano Banana image gen only | No |
| "Full from scratch" | Full Pipeline | Copy + compliance + images (classic static flow) | Optional |
| "Check my ad performance" | Account Check | Pipeboard read-only -- insights, winners/losers | Required |
| "Give me 50 creative variations" | Hook Library | Bulk generation (flexible quantity) | No |
| "Give me 5 variations of this winning ad" | Performance Iteration | Pull winner + generate variants **(Phase 2 -- coming)** | Read-only |
| "Duplicate this ad set with new creative" | Duplicate + Swap | Clone + swap flow **(Phase 1.5 -- coming)** | Required |
| "Make me video scripts" | Video Scripts | Full video script pipeline | No |
| "Review my ads" / "compliance check" | Review | 6-lens compliance review | No |
| "What's working before we create?" | Pre-Gen Account Check | Account overview + creative audit | Required |

### Intent Detection Logic

```
1. Parse user message for trigger phrases
2. Check for explicit mode keywords first:
   - "review" / "compliance" / "audit" → Review
   - "video scripts" / "spoken word" → Video Scripts
   - "static ads" / "full from scratch" → Full Pipeline
3. Check for component-specific language:
   - "just copy" / "only copy" / "have images" → Copy Only
   - "just images" / "only images" / "have copy" → Image Only
   - "repurpose" / "transcribe" / "video I shot" → Video Repurpose
   - "variations" / "hook library" / "one-liners" / "creative variations" → Hook Library
4. Check for account-related language:
   - "performance" / "what's working" / "check account" / "CPA" / "ROAS" → Account Check
   - "duplicate" / "swap" / "push to account" → Duplicate + Swap (Phase 1.5)
5. Check for ideation language:
   - "ideas" / "brainstorm" / "concepts" / "what should I run" → Ideation
6. If unclear → ask: "What do you have and what do you need?"
```

### Backward Compatibility

Old mode names still work as explicit triggers:

| Old Trigger | Maps To |
|-------------|---------|
| "static ads" | Full Pipeline |
| "video scripts" | Video Scripts |
| "one-liners" | Hook Library (creative variations) |
| "review" | Review |

---

## Component Architecture

Each entry point assembles different components. Components are modular -- they can be combined in any order.

### Available Components

| Component | What It Does | Reference |
|-----------|-------------|-----------|
| **Pre-flight** | Score reference files, check readiness | [preflight-algorithm.md](preflight-algorithm.md) |
| **Account Check** | Pull live account data via Pipeboard | [pipeboard-integration.md](pipeboard-integration.md) |
| **Copy Engine** | Generate primaries, headlines, hooks | SKILL.md (Static Ads section) |
| **Hook Library** | Generate N creative variations (was "one-liners") | [one-liner-methodology.md](one-liner-methodology.md) |
| **Video Scripts** | Generate spoken-word scripts | [video-templates-hooks.md](video-templates-hooks.md) |
| **Image Gen** | Nano Banana image prompts + generation | [image-generation-workflow.md](image-generation-workflow.md) |
| **Compliance Review** | 6-lens review pipeline | [review-workflow.md](review-workflow.md) |
| **Post-Gen Pipeline** | Git commit + compliance + image gen | [post-generation-pipeline.md](post-generation-pipeline.md) |
| **Transcription** | Video/audio transcription (whisper or manual) | `/think` references |

### Component Composition by Entry Point

| Entry Point | Pre-flight | Account | Copy | Hooks | Video | Images | Review | Post-Gen |
|-------------|-----------|---------|------|-------|-------|--------|--------|----------|
| Full Pipeline | Yes | Optional | Yes | -- | -- | Yes | Auto | Yes |
| Copy Only | Yes | -- | Yes | -- | -- | -- | Auto | Yes |
| Image Only | Lite | -- | -- | -- | -- | Yes | -- | Yes |
| Hook Library | Yes | -- | -- | Yes | -- | Optional | Auto | Yes |
| Video Scripts | Yes | -- | -- | -- | Yes | -- | Auto | Yes |
| Video Repurpose | Yes | -- | Yes | -- | -- | Optional | Auto | Yes |
| Ideation | Lite | Optional | Concepts | -- | -- | -- | -- | -- |
| Account Check | -- | Yes | -- | -- | -- | -- | -- | -- |
| Review | -- | -- | -- | -- | -- | -- | Yes | -- |
| Duplicate + Swap | -- | Yes | Optional | -- | -- | Optional | -- | -- |

**Legend:** Yes = always included, Optional = if available/requested, Auto = runs automatically, Lite = abbreviated check, -- = not included

---

## Quantity Flexibility

The old system locked users into fixed batch sizes (30 one-liners, 5-6 concepts). The new system respects user intent:

| User Says | Quantity |
|-----------|---------|
| "Give me 5 variations" | 5 |
| "50 creative variations" | 50 |
| "A few hooks to test" | 5-10 (suggest range, confirm) |
| "Full batch" | Default (30 for hooks, 5-6 concepts for static) |
| No quantity specified | Ask: "How many do you want? A few to test (5-10) or a full batch (30+)?" |

---

## Routing Flow

```
User message arrives
│
├─ Pre-flight runs (Step 0 — always, unless pure Account Check)
│
├─ Detect intent (see detection logic above)
│
├─ If Pipeboard available AND relevant intent:
│   └─ "Want me to check what's working before we create?"
│       ├─ Yes → Account Check component runs first
│       └─ No → Skip, proceed to generation
│
├─ Assemble component pipeline for detected intent
│
├─ Execute pipeline:
│   ├─ Copy/Hooks/Video generation
│   ├─ Save output to outputs/
│   └─ Post-Gen Pipeline (auto: commit + compliance + images)
│
└─ If Pipeboard available AND write-capable (Phase 1.5):
    └─ "Want to push this to your ad account?"
        ├─ Yes → Duplicate + Swap flow
        └─ No → Done
```

---

## Campaign Naming

Campaign name is still required before saving output. The entry point doesn't change this -- all output paths include the campaign name:

```
outputs/YYYY-MM-DD-{type}-[offer]-{campaign}/
```

Where `{type}` maps from the entry point:
- Full Pipeline / Copy Only → `static-ads`
- Hook Library → `creative-variations` (was `one-liners`)
- Video Scripts → `video-ads`
- Video Repurpose → `video-repurpose`

---

## Error Handling

| Situation | What Happens |
|-----------|-------------|
| Intent unclear | Ask: "What do you have and what do you need?" |
| Pipeboard required but missing | "This needs ad account access. Set up Pipeboard? Or skip and work from reference only." |
| Pre-flight fails (thin reference) | Route to /think (same as current behavior) |
| User changes mind mid-pipeline | "No problem. What would you like instead?" Re-detect intent. |

---

## See Also

- [pipeboard-integration.md](pipeboard-integration.md) -- Account access details
- [one-liner-methodology.md](one-liner-methodology.md) -- Hook library methodology (Joel's cold-traffic work preserved)
- [preflight-algorithm.md](preflight-algorithm.md) -- Pre-flight scoring
