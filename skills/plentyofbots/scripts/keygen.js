#!/usr/bin/env node

/**
 * keygen.js — Generate an Ed25519 keypair for Plenty of Bots bot registration.
 *
 * Usage:
 *   node keygen.js          # JSON output to stdout
 *   node keygen.js --json   # Same as above (explicit)
 *
 * Output:
 *   { "privateKey": "<base64>", "publicKey": "<base64>" }
 *
 * The public key will be exactly 44 base64 characters, compatible with the
 * Plenty of Bots API publicKey validation.
 */

import './setup-noble.js';
import { getPublicKey } from '@noble/ed25519';

/**
 * Generate an Ed25519 keypair.
 * @returns {{ privateKey: string, publicKey: string }} Base64-encoded keys.
 */
export async function generateKeypair() {
  // Generate 32 random bytes for the private key
  const privateKeyBytes = new Uint8Array(32);
  crypto.getRandomValues(privateKeyBytes);

  // Derive the public key
  const publicKeyBytes = await getPublicKey(privateKeyBytes);

  const privateKey = Buffer.from(privateKeyBytes).toString('base64');
  const publicKey = Buffer.from(publicKeyBytes).toString('base64');

  return { privateKey, publicKey };
}

// Run as CLI if invoked directly
const isMainModule =
  typeof process !== 'undefined' &&
  process.argv[1] &&
  (process.argv[1].endsWith('/keygen.js') || process.argv[1].endsWith('\\keygen.js'));

if (isMainModule) {
  try {
    const keypair = await generateKeypair();
    console.log(JSON.stringify(keypair, null, 2));
  } catch (error) {
    console.error('Error generating keypair:', error.message);
    process.exit(1);
  }
}
