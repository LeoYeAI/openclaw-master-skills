---
name: voice-agent
description: >
  Gives the agent a complete voice layer using ElevenLabs. Clones the
  principal's voice, generates MP3 audio from any text (VSL, podcasts,
  video scripts, nurturing sequences), and deploys a conversational AI
  agent for automated inbound and outbound calls via Twilio. Self-configures
  by navigating elevenlabs.io autonomously via virtual-desktop — no manual
  API key setup required. Use when the agent needs to speak, call leads,
  answer prospects, or produce audio content at scale.
version: 1.0.0
author: Wesley Armando (Georges Andronescu)
license: MIT
metadata:
  openclaw:
    emoji: "🎙️"
    security_level: L2
    always: false
    required_paths:
      read:
        - /workspace/voice/config.json
        - /workspace/voice/scripts/
        - /workspace/voice/samples/
        - /workspace/.learnings/LEARNINGS.md
      write:
        - /workspace/voice/config.json
        - /workspace/voice/scripts/
        - /workspace/voice/output/
        - /workspace/voice/calls/
        - /workspace/.learnings/LEARNINGS.md
        - /workspace/.learnings/ERRORS.md
        - /workspace/AUDIT.md
    network_behavior:
      makes_requests: true
      request_targets:
        - https://elevenlabs.io (dashboard navigation via virtual-desktop)
        - https://api.elevenlabs.io (ElevenLabs REST API — requires ELEVENLABS_API_KEY)
        - https://api.twilio.com (Twilio API — optional, requires TWILIO credentials)
      uses_agent_telegram: true
      telegram_note: >
        Notifies principal when voice clone is ready, audio file generated,
        or call completed. Reports call transcripts and outcomes.
    always: false
    requires:
      skills:
        - virtual-desktop
      optional_skills:
        - acquisition-master
        - funnel-builder
      bins:
        - python3
        - ffmpeg
---

# Voice Agent — Autonomous Voice Layer for Wesley

> "The most trusted voice in any room is the one that sounds like you."

The agent doesn't just write content. It speaks it.
This skill gives Wesley a voice — his own voice — deployed at scale.

---

## What This Skill Does

```
LAYER 1 — VOICE SETUP (self-configuring)
  Navigates elevenlabs.io autonomously via virtual-desktop
  Logs in via Google OAuth or email/password
  Creates API key, clones voice, configures agent
  Writes all credentials to .env automatically

LAYER 2 — TEXT TO SPEECH
  Converts any text to MP3 using Wesley's cloned voice
  VSL scripts, podcast intros, video narrations
  Email audio versions, social audio clips

LAYER 3 — CONVERSATIONAL AGENT (with Twilio)
  Outbound calls to leads — automated follow-up
  Inbound calls — answers 24/7, qualifies, reports
  Natural turn-taking, handles objections, books calls
```

---

## PHASE 1 — SELF-CONFIGURATION

The agent runs this phase automatically on first use.
It uses virtual-desktop to navigate ElevenLabs and retrieve its own credentials.

### Step 1 — Login Detection

```
The agent checks /workspace/voice/config.json for existing credentials.

IF ELEVENLABS_API_KEY already in config.json:
  → Skip to Phase 2 (already configured)

IF NOT configured:
  → Run the self-configuration sequence below
```

### Step 2 — Connect to ElevenLabs

```
OPTION A — Google OAuth (preferred — zero credentials required)
  Condition: virtual-desktop has an active Google session

  Process:
  1. virtual-desktop opens https://elevenlabs.io/app/sign-in
  2. Clicks "Continue with Google"
  3. Google session is already active in the browser
  4. ElevenLabs dashboard loads automatically
  5. Proceed to API key creation

OPTION B — Email / Password
  Condition: ELEVENLABS_EMAIL and ELEVENLABS_PASSWORD in .env

  Process:
  1. virtual-desktop opens https://elevenlabs.io/app/sign-in
  2. Fills email field with ELEVENLABS_EMAIL
  3. Fills password field with ELEVENLABS_PASSWORD
  4. Clicks "Sign in"
  5. ElevenLabs dashboard loads
  6. Proceed to API key creation

FALLBACK — Manual
  If neither option works:
  Log to AUDIT.md: "ElevenLabs login failed — manual setup required"
  Notify principal via Telegram with exact steps to follow
```

### Step 3 — Create API Key

```
Navigation path (2026 ElevenLabs UI):
  Dashboard → bottom-left corner → "Developers"
  → Tab "API Keys"
  → Button "Create API Key"
  → Name: "wesley-agent"
  → Click "Create"
  → Copy the generated key (shown only once)
  → Write to /workspace/voice/config.json:
    { "ELEVENLABS_API_KEY": "sk_..." }
  → Also write to .env:
    ELEVENLABS_API_KEY=sk_...
```

### Step 4 — Clone the Voice

```
Requires: 3 MP3 files in /workspace/voice/samples/
  Minimum: 30 seconds each, clear audio, no background noise
  Optimal: 3-5 minutes total, varied sentences

Navigation path:
  Dashboard → "Voices" → "Add Voice"
  → "Voice Clone" → "Instant Voice Clone"
  → Upload files from /workspace/voice/samples/
  → Name: "Wesley"
  → Click "Create Voice Clone"
  → Wait for processing (usually < 30 seconds)
  → Copy the Voice ID from the voice card
  → Write to config.json: { "ELEVENLABS_VOICE_ID": "abc123..." }

IF no MP3 files in /workspace/voice/samples/:
  → Log to AUDIT.md: "Voice samples missing"
  → Notify principal via Telegram:
    "To clone your voice, record 3 audio clips of 30-60 seconds each
     (read any text naturally), save as MP3, and upload to
     /workspace/voice/samples/
     Then run voice-agent again."
  → Pause and wait for samples
```

### Step 5 — Create Conversational Agent (optional — for calls)

```
Only runs if TWILIO_ACCOUNT_SID is in .env

Navigation path:
  Dashboard → "Agents" → "Create Agent"
  → Name: "Wesley Sales Agent"
  → Voice: select "Wesley" (the cloned voice)
  → System prompt: read from /workspace/voice/templates/agent_prompt.md
  → Save → Copy Agent ID
  → Write to config.json: { "ELEVENLABS_AGENT_ID": "agent_..." }

Then connect Twilio:
  Dashboard → "Agents" → select "Wesley Sales Agent"
  → "Phone Numbers" tab → "Add Phone Number"
  → Enter TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN
  → Select TWILIO_PHONE_NUMBER
  → ElevenLabs configures Twilio automatically
  → Write to config.json: { "TWILIO_CONFIGURED": true }
```

### Configuration Complete

```
When all steps are done, config.json contains:
{
  "ELEVENLABS_API_KEY": "sk_...",
  "ELEVENLABS_VOICE_ID": "...",
  "ELEVENLABS_AGENT_ID": "...",     ← if Twilio configured
  "TWILIO_CONFIGURED": true,         ← if Twilio configured
  "setup_date": "YYYY-MM-DD",
  "voice_name": "Wesley"
}

Telegram notification:
"🎙️ Voice Agent configured and ready.
 Voice: Wesley (cloned)
 TTS: active
 Calls: [active / not configured]"
```

---

## VOICE CLONING — Complete Reference

This section gives the agent every command and navigation step
needed to clone the principal's voice. Two paths available —
use whichever fits the context.

---

### What You Need Before Starting

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

### PATH A — Terminal / API (fastest — no browser needed)

Use this path when ELEVENLABS_API_KEY is already in config.json.
The agent calls the API directly without virtual-desktop.

#### Step 1 — Install the SDK

```bash
pip install elevenlabs --break-system-packages
pip install requests --break-system-packages
```

#### Step 2 — Verify API key works

```bash
curl -s https://api.elevenlabs.io/v1/user   -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -m json.tool
# Expected: JSON with subscription info
# If 401 error: API key is wrong or expired
```

#### Step 3 — Clone the voice via Python SDK

```python
from elevenlabs.client import ElevenLabs
import json, os

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

# Create Instant Voice Clone
voice = client.voices.ivc.create(
    name="Wesley",
    description="Wesley Armando — principal voice for autonomous agent",
    files=[
        "/workspace/voice/samples/sample_01.mp3",
        "/workspace/voice/samples/sample_02.mp3",
        "/workspace/voice/samples/sample_03.mp3",
    ],
)

print(f"Voice ID: {voice.voice_id}")
print(f"Name: {voice.name}")

# Save to config.json
config_path = "/workspace/voice/config.json"
with open(config_path) as f:
    config = json.load(f)
config["ELEVENLABS_VOICE_ID"] = voice.voice_id
config["voice_name"] = voice.name
with open(config_path, "w") as f:
    json.dump(config, f, indent=2)

print(f"✅ Voice ID saved to config.json")
```

#### Step 3 — Clone via curl (alternative)

```bash
# Clone with multiple files
curl -X POST https://api.elevenlabs.io/v1/voices/add   -H "xi-api-key: $ELEVENLABS_API_KEY"   -F "name=Wesley"   -F "description=Wesley Armando principal voice"   -F "files=@/workspace/voice/samples/sample_01.mp3"   -F "files=@/workspace/voice/samples/sample_02.mp3"   -F "files=@/workspace/voice/samples/sample_03.mp3"   | python3 -m json.tool

# Response contains:
# { "voice_id": "abc123...", "name": "Wesley" }

# Extract and save the voice_id
VOICE_ID=$(curl -s -X POST https://api.elevenlabs.io/v1/voices/add   -H "xi-api-key: $ELEVENLABS_API_KEY"   -F "name=Wesley"   -F "files=@/workspace/voice/samples/sample_01.mp3"   -F "files=@/workspace/voice/samples/sample_02.mp3"   -F "files=@/workspace/voice/samples/sample_03.mp3"   | python3 -c "import sys,json; print(json.load(sys.stdin)['voice_id'])")

echo "Voice ID: $VOICE_ID"

# Write to .env
echo "ELEVENLABS_VOICE_ID=$VOICE_ID" >> /docker/openclaw-yyvg/.env
echo "✅ ELEVENLABS_VOICE_ID written to .env"
```

#### Step 4 — List all voices (verify clone appears)

```bash
# Via curl
curl -s https://api.elevenlabs.io/v1/voices   -H "xi-api-key: $ELEVENLABS_API_KEY"   | python3 -c "
import sys, json
data = json.load(sys.stdin)
for v in data['voices']:
    print(f"{v['voice_id']} | {v['name']} | {v['category']}")
"

# Via Python SDK
python3 -c "
from elevenlabs.client import ElevenLabs
import os
client = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])
resp = client.voices.search()
for v in resp.voices:
    print(f'{v.voice_id} | {v.name} | {v.category}')
"
```

#### Step 5 — Test the cloned voice

```bash
# Generate a test MP3 with the cloned voice
python3 -c "
from elevenlabs.client import ElevenLabs
import os, json

with open('/workspace/voice/config.json') as f:
    cfg = json.load(f)

client = ElevenLabs(api_key=cfg['ELEVENLABS_API_KEY'])
audio = client.text_to_speech.convert(
    text='Hello, this is Wesley. Voice clone test successful.',
    voice_id=cfg['ELEVENLABS_VOICE_ID'],
    model_id='eleven_multilingual_v2',
    output_format='mp3_44100_128',
)
with open('/workspace/voice/output/test_clone.mp3', 'wb') as f:
    for chunk in audio:
        f.write(chunk)
print('✅ Test audio saved: /workspace/voice/output/test_clone.mp3')
"
```

---

### PATH B — Browser Navigation via virtual-desktop

Use this path when API key is not yet available.
The agent uses virtual-desktop + Playwright to navigate the dashboard.

#### Step 1 — Login

```
virtual-desktop opens: https://elevenlabs.io/app/sign-in

OPTION A (Google OAuth):
  → Wait for page to load
  → Click button: "Continue with Google"
  → Google session auto-completes the login
  → Dashboard loads at: https://elevenlabs.io/app/home

OPTION B (Email + Password):
  → Find input: [placeholder="Email address"] or [type="email"]
  → Fill: os.environ["ELEVENLABS_EMAIL"]
  → Find input: [type="password"]
  → Fill: os.environ["ELEVENLABS_PASSWORD"]
  → Click button: "Sign in"
  → Dashboard loads

VERIFY LOGIN:
  → URL should contain: elevenlabs.io/app/
  → If login fails: log to ERRORS.md, notify principal
```

#### Step 2 — Get API Key from dashboard

```
Navigation path (2026 UI):
  1. Look bottom-left corner for "Developers" or username icon
  2. Click "Developers"
  3. Click tab: "API Keys"
  4. Click button: "Create API Key"
  5. In modal: type name "wesley-agent"
  6. Click "Create"
  7. Copy the displayed key (SHOWN ONLY ONCE)
     → Use Playwright: page.locator('[data-testid="api-key"]').inner_text()
     → Or: find input with type="password" that appears after creation
  8. Save immediately:
     → Write to /workspace/voice/config.json
     → Write to /docker/openclaw-yyvg/.env as ELEVENLABS_API_KEY=sk_...

  Direct URL shortcut: https://elevenlabs.io/app/settings/api-keys
```

#### Step 3 — Create Voice Clone from dashboard

```
Navigation path:
  1. Click left sidebar: "Voices" (or go to /app/voice-lab)
  2. Click button: "Add Voice"
  3. Click: "Voice Clone"
  4. Click: "Instant Voice Clone"
  5. Upload files:
     → Drag and drop from /workspace/voice/samples/
     → Or click "Upload" and select all 3 MP3 files
  6. Fill field "Name": "Wesley"
  7. Fill field "Description": "Wesley Armando principal voice"
  8. Click: "Add Voice"
  9. Wait for processing bar (usually < 30 seconds)
  10. Click on the new "Wesley" voice card
  11. Copy the Voice ID:
      → Click the three-dot menu "⋯" on the voice card
      → Click "Copy Voice ID"
      → Or find in URL: elevenlabs.io/app/voice-lab/[VOICE_ID]
  12. Save to config.json + .env

  Direct URL shortcut: https://elevenlabs.io/app/voice-lab
```

#### Step 4 — Verify in dashboard

```
After cloning:
  → Go to: https://elevenlabs.io/app/voice-lab
  → Locate "Wesley" in the voice list
  → Click "Use" to test with a text sample
  → If it sounds like the principal → success
  → Click the ⋯ menu → "Copy Voice ID" → save to config.json
```

---

### Troubleshooting Voice Clone

```
PROBLEM: "Insufficient credits" error
  Solution: Check plan at elevenlabs.io/app/subscription
  IVC requires Starter ($5/month) minimum
  Action: upgrade plan via dashboard → Subscription

PROBLEM: Clone sounds robotic or wrong
  Causes:
  → Audio files too short (< 30 seconds each)
  → Background noise in samples
  → Multiple speakers in same file
  Solution:
  → Delete the bad clone: DELETE /v1/voices/{voice_id}
    curl -X DELETE https://api.elevenlabs.io/v1/voices/$VOICE_ID       -H "xi-api-key: $ELEVENLABS_API_KEY"
  → Record new samples (quieter environment, longer duration)
  → Re-run cloning process

PROBLEM: Voice ID not found when calling TTS
  Solution: List all voices and find correct ID
    curl -s https://api.elevenlabs.io/v1/voices       -H "xi-api-key: $ELEVENLABS_API_KEY"       | python3 -m json.tool | grep -A2 "Wesley"

PROBLEM: "Invalid API key" (401)
  Solution: Regenerate key in dashboard
  Direct URL: https://elevenlabs.io/app/settings/api-keys
  Update config.json and .env with new key

PROBLEM: ffmpeg not found for audio concatenation
  Solution:
    apt-get update && apt-get install -y ffmpeg
  Verify: ffmpeg -version
```

---

### Quick Reference — API Endpoints

```
GET  /v1/user               → check account + subscription
GET  /v1/voices             → list all voices
POST /v1/voices/add         → create IVC clone (multipart form)
GET  /v1/voices/{id}        → get voice details
DELETE /v1/voices/{id}      → delete a voice
POST /v1/text-to-speech/{id} → generate audio (JSON body)
GET  /v1/models             → list available models

Base URL: https://api.elevenlabs.io
Auth header: xi-api-key: YOUR_KEY
```


---

## PHASE 2 — TEXT TO SPEECH

Converts any text to audio using Wesley's cloned voice.

### Use Cases

```
VSL (Video Sales Letter)
  Input:  /workspace/voice/scripts/vsl_[offer].md
  Output: /workspace/voice/output/vsl_[offer].mp3
  Use:    record your VSL once, never again

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
  Output: 15-30 second MP3 for Twitter Spaces, Instagram
```

### TTS Models

```
eleven_flash_v2_5  → latency 75ms — use for real-time / calls
eleven_multilingual_v2 → best quality — use for VSL / podcasts
eleven_v3          → most expressive — use for storytelling content
```

### TTS Process

```
1. Read script from /workspace/voice/scripts/[name].md
2. Split into chunks of max 1,000 characters
   (optimal for quality and rate limits)
3. Call ElevenLabs TTS API for each chunk
4. Concatenate with ffmpeg → single MP3
5. Save to /workspace/voice/output/[name].mp3
6. Log to AUDIT.md: "TTS generated: [name].mp3 — [duration]s"
7. Notify principal via Telegram with file path
```

---

## PHASE 3 — CONVERSATIONAL CALLS (requires Twilio)

### Outbound Calls — Lead Follow-up

```
Triggered by:
  → acquisition-master: lead didn't open email after 3 days
  → funnel-builder: lead clicked pricing page but didn't buy
  → Manual: principal requests call to specific number

Call flow:
  1. Agent reads lead data from /workspace/voice/calls/pending/
  2. Personalizes the call script with lead name + context
  3. Initiates outbound call via ElevenLabs + Twilio
  4. Conversation happens in real-time (Wesley's cloned voice)
  5. Transcript saved to /workspace/voice/calls/history/
  6. Outcome logged: interested / not_interested / callback / voicemail
  7. Telegram notification with transcript summary

Call script logic:
  → Warm opening (uses lead's first name)
  → Reference to their specific action (email click, page visit)
  → One clear question: "Are you still interested in [X]?"
  → If yes → book a call via Calendly link (sent by SMS after)
  → If no  → polite close, tag as cold in funnel
  → If voicemail → leave 20s message, follow up by email
```

### Inbound Calls — 24/7 Qualification

```
When someone calls the Twilio number:
  → ElevenLabs agent answers in Wesley's voice
  → Asks 3 qualification questions:
    1. "What's your current situation with [niche problem]?"
    2. "Have you tried to solve this before?"
    3. "What would your ideal outcome look like?"
  → If qualified → books call via Calendly
  → If not qualified → sends free resource by SMS
  → Transcript + qualification score → /workspace/voice/calls/history/
  → Telegram alert: "📞 Inbound call — [score]/10 — [summary]"
```

### Call Qualification Scoring

```
Score 8-10 → hot lead → immediate Telegram alert to principal
Score 5-7  → warm lead → add to nurture sequence
Score 1-4  → cold lead → send free resource, no follow-up for 30 days
```

---

## Workspace Structure

```
/workspace/voice/
├── config.json           ← API keys + Voice ID (auto-written by agent)
├── samples/              ← MP3 voice samples for cloning (you provide)
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
└── templates/
    └── agent_prompt.md   ← System prompt for the conversational agent
```

---

## Installation & Setup

### What You Need to Provide

```
MINIMUM (TTS only — no calls):
  Option A: Google account connected in virtual-desktop browser
  Option B: ELEVENLABS_EMAIL + ELEVENLABS_PASSWORD in .env
  + 3 MP3 voice samples in /workspace/voice/samples/

FOR CALLS (add Twilio):
  TWILIO_ACCOUNT_SID   → console.twilio.com → Account Info
  TWILIO_AUTH_TOKEN    → console.twilio.com → Account Info
  TWILIO_PHONE_NUMBER  → buy a number on Twilio (~$1/month)

WHAT THE AGENT RETRIEVES AUTOMATICALLY:
  ELEVENLABS_API_KEY   → created by agent on elevenlabs.io
  ELEVENLABS_VOICE_ID  → created after uploading your samples
  ELEVENLABS_AGENT_ID  → created if Twilio credentials present
```

### Bootstrap Instructions

```
1. Choose your login method:
   Option A: ensure Google is connected in virtual-desktop
   Option B: add to .env:
     ELEVENLABS_EMAIL=your@email.com
     ELEVENLABS_PASSWORD=yourpassword

2. Record 3 voice samples:
   → Read any text naturally, 30-60 seconds each
   → Save as MP3 (any quality works for IVC)
   → Upload to /workspace/voice/samples/

3. (Optional) Add Twilio credentials to .env for calls

4. Run voice-agent — it configures itself automatically

5. Test TTS:
   python3 /workspace/voice/scripts/voice_generator.py tts \
     --text "Hello, this is Wesley." --output test.mp3
```

### Setup Checklist

```
[ ] Login method ready (Google OAuth or email/password)
[ ] 3 MP3 samples uploaded to /workspace/voice/samples/
[ ] virtual-desktop skill installed
[ ] ffmpeg available on container (ffmpeg --version)
[ ] python3 available (python3 --version)
[ ] pip install elevenlabs --break-system-packages
[ ] pip install twilio --break-system-packages (optional)
[ ] First run completed — config.json populated
[ ] Test TTS successful — output MP3 plays correctly
[ ] (Optional) Twilio credentials added for call capability
```

### Cron Schedule

```
# Daily outbound follow-up calls — 10h (working hours only)
0 10 * * 1-5   voice-agent → process /workspace/voice/calls/pending/

# Weekly VSL refresh — every Sunday 11h
0 11 * * 0     voice-agent → regenerate VSLs if scripts updated

# Call transcript review — every Monday 9h
0 9 * * 1      voice-agent → summarize week's calls to AUDIT.md
```

---

## Files Written By This Skill

| File | Frequency | Content |
|---|---|---|
| `/workspace/voice/config.json` | Once (setup) | API keys, Voice ID, Agent ID |
| `/workspace/voice/output/*.mp3` | Per generation | Generated audio files |
| `/workspace/voice/calls/history/*.json` | Per call | Transcript + outcome + score |
| `/workspace/.learnings/LEARNINGS.md` | Weekly | Call patterns, best scripts |
| `/workspace/.learnings/ERRORS.md` | On error | Login failures, API errors |
| `/workspace/AUDIT.md` | On event | TTS generated, calls made, alerts |

---

## Constraints

```
❌ Never store voice samples or audio files outside /workspace/voice/
❌ Never use the cloned voice to impersonate someone other than the principal
❌ Never make calls outside working hours (9h-19h Mon-Fri)
❌ Never leave more than one voicemail per lead per week
❌ Never fabricate call transcripts or outcomes
✅ Always log every call with transcript to calls/history/
✅ Always notify principal when a hot lead (score 8+) calls or is called
✅ Always respect lead's request to not be contacted again
✅ If ElevenLabs login fails → notify principal, do not retry more than 3 times
✅ If voice samples missing → pause and notify, do not attempt cloning
```

---

## Error Handling

```
ERROR: ElevenLabs login failed
  Action: Try Option A (Google) then Option B (email/password)
  After 3 failures: notify principal via Telegram with manual steps
  Log: ERRORS.md → "ElevenLabs login failed [date] — manual setup needed"

ERROR: Voice samples missing
  Action: Do NOT attempt voice cloning
  Notify: Telegram → "Upload 3 MP3 samples to /workspace/voice/samples/"
  Log: AUDIT.md → "Voice setup paused — samples missing"

ERROR: API rate limit hit
  Action: Wait 60 seconds, retry once
  If still failing: queue the job for next hour
  Log: ERRORS.md → "Rate limit hit — job queued [date]"

ERROR: Twilio call fails
  Action: Log failure, mark lead as call_failed in pending/
  Retry: next day same time slot
  Log: ERRORS.md → "Call failed: [lead_id] — [error] [date]"

ERROR: ffmpeg not found
  Action: Install automatically:
    apt-get install -y ffmpeg
  If install fails: notify principal
  Log: ERRORS.md → "ffmpeg missing — install attempted [date]"
```
