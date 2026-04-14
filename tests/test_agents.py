"""Tests for the three Simulation Council agents."""

import pytest
from src.models.user_profile import UserProfile, SoftSkills, PersonalityTraits
from src.models.simulation_state import SimulationState, Turn
from src.agents.antagonist import Antagonist
from src.agents.environmentalist import Environmentalist
from src.agents.observer import Observer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_profile(name="Student"):
    return UserProfile(
        name=name,
        academic_gpa=3.5,
        soft_skills=SoftSkills(
            communication=7.0,
            leadership=6.0,
            problem_solving=8.0,
            emotional_intelligence=6.5,
            adaptability=7.5,
            negotiation=5.5,
        ),
        strengths=["problem-solving", "adaptability"],
        weaknesses=["negotiation"],
    )


def _make_state():
    return SimulationState(
        scenario_title="Test Interview",
        scenario_description="Demo scenario.",
    )


# ---------------------------------------------------------------------------
# Antagonist
# ---------------------------------------------------------------------------

class TestAntagonist:
    @pytest.mark.parametrize("scenario_type", ["interview", "conflict", "pitch"])
    def test_respond_returns_string_for_all_scenarios(self, scenario_type):
        ant = Antagonist(scenario_type=scenario_type)
        response = ant.respond("I believe in data-driven decisions.", 0.5)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_unknown_scenario_falls_back_to_interview(self):
        ant = Antagonist(scenario_type="unknown_type")
        assert ant.scenario_type == "interview"

    def test_pressure_levels(self):
        ant = Antagonist(scenario_type="interview")
        # low probability → "low" pressure (sceptical response)
        r_low = ant.respond("I dunno", 0.2)
        # high probability → "high" pressure (positive response)
        r_high = ant.respond("Specifically, I used data to improve results by 40%", 0.8)
        assert isinstance(r_low, str)
        assert isinstance(r_high, str)

    def test_role_label(self):
        assert Antagonist(scenario_type="interview").role_label == "Interviewer"
        assert Antagonist(scenario_type="conflict").role_label == "Manager"
        assert Antagonist(scenario_type="pitch").role_label == "Client"

    def test_response_includes_action_snippet(self):
        ant = Antagonist(scenario_type="interview")
        response = ant.respond("My unique approach is data-centric.", 0.5)
        # The template contextual prefix quotes the action
        assert "You said:" in response


# ---------------------------------------------------------------------------
# Environmentalist
# ---------------------------------------------------------------------------

class TestEnvironmentalist:
    def test_no_event_on_turn_1(self):
        env = Environmentalist(event_frequency=1.0, seed=0)
        assert env.maybe_inject_event(1) is None

    def test_event_returns_string_when_fires(self):
        # With frequency=1.0 and turn > 1 it should always fire
        env = Environmentalist(scenario_type="interview", event_frequency=1.0, seed=0)
        event = env.maybe_inject_event(2)
        assert event is not None
        assert isinstance(event, str)
        assert len(event) > 0

    def test_event_may_not_fire_with_zero_frequency(self):
        env = Environmentalist(event_frequency=0.0, seed=0)
        for turn in range(2, 10):
            assert env.maybe_inject_event(turn) is None

    def test_unknown_scenario_defaults_to_interview(self):
        env = Environmentalist(scenario_type="nonsense")
        assert env.scenario_type == "interview"

    @pytest.mark.parametrize("scenario_type", ["interview", "conflict", "pitch"])
    def test_force_event_for_all_scenarios(self, scenario_type):
        env = Environmentalist(scenario_type=scenario_type, seed=1)
        event = env.force_event()
        assert isinstance(event, str)
        assert len(event) > 0

    def test_events_pool_resets_after_exhaustion(self):
        """Ensure events cycle rather than raising once pool is exhausted."""
        env = Environmentalist(scenario_type="interview", event_frequency=1.0, seed=99)
        events = []
        for turn in range(2, 20):
            e = env.maybe_inject_event(turn)
            if e:
                events.append(e)
        assert len(events) > 0


# ---------------------------------------------------------------------------
# Observer
# ---------------------------------------------------------------------------

class TestObserver:
    def test_analyse_turn_returns_string(self):
        obs = Observer(_make_profile())
        turn = Turn(
            turn_number=1,
            user_action="Because of the evidence I gathered I was able to achieve a 40% improvement.",
            success_probability=0.7,
            cumulative_score=65.0,
        )
        note = obs.analyse_turn(turn)
        assert isinstance(note, str)
        assert len(note) > 0

    def test_observer_notes_accumulate(self):
        obs = Observer(_make_profile())
        for i in range(3):
            t = Turn(turn_number=i + 1, user_action="Short action.", success_probability=0.5, cumulative_score=50.0)
            obs.analyse_turn(t)
        assert len(obs.get_all_notes()) == 3

    def test_reset_clears_notes(self):
        obs = Observer(_make_profile())
        obs.analyse_turn(Turn(turn_number=1, user_action="test", success_probability=0.5, cumulative_score=50.0))
        obs.reset()
        assert obs.get_all_notes() == []

    def test_short_action_flagged(self):
        obs = Observer(_make_profile())
        t = Turn(turn_number=1, user_action="I tried.", success_probability=0.5, cumulative_score=50.0)
        note = obs.analyse_turn(t)
        assert "brief" in note.lower() or "under-confidence" in note.lower()

    def test_environmental_event_noted(self):
        obs = Observer(_make_profile())
        t = Turn(
            turn_number=2,
            user_action="I believe this strategy works.",
            success_probability=0.6,
            cumulative_score=58.0,
            environmental_event="Interviewer checks phone urgently.",
        )
        note = obs.analyse_turn(t)
        assert "disruption" in note.lower() or "external" in note.lower() or "adaptability" in note.lower()
