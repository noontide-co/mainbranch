"""Numbered Main Branch repo migrations."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from types import ModuleType

from mb.migrations.base import MigrationInfo, MigrationPlan

MIGRATION_MODULES = ("mb.migrations.001_v01_to_v02_path_config",)


def registered() -> list[tuple[MigrationInfo, ModuleType]]:
    """Return migrations in apply order."""
    modules = [import_module(name) for name in MIGRATION_MODULES]
    return [(module.INFO, module) for module in modules]


def version_map() -> dict[str, str]:
    """Return the registered from-version -> module map."""
    return {info.from_version: module.__name__ for info, module in registered()}


def plan_for(info: MigrationInfo, module: ModuleType, repo: Path) -> MigrationPlan:
    """Call a migration module's plan function with a typed return value."""
    raw_plan = module.plan(repo)
    if not isinstance(raw_plan, MigrationPlan):
        raise TypeError(f"{info.name} returned an invalid migration plan")
    return raw_plan
