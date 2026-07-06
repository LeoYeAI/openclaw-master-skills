"""
Message envelope schema, builder, and validator for OpenClaw Messaging.

Every message follows a strict structure. No freeform text between agents.
This module enforces the schema and provides utilities for building valid messages.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Any, Literal

# Message types
MessageType = Literal["request", "response", "notification", "error"]

# Standard intents
Intent = Literal[
    "ping",
    "query",
    "task_request",
    "task_result",
    "context_exchange",
    "capability_check",
    "ack",
    "pong",
]

# Content types
ContentType = Literal["application/json", "text/plain"]

# Version
PROTOCOL_VERSION = "1.0"

# Limits
MAX_MESSAGE_SIZE = 64 * 1024  # 64KB
DEFAULT_TTL = 3600  # 1 hour


class EnvelopeError(Exception):
    """Raised when envelope validation fails."""
    pass


class EnvelopeBuilder:
    """Builder for constructing valid message envelopes."""

    def __init__(self):
        self._envelope = {
            'id': None,
            'type': None,
            'correlation_id': None,
            'sender': None,
            'recipient': None,
            'timestamp': None,
            'ttl': DEFAULT_TTL,
            'version': PROTOCOL_VERSION,
        }
        self._payload = {
            'intent': None,
            'content_type': 'application/json',
            'body': None,
        }

    def message_id(self, msg_id: Optional[str] = None) -> 'EnvelopeBuilder':
        """Set or generate message ID."""
        self._envelope['id'] = msg_id or f"msg_{uuid.uuid4().hex}"
        return self

    def message_type(self, msg_type: MessageType) -> 'EnvelopeBuilder':
        """Set message type (request, response, notification, error)."""
        valid_types = ('request', 'response', 'notification', 'error')
        if msg_type not in valid_types:
            raise EnvelopeError(f"Invalid message type: {msg_type}")
        self._envelope['type'] = msg_type
        return self

    def correlation_id(self, corr_id: Optional[str]) -> 'EnvelopeBuilder':
        """Set correlation ID (links response to original request)."""
        self._envelope['correlation_id'] = corr_id
        return self

    def sender(self, sender_id: str) -> 'EnvelopeBuilder':
        """Set sender vault ID or alias."""
        if not sender_id:
            raise EnvelopeError("Sender cannot be empty")
        self._envelope['sender'] = sender_id
        return self

    def recipient(self, recipient_id: str) -> 'EnvelopeBuilder':
        """Set recipient vault ID or alias."""
        if not recipient_id:
            raise EnvelopeError("Recipient cannot be empty")
        self._envelope['recipient'] = recipient_id
        return self

    def timestamp(self, ts: Optional[str] = None) -> 'EnvelopeBuilder':
        """Set or generate timestamp (ISO 8601)."""
        if ts is None:
            ts = datetime.now(timezone.utc).isoformat()
        self._envelope['timestamp'] = ts
        return self

    def ttl(self, seconds: int) -> 'EnvelopeBuilder':
        """Set message time-to-live in seconds."""
        if seconds <= 0:
            raise EnvelopeError("TTL must be positive")
        self._envelope['ttl'] = seconds
        return self

    def intent(self, intent: str) -> 'EnvelopeBuilder':
        """Set message intent."""
        if not intent:
            raise EnvelopeError("Intent cannot be empty")
        self._payload['intent'] = intent
        return self

    def content_type(self, ct: ContentType) -> 'EnvelopeBuilder':
        """Set payload content type."""
        self._payload['content_type'] = ct
        return self

    def body(self, content: Any) -> 'EnvelopeBuilder':
        """Set payload body."""
        self._payload['body'] = content
        return self

    def build(self) -> dict:
        """
        Build and validate the complete message.

        Returns:
            Dict with 'envelope' and 'payload' keys

        Raises:
            EnvelopeError: If required fields are missing
        """
        # Auto-generate ID if not set
        if self._envelope['id'] is None:
            self.message_id()

        # Auto-generate timestamp if not set
        if self._envelope['timestamp'] is None:
            self.timestamp()

        # Validate required fields
        required_envelope = ['id', 'type', 'sender', 'recipient', 'timestamp', 'version']
        for field in required_envelope:
            if self._envelope.get(field) is None:
                raise EnvelopeError(f"Missing required envelope field: {field}")

        if self._payload.get('intent') is None:
            raise EnvelopeError("Missing required payload field: intent")

        message = {
            'envelope': self._envelope.copy(),
            'payload': self._payload.copy(),
        }

        # Validate size
        validate_size(message)

        return message


def create_request(
    sender: str,
    recipient: str,
    intent: str,
    body: Any,
    ttl: int = DEFAULT_TTL,
    content_type: ContentType = "application/json",
) -> dict:
    """
    Convenience function to create a request message.

    Args:
        sender: Sender vault ID
        recipient: Recipient vault ID or alias
        intent: Message intent
        body: Payload body
        ttl: Time-to-live in seconds
        content_type: Payload content type

    Returns:
        Complete message dict
    """
    return (
        EnvelopeBuilder()
        .message_type("request")
        .sender(sender)
        .recipient(recipient)
        .intent(intent)
        .body(body)
        .ttl(ttl)
        .content_type(content_type)
        .build()
    )


def create_response(
    sender: str,
    recipient: str,
    correlation_id: str,
    intent: str,
    body: Any,
    ttl: int = DEFAULT_TTL,
    content_type: ContentType = "application/json",
) -> dict:
    """
    Convenience function to create a response message.

    Args:
        sender: Sender vault ID
        recipient: Recipient vault ID
        correlation_id: ID of the original request
        intent: Response intent (e.g., 'task_result', 'pong')
        body: Payload body
        ttl: Time-to-live in seconds
        content_type: Payload content type

    Returns:
        Complete message dict
    """
    return (
        EnvelopeBuilder()
        .message_type("response")
        .sender(sender)
        .recipient(recipient)
        .correlation_id(correlation_id)
        .intent(intent)
        .body(body)
        .ttl(ttl)
        .content_type(content_type)
        .build()
    )


def create_error(
    sender: str,
    recipient: str,
    correlation_id: Optional[str],
    error_code: str,
    error_message: str,
) -> dict:
    """
    Convenience function to create an error message.

    Args:
        sender: Sender vault ID
        recipient: Recipient vault ID
        correlation_id: ID of the original request (if applicable)
        error_code: Machine-readable error code
        error_message: Human-readable error description

    Returns:
        Complete message dict
    """
    return (
        EnvelopeBuilder()
        .message_type("error")
        .sender(sender)
        .recipient(recipient)
        .correlation_id(correlation_id)
        .intent("error")
        .body({
            'error_code': error_code,
            'error_message': error_message,
        })
        .build()
    )


def create_notification(
    sender: str,
    recipient: str,
    intent: str,
    body: Any,
    ttl: int = DEFAULT_TTL,
) -> dict:
    """
    Convenience function to create a notification (no response expected).

    Args:
        sender: Sender vault ID
        recipient: Recipient vault ID
        intent: Notification intent
        body: Payload body
        ttl: Time-to-live in seconds

    Returns:
        Complete message dict
    """
    return (
        EnvelopeBuilder()
        .message_type("notification")
        .sender(sender)
        .recipient(recipient)
        .intent(intent)
        .body(body)
        .ttl(ttl)
        .build()
    )


def validate(message: dict) -> bool:
    """
    Validate a message against the schema.

    Args:
        message: Message dict to validate

    Returns:
        True if valid

    Raises:
        EnvelopeError: If validation fails
    """
    if not isinstance(message, dict):
        raise EnvelopeError("Message must be a dict")

    if 'envelope' not in message:
        raise EnvelopeError("Missing 'envelope' key")

    if 'payload' not in message:
        raise EnvelopeError("Missing 'payload' key")

    envelope = message['envelope']
    payload = message['payload']

    # Validate envelope fields
    required_envelope = ['id', 'type', 'sender', 'recipient', 'timestamp', 'version']
    for field in required_envelope:
        if field not in envelope or envelope[field] is None:
            raise EnvelopeError(f"Missing required envelope field: {field}")

    # Validate message type
    valid_types = ('request', 'response', 'notification', 'error')
    if envelope['type'] not in valid_types:
        raise EnvelopeError(f"Invalid message type: {envelope['type']}")

    # Validate version
    if envelope['version'] != PROTOCOL_VERSION:
        raise EnvelopeError(f"Unsupported protocol version: {envelope['version']}")

    # Validate payload
    if 'intent' not in payload or payload['intent'] is None:
        raise EnvelopeError("Missing required payload field: intent")

    # Validate size
    validate_size(message)

    return True


def validate_size(message: dict) -> bool:
    """
    Validate message size against 64KB limit.

    Args:
        message: Message dict to validate

    Returns:
        True if valid

    Raises:
        EnvelopeError: If message exceeds size limit
    """
    import json
    size = len(json.dumps(message).encode('utf-8'))
    if size > MAX_MESSAGE_SIZE:
        raise EnvelopeError(f"Message size ({size} bytes) exceeds limit ({MAX_MESSAGE_SIZE} bytes)")
    return True


def get_signable_content(message: dict) -> dict:
    """
    Extract the content that should be signed (envelope + payload).

    Args:
        message: Complete message dict

    Returns:
        Dict containing envelope and payload for signing
    """
    return {
        'envelope': message['envelope'],
        'payload': message['payload'],
    }


def is_expired(message: dict) -> bool:
    """
    Check if a message has expired based on its TTL.

    Args:
        message: Message dict to check

    Returns:
        True if expired, False otherwise
    """
    envelope = message.get('envelope', {})
    timestamp_str = envelope.get('timestamp')
    ttl = envelope.get('ttl', DEFAULT_TTL)

    if not timestamp_str:
        return True  # No timestamp = expired

    try:
        # Parse ISO 8601 timestamp
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        age_seconds = (now - timestamp).total_seconds()
        return age_seconds > ttl
    except (ValueError, TypeError):
        return True  # Invalid timestamp = expired


def get_message_id(message: dict) -> Optional[str]:
    """Extract message ID from a message."""
    return message.get('envelope', {}).get('id')


def get_sender(message: dict) -> Optional[str]:
    """Extract sender from a message."""
    return message.get('envelope', {}).get('sender')


def get_recipient(message: dict) -> Optional[str]:
    """Extract recipient from a message."""
    return message.get('envelope', {}).get('recipient')


def get_correlation_id(message: dict) -> Optional[str]:
    """Extract correlation ID from a message."""
    return message.get('envelope', {}).get('correlation_id')


def get_intent(message: dict) -> Optional[str]:
    """Extract intent from a message."""
    return message.get('payload', {}).get('intent')


def get_body(message: dict) -> Any:
    """Extract body from a message."""
    return message.get('payload', {}).get('body')
