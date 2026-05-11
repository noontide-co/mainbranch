"""Read-only relationship suggestions for business repo files."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

from mb import graph, related_links, relationships

SCHEMA_VERSION = "1.0"
MATRIX_DOC = "docs/business-connections.md"

ACTION_TYPED = "add_typed_frontmatter_link"
ACTION_INLINE = "add_inline_markdown_link"
ACTION_ENTITY = "add_entity_tag"
ACTION_DATA = "link_report_or_data_metadata"
ACTION_CONTEXT = "leave_nearby_context"
ACTION_IGNORE = "ignore"

ACTION_LABELS: dict[str, str] = {
    ACTION_TYPED: "add typed frontmatter link",
    ACTION_INLINE: "add inline Markdown link",
    ACTION_ENTITY: "add entity tag",
    ACTION_DATA: "link report or data metadata",
    ACTION_CONTEXT: "leave as nearby context",
    ACTION_IGNORE: "ignore",
}

STOPWORDS = {
    "about",
    "after",
    "again",
    "against",
    "also",
    "because",
    "before",
    "being",
    "business",
    "could",
    "decision",
    "decisions",
    "does",
    "files",
    "from",
    "have",
    "into",
    "links",
    "main",
    "markdown",
    "more",
    "needs",
    "note",
    "notes",
    "only",
    "other",
    "repo",
    "research",
    "should",
    "that",
    "their",
    "there",
    "these",
    "this",
    "through",
    "with",
}
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")


def _read_markdown(path: Path) -> tuple[dict[str, Any], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}, ""
    if not text.startswith("---"):
        return {}, text
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}, text
    try:
        parsed = yaml.safe_load(text[3:end].lstrip("\n")) or {}
    except yaml.YAMLError:
        return {}, text[end + len("\n---") :]
    frontmatter = parsed if isinstance(parsed, dict) else {}
    return frontmatter, text[end + len("\n---") :]


def _tokens(text: str) -> set[str]:
    return {
        token.replace("_", "-").lower()
        for token in TOKEN_RE.findall(text)
        if token.lower() not in STOPWORDS
    }


def _title(path: Path, frontmatter: dict[str, Any], body: str) -> str:
    for key in ("title", "topic", "name", "slug"):
        value = frontmatter.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for line in body.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return path.stem.replace("-", " ").strip().title() or path.name


def _phrase_variants(repo: Path, path: Path, title: str) -> set[str]:
    stem_words = path.stem.replace("-", " ").replace("_", " ").strip().lower()
    variants = {
        path.relative_to(repo).as_posix().lower(),
        path.stem.lower(),
        title.lower(),
        stem_words,
    }
    return {variant for variant in variants if variant}


def _mentioned(text: str, variants: set[str]) -> bool:
    lowered = text.lower()
    return any(variant in lowered for variant in variants if len(variant) >= 5)


def _coerce_refs(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _existing_frontmatter_targets(
    repo: Path,
    source: Path,
    frontmatter: dict[str, Any],
) -> set[str]:
    source_rel = source.relative_to(repo).as_posix()
    targets: set[str] = set()
    for field in relationships.relationship_fields_for_source(source_rel):
        for raw_ref in _coerce_refs(frontmatter.get(field)):
            clean = relationships.clean_ref(raw_ref)
            if not clean:
                continue
            if relationships.is_external_ref(clean):
                targets.add(clean)
                continue
            target = (repo / clean).resolve()
            try:
                rel = target.relative_to(repo).as_posix()
            except ValueError:
                continue
            targets.add(rel)
    return targets


def _existing_body_targets(
    repo: Path,
    source: Path,
    body: str,
    index: related_links.MarkdownIndex,
) -> set[str]:
    targets = related_links.related_section_targets(repo, source, body, index=index)
    body_without_code = relationships.strip_markdown_code(body)
    for _, raw_target in relationships.iter_markdown_links(body_without_code):
        clean = relationships.markdown_link_target(raw_target)
        if not clean or relationships.is_external_ref(clean):
            continue
        resolved = relationships.resolve_markdown_link(repo, source, clean)
        if resolved is not None:
            targets.add(resolved.relative_to(repo).as_posix())
    for match in relationships.WIKILINK_RE.finditer(body_without_code):
        resolved = related_links.resolve_wikilink(
            match.group(1),
            repo=repo,
            files_by_rel=index.by_rel,
            files_by_stem=index.by_stem,
        )
        if resolved is not None:
            targets.add(resolved.relative_to(repo).as_posix())
    return targets


def _field_for_target(rel_path: str) -> str | None:
    parts = Path(rel_path).parts
    if not parts:
        return None
    root = parts[0]
    if root == "bets":
        return "linked_bets"
    if root == "campaigns":
        return "linked_pushes"
    if root == "core" and len(parts) > 1 and parts[1] == "offers":
        return "linked_offers"
    if root == "decisions":
        return "linked_decisions"
    if root in {"docs", "documents"}:
        return "linked_docs"
    if root in {"log", "outcomes", "outputs"}:
        return "linked_outcomes"
    if root == "pushes":
        return "linked_pushes"
    if root == "research":
        return "linked_research"
    return None


def _is_data_or_report(rel_path: str, frontmatter: dict[str, Any]) -> bool:
    parts = Path(rel_path).parts
    if parts and parts[0] in {"data", "reports"}:
        return True
    item_type = frontmatter.get("type")
    return isinstance(item_type, str) and item_type in {"data_source", "dataset", "report"}


def _target_payload(rel_path: str, *, title: str, field: str | None = None) -> dict[str, Any]:
    target: dict[str, Any] = {"path": rel_path, "title": title}
    if field:
        target["field"] = field
    return target


def _suggestion(
    *,
    action: str,
    score: int,
    target: dict[str, Any],
    reasons: list[str],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "action": action,
        "action_label": ACTION_LABELS[action],
        "score": score,
        "target": target,
        "reasons": reasons,
        "evidence": evidence,
    }


def _candidate_suggestion(
    *,
    repo: Path,
    source_mention_text: str,
    source_tokens: set[str],
    existing_frontmatter_targets: set[str],
    existing_body_targets: set[str],
    target_path: Path,
) -> dict[str, Any]:
    rel_path = target_path.relative_to(repo).as_posix()
    target_frontmatter, target_body = _read_markdown(target_path)
    title = _title(target_path, target_frontmatter, target_body)
    field = _field_for_target(rel_path)
    mentioned = _mentioned(source_mention_text, _phrase_variants(repo, target_path, title))
    shared_tokens = sorted(source_tokens & _tokens(f"{rel_path}\n{title}\n{target_body[:2000]}"))[
        :8
    ]
    evidence = {
        "mentioned_by_name": mentioned,
        "shared_terms": shared_tokens,
    }

    if rel_path in existing_frontmatter_targets or rel_path in existing_body_targets:
        return _suggestion(
            action=ACTION_IGNORE,
            score=0,
            target=_target_payload(rel_path, title=title, field=field),
            reasons=[
                "This target is already connected in frontmatter or the body.",
                "Do not suggest duplicate links; use repair commands for missing mirrors.",
            ],
            evidence=evidence,
        )

    if _is_data_or_report(rel_path, target_frontmatter) and (mentioned or len(shared_tokens) >= 2):
        score = 82 if mentioned else min(70, 50 + len(shared_tokens) * 4)
        return _suggestion(
            action=ACTION_DATA,
            score=score,
            target=_target_payload(rel_path, title=title),
            reasons=[
                "The candidate looks like a report or data note.",
                "Connect it as evidence metadata instead of making raw data frontmatter truth.",
            ],
            evidence=evidence,
        )

    if field and mentioned and rel_path not in existing_frontmatter_targets:
        return _suggestion(
            action=ACTION_TYPED,
            score=90,
            target=_target_payload(rel_path, title=title, field=field),
            reasons=[
                f"The source directly names {title}.",
                f"`{field}` is the matching typed frontmatter field for this file family.",
            ],
            evidence=evidence,
        )

    if mentioned and rel_path not in existing_body_targets:
        return _suggestion(
            action=ACTION_INLINE,
            score=72,
            target=_target_payload(rel_path, title=title),
            reasons=[
                "The source directly names this file, but it is not a typed "
                "relationship candidate.",
                "An inline Markdown link keeps the sentence helpful for human readers.",
            ],
            evidence=evidence,
        )

    if field and len(shared_tokens) >= 3 and rel_path not in existing_frontmatter_targets:
        score = min(55, 25 + len(shared_tokens) * 5)
        return _suggestion(
            action=ACTION_CONTEXT,
            score=score,
            target=_target_payload(rel_path, title=title, field=field),
            reasons=[
                "The files share business terms, but the evidence is weak.",
                "Leave this as nearby context unless the operator confirms a real relationship.",
            ],
            evidence=evidence,
        )

    return _suggestion(
        action=ACTION_IGNORE,
        score=0,
        target=_target_payload(rel_path, title=title, field=field),
        reasons=["No strong name match, typed relationship, or useful shared evidence."],
        evidence=evidence,
    )


def _entity_suggestions(
    *,
    repo: Path,
    source_text: str,
    source_tokens: set[str],
    source_path: Path,
    files: tuple[Path, ...],
) -> list[dict[str, Any]]:
    existing_tags = {
        f"#{kind}/{slug}" for kind, slug in graph.ENTITY_HASHTAG_RE.findall(source_text)
    }
    discovered: dict[str, set[str]] = {}
    for path in files:
        if path == source_path:
            continue
        _, body = _read_markdown(path)
        for kind, slug in graph.ENTITY_HASHTAG_RE.findall(body):
            tag = f"#{kind}/{slug}"
            if tag in existing_tags:
                continue
            terms = _tokens(slug.replace("/", " ").replace("-", " "))
            if terms and terms.issubset(source_tokens):
                discovered.setdefault(tag, set()).add(path.relative_to(repo).as_posix())

    suggestions: list[dict[str, Any]] = []
    for tag, paths in sorted(discovered.items()):
        suggestions.append(
            _suggestion(
                action=ACTION_ENTITY,
                score=65,
                target={"tag": tag},
                reasons=[
                    f"The source names the entity terms for `{tag}`.",
                    "Use entity tags for recurring companies, offers, channels, "
                    "competitors, or metrics.",
                ],
                evidence={"seen_in": sorted(paths)[:5]},
            )
        )
    return suggestions


def suggest_links(
    source_file: str | Path,
    *,
    repo: str | Path = ".",
    limit: int = 10,
    include_ignored: bool = False,
) -> dict[str, Any]:
    """Return ranked link suggestions without editing files."""

    root = Path(repo).expanduser().resolve()
    source = Path(source_file).expanduser()
    if not source.is_absolute():
        source = root / source
    source = source.resolve()
    try:
        source_rel = source.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(f"{source_file} is outside repo {root}") from exc
    if not source.is_file():
        raise ValueError(f"{source_rel} does not exist")
    if source.suffix != ".md":
        raise ValueError(f"{source_rel} is not a Markdown file")

    index = related_links.markdown_index(root)
    source_frontmatter, source_body = _read_markdown(source)
    source_frontmatter_text = yaml.safe_dump(source_frontmatter, sort_keys=True)
    source_index_text = f"{source_rel}\n{source_frontmatter_text}\n{source_body}"
    source_mention_text = f"{source_rel}\n{source_body}"
    source_tokens = _tokens(source_index_text)
    existing_frontmatter = _existing_frontmatter_targets(root, source, source_frontmatter)
    existing_body = _existing_body_targets(root, source, source_body, index)

    ignored_count = 0
    suggestions: list[dict[str, Any]] = []
    for target_path in index.files:
        if target_path == source:
            continue
        candidate = _candidate_suggestion(
            repo=root,
            source_mention_text=source_mention_text,
            source_tokens=source_tokens,
            existing_frontmatter_targets=existing_frontmatter,
            existing_body_targets=existing_body,
            target_path=target_path,
        )
        if candidate["action"] == ACTION_IGNORE:
            ignored_count += 1
            if not include_ignored:
                continue
        suggestions.append(candidate)

    suggestions.extend(
        _entity_suggestions(
            repo=root,
            source_text=source_mention_text,
            source_tokens=source_tokens,
            source_path=source,
            files=index.files,
        )
    )
    suggestions.sort(key=lambda item: (-int(item["score"]), str(item["target"])))
    if limit >= 0:
        suggestions = suggestions[:limit]

    counts = Counter(str(item["action"]) for item in suggestions)
    return {
        "ok": True,
        "command": "mb suggest links",
        "schema_version": SCHEMA_VERSION,
        "repo": str(root),
        "source": source_rel,
        "matrix": {
            "doc": MATRIX_DOC,
            "actions": [{"id": action, "label": label} for action, label in ACTION_LABELS.items()],
        },
        "suggestions": suggestions,
        "summary": {
            "total": len(suggestions),
            "by_action": dict(sorted(counts.items())),
            "ignored_candidates": ignored_count,
            "writes": 0,
        },
        "safe_to_apply": False,
    }


def render_human(report: dict[str, Any]) -> None:
    """Print a compact human summary for terminal use."""

    console = Console()
    console.print(f"\n[bold]mb suggest links[/bold]  {report['source']}")
    console.print("No files were changed.\n")
    suggestions = report["suggestions"]
    if not suggestions:
        console.print("No useful link candidates found.")
        return
    for item in suggestions:
        target = item["target"]
        target_label = target.get("path") or target.get("tag") or "candidate"
        console.print(
            f"[bold]{item['score']:>3}[/bold]  {item['action_label']}  [cyan]{target_label}[/cyan]"
        )
        field = target.get("field")
        if field:
            console.print(f"     field: {field}")
        for reason in item["reasons"]:
            console.print(f"     - {reason}")
    console.print(f"\nDecision guide: {report['matrix']['doc']}")
