#!/usr/bin/env node
/**
 * NervePay Request Helper
 *
 * Zero-dependency Ed25519 signing helper for agents.
 * Uses only Node.js built-in crypto.
 *
 * USAGE:
 *   export NERVEPAY_DID="did:nervepay:agent:abc123..."
 *   export NERVEPAY_PRIVATE_KEY="ed25519:5Kd7..."
 *   export NERVEPAY_API_URL="https://api.nervepay.xyz"  # optional
 *
 *   # Authenticated GET
 *   node nervepay-request.mjs GET /v1/agent-identity/whoami
 *
 *   # Authenticated POST with body
 *   node nervepay-request.mjs POST /v1/agent-identity/track-service '{"service_name":"openai"}'
 */

import crypto from 'node:crypto';

// ============================================================================
// CONFIGURATION
// ============================================================================

const API_URL = process.env.NERVEPAY_API_URL || 'https://api.nervepay.xyz';
const AGENT_DID = process.env.NERVEPAY_DID;
const AGENT_PRIVATE_KEY = process.env.NERVEPAY_PRIVATE_KEY;

// ============================================================================
// BASE58 ENCODING
// ============================================================================

const BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

function decodeBase58(str) {
  const bytes = [];
  for (const char of str) {
    const index = BASE58_ALPHABET.indexOf(char);
    if (index === -1) throw new Error(`Invalid base58 character: ${char}`);

    let carry = index;
    for (let i = 0; i < bytes.length; i++) {
      carry += bytes[i] * 58;
      bytes[i] = carry & 0xff;
      carry >>= 8;
    }
    while (carry > 0) {
      bytes.push(carry & 0xff);
      carry >>= 8;
    }
  }

  for (const char of str) {
    if (char !== '1') break;
    bytes.push(0);
  }

  return Buffer.from(bytes.reverse());
}

// ============================================================================
// ED25519 SIGNING
// ============================================================================

function signRequest(privateKeyBase58, payload) {
  const keyStr = privateKeyBase58.replace(/^ed25519:/, '');
  const privateKeyBytes = decodeBase58(keyStr);
  const seed = Uint8Array.prototype.slice.call(privateKeyBytes, 0, 32);

  const pkcs8Header = Buffer.from('302e020100300506032b657004220420', 'hex');
  const keyObject = crypto.createPrivateKey({
    key: Buffer.concat([pkcs8Header, seed]),
    format: 'der',
    type: 'pkcs8'
  });

  const message = JSON.stringify(payload);
  const signature = crypto.sign(null, Buffer.from(message), keyObject);

  return signature.toString('base64');
}

// ============================================================================
// REQUEST BUILDER
// ============================================================================

function generateAuthHeaders(did, privateKey, method, path, query = null, body = null) {
  const nonce = crypto.randomUUID();
  const timestamp = new Date().toISOString();

  // Hash body if present (must match backend's SHA-256 hashing)
  let bodyHash = null;
  if (body) {
    const hash = crypto.createHash('sha256').update(body).digest('hex');
    bodyHash = hash;
  }

  const payload = {
    method: method.toUpperCase(),
    path,
    query,
    body: bodyHash,
    nonce,
    timestamp,
    agent_did: did,
  };

  const signature = signRequest(privateKey, payload);

  return {
    'Agent-DID': did,
    'X-Agent-Signature': signature,
    'X-Agent-Nonce': nonce,
    'X-Signature-Timestamp': timestamp,
  };
}

async function makeRequest(method, path, bodyStr = null) {
  if (!AGENT_DID || !AGENT_PRIVATE_KEY) {
    console.error(JSON.stringify({
      error: 'Missing required environment variables',
      required: ['NERVEPAY_DID', 'NERVEPAY_PRIVATE_KEY']
    }, null, 2));
    process.exit(1);
  }

  // Parse query string from path
  const [pathOnly, queryStr] = path.split('?');
  const query = queryStr || null;

  const url = query ? `${API_URL}${pathOnly}?${query}` : `${API_URL}${pathOnly}`;
  const headers = generateAuthHeaders(AGENT_DID, AGENT_PRIVATE_KEY, method, pathOnly, query, bodyStr);

  if (bodyStr) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: bodyStr || undefined,
    });

    const responseText = await response.text();

    let data;
    try {
      data = JSON.parse(responseText);
    } catch {
      data = responseText;
    }

    const result = {
      ok: response.ok,
      status: response.status,
      statusText: response.statusText,
      data,
    };

    console.log(JSON.stringify(result, null, 2));

    if (!response.ok) {
      process.exit(1);
    }
  } catch (error) {
    console.error(JSON.stringify({
      error: error.message,
      stack: error.stack
    }, null, 2));
    process.exit(1);
  }
}

// ============================================================================
// CLI
// ============================================================================

const [method, path, bodyStr] = process.argv.slice(2);

if (!method || !path) {
  console.error('Usage: nervepay-request.mjs METHOD PATH [BODY_JSON]');
  console.error('Example: nervepay-request.mjs GET /v1/agent-identity/whoami');
  console.error('Example: nervepay-request.mjs POST /v1/agent-identity/track-service \'{"service_name":"openai"}\'');
  process.exit(1);
}

makeRequest(method.toUpperCase(), path, bodyStr);
