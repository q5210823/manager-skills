<div align="center">

# manager.skills

> Not a passive to-do helper. A manager that treats you like a rising star.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

Provide your long-term goal, current identity, current resources, active projects, and daily time budget,<br>
and generate an AI manager Skill that plans, pushes, reviews, and applies pressure when needed.

[Install](#install) · [Usage](#usage) · [Features](#features) · [Project Structure](#project-structure) · [Publishing](#publishing) · [中文](README.md)

</div>

---

## Product Positioning

Most people do not lack goals. They lack someone consistently managing their momentum.

`manager.skills` is not a normal to-do tool and not a generic assistant. It is built to:

1. decide what deserves attention
2. break long-term goals into weekly and daily actions
3. call out delay directly
4. enforce a review loop and course-correct constantly

In one sentence:

**It does not help you remember tasks. It helps you rise.**

---

## V1 Scope

V1 focuses on the smallest useful loop:

1. collect 5 fixed inputs
2. generate a manager persona
3. generate strategy, weekly priorities, and daily briefs
4. provide 3 pressure modes
5. generate daily review rules

V1 does not include:

1. calendar sync
2. Chrome extension UI
3. external platform auto-ingestion
4. multi-role collaboration

---

## Inputs

V1 only uses these 5 fields:

1. `long_term_goal`
2. `current_identity`
3. `current_resources`
4. `current_projects`
5. `daily_time_budget`

The more concrete the input is, the more usable the generated manager becomes.

---

## Install

### OpenClaw

```bash
git clone https://github.com/q5210823/manager-skills.git ~/.openclaw/workspace/skills/create-manager
```

### Claude Code

```bash
mkdir -p .claude/skills
git clone https://github.com/q5210823/manager-skills.git .claude/skills/create-manager
```

### Dependencies

```bash
pip3 install -r requirements.txt
```

---

## Usage

Invoke:

```text
/create-manager
```

Then provide:

1. long-term goal
2. current identity
3. current resources
4. current projects
5. daily time budget

Generated manager Skills are stored under:

```text
./managers/{slug}/
```

---

## Local Entry Points

### 1. CLI

Generate a minimal manager directly from JSON:

```bash
python3 tools/create_manager.py --input managers/sample_manager_input.json
```

### 2. Local Web Form

Run the local browser form:

```bash
python3 tools/manager_web.py
```

Then open [http://127.0.0.1:8765](http://127.0.0.1:8765).

---

## Outputs

Each generated manager Skill is expected to produce:

1. a manager profile
2. weekly priorities
3. daily task briefs
4. progress push messages
5. daily review prompts

High-pressure mode is allowed to be sharper, but still bounded:

1. it can call out delay and excuses
2. it can highlight opportunity cost
3. it does not use personal humiliation
4. it does not spiral into uncontrolled verbal attack

---

## Features

### Generated Skill Structure

Each manager Skill has two parts:

| Part | Content |
|------|---------|
| **Part A — Execution System** | Stage judgment, weekly priorities, daily task rules, review rules |
| **Part B — Persona** | Role framing, speaking style, pressure modes, behavior boundaries |

Execution flow:

`Receive goal or problem -> Execution System decides what matters most -> Persona chooses tone and pressure -> manager-style response`

### Pressure Modes

1. `Gentle`
   Best for building rhythm
2. `Professional`
   Best for normal planning and follow-up
3. `High Pressure`
   Best for repeated delay or high-stakes moments

### Evolution

1. append new information -> merge with `merger.md`
2. conversational correction -> write to the `Correction` layer
3. version management -> update and rollback support

---

## Who It Is For

Best suited for users who:

1. have a serious long-term goal
2. want to build a personal brand, body of work, or career momentum
3. struggle with consistency and need external pressure
4. want to be managed, not just reminded

---

## Project Structure

This repository root is itself an installable skill directory:

```text
manager-skills/
├── SKILL.md
├── README.md
├── README_EN.md
├── INSTALL.md
├── prompts/
├── tools/
├── managers/
├── docs/
├── web/
└── LICENSE
```

---

## Example Data and Privacy

The repo only keeps example data:

1. `managers/example_artist_manager/`
2. `managers/sample_manager_input.json`

Do not replace them with real personal data and commit directly.

Real generated manager directories should stay uncommitted.

---

## Publishing

Recommended repository names:

1. `manager-skills`
2. `manager.skills`

Recommended display names:

1. Chinese: `经纪人.skills`
2. English: `manager.skills`

The repository root is already ready to be installed directly by OpenClaw / AgentSkills style workflows.

---

## Notes

1. V1 validates the manager role and execution loop, not a full productivity platform
2. A few generic collectors from the original base still remain, but they are not the main V1 path
3. Better source inputs lead to much stronger generated managers
