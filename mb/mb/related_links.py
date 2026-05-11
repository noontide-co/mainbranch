"""Related-links mirror helpers for validation and doctor repair."""

from __future__ import annotations

import posixpath
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from mb import relationships

RELATED_HEADING_RE = re.compile(r"^##\s+Related links\s*$", re.IGNORECASE)
SECTION_BOUNDARY_RE = re.compile(r"^#{1,2}\s+\S")
MISSING_RELATED_LINK_MIRROR_CATEGORY = "missing_related_link_mirror"


@dataclass(frozen=True)
class MirrorRef:
    """A frontmatter relationship that can be mirrored in the body."""

    field: str
    target: str
    key: str
    href: str
    label: str


@dataclass(frozen=True)
class MarkdownIndex:
    """Markdown lookup tables shared across one repo scan."""

    files: tuple[Path, ...]
    by_rel: dict[str, Path]
    by_stem: dict[str, list[Path]]


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


def _read_frontmatter_and_body(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None, ""
    if not text.startswith("---"):
        return None, text
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return None, text
    try:
        parsed = yaml.safe_load(text[3:end].lstrip("\n")) or {}
    except yaml.YAMLError:
        return None, text[end + len("\n---") :]
    return parsed if isinstance(parsed, dict) else None, text[end + len("\n---") :]


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


def _markdown_files(repo: Path) -> tuple[Path, ...]:
    return tuple(
        path
        for path in sorted(repo.rglob("*.md"))
        if path.is_file() and not _is_hidden_or_generated(path, repo)
    )


def _title_from_file(path: Path) -> str:
    fm, body = _read_frontmatter_and_body(path)
    if fm:
        for key in ("title", "topic", "name", "slug"):
            value = fm.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    for line in body.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return path.stem.replace("-", " ").strip().title() or path.name


def _relative_href(source: Path, target: Path) -> str:
    rel = posixpath.relpath(target.as_posix(), start=source.parent.as_posix())
    return rel if rel != "." else target.name


def _section_bounds(body: str) -> tuple[int, int] | None:
    lines = body.splitlines(keepends=True)
    start = None
    for index, line in enumerate(lines):
        if RELATED_HEADING_RE.match(line.strip()):
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if SECTION_BOUNDARY_RE.match(lines[index].strip()):
            end = index
            break
    return start, end


def _section_text(body: str) -> str:
    bounds = _section_bounds(body)
    if bounds is None:
        return ""
    start, end = bounds
    return "".join(body.splitlines(keepends=True)[start + 1 : end])


def markdown_index(repo: Path, files: Iterable[Path] | None = None) -> MarkdownIndex:
    by_rel: dict[str, Path] = {}
    by_stem: dict[str, list[Path]] = {}
    indexed_files = tuple(files) if files is not None else _markdown_files(repo)
    for path in indexed_files:
        by_rel[path.relative_to(repo).as_posix()] = path
        by_stem.setdefault(path.stem, []).append(path)
    return MarkdownIndex(files=indexed_files, by_rel=by_rel, by_stem=by_stem)


def resolve_wikilink(
    target: str,
    *,
    repo: Path,
    files_by_rel: dict[str, Path],
    files_by_stem: dict[str, list[Path]],
) -> Path | None:
    clean = relationships.wikilink_target(target)
    if not clean:
        return None
    candidates = [clean]
    if not clean.endswith(".md"):
        candidates.append(f"{clean}.md")
    for candidate in candidates:
        if candidate in files_by_rel:
            return files_by_rel[candidate]
    if len(Path(clean).parts) > 1:
        return None
    matches = files_by_stem.get(Path(clean).stem, [])
    return matches[0] if len(matches) == 1 else None


def related_section_targets(
    repo: Path,
    source: Path,
    body: str,
    *,
    index: MarkdownIndex | None = None,
) -> set[str]:
    """Return repo-relative target keys already mirrored in ``## Related links``."""

    section = relationships.strip_markdown_code(_section_text(body))
    if not section:
        return set()
    targets: set[str] = set()
    lookup = index or markdown_index(repo)
    for _, raw_target in relationships.iter_markdown_links(section):
        clean = relationships.markdown_link_target(raw_target)
        if not clean:
            continue
        if relationships.is_external_ref(clean):
            targets.add(clean)
            continue
        resolved = relationships.resolve_markdown_link(repo, source, clean)
        if resolved is not None:
            targets.add(resolved.relative_to(repo).as_posix())
    for match in relationships.WIKILINK_RE.finditer(section):
        resolved = resolve_wikilink(
            match.group(1),
            repo=repo,
            files_by_rel=lookup.by_rel,
            files_by_stem=lookup.by_stem,
        )
        if resolved is not None:
            targets.add(resolved.relative_to(repo).as_posix())
    return targets


def frontmatter_mirror_refs(repo: Path, source: Path, fm: dict[str, Any]) -> list[MirrorRef]:
    """Return frontmatter relationship refs that are safe to mirror in the body."""

    source_rel = source.relative_to(repo).as_posix()
    refs: list[MirrorRef] = []
    seen: set[tuple[str, str]] = set()
    for field in relationships.relationship_fields_for_source(source_rel):
        if field not in fm:
            continue
        raw_refs, valid_type = _coerce_refs(fm.get(field))
        if not valid_type:
            continue
        for raw_ref in raw_refs:
            clean = relationships.clean_ref(raw_ref)
            if not clean:
                continue
            if relationships.is_external_ref(clean):
                continue
            target = (repo / clean).resolve()
            try:
                target.relative_to(repo)
            except ValueError:
                continue
            if not target.is_file():
                continue
            key = target.relative_to(repo).as_posix()
            if (field, key) in seen:
                continue
            seen.add((field, key))
            refs.append(
                MirrorRef(
                    field=field,
                    target=raw_ref,
                    key=key,
                    href=_relative_href(source, target),
                    label=_title_from_file(target),
                )
            )
    return refs


def missing_mirror_refs(
    repo: Path,
    source: Path,
    fm: dict[str, Any],
    body: str,
    *,
    index: MarkdownIndex | None = None,
) -> list[MirrorRef]:
    mirrored = related_section_targets(repo, source, body, index=index)
    return [ref for ref in frontmatter_mirror_refs(repo, source, fm) if ref.key not in mirrored]


def plan(repo: str | Path = ".") -> dict[str, Any]:
    """Plan Related links mirror repairs without writing files."""

    root = Path(repo).expanduser().resolve()
    index = markdown_index(root)
    files: list[dict[str, Any]] = []
    total_missing = 0
    for path in index.files:
        fm, body = _read_frontmatter_and_body(path)
        if fm is None:
            continue
        missing = missing_mirror_refs(root, path, fm, body, index=index)
        if not missing:
            continue
        total_missing += len(missing)
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "missing": [
                    {
                        "field": ref.field,
                        "target": ref.key,
                        "href": ref.href,
                        "label": ref.label,
                        "line": f"- [{ref.label}]({ref.href})",
                    }
                    for ref in missing
                ],
                "has_related_links": _section_bounds(body) is not None,
            }
        )
    return {
        "ok": total_missing == 0,
        "repo": str(root),
        "files": files,
        "summary": {
            "files": len(files),
            "missing_links": total_missing,
        },
        "safe_to_apply": True,
    }


def _insert_missing_lines(body: str, lines_to_add: list[str]) -> str:
    bounds = _section_bounds(body)
    addition = "\n".join(lines_to_add) + "\n"
    if bounds is None:
        prefix = "" if not body or body.endswith("\n") else "\n"
        return f"{body}{prefix}\n## Related links\n\n{addition}"

    lines = body.splitlines(keepends=True)
    _start, end = bounds
    insert_at = end
    prefix = ""
    if insert_at > 0 and lines[insert_at - 1].strip():
        prefix = "\n"
    suffix = "" if insert_at >= len(lines) or not lines[insert_at].strip() else "\n"
    lines[insert_at:insert_at] = [prefix + addition + suffix]
    return "".join(lines)


def apply(repo: str | Path = ".") -> dict[str, Any]:
    """Apply safe Related links mirror repairs from frontmatter."""

    root = Path(repo).expanduser().resolve()
    repair_plan = plan(root)
    changed: list[dict[str, Any]] = []
    errors: list[str] = []
    planned_by_path = {item["path"]: item for item in repair_plan["files"]}
    for rel, item in planned_by_path.items():
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{rel}: {exc}")
            continue
        body_start = 0
        if text.startswith("---"):
            try:
                body_start = text.index("\n---", 3) + len("\n---")
            except ValueError:
                errors.append(f"{rel}: unterminated frontmatter")
                continue
        prefix = text[:body_start]
        body = text[body_start:]
        missing_lines = [str(entry["line"]) for entry in item["missing"]]
        updated = prefix + _insert_missing_lines(body, missing_lines)
        if updated == text:
            continue
        try:
            path.write_text(updated, encoding="utf-8")
        except OSError as exc:
            errors.append(f"{rel}: {exc}")
            continue
        changed.append(
            {
                "path": rel,
                "added": missing_lines,
                "created_section": not bool(item["has_related_links"]),
            }
        )
    return {
        "ok": not errors,
        "repo": str(root),
        "planned": repair_plan,
        "changed": changed,
        "errors": errors,
        "summary": {
            "files_changed": len(changed),
            "links_added": sum(len(item["added"]) for item in changed),
            "errors": len(errors),
        },
    }
