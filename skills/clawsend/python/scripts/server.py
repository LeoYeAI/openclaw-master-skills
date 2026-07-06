#!/usr/bin/env python3
"""
ClawHub Relay Server - OpenClaw Messaging v1

A centralized message relay for OpenClaw agents. Features:
- Challenge-response registration (no identity hijacking)
- Signed message verification
- Rate limiting per sender
- TTL-based message expiry
- Conversation logging
- SQLite with WAL mode for concurrent reads
"""

import os
import sys
import json
import uuid
import sqlite3
import threading
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Optional

from flask import Flask, request, jsonify, g

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib import crypto
from lib import envelope as env

# =============================================================================
# Configuration
# =============================================================================

app = Flask(__name__)

# Database path (configurable via environment)
DATABASE_PATH = os.environ.get('CLAWHUB_DB', 'clawhub.db')

# Rate limiting
RATE_LIMIT_MESSAGES = int(os.environ.get('CLAWHUB_RATE_LIMIT', '60'))  # per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Challenge expiry
CHALLENGE_EXPIRY = 300  # 5 minutes

# Message limits
MAX_MESSAGE_SIZE = 64 * 1024  # 64KB

# Background cleanup interval
CLEANUP_INTERVAL = 60  # seconds


# =============================================================================
# Database
# =============================================================================

def get_db():
    """Get database connection for current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
        # Enable WAL mode for concurrent reads
        g.db.execute('PRAGMA journal_mode=WAL')
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database schema."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute('PRAGMA journal_mode=WAL')

    # Agents table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            vault_id TEXT PRIMARY KEY,
            alias TEXT UNIQUE,
            signing_public_key TEXT NOT NULL,
            encryption_public_key TEXT NOT NULL,
            registered_at TEXT NOT NULL,
            last_seen_at TEXT
        )
    ''')

    # Pending challenges for registration
    conn.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            vault_id TEXT PRIMARY KEY,
            challenge TEXT NOT NULL,
            signing_public_key TEXT NOT NULL,
            encryption_public_key TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    # Messages table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender_vault_id TEXT NOT NULL,
            recipient_vault_id TEXT NOT NULL,
            message_type TEXT NOT NULL,
            intent TEXT NOT NULL,
            correlation_id TEXT,
            message_json TEXT NOT NULL,
            signature TEXT NOT NULL,
            encrypted_payload_json TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            delivered_at TEXT,
            acknowledged_at TEXT,
            FOREIGN KEY (sender_vault_id) REFERENCES agents(vault_id),
            FOREIGN KEY (recipient_vault_id) REFERENCES agents(vault_id)
        )
    ''')

    # Rate limiting table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rate_limits (
            vault_id TEXT NOT NULL,
            window_start TEXT NOT NULL,
            message_count INTEGER DEFAULT 0,
            PRIMARY KEY (vault_id, window_start)
        )
    ''')

    # Conversation logs
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            participant_a TEXT NOT NULL,
            participant_b TEXT NOT NULL,
            started_at TEXT NOT NULL,
            last_message_at TEXT,
            message_count INTEGER DEFAULT 0,
            outcome TEXT
        )
    ''')

    # Create indexes
    conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_recipient ON messages(recipient_vault_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_vault_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_expires ON messages(expires_at)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_messages_correlation ON messages(correlation_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_agents_alias ON agents(alias)')

    conn.commit()
    conn.close()


# =============================================================================
# Helpers
# =============================================================================

def json_response(data: dict, status: int = 200):
    """Create JSON response."""
    return jsonify(data), status


def error_response(message: str, status: int = 400, code: str = "error"):
    """Create error response."""
    return jsonify({'error': message, 'code': code}), status


def get_current_rate_window() -> str:
    """Get current rate limiting window (1-minute granularity)."""
    now = datetime.now(timezone.utc)
    return now.strftime('%Y-%m-%dT%H:%M')


def check_rate_limit(vault_id: str) -> bool:
    """
    Check if sender is within rate limit.

    Returns:
        True if within limit, False if exceeded
    """
    db = get_db()
    window = get_current_rate_window()

    row = db.execute(
        'SELECT message_count FROM rate_limits WHERE vault_id = ? AND window_start = ?',
        (vault_id, window)
    ).fetchone()

    if row is None:
        return True

    return row['message_count'] < RATE_LIMIT_MESSAGES


def increment_rate_limit(vault_id: str):
    """Increment rate limit counter for sender."""
    db = get_db()
    window = get_current_rate_window()

    db.execute('''
        INSERT INTO rate_limits (vault_id, window_start, message_count)
        VALUES (?, ?, 1)
        ON CONFLICT(vault_id, window_start) DO UPDATE SET message_count = message_count + 1
    ''', (vault_id, window))
    db.commit()


def get_agent(vault_id: str) -> Optional[dict]:
    """Get agent by vault ID."""
    db = get_db()
    row = db.execute('SELECT * FROM agents WHERE vault_id = ?', (vault_id,)).fetchone()
    if row:
        return dict(row)
    return None


def get_agent_by_alias(alias: str) -> Optional[dict]:
    """Get agent by alias."""
    db = get_db()
    row = db.execute('SELECT * FROM agents WHERE alias = ?', (alias,)).fetchone()
    if row:
        return dict(row)
    return None


def resolve_recipient(recipient: str) -> Optional[dict]:
    """Resolve recipient (vault_id or alias) to agent."""
    # Try vault ID first
    agent = get_agent(recipient)
    if agent:
        return agent
    # Try alias
    return get_agent_by_alias(recipient)


def verify_request_signature(vault_id: str, data: dict, signature: str) -> bool:
    """Verify signature on request body."""
    agent = get_agent(vault_id)
    if not agent:
        return False

    try:
        public_key = crypto.b64_to_public_signing_key(agent['signing_public_key'])
        return crypto.verify_json(public_key, data, signature)
    except crypto.SignatureError:
        return False


def requires_auth(f):
    """Decorator requiring signed authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        vault_id = request.headers.get('X-Vault-ID')
        signature = request.headers.get('X-Signature')

        if not vault_id or not signature:
            return error_response('Missing authentication headers', 401, 'auth_required')

        data = request.get_json()
        if not data:
            return error_response('Missing request body', 400, 'invalid_request')

        if not verify_request_signature(vault_id, data, signature):
            return error_response('Invalid signature', 403, 'invalid_signature')

        # Update last seen
        db = get_db()
        db.execute(
            'UPDATE agents SET last_seen_at = ? WHERE vault_id = ?',
            (datetime.now(timezone.utc).isoformat(), vault_id)
        )
        db.commit()

        g.vault_id = vault_id
        return f(*args, **kwargs)
    return decorated


def get_or_create_conversation(participant_a: str, participant_b: str) -> str:
    """Get or create a conversation between two participants."""
    db = get_db()

    # Normalize order for consistent lookup
    p1, p2 = sorted([participant_a, participant_b])

    row = db.execute(
        'SELECT id FROM conversations WHERE participant_a = ? AND participant_b = ?',
        (p1, p2)
    ).fetchone()

    if row:
        return row['id']

    # Create new conversation
    conv_id = f"conv_{uuid.uuid4().hex}"
    now = datetime.now(timezone.utc).isoformat()

    db.execute('''
        INSERT INTO conversations (id, participant_a, participant_b, started_at, last_message_at, message_count)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (conv_id, p1, p2, now, now))
    db.commit()

    return conv_id


def update_conversation(conv_id: str):
    """Update conversation stats after a message."""
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    db.execute('''
        UPDATE conversations
        SET last_message_at = ?, message_count = message_count + 1
        WHERE id = ?
    ''', (now, conv_id))
    db.commit()


# =============================================================================
# Registration Endpoints
# =============================================================================

@app.route('/register/challenge', methods=['POST'])
def request_challenge():
    """
    Request a registration challenge.

    Body:
        vault_id: Vault ID to register
        signing_public_key: Base64 Ed25519 public key
        encryption_public_key: Base64 X25519 public key

    Returns:
        challenge: Random challenge to sign
    """
    data = request.get_json()
    if not data:
        return error_response('Missing request body', 400)

    vault_id = data.get('vault_id')
    signing_key = data.get('signing_public_key')
    encryption_key = data.get('encryption_public_key')

    if not all([vault_id, signing_key, encryption_key]):
        return error_response('Missing required fields', 400)

    # Check if already registered
    if get_agent(vault_id):
        return error_response('Vault already registered', 409, 'already_registered')

    # Generate challenge
    challenge = crypto.generate_challenge()
    now = datetime.now(timezone.utc).isoformat()

    db = get_db()
    db.execute('''
        INSERT OR REPLACE INTO challenges (vault_id, challenge, signing_public_key, encryption_public_key, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (vault_id, challenge, signing_key, encryption_key, now))
    db.commit()

    return json_response({'challenge': challenge})


@app.route('/register', methods=['POST'])
def complete_registration():
    """
    Complete registration with signed challenge.

    Body:
        vault_id: Vault ID
        signing_public_key: Base64 Ed25519 public key
        encryption_public_key: Base64 X25519 public key
        challenge: The challenge received earlier
        challenge_signature: Signature over the challenge
        alias: Optional alias

    Returns:
        Registration confirmation
    """
    data = request.get_json()
    if not data:
        return error_response('Missing request body', 400)

    vault_id = data.get('vault_id')
    signing_key = data.get('signing_public_key')
    encryption_key = data.get('encryption_public_key')
    challenge = data.get('challenge')
    challenge_sig = data.get('challenge_signature')
    alias = data.get('alias')

    if not all([vault_id, signing_key, encryption_key, challenge, challenge_sig]):
        return error_response('Missing required fields', 400)

    # Check if already registered
    if get_agent(vault_id):
        return error_response('Vault already registered', 409, 'already_registered')

    # Verify challenge exists and matches
    db = get_db()
    row = db.execute(
        'SELECT * FROM challenges WHERE vault_id = ?',
        (vault_id,)
    ).fetchone()

    if not row:
        return error_response('No pending challenge for this vault', 400, 'no_challenge')

    if row['challenge'] != challenge:
        return error_response('Challenge mismatch', 400, 'challenge_mismatch')

    if row['signing_public_key'] != signing_key:
        return error_response('Public key mismatch', 400, 'key_mismatch')

    # Check challenge expiry
    created = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
    age = (datetime.now(timezone.utc) - created).total_seconds()
    if age > CHALLENGE_EXPIRY:
        db.execute('DELETE FROM challenges WHERE vault_id = ?', (vault_id,))
        db.commit()
        return error_response('Challenge expired', 400, 'challenge_expired')

    # Verify signature
    try:
        public_key = crypto.b64_to_public_signing_key(signing_key)
        crypto.verify_challenge(public_key, challenge, challenge_sig)
    except crypto.SignatureError:
        return error_response('Invalid challenge signature', 403, 'invalid_signature')

    # Check alias availability
    if alias:
        existing = get_agent_by_alias(alias)
        if existing:
            return error_response(f'Alias "{alias}" already taken', 409, 'alias_taken')

    # Register agent
    now = datetime.now(timezone.utc).isoformat()

    db.execute('''
        INSERT INTO agents (vault_id, alias, signing_public_key, encryption_public_key, registered_at, last_seen_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (vault_id, alias, signing_key, encryption_key, now, now))

    # Clean up challenge
    db.execute('DELETE FROM challenges WHERE vault_id = ?', (vault_id,))
    db.commit()

    return json_response({
        'status': 'registered',
        'vault_id': vault_id,
        'alias': alias,
        'registered_at': now,
    })


# =============================================================================
# Messaging Endpoints
# =============================================================================

@app.route('/send', methods=['POST'])
@requires_auth
def send_message():
    """
    Send a message through the relay.

    Body:
        message: Message envelope and payload
        signature: Base64 signature over message
        encrypted_payload: Optional encrypted payload

    Returns:
        message_id: ID of sent message
    """
    data = request.get_json()
    message = data.get('message')
    signature = data.get('signature')
    encrypted_payload = data.get('encrypted_payload')

    if not message or not signature:
        return error_response('Missing message or signature', 400)

    # Validate envelope
    try:
        env.validate(message)
    except env.EnvelopeError as e:
        return error_response(f'Invalid envelope: {e}', 400, 'invalid_envelope')

    sender = env.get_sender(message)
    recipient_id = env.get_recipient(message)
    msg_id = env.get_message_id(message)

    # Verify sender matches authenticated vault
    if sender != g.vault_id:
        return error_response('Sender does not match authenticated vault', 403, 'sender_mismatch')

    # Check rate limit
    if not check_rate_limit(sender):
        return error_response('Rate limit exceeded', 429, 'rate_limited')

    # Resolve recipient
    recipient = resolve_recipient(recipient_id)
    if not recipient:
        return error_response(f'Recipient not found: {recipient_id}', 404, 'recipient_not_found')

    recipient_vault_id = recipient['vault_id']

    # Verify message signature
    sender_agent = get_agent(sender)
    try:
        public_key = crypto.b64_to_public_signing_key(sender_agent['signing_public_key'])
        signable = env.get_signable_content(message)
        crypto.verify_json(public_key, signable, signature)
    except crypto.SignatureError:
        return error_response('Invalid message signature', 403, 'invalid_signature')

    # Check message size
    message_json = json.dumps(message)
    if len(message_json.encode('utf-8')) > MAX_MESSAGE_SIZE:
        return error_response('Message too large', 400, 'message_too_large')

    # Calculate expiry
    envelope = message['envelope']
    ttl = envelope.get('ttl', env.DEFAULT_TTL)
    created = datetime.now(timezone.utc)
    expires = datetime.fromtimestamp(created.timestamp() + ttl, timezone.utc)

    # Store message
    db = get_db()
    db.execute('''
        INSERT INTO messages (
            id, sender_vault_id, recipient_vault_id, message_type, intent,
            correlation_id, message_json, signature, encrypted_payload_json,
            created_at, expires_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        msg_id,
        sender,
        recipient_vault_id,
        envelope['type'],
        message['payload']['intent'],
        envelope.get('correlation_id'),
        message_json,
        signature,
        json.dumps(encrypted_payload) if encrypted_payload else None,
        created.isoformat(),
        expires.isoformat(),
    ))

    # Update rate limit
    increment_rate_limit(sender)

    # Update conversation
    conv_id = get_or_create_conversation(sender, recipient_vault_id)
    update_conversation(conv_id)

    db.commit()

    return json_response({
        'status': 'sent',
        'message_id': msg_id,
        'recipient': recipient_vault_id,
        'conversation_id': conv_id,
    })


@app.route('/receive/<vault_id>', methods=['GET'])
def receive_messages(vault_id: str):
    """
    Receive unread messages for a vault.

    Args:
        vault_id: Recipient vault ID

    Query params:
        limit: Max messages to return (default 50)
        debug: If true, include debug info

    Returns:
        messages: List of messages
    """
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 100)  # Cap at 100
    debug = request.args.get('debug', 'false').lower() == 'true'

    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    # Get undelivered, non-expired messages
    rows = db.execute('''
        SELECT id, sender_vault_id, message_json, signature, encrypted_payload_json, created_at
        FROM messages
        WHERE recipient_vault_id = ?
          AND delivered_at IS NULL
          AND expires_at > ?
        ORDER BY created_at ASC
        LIMIT ?
    ''', (vault_id, now, limit)).fetchall()

    # Debug: count all messages for this recipient
    debug_info = None
    if debug:
        total = db.execute(
            'SELECT COUNT(*) as c FROM messages WHERE recipient_vault_id = ?',
            (vault_id,)
        ).fetchone()['c']
        delivered = db.execute(
            'SELECT COUNT(*) as c FROM messages WHERE recipient_vault_id = ? AND delivered_at IS NOT NULL',
            (vault_id,)
        ).fetchone()['c']
        expired = db.execute(
            'SELECT COUNT(*) as c FROM messages WHERE recipient_vault_id = ? AND expires_at <= ?',
            (vault_id, now)
        ).fetchone()['c']
        pending = db.execute(
            'SELECT COUNT(*) as c FROM messages WHERE recipient_vault_id = ? AND delivered_at IS NULL AND expires_at > ?',
            (vault_id, now)
        ).fetchone()['c']

        # Show sample of recent messages for this recipient
        recent_msgs = db.execute('''
            SELECT id, sender_vault_id, created_at, expires_at, delivered_at
            FROM messages
            WHERE recipient_vault_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        ''', (vault_id,)).fetchall()

        # Also check if there are messages with similar vault IDs (prefix match)
        similar_recipients = db.execute('''
            SELECT DISTINCT recipient_vault_id, COUNT(*) as msg_count
            FROM messages
            WHERE recipient_vault_id LIKE ?
            GROUP BY recipient_vault_id
            LIMIT 10
        ''', (vault_id[:20] + '%',)).fetchall()

        debug_info = {
            'requested_vault_id': vault_id,
            'total_messages': total,
            'already_delivered': delivered,
            'expired': expired,
            'pending_available': pending,
            'current_time': now,
            'recent_messages': [dict(row) for row in recent_msgs],
            'similar_recipients': [{'vault_id': row['recipient_vault_id'], 'count': row['msg_count']} for row in similar_recipients],
        }

    messages = []
    message_ids = []

    for row in rows:
        msg_data = {
            'message_id': row['id'],
            'sender': row['sender_vault_id'],
            'message': json.loads(row['message_json']),
            'signature': row['signature'],
            'received_at': now,
        }
        if row['encrypted_payload_json']:
            msg_data['encrypted_payload'] = json.loads(row['encrypted_payload_json'])
        messages.append(msg_data)
        message_ids.append(row['id'])

    # Mark as delivered
    if message_ids:
        placeholders = ','.join(['?' for _ in message_ids])
        db.execute(f'''
            UPDATE messages SET delivered_at = ? WHERE id IN ({placeholders})
        ''', [now] + message_ids)
        db.commit()

    response = {
        'messages': messages,
        'count': len(messages),
    }
    if debug_info:
        response['debug'] = debug_info

    return json_response(response)


@app.route('/ack/<message_id>', methods=['POST'])
@requires_auth
def acknowledge_message(message_id: str):
    """
    Acknowledge receipt of a message.

    Args:
        message_id: ID of message to acknowledge

    Body:
        vault_id: Acknowledging vault ID
    """
    data = request.get_json()
    vault_id = data.get('vault_id')

    if vault_id != g.vault_id:
        return error_response('Vault ID mismatch', 403)

    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    # Verify message exists and belongs to this recipient
    row = db.execute(
        'SELECT recipient_vault_id, sender_vault_id FROM messages WHERE id = ?',
        (message_id,)
    ).fetchone()

    if not row:
        return error_response('Message not found', 404)

    if row['recipient_vault_id'] != vault_id:
        return error_response('Not authorized to acknowledge this message', 403)

    # Update acknowledgment
    db.execute(
        'UPDATE messages SET acknowledged_at = ? WHERE id = ?',
        (now, message_id)
    )
    db.commit()

    return json_response({
        'status': 'acknowledged',
        'message_id': message_id,
        'acknowledged_at': now,
    })


@app.route('/unread/<vault_id>', methods=['GET'])
def get_unread_count(vault_id: str):
    """
    Get count of unread messages for a vault (heartbeat check).

    This endpoint does NOT mark messages as delivered - it's for
    lightweight polling to check if new messages exist.

    Args:
        vault_id: Recipient vault ID

    Returns:
        count: Number of unread messages
        has_messages: Boolean for quick check
    """
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    # Count undelivered, non-expired messages
    row = db.execute('''
        SELECT COUNT(*) as count
        FROM messages
        WHERE recipient_vault_id = ?
          AND delivered_at IS NULL
          AND expires_at > ?
    ''', (vault_id, now)).fetchone()

    count = row['count']

    return json_response({
        'vault_id': vault_id,
        'unread_count': count,
        'has_messages': count > 0,
        'checked_at': now,
    })


# =============================================================================
# Discovery Endpoints
# =============================================================================

@app.route('/agents', methods=['GET'])
def list_agents():
    """
    List registered agents.

    Query params:
        limit: Max agents to return (default 100)

    Returns:
        agents: List of public agent info
    """
    limit = request.args.get('limit', 100, type=int)
    limit = min(limit, 500)

    db = get_db()
    rows = db.execute('''
        SELECT vault_id, alias, signing_public_key, encryption_public_key, registered_at
        FROM agents
        ORDER BY registered_at DESC
        LIMIT ?
    ''', (limit,)).fetchall()

    agents = [dict(row) for row in rows]

    return json_response({
        'agents': agents,
        'count': len(agents),
    })


@app.route('/resolve/<alias>', methods=['GET'])
def resolve_alias(alias: str):
    """
    Resolve alias to vault info.

    Args:
        alias: Alias to resolve

    Returns:
        Agent info or 404
    """
    agent = get_agent_by_alias(alias)
    if not agent:
        return error_response(f'Alias not found: {alias}', 404, 'not_found')

    return json_response({
        'vault_id': agent['vault_id'],
        'alias': agent['alias'],
        'signing_public_key': agent['signing_public_key'],
        'encryption_public_key': agent['encryption_public_key'],
    })


@app.route('/alias', methods=['POST'])
@requires_auth
def set_alias():
    """
    Set or update alias for authenticated vault.

    Body:
        vault_id: Vault ID
        alias: New alias

    Returns:
        Updated alias info
    """
    data = request.get_json()
    vault_id = data.get('vault_id')
    alias = data.get('alias')

    if vault_id != g.vault_id:
        return error_response('Vault ID mismatch', 403)

    if not alias:
        return error_response('Alias required', 400)

    # Check availability
    existing = get_agent_by_alias(alias)
    if existing and existing['vault_id'] != vault_id:
        return error_response(f'Alias "{alias}" already taken', 409, 'alias_taken')

    db = get_db()
    db.execute('UPDATE agents SET alias = ? WHERE vault_id = ?', (alias, vault_id))
    db.commit()

    return json_response({
        'status': 'updated',
        'vault_id': vault_id,
        'alias': alias,
    })


# =============================================================================
# Observability Endpoints
# =============================================================================

@app.route('/messages/<conversation_id>/log', methods=['GET'])
def get_conversation_log(conversation_id: str):
    """
    Get conversation log.

    Args:
        conversation_id: Conversation ID

    Returns:
        Conversation details with message summaries
    """
    db = get_db()

    # Get conversation
    conv = db.execute(
        'SELECT * FROM conversations WHERE id = ?',
        (conversation_id,)
    ).fetchone()

    if not conv:
        return error_response('Conversation not found', 404)

    conv_dict = dict(conv)

    # Get messages in this conversation
    rows = db.execute('''
        SELECT id, sender_vault_id, recipient_vault_id, message_type, intent,
               correlation_id, created_at, delivered_at, acknowledged_at
        FROM messages
        WHERE (sender_vault_id = ? AND recipient_vault_id = ?)
           OR (sender_vault_id = ? AND recipient_vault_id = ?)
        ORDER BY created_at ASC
    ''', (
        conv_dict['participant_a'], conv_dict['participant_b'],
        conv_dict['participant_b'], conv_dict['participant_a']
    )).fetchall()

    messages = []
    for row in rows:
        msg = dict(row)
        msg['direction'] = 'a_to_b' if msg['sender_vault_id'] == conv_dict['participant_a'] else 'b_to_a'
        msg['status'] = 'acknowledged' if msg['acknowledged_at'] else ('delivered' if msg['delivered_at'] else 'pending')
        messages.append(msg)

    return json_response({
        'conversation': conv_dict,
        'messages': messages,
    })


@app.route('/logs/<vault_id>', methods=['GET'])
def get_agent_logs(vault_id: str):
    """
    Get all conversations for an agent.

    Args:
        vault_id: Vault ID

    Query params:
        limit: Max conversations to return

    Returns:
        List of conversations
    """
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 100)

    db = get_db()
    rows = db.execute('''
        SELECT * FROM conversations
        WHERE participant_a = ? OR participant_b = ?
        ORDER BY last_message_at DESC
        LIMIT ?
    ''', (vault_id, vault_id, limit)).fetchall()

    return json_response({
        'conversations': [dict(row) for row in rows],
        'count': len(rows),
    })


# =============================================================================
# Health & Maintenance
# =============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    db = get_db()

    # Quick DB check
    try:
        db.execute('SELECT 1').fetchone()
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {e}'

    return json_response({
        'status': 'healthy' if db_status == 'ok' else 'degraded',
        'database': db_status,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    })


def cleanup_expired():
    """Background task to clean up expired messages and challenges."""
    while True:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            now = datetime.now(timezone.utc).isoformat()

            # Delete expired messages
            conn.execute('DELETE FROM messages WHERE expires_at < ?', (now,))

            # Delete expired challenges
            cutoff = datetime.fromtimestamp(
                datetime.now(timezone.utc).timestamp() - CHALLENGE_EXPIRY,
                timezone.utc
            ).isoformat()
            conn.execute('DELETE FROM challenges WHERE created_at < ?', (cutoff,))

            # Clean old rate limit entries (older than 1 hour)
            hour_ago = datetime.fromtimestamp(
                datetime.now(timezone.utc).timestamp() - 3600,
                timezone.utc
            ).strftime('%Y-%m-%dT%H:%M')
            conn.execute('DELETE FROM rate_limits WHERE window_start < ?', (hour_ago,))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Cleanup error: {e}", file=sys.stderr)

        time.sleep(CLEANUP_INTERVAL)


# =============================================================================
# Initialization (for gunicorn/production)
# =============================================================================

_initialized = False

def initialize():
    """Initialize database and background tasks. Safe to call multiple times."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    # Initialize database
    init_db()
    print(f"Database initialized at {DATABASE_PATH}", file=sys.stderr)

    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
    cleanup_thread.start()
    print("Background cleanup started", file=sys.stderr)


# Auto-initialize when imported (for gunicorn)
initialize()


# =============================================================================
# Main (for direct execution)
# =============================================================================

def main():
    """Run the server directly (development mode)."""
    import argparse

    parser = argparse.ArgumentParser(description='ClawHub Relay Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--db', help='Database path (overrides CLAWHUB_DB env var)')
    args = parser.parse_args()

    if args.db:
        global DATABASE_PATH, _initialized
        DATABASE_PATH = args.db
        _initialized = False  # Re-initialize with new path
        initialize()

    # Run server
    print(f"Starting ClawHub relay on {args.host}:{args.port}", file=sys.stderr)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
