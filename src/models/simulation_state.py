"""
Simulation state: tracks turns, decisions, running scores, and final outcome paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Turn:
    """
    Represents one exchange in the simulation.

    Attributes
    ----------
    turn_number:        Sequential index (1-based).
    user_action:        What the student said or did.
    antagonist_reply:   The counterpart's dynamic response.
    environmental_event: Any external disruption injected by the Environmentalist.
    observer_notes:     Silent notes logged by the Observer agent.
    success_probability: P(success | action, context) for this turn (0-1).
    cumulative_score:   Running performance score (0-100).
    """

    turn_number: int
    user_action: str
    antagonist_reply: str = ""
    environmental_event: Optional[str] = None
    observer_notes: str = ""
    success_probability: float = 0.5
    cumulative_score: float = 50.0


@dataclass
class OutcomePath:
    """
    One of three diverging endings generated at the close of a simulation.

    path_type: "optimal" | "realistic" | "safety_net"
    """

    path_type: str  # "optimal", "realistic", "safety_net"
    title: str
    description: str
    final_score: float  # 0-100


@dataclass
class SimulationState:
    """
    Mutable container that holds the full state of a running simulation session.

    Attributes
    ----------
    scenario_title:    Short label for the scenario (e.g., "Job Interview at Tech Corp").
    scenario_description: Full context paragraph.
    turns:             Ordered list of every exchange so far.
    outcome_paths:     Populated once the simulation ends (three paths).
    is_complete:       True once the session has been finalised.
    """

    scenario_title: str
    scenario_description: str
    turns: List[Turn] = field(default_factory=list)
    outcome_paths: List[OutcomePath] = field(default_factory=list)
    is_complete: bool = False

    def current_turn_number(self) -> int:
        return len(self.turns) + 1

    def latest_turn(self) -> Optional[Turn]:
        return self.turns[-1] if self.turns else None

    def average_success_probability(self) -> float:
        if not self.turns:
            return 0.5
        return sum(t.success_probability for t in self.turns) / len(self.turns)

    def final_cumulative_score(self) -> float:
        if not self.turns:
            return 50.0
        return self.turns[-1].cumulative_score
