# Text to Speech Reference

## API Endpoints

- **List voices:** `GET /api/v1/voice/voice-profiles` (header: `X-API-Key`)
- **Generate:** `POST /api/v1/voice/voices/{VOICE_UUID}/generate` (form data, not JSON!)
- **Poll status:** `GET /api/v1/voice/tts-jobs/{JOB_ID}/status`

## Generate Parameters (form data)

| Field | Required | Description |
|-------|----------|-------------|
| input_text | yes | Text to speak (max 5000 chars) |
| audio_format | no | mp3, wav, ogg (default: mp3) |
| speed | no | 0.25 - 4.0 (default: 1.0) |
| language | no | ISO code, auto-detected if omitted |

**Critical:** Use `input_text` not `text`. Send as form data, not JSON body.

## Voice Types

- **50+ production-ready voices** — multilingual, supporting 60+ languages with auto-detection
- **Custom clones** — clone any voice with ~5 seconds of audio

## Voice Identification

Voices can be referenced by:
- UUID: `550e8400-e29b-41d4-a716-446655440000`
- Name: `aura`, `jester`, `sage`, `ava`, `surge`, `willow`
- Integer ID: `123`

## Response Format

Generate response:
```json
{
  "job_id": 12345,
  "status": "pending",
  "credits_reserved": 25
}
```

Status response (completed):
```json
{
  "status": "completed",
  "output_url": "https://r2-url/generated.mp3"
}
```

## Known Issues

- Output files are WAV disguised as .mp3 — convert with: `ffmpeg -i output.mp3 -c:a aac real.m4a`
- SDK `Client` class may have different method signatures than docs — use raw HTTP for reliability
- ~55 credits per generation, wallet-based billing
