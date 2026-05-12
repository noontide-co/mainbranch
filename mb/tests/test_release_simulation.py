"""Release simulation manifest tests."""

from __future__ import annotations

import pytest

from mb import release_simulation


def test_packaged_release_simulation_manifest_is_valid() -> None:
    manifest = release_simulation.load_manifest()

    assert manifest["schema_version"] == "1.0"
    assert release_simulation.validate_manifest(manifest) == []


def test_release_simulation_exposes_known_fixture_profiles() -> None:
    simulations = release_simulation.simulations()
    profiles = {sim.fixture_profile for sim in simulations}

    assert "broken_skill_wiring_fixture" in profiles
    assert "legacy_drift_fixture" in profiles
    assert "dirty_checkpoint_fixture" in profiles
    assert profiles <= release_simulation.KNOWN_FIXTURE_PROFILES


def test_release_simulation_tiers_have_expected_prompt_coverage() -> None:
    pr_smoke = release_simulation.simulations_for_tier("pr_smoke")
    prerelease = release_simulation.simulations_for_tier("prerelease_candidate")
    release = release_simulation.simulations_for_tier("release_acceptance")

    assert [sim.id for sim in pr_smoke] == [
        "fresh_first_day",
        "messy_morning_thought_dump",
    ]
    assert "ambiguous_mb_start_offer_choice" in {sim.id for sim in prerelease}
    assert "ambiguous_mb_start_offer_choice" in {sim.id for sim in release}
    assert "rich_migration_triage_map" in {sim.id for sim in prerelease}
    assert "rich_migration_triage_map" in {sim.id for sim in release}
    assert "conversion_video_natural_prompt_routing" in {sim.id for sim in prerelease}
    assert "conversion_video_natural_prompt_routing" in {sim.id for sim in release}
    assert "bookkeeping_safety_handoff" in {sim.id for sim in prerelease}
    assert "bookkeeping_safety_handoff" in {sim.id for sim in release}
    assert len(prerelease) >= 8
    assert len(release) >= 7
    assert sum(1 for sim in prerelease if sim.prompt.strip()) >= 6
    assert all(sim.expected_behaviors for sim in prerelease)
    assert all(sim.must_observe for sim in prerelease)


def test_release_simulation_covers_ambiguous_mb_start_offer_choice() -> None:
    simulations = {
        sim.id: sim for sim in release_simulation.simulations_for_tier("prerelease_candidate")
    }

    sim = simulations["ambiguous_mb_start_offer_choice"]

    assert sim.label == "ambiguous-choice"
    assert "1" in sim.prompt
    assert any("duplicate numeric" in item.lower() for item in sim.must_observe)
    assert any(".vip/local.yaml" in item for item in sim.must_not)
    assert "ask_before_write" in sim.expected_behaviors


def test_release_simulation_covers_rich_migration_triage_map() -> None:
    simulations = {
        sim.id: sim for sim in release_simulation.simulations_for_tier("prerelease_candidate")
    }

    sim = simulations["rich_migration_triage_map"]

    assert sim.label == "migration-triage"
    observed = " ".join(sim.must_observe).lower()
    assert "primitive map" in observed
    assert "linked operating boundaries" in " ".join(sim.must_observe)
    assert "live bet" in observed
    assert "durable offer candidate" in observed
    assert "core/offers/<slug>/proof/" in observed
    assert "renaming, deleting" in observed
    assert any("vaguely scan the repo" in item for item in sim.must_not)
    assert any("private local-state" in item for item in sim.must_not)
    assert "repo_boundary_safety" in sim.expected_behaviors


def test_release_simulation_covers_conversion_video_natural_prompts() -> None:
    simulations = {
        sim.id: sim for sim in release_simulation.simulations_for_tier("prerelease_candidate")
    }

    sim = simulations["conversion_video_natural_prompt_routing"]

    prompt = sim.prompt.lower()
    assert "write a vsl for this offer" in prompt
    assert "sales video for my about page" in prompt
    assert "video ad script" in prompt
    assert "analyze this vsl and extract the pitch" in prompt
    assert "short clips from this sales video" in prompt
    observed = " ".join(sim.must_observe).lower()
    assert "/mb-site" in observed
    assert "/mb-ads" in observed
    assert "/mb-think" in observed
    assert "/mb-organic" in observed
    assert "standalone /mb-vsl skill" in observed
    assert "loop_routing" in sim.expected_behaviors
    assert "ask_before_write" in sim.expected_behaviors


def test_release_simulation_covers_bookkeeping_safety_handoff() -> None:
    simulations = {
        sim.id: sim for sim in release_simulation.simulations_for_tier("prerelease_candidate")
    }

    sim = simulations["bookkeeping_safety_handoff"]

    prompt = sim.prompt.lower()
    assert "hledger" in prompt
    assert "real finance" in prompt
    observed = " ".join(sim.must_observe).lower()
    blocked = " ".join(sim.must_not).lower()
    assert "mb books check" in observed
    assert "mb connect" in observed
    assert "mb educational hledger" in observed
    assert ".mb/private/" in observed
    assert "beancount" in blocked
    assert "raw finance data" in observed
    assert "bookkeeping_safety" in sim.expected_behaviors
    assert "runtime_provider_honesty" in sim.expected_behaviors


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


def test_score_transcript_checks_bookkeeping_safety_language() -> None:
    generic = "Finance looks fine. Put your books in the repo and continue."
    grounded = """
    I ran mb books check and mb connect status. hledger is the bookkeeping rail,
    real ledgers stay in the private books vault, and the summary evidence is
    public-safe.
    """

    generic_score = release_simulation.score_transcript(generic)
    grounded_score = release_simulation.score_transcript(grounded)

    assert generic_score["checks"]["bookkeeping_safety"]["ok"] is False
    assert grounded_score["checks"]["bookkeeping_safety"]["ok"] is True


@pytest.mark.parametrize(
    "transcript",
    [
        "Unknown command: /mb-start",
        "Unknown command: /mb-think",
        "Unknown command: /mb-start. Run /help to see available commands.",
        "Unknown command:\n/mb-start",
        "Claude runtime output: Unknown command: /mb-start",
        "Final diagnosis: slash command discovery failure. Unknown command: /mb-start",
    ],
)
def test_score_transcript_flags_observed_unknown_command_failures(transcript: str) -> None:
    score = release_simulation.score_transcript(transcript)

    assert release_simulation.contains_observed_unknown_command_failure(transcript) is True
    assert score["checks"]["skill_discovery"]["ok"] is False
    assert score["checks"]["skill_discovery"]["observed_unknown_command_failure"] is True


def test_score_transcript_allows_unknown_command_diagnostic_wording() -> None:
    transcript = """
    /mb-start was discovered enough to route the repair conversation. When you
    saw `/mb-start` "not showing up" - was it `Unknown command: /mb-start`, the
    slash menu missing it, or something else?
    This is a false positive, not a discovery failure: `Unknown command:
    /mb-start` was quoted symptom language.
    """

    score = release_simulation.score_transcript(transcript)

    assert release_simulation.contains_observed_unknown_command_failure(transcript) is False
    assert score["checks"]["skill_discovery"]["ok"] is True
    assert score["checks"]["skill_discovery"]["observed_unknown_command_failure"] is False


def test_score_transcript_allows_unknown_command_repair_guidance() -> None:
    transcript = """
    /mb-start was discovered, and this is repair guidance. If Claude reports
    `Unknown command: /mb-start`, run `mb start --json`, `mb doctor`, and
    `mb skill repair --repo .` before manual fixes.
    """

    score = release_simulation.score_transcript(transcript)

    assert release_simulation.contains_observed_unknown_command_failure(transcript) is False
    assert score["checks"]["skill_discovery"]["ok"] is True
    assert score["checks"]["supported_repair_path"]["ok"] is True


def test_score_transcript_allows_single_line_conditional_unknown_command_marker() -> None:
    transcript = """
    /mb-start was discovered. If Claude reports Unknown command: /mb-start,
    that's a slash command discovery failure - run mb skill repair.
    """

    score = release_simulation.score_transcript(transcript)

    assert release_simulation.contains_observed_unknown_command_failure(transcript) is False
    assert score["checks"]["skill_discovery"]["ok"] is True
    assert score["checks"]["supported_repair_path"]["ok"] is True
