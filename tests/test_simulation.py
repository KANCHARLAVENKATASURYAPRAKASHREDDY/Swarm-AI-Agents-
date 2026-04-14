"""Tests for the simulation probability engine, branching engine, and core engine."""

import pytest
from src.models.user_profile import UserProfile, SoftSkills, PersonalityTraits, PastExperience
from src.models.simulation_state import SimulationState, Turn
from src.simulation.probability import ProbabilityEngine
from src.simulation.branches import BranchingEngine
from src.simulation.engine import SimulationEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_profile():
    return UserProfile(
        name="Test Student",
        academic_gpa=3.5,
        soft_skills=SoftSkills(
            communication=7.0,
            leadership=6.0,
            problem_solving=8.0,
            emotional_intelligence=6.5,
            adaptability=7.5,
            negotiation=5.5,
        ),
        strengths=["problem-solving"],
        weaknesses=["negotiation"],
    )


def _make_state():
    return SimulationState(
        scenario_title="Test Scenario",
        scenario_description="Test.",
    )


# ---------------------------------------------------------------------------
# ProbabilityEngine
# ---------------------------------------------------------------------------

class TestProbabilityEngine:
    def test_result_in_valid_range(self):
        engine = ProbabilityEngine()
        profile = _make_profile()
        prob = engine.calculate("I believe in data-driven solutions.", profile)
        assert 0.05 <= prob <= 0.95

    def test_strong_action_scores_higher_than_weak(self):
        engine = ProbabilityEngine()
        profile = _make_profile()
        strong = (
            "Specifically, I used data to achieve the target because I had a clear metric. "
            "For example, I improved throughput by 40% through evidence-based refactoring."
        )
        weak = "I'm not sure maybe I kind of know the answer I guess."
        assert engine.calculate(strong, profile) > engine.calculate(weak, profile)

    def test_empty_action_still_returns_valid_prob(self):
        engine = ProbabilityEngine()
        prob = engine.calculate("", _make_profile())
        assert 0.05 <= prob <= 0.95

    def test_unknown_scenario_defaults_to_interview(self):
        engine = ProbabilityEngine(scenario_type="nonsense")
        assert engine.scenario_type == "interview"

    def test_momentum_component_with_previous_turns(self):
        """With high prior turns, momentum should push the score up."""
        engine = ProbabilityEngine()
        profile = _make_profile()
        state = _make_state()
        # Inject high-probability past turns
        for i in range(3):
            state.turns.append(
                Turn(turn_number=i + 1, user_action="good", success_probability=0.9, cumulative_score=80.0)
            )
        prob_with_momentum = engine.calculate("I believe this strategy works.", profile, state)
        prob_no_momentum = engine.calculate("I believe this strategy works.", profile, None)
        assert prob_with_momentum >= prob_no_momentum


# ---------------------------------------------------------------------------
# BranchingEngine
# ---------------------------------------------------------------------------

class TestBranchingEngine:
    @pytest.mark.parametrize("scenario_type", ["interview", "conflict", "pitch"])
    def test_generates_three_paths(self, scenario_type):
        engine = BranchingEngine(scenario_type=scenario_type)
        profile = _make_profile()
        state = _make_state()
        state.turns.append(
            Turn(turn_number=1, user_action="test", success_probability=0.6, cumulative_score=60.0)
        )
        paths = engine.generate(state, profile)
        assert len(paths) == 3

    def test_path_types_present(self):
        engine = BranchingEngine()
        state = _make_state()
        state.turns.append(
            Turn(turn_number=1, user_action="test", success_probability=0.6, cumulative_score=60.0)
        )
        paths = engine.generate(state, _make_profile())
        types = {p.path_type for p in paths}
        assert types == {"optimal", "realistic", "safety_net"}

    def test_score_ordering(self):
        """Optimal >= Realistic >= Safety-Net."""
        engine = BranchingEngine()
        state = _make_state()
        state.turns.append(
            Turn(turn_number=1, user_action="test", success_probability=0.6, cumulative_score=65.0)
        )
        paths = engine.generate(state, _make_profile())
        by_type = {p.path_type: p.final_score for p in paths}
        assert by_type["optimal"] >= by_type["realistic"]
        assert by_type["realistic"] >= by_type["safety_net"]

    def test_descriptions_are_non_empty(self):
        engine = BranchingEngine()
        state = _make_state()
        state.turns.append(
            Turn(turn_number=1, user_action="test", success_probability=0.7, cumulative_score=70.0)
        )
        for path in engine.generate(state, _make_profile()):
            assert path.description.strip()


# ---------------------------------------------------------------------------
# SimulationEngine (integration-level)
# ---------------------------------------------------------------------------

class TestSimulationEngine:
    def _make_engine(self, scenario_type="interview"):
        return SimulationEngine(
            profile=_make_profile(),
            scenario_title="Job Interview",
            scenario_description="A challenging technical interview.",
            scenario_type=scenario_type,
            event_frequency=0.0,   # Disable random events for determinism
            env_seed=0,
        )

    def test_process_turn_returns_turn(self):
        engine = self._make_engine()
        turn = engine.process_turn("I believe this solution is optimal because of the data.")
        assert turn.turn_number == 1
        assert turn.antagonist_reply
        assert 0.05 <= turn.success_probability <= 0.95
        assert 0.0 <= turn.cumulative_score <= 100.0

    def test_multiple_turns_increment(self):
        engine = self._make_engine()
        engine.process_turn("First action.")
        turn2 = engine.process_turn("Second action with more detail therefore I propose this.")
        assert turn2.turn_number == 2

    def test_finalise_produces_three_paths(self):
        engine = self._make_engine()
        engine.process_turn("I believe we can solve this specifically by refactoring.")
        state = engine.finalise()
        assert state.is_complete
        assert len(state.outcome_paths) == 3

    def test_process_turn_after_finalise_raises(self):
        engine = self._make_engine()
        engine.process_turn("test")
        engine.finalise()
        with pytest.raises(RuntimeError, match="complete"):
            engine.process_turn("late action")

    def test_reset_restarts_session(self):
        engine = self._make_engine()
        engine.process_turn("test")
        engine.finalise()
        engine.reset()
        assert not engine.state.is_complete
        assert engine.state.turns == []
        # Should be able to process again
        turn = engine.process_turn("new action")
        assert turn.turn_number == 1

    def test_invalid_profile_raises_on_init(self):
        bad_profile = UserProfile(name="", academic_gpa=3.5)
        with pytest.raises(ValueError, match="name"):
            SimulationEngine(
                profile=bad_profile,
                scenario_title="X",
                scenario_description="Y",
            )

    @pytest.mark.parametrize("scenario_type", ["interview", "conflict", "pitch"])
    def test_all_scenario_types(self, scenario_type):
        engine = self._make_engine(scenario_type=scenario_type)
        turn = engine.process_turn("I have a strategy because I collected relevant data.")
        assert turn.antagonist_reply
