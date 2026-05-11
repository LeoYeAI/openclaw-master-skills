#!/usr/bin/env node
/**
 * create-wallet.js — CLI script to create an encrypted WDK vault file.
 *
 * Usage:
 *   node lib/create-wallet.js --password-file <path> [--vault-file <path>] [--force]
 *
 * Outputs JSON to stdout: { address, vaultFile }
 *
 * The vault format is compatible with signer.js / WdkSecretManager:
 *   { encryptedEntropy: <hex>, salt: <hex> }
 *
 * encryptedEntropy hex encodes: [version=0][nonce(24b)][secretbox_easy(plain, nonce, key)]
 *   where plain = [length_byte, ...entropy_bytes]
 */

import { readFileSync, writeFileSync, existsSync, chmodSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { homedir } from 'os';

/** Expand leading ~ to the user's home directory. */
function expandTilde(p) {
  if (typeof p === 'string' && p.startsWith('~/')) {
    return join(homedir(), p.slice(2));
  }
  return p;
}
import { randomBytes, pbkdf2Sync } from 'crypto';
import { Wallet } from 'ethers6';

// sodium-native and bip39-mnemonic are CJS; load via createRequire
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const sodium = require('sodium-native');
const b4a = require('b4a');
const bip39 = require('bip39-mnemonic');

// ---------------------------------------------------------------------------
// CLI argument parsing
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = argv.slice(2);
  const opts = {
    passwordFile: null,
    vaultFile: join(homedir(), '.aurehub', '.wdk_vault'),
    force: false,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--password-file') {
      opts.passwordFile = expandTilde(args[++i]);
    } else if (arg === '--vault-file') {
      opts.vaultFile = expandTilde(args[++i]);
    } else if (arg === '--force') {
      opts.force = true;
    } else {
      fatal(`Unknown argument: ${arg}`);
    }
  }

  if (!opts.passwordFile) {
    fatal('--password-file is required');
  }

  return opts;
}

// ---------------------------------------------------------------------------
// Error helpers
// ---------------------------------------------------------------------------

function fatal(msg) {
  process.stderr.write(`Error: ${msg}\n`);
  process.exit(1);
}

// ---------------------------------------------------------------------------
// WDK vault encryption
//
// Matches WdkSecretManager#encrypt() exactly so signer.js can decrypt.
//
// Encryption layout (encryptedEntropy hex):
//   byte 0        : version = 0
//   bytes 1..24   : nonce (crypto_secretbox_NONCEBYTES = 24)
//   bytes 25..end : ciphertext from crypto_secretbox_easy
//                     plain = [length_byte(1), ...entropy]
// ---------------------------------------------------------------------------

function wdkEncrypt(entropy, key) {
  const NONCEBYTES = sodium.crypto_secretbox_NONCEBYTES; // 24
  const MACBYTES = sodium.crypto_secretbox_MACBYTES;     // 16
  const buffLength = entropy.byteLength;

  const nonce = b4a.alloc(NONCEBYTES);
  sodium.randombytes_buf(nonce);

  // Total payload: 1 (version) + 24 (nonce) + 1 (length) + buffLength + 16 (mac)
  const payload = b4a.alloc(1 + NONCEBYTES + 1 + buffLength + MACBYTES);
  payload[0] = 0; // version
  payload.set(nonce, 1);

  // cipher occupies the rest: 1 + buffLength + MACBYTES bytes
  const cipher = payload.subarray(1 + NONCEBYTES);
  // plain is cipher minus MAC trailer
  const plain = cipher.subarray(0, cipher.byteLength - MACBYTES);
  plain[0] = buffLength;
  plain.set(entropy, 1);

  sodium.crypto_secretbox_easy(cipher, plain, nonce, key);

  return payload;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const opts = parseArgs(process.argv);

  // 1. Read password
  let password;
  try {
    password = readFileSync(opts.passwordFile, 'utf8').trim();
  } catch (err) {
    fatal(`Cannot read password file "${opts.passwordFile}": ${err.message}`);
  }

  // 2. Validate password length
  if (password.length < 12) {
    fatal('Password must be at least 12 characters long');
  }

  // 3. Check vault file existence
  if (existsSync(opts.vaultFile) && !opts.force) {
    fatal(`Vault file already exists at "${opts.vaultFile}". Use --force to overwrite.`);
  }

  // 4. Generate 16 bytes random entropy (BIP-39 seed)
  const entropy = randomBytes(16);

  // 5. Generate 16-byte random salt for PBKDF2 key derivation (matches WDK source)
  const salt = randomBytes(16);

  // 6. Derive 32-byte key via PBKDF2-SHA256
  const key = pbkdf2Sync(password, salt, 100_000, 32, 'sha256');

  // 7. Encrypt entropy using XSalsa20-Poly1305 (WDK format)
  const encryptedEntropy = wdkEncrypt(entropy, key);
  key.fill(0);

  // 8. Assemble vault JSON
  const vault = {
    encryptedEntropy: encryptedEntropy.toString('hex'),
    salt: salt.toString('hex'),
  };

  // 9. Ensure parent directory exists
  const vaultDir = dirname(opts.vaultFile);
  mkdirSync(vaultDir, { recursive: true });

  // 10. Write vault file
  writeFileSync(opts.vaultFile, JSON.stringify(vault, null, 2), { encoding: 'utf8' });

  // 11. Set permissions to 600
  chmodSync(opts.vaultFile, 0o600);

  // 12. Derive wallet address: entropy → mnemonic → Wallet.fromPhrase
  let wallet;
  try {
    const mnemonic = bip39.entropyToMnemonic(entropy);
    wallet = Wallet.fromPhrase(mnemonic);
  } finally {
    sodium.sodium_memzero(entropy);
  }

  // 13. Output result as JSON to stdout
  process.stdout.write(JSON.stringify({ address: wallet.address, vaultFile: opts.vaultFile }) + '\n');
}

main().catch(err => {
  process.stderr.write(`Error: ${err.message}\n`);
  process.exit(1);
});
