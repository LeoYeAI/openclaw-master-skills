# Claw Connector relay

Dumb encrypted passthrough relay for Claw Connector peer sessions.

The relay **cannot read message content** — Noise_XX encryption is applied end-to-end
before any frame reaches the relay. The relay only routes binary frames between clients
that share a paired relay token. It is stateless between restarts.

---

## Quick start (Docker Compose)

```bash
# 1. Clone or copy this directory onto your server
# 2. Configure environment
cp .env.example .env
# Edit .env — set RELAY_SECRET to a strong random value

# 3. Start
docker compose up -d

# 4. Verify
curl http://localhost:8080/myip
```

---

## HTTP API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/myip` | Returns caller's public IP as `{"ip": "..."}` |
| `GET` | `/reserve` | Reserves a relay slot, returns `{"relay_token": "rt_...", "expires_at": "..."}` |
| `GET` | `/reserve/{token}/revoke` | Revokes a relay token |

### Reserve a slot

```bash
curl http://localhost:8080/reserve
# {"relay_token":"rt_abc123...","expires_at":"2026-03-30T12:00:00Z"}
```

### Revoke a slot

```bash
curl http://localhost:8080/reserve/rt_abc123.../revoke
# {"status":"revoked"}
```

---

## WebSocket protocol

Connect to `ws://host:port/ws` and send a registration JSON as the first message:

**Listener** (waiting agent):
```json
{ "action": "listen", "relay_token": "rt_..." }
```

**Connector** (initiating agent):
```json
{
  "action": "connect",
  "my_relay_token": "rt_...",
  "target_relay_token": "rt_...",
  "session_id": "<uuid>"
}
```

After registration, all subsequent frames are forwarded opaquely to the paired client.
The relay never inspects frame content.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RELAY_HOST` | `0.0.0.0` | Bind address |
| `RELAY_PORT` | `8080` | Bind port |
| `RELAY_SECRET` | random | Admin secret (not used by clients) |
| `RELAY_LOG_LEVEL` | `INFO` | Log verbosity |

---

## Security properties

- **No content logging** — frame bodies are never read or stored
- **Rate limiting** — 100 connections/IP/hour (WebSocket + HTTP combined)
- **Session timeout** — tokens expire after 2 hours of inactivity
- **Max payload** — 64 KB per frame (oversized frames are dropped, not rejected at WS)
- **No persistence** — all state is in-memory; restarts clear all sessions
- **Read-only filesystem** — Docker image uses `read_only: true`
- **Dropped capabilities** — container runs with `cap_drop: ALL`
- **Non-root** — relay process runs as `relay` system user (UID set at image build)

---

## Self-hosting notes

- Place behind a TLS-terminating reverse proxy (nginx, Caddy, Traefik) for `wss://` support.
  The relay itself speaks plain `ws://` — TLS termination is the proxy's responsibility.
- To use your self-hosted relay with Claw Connector, set `DIPLOMAT_RELAY_URL` in your
  agent environment:
  ```
  DIPLOMAT_RELAY_URL=wss://your-relay.example.com:443
  ```
- The community relay (`wss://claw-diplomat-relay-production.up.railway.app:443`) is operated by the
  Claw Connector maintainers and is available to all users by default.

---

## Development / local testing

```bash
# Run without Docker
pip install websockets>=12.0
python3 relay.py

# Run tests (from project root)
pytest tests/test_relay.py -v
```
