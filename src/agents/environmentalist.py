"""
Environmentalist Agent

Manages external variables and injects realistic random events during a
simulation to mimic real-world unpredictability.

Examples of injected events:
* A sudden market-shift announcement during a sales pitch.
* A technical glitch that interrupts an interview.
* An urgent message from a senior stakeholder mid-conflict.
"""

from __future__ import annotations

import random
from typing import List, Optional


class Environmentalist:
    """
    Injects contextual disruptions at configurable intervals.

    Parameters
    ----------
    scenario_type:    "interview" | "conflict" | "pitch"
    event_frequency:  Probability (0-1) that an event fires on any given turn.
    seed:             Optional RNG seed for reproducible simulations.
    """

    _EVENTS: dict[str, List[str]] = {
        "interview": [
            "The interviewer receives an urgent Slack message and glances at their phone.",
            "A colleague enters the room and whispers something to the interviewer — they nod and refocus on you.",
            "The video call drops for three seconds; you reconnect.",
            "The interviewer mentions the role's budget has just been revised — it may affect the team size.",
            "You notice the interviewer's expression shift after reviewing your resume.",
        ],
        "conflict": [
            "An executive walks past the glass-walled meeting room, clearly watching the discussion.",
            "The manager receives a critical email mid-conversation and visibly tenses.",
            "The quarterly results have just been released — they are worse than projected.",
            "A team member messages the group chat with an unexpected blocker.",
            "The meeting room is double-booked; you have five additional minutes before the next group arrives.",
        ],
        "pitch": [
            "The client's CFO unexpectedly joins the call.",
            "A competitor has just announced a major product update — the client brings it up.",
            "The client's internet connection degrades; you lose audio for 15 seconds.",
            "The client mentions they are also evaluating two other vendors this week.",
            "Breaking news in the client's industry flashes on the screen behind them.",
        ],
    }

    def __init__(
        self,
        scenario_type: str = "interview",
        event_frequency: float = 0.35,
        seed: Optional[int] = None,
    ) -> None:
        self.scenario_type = scenario_type if scenario_type in self._EVENTS else "interview"
        self.event_frequency = max(0.0, min(1.0, event_frequency))
        self._rng = random.Random(seed)
        self._used_events: set[str] = set()

    def maybe_inject_event(self, turn_number: int) -> Optional[str]:
        """
        Decide whether to fire an environmental event this turn.

        Returns the event description string, or ``None`` if no event fires.
        The first turn never fires an event to give the simulation a clean start.
        """
        if turn_number <= 1:
            return None

        if self._rng.random() > self.event_frequency:
            return None

        available = [e for e in self._EVENTS[self.scenario_type] if e not in self._used_events]
        if not available:
            # All events exhausted — reset the pool
            self._used_events.clear()
            available = self._EVENTS[self.scenario_type]

        event = self._rng.choice(available)
        self._used_events.add(event)
        return event

    def force_event(self) -> str:
        """Return a random event regardless of frequency (for testing/demo)."""
        return self._rng.choice(self._EVENTS[self.scenario_type])
