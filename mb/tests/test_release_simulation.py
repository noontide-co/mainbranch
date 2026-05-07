"""Release simulation manifest tests."""

from __future__ import annotations

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
    assert all(sim.expected_behaviors for sim in prerelease[:6])
    assert all(sim.must_observe for sim in prerelease[:6])


def test_score_transcript_flags_provider_overclaim() -> None:
    transcript = """
    I ran mb status for the Dogfood Studio business repo, routed this through
    Sense and Decide, will ask before writing, and will capture evidence.
    Postiz is supported, so I can publish automatically.
    """

    score = release_simulation.score_transcript(transcript)

    assert score["checks"]["runtime_provider_honesty"]["ok"] is False
    assert "proxy evidence" in score["heuristic_notice"]
