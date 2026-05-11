#!/usr/bin/env node
/**
 * export-seed.js — Decrypt a WDK vault and print the BIP-39 mnemonic.
 *
 * Usage:
 *   node lib/export-seed.js [--password-file <path>] [--vault-file <path>]
 *
 * Defaults:
 *   --password-file  ~/.aurehub/.wdk_password
 *   --vault-file     ~/.aurehub/.wdk_vault
 *
 * Security:
 *   - Requires an interactive terminal (TTY). Refuses to run when stdout is
 *     piped or captured (e.g. by an AI agent) to prevent seed leakage.
 *   - Prompts for confirmation before revealing the mnemonic.
 *   - Displays the seed briefly, then offers to clear the screen.
 */

import { readFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { pbkdf2Sync } from 'crypto';
import { createInterface } from 'readline';

import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const sodium = require('sodium-native');
const b4a = require('b4a');
const bip39 = require('bip39-mnemonic');

function expandTilde(p) {
  if (typeof p === 'string' && p.startsWith('~/')) {
    return join(homedir(), p.slice(2));
  }
  return p;
}

function fatal(msg) {
  process.stderr.write(`Error: ${msg}\n`);
  process.exit(1);
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const opts = {
    passwordFile: join(homedir(), '.aurehub', '.wdk_password'),
    vaultFile: join(homedir(), '.aurehub', '.wdk_vault'),
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--password-file') {
      opts.passwordFile = expandTilde(args[++i]);
    } else if (arg === '--vault-file') {
      opts.vaultFile = expandTilde(args[++i]);
    } else {
      fatal(`Unknown argument: ${arg}`);
    }
  }

  return opts;
}

/**
 * Prompt the user on the TTY and return their answer.
 * Prompts are written to stderr so stdout stays clean.
 */
function askTty(question) {
  return new Promise((resolve) => {
    const rl = createInterface({
      input: process.stdin,
      output: process.stderr,
      terminal: true,
    });
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

function wdkDecrypt(payload, key) {
  const NONCEBYTES = sodium.crypto_secretbox_NONCEBYTES;
  const MACBYTES = sodium.crypto_secretbox_MACBYTES;

  if (payload[0] !== 0) throw new Error('Unsupported encryption version');

  const nonce = payload.subarray(1, 1 + NONCEBYTES);
  const cipher = payload.subarray(1 + NONCEBYTES);
  const plain = b4a.alloc(cipher.byteLength - MACBYTES);

  if (!sodium.crypto_secretbox_open_easy(plain, cipher, nonce, key)) {
    throw new Error('Decryption failed — wrong password or corrupted vault');
  }

  const bytes = plain[0];
  const result = b4a.alloc(bytes);
  result.set(plain.subarray(1, 1 + bytes));
  sodium.sodium_memzero(plain);
  return result;
}

async function main() {
  const opts = parseArgs(process.argv);

  // ── TTY gate: refuse to reveal seed in non-interactive contexts ──────────
  if (!process.stdin.isTTY || !process.stdout.isTTY || !process.stderr.isTTY) {
    fatal(
      'This command must be run in an interactive terminal.\n' +
      'It cannot be executed by scripts, agents, or piped commands\n' +
      'to prevent your seed phrase from leaking into logs or chat history.\n\n' +
      'Open a terminal window and run the command directly.'
    );
  }

  // ── Decrypt vault ────────────────────────────────────────────────────────
  let password;
  try {
    password = readFileSync(opts.passwordFile, 'utf8').trim();
  } catch (err) {
    fatal(`Cannot read password file "${opts.passwordFile}": ${err.message}`);
  }

  let vaultJson;
  try {
    vaultJson = readFileSync(opts.vaultFile, 'utf8');
  } catch (err) {
    fatal(`Cannot read vault file "${opts.vaultFile}": ${err.message}`);
  }

  const vault = JSON.parse(vaultJson);
  if (!vault.encryptedEntropy || !vault.salt) {
    fatal('Vault is missing required fields: encryptedEntropy, salt');
  }

  const salt = Buffer.from(vault.salt, 'hex');
  const encryptedEntropy = Buffer.from(vault.encryptedEntropy, 'hex');
  const key = pbkdf2Sync(password, salt, 100_000, 32, 'sha256');
  const entropy = wdkDecrypt(encryptedEntropy, key);
  key.fill(0);
  const mnemonic = bip39.entropyToMnemonic(entropy);
  sodium.sodium_memzero(entropy);

  // ── Interactive confirmation ─────────────────────────────────────────────
  process.stderr.write('\n');
  process.stderr.write('  ┌─────────────────────────────────────────────────────┐\n');
  process.stderr.write('  │  WARNING: Your seed phrase is about to be displayed │\n');
  process.stderr.write('  │                                                     │\n');
  process.stderr.write('  │  • Make sure no one can see your screen             │\n');
  process.stderr.write('  │  • Do not screenshot or copy to clipboard           │\n');
  process.stderr.write('  │  • Write the words on paper and store offline       │\n');
  process.stderr.write('  └─────────────────────────────────────────────────────┘\n');
  process.stderr.write('\n');

  const confirm = await askTty('  Type "yes" to reveal your seed phrase: ');
  if (confirm.toLowerCase() !== 'yes') {
    process.stderr.write('  Cancelled.\n');
    process.exit(0);
  }

  // ── Display seed phrase ──────────────────────────────────────────────────
  process.stderr.write('\n  Your 12-word seed phrase:\n\n');
  process.stderr.write(`  ${mnemonic}\n`);
  process.stderr.write('\n');

  // ── Post-display: offer to clear screen ──────────────────────────────────
  const clear = await askTty('  Press Enter to clear the screen (or type "keep" to leave it): ');
  if (clear.toLowerCase() !== 'keep') {
    // ANSI escape: clear screen + move cursor to top
    process.stdout.write('\x1b[2J\x1b[H');
    process.stderr.write('  Screen cleared. Your seed phrase is no longer visible.\n');
  }
}

main().catch(err => {
  process.stderr.write(`Error: ${err.message}\n`);
  process.exit(1);
});
