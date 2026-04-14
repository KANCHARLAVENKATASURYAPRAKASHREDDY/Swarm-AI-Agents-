# Swarm AI Agents — Digital Twin Simulation

A multi-agent AI system that creates a personalised **Digital Twin** of a student or professional and places it inside realistic, high-stakes scenarios (job interviews, workplace conflicts, business pitches). A swarm of three specialised AI agents runs the simulation turn-by-turn, giving real-time feedback and generating a detailed **After-Action Report (AAR)** at the end.

---

## Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Agent Architecture](#agent-architecture)
4. [Project Structure](#project-structure)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Digital Twin Profile](#digital-twin-profile)
8. [Scenarios](#scenarios)
9. [After-Action Report](#after-action-report)
10. [Running Tests](#running-tests)

---

## Overview

The **Digital Twin Simulation** uses a swarm of cooperating AI agents to model how a specific individual would perform under pressure. Each agent plays a distinct role:

| Agent | Role |
|---|---|
| **Antagonist** | Dynamic counterpart (interviewer, manager, client) that adapts its pressure level to the user's performance |
| **Observer** | Silent data analyst that records tone, reasoning quality, and probability metrics turn-by-turn |
| **Environmentalist** | Injects unpredictable real-world disruptions (phone calls, market news, technical glitches) to test adaptability |

After the simulation, an **AfterActionReport** synthesizes all agent data into an actionable performance review.

---

## How It Works

```
User provides an action (text input)
          │
          ▼
┌─────────────────────────────────────┐
│         SimulationEngine            │
│                                     │
│  1. Environmentalist → random event?│
│  2. ProbabilityEngine → P(success)  │
│  3. BranchEngine → scenario branch  │
│  4. Antagonist → dynamic reply      │
│  5. Observer → analytical note      │
└─────────────────────────────────────┘
          │
          ▼
    Turn result displayed
          │
  (repeat up to max turns)
          │
          ▼
  AfterActionReport generated
```

Each turn computes a **success probability** (0–1) derived from the user's profile, their action quality (word choice, reasoning markers), and any active environmental disruption. The Antagonist then responds with matching pressure: sceptical when probability is low, encouraging when it is high.

---

## Agent Architecture

### Antagonist (`src/agents/antagonist.py`)
- Plays a realistic counterpart whose tone adapts to `P(success)`.
- Three performance tiers map `P(success)` to response style:
  - `low` (< 0.4) — sceptical, challenging tone (user is underperforming).
  - `medium` (0.4–0.65) — neutral, probing tone.
  - `high` (> 0.65) — encouraging, positive tone (user is excelling).
- Scenario-specific personas: *Interviewer*, *Manager*, *Client*.

### Observer (`src/agents/observer.py`)
- Silently monitors every turn — the user never sees its output during the simulation.
- Analyzes response length, presence of reasoning connectors (`because`, `therefore`, `specifically`, …), and performance trajectory.
- Accumulates structured notes fed directly into the AAR.

### Environmentalist (`src/agents/environmentalist.py`)
- Injects contextual disruptions at a configurable frequency (default 35%).
- The frequency is controlled by the `event_frequency` parameter of `SimulationEngine` (a float between 0.0 and 1.0).
- Events are scenario-specific and non-repeating within a session.
- The first turn is always event-free to give the simulation a clean start.

---

## Project Structure

```
Swarm-AI-Agents-/
├── main.py                  # CLI entry point (interactive & demo modes)
├── requirements.txt         # Python dependencies
├── src/
│   ├── agents/
│   │   ├── antagonist.py    # Antagonist agent
│   │   ├── environmentalist.py  # Environmentalist agent
│   │   └── observer.py      # Observer agent
│   ├── analytics/
│   │   └── aar.py           # After-Action Report generator
│   ├── models/
│   │   ├── user_profile.py  # UserProfile, PersonalityTraits, SoftSkills, PastExperience
│   │   └── simulation_state.py  # SimulationState and Turn data models
│   └── simulation/
│       ├── engine.py        # SimulationEngine — orchestrates all agents per turn
│       ├── branches.py      # Scenario branching logic
│       └── probability.py   # P(success) computation engine
└── tests/                   # pytest test suite
```

---

## Installation

**Requirements:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/KANCHARLAVENKATASURYAPRAKASHREDDY/Swarm-AI-Agents-.git
cd Swarm-AI-Agents-

# (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Interactive mode

Run the simulation and type your own responses at each turn:

```bash
python main.py
```

You will be prompted for your name, then placed in the default scenario. Type `quit` at any prompt to end early and receive the After-Action Report.

### Demo mode

Run a fully automated demo with pre-scripted actions (useful for CI or quick previews):

```bash
python main.py --demo
```

The demo uses a pre-built profile (**Alex Chen**, CS graduate) and walks through a *Senior Software Engineer Interview at TechCorp* scenario.

### Example session output

```
══════════════════════════════════════════════════════════════════════
  DIGITAL TWIN SIMULATION — DEMO MODE
══════════════════════════════════════════════════════════════════════

  Profile : Alex Chen
  Scenario: Senior Software Engineer Interview at TechCorp

──────────────────────────────────────────────────────────────────────
  TURN 1
──────────────────────────────────────────────────────────────────────
  [P(success) = 0.71]  [Cumulative Score = 7.1]

  🎭 You said: "I believe my strength lies in building scalable…" —
     Excellent point — I hadn't considered that angle. Please continue.

  🔍 Observer: Turn 1: Response length (27 words) is within an
     effective communication range.  |  Turn 1: Detected structured
     reasoning markers ['because', 'specifically'] …
```

---

## Digital Twin Profile

A `UserProfile` captures the key dimensions of a person's background:

| Field | Description |
|---|---|
| `name` | Student / participant name |
| `academic_gpa` | GPA on a 4.0 scale |
| `academic_major` | Field of study |
| `personality` | Big-Five scores (openness, conscientiousness, extraversion, agreeableness, neuroticism) on a 0–10 scale |
| `soft_skills` | Communication, leadership, problem solving, emotional intelligence, adaptability, negotiation (0–10 each) |
| `experiences` | List of past experiences with title, description, outcome, and relevance score |
| `strengths` | Free-text list of known strengths |
| `weaknesses` | Free-text list of known weaknesses |

The profile drives both the **probability engine** (baseline P(success)) and the **AAR** (personalised recommendations).

---

## Scenarios

Three scenario types are supported out of the box:

| Type | Description | Antagonist persona |
|---|---|---|
| `interview` | Job interview with a sceptical panel | Interviewer |
| `conflict` | Workplace conflict with a demanding manager | Manager |
| `pitch` | Business pitch to a cautious client | Client |

Each scenario type has its own set of environmental events and Antagonist response templates.

---

## After-Action Report

At the end of every session the `AfterActionReport` generates a structured review covering:

- **Overall performance score** and grade.
- **Turn-by-turn breakdown** of success probability.
- **Strengths demonstrated** during the simulation.
- **Areas for improvement** mapped to the user's known weaknesses.
- **Observer annotations** — tone analysis, reasoning quality, adaptability notes.
- **Recommended next steps** personalised to the profile.

---

## Running Tests

```bash
pytest
```

Tests live in the `tests/` directory and cover the agents, probability engine, simulation state, and AAR generator.
