from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parent

ENGINE_SUBDIRS = (
    "educational",
    "lenses",
    "playbooks",
    "reference",
    "scripts",
    "skills",
)


def _copy_generated_data(target_root: Path) -> None:
    engine_root = target_root / "mb" / "_engine"
    engine_claude = target_root / "mb" / "_engine" / ".claude"
    for name in ENGINE_SUBDIRS:
        source = REPO_ROOT / ".claude" / name
        if not source.exists():
            continue
        target = engine_claude / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
        )
    plugin_source = REPO_ROOT / ".claude-plugin"
    if plugin_source.exists():
        plugin_target = engine_root / ".claude-plugin"
        if plugin_target.exists():
            shutil.rmtree(plugin_target)
        shutil.copytree(plugin_source, plugin_target)


class build_py(_build_py):
    def run(self) -> None:
        super().run()
        _copy_generated_data(Path(self.build_lib))


class sdist(_sdist):
    def make_release_tree(self, base_dir: str, files: list[str]) -> None:
        super().make_release_tree(base_dir, files)
        _copy_generated_data(Path(base_dir))


setup(cmdclass={"build_py": build_py, "sdist": sdist})
