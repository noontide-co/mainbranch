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
