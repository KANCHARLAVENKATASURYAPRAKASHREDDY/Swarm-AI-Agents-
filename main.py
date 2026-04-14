"""
Digital Twin Simulation — CLI Entry Point

Runs a fully interactive multi-agent simulation session.

Usage
-----
    python main.py

The script walks the user through:
  1. Building their Digital Twin profile.
  2. Choosing a scenario.
  3. Playing through the simulation (type your actions at each turn).
  4. Receiving the After-Action Report.

Type 'quit' at any action prompt to end the session early and see results.
"""

from __future__ import annotations

import sys

from src.models.user_profile import (
    UserProfile,
    PersonalityTraits,
    SoftSkills,
    PastExperience,
)
from src.simulation.engine import SimulationEngine
from src.analytics.aar import AfterActionReport


# ---------------------------------------------------------------------------
# Pre-built demo profiles and scenarios (used when running non-interactively)
# ---------------------------------------------------------------------------

DEMO_PROFILE = UserProfile(
    name="Alex Chen",
    academic_gpa=3.6,
    academic_major="Computer Science",
    personality=PersonalityTraits(
        openness=8.0,
        conscientiousness=7.5,
        extraversion=6.0,
        agreeableness=7.0,
        neuroticism=4.5,
    ),
    soft_skills=SoftSkills(
        communication=7.0,
        leadership=6.5,
        problem_solving=8.5,
        emotional_intelligence=6.0,
        adaptability=7.5,
        negotiation=5.5,
    ),
    experiences=[
        PastExperience(
            title="Summer Internship — Backend Engineer",
            description="Designed a REST API that reduced response time by 40%.",
            outcome="positive",
            relevance_score=9.0,
        ),
        PastExperience(
            title="Team Lead — Capstone Project",
            description="Led a 5-person team; managed conflict over sprint goals.",
            outcome="positive",
            relevance_score=7.5,
        ),
    ],
    strengths=["technical problem-solving", "data-driven reasoning", "adaptability"],
    weaknesses=["negotiation under pressure", "managing emotional responses"],
)

DEMO_SCENARIO = {
    "title": "Senior Software Engineer Interview at TechCorp",
    "description": (
        "You are interviewing for a Senior Software Engineer role at TechCorp, "
        "a Series-C fintech startup. The panel consists of a Principal Engineer "
        "(your Antagonist) known for rigorous technical and behavioural probing. "
        "The role is competitive — three other candidates are in final rounds."
    ),
    "type": "interview",
}


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

SEPARATOR = "─" * 70


def _header(title: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def _print_turn(turn) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  TURN {turn.turn_number}")
    print(SEPARATOR)
    print(f"  [P(success) = {turn.success_probability:.2f}]  "
          f"[Cumulative Score = {turn.cumulative_score:.1f}]")
    if turn.environmental_event:
        print(f"\n  ⚡ ENVIRONMENTAL EVENT: {turn.environmental_event}")
    print(f"\n  🎭 {turn.antagonist_reply}")
    print(f"\n  🔍 Observer: {turn.observer_notes[:120]}…")


# ---------------------------------------------------------------------------
# Main simulation loop
# ---------------------------------------------------------------------------

def run_demo() -> None:
    """Run a fully automated demo with pre-scripted actions."""
    _header("DIGITAL TWIN SIMULATION — DEMO MODE")
    print(f"\n  Profile : {DEMO_PROFILE.name}")
    print(f"  Scenario: {DEMO_SCENARIO['title']}\n")
    print(f"  {DEMO_SCENARIO['description']}\n")

    engine = SimulationEngine(
        profile=DEMO_PROFILE,
        scenario_title=DEMO_SCENARIO["title"],
        scenario_description=DEMO_SCENARIO["description"],
        scenario_type=DEMO_SCENARIO["type"],
        event_frequency=0.4,
        env_seed=42,
    )

    demo_actions = [
        (
            "I believe my strength lies in building scalable backend systems. "
            "For example, during my internship I reduced API response time by 40% "
            "by redesigning the caching layer, because I specifically identified "
            "the bottleneck through profiling data."
        ),
        (
            "When faced with ambiguity I first gather data and define success metrics "
            "before proposing a solution. Therefore, I always start with a brief "
            "discovery phase to align stakeholders."
        ),
        (
            "I'm not entirely sure how I'd handle a full rewrite under a tight deadline "
            "maybe I would just kind of tackle the most critical modules first and hope "
            "for the best."
        ),
        (
            "Looking back, I'd approach that differently. I would prioritise ruthlessly "
            "using an impact-vs-effort matrix, communicate the trade-offs clearly to "
            "leadership, and establish daily check-ins to surface blockers early."
        ),
    ]

    for action in demo_actions:
        turn = engine.process_turn(action)
        _print_turn(turn)

    state = engine.finalise()

    aar_generator = AfterActionReport(
        state=state,
        profile=DEMO_PROFILE,
        observer=engine.observer,
    )
    report = aar_generator.generate()
    print(f"\n{report.to_text()}")


def run_interactive() -> None:
    """Run an interactive simulation driven by the user's keyboard input."""
    _header("DIGITAL TWIN SIMULATION — INTERACTIVE MODE")

    print("\n  Building your Digital Twin profile…")
    name = input("  Your name: ").strip() or "Student"

    engine = SimulationEngine(
        profile=DEMO_PROFILE.__class__(
            name=name,
            academic_gpa=DEMO_PROFILE.academic_gpa,
            academic_major=DEMO_PROFILE.academic_major,
            personality=DEMO_PROFILE.personality,
            soft_skills=DEMO_PROFILE.soft_skills,
            experiences=DEMO_PROFILE.experiences,
            strengths=DEMO_PROFILE.strengths,
            weaknesses=DEMO_PROFILE.weaknesses,
        ),
        scenario_title=DEMO_SCENARIO["title"],
        scenario_description=DEMO_SCENARIO["description"],
        scenario_type=DEMO_SCENARIO["type"],
        event_frequency=0.4,
    )

    print(f"\n  Scenario: {DEMO_SCENARIO['title']}")
    print(f"  {DEMO_SCENARIO['description']}")
    print("\n  Type your response at each turn. Enter 'quit' to end early.\n")

    max_turns = 6
    for _ in range(max_turns):
        action = input(f"\n  [Turn {engine.state.current_turn_number()}] Your action: ").strip()
        if not action or action.lower() == "quit":
            break
        turn = engine.process_turn(action)
        _print_turn(turn)

    state = engine.finalise()
    aar_generator = AfterActionReport(
        state=state,
        profile=engine.profile,
        observer=engine.observer,
    )
    report = aar_generator.generate()
    print(f"\n{report.to_text()}")


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if "--demo" in sys.argv or not sys.stdin.isatty():
        run_demo()
    else:
        run_interactive()
