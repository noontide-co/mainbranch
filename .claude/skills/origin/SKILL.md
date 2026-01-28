---
name: origin
description: "Extract founder origin story using Hero's Journey framework. Creates origin.md (full backstory), distills to soul.md (reconnection fuel), generates social bios. Use when: (1) User has no soul.md or origin.md (2) User says 'origin', 'my story', 'who am I', 'why I do this' (3) User wants to create social bios (4) User feels disconnected and needs to reconnect."
---

# Origin

Extract your origin story. Create reconnection fuel. Generate bios.

---

## Why This Matters

Most founders can't articulate why they do what they do. They have skills, offers, audiences — but no story that connects it all.

The Hero's Journey framework surfaces your story through narrative, not interrogation. Values emerge from the journey. You don't answer "what are your values?" — you tell your story and the values reveal themselves.

**Two outputs:**
- `origin.md` — Full backstory (how you got here)
- `soul.md` — Condensed reconnection fuel (5-min read when drifting)

---

## Modes

Detect mode from user intent:

| User Says | Mode | Duration |
|-----------|------|----------|
| "origin", "my story", "who am I" | Discovery | 15-20 min |
| "add to my story", "new chapter" | Deepen | 5-10 min |
| "feeling disconnected", "why am I doing this" | Reconnect | 5 min |
| "create soul.md", "distill" | Distill | 5 min |
| "bio", "social bio", "X bio", "LinkedIn" | Bio | 2-3 min |

---

## Discovery Mode (Default)

Full Hero's Journey interview for first-time setup.

### Pre-Check

```bash
# Check if origin.md exists
if [ -f "reference/core/origin.md" ]; then
  echo "origin.md exists"
else
  echo "No origin.md - run discovery"
fi
```

If origin.md exists, ask: "You already have an origin story. Want to deepen it, reconnect with it, or start fresh?"

### The Interview

Run through 6 stages. Ask one question at a time. Wait for response. Follow up naturally.

**STAGE 1: ORDINARY WORLD**
> "What was your life like before this? Tell me about your professional background."

Follow-ups:
- "What did [X years in Y] teach you that most people don't know?"
- "What were you good at? What drained you?"

**STAGE 1b: PAINS & DESIRES**
> "What was wrong with the old way? What frustrated you most?"

Follow-ups:
- "What did you wish existed?" (desires - the pull)
- "What pushed you to finally do something about it?" (pains - the push)

**STAGE 2: CALL TO ADVENTURE**
> "What was the moment that changed everything?"

Follow-ups:
- "When did you first think 'someone should fix this'?"
- Keep asking "why" until you hit a core value (5 Whys technique)

If no clear moment: "Not everyone has a dramatic epiphany. Was it more of a gradual recognition?"

**STAGE 3: REFUSAL OF THE CALL**
> "What almost stopped you? What were you afraid of?"

Follow-ups:
- "Why didn't you start sooner?"
- "What voice in your head said 'this won't work'?"

**STAGE 4: CROSSING THE THRESHOLD**
> "What was the moment you actually committed?"

Follow-ups:
- "What did you have to give up or risk?"
- "Who or what gave you the push?"

**STAGE 5: ROAD OF TRIALS**
> "What was harder than you expected? Who helped you along the way?"

Follow-ups:
- "Tell me about a moment that reminded you why you do this." (trench story)
- "What almost made you quit?"

Collect 2-3 trench stories here.

**STAGE 6: RETURN WITH ELIXIR**
> "What do you know now that you wish you knew then?"

Follow-ups:
- "What would you never compromise on, even for money?"
- "If this works, what does your life look like?"

### Output

Generate `reference/core/origin.md` using template. See [templates/origin-template.md](templates/origin-template.md).

After saving, ask: "Want me to distill this into soul.md (5-min reconnection fuel)?"

---

## Deepen Mode

Add new chapters to existing origin.md.

```
/origin deepen
```

### Questions

- "What's happened since you wrote your origin story?"
- "Any new trench stories? Moments that reminded you why you do this?"
- "Has your vision evolved? What does success look like now?"
- "Any new wisdom? Things you've learned recently?"

### Output

Append to existing origin.md sections. Update soul.md if it exists.

---

## Reconnect Mode

Quick re-read when feeling disconnected.

```
/origin reconnect
```

### Flow

1. Read soul.md aloud (display it)
2. Ask one reflective question:
   - "Does this still feel true?"
   - "What's changed since you wrote this?"
   - "What would you add now?"
3. Offer to update if anything feels stale

---

## Distill Mode

Create soul.md from origin.md.

```
/origin distill
```

### Pre-Check

```bash
if [ ! -f "reference/core/origin.md" ]; then
  echo "No origin.md found. Run /origin first to create your origin story."
  exit 1
fi
```

### Extraction

Pull from origin.md:
- **The Spark** → "Why I do this"
- **Trench stories** from Road of Trials
- **The Test** (3 questions from philosophy)
- **Values** condensed
- **Vision** summary

### Output

Generate `reference/core/soul.md` using template. See [templates/soul-template.md](templates/soul-template.md).

---

## Bio Mode

Generate social media bios from origin.md.

```
/origin bio
/origin bio X
/origin bio LinkedIn
```

### Pre-Check

```bash
if [ ! -f "reference/core/origin.md" ]; then
  echo "No origin.md found. Run /origin first to create your origin story."
  exit 1
fi
```

### Output Format

Generate bios in 3 lengths for each platform:

**X/Twitter (160 char max):**
```
Short: [Role] + [Unique angle] + [Current focus]
```

**LinkedIn (300 char):**
```
Medium: [Background] + [What I do now] + [Why it matters]
```

**Skool / Full (paragraph):**
```
Full: [Origin hook] + [Journey summary] + [Current mission] + [What I bring]
```

### Pulls From origin.md

- The Before → Background/credentials
- The Wisdom → Unique angle
- The Leap → Current focus
- The Vision → Why it matters

See [templates/bio-template.md](templates/bio-template.md).

---

## Handling Resistance

Some users resist introspection. Strategies:

| Resistance | Response |
|------------|----------|
| "This feels too woo" | Start with facts (background, profession) — safe territory |
| "My story isn't interesting" | "You don't need drama. You need clarity." |
| "Just want to get to work" | "5 minutes now saves hours of generic output later." |
| "I don't know" | Use frustration: "What pisses you off about your industry?" |
| "Can we skip this?" | "We can do quick version now, deepen later." |

**Key insight:** Resistance usually means wrong framing, not no story. "Tell me your story" beats "What are your values?"

---

## Output Locations

All files save to user's business repo:

```
your-repo/
├── reference/
│   └── core/
│       ├── origin.md    <- Full backstory
│       └── soul.md      <- Reconnection fuel
```

---

## References

- [references/hero-journey.md](references/hero-journey.md) — 6-stage framework details
- [references/question-bank.md](references/question-bank.md) — All questions with follow-ups
- [references/examples/origin-example.md](references/examples/origin-example.md) — Sample output

## Templates

- [templates/origin-template.md](templates/origin-template.md)
- [templates/soul-template.md](templates/soul-template.md)
- [templates/bio-template.md](templates/bio-template.md)
