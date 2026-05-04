# Deep Research to Wiki Format

How to convert Gemini/GPT deep research into wiki-ready format with lead magnet structure.

---

## Two-File Pattern

Every deep research becomes **two files**:

| File | Location | Purpose | Length |
|------|----------|---------|--------|
| **Summary note** | `src/content/notes/` | Tripwire — discoverable entry point | ~200-400 words |
| **Full research** | `src/content/research/` | Comprehensive analysis | 500-2000+ lines |

**Why two files:**
- Summary is discoverable via search and WikiLinks
- Full research is linked from summary
- Readers get hooked by summary, click through to depth
- Each deep research session becomes a lead magnet

---

## Summary Note (Tripwire)

The summary lives in `notes/` so it appears in normal wiki navigation.

### Frontmatter

```yaml
---
title: "Research: [Topic Title]"
created: 2026-01-21
visibility: public
status: live
type: research-summary
summary: "Key takeaways from research on [topic]..."
tags: [research, topic-specific-tag]
---
```

### Content Structure

1. **Hook** — Why this matters (1-2 sentences)
2. **Key Findings** — 5-6 bullet points or short paragraphs
3. **Implications** — What this means for the reader
4. **Full Research Link** — Pointer to comprehensive doc

### Example Summary

```markdown
---
title: "Research: Creator Platform Pricing 2024-2025"
created: 2026-01-21
visibility: public
status: live
type: research-summary
summary: "Sentiment analysis of how creators price their offerings in 2024-2025."
tags: [research, pricing, creator-economy]
---

The creator economy is repricing. After years of race-to-bottom free content,
creators are discovering that [[Subscription unlocks depth into the mind]] —
people pay for access to thinking, not just content.

## Key Findings

- **$5-15/month** is the new normal for community access
- **Premium tiers ($50-100+)** work when they include direct access
- Freemium with depth-gating outperforms hard paywalls
- [[Three panes deep then you pay]] is an emerging pattern

## Implications

If you're building a public wiki, the research suggests:
1. Free access to surface-level content
2. Subscription for deep exploration
3. Premium tier for direct engagement

## Full Research

[[Creator Platform Pricing Research 2024-2025]] — comprehensive 8,400-word analysis
```

---

## Full Research File

Lives in `src/content/research/` for organization.

### Frontmatter

```yaml
---
title: "Creator Platform Pricing Research 2024-2025"
created: 2026-01-21
visibility: public
status: live
summaryNote: "research-creator-platform-pricing"
wordCount: 8400
model: "Gemini 2.0 Flash"
aiSource: "Deep Research"
---
```

### Content

Preserve the full research content. Key formatting:

1. **Keep structure** — Headings, sections, examples
2. **Add WikiLinks** — Link concepts to existing notes
3. **Format external links** — See below
4. **Clean up AI artifacts** — Remove "As an AI..." phrases

---

## External Link Format

Commune wiki uses HTML for external links with arrow indicator:

```html
<a href="https://example.com/article" target="_blank" rel="noopener noreferrer">
  Article Title<span class="external-link-icon" aria-hidden="true">↗</span>
</a>
```

**Convert:**
```markdown
[Article Title](https://example.com/article)
```

**To:**
```html
<a href="https://example.com/article" target="_blank" rel="noopener noreferrer">Article Title<span class="external-link-icon" aria-hidden="true">↗</span></a>
```

**Why HTML:**
- Clear visual distinction from WikiLinks
- Opens in new tab (preserves wiki context)
- Security attributes included

---

## WikiLink Discovery

When converting research, search for linkable concepts:

```bash
# Find existing notes that might relate
grep -r "keyword" src/content/notes/ --include="*.md" -l

# List all note titles
ls src/content/notes/ | sed 's/.md$//' | tr '-' ' '
```

**Link aggressively.** If a concept exists as a note, link it. This creates the network effect.

---

## Workflow

1. **Read source research file**

2. **Extract key findings** for summary (5-6 points)

3. **Create summary note** in `notes/research-[slug].md`

4. **Create full research** in `research/[slug].md`

5. **Add WikiLinks** to both files
   - Search existing notes for related concepts
   - Link liberally — every concept that has a note should link

6. **Format external links** as HTML

7. **Link them together**
   - Summary has `[[Full Research Title]]` link
   - Full research has `summaryNote: "slug"` in frontmatter

8. **Commit and publish**
   ```bash
   git add -A
   git commit -m "[add] Research: Topic Name"
   git push
   ```

---

## Lead Magnet Flow

```
[User searches topic on Google]
        ↓
[Finds summary note — SEO optimized]
        ↓
[Reads key findings — intrigued]
        ↓
[Clicks "Full Research" WikiLink]
        ↓
[Opens in sliding pane — 700+ lines]
        ↓
[Notices WikiLinks in full doc]
        ↓
[Clicks through — explores wiki]
        ↓
[Tripwire worked — new reader]
```

Every deep research session (Gemini, GPT, etc.) becomes a discoverable entry point.

---

## Example: Converting Gemini Research

**Input:** 10-page Gemini deep research on "OSS Business Models"

**Output:**

1. `src/content/notes/research-oss-business-models.md` (~300 words)
   - Summary with key findings
   - Links to `[[OSS Business Models Research]]`

2. `src/content/research/oss-business-models.md` (~800 lines)
   - Full Gemini output
   - WikiLinks added throughout
   - External links formatted as HTML
   - `summaryNote: "research-oss-business-models"`

**Commit:**
```bash
git commit -m "[add] Research: OSS Business Models (Gemini deep research)"
```

---

## Quality Checklist

Before publishing research to wiki:

- [ ] Summary note exists in `notes/` (tripwire)
- [ ] Full research exists in `research/`
- [ ] Summary has `type: research-summary` in frontmatter
- [ ] Full research has `summaryNote` linking back to summary
- [ ] Full research has `wordCount` and `model` fields
- [ ] Summary is 200-400 words with key findings
- [ ] Summary links to full research with WikiLink
- [ ] External links formatted as HTML with arrow icon
- [ ] WikiLinks added to related existing notes
- [ ] Both files have matching `created` dates
