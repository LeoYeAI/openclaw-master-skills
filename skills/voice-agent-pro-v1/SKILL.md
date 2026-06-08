---
name: voice-agent-pro-v3
description: >
  Gives any OpenClaw agent a complete voice layer via ElevenLabs.
  Clones the principal's voice from audio samples, converts any text
  to MP3 audio (VSL, podcasts, video narrations, nurturing sequences),
  and deploys a conversational AI agent for automated inbound and
  outbound calls via Twilio. Use when the agent needs to generate
  audio content, call leads, or answer prospects 24/7 in the
  principal's cloned voice. Requires ELEVENLABS_API_KEY and
  ELEVENLABS_VOICE_ID — see Setup section in SKILL.md.
version: 3.1.0
author: Wesley Armando (Georges Andronescu)
license: MIT
metadata:
  openclaw:
    emoji: "🎙️"
    security_level: L2
    required_paths:
      read:
        - /workspace/voice/config.json
        - /workspace/voice/scripts/
        - /workspace/voice/samples/
        - /workspace/voice/references/setup_guide.md
        - /workspace/.learnings/LEARNINGS.md
      write:
        - /workspace/voice/config.json
        - /workspace/voice/output/
        - /workspace/voice/calls/
        - /workspace/.learnings/
        - /workspace/AUDIT.md
    network_behavior:
      makes_requests: true
      request_targets:
        - https://api.elevenlabs.io (ElevenLabs REST API — requires ELEVENLABS_API_KEY)
        - https://api.twilio.com (Twilio REST API — optional, requires TWILIO_ACCOUNT_SID)
        - https://api.telegram.org (Telegram Bot API — requires TELEGRAM_BOT_TOKEN)
      uses_agent_telegram: true
    requires.env:
      - TELEGRAM_BOT_TOKEN
      - TELEGRAM_CHAT_ID
      - ELEVENLABS_API_KEY
      - ELEVENLABS_VOICE_ID
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
      - TWILIO_PHONE_NUMBER
---

# Voice Agent Pro V3 — Autonomous Voice Layer

> "The most trusted voice in any room is the one that sounds like you."

This skill gives the principal a voice — their own voice — deployed at scale.

```
LAYER 1 — VOICE SETUP
  Clones the principal's voice from MP3 samples via ElevenLabs API
  Requires ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in .env
  Full setup guide with all commands: references/setup_guide.md

LAYER 2 — TEXT TO SPEECH
  Converts any text to MP3 using the principal's cloned voice
  VSL scripts, podcast intros, video narrations, email audio versions

LAYER 3 — CONVERSATIONAL AGENT (with Twilio)
  Outbound calls to leads — automated follow-up
  Inbound calls — answers 24/7, qualifies, reports
```

---

## SETUP — Required Before First Use

### Step 1 — Install dependencies

The agent runs these commands **inside the OpenClaw container**.
If you prefer to run them manually from your VPS host, use:
`docker exec openclaw-yyvg-openclaw-1 pip install elevenlabs --break-system-packages`

```bash
# Inside the container (agent runs this directly)
pip install elevenlabs --break-system-packages
pip install twilio --break-system-packages
apt-get update && apt-get install -y ffmpeg

# Verify
ffmpeg -version | head -1
python3 -c "from elevenlabs.client import ElevenLabs; print('✅ SDK ready')"
```

> Note: `--break-system-packages` is required on Ubuntu 24.04 / Debian 12+
> containers. If you get an "externally-managed-environment" error, this
> flag resolves it. On older systems, plain `pip install elevenlabs` works.

### Step 2 — Access ElevenLabs

```
OPTION A — Via virtual-desktop (if installed)
  If the virtual-desktop skill is installed and a Google session
  is active in the browser, the agent can navigate elevenlabs.io
  and create the API key automatically:
  → Go to: https://elevenlabs.io/app/sign-in
  → Click "Continue with Google" (uses active session)
  → Navigate: Developers → API Keys → Create API Key
  → Copy the key and run apply-config (Step 6)

OPTION B — Manual (recommended for first setup)
  → Go to: https://elevenlabs.io/app/settings/api-keys
  → Click "Create API Key" → name it → copy it
  → Add to your agent .env file: ELEVENLABS_API_KEY=sk_...
```

```bash
# Verify it works
curl -s https://api.elevenlabs.io/v1/user \
  -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -m json.tool
# Expected: JSON with subscription info — if 401, key is wrong
```

### Step 3 — Clone your voice

Provide 3 MP3 files of your voice (30-60 seconds each, clear audio)
in `/workspace/voice/samples/` before running this step.

#### Via Python SDK

```python
from elevenlabs.client import ElevenLabs
import json, os

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
voice = client.voices.ivc.create(
    name="[AGENT_VOICE_NAME]",
    description="[PRINCIPAL_NAME] cloned voice",
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
print("✅ Voice ID saved to config.json")
```

#### Via curl

```bash
VOICE_ID=$(curl -s -X POST https://api.elevenlabs.io/v1/voices/add \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "name=[AGENT_VOICE_NAME]" \
  -F "description=[PRINCIPAL_NAME] cloned voice" \
  -F "files=@/workspace/voice/samples/sample_01.mp3" \
  -F "files=@/workspace/voice/samples/sample_02.mp3" \
  -F "files=@/workspace/voice/samples/sample_03.mp3" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['voice_id'])")

echo "Voice ID: $VOICE_ID"
# Add to your agent .env: ELEVENLABS_VOICE_ID=$VOICE_ID
```

### Step 4 — List voices (verify clone)

```bash
curl -s https://api.elevenlabs.io/v1/voices \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  | python3 -c "
import sys, json
for v in json.load(sys.stdin)['voices']:
    print(f"{v['voice_id']} | {v['name']} | {v['category']}")
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
import os; os.makedirs('/workspace/voice/output', exist_ok=True)
with open('/workspace/voice/output/test_clone.mp3', 'wb') as f:
    for chunk in audio:
        f.write(chunk)
print('✅ Test audio: /workspace/voice/output/test_clone.mp3')
"
```

### Step 6 — Apply config and verify

```bash
# Apply credentials to config.json (no container restart needed)
python3 /workspace/voice/scripts/voice_generator.py apply-config \
  --api-key "$ELEVENLABS_API_KEY" \
  --voice-id "$ELEVENLABS_VOICE_ID"

# Verify everything is ready
python3 /workspace/voice/scripts/voice_generator.py status
# Expected:
#   API Key:    ✅ configured
#   Voice ID:   ✅ abc123...
```

> The skill reads credentials from config.json at runtime —
> no container restart needed after updating credentials.

> For browser dashboard navigation guide (step-by-step with screenshots):
> `references/setup_guide.md`

---

## PHASE 1 — TEXT TO SPEECH

Converts any text to audio using the principal's cloned voice.

### Use Cases

```
VSL (Video Sales Letter)
  Input:  /workspace/voice/scripts/vsl_[offer].md
  Output: /workspace/voice/output/vsl_[offer].mp3
  Use:    record your VSL once — never again

PODCAST INTRO / OUTRO
  Input:  /workspace/voice/scripts/podcast_[episode].md
  Output: /workspace/voice/output/podcast_[episode].mp3

VIDEO NARRATION
  Input:  text from content-creator-pro queue
  Output: MP3 ready for CapCut / video editor

EMAIL AUDIO VERSION
  Input:  email text from acquisition-master sequences
  Output: MP3 attached or linked in email

SOCIAL AUDIO CLIPS
  Input:  hook text from content-creator-pro
  Output: 15-30 second MP3 for Instagram, Twitter Spaces
```

### TTS Models

```
eleven_flash_v2_5        → 75ms latency — use for real-time / calls
eleven_multilingual_v2   → best quality — use for VSL / podcasts
eleven_v3                → most expressive — use for storytelling content
```

### TTS Process

```
1. Read script from /workspace/voice/scripts/[name].md
2. Split into chunks of max 900 characters (sentence boundaries)
3. Call ElevenLabs TTS API for each chunk
4. Concatenate chunks with ffmpeg → single MP3
5. Save to /workspace/voice/output/[name].mp3
6. Log to AUDIT.md: "TTS generated: [name].mp3 — [duration]s"
7. Notify principal via Telegram with file path
```

### CLI Usage

```bash
# Generate from text
python3 /workspace/voice/scripts/voice_generator.py tts \
  --text "Hello, this is [PRINCIPAL_NAME]." \
  --output /workspace/voice/output/hello.mp3

# Generate from script file
python3 /workspace/voice/scripts/voice_generator.py tts \
  --script /workspace/voice/scripts/vsl_offer.md \
  --model eleven_multilingual_v2

# Check status
python3 /workspace/voice/scripts/voice_generator.py status
```

---

## PHASE 2 — CONVERSATIONAL CALLS (requires Twilio)

### Setup Twilio

```bash
# Add to your agent .env file:
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Twilio account: console.twilio.com
# Phone number: ~$1/month
```

### Connect Twilio to ElevenLabs Agent

```
1. Go to: https://elevenlabs.io/app/conversational-ai
2. Click "Create Agent"
3. Name: "[PRINCIPAL_NAME] Sales Agent"
4. Voice: select "[AGENT_VOICE_NAME]"
5. Agent instructions: paste content from templates/agent_prompt.md
6. Save → copy Agent ID → save to config.json
7. Tab "Phone Numbers" → "Add Phone Number"
8. Enter TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN
9. Select TWILIO_PHONE_NUMBER
10. ElevenLabs configures Twilio automatically
```

### Outbound Calls — Lead Follow-up

```
Triggered by:
  → acquisition-master: lead didn't open email after 3 days
  → funnel-builder: lead clicked pricing page but didn't buy
  → Manual: principal requests call to specific number

Call flow:
  1. Agent reads lead data from /workspace/voice/calls/pending/
  2. Personalizes call script with lead name + context
  3. Initiates outbound call via ElevenLabs + Twilio
  4. Conversation in real-time (principal's cloned voice)
  5. Transcript saved to /workspace/voice/calls/history/
  6. Outcome: interested / not_interested / callback / voicemail
  7. Telegram notification with transcript summary

Call schedule: Mon-Fri 9h-19h only
Max voicemails: 1 per lead per week
```

### Inbound Calls — 24/7 Qualification

```
When someone calls the Twilio number:
  → Agent answers in principal's cloned voice
  → 3 qualification questions:
    Q1: "What's your current situation with [niche problem]?"
    Q2: "Have you tried to solve this before?"
    Q3: "What would your ideal outcome look like?"
  → Score 8-10: hot lead → books call via Calendly
  → Score 5-7:  warm lead → sends free resource by SMS
  → Score 1-4:  cold lead → polite close
  → Transcript + score → /workspace/voice/calls/history/
  → Telegram: "📞 Inbound call — [score]/10 — [summary]"
```

### Qualification Scoring

```
Score 8-10 → hot lead → immediate Telegram alert to principal
Score 5-7  → warm lead → add to nurture sequence
Score 1-4  → cold lead → send free resource, no follow-up 30 days
```

### Call CLI

```bash
# List pending calls
python3 /workspace/voice/scripts/voice_generator.py calls --action list

# Weekly call summary
python3 /workspace/voice/scripts/voice_generator.py calls --action summary
```

---

## Troubleshooting Voice Clone

```
PROBLEM: "Insufficient credits" / 403 error
  Solution: Check plan at elevenlabs.io/app/subscription
  IVC requires Starter ($5/month) minimum
  Action: upgrade at https://elevenlabs.io/pricing

PROBLEM: Clone sounds robotic or wrong
  Causes:
  → Audio files too short (< 30 seconds each)
  → Background noise in samples
  → Multiple speakers in same file
  Solution:
  → Delete the bad clone:
    curl -X DELETE https://api.elevenlabs.io/v1/voices/$VOICE_ID \
      -H "xi-api-key: $ELEVENLABS_API_KEY"
  → Record better samples (quieter, longer, more natural)
  → Re-run cloning

PROBLEM: Voice ID not found when calling TTS
  Solution:
    curl -s https://api.elevenlabs.io/v1/voices \
      -H "xi-api-key: $ELEVENLABS_API_KEY" \
      | python3 -m json.tool | grep -A2 "[AGENT_VOICE_NAME]"

PROBLEM: "Invalid API key" (401 on all requests)
  Solution: Regenerate at https://elevenlabs.io/app/settings/api-keys
  Update .env and restart agent container

PROBLEM: ffmpeg not found
  Solution: apt-get update && apt-get install -y ffmpeg
  Verify: ffmpeg -version
```

---

## Quick Reference — API Endpoints

```
Base URL : https://api.elevenlabs.io
Auth     : xi-api-key: YOUR_KEY

GET    /v1/user                 → account + subscription info
GET    /v1/voices               → list all voices
POST   /v1/voices/add           → create IVC clone (multipart form)
DELETE /v1/voices/{id}          → delete a voice
POST   /v1/text-to-speech/{id}  → generate audio (JSON body)
GET    /v1/models               → list available models
```

---

## Installation & Setup

### What You Need to Provide

```
MINIMUM (TTS only):
  ELEVENLABS_API_KEY    → elevenlabs.io → Developers → API Keys
  ELEVENLABS_VOICE_ID   → created after voice cloning (see Step 3)
  3 MP3 voice samples   → /workspace/voice/samples/ (30-60s each)

FOR CALLS (add):
  TWILIO_ACCOUNT_SID    → console.twilio.com
  TWILIO_AUTH_TOKEN     → console.twilio.com
  TWILIO_PHONE_NUMBER   → buy a number on Twilio (~$1/month)

AGENT ALREADY HAS:
  TELEGRAM_BOT_TOKEN    → already in your agent .env
  TELEGRAM_CHAT_ID      → already in your agent .env
```

### Voice Sample Requirements

```
Minimum : 1 file × 30 seconds
Recommended : 3 files × 1-2 minutes each
Optimal (Professional Clone) : 30+ minutes total

Quality:
  → Clear voice, no background noise
  → Natural speech rhythm
  → Consistent microphone distance
  → Format: MP3, WAV, M4A, FLAC all accepted
  → No multiple speakers in same file

ElevenLabs plan required:
  IVC (Instant Voice Clone) : Starter plan ($5/month)
  PVC (Professional, hyper-realistic) : Creator plan ($22/month)
```

### Setup Checklist

```
[ ] pip install elevenlabs --break-system-packages
[ ] pip install twilio --break-system-packages (if using calls)
[ ] apt-get update && apt-get install -y ffmpeg
[ ] 3 MP3 samples uploaded to /workspace/voice/samples/
[ ] ELEVENLABS_API_KEY added to agent .env
[ ] ELEVENLABS_VOICE_ID added to agent .env (after cloning)
[ ] python3 voice_generator.py apply-config --api-key ... --voice-id ...
[ ] voice_generator.py status shows ✅ API Key and Voice ID
[ ] Test TTS successful (output MP3 plays correctly)
[ ] (Optional) Twilio credentials added for calls
```

### Cron Schedule

```
# Outbound follow-up calls — Mon-Fri 10h
0 10 * * 1-5   voice-agent-pro-v3 → process /workspace/voice/calls/pending/

# Weekly VSL refresh — Sunday 11h
0 11 * * 0     voice-agent-pro-v3 → regenerate VSLs if scripts updated

# Call transcript review — Monday 9h
0 9 * * 1      python3 /workspace/voice/scripts/voice_generator.py calls --action summary
```

---

## Files Written By This Skill

| File | Frequency | Content |
|---|---|---|
| `/workspace/voice/config.json` | Once (setup) | API keys, Voice ID, Agent ID |
| `/workspace/voice/output/*.mp3` | Per generation | Generated audio files |
| `/workspace/voice/calls/pending/*.json` | Per lead | Calls to make |
| `/workspace/voice/calls/history/*.json` | Per call | Transcript + outcome + score |
| `/workspace/.learnings/LEARNINGS.md` | Weekly | Call patterns, best scripts |
| `/workspace/.learnings/ERRORS.md` | On error | API errors, setup failures |
| `/workspace/AUDIT.md` | On event | TTS generated, calls made, alerts |

---

## Workspace Structure

```
/workspace/voice/
├── config.json           ← API keys + Voice ID (from templates/config.json)
├── samples/              ← MP3 voice samples (you provide, 30-60s each)
│   ├── sample_01.mp3
│   ├── sample_02.mp3
│   └── sample_03.mp3
├── scripts/              ← Text scripts to convert to audio
│   └── [name].md
├── output/               ← Generated MP3 files
│   └── [name].mp3
├── calls/
│   ├── pending/          ← Calls to make (written by acquisition-master)
│   │   └── [lead_id].json
│   └── history/          ← Completed call transcripts
│       └── [date]-[lead_id].json
└── references/
    └── setup_guide.md    ← Full setup commands + browser dashboard guide
```

---

## Constraints

```
❌ Never store voice samples outside /workspace/voice/samples/
❌ Never use the cloned voice to impersonate anyone other than the principal
❌ Never make calls outside working hours (9h-19h Mon-Fri)
❌ Never leave more than 1 voicemail per lead per week
❌ Never fabricate call transcripts or outcomes
✅ Always log every call with transcript to calls/history/
✅ Always notify principal when a hot lead (score 8+) calls
✅ Always respect lead's request to not be contacted again
✅ If ELEVENLABS_API_KEY missing → log to ERRORS.md, notify principal
✅ If voice samples missing → pause cloning, notify principal
✅ Consent: only clone and use the voice of the principal with explicit consent
```

---

## Error Handling

```
ERROR: ELEVENLABS_API_KEY invalid or missing
  Action: Verify at https://elevenlabs.io/app/settings/api-keys
  Log: ERRORS.md → "API key invalid [date] — check agent .env"

ERROR: Voice samples missing
  Action: Do NOT attempt voice cloning
  Notify: via Telegram → "Upload 3 MP3 samples to /workspace/voice/samples/"
  Log: AUDIT.md → "Voice setup paused — samples missing"

ERROR: API rate limit hit (429)
  Action: Wait 60 seconds, retry once
  If still failing: queue job for next hour
  Log: ERRORS.md → "Rate limit hit — job queued [date]"

ERROR: Twilio call fails
  Action: Log failure, mark lead as call_failed in pending/
  Retry: next day same time slot
  Log: ERRORS.md → "Call failed: [lead_id] — [error] [date]"

ERROR: ffmpeg not found
  Action: apt-get update && apt-get install -y ffmpeg
  Log: ERRORS.md → "ffmpeg missing — install attempted [date]"

ERROR: ELEVENLABS_VOICE_ID not set
  Action: Run voice cloning (Step 3 in Setup section above)
  Log: AUDIT.md → "Voice ID missing — cloning required"
```
