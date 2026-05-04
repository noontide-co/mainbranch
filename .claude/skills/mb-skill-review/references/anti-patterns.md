# Anti-Patterns — What NOT to Bake Into Site Copy or Generation

Two categories: (1) the **AI-tell list** (verbatim from Haines's seo-audit / ai-writing-detection — gates copy at review time), and (2) the **generation anti-patterns** (lessons from prior failed prompt attempts — shape the generation system prompt).

The De-AI'd review gate hard-fails any draft that violates the AI-tell list.

---

## Part 1 — AI-tell list (gates copy at review)

### Em-dash rule (primary AI tell)

Em-dash is the primary AI tell. Replace with commas, colons, or parentheses. **More than 1 em-dash per page = revise.**

### Overused verbs (cut or replace)

delve, leverage, optimize, utilize, facilitate, foster, bolster, underscore, unveil, navigate, streamline, enhance.

### Overused adjectives (cut or replace)

robust, comprehensive, pivotal, crucial, vital, transformative, cutting-edge, groundbreaking, innovative, seamless, intricate, nuanced, multifaceted, holistic.

### AI-flag opening phrases (banned)

- "In today's fast-paced world,"
- "In the realm of,"
- "It's important to note,"
- "Let's delve into,"
- "Imagine a world where."

### AI-flag transitional phrases (banned)

- "That being said,"
- "With that in mind,"
- "It's worth mentioning,"
- "At its core,"
- "To put it simply,"
- "In essence,"
- "This begs the question."

### AI-flag concluding phrases (banned)

- "In conclusion,"
- "To sum up,"
- "By [doing X], you can [achieve Y],"
- "At the end of the day."

### AI-flag structural patterns (banned)

- "Whether you're a [X], [Y], or [Z]…"
- "It's not just [X], it's also [Y]…"
- Sentences starting with "By [gerund]…"

### Plain English alternatives

| Cut | Use |
|---|---|
| Utilize | Use |
| Implement | Set up |
| Leverage | Use |
| Facilitate | Help |
| Innovative | New |
| Robust | Strong |
| Seamless | Smooth |
| Cutting-edge | New / Modern |

### Cut these words (almost always)

very, really, extremely, incredibly, just, actually, basically, in order to, that, things, stuff.

### Hard-fail rules for the De-AI'd gate

The gate fails if ANY of:

- More than 1 em-dash on the page
- Any banned opening / transitional / concluding / structural phrase
- 3+ overused verbs OR 3+ overused adjectives in a single page
- Any "Plain English alternatives" word in headline / hero copy

Operator may proceed past failure with `--ignore-ai-tells`; the override is logged in the brief frontmatter.

---

## Part 2 — Generation anti-patterns (shape the system prompt)

### 1. Over-prescription

**Pattern:** Specifying typography, exact hex, section structure, spacing, even shadow values.

**Result:** Every output looks like every other output. The LLM has nothing to decide; it slot-fills.

**Fix:** Specify structural constraints (~4-6 pages, SEO, footer, mobile-first, perf budget). Leave aesthetic decisions to the LLM with reference URLs as taste signal.

### 2. Hex-locked color critique

**Pattern:** Telling the LLM "the CTA needs to be `#10b981`."

**Result:** The LLM stops making aesthetic judgments.

**Fix:** Critique by describing the *quality* you want ("the CTA needs more grounded weight"), not the value.

### 3. "Make it look like Howdy"

**Pattern:** Pointing at a successful site and saying "make this look like that."

**Result:** Surface-copying. Derivative output.

**Fix:** Reference URLs are **polish anchors**, not templates.

### 4. Templated placeholder tokens (`{BRAND_NAME}`)

**Pattern:** Defining a template repo with placeholders.

**Result:** Mail-merge engine. Aesthetic invention impossible.

**Fix:** No template repo. Generate fresh HTML/CSS/SVG per offer.

### 5. Over-enumerating "available sections"

**Pattern:** "Choose from these section types: hero-left-image, hero-right-image, ..."

**Result:** Picks from a menu instead of inventing.

**Fix:** Name the mandatory pages and a few decision points. Don't enumerate component types.

### 6. Building in fallbacks for "if the LLM gets confused"

**Pattern:** "If you're not sure, default to a centered headline with a CTA below."

**Result:** The LLM uses the fallback every time.

**Fix:** No fallbacks. Send the LLM to the reference URLs and the offer's voice.

### 7. Suppressing variance

**Pattern:** "Make sure two runs produce similar output."

**Result:** Clamps to the safe default. Variance is the feature.

**Fix:** Test for variance. Two runs on the same offer should produce visually distinct output that both fit the offer.

### 8. AI for product UI screenshots

**Pattern:** Asking the LLM to generate UI screenshots of the product.

**Result:** Hallucinated UI. AI cannot draw the product correctly. Trust dies.

**Fix:** Always capture real screenshots. Frame in browser/device mockups. Annotate with code overlays.

---

## Critique that doesn't break generation

When you don't like a generated site:

- **Describe the quality, not the value.** "The hero feels too cold for an emotional offer" → not → "change `#0a0a0a` to `#1c1917`."
- **Name the missing thing, not the present thing.** "There's no signature visual" → not → "remove the gradient."
- **Ask for a different decision, not a different parameter.** "Pick a different hero artifact — a receipt, not a stamp."
- **Re-run before iterating.** First generation is often conservative; re-run before directing.

Generation only works when the LLM is making aesthetic decisions. Every constraint we add is a decision we're taking away.
