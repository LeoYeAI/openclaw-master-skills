---
name: audiopod
description: Use AudioPod AI's API for audio processing tasks including AI music generation (text-to-music, text-to-rap, instrumentals, samples, vocals), stem separation, text-to-speech, noise reduction, speech-to-text transcription, speaker separation, and media extraction. Use when the user needs to generate music/songs/rap from text, split a song into stems/vocals/instruments, generate speech from text, clean up noisy audio, transcribe audio/video, or extract audio from YouTube/URLs. Requires AUDIOPOD_API_KEY env var or pass api_key directly.
---

# AudioPod AI

Full audio processing API: music generation, stem separation, TTS, noise reduction, transcription, speaker separation, wallet management.

## Setup

```bash
pip install audiopod  # Python
npm install audiopod  # Node.js
```

Auth: set `AUDIOPOD_API_KEY` env var or pass to client constructor.

### Getting an API Key
1. Sign up at https://audiopod.ai/auth/signup (free, no credit card required)
2. Go to https://www.audiopod.ai/dashboard/account/api-keys
3. Click "Create API Key" and copy the key (starts with `ap_`)
4. Add funds to your wallet at https://www.audiopod.ai/dashboard/account/wallet (pay-as-you-go, no subscription)

```python
from audiopod import AudioPod
client = AudioPod()  # uses AUDIOPOD_API_KEY env var
# or: client = AudioPod(api_key="ap_...")
```

---

## AI Music Generation

Generate songs, rap, instrumentals, samples, and vocals from text prompts.

**Tasks:** `text2music` (song with vocals), `text2rap` (rap), `prompt2instrumental` (instrumental), `lyric2vocals` (vocals only), `text2samples` (loops/samples), `audio2audio` (style transfer), `songbloom`

### Python SDK

```python
# Generate a full song with lyrics
result = client.music.song(
    prompt="Upbeat pop, synth, drums, 120 bpm, female vocals, radio-ready",
    lyrics="Verse 1:\nWalking down the street on a sunny day\n\nChorus:\nWe're on fire tonight!",
    duration=60
)
print(result["output_url"])

# Generate rap
result = client.music.rap(
    prompt="Lo-Fi Hip Hop, 100 BPM, male rap, melancholy, keyboard chords",
    lyrics="Verse 1:\nStarted from the bottom, now we climbing...",
    duration=60
)

# Generate instrumental (no lyrics needed)
result = client.music.instrumental(
    prompt="Atmospheric ambient soundscape, uplifting, driving mood",
    duration=30
)

# Generic generate with explicit task
result = client.music.generate(
    prompt="Electronic dance music, high energy",
    task="text2samples",  # any task type
    duration=30
)

# Async: submit then poll
job = client.music.create(
    prompt="Chill lofi beat", 
    duration=30, 
    task="prompt2instrumental"
)
result = client.music.wait_for_completion(job["id"], timeout=600)

# Get available genre presets
presets = client.music.get_presets()

# List/manage jobs
jobs = client.music.list(skip=0, limit=50)
job = client.music.get(job_id=123)
client.music.delete(job_id=123)
```

### cURL

```bash
# Song with lyrics
curl -X POST "https://api.audiopod.ai/api/v1/music/text2music" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"upbeat pop, synth, 120bpm, female vocals", "lyrics":"Walking down the street...", "audio_duration":60}'

# Rap
curl -X POST "https://api.audiopod.ai/api/v1/music/text2rap" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Lo-Fi Hip Hop, male rap, 100 BPM", "lyrics":"Started from the bottom...", "audio_duration":60}'

# Instrumental
curl -X POST "https://api.audiopod.ai/api/v1/music/prompt2instrumental" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"ambient soundscape, uplifting", "audio_duration":30}'

# Samples/loops
curl -X POST "https://api.audiopod.ai/api/v1/music/text2samples" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"drum loop, sad mood", "audio_duration":15}'

# Vocals only
curl -X POST "https://api.audiopod.ai/api/v1/music/lyric2vocals" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"clean vocals, happy", "lyrics":"Eternal chorus of unity...", "audio_duration":30}'

# Check job status / get result
curl "https://api.audiopod.ai/api/v1/music/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Get genre presets
curl "https://api.audiopod.ai/api/v1/music/presets" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# List jobs
curl "https://api.audiopod.ai/api/v1/music/jobs?skip=0&limit=50" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Delete job
curl -X DELETE "https://api.audiopod.ai/api/v1/music/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"
```

### Parameters

| Field | Required | Description |
|-------|----------|-------------|
| prompt | yes | Style/genre description |
| lyrics | for song/rap/vocals | Song lyrics with verse/chorus structure |
| audio_duration | no | Duration in seconds (default: 30) |
| genre_preset | no | Genre preset name (from presets endpoint) |
| display_name | no | Track display name |

---

## Stem Separation

Split audio into individual instrument/vocal tracks.

### Modes

| Mode | Stems | Output | Use Case |
|------|-------|--------|----------|
| single | 1 | Specified stem only | Vocal isolation, drum extraction |
| two | 2 | vocals + instrumental | Karaoke tracks |
| four | 4 | vocals, drums, bass, other | Standard remixing (default) |
| six | 6 | + guitar, piano | Full instrument separation |
| producer | 8 | + kick, snare, hihat | Beat production |
| studio | 12 | + cymbals, sub_bass, synth | Professional mixing |
| mastering | 16 | Maximum detail | Forensic analysis |

**Single stem options:** vocals, drums, bass, guitar, piano, other

### Python SDK

```python
# Sync: extract and wait for result
result = client.stems.separate(
    url="https://youtube.com/watch?v=VIDEO_ID",
    mode="six",
    timeout=600
)
for stem, url in result["download_urls"].items():
    print(f"{stem}: {url}")

# From local file
result = client.stems.separate(file="/path/to/song.mp3", mode="four")

# Single stem extraction
result = client.stems.separate(
    url="https://youtube.com/watch?v=ID",
    mode="single",
    stem="vocals"
)

# Async: submit then poll
job = client.stems.extract(url="https://youtube.com/watch?v=ID", mode="six")
print(f"Job ID: {job['id']}")
status = client.stems.status(job["id"])
# or wait:
result = client.stems.wait_for_completion(job["id"], timeout=600)

# List available modes
modes = client.stems.modes()

# Job management
jobs = client.stems.list(skip=0, limit=50, status="COMPLETED")
job = client.stems.get(job_id=1234)
client.stems.delete(job_id=1234)
```

### cURL

```bash
# Extract from URL
curl -X POST "https://api.audiopod.ai/api/v1/stem-extraction/api/extract" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -F "url=https://youtube.com/watch?v=VIDEO_ID" \
  -F "mode=six"

# Extract from file
curl -X POST "https://api.audiopod.ai/api/v1/stem-extraction/api/extract" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -F "file=@/path/to/song.mp3" \
  -F "mode=four"

# Single stem
curl -X POST "https://api.audiopod.ai/api/v1/stem-extraction/api/extract" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -F "url=URL" \
  -F "mode=single" \
  -F "stem=vocals"

# Check job status
curl "https://api.audiopod.ai/api/v1/stem-extraction/status/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# List available modes
curl "https://api.audiopod.ai/api/v1/stem-extraction/modes" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# List jobs (filter by status: PENDING, PROCESSING, COMPLETED, FAILED)
curl "https://api.audiopod.ai/api/v1/stem-extraction/jobs?skip=0&limit=50&status=COMPLETED" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Get specific job
curl "https://api.audiopod.ai/api/v1/stem-extraction/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Delete job
curl -X DELETE "https://api.audiopod.ai/api/v1/stem-extraction/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"
```

### Response Format

```json
{
  "id": 1234,
  "status": "COMPLETED",
  "download_urls": {
    "vocals": "https://...",
    "drums": "https://...",
    "bass": "https://...",
    "other": "https://..."
  },
  "quality_scores": {
    "vocals": 0.95,
    "drums": 0.88
  }
}
```

---

## Text to Speech

Generate speech from text with 50+ voices in 60+ languages. Supports voice cloning.

### Voice Types

- **50+ production-ready voices** — multilingual, supporting 60+ languages with auto-detection
- **Custom clones** — clone any voice with ~5 seconds of audio sample

### Python SDK

```python
# Generate speech and wait for result
result = client.voice.generate(
    text="Hello, world! This is a test.",
    voice_id=123,
    speed=1.0
)
print(result["output_url"])

# Async: submit then poll
job = client.voice.speak(
    text="Hello world",
    voice_id=123,
    speed=1.0
)
status = client.voice.get_job(job["id"])
result = client.voice.wait_for_completion(job["id"], timeout=300)

# List all available voices
voices = client.voice.list()
for v in voices:
    print(f"{v['id']}: {v['name']}")

# Clone a voice (needs ~5 sec audio sample)
new_voice = client.voice.create(
    name="My Voice Clone",
    audio_file="./sample.mp3",
    description="Cloned from recording"
)

# Get/delete voice
voice = client.voice.get(voice_id=123)
client.voice.delete(voice_id=123)
```

### cURL (Raw HTTP — most reliable)

```bash
# List all voices
curl "https://api.audiopod.ai/api/v1/voice/voice-profiles" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Generate speech (FORM DATA, not JSON!)
curl -X POST "https://api.audiopod.ai/api/v1/voice/voices/{VOICE_UUID}/generate" \
  -H "Authorization: Bearer $AUDIOPOD_API_KEY" \
  -d "input_text=Hello world, this is a test" \
  -d "audio_format=mp3" \
  -d "speed=1.0"

# Poll job status
curl "https://api.audiopod.ai/api/v1/voice/tts-jobs/{JOB_ID}/status" \
  -H "Authorization: Bearer $AUDIOPOD_API_KEY"

# SDK-style endpoints (alternative)
# Generate via SDK endpoint
curl -X POST "https://api.audiopod.ai/api/v1/voice/tts/generate" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world","voice_id":123,"speed":1.0}'

# Poll via SDK endpoint
curl "https://api.audiopod.ai/api/v1/voice/tts/status/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# List voices (SDK endpoint)
curl "https://api.audiopod.ai/api/v1/voice/voices" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Clone a voice
curl -X POST "https://api.audiopod.ai/api/v1/voice/voices" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -F "name=My Voice" \
  -F "file=@sample.mp3" \
  -F "description=Cloned voice"

# Delete voice
curl -X DELETE "https://api.audiopod.ai/api/v1/voice/voices/VOICE_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"
```

### Generate Parameters

| Field | Required | Description |
|-------|----------|-------------|
| input_text | yes | Text to speak (max 5000 chars). Use `input_text` for raw HTTP, `text` for SDK |
| audio_format | no | mp3, wav, ogg (default: mp3) |
| speed | no | 0.25 - 4.0 (default: 1.0) |
| language | no | ISO code, auto-detected if omitted |

### Response Format

```json
// Generate response
{"job_id": 12345, "status": "pending", "credits_reserved": 25}

// Status response (completed)
{"status": "completed", "output_url": "https://r2-url/generated.mp3"}
```

### Important Notes

- Raw HTTP generate endpoint uses **form data**, not JSON. Field is `input_text` not `text`
- SDK endpoint (`/api/v1/voice/tts/generate`) uses JSON with field `text`
- Output files may be WAV disguised as .mp3 — convert with `ffmpeg -i output.mp3 -c:a aac real.m4a`
- ~55 credits per generation, wallet-based billing

---

## Speaker Separation

Separate audio by speaker with automatic diarization.

### Python SDK

```python
# Diarize and wait for result
result = client.speaker.identify(
    file="./meeting.mp3",
    num_speakers=3,  # optional hint for accuracy
    timeout=600
)
for segment in result["segments"]:
    print(f"Speaker {segment['speaker']}: {segment['text']} [{segment['start']:.1f}s - {segment['end']:.1f}s]")

# From URL
result = client.speaker.identify(
    url="https://youtube.com/watch?v=VIDEO_ID",
    num_speakers=2
)

# Async: submit then poll
job = client.speaker.diarize(
    file="./meeting.mp3",
    num_speakers=3
)
result = client.speaker.wait_for_completion(job["id"], timeout=600)

# Job management
jobs = client.speaker.list(skip=0, limit=50, status="COMPLETED")
job = client.speaker.get(job_id=123)
client.speaker.delete(job_id=123)
```

### cURL

```bash
# Diarize from file
curl -X POST "https://api.audiopod.ai/api/v1/speaker/diarize" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -F "file=@meeting.mp3" \
  -F "num_speakers=3"

# Diarize from URL
curl -X POST "https://api.audiopod.ai/api/v1/speaker/diarize" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -F "url=https://youtube.com/watch?v=VIDEO_ID" \
  -F "num_speakers=2"

# Check job status
curl "https://api.audiopod.ai/api/v1/speaker/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# List jobs
curl "https://api.audiopod.ai/api/v1/speaker/jobs?skip=0&limit=50" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Delete job
curl -X DELETE "https://api.audiopod.ai/api/v1/speaker/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"
```

---

## Speech to Text (Transcription)

Transcribe audio/video with speaker diarization, word-level timestamps, and multiple output formats.

### Python SDK

```python
# Transcribe URL and wait
result = client.transcription.transcribe(
    url="https://youtube.com/watch?v=VIDEO_ID",
    speaker_diarization=True,
    min_speakers=2,
    max_speakers=5,
    timeout=600
)
print(f"Language: {result['detected_language']}")
for seg in result["segments"]:
    print(f"[{seg['start']:.1f}s] {seg.get('speaker','?')}: {seg['text']}")

# Batch: multiple URLs at once
result = client.transcription.transcribe(
    urls=["https://youtube.com/watch?v=ID1", "https://youtube.com/watch?v=ID2"],
    speaker_diarization=True
)

# Upload local file
job = client.transcription.upload(
    file_path="./recording.mp3",
    language="en",
    speaker_diarization=True
)
result = client.transcription.wait_for_completion(job["id"], timeout=600)

# Async: submit then poll
job = client.transcription.create(
    url="https://youtube.com/watch?v=ID",
    language="en",
    speaker_diarization=True,
    word_timestamps=True,
    min_speakers=2,
    max_speakers=4
)
result = client.transcription.wait_for_completion(job["id"], timeout=600)

# Get transcript in different formats
transcript_json = client.transcription.get_transcript(job_id=123, format="json")
transcript_srt = client.transcription.get_transcript(job_id=123, format="srt")
transcript_vtt = client.transcription.get_transcript(job_id=123, format="vtt")
transcript_txt = client.transcription.get_transcript(job_id=123, format="txt")

# Job management
jobs = client.transcription.list(skip=0, limit=50, status="COMPLETED")
job = client.transcription.get(job_id=123)
client.transcription.delete(job_id=123)
```

### cURL

```bash
# Transcribe from URL
curl -X POST "https://api.audiopod.ai/api/v1/transcribe/transcribe" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://youtube.com/watch?v=ID","enable_speaker_diarization":true,"word_timestamps":true}'

# Transcribe multiple URLs
curl -X POST "https://api.audiopod.ai/api/v1/transcribe/transcribe" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls":["URL1","URL2"],"enable_speaker_diarization":true}'

# Upload file for transcription
curl -X POST "https://api.audiopod.ai/api/v1/transcribe/transcribe-upload" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -F "files=@recording.mp3" \
  -F "language=en" \
  -F "enable_speaker_diarization=true"

# Get job status
curl "https://api.audiopod.ai/api/v1/transcribe/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Get transcript in specific format (json, srt, vtt, txt)
curl "https://api.audiopod.ai/api/v1/transcribe/jobs/JOB_ID/transcript?format=srt" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# List jobs
curl "https://api.audiopod.ai/api/v1/transcribe/jobs?offset=0&limit=50" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Delete job
curl -X DELETE "https://api.audiopod.ai/api/v1/transcribe/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"
```

### Parameters

| Field | Required | Description |
|-------|----------|-------------|
| url / urls | yes (or file) | URL(s) to transcribe (YouTube, SoundCloud, direct links) |
| language | no | ISO 639-1 code (auto-detected if omitted) |
| enable_speaker_diarization | no | Enable speaker identification (default: false) |
| min_speakers / max_speakers | no | Speaker count hints for better diarization |
| word_timestamps | no | Enable word-level timestamps (default: true) |

### Output Formats

- **json** — Full structured output with segments, timestamps, speakers
- **srt** — SubRip subtitle format
- **vtt** — WebVTT subtitle format
- **txt** — Plain text transcript

---

## Noise Reduction

Remove background noise from audio/video files.

### Python SDK

```python
# Denoise and wait for result
result = client.denoiser.denoise(file="./noisy-audio.mp3", timeout=600)
print(f"Clean audio: {result['output_url']}")

# From URL
result = client.denoiser.denoise(url="https://example.com/noisy.mp3")

# Async: submit then poll
job = client.denoiser.create(file="./noisy-audio.mp3")
result = client.denoiser.wait_for_completion(job["id"], timeout=600)

# From URL (async)
job = client.denoiser.create(url="https://example.com/noisy.mp3")

# Job management
jobs = client.denoiser.list(skip=0, limit=50, status="COMPLETED")
job = client.denoiser.get(job_id=123)
client.denoiser.delete(job_id=123)
```

### cURL

```bash
# Denoise from file
curl -X POST "https://api.audiopod.ai/api/v1/denoiser/denoise" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -F "file=@noisy-audio.mp3"

# Denoise from URL
curl -X POST "https://api.audiopod.ai/api/v1/denoiser/denoise" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -F "url=https://example.com/noisy.mp3"

# Check job status
curl "https://api.audiopod.ai/api/v1/denoiser/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# List jobs
curl "https://api.audiopod.ai/api/v1/denoiser/jobs?skip=0&limit=50" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Delete job
curl -X DELETE "https://api.audiopod.ai/api/v1/denoiser/jobs/JOB_ID" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"
```

---

## Wallet & Billing

Check balance, estimate costs, and view usage history.

### Python SDK

```python
# Get current balance
balance = client.wallet.get_balance()
print(f"Balance: ${balance['balance_usd']}")

# Check if balance is sufficient for an operation
check = client.wallet.check_balance(
    service_type="stem_extraction",
    duration_seconds=180
)
print(f"Sufficient: {check['sufficient']}")

# Estimate cost before running
estimate = client.wallet.estimate_cost(
    service_type="transcription",
    duration_seconds=300
)
print(f"Cost: ${estimate['cost_usd']}")

# Get pricing for all services
pricing = client.wallet.get_pricing()

# View usage history
usage = client.wallet.get_usage(page=1, limit=50)
```

### cURL

```bash
# Get balance
curl "https://api.audiopod.ai/api/v1/api-wallet/balance" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Check balance sufficiency
curl -X POST "https://api.audiopod.ai/api/v1/api-wallet/check-balance" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"service_type":"stem_extraction","duration_seconds":180}'

# Estimate cost
curl -X POST "https://api.audiopod.ai/api/v1/api-wallet/estimate-cost" \
  -H "X-API-Key: $AUDIOPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"service_type":"transcription","duration_seconds":300}'

# Get pricing
curl "https://api.audiopod.ai/api/v1/api-wallet/pricing" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"

# Usage history
curl "https://api.audiopod.ai/api/v1/api-wallet/usage?page=1&limit=50" \
  -H "X-API-Key: $AUDIOPOD_API_KEY"
```

---

## API Endpoint Summary

| Service | Endpoint | Method |
|---------|----------|--------|
| **Music** | `/api/v1/music/{task}` | POST |
| Music jobs | `/api/v1/music/jobs/{id}` | GET/DELETE |
| Music presets | `/api/v1/music/presets` | GET |
| **Stems** | `/api/v1/stem-extraction/api/extract` | POST (multipart) |
| Stems status | `/api/v1/stem-extraction/status/{id}` | GET |
| Stems modes | `/api/v1/stem-extraction/modes` | GET |
| Stems jobs | `/api/v1/stem-extraction/jobs` | GET |
| **TTS** generate | `/api/v1/voice/voices/{uuid}/generate` | POST (form data) |
| TTS generate (SDK) | `/api/v1/voice/tts/generate` | POST (JSON) |
| TTS status | `/api/v1/voice/tts-jobs/{id}/status` | GET |
| TTS status (SDK) | `/api/v1/voice/tts/status/{id}` | GET |
| Voice list | `/api/v1/voice/voice-profiles` | GET |
| Voice list (SDK) | `/api/v1/voice/voices` | GET |
| **Speaker** | `/api/v1/speaker/diarize` | POST (multipart) |
| Speaker jobs | `/api/v1/speaker/jobs/{id}` | GET/DELETE |
| **Transcribe** URL | `/api/v1/transcribe/transcribe` | POST (JSON) |
| Transcribe upload | `/api/v1/transcribe/transcribe-upload` | POST (multipart) |
| Transcript output | `/api/v1/transcribe/jobs/{id}/transcript?format=` | GET |
| Transcribe jobs | `/api/v1/transcribe/jobs` | GET |
| **Denoise** | `/api/v1/denoiser/denoise` | POST (multipart) |
| Denoise jobs | `/api/v1/denoiser/jobs/{id}` | GET/DELETE |
| **Wallet** balance | `/api/v1/api-wallet/balance` | GET |
| Wallet pricing | `/api/v1/api-wallet/pricing` | GET |
| Wallet usage | `/api/v1/api-wallet/usage` | GET |

## Auth Headers

Two auth styles work:
- `X-API-Key: ap_...` — works for most endpoints
- `Authorization: Bearer ap_...` — works for TTS generate/status

## Known Issues

- SDK method signatures may differ from raw API — when in doubt, use cURL examples
- TTS output stored on Cloudflare R2, download via `output_url` in job status
- TTS output files may be WAV disguised as .mp3 — convert with ffmpeg before sending via WhatsApp
