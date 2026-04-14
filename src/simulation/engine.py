"""
Simulation Engine

Orchestrates the full Digital Twin simulation:
  1. Ingests the UserProfile (Digital Twin data).
  2. Deploys the Simulation Council (Antagonist, Environmentalist, Observer).
  3. Processes each student turn through the probability engine.
  4. Applies environmental events.
  5. Updates the SimulationState.
  6. Finalises the session with three outcome branches.
"""

from __future__ import annotations

from typing import Optional

from ..models.user_profile import UserProfile
from ..models.simulation_state import SimulationState, Turn
from ..agents.antagonist import Antagonist
from ..agents.environmentalist import Environmentalist
from ..agents.observer import Observer
from .probability import ProbabilityEngine
from .branches import BranchingEngine


class SimulationEngine:
    """
    Central coordinator for the Digital Twin simulation session.

    Parameters
    ----------
    profile:          The student's UserProfile.
    scenario_title:   Short label for the scenario.
    scenario_description: Full scenario context.
    scenario_type:    "interview" | "conflict" | "pitch".
    event_frequency:  Probability that the Environmentalist fires on any turn.
    env_seed:         Optional seed for reproducible environmental events.
    """

    def __init__(
        self,
        profile: UserProfile,
        scenario_title: str,
        scenario_description: str,
        scenario_type: str = "interview",
        event_frequency: float = 0.35,
        env_seed: Optional[int] = None,
    ) -> None:
        profile.validate()
        self.profile = profile
        self.scenario_type = scenario_type

        # Simulation state
        self.state = SimulationState(
            scenario_title=scenario_title,
            scenario_description=scenario_description,
        )

        # Simulation Council
        self.antagonist = Antagonist(scenario_type=scenario_type)
        self.environmentalist = Environmentalist(
            scenario_type=scenario_type,
            event_frequency=event_frequency,
            seed=env_seed,
        )
        self.observer = Observer(profile=profile)

        # Engines
        self.probability_engine = ProbabilityEngine(scenario_type=scenario_type)
        self.branching_engine = BranchingEngine(scenario_type=scenario_type)

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def process_turn(self, user_action: str) -> Turn:
        """
        Process a single student action and advance the simulation.

        Workflow per turn
        -----------------
        1. Calculate P(success | action, context).
        2. Ask the Antagonist for a dynamic response.
        3. Check whether the Environmentalist fires an event.
        4. Ask the Observer to annotate the turn.
        5. Update the cumulative performance score.
        6. Record and return the completed Turn.

        Parameters
        ----------
        user_action : The student's input text.

        Returns
        -------
        The completed Turn object.
        """
        if self.state.is_complete:
            raise RuntimeError("Simulation is already complete. Call reset() to start a new session.")

        turn_number = self.state.current_turn_number()

        # 1. Probability
        prob = self.probability_engine.calculate(user_action, self.profile, self.state)

        # 2. Antagonist response
        antagonist_reply = self.antagonist.respond(user_action, prob, self.state)

        # 3. Environmental event
        env_event = self.environmentalist.maybe_inject_event(turn_number)

        # 4. Cumulative score update
        cumulative_score = self._update_cumulative_score(prob, env_event)

        # 5. Build the Turn
        turn = Turn(
            turn_number=turn_number,
            user_action=user_action,
            antagonist_reply=antagonist_reply,
            environmental_event=env_event,
            success_probability=prob,
            cumulative_score=cumulative_score,
        )

        # 6. Observer annotation
        turn.observer_notes = self.observer.analyse_turn(turn)

        # Record
        self.state.turns.append(turn)
        return turn

    def finalise(self) -> SimulationState:
        """
        End the simulation, generate outcome branches, and mark state complete.

        Returns the finalised SimulationState.
        """
        if self.state.is_complete:
            return self.state

        self.state.outcome_paths = self.branching_engine.generate(self.state, self.profile)
        self.state.is_complete = True
        return self.state

    def reset(
        self,
        scenario_title: Optional[str] = None,
        scenario_description: Optional[str] = None,
    ) -> None:
        """Reset the simulation for a new session (same profile and agents)."""
        self.state = SimulationState(
            scenario_title=scenario_title or self.state.scenario_title,
            scenario_description=scenario_description or self.state.scenario_description,
        )
        self.observer.reset()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_cumulative_score(self, prob: float, env_event: Optional[str]) -> float:
        """
        Derive a running 0-100 performance score.

        Formula:
          new_score = prev_score * 0.7 + prob * 100 * 0.3
          apply a small penalty (-3) when an environmental event disrupts the turn.
        """
        prev = self.state.final_cumulative_score() if self.state.turns else 50.0
        new_score = prev * 0.7 + (prob * 100.0) * 0.3
        if env_event:
            new_score -= 3.0
        return max(0.0, min(100.0, round(new_score, 2)))
