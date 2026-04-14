"""
User profile data model for the Digital Twin simulation.

Encapsulates a student's academic history, personality traits, soft skills,
and past experiences so every simulation is personalised to that individual.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class PersonalityTraits:
    """Big-Five inspired personality snapshot (scores 0-10)."""

    openness: float = 5.0
    conscientiousness: float = 5.0
    extraversion: float = 5.0
    agreeableness: float = 5.0
    neuroticism: float = 5.0

    def validate(self) -> None:
        for attr in ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"):
            value = getattr(self, attr)
            if not (0.0 <= value <= 10.0):
                raise ValueError(f"PersonalityTraits.{attr} must be between 0 and 10, got {value}")


@dataclass
class SoftSkills:
    """Self-assessed or evaluated soft-skill scores (0-10)."""

    communication: float = 5.0
    leadership: float = 5.0
    problem_solving: float = 5.0
    emotional_intelligence: float = 5.0
    adaptability: float = 5.0
    negotiation: float = 5.0

    def validate(self) -> None:
        for attr in (
            "communication",
            "leadership",
            "problem_solving",
            "emotional_intelligence",
            "adaptability",
            "negotiation",
        ):
            value = getattr(self, attr)
            if not (0.0 <= value <= 10.0):
                raise ValueError(f"SoftSkills.{attr} must be between 0 and 10, got {value}")

    def average(self) -> float:
        values = [
            self.communication,
            self.leadership,
            self.problem_solving,
            self.emotional_intelligence,
            self.adaptability,
            self.negotiation,
        ]
        return sum(values) / len(values)


@dataclass
class PastExperience:
    """A single entry in the student's experience history."""

    title: str
    description: str
    outcome: str = "neutral"  # "positive", "negative", "neutral"
    relevance_score: float = 5.0  # 0-10 relevance to current simulation

    def validate(self) -> None:
        if self.outcome not in ("positive", "negative", "neutral"):
            raise ValueError(f"PastExperience.outcome must be 'positive', 'negative', or 'neutral', got {self.outcome!r}")
        if not (0.0 <= self.relevance_score <= 10.0):
            raise ValueError(f"PastExperience.relevance_score must be between 0 and 10, got {self.relevance_score}")


@dataclass
class UserProfile:
    """
    Comprehensive profile used to construct a student's Digital Twin.

    Attributes
    ----------
    name:               Student's name.
    academic_gpa:       GPA on a 4.0 scale.
    academic_major:     Field of study.
    personality:        Big-Five personality scores.
    soft_skills:        Soft-skill scores.
    experiences:        List of past experiences.
    weaknesses:         Free-text list of known weaknesses.
    strengths:          Free-text list of known strengths.
    """

    name: str
    academic_gpa: float = 3.0
    academic_major: str = "General"
    personality: PersonalityTraits = field(default_factory=PersonalityTraits)
    soft_skills: SoftSkills = field(default_factory=SoftSkills)
    experiences: List[PastExperience] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("UserProfile.name must not be empty.")
        if not (0.0 <= self.academic_gpa <= 4.0):
            raise ValueError(f"UserProfile.academic_gpa must be between 0 and 4, got {self.academic_gpa}")
        self.personality.validate()
        self.soft_skills.validate()
        for exp in self.experiences:
            exp.validate()

    def potential_score(self) -> float:
        """
        Compute an overall 'maximum potential' score (0-100) that reflects what
        the student could achieve if they leveraged all their strengths perfectly.
        """
        gpa_component = (self.academic_gpa / 4.0) * 25.0
        skills_component = (self.soft_skills.average() / 10.0) * 50.0
        experience_bonus = min(len(self.experiences) * 2.5, 25.0)
        return gpa_component + skills_component + experience_bonus
