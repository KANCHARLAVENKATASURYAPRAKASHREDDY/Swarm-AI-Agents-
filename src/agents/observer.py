"""
Observer Agent (Data Analyst)

Silently monitors every turn, comparing the student's tone, logic, and
decision-making against their historical Digital Twin data.

Produces structured annotations for the After-Action Report.
"""

from __future__ import annotations

from typing import List

from ..models.user_profile import UserProfile
from ..models.simulation_state import Turn


class Observer:
    """
    Passive monitor that generates analytical notes after each turn.

    The Observer never speaks to the student.  Its output feeds the AAR.
    """

    def __init__(self, profile: UserProfile) -> None:
        self._profile = profile
        self._all_notes: List[str] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyse_turn(self, turn: Turn) -> str:
        """
        Analyse a completed turn and return a diagnostic note.

        The note compares observed behaviour with the user's profile baselines.
        """
        notes: List[str] = []

        # Tone analysis proxy: word count as a crude signal for verbosity/confidence
        word_count = len(turn.user_action.split())
        if word_count < 10:
            notes.append(
                f"Turn {turn.turn_number}: Response was very brief ({word_count} words) — "
                "may signal under-confidence or lack of preparation."
            )
        elif word_count > 100:
            notes.append(
                f"Turn {turn.turn_number}: Response was lengthy ({word_count} words) — "
                "risk of losing the listener; conciseness is a known growth area."
            )
        else:
            notes.append(
                f"Turn {turn.turn_number}: Response length ({word_count} words) is within "
                "an effective communication range."
            )

        # Logic signal: presence of reasoning keywords
        reasoning_keywords = {"because", "therefore", "however", "although", "specifically", "for example"}
        found = reasoning_keywords & set(turn.user_action.lower().split())
        if found:
            notes.append(
                f"Turn {turn.turn_number}: Detected structured reasoning markers {sorted(found)} — "
                "aligns with strong problem-solving profile."
            )
        else:
            notes.append(
                f"Turn {turn.turn_number}: No reasoning connectors detected — "
                "consider using 'because', 'therefore', or 'specifically' to sharpen logic."
            )

        # Performance trajectory
        if turn.success_probability >= 0.65:
            notes.append(
                f"Turn {turn.turn_number}: P(success)={turn.success_probability:.2f} — "
                "above threshold; consistent with top-quartile performance."
            )
        elif turn.success_probability >= 0.40:
            notes.append(
                f"Turn {turn.turn_number}: P(success)={turn.success_probability:.2f} — "
                "at median; room to leverage strengths more assertively."
            )
        else:
            notes.append(
                f"Turn {turn.turn_number}: P(success)={turn.success_probability:.2f} — "
                "below threshold; weaknesses surfacing in this exchange."
            )

        # Environmental event impact
        if turn.environmental_event:
            notes.append(
                f"Turn {turn.turn_number}: External disruption occurred — "
                f"'{turn.environmental_event[:80]}' "
                "Adaptability response will be factored into AAR."
            )

        combined = "  |  ".join(notes)
        self._all_notes.append(combined)
        return combined

    def get_all_notes(self) -> List[str]:
        """Return all observer notes accumulated so far."""
        return list(self._all_notes)

    def reset(self) -> None:
        """Clear accumulated notes (useful between simulation runs)."""
        self._all_notes.clear()
