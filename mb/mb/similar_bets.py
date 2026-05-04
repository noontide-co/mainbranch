"""Deterministic similar-bets lookup for business repo memory."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import typer
import yaml

from mb import graph as graph_mod

SCHEMA_VERSION = "1.0"
MAX_BODY_CHARS = 8000
DOCUMENTED_BET_STATUSES = {"open", "paused", "closed", "canceled"}
DOCUMENTED_OFFER_STATUSES = {"proposed", "running", "scaling", "killed", "graduated", "died"}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "by",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "this",
    "to",
    "we",
    "with",
    "you",
    "your",
}


@dataclass(frozen=True)
class SourceRecord:
    source_type: str
    path: str
    title: str
    status: str
    outcome_bucket: str
    frontmatter: dict[str, Any]
    body: str
    metadata_terms: set[str]
    graph_terms: set[str]
    graph_paths: list[str]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return {}, text
    raw = text[3:end].strip()
    try:
        parsed = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}, text
    body = text[end + len("\n---") :]
    return parsed if isinstance(parsed, dict) else {}, body


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", value.lower())
        if token not in STOPWORDS
    }


def _coerce_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _all_frontmatter_text(frontmatter: dict[str, Any]) -> str:
    parts: list[str] = []
    for value in frontmatter.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(item for item in value if isinstance(item, str))
    return " ".join(parts)


def _metadata_terms(frontmatter: dict[str, Any]) -> set[str]:
    terms: set[str] = set()
    for field in (
        "status",
        "metric",
        "target",
        "result",
        "appetite",
        "hypothesis",
        "channels",
        "tags",
        "people",
        "companies",
        "offers",
        "offer",
        "metrics",
        "competitors",
    ):
        for value in _coerce_strings(frontmatter.get(field)):
            terms.update(_tokens(value))
    return terms


def _title_from_markdown(path: Path, frontmatter: dict[str, Any], body: str) -> str:
    for key in ("title", "name", "slug", "hypothesis"):
        value = frontmatter.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return path.stem.replace("-", " ")


def _offer_status(frontmatter: dict[str, Any], body: str) -> str:
    status = str(frontmatter.get("status", "") or "").strip()
    if status:
        return status
    lowered = body.lower()
    if "died" in lowered or "killed" in lowered:
        return "died"
    if "scaling" in lowered:
        return "scaling"
    return ""


def _outcome_bucket(source_type: str, status: str, frontmatter: dict[str, Any], body: str) -> str:
    text = " ".join(
        [
            status,
            str(frontmatter.get("result", "") or ""),
            body[:MAX_BODY_CHARS],
        ]
    ).lower()
    normalized_status = status.lower()
    if source_type == "offer":
        if normalized_status in {"died", "killed"}:
            return "killed"
        if normalized_status == "graduated":
            return "graduated"
        if normalized_status == "scaling":
            return "worked"
        if normalized_status in {"proposed", "running"}:
            return "active"
        return "unknown"
    if normalized_status == "canceled":
        return "killed"
    if normalized_status in {"open", "paused"}:
        return "active"
    if normalized_status == "closed" and str(frontmatter.get("result", "") or "").strip():
        if any(word in text for word in ("graduated", "became an offer", "became a workflow")):
            return "graduated"
        if any(
            word in text for word in ("failed", "missed", "lost", "did not", "didn't", "killed")
        ):
            return "failed"
        if any(
            word in text for word in ("worked", "hit", "won", "success", "profitable", "scaled")
        ):
            return "worked"
        return "evidence"
    return "unknown"


def _linked_files(frontmatter: dict[str, Any]) -> list[str]:
    links: list[str] = []
    for field in (
        "linked_decisions",
        "linked_research",
        "linked_campaigns",
        "linked_outcomes",
        "linked_bets",
        "related_prds",
        "linked_prds",
    ):
        for value in _coerce_strings(frontmatter.get(field)):
            if value not in links:
                links.append(value)
    return links


def _graph_terms_by_path(index: dict[str, Any]) -> dict[str, tuple[set[str], list[str]]]:
    node_labels: dict[str, str] = {
        str(node.get("id")): str(node.get("label") or "")
        for node in index.get("nodes", [])
        if isinstance(node, dict)
    }
    file_ids = {
        str(node.get("id")): str(node.get("path") or "")
        for node in index.get("nodes", [])
        if isinstance(node, dict) and node.get("type") == "file"
    }
    by_path: dict[str, tuple[set[str], list[str]]] = {}
    for edge in index.get("edges", []):
        if not isinstance(edge, dict):
            continue
        source = str(edge.get("source") or "")
        target = str(edge.get("target") or "")
        if source not in file_ids:
            continue
        rel = file_ids[source]
        terms, paths = by_path.setdefault(rel, (set(), []))
        label = node_labels.get(target, "")
        terms.update(_tokens(label))
        if target.startswith("file:"):
            target_path = target.removeprefix("file:")
            if target_path not in paths:
                paths.append(target_path)
    return by_path


def _iter_source_files(repo: Path) -> list[tuple[str, Path]]:
    sources: list[tuple[str, Path]] = []
    bets = repo / "bets"
    if bets.exists():
        sources.extend(("bet", path) for path in sorted(bets.glob("*.md")) if path.is_file())
    offers = repo / "core" / "offers"
    if offers.exists():
        sources.extend(
            ("offer", path) for path in sorted(offers.glob("*/offer.md")) if path.is_file()
        )
    return sources


def _records(repo: Path, graph_index: dict[str, Any]) -> list[SourceRecord]:
    graph_terms = _graph_terms_by_path(graph_index)
    records: list[SourceRecord] = []
    for source_type, path in _iter_source_files(repo):
        text = _read_text(path)
        frontmatter, body = _split_frontmatter(text)
        try:
            rel = path.relative_to(repo).as_posix()
        except ValueError:
            rel = str(path)
        title = _title_from_markdown(path, frontmatter, body)
        status = (
            _offer_status(frontmatter, body)
            if source_type == "offer"
            else str(frontmatter.get("status", "") or "").strip()
        )
        graph_record_terms, graph_paths = graph_terms.get(rel, (set(), []))
        records.append(
            SourceRecord(
                source_type=source_type,
                path=rel,
                title=title,
                status=status,
                outcome_bucket=_outcome_bucket(source_type, status, frontmatter, body),
                frontmatter=frontmatter,
                body=body[:MAX_BODY_CHARS],
                metadata_terms=_metadata_terms(frontmatter),
                graph_terms=graph_record_terms,
                graph_paths=graph_paths,
            )
        )
    return records


def _score_record(record: SourceRecord, query_tokens: set[str]) -> dict[str, Any] | None:
    if not query_tokens:
        return None
    text_terms = _tokens(
        " ".join(
            [
                record.title,
                _all_frontmatter_text(record.frontmatter),
                record.body,
            ]
        )
    )
    text_overlap = sorted(query_tokens & text_terms)
    metadata_overlap = sorted(query_tokens & record.metadata_terms)
    graph_overlap = sorted(query_tokens & record.graph_terms)
    if not text_overlap and not metadata_overlap and not graph_overlap:
        return None
    text_score = len(text_overlap) / len(query_tokens)
    metadata_score = len(metadata_overlap) / len(query_tokens)
    graph_score = len(graph_overlap) / len(query_tokens)
    has_outcome = record.outcome_bucket in {"worked", "failed", "graduated", "killed"}
    status_bonus = 0.08 if has_outcome else 0
    source_bonus = 0.05 if record.source_type == "bet" else 0.02
    score = round(
        text_score + (0.5 * metadata_score) + (0.35 * graph_score) + status_bonus + source_bonus,
        4,
    )
    why: list[str] = []
    if text_overlap:
        why.append(f"text overlap: {', '.join(text_overlap[:8])}")
    if metadata_overlap:
        why.append(f"metadata overlap: {', '.join(metadata_overlap[:8])}")
    if graph_overlap:
        why.append(f"graph overlap: {', '.join(graph_overlap[:8])}")
    if record.outcome_bucket not in {"active", "unknown"}:
        why.append(f"has outcome evidence: {record.outcome_bucket}")
    return {
        "score": score,
        "similarity": {
            "text_overlap": text_overlap,
            "metadata_overlap": metadata_overlap,
            "graph_overlap": graph_overlap,
        },
        "why": why,
    }


def _evidence(record: SourceRecord) -> dict[str, Any]:
    result = str(record.frontmatter.get("result", "") or "").strip()
    target = str(record.frontmatter.get("target", "") or "").strip()
    metric = str(record.frontmatter.get("metric", "") or "").strip()
    evidence_items: list[str] = []
    if target:
        evidence_items.append(f"target: {target}")
    if metric:
        evidence_items.append(f"metric: {metric}")
    if result:
        evidence_items.append(f"result: {result}")
    if record.status:
        evidence_items.append(f"status: {record.status}")
    return {
        "bucket": record.outcome_bucket,
        "status": record.status,
        "summary": evidence_items[:4],
    }


def run(path: str = ".", thesis: str = "", *, limit: int = 5) -> dict[str, Any]:
    """Find deterministic similar past bets and offer context."""
    repo = Path(path).resolve()
    graph_index = graph_mod.build_index(str(repo))
    records = _records(repo, graph_index)
    query_tokens = _tokens(thesis)
    matches: list[dict[str, Any]] = []
    for record in records:
        scored = _score_record(record, query_tokens)
        if scored is None:
            continue
        match = {
            "source_type": record.source_type,
            "path": record.path,
            "title": record.title,
            "status": record.status,
            "outcome_bucket": record.outcome_bucket,
            "evidence": _evidence(record),
            "linked_files": sorted(set(_linked_files(record.frontmatter) + record.graph_paths)),
            **scored,
        }
        matches.append(match)
    matches.sort(key=lambda item: (-float(item["score"]), str(item["path"])))
    selected = matches[: max(limit, 0)]
    outcome_counts = Counter(str(match["outcome_bucket"]) for match in selected)
    return {
        "schema_version": SCHEMA_VERSION,
        "schema": {
            "name": "mainbranch.similar_bets",
            "version": SCHEMA_VERSION,
            "compatibility": "v1 additions are additive; existing v1 keys must not change meaning.",
            "status_inputs": {
                "bets": sorted(DOCUMENTED_BET_STATUSES),
                "offers": sorted(DOCUMENTED_OFFER_STATUSES),
            },
            "outcome_bucket_note": (
                "Buckets summarize documented statuses plus result/body wording for closed bets."
            ),
        },
        "generated_at": _utc_now(),
        "repo": {"path": str(repo)},
        "thesis": thesis,
        "query": {"tokens": sorted(query_tokens)},
        "summary": {
            "records_scanned": len(records),
            "matches": len(selected),
            "bets": len([match for match in selected if match["source_type"] == "bet"]),
            "offers": len([match for match in selected if match["source_type"] == "offer"]),
            "worked": outcome_counts["worked"],
            "failed": outcome_counts["failed"],
            "graduated": outcome_counts["graduated"],
            "killed": outcome_counts["killed"],
        },
        "matches": selected,
    }


def render_human(report: dict[str, Any]) -> None:
    """Print concise terminal output for similar-bets results."""
    typer.echo(f"mb similar-bets  {json.dumps(report['thesis'])}")
    summary = report["summary"]
    typer.echo(
        f"{summary['matches']} match(es) from {summary['records_scanned']} record(s); "
        f"worked {summary['worked']}, failed {summary['failed']}, "
        f"graduated {summary['graduated']}, killed {summary['killed']}."
    )
    for match in report["matches"]:
        typer.echo(f"- {match['score']:.2f}  {match['path']}  [{match['outcome_bucket']}]")
        for reason in match["why"][:3]:
            typer.echo(f"  why: {reason}")
        for item in match["evidence"]["summary"][:2]:
            typer.echo(f"  evidence: {item}")
