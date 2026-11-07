# DIANA — Autonomous AI Agent (Black-Box Case Study)

<p align="center">
  <img alt="status" src="https://img.shields.io/badge/status-active-brightgreen">
  <img alt="python" src="https://img.shields.io/badge/backend-Python%20%2B%20FastAPI-3776AB?logo=python&logoColor=white">
  <img alt="frontend" src="https://img.shields.io/badge/frontend-Electron%20%2B%20WebGL-47848F?logo=electron&logoColor=white">
  <img alt="llm" src="https://img.shields.io/badge/AI-function%20calling-8A2BE2">
  <img alt="license" src="https://img.shields.io/badge/docs%20license-MIT-blue">
  <img alt="code" src="https://img.shields.io/badge/core%20code-proprietary-lightgrey">
</p>

<!-- ================= DEMO MEDIA SLOT =================
     Drop the assets into docs/media/ and the links below start working.
     Option A (GIF in repo):    ![DIANA demo](docs/media/diana-demo.gif)
     Option B (YouTube video):  [![Watch the demo](docs/media/demo-thumb.png)](https://youtu.be/YOUR_ID)
     Option C (MP4 in repo):    [Download demo (MP4)](docs/media/diana-demo.mp4)
     ==================================================== -->

<p align="center">
  <img src="https://img.shields.io/badge/▶%20demo-coming%20soon-orange?style=for-the-badge" alt="Demo coming soon">
</p>

<p align="center">
  <i>Screen recording in progress — the slot below is wired and ready.</i>
</p>

<p align="center">
  <a href="docs/engineering.md">Engineering Notes</a>
  &nbsp;·&nbsp;
  <a href="docs/diagrams/architecture.md">Architecture</a>
  &nbsp;·&nbsp;
  <a href="docs/protection.md">Security</a>
  &nbsp;·&nbsp;
  <a href="docs/voice.md">Voice</a>
  &nbsp;·&nbsp;
  <a href="docs/autonomy.md">Autonomy</a>
  &nbsp;·&nbsp;
  <a href="docs/roadmap.md">Roadmap</a>
</p>

> 🎬 **Media slot ready (assets pending):** drop `diana-demo.gif` (and optionally `diana-demo.mp4` / `demo-thumb.png`) into `docs/media/` — the links above start working immediately. Until then, see [docs/media/README.md](docs/media/README.md) for the recording guide (what to show, in what order, ideal length).

> **Note:** This repository is a **technical showcase (black-box)**. It documents the architecture, engineering concepts, and challenges overcome while building DIANA. **The core functional code is not here** — it is proprietary. What you will find are diagrams, architecture specifications, and generic snippets that illustrate engineering patterns without exposing business logic.

---

## What is DIANA

DIANA is a **personal AI assistant that lives on your desktop, controls the operating system for real, and rewrites its own source code safely**. She is not a chatbot: she executes actions on the user's PC (open/close applications, edit files, run scripts, control IoT devices, measure hardware), speaks to the user through voice (STT + TTS), and is rendered on screen as a **reactive energy orb** that changes state, color and motion according to her emotional state and activity.

The engineering differentiator rests on five pillars:

1. **LLM orchestration with real function calling** — the model does not "describe what it would do"; it emits structured tool calls that are executed on the system, with verified results returned to the model.
2. **Safe self-modification of code** — the AI can rewrite its own source code, but every edit passes through a validation pipeline that automatically reverts anything that breaks syntax, introduces undefined names, or fails a real runtime test.
3. **Agent honesty (grounding)** — the agent never fabricates measurements or tool results. If a skill does not exist, it admits so and proposes installing it; if a tool fails, it reports the exact error.
4. **Initiative and autonomy** — a multi-brain bus (sensors → limbic state → planner → executor) lets her notice context on the machine, propose actions and run long multi-step plans without being asked again.
5. **Local-first security layer** — a five-layer protection system watches the machine (processes, files, startup entries, filters, optional LLM analyst) with a false-positive filter and a risk engine.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER (voice / chat / text)              │
└───────────────────────────┬─────────────────────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │     ELECTRON (Desktop Frontend)   │
          │  ─────────────────────────────    │
          │  • Chat window                    │
          │  • Reactive energy orb (state/emotion driven)
          │  • TTS playback + audio capture   │
          └─────────────────┬─────────────────┘
                            │  HTTP / WebSocket
          ┌─────────────────▼─────────────────┐
          │      FASTAPI (Python Backend)     │
          │  ─────────────────────────────    │
          │  • REST API + WS broadcast        │
          │  • LLM orchestrator               │
          │  • Tool dispatcher (41+ tools)    │
          │  • Skill registry (runtime)       │
          │  • Self-modification pipeline     │
          │  • Autonomy bus + planner         │
          │  • Protection / security layers   │
          └──────┬──────────────┬─────────────┘
                 │              │
     ┌───────────▼───┐   ┌──────▼────────────┐
     │  LLM Provider │   │  Windows System   │
     │  (DeepSeek /  │   │  ───────────────  │
     │   Groq / etc) │   │  • Processes      │
     └───────────────┘   │  • Files          │
                         │  • Hardware       │
                         │  • IoT (Tuya)     │
                         │  • Voice (TTS)    │
                         └───────────────────┘
```

Detailed diagram in [`docs/diagrams/architecture.md`](docs/diagrams/architecture.md).

### Documentation

| Document | What it covers |
|---|---|
| [Engineering Notes](docs/engineering.md) | Failure taxonomy, self-modification guard chain, grounding strategy, design trade-offs |
| [Architecture Diagrams](docs/diagrams/architecture.md) | Request flow, edit pipeline, file safety, skill lifecycle, autonomy loop, protection cycle |
| [Autonomy](docs/autonomy.md) | Sensors, limbic state, work vs. idle mode, planner and task queue |
| [Protection Layers](docs/protection.md) | Five-layer local security system and alert flow |
| [Voice Pipeline](docs/voice.md) | Audio preprocessing, STT fallback, correction layer, TTS |
| [Roadmap](docs/roadmap.md) | Done, next, and explicit non-goals |

---

## Engineering Pillars

### 1. Tool Calling with Result Verification

The orchestrator sends the LLM a catalogue of tools (41+) with JSON schemas. The model chooses which to call. Every call returns a structured object (`ok`, `result`, `error`, `explained`). The agent **may only claim success if `ok == true`** — a rule enforced by the system prompt and validated in the backend.

Illustrative snippet: [`snippets/tool_dispatch.py`](snippets/tool_dispatch.py)

### 2. Safe Self-Modification Pipeline

The AI can edit its own source code. To do so, every write goes through:

1. **Syntax validation** (AST parse) before writing
2. **Undefined-name check** (pyflakes) — catches removed functions with orphaned call sites
3. **Real post-write test** — imports the module; on failure the edit is **automatically rolled back**
4. **Automatic backup** before any write

Illustrative snippet: [`snippets/safe_edit_pipeline.py`](snippets/safe_edit_pipeline.py)

### 3. Grounding / Anti-Hallucination

System rules prevent the agent from inventing measurable data. If the user asks "what is my CPU temperature?" and no measurement skill is installed, the mandatory answer is to admit it and offer to install one — never to estimate a number.

### 4. Reactive Orb with Emotional State

The backend emits an `emotion` field in the response (happy, excited, surprised, thinking, sad, angry, neutral) plus an activity state. The desktop frontend renders a **procedural energy orb** (WebGL shader) that reacts to that state: color, pulse frequency, glow and turbulence change with the emotion, and it shifts to an "active" mode while tools are executing. Voice output is synchronized with the orb's pulse, so the assistant feels physically present without needing a rigged 3D character.

### 5. Bidirectional Voice

- **STT**: audio capture → preprocessing (AGC/noise) → transcription with provider fallback → phonetic correction layer
- **TTS**: text → speech, with markdown stripping before synthesis (asterisks were being spoken aloud as "asterisk")
- Multi-language support (responds in English when the user speaks English)

### 6. Dynamic Skill Registry

Skills are Python modules discoverable at runtime. The agent can **create new skills** on request, register them, and execute them immediately. This allows the system to evolve without a deploy.

### 7. Autonomy Bus and Planner

A lightweight limbic-inspired layer combines PC sensors (active window, CPU, RAM, disk, battery, time of day) into a state, and a planner decomposes large goals into verified steps. The agent can work through a multi-step plan, checking each step's real result, and reporting honestly what was done, what failed and what is pending.

### 8. Local IoT Integration

Discovery and control of Tuya/Smart Life devices **without the cloud** (local UDP/TCP protocol), with multi-device scenes (e.g. "cinema mode" = dim lights + turn on TV).

### 9. Security and Protection Layers

A five-layer local protection system: process monitor, file scanner, startup auditing, false-positive filter and an optional LLM analyst. It runs inside the backend lifespan, logs alerts, and exposes explicit control actions (status, scan, alerts, start/stop).

---

## Engineering Challenges Overcome

| Challenge | Solution |
|---|---|
| AI rewriting its own code and breaking the backend | Triple-validation pipeline with automatic rollback |
| Hallucination of hardware metrics | Grounding rules + mandatory real skill for measurement |
| Voice output that "feels" like a present character | Reactive orb driven by emotion + activity + audio pulse |
| Real-time emotional feedback | Emotion field → orb state machine (color, pulse, turbulence) |
| Self-diagnosis of tool failures | Structured error objects with `cause`/`action`/`can_autofix` |
| Long conversation context | Summarization system focused on current task vs. history |
| Safety of destructive actions | Mandatory confirmation + file quarantine + app whitelist |
| Running long multi-step work without losing the thread | Task queue with per-step verification and progress file |

---

## Project Structure (partial, no proprietary code)

```
ai-assistant-3d/
├── backend/
│   ├── app/
│   │   ├── api/              # REST routes + WebSocket
│   │   ├── core/             # LLM orchestrator, dispatcher
│   │   ├── tools/            # Catalogue of 41+ tools
│   │   ├── skills/           # Dynamic skill registry
│   │   │   ├── builtin/      # Native skills
│   │   │   └── generated/    # Skills created at runtime
│   │   ├── services/         # STT, TTS, vision, IoT, autonomy
│   │   ├── protection/       # 5-layer security system
│   │   ├── rules/            # Safety and behaviour rules engine
│   │   └── memory/           # Persistent memory + diary
│   └── data/                 # Persistence (runtime, not versioned)
├── frontend/                 # Chat UI + orb renderer
├── electron/                 # Desktop shell
└── rules/                    # Behaviour rules (Markdown)
```

---

## Known Limitations (Technical Honesty)

- The agent has **no** native screen vision — it relies on measurement tools to judge visual results.
- Tool-calling quality depends on the configured LLM provider.
- The orb renderer requires WebGL support.
- IoT control is local (same network); there is no cloud bridge.
- Self-modification is scoped to project files and always validated — this is not "an AGI rewriting itself".

---

## Stack

**Backend:** Python, FastAPI, WebSockets, asyncio, pyflakes, AST
**Frontend:** Electron, JavaScript/TypeScript, WebGL (orb), Web Audio API
**AI:** LLM via API (DeepSeek/Groq), function calling, STT/TTS
**Infra:** Windows, git, robocopy (backup), PowerShell (automation)

---


## Demo — what the recording should show

A 60–90 second screen capture is enough to prove every claim in this document. Recommended order:

| # | Shot | What it proves |
|---|------|----------------|
| 1 | Voice question → orb reacts → spoken answer | STT + TTS + orb state driver |
| 2 | "Open Chrome and search for X" → real action | Function calling executed on the OS |
| 3 | Missing skill → agent admits + proposes install | Grounding / no hallucination |
| 4 | Self-edit request → validation pipeline → auto-revert of a broken edit | Safe self-modification |
| 5 | Protection scan → alert raised → false-positive filter | Five-layer local security |

See [docs/media/README.md](docs/media/README.md) for the full recording checklist.

---

## Author

**Winston Pereira** — AI Product Architect

Building Diana as a working proof that a single developer can ship an agent with real tool use, real verification, and real local security.

- LinkedIn: [winston-pereira-0748243bb](https://www.linkedin.com/in/winston-pereira-0748243bb/)
- GitHub: [@WinstonPereira](https://github.com/WinstonPereira)

Open to conversations about AI agent architecture, tool-use safety, and applied LLM engineering.
