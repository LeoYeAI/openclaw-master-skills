# voice-agent

🎙️ **Complete voice layer for Wesley — ElevenLabs + Twilio.**

Clones your voice. Generates audio. Makes and receives calls.
Self-configures by navigating elevenlabs.io autonomously — no manual setup.

---

## What It Does

- **Self-configuration** — logs into ElevenLabs via Google OAuth or email/password, creates API key, clones voice, all automatically
- **Voice cloning** — Instant Voice Clone from 3 MP3 samples (30 seconds each)
- **Text to Speech** — converts VSL scripts, podcast intros, video narrations to MP3
- **Outbound calls** — automated follow-up calls to leads in Wesley's voice
- **Inbound calls** — answers 24/7, qualifies prospects, books calls, reports outcomes
- **Telegram notifications** — alerts on hot leads, call summaries, audio ready

---

## Login Options

```
OPTION A (preferred) — Google OAuth
  No credentials needed
  virtual-desktop uses the active Google session
  → click "Continue with Google" on elevenlabs.io

OPTION B — Email / Password
  Add to .env:
    ELEVENLABS_EMAIL=your@email.com
    ELEVENLABS_PASSWORD=yourpassword
```

---

## What You Provide

```
Minimum (TTS only):
  → Google connected in virtual-desktop, OR email/password in .env
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
| `templates/agent_prompt.md` | System prompt for the conversational agent |
| `templates/config.json` | Config structure template |

---

## Python CLI

```bash
# Generate audio from text
python3 voice_generator.py tts --text "Hello, this is Wesley." --output hello.mp3

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

- **virtual-desktop** → required for self-configuration on elevenlabs.io
- **acquisition-master** → triggers calls when leads don't respond to email
- **funnel-builder** → triggers calls when leads visit pricing page
- **content-creator-pro** → provides scripts for audio content generation

---

## Author

Wesley Armando (Georges Andronescu)
