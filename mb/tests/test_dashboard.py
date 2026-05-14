from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from mb import dashboard as dashboard_mod
from mb import image_rail as image_rail_mod
from mb.cli import app
from mb.init import run as init_run

runner = CliRunner()


def test_dashboard_builds_static_html_without_ad_context(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")

    result = runner.invoke(app, ["dashboard", "build", "--repo", str(repo), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["output"]["path"] == ".mb/dashboard/index.html"
    assert payload["output"]["committed_by_default"] is False
    assert payload["dashboard"]["read_only"] is True
    assert payload["dashboard"]["source_boundary"]["dashboard"] == "visual_map"
    assert payload["dashboard"]["ad_readiness"]["state"] in {"blocked", "partial"}
    assert payload["dashboard"]["creative_state"]["state"] == "empty"
    assert "Record image candidate state" in [
        action["title"] for action in payload["dashboard"]["next_actions"]
    ]

    html_path = repo / ".mb" / "dashboard" / "index.html"
    assert html_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "Local repo cockpit" in html
    assert "Read-only visual map" in html
    assert str(repo) not in html


def test_dashboard_reads_image_index_candidate_state(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    repo = tmp_path / "biz"
    repo.mkdir()
    image_rail_mod.smoke_openai(
        repo=str(repo),
        push_slug="2026-05-13-fake-openai-smoke",
        docs_checked="2026-05-13",
        generate=False,
    )

    data = dashboard_mod.collect(repo)

    assert data["creative_state"]["state"] == "review"
    assert data["creative_state"]["source_bites"][0]["extracted_phrase"] == (
        "I keep losing the thread"
    )
    assert data["creative_state"]["candidates"][0]["concept_id"] == "lost-thread-branch-map"
    assert data["creative_state"]["candidates"][0]["creative_playbook_id"] == (
        "specific_object_metaphor"
    )
    assert data["ad_readiness"]["state"] == "ready"
    assert data["provider_readiness"]["providers"][1]["id"] == "openai_image_rail"
    assert data["provider_readiness"]["providers"][1]["state"] == "blocked"
    assert data["creative_state"]["image_indexes"][0]["generated_count"] == 0

    serialized = json.dumps(data)
    assert "Create a fixture-safe Facebook feed image-ad base" not in serialized
    assert "OPENAI_API_KEY" not in serialized


def test_dashboard_redacts_private_paths_and_secret_like_values(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    (repo / "pushes" / "2026-05-13-private-smoke").mkdir(parents=True)
    (repo / "pushes" / "2026-05-13-private-smoke" / "image-index.md").write_text(
        """# Image Index

```yaml
ad_readiness_gate:
  state: partial
  hard_stop_missing_fields: []
  soft_warning_missing_fields: [meta_summary]
selected_source_bites:
  - concept_id: private-path
    source_type: customer_language
    source_file: /Users/devonmeadows/private/audience.md
    extracted_phrase: sk-abcdefghijklmnop
    visual_translation: /private/tmp/customer-context.md
concepts:
  - concept_id: private-path
    creative_playbook_id: specific_object_metaphor
    router_reason: Use /Users/devonmeadows/private/router.md
    source_bite:
      extracted_phrase: ghp_abcdefghijklmnop
    review:
      status: rejected
      decision: reject
      scores:
        native_feed_fit: 1
assets:
  - asset_id: asset-1
    concept_id: private-path
    state: blocked
    output_reference: /Users/devonmeadows/private/image.png
    blocker_code: EAABabcdefghijklmnop
visual_calibration_result:
  state: blocked
  generated_count: 0
  all_rejected: true
```
""",
        encoding="utf-8",
    )

    data = dashboard_mod.collect(repo)
    serialized = json.dumps(data)

    assert "/Users/devonmeadows" not in serialized
    assert "/private/tmp" not in serialized
    assert "sk-abcdefghijklmnop" not in serialized
    assert "ghp_abcdefghijklmnop" not in serialized
    assert "EAABabcdefghijklmnop" not in serialized
    assert "[local path]" in serialized
    assert "[redacted secret]" in serialized


def test_dashboard_open_builds_and_launches_browser(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "biz"
    init_run(path=str(repo), name="Acme")
    opened: list[str] = []

    def fake_open(uri: str) -> bool:
        opened.append(uri)
        return True

    monkeypatch.setattr(dashboard_mod, "_open_browser", fake_open)

    result: dict[str, Any] = dashboard_mod.open_dashboard(repo)

    assert result["opened"] is True
    assert opened and opened[0].startswith("file:")
    assert (repo / ".mb" / "dashboard" / "index.html").exists()
