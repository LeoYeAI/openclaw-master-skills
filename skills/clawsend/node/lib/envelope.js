/**
 * Message envelope and schema for ClawSend.
 */

import { randomUUID } from 'crypto';

// Protocol version
export const PROTOCOL_VERSION = '1.0';

// Valid message types
export const MESSAGE_TYPES = ['request', 'response', 'notification', 'error'];

// Standard intents
export const STANDARD_INTENTS = [
  'ping',
  'pong',
  'query',
  'task_request',
  'task_result',
  'context_exchange',
  'capability_check',
  'error',
];

/**
 * Create a message envelope.
 * @param {object} options
 * @returns {object}
 */
export function createEnvelope({
  sender,
  recipient,
  type = 'request',
  ttl = 3600,
  correlationId = null,
}) {
  return {
    id: `msg_${randomUUID().replace(/-/g, '')}`,
    type,
    correlation_id: correlationId,
    sender,
    recipient,
    timestamp: new Date().toISOString(),
    ttl,
    version: PROTOCOL_VERSION,
  };
}

/**
 * Create a full message with envelope and payload.
 * @param {object} options
 * @returns {object}
 */
export function createMessage({
  sender,
  recipient,
  type = 'request',
  intent,
  body = {},
  ttl = 3600,
  correlationId = null,
  contentType = 'application/json',
}) {
  return {
    envelope: createEnvelope({ sender, recipient, type, ttl, correlationId }),
    payload: {
      intent,
      content_type: contentType,
      body,
    },
  };
}

/**
 * Get the signable content from a message (envelope + payload).
 * @param {object} message
 * @returns {object}
 */
export function getSignableContent(message) {
  return {
    envelope: message.envelope,
    payload: message.payload,
  };
}

/**
 * Validate a message envelope.
 * @param {object} envelope
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateEnvelope(envelope) {
  const errors = [];

  if (!envelope.id) errors.push('Missing message ID');
  if (!envelope.type) errors.push('Missing message type');
  if (!MESSAGE_TYPES.includes(envelope.type)) {
    errors.push(`Invalid message type: ${envelope.type}`);
  }
  if (!envelope.sender) errors.push('Missing sender');
  if (!envelope.recipient) errors.push('Missing recipient');
  if (!envelope.timestamp) errors.push('Missing timestamp');

  return { valid: errors.length === 0, errors };
}

/**
 * Validate a full message.
 * @param {object} message
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateMessage(message) {
  const errors = [];

  if (!message.envelope) {
    errors.push('Missing envelope');
  } else {
    const envResult = validateEnvelope(message.envelope);
    errors.push(...envResult.errors);
  }

  if (!message.payload) {
    errors.push('Missing payload');
  } else {
    if (!message.payload.intent) errors.push('Missing payload intent');
  }

  return { valid: errors.length === 0, errors };
}
