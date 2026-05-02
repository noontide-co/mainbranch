"""Shared migration planning primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ChangeKind = Literal[
    "mkdir",
    "move_file",
    "delete_file",
    "write_file",
    "remove_empty_dir",
    "symlink",
]


@dataclass(frozen=True)
class MigrationInfo:
    """Registered migration metadata."""

    id: str
    name: str
    from_version: str
    to_version: str
    description: str


@dataclass(frozen=True)
class PlannedChange:
    """One filesystem change relative to a business repo."""

    kind: ChangeKind
    path: str
    source: str = ""
    target: str = ""
    content: str = ""


@dataclass
class MigrationPlan:
    """Dry-run plan for a migration."""

    migration: MigrationInfo
    changes: list[PlannedChange] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)
