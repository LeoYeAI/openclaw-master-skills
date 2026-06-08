# voice-agent-pro-v3 (v3.1.0)

🎙️ **Complete autonomous voice layer — ElevenLabs + Twilio.**

Clones your voice. Generates audio. Makes and receives calls.
Generates audio using the ElevenLabs API with your cloned voice.

---

## What It Does

- **Voice cloning** — clones the principal's voice via ElevenLabs API from 3 MP3 samples
- **Voice cloning** — Instant Voice Clone from 3 MP3 samples (30 seconds each)
- **Text to Speech** — converts VSL scripts, podcast intros, video narrations to MP3
- **Outbound calls** — automated follow-up calls to leads in the principal's voice
- **Inbound calls** — answers 24/7, qualifies prospects, books calls, reports outcomes
- **Telegram notifications** — alerts on hot leads, call summaries, audio ready

---

## Required Credentials

```
REQUIRED (add to .env before first use):
  ELEVENLABS_API_KEY=sk_...      → elevenlabs.io → Developers → API Keys
  ELEVENLABS_VOICE_ID=...        → created after voice cloning (see SKILL.md)
  TELEGRAM_BOT_TOKEN=...         → agent's existing Telegram bot
  TELEGRAM_CHAT_ID=...           → agent's existing chat ID

OPTIONAL (for phone calls):
  TWILIO_ACCOUNT_SID=...         → console.twilio.com
  TWILIO_AUTH_TOKEN=...          → console.twilio.com
  TWILIO_PHONE_NUMBER=+1...      → buy a number on Twilio (~$1/month)
```

> The voice cloning setup guide (PATH A terminal + PATH B browser)
> is in SKILL.md — the agent follows it step by step to create
> ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID on first run.

---

## What You Provide

```
Minimum (TTS only):
  → ELEVENLABS_API_KEY in .env (from elevenlabs.io/app/settings/api-keys)
  → 3 MP3 voice samples in /workspace/voice/samples/

For calls (add):
  → TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN + TWILIO_PHONE_NUMBER
```

---

## What the Agent Retrieves Automatically

```
ELEVENLABS_API_KEY   → created in elevenlabs.io dashboard
ELEVENLABS_VOICE_ID  → created after uploading your samples
ELEVENLABS_AGENT_ID  → created if Twilio credentials present
```

---

## Files

| File | Role |
|---|---|
| `SKILL.md` | Full voice system — setup, TTS, calls |
| `README.md` | This file |
| `scripts/voice_generator.py` | Python CLI — TTS generation, call management |
| `templates/agent_prompt.md` | Conversation instructions for the ElevenLabs agent |
| `templates/config.json` | Config structure template |
| `references/setup_guide.md` | Browser dashboard guide (optional — for manual setup) |

---

## Python CLI

```bash
# Generate audio from text
python3 voice_generator.py tts --text "Hello, this is [PRINCIPAL_NAME]." --output hello.mp3

# Generate audio from script file
python3 voice_generator.py tts --script /workspace/voice/scripts/vsl.md

# Check configuration status
python3 voice_generator.py status

# List pending calls
python3 voice_generator.py calls --action list

# Weekly call summary
python3 voice_generator.py calls --action summary
```

---

## Works Best Combined With

- **virtual-desktop** → optional, for browser-based setup (see references/setup_guide.md)
- **acquisition-master** → triggers calls when leads don't respond to email
- **funnel-builder** → triggers calls when leads visit pricing page
- **content-creator-pro** → provides scripts for audio content generation

---

## Author

[PRINCIPAL_NAME]
