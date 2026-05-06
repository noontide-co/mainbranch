"""Shared deterministic facts for canonical pushes and legacy campaigns."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

PUSH_STATUS = {
    "draft",
    "planned",
    "active",
    "paused",
    "completed",
    "canceled",
    "archived",
}

PUSH_KIND = {
    "launch",
    "drop",
    "challenge",
    "promo",
    "nurture",
    "outreach",
    "event",
    "announcement",
    "round",
    "wave",
}

PUSH_HEALTH = {"on-track", "at-risk", "blocked", "unknown"}
PUSH_FOLDER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$")
PUSH_FOLDER_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")

CAMPAIGN_COMPATIBILITY_DEPRECATION = (
    "campaigns/ is legacy compatibility. New writes use pushes/ and linked_pushes; "
    "legacy campaign JSON keys are deprecated during the compatibility window."
)


def read_frontmatter(path: Path) -> dict[str, Any]:
    """Read YAML frontmatter from a markdown file; return an empty dict on miss."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}
    try:
        data = yaml.safe_load(text[3:end].lstrip("\n")) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def title_from_markdown(path: Path) -> str:
    """Return the first H1 title or a readable stem fallback."""
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()
    except OSError:
        pass
    return path.stem.replace("-", " ")


def _string(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _date_string(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    iso_method = getattr(value, "isoformat", None)
    if callable(iso_method):
        iso = iso_method()
        return iso.strip() if isinstance(iso, str) else ""
    return ""


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _goal(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        goal: dict[str, str] = {}
        for key in ("metric", "target", "by"):
            raw = value.get(key)
            if isinstance(raw, str):
                goal[key] = raw
            elif raw is not None:
                goal[key] = str(raw)
        return goal
    if isinstance(value, str) and value.strip():
        return {"summary": value.strip()}
    return {}


def _record_date(meta: dict[str, Any], path: Path) -> str:
    for key in ("started", "review_on", "date"):
        value = _date_string(meta.get(key))
        if value:
            return value
    folder_match = PUSH_FOLDER_DATE_RE.match(path.parent.name)
    if folder_match:
        return folder_match.group(1)
    return ""


def _summarize_record(repo: Path, path: Path, *, legacy: bool) -> dict[str, Any]:
    meta = read_frontmatter(path)
    try:
        rel = path.relative_to(repo).as_posix()
    except ValueError:
        rel = str(path)
    record_type = _string(meta.get("type")) or ("campaign" if legacy else "push")
    return {
        "path": rel,
        "title": title_from_markdown(path),
        "slug": _string(meta.get("slug")) or path.parent.name,
        "type": "push",
        "record_type": record_type,
        "kind": _string(meta.get("kind")),
        "status": _string(meta.get("status")),
        "health": _string(meta.get("health")),
        "goal": _goal(meta.get("goal")),
        "owner": _string(meta.get("owner")),
        "audience": _string(meta.get("audience")),
        "offer": _string(meta.get("offer")),
        "promise": _string(meta.get("promise")),
        "channels": _strings(meta.get("channels")),
        "started": _date_string(meta.get("started")),
        "review_on": _date_string(meta.get("review_on")),
        "date": _record_date(meta, path),
        "source": "legacy_campaign" if legacy else "canonical",
        "source_root": "campaigns" if legacy else "pushes",
        "legacy": legacy,
        "deprecated": legacy,
    }


def _record_paths(repo: Path, glob: str) -> list[Path]:
    return sorted(path for path in repo.glob(glob) if path.is_file())


def facts(repo: str | Path) -> dict[str, Any]:
    """Return additive push facts for status, start, graph, and dashboards."""
    root = Path(repo).resolve()
    canonical = [
        _summarize_record(root, path, legacy=False)
        for path in _record_paths(root, "pushes/*/push.md")
    ]
    legacy = [
        _summarize_record(root, path, legacy=True)
        for path in _record_paths(root, "campaigns/*/campaign.md")
    ]
    records = canonical + legacy
    active = [record for record in records if record["status"] == "active"]
    active_legacy = [record for record in legacy if record["status"] == "active"]
    return {
        "records": records,
        "active": active,
        "count": len(records),
        "canonical_count": len(canonical),
        "legacy_campaign_count": len(legacy),
        "legacy_campaigns": legacy,
        "active_legacy_campaigns": active_legacy,
        "compatibility": {
            "canonical_root": "pushes",
            "canonical_type": "push",
            "canonical_link_field": "linked_pushes",
            "legacy_root": "campaigns",
            "legacy_type": "campaign",
            "legacy_link_field": "linked_campaigns",
            "legacy_campaigns_read": True,
            "legacy_campaign_keys_deprecated": True,
            "deprecation": CAMPAIGN_COMPATIBILITY_DEPRECATION,
        },
    }
