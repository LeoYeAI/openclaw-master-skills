# Voice: Talk Mode & Voice Wake

> Sources:
> - https://docs.openclaw.ai/nodes/talk
> - https://docs.openclaw.ai/nodes/voicewake

## Talk Mode

### Behavior (macOS)

- Always-on overlay while Talk mode is enabled.
- Phase transitions: Listening → Thinking → Speaking.
- On a short pause (silence window), the current transcript is sent.
- Replies are written to WebChat (same as typing).
- **Interrupt on speech** (default on): if the user starts talking while the assistant is speaking, playback stops and the interruption timestamp is noted for the next prompt.

### Voice Directives in Replies

The agent can include a JSON line as the first non-empty line of its reply to control voice parameters:

```json
{ "voice": "<voice-id>", "once": true }
```

Supported keys:
- `voice` / `voice_id` / `voiceId`
- `model` / `model_id` / `modelId`
- `speed`, `rate` (WPM), `stability`, `similarity`, `style`, `speakerBoost`
- `seed`, `normalize`, `lang`, `output_format`, `latency_tier`
- `once` — `true` applies to current reply only; without it, becomes new default

The JSON line is stripped before TTS playback.

### Configuration

```json5
{
  talk: {
    voiceId: "elevenlabs_voice_id",
    modelId: "eleven_v3",
    outputFormat: "mp3_44100_128",
    apiKey: "elevenlabs_api_key",
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

| Key | Default / Fallback |
|---|---|
| `interruptOnSpeech` | `true` |
| `silenceTimeoutMs` | 700ms (macOS/Android), 900ms (iOS) |
| `voiceId` | `ELEVENLABS_VOICE_ID` / `SAG_VOICE_ID` / first ElevenLabs voice |
| `modelId` | `eleven_v3` |
| `apiKey` | `ELEVENLABS_API_KEY` |
| `outputFormat` | `pcm_44100` (macOS/iOS), `pcm_24000` (Android) |

### macOS UI

- Menu bar toggle: Talk
- Config tab: Talk Mode group (voice id + interrupt toggle)
- Overlay states:
  - Listening: cloud pulses with mic level
  - Thinking: sinking animation
  - Speaking: radiating rings
  - Click cloud: stop speaking
  - Click X: exit Talk mode

---

## Voice Wake (Global Wake Words)

### Storage (Gateway Host)

- Wake word models stored on the Gateway host.
- Clients download models via Gateway RPC.

### Protocol

#### Methods

- `voicewake.models` — list available models
- `voicewake.download` — download a model file
- `voicewake.config.*` — get/set wake word config

#### Events

- `voicewake.trigger` — wake word detected
- `voicewake.config` — config changed

### Client Behavior

#### macOS App

- Uses Porcupine wake word engine.
- Global microphone listening (requires Microphone permission).
- Wake word triggers Talk mode entry.

#### iOS Node

- Background wake word detection.
- Triggers Talk mode on the iOS node.

#### Android Node

- Background wake word detection via Porcupine.
- Triggers Talk mode entry.
