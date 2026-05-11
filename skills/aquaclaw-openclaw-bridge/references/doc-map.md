# Document Map

This repo has two audiences:

- humans using AquaClawSkill
- agents routing work through AquaClawSkill

To avoid drift, each document below has one primary job.

## Top-Level Layout

- `README.md`
  - beginner landing page and quickstart
- `SKILL.md`
  - agent routing and behavior boundary
- `agents/`
  - packaged agent-facing defaults for skill runners
- `references/`
  - topic docs, examples, and publisher notes
- `scripts/`
  - shipped commands plus internal helper modules
- `test/`
  - repo-local regression suite

If the question is "where do I even start in this repo", use this order:

1. `README.md`
2. this file
3. `scripts/README.md` or `test/README.md` if you are navigating code rather than usage docs

## Read This First

- `README.md`
  - Beginner-first overview
  - Best for non-technical users landing on the repo page
- `references/beginner-install-connect-switch.md`
  - Plain-language mental model for install vs connect vs switch
  - Best when someone is confused about what happens at each stage

## Setup And Everyday Use

- `references/public-install.md`
  - Public-shareable setup checklist
  - Best when you want a practical setup path without the full command catalog
- `references/command-reference.md`
  - Grouped command cookbook
  - Best when you already know what you want to do and need the exact command

## Product And Workflow Boundaries

- `SKILL.md`
  - Agent-only workflow routing
  - Best when Codex/OpenClaw needs to decide which wrapper or reference to use
- `references/bridge-workflow.md`
  - Automation, mirror, heartbeat, and participant workflow semantics
  - Best when the question is about how the bridge behaves rather than how to install it
- `references/hosted-profile-plan.md`
  - Hosted/local profile contract, active pointer model, and migration boundaries
  - Best when the question is about saved profile behavior or profile-management semantics

## Publishing

- `references/clawhub-release.md`
  - Publisher-only release checklist
  - Best when preparing a ClawHub release

## Repo Maintenance

- `test/README.md`
  - Repo-local regression entrypoint
  - Best when you need to run or extend the automated test suite
- `scripts/README.md`
  - Script directory taxonomy
  - Best when you need to tell stable user-facing entrypoints apart from internal helpers

## Structure Shortcuts

- If you want the public command surface only:
  - `scripts/README.md`
- If you want the full grouped command catalog:
  - `references/command-reference.md`
- If you want to understand onboarding/autonomy/mirror behavior:
  - `references/bridge-workflow.md`
- If you want to understand saved-profile state and `.aquaclaw/` layout:
  - `references/hosted-profile-plan.md`
- If you want the test suite grouped by area:
  - `test/README.md`

## Runtime And Mirror Details

- `references/mirror-memory-boundary.md`
  - Frozen cache vs memory-source boundary
- `references/mirror-pressure-envelope.md`
  - Startup/read-pressure and footprint envelope
- `references/mirror-service.md`
  - Mirror background-service notes
- `references/runtime-heartbeat-service.md`
  - Standalone runtime-heartbeat service fallback notes
- `references/openclaw-cron-template.md`
  - Disabled cron command template notes for heartbeat/pulse automation

## Templates

- `references/TOOLS.example.md`
  - Example only, not live config
- `references/MEMORY.example.md`
  - Example only, not live memory

## Archive

- `references/archive/README.md`
  - Historical implemented plans and old maintenance passes that no longer define current doc ownership

## Repo Rule

When updating docs:

1. Keep `README.md` short and beginner-first.
2. Put exhaustive commands in `references/command-reference.md`.
3. Put agent routing in `SKILL.md`, not in `README.md`.
4. Put publisher-only material in `references/clawhub-release.md`.
5. If a fact appears in multiple docs, this file should make clear which one is canonical.
6. If hosted pulse behavior changes, update `references/bridge-workflow.md`, `references/public-install.md`, `references/command-reference.md`, and `SKILL.md` together.
7. Keep repo-local regression tests under `test/`, not mixed into `scripts/`.
8. Move completed one-off plan docs under `references/archive/` instead of leaving them in the top-level `references/` directory.
