"""Fixture-safe image rail smoke helpers."""

from __future__ import annotations

import base64
import importlib
import importlib.util
import os
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import yaml

DEFAULT_PUSH_SLUG = "2026-05-13-openai-image-rail-smoke"
DEFAULT_ASSET_ID = "fake-openai-image-001"
DEFAULT_MODEL = "gpt-image-2"
DEFAULT_MODEL_SNAPSHOT = "gpt-image-2-2026-04-21"
DEFAULT_SIZE = "1024x1536"
DEFAULT_QUALITY = "medium"
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_PROMPT = """\
Create a fixture-safe static ad concept for a fictional business called
Northstar Ledger. Show an abstract desk scene with a clean notebook, simple
charts, and warm natural light. Do not include real brands, real people,
customer data, logos, screenshots, account details, or private information.
Leave open space near the upper center for a later deterministic text overlay.
"""

SmokeState = Literal["generated", "blocked"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _logical_output(push_slug: str, asset_id: str, extension: str = "png") -> str:
    return f"mb-media://pushes/{push_slug}/images/{asset_id}.{extension}"


def _repo_relative(path: Path, repo: Path) -> str:
    return path.resolve().relative_to(repo.resolve()).as_posix()


def _media_path(repo: Path, media_root: str, push_slug: str, asset_id: str) -> Path:
    root = Path(media_root).expanduser()
    if not root.is_absolute():
        root = repo / root
    return root / "pushes" / push_slug / "images" / f"{asset_id}.png"


def _provider_blocker(generate: bool) -> tuple[str, str]:
    if not generate:
        return (
            "generation_not_approved",
            (
                "Provider generation was not requested. Re-run with --generate only after "
                "the operator approves the provider call and local credential boundary."
            ),
        )
    if not os.environ.get("OPENAI_API_KEY"):
        return (
            "missing_openai_api_key",
            (
                "OPENAI_API_KEY is not set in the local runtime. Do not paste provider "
                "keys into chat or committed repo files."
            ),
        )
    if importlib.util.find_spec("openai") is None:
        return (
            "missing_openai_package",
            "The optional openai Python package is not installed in the local runtime.",
        )
    return "", ""


def _generate_openai_image(prompt: str, *, model: str, size: str, quality: str) -> bytes:
    openai_mod: Any = importlib.import_module("openai")
    client = openai_mod.OpenAI()

    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )
    encoded = response.data[0].b64_json
    if not encoded:
        raise RuntimeError("OpenAI image response did not include b64_json output")
    return base64.b64decode(encoded)


def _png_dimensions(image_bytes: bytes) -> dict[str, int] | None:
    if len(image_bytes) < 24:
        return None
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    if image_bytes[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", image_bytes[16:24])
    return {"width": width, "height": height}


def _asset_record(
    *,
    push_slug: str,
    asset_id: str,
    docs_checked: str,
    generated_at: str,
    state: SmokeState,
    blocker_code: str,
    blocker: str,
    credential_state: str,
    output_reference: str,
    prompt: str,
    model: str,
    size: str,
    quality: str,
    generated_dimensions: dict[str, int] | None,
) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "rail": "provider",
        "provider": "openai",
        "model": model,
        "model_snapshot": DEFAULT_MODEL_SNAPSHOT,
        "endpoint": "v1/images/generations",
        "docs_checked": docs_checked,
        "state": state,
        "blocker_code": blocker_code or None,
        "blocker": blocker or None,
        "credential_ref": "openai:image-generation",
        "credential_state": credential_state,
        "prompt": prompt.strip(),
        "source_context": [
            {
                "path": f"pushes/{push_slug}/image-index.md",
                "role": "fake_push_context",
                "safe_to_share": True,
            },
            {
                "path": "fixture:fictional-northstar-ledger",
                "role": "source_brief",
                "safe_to_share": True,
            },
        ],
        "references": [],
        "dimensions": {
            "requested_size": size,
            "aspect_ratio": "2:3",
            "format": "png",
            "quality": quality,
            "generated_width": (
                generated_dimensions["width"] if generated_dimensions is not None else None
            ),
            "generated_height": (
                generated_dimensions["height"] if generated_dimensions is not None else None
            ),
        },
        "output_reference": output_reference,
        "storage_backend": "mb-media",
        "committed_binary": False,
        "retries": 0,
        "timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
        "cost": {
            "estimate": "unknown_token_metered",
            "actual": "unknown",
            "usage": None,
        },
        "review_status": "unreviewed",
        "safe_to_share": True,
        "generated_at": generated_at,
        "operator_notes": (
            "Fixture-safe OpenAI image rail smoke. Commit this record only; keep any "
            "generated binary in configured private media storage."
        ),
    }


def _render_index(record: dict[str, Any]) -> str:
    yaml_text = yaml.safe_dump(record, sort_keys=False, allow_unicode=False)
    return (
        "# Image Index - OpenAI Image Rail Smoke\n\n"
        "This fixture-safe record proves the first narrow OpenAI image rail "
        "without committing generated binaries, secrets, private paths, or "
        "provider request credentials.\n\n"
        "```yaml\n"
        f"{yaml_text}"
        "```\n"
    )


def smoke_openai(
    *,
    repo: str,
    push_slug: str = DEFAULT_PUSH_SLUG,
    docs_checked: str,
    media_root: str = ".mb/media",
    generate: bool = False,
) -> dict[str, Any]:
    """Run or block the narrow OpenAI image rail smoke and write an asset record."""

    repo_path = Path(repo).resolve()
    push_dir = repo_path / "pushes" / push_slug
    push_dir.mkdir(parents=True, exist_ok=True)

    index_path = push_dir / "image-index.md"
    generated_at = _utc_now()
    output_reference = _logical_output(push_slug, DEFAULT_ASSET_ID)

    blocker_code, blocker = _provider_blocker(generate)
    credential_state = "configured_env" if os.environ.get("OPENAI_API_KEY") else "missing_env"
    state: SmokeState = "blocked" if blocker_code else "generated"

    binary_written = False
    generated_dimensions: dict[str, int] | None = None
    if state == "generated":
        out_path = _media_path(repo_path, media_root, push_slug, DEFAULT_ASSET_ID)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            image_bytes = _generate_openai_image(
                DEFAULT_PROMPT,
                model=DEFAULT_MODEL,
                size=DEFAULT_SIZE,
                quality=DEFAULT_QUALITY,
            )
        except Exception as exc:  # noqa: BLE001 - provider errors must become sanitized records.
            state = "blocked"
            blocker_code = "provider_request_failed"
            blocker = (
                f"OpenAI image generation failed before a usable image was written "
                f"({exc.__class__.__name__}). Check the local provider account, "
                f"organization verification, quota, model access, and network state."
            )
        else:
            generated_dimensions = _png_dimensions(image_bytes)
            out_path.write_bytes(image_bytes)
            binary_written = True

    record = {
        "schema": "mainbranch.image_index.v0",
        "push_slug": push_slug,
        "docs_checked": docs_checked,
        "output_record_written": True,
        "binary_committed": False,
        "assets": [
            _asset_record(
                push_slug=push_slug,
                asset_id=DEFAULT_ASSET_ID,
                docs_checked=docs_checked,
                generated_at=generated_at,
                state=state,
                blocker_code=blocker_code,
                blocker=blocker,
                credential_state=credential_state,
                output_reference=output_reference,
                prompt=DEFAULT_PROMPT,
                model=DEFAULT_MODEL,
                size=DEFAULT_SIZE,
                quality=DEFAULT_QUALITY,
                generated_dimensions=generated_dimensions,
            )
        ],
    }
    index_path.write_text(_render_index(record), encoding="utf-8")

    return {
        "ok": True,
        "provider": "openai",
        "model": DEFAULT_MODEL,
        "state": state,
        "blocker_code": blocker_code or None,
        "output_record_written": True,
        "record_path": _repo_relative(index_path, repo_path),
        "output_reference": output_reference,
        "storage_backend": "mb-media",
        "dimensions": {
            "requested_size": DEFAULT_SIZE,
            "aspect_ratio": "2:3",
            "format": "png",
            "quality": DEFAULT_QUALITY,
        },
        "generated_dimensions": generated_dimensions,
        "binary_written": binary_written,
        "binary_committed": False,
        "safe_to_share": True,
        "docs_checked": docs_checked,
    }
