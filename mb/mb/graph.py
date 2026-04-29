"""``mb graph`` — emit Graphviz DOT for the repo's link graph.

v0.1 walks frontmatter for ``linked_research:``, ``linked_decisions:``,
and ``supersedes:`` keys. Builds an adjacency list. Outputs DOT to stdout
or, with ``--open``, shells to ``dot -Tpng`` and ``open``/``xdg-open``.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

LINK_KEYS = ("linked_research", "linked_decisions", "supersedes")


def _read_frontmatter(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    try:
        end = text.index("\n---", 3)
    except ValueError:
        return None
    try:
        data = yaml.safe_load(text[3:end].lstrip("\n")) or {}
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _node_id(p: Path, root: Path) -> str:
    rel = str(p.relative_to(root))
    return rel.replace("/", "_").replace(".", "_").replace("-", "_")


def _node_label(p: Path, root: Path) -> str:
    return str(p.relative_to(root))


def build_dot(path: str) -> str:
    """Build DOT output as a string."""
    root = Path(path).resolve()
    edges: list[tuple[str, str, str]] = []
    nodes: dict[str, str] = {}

    targets: list[Path] = []
    for sub in ("decisions", "research"):
        d = root / sub
        if d.exists():
            targets.extend(sorted(d.glob("*.md")))
    for offer in (root / "core" / "offers").glob("*/offer.md"):
        targets.append(offer)

    for p in targets:
        nid = _node_id(p, root)
        nodes[nid] = _node_label(p, root)

    for p in targets:
        fm = _read_frontmatter(p)
        if not fm:
            continue
        src_id = _node_id(p, root)
        for key in LINK_KEYS:
            val = fm.get(key)
            if not val:
                continue
            if isinstance(val, str):
                val = [val]
            if not isinstance(val, list):
                continue
            for ref in val:
                if not isinstance(ref, str):
                    continue
                target_path = (root / ref).resolve()
                if target_path.exists():
                    tid = _node_id(target_path, root)
                    if tid not in nodes:
                        nodes[tid] = ref
                else:
                    # external / unresolved reference — keep as a stub node
                    tid = ref.replace("/", "_").replace(".", "_").replace("-", "_")
                    nodes.setdefault(tid, ref)
                edges.append((src_id, tid, key))

    lines = ["digraph mb {", '  rankdir="LR";', '  node [shape=box, fontname="Helvetica"];']
    for nid, label in sorted(nodes.items()):
        lines.append(f'  {nid} [label="{label}"];')
    for src, tgt, kind in edges:
        style = "solid" if kind != "supersedes" else "dashed"
        lines.append(f'  {src} -> {tgt} [label="{kind}", style={style}];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def open_dot(dot: str) -> None:
    """Render DOT to PNG and open it."""
    if not shutil.which("dot"):
        raise RuntimeError("graphviz `dot` not on PATH (brew install graphviz)")
    if platform.system() == "Windows":
        raise RuntimeError("--open is unsupported on Windows in v0.1")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        png_path = f.name
    proc = subprocess.run(
        ["dot", "-Tpng", "-o", png_path],
        input=dot,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"dot failed: {proc.stderr}")
    opener = "open" if platform.system() == "Darwin" else "xdg-open"
    subprocess.run([opener, png_path], check=False)
