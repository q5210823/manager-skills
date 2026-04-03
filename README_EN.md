<div align="center">

# manager.skills

> Not a passive to-do helper. A manager that treats you like a rising star.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

Build an “artist profile” first, then generate phase sprints, hourly call sheets,
PUA modes, daily reports, and check-in areas.  
Supports OpenClaw / Claude Code skill workflows and also ships with a Chrome extension prototype for testing.

[Install](#install) · [Usage](#usage) · [Demo](#demo) · [Features](#features) · [Project Structure](#project-structure) · [中文](README.md)

</div>

---

## Product Positioning

Most people do not lack goals. They lack someone consistently managing their momentum.

`manager.skills` is not a normal to-do tool and not a generic assistant. It is designed to:

1. build an artist-style profile
2. break growth into 7 / 30 / 90 day phase sprints
3. generate hourly daily call sheets
4. switch between different pressure modes
5. maintain rhythm through reports, check-ins, reviews, and accountability

In one sentence:

**It does not help you remember tasks. It helps you rise.**

---

## Current Capabilities

The current version already supports:

1. `Artist Profile Intake`
   long-term goal, existing skills, unlock skills, resource network, personality tags, phase duration, energy budget, time blocks
2. `Phase Sprints`
   supports `7 days / 30 days / 90 days`
3. `Call Sheet Preview`
   generates a manager-style structured schedule preview
4. `PUA Engine`
   supports `Strict / Sarcastic / Hype`
5. `Daily Report / Check-in Sections`
   visible directly inside the extension preview
6. `OpenClaw Feishu Sync Tool`
   handled via local tooling instead of the Chrome extension

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

### 1. Skill Entry

Invoke:

```text
/create-manager
```

The updated flow builds an artist profile first, then moves into phase planning and call-sheet generation.

### 2. Chrome Extension Testing

The repository root already includes a `manifest.json`, so you can load the entire repo directly in Chrome:

1. open `chrome://extensions/`
2. enable Developer Mode
3. click “Load unpacked”
4. choose the repo root directory

Clicking the extension icon opens a new tab for testing.

### 3. OpenClaw Feishu Sync

Feishu sync is implemented in local tooling, not inside the Chrome extension:

```bash
python3 tools/feishu_calendar_sync.py --setup
python3 tools/feishu_calendar_sync.py --list-calendars
python3 tools/feishu_calendar_sync.py --input managers/sample_manager_input.json --manager-name "Ace Manager"
```

---

## Demo

> Input:
>
> `Build a clearly positioned personal brand within 90 days, publish consistently, and land the first batch of paid collaborations`
>
> `Existing skills: writing, Xiaohongshu creator, basic editing`
>
> `Unlock skills: live presence, sales, community operations`

**Scenario 1: Daily Call Sheet**

```text
manager.skills ❯ No grandstanding today. Only 3 time blocks:

                20:00-22:00  Core output - Writing
                22:00-23:00  Upgrade training - Live presence
                23:00-23:30  Daily review and check-in

                No visible output means no real progress.
```

**Scenario 2: Delay Correction**

```text
User            ❯ I spent the whole day reading materials, so it wasn't completely wasted

manager.skills ❯ That was preparation, not progress.
                If it did not become a publishable asset, a shipped result, or a commercial move,
                it was just a more respectable-looking delay.
```

**Scenario 3: Daily Report**

```text
manager.skills ❯ The biggest mistake today was not that you failed to finish.
                It was putting the most valuable action at the very end.
                Produce first, organize later. Get the order wrong and the rhythm collapses.
```

---

## Features

### Generated Skill Structure

Each manager Skill has two parts:

| Part | Content |
|------|---------|
| **Part A — Artist Management System** | artist profile, phase sprints, hourly call sheets, daily reports, check-ins, accountability and rewards |
| **Part B — Persona / PUA Engine** | role framing, speaking style, strict / sarcastic / hype modes, review voice |

Execution flow:

`Receive goal or problem -> management system decides what matters most -> persona chooses tone and pressure -> manager-style response`

### Chrome Extension Interaction

The current extension prototype already supports:

1. searchable tags
2. multi-select tags with custom additions
3. separate workday / weekend time blocks
4. open-on-click in a new tab
5. call-sheet style preview
6. daily report and check-in sections

### PUA Engine

Supports three modes:

1. `Strict`
   cold, direct, wake-you-up mode
2. `Sarcastic`
   sharp, ironic, clears delusion
3. `Hype`
   motivational, dramatic, keeps momentum alive

### Feishu Sync

Feishu sync is implemented in OpenClaw / local tools, not the Chrome extension:

1. configure calendar credentials
2. list existing calendars
3. generate time blocks from the artist profile and sync them to Feishu calendar
4. provide clearer failure diagnostics when sync breaks

---

## Project Structure

This repository root is itself an installable skill directory:

```text
manager-skills/
├── manifest.json
├── SKILL.md
├── README.md
├── README_EN.md
├── INSTALL.md
├── prompts/
├── tools/
│   ├── create_manager.py
│   ├── manager_web.py
│   ├── feishu_calendar_sync.py
│   ├── skill_writer.py
│   └── version_manager.py
├── chrome_extension/
│   ├── background.js
│   ├── popup.html
│   ├── popup.css
│   └── popup.js
├── managers/
│   ├── example_artist_manager/
│   └── sample_manager_input.json
├── docs/
├── web/
└── LICENSE
```
