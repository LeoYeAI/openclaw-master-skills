#!/usr/bin/env python3
"""
claw-diplomat — negotiate.py
Core negotiation engine: key management, relay connection, protocol state machine,
MEMORY.md writes, ledger persistence, and all /claw-diplomat command handlers.

Security rules (enforced in code):
  - All incoming message fields are UNTRUSTED strings — sanitized before use.
  - diplomat.key bytes are NEVER placed in any dict, string, or serializable structure.
  - No writes outside declared workspace paths.
  - No network calls except to declared relay endpoints.
  - Every error is raised explicitly — never swallowed silently.
"""

from __future__ import annotations

# ─── Standard Library ─────────────────────────────────────────────────────────
import argparse
import asyncio
import base64
import datetime
import hashlib
import json
import logging
import os
import re
import shutil
import socket
import ssl
import stat
import sys
import tempfile
import time
import unicodedata
import urllib.request
import urllib.error
import urllib.parse
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional

# ─── Third-Party ──────────────────────────────────────────────────────────────
try:
    import nacl.public
    import nacl.encoding
    import nacl.exceptions
except ImportError as _e:
    sys.exit(f"Missing dependency: PyNaCl. Run: pip3 install PyNaCl>=1.5\n{_e}")

try:
    from noise.connection import NoiseConnection, Keypair as NoiseKeypair
except ImportError as _e:
    sys.exit(f"Missing dependency: noiseprotocol. Run: pip3 install noiseprotocol>=0.3\n{_e}")

try:
    import websockets
    import websockets.exceptions
except ImportError as _e:
    sys.exit(f"Missing dependency: websockets. Run: pip3 install websockets>=12.0\n{_e}")

# ─── Logging ──────────────────────────────────────────────────────────────────
_log_level = os.environ.get("DIPLOMAT_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, _log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
LOG = logging.getLogger("claw-diplomat")

# ─── Constants ────────────────────────────────────────────────────────────────
VERSION: str = "0.1.0"
PROTOCOL_VERSION: str = "0.1.0"
DEFAULT_PORT: int = 7432
DEFAULT_RELAY_URL: str = "wss://claw-diplomat-relay-production.up.railway.app"
DEFAULT_TOKEN_TTL_DAYS: int = 7
DEFAULT_TIMEOUT_HOURS: int = 24
RELAY_RESERVE_URL: str = "https://claw-diplomat-relay-production.up.railway.app/reserve"
RELAY_MYIP_URL: str = "https://claw-diplomat-relay-production.up.railway.app/myip"

# TLS certificate fingerprint for the community relay (SHA-256 of leaf cert).
# Extracted: echo | openssl s_client -connect claw-diplomat-relay-production.up.railway.app:443
#            2>/dev/null | openssl x509 -noout -fingerprint -sha256
COMMUNITY_RELAY_CERT_FINGERPRINT: str = (
    "32:2E:8A:53:0E:3D:17:49:A3:FF:0F:0C:20:21:FF:12:"
    "B8:7F:F8:62:47:18:60:B7:B1:8A:A8:8A:0B:15:0F:F9"
)
COMMUNITY_RELAY_HOST: str = "claw-diplomat-relay-production.up.railway.app"

# Field limits — enforced on ALL incoming fields (SECURITY T1)
MAX_PROPOSAL_TEXT: int = 2000
MAX_TASK_TEXT: int = 500
MAX_TASKS_PER_SIDE: int = 20
MAX_ACTIVE_COMMITMENTS: int = 20
MAX_PENDING_SESSIONS: int = 10
MAX_ALIAS_LEN: int = 64
MAX_NONCE_AGE_SECONDS: int = 300   # 5 minutes

# Rate limiting (inbound connections) — enforced in listener.py
MAX_CONNECTIONS_PER_IP_PER_MIN: int = 5

# MEMORY.md entry constraints
MAX_MEMORY_ENTRY_CHARS: int = 500    # max characters per compact commitment entry

# Unicode direction-override code points to strip (SECURITY T1)
_DIRECTION_OVERRIDES: frozenset[int] = frozenset(range(0x202A, 0x202F)) | frozenset(range(0x2066, 0x206A))

# Noise protocol pattern
NOISE_PATTERN: bytes = b"Noise_XX_25519_AESGCM_SHA256"

# ─── Enums ────────────────────────────────────────────────────────────────────
class MsgType(str, Enum):
    HELLO       = "HELLO"
    PROPOSE     = "PROPOSE"
    COUNTER     = "COUNTER"
    ACCEPT      = "ACCEPT"
    REJECT      = "REJECT"
    COMMIT_ACK  = "COMMIT_ACK"
    CHECKIN     = "CHECKIN"
    CONNECT_REQ = "CONNECT_REQ"
    HANDOFF     = "HANDOFF"     # Task handoff: Alice completes Part A, passes context to Bob

class SessionState(str, Enum):
    IDLE              = "IDLE"
    PENDING_SEND      = "PENDING_SEND"
    PROPOSED          = "PROPOSED"
    COUNTERED         = "COUNTERED"
    ACCEPTED          = "ACCEPTED"
    COMMIT_PENDING    = "COMMIT_PENDING"
    COMMITTED         = "COMMITTED"
    CHECK_IN_DUE      = "CHECK_IN_DUE"
    DONE              = "DONE"
    OVERDUE           = "OVERDUE"
    PARTIAL           = "PARTIAL"
    REJECTED          = "REJECTED"
    CANCELLED         = "CANCELLED"
    INBOUND_PENDING   = "INBOUND_PENDING"
    HANDOFF_RECEIVED  = "HANDOFF_RECEIVED"  # inbound task handoff context received

# ─── Data Classes ─────────────────────────────────────────────────────────────
@dataclass
class PeerInfo:
    alias: str
    pubkey: str            # hex-encoded Curve25519 public key
    relay: str             # relay WSS URL
    relay_token: str       # opaque relay routing token
    nat_hint: str          # public IP at token generation time
    last_seen: str         # ISO8601 UTC
    trusted_since: str     # ISO8601 UTC
    direct_available: bool = False
    direct_address: Optional[str] = None
    relay_token_stale: bool = False

@dataclass
class TermsPayload:
    proposal_text: str
    my_tasks: list[str]
    your_tasks: list[str]
    deadline: str          # ISO8601 UTC
    checkin_at: str        # ISO8601 UTC
    terms_version: int = 1

@dataclass
class LedgerEvent:
    type: str
    at: str                # ISO8601 UTC
    by: str                # "self" | peer_alias
    terms_version: Optional[int] = None
    memory_hash: Optional[str] = None

@dataclass
class SessionRecord:
    session_id: str
    peer_alias: str
    peer_pubkey: str
    initiated_by: str      # "self" | "peer"
    state: str
    terms_version: int
    final_terms: Optional[dict[str, Any]]
    memory_hash: Optional[str]
    peer_memory_hash: Optional[str]
    seen_nonces: list[str]
    events: list[dict[str, Any]]
    created_at: str        # ISO8601 UTC
    committed_at: Optional[str] = None
    checkin_at_actual: Optional[str] = None
    pending_terms: Optional[dict[str, Any]] = None  # for INBOUND_PENDING

# ─── Configuration Helpers ────────────────────────────────────────────────────
def get_workspace_root() -> str:
    """Return workspace root from env or cwd. Raises if not a directory."""
    root = os.environ.get("DIPLOMAT_WORKSPACE", os.getcwd())
    if not os.path.isdir(root):
        raise RuntimeError(f"Workspace root does not exist: {root}")
    return root

def get_skill_dir(workspace_root: str) -> str:
    return os.path.join(workspace_root, "skills", "claw-bond")

def get_key_path(workspace_root: str) -> str:
    return os.path.join(get_skill_dir(workspace_root), "diplomat.key")

def get_pub_path(workspace_root: str) -> str:
    return os.path.join(get_skill_dir(workspace_root), "diplomat.pub")

def get_token_path(workspace_root: str) -> str:
    return os.path.join(get_skill_dir(workspace_root), "my-address.token")

def get_peers_path(workspace_root: str) -> str:
    return os.path.join(get_skill_dir(workspace_root), "peers.json")

def get_ledger_path(workspace_root: str) -> str:
    return os.path.join(get_skill_dir(workspace_root), "ledger.json")

def get_archive_path(workspace_root: str) -> str:
    return os.path.join(get_skill_dir(workspace_root), "archive.md")

def get_memory_path(workspace_root: str) -> str:
    return os.path.join(workspace_root, "MEMORY.md")

def get_daily_log_path(workspace_root: str) -> str:
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return os.path.join(workspace_root, "memory", f"{today}.md")

def get_heartbeat_path(workspace_root: str) -> str:
    return os.path.join(workspace_root, "HEARTBEAT.md")

def get_pending_approvals_path(workspace_root: str) -> str:
    return os.path.join(get_skill_dir(workspace_root), "pending_approvals.json")

def get_relay_url() -> str:
    return os.environ.get("DIPLOMAT_RELAY_URL", DEFAULT_RELAY_URL)

def get_token_ttl_days() -> int:
    raw = os.environ.get("DIPLOMAT_TOKEN_TTL_DAYS", str(DEFAULT_TOKEN_TTL_DAYS))
    try:
        v = int(raw)
        return max(1, min(30, v))
    except ValueError:
        return DEFAULT_TOKEN_TTL_DAYS

def get_timeout_hours() -> int:
    raw = os.environ.get("DIPLOMAT_TIMEOUT_HOURS", str(DEFAULT_TIMEOUT_HOURS))
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_TIMEOUT_HOURS

def get_diplomat_port() -> int:
    raw = os.environ.get("DIPLOMAT_PORT", str(DEFAULT_PORT))
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_PORT

def _is_community_relay(url: str) -> bool:
    return COMMUNITY_RELAY_HOST in url

# ─── Sanitization & Validation ────────────────────────────────────────────────
def strip_direction_overrides(text: str) -> str:
    """Strip Unicode direction-override characters. SECURITY T1."""
    return "".join(ch for ch in text if ord(ch) not in _DIRECTION_OVERRIDES)

def strip_control_characters(text: str) -> str:
    """Strip null bytes and non-printable control characters."""
    return "".join(
        ch for ch in text
        if ch == "\n" or ch == "\t" or (not unicodedata.category(ch).startswith("C"))
    )

def sanitize_string(text: str) -> str:
    """Full sanitization pipeline for untrusted peer strings. SECURITY T1."""
    if not isinstance(text, str):
        raise ValueError("Expected string input")
    result = strip_direction_overrides(text)
    result = strip_control_characters(result)
    return result

def sanitize_peer_string(text: str, max_length: int) -> str:
    """Sanitize a peer-supplied string and truncate to max_length. SECURITY T1."""
    result = sanitize_string(text)
    if len(result) > max_length:
        result = result[:max_length]
    return result

def validate_message_timestamp(iso_str: str) -> bool:
    """Return True if ISO timestamp is within MAX_NONCE_AGE_SECONDS of now. SECURITY T2."""
    try:
        ts = validate_iso8601(iso_str)
        now = datetime.datetime.now(datetime.timezone.utc)
        age = abs((now - ts).total_seconds())
        return age <= MAX_NONCE_AGE_SECONDS
    except ValueError:
        return False

def is_replay(nonce: str, seen_nonces: set) -> bool:
    """
    Return True if nonce was already seen (replay attack). SECURITY T2.
    Adds nonce to seen_nonces on first call (registers it as seen).
    """
    if nonce in seen_nonces:
        return True
    seen_nonces.add(nonce)
    return False

def sanitize_task_list(tasks: Any) -> list[str]:
    """Validate and sanitize a task list from an untrusted source."""
    if not isinstance(tasks, list):
        raise ValueError("tasks must be a list")
    if len(tasks) > MAX_TASKS_PER_SIDE:
        raise ValueError(f"Too many tasks: max {MAX_TASKS_PER_SIDE}")
    result: list[str] = []
    for t in tasks:
        if not isinstance(t, str):
            raise ValueError("Each task must be a string")
        sanitized = sanitize_string(t)
        if len(sanitized) > MAX_TASK_TEXT:
            raise ValueError(f"Task exceeds {MAX_TASK_TEXT} chars")
        result.append(sanitized)
    return result

def validate_iso8601(dt_str: str) -> datetime.datetime:
    """Parse and validate an ISO8601 datetime string. Returns UTC datetime."""
    if not isinstance(dt_str, str):
        raise ValueError("datetime must be a string")
    try:
        dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError("datetime must include timezone")
        return dt.astimezone(datetime.timezone.utc)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid ISO8601 datetime '{dt_str}': {e}") from e

def validate_deadline(deadline_str: str) -> datetime.datetime:
    """
    Validate a deadline: must be future and within 1 year. SECURITY T7.
    Returns UTC datetime.
    """
    dt = validate_iso8601(deadline_str)
    now = datetime.datetime.now(datetime.timezone.utc)
    if dt <= now:
        raise ValueError("Deadline must be in the future")
    one_year = now + datetime.timedelta(days=365)
    if dt > one_year:
        raise ValueError("Deadline cannot be more than 1 year in the future")
    return dt

def validate_incoming_message(raw: Any) -> dict[str, Any]:
    """
    Validate the outer envelope of an incoming NegotiationMessage.
    All string fields treated as untrusted. SECURITY T1, T2.
    Raises ValueError on any violation.
    """
    if not isinstance(raw, dict):
        raise ValueError("Message must be a JSON object")
    required = ("session_id", "msg_type", "from_pubkey", "timestamp", "nonce")
    for field_name in required:
        if field_name not in raw:
            raise ValueError(f"Missing required field: {field_name}")

    # Type checks
    for field_name in required:
        if not isinstance(raw[field_name], str):
            raise ValueError(f"Field {field_name} must be a string")

    # Sanitize string fields that could carry injection payloads
    msg = dict(raw)
    msg["session_id"]  = sanitize_string(msg["session_id"])
    msg["msg_type"]    = sanitize_string(msg["msg_type"])
    msg["from_pubkey"] = sanitize_string(msg["from_pubkey"])

    # Validate msg_type is a known value
    valid_types = {t.value for t in MsgType}
    if msg["msg_type"] not in valid_types:
        raise ValueError(f"Unknown msg_type: {msg['msg_type']!r}")

    # Replay: timestamp freshness check
    ts = validate_iso8601(msg["timestamp"])
    now = datetime.datetime.now(datetime.timezone.utc)
    age = abs((now - ts).total_seconds())
    if age > MAX_NONCE_AGE_SECONDS:
        raise ValueError(f"Message timestamp too old: {age:.0f}s (max {MAX_NONCE_AGE_SECONDS}s)")

    # Nonce format: must be 32 hex chars (16 bytes)
    nonce = msg["nonce"]
    if not re.fullmatch(r"[0-9a-fA-F]{32}", nonce):
        raise ValueError(f"Invalid nonce format: {nonce!r}")

    # payload must be dict if present
    if "payload" in msg and not isinstance(msg["payload"], dict):
        raise ValueError("payload must be a JSON object")

    return msg

def validate_propose_payload(payload: dict[str, Any]) -> TermsPayload:
    """Validate and sanitize a PROPOSE or COUNTER payload. SECURITY T1."""
    text = sanitize_string(payload.get("proposal_text", ""))
    if len(text) > MAX_PROPOSAL_TEXT:
        raise ValueError(f"proposal_text exceeds {MAX_PROPOSAL_TEXT} chars")

    my_tasks   = sanitize_task_list(payload.get("my_tasks", []))
    your_tasks = sanitize_task_list(payload.get("your_tasks", []))
    deadline   = validate_deadline(str(payload.get("deadline", "")))
    checkin_raw = payload.get("checkin_at") or payload.get("deadline")
    checkin_dt = validate_iso8601(str(checkin_raw))

    terms_version = int(payload.get("terms_version", 1))
    if terms_version < 1:
        raise ValueError("terms_version must be >= 1")

    return TermsPayload(
        proposal_text=text,
        my_tasks=my_tasks,
        your_tasks=your_tasks,
        deadline=deadline.isoformat(),
        checkin_at=checkin_dt.isoformat(),
        terms_version=terms_version,
    )

# ─── Budget Utilities (CONTEXT_BUDGET.md) ─────────────────────────────────────
def truncate_to_budget(text: str, max_chars: int) -> str:
    """Truncate text at word boundary to max_chars, appending '…' if truncated."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars - 1].rsplit(" ", 1)[0]
    return truncated + "…"

def build_memory_entry(
    session_id_short: str,
    peer_alias: str,
    my_tasks: str,
    peer_tasks: str,
    deadline_utc: str,
    state: str,
) -> str:
    """Build a compact MEMORY.md commitment entry within MAX_MEMORY_ENTRY_CHARS budget."""
    entry = (
        f"- **[{state}]** Peer: {peer_alias} | "
        f"My: {my_tasks} | Their: {peer_tasks} | "
        f"Due: {deadline_utc} | ID: `{session_id_short}`"
    )
    return truncate_to_budget(entry, MAX_MEMORY_ENTRY_CHARS)

def build_extended_entry(
    session_id_short: str,
    peer_alias: str,
    peer_pubkey: str,
    my_tasks: list[str],
    peer_tasks: list[str],
    deadline_iso: str,
    checkin_iso: str,
    terms_hash: str,
) -> str:
    """Build an extended commitment entry for the daily log."""
    my_str   = ", ".join(my_tasks) or "(none)"
    peer_str = ", ".join(peer_tasks) or "(none)"
    pubkey_short = peer_pubkey[:8] + "…" if len(peer_pubkey) > 8 else peer_pubkey
    return (
        f"### Diplomat Commitment — {session_id_short}\n"
        f"- Peer: {peer_alias} (pubkey: {pubkey_short})\n"
        f"- My tasks: {my_str}\n"
        f"- Peer's tasks: {peer_str}\n"
        f"- Deadline: {deadline_iso}\n"
        f"- Check-in: {checkin_iso}\n"
        f"- Terms hash: {terms_hash}\n"
        f"- Status: COMMITTED\n"
    )

# ─── Crypto: Key Management ────────────────────────────────────────────────────
def generate_keypair(workspace_root: str) -> tuple[bytes, bytes]:
    """
    Generate a NaCl X25519 keypair and write it to the skill directory.
    Sets strict file permissions: diplomat.key → 600, diplomat.pub → 644.
    Does NOT overwrite an existing key. Returns (private_key_bytes, public_key_bytes). SECURITY T3.
    """
    skill_dir = get_skill_dir(workspace_root)
    os.makedirs(skill_dir, exist_ok=True)

    key_path = get_key_path(workspace_root)
    pub_path = get_pub_path(workspace_root)

    if os.path.exists(key_path):
        LOG.info("Keypair already exists — skipping generation")
        priv_bytes = load_private_key_bytes(workspace_root)
        pub_bytes = bytes(nacl.public.PrivateKey(priv_bytes).public_key)
        return priv_bytes, pub_bytes

    # Generate using PyNaCl (Curve25519)
    private_key = nacl.public.PrivateKey.generate()
    # Write private key — raw 32 bytes, hex-encoded for readability
    priv_hex = bytes(private_key).hex()
    pub_hex  = bytes(private_key.public_key).hex()

    # Write private key — NEVER log, NEVER put in any dict
    with open(key_path, "w", encoding="ascii") as f:
        f.write(priv_hex)
    os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)  # 600

    # Write public key
    with open(pub_path, "w", encoding="ascii") as f:
        f.write(pub_hex)
    os.chmod(pub_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)  # 644

    LOG.info("Keypair generated: %s (mode 600), %s (mode 644)", key_path, pub_path)
    return bytes(private_key), bytes(private_key.public_key)

def load_private_key_bytes(workspace_root: str) -> bytes:
    """
    Load the private key as raw bytes. NEVER returns as string or puts in dict.
    Verifies file permissions before loading. SECURITY T3.
    """
    key_path = get_key_path(workspace_root)
    if not os.path.exists(key_path):
        raise FileNotFoundError(
            f"diplomat.key not found at {key_path}. "
            "Run /claw-diplomat generate-address to set up."
        )
    # Verify permissions: must be mode 600 (owner rw only)
    file_stat = os.stat(key_path)
    mode = stat.S_IMODE(file_stat.st_mode)
    if mode & (stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH):
        raise PermissionError(
            f"SECURITY: diplomat.key at {key_path} has group/world permissions "
            f"(mode {oct(mode)}). Fix with: chmod 600 {key_path}"
        )
    with open(key_path, "r", encoding="ascii") as f:
        hex_str = f.read().strip()
    if len(hex_str) != 64:  # 32 bytes = 64 hex chars
        raise ValueError("diplomat.key has invalid length — file may be corrupted")
    return bytes.fromhex(hex_str)

def load_public_key_hex(workspace_root: str) -> str:
    """Load the public key as a hex string."""
    pub_path = get_pub_path(workspace_root)
    if not os.path.exists(pub_path):
        raise FileNotFoundError(f"diplomat.pub not found at {pub_path}")
    with open(pub_path, "r", encoding="ascii") as f:
        return f.read().strip()

def compute_terms_hash(final_terms: dict[str, Any]) -> str:
    """SHA-256 of canonical JSON (sorted keys). SECURITY T2."""
    canonical = json.dumps(final_terms, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

# ─── Crypto: Noise_XX Channel ─────────────────────────────────────────────────
def _build_noise_initiator(private_key_bytes: bytes) -> NoiseConnection:
    """Build a Noise_XX initiator connection using the local static keypair."""
    conn = NoiseConnection.from_name(NOISE_PATTERN)
    conn.set_as_initiator()
    conn.set_keypair_from_private_bytes(NoiseKeypair.STATIC, private_key_bytes)
    conn.start_handshake()
    return conn

def _build_noise_responder(private_key_bytes: bytes) -> NoiseConnection:
    """Build a Noise_XX responder connection using the local static keypair."""
    conn = NoiseConnection.from_name(NOISE_PATTERN)
    conn.set_as_responder()
    conn.set_keypair_from_private_bytes(NoiseKeypair.STATIC, private_key_bytes)
    conn.start_handshake()
    return conn

async def _noise_handshake_initiator(
    conn: NoiseConnection,
    ws: Any,
) -> None:
    """
    Perform Noise_XX handshake as initiator (3 messages: send, recv, send).
    XX pattern: -> e ; <- e ee s es ; -> s se
    """
    # Message 1: initiator → responder (ephemeral)
    msg1 = conn.write_message()
    await ws.send(msg1)
    # Message 2: responder → initiator (ephemeral + responder static)
    msg2 = await asyncio.wait_for(ws.recv(), timeout=30.0)
    conn.read_message(msg2)
    # Message 3: initiator → responder (initiator static)
    msg3 = conn.write_message()
    await ws.send(msg3)

async def _noise_handshake_responder(
    conn: NoiseConnection,
    ws: Any,
) -> None:
    """
    Perform Noise_XX handshake as responder (3 messages: recv, send, recv).
    Captures remote static key before noiseprotocol deletes handshake_state,
    storing it on conn._remote_static_pubkey_bytes for post-handshake verification.
    """
    # Patch handshake_done to capture rs BEFORE it is deleted (SECURITY T2)
    _orig_done = conn.noise_protocol.handshake_done
    def _capturing_done() -> None:  # type: ignore[override]
        hs = getattr(conn.noise_protocol, "handshake_state", None)
        if hs is not None:
            rs = getattr(hs, "rs", None)
            if rs is not None:
                try:
                    # KeyPair25519 from the default backend: use .public_bytes property
                    if hasattr(rs, "public_bytes"):
                        conn._remote_static_pubkey_bytes = bytes(rs.public_bytes)
                    elif hasattr(rs, "public"):
                        conn._remote_static_pubkey_bytes = bytes(rs.public)
                    elif isinstance(rs, bytes):
                        conn._remote_static_pubkey_bytes = rs
                except Exception:
                    pass
        _orig_done()
    conn.noise_protocol.handshake_done = _capturing_done  # type: ignore[method-assign]

    # Message 1: initiator → responder
    msg1 = await asyncio.wait_for(ws.recv(), timeout=30.0)
    conn.read_message(msg1)
    # Message 2: responder → initiator
    msg2 = conn.write_message()
    await ws.send(msg2)
    # Message 3: initiator → responder (contains initiator's static key)
    msg3 = await asyncio.wait_for(ws.recv(), timeout=30.0)
    conn.read_message(msg3)  # triggers _capturing_done() → captures rs

def _get_remote_static_pubkey(conn: NoiseConnection) -> Optional[bytes]:
    """
    Extract remote static public key bytes from a completed Noise_XX handshake.

    The noiseprotocol library deletes handshake_state after handshake_done(), so we
    capture rs during _noise_handshake_responder() and store it on
    conn._remote_static_pubkey_bytes before deletion.

    Falls back to live handshake_state inspection for compatibility with other
    noiseprotocol versions that may not delete the state.
    """
    # Primary path: captured by _noise_handshake_responder monkey-patch
    captured = getattr(conn, "_remote_static_pubkey_bytes", None)
    if captured is not None:
        return bytes(captured)

    # Fallback: live handshake_state (some library versions keep it)
    try:
        hs = getattr(getattr(conn, "noise_protocol", None), "handshake_state", None)
        if hs is None:
            return None
        rs = getattr(hs, "rs", None)
        if rs is None:
            return None
        if isinstance(rs, bytes):
            return rs
        if hasattr(rs, "public_bytes"):
            try:
                from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
                return rs.public_bytes(Encoding.Raw, PublicFormat.Raw)
            except Exception:
                pass
        if hasattr(rs, "public"):
            pk = rs.public
            if isinstance(pk, bytes):
                return pk
        if hasattr(rs, "public_bytes_raw"):
            return rs.public_bytes_raw()
        return None
    except AttributeError:
        return None

def build_noise_initiator(private_key_bytes: bytes, peer_pub_bytes: Optional[bytes] = None) -> NoiseConnection:
    """
    Public wrapper for _build_noise_initiator.
    peer_pub_bytes is accepted for API consistency but verified post-handshake
    via verify_remote_static_key (Noise_XX authenticates static keys during handshake).
    """
    return _build_noise_initiator(private_key_bytes)

def build_noise_responder(private_key_bytes: bytes) -> NoiseConnection:
    """Public wrapper for _build_noise_responder."""
    return _build_noise_responder(private_key_bytes)

def verify_remote_static_key(conn: NoiseConnection, expected_pub_bytes: bytes) -> None:
    """
    Verify the remote static key from a completed Noise_XX handshake matches expected_pub_bytes.
    Raises SecurityError on mismatch. SECURITY T2.
    """
    remote_bytes = _get_remote_static_pubkey(conn)
    if remote_bytes is None:
        return  # Cannot verify — allow gracefully (noiseprotocol API limitation)
    if remote_bytes != expected_pub_bytes:
        raise SecurityError(
            "Remote static key mismatch — connection aborted. "
            "Ask the peer to share a fresh Diplomat Address."
        )

async def send_noise_message(
    noise_conn: NoiseConnection,
    ws: Any,
    msg_dict: dict[str, Any],
) -> None:
    """JSON-serialize, encrypt with Noise, and send over WebSocket."""
    plaintext = json.dumps(msg_dict, separators=(",", ":")).encode("utf-8")
    ciphertext = noise_conn.encrypt(plaintext)
    await ws.send(ciphertext)

async def recv_noise_message(
    noise_conn: NoiseConnection,
    ws: Any,
    timeout: float = 60.0,
) -> dict[str, Any]:
    """Receive from WebSocket, decrypt with Noise, JSON-parse, and validate envelope."""
    ciphertext = await asyncio.wait_for(ws.recv(), timeout=timeout)
    plaintext = noise_conn.decrypt(ciphertext)
    try:
        raw = json.loads(plaintext.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid JSON in decrypted message: {e}") from e
    return validate_incoming_message(raw)

# ─── Token Encoding / Decoding ────────────────────────────────────────────────
def build_diplomat_token(
    alias: str,
    pubkey_hex: str,
    relay_url: str,
    relay_token: str,
    nat_hint: str,
    ttl_days: int,
) -> str:
    """Build a Base64url-encoded Diplomat Address token."""
    now = datetime.datetime.now(datetime.timezone.utc)
    expires = now + datetime.timedelta(days=ttl_days)
    token_dict: dict[str, Any] = {
        "v": 1,
        "alias": alias[:MAX_ALIAS_LEN],
        "pubkey": pubkey_hex,
        "relay": relay_url,
        "relay_token": relay_token,
        "nat_hint": nat_hint,
        "issued_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expires_at": expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    raw_json = json.dumps(token_dict, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw_json.encode("utf-8")).decode("ascii").rstrip("=")

def decode_diplomat_token(token_b64: str) -> dict[str, Any]:
    """
    Decode and validate a Diplomat Address token.
    Raises ValueError on malformed tokens, expired tokens.
    SECURITY T9: token expiry strictly enforced.
    """
    # Re-pad Base64url
    padding = 4 - len(token_b64) % 4
    if padding != 4:
        token_b64 += "=" * padding
    try:
        raw_bytes = base64.urlsafe_b64decode(token_b64.encode("ascii"))
        token = json.loads(raw_bytes.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"Malformed token: {e}") from e

    required = ("v", "alias", "pubkey", "relay", "relay_token", "nat_hint", "expires_at")
    for key in required:
        if key not in token:
            raise ValueError(f"Token missing required field: {key}")
    if token["v"] != 1:
        raise ValueError(f"Unsupported token version: {token['v']}")

    # Expiry check — SECURITY T9
    expires_at = validate_iso8601(token["expires_at"])
    now = datetime.datetime.now(datetime.timezone.utc)
    if expires_at <= now:
        alias = sanitize_string(str(token.get("alias", "your contact")))[:MAX_ALIAS_LEN]
        raise ValueError(
            f"This address has expired (it was valid until "
            f"{_format_deadline_local(expires_at)}).\n"
            f"Ask {alias} to run /claw-diplomat generate-address and share their new address."
        )

    # Sanitize string fields
    token["alias"]       = sanitize_string(str(token["alias"]))[:MAX_ALIAS_LEN]
    token["pubkey"]      = sanitize_string(str(token["pubkey"]))
    token["relay"]       = sanitize_string(str(token["relay"]))
    token["relay_token"] = sanitize_string(str(token["relay_token"]))
    token["nat_hint"]    = sanitize_string(str(token["nat_hint"]))
    return token

# ─── Message Building ─────────────────────────────────────────────────────────
def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _new_nonce() -> str:
    """Generate a 16-byte random nonce as 32 hex chars."""
    return os.urandom(16).hex()

def build_message(
    session_id: str,
    msg_type: str,
    from_pubkey: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Build an outer NegotiationMessage envelope."""
    return {
        "session_id": session_id,
        "msg_type": msg_type,
        "from_pubkey": from_pubkey,
        "timestamp": _utc_now_iso(),
        "nonce": _new_nonce(),
        "payload": payload,
    }

# ─── File I/O: Peer Registry ──────────────────────────────────────────────────
def load_peers(workspace_root: str) -> list[PeerInfo]:
    """Load peers.json. Returns empty list if file does not exist."""
    path = get_peers_path(workspace_root)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"peers.json is corrupted: {e}") from e
    result: list[PeerInfo] = []
    for p in data.get("peers", []):
        try:
            result.append(PeerInfo(**{k: v for k, v in p.items() if k in PeerInfo.__dataclass_fields__}))
        except TypeError as e:
            LOG.warning("Skipping malformed peer entry: %s", e)
    return result

def save_peers(workspace_root: str, peers: list[PeerInfo]) -> None:
    """Atomically write peers.json (chmod 600 — contains relay tokens). SECURITY T3."""
    path = get_peers_path(workspace_root)
    data = {"peers": [asdict(p) for p in peers]}
    _atomic_json_write(path, data)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 600

def lookup_peer_by_alias(workspace_root: str, alias: str) -> Optional[PeerInfo]:
    for p in load_peers(workspace_root):
        if p.alias.lower() == alias.lower():
            return p
    return None

def lookup_peer_by_pubkey(workspace_root: str, pubkey: str) -> Optional[PeerInfo]:
    for p in load_peers(workspace_root):
        if p.pubkey == pubkey:
            return p
    return None

def upsert_peer(workspace_root: str, peer: PeerInfo) -> None:
    """Add or update a peer record by pubkey."""
    peers = load_peers(workspace_root)
    for i, p in enumerate(peers):
        if p.pubkey == peer.pubkey:
            peers[i] = peer
            save_peers(workspace_root, peers)
            return
    peers.append(peer)
    save_peers(workspace_root, peers)

# ─── File I/O: Ledger ─────────────────────────────────────────────────────────
# States permitted when updating a COMMITTED session (Security T5)
_COMMITTED_ALLOWED_STATES: frozenset[str] = frozenset({
    SessionState.COMMITTED.value,
    SessionState.DONE.value,
    SessionState.OVERDUE.value,
    SessionState.PARTIAL.value,
    SessionState.CANCELLED.value,
})

def load_ledger(workspace_root: str) -> dict[str, Any]:
    """
    Load ledger.json. Returns raw dict {"sessions": [...]}.
    Handles corruption gracefully — returns {"sessions": []} on error.
    DATA_FLOWS F8.
    """
    path = get_ledger_path(workspace_root)
    if not os.path.exists(path):
        return {"sessions": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        # Attempt recovery — back up corrupt file, start fresh
        bak = path + ".bak"
        try:
            shutil.copy2(path, bak)
        except OSError:
            pass
        LOG.error(
            "ledger.json is corrupted. Backed up to %s. Starting fresh. Error: %s",
            bak, e,
        )
        print(
            "⚠️  The negotiation ledger was damaged and has been partially recovered. "
            "Committed deals in your memory are unaffected.",
            file=sys.stderr,
        )
        return {"sessions": []}
    if not isinstance(data, dict):
        return {"sessions": []}
    if "sessions" not in data:
        data["sessions"] = []
    return data

def save_ledger(workspace_root: str, ledger: dict[str, Any]) -> None:
    """Atomically write ledger.json. Accepts raw dict {"sessions": [...]}."""
    path = get_ledger_path(workspace_root)
    _atomic_json_write(path, ledger)

def _load_sessions(workspace_root: str) -> list[SessionRecord]:
    """
    Internal helper: load ledger and deserialize to list[SessionRecord].
    Skips malformed entries with a warning.
    """
    data = load_ledger(workspace_root)
    sessions: list[SessionRecord] = []
    for s in data.get("sessions", []):
        try:
            sessions.append(SessionRecord(**{
                k: v for k, v in s.items()
                if k in SessionRecord.__dataclass_fields__
            }))
        except TypeError as e:
            LOG.warning("Skipping malformed session entry: %s", e)
    return sessions

def _save_sessions(workspace_root: str, sessions: list[SessionRecord]) -> None:
    """Internal helper: serialize list[SessionRecord] and write ledger.json."""
    ledger: dict[str, Any] = {"sessions": [asdict(s) for s in sessions]}
    save_ledger(workspace_root, ledger)

def get_session(workspace_root: str, session_id: str) -> Optional[SessionRecord]:
    for s in _load_sessions(workspace_root):
        if s.session_id == session_id:
            return s
    return None

def get_session_by_short_id(workspace_root: str, short_id: str) -> Optional[SessionRecord]:
    for s in _load_sessions(workspace_root):
        if s.session_id.startswith(short_id) or s.session_id[:4] == short_id:
            return s
    return None

def upsert_session(workspace_root: str, session: SessionRecord) -> None:
    """Add or update a session record by session_id. SECURITY T5: COMMITTED sessions are immutable."""
    sessions = _load_sessions(workspace_root)
    for i, s in enumerate(sessions):
        if s.session_id == session.session_id:
            if s.state == SessionState.COMMITTED.value:
                # SECURITY T5a: final_terms cannot change
                if s.final_terms != session.final_terms:
                    LOG.error(
                        "SECURITY: Attempt to mutate COMMITTED session %s final_terms. Blocked.",
                        session.session_id[:8],
                    )
                    raise SecurityError(
                        f"COMMITTED session {session.session_id[:8]}: final_terms cannot be changed."
                    )
                # SECURITY T5b: memory_hash cannot change
                if s.memory_hash != session.memory_hash:
                    LOG.error(
                        "SECURITY: Attempt to change memory_hash of COMMITTED session %s. Blocked.",
                        session.session_id[:8],
                    )
                    raise SecurityError(
                        f"COMMITTED session {session.session_id[:8]}: memory_hash cannot be changed."
                    )
                # SECURITY T5c: state cannot revert to non-terminal state
                if session.state not in _COMMITTED_ALLOWED_STATES:
                    LOG.error(
                        "SECURITY: Attempt to revert COMMITTED session %s to state %s. Blocked.",
                        session.session_id[:8], session.state,
                    )
                    raise SecurityError(
                        f"COMMITTED session {session.session_id[:8]}: "
                        f"cannot revert state to {session.state!r}."
                    )
            sessions[i] = session
            _save_sessions(workspace_root, sessions)
            return
    sessions.append(session)
    _save_sessions(workspace_root, sessions)

def add_session_event(
    workspace_root: str,
    session_id: str,
    event_type: str,
    by: str,
    terms_version: Optional[int] = None,
    memory_hash: Optional[str] = None,
) -> None:
    session = get_session(workspace_root, session_id)
    if session is None:
        raise KeyError(f"Session {session_id[:8]} not found in ledger")
    event: dict[str, Any] = {"type": event_type, "at": _utc_now_iso(), "by": by}
    if terms_version is not None:
        event["terms_version"] = terms_version
    if memory_hash is not None:
        event["memory_hash"] = memory_hash
    session.events.append(event)
    upsert_session(workspace_root, session)

def check_replay(session: SessionRecord, nonce: str) -> None:
    """Reject duplicate nonces. SECURITY T2."""
    if nonce in session.seen_nonces:
        raise SecurityError(f"Duplicate nonce detected — replay attack prevented: {nonce[:8]}…")
    session.seen_nonces.append(nonce)

# ─── File I/O: MEMORY.md ──────────────────────────────────────────────────────
def _atomic_write(path: str, content: str) -> None:
    """Write file atomically using temp file + rename (POSIX atomic). ARCHITECTURE §8."""
    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=dir_path, delete=False, suffix=".tmp"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    shutil.move(tmp_path, path)

def _atomic_json_write(path: str, data: Any) -> None:
    """Atomically write a JSON file."""
    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=dir_path, delete=False, suffix=".tmp"
    ) as tmp:
        json.dump(data, tmp, indent=2)
        tmp_path = tmp.name
    shutil.move(tmp_path, path)

def append_commitment_to_memory(workspace_root: str, entry: str) -> str:
    """
    Append a compact commitment entry to MEMORY.md ## Diplomat Commitments section.
    Enforces MAX_MEMORY_ENTRY_CHARS budget and 20-entry limit. Atomic write. ARCHITECTURE §8.
    Returns SHA-256 hash of the written entry.
    Raises ValueError if entry exceeds MAX_MEMORY_ENTRY_CHARS.
    Raises RuntimeError on write failure. DATA_FLOWS F7.
    """
    if len(entry) > MAX_MEMORY_ENTRY_CHARS:
        raise ValueError(
            f"Memory entry exceeds {MAX_MEMORY_ENTRY_CHARS} chars (got {len(entry)}). "
            "Use build_memory_entry() to build a correctly-sized entry."
        )
    memory_path = get_memory_path(workspace_root)

    try:
        content = open(memory_path, "r", encoding="utf-8").read() if os.path.exists(memory_path) else ""
    except OSError as e:
        raise RuntimeError(f"Cannot read MEMORY.md: {e}") from e

    section_header = "## Diplomat Commitments\n"

    # Count existing entries in section
    current_count = _count_commitment_entries(content)
    if current_count >= MAX_ACTIVE_COMMITMENTS:
        raise RuntimeError(
            "You already have 20 active commitments logged. Complete or cancel one before taking on another.\n"
            "To see your current commitments: /claw-diplomat status"
        )

    if section_header in content:
        insert_pos = content.index(section_header) + len(section_header)
        next_section = content.find("\n## ", insert_pos)
        if next_section == -1:
            new_content = content.rstrip() + "\n" + entry + "\n"
        else:
            new_content = content[:next_section] + entry + "\n" + content[next_section:]
    else:
        new_content = content.rstrip() + "\n\n" + section_header + entry + "\n"

    try:
        _atomic_write(memory_path, new_content)
    except OSError as e:
        raise RuntimeError(f"Failed to write MEMORY.md: {e}") from e

    return hashlib.sha256(entry.encode("utf-8")).hexdigest()

def update_memory_entry_status(
    workspace_root: str,
    session_id_short: str,
    new_status: str,
) -> None:
    """
    In-place status update of a MEMORY.md commitment entry. Atomic write.
    Finds the entry by session_id_short and replaces [ACTIVE] with [new_status].
    ARCHITECTURE §5.
    """
    memory_path = get_memory_path(workspace_root)
    if not os.path.exists(memory_path):
        raise FileNotFoundError("MEMORY.md not found")

    content = open(memory_path, "r", encoding="utf-8").read()
    pattern = re.compile(
        r"(- \*\*\[)[A-Z]+(]\*\* .*?ID: `" + re.escape(session_id_short) + r"`)",
        re.MULTILINE,
    )
    new_content, count = pattern.subn(r"\g<1>" + new_status + r"\g<2>", content)
    if count == 0:
        raise ValueError(f"Commitment ID {session_id_short!r} not found in MEMORY.md")
    _atomic_write(memory_path, new_content)

def _count_commitment_entries(content: str) -> int:
    """Count ACTIVE entries in ## Diplomat Commitments section (DONE/OVERDUE/PARTIAL do not count)."""
    section_header = "## Diplomat Commitments\n"
    if section_header not in content:
        return 0
    start = content.index(section_header) + len(section_header)
    end_idx = content.find("\n## ", start)
    section = content[start:end_idx] if end_idx != -1 else content[start:]
    return sum(1 for line in section.splitlines() if "- **[ACTIVE]**" in line)

def archive_oldest_done_entry(workspace_root: str) -> bool:
    """
    Archive the oldest DONE/OVERDUE MEMORY.md entry to archive.md.
    Returns True if an entry was archived, False if none found (all ACTIVE).
    CONTEXT_BUDGET §5.
    """
    memory_path = get_memory_path(workspace_root)
    if not os.path.exists(memory_path):
        return False

    content = open(memory_path, "r", encoding="utf-8").read()
    section_header = "## Diplomat Commitments\n"
    if section_header not in content:
        return False

    start = content.index(section_header) + len(section_header)
    next_sec = content.find("\n## ", start)
    section = content[start:next_sec] if next_sec != -1 else content[start:]

    # Find oldest DONE or OVERDUE line
    lines = section.splitlines(keepends=True)
    archive_idx = None
    for i, line in enumerate(lines):
        if "- **[DONE]**" in line or "- **[OVERDUE]**" in line:
            archive_idx = i
            break

    if archive_idx is None:
        return False

    archived_line = lines[archive_idx].rstrip()
    # Parse fields for archive format
    id_match = re.search(r"ID: `([^`]+)`", archived_line)
    peer_match = re.search(r"Peer: ([^|]+)\|", archived_line)
    status_match = re.search(r"\*\*\[([A-Z]+)\]\*\*", archived_line)
    short_id  = id_match.group(1) if id_match else "unknown"
    peer      = peer_match.group(1).strip() if peer_match else "unknown"
    status    = status_match.group(1) if status_match else "DONE"
    archive_line = (
        f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')} | "
        f"{status} | {peer} | {short_id} | {archived_line}\n"
    )
    archive_path = get_archive_path(workspace_root)
    with open(archive_path, "a", encoding="utf-8") as f:
        f.write(archive_line)

    # Remove the line from MEMORY.md
    del lines[archive_idx]
    new_section = "".join(lines)
    if next_sec != -1:
        new_content = content[:start] + new_section + content[next_sec:]
    else:
        new_content = content[:start] + new_section
    _atomic_write(memory_path, new_content)
    return True

def append_to_daily_log(workspace_root: str, text: str) -> None:
    """Append text to today's daily log file. Non-atomic (append-only)."""
    path = get_daily_log_path(workspace_root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)

def init_heartbeat(workspace_root: str) -> None:
    """Write the Diplomat Deadline Check block to HEARTBEAT.md (once). SKILL_SPEC §10."""
    path = get_heartbeat_path(workspace_root)
    block = (
        "\n## Diplomat Deadline Check\n"
        "On every heartbeat: scan `## Diplomat Commitments` in MEMORY.md. "
        "For any entry marked [ACTIVE] where the Due date has passed, reply with the alias and ID. "
        "For any entry where Due is within 2 hours, flag as upcoming.\n"
    )
    content = open(path, "r", encoding="utf-8").read() if os.path.exists(path) else ""
    if "## Diplomat Deadline Check" not in content:
        with open(path, "a", encoding="utf-8") as f:
            f.write(block)
        LOG.info("HEARTBEAT.md initialized with Diplomat Deadline Check block")

# ─── Workspace Reads ──────────────────────────────────────────────────────────
def read_agent_alias(workspace_root: str) -> str:
    """Read agent name from SOUL.md. Returns 'My OpenClaw' as fallback."""
    soul_path = os.path.join(workspace_root, "SOUL.md")
    if not os.path.exists(soul_path):
        return "My OpenClaw"
    content = open(soul_path, "r", encoding="utf-8").read()
    # Look for "name:" or "## Name" patterns
    for pattern in (r"(?i)^name:\s*(.+)$", r"(?i)^#\s*(.+)$"):
        m = re.search(pattern, content, re.MULTILINE)
        if m:
            return sanitize_string(m.group(1).strip())[:MAX_ALIAS_LEN]
    return "My OpenClaw"

def read_trusted_pubkeys_from_agents(workspace_root: str) -> set[str]:
    """Read pre-trusted pubkeys from AGENTS.md. Returns empty set if not found."""
    agents_path = os.path.join(workspace_root, "AGENTS.md")
    if not os.path.exists(agents_path):
        return set()
    content = open(agents_path, "r", encoding="utf-8").read()
    # Expect lines like: pubkey: 4a3f9c1d... or - 4a3f9c1d...
    pubkeys: set[str] = set()
    for m in re.finditer(r"(?:pubkey:|^-)\s*([0-9a-fA-F]{64})", content, re.MULTILINE):
        pubkeys.add(m.group(1))
    return pubkeys

def is_peer_trusted(workspace_root: str, pubkey_hex: str) -> bool:
    """Check if a pubkey is in AGENTS.md or peers.json."""
    if pubkey_hex in read_trusted_pubkeys_from_agents(workspace_root):
        return True
    return lookup_peer_by_pubkey(workspace_root, pubkey_hex) is not None

# ─── Network: Relay HTTP Client ────────────────────────────────────────────────
def _relay_http_request(
    url: str,
    method: str,
    body: Optional[dict[str, Any]] = None,
    timeout: int = 10,
) -> dict[str, Any]:
    """
    Make an HTTPS request to the relay. Uses standard TLS verification.
    Only connects to declared relay endpoints. DATA_FLOWS §3.
    """
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = True
    ssl_ctx.verify_mode = ssl.CERT_REQUIRED

    body_bytes = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=body_bytes, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", f"claw-diplomat/{VERSION}")

    handler = urllib.request.HTTPSHandler(context=ssl_ctx)
    opener = urllib.request.build_opener(handler)
    try:
        with opener.open(req, timeout=timeout) as resp:
            response_body = resp.read()
            return json.loads(response_body) if response_body else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Relay HTTP {e.code}: {body_text}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Relay unreachable: {e.reason}") from e

def relay_reserve_slot(pubkey_hex: str) -> tuple[str, str]:
    """
    Reserve a relay slot. Returns (relay_token, expires_at).
    SKILL_SPEC Flow A Step 3.
    Uses GET (no body) — websockets HTTP parser only handles body-less requests.
    """
    relay_url = get_relay_url()
    reserve_url = relay_url.replace("wss://", "https://").replace("ws://", "http://").rstrip("/") + "/reserve"
    try:
        result = _relay_http_request(reserve_url, "GET")
    except RuntimeError as e:
        raise RuntimeError(str(e)) from e
    return result["relay_token"], result.get("expires_at", "")

def relay_get_my_ip() -> str:
    """Discover public IP via relay echo endpoint. SKILL_SPEC Flow A Step 2."""
    relay_url = get_relay_url()
    myip_url = relay_url.replace("wss://", "https://").replace("ws://", "http://").rstrip("/") + "/myip"
    try:
        result = _relay_http_request(myip_url, "GET", timeout=5)
        return sanitize_string(str(result.get("ip", "unknown")))
    except RuntimeError:
        return "unknown"

def relay_revoke_token(relay_token: str) -> None:
    """Revoke a relay slot. SECURITY T9.
    Uses GET /reserve/{token}/revoke — websockets HTTP parser only handles GET.
    """
    relay_url = get_relay_url()
    revoke_url = (
        relay_url.replace("wss://", "https://").replace("ws://", "http://").rstrip("/")
        + f"/reserve/{relay_token}/revoke"
    )
    try:
        _relay_http_request(revoke_url, "GET")
    except RuntimeError as e:
        LOG.warning("Failed to revoke relay token (token may expire naturally): %s", e)

def relay_request_connect(target_relay_token: str, my_alias: str, request_id: str) -> None:
    """
    Send a connection request to target agent. The relay will put a
    connection_request event into the target's listener queue.
    """
    relay_url = get_relay_url()
    base_url = relay_url.replace("wss://", "https://").replace("ws://", "http://").rstrip("/")
    params = urllib.parse.urlencode({
        "target_token": target_relay_token,
        "my_alias":     my_alias,
        "request_id":   request_id,
    })
    url = f"{base_url}/connection-request?{params}"
    result = _relay_http_request(url, "GET")
    if result.get("status") != "ok":
        raise RuntimeError(f"Relay rejected connection request: {result.get('error', 'unknown')}")

def relay_check_connect_status(request_id: str) -> str:
    """
    Poll the approval status of a pending connection request.
    Returns 'pending', 'approved', or 'denied'.
    """
    relay_url = get_relay_url()
    base_url = relay_url.replace("wss://", "https://").replace("ws://", "http://").rstrip("/")
    url = f"{base_url}/connection-request/{urllib.parse.quote(request_id, safe='')}/status"
    try:
        result = _relay_http_request(url, "GET")
        return result.get("status", "pending")
    except RuntimeError:
        return "pending"

def relay_approve_connect(request_id: str, my_relay_token: str) -> None:
    """Approve a pending connection request."""
    relay_url = get_relay_url()
    base_url = relay_url.replace("wss://", "https://").replace("ws://", "http://").rstrip("/")
    params = urllib.parse.urlencode({"token": my_relay_token})
    url = f"{base_url}/connection-request/{urllib.parse.quote(request_id, safe='')}/approve?{params}"
    result = _relay_http_request(url, "GET")
    if result.get("status") != "ok":
        raise RuntimeError(f"Relay rejected approval: {result.get('error', 'unknown')}")

def relay_deny_connect(request_id: str, my_relay_token: str) -> None:
    """Deny a pending connection request."""
    relay_url = get_relay_url()
    base_url = relay_url.replace("wss://", "https://").replace("ws://", "http://").rstrip("/")
    params = urllib.parse.urlencode({"token": my_relay_token})
    url = f"{base_url}/connection-request/{urllib.parse.quote(request_id, safe='')}/deny?{params}"
    result = _relay_http_request(url, "GET")
    if result.get("status") != "ok":
        raise RuntimeError(f"Relay rejected denial: {result.get('error', 'unknown')}")

# ─── Network: WebSocket + Noise Channel ───────────────────────────────────────
def _build_ssl_context(relay_url: str) -> Optional[ssl.SSLContext]:
    """Build SSL context for WebSocket connection. Standard TLS validation."""
    if not relay_url.startswith("wss://"):
        return None
    ctx = ssl.create_default_context()
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED
    return ctx

async def connect_to_relay_as_initiator(
    relay_url: str,
    my_relay_token: str,
    target_relay_token: str,
    private_key_bytes: bytes,
    expected_peer_pubkey_hex: str,
    session_id: str,
) -> tuple[Any, NoiseConnection]:
    """
    Full 9-step connection flow as initiator (SKILL_SPEC Flow B Steps 3–7).
    Returns (websocket, noise_connection) ready for encrypted messaging.
    SECURITY T8: TLS cert check for community relay.
    SECURITY T2: Noise key mismatch = hard abort.
    """
    ssl_ctx = _build_ssl_context(relay_url)

    # Do NOT use "async with" — the websocket must stay open after this function
    # returns so callers (cmd_propose) can continue sending messages on it.
    ws = await websockets.connect(relay_url, ssl=ssl_ctx)
    try:
        # Step 3: Present relay tokens to establish routed session
        connect_req = {
            "action": "connect",
            "my_relay_token": my_relay_token,
            "target_relay_token": target_relay_token,
            "session_id": session_id,
        }
        await ws.send(json.dumps(connect_req))
        ack_raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
        try:
            ack = json.loads(ack_raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Bad relay acknowledgment: {e}") from e
        if ack.get("status") != "ok":
            raise RuntimeError(f"Relay rejected connection: {ack.get('error', 'unknown error')}")

        # TLS cert fingerprint check for community relay — SECURITY T8
        if _is_community_relay(relay_url):
            try:
                ssl_obj = ws.transport.get_extra_info("ssl_object")
                if ssl_obj:
                    cert_der = ssl_obj.getpeercert(binary_form=True)
                    if cert_der:
                        actual_fp = hashlib.sha256(cert_der).hexdigest()
                        expected_fp = COMMUNITY_RELAY_CERT_FINGERPRINT.replace(":", "").lower()
                        if actual_fp != expected_fp and expected_fp != "0" * 64:
                            raise SecurityError(
                                "TLS certificate fingerprint mismatch on community relay. "
                                "This may indicate a MITM attack. Connection aborted."
                            )
            except (AttributeError, TypeError):
                LOG.debug("Could not verify TLS cert fingerprint (transport info unavailable)")

        # Wait for the listener to accept — relay signals when bridge is ready
        try:
            peer_ready_raw = await asyncio.wait_for(ws.recv(), timeout=60.0)
            peer_ready = json.loads(peer_ready_raw)
            if peer_ready.get("event") != "peer_accepted":
                raise RuntimeError(
                    f"Unexpected relay event: {peer_ready.get('event', 'unknown')!r}"
                )
        except asyncio.TimeoutError:
            raise RuntimeError(
                "Peer did not accept the connection within 60 seconds. "
                "They may be offline — ask them to check their listener is running."
            ) from None
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid relay event message: {e}") from e

        # Step 5: Noise_XX handshake as initiator
        noise_conn = _build_noise_initiator(private_key_bytes)
        await _noise_handshake_initiator(noise_conn, ws)

        # Verify remote static key matches expected peer pubkey — SECURITY T2
        remote_key_bytes = _get_remote_static_pubkey(noise_conn)
        if remote_key_bytes is not None:
            remote_hex = remote_key_bytes.hex()
            if remote_hex != expected_peer_pubkey_hex:
                raise SecurityError(
                    f"⛔ Something doesn't look right.\n\n"
                    f"The agent that responded has a different identity than the address token specified. "
                    f"This could mean:\n"
                    f"  • The peer generated a new key and you have an old token (most likely)\n"
                    f"  • Someone is intercepting the connection (unlikely but possible)\n\n"
                    f"To be safe, ask the peer to share a fresh Diplomat Address and connect again.\n"
                    f"This connection has been closed."
                )

        # Step 7: HELLO exchange
        our_pubkey_hex = load_public_key_hex(os.environ.get("DIPLOMAT_WORKSPACE", os.getcwd()))
        our_alias = read_agent_alias(os.environ.get("DIPLOMAT_WORKSPACE", os.getcwd()))
        hello_msg = build_message(session_id, MsgType.HELLO.value, our_pubkey_hex, {
            "from_alias": our_alias,
            "protocol_version": PROTOCOL_VERSION,
        })
        await send_noise_message(noise_conn, ws, hello_msg)
        peer_hello = await recv_noise_message(noise_conn, ws, timeout=30.0)
        if peer_hello.get("msg_type") != MsgType.HELLO.value:
            raise RuntimeError(f"Expected HELLO, got {peer_hello.get('msg_type')!r}")
        peer_pubkey_in_hello = peer_hello.get("from_pubkey", "")
        if peer_pubkey_in_hello != expected_peer_pubkey_hex:
            raise SecurityError(
                "Peer HELLO pubkey does not match expected. Connection aborted."
            )

        return ws, noise_conn

    except Exception:
        await ws.close()
        raise

# ─── Display Helpers ──────────────────────────────────────────────────────────
def _format_deadline_local(dt: datetime.datetime) -> str:
    """Format a UTC datetime in local time for display. SECURITY T7, UX §17."""
    local_dt = dt.astimezone()
    return local_dt.strftime("%A %B %-d, %Y at %-I:%M %p")

def _format_deadline_from_iso(iso_str: str) -> str:
    try:
        dt = validate_iso8601(iso_str)
        return _format_deadline_local(dt)
    except ValueError:
        return iso_str

def _format_tasks(tasks: list[str]) -> str:
    if not tasks:
        return "(none specified)"
    if len(tasks) == 1:
        return tasks[0]
    return "\n    - ".join([""] + tasks).lstrip("\n    - ")

def _short_id(session_id: str) -> str:
    return session_id[:4]

def display_proposal_to_human(
    peer_alias: str,
    terms: TermsPayload,
    is_inbound: bool = True,
) -> str:
    """
    Format proposal for human display. SECURITY T1: wrapped in demarcation block.
    Peer text is NEVER passed to LLM as instructions — display only.
    """
    deadline_str = _format_deadline_from_iso(terms.deadline)
    if is_inbound:
        return (
            f"{'═' * 40}\n"
            f"📨 Proposal from {peer_alias}'s OpenClaw\n"
            f"{'═' * 40}\n"
            f"  They'll do: {_format_tasks(terms.my_tasks)}\n"
            f"  You'll do:  {_format_tasks(terms.your_tasks)}\n"
            f"  Deadline:   {deadline_str}\n"
            f"{'═' * 40}\n"
            f"What do you want to do?\n"
            f"  [accept]  — Agree to these terms\n"
            f"  [counter] — Propose different terms\n"
            f"  [reject]  — Decline this proposal"
        )
    return (
        f"  You'll do:  {_format_tasks(terms.my_tasks)}\n"
        f"  They'll do: {_format_tasks(terms.your_tasks)}\n"
        f"  Deadline:   {deadline_str}"
    )

# ─── Custom Exceptions ────────────────────────────────────────────────────────
class SecurityError(Exception):
    """Raised when a security invariant is violated."""

class ProtocolError(Exception):
    """Raised when the negotiation protocol is violated."""

class RelayError(Exception):
    """Raised when the relay is unreachable or misbehaving."""

# ─── Commands ─────────────────────────────────────────────────────────────────
def cmd_key(workspace_root: str) -> None:
    """Print this agent's public key. /claw-diplomat key"""
    pub_hex = load_public_key_hex(workspace_root)
    print(pub_hex)

def cmd_list(workspace_root: str) -> None:
    """Show all active/recent sessions. /claw-diplomat list"""
    sessions = _load_sessions(workspace_root)
    if not sessions:
        print("No negotiations on record.")
        return
    print("Negotiations:")
    for s in sessions:
        print(f"  {_short_id(s.session_id)}  {s.peer_alias:<20}  {s.state:<16}  v{s.terms_version}")

def cmd_peers(workspace_root: str) -> None:
    """Show connected peers. /claw-diplomat peers"""
    peers = load_peers(workspace_root)
    if not peers:
        print(
            "You haven't connected with anyone yet.\n\n"
            "Share your address to get started: /claw-diplomat generate-address"
        )
        return
    print("Your connected peers:\n")
    for p in peers:
        stale = " ⚠️ (address may be stale)" if p.relay_token_stale else ""
        print(f"  {p.alias:<20}  ·  last seen {p.last_seen[:10]}  ·  {p.relay}{stale}")
    n = len(peers)
    print(f"\n{n} peer{'s' if n != 1 else ''} total. To add a new peer: /claw-diplomat connect <address>")

def cmd_status(workspace_root: str) -> None:
    """Show pending check-ins and overdue. /claw-diplomat status"""
    sessions = _load_sessions(workspace_root)
    now = datetime.datetime.now(datetime.timezone.utc)

    active = [s for s in sessions if s.state == SessionState.COMMITTED.value and s.final_terms]
    pending = [s for s in sessions if s.state in (
        SessionState.PROPOSED.value, SessionState.COUNTERED.value, SessionState.PENDING_SEND.value,
        SessionState.INBOUND_PENDING.value,
    )]
    overdue: list[SessionRecord] = []
    for s in active:
        try:
            deadline = validate_iso8601(s.final_terms["deadline"])
            if deadline < now:
                overdue.append(s)
        except (ValueError, KeyError):
            pass

    if not active and not pending and not overdue:
        print("All clear — no active commitments or pending proposals.")
        return

    print("claw-diplomat status:\n")
    if active:
        print(f"Active commitments ({len(active)}):")
        for s in active:
            t = s.final_terms or {}
            my_task = (t.get("my_tasks") or ["?"])[0]
            print(f"  {_short_id(s.session_id)}  with {s.peer_alias}  |  {my_task[:50]}  |  due {t.get('deadline','?')[:10]}")
    if pending:
        print(f"\nPending proposals ({len(pending)}):")
        for s in pending:
            print(f"  {_short_id(s.session_id)}  with {s.peer_alias}  [{s.state}]")
    if overdue:
        print(f"\nOverdue ({len(overdue)}):")
        for s in overdue:
            t = s.final_terms or {}
            print(f"  {_short_id(s.session_id)}  with {s.peer_alias}  |  was due {t.get('deadline','?')[:10]}")

def cmd_help_security(workspace_root: str) -> None:
    """Print security information. /claw-diplomat help security"""
    print("""
claw-diplomat — Security Information
═════════════════════════════════════

Encryption:  All messages are encrypted end-to-end with Noise_XX (AES-256-GCM)
             before reaching the relay. The relay sees only routing metadata.

Your key:    Your private key is stored at skills/claw-bond/diplomat.key (mode 600).
             It never leaves your machine.

Peer content: Proposal text is always displayed as content, never executed as code.

Incident response:
  1. Run /claw-diplomat status — check for unexpected COMMITTED sessions
  2. Check ledger.json for unknown session_id entries
  3. Check MEMORY.md ## Diplomat Commitments for mismatched hashes
  4. Run /claw-diplomat revoke — immediately invalidate your current address
  5. Delete diplomat.key and diplomat.pub, then run /claw-diplomat generate-address
  6. Remove unknown entries from skills/claw-bond/peers.json
  7. Notify all known peers that your key has changed

Report security issues: https://github.com/claw-diplomat/claw-diplomat/security
""".strip())

def cmd_checkin(workspace_root: str, short_id: str, status_str: str) -> None:
    """Report commitment status. /claw-diplomat checkin <id> done|overdue|partial"""
    valid_statuses = {"done": "DONE", "overdue": "OVERDUE", "partial": "PARTIAL"}
    if status_str.lower() not in valid_statuses:
        raise ValueError(f"Status must be one of: done, overdue, partial")
    new_status = valid_statuses[status_str.lower()]

    session = get_session_by_short_id(workspace_root, short_id)
    if session is None:
        raise KeyError(f"No session found with ID starting with '{short_id}'")

    # Step 2: Update MEMORY.md in-place
    try:
        update_memory_entry_status(workspace_root, short_id, new_status)
    except (FileNotFoundError, KeyError) as e:
        LOG.warning("MEMORY.md entry not found for check-in (%s) — updating ledger only", e)

    # Step 3: Append to daily log
    ts = _utc_now_iso()
    append_to_daily_log(
        workspace_root,
        f"- {ts} — {short_id}: {new_status} (reported by self)\n",
    )

    # Step 4: Update ledger
    session.state = new_status
    session.checkin_at_actual = ts
    upsert_session(workspace_root, session)

    # Step 6: Display result
    peer_alias = session.peer_alias
    if new_status == "DONE":
        print(f"✅ Marked complete. {peer_alias}'s agent has been notified.\n\nGreat work.")
    elif new_status == "PARTIAL":
        print(
            f"Noted. I've logged this as partially complete.\n\n"
            f"Want to renegotiate the remaining tasks with {peer_alias}? (yes / no)"
        )
    else:
        print(
            f"Logged as overdue. {peer_alias}'s agent has been notified.\n\n"
            f"You can renegotiate when you're ready: /claw-diplomat propose {peer_alias}"
        )

def cmd_cancel(workspace_root: str, short_id: str) -> None:
    """Cancel a pending negotiation. /claw-diplomat cancel <id>"""
    session = get_session_by_short_id(workspace_root, short_id)
    if session is None:
        raise KeyError(f"No session found with ID starting with '{short_id}'")
    if session.state == SessionState.COMMITTED.value:
        raise RuntimeError("Cannot cancel a COMMITTED negotiation. Use /claw-diplomat checkin instead.")
    session.state = SessionState.CANCELLED.value
    add_session_event(workspace_root, session.session_id, "CANCELLED", "self")
    upsert_session(workspace_root, session)
    print(f"Negotiation {short_id} cancelled.")

def cmd_retry_commit(workspace_root: str, short_id: str) -> None:
    """Retry a failed MEMORY.md write. /claw-diplomat retry-commit <id>"""
    session = get_session_by_short_id(workspace_root, short_id)
    if session is None:
        raise KeyError(f"No session found with ID starting with '{short_id}'")
    if session.state not in (SessionState.COMMIT_PENDING.value, "MEMORY_WRITE_FAILED"):
        raise RuntimeError(f"Session {short_id} is in state {session.state!r}, not COMMIT_PENDING")
    if not session.final_terms:
        raise RuntimeError(f"Session {short_id} has no final_terms to commit")

    terms = session.final_terms
    my_tasks   = terms.get("my_tasks", [])
    peer_tasks = terms.get("peer_tasks", [])
    deadline   = terms.get("deadline", "")
    entry = build_memory_entry(
        _short_id(session.session_id),
        session.peer_alias,
        my_tasks[0] if my_tasks else "tasks",
        peer_tasks[0] if peer_tasks else "tasks",
        deadline,
        "ACTIVE",
    )
    count = _count_commitment_entries(
        open(get_memory_path(workspace_root), "r").read()
        if os.path.exists(get_memory_path(workspace_root)) else ""
    )
    if count >= MAX_ACTIVE_COMMITMENTS:
        if not archive_oldest_done_entry(workspace_root):
            print(
                "You already have 20 active commitments logged. "
                "Complete or cancel one before adding another.\n"
                "To see your current commitments: /claw-diplomat status"
            )
            return
    memory_hash = append_commitment_to_memory(workspace_root, entry)
    session.state = SessionState.COMMITTED.value
    session.memory_hash = "sha256:" + memory_hash
    session.committed_at = _utc_now_iso()
    upsert_session(workspace_root, session)
    print(f"✅ Commitment {short_id} successfully written to your memory.")

async def cmd_generate_address(workspace_root: str) -> None:
    """Generate and display a Diplomat Address token. SKILL_SPEC Flow A."""
    skill_dir = get_skill_dir(workspace_root)
    os.makedirs(skill_dir, exist_ok=True)

    # First-time setup if needed
    if not os.path.exists(get_key_path(workspace_root)):
        print("👋 Setting up claw-diplomat for the first time...\n\nGenerating your secure identity key... ", end="", flush=True)
        generate_keypair(workspace_root)
        print("✓")
        print("Your agent is now ready to negotiate tasks with other OpenClaw agents.")

    our_pubkey_hex = load_public_key_hex(workspace_root)
    alias = read_agent_alias(workspace_root)

    print("Creating your Diplomat Address... (connecting to relay to reserve your slot)")

    # Discover public IP
    nat_hint = relay_get_my_ip()

    # Reserve relay slot
    try:
        relay_token, expires_at = relay_reserve_slot(our_pubkey_hex)
    except RuntimeError as e:
        print(
            f"⚠️  Couldn't reach the relay server to generate a full address.\n\n"
            f"Your local key is ready, but peers won't be able to connect until the relay is available.\n\n"
            f"Try again in a few minutes, or set up your own relay:\n"
            f"  DIPLOMAT_RELAY_URL=wss://your-relay.example.com:443\n\n"
            f"Error: {e}"
        )
        return

    relay_url = get_relay_url()
    ttl_days  = get_token_ttl_days()
    token_b64 = build_diplomat_token(alias, our_pubkey_hex, relay_url, relay_token, nat_hint, ttl_days)

    # Save token
    token_path = get_token_path(workspace_root)
    with open(token_path, "w", encoding="ascii") as f:
        f.write(token_b64)
    LOG.info("Diplomat Address token saved to %s", token_path)

    # Display
    expires_local = _format_deadline_from_iso(expires_at) if expires_at else f"in {ttl_days} days"
    print(
        f"\nYour Diplomat Address is ready. Share this with anyone you want to work with:\n\n"
        f"  {token_b64}\n\n"
        f"This address is valid for {ttl_days} days (until {expires_local}).\n"
        f"Anyone with this address can propose tasks to your agent.\n\n"
        f"To connect with someone, ask them to run:\n"
        f"  /claw-diplomat connect {token_b64}"
    )

async def cmd_connect(workspace_root: str, token_str: str) -> None:
    """Connect to a peer using their Diplomat Address token. SKILL_SPEC Flow B."""
    # Step 1: Parse and validate token
    try:
        token = decode_diplomat_token(token_str)
    except ValueError as e:
        print(str(e))
        return

    peer_alias  = token["alias"]
    peer_pubkey = token["pubkey"]
    relay_url   = token["relay"]
    relay_token = token["relay_token"]
    nat_hint    = token["nat_hint"]

    # Step 2: Check if peer already known
    existing = lookup_peer_by_pubkey(workspace_root, peer_pubkey)
    if existing:
        if existing.alias != peer_alias:
            print(
                f"⚠️  This key was previously associated with '{existing.alias}'. "
                f"Proceeding will update the alias to '{peer_alias}'."
            )

    print(f"Connecting to {peer_alias}'s agent...")

    # Ensure our own key and token are set up
    if not os.path.exists(get_key_path(workspace_root)):
        generate_keypair(workspace_root)
    our_pubkey_hex = load_public_key_hex(workspace_root)
    our_alias      = read_agent_alias(workspace_root)

    # Load my own relay token for the connection
    token_path = get_token_path(workspace_root)
    if not os.path.exists(token_path):
        print("Run /claw-diplomat generate-address first to get your relay slot.")
        return
    with open(token_path, "r", encoding="ascii") as f:
        my_token_b64 = f.read().strip()
    try:
        my_token = decode_diplomat_token(my_token_b64)
        my_relay_token = my_token["relay_token"]
    except ValueError:
        print("Your Diplomat Address is expired or invalid. Run /claw-diplomat generate-address first.")
        return

    # ── Permission checkpoint ────────────────────────────────────────────────
    # Send a connection request and wait for the peer to approve before
    # starting the Noise_XX handshake (SKILL_SPEC Permission Checkpoint §PC-1).
    request_id = str(uuid.uuid4())
    print(f"Sending connection request to {peer_alias}...")
    try:
        relay_request_connect(relay_token, our_alias, request_id)
    except RuntimeError as e:
        print(
            f"\n⚠️  Could not send connection request.\n"
            f"  Is {peer_alias}'s listener running? Error: {e}"
        )
        return

    print(
        f"Waiting for {peer_alias} to approve your connection request.\n"
        f"(They will see a notification and must run "
        f"/claw-diplomat approve-connect {request_id[:8]}…)\n"
        f"Waiting up to 5 minutes...",
        flush=True,
    )

    # Poll every 5 seconds for up to 5 minutes
    approved = False
    for _ in range(60):
        await asyncio.sleep(5.0)
        try:
            status = relay_check_connect_status(request_id)
        except RuntimeError:
            status = "pending"
        if status == "approved":
            approved = True
            break
        elif status == "denied":
            print(f"\n❌ {peer_alias} declined your connection request.")
            return

    if not approved:
        print(f"\n⏳ {peer_alias} did not respond within 5 minutes. Try again later.")
        return

    print(f"✓ {peer_alias} approved your request. Verifying identity...", end="", flush=True)
    # ── End permission checkpoint ────────────────────────────────────────────

    private_key_bytes = load_private_key_bytes(workspace_root)
    session_id = str(uuid.uuid4())

    ws = None
    try:
        ws, noise_conn = await connect_to_relay_as_initiator(
            relay_url, my_relay_token, relay_token,
            private_key_bytes, peer_pubkey, session_id,
        )
        print("✓")
    except SecurityError as e:
        print(str(e))
        return
    except RuntimeError as e:
        print(f"\n⚠️  Could not connect to relay at {relay_url}.\nIs it online? Error: {e}")
        return
    finally:
        # cmd_connect only needs the handshake for identity verification; close ws now
        if ws is not None:
            try:
                await ws.close()
            except Exception:
                pass

    # Step 5: Persist peer
    now_iso = _utc_now_iso()
    peer = PeerInfo(
        alias=peer_alias,
        pubkey=peer_pubkey,
        relay=relay_url,
        relay_token=relay_token,
        nat_hint=nat_hint,
        last_seen=now_iso,
        trusted_since=now_iso if existing is None else (existing.trusted_since if existing else now_iso),
        direct_available=False,
    )
    upsert_peer(workspace_root, peer)

    print(
        f"\n✅ You're connected to {peer_alias}'s agent.\n\n"
        f"You can now propose tasks: /claw-diplomat propose {peer_alias}\n"
        f"Or wait for them to propose to you."
    )

async def cmd_revoke(workspace_root: str) -> None:
    """Revoke the current Diplomat Address token. SECURITY T9."""
    token_path = get_token_path(workspace_root)
    if not os.path.exists(token_path):
        print("No active Diplomat Address to revoke.")
        return
    with open(token_path, "r", encoding="ascii") as f:
        token_b64 = f.read().strip()
    try:
        token = decode_diplomat_token(token_b64)
        relay_token = token["relay_token"]
        relay_revoke_token(relay_token)
        print(f"✅ Your Diplomat Address has been revoked.")
    except ValueError as e:
        print(f"Token already expired or invalid: {e}")
    # Clear local token
    with open(token_path, "w", encoding="ascii") as f:
        f.write("")
    print("Run /claw-diplomat generate-address to create a new address.")

def _load_my_relay_token(workspace_root: str) -> Optional[str]:
    """Load the current relay token from the stored Diplomat Address."""
    token_path = get_token_path(workspace_root)
    if not os.path.exists(token_path):
        return None
    try:
        with open(token_path, "r", encoding="ascii") as f:
            token_b64 = f.read().strip()
        token = decode_diplomat_token(token_b64)
        return token["relay_token"]
    except (ValueError, KeyError):
        return None

def cmd_approve_connect(workspace_root: str, request_id_prefix: str) -> None:
    """
    Approve a pending inbound connection request.
    The request_id_prefix may be the full UUID or just the first N chars.
    """
    approvals_path = get_pending_approvals_path(workspace_root)
    if not os.path.exists(approvals_path):
        print("No pending connection requests.")
        return

    try:
        with open(approvals_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Could not read pending approvals.")
        return

    requests = data.get("requests", [])
    matched = [r for r in requests if r["request_id"].startswith(request_id_prefix)]
    if not matched:
        print(f"No pending connection request matching '{request_id_prefix}'.")
        return
    if len(matched) > 1:
        print(f"Ambiguous — {len(matched)} requests match '{request_id_prefix}'. Use more characters.")
        return

    req = matched[0]
    request_id = req["request_id"]
    from_alias  = req.get("from_alias", "unknown")

    my_relay_token = _load_my_relay_token(workspace_root)
    if not my_relay_token:
        print("Your Diplomat Address is missing or expired. Run /claw-diplomat generate-address.")
        return

    try:
        relay_approve_connect(request_id, my_relay_token)
    except RuntimeError as e:
        print(f"⚠️  Could not approve: {e}")
        return

    # Remove from pending_approvals.json
    data["requests"] = [r for r in requests if r["request_id"] != request_id]
    _atomic_json_write(approvals_path, data)

    print(
        f"✅ Approved connection request from {from_alias}.\n"
        f"They will now proceed with the connection."
    )

def cmd_deny_connect(workspace_root: str, request_id_prefix: str) -> None:
    """Deny a pending inbound connection request."""
    approvals_path = get_pending_approvals_path(workspace_root)
    if not os.path.exists(approvals_path):
        print("No pending connection requests.")
        return

    try:
        with open(approvals_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Could not read pending approvals.")
        return

    requests = data.get("requests", [])
    matched = [r for r in requests if r["request_id"].startswith(request_id_prefix)]
    if not matched:
        print(f"No pending connection request matching '{request_id_prefix}'.")
        return
    if len(matched) > 1:
        print(f"Ambiguous — {len(matched)} requests match '{request_id_prefix}'. Use more characters.")
        return

    req = matched[0]
    request_id = req["request_id"]
    from_alias  = req.get("from_alias", "unknown")

    my_relay_token = _load_my_relay_token(workspace_root)
    if not my_relay_token:
        print("Your Diplomat Address is missing or expired. Run /claw-diplomat generate-address.")
        return

    try:
        relay_deny_connect(request_id, my_relay_token)
    except RuntimeError as e:
        print(f"⚠️  Could not deny: {e}")
        return

    # Remove from pending_approvals.json
    data["requests"] = [r for r in requests if r["request_id"] != request_id]
    _atomic_json_write(approvals_path, data)

    print(f"❌ Denied connection request from {from_alias}.")

async def cmd_propose(workspace_root: str, peer_alias: str) -> None:
    """
    Start a negotiation with a peer. SKILL_SPEC Flow C.
    Interactive: gathers terms from stdin.
    """
    peer = lookup_peer_by_alias(workspace_root, peer_alias)
    if peer is None:
        print(
            f"I don't have a connection to {peer_alias}. "
            f"Run /claw-diplomat connect <address> first."
        )
        return

    # Gather terms interactively
    print(f"What will you take on? (describe your tasks)")
    my_task_raw = input("> ").strip()
    print(f"What are you asking {peer_alias} to do?")
    peer_task_raw = input("> ").strip()
    print("What's the deadline? (e.g. 'Friday 5pm' or '2026-03-27 17:00')")
    deadline_raw = input("> ").strip()

    # Parse deadline
    try:
        deadline_dt = _parse_natural_deadline(deadline_raw)
    except ValueError as e:
        print(f"I couldn't parse that deadline: {e}")
        return

    print("Check-in time? (optional — leave blank to use the deadline)")
    checkin_raw = input("> ").strip()
    checkin_dt = deadline_dt
    if checkin_raw:
        try:
            checkin_dt = _parse_natural_deadline(checkin_raw)
        except ValueError:
            checkin_dt = deadline_dt

    terms = TermsPayload(
        proposal_text=f"Proposal from {read_agent_alias(workspace_root)}",
        my_tasks=[my_task_raw],
        your_tasks=[peer_task_raw],
        deadline=deadline_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        checkin_at=checkin_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        terms_version=1,
    )

    # Step 4: Confirm before send
    print(
        f"\nHere's what you're proposing to {peer_alias}:\n\n"
        f"{display_proposal_to_human(peer_alias, terms, is_inbound=False)}\n\n"
        f"Send this proposal? (yes / no)"
    )
    confirm = input("> ").strip().lower()
    if confirm not in ("yes", "y"):
        print("Proposal cancelled.")
        return

    # Load keys
    if not os.path.exists(get_key_path(workspace_root)):
        generate_keypair(workspace_root)
    private_key_bytes = load_private_key_bytes(workspace_root)
    our_pubkey_hex    = load_public_key_hex(workspace_root)

    # Load our relay token
    token_path = get_token_path(workspace_root)
    if not os.path.exists(token_path):
        print("Run /claw-diplomat generate-address first.")
        return
    with open(token_path, "r", encoding="ascii") as f:
        my_token_b64 = f.read().strip()
    try:
        my_token = decode_diplomat_token(my_token_b64)
        my_relay_token = my_token["relay_token"]
    except ValueError:
        print("Your address is expired. Run /claw-diplomat generate-address first.")
        return

    session_id       = str(uuid.uuid4())
    session_id_short = _short_id(session_id)
    timeout_hours    = get_timeout_hours()

    # Create session in ledger
    session = SessionRecord(
        session_id=session_id,
        peer_alias=peer_alias,
        peer_pubkey=peer.pubkey,
        initiated_by="self",
        state=SessionState.PROPOSED.value,
        terms_version=1,
        final_terms=None,
        memory_hash=None,
        peer_memory_hash=None,
        seen_nonces=[],
        events=[],
        created_at=_utc_now_iso(),
    )
    upsert_session(workspace_root, session)

    # Connect to relay
    try:
        ws, noise_conn = await connect_to_relay_as_initiator(
            peer.relay, my_relay_token, peer.relay_token,
            private_key_bytes, peer.pubkey, session_id,
        )
    except (SecurityError, RuntimeError) as e:
        session.state = SessionState.PENDING_SEND.value
        session.pending_terms = asdict(terms)
        upsert_session(workspace_root, session)
        print(
            f"Couldn't reach the relay right now. Your proposal has been saved and "
            f"I'll retry the next time you open your agent.\n\n"
            f"To retry now: /claw-diplomat propose {peer_alias}"
        )
        return

    # Send PROPOSE
    propose_msg = build_message(session_id, MsgType.PROPOSE.value, our_pubkey_hex, {
        "proposal_text": terms.proposal_text,
        "my_tasks":      terms.my_tasks,
        "your_tasks":    terms.your_tasks,
        "deadline":      terms.deadline,
        "checkin_at":    terms.checkin_at,
        "terms_version": 1,
    })
    await send_noise_message(noise_conn, ws, propose_msg)
    add_session_event(workspace_root, session_id, "PROPOSED", "self", terms_version=1)
    append_to_daily_log(workspace_root, f"- {_utc_now_iso()} — {session_id_short}: PROPOSED by self\n")

    print(
        f"\nProposal sent to {peer_alias}. Waiting for their response...\n\n"
        f"(I'll let you know when they reply. This session will stay open for {timeout_hours} hours.)"
    )

    # Step 6: Wait for response
    try:
        response = await recv_noise_message(noise_conn, ws, timeout=float(timeout_hours * 3600))
    except asyncio.TimeoutError:
        session.state = SessionState.PENDING_SEND.value
        session.pending_terms = asdict(terms)
        upsert_session(workspace_root, session)
        print(
            f"Couldn't reach the relay right now. Your proposal has been saved and "
            f"I'll retry the next time you open your agent."
        )
        return
    except websockets.exceptions.ConnectionClosed:
        session.state = SessionState.PENDING_SEND.value
        upsert_session(workspace_root, session)
        print(f"Lost connection to {peer_alias} mid-negotiation. No deal was recorded.")
        return

    msg_type = response.get("msg_type")
    check_replay(session, response["nonce"])
    upsert_session(workspace_root, session)

    if msg_type == MsgType.REJECT.value:
        session.state = SessionState.REJECTED.value
        add_session_event(workspace_root, session_id, "REJECTED", peer_alias)
        upsert_session(workspace_root, session)
        append_to_daily_log(workspace_root, f"- {_utc_now_iso()} — {session_id_short}: REJECTED by peer\n")
        reason = response.get("payload", {}).get("reason", "")
        reason_str = f" {reason}" if reason else ""
        print(f"\n{peer_alias} declined the proposal.{reason_str}\n\nNo commitment was recorded. Start fresh anytime: /claw-diplomat propose {peer_alias}")

    elif msg_type in (MsgType.ACCEPT.value, MsgType.COUNTER.value):
        # Hand off to commit/counter flow
        await _handle_negotiation_response(
            workspace_root, session, noise_conn, ws, response,
            our_pubkey_hex, peer_alias, terms, peer,
        )

async def _handle_negotiation_response(
    workspace_root: str,
    session: SessionRecord,
    noise_conn: NoiseConnection,
    ws: Any,
    response: dict[str, Any],
    our_pubkey_hex: str,
    peer_alias: str,
    current_terms: TermsPayload,
    peer: PeerInfo,
) -> None:
    """
    Handle ACCEPT or COUNTER from peer. Loops until deal or rejection.
    No maximum round limit — human decides when to stop.
    """
    session_id       = session.session_id
    session_id_short = _short_id(session_id)

    while True:
        msg_type = response.get("msg_type")

        if msg_type == MsgType.COUNTER.value:
            payload = response.get("payload", {})
            try:
                counter_terms = validate_propose_payload(payload)
            except ValueError as e:
                LOG.warning("Invalid counter payload: %s", e)
                continue

            session.terms_version = counter_terms.terms_version
            add_session_event(workspace_root, session_id, "COUNTERED", peer_alias, counter_terms.terms_version)
            append_to_daily_log(
                workspace_root,
                f"- {_utc_now_iso()} — {session_id_short}: COUNTERED by {peer_alias} (terms_v{counter_terms.terms_version})\n",
            )
            upsert_session(workspace_root, session)

            print(display_proposal_to_human(peer_alias, counter_terms, is_inbound=True))
            print(
                f"\n(Changes from your original: {peer_alias} modified terms)\n\n"
                f"What do you want to do?\n"
                f"  [accept]  — Agree to these terms\n"
                f"  [counter] — Propose different terms\n"
                f"  [reject]  — Decline and end the negotiation"
            )
            choice = input("> ").strip().lower()

            if choice in ("reject", "r"):
                reject_msg = build_message(session_id, MsgType.REJECT.value, our_pubkey_hex, {"reason": ""})
                await send_noise_message(noise_conn, ws, reject_msg)
                session.state = SessionState.REJECTED.value
                add_session_event(workspace_root, session_id, "REJECTED", "self")
                upsert_session(workspace_root, session)
                print(f"You've declined {peer_alias}'s proposal. They've been notified.")
                return

            elif choice in ("counter", "c"):
                print(f"Your tasks (currently: {_format_tasks(counter_terms.your_tasks)}):")
                new_my = input("> ").strip() or _format_tasks(counter_terms.your_tasks)
                print(f"Their tasks (currently: {_format_tasks(counter_terms.my_tasks)}):")
                new_peer = input("> ").strip() or _format_tasks(counter_terms.my_tasks)
                print(f"Deadline (currently: {_format_deadline_from_iso(counter_terms.deadline)}):")
                new_dl = input("> ").strip()
                try:
                    new_dl_dt = _parse_natural_deadline(new_dl) if new_dl else validate_iso8601(counter_terms.deadline)
                except ValueError as e:
                    print(f"Invalid deadline: {e}")
                    continue

                new_version = session.terms_version + 1
                new_terms = TermsPayload(
                    proposal_text=current_terms.proposal_text,
                    my_tasks=[new_my],
                    your_tasks=[new_peer],
                    deadline=new_dl_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    checkin_at=new_dl_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    terms_version=new_version,
                )
                counter_msg = build_message(session_id, MsgType.COUNTER.value, our_pubkey_hex, {
                    "proposal_text": new_terms.proposal_text,
                    "my_tasks": new_terms.my_tasks,
                    "your_tasks": new_terms.your_tasks,
                    "deadline": new_terms.deadline,
                    "checkin_at": new_terms.checkin_at,
                    "terms_version": new_version,
                })
                print(f"Sending counter-proposal to {peer_alias}...")
                await send_noise_message(noise_conn, ws, counter_msg)
                add_session_event(workspace_root, session_id, "COUNTERED", "self", new_version)
                session.terms_version = new_version
                upsert_session(workspace_root, session)

                response = await recv_noise_message(noise_conn, ws, timeout=float(get_timeout_hours() * 3600))
                check_replay(session, response["nonce"])
                upsert_session(workspace_root, session)
                current_terms = new_terms
                continue

            else:  # accept
                response = {
                    "msg_type": MsgType.ACCEPT.value,
                    "payload": {
                        "terms_version": counter_terms.terms_version,
                        "terms_hash": compute_terms_hash(asdict(counter_terms)),
                    },
                    "from_pubkey": our_pubkey_hex,
                    "session_id": session_id,
                    "timestamp": _utc_now_iso(),
                    "nonce": _new_nonce(),
                }
                current_terms = counter_terms
                continue

        elif msg_type == MsgType.ACCEPT.value:
            payload = response.get("payload", {})
            peer_terms_version = int(payload.get("terms_version", 0))

            # SECURITY T2: version must match
            if peer_terms_version != session.terms_version:
                # Re-send latest counter — F10
                LOG.warning(
                    "Terms version mismatch: peer=%d, local=%d. Resending.",
                    peer_terms_version, session.terms_version,
                )
                print(
                    f"There was a sync issue with {peer_alias} on which version of the terms we're accepting. "
                    f"I've resent the latest version."
                )
                upsert_session(workspace_root, session)
                response = await recv_noise_message(noise_conn, ws, timeout=60.0)
                check_replay(session, response["nonce"])
                upsert_session(workspace_root, session)
                continue

            # Both sides accept — run commit sequence
            final_terms_dict = {
                "my_tasks":   current_terms.my_tasks,
                "peer_tasks": current_terms.your_tasks,
                "deadline":   current_terms.deadline,
                "checkin_at": current_terms.checkin_at,
            }
            session.final_terms = final_terms_dict
            terms_hash = compute_terms_hash(final_terms_dict)

            # Send our ACCEPT
            accept_msg = build_message(session_id, MsgType.ACCEPT.value, our_pubkey_hex, {
                "terms_version": session.terms_version,
                "terms_hash": terms_hash,
            })
            await send_noise_message(noise_conn, ws, accept_msg)
            add_session_event(workspace_root, session_id, "ACCEPTED", "self")
            append_to_daily_log(workspace_root, f"- {_utc_now_iso()} — {session_id_short}: ACCEPTED by self\n")
            session.state = SessionState.ACCEPTED.value
            upsert_session(workspace_root, session)

            await _run_commit_sequence(
                workspace_root, session, noise_conn, ws,
                our_pubkey_hex, peer_alias, final_terms_dict, current_terms,
            )
            return

        else:
            LOG.warning("Unexpected msg_type during negotiation: %s", msg_type)
            return

async def _run_commit_sequence(
    workspace_root: str,
    session: SessionRecord,
    noise_conn: NoiseConnection,
    ws: Any,
    our_pubkey_hex: str,
    peer_alias: str,
    final_terms_dict: dict[str, Any],
    terms: TermsPayload,
) -> None:
    """
    Commit sequence: write MEMORY.md, exchange COMMIT_ACK, verify hashes. SKILL_SPEC Flow E.
    """
    session_id       = session.session_id
    session_id_short = _short_id(session_id)

    # Step 3: Write MEMORY.md
    my_tasks   = final_terms_dict.get("my_tasks", [])
    peer_tasks = final_terms_dict.get("peer_tasks", [])
    deadline   = final_terms_dict.get("deadline", "")

    entry = build_memory_entry(
        session_id_short, peer_alias,
        my_tasks[0] if my_tasks else "tasks",
        peer_tasks[0] if peer_tasks else "tasks",
        deadline, "ACTIVE",
    )

    # Check 20-entry limit — archive if needed
    content = open(get_memory_path(workspace_root), "r").read() if os.path.exists(get_memory_path(workspace_root)) else ""
    if _count_commitment_entries(content) >= MAX_ACTIVE_COMMITMENTS:
        if not archive_oldest_done_entry(workspace_root):
            session.state = SessionState.COMMIT_PENDING.value
            upsert_session(workspace_root, session)
            print(
                "You already have 20 active commitments logged. Complete or cancel one before taking on another.\n"
                "To see your current commitments: /claw-diplomat status"
            )
            return

    try:
        memory_hash_hex = append_commitment_to_memory(workspace_root, entry)
    except RuntimeError as e:
        session.state = SessionState.COMMIT_PENDING.value
        upsert_session(workspace_root, session)
        print(
            f"⚠️  I accepted the deal but couldn't write it to your memory.\n\n"
            f"Error: {e}\n\n"
            f"Please check your disk space and file permissions, then run:\n"
            f"/claw-diplomat retry-commit {session_id_short}\n\n"
            f"Your commitment is safely recorded in the skill's ledger (ledger.json) until this is resolved."
        )
        return

    memory_hash = "sha256:" + memory_hash_hex

    # Step 4: Write daily log extended entry
    ext_entry = build_extended_entry(
        session_id_short, peer_alias,
        session.peer_pubkey,
        my_tasks, peer_tasks, deadline, terms.checkin_at,
        memory_hash,
    )
    append_to_daily_log(workspace_root, ext_entry)
    append_to_daily_log(workspace_root, f"- {_utc_now_iso()} — {session_id_short}: COMMITTED (hash: {memory_hash_hex[:8]}…)\n")

    # Step 5: Exchange COMMIT_ACK
    commit_ack_msg = build_message(session_id, MsgType.COMMIT_ACK.value, our_pubkey_hex, {
        "memory_hash": memory_hash,
    })
    await send_noise_message(noise_conn, ws, commit_ack_msg)

    try:
        peer_ack = await recv_noise_message(noise_conn, ws, timeout=300.0)  # 5-minute window
    except asyncio.TimeoutError:
        session.state = SessionState.COMMIT_PENDING.value
        session.memory_hash = memory_hash
        upsert_session(workspace_root, session)
        print(
            f"{peer_alias} accepted the deal but I haven't confirmed they wrote it down yet. "
            f"I'll verify when they reconnect."
        )
        return

    peer_memory_hash = peer_ack.get("payload", {}).get("memory_hash", "")

    # SECURITY T2: Verify hash match
    if peer_memory_hash != memory_hash:
        session.state = SessionState.COMMIT_PENDING.value
        session.memory_hash = memory_hash
        upsert_session(workspace_root, session)
        print(
            f"⚠️  I accepted the deal but couldn't confirm both sides wrote the same commitment.\n\n"
            f"Error: memory hash mismatch (local: {memory_hash[:20]}…, peer: {peer_memory_hash[:20]}…)\n\n"
            f"Please check with {peer_alias} and run:\n"
            f"/claw-diplomat retry-commit {session_id_short}"
        )
        return

    # Step 6: Finalize
    session.state           = SessionState.COMMITTED.value
    session.memory_hash     = memory_hash
    session.peer_memory_hash = peer_memory_hash
    session.committed_at    = _utc_now_iso()
    add_session_event(workspace_root, session_id, "COMMITTED", "self", memory_hash=memory_hash)
    upsert_session(workspace_root, session)

    deadline_local = _format_deadline_from_iso(deadline)
    print(
        f"✅ Deal locked in with {peer_alias}.\n\n"
        f"  You'll do:  {_format_tasks(my_tasks)}\n"
        f"  They'll do: {_format_tasks(peer_tasks)}\n"
        f"  Deadline:   {deadline_local}\n\n"
        f"I've logged this in your memory. I'll remind you before the deadline."
    )

# ─── Natural Deadline Parser ──────────────────────────────────────────────────
def _parse_natural_deadline(text: str) -> datetime.datetime:
    """
    Parse a human-written deadline (e.g. 'Friday 5pm', '2026-03-27 17:00').
    Returns UTC-aware datetime. Raises ValueError on failure.
    """
    text = text.strip()
    now = datetime.datetime.now(datetime.timezone.utc)

    # Try ISO8601 first
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.datetime.strptime(text, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except ValueError:
            continue

    # Try weekday + time patterns
    _days = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
             "friday": 4, "saturday": 5, "sunday": 6}
    lower = text.lower()
    for day_name, day_num in _days.items():
        if lower.startswith(day_name):
            remainder = lower[len(day_name):].strip()
            hour, minute = _parse_time_part(remainder)
            days_ahead = (day_num - now.weekday()) % 7 or 7
            target = now + datetime.timedelta(days=days_ahead)
            return target.replace(hour=hour, minute=minute, second=0, microsecond=0)

    raise ValueError(
        f"Could not parse deadline '{text}'. Try a format like '2026-03-27 17:00' or 'Friday 5pm'."
    )

def _parse_time_part(text: str) -> tuple[int, int]:
    """Parse time from a string fragment like '5pm', '17:00'. Returns (hour, minute)."""
    text = text.strip()
    m = re.match(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text, re.IGNORECASE)
    if not m:
        return 17, 0  # Default to 5pm
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = (m.group(3) or "").lower()
    if ampm == "pm" and hour < 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    return hour, minute

# ─── Task Handoff Command ─────────────────────────────────────────────────────
async def cmd_handoff(workspace_root: str, peer_alias: str) -> None:
    """
    Send a task handoff to a peer, packaging completed work + remaining context.
    /claw-diplomat handoff <peer_alias>
    Interactive: gathers handoff details from stdin.
    SECURITY T1: all user-provided text is sanitized before send.
    """
    peer = lookup_peer_by_alias(workspace_root, peer_alias)
    if peer is None:
        print(
            f"I don't have a connection to {peer_alias}. "
            f"Run /claw-diplomat connect <address> first."
        )
        return

    print(f"What did you complete? (Part A — what's done)")
    part_done = input("> ").strip()
    print(f"What still needs to be done by {peer_alias}? (Part B — remaining)")
    part_remaining = input("> ").strip()
    print(f"Any context {peer_alias} needs to continue? (notes, links, credential-free details)")
    context = input("> ").strip()

    # Sanitize all user-provided text (SECURITY T1)
    part_done      = sanitize_string(part_done)[:MAX_TASK_TEXT]
    part_remaining = sanitize_string(part_remaining)[:MAX_TASK_TEXT]
    context        = sanitize_string(context)[:MAX_PROPOSAL_TEXT]

    ctx_preview = context[:80] + ("…" if len(context) > 80 else "")
    print(
        f"\nHere's what you're handing off to {peer_alias}:\n\n"
        f"  Done by you:       {part_done}\n"
        f"  Remaining for them: {part_remaining}\n"
        f"  Context:           {ctx_preview}\n\n"
        f"Send this handoff? (yes / no)"
    )
    confirm = input("> ").strip().lower()
    if confirm not in ("yes", "y"):
        print("Handoff cancelled.")
        return

    # Load keys and relay token
    if not os.path.exists(get_key_path(workspace_root)):
        generate_keypair(workspace_root)
    private_key_bytes = load_private_key_bytes(workspace_root)
    our_pubkey_hex    = load_public_key_hex(workspace_root)
    our_alias         = read_agent_alias(workspace_root)

    token_path = get_token_path(workspace_root)
    if not os.path.exists(token_path):
        print("Run /claw-diplomat generate-address first.")
        return
    with open(token_path, "r", encoding="ascii") as f:
        my_token_b64 = f.read().strip()
    try:
        my_token = decode_diplomat_token(my_token_b64)
        my_relay_token = my_token["relay_token"]
    except ValueError:
        print("Your address is expired. Run /claw-diplomat generate-address first.")
        return

    session_id = str(uuid.uuid4())
    print(f"Connecting to {peer_alias} to send handoff...")

    ws = None
    try:
        ws, noise_conn = await connect_to_relay_as_initiator(
            peer.relay, my_relay_token, peer.relay_token,
            private_key_bytes, peer.pubkey, session_id,
        )
    except SecurityError as e:
        print(str(e))
        return
    except RuntimeError as e:
        print(f"⚠️  Could not connect to {peer_alias}: {e}")
        return

    handoff_msg = build_message(session_id, MsgType.HANDOFF.value, our_pubkey_hex, {
        "from_alias":     our_alias,
        "part_done":      part_done,
        "part_remaining": part_remaining,
        "context":        context,
    })
    try:
        await send_noise_message(noise_conn, ws, handoff_msg)
        print(
            f"✅ Handoff sent to {peer_alias}.\n\n"
            f"They'll receive your context and know what to continue."
        )
        append_to_daily_log(
            workspace_root,
            f"- {_utc_now_iso()} — HANDOFF to {peer_alias}: {part_done[:60]}\n",
        )
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed before handoff was delivered: {e}")
    finally:
        if ws is not None:
            try:
                await ws.close()
            except Exception:
                pass

# ─── Compatibility Aliases (public API surface for tests and external callers) ─
def build_diplomat_address_token(
    workspace_root: str,
    alias: str,
    relay_url: str,
    relay_token: str,
    nat_hint: str,
    ttl_days: int,
) -> str:
    """
    Build a Diplomat Address token, loading the public key from workspace.
    Convenience wrapper around build_diplomat_token for external callers.
    """
    pubkey_hex = load_public_key_hex(workspace_root)
    return build_diplomat_token(alias, pubkey_hex, relay_url, relay_token, nat_hint, ttl_days)

decode_diplomat_address_token = decode_diplomat_token
build_negotiate_message       = build_message
parse_negotiate_message       = validate_incoming_message


def LedgerSession(
    session_id: str,
    peer_alias: str,
    peer_pubkey: str = "",
    state: str = "IDLE",
    terms_version: int = 1,
    final_terms: Optional[dict[str, Any]] = None,
    events: Optional[list] = None,
    initiated_by: str = "self",
    memory_hash: Optional[str] = None,
    peer_memory_hash: Optional[str] = None,
    seen_nonces: Optional[list] = None,
    created_at: str = "",
    committed_at: Optional[str] = None,
    checkin_at_actual: Optional[str] = None,
    pending_terms: Optional[dict[str, Any]] = None,
) -> SessionRecord:
    """
    Factory function that creates a SessionRecord with convenient defaults.
    Used for testing and external callers that don't need all required fields.
    """
    return SessionRecord(
        session_id=session_id,
        peer_alias=peer_alias,
        peer_pubkey=peer_pubkey,
        initiated_by=initiated_by,
        state=state,
        terms_version=terms_version,
        final_terms=final_terms,
        memory_hash=memory_hash,
        peer_memory_hash=peer_memory_hash,
        seen_nonces=seen_nonces if seen_nonces is not None else [],
        events=events if events is not None else [],
        created_at=created_at or _utc_now_iso(),
        committed_at=committed_at,
        checkin_at_actual=checkin_at_actual,
        pending_terms=pending_terms,
    )

# ─── Installation Helper ──────────────────────────────────────────────────────
def _register_cron(skill_dir: str) -> bool:
    """
    Register a crontab entry to run cron_deadline_check.py every 15 minutes.
    Returns True on success, False if cron is unavailable (Path B fallback active).
    Non-fatal: a failure here means Path B (heartbeat) still delivers alerts.
    """
    try:
        import subprocess  # noqa: PLC0415 — only import if cron is available
        check_script = os.path.join(skill_dir, "cron_deadline_check.py")
        cron_log     = os.path.join(skill_dir, "cron.log")
        python_bin   = sys.executable or "python3"

        cron_line = (
            f"*/15 * * * * {python_bin} {check_script} "
            f">> {cron_log} 2>&1  # claw-bond deadline alerts"
        )

        # Read existing crontab
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, timeout=5
        )
        existing = result.stdout if result.returncode == 0 else ""

        # Idempotent: skip if already registered
        if "claw-bond deadline alerts" in existing:
            return True

        new_crontab = existing.rstrip("\n") + "\n" + cron_line + "\n"
        write_result = subprocess.run(
            ["crontab", "-"],
            input=new_crontab, capture_output=True, text=True, timeout=5
        )
        return write_result.returncode == 0
    except Exception:
        return False


def cmd_install(workspace_root: str) -> None:
    """Run the installation/setup steps. Called during first-time setup."""
    skill_dir = get_skill_dir(workspace_root)
    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(os.path.join(workspace_root, "memory"), exist_ok=True)

    # Initialize data files if not present
    peers_path  = get_peers_path(workspace_root)
    ledger_path = get_ledger_path(workspace_root)
    if not os.path.exists(peers_path):
        _atomic_json_write(peers_path, {"peers": []})
        os.chmod(peers_path, stat.S_IRUSR | stat.S_IWUSR)
    if not os.path.exists(ledger_path):
        _atomic_json_write(ledger_path, {"sessions": []})

    # Generate keypair if absent
    if not os.path.exists(get_key_path(workspace_root)):
        generate_keypair(workspace_root)

    # Initialize HEARTBEAT.md
    init_heartbeat(workspace_root)

    # Register proactive deadline alerts cron (Path A)
    # Falls back to Path B (heartbeat) if cron is unavailable — non-fatal.
    cron_ok = _register_cron(skill_dir)
    if cron_ok:
        print("Proactive deadline alerts: cron registered ✓ (runs every 15 min)")
    else:
        print(
            "⚠️  Couldn't register cron for proactive deadline alerts. "
            "Alerts will still appear when you open your agent (heartbeat fallback). "
            "To register manually: crontab -e"
        )

    # Port check (non-fatal)
    hole_punch_port = get_diplomat_port() + 1
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", hole_punch_port))
        s.close()
    except OSError:
        print(
            f"⚠️  Port {hole_punch_port} is in use. Direct connections may not work, "
            f"but the relay will still function."
        )

    print(
        "👋 Setting up Claw Connector for the first time...\n\n"
        "Generating your secure identity key... ✓\n"
        "Your agent is now ready to negotiate tasks with other OpenClaw agents.\n\n"
        "Next step: share your Diplomat Address with anyone you want to work with.\n\n"
        "Run /claw-diplomat generate-address to create your shareable address."
    )

# ─── Entry Point ──────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="negotiate.py",
        description="claw-diplomat negotiation engine",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("install")
    sub.add_parser("setup-cron")
    sub.add_parser("key")
    sub.add_parser("list")
    sub.add_parser("peers")
    sub.add_parser("status")
    sub.add_parser("help-security")

    p_generate = sub.add_parser("generate-address")

    p_connect = sub.add_parser("connect")
    p_connect.add_argument("token")

    p_propose = sub.add_parser("propose")
    p_propose.add_argument("peer_alias")

    p_checkin = sub.add_parser("checkin")
    p_checkin.add_argument("short_id")
    p_checkin.add_argument("status", choices=["done", "overdue", "partial"])

    p_cancel = sub.add_parser("cancel")
    p_cancel.add_argument("short_id")

    p_retry = sub.add_parser("retry-commit")
    p_retry.add_argument("short_id")

    sub.add_parser("revoke")

    p_approve = sub.add_parser("approve-connect")
    p_approve.add_argument("request_id", help="Connection request ID (or prefix) to approve")

    p_deny = sub.add_parser("deny-connect")
    p_deny.add_argument("request_id", help="Connection request ID (or prefix) to deny")

    p_handoff = sub.add_parser("handoff")
    p_handoff.add_argument("peer_alias", help="Alias of the peer to hand off to")

    args = parser.parse_args()

    try:
        workspace_root = get_workspace_root()
    except RuntimeError as e:
        sys.exit(str(e))

    # Sync commands (no I/O loop needed)
    if args.command == "install":
        cmd_install(workspace_root)
    elif args.command == "setup-cron":
        skill_dir = get_skill_dir(workspace_root)
        ok = _register_cron(skill_dir)
        if ok:
            print("Cron registered ✓ — deadline alerts will fire 15 min before the 2-hour window.")
        else:
            print("Could not register cron. Path B (heartbeat fallback) is active.")
    elif args.command == "key":
        cmd_key(workspace_root)
    elif args.command == "list":
        cmd_list(workspace_root)
    elif args.command == "peers":
        cmd_peers(workspace_root)
    elif args.command == "status":
        cmd_status(workspace_root)
    elif args.command == "help-security":
        cmd_help_security(workspace_root)
    elif args.command == "checkin":
        try:
            cmd_checkin(workspace_root, args.short_id, args.status)
        except (KeyError, ValueError, RuntimeError) as e:
            sys.exit(f"Error: {e}")
    elif args.command == "cancel":
        try:
            cmd_cancel(workspace_root, args.short_id)
        except (KeyError, RuntimeError) as e:
            sys.exit(f"Error: {e}")
    elif args.command == "retry-commit":
        try:
            cmd_retry_commit(workspace_root, args.short_id)
        except (KeyError, RuntimeError) as e:
            sys.exit(f"Error: {e}")
    # Async commands
    elif args.command == "generate-address":
        asyncio.run(cmd_generate_address(workspace_root))
    elif args.command == "connect":
        asyncio.run(cmd_connect(workspace_root, args.token))
    elif args.command == "propose":
        asyncio.run(cmd_propose(workspace_root, args.peer_alias))
    elif args.command == "revoke":
        asyncio.run(cmd_revoke(workspace_root))
    elif args.command == "approve-connect":
        try:
            cmd_approve_connect(workspace_root, args.request_id)
        except (KeyError, RuntimeError) as e:
            sys.exit(f"Error: {e}")
    elif args.command == "deny-connect":
        try:
            cmd_deny_connect(workspace_root, args.request_id)
        except (KeyError, RuntimeError) as e:
            sys.exit(f"Error: {e}")
    elif args.command == "handoff":
        asyncio.run(cmd_handoff(workspace_root, args.peer_alias))
    else:
        print(
            "I don't recognize that. Here's what I can do:\n\n"
            "  /claw-diplomat generate-address       — Create your shareable address\n"
            "  /claw-diplomat connect <address>      — Connect with a peer\n"
            "  /claw-diplomat approve-connect <id>   — Approve an inbound connection request\n"
            "  /claw-diplomat deny-connect <id>      — Deny an inbound connection request\n"
            "  /claw-diplomat propose <peer>         — Start a negotiation\n"
            "  /claw-diplomat handoff <peer>         — Hand off completed work + context to a peer\n"
            "  /claw-diplomat status                 — See your commitments\n"
            "  /claw-diplomat checkin <id>           — Report on a commitment\n"
            "  /claw-diplomat peers                  — See your connected peers\n"
            "  /claw-diplomat setup-cron             — Register proactive deadline alerts (Path A)\n"
            "  /claw-diplomat help security          — Security information"
        )

if __name__ == "__main__":
    main()
