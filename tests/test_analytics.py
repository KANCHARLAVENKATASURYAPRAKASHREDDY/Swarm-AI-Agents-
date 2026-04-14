"""Tests for the After-Action Report generator."""

import pytest
from src.models.user_profile import UserProfile, SoftSkills, PastExperience
from src.models.simulation_state import SimulationState, Turn, OutcomePath
from src.agents.observer import Observer
from src.analytics.aar import AfterActionReport, AARReport


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_profile():
    return UserProfile(
        name="Jordan Smith",
        academic_gpa=3.2,
        soft_skills=SoftSkills(
            communication=6.5,
            leadership=5.5,
            problem_solving=7.5,
            emotional_intelligence=6.0,
            adaptability=7.0,
            negotiation=5.0,
        ),
        strengths=["analytical thinking", "persistence"],
        weaknesses=["public speaking", "time management"],
    )


def _make_complete_state():
    state = SimulationState(
        scenario_title="Management Conflict",
        scenario_description="Resolving a team conflict.",
    )
    for i in range(3):
        state.turns.append(
            Turn(
                turn_number=i + 1,
                user_action="I believe we should address this because the data supports it.",
                success_probability=0.6 + i * 0.05,
                cumulative_score=55.0 + i * 5.0,
            )
        )
    state.outcome_paths = [
        OutcomePath("optimal", "Great", "You excelled.", 90.0),
        OutcomePath("realistic", "Good", "Solid performance.", 65.0),
        OutcomePath("safety_net", "Missed", "Gaps appeared.", 45.0),
    ]
    state.is_complete = True
    return state


def _make_observer_with_notes(profile):
    obs = Observer(profile)
    for t in _make_complete_state().turns:
        obs.analyse_turn(t)
    return obs


# ---------------------------------------------------------------------------
# AARReport.to_text
# ---------------------------------------------------------------------------

class TestAARReportToText:
    def test_contains_student_name(self):
        profile = _make_profile()
        state = _make_complete_state()
        obs = _make_observer_with_notes(profile)
        report = AfterActionReport(state, profile, obs).generate()
        text = report.to_text()
        assert "Jordan Smith" in text

    def test_contains_scenario_title(self):
        profile = _make_profile()
        state = _make_complete_state()
        obs = _make_observer_with_notes(profile)
        report = AfterActionReport(state, profile, obs).generate()
        text = report.to_text()
        assert "Management Conflict" in text

    def test_contains_three_paths(self):
        profile = _make_profile()
        state = _make_complete_state()
        obs = _make_observer_with_notes(profile)
        report = AfterActionReport(state, profile, obs).generate()
        text = report.to_text()
        assert "OPTIMAL" in text
        assert "REALISTIC" in text
        assert "SAFETY_NET" in text

    def test_contains_actionable_insights(self):
        profile = _make_profile()
        state = _make_complete_state()
        obs = _make_observer_with_notes(profile)
        report = AfterActionReport(state, profile, obs).generate()
        text = report.to_text()
        assert "ACTIONABLE INSIGHTS" in text


# ---------------------------------------------------------------------------
# AfterActionReport.generate
# ---------------------------------------------------------------------------

class TestAfterActionReportGenerate:
    def test_raises_if_not_complete(self):
        profile = _make_profile()
        incomplete = SimulationState(scenario_title="X", scenario_description="Y")
        obs = Observer(profile)
        with pytest.raises(ValueError, match="incomplete"):
            AfterActionReport(incomplete, profile, obs).generate()

    def test_gap_score_non_negative(self):
        profile = _make_profile()
        state = _make_complete_state()
        obs = _make_observer_with_notes(profile)
        report = AfterActionReport(state, profile, obs).generate()
        assert report.gap_score >= 0.0

    def test_three_actionable_insights(self):
        profile = _make_profile()
        state = _make_complete_state()
        obs = _make_observer_with_notes(profile)
        report = AfterActionReport(state, profile, obs).generate()
        assert len(report.actionable_insights) == 3

    def test_report_fields_populated(self):
        profile = _make_profile()
        state = _make_complete_state()
        obs = _make_observer_with_notes(profile)
        report = AfterActionReport(state, profile, obs).generate()
        assert report.student_name == "Jordan Smith"
        assert report.total_turns == 3
        assert 0.0 <= report.average_success_probability <= 1.0
        assert 0.0 <= report.final_cumulative_score <= 100.0
        assert report.maximum_potential_score > 0.0

    def test_insights_include_weakness(self):
        profile = _make_profile()
        state = _make_complete_state()
        obs = _make_observer_with_notes(profile)
        report = AfterActionReport(state, profile, obs).generate()
        combined = " ".join(report.actionable_insights).lower()
        # First insight should reference the first weakness
        assert "public speaking" in combined
