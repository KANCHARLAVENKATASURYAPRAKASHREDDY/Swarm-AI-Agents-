"""
Branching Engine

Computes three diverging outcome paths for every simulation session:

1. **Optimal Path**    – What would have happened if the student played
                         perfectly to their strengths.
2. **Realistic Path**  – The most probable outcome based on actual performance.
3. **Safety-Net Failure** – A constructive look at what failure looks like,
                            and why it happened.
"""

from __future__ import annotations

from ..models.user_profile import UserProfile
from ..models.simulation_state import SimulationState, OutcomePath


class BranchingEngine:
    """
    Generates the three outcome paths at the end of a simulation session.
    """

    # Scenario-flavoured language for each outcome tier
    _TEMPLATES: dict[str, dict[str, dict[str, str]]] = {
        "interview": {
            "optimal": {
                "title": "You Aced It — Offer Extended",
                "description": (
                    "In this path you leveraged your {strengths} seamlessly. "
                    "Each answer was concise, evidence-backed, and showed strategic thinking. "
                    "The interviewer fast-tracked you to a second round within 24 hours, "
                    "resulting in an offer at the top of the salary band."
                ),
            },
            "realistic": {
                "title": "Solid Performance — Shortlisted",
                "description": (
                    "Your actual performance secured you a shortlist position. "
                    "The panel noted your technical depth but flagged that responses on "
                    "{weaknesses} lacked specificity. Expect a follow-up task or a second "
                    "interview to clarify those gaps."
                ),
            },
            "safety_net": {
                "title": "Rejected — But Here's Why",
                "description": (
                    "When your weaknesses around {weaknesses} dominated, the interview "
                    "stalled. Brief, uncertain responses signalled a lack of preparation. "
                    "The hiring team moved on. This is fixable: rehearse structured STAR "
                    "answers for your two biggest gap areas."
                ),
            },
        },
        "conflict": {
            "optimal": {
                "title": "Conflict De-escalated — Trust Rebuilt",
                "description": (
                    "By combining {strengths} with empathetic listening, you guided the "
                    "conversation from blame to problem-solving. The manager left with a "
                    "revised plan and renewed confidence in your leadership."
                ),
            },
            "realistic": {
                "title": "Tension Managed — Partial Resolution",
                "description": (
                    "You held your ground on key points but let defensiveness surface when "
                    "challenged on {weaknesses}. The situation stabilised without full "
                    "resolution; a follow-up meeting has been requested."
                ),
            },
            "safety_net": {
                "title": "Escalated — Requires HR Intervention",
                "description": (
                    "Unchecked {weaknesses} caused the dialogue to deteriorate. "
                    "Blame language replaced constructive framing and the manager escalated "
                    "to HR. Key takeaway: prepare a 'bridge statement' to use when "
                    "emotions spike."
                ),
            },
        },
        "pitch": {
            "optimal": {
                "title": "Deal Closed — Pilot Signed",
                "description": (
                    "Your {strengths} shone through. You reframed every objection into an "
                    "opportunity, backed claims with data, and built visible rapport with "
                    "the decision-maker. A pilot contract was signed the same week."
                ),
            },
            "realistic": {
                "title": "Interest Secured — Proposal Requested",
                "description": (
                    "The client is engaged but cautious. Gaps around {weaknesses} left "
                    "some ROI questions unanswered. They have asked for a detailed proposal "
                    "before proceeding — a standard next step, but not a close."
                ),
            },
            "safety_net": {
                "title": "No Deal — Opportunity Lost",
                "description": (
                    "Uncertainty about {weaknesses} eroded credibility at the decisive "
                    "moment. The client cited 'lack of clear differentiation' and chose a "
                    "competitor. Sharpen your unique-value narrative and pre-empt the top "
                    "three objections before your next pitch."
                ),
            },
        },
    }

    def __init__(self, scenario_type: str = "interview") -> None:
        self.scenario_type = scenario_type if scenario_type in self._TEMPLATES else "interview"

    def generate(self, state: SimulationState, profile: UserProfile) -> list[OutcomePath]:
        """
        Produce the three outcome paths.

        Scores are anchored to actual performance plus deltas:
        * Optimal  = actual + 25% of remaining headroom, capped at 98.
        * Realistic = actual performance score as-is.
        * Safety-Net = actual − 20%, floored at 10.
        """
        actual_score = state.final_cumulative_score()
        optimal_score = min(98.0, actual_score + 0.25 * (100.0 - actual_score))
        safety_net_score = max(10.0, actual_score - 20.0)

        strengths_text = ", ".join(profile.strengths[:3]) if profile.strengths else "core competencies"
        weaknesses_text = ", ".join(profile.weaknesses[:2]) if profile.weaknesses else "identified gaps"

        templates = self._TEMPLATES[self.scenario_type]

        paths = [
            OutcomePath(
                path_type="optimal",
                title=templates["optimal"]["title"],
                description=templates["optimal"]["description"].format(
                    strengths=strengths_text,
                    weaknesses=weaknesses_text,
                ),
                final_score=round(optimal_score, 1),
            ),
            OutcomePath(
                path_type="realistic",
                title=templates["realistic"]["title"],
                description=templates["realistic"]["description"].format(
                    strengths=strengths_text,
                    weaknesses=weaknesses_text,
                ),
                final_score=round(actual_score, 1),
            ),
            OutcomePath(
                path_type="safety_net",
                title=templates["safety_net"]["title"],
                description=templates["safety_net"]["description"].format(
                    strengths=strengths_text,
                    weaknesses=weaknesses_text,
                ),
                final_score=round(safety_net_score, 1),
            ),
        ]
        return paths
