"""``mb validate`` — frontmatter and optional cross-reference checks.

Hard-coded schema per the master decision. Cross-reference validation is
opt-in because local authoring should warn by default and CI can opt into
strict mode. Per-file frontmatter errors always fail.

The schemas tolerate extras; only listed required keys are checked.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from mb import pushes as pushes_mod
from mb import relationships

DECISION_STATUS = {"proposed", "accepted", "rejected", "superseded", "running"}
OFFER_STATUS = {
    "proposed",
    "running",
    "scaling",
    "killed",
    "graduated",
    "died",
    "accepted",
    "rejected",
}
RESEARCH_STATUS = {"complete", "in-progress", "stale"}
BET_STATUS = {"open", "paused", "closed", "canceled"}
CAMPAIGN_STATUS = pushes_mod.PUSH_STATUS
PUSH_KIND = pushes_mod.PUSH_KIND
PUSH_HEALTH = pushes_mod.PUSH_HEALTH
PLAYBOOK_STATUS = {
    "draft",
    "planned",
    "approved",
    "active",
    "paused",
    "completed",
    "canceled",
    "retired",
}
PLAYBOOK_PROVIDER_BOUNDARY = {
    "plan-only",
    "external-manual",
    "candidate-adapter",
    "accepted-adapter",
}
PLAYBOOK_APPROVAL_STATUS = {"not-required", "needed", "approved", "rejected"}
PLAYBOOK_RESOURCE_KIND = {"url", "file", "repo", "document", "manual", "none"}
PLAYBOOK_ACCEPTED_MUTATION_PROVIDERS: set[str] = set()
PLAYBOOK_PROVIDER_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SECRET_KEY_RE = re.compile(
    r"(api[_-]?key|access[_-]?token|refresh[_-]?token|bearer|credential|"
    r"client[_-]?secret|password|private[_-]?key|session|cookie|secret)",
    re.IGNORECASE,
)
SECRET_VALUE_RE = re.compile(
    r"(-----BEGIN [A-Z ]*PRIVATE KEY-----|bearer\s+[A-Za-z0-9._~+/=-]{10,}|"
    r"gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{10,}|"
    r"xox[baprs]-[A-Za-z0-9-]{10,}|api[_-]?key\s*[:=])",
    re.IGNORECASE,
)

LINK_FIELDS = relationships.RELATIONSHIP_FIELDS

DECISION_STATUS_ORDER = {
    "proposed": 0,
    "running": 1,
    "accepted": 2,
    "rejected": 2,
    "superseded": 2,
}
OFFER_STATUS_ORDER = {
    "proposed": 0,
    "running": 1,
    "accepted": 1,
    "rejected": 1,
    "scaling": 2,
    "killed": 3,
    "graduated": 3,
    "died": 3,
}
CAMPAIGN_STATUS_ORDER = {
    "draft": 0,
    "planned": 1,
    "active": 2,
    "paused": 2,
    "completed": 3,
    "canceled": 3,
    "archived": 4,
}

SCHEMAS: dict[str, dict[str, Any]] = {
    "decisions": {
        "glob": "decisions/*.md",
        "required": ["date", "status"],
        "enums": {"status": DECISION_STATUS},
    },
    "core/offers": {
        "glob": "core/offers/*/offer.md",
        "required": ["slug", "status"],
        "enums": {"status": OFFER_STATUS},
    },
    "research": {
        "glob": "research/*.md",
        "required": ["date", "topic", "source"],
        "enums": {},
    },
    "bets": {
        "glob": "bets/*.md",
        # `linked_campaigns` stays required for backward compatibility with
        # every committed bet. New bet writes also include `linked_pushes`
        # (canonical, recognized in LINK_FIELDS). A follow-up PR can drop
        # `linked_campaigns` from required once the migration apply lands.
        "required": [
            "status",
            "opened",
            "deadline",
            "appetite",
            "hypothesis",
            "metric",
            "target",
            "result",
            "linked_decisions",
            "linked_research",
            "linked_campaigns",
            "linked_outcomes",
            "public",
            "channels",
            "tags",
        ],
        "enums": {"status": BET_STATUS},
    },
    "log": {
        "glob": "log/*.md",
        "required": ["date"],
        "enums": {},
    },
    "campaigns": {
        "glob": "campaigns/*/campaign.md",
        "required": ["slug", "status"],
        "enums": {"status": CAMPAIGN_STATUS},
        "primitive": "legacy-campaign",
    },
    "pushes": {
        "glob": "pushes/*/push.md",
        "required": [
            "type",
            "slug",
            "kind",
            "status",
            "health",
            "goal",
            "owner",
            "audience",
            "offer",
            "promise",
        ],
        "enums": {"kind": PUSH_KIND, "status": CAMPAIGN_STATUS, "health": PUSH_HEALTH},
        "primitive": "push",
    },
    "push-playbooks": {
        "glob": "pushes/*/playbooks/*.md",
        "required": [
            "type",
            "status",
            "push",
            "platform",
            "provider",
            "provider_boundary",
            "trigger",
            "resource",
            "approval",
            "state",
            "validation",
            "linked_outcomes",
        ],
        "enums": {
            "status": PLAYBOOK_STATUS,
            "provider_boundary": PLAYBOOK_PROVIDER_BOUNDARY,
        },
        "primitive": "playbook",
    },
    "documents": {
        "glob": "documents/*.md",
        "required": ["title"],
        "enums": {},
    },
}


def _read_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Return (frontmatter dict, error). Either may be None."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"unreadable: {exc}"
    if not text.startswith("---"):
        return None, "no frontmatter"
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return None, "unterminated frontmatter"
    body = text[3:end].lstrip("\n")
    try:
        data = yaml.safe_load(body) or {}
    except yaml.YAMLError as exc:
        return None, f"yaml error: {exc}"
    if not isinstance(data, dict):
        return None, "frontmatter not a mapping"
    return data, None


def _check_one(path: Path, schema: dict[str, Any]) -> dict[str, Any]:
    fm, err = _read_frontmatter(path)
    if err is not None:
        return {"path": str(path), "ok": False, "errors": [err], "warnings": []}
    assert fm is not None
    errors: list[str] = []
    for k in schema["required"]:
        if k not in fm:
            errors.append(f"missing key: {k}")
    for k, allowed in schema.get("enums", {}).items():
        if k in fm and fm[k] not in allowed:
            errors.append(f"{k}={fm[k]!r} not in {sorted(allowed)}")
    primitive = schema.get("primitive")
    if primitive == "push":
        _check_push_frontmatter(path, fm, errors)
    elif primitive == "playbook":
        _check_playbook_frontmatter(path, fm, errors)
    elif primitive == "legacy-campaign":
        _check_legacy_campaign_frontmatter(fm, errors)
    _check_provider_refs_shape(fm, errors)
    return {"path": str(path), "ok": not errors, "errors": errors, "warnings": []}


def _require_non_empty_string(fm: dict[str, Any], key: str, errors: list[str]) -> None:
    if key not in fm:
        return
    value = fm.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key} must be a non-empty string")


def _scalar_as_string(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    iso_method = getattr(value, "isoformat", None)
    if callable(iso_method):
        iso = iso_method()
        return iso.strip() if isinstance(iso, str) else ""
    if isinstance(value, int | float):
        return str(value)
    return ""


def _check_push_frontmatter(path: Path, fm: dict[str, Any], errors: list[str]) -> None:
    if not pushes_mod.PUSH_FOLDER_RE.fullmatch(path.parent.name):
        errors.append("push folder must match YYYY-MM-DD-slug")
    if fm.get("type") != "push":
        errors.append("type must be 'push'")
    for key in ("slug", "kind", "status", "health", "owner", "audience", "offer", "promise"):
        _require_non_empty_string(fm, key, errors)
    promise = fm.get("promise")
    if isinstance(promise, str) and len(promise.strip()) > 140:
        errors.append("promise must be 140 characters or fewer")
    goal = fm.get("goal")
    if "goal" not in fm:
        return
    if not isinstance(goal, dict):
        errors.append("goal must be a mapping with metric, target, and by")
        return
    for key in ("metric", "target", "by"):
        value = _scalar_as_string(goal.get(key))
        if not value:
            errors.append(f"goal.{key} must be a non-empty string")
    by = _scalar_as_string(goal.get("by"))
    if by and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", by):
        errors.append("goal.by must be YYYY-MM-DD")


def _require_mapping(fm: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any] | None:
    if key not in fm:
        return None
    value = fm.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be a mapping")
        return None
    return value


def _mapping_value_as_string(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    return value.strip() if isinstance(value, str) else ""


def _require_mapping_string(
    mapping: dict[str, Any],
    key: str,
    errors: list[str],
    *,
    prefix: str,
) -> str:
    value = _mapping_value_as_string(mapping, key)
    if not value:
        errors.append(f"{prefix}.{key} must be a non-empty string")
    return value


def _check_playbook_push_link(path: Path, fm: dict[str, Any], errors: list[str]) -> None:
    push_folder = path.parent.parent
    if path.parent.name != "playbooks" or push_folder.parent.name != "pushes":
        errors.append("playbook files must live under pushes/<YYYY-MM-DD-slug>/playbooks/")
        return
    if not pushes_mod.PUSH_FOLDER_RE.fullmatch(push_folder.name):
        errors.append("playbook push folder must match YYYY-MM-DD-slug")
    raw_push = fm.get("push")
    if not isinstance(raw_push, str) or not raw_push.strip():
        if "push" in fm:
            errors.append("push must link to the containing push.md")
        return
    clean_push = relationships.clean_ref(raw_push)
    if not clean_push:
        errors.append("push must link to the containing push.md")
        return
    repo = push_folder.parent.parent
    if clean_push.startswith("pushes/"):
        target = (repo / clean_push).resolve()
    else:
        target = (path.parent / clean_push).resolve()
    expected = (push_folder / "push.md").resolve()
    if target != expected:
        errors.append("push must link to the containing push.md")
    if not expected.exists():
        errors.append("push target does not exist")


def _iter_secret_paths(value: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            if SECRET_KEY_RE.search(key_text):
                findings.append(path)
            findings.extend(_iter_secret_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            findings.extend(_iter_secret_paths(nested, path))
    elif isinstance(value, str) and SECRET_VALUE_RE.search(value):
        findings.append(prefix or "<value>")
    return findings


def _check_playbook_frontmatter(path: Path, fm: dict[str, Any], errors: list[str]) -> None:
    _check_playbook_push_link(path, fm, errors)
    if fm.get("type") != "playbook":
        errors.append("type must be 'playbook'")
    for key in ("platform", "provider", "provider_boundary"):
        _require_non_empty_string(fm, key, errors)

    provider = fm.get("provider")
    if isinstance(provider, str) and provider.strip():
        provider_id = provider.strip()
        if not PLAYBOOK_PROVIDER_RE.fullmatch(provider_id):
            errors.append("provider must be a lowercase hyphenated provider id")
        if (
            fm.get("provider_boundary") == "accepted-adapter"
            and provider_id not in PLAYBOOK_ACCEPTED_MUTATION_PROVIDERS
        ):
            errors.append(
                "provider_boundary=accepted-adapter requires a tested Main Branch provider adapter"
            )

    trigger = _require_mapping(fm, "trigger", errors)
    if trigger is not None:
        trigger_kind = _require_mapping_string(trigger, "kind", errors, prefix="trigger")
        if trigger_kind in {"comment_keyword", "dm_keyword"}:
            _require_mapping_string(trigger, "keyword", errors, prefix="trigger")

    resource = _require_mapping(fm, "resource", errors)
    if resource is not None:
        resource_kind = _require_mapping_string(resource, "kind", errors, prefix="resource")
        if resource_kind and resource_kind not in PLAYBOOK_RESOURCE_KIND:
            errors.append(
                f"resource.kind={resource_kind!r} not in {sorted(PLAYBOOK_RESOURCE_KIND)}"
            )
        if resource_kind != "none":
            _require_mapping_string(resource, "value", errors, prefix="resource")

    approval = _require_mapping(fm, "approval", errors)
    if approval is not None:
        if not isinstance(approval.get("required"), bool):
            errors.append("approval.required must be true or false")
        status = _require_mapping_string(approval, "status", errors, prefix="approval")
        if status and status not in PLAYBOOK_APPROVAL_STATUS:
            errors.append(f"approval.status={status!r} not in {sorted(PLAYBOOK_APPROVAL_STATUS)}")

    state = _require_mapping(fm, "state", errors)
    if state is not None and "provider_refs" in state:
        provider_refs = state.get("provider_refs")
        if not isinstance(provider_refs, dict | list) and provider_refs is not None:
            errors.append("state.provider_refs must be a mapping, list, or null")

    validation = _require_mapping(fm, "validation", errors)
    if validation is not None:
        if "dry_run" not in validation:
            errors.append("validation.dry_run must be recorded")
        if "smoke_evidence" not in validation:
            errors.append("validation.smoke_evidence must be recorded")

    refs, valid_refs = _coerce_refs(fm.get("linked_outcomes"))
    if "linked_outcomes" in fm and not valid_refs:
        errors.append("linked_outcomes must be a string or list of strings")
    if any(ref.strip().lower().startswith(("http://", "https://")) for ref in refs):
        errors.append("linked_outcomes should point to repo outcome/log files, not external URLs")

    secret_paths = sorted(set(_iter_secret_paths(fm)))
    if secret_paths:
        errors.append("playbook frontmatter must not contain secrets: " + ", ".join(secret_paths))


def _check_legacy_campaign_frontmatter(fm: dict[str, Any], errors: list[str]) -> None:
    record_type = fm.get("type")
    if record_type is not None and record_type not in {"campaign", "push"}:
        errors.append("type must be 'campaign' or 'push' for legacy campaign records")


def _check_provider_refs_shape(fm: dict[str, Any], errors: list[str]) -> None:
    if "provider_refs" not in fm:
        return
    provider_refs = fm.get("provider_refs")
    if not isinstance(provider_refs, dict):
        errors.append("provider_refs must be a mapping of provider names to non-secret refs")
        return
    for provider, refs in provider_refs.items():
        if not isinstance(provider, str) or not provider.strip():
            errors.append("provider_refs provider names must be non-empty strings")
            continue
        if refs is None:
            continue
        if isinstance(refs, dict):
            if not all(isinstance(key, str) and key.strip() for key in refs):
                errors.append(f"provider_refs.{provider} ref names must be non-empty strings")
            continue
        if isinstance(refs, list):
            if not all(isinstance(item, dict) for item in refs):
                errors.append(f"provider_refs.{provider} must be a mapping or list of mappings")
                continue
            invalid_keys = [
                key for item in refs for key in item if not isinstance(key, str) or not key.strip()
            ]
            if invalid_keys:
                errors.append(f"provider_refs.{provider} ref names must be non-empty strings")
            continue
        errors.append(f"provider_refs.{provider} must be a mapping or list of mappings")


def _is_hidden_or_generated(path: Path, repo: Path) -> bool:
    rel_parts = path.relative_to(repo).parts
    is_bundled_data = rel_parts[:2] == ("mb", "_data") or rel_parts[:1] == ("_data",)
    return (
        any(
            part.startswith(".") or part in {"__pycache__", "node_modules", ".venv", "venv"}
            for part in rel_parts
        )
        or is_bundled_data
    )


def _iter_frontmatter_files(repo: Path) -> list[Path]:
    return [
        f
        for f in sorted(repo.rglob("*.md"))
        if f.is_file() and not _is_hidden_or_generated(f, repo)
    ]


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


def _read_markdown_body(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return text
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return text
    return text[end + len("\n---") :]


def _resolve_wikilink(
    *,
    repo: Path,
    target: str,
    files_by_stem: dict[str, list[Path]],
    files_by_rel: dict[str, Path],
) -> tuple[Path | None, bool]:
    clean = relationships.wikilink_target(target)
    if not clean:
        return None, False
    is_bare_wikilink = len(Path(clean).parts) == 1
    candidates = [clean]
    if not clean.endswith(".md"):
        candidates.append(f"{clean}.md")
    for candidate in candidates:
        direct = files_by_rel.get(candidate)
        if direct is not None:
            return direct, False
        repo_direct = (repo / candidate).resolve()
        try:
            repo_direct.relative_to(repo)
        except ValueError:
            continue
        if repo_direct.is_file() and repo_direct.suffix == ".md":
            return repo_direct, False
    if not is_bare_wikilink:
        return None, False
    matches = files_by_stem.get(Path(clean).stem, [])
    if len(matches) == 1:
        return matches[0], False
    return None, len(matches) > 1


def _status_order_for(path: Path) -> dict[str, int] | None:
    parts = path.parts
    if "decisions" in parts:
        return DECISION_STATUS_ORDER
    if "pushes" in parts or "campaigns" in parts:
        return CAMPAIGN_STATUS_ORDER
    if "offers" in parts:
        return OFFER_STATUS_ORDER
    return None


def _finding(
    *,
    code: str,
    source: Path,
    repo: Path,
    field: str,
    target: str,
    message: str,
) -> dict[str, str]:
    return {
        "code": code,
        "path": str(source.relative_to(repo)),
        "field": field,
        "target": target,
        "message": message,
    }


def _add_file_warning(
    files_by_path: dict[str, dict[str, Any]],
    *,
    repo: Path,
    source: Path,
    message: str,
) -> None:
    rel = str(source.relative_to(repo))
    if rel not in files_by_path:
        files_by_path[rel] = {
            "path": rel,
            "ok": True,
            "errors": [],
            "warnings": [],
            "schema": "cross-refs",
        }
    files_by_path[rel].setdefault("warnings", []).append(message)


def _check_status_transition(
    *,
    source: Path,
    target: Path,
    repo: Path,
    field: str,
    ref: str,
    source_fm: dict[str, Any],
    findings: list[dict[str, str]],
) -> None:
    if field != "supersedes":
        return
    source_order = _status_order_for(source.relative_to(repo))
    target_order = _status_order_for(target.relative_to(repo))
    if source_order is None or target_order is None or source_order is not target_order:
        return
    source_status = source_fm.get("status")
    target_fm, target_err = _read_frontmatter(target)
    if target_err is not None or target_fm is None:
        return
    target_status = target_fm.get("status")
    if not isinstance(source_status, str) or not isinstance(target_status, str):
        return
    if source_status not in source_order or target_status not in source_order:
        return
    if source_order[source_status] < source_order[target_status]:
        findings.append(
            _finding(
                code="status-transition",
                source=source,
                repo=repo,
                field=field,
                target=ref,
                message=(
                    f"{field} target {ref!r} is status {target_status!r}; "
                    f"source status {source_status!r} would move backward"
                ),
            )
        )


def _relative_ref(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def _ref_list_contains(value: Any, expected: str) -> bool:
    refs, valid_type = _coerce_refs(value)
    return valid_type and expected in {relationships.clean_ref(ref) for ref in refs}


def _reverse_bet_field(source: Path, repo: Path) -> str:
    parts = source.relative_to(repo).parts
    if not parts:
        return ""
    section = parts[0]
    if section == "decisions":
        return "linked_decisions"
    if section == "research":
        return "linked_research"
    if section == "pushes":
        return "linked_pushes"
    if section == "campaigns":
        return "linked_campaigns"
    if section in {"log", "documents"}:
        return "linked_outcomes"
    return ""


def _check_bet_backlink(
    *,
    source: Path,
    target: Path,
    repo: Path,
    field: str,
    ref: str,
    target_fm: dict[str, Any],
    findings: list[dict[str, str]],
) -> None:
    source_rel = _relative_ref(source, repo)
    target_rel = _relative_ref(target, repo)
    source_is_bet = source_rel.startswith("bets/")
    target_is_bet = target_rel.startswith("bets/")

    if (
        source_is_bet
        and not target_is_bet
        and field
        in {
            "linked_decisions",
            "linked_research",
            "linked_pushes",
            "linked_campaigns",
            "linked_outcomes",
        }
    ):
        if not _ref_list_contains(target_fm.get("linked_bets"), source_rel):
            findings.append(
                _finding(
                    code="missing-bet-backlink",
                    source=source,
                    repo=repo,
                    field=field,
                    target=ref,
                    message=(f"{field} target {ref!r} should include linked_bets: {source_rel}"),
                )
            )
        return

    if field == "linked_bets" and target_is_bet and not source_is_bet:
        reverse_field = _reverse_bet_field(source, repo)
        if reverse_field and not _ref_list_contains(target_fm.get(reverse_field), source_rel):
            findings.append(
                _finding(
                    code="missing-bet-backlink",
                    source=source,
                    repo=repo,
                    field=field,
                    target=ref,
                    message=(
                        f"{field} target {ref!r} should include {reverse_field}: {source_rel}"
                    ),
                )
            )


def _check_cross_refs(
    repo: Path,
    files_by_path: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    orphan_offers: list[dict[str, str]] = []
    markdown_files = _iter_frontmatter_files(repo)
    files_by_stem: dict[str, list[Path]] = {}
    files_by_rel: dict[str, Path] = {}

    for file_path in markdown_files:
        rel = file_path.relative_to(repo).as_posix()
        files_by_rel[rel] = file_path
        files_by_stem.setdefault(file_path.stem, []).append(file_path)

    for source in markdown_files:
        fm, err = _read_frontmatter(source)
        if err is not None or fm is None:
            continue
        source_rel = source.relative_to(repo).as_posix()
        for field in relationships.relationship_fields_for_source(source_rel):
            if field not in fm:
                continue
            refs, valid_type = _coerce_refs(fm.get(field))
            if not valid_type:
                findings.append(
                    _finding(
                        code="invalid-link-field",
                        source=source,
                        repo=repo,
                        field=field,
                        target="",
                        message=f"{field} must be a string or list of strings",
                    )
                )
                continue
            for ref in refs:
                if relationships.is_external_ref(ref):
                    continue
                clean_ref = relationships.clean_ref(ref)
                if not clean_ref:
                    continue
                target = (repo / clean_ref).resolve()
                try:
                    target.relative_to(repo)
                except ValueError:
                    findings.append(
                        _finding(
                            code="target-outside-repo",
                            source=source,
                            repo=repo,
                            field=field,
                            target=ref,
                            message=f"{field} target {ref!r} resolves outside the repo",
                        )
                    )
                    continue
                if not target.exists():
                    findings.append(
                        _finding(
                            code="missing-target",
                            source=source,
                            repo=repo,
                            field=field,
                            target=ref,
                            message=f"{field} target {ref!r} does not exist",
                        )
                    )
                    continue
                _check_status_transition(
                    source=source,
                    target=target,
                    repo=repo,
                    field=field,
                    ref=ref,
                    source_fm=fm,
                    findings=findings,
                )
                target_fm, target_err = _read_frontmatter(target)
                if target_err is None and target_fm is not None:
                    _check_bet_backlink(
                        source=source,
                        target=target,
                        repo=repo,
                        field=field,
                        ref=ref,
                        target_fm=target_fm,
                        findings=findings,
                    )

    for source in markdown_files:
        body = _read_markdown_body(source)
        if body is None:
            continue
        body_without_code = relationships.strip_markdown_code(body)
        for match in relationships.WIKILINK_RE.finditer(body_without_code):
            raw_target = match.group(1)
            clean_target = relationships.wikilink_target(raw_target)
            if not clean_target:
                continue
            resolved, ambiguous = _resolve_wikilink(
                repo=repo,
                target=raw_target,
                files_by_stem=files_by_stem,
                files_by_rel=files_by_rel,
            )
            if resolved is not None:
                continue
            code = "ambiguous-wikilink" if ambiguous else "missing-wikilink-target"
            message = (
                f"wikilink target {raw_target!r} matches multiple markdown files"
                if ambiguous
                else f"wikilink target {raw_target!r} does not resolve to a markdown file"
            )
            findings.append(
                _finding(
                    code=code,
                    source=source,
                    repo=repo,
                    field="wikilink",
                    target=raw_target,
                    message=message,
                )
            )
        for _, raw_target in relationships.iter_markdown_links(body_without_code):
            clean_target = relationships.markdown_link_target(raw_target)
            if not clean_target or relationships.is_external_ref(clean_target):
                continue
            if not relationships.is_local_markdown_ref(clean_target):
                continue
            if relationships.resolve_markdown_link(repo, source, clean_target) is not None:
                continue
            findings.append(
                _finding(
                    code="missing-markdown-link-target",
                    source=source,
                    repo=repo,
                    field="markdown_link",
                    target=clean_target,
                    message=(
                        f"markdown link target {clean_target!r} does not resolve to a markdown file"
                    ),
                )
            )

    offers_root = repo / "core" / "offers"
    if offers_root.exists():
        for offer_dir in sorted(p for p in offers_root.iterdir() if p.is_dir()):
            if (offer_dir / "offer.md").exists():
                continue
            rel = str(offer_dir.relative_to(repo))
            orphan_offers.append(
                {
                    "code": "orphan-offer",
                    "path": rel,
                    "field": "core/offers",
                    "target": "offer.md",
                    "message": f"{rel}/ is missing offer.md",
                }
            )

    for finding in findings:
        _add_file_warning(
            files_by_path,
            repo=repo,
            source=repo / finding["path"],
            message=finding["message"],
        )
    for finding in orphan_offers:
        rel = finding["path"]
        files_by_path.setdefault(
            rel,
            {
                "path": rel,
                "ok": True,
                "errors": [],
                "warnings": [],
                "schema": "core/offers",
            },
        )
        files_by_path[rel].setdefault("warnings", []).append(finding["message"])

    return {
        "enabled": True,
        "checked_fields": list(LINK_FIELDS),
        "registry": relationships.registry_payload(),
        "warnings": findings + orphan_offers,
        "orphan_offers": orphan_offers,
    }


def _legacy_frontmatter_repair(repo: Path, error_count: int) -> dict[str, Any] | None:
    if error_count == 0:
        return None
    migrated_markers = [
        repo / ".mb" / "schema_version",
        repo / "decisions" / "2026-05-02-mainbranch-v02-path-migration.md",
    ]
    has_compat_links = (repo / "reference" / "core").is_symlink() or (
        repo / "reference" / "offers"
    ).is_symlink()
    if not has_compat_links and not any(path.exists() for path in migrated_markers):
        return None
    return {
        "code": "legacy-frontmatter-schema-debt",
        "message": (
            "Layout migration can succeed while old markdown files still fail the "
            "current frontmatter schema. Treat these as legacy content repairs, "
            "not as evidence that the path migration failed."
        ),
        "next_steps": [
            "Run `mb validate --json` and group failures by missing key or status enum.",
            "Repair frontmatter in small batches on the migration branch.",
            "Use `mb validate --cross-refs` after schema errors are down to zero.",
        ],
    }


def run(
    path: str,
    verbose: bool = False,
    cross_refs: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    """Run validation across all known schemas. Verbose adds key dumps."""
    repo = Path(path).resolve()
    files_by_path: dict[str, dict[str, Any]] = {}
    for schema_name, schema in SCHEMAS.items():
        glob = schema["glob"]
        for f in sorted(repo.glob(glob)):
            r = _check_one(f, schema)
            r["schema"] = schema_name
            r["path"] = str(f.relative_to(repo))
            files_by_path[r["path"]] = r

    cross_ref_report = {"enabled": False, "checked_fields": [], "warnings": [], "orphan_offers": []}
    if cross_refs:
        cross_ref_report = _check_cross_refs(repo, files_by_path)

    files = list(files_by_path.values())
    warning_count = sum(len(f.get("warnings", [])) for f in files)
    error_count = sum(len(f.get("errors", [])) for f in files)
    ok = error_count == 0 and (warning_count == 0 or not strict)
    if strict:
        for file_result in files:
            if file_result.get("warnings"):
                file_result["ok"] = False
    return {
        "ok": ok,
        "files": files,
        "repo": str(repo),
        "strict": strict,
        "cross_refs": cross_ref_report,
        "legacy_repair": _legacy_frontmatter_repair(repo, error_count),
        "summary": {"errors": error_count, "warnings": warning_count},
    }


def render_human(report: dict[str, Any], verbose: bool = False) -> None:
    """Print results to stdout."""
    from rich.console import Console

    console = Console()
    if not report["files"]:
        console.print("[yellow]nothing to check yet.[/yellow]")
        return
    by_schema: dict[str, list[dict[str, Any]]] = {}
    for f in report["files"]:
        by_schema.setdefault(f["schema"], []).append(f)
    for schema, items in by_schema.items():
        console.print(f"\n[bold]{schema}[/bold]")
        for f in items:
            if f["errors"]:
                mark = "[red]fail[/red]"
            elif f.get("warnings"):
                mark = "[yellow]warn[/yellow]"
            else:
                mark = "[green]ok[/green]"
            console.print(f"  {mark}  {f['path']}")
            if f["errors"] or f.get("warnings") or verbose:
                for e in f["errors"]:
                    console.print(f"        - {e}")
                for warning in f.get("warnings", []):
                    console.print(f"        - {warning}")
    legacy_repair = report.get("legacy_repair")
    if legacy_repair:
        console.print("\n[bold yellow]Legacy frontmatter repair[/bold yellow]")
        console.print(f"  {legacy_repair['message']}")
        for step in legacy_repair.get("next_steps", []):
            console.print(f"  - {step}")
    console.print()
    if report["ok"]:
        if report["summary"]["warnings"]:
            console.print(
                f"[yellow]{report['summary']['warnings']} warning(s) found; "
                "use --strict to fail on warnings.[/yellow]"
            )
        else:
            console.print("[green]all metadata looks right.[/green]")
    else:
        if report["summary"]["errors"]:
            bad = sum(1 for f in report["files"] if f["errors"])
            console.print(f"[red]{bad} file(s) need fixing — see above.[/red]")
        else:
            console.print(
                f"[red]{report['summary']['warnings']} warning(s) fail in strict mode.[/red]"
            )
