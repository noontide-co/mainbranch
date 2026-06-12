"""Contact+event spine declaration (`mb spine declare` / `mb spine show`).

The spine is a declared position, not a database to install
(decisions/2026-06-12-spine-levels.md). A business records which system
plays the contact+event spine role — or that none does, on purpose — as a
committed repo fact at ``core/operations/spine.md``. Grading and the owned
build path ship as later slices; this module is the declare rung.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SPINE_RELATIVE_PATH = Path("core") / "operations" / "spine.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_lenses(raw: list[str]) -> list[dict[str, str]]:
    lenses: list[dict[str, str]] = []
    for item in raw:
        text = item.strip()
        if not text:
            continue
        store, _, domain = text.partition(":")
        store = store.strip()
        if not store:
            raise ValueError(f"lens {item!r} must be <store> or <store>:<domain>")
        lenses.append({"store": store, "domain": domain.strip()})
    return lenses


def declare(
    repo: str | Path = ".",
    *,
    store: str,
    intentional_none: bool = False,
    lenses: list[str] | None = None,
    gaps: list[str] | None = None,
    revisit: str = "",
    force: bool = False,
) -> dict[str, Any]:
    """Write the spine declaration as a committed repo fact."""
    root = Path(repo).resolve()
    store_id = store.strip().lower()
    if not store_id:
        raise ValueError("store is required; use `none` for an intentional no-spine position")
    if store_id == "none" and not intentional_none:
        raise ValueError(
            "declaring no spine requires --intentional — an undeclared gap and a "
            "deliberate product stance are different facts"
        )
    if store_id != "none" and intentional_none:
        raise ValueError("--intentional only applies with --store none")
    path = root / SPINE_RELATIVE_PATH
    if path.exists() and not force:
        return {
            "ok": False,
            "repo": str(root),
            "path": str(SPINE_RELATIVE_PATH),
            "summary": ("a spine declaration already exists; rerun with --force to replace it"),
        }
    parsed_lenses = _parse_lenses(lenses or [])
    frontmatter: dict[str, Any] = {
        "type": "spine",
        "store": store_id,
        "intentional_none": bool(intentional_none),
        "lenses": parsed_lenses,
        "known_gaps": [gap.strip() for gap in (gaps or []) if gap.strip()],
        "revisit_trigger": revisit.strip(),
        "declared_at": _now(),
    }
    if store_id == "none":
        body = (
            "# Contact+event spine: none, on purpose\n\n"
            "This business deliberately holds no person-store. The position is\n"
            "declared so agents treat it as a stance, not a gap. Revisit when the\n"
            "trigger below fires.\n"
        )
    else:
        body = (
            f"# Contact+event spine: {store_id}\n\n"
            f"`{store_id}` is the system of record for this business's people.\n"
            "Every other tool is a fan-out lens, never a second source of truth.\n"
            "Agents read people and events from the spine; sync flows *to* the\n"
            "lenses (operating-principles §2).\n"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n" + body
    path.write_text(text, encoding="utf-8")
    return {
        "ok": True,
        "repo": str(root),
        "path": str(SPINE_RELATIVE_PATH),
        "declaration": frontmatter,
        "summary": (
            "spine declared: none (intentional)"
            if store_id == "none"
            else f"spine declared: {store_id}"
            + (f" with {len(parsed_lenses)} lens(es)" if parsed_lenses else "")
        ),
    }


def show(repo: str | Path = ".") -> dict[str, Any]:
    """Read the spine declaration back as facts."""
    root = Path(repo).resolve()
    path = root / SPINE_RELATIVE_PATH
    if not path.is_file():
        return {
            "ok": False,
            "declared": False,
            "repo": str(root),
            "path": str(SPINE_RELATIVE_PATH),
            "summary": (
                "no spine declaration — run `mb spine declare --store <provider>` "
                "(or `--store none --intentional`)"
            ),
        }
    text = path.read_text(encoding="utf-8")
    frontmatter: dict[str, Any] = {}
    if text.startswith("---"):
        try:
            end = text.index("\n---", 3)
            raw = yaml.safe_load(text[3:end].lstrip("\n")) or {}
            frontmatter = raw if isinstance(raw, dict) else {}
        except (ValueError, yaml.YAMLError):
            frontmatter = {}
    if not frontmatter:
        return {
            "ok": False,
            "declared": False,
            "repo": str(root),
            "path": str(SPINE_RELATIVE_PATH),
            "summary": "spine file exists but its frontmatter is unreadable — re-declare",
        }
    return {
        "ok": True,
        "declared": True,
        "repo": str(root),
        "path": str(SPINE_RELATIVE_PATH),
        "declaration": frontmatter,
        "summary": (
            "spine: none (intentional)"
            if frontmatter.get("store") == "none"
            else f"spine: {frontmatter.get('store')}"
        ),
    }


OWNED_SCHEMA_SQL = """-- Contact+event spine: the person and their full timeline, owned.
-- Two tables on purpose (operating-principles §2/§3: right shape first,
-- leanest durable form). Portable SQLite; Cloudflare D1 instructions in
-- spine/README.md.

-- contact: the person. Unified by email (lowercased) when known.
CREATE TABLE IF NOT EXISTS contact (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  email       TEXT UNIQUE,          -- the unifier (lowercase, trimmed); NULL while anonymous
  phone       TEXT,
  name        TEXT,
  company     TEXT,
  domain      TEXT,                 -- normalized website when relevant
  city        TEXT,
  source      TEXT,                 -- first touch: form | chat | paid | ad | import
  status      TEXT NOT NULL DEFAULT 'lead',  -- lifecycle: lead -> customer -> ...
  click_id    TEXT,                 -- ad click id for consented attribution
  browser_id  TEXT,                 -- ad browser id for consented attribution
  ad_optout   INTEGER NOT NULL DEFAULT 0,  -- consent recorded once, on the person
  first_seen  TEXT,
  last_seen   TEXT,
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT
);
CREATE INDEX IF NOT EXISTS idx_contact_domain ON contact(domain);
CREATE INDEX IF NOT EXISTS idx_contact_status ON contact(status);

-- event: the timeline. Every touch is a row; contact_id is nullable so an
-- anonymous event can be recorded now and linked when the email arrives.
CREATE TABLE IF NOT EXISTS event (
  id                   INTEGER PRIMARY KEY AUTOINCREMENT,
  contact_id           INTEGER REFERENCES contact(id),
  type                 TEXT NOT NULL,   -- e.g. form_submit | chat_turn | paid | email_sent
  ts                   TEXT NOT NULL,   -- ISO timestamp of the event
  source               TEXT,            -- channel
  amount_cents         INTEGER,         -- for paid events
  payload              TEXT,            -- JSON detail
  -- Delivery truth (docs/delivery-truth.md): acceptance is not delivery.
  provider_message_id  TEXT,            -- the send's join key; never skip on send events
  delivery_state       TEXT,            -- accepted | delivered | bounced | suppressed
  created_at           TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_event_contact  ON event(contact_id, ts);
CREATE INDEX IF NOT EXISTS idx_event_type     ON event(type, ts);
CREATE INDEX IF NOT EXISTS idx_event_delivery ON event(delivery_state)
  WHERE delivery_state IS NOT NULL;
"""

OWNED_README = """# The owned contact+event spine

The person and their full timeline, in a store you own. Built when a
trigger fires (decisions/2026-06-12-spine-levels.md) — never as a default
migration away from a platform that serves you.

## Setting it up on Cloudflare D1 (the proven path)

```bash
npx wrangler d1 create <business>-spine
npx wrangler d1 execute <business>-spine --remote --file spine/schema.sql
```

Bind it to your workers in wrangler.toml, write server-side behind auth
(operating-principles §7), and update `core/operations/spine.md` via
`mb spine declare --force` so the declared position matches reality.

Any SQLite (or Postgres with minor type tweaks) works the same; the schema
is portable on purpose.

## The rules that keep it a spine

- **One row per person**, unified by lowercased email; anonymous events
  link later.
- **Every touch is an event row.** Chats with content, sends, payments —
  if it happened to a person, it lands here.
- **Send events carry delivery truth**: record `provider_message_id` at
  send with `delivery_state = 'accepted'`; flip it from the provider's
  webhook + a reconcile sweep. Never report "sent" from the API 200
  (docs/delivery-truth.md).
- **Platforms become lenses.** Sync TO the email tool and ad platforms
  from here; never let them become a second source of record.

## Canned queries

Did we actually reach this person?
```sql
SELECT type, ts, delivery_state FROM event
WHERE contact_id = (SELECT id FROM contact WHERE email = ?)
  AND provider_message_id IS NOT NULL ORDER BY ts DESC;
```

Real contacts captured but never successfully sent anything (unserved):
```sql
SELECT c.email, c.created_at FROM contact c
WHERE c.email IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM event e WHERE e.contact_id = c.id
                  AND e.delivery_state = 'delivered');
```

Warm but never bought:
```sql
SELECT c.email, COUNT(e.id) AS touches FROM contact c
JOIN event e ON e.contact_id = c.id
WHERE c.status = 'lead' GROUP BY c.id
HAVING touches >= 3 ORDER BY touches DESC;
```

One person's full timeline:
```sql
SELECT ts, type, source, delivery_state, payload FROM event
WHERE contact_id = (SELECT id FROM contact WHERE email = ?) ORDER BY ts;
```
"""


def init_owned(repo: str | Path = ".", *, force: bool = False) -> dict[str, Any]:
    """Scaffold the owned contact+event schema + instructions."""
    root = Path(repo).resolve()
    spine_dir = root / "spine"
    schema_path = spine_dir / "schema.sql"
    readme_path = spine_dir / "README.md"
    existing = [str(p.relative_to(root)) for p in (schema_path, readme_path) if p.exists()]
    if existing and not force:
        return {
            "ok": False,
            "repo": str(root),
            "written": [],
            "skipped": existing,
            "summary": "spine files already exist; rerun with --force to overwrite",
        }
    spine_dir.mkdir(parents=True, exist_ok=True)
    schema_path.write_text(OWNED_SCHEMA_SQL, encoding="utf-8")
    readme_path.write_text(OWNED_README, encoding="utf-8")
    return {
        "ok": True,
        "repo": str(root),
        "written": [
            str(schema_path.relative_to(root)),
            str(readme_path.relative_to(root)),
        ],
        "skipped": [],
        "summary": (
            "owned spine scaffolded — apply spine/schema.sql to your store "
            "(D1 commands in spine/README.md), then update the declaration "
            "with `mb spine declare --force`"
        ),
    }
