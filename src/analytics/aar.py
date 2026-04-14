"""
After-Action Report (AAR) Generator

Produces a structured, human-readable debrief at the close of each simulation
session, covering:

* Session Summary  – scenario, turns, average P(success).
* Three Outcome Paths – Optimal, Realistic, Safety-Net.
* Gap Analysis     – delta between maximum potential and actual performance.
* Actionable Insights – three concrete improvement steps derived from
                         Observer notes and profile data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ..models.user_profile import UserProfile
from ..models.simulation_state import SimulationState
from ..agents.observer import Observer


@dataclass
class AARReport:
    """Structured representation of the After-Action Report."""

    student_name: str
    scenario_title: str
    total_turns: int
    average_success_probability: float
    final_cumulative_score: float
    maximum_potential_score: float
    gap_score: float                     # potential - actual
    outcome_paths: list = field(default_factory=list)
    observer_notes: List[str] = field(default_factory=list)
    actionable_insights: List[str] = field(default_factory=list)

    def to_text(self) -> str:
        """Render the AAR as a formatted plain-text report."""
        lines = [
            "=" * 70,
            "          AFTER-ACTION REPORT (AAR) — DIGITAL TWIN SIMULATION",
            "=" * 70,
            f"  Student   : {self.student_name}",
            f"  Scenario  : {self.scenario_title}",
            f"  Turns     : {self.total_turns}",
            f"  Avg P(success): {self.average_success_probability:.2f}",
            f"  Final Score   : {self.final_cumulative_score:.1f} / 100",
            f"  Max Potential : {self.maximum_potential_score:.1f} / 100",
            f"  Gap           : {self.gap_score:.1f} points",
            "",
            "─" * 70,
            "  OUTCOME PATHS",
            "─" * 70,
        ]

        for path in self.outcome_paths:
            lines += [
                f"  [{path.path_type.upper()}]  {path.title}  (Score: {path.final_score})",
                f"  {path.description}",
                "",
            ]

        lines += [
            "─" * 70,
            "  OBSERVER HIGHLIGHTS (last 3 notes)",
            "─" * 70,
        ]
        for note in self.observer_notes[-3:]:
            lines.append(f"  • {note}")

        lines += [
            "",
            "─" * 70,
            "  ACTIONABLE INSIGHTS",
            "─" * 70,
        ]
        for i, insight in enumerate(self.actionable_insights, start=1):
            lines.append(f"  {i}. {insight}")

        lines += ["", "=" * 70]
        return "\n".join(lines)


class AfterActionReport:
    """
    Factory that builds an AARReport from a finalised SimulationState,
    the student's UserProfile, and the Observer's accumulated notes.
    """

    def __init__(
        self,
        state: SimulationState,
        profile: UserProfile,
        observer: Observer,
    ) -> None:
        if not state.is_complete:
            raise ValueError("Cannot generate AAR for an incomplete simulation. Call engine.finalise() first.")
        self._state = state
        self._profile = profile
        self._observer = observer

    def generate(self) -> AARReport:
        """Build and return the AARReport."""
        actual_score = self._state.final_cumulative_score()
        potential_score = self._profile.potential_score()
        gap = max(0.0, potential_score - actual_score)

        insights = self._derive_insights(actual_score, gap)

        return AARReport(
            student_name=self._profile.name,
            scenario_title=self._state.scenario_title,
            total_turns=len(self._state.turns),
            average_success_probability=round(self._state.average_success_probability(), 3),
            final_cumulative_score=round(actual_score, 1),
            maximum_potential_score=round(potential_score, 1),
            gap_score=round(gap, 1),
            outcome_paths=self._state.outcome_paths,
            observer_notes=self._observer.get_all_notes(),
            actionable_insights=insights,
        )

    # ------------------------------------------------------------------
    # Insight generation
    # ------------------------------------------------------------------

    def _derive_insights(self, actual_score: float, gap: float) -> List[str]:
        """
        Derive three actionable insights from:
        * Gap magnitude.
        * Known weaknesses in the profile.
        * Observer notes pattern analysis.
        """
        insights: List[str] = []

        # Insight 1 – biggest weakness
        if self._profile.weaknesses:
            w = self._profile.weaknesses[0]
            insights.append(
                f"Focus improvement on '{w}': dedicate 20 minutes daily to structured "
                "practice scenarios specifically targeting this area."
            )
        else:
            insights.append(
                "Identify and document your top two skill gaps through peer or mentor feedback "
                "before your next high-stakes encounter."
            )

        # Insight 2 – communication or reasoning based on notes
        notes_text = " ".join(self._observer.get_all_notes()).lower()
        if "brief" in notes_text or "under-confidence" in notes_text:
            insights.append(
                "Expand your response depth: use the STAR framework (Situation, Task, Action, "
                "Result) to ensure every answer is at least 40-60 words with concrete evidence."
            )
        elif "lengthy" in notes_text or "conciseness" in notes_text:
            insights.append(
                "Practice concision: set a 90-second timer when rehearsing answers. "
                "Cut filler phrases ('kind of', 'sort of') and lead with your main point."
            )
        else:
            insights.append(
                "Strengthen logical connectors in your language ('because', 'therefore', "
                "'specifically') to signal structured thinking to evaluators."
            )

        # Insight 3 – score gap
        if gap > 20:
            insights.append(
                f"Your performance gap is {gap:.1f} points — significant room remains. "
                "Run two additional simulation sessions per week focused on your weakest turns, "
                "tracking P(success) improvement over time."
            )
        elif gap > 10:
            insights.append(
                f"You are within {gap:.1f} points of your potential. "
                "One targeted mock session plus reflective journaling after each practice "
                "round should close this gap within a month."
            )
        else:
            insights.append(
                "You are performing close to your maximum potential — "
                "shift focus to consistency under pressure and managing environmental disruptions."
            )

        return insights
