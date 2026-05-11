# SignalRadar Platform Adapter Matrix

## Summary

- There is no single universal "skill package" standard across all AI platforms.
- Use `core + adapter` architecture:
  - Core: protocol objects, decision logic, state model.
  - Adapter: packaging, auth, invocation, routing for each platform.

## Core (Shared Across Platforms)

- `EntrySpec`, `SignalEvent`, `IntentSpec`, `DeliveryEnvelope`
- Threshold and baseline logic
- UTC storage + user-timezone rendering
- Error envelope and idempotency policy

## Adapter Matrix

### 1) OpenClaw + ClawHub (Primary)

Compatibility: Native

Adapter tasks:

- Keep `SKILL.md` + `references/` + `scripts/` structure.
- Publish with `clawhub publish`.
- Route via channel targets (`discord`, `telegram`, etc.).

### 2) Claude ecosystem (Connectors / MCP)

Compatibility: High via MCP adapter (not direct SKILL.md marketplace import)

Adapter tasks:

- Expose SignalRadar capabilities as MCP tools:
  - `signalradar_ingest`
  - `signalradar_decide`
  - `signalradar_route`
  - `signalradar_config_update`
- Map auth to OAuth/API key model used by connector runtime.
- Keep the same machine payload schema to preserve agent interoperability.

### 3) OpenAI ecosystem (GPT Store / Apps)

Compatibility: Medium-High via GPT/App adapter

Adapter tasks:

- For GPT Actions path: expose HTTPS endpoints with OpenAPI schema.
- For Apps SDK path: expose MCP-compatible tool surface and app metadata.
- Keep deterministic JSON outputs in action/app responses.
- Adapt sharing model:
  - Public GPT Store for eligible GPTs
  - Workspace-only for app-enabled variants

### 4) Microsoft 365 Copilot / Copilot Studio

Compatibility: Medium via Copilot agent adapter

Adapter tasks:

- Wrap core functions as agent actions/plugins callable in Copilot Studio.
- Package for Teams + Microsoft 365 Copilot channels.
- Add org-level publish/approval metadata required by tenant controls.

### 5) Google Gemini Gems

Compatibility: Medium-Low for full automation, High for instruction-only variant

Adapter tasks:

- Gem version: instruction layer + guided workflow prompts.
- For live tool execution, bridge through MCP/server backend and external APIs.
- Keep protocol fields documented for consistent output expectations.

## Recommended Packaging Strategy

1. Keep OpenClaw package as source of truth.
2. Publish one "core contract" doc and generate platform-specific wrappers.
3. Reuse tests across adapters for:
   - threshold logic
   - schema validation
   - idempotency behavior
   - timezone rendering

