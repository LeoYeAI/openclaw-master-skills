# Changelog

## 1.5.3 (2026-02-26)

### Security
- **Tailscale APT install**: Replaced `curl | sh` with official APT repository for Tailscale installation
- **Context sanitization**: User context is stripped to natural-language characters only (letters, numbers, common punctuation). IP addresses and domains are removed. Capped at 1000 characters.
- **Provider keys in config.json**: API keys stored in `config.json` (chmod 600) instead of systemd environment variables

### Features
- **Sanitized context returned to client**: All context endpoints (PUT, POST, WebSocket) return the sanitized text so the app can show users exactly what is stored
- **Setup re-run preserves keys**: Re-running setup prompts to keep, update, or delete existing API keys
- **Provider auto-fallback**: If preferred STT/TTS provider has no API key, automatically falls back to first available provider
- **`clack update` command**: Pull latest code and restart with a single command

### Docs
- Fixed WebSocket endpoint path (`/ws` → `/voice`)
- Fixed step numbering in README quickstart
- Added `set_context`, `context_updated`, `context_cleared` to WebSocket protocol docs
- Updated configuration docs to reflect `config.json` for provider keys
- Added input sanitization details to Security sections

---

## 1.3.0 (2026-02-21)

### Security
- **Encrypted connections only**: App now supports Domain (SSL/WSS) and Tailscale modes — unencrypted public connections removed
- **Port hardening**: Port 9878 should be firewalled; documentation updated with iptables rules for localhost + Tailscale only
- **Multi-provider voice selection**: OpenAI (9 voices) and Deepgram (12 Aura voices) with aliases, alongside existing ElevenLabs voices

### Features
- **Tailscale support**: Connect via Tailscale IP with WireGuard encryption at the network layer
- **Domain mode**: WSS on port 443 via Caddy reverse proxy with automatic SSL
- **Configurable port**: Custom port setting in server settings (Tailscale mode)
- **Security info page**: New "Info & Legal" section with Security, Setup Guide, Before You Start, Terms, and Privacy
- **Context save button**: Explicit save for session context field
- **App icon**: Real app icon on website and README

### Removed
- Auto-reconnect on disconnect (was causing reliability issues)
- Unencrypted (WS) connection option for public IPs

### App Changes
- Connection picker: "Domain (SSL)" and "Tailscale" replace old Auto/WSS/WS options
- Port field only visible in Tailscale mode
- "Info & Legal" replaces "Legal" with Security and Setup Guide sub-pages
- Removed reconnecting indicator from UI

---

## 1.2.0 (2026-06-22)

### Features
- **Per-session provider selection**: STT and TTS providers can be chosen independently per call via `sttProvider` and `ttsProvider` in the session start config
- **Auto-detection of available providers**: Server detects all configured API keys at startup and exposes them via `GET /info`
- **`GET /info` endpoint**: Returns agent name, available STT providers, available TTS providers, and defaults
- **`CLACK_AGENT_NAME` env var**: Configurable agent name shown in the iOS app (default: "Storm")
- **Mixed provider combos**: Use on-device STT with cloud TTS (or any combination) — no longer all-or-nothing

### App Changes
- **Voice Processing settings page**: New dedicated page with independent STT/TTS provider pickers
- **Dynamic provider list**: App fetches available providers from server and shows them as options alongside "On-Device"
- **Settings reorder**: Voice Detection → Context → Behavior
- **Server section**: Green checkmark when paired
- **Voice picker**: Only shown when TTS is not set to on-device

### Protocol
- Added `sttProvider` and `ttsProvider` fields to session start config
- `GET /info` returns `{ agentName, stt: { available, default }, tts: { available, default } }`

---

## 1.1.0 (2026-02-20)

### Security
- Rate-limited pairing: 5 attempts per IP per 5 minutes, 2-second delay on failed attempts
- Auth token required for all endpoints except `GET /health` and `POST /pair`

### Features
- **Session key prefix**: Each voice call creates a `clack:<uuid>` session in OpenClaw (isolated per call)
- **Echo test mode**: Server-wide via `CLACK_ECHO_MODE=true` env var, or per-session via client config
- **Local speech mode**: On-device STT/TTS support via `text_input` message type — only LLM calls go through server, zero speech API usage
- **Audio normalization**: Peak normalization with capped gain for echo mode playback
- **Interrupt/TTS cancellation**: Cancel in-progress TTS for all providers (ElevenLabs, OpenAI, Deepgram)
- **`GET /sessions` endpoint**: List active sessions
- **Conversation history persistence**: Shared history file across calls (configurable via `CLACK_HISTORY_DIR`), up to 50 messages (configurable via `CLACK_MAX_HISTORY`)
- **Input length limit**: Server-side 300-char max (`CLACK_MAX_INPUT_CHARS`) — transcripts exceeding this are truncated
- **AI response rules**: 1–3 sentences enforced, `max_tokens` capped at 150

### Protocol
- Added `text_input` client message type for local speech mode
- Added `interrupt` client message type for TTS cancellation
- Added `tts_cancelled` server message type
- Added `echo` option to session start config

## 1.0.0 (2026-02-20)

### Features
- Multi-provider support: ElevenLabs, OpenAI, and Deepgram for both STT and TTS
- 20 built-in ElevenLabs voice aliases
- Voice response rules: AI responses enforced short (1-3 sentences) for natural conversation
- Input length limiting: Configurable max transcript length (default 300 chars)
- Confidence filtering: Low-confidence and short STT results are discarded
- Echo detection: Prevents TTS → mic → STT feedback loops
- Hallucination detection: Filters repetitive/nonsense transcriptions
- Audio chunking: Auto-splits long recordings for reliable transcription
- Device pairing: One-time code system for secure authentication
- Conversation history: Persistent across sessions with configurable depth
- Keepalive pings during LLM processing to prevent client timeouts
- Per-session voice override via WebSocket config
- HTTP endpoints: health, voices, history, pairing
- Automated setup script with systemd service configuration
- Auto-detection of OpenClaw gateway config

### Protocol
- WebSocket endpoint at `/voice` with token auth (query param or message)
- Binary PCM audio frames (16kHz, 16-bit, mono)
- JSON control messages for session lifecycle
- Processing stage notifications (transcribing, thinking, speaking, filtered)
