# Media Requirements & Voice Note Handling

## Media Path Restriction (WhatsApp)

The openclaw gateway only allows sending media files from `~/.openclaw/media/`. Any file outside this directory will be rejected with `LocalMediaAccessError`.

**When sending images, comics, voice notes, or any media to a narrator via WhatsApp:**

1. Always save/copy the file to `~/.openclaw/media/` first
2. Use that path when sending via `openclaw message send --media` or `MEDIA:` line

```bash
# Correct — file under allowed media directory
openclaw message send --target "+1234567890" --media ~/.openclaw/media/comic.png --message "Hi"

# Blocked — file outside allowed directory
openclaw message send --target "+1234567890" --media ~/Desktop/comic.png --message "Hi"
```

Note: `channels.whatsapp.mediaLocalRoots` is NOT a valid openclaw config key — do not add it.

---

## Channel-Specific Media Format Requirements

Openclaw does NOT auto-convert media formats. The agent must provide correctly formatted media for each target channel.

### Voice Notes (critical — wrong format = file download instead of voice player)

| Channel | Required Format | Max Size | Max Duration | Notes |
|---|---|---|---|---|
| WhatsApp | OGG/Opus (`.ogg`) | 16 MB | Unlimited | MP3/AAC show as file download, NOT voice message |
| Telegram | OGG/Opus (`.ogg`) | 50 MB | Unlimited | Use `sendVoice` endpoint; MP3/M4A also work |
| WeChat | AMR (`.amr`) | 256 KB | 60 sec | Extremely restrictive; must convert |
| iMessage | AAC/M4A, MP3, OGG | 100 MB | Unlimited | Most formats work; iMessage is flexible |

Edge TTS produces MP3. For WhatsApp voice messages, convert: `ffmpeg -i input.mp3 -c:a libopus -b:a 32k output.ogg`

### Images (comics/illustrations)

| Channel | Formats | Max Size | Recommended Resolution |
|---|---|---|---|
| WhatsApp | JPG, PNG | 16 MB | 800-1600px (auto-compresses) |
| Telegram | JPG, PNG, GIF, WebP | 10 MB | 1280x1280px |
| WeChat | JPG, PNG | 10 MB | Max 1000x1000px |
| iMessage | JPG, PNG, GIF, HEIC | 100 MB | No specific limit |

For cross-channel comics: use 1200x1200px JPG/PNG.

### Text & Captions

| Channel | Message Limit | Caption Limit |
|---|---|---|
| WhatsApp | 65,536 chars | 256 chars |
| Telegram | 4,096 chars | 1,024 chars (4,096 premium) |
| WeChat | 5,000 chars | N/A |
| iMessage | ~20,000 chars | N/A |

### Key rules for multi-channel agents
1. Always check `channel` from message context before sending media
2. Branch format conversion logic by channel
3. WeChat is most restrictive (256KB voice, 1000px images)
4. iMessage is most generous (100MB, flexible formats, macOS only)
5. Telegram is also generous (50MB, flexible formats)

---

## TTS Config Location

TTS config MUST be under `messages.tts` in openclaw.json, NOT `tools.media.tts`.
- `tools.media.tts` → rejected: `Invalid config: tools.media: Unrecognized key: "tts"`
- `messages.tts` → correct (per openclaw docs)

For Chinese narrators, set `"voice": "zh-CN-XiaoxiaoNeural"`. Without this, edge-tts defaults to English and produces garbled speech.

---

## Media Sends Timeout (Text Works, Media Hangs)

**Symptom:** `openclaw message send --media` or agent media sends timeout after 10-30s, but text messages succeed instantly.

**Root cause:** An uncaught exception in the gateway (e.g. failed voice note decode: `ENOENT: .../audio{ID}-enc`) crashes the WhatsApp WebSocket. Media uploads break but text still works.

**Solution:** `openclaw gateway restart`

**Diagnostic signs in `/tmp/openclaw/openclaw-*.log`:**
- `[openclaw] Uncaught exception: Error: ENOENT`
- `Error: gateway closed (1006 abnormal closure)`
- Multiple "Sending message (media)" with no "Sent" confirmation

Do NOT repeatedly retry media sends — they will keep timing out. Restart the gateway first.

---

## Voice Note Handling (STT)

When a narrator sends a voice note, use this priority order to transcribe it:

### Tier 1 — Openclaw native (preferred)
Check if Openclaw's `tools.media.audio` is configured. If yes, Openclaw has already transcribed the `.ogg` automatically before the message reached this skill. Use the transcription directly.

### Tier 2 — Local CLI fallback
If Openclaw native STT is not configured, check which binary is available:

```
# Apple Silicon (mlx-whisper)
which mlx-whisper-transcribe && mlx-whisper-transcribe {{MediaPath}}

# Intel Mac / Linux (openai-whisper via brew)
which whisper && whisper {{MediaPath}} --model small --output_format txt
```

Run whichever is found. Store the transcription text in the fragment.

### Tier 3 — Manual fallback (no STT installed)
If neither binary is found, tell the user:

```
Voice note received but no transcription tool is installed.

To enable automatic voice transcription, run one of:
  - /memorist_agent setup-stt     (auto-installs mlx-whisper on Apple Silicon)
  - brew install openai-whisper   (manual install for Intel Mac / Linux)

For now, please listen to the voice note and type what they said:
  File: ~/.openclaw/media/inbound/{filename}.ogg
```

Save the manually typed text as the answer, and flag the fragment with `"transcriptionMethod": "manual"`.

### /memorist_agent setup-stt

A helper command that auto-detects the machine and installs the right transcription tool:

1. Check `uname -m`:
   - `arm64` → run `pip3 install mlx-whisper` and configure `~/.openclaw/openclaw.json` under `tools.media.audio`
   - `x86_64` / Linux → run `brew install openai-whisper` or `pip3 install openai-whisper`
2. Test with: `mlx-whisper-transcribe` or `whisper --version`
3. Report: "STT ready: {tool} (local). Voice notes will be transcribed automatically."
