"""Tests for data models: UserProfile, SimulationState."""

import pytest
from src.models.user_profile import (
    UserProfile,
    PersonalityTraits,
    SoftSkills,
    PastExperience,
)
from src.models.simulation_state import SimulationState, Turn, OutcomePath


# ---------------------------------------------------------------------------
# PersonalityTraits
# ---------------------------------------------------------------------------

class TestPersonalityTraits:
    def test_defaults_are_valid(self):
        pt = PersonalityTraits()
        pt.validate()  # should not raise

    def test_out_of_range_raises(self):
        pt = PersonalityTraits(openness=11.0)
        with pytest.raises(ValueError, match="openness"):
            pt.validate()

    def test_negative_raises(self):
        pt = PersonalityTraits(neuroticism=-1.0)
        with pytest.raises(ValueError, match="neuroticism"):
            pt.validate()


# ---------------------------------------------------------------------------
# SoftSkills
# ---------------------------------------------------------------------------

class TestSoftSkills:
    def test_average_correct(self):
        ss = SoftSkills(
            communication=8.0,
            leadership=6.0,
            problem_solving=7.0,
            emotional_intelligence=5.0,
            adaptability=9.0,
            negotiation=7.0,
        )
        assert ss.average() == pytest.approx(7.0)

    def test_validate_out_of_range(self):
        ss = SoftSkills(leadership=12.0)
        with pytest.raises(ValueError, match="leadership"):
            ss.validate()


# ---------------------------------------------------------------------------
# PastExperience
# ---------------------------------------------------------------------------

class TestPastExperience:
    def test_valid_experience(self):
        exp = PastExperience(
            title="Internship",
            description="Did good work.",
            outcome="positive",
            relevance_score=8.5,
        )
        exp.validate()  # no raise

    def test_invalid_outcome(self):
        exp = PastExperience(title="X", description="Y", outcome="excellent")
        with pytest.raises(ValueError, match="outcome"):
            exp.validate()

    def test_invalid_relevance(self):
        exp = PastExperience(title="X", description="Y", relevance_score=11.0)
        with pytest.raises(ValueError, match="relevance_score"):
            exp.validate()


# ---------------------------------------------------------------------------
# UserProfile
# ---------------------------------------------------------------------------

class TestUserProfile:
    def _make_profile(self, **kwargs):
        defaults = dict(name="Test Student", academic_gpa=3.5)
        defaults.update(kwargs)
        return UserProfile(**defaults)

    def test_valid_profile(self):
        p = self._make_profile()
        p.validate()

    def test_empty_name_raises(self):
        p = self._make_profile(name="  ")
        with pytest.raises(ValueError, match="name"):
            p.validate()

    def test_gpa_out_of_range(self):
        p = self._make_profile(academic_gpa=4.5)
        with pytest.raises(ValueError, match="gpa"):
            p.validate()

    def test_potential_score_range(self):
        p = self._make_profile()
        score = p.potential_score()
        assert 0.0 <= score <= 100.0

    def test_potential_score_increases_with_experience(self):
        p_no_exp = self._make_profile()
        p_with_exp = self._make_profile(
            experiences=[
                PastExperience("E1", "d", "positive", 8.0),
                PastExperience("E2", "d", "neutral", 5.0),
            ]
        )
        assert p_with_exp.potential_score() > p_no_exp.potential_score()


# ---------------------------------------------------------------------------
# SimulationState
# ---------------------------------------------------------------------------

class TestSimulationState:
    def _make_state(self):
        return SimulationState(
            scenario_title="Test Scenario",
            scenario_description="A test scenario.",
        )

    def test_initial_turn_number(self):
        s = self._make_state()
        assert s.current_turn_number() == 1

    def test_latest_turn_none_when_empty(self):
        s = self._make_state()
        assert s.latest_turn() is None

    def test_average_success_probability_default(self):
        s = self._make_state()
        assert s.average_success_probability() == 0.5

    def test_turns_recorded_correctly(self):
        s = self._make_state()
        t1 = Turn(turn_number=1, user_action="Hello", success_probability=0.7, cumulative_score=60.0)
        t2 = Turn(turn_number=2, user_action="World", success_probability=0.3, cumulative_score=55.0)
        s.turns.extend([t1, t2])
        assert s.current_turn_number() == 3
        assert s.latest_turn() == t2
        assert s.average_success_probability() == pytest.approx(0.5)
        assert s.final_cumulative_score() == 55.0
