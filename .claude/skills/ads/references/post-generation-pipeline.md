# Automatic Post-Generation Pipeline

**Every generation mode (Static, One-Liner, Video) runs this pipeline automatically after saving output.** Do not ask the user whether to run compliance review -- it is automatic.

## Step 1: Git Commit Pre-Review

```bash
git add outputs/YYYY-MM-DD-*
git commit -m "[output] {type} batch pre-review"
```

This preserves the original before any fixes. The user can always `git diff HEAD~1` to see what changed.

## Step 2: Select Lens Tier

| Output Type | Tier | Lenses |
|-------------|------|--------|
| One-liners (text only) | Copy Review | FTC, Meta Policy, Copy Quality, Voice Auth, Substantiation (5) |
| Video scripts (spoken word) | Copy Review | FTC, Meta Policy, Copy Quality, Voice Auth, Substantiation (5) |
| Static ads (copy + image prompts) | Full Review | All 5 above + Visual Standards (6) |

Visual Standards evaluates image prompt composition and safe zones -- skip it for text-only outputs.

## Step 3: Check Nano Banana Availability

If Nano Banana was detected at Step 0d AND the mode produces images (Static or One-Liner):

1. Calculate cost estimate:
   - **Static ads:** N angles x 3 styles x ~$0.05/image
   - **One-liners:** 8 background clusters x ~$0.05/image = ~$0.40
2. Ask ONE question: "Compliance review will run automatically. Also generate images? Est. cost: ~$X for N images. (y/n)"
3. If yes -> include image gen agent in the parallel spawn
4. If no -> skip image gen, run compliance only
5. If Nano Banana unavailable -> skip image gen silently, compliance runs alone

**Video scripts:** No image generation. Skip this step.

## Step 4: Spawn Parallel Agents (Single Message)

Spawn ALL agents in a single message for parallel execution. Use `subagent_type: "general-purpose"` for all agents.

**Compliance agents (read-only pattern -- zero persistence risk):**

Each compliance agent receives:
- **Ad content inline** (pass the full batch file content in the prompt -- do NOT just give a file path)
- **Lens file path** (agent reads its assigned lens from `.claude/lenses/`)
- **Business context** (only what that lens needs):
  - FTC: offer.md, testimonials.md, typicality.md
  - Meta Policy: offer.md
  - Copy Quality: offer.md, audience.md, skool-surfaces.md (if exists)
  - Voice Auth: voice.md
  - Substantiation: offer.md, testimonials.md, typicality.md
  - Visual Standards: (no extra context needed -- evaluates image prompts)

Each agent prompt must include:
```
Evaluate every ad/one-liner/script against the lens checklist.
For each issue, return:
  - severity: P1 | P2 | P3
  - item_ref: which ad/line
  - issue: what's wrong
  - evidence: exact text that violates
  - rule: which check this violates
  - fix: specific rewrite
Return "NO ISSUES" explicitly if everything passes.
Do NOT write any files. Do NOT fix anything. Report only.
```

**Image generation agents (write-with-fallback pattern -- if user approved):**

Spawn ONE subagent PER IMAGE (or per 2-3 images if generating 15+). All image agents launch in the SAME message as compliance agents.

Each agent receives its prompt(s), visual-style.md context, output path, and target filenames. Agents generate via Python SDK, post-process, verify on disk, and return path + status + cost.

**IMPORTANT:** Main conversation writes `prompts.json` to disk BEFORE spawning agents (Python file I/O -- not affected by Write tool durability bug). Failed images get retried with a fresh single-image agent.

See [image-generation-workflow.md](image-generation-workflow.md) -> "Parallel Agent Spawning" for batching strategy, rate limiting, agent prompt template, and failure handling.

## Step 5: Synthesize Results

When all agents return:

1. **Compliance synthesis:**
   - Collect all lens findings
   - Deduplicate (FTC and Substantiation may flag same issue)
   - Build unified P1/P2/P3 report
   - **Auto-apply P2/P3 fixes** to the batch file using Edit tool
   - **P1 issues:** Surface to user for decision. Do NOT auto-fix. Mark status as BLOCKED.

2. **Image synthesis (if applicable):**
   - Collect results from all image agents, retry any failures, write `image-index.md`

3. **Write `review-log.md`** documenting all compliance changes

## Step 6: Present Unified Report

```
Pipeline complete:
  Review: [STATUS] (P1: N, P2: N fixed, P3: N noted)
  Images: [N generated / N/A]
  Cost: [$X / N/A]

  [If P1 exists: show blocking issues with suggested fixes]
  [If P2 applied: show summary of auto-fixes]

  Files:
    outputs/YYYY-MM-DD-{type}-{campaign}/
    |- {batch-file}.md (copy, reviewed)
    |- review-log.md
    [|- image-index.md]
    [|- images/ (N files)]

  Commit reviewed copy [+ images]? (y/n)
```

## Step 7: Git Commit Post-Review

If user approves:

```bash
git add outputs/YYYY-MM-DD-*
git commit -m "[review] {type} batch - N fixes applied"
```

## Pipeline Timing

Compliance review (5-6 agents, read-only) typically completes in 30-60 seconds.
Image generation (parallel agents, one per image) typically completes in 30-90 seconds for 15 images.
All agents -- compliance + image -- run in parallel, so total time = max(slowest compliance agent, slowest image agent).

## One-Liner Image Generation Details

One-liners use **Template 4 (background-only)** from [image-prompt-templates.md](image-prompt-templates.md).

After 30 one-liners are generated, cluster them by hook category:

| Cluster | Scene Type | Approx Lines |
|---------|-----------|--------------|
| Problem agitation | Dark, moody atmospheric | 4-6 |
| Emotional state | Warm, intimate | 3-5 |
| Transformation | Aspirational, bright lifestyle | 4-6 |
| Contrarian | Bold, stark, max contrast | 3-5 |
| Identity callout | Person-centered, relatable | 3-5 |
| Social proof | Clean, authoritative abstract | 2-4 |
| Curiosity/reframe | Two-tone, conceptual | 2-4 |
| Overflow | Versatile, brand-forward | 2-3 |

Generate 1 background per cluster (8 total) using **parallel subagents -- one agent per cluster**. Each agent generates its background, post-processes it, and returns the path + status. All 8 agents spawn in the same message as compliance agents. Map each one-liner to its cluster. Text overlay composited via Pillow post-processing (separate from Gemini generation).

**Cost:** 8 images x ~$0.05 = ~$0.40 (recommended). User can choose 15 backgrounds ($0.75) or 30 unique ($1.50). At 15+, batch agents into groups of 2-3 images each to limit agent count.

See [image-generation-workflow.md](image-generation-workflow.md) for Nano Banana integration details.
