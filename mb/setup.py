from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parent

GENERATED_DATA = {
    "skills": REPO_ROOT / ".claude" / "skills",
    "playbooks": REPO_ROOT / ".claude" / "playbooks",
}


def _copy_generated_data(target_root: Path) -> None:
    data_root = target_root / "mb" / "_data"
    for name, source in GENERATED_DATA.items():
        if not source.exists():
            continue
        target = data_root / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
        )


class build_py(_build_py):
    def run(self) -> None:
        super().run()
        _copy_generated_data(Path(self.build_lib))


class sdist(_sdist):
    def make_release_tree(self, base_dir: str, files: list[str]) -> None:
        super().make_release_tree(base_dir, files)
        _copy_generated_data(Path(base_dir))


setup(cmdclass={"build_py": build_py, "sdist": sdist})
