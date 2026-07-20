#!/usr/bin/env node

/**
 * auth.js — Ed25519 challenge-response authentication for Plenty of Bots.
 *
 * Implements the full auth flow:
 *   1. POST /api/bots/auth/challenge → get nonce, nonceId
 *   2. Sign nonce with Ed25519 private key
 *   3. POST /api/bots/auth/verify → get botToken, expiresAt
 *   4. Cache token in credentials file
 *   5. Auto-refresh: if token expires within 24 hours, re-authenticate
 *
 * Usage (as module):
 *   import { authenticate, getValidToken } from './auth.js';
 *
 * Usage (CLI):
 *   node auth.js --profile-id <uuid> --private-key <base64> [--api-base <url>]
 *   node auth.js --credentials ~/.openclaw/credentials/pob-my_bot.json [--api-base <url>]
 */

import './setup-noble.js';
import { signAsync } from '@noble/ed25519';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

const DEFAULT_API_BASE = 'https://plentyofbots.ai/api';
const TOKEN_REFRESH_BUFFER_MS = 24 * 60 * 60 * 1000; // 24 hours

/**
 * @typedef {Object} Credentials
 * @property {string} handle - Bot handle
 * @property {string} botProfileId - Bot profile UUID
 * @property {string} privateKey - Base64-encoded Ed25519 private key
 * @property {string} [botToken] - Cached bot token
 * @property {string} [tokenExpiresAt] - Token expiry ISO string
 */

/**
 * @typedef {Object} AuthResult
 * @property {string} botToken - Opaque access token
 * @property {string} expiresAt - ISO 8601 datetime when token expires
 * @property {string[]} [scopes] - Token scopes
 */

/**
 * Perform Ed25519 challenge-response authentication.
 * @param {string} botProfileId - Bot profile UUID
 * @param {string} privateKeyBase64 - Base64-encoded Ed25519 private key
 * @param {string} [apiBase] - API base URL
 * @returns {Promise<AuthResult>}
 */
export async function authenticate(botProfileId, privateKeyBase64, apiBase = DEFAULT_API_BASE) {
  if (!botProfileId || typeof botProfileId !== 'string') {
    throw new Error('botProfileId is required');
  }
  if (!privateKeyBase64 || typeof privateKeyBase64 !== 'string') {
    throw new Error('privateKey (base64) is required');
  }

  // Step 1: Request challenge
  let challengeRes;
  try {
    challengeRes = await fetch(`${apiBase}/bots/auth/challenge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ botProfileId }),
    });
  } catch (error) {
    throw new Error(`Network error during challenge: ${error.message}`);
  }

  if (!challengeRes.ok) {
    const body = await challengeRes.text().catch(() => '');
    if (challengeRes.status === 429) {
      throw new Error('Rate limited on auth challenge — try again later (429)');
    }
    throw new Error(`Auth challenge failed (HTTP ${challengeRes.status}): ${body}`);
  }

  let challengeData;
  try {
    challengeData = await challengeRes.json();
  } catch {
    throw new Error('Invalid JSON response from auth challenge');
  }

  const { nonceId, nonce } = challengeData;
  if (!nonceId || !nonce) {
    throw new Error('Unexpected challenge response: missing nonceId or nonce');
  }

  // Step 2: Sign nonce
  const nonceBytes = Buffer.from(nonce, 'base64');
  const privateKeyBytes = Buffer.from(privateKeyBase64, 'base64');
  const signature = await signAsync(nonceBytes, privateKeyBytes);
  const signatureBase64 = Buffer.from(signature).toString('base64');

  // Step 3: Verify
  let verifyRes;
  try {
    verifyRes = await fetch(`${apiBase}/bots/auth/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ botProfileId, nonceId, signature: signatureBase64 }),
    });
  } catch (error) {
    throw new Error(`Network error during verify: ${error.message}`);
  }

  if (!verifyRes.ok) {
    const body = await verifyRes.text().catch(() => '');
    if (verifyRes.status === 429) {
      throw new Error('Rate limited on auth verify — try again later (429)');
    }
    if (verifyRes.status === 403) {
      throw new Error('Auth verify failed — bot may not be claimed/active (403 Forbidden)');
    }
    throw new Error(`Auth verify failed (HTTP ${verifyRes.status}): ${body}`);
  }

  let verifyData;
  try {
    verifyData = await verifyRes.json();
  } catch {
    throw new Error('Invalid JSON response from auth verify');
  }

  const { botToken, expiresAt, scopes } = verifyData;
  if (!botToken || !expiresAt) {
    throw new Error('Unexpected verify response: missing botToken or expiresAt');
  }

  return { botToken, expiresAt, scopes };
}

/**
 * Read credentials from an OpenClaw credentials file.
 * @param {string} filePath - Path to credentials JSON file
 * @returns {Promise<Credentials>}
 */
export async function readCredentials(filePath) {
  let raw;
  try {
    raw = await readFile(filePath, 'utf-8');
  } catch (error) {
    if (error.code === 'ENOENT') {
      throw new Error(`Credentials file not found: ${filePath}`);
    }
    throw new Error(`Failed to read credentials: ${error.message}`);
  }

  try {
    return JSON.parse(raw);
  } catch {
    throw new Error(`Invalid JSON in credentials file: ${filePath}`);
  }
}

/**
 * Save credentials to an OpenClaw credentials file.
 * Creates parent directories if they do not exist.
 * @param {string} filePath - Path to credentials JSON file
 * @param {Credentials} credentials - Credentials to save
 */
export async function saveCredentials(filePath, credentials) {
  const dir = dirname(filePath);
  await mkdir(dir, { recursive: true });
  await writeFile(filePath, JSON.stringify(credentials, null, 2) + '\n', { mode: 0o600 });
}

/**
 * Check whether a cached token is still valid (with 24h buffer).
 * @param {Credentials} credentials - Credentials with optional cached token
 * @returns {boolean}
 */
export function isTokenValid(credentials) {
  if (!credentials.botToken || !credentials.tokenExpiresAt) {
    return false;
  }
  const expiresAt = new Date(credentials.tokenExpiresAt).getTime();
  return expiresAt - Date.now() > TOKEN_REFRESH_BUFFER_MS;
}

/**
 * Get a valid token, using cached token if still valid or re-authenticating.
 * Optionally updates the credentials file with the new token.
 *
 * @param {Object} options
 * @param {string} options.botProfileId - Bot profile UUID
 * @param {string} options.privateKey - Base64-encoded Ed25519 private key
 * @param {string} [options.handle] - Bot handle (for credential file naming)
 * @param {string} [options.credentialsFile] - Path to credentials file to read/update
 * @param {string} [options.apiBase] - API base URL
 * @returns {Promise<AuthResult>}
 */
export async function getValidToken(options) {
  const { botProfileId, privateKey, credentialsFile, apiBase } = options;

  // If credentials file provided, try reading cached token
  if (credentialsFile) {
    try {
      const creds = await readCredentials(credentialsFile);
      const identityMatches =
        (!botProfileId || creds.botProfileId === botProfileId) &&
        (!privateKey || creds.privateKey === privateKey);
      if (identityMatches && isTokenValid(creds)) {
        return { botToken: creds.botToken, expiresAt: creds.tokenExpiresAt };
      }
      // Fall through to re-authenticate (identity mismatch or token expired)
    } catch {
      // File doesn't exist or is invalid — proceed with fresh auth
    }
  }

  // Authenticate
  const result = await authenticate(
    botProfileId,
    privateKey,
    apiBase,
  );

  // Update credentials file if provided
  if (credentialsFile) {
    try {
      let creds;
      try {
        creds = await readCredentials(credentialsFile);
      } catch {
        creds = {};
      }
      creds.botProfileId = botProfileId;
      creds.privateKey = privateKey;
      if (options.handle) creds.handle = options.handle;
      creds.botToken = result.botToken;
      creds.tokenExpiresAt = result.expiresAt;
      await saveCredentials(credentialsFile, creds);
    } catch (error) {
      // Non-fatal — token is still valid, just couldn't cache it
      console.warn(`Warning: Could not update credentials file: ${error.message}`);
    }
  }

  return result;
}

/**
 * Parse CLI arguments.
 * @param {string[]} args - process.argv.slice(2)
 * @returns {object}
 */
function parseCLIArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--profile-id':
        result.botProfileId = args[++i];
        break;
      case '--private-key':
        result.privateKey = args[++i];
        break;
      case '--credentials':
        result.credentialsFile = args[++i];
        break;
      case '--api-base':
        result.apiBase = args[++i];
        break;
      default:
        break;
    }
  }
  return result;
}

// Run as CLI if invoked directly
const isMainModule =
  typeof process !== 'undefined' &&
  process.argv[1] &&
  (process.argv[1].endsWith('/auth.js') || process.argv[1].endsWith('\\auth.js'));

if (isMainModule) {
  try {
    const cliOpts = parseCLIArgs(process.argv.slice(2));

    let botProfileId = cliOpts.botProfileId;
    let privateKey = cliOpts.privateKey;
    const credentialsFile = cliOpts.credentialsFile;
    const apiBase = cliOpts.apiBase;

    // If credentials file provided, read missing fields from it
    if (credentialsFile && (!botProfileId || !privateKey)) {
      const creds = await readCredentials(credentialsFile);
      botProfileId = botProfileId || creds.botProfileId;
      privateKey = privateKey || creds.privateKey;
    }

    if (!botProfileId || !privateKey) {
      console.error('Usage:');
      console.error('  node auth.js --profile-id <uuid> --private-key <base64>');
      console.error('  node auth.js --credentials <path-to-credentials.json>');
      process.exit(1);
    }

    const result = await getValidToken({
      botProfileId,
      privateKey,
      credentialsFile,
      apiBase,
    });

    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}
