"""``mb topology`` — shared reader for repo topology registry and child descriptors.

This module is the single role-neutral source of normalized topology facts that
``mb status``, ``mb graph``, and ``mb doctor repair --plan`` consume. It reads
``core/operations/repo-topology.md`` and ``.mainbranch/repo.json`` (or the
legacy ``.mainbranch/source.json``) and reports public-safe topology metadata
separately from local-machine facts.

Schema validation lives in :mod:`mb.validate`. This module reads what the
validator already accepts, normalizes it for downstream consumers, and reports
drift evidence without copying private content, renaming repos, or rewriting
files.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from mb import github_activity

REGISTRY_RELATIVE_PATH = Path("core/operations/repo-topology.md")
CHILD_REPO_RELATIVE_PATH = Path(".mainbranch") / "repo.json"
LEGACY_SITE_RELATIVE_PATH = Path(".mainbranch") / "source.json"
CHILD_REPO_SCHEMA = "mb.child_repo.v0"

TOPOLOGY_ROLES = frozenset(
    {
        "business",
        "site",
        "offer",
        "product",
        "client",
        "finance",
        "legal",
        "ops",
        "integration_sidecar",
        "experiment",
        "archive",
    }
)
TOPOLOGY_LIFECYCLES = frozenset({"proposed", "active", "paused", "superseded", "archived"})
TOPOLOGY_VISIBILITIES = frozenset({"public", "team_private", "restricted", "local_only"})
TOPOLOGY_RELATIONSHIPS = frozenset(
    {
        "hub_for",
        "child_of",
        "execution_vehicle_for",
        "graduated_from",
        "supersedes",
        "archived_from",
        "source_for",
        "reports_to",
        "uses_provider",
    }
)

LINKED_FIELDS: tuple[str, ...] = (
    "linked_offers",
    "linked_pushes",
    "linked_bets",
    "linked_decisions",
    "linked_research",
    "linked_documents",
    "linked_docs",
    "linked_logs",
    "linked_outcomes",
    "linked_playbook_runs",
)

LOCAL_ABSOLUTE_PATH_RE = re.compile(r"^(?:/|~[/\\]|[A-Za-z]:[/\\])")
SECRET_KEY_RE = re.compile(
    r"(api[_-]?key|access[_-]?token|refresh[_-]?token|bearer|credential|"
    r"client[_-]?secret|password|private[_-]?key|session|cookie|secret)",
    re.IGNORECASE,
)
UNSAFE_KEY_RE = re.compile(
    r"(ledger|bank|payroll|tax|contract|legal[_-]?advice|dispute|customer|member|"
    r"account[_-]?number|raw[_-]?(?:data|export|cache|metric)|provider[_-]?cache|"
    r"local[_-]?path|absolute[_-]?path)",
    re.IGNORECASE,
)
KNOWN_TOPOLOGY_KEYS = frozenset(
    {
        "slug",
        "display_name",
        "role",
        "lifecycle",
        "status",
        "visibility",
        "purpose",
        "github_owner",
        "repo_name",
        "remote",
        "domain",
        "parent",
        "relationship",
        "uses_provider",
        *LINKED_FIELDS,
        "linked_playbooks",
    }
)


# ---------------------------------------------------------------------------
# Reading helpers
# ---------------------------------------------------------------------------


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}, text
    try:
        data = yaml.safe_load(text[3:end].lstrip("\n")) or {}
    except yaml.YAMLError:
        return {}, text
    body = text[end + len("\n---") :]
    if not isinstance(data, dict):
        return {}, body
    return data, body


def _string(value: Any) -> str:
    return str(value).strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = _string(item)
        if text:
            out.append(text)
    return out


def normalize_remote(value: Any) -> str:
    """Normalize a remote handle to ``owner/repo`` or empty string.

    Accepts ``github:owner/repo``, ``https://github.com/owner/repo(.git)``,
    ``git@github.com:owner/repo(.git)``, and bare ``owner/repo`` strings.
    """
    text = _string(value)
    if not text:
        return ""
    if text.startswith("github:"):
        text = text.removeprefix("github:").strip()
    name = github_activity.repo_full_name(text)
    if name:
        return name
    if "/" in text and "://" not in text and "@" not in text and " " not in text:
        candidate = text.removesuffix(".git").strip("/")
        parts = candidate.split("/")
        if len(parts) == 2 and parts[0] and parts[1]:
            return f"{parts[0]}/{parts[1]}"
    return ""


# ---------------------------------------------------------------------------
# Registry reader
# ---------------------------------------------------------------------------


def _normalize_repo_entry(entry: dict[str, Any]) -> dict[str, Any]:
    relationships = _string_list(entry.get("relationship"))
    linked = {field: _string_list(entry.get(field)) for field in LINKED_FIELDS}
    blueprint_refs = _string_list(entry.get("linked_playbooks"))
    uses_provider = _string_list(entry.get("uses_provider"))
    remote = _string(entry.get("remote"))
    extras = sorted(
        str(key) for key in entry if isinstance(key, str) and key not in KNOWN_TOPOLOGY_KEYS
    )
    role = _string(entry.get("role"))
    is_hub = role == "business" or "hub_for" in relationships
    domain = _string(entry.get("domain"))
    return {
        "slug": _string(entry.get("slug")),
        "display_name": _string(entry.get("display_name")),
        "role": role,
        "lifecycle": _string(entry.get("lifecycle")),
        "visibility": _string(entry.get("visibility")),
        "purpose": _string(entry.get("purpose")),
        "github_owner": _string(entry.get("github_owner")),
        "repo_name": _string(entry.get("repo_name")),
        "remote": remote,
        "remote_full_name": normalize_remote(remote)
        or (
            f"{_string(entry.get('github_owner'))}/{_string(entry.get('repo_name'))}"
            if entry.get("github_owner") and entry.get("repo_name")
            else ""
        ),
        "domain": domain,
        "parent": _string(entry.get("parent")),
        "relationships": relationships,
        **linked,
        "linked_playbook_blueprints": blueprint_refs,
        "uses_provider": uses_provider,
        "is_hub": is_hub,
        "extra_keys": extras,
    }


def read_registry(repo: Path) -> dict[str, Any]:
    """Read ``core/operations/repo-topology.md`` and normalize repo entries.

    Returns a stable dict whether or not the registry exists. Public-safe; never
    contains absolute machine paths.
    """
    rel = REGISTRY_RELATIVE_PATH.as_posix()
    path = repo / REGISTRY_RELATIVE_PATH
    if not path.exists():
        return {
            "found": False,
            "path": rel,
            "ok": False,
            "error": "missing",
            "schema": "",
            "status": "",
            "home": "",
            "home_full_name": "",
            "business_display_name": "",
            "repos": [],
        }
    text = _read_text(path)
    if text is None:
        return {
            "found": True,
            "path": rel,
            "ok": False,
            "error": "unreadable",
            "schema": "",
            "status": "",
            "home": "",
            "home_full_name": "",
            "business_display_name": "",
            "repos": [],
        }
    fm, _ = _split_frontmatter(text)
    if not fm:
        return {
            "found": True,
            "path": rel,
            "ok": False,
            "error": "missing or unparsable frontmatter",
            "schema": "",
            "status": "",
            "home": "",
            "home_full_name": "",
            "business_display_name": "",
            "repos": [],
        }
    if fm.get("type") != "repo_topology":
        return {
            "found": True,
            "path": rel,
            "ok": False,
            "error": "type is not 'repo_topology'",
            "schema": _string(fm.get("schema")),
            "status": _string(fm.get("status")),
            "home": _string(fm.get("home")),
            "home_full_name": normalize_remote(fm.get("home")),
            "business_display_name": _string(fm.get("business_display_name")),
            "repos": [],
        }
    raw_repos = fm.get("repos")
    if not isinstance(raw_repos, list) or not raw_repos:
        return {
            "found": True,
            "path": rel,
            "ok": False,
            "error": "repos must be a non-empty list of mappings",
            "schema": _string(fm.get("schema")),
            "status": _string(fm.get("status")),
            "home": _string(fm.get("home")),
            "home_full_name": normalize_remote(fm.get("home")),
            "business_display_name": _string(fm.get("business_display_name")),
            "repos": [],
        }
    repos: list[dict[str, Any]] = []
    for entry in raw_repos:
        if not isinstance(entry, dict):
            continue
        repos.append(_normalize_repo_entry(entry))
    return {
        "found": True,
        "path": rel,
        "ok": True,
        "error": "",
        "schema": _string(fm.get("schema")),
        "status": _string(fm.get("status")),
        "home": _string(fm.get("home")),
        "home_full_name": normalize_remote(fm.get("home")),
        "business_display_name": _string(fm.get("business_display_name")),
        "repos": repos,
    }


# ---------------------------------------------------------------------------
# Child descriptor reader
# ---------------------------------------------------------------------------


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return {}, "missing"
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f"invalid JSON: {exc}"
    if not isinstance(parsed, dict):
        return {}, "not a JSON object"
    return parsed, ""


def _empty_descriptor() -> dict[str, Any]:
    return {
        "found": False,
        "kind": "",
        "path": "",
        "ok": False,
        "error": "missing",
        "schema": "",
        "role": "",
        "display_name": "",
        "github_owner": "",
        "repo_name": "",
        "remote_full_name": "",
        "safe_purpose": "",
        "parent": {
            "display_name": "",
            "github_owner": "",
            "repo_name": "",
            "remote": "",
            "remote_full_name": "",
            "local_checkout_relative": "",
        },
        "linked": {"offers": [], "pushes": [], "bets": [], "decisions": []},
        "return_to_hub_command": "",
        "safe_to_share": True,
        "legacy_business_repo_present": False,
    }


def _normalize_repo_json(payload: dict[str, Any], rel: str) -> dict[str, Any]:
    parent = payload.get("parent")
    parent_data: dict[str, Any] = parent if isinstance(parent, dict) else {}
    linked = payload.get("linked")
    linked_data: dict[str, Any] = linked if isinstance(linked, dict) else {}
    schema = _string(payload.get("schema")) or CHILD_REPO_SCHEMA
    error = ""
    if schema != CHILD_REPO_SCHEMA:
        error = f"unsupported schema {schema!r}"
    parent_remote = _string(parent_data.get("remote"))
    parent_remote_full = normalize_remote(parent_remote) or (
        f"{_string(parent_data.get('github_owner'))}/{_string(parent_data.get('repo_name'))}"
        if parent_data.get("github_owner") and parent_data.get("repo_name")
        else ""
    )
    local_checkout_raw = _string(parent_data.get("local_checkout"))
    if local_checkout_raw and LOCAL_ABSOLUTE_PATH_RE.match(local_checkout_raw):
        # never expose absolute path; preserve presence flag instead
        local_checkout = ""
    else:
        local_checkout = local_checkout_raw
    role = _string(payload.get("role"))
    return {
        "found": True,
        "kind": "repo_json",
        "path": rel,
        "ok": not error,
        "error": error,
        "schema": schema,
        "role": role,
        "display_name": _string(payload.get("display_name")),
        "github_owner": _string(payload.get("github_owner")),
        "repo_name": _string(payload.get("repo_name")),
        "remote_full_name": (
            f"{_string(payload.get('github_owner'))}/{_string(payload.get('repo_name'))}"
            if payload.get("github_owner") and payload.get("repo_name")
            else ""
        ),
        "safe_purpose": _string(payload.get("safe_purpose")),
        "parent": {
            "display_name": _string(parent_data.get("display_name")),
            "github_owner": _string(parent_data.get("github_owner")),
            "repo_name": _string(parent_data.get("repo_name")),
            "remote": parent_remote,
            "remote_full_name": parent_remote_full,
            "local_checkout_relative": local_checkout,
        },
        "linked": {
            "offers": _string_list(linked_data.get("offers")),
            "pushes": _string_list(linked_data.get("pushes")),
            "bets": _string_list(linked_data.get("bets")),
            "decisions": _string_list(linked_data.get("decisions")),
        },
        "return_to_hub_command": _string(payload.get("return_to_hub_command")),
        "safe_to_share": bool(payload.get("safe_to_share", True)),
        "legacy_business_repo_present": False,
    }


def _normalize_legacy_source(payload: dict[str, Any], rel: str) -> dict[str, Any]:
    business_repo = _string(payload.get("business_repo"))
    legacy_absolute = bool(business_repo) and bool(LOCAL_ABSOLUTE_PATH_RE.match(business_repo))
    return {
        "found": True,
        "kind": "legacy_source",
        "path": rel,
        "ok": True,
        "error": "",
        "schema": "legacy.site_source",
        "role": "site",
        "display_name": "",
        "github_owner": "",
        "repo_name": "",
        "remote_full_name": "",
        "safe_purpose": "",
        "parent": {
            "display_name": "",
            "github_owner": "",
            "repo_name": "",
            "remote": "",
            "remote_full_name": "",
            "local_checkout_relative": "",
        },
        "linked": {
            "offers": [_string(payload.get("offer_path"))]
            if _string(payload.get("offer_path"))
            else [],
            "pushes": [_string(payload.get("campaign_path"))]
            if _string(payload.get("campaign_path"))
            else [],
            "bets": [],
            "decisions": [],
        },
        "return_to_hub_command": "",
        "safe_to_share": bool(payload.get("safe_to_share", True)),
        "legacy_business_repo_present": legacy_absolute,
    }


def read_child_descriptor(repo: Path) -> dict[str, Any]:
    """Read ``.mainbranch/repo.json`` (preferred) or ``.mainbranch/source.json``.

    Returns a normalized dict with public-safe fields. Absolute local paths from
    legacy ``source.json`` are never copied into the public payload; their
    presence is recorded via ``legacy_business_repo_present`` only.
    """
    repo_json = repo / CHILD_REPO_RELATIVE_PATH
    source_json = repo / LEGACY_SITE_RELATIVE_PATH
    if repo_json.exists():
        payload, error = _read_json(repo_json)
        if error:
            empty = _empty_descriptor()
            empty["found"] = True
            empty["kind"] = "repo_json"
            empty["path"] = CHILD_REPO_RELATIVE_PATH.as_posix()
            empty["error"] = error
            return empty
        return _normalize_repo_json(payload, CHILD_REPO_RELATIVE_PATH.as_posix())
    if source_json.exists():
        payload, error = _read_json(source_json)
        if error:
            empty = _empty_descriptor()
            empty["found"] = True
            empty["kind"] = "legacy_source"
            empty["path"] = LEGACY_SITE_RELATIVE_PATH.as_posix()
            empty["error"] = error
            return empty
        return _normalize_legacy_source(payload, LEGACY_SITE_RELATIVE_PATH.as_posix())
    return _empty_descriptor()


# ---------------------------------------------------------------------------
# Current-repo view, counts, summaries
# ---------------------------------------------------------------------------


def current_repo_view(
    *,
    registry: dict[str, Any],
    descriptor: dict[str, Any],
    git_remote: str = "",
) -> dict[str, Any]:
    """Resolve which topology entry corresponds to the current repo.

    Match priority: registry remote (normalized) → registry github_owner/repo_name
    → descriptor github_owner/repo_name. Returns role-neutral facts only.
    """
    git_full = normalize_remote(git_remote)
    matched_entry: dict[str, Any] | None = None
    match_source = "none"

    if registry.get("ok") and git_full:
        for entry in registry.get("repos", []):
            if entry.get("remote_full_name") == git_full:
                matched_entry = entry
                match_source = "registry_remote"
                break

    if matched_entry is None and registry.get("ok") and descriptor.get("found"):
        # Only match by descriptor handle when the descriptor itself names its
        # owner/repo. Falling back to the parent's owner combined with the
        # child's repo name would silently false-match unrelated registry
        # entries when a child repo lives in a different GitHub org.
        owner = descriptor.get("github_owner")
        repo_name = descriptor.get("repo_name")
        if owner and repo_name:
            target = f"{owner}/{repo_name}"
            for entry in registry.get("repos", []):
                if entry.get("remote_full_name") == target:
                    matched_entry = entry
                    match_source = "registry_owner_repo"
                    break

    if matched_entry is not None:
        parent_slug = matched_entry.get("parent") or ""
        parent_full = ""
        for entry in registry.get("repos", []):
            if entry.get("slug") == parent_slug:
                parent_full = entry.get("remote_full_name") or ""
                break
        return {
            "matched": True,
            "match_source": match_source,
            "slug": matched_entry.get("slug", ""),
            "role": matched_entry.get("role", ""),
            "lifecycle": matched_entry.get("lifecycle", ""),
            "visibility": matched_entry.get("visibility", ""),
            "display_name": matched_entry.get("display_name", ""),
            "github_owner": matched_entry.get("github_owner", ""),
            "repo_name": matched_entry.get("repo_name", ""),
            "remote_full_name": matched_entry.get("remote_full_name", ""),
            "domain": matched_entry.get("domain", ""),
            "parent_slug": parent_slug,
            "parent_remote_full_name": parent_full,
            "is_hub": bool(matched_entry.get("is_hub")),
            "registry_role_matches_descriptor": _registry_role_matches_descriptor(
                matched_entry, descriptor
            ),
        }

    if descriptor.get("found"):
        return {
            "matched": False,
            "match_source": "descriptor",
            "slug": "",
            "role": descriptor.get("role", ""),
            "lifecycle": "",
            "visibility": "",
            "display_name": descriptor.get("display_name", ""),
            "github_owner": descriptor.get("github_owner", ""),
            "repo_name": descriptor.get("repo_name", ""),
            "remote_full_name": descriptor.get("remote_full_name", ""),
            "domain": "",
            "parent_slug": "",
            "parent_remote_full_name": descriptor.get("parent", {}).get("remote_full_name", ""),
            "is_hub": False,
            "registry_role_matches_descriptor": None,
        }

    return {
        "matched": False,
        "match_source": "none",
        "slug": "",
        "role": "",
        "lifecycle": "",
        "visibility": "",
        "display_name": "",
        "github_owner": "",
        "repo_name": "",
        "remote_full_name": git_full,
        "domain": "",
        "parent_slug": "",
        "parent_remote_full_name": "",
        "is_hub": False,
        "registry_role_matches_descriptor": None,
    }


def _registry_role_matches_descriptor(
    entry: dict[str, Any], descriptor: dict[str, Any]
) -> bool | None:
    if not descriptor.get("found"):
        return None
    desc_role = _string(descriptor.get("role"))
    if not desc_role:
        return None
    return entry.get("role") == desc_role


def child_role_counts(
    registry: dict[str, Any],
    *,
    exclude_slug: str = "",
) -> dict[str, Any]:
    """Count child repos by role and lifecycle.

    The hub itself (``role == "business"`` or ``slug == exclude_slug``) is
    excluded so child counts describe operating surfaces, not the hub.
    """
    by_role: dict[str, dict[str, int]] = {}
    by_lifecycle: dict[str, int] = {}
    total = 0
    if not registry.get("ok"):
        return {"by_role": {}, "by_lifecycle": {}, "total": 0}
    for entry in registry.get("repos", []):
        slug = entry.get("slug", "")
        if slug == exclude_slug:
            continue
        if entry.get("role") == "business":
            continue
        role = entry.get("role") or "unknown"
        lifecycle = entry.get("lifecycle") or "unknown"
        bucket = by_role.setdefault(role, {})
        bucket[lifecycle] = bucket.get(lifecycle, 0) + 1
        by_lifecycle[lifecycle] = by_lifecycle.get(lifecycle, 0) + 1
        total += 1
    return {"by_role": by_role, "by_lifecycle": by_lifecycle, "total": total}


def restricted_repo_summary(registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Return safe boundary notes for non-public repos.

    Restricted/team-private/local-only repos are expected business boundaries,
    not warnings. Drift findings are emitted separately when the entry contains
    unsafe metadata.
    """
    notes: list[dict[str, Any]] = []
    if not registry.get("ok"):
        return notes
    for entry in registry.get("repos", []):
        visibility = entry.get("visibility", "")
        if visibility in {"public", ""}:
            continue
        notes.append(
            {
                "slug": entry.get("slug", ""),
                "display_name": entry.get("display_name", ""),
                "role": entry.get("role", ""),
                "visibility": visibility,
                "lifecycle": entry.get("lifecycle", ""),
                "purpose": entry.get("purpose", ""),
                "parent": entry.get("parent", ""),
                "safe_to_share": True,
            }
        )
    return notes


# ---------------------------------------------------------------------------
# Drift findings
# ---------------------------------------------------------------------------


def _has_unsafe_keys(entry: dict[str, Any]) -> list[str]:
    hits: list[str] = []
    for key in entry.get("extra_keys", []):
        if SECRET_KEY_RE.search(key) or UNSAFE_KEY_RE.search(key):
            hits.append(str(key))
    return sorted(set(hits))


def _has_absolute_path_value(entry: dict[str, Any]) -> bool:
    for field in ("purpose", "remote", "domain"):
        value = entry.get(field, "")
        if isinstance(value, str) and LOCAL_ABSOLUTE_PATH_RE.match(value):
            return True
    return False


def drift_findings(
    *,
    registry: dict[str, Any],
    descriptor: dict[str, Any],
    current_view: dict[str, Any],
) -> list[dict[str, Any]]:
    """Emit deterministic, public-safe drift findings.

    Findings are advisory: the doctor section formats them as preview-only
    actions. The reader never renames, deletes, or rewrites files.
    """
    findings: list[dict[str, Any]] = []

    registry_found = bool(registry.get("found"))
    registry_ok = bool(registry.get("ok"))

    if not registry_found:
        # Missing registry alone is informational; only escalates if a child
        # descriptor points to a hub that cannot be matched.
        if descriptor.get("found") and descriptor.get("parent", {}).get("remote_full_name"):
            findings.append(
                {
                    "code": "topology_descriptor_orphan",
                    "severity": "warn",
                    "summary": (
                        "child descriptor points to a hub but no "
                        "core/operations/repo-topology.md is present in this repo"
                    ),
                    "detail": (
                        "Open the hub repo and add the topology registry, or "
                        "remove the parent reference from the child descriptor"
                    ),
                    "repair_command": "mb status --json --peek",
                    "path": descriptor.get("path", ""),
                    "safe_to_share": True,
                }
            )
        else:
            findings.append(
                {
                    "code": "topology_registry_missing",
                    "severity": "info",
                    "summary": "no core/operations/repo-topology.md yet",
                    "detail": (
                        "topology is optional; add a registry when multiple "
                        "repos need a shared business map"
                    ),
                    "repair_command": "",
                    "path": REGISTRY_RELATIVE_PATH.as_posix(),
                    "safe_to_share": True,
                }
            )
        if descriptor.get("found") and not descriptor.get("ok"):
            findings.append(
                {
                    "code": "topology_descriptor_unparsable",
                    "severity": "warn",
                    "summary": "child descriptor present but could not be parsed",
                    "detail": str(descriptor.get("error") or ""),
                    "repair_command": "",
                    "path": descriptor.get("path", ""),
                    "safe_to_share": True,
                }
            )
        if descriptor.get("legacy_business_repo_present"):
            findings.append(
                {
                    "code": "topology_legacy_source_local_path",
                    "severity": "warn",
                    "summary": (
                        "legacy .mainbranch/source.json contains an absolute "
                        "business_repo path; review before sharing"
                    ),
                    "detail": (
                        "absolute paths are not copied into shareable topology "
                        "output; migrate to .mainbranch/repo.json when convenient"
                    ),
                    "repair_command": "",
                    "path": descriptor.get("path", ""),
                    "safe_to_share": True,
                }
            )
        return findings

    if not registry_ok:
        findings.append(
            {
                "code": "topology_registry_unparsable",
                "severity": "warn",
                "summary": (
                    f"core/operations/repo-topology.md present but unusable: "
                    f"{registry.get('error') or 'unknown error'}"
                ),
                "detail": "run `mb validate --json` for the schema-level reasons",
                "repair_command": "mb validate --json",
                "path": registry.get("path", ""),
                "safe_to_share": True,
            }
        )
        return findings

    # Registry exists and is parsable — check entry-level evidence.
    repos = registry.get("repos", [])
    slugs = {entry.get("slug") for entry in repos if entry.get("slug")}

    for entry in repos:
        prefix = f"repos[{entry.get('slug') or '?'}]"
        unsafe_keys = _has_unsafe_keys(entry)
        if unsafe_keys:
            findings.append(
                {
                    "code": "topology_repo_unsafe_keys",
                    "severity": "warn",
                    "summary": (f"{prefix} contains keys that look sensitive or machine-specific"),
                    "detail": (
                        f"unexpected keys: {', '.join(unsafe_keys)}; keep finance, "
                        "legal, customer, provider-cache, credential, and local-path "
                        "details out of the topology registry"
                    ),
                    "repair_command": "mb validate --json",
                    "path": registry.get("path", ""),
                    "safe_to_share": True,
                }
            )
        if _has_absolute_path_value(entry):
            findings.append(
                {
                    "code": "topology_repo_absolute_path",
                    "severity": "warn",
                    "summary": (f"{prefix} has a value that looks like a local absolute path"),
                    "detail": (
                        "keep durable topology on GitHub handles and business "
                        "relationships, not machine-specific paths"
                    ),
                    "repair_command": "mb validate --json",
                    "path": registry.get("path", ""),
                    "safe_to_share": True,
                }
            )
        if entry.get("linked_playbook_blueprints"):
            findings.append(
                {
                    "code": "topology_playbook_blueprint_reference",
                    "severity": "info",
                    "summary": (
                        f"{prefix} uses linked_playbooks; reusable playbook "
                        "blueprints belong in engine/package capability, not "
                        "business repo topology"
                    ),
                    "detail": (
                        "use linked_playbook_runs to link a specific "
                        "pushes/<push>/playbooks/<playbook>.md run record"
                    ),
                    "repair_command": "",
                    "path": registry.get("path", ""),
                    "safe_to_share": True,
                }
            )
        parent = entry.get("parent")
        if parent and parent not in slugs:
            findings.append(
                {
                    "code": "topology_parent_slug_unmatched",
                    "severity": "warn",
                    "summary": (
                        f"{prefix}.parent={parent!r} does not match any repo slug in the registry"
                    ),
                    "detail": ("parent slugs should reference another entry in repos[]"),
                    "repair_command": "mb validate --json",
                    "path": registry.get("path", ""),
                    "safe_to_share": True,
                }
            )

    # Descriptor cross-checks.
    if descriptor.get("found") and descriptor.get("ok"):
        desc_owner = descriptor.get("github_owner")
        desc_repo = descriptor.get("repo_name")
        desc_full = f"{desc_owner}/{desc_repo}" if desc_owner and desc_repo else ""
        parent = descriptor.get("parent", {})
        parent_full = parent.get("remote_full_name") or ""

        # Descriptor parent should resolve to a registry entry by handle.
        if parent_full:
            handles = {entry.get("remote_full_name") for entry in repos}
            if parent_full not in handles:
                findings.append(
                    {
                        "code": "topology_descriptor_parent_unmatched",
                        "severity": "warn",
                        "summary": (
                            "child descriptor parent does not match any "
                            "GitHub handle in the registry"
                        ),
                        "detail": (
                            "the descriptor names a hub repo that this "
                            "topology registry does not list"
                        ),
                        "repair_command": "",
                        "path": descriptor.get("path", ""),
                        "safe_to_share": True,
                    }
                )
        # Descriptor role should match registry entry for the same handle.
        if desc_full and current_view.get("matched"):
            mismatch = current_view.get("registry_role_matches_descriptor")
            if mismatch is False:
                findings.append(
                    {
                        "code": "topology_descriptor_role_mismatch",
                        "severity": "warn",
                        "summary": (
                            "child descriptor role does not match the role "
                            "recorded for this repo in the hub topology"
                        ),
                        "detail": (
                            f"descriptor role={descriptor.get('role')!r}, "
                            f"registry role={current_view.get('role')!r}"
                        ),
                        "repair_command": "",
                        "path": descriptor.get("path", ""),
                        "safe_to_share": True,
                    }
                )
        if descriptor.get("legacy_business_repo_present"):
            findings.append(
                {
                    "code": "topology_legacy_source_local_path",
                    "severity": "warn",
                    "summary": (
                        "legacy .mainbranch/source.json contains an absolute business_repo path"
                    ),
                    "detail": (
                        "absolute paths are not copied into shareable topology "
                        "output; migrate to .mainbranch/repo.json when convenient"
                    ),
                    "repair_command": "",
                    "path": descriptor.get("path", ""),
                    "safe_to_share": True,
                }
            )
    elif descriptor.get("found") and not descriptor.get("ok"):
        findings.append(
            {
                "code": "topology_descriptor_unparsable",
                "severity": "warn",
                "summary": "child descriptor present but could not be parsed",
                "detail": str(descriptor.get("error") or ""),
                "repair_command": "",
                "path": descriptor.get("path", ""),
                "safe_to_share": True,
            }
        )

    return findings


# ---------------------------------------------------------------------------
# Top-level view used by status / graph / doctor
# ---------------------------------------------------------------------------


def collect(
    repo: str | Path,
    *,
    git_remote: str = "",
) -> dict[str, Any]:
    """Build the public-safe topology view for a repo.

    Local-machine facts (e.g. absolute clone path) belong to callers, not this
    payload. The returned dict can be embedded in JSON intended for any consumer
    that already has access to the hub repo.
    """
    repo_path = Path(repo).resolve()
    registry = read_registry(repo_path)
    descriptor = read_child_descriptor(repo_path)
    view = current_repo_view(
        registry=registry,
        descriptor=descriptor,
        git_remote=git_remote,
    )
    exclude_slug = str(view.get("slug") or "") if view.get("matched") and view.get("is_hub") else ""
    counts = child_role_counts(registry, exclude_slug=exclude_slug)
    boundary_notes = restricted_repo_summary(registry)
    findings = drift_findings(
        registry=registry,
        descriptor=descriptor,
        current_view=view,
    )
    summary = {
        "registry_found": bool(registry.get("found")),
        "registry_ok": bool(registry.get("ok")),
        "descriptor_found": bool(descriptor.get("found")),
        "descriptor_kind": descriptor.get("kind", ""),
        "current_repo_matched": bool(view.get("matched")),
        "child_repo_count": counts.get("total", 0),
        "restricted_repo_count": len(boundary_notes),
        "findings": len(findings),
        "warnings": sum(1 for f in findings if f.get("severity") == "warn"),
        "errors": sum(1 for f in findings if f.get("severity") == "error"),
    }
    return {
        "schema": "mb.topology.view.v0",
        "summary": summary,
        "registry": {
            "found": registry.get("found"),
            "ok": registry.get("ok"),
            "path": registry.get("path"),
            "error": registry.get("error"),
            "schema": registry.get("schema"),
            "status": registry.get("status"),
            "home": registry.get("home"),
            "home_full_name": registry.get("home_full_name"),
            "business_display_name": registry.get("business_display_name"),
            "repos": registry.get("repos", []),
        },
        "descriptor": descriptor,
        "current_repo": view,
        "child_counts": counts,
        "restricted_repos": boundary_notes,
        "findings": findings,
        "safe_to_share": True,
    }
