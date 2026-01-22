# Weekly Updates Template

Template and workflow for generating "Recent Updates" notes from Git history.

---

## When to Generate

| Trigger | Condition |
|---------|-----------|
| Weekly | Friday + >3 commits this week |
| Daily | >15 commits in single day |
| Manual | User invokes `/wiki recent` |

---

## Frontmatter

```yaml
---
title: "Updates: Week of January 20, 2026"
created: 2026-01-24
visibility: public
status: live
type: weekly-update
auto_generated: true
---
```

**Required fields:**
- `title` — "Updates: Week of [Month Day, Year]"
- `created` — Date generated
- `type: weekly-update` — Distinguishes from regular notes
- `auto_generated: true` — Marks as machine-generated

---

## Content Structure

```markdown
## This Week

### New Notes
- [[Note A]] — brief description
- [[Note B]] — brief description

### Updated
- [[Note C]] — what changed
- [[Note D]] — what changed

### Research
- Added [[Deep Research: Topic X]]

---
*Auto-generated from Git history*
```

**Sections:**
1. **New Notes** — Notes added this period
2. **Updated** — Existing notes modified
3. **Research** — Research docs added

Only include sections with content. Skip empty sections.

---

## Git Commands

**Get commits for the week:**
```bash
git log --since="1 week ago" --pretty=format:"%h %s" --name-only
```

**Get commits for today (if >15):**
```bash
git log --since="1 day ago" --pretty=format:"%h %s" --name-only
```

**Parse changed files:**
- Files in `src/content/notes/` → categorize as new or updated
- Files in `src/content/research/` → research section
- Use `git diff --name-status` to distinguish A (added) vs M (modified)

---

## File Location

Save to: `src/content/updates/YYYY-MM-DD.md`

The updates collection is separate from notes to keep the main notes/ clean.

---

## Example Output

```yaml
---
title: "Updates: Week of January 20, 2026"
created: 2026-01-24
visibility: public
status: live
type: weekly-update
auto_generated: true
---

## This Week

### New Notes
- [[Compounding Knowledge]] — how reference files build on each other
- [[Active vs Passive Memory]] — why Main Branch uses files not chat history
- [[WikiLinks Create Serendipity]] — emergent connections from dense linking

### Updated
- [[Evergreen Notes]] — added word count guidelines
- [[Atomic Notes]] — clarified "one idea" definition

### Research
- Added [[Deep Research: Creator Platform Pricing 2024-2025]]

---
*Auto-generated from Git history*
```

---

## Quality Checklist

Before publishing update note:

- [ ] Title uses format "Updates: Week of [Month Day, Year]"
- [ ] `type: weekly-update` in frontmatter
- [ ] `auto_generated: true` in frontmatter
- [ ] Only non-empty sections included (skip sections with no content)
- [ ] Each note linked with WikiLink syntax `[[Note Title]]`
- [ ] Brief descriptions after each link (what's new/changed)
- [ ] Saved to `src/content/updates/YYYY-MM-DD.md`
- [ ] Footer attribution line included
