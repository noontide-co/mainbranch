"""``mb graph`` — build a deterministic repo graph index and DOT view."""

from __future__ import annotations

import platform
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

from mb import pushes as pushes_mod
from mb import relationships

INDEX_VERSION = 1
EdgeKey = tuple[str, str, str, tuple[tuple[str, str], ...]]

LINK_FIELDS = relationships.RELATIONSHIP_FIELDS

ENTITY_FIELDS = {
    "people": "person",
    "person": "person",
    "companies": "company",
    "company": "company",
    "offers": "offer",
    "offer": "offer",
    "channels": "channel",
    "channel": "channel",
    "competitors": "competitor",
    "competitor": "competitor",
    "metrics": "metric",
    "metric": "metric",
}

ENTITY_TAG_TYPES = {
    "person": "person",
    "people": "person",
    "company": "company",
    "companies": "company",
    "offer": "offer",
    "offers": "offer",
    "channel": "channel",
    "channels": "channel",
    "competitor": "competitor",
    "competitors": "competitor",
    "metric": "metric",
    "metrics": "metric",
}

ENTITY_HASHTAG_RE = re.compile(
    r"(?<![\w/])#("
    + "|".join(sorted(ENTITY_TAG_TYPES))
    + r")/([A-Za-z0-9][A-Za-z0-9_-]*(?:/[A-Za-z0-9][A-Za-z0-9_-]*)*)"
)


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
    return data if isinstance(data, dict) else {}, body


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


def _iter_markdown_files(repo: Path) -> list[Path]:
    return [
        path
        for path in sorted(repo.rglob("*.md"))
        if path.is_file() and not _is_hidden_or_generated(path, repo)
    ]


def _coerce_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _file_id(path: Path, repo: Path) -> str:
    return f"file:{path.relative_to(repo).as_posix()}"


def _external_id(ref: str) -> str:
    return f"external:{_slug(ref)}"


def _entity_id(entity_type: str, value: str) -> str:
    return f"{entity_type}:{_slug(value)}"


def _slug(value: str) -> str:
    lowered = value.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "unknown"


def _label_from_value(value: str) -> str:
    clean = value.strip().replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", clean).strip() or "unknown"


def _node_sort_key(node: dict[str, Any]) -> tuple[str, str]:
    return (str(node["type"]), str(node["id"]))


def _edge_sort_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (str(edge["source"]), str(edge["target"]), str(edge["type"]))


def _add_node(nodes: dict[str, dict[str, Any]], node: dict[str, Any]) -> None:
    existing = nodes.get(str(node["id"]))
    if existing is None:
        nodes[str(node["id"])] = node
        return
    existing_metadata = existing.setdefault("metadata", {})
    for key, value in node.get("metadata", {}).items():
        if key not in existing_metadata:
            existing_metadata[key] = value


def _add_edge(
    edges: list[dict[str, Any]],
    seen_edges: set[EdgeKey],
    *,
    source: str,
    target: str,
    edge_type: str,
    evidence: dict[str, str],
) -> None:
    key = (source, target, edge_type, tuple(sorted(evidence.items())))
    if key in seen_edges:
        return
    seen_edges.add(key)
    original_field = evidence.get("field") or evidence.get("kind") or edge_type
    source_path = evidence.get("path")
    edge = {
        "source": source,
        "target": target,
        "type": edge_type,
        "rel_type": relationships.normalize_relationship(
            original_field,
            source_path=source_path,
            fallback=edge_type,
        ),
        "original_field": original_field,
        "evidence": evidence,
    }
    edges.append(edge)


def _frontmatter_summary(frontmatter: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in (
        "title",
        "topic",
        "type",
        "slug",
        "kind",
        "status",
        "health",
        "date",
        "source",
        "owner",
        "audience",
        "offer",
        "promise",
    ):
        if key in frontmatter and isinstance(frontmatter[key], str):
            summary[key] = frontmatter[key]
    return summary


def _label_for_file(path: Path, repo: Path, frontmatter: dict[str, Any]) -> str:
    for key in ("title", "topic", "slug"):
        value = frontmatter.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return path.relative_to(repo).as_posix()


def _resolve_repo_ref(repo: Path, ref: str) -> Path | None:
    clean_ref = relationships.clean_ref(ref)
    if not clean_ref:
        return None
    target = (repo / clean_ref).resolve()
    try:
        target.relative_to(repo)
    except ValueError:
        return None
    return target


def _resolve_wikilink(
    *,
    repo: Path,
    target: str,
    files_by_stem: dict[str, list[Path]],
    files_by_rel: dict[str, Path],
) -> Path | None:
    clean = relationships.wikilink_target(target)
    if not clean:
        return None
    candidates = [clean]
    if not clean.endswith(".md"):
        candidates.append(f"{clean}.md")
    for candidate in candidates:
        direct = files_by_rel.get(candidate)
        if direct is not None:
            return direct
        repo_direct = _resolve_repo_ref(repo, candidate)
        if repo_direct is not None and repo_direct.exists():
            return repo_direct
    stem = Path(clean).stem
    matches = files_by_stem.get(stem, [])
    if len(matches) == 1:
        return matches[0]
    return None


def _add_reference_edge(
    *,
    repo: Path,
    nodes: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
    seen_edges: set[EdgeKey],
    source_id: str,
    ref: str,
    edge_type: str,
    evidence: dict[str, str],
) -> None:
    target = _resolve_repo_ref(repo, ref)
    if target is not None and target.exists():
        target_id = _file_id(target, repo)
        if target_id not in nodes:
            _add_node(
                nodes,
                {
                    "id": target_id,
                    "type": "file",
                    "label": target.relative_to(repo).as_posix(),
                    "path": target.relative_to(repo).as_posix(),
                    "metadata": {},
                },
            )
    elif relationships.is_external_ref(ref):
        target_id = _external_id(ref)
        _add_node(
            nodes,
            {
                "id": target_id,
                "type": "external",
                "label": ref,
                "metadata": {"ref": ref},
            },
        )
    else:
        target_id = f"missing:{_slug(ref)}"
        _add_node(
            nodes,
            {
                "id": target_id,
                "type": "missing",
                "label": ref,
                "metadata": {"ref": ref},
            },
        )
    _add_edge(
        edges,
        seen_edges,
        source=source_id,
        target=target_id,
        edge_type=edge_type,
        evidence=evidence,
    )


def _iter_entity_values(frontmatter: dict[str, Any], body: str) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    for field, entity_type in ENTITY_FIELDS.items():
        for value in _coerce_strings(frontmatter.get(field)):
            found.append((entity_type, value, field))
    for tag in _coerce_strings(frontmatter.get("tags")):
        if ":" not in tag:
            continue
        prefix, value = tag.split(":", 1)
        tag_entity_type = ENTITY_TAG_TYPES.get(prefix.strip().lower())
        if tag_entity_type is not None and value.strip():
            found.append((tag_entity_type, value, "tags"))
    for match in ENTITY_HASHTAG_RE.finditer(body):
        entity_type = ENTITY_TAG_TYPES[match.group(1).lower()]
        value = match.group(2).replace("/", " ")
        found.append((entity_type, value, "hashtag"))
    return found


def _iter_provider_refs(frontmatter: dict[str, Any]) -> list[tuple[str, list[str]]]:
    provider_refs = frontmatter.get("provider_refs")
    if not isinstance(provider_refs, dict):
        return []
    found: list[tuple[str, list[str]]] = []
    for provider, refs in provider_refs.items():
        if not isinstance(provider, str) or not provider.strip():
            continue
        ref_kinds: list[str] = []
        if isinstance(refs, dict):
            ref_kinds = sorted(str(key) for key in refs if isinstance(key, str))
        elif isinstance(refs, list):
            for item in refs:
                if isinstance(item, dict):
                    ref_kinds.extend(str(key) for key in item if isinstance(key, str))
        found.append((provider, sorted(set(ref_kinds))))
    return found


def build_index(path: str) -> dict[str, Any]:
    """Build the machine-readable repo graph index."""
    repo = Path(path).resolve()
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    seen_edges: set[EdgeKey] = set()
    files = _iter_markdown_files(repo) if repo.exists() else []
    files_by_stem: dict[str, list[Path]] = {}
    files_by_rel: dict[str, Path] = {}

    for file_path in files:
        rel = file_path.relative_to(repo).as_posix()
        files_by_rel[rel] = file_path
        files_by_stem.setdefault(file_path.stem, []).append(file_path)

    file_records: dict[Path, tuple[dict[str, Any], str]] = {}
    for file_path in files:
        text = _read_text(file_path)
        if text is None:
            continue
        frontmatter, body = _split_frontmatter(text)
        file_records[file_path] = (frontmatter, body)
        file_id = _file_id(file_path, repo)
        rel = file_path.relative_to(repo).as_posix()
        _add_node(
            nodes,
            {
                "id": file_id,
                "type": "file",
                "label": _label_for_file(file_path, repo, frontmatter),
                "path": rel,
                "metadata": {
                    "frontmatter": _frontmatter_summary(frontmatter),
                    "section": file_path.relative_to(repo).parts[0],
                },
            },
        )

    for file_path, (frontmatter, body) in file_records.items():
        source_id = _file_id(file_path, repo)
        source_rel = file_path.relative_to(repo).as_posix()

        for field in relationships.relationship_fields_for_source(source_rel):
            for ref in _coerce_strings(frontmatter.get(field)):
                _add_reference_edge(
                    repo=repo,
                    nodes=nodes,
                    edges=edges,
                    seen_edges=seen_edges,
                    source_id=source_id,
                    ref=ref,
                    edge_type=field,
                    evidence={"kind": "frontmatter", "field": field, "path": source_rel},
                )

        body_without_code = relationships.strip_markdown_code(body)

        for match in relationships.WIKILINK_RE.finditer(body_without_code):
            raw_target = match.group(1)
            resolved = _resolve_wikilink(
                repo=repo,
                target=raw_target,
                files_by_stem=files_by_stem,
                files_by_rel=files_by_rel,
            )
            if resolved is None:
                target_ref = relationships.wikilink_target(raw_target)
                target_id = f"wikilink:{_slug(target_ref)}"
                _add_node(
                    nodes,
                    {
                        "id": target_id,
                        "type": "wikilink",
                        "label": target_ref,
                        "metadata": {"ref": target_ref},
                    },
                )
            else:
                target_id = _file_id(resolved, repo)
            _add_edge(
                edges,
                seen_edges,
                source=source_id,
                target=target_id,
                edge_type="wikilink",
                evidence={"kind": "wikilink", "target": raw_target, "path": source_rel},
            )

        for _, raw_target in relationships.iter_markdown_links(body_without_code):
            clean_target = relationships.markdown_link_target(raw_target)
            if not clean_target:
                continue
            if relationships.is_external_ref(clean_target):
                target_id = _external_id(clean_target)
                _add_node(
                    nodes,
                    {
                        "id": target_id,
                        "type": "external",
                        "label": clean_target,
                        "metadata": {"ref": clean_target},
                    },
                )
            elif relationships.is_local_markdown_ref(clean_target):
                resolved = relationships.resolve_markdown_link(repo, file_path, clean_target)
                if resolved is None:
                    target_id = f"missing:{_slug(clean_target)}"
                    _add_node(
                        nodes,
                        {
                            "id": target_id,
                            "type": "missing",
                            "label": clean_target,
                            "metadata": {"ref": clean_target},
                        },
                    )
                else:
                    target_id = _file_id(resolved, repo)
            else:
                continue
            _add_edge(
                edges,
                seen_edges,
                source=source_id,
                target=target_id,
                edge_type="markdown_link",
                evidence={"kind": "markdown_link", "target": clean_target, "path": source_rel},
            )

        for provider, ref_kinds in _iter_provider_refs(frontmatter):
            target_id = f"provider:{_slug(provider)}"
            _add_node(
                nodes,
                {
                    "id": target_id,
                    "type": "provider",
                    "label": _label_from_value(provider),
                    "metadata": {
                        "provider": provider,
                        "ref_kinds": ref_kinds,
                        "exposes_raw_values": False,
                    },
                },
            )
            _add_edge(
                edges,
                seen_edges,
                source=source_id,
                target=target_id,
                edge_type="provider_refs",
                evidence={
                    "kind": "frontmatter",
                    "field": "provider_refs",
                    "path": source_rel,
                    "provider": provider,
                    "ref_kinds": ",".join(ref_kinds),
                },
            )

        for entity_type, value, source in _iter_entity_values(frontmatter, body_without_code):
            target_id = _entity_id(entity_type, value)
            _add_node(
                nodes,
                {
                    "id": target_id,
                    "type": entity_type,
                    "label": _label_from_value(value),
                    "metadata": {"canonical": _slug(value)},
                },
            )
            _add_edge(
                edges,
                seen_edges,
                source=source_id,
                target=target_id,
                edge_type="mentions",
                evidence={"kind": "entity", "field": source, "path": source_rel},
            )

    sorted_nodes = sorted(nodes.values(), key=_node_sort_key)
    sorted_edges = sorted(edges, key=_edge_sort_key)
    push_facts = pushes_mod.facts(repo)
    entity_counts = {
        entity_type: sum(1 for node in sorted_nodes if node["type"] == entity_type)
        for entity_type in sorted(set(ENTITY_TAG_TYPES.values()))
    }
    return {
        "version": INDEX_VERSION,
        "registry": relationships.registry_payload(),
        "repo": str(repo),
        "nodes": sorted_nodes,
        "edges": sorted_edges,
        "summary": {
            "files": sum(1 for node in sorted_nodes if node["type"] == "file"),
            "nodes": len(sorted_nodes),
            "edges": len(sorted_edges),
            "entities": entity_counts,
            "push_count": push_facts["count"],
            "canonical_push_count": push_facts["canonical_count"],
            "legacy_campaign_count": push_facts["legacy_campaign_count"],
        },
        "pushes": push_facts["records"],
        "active_pushes": push_facts["active"],
        "push_count": push_facts["count"],
        "canonical_push_count": push_facts["canonical_count"],
        "campaigns": push_facts["legacy_campaigns"],
        "active_campaigns": push_facts["active_legacy_campaigns"],
        "campaign_count": push_facts["legacy_campaign_count"],
        "deprecated_campaign_keys": True,
        "push_compatibility": push_facts["compatibility"],
    }


def _dot_id(node_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", node_id)


def _dot_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def build_dot(path: str) -> str:
    """Build DOT output as a string."""
    return index_to_dot(build_index(path))


def index_to_dot(index: dict[str, Any]) -> str:
    """Render a graph index as Graphviz DOT."""
    lines = ["digraph mb {", '  rankdir="LR";', '  node [shape=box, fontname="Helvetica"];']
    for node in index["nodes"]:
        attrs = [f"label={_dot_quote(str(node['label']))}"]
        if node["type"] != "file":
            attrs.append("shape=ellipse")
        lines.append(f"  {_dot_id(str(node['id']))} [{', '.join(attrs)}];")
    for edge in index["edges"]:
        style = "dashed" if edge["type"] == "supersedes" else "solid"
        lines.append(
            "  "
            f"{_dot_id(str(edge['source']))} -> {_dot_id(str(edge['target']))} "
            f"[label={_dot_quote(str(edge['type']))}, style={style}];"
        )
    lines.append("}")
    return "\n".join(lines) + "\n"


def open_dot(dot: str) -> None:
    """Render DOT to PNG and open it."""
    if not shutil.which("dot"):
        raise RuntimeError("graphviz `dot` not on PATH (brew install graphviz)")
    if platform.system() == "Windows":
        raise RuntimeError("--open is unsupported on Windows")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        png_path = f.name
    proc = subprocess.run(
        ["dot", "-Tpng", "-o", png_path],
        input=dot,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"dot failed: {proc.stderr}")
    opener = "open" if platform.system() == "Darwin" else "xdg-open"
    subprocess.run([opener, png_path], check=False)
