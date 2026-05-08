"""Release simulation manifest tests."""

from __future__ import annotations

import pytest

from mb import release_simulation


def test_packaged_release_simulation_manifest_is_valid() -> None:
    manifest = release_simulation.load_manifest()

    assert manifest["schema_version"] == "1.0"
    assert release_simulation.validate_manifest(manifest) == []


def test_release_simulation_tiers_have_expected_prompt_coverage() -> None:
    pr_smoke = release_simulation.simulations_for_tier("pr_smoke")
    prerelease = release_simulation.simulations_for_tier("prerelease_candidate")
    release = release_simulation.simulations_for_tier("release_acceptance")

    assert [sim.id for sim in pr_smoke] == [
        "fresh_first_day",
        "messy_morning_thought_dump",
    ]
    assert len(prerelease) >= 8
    assert len(release) >= 7
    assert sum(1 for sim in prerelease if sim.prompt.strip()) >= 6
    assert all(sim.expected_behaviors for sim in prerelease)
    assert all(sim.must_observe for sim in prerelease)


def test_release_simulation_parser_exposes_expected_tier_choices() -> None:
    from mb import dogfood_harness

    parser = dogfood_harness.build_parser()
    args = parser.parse_args(["--run-claude-print", "--simulation-tier", "pr_smoke"])

    assert args.run_claude_print is True
    assert args.simulation_tier == "pr_smoke"
    with pytest.raises(SystemExit):
        parser.parse_args(["--run-claude-print", "--simulation-tier", "bogus"])


def test_release_simulation_manifest_loads_from_package_data() -> None:
    prompts = release_simulation.claude_prompts_for_tier("pr_smoke")

    assert prompts == (
        (
            "mb-start",
            "/mb-start",
        ),
        (
            "thought-dump",
            "I am opening Dogfood Studio for a normal day. I have ten minutes, "
            "feel fuzzy about whether to improve the onboarding sprint or draft "
            "content, and need you to route me to the right Main Branch primitive "
            "before writing anything durable.",
        ),
    )


def test_score_transcript_flags_provider_overclaim() -> None:
    transcript = """
    I ran mb status for the Dogfood Studio business repo, routed this through
    Sense and Decide, will ask before writing, and will capture evidence.
    Postiz is supported, so I can publish automatically.
    """

    score = release_simulation.score_transcript(transcript)

    assert score["checks"]["runtime_provider_honesty"]["ok"] is False
    assert "proxy evidence" in score["heuristic_notice"]


def test_score_transcript_allows_provider_boundary_disclaimers() -> None:
    transcript = """
    /mb-start is discovered. This routes to Sense -> Decide with a clear next
    action. I will ask before writing and will not send the email, will not
    publish automatically, and will not spend money without approval.
    """

    score = release_simulation.score_transcript(transcript)

    assert score["checks"]["runtime_provider_honesty"]["ok"] is True


def test_score_transcript_uses_tighter_discovery_and_loop_keywords() -> None:
    generic = """
    Main Branch has common sense about relationship health, shipment status,
    and router setup. A generic skill might help.
    """
    routed = "/mb-start was discovered. Expected route: Sense -> Decide."

    generic_score = release_simulation.score_transcript(generic)
    routed_score = release_simulation.score_transcript(routed)

    assert generic_score["checks"]["skill_discovery"]["ok"] is False
    assert generic_score["checks"]["loop_routing"]["ok"] is False
    assert routed_score["checks"]["skill_discovery"]["ok"] is True
    assert routed_score["checks"]["loop_routing"]["ok"] is True
