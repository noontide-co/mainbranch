"""Guards for sales-video/VSL workflow routing."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("prompt", "skill_path", "expected_route"),
    [
        ("write a VSL", ".claude/skills/mb-site/SKILL.md", "/mb-site"),
        ("about page video", ".claude/skills/mb-site/SKILL.md", "/mb-site"),
        ("video ad script", ".claude/skills/mb-ads/SKILL.md", "/mb-ads"),
        ("analyze this VSL", ".claude/skills/mb-think/SKILL.md", "/mb-think"),
        (
            "short clips from sales video",
            ".claude/skills/mb-organic/SKILL.md",
            "/mb-organic",
        ),
    ],
)
def test_natural_sales_video_prompts_route_to_broader_skills(
    prompt: str, skill_path: str, expected_route: str
) -> None:
    start = _read(".claude/skills/mb-start/SKILL.md").lower()
    skill = _read(skill_path).lower()

    assert prompt.lower() in start or prompt.lower() in skill
    assert expected_route in start
    assert "/mb-vsl` is a compatibility router" in start


def test_vsl_framework_references_are_shared_and_reachable_from_broader_skills() -> None:
    shared_refs = [
        ".claude/reference/conversion/vsl-routing.md",
        ".claude/reference/conversion/vsl/skool-18-section.md",
        ".claude/reference/conversion/vsl/b2b-haynes.md",
        ".claude/reference/conversion/vsl/examples/b2b-ijanitorial.md",
    ]
    for ref in shared_refs:
        assert (REPO_ROOT / ref).is_file()

    consumers = [
        ".claude/skills/mb-think/references/sales-video-research.md",
        ".claude/skills/mb-site/references/sales-video.md",
        ".claude/skills/mb-ads/references/long-form-video-ads.md",
        ".claude/skills/mb-organic/references/sales-video-repurpose.md",
        ".claude/skills/mb-vsl/SKILL.md",
    ]
    for consumer in consumers:
        text = _read(consumer)
        assert ".claude/reference/conversion/vsl-routing.md" in text
        assert ".claude/skills/mb-vsl/references" not in text

    assert not (REPO_ROOT / ".claude/skills/mb-vsl/references/frameworks").exists()


def test_operator_help_avoids_retired_data_repo_and_public_conductor_framing() -> None:
    scanned = [
        ".claude/skills/mb-help/SKILL.md",
        ".claude/skills/mb-help/references/two-repos.md",
        ".claude/skills/mb-help/references/workspace-setup.md",
        ".claude/skills/mb-help/references/troubleshooting.md",
        ".claude/reference/engine-path-resolution.md",
        ".claude/reference/conversion/vsl-routing.md",
        ".claude/reference/business-primitives/setup-patterns.md",
        ".claude/skills/mb-start/SKILL.md",
        ".claude/skills/mb-start/references/config-system.md",
        ".claude/skills/mb-start/references/repo-detection.md",
        ".claude/skills/mb-start/references/triage-menu.md",
        ".claude/skills/mb-ads/references/preflight-algorithm.md",
        ".claude/skills/mb-site/references/concept-variations.md",
        ".claude/skills/mb-skill-concept/references/concept-variations.md",
        ".claude/skills/mb-setup/SKILL.md",
        ".claude/skills/mb-setup/references/templates.md",
        "README.md",
        "docs/beginner-setup.md",
        "docs/operator-loops.md",
    ]
    retired_terms = [
        "data repo",
        "engine + data",
        "your data",
        "two-repo model",
        "data (this repo)",
        "shared with all members",
        "<vip_path>",
        "save forever",
        "save to ~/.config/vip/local.yaml",
        "if yes, update `~/.config/vip/local.yaml`",
        "if yes, merge-update `default_repo`",
        "canonical",
        "ground truth",
        "vip-path-resolution",
        "vip path",
        "Conductor",
        "PA config",
        "Pre-Agent",
    ]

    failures: list[str] = []
    for relative in scanned:
        text = _read(relative).lower()
        for term in retired_terms:
            if term.lower() in text:
                failures.append(f"{relative}: contains retired phrase {term!r}")

    assert failures == []
