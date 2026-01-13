# Meta Platform Policy Lens

Review ad copy and visuals for Meta (Facebook/Instagram) automated enforcement triggers.

---

## Core Principle

**Meta's enforcement is algorithmic, not legal.** Even substantiated claims can be rejected if they trigger pattern-matching. Understanding the *mechanism* of triggers is essential.

---

## Personal Attributes Violation

Meta's most common rejection in coaching/health. Users should not feel the platform reveals their intimate data.

### The "You" Trigger

The word "You" + negative state/question = Personal Attributes flag.

| Violation | Why | Safe Pivot |
|-----------|-----|------------|
| "Are you struggling with debt?" | Asserts financial status | "Debt relief strategies for families" |
| "Stop letting anxiety control you" | Asserts mental health | "Overcoming anxiety: A guide" |
| "Tired of being fat?" | Asserts health/body | "I struggled with weight until..." |
| "Meet other Christian singles" | Asserts religion | "Meet Christian singles" |

**Pattern:** Shift from Second Person (You) to First Person (I), Third Person (They/Families), or Service focus.

---

## Unrealistic Outcomes

Algorithm flags high-promise claims regardless of substantiation.

### Blacklisted Phrases

- "Financial freedom"
- "Quit your job"
- "Laptop lifestyle"
- "Make 6-figures"
- "Lose 20 lbs in a week"
- "Work from home"
- "Passive income"
- "Easy money"
- "Quick cash"

### Visual Triggers

- Before/after images (banned for weight loss, restricted for others)
- Bank account screenshots with large numbers
- Dashboards with steep upward graphs

---

## Circumventing Systems (Death Sentence)

This violation leads to **permanent Business Manager ban**. Triggers when AI suspects deception.

### Common Triggers

| Trigger | Why | Avoidance |
|---------|-----|-----------|
| Link shorteners (bit.ly) | Looks like cloaking | Direct links only |
| Unicode obfuscation ("M@ke M0ney") | Demonstrates intent to evade | Standard text |
| Ad-to-page mismatch | Semantic inconsistency | Matching "scent" |
| Redirect chains | Looks like cloaking | Clean URL structure |

### False Positive Avoidance

- Link directly to domain, no complex redirects
- Ensure landing page content matches ad promises
- No fake UI elements (play buttons, download buttons)

---

## Checklist

| Check | Pass Example | Fail Example |
|-------|--------------|--------------|
| **Personal Attributes** | "Weight loss tips for women over 40" | "Are you over 40 struggling to lose weight?" |
| **Prohibited Keywords** | "Revenue growth," "Scale," "Optimization" | "Financial freedom," "Passive income" |
| **Before/After** | Lifestyle image of result state | Side-by-side transformation |
| **Link Integrity** | brand.com/offer | bit.ly → tracker → landing |
| **Text Obfuscation** | "Make Money" | "M@ke M0ney" |
| **Button Fakes** | Real video, static image | Fake play button on image |

---

## The "You" Workarounds

| Risky Pattern | Safe Alternative |
|---------------|-----------------|
| "Are you..." | "For those who..." |
| "Your [problem]" | "[Problem] is..." |
| "Do you have..." | "Many people experience..." |
| "Stop your..." | "Strategies for managing..." |

---

## Red Flags (Always Flag)

- Direct "you" + negative state combination
- Any blacklisted phrase in copy or image text
- Before/after visual structure
- Link shorteners or redirect chains
- Unicode characters in words
- Fake UI elements

---

## Severity

| Level | Criteria | Action |
|-------|----------|--------|
| **P1 - Blocks** | Circumventing systems triggers, fake UI | Cannot ship |
| **P2 - Fix** | Personal attributes, prohibited keywords | Rewrite before launch |
| **P3 - Note** | Could be flagged, borderline phrases | Monitor after launch |

---

*Source: Meta Ad Policies, Jon Loomer Digital, Reddit r/FacebookAds practitioner reports*
