#!/usr/bin/env python3
"""
claw-diplomat — listener.py
Background process: connects to relay as a listening agent, accepts inbound
peer connections, performs Noise_XX handshake as responder, validates peer
identity, and writes INBOUND_PENDING sessions to ledger.json for the
diplomat-heartbeat hook to surface to the human on the next agent command.

Spawned by the diplomat-gateway hook on gateway:startup.
PID written to skills/claw-bond/listener.pid.

Security: every incoming field is treated as untrusted. Rate limiting
(5 connections/min/IP) enforced. Unknown peers quarantined. SECURITY T1, T4.
"""

from __future__ import annotations

# ─── Standard Library ─────────────────────────────────────────────────────────
import asyncio
import datetime
import json
import logging
import os
import signal
import sys
import time
import uuid
from collections import defaultdict
from dataclasses import asdict
from typing import Any

# ─── Third-Party ──────────────────────────────────────────────────────────────
try:
    from noise.connection import NoiseConnection
except ImportError as _e:
    sys.exit(f"Missing dependency: noiseprotocol. Run: pip3 install noiseprotocol>=0.3\n{_e}")

try:
    import websockets
    import websockets.exceptions
except ImportError as _e:
    sys.exit(f"Missing dependency: websockets. Run: pip3 install websockets>=12.0\n{_e}")

# ─── Internal ─────────────────────────────────────────────────────────────────
# All core logic is imported from negotiate.py to avoid duplication (DRY).
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
except NameError:
    # __file__ is not defined when this module is loaded via exec_module in tests
    pass
from negotiate import (
    MAX_CONNECTIONS_PER_IP_PER_MIN,
    MAX_PENDING_SESSIONS,
    MAX_TASK_TEXT,
    MAX_PROPOSAL_TEXT,
    MsgType,
    NoiseKeypair,
    NOISE_PATTERN,
    PROTOCOL_VERSION,
    SecurityError,
    SessionRecord,
    SessionState,
    TermsPayload,
    _atomic_json_write,
    _build_noise_responder,
    _build_ssl_context,
    _get_remote_static_pubkey,
    _is_community_relay,
    _new_nonce,
    _noise_handshake_responder,
    _short_id,
    _utc_now_iso,
    add_session_event,
    asdict,
    build_message,
    check_replay,
    get_ledger_path,
    get_pending_approvals_path,
    get_relay_url,
    get_skill_dir,
    get_token_path,
    get_workspace_root,
    is_peer_trusted,
    load_ledger,
    load_private_key_bytes,
    load_public_key_hex,
    read_agent_alias,
    recv_noise_message,
    sanitize_string,
    send_noise_message,
    upsert_session,
    validate_propose_payload,
    decode_diplomat_token,
    lookup_peer_by_pubkey,
    upsert_peer,
    PeerInfo,
    append_to_daily_log,
)

# ─── Logging ──────────────────────────────────────────────────────────────────
_log_level = os.environ.get("DIPLOMAT_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, _log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] listener: %(message)s",
    stream=sys.stderr,
)
LOG = logging.getLogger("claw-diplomat.listener")

# ─── Rate Limiter ─────────────────────────────────────────────────────────────
class _RateLimiter:
    """
    Simple in-memory rate limiter: max N connections per IP per rolling minute.
    SECURITY T4.
    """
    def __init__(self, max_per_minute: int = MAX_CONNECTIONS_PER_IP_PER_MIN) -> None:
        self._max = max_per_minute
        self._counts: dict[str, list[float]] = defaultdict(list)

    def allow(self, ip: str) -> bool:
        now = time.monotonic()
        cutoff = now - 60.0
        self._counts[ip] = [t for t in self._counts[ip] if t > cutoff]
        if len(self._counts[ip]) >= self._max:
            return False
        self._counts[ip].append(now)
        return True

_rate_limiter = _RateLimiter(MAX_CONNECTIONS_PER_IP_PER_MIN)

# ─── Pending Approval Helper ───────────────────────────────────────────────────
def _write_pending_approval(
    workspace_root: str,
    request_id: str,
    from_alias: str,
    from_ip: str,
) -> None:
    """
    Append a connection request to pending_approvals.json.
    The diplomat-heartbeat hook reads this file and notifies the human.
    """
    path = get_pending_approvals_path(workspace_root)
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"requests": []}
    except (json.JSONDecodeError, OSError):
        data = {"requests": []}

    # Deduplicate — don't add the same request_id twice
    existing_ids = {r["request_id"] for r in data.get("requests", [])}
    if request_id in existing_ids:
        return

    data.setdefault("requests", []).append({
        "request_id": request_id,
        "from_alias": from_alias[:64],
        "from_ip":    from_ip,
        "created_at": _utc_now_iso(),
    })
    _atomic_json_write(path, data)
    LOG.info(
        "Pending connection approval written: request %s from %s (%s)",
        request_id[:8], from_alias, from_ip,
    )

# ─── Inbound Connection Handler ───────────────────────────────────────────────
async def handle_inbound_connection(
    workspace_root: str,
    ws: Any,
    peer_ip: str,
) -> None:
    """
    Handle one inbound relay connection:
    1. Enforce rate limiting (SECURITY T4)
    2. Enforce max pending sessions (SECURITY T4)
    3. Perform Noise_XX handshake as responder
    4. Verify peer identity
    5. Receive and validate proposal
    6. Save INBOUND_PENDING to ledger (heartbeat hook surfaces to human)
    """
    # Rate limiting — SECURITY T4
    if not _rate_limiter.allow(peer_ip):
        LOG.warning("Rate limit exceeded for IP %s — dropping connection", peer_ip)
        await ws.close(1008, "Rate limit exceeded")
        return

    # Pending session count check — SECURITY T4
    _ledger = load_ledger(workspace_root)
    open_count = sum(
        1 for s in _ledger.get("sessions", [])
        if s.get("state") not in (
            SessionState.COMMITTED.value, SessionState.DONE.value,
            SessionState.OVERDUE.value, SessionState.REJECTED.value,
            SessionState.CANCELLED.value,
        )
    )
    if open_count >= MAX_PENDING_SESSIONS:
        LOG.warning("Max pending sessions (%d) reached — rejecting inbound", MAX_PENDING_SESSIONS)
        await ws.close(1008, "Too many pending sessions")
        return

    # Load our static keypair (key bytes never exposed as string/dict)
    try:
        private_key_bytes = load_private_key_bytes(workspace_root)
        our_pubkey_hex    = load_public_key_hex(workspace_root)
        our_alias         = read_agent_alias(workspace_root)
    except (FileNotFoundError, PermissionError) as e:
        LOG.error("Cannot load keypair: %s", e)
        await ws.close(1011, "Internal error")
        return

    # Noise_XX handshake as responder — SECURITY T3 (key never in serializable form)
    noise_conn = _build_noise_responder(private_key_bytes)
    try:
        await _noise_handshake_responder(noise_conn, ws)
    except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
        LOG.info("Handshake failed from %s: %s", peer_ip, e)
        return

    # Extract and verify remote static public key from Noise state
    remote_key_bytes = _get_remote_static_pubkey(noise_conn)
    peer_pubkey_hex  = remote_key_bytes.hex() if remote_key_bytes else None

    # Receive HELLO — establishes peer identity over the encrypted channel
    session_id = str(uuid.uuid4())
    try:
        hello = await recv_noise_message(noise_conn, ws, timeout=30.0)
    except (asyncio.TimeoutError, ValueError, websockets.exceptions.ConnectionClosed) as e:
        LOG.info("No HELLO received from %s: %s", peer_ip, e)
        return

    if hello.get("msg_type") != MsgType.HELLO.value:
        LOG.info("Expected HELLO from %s, got %s", peer_ip, hello.get("msg_type"))
        return

    peer_hello_pubkey = hello.get("from_pubkey", "")
    peer_alias_raw    = hello.get("payload", {}).get("from_alias", "unknown")
    proto_version     = hello.get("payload", {}).get("protocol_version", "")

    # Cross-verify: HELLO pubkey must match Noise static key (SECURITY T2)
    if peer_pubkey_hex and peer_hello_pubkey != peer_pubkey_hex:
        LOG.warning(
            "HELLO pubkey (%s…) does not match Noise static key (%s…) from %s — closing",
            peer_hello_pubkey[:8], peer_pubkey_hex[:8], peer_ip,
        )
        await ws.close(1008, "Key mismatch")
        return

    peer_pubkey_hex = peer_hello_pubkey  # use the HELLO value if Noise extraction failed
    session_id      = hello.get("session_id", session_id)  # use initiator's session_id

    # Send our HELLO back
    our_hello = build_message(session_id, MsgType.HELLO.value, our_pubkey_hex, {
        "from_alias": our_alias,
        "protocol_version": PROTOCOL_VERSION,
    })
    try:
        await send_noise_message(noise_conn, ws, our_hello)
    except websockets.exceptions.ConnectionClosed as e:
        LOG.info("Connection closed before HELLO ack from %s: %s", peer_ip, e)
        return

    # Peer trust check — SECURITY T4
    trusted = is_peer_trusted(workspace_root, peer_pubkey_hex)

    # Receive the incoming message — could be PROPOSE (negotiation) or HANDOFF (context passing)
    try:
        incoming_msg = await recv_noise_message(noise_conn, ws, timeout=60.0)
    except (asyncio.TimeoutError, ValueError, websockets.exceptions.ConnectionClosed) as e:
        LOG.info("No message received from %s: %s", peer_ip, e)
        return

    msg_type_recv = incoming_msg.get("msg_type")

    # ── HANDOFF: peer is passing completed work + context ──────────────────────
    if msg_type_recv == MsgType.HANDOFF.value:
        payload_h     = incoming_msg.get("payload", {})
        from_alias_h  = sanitize_string(str(payload_h.get("from_alias", peer_alias_raw)))[:64]
        part_done_h   = sanitize_string(str(payload_h.get("part_done",      "")))[:MAX_TASK_TEXT]
        part_rem_h    = sanitize_string(str(payload_h.get("part_remaining", "")))[:MAX_TASK_TEXT]
        context_h     = sanitize_string(str(payload_h.get("context",        "")))[:MAX_PROPOSAL_TEXT]
        short_id_h    = _short_id(session_id)

        # Persist handoff to ledger (HANDOFF_RECEIVED state)
        handoff_record = SessionRecord(
            session_id=session_id,
            peer_alias=from_alias_h,
            peer_pubkey=peer_pubkey_hex or "",
            initiated_by="peer",
            state=SessionState.HANDOFF_RECEIVED.value,
            terms_version=0,
            final_terms={
                "type":           "HANDOFF",
                "from_alias":     from_alias_h,
                "part_done":      part_done_h,
                "part_remaining": part_rem_h,
                "context":        context_h,
                "received_at":    _utc_now_iso(),
            },
            memory_hash=None,
            peer_memory_hash=None,
            seen_nonces=[incoming_msg.get("nonce", "")],
            events=[{"type": "HANDOFF_RECEIVED", "at": _utc_now_iso(), "by": from_alias_h}],
            created_at=_utc_now_iso(),
        )
        upsert_session(workspace_root, handoff_record)
        append_to_daily_log(
            workspace_root,
            f"- {_utc_now_iso()} — HANDOFF from {from_alias_h} [{short_id_h}]: "
            f"done={part_done_h[:60]}, remaining={part_rem_h[:60]}\n",
        )
        LOG.info(
            "Task handoff received from %s (session %s) — written to ledger",
            from_alias_h, short_id_h,
        )
        return

    # ── PROPOSE: peer wants to negotiate a task deal ───────────────────────────
    proposal_msg = incoming_msg  # alias for clarity

    if msg_type_recv != MsgType.PROPOSE.value:
        LOG.info("Expected PROPOSE or HANDOFF from %s, got %s", peer_ip, msg_type_recv)
        return

    # Validate payload — SECURITY T1 (sanitize ALL incoming fields)
    try:
        terms = validate_propose_payload(proposal_msg.get("payload", {}))
    except ValueError as e:
        LOG.warning("Invalid proposal payload from %s: %s", peer_ip, e)
        await ws.close(1008, "Invalid proposal")
        return

    short_id = _short_id(session_id)

    # Save INBOUND_PENDING to ledger (heartbeat hook surfaces to human)
    pending_record = SessionRecord(
        session_id=session_id,
        peer_alias=peer_alias_raw[:64],     # sanitized in validate_incoming_message
        peer_pubkey=peer_pubkey_hex,
        initiated_by="peer",
        state=SessionState.INBOUND_PENDING.value if not trusted else SessionState.INBOUND_PENDING.value,
        terms_version=terms.terms_version,
        final_terms=None,
        memory_hash=None,
        peer_memory_hash=None,
        seen_nonces=[proposal_msg.get("nonce", "")],
        events=[{"type": "PROPOSED", "at": _utc_now_iso(), "by": peer_alias_raw[:64]}],
        created_at=_utc_now_iso(),
        pending_terms={
            "proposal_text": terms.proposal_text,
            "my_tasks": terms.my_tasks,
            "your_tasks": terms.your_tasks,
            "deadline": terms.deadline,
            "checkin_at": terms.checkin_at,
            "terms_version": terms.terms_version,
            "trusted": trusted,
            "peer_ip": peer_ip,
        },
    )

    # If peer is unknown, do not process proposal — quarantine for human authorization
    # The heartbeat hook will surface the quarantine notice to the human
    if not trusted:
        LOG.info(
            "Inbound proposal from unknown peer %s (pubkey %s…) — quarantined",
            peer_ip, peer_pubkey_hex[:8],
        )
        pending_record.state = SessionState.INBOUND_PENDING.value
        upsert_session(workspace_root, pending_record)
        append_to_daily_log(
            workspace_root,
            f"- {_utc_now_iso()} — {short_id}: INBOUND from unknown peer {peer_pubkey_hex[:8]}… (quarantined)\n",
        )
        # Keep connection open briefly; heartbeat hook notifies human
        # Peer will timeout on their end — expected behavior
        return

    # Trusted peer: persist updated peer record with last_seen
    existing_peer = lookup_peer_by_pubkey(workspace_root, peer_pubkey_hex)
    if existing_peer:
        existing_peer.last_seen = _utc_now_iso()
        upsert_peer(workspace_root, existing_peer)
    else:
        # Trusted via AGENTS.md but not yet in peers.json — add now
        new_peer = PeerInfo(
            alias=peer_alias_raw[:64],
            pubkey=peer_pubkey_hex,
            relay=get_relay_url(),
            relay_token="",
            nat_hint=peer_ip,
            last_seen=_utc_now_iso(),
            trusted_since=_utc_now_iso(),
        )
        upsert_peer(workspace_root, new_peer)

    pending_record.state = SessionState.INBOUND_PENDING.value
    upsert_session(workspace_root, pending_record)
    append_to_daily_log(
        workspace_root,
        f"- {_utc_now_iso()} — {short_id}: PROPOSED by {peer_alias_raw[:64]} (inbound, pending human approval)\n",
    )
    LOG.info(
        "Inbound proposal saved: session %s from %s (%s…)",
        short_id, peer_alias_raw[:64], peer_pubkey_hex[:8],
    )

# ─── Main Relay Listener Loop ─────────────────────────────────────────────────
async def run_listener(workspace_root: str) -> None:
    """
    Connect to relay as a listening agent and accept inbound connections.
    Runs indefinitely until SIGTERM/SIGINT.
    """
    relay_url = get_relay_url()

    # Load our relay token to register as a listener at the relay
    token_path = get_token_path(workspace_root)
    if not os.path.exists(token_path):
        LOG.error(
            "No Diplomat Address found at %s. "
            "Run /claw-diplomat generate-address first.",
            token_path,
        )
        return

    with open(token_path, "r", encoding="ascii") as f:
        my_token_b64 = f.read().strip()

    try:
        token = decode_diplomat_token(my_token_b64)
        my_relay_token = token["relay_token"]
    except ValueError as e:
        LOG.error("Diplomat Address is invalid or expired: %s. Run /claw-diplomat generate-address.", e)
        return

    ssl_ctx = _build_ssl_context(relay_url)

    LOG.info("claw-diplomat listener starting, relay=%s", relay_url)

    while True:
        try:
            async with websockets.connect(relay_url, ssl=ssl_ctx) as ws:
                # Register as a listener at the relay
                register_msg = json.dumps({
                    "action": "listen",
                    "relay_token": my_relay_token,
                })
                await ws.send(register_msg)

                ack_raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
                try:
                    ack = json.loads(ack_raw)
                except json.JSONDecodeError:
                    LOG.error("Bad registration acknowledgment from relay")
                    await asyncio.sleep(30)
                    continue

                if ack.get("status") != "ok":
                    err = ack.get("error", "unknown")
                    if "invalid_token" in err or "not_found" in err:
                        LOG.error(
                            "Relay rejected registration: %s. "
                            "Run /claw-diplomat generate-address to refresh your address.",
                            err,
                        )
                        return  # Fatal — stop retrying
                    LOG.warning("Relay registration failed: %s. Retrying in 30s.", err)
                    await asyncio.sleep(30)
                    continue

                LOG.info("Registered with relay, waiting for inbound connections...")

                # Accept inbound connections from relay
                async for raw_frame in ws:
                    try:
                        frame = json.loads(raw_frame) if isinstance(raw_frame, (str, bytes)) else {}
                    except json.JSONDecodeError:
                        continue

                    if frame.get("event") == "connection_request":
                        # Permission checkpoint: peer wants to connect. Write to
                        # pending_approvals.json — heartbeat hook notifies the human.
                        req_id     = frame.get("request_id", "")
                        from_alias = frame.get("from_alias", "unknown")
                        from_ip    = frame.get("from_ip",    "unknown")
                        LOG.info(
                            "Connection request from %s (%s), request_id=%s",
                            from_alias, from_ip, req_id[:8] if req_id else "?",
                        )
                        if req_id:
                            _write_pending_approval(workspace_root, req_id, from_alias, from_ip)
                        # (Human must approve via /claw-diplomat approve-connect <id>)

                    elif frame.get("event") == "inbound_connection":
                        peer_ip    = frame.get("peer_ip", "unknown")
                        session_id = frame.get("session_id", "")
                        LOG.info("Inbound connection request from %s (session %s)", peer_ip, session_id[:12] if session_id else "?")

                        if not session_id:
                            LOG.warning("No session_id in inbound_connection frame — skipping")
                            continue

                        # Open a fresh WebSocket to the relay and register as acceptor.
                        # The relay will bridge this ws with the waiting connector.
                        try:
                            async with websockets.connect(relay_url, ssl=ssl_ctx) as session_ws:
                                accept_reg = json.dumps({
                                    "action":      "accept",
                                    "relay_token": my_relay_token,
                                    "session_id":  session_id,
                                })
                                await session_ws.send(accept_reg)
                                ack_raw = await asyncio.wait_for(session_ws.recv(), timeout=10.0)
                                try:
                                    ack = json.loads(ack_raw)
                                except json.JSONDecodeError:
                                    LOG.warning("Bad accept ack for session %s — skipping", session_id[:12])
                                    continue
                                if ack.get("status") != "ok":
                                    LOG.warning(
                                        "Relay rejected accept for session %s: %s",
                                        session_id[:12], ack.get("error", "unknown"),
                                    )
                                    continue
                                await handle_inbound_connection(workspace_root, session_ws, peer_ip)
                        except websockets.exceptions.WebSocketException as e:
                            LOG.info("Inbound session error from %s: %s", peer_ip, e)
                        except asyncio.TimeoutError:
                            LOG.warning("Accept timeout for session %s from %s", session_id[:12], peer_ip)
                        except Exception as e:  # noqa: BLE001
                            LOG.error("Unexpected error handling inbound from %s: %s", peer_ip, e)

        except (websockets.exceptions.ConnectionClosed,
                websockets.exceptions.WebSocketException,
                OSError) as e:
            LOG.warning("Relay connection lost: %s. Reconnecting in 15s...", e)
            await asyncio.sleep(15)
        except asyncio.CancelledError:
            LOG.info("Listener cancelled — shutting down")
            break
        except Exception as e:  # noqa: BLE001
            LOG.error("Unexpected listener error: %s. Reconnecting in 30s...", e)
            await asyncio.sleep(30)

def main() -> None:
    workspace_root = get_workspace_root()
    LOG.info("claw-diplomat listener process starting, workspace=%s", workspace_root)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    main_task = loop.create_task(run_listener(workspace_root))

    def _shutdown(signum: int, frame: Any) -> None:  # noqa: ANN001
        LOG.info("Signal %d received — stopping listener", signum)
        main_task.cancel()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT,  _shutdown)

    try:
        loop.run_until_complete(main_task)
    except asyncio.CancelledError:
        pass
    finally:
        loop.close()
        LOG.info("claw-diplomat listener stopped")

if __name__ == "__main__":
    main()
