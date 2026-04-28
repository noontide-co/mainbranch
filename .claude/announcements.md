# Announcements

What's new since the last time you ran Main Branch. `/start` reads this file before showing the menu and surfaces unseen entries as a "What's new" banner. `/pull` prints new entries after pulling vip updates.

---

## Format

Each announcement is a `## <slug>` heading followed by metadata and a body. Slugs are stable identifiers (kebab-case, descriptive). Read top to bottom — newest at the top.

```markdown
## <slug>
- date: YYYY-MM-DD
- expires: YYYY-MM-DD              (auto-stops surfacing after this date)
- skill: /<skill-name>             (the skill the announcement is about, used to mark seen on use)
- title: <one-line headline>

<2-line body, caveman brevity>
```

The skill marks an announcement as seen in `~/.config/vip/local.yaml:seen_announcements` when:
- The user routes to the announced skill
- The user types "dismiss" / "seen" / "got it"
- The current date is past `expires`

---

## Active

## site-oneflow
- date: 2026-04-28
- expires: 2026-05-12
- skill: /site
- title: `/site` is now one-flow: brief → live site in one shot.

The skill walks research → brief → review → lock → setup → conversion endpoint (Stripe / lead form / appointment / webhook) → 2 home concepts on localhost → pick → publish raw → build out → publish. Try option 7 in `/start`, or run `/site` directly.

---

## Archive

(Move expired announcements here. Keep the file scannable — old entries serve as changelog.)
