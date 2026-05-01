"""``mb doctor`` smoke + cloud-backup detection."""

from __future__ import annotations

from pathlib import Path

from mb.doctor import _detect_cloud_paths, run


def test_doctor_runs_on_empty_dir(tmp_path: Path) -> None:
    report = run(path=str(tmp_path))
    assert "checks" in report
    names = {c["name"] for c in report["checks"]}
    assert {"claude-code", "gh-auth", "network", "anti-cloud-backup"}.issubset(names)


def test_cloud_path_detection_via_symlink(tmp_path: Path, monkeypatch) -> None:
    # Build a fake repo whose core/finance/ is a symlink pointing at a path
    # whose realpath includes "Dropbox".
    fake_home = tmp_path / "home"
    cloud = fake_home / "Dropbox" / "Stuff"
    cloud.mkdir(parents=True)
    repo = tmp_path / "biz"
    (repo / "core").mkdir(parents=True)
    (repo / "core" / "finance").symlink_to(cloud)

    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    hits = _detect_cloud_paths(repo)
    assert "Dropbox" in hits


def test_doctor_clean_finance_passes(tmp_path: Path) -> None:
    repo = tmp_path / "biz"
    (repo / "core" / "finance").mkdir(parents=True)
    report = run(path=str(repo))
    cloud = next(c for c in report["checks"] if c["name"] == "anti-cloud-backup")
    assert cloud["ok"] is True
