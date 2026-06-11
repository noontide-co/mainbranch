"""Push facts parsing."""

from __future__ import annotations

from pathlib import Path

from mb import pushes as pushes_mod


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_push_facts_include_media_fields(tmp_path: Path) -> None:
    _write(
        tmp_path / "pushes" / "2026-06-11-ad-batch" / "push.md",
        (
            "---\n"
            "type: push\n"
            "slug: ad-batch\n"
            "kind: launch\n"
            "status: active\n"
            "health: on-track\n"
            "owner: Devon\n"
            "audience: roofers\n"
            "offer: core/offers/roofing/offer.md\n"
            "promise: Booked-out calendar.\n"
            "media_location: https://drive.google.com/drive/folders/fixture\n"
            "media_backend: google-drive\n"
            "---\n"
            "# Ad batch\n"
        ),
    )
    _write(
        tmp_path / "pushes" / "2026-06-12-no-media" / "push.md",
        (
            "---\n"
            "type: push\n"
            "slug: no-media\n"
            "kind: launch\n"
            "status: planned\n"
            "health: unknown\n"
            "owner: Devon\n"
            "audience: roofers\n"
            "offer: core/offers/roofing/offer.md\n"
            "promise: Booked-out calendar.\n"
            "---\n"
            "# No media\n"
        ),
    )

    report = pushes_mod.facts(tmp_path)
    by_slug = {record["slug"]: record for record in report["records"]}

    assert by_slug["ad-batch"]["media_location"] == (
        "https://drive.google.com/drive/folders/fixture"
    )
    assert by_slug["ad-batch"]["media_backend"] == "google-drive"
    assert by_slug["no-media"]["media_location"] == ""
    assert by_slug["no-media"]["media_backend"] == ""
