from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import yaml
from typer.testing import CliRunner

from mb import image_rail as image_rail_mod
from mb.cli import app

runner = CliRunner()


def _record_from_index(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    _, fenced = text.split("```yaml\n", 1)
    yaml_text, _ = fenced.split("\n```", 1)
    return cast(dict[str, Any], yaml.safe_load(yaml_text))


def test_openai_image_smoke_writes_safe_blocked_record(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(
        app,
        [
            "image",
            "smoke-openai",
            "--repo",
            str(repo),
            "--push-slug",
            "2026-05-13-fake-openai-smoke",
            "--docs-checked",
            "2026-05-13",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["provider"] == "openai"
    assert payload["model"] == "gpt-image-2"
    assert payload["state"] == "blocked"
    assert payload["blocker_code"] == "generation_not_approved"
    assert payload["output_record_written"] is True
    assert payload["binary_committed"] is False

    index_path = repo / "pushes" / "2026-05-13-fake-openai-smoke" / "image-index.md"
    assert index_path.exists()
    record = _record_from_index(index_path)
    asset = record["assets"][0]

    assert record["schema"] == "mainbranch.image_index.v0"
    assert asset["provider"] == "openai"
    assert asset["model"] == "gpt-image-2"
    assert asset["model_snapshot"] == "gpt-image-2-2026-04-21"
    assert asset["credential_state"] == "missing_env"
    assert asset["output_reference"].startswith("mb-media://pushes/")
    assert asset["storage_backend"] == "mb-media"
    assert asset["committed_binary"] is False
    assert asset["safe_to_share"] is True

    text = index_path.read_text(encoding="utf-8")
    assert str(tmp_path) not in text
    assert "OPENAI_API_KEY=" not in text
    assert not (repo / ".mb" / "media").exists()


def test_openai_image_smoke_generate_without_key_records_missing_key(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    repo = tmp_path / "biz"
    repo.mkdir()

    result = runner.invoke(
        app,
        [
            "image",
            "smoke-openai",
            "--repo",
            str(repo),
            "--push-slug",
            "2026-05-13-fake-openai-smoke",
            "--docs-checked",
            "2026-05-13",
            "--generate",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["state"] == "blocked"
    assert payload["blocker_code"] == "missing_openai_api_key"

    index_path = repo / "pushes" / "2026-05-13-fake-openai-smoke" / "image-index.md"
    record = _record_from_index(index_path)
    asset = record["assets"][0]
    assert asset["blocker_code"] == "missing_openai_api_key"
    assert "Do not paste provider keys" in asset["blocker"]


def test_openai_image_smoke_generated_path_keeps_binary_in_media_cache(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-written")
    monkeypatch.setattr(image_rail_mod, "_provider_blocker", lambda generate: ("", ""))
    monkeypatch.setattr(
        image_rail_mod,
        "_generate_openai_image",
        lambda prompt, *, model, size, quality: (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x04\x00\x00\x00\x06\x00fake-png-tail"
        ),
    )

    result = runner.invoke(
        app,
        [
            "image",
            "smoke-openai",
            "--repo",
            str(repo),
            "--push-slug",
            "2026-05-13-fake-openai-smoke",
            "--docs-checked",
            "2026-05-13",
            "--generate",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["state"] == "generated"
    assert payload["generated_dimensions"] == {"width": 1024, "height": 1536}
    assert payload["binary_written"] is True
    assert payload["binary_committed"] is False

    media_path = (
        repo
        / ".mb"
        / "media"
        / "pushes"
        / "2026-05-13-fake-openai-smoke"
        / "images"
        / "fake-openai-image-001.png"
    )
    assert media_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    index_path = repo / "pushes" / "2026-05-13-fake-openai-smoke" / "image-index.md"
    record = _record_from_index(index_path)
    dimensions = record["assets"][0]["dimensions"]
    assert dimensions["generated_width"] == 1024
    assert dimensions["generated_height"] == 1536
    text = index_path.read_text(encoding="utf-8")
    assert str(media_path) not in text
    assert "test-key-not-written" not in text


def test_openai_image_smoke_provider_failure_writes_sanitized_blocker(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "biz"
    repo.mkdir()
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-written")
    monkeypatch.setattr(image_rail_mod, "_provider_blocker", lambda generate: ("", ""))

    def fail_generation(prompt: str, *, model: str, size: str, quality: str) -> bytes:
        raise RuntimeError("secret-bearing provider details should not be recorded")

    monkeypatch.setattr(image_rail_mod, "_generate_openai_image", fail_generation)

    result = runner.invoke(
        app,
        [
            "image",
            "smoke-openai",
            "--repo",
            str(repo),
            "--push-slug",
            "2026-05-13-fake-openai-smoke",
            "--docs-checked",
            "2026-05-13",
            "--generate",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["state"] == "blocked"
    assert payload["blocker_code"] == "provider_request_failed"

    index_path = repo / "pushes" / "2026-05-13-fake-openai-smoke" / "image-index.md"
    text = index_path.read_text(encoding="utf-8")
    assert "RuntimeError" in text
    assert "secret-bearing provider details" not in text
    assert "test-key-not-written" not in text


def test_init_gitignore_keeps_media_cache_out_of_git(tmp_path: Path) -> None:
    result = runner.invoke(app, ["init", str(tmp_path / "biz"), "--name", "Acme"])

    assert result.exit_code == 0
    gitignore = (tmp_path / "biz" / ".gitignore").read_text(encoding="utf-8")
    assert ".mb/media/" in gitignore
