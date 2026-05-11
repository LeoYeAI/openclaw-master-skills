#!/usr/bin/env python3
"""
claw-diplomat relay server — relay.py

Dumb encrypted passthrough relay for peer-to-peer claw-diplomat sessions.
Routes WebSocket frames between clients who share a relay_token session pair.
Cannot read message content (Noise_XX is applied end-to-end before the relay).

HTTP endpoints (handled via websockets process_request):
  GET  /myip                     → returns caller's public IP
  GET  /reserve                  → reserves a relay slot, returns relay_token
  GET  /reserve/{token}/revoke   → revokes a relay token
  GET  /connection-request?target_token=&my_alias=&request_id=
                                 → send a connection request to a listening agent
  GET  /connection-request/{id}/status
                                 → poll approval status (pending/approved/denied)
  GET  /connection-request/{id}/approve?token=
                                 → approve a pending connection request
  GET  /connection-request/{id}/deny?token=
                                 → deny a pending connection request

WebSocket endpoint:
  WS /ws                         → relay channel (requires relay_token in header)

Security properties:
  - No message content logging
  - Rate limiting: 100 connections/IP/hour
  - Session timeout: 2h idle
  - Max payload: 64KB
  - Only RELAY_SECRET env var for admin operations (not used by clients)
  - No persistence — relay is stateless between restarts
  - No dependency on any external service
"""

from __future__ import annotations

# ─── Standard Library ─────────────────────────────────────────────────────────
import asyncio
import hashlib
import hmac
import http
import json
import logging
import os
import secrets
import time
import urllib.parse
from collections import defaultdict
from typing import Any, Optional

# ─── Third-Party ──────────────────────────────────────────────────────────────
try:
    import websockets
    from websockets.asyncio.server import ServerConnection, serve
except ImportError as _e:
    import sys
    sys.exit(f"Missing dependency: websockets >= 12.0. Run: pip3 install websockets>=12.0\n{_e}")

# ─── Configuration ────────────────────────────────────────────────────────────
HOST: str         = os.environ.get("RELAY_HOST", "0.0.0.0")
PORT: int         = int(os.environ.get("RELAY_PORT", "8080"))
MAX_PAYLOAD_BYTES: int = 64 * 1024                     # 64KB per spec
SESSION_TIMEOUT_S: int = 2 * 60 * 60                  # 2 hours idle
MAX_CONN_PER_IP_PER_HOUR: int = 100
TOKEN_LENGTH: int = 24                                  # bytes → 48 hex chars

# Admin secret (optional) — not used by clients, reserved for future relay management
RELAY_SECRET: str = os.environ.get("RELAY_SECRET", secrets.token_hex(32))

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL = os.environ.get("RELAY_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] relay: %(message)s",
)
LOG = logging.getLogger("claw-diplomat.relay")

# ─── In-Memory State ──────────────────────────────────────────────────────────
# relay_token → asyncio.Queue  (messages destined for this token's connection)
_token_queues:   dict[str, asyncio.Queue[bytes]] = {}
# relay_token → asyncio.Event  (set when a peer connects and is ready)
_token_ready:    dict[str, asyncio.Event]         = {}
# relay_token → peer_relay_token  (paired sessions)
_token_pairs:    dict[str, str]                   = {}
# relay_token → last_activity timestamp
_token_activity: dict[str, float]                 = {}
# IP → list of connection timestamps (for rate limiting)
_ip_connections: dict[str, list[float]]           = defaultdict(list)
# session_id → Queue of (acceptor_ws, done_event) — connector waits here for listener to accept
_pending_accept: dict[str, asyncio.Queue]         = {}
# request_id → {target_token, from_alias, from_ip, status, created_at}
_connection_requests: dict[str, dict[str, Any]]   = {}

# Connection request TTL: 24 hours
CONN_REQ_TTL_S: int = 24 * 60 * 60
# Max alias length accepted in connection requests
MAX_ALIAS_LEN: int  = 64

def _generate_relay_token() -> str:
    return "rt_" + secrets.token_hex(TOKEN_LENGTH)

def _rate_check(ip: str) -> bool:
    """Return True if this IP is within the allowed rate. SECURITY."""
    now = time.monotonic()
    cutoff = now - 3600.0
    _ip_connections[ip] = [t for t in _ip_connections[ip] if t > cutoff]
    if len(_ip_connections[ip]) >= MAX_CONN_PER_IP_PER_HOUR:
        return False
    _ip_connections[ip].append(now)
    return True

def _cleanup_expired_tokens() -> None:
    """Remove idle tokens and stale connection requests to prevent memory growth."""
    now = time.monotonic()
    expired = [
        tok for tok, last in _token_activity.items()
        if now - last > SESSION_TIMEOUT_S
    ]
    for tok in expired:
        _token_queues.pop(tok, None)
        _token_ready.pop(tok, None)
        _token_pairs.pop(tok, None)
        _token_activity.pop(tok, None)
        LOG.debug("Expired idle token: %s…", tok[:12])

    wall_now = time.time()
    stale_reqs = [
        rid for rid, req in _connection_requests.items()
        if wall_now - req.get("created_at_wall", 0) > CONN_REQ_TTL_S
    ]
    for rid in stale_reqs:
        _connection_requests.pop(rid, None)
        LOG.debug("Expired connection request: %s…", rid[:8])

# ─── HTTP Request Handler ─────────────────────────────────────────────────────
async def process_request(connection: ServerConnection, request: Any) -> Any:
    """
    Handle HTTP requests before WebSocket upgrade.
    Uses connection.respond() — the documented websockets 12.x/13.x API.
    Returns None to proceed with the WebSocket handshake.
    """
    path = request.path.rstrip("/")
    peer_ip = connection.remote_address[0] if connection.remote_address else "unknown"

    # ── Rate check ─────────────────────────────────────────────────────────
    if not _rate_check(peer_ip):
        return connection.respond(
            http.HTTPStatus.TOO_MANY_REQUESTS,
            json.dumps({"error": "rate_limit_exceeded"}) + "\n",
        )

    # ── GET /myip ──────────────────────────────────────────────────────────
    if path == "/myip":
        return connection.respond(
            http.HTTPStatus.OK,
            json.dumps({"ip": peer_ip}) + "\n",
        )

    # ── GET /reserve ───────────────────────────────────────────────────────
    if path == "/reserve":
        _cleanup_expired_tokens()
        relay_token = _generate_relay_token()
        expires_at  = time.time() + 7 * 24 * 3600  # 7-day TTL

        _token_queues[relay_token]   = asyncio.Queue()
        _token_ready[relay_token]    = asyncio.Event()
        _token_activity[relay_token] = time.monotonic()

        LOG.info("Reserved slot: %s… for IP %s", relay_token[:12], peer_ip)
        return connection.respond(
            http.HTTPStatus.OK,
            json.dumps({"relay_token": relay_token, "expires_at": _format_iso(expires_at)}) + "\n",
        )

    # ── GET /reserve/{token}/revoke ────────────────────────────────────────
    if path.startswith("/reserve/") and path.endswith("/revoke"):
        token = path[len("/reserve/"):-len("/revoke")]
        if token in _token_queues:
            _token_queues.pop(token, None)
            _token_ready.pop(token, None)
            _token_pairs.pop(token, None)
            _token_activity.pop(token, None)
            LOG.info("Revoked token: %s…", token[:12])
            return connection.respond(
                http.HTTPStatus.OK,
                json.dumps({"status": "revoked"}) + "\n",
            )
        return connection.respond(
            http.HTTPStatus.NOT_FOUND,
            json.dumps({"error": "not_found"}) + "\n",
        )

    # ── Connection-request endpoints ───────────────────────────────────────
    parsed   = urllib.parse.urlparse(request.path)
    clean    = parsed.path.rstrip("/")
    qs       = urllib.parse.parse_qs(parsed.query, keep_blank_values=False)

    # GET /connection-request?target_token=&my_alias=&request_id=
    if clean == "/connection-request":
        target_token = (qs.get("target_token") or [""])[0]
        my_alias_raw = (qs.get("my_alias")     or ["unknown"])[0][:MAX_ALIAS_LEN]
        request_id   = (qs.get("request_id")   or [""])[0][:64]

        if not target_token or target_token not in _token_queues:
            return connection.respond(
                http.HTTPStatus.NOT_FOUND,
                json.dumps({"error": "target_not_found"}) + "\n",
            )
        if not request_id:
            return connection.respond(
                http.HTTPStatus.BAD_REQUEST,
                json.dumps({"error": "request_id_required"}) + "\n",
            )
        if request_id in _connection_requests:
            # Idempotent — already submitted
            return connection.respond(
                http.HTTPStatus.OK,
                json.dumps({"status": "ok", "request_id": request_id}) + "\n",
            )

        _connection_requests[request_id] = {
            "target_token":    target_token,
            "from_alias":      my_alias_raw,
            "from_ip":         peer_ip,
            "status":          "pending",
            "created_at_wall": time.time(),
        }

        # Notify the target listener (process_request is async — direct await is fine)
        notify_frame = json.dumps({
            "event":      "connection_request",
            "request_id": request_id,
            "from_alias": my_alias_raw,
            "from_ip":    peer_ip,
        }).encode("utf-8")
        target_queue = _token_queues[target_token]
        await target_queue.put(notify_frame)
        LOG.info("Connection request %s… from %s (%s) → token %s…",
                 request_id[:8], my_alias_raw, peer_ip, target_token[:12])
        return connection.respond(
            http.HTTPStatus.OK,
            json.dumps({"status": "ok", "request_id": request_id}) + "\n",
        )

    # GET /connection-request/{id}/status
    if clean.startswith("/connection-request/") and clean.endswith("/status"):
        rid = clean[len("/connection-request/"):-len("/status")]
        req = _connection_requests.get(rid)
        if req is None:
            return connection.respond(
                http.HTTPStatus.NOT_FOUND,
                json.dumps({"error": "not_found"}) + "\n",
            )
        return connection.respond(
            http.HTTPStatus.OK,
            json.dumps({"status": req["status"]}) + "\n",
        )

    # GET /connection-request/{id}/approve?token=
    if clean.startswith("/connection-request/") and clean.endswith("/approve"):
        rid   = clean[len("/connection-request/"):-len("/approve")]
        token = (qs.get("token") or [""])[0]
        req   = _connection_requests.get(rid)
        if req is None:
            return connection.respond(
                http.HTTPStatus.NOT_FOUND,
                json.dumps({"error": "not_found"}) + "\n",
            )
        if token != req["target_token"]:
            return connection.respond(
                http.HTTPStatus.FORBIDDEN,
                json.dumps({"error": "forbidden"}) + "\n",
            )
        req["status"] = "approved"
        LOG.info("Connection request %s… approved by token %s…", rid[:8], token[:12])
        return connection.respond(
            http.HTTPStatus.OK,
            json.dumps({"status": "ok"}) + "\n",
        )

    # GET /connection-request/{id}/deny?token=
    if clean.startswith("/connection-request/") and clean.endswith("/deny"):
        rid   = clean[len("/connection-request/"):-len("/deny")]
        token = (qs.get("token") or [""])[0]
        req   = _connection_requests.get(rid)
        if req is None:
            return connection.respond(
                http.HTTPStatus.NOT_FOUND,
                json.dumps({"error": "not_found"}) + "\n",
            )
        if token != req["target_token"]:
            return connection.respond(
                http.HTTPStatus.FORBIDDEN,
                json.dumps({"error": "forbidden"}) + "\n",
            )
        req["status"] = "denied"
        LOG.info("Connection request %s… denied by token %s…", rid[:8], token[:12])
        return connection.respond(
            http.HTTPStatus.OK,
            json.dumps({"status": "ok"}) + "\n",
        )

    # ── /ws → proceed with WebSocket upgrade ──────────────────────────────
    if clean in ("/ws", ""):
        return None

    # Unknown path
    return connection.respond(
        http.HTTPStatus.NOT_FOUND,
        json.dumps({"error": "not_found"}) + "\n",
    )

# ─── WebSocket Handler ────────────────────────────────────────────────────────
async def handle_ws(ws: ServerConnection) -> None:
    """
    Handle one WebSocket connection.
    Client must send registration JSON as first message:
      { "action": "listen",   "relay_token": "rt_..."  }
      { "action": "connect",  "my_relay_token": "rt_...", "target_relay_token": "rt_...", "session_id": "..." }
    After registration, relay routes all subsequent frames to the paired client.
    Content is NEVER read or logged beyond routing metadata.
    """
    peer_ip = ws.remote_address[0] if ws.remote_address else "unknown"

    if not _rate_check(peer_ip):
        await ws.close(1008, "Rate limit exceeded")
        LOG.warning("Rate limit: dropped %s", peer_ip)
        return

    # First message: registration
    try:
        raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
    except asyncio.TimeoutError:
        await ws.close(1001, "Registration timeout")
        return

    try:
        reg = json.loads(raw) if isinstance(raw, (str, bytes)) else {}
    except json.JSONDecodeError:
        await ws.close(1008, "Invalid registration")
        return

    action = reg.get("action", "")

    if action == "listen":
        await _handle_listener(ws, reg, peer_ip)
    elif action == "connect":
        await _handle_connector(ws, reg, peer_ip)
    elif action == "accept":
        await _handle_accept(ws, reg, peer_ip)
    else:
        await ws.close(1008, "Unknown action")

async def _handle_listener(ws: ServerConnection, reg: dict[str, Any], peer_ip: str) -> None:
    """Register as a listener and wait for a connector to pair with."""
    relay_token = reg.get("relay_token", "")
    if relay_token not in _token_queues:
        await ws.send(json.dumps({"status": "error", "error": "invalid_token"}))
        await ws.close(1008, "Invalid token")
        return

    _token_activity[relay_token] = time.monotonic()
    _token_ready[relay_token].set()
    await ws.send(json.dumps({"status": "ok", "role": "listener"}))
    LOG.debug("Listener registered: %s…", relay_token[:12])

    queue = _token_queues[relay_token]
    try:
        while True:
            # Forward messages from queue (sent by connector) to this listener
            msg = await asyncio.wait_for(queue.get(), timeout=SESSION_TIMEOUT_S)
            if len(msg) > MAX_PAYLOAD_BYTES:
                LOG.warning("Oversized message from queue (%d bytes) — dropped", len(msg))
                continue
            await ws.send(msg)
            _token_activity[relay_token] = time.monotonic()
    except asyncio.TimeoutError:
        LOG.info("Listener session timeout: %s…", relay_token[:12])
    except websockets.exceptions.ConnectionClosed:
        LOG.debug("Listener disconnected: %s…", relay_token[:12])
    finally:
        _token_ready[relay_token].clear()

async def _handle_connector(ws: ServerConnection, reg: dict[str, Any], peer_ip: str) -> None:
    """
    Connect to a listening agent. Notifies the listener via its queue, waits for
    the listener to open an accept WebSocket, then bridges both connections
    bidirectionally using _bridge().
    """
    my_relay_token     = reg.get("my_relay_token", "")
    target_relay_token = reg.get("target_relay_token", "")
    session_id         = reg.get("session_id", "")

    if not target_relay_token or target_relay_token not in _token_queues:
        await ws.send(json.dumps({"status": "error", "error": "peer_not_found"}))
        await ws.close(1008, "Peer not found")
        return

    # Create accept-handoff queue: listener will put (acceptor_ws, done_event) here
    accept_queue: asyncio.Queue = asyncio.Queue()
    _pending_accept[session_id] = accept_queue
    done_event: Optional[asyncio.Event] = None

    try:
        # Notify the target listener
        target_queue = _token_queues[target_relay_token]
        notify_frame = json.dumps({
            "event":      "inbound_connection",
            "peer_ip":    peer_ip,
            "session_id": session_id,
        }).encode("utf-8")
        await target_queue.put(notify_frame)
        _token_activity[target_relay_token] = time.monotonic()

        await ws.send(json.dumps({"status": "ok", "role": "connector"}))
        LOG.debug("Connector %s…→%s…: listener notified, waiting for accept", my_relay_token[:12], target_relay_token[:12])

        # Wait for the listener to open an "accept" WebSocket for this session
        try:
            acceptor_ws, done_event = await asyncio.wait_for(accept_queue.get(), timeout=60.0)
        except asyncio.TimeoutError:
            LOG.info("Session %s: peer did not accept within 60s", session_id[:12] if session_id else "?")
            return

        # Bridge is ready — signal the connector to start the Noise handshake
        try:
            await ws.send(json.dumps({"event": "peer_accepted"}))
        except websockets.exceptions.ConnectionClosed:
            done_event.set()
            return

        LOG.info("Bridging session %s", session_id[:12] if session_id else "?")
        await _bridge(ws, acceptor_ws, session_id)

    finally:
        _pending_accept.pop(session_id, None)
        if done_event is not None:
            done_event.set()


async def _handle_accept(ws: ServerConnection, reg: dict[str, Any], peer_ip: str) -> None:
    """
    Handle a listener opening an accept connection for a pending session.
    Hands the acceptor WebSocket to the waiting connector via _pending_accept,
    then stays alive until the bridge finishes.
    """
    session_id  = reg.get("session_id", "")
    relay_token = reg.get("relay_token", "")

    if not relay_token or relay_token not in _token_queues:
        await ws.send(json.dumps({"status": "error", "error": "invalid_token"}))
        await ws.close(1008, "Invalid token")
        return

    if not session_id or session_id not in _pending_accept:
        await ws.send(json.dumps({"status": "error", "error": "session_not_found"}))
        await ws.close(1008, "Session not found")
        return

    _token_activity[relay_token] = time.monotonic()
    await ws.send(json.dumps({"status": "ok", "role": "acceptor"}))

    done_event = asyncio.Event()
    await _pending_accept[session_id].put((ws, done_event))
    LOG.debug("Acceptor registered for session %s", session_id[:12] if session_id else "?")

    # Stay alive while the bridge runs in _handle_connector
    await done_event.wait()


async def _bridge(ws_a: ServerConnection, ws_b: ServerConnection, session_id: str = "") -> None:
    """Bidirectionally forward raw frames between two WebSocket connections."""
    short = session_id[:12] if session_id else "?"

    async def _forward(src: ServerConnection, dst: ServerConnection) -> None:
        try:
            async for msg in src:
                if isinstance(msg, str):
                    msg = msg.encode("utf-8")
                if len(msg) > MAX_PAYLOAD_BYTES:
                    LOG.warning("Oversized frame (%d B) in session %s — dropped", len(msg), short)
                    continue
                await dst.send(msg)
        except websockets.exceptions.ConnectionClosed:
            pass

    task_ab = asyncio.create_task(_forward(ws_a, ws_b))
    task_ba = asyncio.create_task(_forward(ws_b, ws_a))
    try:
        _done, pending = await asyncio.wait({task_ab, task_ba}, return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()
            try:
                await t
            except (asyncio.CancelledError, Exception):
                pass
    finally:
        LOG.info("Bridge ended: session %s", short)

def _format_iso(ts: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ─── Cleanup Task ─────────────────────────────────────────────────────────────
async def _periodic_cleanup() -> None:
    """Every 10 minutes, expire idle tokens."""
    while True:
        await asyncio.sleep(600)
        _cleanup_expired_tokens()

# ─── Entry Point ──────────────────────────────────────────────────────────────
async def main() -> None:
    LOG.info("claw-diplomat relay starting on %s:%d", HOST, PORT)
    LOG.info("Max payload: %dKB, session timeout: %dh, rate limit: %d/IP/hr",
             MAX_PAYLOAD_BYTES // 1024, SESSION_TIMEOUT_S // 3600, MAX_CONN_PER_IP_PER_HOUR)

    asyncio.create_task(_periodic_cleanup())

    async with serve(
        handle_ws,
        HOST,
        PORT,
        process_request=process_request,
        max_size=MAX_PAYLOAD_BYTES,
    ):
        LOG.info("Relay ready at ws://%s:%d/ws", HOST, PORT)
        await asyncio.get_event_loop().create_future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
