# Media (Camera, Images, Audio) Reference

> Sources: https://docs.openclaw.ai/nodes/camera, /nodes/images, /nodes/audio

## Camera Capture

The agent can request camera photos from connected nodes (iOS, Android, macOS).

### Platform Support

| Platform | Default | Notes |
|---|---|---|
| iOS | On | Requires foreground; uses `node.invoke` via Gateway |
| Android | On | Requires camera + storage permissions; foreground required |
| macOS | Off | Uses `node invoke` CLI helper |

### Agent-Initiated Capture
- Agent calls `node.invoke` with camera command via Gateway protocol.
- iOS/Android require the app to be in foreground.
- Captured image is saved to a temp file and injected as media attachment.

### CLI Helper
```bash
openclaw node invoke <nodeId> camera capture
```

### Safety + Practical Limits
- Camera capture requires user opt-in per-node.
- Image resolution and size limits apply per-platform.
- macOS screen video is OS-level, not agent-controlled.

## Image & Media Support

### CLI Surface
```bash
openclaw message send --media <path-or-url> [--message <caption>]
```
- `--media` optional; caption can be empty for media-only sends
- `--dry-run` prints resolved payload
- `--json` emits `{ channel, to, messageId, mediaUrl, caption }`

### WhatsApp Web Behavior

| Media Type | Processing | Max Size |
|---|---|---|
| **Images** | Resize + recompress to JPEG (max side 2048px) targeting `agents.defaults.mediaMaxMb` (default 5 MB) | 6 MB |
| **Audio/Voice/Video** | Pass-through; audio sent as voice note (`ptt: true`) | 16 MB |
| **Documents** | Pass-through, filename preserved | 100 MB |

- **WhatsApp GIF playback**: send MP4 with `gifPlayback: true` (CLI: `--gif-playback`)
- MIME detection: magic bytes → headers → file extension
- Caption from `--message` or `reply.text`; empty caption allowed

### Auto-Reply Pipeline
- `getReplyFromConfig` returns `{ text?, mediaUrl?, mediaUrls? }`
- Multiple media entries sent sequentially

### Inbound Media
- Incoming images/documents are downloaded and attached to the agent prompt.
- Size limits enforced before sending to the model.

## Audio / Voice Notes

### What Works
1. Auto-detect enabled audio transcription providers.
2. Locate first audio attachment (local path or URL).
3. Enforce `maxBytes` per provider.
4. Run first eligible model entry in order (provider or CLI).
5. On success: replace Body with `[Audio]` block and set `{{Transcript}}`.
6. Command parsing: slash commands work from transcript.

### Auto-Detection Priority (Default)
1. **Local CLIs** (if installed):
   - `sherpa-onnx-offline` (requires `SHERPA_ONNX_MODEL_DIR`)
   - `whisper-cli` (whisper-cpp; uses `WHISPER_CPP_MODEL` or bundled tiny)
   - `whisper` (Python CLI; auto-downloads models)
2. **Gemini CLI** (`gemini`) using `read_many_files`
3. **Provider keys**: OpenAI → Groq → Deepgram → Google

### Config Examples

```json5
// Provider + CLI fallback (OpenAI + Whisper CLI)
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [
          { provider: "openai", maxBytes: 26214400 },
          { cli: "whisper-cli", maxBytes: 26214400 },
        ],
      },
    },
  },
}
```

```json5
// Provider-only (Deepgram)
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "deepgram" }],
      },
    },
  },
}
```

```json5
// Echo transcript to chat (opt-in)
{
  tools: {
    media: {
      audio: {
        echoTranscript: true,
      },
    },
  },
}
```

### Mention Detection in Groups
- Audio transcription enables mention detection in group voice notes.
- If transcript contains agent mention pattern, the message triggers agent response.

### Gotchas
- `tools.media.audio.enabled: false` explicitly disables all transcription.
- Auto-detection probes `PATH` for CLI tools.
- Proxy environment variables respected for provider API calls.

### Environment Variables

| Variable | Purpose |
|---|---|
| `SHERPA_ONNX_MODEL_DIR` | Model dir for sherpa-onnx-offline |
| `WHISPER_CPP_MODEL` | Model path for whisper-cli |
| `DEEPGRAM_API_KEY` | Deepgram API key |
| `OPENAI_API_KEY` | OpenAI Whisper API key |

## See Also

- [voice.md](voice.md) — Talk Mode and Voice Wake
- [nodes.md](nodes.md) — iOS, Android, macOS companion apps
- [channels.md](channels.md) — Channel-specific media limits
