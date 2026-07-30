---
name: clack
version: 1.5.3
description: Deploy and manage Clack, a voice relay server for OpenClaw. Bridges voice input (WebSocket) through STT → OpenClaw agent → TTS, enabling real-time voice conversations with your agent. Supports ElevenLabs, OpenAI, and Deepgram for STT/TTS. Per-session provider selection — users can independently choose STT and TTS providers (including on-device) from the app settings. Encrypted connections via Domain (SSL) or Tailscale. Supports local speech mode where STT/TTS run on-device and only LLM calls go through the server. Use when a user wants to set up voice chat, voice relay, voice interface, Clack, or talk to their agent by voice.
metadata:
  openclaw:
    requires:
      env:
        - OPENCLAW_GATEWAY_TOKEN
        - RELAY_AUTH_TOKEN
      bins:
        - python3
        - systemctl
    primaryEnv: OPENCLAW_GATEWAY_TOKEN
    os:
      - linux
    emoji: "🎙️"
    homepage: https://github.com/fbn3799/clack-skill
---

# Clack

WebSocket relay server that enables real-time voice conversations with an OpenClaw agent.

**Flow:** Client audio (PCM 16kHz/16-bit/mono) → STT → OpenClaw Gateway → TTS → PCM audio back to client.

**Per-session provider selection:** The client can independently choose STT and TTS providers per call — any combination of on-device (Apple speech frameworks) and server-side providers (ElevenLabs, OpenAI, Deepgram). The server auto-detects all available providers based on configured API keys and exposes them via `/info`.

## Prerequisites

- Python 3.10+
- API key for at least one provider (ElevenLabs, OpenAI, or Deepgram) — not needed for local speech mode
- OpenClaw Gateway with `chatCompletions` endpoint enabled
- Root/sudo access (for systemd)
- **Secure connection**: Domain with SSL (recommended) or Tailscale

## Setup

Run the setup script. It creates a venv, installs deps, prompts for API keys, configures a systemd service, and optionally sets up SSL.

```bash
sudo bash scripts/setup.sh
```

The script auto-detects your OpenClaw gateway config and interactively prompts for provider API keys (ElevenLabs, OpenAI, Deepgram — all optional). On re-runs, existing keys can be kept, updated, or deleted.

### Options

```bash
bash scripts/setup.sh [--port 9878] [--domain clack.example.com]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `9878` | Relay server port |
| `--domain` | *(none)* | Domain for SSL setup (enables WSS) |

### Connection modes

All connections are encrypted. The app supports two modes:

**Domain with SSL (recommended):**
```bash
bash scripts/setup.sh --domain clack.yourdomain.com
# → wss://clack.yourdomain.com/voice
```
Requires a DNS A record pointing the domain to your server IP. The setup script auto-configures SSL via Caddy. You can use a free domain from [DuckDNS](https://www.duckdns.org) or your own.

**Tailscale:**
```bash
# Install Tailscale on your server, then connect from the app using your Tailscale IP
# → ws://100.x.x.x:9878/voice (encrypted at network level)
```
No domain or SSL setup needed. Tailscale encrypts all traffic at the network layer. Install Tailscale on both your server and phone, then use the server's Tailscale IP in the app.

**Security note:** Port 9878 should be firewalled from the public internet. Only allow access via localhost (for Caddy reverse proxy) and Tailscale. The app does not support unencrypted public connections.

### Enable OpenClaw Gateway endpoint

The gateway must have `chatCompletions` enabled. Apply this config patch:

```json
{"http": {"endpoints": {"chatCompletions": {"enabled": true}}}}
```

## Management

```bash
clack status     # Check service status
clack restart    # Restart the server
clack logs       # Tail logs
clack pair       # Generate a new pairing code
clack update     # Pull latest code and restart
clack setup      # Re-run interactive setup (add SSL later, update keys, etc.)
clack uninstall  # Remove service and venv
```

## Client App

📱 **iOS** — Available on the [App Store](https://clack-app.com) (or build from source at [github.com/fbn3799/clack-app](https://github.com/fbn3799/clack-app))
🤖 **Android** — Coming soon!

## Security

### Authentication
All endpoints except `GET /health` and `POST /pair` require a valid auth token (`RELAY_AUTH_TOKEN`). Tokens are verified using constant-time HMAC comparison to prevent timing attacks.

### Pairing System
- **6-character alphanumeric** one-time codes (~2.1 billion combinations)
- Codes expire after **5 minutes** (TTL) and are single-use
- **Rate limited:** 5 attempts per IP per 5 minutes — returns HTTP 429 after
- **2-second delay** on failed attempts to slow brute force
- Generating a code requires the admin auth token (`GET /pair`)
- Redeeming a code is public but rate-limited (`POST /pair`)

### Encrypted Connections
- **Domain mode:** WSS (WebSocket Secure) via Caddy with automatic SSL certificates
- **Tailscale mode:** WireGuard encryption at the network layer
- The app enforces encrypted connections — no unencrypted public access
- Port 9878 should be firewalled; only accessible via localhost and Tailscale

### Input Sanitization
All user-facing text inputs are sanitized before processing:
- **Voice transcripts:** Capped at 300 characters (`CLACK_MAX_INPUT_CHARS`), echo detection filters feedback loops, hallucination detection discards nonsense STT output
- **User context:** Stripped to natural-language characters only (letters, numbers, common punctuation, whitespace). Control characters, escape sequences, and non-printable characters are removed. Capped at 1000 characters. Context is wrapped in explicit delimiters before injection into the system prompt.
- **No shell execution:** All external communication uses structured HTTP/WebSocket APIs. No user input is ever passed to a shell.

### Data Privacy
- No analytics, tracking, or telemetry
- Voice audio goes to your server and only to the providers you choose
- The iOS app stores only settings locally (server address, token, preferences)
- Third-party API usage depends on your provider config (ElevenLabs, OpenAI, Deepgram)

## Session Routing

Each voice call creates a **`clack:<uuid>`** session in OpenClaw. These are small, isolated sessions — one per call — so voice conversations don't pollute your main agent context.

### Session Picker
The session picker in the iOS app provides **context injection only**. When you select a session key, it is added as text context to the LLM prompt — it does not change routing. All voice calls still create their own `clack:<uuid>` session.

## User Context

Users can provide persistent context that gets injected into the system prompt for every voice call. This lets the AI know about the user's preferences, notes, or any background information.

### How to set context
- **App text field:** In the Clack app under Settings → Context, enter free-form text
- **Session picker:** Select an OpenClaw session to inject its content as context
- **WebSocket message:** Send `{"type": "set_context", "text": "..."}` during a voice session
- **HTTP API:** `PUT /context?token=...&text=...` or `POST /context` with JSON body `{"text": "..."}`

Context is sanitized before saving — only natural-language characters are kept (letters, numbers, common punctuation). IP addresses and domains are stripped. The server returns the sanitized text in the response so the app can show the user exactly what will be sent as context.

Context persists across calls and server restarts. Clear it via `DELETE /context` or by sending an empty `set_context` message.

## Conversation History

The relay maintains a **shared history file** across calls for continuity. History is stored as JSON in `CLACK_HISTORY_DIR` (default: `/var/lib/clack/history`).

- **Max messages:** 50 (configurable via `CLACK_MAX_HISTORY`)
- History persists across calls and server restarts
- Viewable via `GET /history`, clearable via `DELETE /history`

## Echo Test Mode

For testing audio round-trips without using LLM credits:

- **Server-wide:** Set `CLACK_ECHO_MODE=true` environment variable
- **Per-session:** Send `{"type":"start","config":{"echo":true}}` from the client

In echo mode, transcribed text is echoed back through TTS instead of being sent to the LLM. Audio is **peak-normalized** with capped gain to ensure consistent playback volume.

## Provider Selection

STT and TTS providers can be configured independently per session. The server auto-detects all available providers at startup based on which API keys are set (`ELEVENLABS_API_KEY`, `OPENAI_API_KEY`, `DEEPGRAM_API_KEY`).

### Available modes per direction (STT / TTS):
- **On-device (local):** Uses Apple's built-in speech frameworks. Zero API costs.
- **Server provider:** ElevenLabs, OpenAI, or Deepgram — whichever keys are configured.

### How it works:
1. App fetches `GET /info` to discover available providers
2. User picks STT and TTS providers independently in Settings → Voice
3. On call start, the app sends `sttProvider` and `ttsProvider` in the session config
4. Server creates the appropriate provider instances per session

### Example combinations:
| STT | TTS | Use case |
|-----|-----|----------|
| ElevenLabs | ElevenLabs | Full cloud — best quality |
| On-device | ElevenLabs | Save STT costs, keep premium voices |
| On-device | On-device | Fully local — zero API usage, works offline |
| OpenAI | Deepgram | Mix providers freely |

**Cost optimization:** Use on-device STT (free, unlimited) with a premium cloud TTS voice — get great output quality while eliminating transcription costs entirely. Or go fully on-device for zero API spend.

### Text input mode
When STT is set to on-device, the client sends transcribed text instead of audio:

```json
{"type": "text_input", "text": "What's the weather like?"}
```

When TTS is set to on-device, the server returns `response_text` only and skips audio synthesis.

## AI Response Rules

- Responses are enforced to **1–3 sentences** for natural voice conversation
- Server-side **max_tokens: 150** to prevent runaway responses
- Server-side **max input: 300 characters** (`CLACK_MAX_INPUT_CHARS`) — transcripts exceeding this are truncated

## HTTP Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `GET /health` | GET | No | Health check — returns service status |
| `POST /pair` | POST | No | Redeem pairing code → get auth token (rate-limited) |
| `GET /pair` | GET | Yes | Generate one-time pairing code |
| `GET /info` | GET | Yes | Server info: agent name, available STT/TTS providers |
| `GET /voices` | GET | Yes | List available TTS voices |
| `GET /sessions` | GET | Yes | List active sessions |
| `GET /history` | GET | Yes | Get conversation history |
| `DELETE /history` | DELETE | Yes | Clear conversation history |
| `GET /context` | GET | Yes | Get current user context |
| `PUT /context` | PUT | Yes | Set user context (query param `text`) |
| `POST /context` | POST | Yes | Set user context (JSON body `{"text": "..."}`) |
| `DELETE /context` | DELETE | Yes | Clear user context |
| `WebSocket /voice` | WS | Yes | Voice relay connection |

## WebSocket Protocol

**Endpoint:** `ws://<host>:<port>/voice?token=<RELAY_AUTH_TOKEN>`

### Client → Server

| Message | Format | Description |
|---------|--------|-------------|
| `{"type":"start","config":{...}}` | JSON | Start session. Config: `voice`, `systemPrompt`, `echo`, `sttProvider`, `ttsProvider` |
| Binary frames | bytes | Raw PCM audio (16kHz, 16-bit, mono) |
| `{"type":"text_input","text":"..."}` | JSON | Local speech mode — send text directly |
| `{"type":"end_speech"}` | JSON | Signal end of speech, triggers processing |
| `{"type":"interrupt"}` | JSON | Cancel current TTS playback |
| `{"type":"ping"}` | JSON | Keepalive |
| `{"type":"set_context","text":"..."}` | JSON | Set user context (sanitized before saving) |
| `{"type":"auth","token":"..."}` | JSON | Authenticate (alternative to query param) |

### Server → Client

| Message | Format | Description |
|---------|--------|-------------|
| `{"type":"ready"}` | JSON | Session ready |
| `{"type":"auth_ok"}` / `{"type":"auth_failed"}` | JSON | Auth result |
| `{"type":"processing","stage":"..."}` | JSON | Stage: `transcribing`, `thinking`, `speaking`, `filtered` |
| `{"type":"transcript","text":"...","final":true}` | JSON | STT result |
| `{"type":"response_text","text":"..."}` | JSON | LLM text response |
| `{"type":"response_start","format":"pcm_16000"}` | JSON | Audio stream starting |
| Binary frames | bytes | TTS audio (PCM 16kHz, 16-bit, mono) |
| `{"type":"response_end"}` | JSON | Audio stream done |
| `{"type":"tts_cancelled"}` | JSON | TTS playback was interrupted |
| `{"type":"context_updated","text":"..."}` | JSON | Context saved — `text` contains the sanitized version |
| `{"type":"context_cleared"}` | JSON | Context was cleared |

## Features

- **Multi-provider STT/TTS**: ElevenLabs, OpenAI, and Deepgram support
- **Independent voice input/output configuration**: Choose STT and TTS providers separately — full control over how your voice is transcribed and how the AI speaks back
- **On-device speech**: Apple speech frameworks for STT and/or TTS — zero API costs, mix with cloud providers freely
- **Cost optimization**: Use free on-device transcription with premium cloud voices, or go fully local for zero spend
- **Voice response rules**: AI responses enforced short (1-3 sentences, max_tokens 150)
- **Input length limiting**: Configurable max transcript length (default 300 chars)
- **Confidence filtering**: Low-confidence STT results are discarded
- **Echo detection**: Prevents feedback loops (TTS → mic → STT)
- **Echo test mode**: Test audio pipeline without LLM (server-wide or per-session)
- **Audio normalization**: Peak normalization with capped gain for echo mode playback
- **Audio chunking**: Long recordings auto-split for reliable transcription
- **Hallucination detection**: Filters repetitive/nonsense STT output
- **Interrupt/TTS cancellation**: Cancel in-progress TTS for all providers
- **Pairing system**: Rate-limited one-time codes for secure device pairing
- **Session isolation**: Each call gets its own `clack:<uuid>` session
- **Conversation history**: Shared across calls, 50 messages max, persistent
- **Token auth**: Constant-time HMAC verification
- **Keepalive pings**: Prevents client timeout during long LLM responses
- **Silence detection**: Default threshold 220, configurable range 20–1000
- **Auto-restart**: systemd restarts on crash

## Voice Configuration

20 built-in ElevenLabs voices available. Default: `Will`. Pass voice name or ID in session config:

```json
{"type": "start", "config": {"voice": "aria"}}
```

Available aliases: will, aria, roger, sarah, laura, charlie, george, callum, river, liam, charlotte, alice, matilda, jessica, eric, chris, brian, daniel, lily, bill.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RELAY_AUTH_TOKEN` | — | **Required.** Client auth token (32-char) |
| `OPENCLAW_GATEWAY_URL` | `http://127.0.0.1:18789` | OpenClaw Gateway URL |
| `OPENCLAW_GATEWAY_TOKEN` | — | Gateway bearer token |
| `STT_PROVIDER` | `elevenlabs` | STT provider (`elevenlabs`, `openai`, `deepgram`) |
| `TTS_PROVIDER` | `elevenlabs` | TTS provider (`elevenlabs`, `openai`, `deepgram`) |
| `TTS_VOICE` | `Will` | Default voice (name or ID) |
| `VOICE_RELAY_PORT` | `9878` | Server port |
| `CLACK_ECHO_MODE` | `false` | Enable echo test mode server-wide |
| `CLACK_MAX_INPUT_CHARS` | `300` | Max transcript length (chars) |
| `CLACK_HISTORY_DIR` | `/var/lib/clack/history` | History file storage directory |
| `CLACK_MAX_HISTORY` | `50` | Max conversation history messages |
| `CLACK_AGENT_NAME` | `Storm` | Agent name shown in the iOS app |

Provider API keys (`ELEVENLABS_API_KEY`, `OPENAI_API_KEY`, `DEEPGRAM_API_KEY`) are stored in `config.json` with restricted file permissions, not as environment variables. The setup script manages these interactively.
