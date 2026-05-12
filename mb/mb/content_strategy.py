"""Layered content strategy validation and status facts."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from mb import relationships

SCHEMA_VERSION = "1.0"
STALE_REVIEW_DAYS = 90
STATUS_VALUES = {"draft", "active", "paused", "needs-review", "stale", "archived"}

BUSINESS_PATH = "core/content-strategy.md"
DISTRIBUTION_PATH = "core/marketing/distribution-strategy.md"
CHANNELS_ROOT = "core/marketing/channels"
ACCOUNTS_ROOT = "core/marketing/accounts"
PEOPLE_ROOT = "core/people"

INDEX_FIELDS = (
    "linked_strategy_layers",
    "strategy_layers",
    "linked_distribution_strategy",
    "linked_channel_strategies",
    "linked_account_strategies",
    "linked_people",
)

UNINDEXED_LAYER_MESSAGE = "layer exists but is not indexed from core/content-strategy.md"


def _read_markdown(path: Path) -> tuple[dict[str, Any] | None, str, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, "", f"unreadable: {exc}"
    if not text.startswith("---"):
        return None, text, "no frontmatter"
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return None, text, "unterminated frontmatter"
    raw = text[3:end].lstrip("\n")
    try:
        parsed = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        return None, text[end + len("\n---") :], f"yaml error: {exc}"
    if not isinstance(parsed, dict):
        return None, text[end + len("\n---") :], "frontmatter not a mapping"
    return parsed, text[end + len("\n---") :], None


def _coerce_refs(value: Any) -> tuple[list[str], bool]:
    if value is None:
        return [], True
    if isinstance(value, str):
        return [value], True
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)], all(
            isinstance(item, str) for item in value
        )
    return [], False


def _clean_refs(value: Any) -> tuple[list[str], bool]:
    refs, valid = _coerce_refs(value)
    return [clean for ref in refs if (clean := relationships.clean_ref(ref))], valid


def _parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return date.fromisoformat(value.strip()[:10])
        except ValueError:
            return None
    return None


def _word_count(body: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+", relationships.strip_markdown_code(body)))


def _relative(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def _discover(repo: Path) -> dict[str, list[Path] | Path]:
    return {
        "business": repo / BUSINESS_PATH,
        "distribution": repo / DISTRIBUTION_PATH,
        "channels": sorted((repo / CHANNELS_ROOT).glob("*.md")),
        "accounts": sorted((repo / ACCOUNTS_ROOT).glob("*.md")),
        "people": sorted((repo / PEOPLE_ROOT).glob("*.md")),
    }


def _discovered_paths(discovered: dict[str, list[Path] | Path], key: str) -> list[Path]:
    value = discovered.get(key)
    return value if isinstance(value, list) else []


def _indexed_refs(repo: Path) -> tuple[set[str], list[str], bool]:
    content_path = repo / BUSINESS_PATH
    if not content_path.is_file():
        return set(), [], True
    frontmatter, body, err = _read_markdown(content_path)
    if err is not None or frontmatter is None:
        return set(), [], True

    refs: set[str] = set()
    invalid_fields: list[str] = []
    for field in INDEX_FIELDS:
        if field not in frontmatter:
            continue
        field_refs, valid = _clean_refs(frontmatter.get(field))
        refs.update(field_refs)
        if not valid:
            invalid_fields.append(field)

    body_without_code = relationships.strip_markdown_code(body)
    for _, target in relationships.iter_markdown_links(body_without_code):
        clean = relationships.markdown_link_target(target)
        if not clean or relationships.is_external_ref(clean):
            continue
        resolved = relationships.resolve_markdown_link(repo, content_path, clean)
        if resolved is not None:
            refs.add(_relative(resolved, repo))
        else:
            refs.add(relationships.clean_ref(clean))
    for match in relationships.WIKILINK_RE.finditer(body_without_code):
        target = relationships.wikilink_target(match.group(1))
        if target:
            refs.add(target if target.endswith(".md") else f"{target}.md")

    has_explicit_index = any(field in frontmatter for field in INDEX_FIELDS)
    return refs, invalid_fields, has_explicit_index


def _target_exists(repo: Path, source: Path, ref: str) -> bool:
    clean = relationships.clean_ref(ref)
    if not clean or relationships.is_external_ref(clean):
        return True
    if clean.startswith(("core/", "research/", "decisions/", "bets/", "pushes/", "log/")):
        target = repo / clean
    else:
        target = (source.parent / clean).resolve()
    try:
        target.resolve().relative_to(repo)
    except ValueError:
        return False
    return target.is_file()


def _finding(
    *,
    code: str,
    path: str,
    severity: str,
    message: str,
    field: str = "",
    state: str = "needs_review",
) -> dict[str, Any]:
    return {
        "code": code,
        "path": path,
        "field": field,
        "severity": severity,
        "state": state,
        "message": message,
        "safe_to_share": True,
    }


def _state_from_findings(findings: list[dict[str, Any]]) -> str:
    states = {str(item.get("state") or "") for item in findings}
    if "disconnected" in states:
        return "disconnected"
    if "stale" in states:
        return "stale"
    if "needs_review" in states:
        return "needs_review"
    return "healthy"


def _warning_finding_code(message: str) -> str:
    if message == UNINDEXED_LAYER_MESSAGE:
        return "content_strategy_unindexed_layer"
    return "content_strategy_warning"


def _add_required_checks(
    *,
    path: str,
    frontmatter: dict[str, Any] | None,
    errors: list[str],
    required: list[str],
    expected_type: str,
) -> None:
    if frontmatter is None:
        return
    for key in required:
        if key not in frontmatter:
            errors.append(f"missing key: {key}")
    if frontmatter.get("type") != expected_type:
        errors.append(f"type must be {expected_type!r}")
    status = frontmatter.get("status")
    if status is not None and status not in STATUS_VALUES:
        errors.append(f"status={status!r} not in {sorted(STATUS_VALUES)}")
    for key in required:
        if key in {"type", "status", "source_links"} or key not in frontmatter:
            continue
        value = frontmatter.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} must be a non-empty string")
    if "source_links" in frontmatter:
        refs, valid = _coerce_refs(frontmatter.get("source_links"))
        if not valid:
            errors.append("source_links must be a string or list of strings")
        elif not all(str(ref).strip() for ref in refs):
            errors.append("source_links must not contain empty strings")


def _add_freshness_checks(
    *,
    frontmatter: dict[str, Any] | None,
    warnings: list[str],
    today: date,
) -> bool:
    if frontmatter is None:
        return False
    stale = False
    for key in ("last_reviewed", "owner", "update_trigger", "source_links"):
        if key not in frontmatter:
            warnings.append(f"missing freshness key: {key}")
    reviewed = _parse_date(frontmatter.get("last_reviewed"))
    if "last_reviewed" in frontmatter and reviewed is None:
        warnings.append("last_reviewed must be YYYY-MM-DD")
    elif reviewed is not None:
        age_days = (today - reviewed).days
        if age_days > STALE_REVIEW_DAYS:
            stale = True
            warnings.append(
                f"last_reviewed is {age_days} days old; review fast-changing platform rules"
            )
    return stale


def _layer_paths(repo: Path) -> list[str]:
    discovered = _discover(repo)
    paths: list[str] = []
    distribution = discovered["distribution"]
    if isinstance(distribution, Path) and distribution.is_file():
        paths.append(_relative(distribution, repo))
    for key in ("channels", "accounts", "people"):
        for path in _discovered_paths(discovered, key):
            if path.is_file():
                paths.append(_relative(path, repo))
    return sorted(paths)


def validation_results(repo: Path, *, today: date | None = None) -> dict[str, dict[str, Any]]:
    """Return mb validate file results for content strategy files."""
    current_date = today or date.today()
    indexed_refs, invalid_index_fields, has_explicit_index = _indexed_refs(repo)
    layer_paths = set(_layer_paths(repo))
    results: dict[str, dict[str, Any]] = {}
    discovered = _discover(repo)

    def check_file(
        file_path: Path,
        *,
        schema: str,
        required: list[str],
        expected_type: str,
        freshness: bool = False,
    ) -> tuple[dict[str, Any] | None, str]:
        rel = _relative(file_path, repo)
        frontmatter, body, err = _read_markdown(file_path)
        errors: list[str] = []
        warnings: list[str] = []
        if err is not None:
            errors.append(err)
        else:
            _add_required_checks(
                path=rel,
                frontmatter=frontmatter,
                errors=errors,
                required=required,
                expected_type=expected_type,
            )
        if _word_count(body) < 20:
            warnings.append("content strategy file is thin; add operator-useful sections")
        if freshness:
            _add_freshness_checks(frontmatter=frontmatter, warnings=warnings, today=current_date)
        results[rel] = {
            "path": rel,
            "ok": not errors,
            "errors": errors,
            "warnings": warnings,
            "schema": schema,
        }
        return frontmatter, rel

    business = discovered["business"]
    if isinstance(business, Path) and business.is_file():
        frontmatter, rel = check_file(
            business,
            schema="content-strategy",
            required=["type", "status"],
            expected_type="content_strategy",
        )
        if frontmatter is not None:
            for field in invalid_index_fields:
                results[rel]["errors"].append(f"{field} must be a string or list of strings")
            for field in INDEX_FIELDS:
                refs, valid = _clean_refs(frontmatter.get(field))
                if field in frontmatter and valid:
                    for ref in refs:
                        if not _target_exists(repo, business, ref):
                            results[rel]["warnings"].append(
                                f"{field} target {ref!r} does not exist"
                            )

    if layer_paths and not (repo / BUSINESS_PATH).is_file():
        rel = BUSINESS_PATH
        results[rel] = {
            "path": rel,
            "ok": True,
            "errors": [],
            "warnings": [
                "layered content strategy files exist but core/content-strategy.md is missing"
            ],
            "schema": "content-strategy",
        }

    distribution = discovered["distribution"]
    if isinstance(distribution, Path) and distribution.is_file():
        check_file(
            distribution,
            schema="content-distribution-strategy",
            required=["type", "status"],
            expected_type="distribution_strategy",
        )

    for channel in _discovered_paths(discovered, "channels"):
        if not channel.is_file():
            continue
        frontmatter, rel = check_file(
            channel,
            schema="content-channel-strategy",
            required=["type", "status", "channel"],
            expected_type="channel_strategy",
            freshness=True,
        )
        if frontmatter is not None and frontmatter.get("channel") != channel.stem:
            results[rel]["warnings"].append("channel should match the file name")

    for account in _discovered_paths(discovered, "accounts"):
        if not account.is_file():
            continue
        frontmatter, rel = check_file(
            account,
            schema="content-account-strategy",
            required=[
                "type",
                "status",
                "platform",
                "account",
                "channel_strategy",
                "voice_source",
            ],
            expected_type="account_strategy",
            freshness=True,
        )
        if frontmatter is not None:
            platform = str(frontmatter.get("platform") or "").strip()
            if platform and not account.stem.startswith(f"{platform}-"):
                results[rel]["warnings"].append("platform should match the file name prefix")
            channel_ref = str(frontmatter.get("channel_strategy") or "").strip()
            if channel_ref and not _target_exists(repo, account, channel_ref):
                results[rel]["errors"].append(
                    f"channel_strategy target {channel_ref!r} does not exist"
                )
            voice_ref = str(frontmatter.get("voice_source") or "").strip()
            if voice_ref and not _target_exists(repo, account, voice_ref):
                results[rel]["errors"].append(f"voice_source target {voice_ref!r} does not exist")
            elif voice_ref and not (
                relationships.clean_ref(voice_ref).startswith("core/people/")
                or relationships.clean_ref(voice_ref) == "core/voice.md"
            ):
                results[rel]["warnings"].append(
                    "voice_source should point to core/people/<person>.md or core/voice.md"
                )

    for person in _discovered_paths(discovered, "people"):
        if not person.is_file():
            continue
        check_file(
            person,
            schema="content-person",
            required=["type", "status"],
            expected_type="person",
        )

    if layer_paths and (repo / BUSINESS_PATH).is_file() and not has_explicit_index:
        results[BUSINESS_PATH].setdefault("warnings", []).append(
            "core/content-strategy.md should index layered files with linked_strategy_layers"
        )
    for layer_path in sorted(layer_paths):
        if layer_path not in indexed_refs:
            results[layer_path].setdefault("warnings", []).append(UNINDEXED_LAYER_MESSAGE)

    for result in results.values():
        result["ok"] = not result.get("errors")
    return results


def _file_state(result: dict[str, Any], *, stale: bool = False) -> str:
    errors = [str(item).lower() for item in result.get("errors") or []]
    warnings = [str(item).lower() for item in result.get("warnings") or []]
    if any(
        "does not exist" in item or ("missing" in item and "core/content" in item)
        for item in errors
    ):
        return "disconnected"
    if any(
        "does not exist" in item or "not indexed" in item or "core/content" in item
        for item in warnings
    ):
        return "disconnected"
    if stale or any("last_reviewed is" in item for item in warnings):
        return "stale"
    if errors or warnings:
        return "needs_review"
    return "healthy"


def facts(repo: Path, *, today: date | None = None) -> dict[str, Any]:
    """Return normalized content strategy health facts for status/dashboard callers."""
    current_date = today or date.today()
    results = validation_results(repo, today=current_date)
    discovered = _discover(repo)
    indexed_refs, _, has_explicit_index = _indexed_refs(repo)
    findings: list[dict[str, Any]] = []
    for rel_path, result in sorted(results.items()):
        for message in result.get("errors") or []:
            state = "disconnected" if "does not exist" in str(message) else "needs_review"
            findings.append(
                _finding(
                    code="content_strategy_error",
                    path=rel_path,
                    severity="error",
                    state=state,
                    message=str(message),
                )
            )
        for message in result.get("warnings") or []:
            text = str(message)
            state = "stale" if "last_reviewed is" in text else "needs_review"
            if "not indexed" in text or "core/content-strategy.md is missing" in text:
                state = "disconnected"
            findings.append(
                _finding(
                    code=_warning_finding_code(text),
                    path=rel_path,
                    severity="warning",
                    state=state,
                    message=text,
                )
            )

    def item(path: Path, *, kind: str, stale: bool = False) -> dict[str, Any]:
        exists = path.is_file()
        rel = _relative(path, repo)
        result = results.get(rel, {"errors": [], "warnings": []})
        frontmatter, _, _ = _read_markdown(path) if exists else ({}, "", None)
        return {
            "kind": kind,
            "path": rel,
            "exists": exists,
            "indexed_from_content_strategy": rel in indexed_refs,
            "frontmatter": {
                "type": str((frontmatter or {}).get("type") or ""),
                "status": str((frontmatter or {}).get("status") or ""),
            },
            "health_state": "missing" if not exists else _file_state(result, stale=stale),
            "safe_to_share": True,
        }

    channels: list[dict[str, Any]] = []
    for path in _discovered_paths(discovered, "channels"):
        if not path.is_file():
            continue
        frontmatter, _, _ = _read_markdown(path)
        reviewed = _parse_date((frontmatter or {}).get("last_reviewed"))
        stale = reviewed is not None and (current_date - reviewed).days > STALE_REVIEW_DAYS
        entry = item(path, kind="channel", stale=stale)
        entry.update(
            {
                "channel": str((frontmatter or {}).get("channel") or path.stem),
                "last_reviewed": reviewed.isoformat() if reviewed else "",
                "stale": stale,
            }
        )
        channels.append(entry)

    accounts: list[dict[str, Any]] = []
    for path in _discovered_paths(discovered, "accounts"):
        if not path.is_file():
            continue
        frontmatter, _, _ = _read_markdown(path)
        channel_ref = str((frontmatter or {}).get("channel_strategy") or "")
        voice_ref = str((frontmatter or {}).get("voice_source") or "")
        reviewed = _parse_date((frontmatter or {}).get("last_reviewed"))
        stale = reviewed is not None and (current_date - reviewed).days > STALE_REVIEW_DAYS
        entry = item(path, kind="account", stale=stale)
        entry.update(
            {
                "platform": str((frontmatter or {}).get("platform") or ""),
                "account": str((frontmatter or {}).get("account") or ""),
                "channel_strategy": channel_ref,
                "channel_connected": bool(channel_ref and _target_exists(repo, path, channel_ref)),
                "voice_source": voice_ref,
                "voice_source_connected": bool(voice_ref and _target_exists(repo, path, voice_ref)),
                "person_connected": bool(
                    relationships.clean_ref(voice_ref).startswith("core/people/")
                    and _target_exists(repo, path, voice_ref)
                ),
                "last_reviewed": reviewed.isoformat() if reviewed else "",
                "stale": stale,
            }
        )
        accounts.append(entry)

    people = [
        item(path, kind="person")
        for path in _discovered_paths(discovered, "people")
        if path.is_file()
    ]
    distribution_path = discovered["distribution"]
    distribution = (
        item(distribution_path, kind="distribution")
        if isinstance(distribution_path, Path)
        else {"kind": "distribution", "path": DISTRIBUTION_PATH, "exists": False}
    )
    business_path = discovered["business"]
    simple = (
        item(business_path, kind="business_strategy")
        if isinstance(business_path, Path)
        else {"kind": "business_strategy", "path": BUSINESS_PATH, "exists": False}
    )
    layer_count = (
        int(bool(distribution.get("exists"))) + len(channels) + len(accounts) + len(people)
    )
    overall_state = (
        "missing"
        if not simple.get("exists") and layer_count == 0
        else _state_from_findings(findings)
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "summary": (
            "Content strategy health is derived from repo files and normalized for agents "
            "and read-only dashboard views."
        ),
        "overall_state": overall_state,
        "simple_entry_point": simple,
        "layers": {
            "distribution": distribution,
            "channels": channels,
            "accounts": accounts,
            "people": people,
        },
        "counts": {
            "layers": layer_count,
            "channels": len(channels),
            "accounts": len(accounts),
            "people": len(people),
            "findings": len(findings),
        },
        "index": {
            "path": BUSINESS_PATH,
            "uses_explicit_frontmatter": has_explicit_index,
            "indexed_paths": sorted(indexed_refs & set(_layer_paths(repo))),
        },
        "findings": findings[:20],
        "safe_to_share": True,
    }
