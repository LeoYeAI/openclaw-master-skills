# Avatar Faculty Reference

This document defines the boundary between OpenPersona and external avatar runtimes.

## Core Principle

- OpenPersona keeps a lightweight avatar bridge in `layers/faculties/avatar/`.
- Real avatar capability (rendering, lip-sync, streaming, provider SDK integration) lives in an external project/skill.
- This follows the same integration philosophy as AgentBooks: protocol in OpenPersona, heavy implementation outside.

## Canonical Install Source

Use the following install source in OpenPersona faculty declarations:

```bash
npx skills add avatar-runtime
# or directly from GitHub:
npx skills add github:acnlabs/avatar-runtime/skill/avatar-runtime
```

## What Stays in OpenPersona

- `layers/faculties/avatar/faculty.json`
  - Capability declaration
  - Default provider selection (for example, `heygen`)
  - Fallback policy (for example, `text_only`)
  - External install source (`install`)
- `layers/faculties/avatar/SKILL.md`
  - Bridge behavior
  - Installed vs. not-installed behavior
  - User-facing degradation policy

## What Stays in External Avatar Project

- Provider adapters (`heygen`, anime/OC providers, custom runtimes)
- Session lifecycle and auth
- Media pipeline (audio/video/image)
- Lip-sync and animation control
- Retry, rate-limit, and vendor error handling
- Vendor-specific command surface and SDK versions

## Provider Model

OpenPersona should treat avatar providers as pluggable backends.

- `heygen` — real-time realistic streaming avatar
- `anime` / `oc` providers (for example style-focused services like [KusaPics](https://kusa.pics/))
- `custom` — self-hosted runtime

Provider choice belongs to persona config (or host runtime policy), not hardcoded generator logic.

## Minimal Provider Contract (P0)

All external avatar skills should expose a stable contract equivalent to:

1. `createSession` — initialize runtime session
2. `sendText` — text input -> avatar response
3. `sendAudio` — audio input -> avatar response
4. `render` — switch visual form/style (image, 3D, motion, voice mode)
5. `status` — runtime health and active capabilities

These action names are interface-level semantics. Transport (CLI, HTTP, WebSocket) is implementation-specific.

## Asset Placement

Persona avatar assets belong in the generated skill pack's `assets/` directory per [Agent Skills spec](https://agentskills.io/specification#assets%2F):

- **`assets/avatar/`** — Virtual avatar assets: images, Live2D models (`.model3.json`), VRM (`.vrm`), textures. Use relative paths like `./assets/avatar/default.model3.json` in `persona.json` or state.
- **`assets/reference/`** — Reference images (e.g. for selfie faculty). `referenceImage` can resolve to `./assets/reference/avatar.png` when bundled.

This keeps the skill pack self-contained and portable; consumers load assets via relative paths without external dependencies.

## Fallback Rules (Required)

If avatar skill/runtime is unavailable:

- Continue text conversation
- Explicitly state avatar mode is unavailable
- Offer installation/activation guidance from `install`
- Never fake visual/voice success

## Recommended Rollout

- **P0:** One production provider (default `heygen`) + graceful fallback
- **P1:** Multi-provider switch (realistic + anime style + custom)
- **P2:** Capability-driven sensory UI sync (icon states driven by runtime `status`)

## See Also

- **[avatar-runtime](https://github.com/acnlabs/avatar-runtime)** — Full technical reference: provider capability matrix, AvatarWidget API, Renderer Registry, VRM/Live2D asset setup, and Session API contract.
