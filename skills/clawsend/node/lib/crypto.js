/**
 * Cryptographic operations for ClawSend.
 *
 * Ed25519 for signing, X25519 + AES-256-GCM for encryption.
 */

import { ed25519 } from '@noble/curves/ed25519';
import { x25519 } from '@noble/curves/ed25519';
import { sha256 } from '@noble/hashes/sha256';
import { hkdf } from '@noble/hashes/hkdf';
import { randomBytes, createCipheriv, createDecipheriv } from 'crypto';

// ============================================================================
// Key Generation
// ============================================================================

/**
 * Generate an Ed25519 signing keypair.
 * @returns {{ privateKey: Uint8Array, publicKey: Uint8Array }}
 */
export function generateSigningKeypair() {
  const privateKey = ed25519.utils.randomPrivateKey();
  const publicKey = ed25519.getPublicKey(privateKey);
  return { privateKey, publicKey };
}

/**
 * Generate an X25519 encryption keypair.
 * @returns {{ privateKey: Uint8Array, publicKey: Uint8Array }}
 */
export function generateEncryptionKeypair() {
  const privateKey = x25519.utils.randomPrivateKey();
  const publicKey = x25519.getPublicKey(privateKey);
  return { privateKey, publicKey };
}

// ============================================================================
// Key Serialization
// ============================================================================

/**
 * Encode bytes to URL-safe base64.
 * @param {Uint8Array} bytes
 * @returns {string}
 */
export function toBase64(bytes) {
  return Buffer.from(bytes).toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
}

/**
 * Decode URL-safe base64 to bytes.
 * @param {string} b64
 * @returns {Uint8Array}
 */
export function fromBase64(b64) {
  // Convert URL-safe base64 back to standard base64
  const standard = b64.replace(/-/g, '+').replace(/_/g, '/');
  return new Uint8Array(Buffer.from(standard, 'base64'));
}

/**
 * Sort object keys recursively for deterministic JSON.
 * @param {any} obj
 * @returns {any}
 */
function sortKeys(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  if (Array.isArray(obj)) {
    return obj.map(sortKeys);
  }
  const sorted = {};
  for (const key of Object.keys(obj).sort()) {
    sorted[key] = sortKeys(obj[key]);
  }
  return sorted;
}

/**
 * Serialize private signing key.
 * @param {Uint8Array} privateKey
 * @returns {Uint8Array}
 */
export function serializePrivateSigningKey(privateKey) {
  return privateKey;
}

/**
 * Deserialize private signing key.
 * @param {Uint8Array} bytes
 * @returns {Uint8Array}
 */
export function deserializePrivateSigningKey(bytes) {
  return bytes;
}

/**
 * Serialize private encryption key.
 * @param {Uint8Array} privateKey
 * @returns {Uint8Array}
 */
export function serializePrivateEncryptionKey(privateKey) {
  return privateKey;
}

/**
 * Deserialize private encryption key.
 * @param {Uint8Array} bytes
 * @returns {Uint8Array}
 */
export function deserializePrivateEncryptionKey(bytes) {
  return bytes;
}

// ============================================================================
// Signing
// ============================================================================

/**
 * Sign data with Ed25519.
 * @param {Uint8Array} privateKey
 * @param {Uint8Array} message
 * @returns {Uint8Array}
 */
export function sign(privateKey, message) {
  return ed25519.sign(message, privateKey);
}

/**
 * Verify Ed25519 signature.
 * @param {Uint8Array} publicKey
 * @param {Uint8Array} message
 * @param {Uint8Array} signature
 * @returns {boolean}
 */
export function verify(publicKey, message, signature) {
  try {
    return ed25519.verify(signature, message, publicKey);
  } catch {
    return false;
  }
}

/**
 * Sign a JSON object.
 * Uses sorted keys and compact JSON for deterministic signing (matches Python).
 * @param {Uint8Array} privateKey
 * @param {object} data
 * @returns {string} Base64-encoded signature
 */
export function signJson(privateKey, data) {
  // Sort keys and use compact JSON (no whitespace) for deterministic signing
  const sorted = sortKeys(data);
  const message = Buffer.from(JSON.stringify(sorted), 'utf-8');
  const signature = sign(privateKey, message);
  return toBase64(signature);
}

/**
 * Verify a JSON object's signature.
 * Uses sorted keys and compact JSON for deterministic verification (matches Python).
 * @param {Uint8Array} publicKey
 * @param {object} data
 * @param {string} signatureB64
 * @returns {boolean}
 */
export function verifyJson(publicKey, data, signatureB64) {
  // Sort keys and use compact JSON (no whitespace) for deterministic verification
  const sorted = sortKeys(data);
  const message = Buffer.from(JSON.stringify(sorted), 'utf-8');
  const signature = fromBase64(signatureB64);
  return verify(publicKey, message, signature);
}

/**
 * Sign a challenge string.
 * @param {Uint8Array} privateKey
 * @param {string} challenge
 * @returns {string} Base64-encoded signature
 */
export function signChallenge(privateKey, challenge) {
  const message = Buffer.from(challenge, 'utf-8');
  const signature = sign(privateKey, message);
  return toBase64(signature);
}

// ============================================================================
// Encryption (X25519 + AES-256-GCM)
// ============================================================================

/**
 * Encrypt JSON for a recipient.
 * @param {Uint8Array} recipientPublicKey
 * @param {object} data
 * @returns {{ ephemeral_public_key: string, nonce: string, ciphertext: string }}
 */
export function encryptJson(recipientPublicKey, data) {
  // Generate ephemeral keypair
  const ephemeralPrivate = x25519.utils.randomPrivateKey();
  const ephemeralPublic = x25519.getPublicKey(ephemeralPrivate);

  // Derive shared secret
  const sharedSecret = x25519.getSharedSecret(ephemeralPrivate, recipientPublicKey);

  // Derive AES key using HKDF
  const aesKey = hkdf(sha256, sharedSecret, undefined, 'clawsend-v1', 32);

  // Generate nonce
  const nonce = randomBytes(12);

  // Encrypt with AES-256-GCM
  const plaintext = Buffer.from(JSON.stringify(data), 'utf-8');
  const cipher = createCipheriv('aes-256-gcm', aesKey, nonce);
  const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const authTag = cipher.getAuthTag();
  const ciphertext = Buffer.concat([encrypted, authTag]);

  return {
    ephemeral_public_key: toBase64(ephemeralPublic),
    nonce: toBase64(nonce),
    ciphertext: toBase64(ciphertext),
  };
}

/**
 * Decrypt JSON from a sender.
 * @param {Uint8Array} privateKey
 * @param {{ ephemeral_public_key: string, nonce: string, ciphertext: string }} encrypted
 * @returns {object}
 */
export function decryptJson(privateKey, encrypted) {
  const ephemeralPublic = fromBase64(encrypted.ephemeral_public_key);
  const nonce = fromBase64(encrypted.nonce);
  const ciphertextWithTag = fromBase64(encrypted.ciphertext);

  // Derive shared secret
  const sharedSecret = x25519.getSharedSecret(privateKey, ephemeralPublic);

  // Derive AES key using HKDF
  const aesKey = hkdf(sha256, sharedSecret, undefined, 'clawsend-v1', 32);

  // Split ciphertext and auth tag
  const ciphertext = ciphertextWithTag.slice(0, -16);
  const authTag = ciphertextWithTag.slice(-16);

  // Decrypt with AES-256-GCM
  const decipher = createDecipheriv('aes-256-gcm', aesKey, nonce);
  decipher.setAuthTag(authTag);
  const decrypted = Buffer.concat([decipher.update(ciphertext), decipher.final()]);

  return JSON.parse(decrypted.toString('utf-8'));
}

export class SignatureError extends Error {
  constructor(message) {
    super(message);
    this.name = 'SignatureError';
  }
}

export class DecryptionError extends Error {
  constructor(message) {
    super(message);
    this.name = 'DecryptionError';
  }
}
