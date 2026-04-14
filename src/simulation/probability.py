"""
Probability Engine

Implements  P(outcome | action, context)  using a weighted Bayesian-inspired
formula that combines:

* The student's soft-skill baseline (from their UserProfile).
* A linguistic quality score derived from the action text.
* The cumulative momentum of the session so far.
* A scenario-specific difficulty multiplier.
"""

from __future__ import annotations

import math
from typing import Optional

from ..models.user_profile import UserProfile
from ..models.simulation_state import SimulationState


class ProbabilityEngine:
    """
    Calculates the probability of a successful outcome for a given action
    within the current simulation context.

    Formula (simplified Bayesian weighting)
    ----------------------------------------
    P = clamp(base_skill  * w1
              + linguistic * w2
              + momentum   * w3
              - difficulty * w4,
              min=0.05, max=0.95)

    Weights  w1=0.40, w2=0.25, w3=0.25, w4=0.10
    """

    _WEIGHTS = {"skill": 0.40, "linguistic": 0.25, "momentum": 0.25, "difficulty": 0.10}

    _DIFFICULTY: dict[str, float] = {
        "interview": 0.15,
        "conflict": 0.20,
        "pitch": 0.18,
    }

    # Positive linguistic signals
    _POSITIVE_SIGNALS = {
        "because", "therefore", "specifically", "for example", "evidence",
        "data", "result", "achieve", "improve", "solution", "confident",
        "strategy", "plan", "metric", "measure",
    }

    # Negative linguistic signals
    _NEGATIVE_SIGNALS = {
        "maybe", "i don't know", "not sure", "possibly", "kind of",
        "sort of", "i guess", "whatever", "nothing", "fail", "mistake",
    }

    def __init__(self, scenario_type: str = "interview") -> None:
        self.scenario_type = scenario_type if scenario_type in self._DIFFICULTY else "interview"

    def calculate(
        self,
        user_action: str,
        profile: UserProfile,
        state: Optional[SimulationState] = None,
    ) -> float:
        """
        Return P(success | action, context) for the current turn.

        Parameters
        ----------
        user_action : What the student said or wrote.
        profile     : The student's Digital Twin profile.
        state       : Running simulation state (for momentum calculation).
        """
        skill_score = self._skill_component(profile)
        linguistic_score = self._linguistic_component(user_action)
        momentum_score = self._momentum_component(state)
        difficulty = self._DIFFICULTY[self.scenario_type]

        raw = (
            skill_score * self._WEIGHTS["skill"]
            + linguistic_score * self._WEIGHTS["linguistic"]
            + momentum_score * self._WEIGHTS["momentum"]
            - difficulty * self._WEIGHTS["difficulty"]
        )
        return self._clamp(raw, 0.05, 0.95)

    # ------------------------------------------------------------------
    # Component helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _skill_component(profile: UserProfile) -> float:
        """Normalised average of the student's soft-skill scores → [0, 1]."""
        return profile.soft_skills.average() / 10.0

    @staticmethod
    def _linguistic_component(action: str) -> float:
        """
        Score the quality of the student's language on a 0-1 scale.

        Uses positive and negative signal counts plus a fluency heuristic
        (sentence-length variance).
        """
        if not action or not action.strip():
            return 0.1

        words = action.lower().split()
        word_set = set(words)
        n_words = len(words)

        positive_hits = len(ProbabilityEngine._POSITIVE_SIGNALS & word_set)
        negative_hits = len(ProbabilityEngine._NEGATIVE_SIGNALS & word_set)

        # Signal score: each positive hit adds 0.06, each negative subtracts 0.08
        signal_score = 0.5 + (positive_hits * 0.06) - (negative_hits * 0.08)

        # Length fluency: ideal range 20-80 words
        if 20 <= n_words <= 80:
            fluency = 1.0
        elif n_words < 20:
            fluency = n_words / 20.0
        else:
            fluency = max(0.5, 1.0 - (n_words - 80) / 200.0)

        score = (signal_score * 0.7) + (fluency * 0.3)
        return ProbabilityEngine._clamp(score, 0.0, 1.0)

    @staticmethod
    def _momentum_component(state: Optional[SimulationState]) -> float:
        """
        Derive a momentum score from recent turn performance.

        If no previous turns, assume neutral (0.5).
        Uses an exponentially weighted average that favours recent turns.
        """
        if state is None or not state.turns:
            return 0.5

        turns = state.turns[-5:]  # consider last 5 turns at most
        weights = [math.exp(0.5 * i) for i in range(len(turns))]
        weighted_sum = sum(w * t.success_probability for w, t in zip(weights, turns))
        total_weight = sum(weights)
        return weighted_sum / total_weight if total_weight > 0 else 0.5

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))
