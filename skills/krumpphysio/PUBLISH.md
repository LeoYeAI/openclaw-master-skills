# Publishing the KrumpPhysio skill to ClawHub

This folder is a **ClawHub-compatible skill** so other OpenClaw agents can learn the KrumpPhysio coach pattern.

## What’s in this skill

- **SKILL.md** – Name, description, and full instructions (identity, coaching, scoring, Canton, Anyway observability, examples).
- **reference.md** – Short reference for agents.
- **PUBLISH.md** – This file.

## How to publish to ClawHub

1. **Install ClawHub CLI** (if needed):
   ```bash
   npm install -g clawhub
   ```

2. **From the skill directory or repo root**, publish the skill. You can either:
   - Publish the whole repo (ClawHub will use the skill under `skills/krumpphysio/`), or
   - Publish only this folder as a standalone skill.

   Example (from repo root, if ClawHub supports subpath):
   ```bash
   clawhub publish skills/krumpphysio
   ```
   Or from inside the skill folder:
   ```bash
   cd skills/krumpphysio
   clawhub publish .
   ```

   Check [ClawHub docs](https://clawhub.com) or `clawhub --help` for the exact publish command and how to link the skill to your ClawHub account (e.g. `arunnadarasa/krumpphysio`).

3. **After publishing**, other users can install the skill with:
   ```bash
   clawhub install arunnadarasa/krumpphysio
   ```
   (Replace with your actual ClawHub skill ID if different.)

4. **OpenClaw**: Ensure the agent’s workspace or skill path includes the installed skill so it appears in the agent’s available skills list. Then the agent will load this skill when the task matches the description (physio, movement scoring, rehab, Krump, Canton logging).

## Skill ID

- **name:** `krumpphysio`
- **description:** Teaches OpenClaw agents to act as a Krump-inspired physiotherapy coach (scoring, Laban, Canton, SDG 3). Use for physio/rehab agents, movement scoring, or health-and-wellbeing flows.
