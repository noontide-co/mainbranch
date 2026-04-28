# Anti-Patterns — What NOT to Bake Into Minisite Generation

Lessons from prior failed prompt attempts. Each pattern below was tried, produced bad output, and is now explicitly avoided. The minisite generation system prompt (`minisite-generation-system.md`) is shaped around these.

## 1. Over-prescription

**Pattern:** The prompt specifies typography (`font-family: Inter, sans-serif`), exact hex colors (`#0a0a0a` background, `#fafafa` text, `#3b82f6` CTA), section structure (`hero → 3-up features → testimonial carousel → pricing table → CTA`), spacing scale, even shadow values.

**Result:** Every output looks like every other output. The LLM has nothing to decide; it slot-fills. The minisite becomes indistinguishable from a generic SaaS template, regardless of offer.

**Fix in `minisite-generation-system.md`:** Specify structural constraints (~4–6 pages, SEO, footer, mobile-first, perf budget). Leave aesthetic decisions — palette, typography, section order, hero artifact — to the LLM with reference URLs as taste signal.

## 2. Hex-locked color critique

**Pattern:** Reviewing a generated minisite, telling the LLM "the CTA needs to be `#10b981` and the heading should be `#0f172a` not `#1e293b`."

**Result:** The LLM stops making aesthetic judgments. Future runs default to "ask the operator for hex codes." The agent loses the ability to pick a palette that fits the offer's voice.

**Fix:** Critique by describing the *quality* you want ("the CTA needs more grounded weight; right now it floats"), not the value. Let the LLM translate quality → hex.

## 3. "Make it look like Howdy"

**Pattern:** Pointing at a successful minisite and saying "make this offer's minisite look like that."

**Result:** Surface-copying. The LLM lifts colors, layouts, fonts. The new minisite reads as derivative — and worse, it doesn't fit the new offer's tone (a billing tool's minisite shouldn't feel like a spiritual coach's).

**Fix:** Reference URLs are **polish anchors**, not templates. The system prompt explicitly says: "read them for polish level, not structure to copy." The user message frames them as "here's the level of intentionality we want; now design something fresh that fits **this** offer."

## 4. Templated placeholder tokens (`{BRAND_NAME}`, `{HERO_HEADLINE}`)

**Pattern:** Defining a template repo with placeholder tokens and instructing the LLM to fill them in.

**Result:** The LLM operates as a mail-merge engine. Output structure is locked to whatever the template authors imagined. Aesthetic invention is impossible — the template predetermined every section, every copy slot, every interactive element.

**Fix:** No template repo. `/site` ships zero source files for the LLM to inherit from. The LLM generates fresh HTML/CSS/SVG per offer, with reference URLs as taste anchors only. If two runs on the same offer produce identical output, generation is broken.

## 5. Over-enumerating "available sections"

**Pattern:** "Choose from these section types: hero-left-image, hero-right-image, three-up-grid, four-up-grid, testimonial-quote-block, testimonial-carousel, pricing-table-3-tier, faq-accordion, cta-banner..."

**Result:** The LLM picks from a menu instead of inventing. The minisite reads as assembled rather than designed. Same problem as #1 (over-prescription) but applied at the section level.

**Fix:** The system prompt names the mandatory pages (home + how-it-works) and a few decision points (which 2–4 supporting pages this offer needs, what the hero artifact should be). It does not enumerate component types. The LLM decides what each page contains.

## 6. Building in fallbacks for "if the LLM gets confused"

**Pattern:** "If you're not sure what to do for the hero, default to a centered headline with a CTA button below."

**Result:** The LLM uses the fallback every time, because it's the safe option. The "default" becomes the actual.

**Fix:** No fallbacks. If the LLM doesn't have enough to make a confident aesthetic choice, the prompt sends it to look at reference URLs and the offer's voice. The output should be a confident decision, not a hedged middle.

## 7. Suppressing variance ("be consistent across runs")

**Pattern:** "Make sure that if I run this twice, I get similar output."

**Result:** The LLM clamps to the safe default. Variance is the feature — different runs produce visually distinct output that all fit the offer. Generation is supposed to surprise.

**Fix:** The system prompt explicitly tests for variance: *"If two runs on the same offer produce visually identical output, you've been too conservative."* The skill's acceptance criteria include "running --one-shot twice on the same spec produces visually different output."

---

## How to write a critique that doesn't break generation

When you don't like a generated minisite:

- **Describe the quality, not the value.** "The hero feels too cold for an emotional offer" → not → "change `#0a0a0a` to `#1c1917`."
- **Name the missing thing, not the present thing.** "There's no signature visual; the hero is just text" → not → "remove the gradient."
- **Ask for a different decision, not a different parameter.** "Pick a different hero artifact — a receipt, not a stamp" → not → "change `<svg viewBox='0 0 100 100'>` to `<svg viewBox='0 0 200 200'>`."
- **Re-run before iterating.** Sometimes the first generation is conservative. A re-run often produces a sharper take. Iterate by re-running, not by directing.

Generation only works when the LLM is making aesthetic decisions. Every constraint we add is a decision we're taking away. Add only the structural ones (file presence, footer, perf, SEO, OG dimensions) — leave the rest open.
