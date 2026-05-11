"""Operator-owned display vocabulary for business repo facts."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

VOCABULARY_RELATIVE_PATH = Path("core") / "vocabulary.md"
DEFAULT_TERMS: dict[str, Any] = {
    "push": {"singular": "push", "plural": "pushes"},
    "statuses": {},
    "channels": {},
    "kinds": {},
}
TERM_KEYS = ("push", "statuses", "channels", "kinds")
PUSH_TERM_KEYS = ("singular", "plural")


def _defaults() -> dict[str, Any]:
    return deepcopy(DEFAULT_TERMS)


def _read_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"unreadable: {exc}"
    if not text.startswith("---"):
        return None, "missing YAML frontmatter"
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return None, "unterminated YAML frontmatter"
    try:
        data = yaml.safe_load(text[3:end].lstrip("\n")) or {}
    except yaml.YAMLError as exc:
        return None, f"YAML error: {exc}"
    if not isinstance(data, dict):
        return None, "frontmatter must be a mapping"
    return data, None


def _string_map(value: Any, key: str, warnings: list[str]) -> dict[str, str]:
    if value in (None, ""):
        return {}
    if not isinstance(value, dict):
        warnings.append(f"terms.{key} must be a mapping of canonical keys to display words")
        return {}
    cleaned: dict[str, str] = {}
    for raw_name, raw_display in sorted(value.items(), key=lambda item: str(item[0])):
        name = str(raw_name).strip() if raw_name is not None else ""
        if not name:
            warnings.append(f"terms.{key} contains an empty key")
            continue
        if not isinstance(raw_display, str) or not raw_display.strip():
            warnings.append(f"terms.{key}.{name} must be a non-empty string")
            continue
        cleaned[name] = raw_display.strip()
    return cleaned


def _parse_terms(raw_terms: Any) -> tuple[dict[str, Any], list[str]]:
    terms = _defaults()
    warnings: list[str] = []
    if raw_terms in (None, ""):
        return terms, warnings
    if not isinstance(raw_terms, dict):
        warnings.append("terms must be a mapping")
        return terms, warnings

    for key in sorted(str(item) for item in raw_terms if str(item) not in TERM_KEYS):
        warnings.append(f"terms.{key} is not recognized and was ignored")

    raw_push = raw_terms.get("push")
    if raw_push not in (None, ""):
        if not isinstance(raw_push, dict):
            warnings.append("terms.push must be a mapping with singular/plural display words")
        else:
            for key in sorted(str(item) for item in raw_push if str(item) not in PUSH_TERM_KEYS):
                warnings.append(f"terms.push.{key} is not recognized and was ignored")
            for key in PUSH_TERM_KEYS:
                value = raw_push.get(key)
                if value in (None, ""):
                    continue
                if not isinstance(value, str) or not value.strip():
                    warnings.append(f"terms.push.{key} must be a non-empty string")
                    continue
                terms["push"][key] = value.strip()

    for key in ("statuses", "channels", "kinds"):
        terms[key] = _string_map(raw_terms.get(key), key, warnings)
    return terms, warnings


def _summary(terms: dict[str, Any]) -> str:
    push_value = terms.get("push")
    push = push_value if isinstance(push_value, dict) else {}
    singular = str(push.get("singular") or "push")
    plural = str(push.get("plural") or "pushes")
    if terms == DEFAULT_TERMS:
        return "Using default vocabulary: push/pushes."
    return f"Using operator vocabulary: {singular}/{plural}."


def facts(repo: str | Path) -> dict[str, Any]:
    """Return deterministic operator vocabulary facts for runtime grounding."""
    repo_path = Path(repo)
    path = repo_path / VOCABULARY_RELATIVE_PATH
    if not path.exists():
        terms = _defaults()
        return {
            "path": VOCABULARY_RELATIVE_PATH.as_posix(),
            "exists": False,
            "ok": True,
            "source": "defaults",
            "type": "",
            "status": "",
            "terms": terms,
            "warnings": [],
            "errors": [],
            "summary": _summary(terms),
        }

    frontmatter, error = _read_frontmatter(path)
    if error is not None:
        terms = _defaults()
        return {
            "path": VOCABULARY_RELATIVE_PATH.as_posix(),
            "exists": True,
            "ok": False,
            "source": VOCABULARY_RELATIVE_PATH.as_posix(),
            "type": "",
            "status": "",
            "terms": terms,
            "warnings": [],
            "errors": [error],
            "summary": _summary(terms),
        }

    assert frontmatter is not None
    warnings: list[str] = []
    file_type = str(frontmatter.get("type") or "")
    if file_type and file_type != "vocabulary":
        warnings.append("type should be 'vocabulary' for operator vocabulary files")
    terms, term_warnings = _parse_terms(frontmatter.get("terms"))
    warnings.extend(term_warnings)
    return {
        "path": VOCABULARY_RELATIVE_PATH.as_posix(),
        "exists": True,
        "ok": True,
        "source": VOCABULARY_RELATIVE_PATH.as_posix(),
        "type": file_type,
        "status": str(frontmatter.get("status") or ""),
        "terms": terms,
        "warnings": warnings,
        "errors": [],
        "summary": _summary(terms),
    }
