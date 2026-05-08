"""Shared relationship registry for graph and validation surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

REGISTRY_VERSION = "0.1"


@dataclass(frozen=True)
class Relationship:
    """A frontmatter field that represents a typed relationship."""

    canonical_type: str
    fields: tuple[str, ...]
    description: str
    source_globs: tuple[str, ...] = ()
    legacy: bool = False

    @property
    def canonical_field(self) -> str:
        return self.fields[0]


RELATIONSHIPS: tuple[Relationship, ...] = (
    Relationship(
        canonical_type="bet",
        fields=("linked_bets",),
        description="Connects a file to a bet that frames or is affected by the work.",
    ),
    Relationship(
        canonical_type="research",
        fields=("linked_research",),
        description="Connects a file to research that supports or informs it.",
    ),
    Relationship(
        canonical_type="decision",
        fields=("linked_decisions", "linked_decision"),
        description="Connects a file to a decision that shaped it.",
        legacy=True,
    ),
    Relationship(
        canonical_type="push",
        fields=("linked_pushes", "linked_campaigns"),
        description="Connects a file to a coordinated push; linked_campaigns is legacy.",
        legacy=True,
    ),
    Relationship(
        canonical_type="outcome",
        fields=("linked_outcomes",),
        description="Connects a file to a result, review, log, or outcome artifact.",
    ),
    Relationship(
        canonical_type="document",
        fields=("linked_docs", "linked_documents"),
        description="Connects a file to supporting docs or documents.",
    ),
    Relationship(
        canonical_type="issue",
        fields=("linked_issues",),
        description="Connects a file to durable GitHub issue work threads.",
    ),
    Relationship(
        canonical_type="offer",
        fields=("linked_offers",),
        description="Connects a file to one or more business offers.",
    ),
    Relationship(
        canonical_type="offer",
        fields=("offer",),
        description="Connects a push to the offer it promotes.",
        source_globs=("pushes/*/push.md", "campaigns/*/campaign.md"),
    ),
    Relationship(
        canonical_type="playbook",
        fields=("linked_playbooks", "playbook"),
        description="Connects a file to a reusable playbook.",
        legacy=True,
    ),
    Relationship(
        canonical_type="strategy",
        fields=("linked_strategy", "linked_strategies"),
        description="Connects a file to strategy context.",
        legacy=True,
    ),
    Relationship(
        canonical_type="prd",
        fields=("linked_prds", "linked_prd", "related_prds"),
        description="Connects a file to PRDs or product direction docs.",
        legacy=True,
    ),
    Relationship(
        canonical_type="supersedes",
        fields=("supersedes",),
        description="Connects a newer artifact to the prior artifact it replaces.",
    ),
)

FIELD_TO_RELATIONSHIP: dict[str, Relationship] = {
    field: relationship for relationship in RELATIONSHIPS for field in relationship.fields
}
RELATIONSHIP_FIELDS: tuple[str, ...] = tuple(FIELD_TO_RELATIONSHIP)

BODY_LINK_REL_TYPE = "reference"
BODY_LINK_ORIGINAL_FIELDS = {"wikilink", "markdown_link"}
PROVIDER_REL_TYPE = "provider"
PROVIDER_ORIGINAL_FIELD = "provider_refs"


def relationship_for_field(field: str, *, source_path: str | None = None) -> Relationship | None:
    """Return the registry entry for a field when it applies to the source file."""

    relationship = FIELD_TO_RELATIONSHIP.get(field)
    if relationship is None:
        return None
    if source_path is None or not relationship.source_globs:
        return relationship
    path = PurePosixPath(source_path)
    if any(path.match(pattern) for pattern in relationship.source_globs):
        return relationship
    return None


def relationship_fields_for_source(source_path: str | None = None) -> tuple[str, ...]:
    """Return relationship fields that should be read for a source file."""

    return tuple(
        field
        for field in RELATIONSHIP_FIELDS
        if relationship_for_field(field, source_path=source_path) is not None
    )


def normalize_relationship(
    original_field: str, *, source_path: str | None = None, fallback: str = BODY_LINK_REL_TYPE
) -> str:
    """Map an edge's source field to a canonical relationship type."""

    if original_field in BODY_LINK_ORIGINAL_FIELDS:
        return BODY_LINK_REL_TYPE
    if original_field == PROVIDER_ORIGINAL_FIELD:
        return PROVIDER_REL_TYPE
    relationship = relationship_for_field(original_field, source_path=source_path)
    if relationship is None:
        return fallback
    return relationship.canonical_type


def registry_payload() -> dict[str, Any]:
    """Return the public registry contract embedded in graph and validation JSON."""

    return {
        "version": REGISTRY_VERSION,
        "relationships": [
            {
                "canonical_type": relationship.canonical_type,
                "canonical_field": relationship.canonical_field,
                "fields": list(relationship.fields),
                "description": relationship.description,
                "source_globs": list(relationship.source_globs),
                "legacy": relationship.legacy,
            }
            for relationship in RELATIONSHIPS
        ],
        "body_links": {
            "canonical_type": BODY_LINK_REL_TYPE,
            "fields": sorted(BODY_LINK_ORIGINAL_FIELDS),
        },
        "provider_refs": {
            "canonical_type": PROVIDER_REL_TYPE,
            "field": PROVIDER_ORIGINAL_FIELD,
            "exposes_raw_values": False,
        },
    }
