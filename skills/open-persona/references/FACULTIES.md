# Faculty Reference

Faculties are **persistent capabilities** that shape how the persona perceives or expresses across conversations. They are declared under the `faculties` array in `persona.json`.

> **Faculties vs Skills** — Faculties are always-on dimensions (voice, cognition, appearance); Skills are discrete on-demand actions. `selfie`, `music`, and `reminder` are **skills** — see `persona.json → skills` array.

## Available Faculties

| Faculty | Dimension | What It Does | Recommend When |
|---------|-----------|-------------|----------------|
| **voice** | expression | TTS via ElevenLabs ✅ / OpenAI ⚠️ / Qwen3-TTS ⚠️ | User wants the persona to speak, voice messages, audio content |
| **avatar** | expression | External avatar runtime bridge (provider-based, fallback-safe) | User wants visual embodiment (image/3D/motion/voice avatar) |
| **memory** | cognition | Cross-session recall via `memories.jsonl` (local, Mem0, Zep); supersession chain for updating memories; top-level `memory.inheritance` in `persona.json` controls whether memories are copied to child personas at fork | User wants persistent memory across conversations |

## Built-in Skills (not faculties)

These are declared in the `skills` array, not `faculties`:

| Skill | What It Does | Env Var |
|-------|-------------|---------|
| **selfie** | AI selfie generation via fal.ai | `FAL_KEY` |
| **music** | AI music composition via ElevenLabs | `ELEVENLABS_API_KEY` |
| **reminder** | Reminders and task management | (none) |

## Environment Variables

- **voice**: `ELEVENLABS_API_KEY` (or `TTS_API_KEY`), `TTS_PROVIDER`, `TTS_VOICE_ID`, `TTS_STABILITY`, `TTS_SIMILARITY`
- **avatar**: `AVATAR_RUNTIME_URL`, `AVATAR_API_KEY` (provider/runtime specific)
- **memory**: (none for local) or `MEMORY_API_KEY` (for Mem0/Zep)
- **selfie** (skill): `FAL_KEY` (from https://fal.ai/dashboard/keys)
- **music** (skill): `ELEVENLABS_API_KEY` (shared with voice — same key from https://elevenlabs.io)

## Rich Faculty Config

Each faculty in `persona.json` is an object with optional config:

```json
{ "name": "voice", "provider": "elevenlabs", "voiceId": "...", "stability": 0.4, "similarity_boost": 0.8 }
```

Config is automatically mapped to env vars at install time. Users only need to add their API key.
