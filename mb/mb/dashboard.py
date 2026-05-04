"""Read-only local dashboard over existing Main Branch JSON contracts."""

from __future__ import annotations

import html
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from mb import graph as graph_mod
from mb import status as status_mod


def _local_state(repo: Path) -> dict[str, Any]:
    root = repo / ".mb"
    if not root.exists():
        return {"path": ".mb", "exists": False, "files": [], "summary": {"files": 0}}
    files = [
        path.relative_to(repo).as_posix()
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != ".DS_Store"
    ]
    return {
        "path": ".mb",
        "exists": True,
        "files": files[:20],
        "summary": {"files": len(files)},
    }


def build_data(repo: str = ".") -> dict[str, Any]:
    """Build dashboard data without mutating repo-local status markers."""
    repo_path = Path(repo).resolve()
    status_report = status_mod.run(path=str(repo_path), update_marker=False)
    graph_index = graph_mod.build_index(str(repo_path))
    brain = status_report.get("brain") or {}
    counts = brain.get("counts") or {}
    bets = brain.get("bets") or {}
    github = status_report.get("github") or {}
    readiness = status_report.get("readiness") or {}
    ranked_actions = readiness.get("ranked_actions") or readiness.get("top_actions") or []
    next_actions = ranked_actions or readiness.get("next_actions") or []
    offers_root = repo_path / "core" / "offers"
    has_bet_memory = bool(counts.get("bets")) or (
        offers_root.exists() and any(offers_root.glob("*/offer.md"))
    )
    return {
        "schema_version": "1.0",
        "schema": {
            "name": "mainbranch.dashboard",
            "version": "1.0",
            "compatibility": "v1 additions are additive; existing v1 keys must not change meaning.",
        },
        "repo": {
            "path": str(repo_path),
            "view": "repo",
            "workspace_ready": False,
            "workspace_note": "Single-repo dashboard v0; workspace/operator views can layer later.",
        },
        "status": status_report,
        "graph": {
            "summary": graph_index.get("summary") or {},
            "nodes": graph_index.get("nodes", [])[:50],
            "edges": graph_index.get("edges", [])[:50],
        },
        "local_state": _local_state(repo_path),
        "sections": {
            "repo_health": {
                "level": readiness.get("level", "unknown"),
                "score": readiness.get("score", 0),
                "drift": (status_report.get("drift") or {}).get("summary") or {},
            },
            "bets": {
                "active": bets.get("active") or [],
                "due_soon": bets.get("due_soon") or [],
                "overdue": bets.get("overdue") or [],
            },
            "github": {
                "available": github.get("available", False),
                "authenticated": github.get("authenticated", False),
                "summary": github.get("summary") or {},
                "sections": github.get("sections") or {},
            },
            "graph": graph_index.get("summary") or {},
            "next_actions": next_actions[:5] if isinstance(next_actions, list) else [],
            "similar_bets": {
                "available": has_bet_memory,
                "command": 'mb similar-bets "<thesis>" --json',
                "source": "bets/*.md plus core/offers/*/offer.md",
            },
        },
    }


def _html_list(items: list[Any], *, empty: str) -> str:
    if not items:
        return f'<p class="muted">{html.escape(empty)}</p>'
    rendered = []
    for item in items[:6]:
        if isinstance(item, dict):
            title = str(item.get("title") or item.get("summary") or item.get("path") or item)
            meta = str(
                item.get("deadline") or item.get("business_status") or item.get("status") or ""
            )
            rendered.append(
                "<li><strong>"
                + html.escape(title)
                + "</strong>"
                + (f"<span>{html.escape(meta)}</span>" if meta else "")
                + "</li>"
            )
        else:
            rendered.append(f"<li>{html.escape(str(item))}</li>")
    return "<ul>" + "".join(rendered) + "</ul>"


def render_html(data: dict[str, Any]) -> str:
    """Render a small self-contained dashboard page."""
    sections = data["sections"]
    health = sections["repo_health"]
    bets = sections["bets"]
    github = sections["github"]
    graph = sections["graph"]
    repo_path = html.escape(str(data["repo"]["path"]))
    assigned = (github.get("sections") or {}).get("assigned_tasks") or []
    proposals = (github.get("sections") or {}).get("open_proposals") or []
    drift_total = html.escape(str((health.get("drift") or {}).get("total", 0)))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Main Branch Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    body {{ margin: 0; background: #f8f7f3; color: #1f2933; }}
    header {{ padding: 24px 28px 16px; border-bottom: 1px solid #d8d6cf; background: #ffffff; }}
    main {{
      padding: 20px 28px 32px;
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }}
    h1 {{ margin: 0 0 6px; font-size: 28px; font-weight: 700; }}
    h2 {{ margin: 0 0 12px; font-size: 16px; }}
    p {{ margin: 0 0 10px; }}
    .repo {{ color: #5b6470; font-size: 13px; overflow-wrap: anywhere; }}
    section {{
      background: #ffffff;
      border: 1px solid #d8d6cf;
      border-radius: 8px;
      padding: 16px;
      min-height: 140px;
    }}
    .metric {{ font-size: 34px; font-weight: 700; line-height: 1; margin-bottom: 4px; }}
    .muted, span {{ color: #64707d; font-size: 13px; }}
    ul {{ margin: 0; padding-left: 18px; }}
    li {{ margin: 8px 0; }}
    li span {{ display: block; margin-top: 2px; }}
    code {{ background: #eef1f4; border-radius: 4px; padding: 2px 5px; }}
  </style>
</head>
<body>
  <header>
    <h1>Main Branch Dashboard</h1>
    <p class="repo">{repo_path}</p>
  </header>
  <main>
    <section>
      <h2>Repo Health</h2>
      <div class="metric">{html.escape(str(health.get("score", 0)))}</div>
      <p>{html.escape(str(health.get("level", "unknown")).replace("_", " "))}</p>
      <p class="muted">Drift signals: {drift_total}</p>
    </section>
    <section>
      <h2>Active Bets</h2>
      {_html_list(bets.get("active") or [], empty="No active bets found.")}
    </section>
    <section>
      <h2>Due / Overdue</h2>
      {_html_list((bets.get("overdue") or []) + (bets.get("due_soon") or []), empty="No due bets.")}
    </section>
    <section>
      <h2>GitHub Tasks</h2>
      {_html_list(assigned, empty="No assigned tasks available.")}
    </section>
    <section>
      <h2>Proposals</h2>
      {_html_list(proposals, empty="No open proposals available.")}
    </section>
    <section>
      <h2>Graph</h2>
      <p><strong>{html.escape(str(graph.get("files", 0)))}</strong> files</p>
      <p><strong>{html.escape(str(graph.get("nodes", 0)))}</strong> nodes</p>
      <p><strong>{html.escape(str(graph.get("edges", 0)))}</strong> edges</p>
    </section>
    <section>
      <h2>Next Actions</h2>
      {_html_list(sections.get("next_actions") or [], empty="No next actions available.")}
    </section>
    <section>
      <h2>Similar Bets</h2>
      <p>{html.escape(str(sections["similar_bets"]["source"]))}</p>
      <p><code>{html.escape(str(sections["similar_bets"]["command"]))}</code></p>
    </section>
  </main>
</body>
</html>
"""


class DashboardServer(HTTPServer):
    repo: Path


def make_server(repo: str = ".", host: str = "127.0.0.1", port: int = 0) -> DashboardServer:
    """Create a dashboard HTTP server. Use port 0 for an ephemeral port."""
    repo_path = Path(repo).resolve()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send(self, body: bytes, content_type: str, status: int = 200) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/api/dashboard":
                payload = json.dumps(build_data(str(repo_path)), indent=2).encode("utf-8")
                self._send(payload, "application/json; charset=utf-8")
                return
            if path in {"", "/"}:
                page = render_html(build_data(str(repo_path))).encode("utf-8")
                self._send(page, "text/html; charset=utf-8")
                return
            self._send(b"not found\n", "text/plain; charset=utf-8", status=404)

    server = DashboardServer((host, port), Handler)
    server.repo = repo_path
    server.timeout = 0.2
    return server


def serve(
    repo: str = ".",
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = False,
) -> None:
    """Start the blocking local dashboard server."""
    server = make_server(repo=repo, host=host, port=port)
    address = server.server_address
    raw_host = address[0]
    actual_host = raw_host.decode("utf-8") if isinstance(raw_host, bytes) else str(raw_host)
    actual_port = int(address[1])
    url = f"http://{actual_host}:{actual_port}/"
    print(f"mb dashboard serving {url}")
    if open_browser:
        threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
