"""
Antagonist Agent

Plays the role of a realistic counterpart (sceptical interviewer, frustrated
client, etc.) and generates dynamic responses to the student's inputs.

The Antagonist's tone and difficulty adapt to the scenario context and the
student's recent performance so the simulation never feels static.
"""

from __future__ import annotations

import random
from typing import List, Optional

from ..models.user_profile import UserProfile
from ..models.simulation_state import SimulationState, Turn


class Antagonist:
    """
    AI counterpart that reacts dynamically to the student's inputs.

    The response style is driven by:
    * The scenario type (interview / conflict / pitch).
    * The student's most recent success probability.
    * A small random-mood factor that reflects real-world unpredictability.
    """

    # Scenario-specific role labels used in responses
    _ROLE_LABELS = {
        "interview": "Interviewer",
        "conflict": "Manager",
        "pitch": "Client",
    }

    # Tone templates keyed by (scenario_type, pressure_level)
    # pressure_level: "low" (<0.4), "medium" (0.4-0.65), "high" (>0.65)
    _RESPONSE_TEMPLATES: dict[str, dict[str, List[str]]] = {
        "interview": {
            "low": [
                "I'm not fully convinced by that answer. Can you give me a concrete example?",
                "That sounds rehearsed. What would you *actually* do in a real crisis?",
                "I've heard stronger responses today. Let's dig deeper — why *you*?",
            ],
            "medium": [
                "That's a reasonable point. But how does it differentiate you from other candidates?",
                "Okay, I can see your logic. Walk me through the risks you foresee.",
                "Fair enough. Now, what's the biggest mistake you've made professionally?",
            ],
            "high": [
                "Excellent point — I hadn't considered that angle. Please continue.",
                "That's exactly the kind of thinking we need here. How would you scale it?",
                "I'm genuinely impressed. Let's talk about where you see this heading long-term.",
            ],
        },
        "conflict": {
            "low": [
                "This is unacceptable. Every week it's a new excuse — when does the team actually deliver?",
                "I'm not interested in *why* it failed. I need solutions, not post-mortems.",
                "Do you realise how this looks to the rest of the organisation?",
            ],
            "medium": [
                "I hear you, but the timeline is non-negotiable. What specifically needs to change?",
                "Fine. But if we slip another sprint, we'll have a much bigger conversation.",
                "What resources do you need? Because I can't keep defending this to leadership.",
            ],
            "high": [
                "Actually, that makes sense. I appreciate you being direct with me.",
                "Alright — send me that proposal and we'll revisit the timeline together.",
                "That's a mature way to frame it. Let's make this work.",
            ],
        },
        "pitch": {
            "low": [
                "Your pricing model doesn't add up. Why would we pay this when alternatives cost less?",
                "I've seen a dozen pitches like this. What makes yours any different?",
                "Our current vendor is fine. Convince me this is worth the switching cost.",
            ],
            "medium": [
                "Interesting. But what's your go-to-market timeline if we sign today?",
                "The ROI numbers look promising — who else in our industry uses this?",
                "Walk me through the implementation risk. Our last migration was a disaster.",
            ],
            "high": [
                "This solves a real pain point for us. Can we pilot it next quarter?",
                "I'm sold on the concept — what does the onboarding look like?",
                "Let's get legal involved. I'd like to move fast on this.",
            ],
        },
    }

    def __init__(self, scenario_type: str = "interview") -> None:
        self.scenario_type = scenario_type if scenario_type in self._ROLE_LABELS else "interview"
        self._rng = random.Random()

    @property
    def role_label(self) -> str:
        return self._ROLE_LABELS[self.scenario_type]

    def respond(
        self,
        user_action: str,
        success_probability: float,
        state: Optional[SimulationState] = None,
    ) -> str:
        """
        Generate a dynamic response to the student's action.

        Parameters
        ----------
        user_action:         The student's latest input.
        success_probability: P(success) computed by the probability engine (0-1).
        state:               Current simulation state (used for context-awareness).

        Returns
        -------
        A string response from the Antagonist character.
        """
        pressure_level = self._pressure_from_probability(success_probability)
        templates = self._RESPONSE_TEMPLATES[self.scenario_type][pressure_level]
        base_response = self._rng.choice(templates)

        # Inject a reference to the student's action to make the reply feel reactive
        action_snippet = user_action[:60].rstrip(".!?,") if user_action else "your response"
        contextual_prefix = f'You said: "{action_snippet}…" — '

        return contextual_prefix + base_response

    @staticmethod
    def _pressure_from_probability(prob: float) -> str:
        if prob < 0.4:
            return "low"
        if prob <= 0.65:
            return "medium"
        return "high"
