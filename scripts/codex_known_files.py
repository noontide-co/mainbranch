#!/usr/bin/env python3
"""Regenerate `mb/mb/codex_known_files.py` by replaying every release's Codex writers.

Codex cleanup deletes a file at an old Codex path only when its content is
proven to be one `mb` wrote. The proof is a digest of the normalised content
(`mb.codex.normalised_generated_digest`) found in the frozen set this script
writes. To build it, the script:

1. lists the release tags (`oe-v*`) whose tree has `mb/mb/codex.py`;
2. extracts each tag with `git archive` into a temporary folder;
3. runs that release's own writers (`write_agents_md`, then
   `write_global_plugin_source` and `write_global_skill_source` where they
   exist) in a fresh temporary HOME and business repo, with a minimal
   environment, and records every file each writer left;
4. keeps the files at the paths today's cleanup removes: the repo-local
   `.agents/` paths, the global plugin source root, the legacy and retired
   global skill folders, and the `main-branch` skill (a copy of it is what the
   repo-local `.agents/skills/main-branch` path held);
5. runs each release twice, once as itself and once with another repo name and
   a sentinel `mb` version, and fails unless both give the same normalised
   digests (so the normalisation covers everything that varies per install).

It never touches the real HOME. Run it from a full clone with the release
tags fetched, with a Python that has `mb`'s dependencies installed:

    python scripts/codex_known_files.py           # check: replay the releases the
                                                  # module names; exit 1 if it differs
    python scripts/codex_known_files.py --write   # replay every release tag, rewrite

CI checkouts are shallow and carry no tags, so the test that runs `--check`
skips there.
"""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "mb" / "mb" / "codex_known_files.py"
SENTINEL_VERSION = "9.8.7"

WRITER = r"""
import json, os, sys
from pathlib import Path
tree, home, repo_name, version = sys.argv[1:5]
sys.path.insert(0, tree)
import mb
assert os.path.realpath(mb.__file__).startswith(os.path.realpath(tree)), mb.__file__
if version != "-":
    mb.__version__ = version
import mb.codex as c
repo = Path(home) / repo_name
repo.mkdir(parents=True)
(repo / "CLAUDE.md").write_text("# " + repo_name + "\n")
plugin_root = c.global_plugin_source_root() if hasattr(c, "global_plugin_source_root") else None
skills_root = (
    c.global_skill_source_root()
    if hasattr(c, "global_skill_source_root")
    else Path(home) / ".codex" / "skills"
)
roots = {"repo": repo, "plugin": plugin_root, "skills": skills_root}
seen = {}
def snapshot():
    for family, root in roots.items():
        if root is None or not root.exists():
            continue
        base = root / ".agents" if family == "repo" else root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and not path.is_symlink():
                key = family + ":" + path.relative_to(root).as_posix()
                text = path.read_text(encoding="utf-8")
                seen.setdefault(key, [])
                if text not in seen[key]:
                    seen[key].append(text)
def write_agents():
    try:
        c.write_agents_md(repo, name=repo_name.title(), gh_username=repo_name + "-owner")
    except TypeError:
        c.write_agents_md(repo)
for writer in (
    write_agents,
    getattr(c, "write_global_plugin_source", None),
    getattr(c, "write_global_skill_source", None),
):
    if writer is not None:
        writer()
        snapshot()
print(json.dumps({"version": mb.__version__, "files": seen}))
"""


def _tags() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "tag", "-l", "oe-v*"], check=True, capture_output=True, text=True
    ).stdout.split()
    tags = []
    for tag in out:
        parts = tag[len("oe-v") :].split(".")
        if not all(part.isdigit() for part in parts):
            continue  # release candidates
        has_codex = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{tag}:mb/mb/codex.py"],
            capture_output=True,
        )
        if has_codex.returncode == 0:
            tags.append(tag)
    return sorted(tags, key=lambda tag: [int(part) for part in tag[len("oe-v") :].split(".")])


def _extract(tag: str, dest: Path) -> None:
    data = subprocess.run(
        ["git", "-C", str(ROOT), "archive", "--format=tar", tag], check=True, capture_output=True
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        if hasattr(tarfile, "data_filter"):
            archive.extractall(dest, filter="data")
        else:  # pragma: no cover - Python without extraction filters
            archive.extractall(dest)  # noqa: S202 - our own git archive


def _replay(tree: Path, repo_name: str, version: str) -> dict[str, list[str]]:
    with tempfile.TemporaryDirectory(prefix="mb-codex-replay-home-") as home:
        env = {"HOME": home, "PATH": "/usr/bin:/bin"}
        proc = subprocess.run(
            [sys.executable, "-I", "-c", WRITER, str(tree / "mb"), home, repo_name, version],
            cwd=home,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
    if proc.returncode != 0:
        raise SystemExit(f"replay failed for {tree.name}: {proc.stderr.strip()[-2000:]}")
    payload: dict[str, list[str]] = json.loads(proc.stdout)["files"]
    return payload


def _cleanup_path(key: str, codex: object) -> bool:
    family, relative = key.split(":", 1)
    if family in {"repo", "plugin"}:
        return True
    first = relative.split("/", 1)[0]
    # The legacy and retired skill folders, and `main-branch`, whose copy is
    # what the repo-local `.agents/skills/main-branch` cleanup path held.
    names = {
        codex.CODEX_LEGACY_GLOBAL_SKILL_NAME,  # type: ignore[attr-defined]
        codex.CODEX_GLOBAL_SKILL_NAME,  # type: ignore[attr-defined]
        *codex.CODEX_RETIRED_GLOBAL_SKILL_NAMES,  # type: ignore[attr-defined]
    }
    return first in names


def _digests(files: dict[str, list[str]], codex: object) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for key, texts in files.items():
        if not _cleanup_path(key, codex):
            continue
        path = Path(key.split(":", 1)[1])
        for text in texts:
            digest = codex.normalised_generated_digest(path.name, text.encode("utf-8"))  # type: ignore[attr-defined]
            if digest is None:
                raise SystemExit(f"{key}: a generated file did not normalise")
            found.setdefault(codex.generated_file_key(path), set()).add(digest)  # type: ignore[attr-defined]
    return found


def build(only: tuple[str, ...] = ()) -> tuple[list[str], dict[str, set[str]], dict[str, int]]:
    sys.path.insert(0, str(ROOT / "mb"))
    from mb import codex

    tags = _tags()
    if only:
        missing = sorted(set(only) - set(tags))
        if missing:
            raise SystemExit(f"release tags not found: {', '.join(missing)}")
        tags = [tag for tag in tags if tag in only]
    if not tags:
        raise SystemExit("no release tags found; fetch them with `git fetch --tags`")
    known: dict[str, set[str]] = {}
    counts: dict[str, int] = {}
    for tag in tags:
        with tempfile.TemporaryDirectory(prefix="mb-codex-replay-tree-") as tmp:
            tree = Path(tmp)
            _extract(tag, tree)
            real = _digests(_replay(tree, "acme", "-"), codex)
            other = _digests(_replay(tree, "zeta-co", SENTINEL_VERSION), codex)
        if real != other:
            raise SystemExit(f"{tag}: normalisation misses something that varies per install")
        counts[tag] = sum(len(values) for values in real.values())
        for key, values in real.items():
            known.setdefault(key, set()).update(values)
    return tags, known, counts


def render(tags: list[str], known: dict[str, set[str]]) -> str:
    lines = [
        '"""Normalised digests of every Codex file a released `mb` wrote at an old Codex path.',
        "",
        "Generated by `scripts/codex_known_files.py`, which replays each release's own",
        "writers in a temporary HOME; do not edit by hand. Rerun it with `--write` after",
        "a release changes what those writers produce. Keys are the file's folder and",
        "name; values are `mb.codex.normalised_generated_digest` results.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "RELEASES_REPLAYED: tuple[str, ...] = (",
        *(f'    "{tag}",' for tag in tags),
        ")",
        "",
        "KNOWN_FILE_DIGESTS: dict[str, frozenset[str]] = {",
    ]
    for key in sorted(known):
        lines.append(f'    "{key}": frozenset(')
        lines.append("        {")
        lines.extend(f'            "{digest}",' for digest in sorted(known[key]))
        lines.append("        }")
        lines.append("    ),")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="rewrite the data module")
    args = parser.parse_args(argv)
    only: tuple[str, ...] = ()
    if not args.write:
        # Check mode reproduces the committed set from the releases it names,
        # so a newer tag does not make it stale until someone regenerates.
        sys.path.insert(0, str(ROOT / "mb"))
        from mb.codex_known_files import RELEASES_REPLAYED

        only = RELEASES_REPLAYED
    tags, known, counts = build(only)
    text = render(tags, known)
    for tag in tags:
        print(f"{tag}: {counts[tag]} files at old Codex paths")
    print(f"{len(tags)} releases, {sum(len(v) for v in known.values())} distinct digests")
    if args.write:
        MODULE.write_text(text, encoding="utf-8")
        print(f"wrote {MODULE.relative_to(ROOT)}")
        return 0
    if MODULE.read_text(encoding="utf-8") != text:
        print(f"{MODULE.relative_to(ROOT)} is stale; rerun with --write", file=sys.stderr)
        return 1
    print(f"{MODULE.relative_to(ROOT)} is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
