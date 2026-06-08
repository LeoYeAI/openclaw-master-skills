## OpenClaw / Hostinger Setup Note

> This guide is for users running the voice-agent-pro-v3 skill inside
> an OpenClaw container on a Hostinger VPS.

### Running commands inside the OpenClaw container

```bash
# From your VPS host via SSH
ssh root@your-vps-ip

# Execute a command inside the container
docker exec openclaw-yyvg-openclaw-1 pip install elevenlabs --break-system-packages
docker exec openclaw-yyvg-openclaw-1 pip install twilio --break-system-packages
docker exec openclaw-yyvg-openclaw-1 apt-get update
docker exec openclaw-yyvg-openclaw-1 apt-get install -y ffmpeg

# Or open an interactive shell inside the container
docker exec -it openclaw-yyvg-openclaw-1 bash
# Then run pip install, apt-get etc. as normal
```

### Restart OpenClaw after .env changes

```bash
cd /docker/openclaw-yyvg
docker compose down && docker compose up -d
docker logs --tail 30 openclaw-yyvg-openclaw-1
```

---

# Setup Guide — Voice Agent Pro V3

> Complete reference for setting up ElevenLabs voice cloning.
> Two paths: terminal (fastest) or browser navigation.
> The agent reads this file during setup.

---

## What You Need Before Starting

```
AUDIO SAMPLES — required for voice cloning
  Minimum : 1 file × 30 seconds
  Recommended : 3 files × 1-2 minutes each
  Optimal (Professional Clone) : 30+ minutes total

  Quality requirements :
  → Clear voice, no background noise or music
  → Natural speech rhythm (not reading robotically)
  → Consistent microphone distance
  → Format : MP3, WAV, M4A, FLAC all accepted
  → No multiple speakers in the same file

  Where to put them :
  /workspace/voice/samples/sample_01.mp3
  /workspace/voice/samples/sample_02.mp3
  /workspace/voice/samples/sample_03.mp3

MINIMUM PLAN REQUIRED
  Instant Voice Clone (IVC) : Starter plan ($5/month) or above
  Professional Voice Clone (PVC) : Creator plan ($22/month) or above
```

---

## PATH A — Terminal / API (fastest — recommended)

### Step 1 — Install dependencies

```bash
pip install elevenlabs --break-system-packages
apt-get update && apt-get install -y ffmpeg
ffmpeg -version | head -1
python3 -c "from elevenlabs.client import ElevenLabs; print('OK')"
```

### Step 2 — Get API key

```bash
# Go to: https://elevenlabs.io/app/settings/api-keys
# Create API Key → copy → add to .env:
echo "ELEVENLABS_API_KEY=sk_your_key_here" >> /docker/openclaw-yyvg/.env

# Verify
curl -s https://api.elevenlabs.io/v1/user \
  -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -m json.tool
```

### Step 3 — Clone voice via Python SDK

```python
from elevenlabs.client import ElevenLabs
import json, os

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

voice = client.voices.ivc.create(
    name="[AGENT_VOICE_NAME]",
    description="[PRINCIPAL_NAME] cloned voice for autonomous agent",
    files=[
        "/workspace/voice/samples/sample_01.mp3",
        "/workspace/voice/samples/sample_02.mp3",
        "/workspace/voice/samples/sample_03.mp3",
    ],
)
print(f"Voice ID: {voice.voice_id}")

# Save to config.json
with open("/workspace/voice/config.json") as f:
    config = json.load(f)
config["ELEVENLABS_VOICE_ID"] = voice.voice_id
with open("/workspace/voice/config.json", "w") as f:
    json.dump(config, f, indent=2)
```

### Step 3 — Clone via curl (alternative)

```bash
# Clone
curl -X POST https://api.elevenlabs.io/v1/voices/add \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "name=[AGENT_VOICE_NAME]" \
  -F "description=[PRINCIPAL_NAME] cloned voice" \
  -F "files=@/workspace/voice/samples/sample_01.mp3" \
  -F "files=@/workspace/voice/samples/sample_02.mp3" \
  -F "files=@/workspace/voice/samples/sample_03.mp3" \
  | python3 -m json.tool

# Extract and save Voice ID
VOICE_ID=$(curl -s -X POST https://api.elevenlabs.io/v1/voices/add \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "name=[AGENT_VOICE_NAME]" \
  -F "files=@/workspace/voice/samples/sample_01.mp3" \
  -F "files=@/workspace/voice/samples/sample_02.mp3" \
  -F "files=@/workspace/voice/samples/sample_03.mp3" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['voice_id'])")

echo "ELEVENLABS_VOICE_ID=$VOICE_ID" >> /docker/openclaw-yyvg/.env
```

### Step 4 — List voices (verify)

```bash
curl -s https://api.elevenlabs.io/v1/voices \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  | python3 -c "
import sys, json
for v in json.load(sys.stdin)['voices']:
    print(f\"{v['voice_id']} | {v['name']} | {v['category']}\")
"
```

### Step 5 — Test the clone

```bash
python3 -c "
from elevenlabs.client import ElevenLabs
import os, json

with open('/workspace/voice/config.json') as f:
    cfg = json.load(f)

client = ElevenLabs(api_key=cfg['ELEVENLABS_API_KEY'])
audio = client.text_to_speech.convert(
    text='Voice clone test successful.',
    voice_id=cfg['ELEVENLABS_VOICE_ID'],
    model_id='eleven_multilingual_v2',
    output_format='mp3_44100_128',
)
with open('/workspace/voice/output/test_clone.mp3', 'wb') as f:
    for chunk in audio:
        f.write(chunk)
print('Test audio saved: /workspace/voice/output/test_clone.mp3')
"
```

### Step 6 — Restart and verify

```bash
cd /docker/openclaw-yyvg && docker compose down && docker compose up -d
python3 /workspace/voice/scripts/voice_generator.py status
```

---

## PATH B — Browser / Dashboard Navigation

### Get API Key

```
1. Go to: https://elevenlabs.io/app/settings/api-keys
2. Click "Create API Key"
3. Name: "[AGENT_VOICE_NAME]-agent"
4. Click "Create" → copy immediately (shown only once)
5. Add to .env: ELEVENLABS_API_KEY=sk_...
```

### Clone Voice

```
1. Go to: https://elevenlabs.io/app/voice-lab
2. Click "Add Voice" → "Voice Clone" → "Instant Voice Clone"
3. Upload 3 MP3 files from /workspace/voice/samples/
4. Name: "[AGENT_VOICE_NAME]"
5. Description: "[PRINCIPAL_NAME] cloned voice"
6. Click "Add Voice" — wait < 30 seconds
7. Click the ⋯ menu on the voice card → "Copy Voice ID"
8. Add to .env: ELEVENLABS_VOICE_ID=...
```

### Create Conversational Agent (optional — for calls)

```
1. Go to: https://elevenlabs.io/app/conversational-ai
2. Click "Create Agent"
3. Name: "[PRINCIPAL_NAME] Sales Agent"
4. Voice: select "[AGENT_VOICE_NAME]"
5. Instructions: paste content from templates/agent_prompt.md
6. Save → copy Agent ID → save to config.json
7. Tab "Phone Numbers" → connect Twilio credentials
```

---

## Troubleshooting

```
401 Unauthorized
  → API key expired → regenerate at /app/settings/api-keys
  → Update .env and restart container

Clone sounds robotic
  → Samples too short or noisy
  → Delete: curl -X DELETE .../v1/voices/$VOICE_ID -H "xi-api-key: $KEY"
  → Record better samples → re-clone

Voice ID not found
  → curl -s .../v1/voices -H "xi-api-key: $KEY" | python3 -m json.tool

Insufficient credits / 403
  → Upgrade plan: https://elevenlabs.io/pricing
  → IVC needs Starter ($5/month) minimum

ffmpeg not found
  → apt-get update && apt-get install -y ffmpeg
```

---

## Quick Reference — API Endpoints

```
Base URL : https://api.elevenlabs.io
Auth     : xi-api-key: YOUR_KEY

GET    /v1/user                 → account + subscription info
GET    /v1/voices               → list all voices
POST   /v1/voices/add           → create IVC clone (multipart)
DELETE /v1/voices/{id}          → delete a voice
POST   /v1/text-to-speech/{id}  → generate audio (JSON body)
GET    /v1/models               → list available models

TTS Models:
  eleven_flash_v2_5        → 75ms latency — real-time / calls
  eleven_multilingual_v2   → best quality — VSL / podcasts
  eleven_v3                → most expressive — storytelling
```
