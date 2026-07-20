#!/usr/bin/env node
// ============================================
// AGENT-PLAY — Lightweight CLI for Agent Gameplay
// Usage: node agent-play.js <command> [args]
// ============================================

import { Keypair, Transaction, PublicKey, Connection, LAMPORTS_PER_SOL } from '@solana/web3.js';
import bs58 from 'bs58';
import nacl from 'tweetnacl';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { createHash } from 'crypto';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

// ─────────────────────────────────────────
// Configuration
// ─────────────────────────────────────────

const BACKEND_URL = process.env.BACKEND_URL || 'https://api.defipoly.app';
const SOLANA_RPC = process.env.SOLANA_RPC || 'https://api.mainnet-beta.solana.com';
const DEFI_MINT = 'FCTD8DyMCDTL76EuGMGpLjxLXsdy46pnXMBeYNwypump';
const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = join(__dirname, '..');
const DEFAULT_WALLET_PATH = join(SKILL_DIR, '.wallet.json');

// ─────────────────────────────────────────
// Wallet Loading
// ─────────────────────────────────────────

function loadWalletFromFile(filePath) {
  const raw = JSON.parse(readFileSync(filePath, 'utf8'));
  const bytes = new Uint8Array(raw.secretKey || raw);
  return Keypair.fromSecretKey(bytes);
}

function loadWallet() {
  // Method 1: Explicit JSON keypair file via env
  if (process.env.WALLET_FILE) {
    return loadWalletFromFile(process.env.WALLET_FILE);
  }

  // Method 2: Base58 private key via env
  if (process.env.WALLET_PRIVATE_KEY) {
    return Keypair.fromSecretKey(bs58.decode(process.env.WALLET_PRIVATE_KEY));
  }

  // Method 3: Auto-discover .wallet.json in skill directory
  if (existsSync(DEFAULT_WALLET_PATH)) {
    return loadWalletFromFile(DEFAULT_WALLET_PATH);
  }

  fail('No wallet found. Run the "setup" command first, or set WALLET_FILE / WALLET_PRIVATE_KEY env var.');
}

// ─────────────────────────────────────────
// JWT Token Caching
// ─────────────────────────────────────────

function tokenCachePath(wallet) {
  const hash = createHash('sha256').update(wallet).digest('hex').slice(0, 12);
  return `/tmp/defipoly-agent-${hash}.json`;
}

function loadCachedToken(wallet) {
  const path = tokenCachePath(wallet);
  if (!existsSync(path)) return null;
  try {
    const data = JSON.parse(readFileSync(path, 'utf8'));
    if (data.wallet !== wallet) return null;
    // Expired if less than 5 minutes remaining
    if (data.expiresAt && Date.now() > data.expiresAt - 5 * 60 * 1000) return null;
    return data.token;
  } catch {
    return null;
  }
}

function saveCachedToken(wallet, token) {
  const data = {
    token,
    wallet,
    expiresAt: Date.now() + 23 * 60 * 60 * 1000, // 23h (conservative)
  };
  writeFileSync(tokenCachePath(wallet), JSON.stringify(data));
}

// ─────────────────────────────────────────
// Authentication
// ─────────────────────────────────────────

async function authenticate(keypair) {
  const wallet = keypair.publicKey.toBase58();

  // Step 1: Get nonce
  const nonceRes = await apiFetch(`/api/auth/nonce?wallet=${wallet}`);
  const { nonce } = nonceRes;

  // Step 2: Sign the nonce message
  const message = `Sign this message to authenticate with Defipoly.\n\nNonce: ${nonce}`;
  const messageBytes = new TextEncoder().encode(message);
  const signature = nacl.sign.detached(messageBytes, keypair.secretKey);

  // Step 3: Get JWT
  const verifyRes = await apiFetch('/api/auth/verify', {
    method: 'POST',
    body: { wallet, signature: bs58.encode(Buffer.from(signature)), nonce },
  });

  saveCachedToken(wallet, verifyRes.token);
  return verifyRes.token;
}

let _cachedToken = null;

async function ensureAuth(keypair) {
  if (_cachedToken) return _cachedToken;

  const wallet = keypair.publicKey.toBase58();
  const cached = loadCachedToken(wallet);
  if (cached) {
    _cachedToken = cached;
    return cached;
  }

  _cachedToken = await authenticate(keypair);
  return _cachedToken;
}

// ─────────────────────────────────────────
// HTTP Helpers
// ─────────────────────────────────────────

async function apiFetch(path, opts = {}) {
  const url = `${BACKEND_URL}${path}`;
  const headers = { 'Content-Type': 'application/json', 'Origin': 'https://defipoly.app' };
  if (opts.token) headers['Authorization'] = `Bearer ${opts.token}`;

  const fetchOpts = { method: opts.method || 'GET', headers };
  if (opts.body) fetchOpts.body = JSON.stringify(opts.body);

  const res = await fetch(url, fetchOpts);

  if (res.status === 429) {
    fail(`Rate limited. Wait before retrying.`);
  }

  const data = await res.json();

  if (!res.ok) {
    throw Object.assign(new Error(data.error || data.message || `HTTP ${res.status}`), { status: res.status });
  }

  return data;
}

async function authedFetch(keypair, path, opts = {}) {
  const token = await ensureAuth(keypair);
  try {
    return await apiFetch(path, { ...opts, token });
  } catch (err) {
    // Auto-retry on 401
    if (err.status === 401) {
      _cachedToken = null;
      const newToken = await authenticate(keypair);
      return await apiFetch(path, { ...opts, token: newToken });
    }
    throw err;
  }
}

// ─────────────────────────────────────────
// Build → Sign → Submit
// ─────────────────────────────────────────

async function executeAction(keypair, endpoint, body = {}) {
  // 1. Build
  const buildData = await authedFetch(keypair, `/api/agent/build/${endpoint}`, {
    method: 'POST',
    body,
  });

  if (!buildData.success && !buildData.transaction) {
    fail(buildData.error || 'Build failed');
  }

  // 2. Sign
  const tx = Transaction.from(Buffer.from(buildData.transaction, 'base64'));
  tx.partialSign(keypair);
  const signedTx = tx.serialize({ requireAllSignatures: false }).toString('base64');

  // 3. Submit
  const submitBody = { transaction: signedTx };
  if (buildData.approvalId) submitBody.approvalId = buildData.approvalId;

  const result = await authedFetch(keypair, '/api/agent/submit', {
    method: 'POST',
    body: submitBody,
  });

  if (!result.success) {
    fail(result.error || 'Submit failed');
  }

  return { signature: result.signature, details: buildData.details || result.details };
}

// ─────────────────────────────────────────
// Output Helpers
// ─────────────────────────────────────────

function fail(msg) {
  console.error(`FAIL ${msg}`);
  process.exit(1);
}

function printAction(action, params, sig) {
  const parts = Object.entries(params).map(([k, v]) => `${k}=${v}`);
  console.log(`OK ${action} ${parts.join(' ')} sig=${sig}`);
}

// ─────────────────────────────────────────
// Commands
// ─────────────────────────────────────────

async function cmdAuth(keypair) {
  const token = await authenticate(keypair);
  console.log(`OK auth wallet=${keypair.publicKey.toBase58()} token=${token.slice(0, 20)}...`);
}

async function cmdInit(keypair) {
  const { signature } = await executeAction(keypair, 'init');
  printAction('init', {}, signature);
}

async function cmdBuy(keypair, args) {
  const propertyId = parseInt(args[0]);
  const slots = parseInt(args[1]) || 1;
  if (isNaN(propertyId)) fail('Usage: buy <propertyId> [slots=1]');
  const { signature } = await executeAction(keypair, 'buy', { propertyId, slots });
  printAction('buy', { propertyId, slots }, signature);
}

async function cmdSell(keypair, args) {
  const propertyId = parseInt(args[0]);
  const slots = parseInt(args[1]);
  if (isNaN(propertyId) || isNaN(slots)) fail('Usage: sell <propertyId> <slots>');
  const { signature } = await executeAction(keypair, 'sell', { propertyId, slots });
  printAction('sell', { propertyId, slots }, signature);
}

async function cmdShield(keypair, args) {
  const propertyId = parseInt(args[0]);
  const hours = parseInt(args[1]) || 24;
  if (isNaN(propertyId)) fail('Usage: shield <propertyId> [hours=24]');
  const { signature } = await executeAction(keypair, 'shield', { propertyId, hours });
  printAction('shield', { propertyId, hours }, signature);
}

async function cmdClaim(keypair) {
  const { signature } = await executeAction(keypair, 'claim');
  printAction('claim', {}, signature);
}

async function cmdBankSteal(keypair, args) {
  const propertyId = parseInt(args[0]);
  if (isNaN(propertyId)) fail('Usage: bank-steal <propertyId>');
  const { signature, details } = await executeAction(keypair, 'bank-steal', { propertyId });
  const success = details?.success ?? true;
  printAction('bank-steal', { propertyId, success }, signature);
}

async function cmdSteal(keypair, args) {
  const targetWallet = args[0];
  const propertyId = parseInt(args[1]);
  if (!targetWallet || isNaN(propertyId)) fail('Usage: steal <targetWallet> <propertyId>');
  const { signature, details } = await executeAction(keypair, 'steal', { targetWallet, propertyId });
  const success = details?.success ?? true;
  printAction('steal', { targetWallet, propertyId, success }, signature);
}

// ─── Dice Commands ───────────────────────

async function cmdDiceRoll(keypair) {
  const result = await authedFetch(keypair, '/api/agent/dice/roll', { method: 'POST' });
  console.log(JSON.stringify(result, null, 2));
}

async function cmdDiceStatus(keypair) {
  const result = await authedFetch(keypair, '/api/agent/dice/status');
  console.log(JSON.stringify(result, null, 2));
}

async function cmdDiceBuy(keypair, args) {
  const propertyId = parseInt(args[0]);
  const slots = parseInt(args[1]) || 1;
  if (isNaN(propertyId)) fail('Usage: dice-buy <propertyId> [slots=1]');
  const { signature, details } = await executeAction(keypair, 'dice-buy', { propertyId, slots });
  printAction('dice-buy', { propertyId, slots, discountBps: details?.discountBps }, signature);
}

async function cmdDiceClaimSnakeEyes(keypair) {
  const { signature, details } = await executeAction(keypair, 'dice-claim-snake-eyes');
  printAction('dice-claim-snake-eyes', { bonusAmount: details?.bonusAmount }, signature);
}

async function cmdDiceClaimDefense(keypair) {
  const { signature, details } = await executeAction(keypair, 'dice-claim-defense');
  printAction('dice-claim-defense', { durationHours: details?.durationHours }, signature);
}

async function cmdDiceClaimCompound(keypair) {
  const { signature, details } = await executeAction(keypair, 'dice-claim-compound');
  printAction('dice-claim-compound', { bonusPercent: details?.bonusPercent }, signature);
}

async function cmdDiceClaimCooldownReset(keypair) {
  const { signature } = await executeAction(keypair, 'dice-claim-cooldown-reset');
  printAction('dice-claim-cooldown-reset', {}, signature);
}

async function cmdDiceClaimStealCooldownReset(keypair) {
  const { signature } = await executeAction(keypair, 'dice-claim-steal-cooldown-reset');
  printAction('dice-claim-steal-cooldown-reset', {}, signature);
}

// ─── Setup & Balance Commands ────────────

async function cmdSetup(args) {
  // Import from base58 private key
  if (args[0]) {
    try {
      const keypair = Keypair.fromSecretKey(bs58.decode(args[0]));
      writeFileSync(DEFAULT_WALLET_PATH, JSON.stringify(Array.from(keypair.secretKey)));
      console.log(`OK setup wallet=${keypair.publicKey.toBase58()} saved=${DEFAULT_WALLET_PATH}`);
    } catch (e) {
      fail(`Invalid base58 private key: ${e.message}`);
    }
    return;
  }

  // Generate a new wallet
  const keypair = Keypair.generate();
  writeFileSync(DEFAULT_WALLET_PATH, JSON.stringify(Array.from(keypair.secretKey)));
  console.log(`OK setup wallet=${keypair.publicKey.toBase58()} saved=${DEFAULT_WALLET_PATH} NEW_WALLET=true`);
  console.error(`\nNew wallet generated: ${keypair.publicKey.toBase58()}`);
  console.error(`Fund it with SOL (for fees) and DPOLY tokens (to play).`);
  console.error(`Get DPOLY at https://defipoly.app`);
}

async function getDefiBalance(walletAddress) {
  const owner = new PublicKey(walletAddress);
  const mint = new PublicKey(DEFI_MINT);
  const connection = new Connection(SOLANA_RPC);

  // Get SOL balance
  const solBalance = await connection.getBalance(owner);

  // Get DEFI token accounts
  const tokenAccounts = await connection.getParsedTokenAccountsByOwner(owner, { mint });
  let dpolyBalance = 0;
  for (const { account } of tokenAccounts.value) {
    dpolyBalance += account.data.parsed.info.tokenAmount.uiAmount || 0;
  }

  return { sol: solBalance / LAMPORTS_PER_SOL, dpoly: dpolyBalance };
}

async function cmdBalance(args) {
  // Use provided address, or fall back to configured wallet
  let address;
  if (args[0]) {
    address = args[0];
  } else {
    try {
      const keypair = loadWallet();
      address = keypair.publicKey.toBase58();
    } catch {
      fail('Usage: balance <wallet_address> (or set up a wallet first with "setup")');
    }
  }

  const { sol, dpoly } = await getDefiBalance(address);
  console.log(JSON.stringify({ wallet: address, sol, dpoly, dpolyMint: DEFI_MINT }));
}

async function cmdScanWallets(args) {
  // Takes one or more wallet addresses, checks DEFI + SOL balance for each
  if (args.length === 0) fail('Usage: scan-wallets <address1> [address2] ...');

  const results = [];
  for (const addr of args) {
    try {
      const { sol, dpoly } = await getDefiBalance(addr);
      results.push({ wallet: addr, sol, dpoly, hasDpoly: dpoly > 0 });
    } catch (e) {
      results.push({ wallet: addr, error: e.message });
    }
  }
  console.log(JSON.stringify(results, null, 2));
}

// ─── Read-Only Commands ──────────────────

async function cmdStatus(keypair) {
  const wallet = keypair.publicKey.toBase58();
  const profile = await apiFetch(`/api/profile/${wallet}`);
  console.log(JSON.stringify(profile, null, 2));
}

async function cmdProperties(args) {
  if (args[0] !== undefined && args[0] !== '') {
    const id = parseInt(args[0]);
    if (isNaN(id)) fail('Usage: properties [id]');
    const state = await apiFetch(`/api/properties/${id}/state`);
    const stats = await apiFetch(`/api/properties/${id}/stats`);
    console.log(JSON.stringify({ ...state, ...stats }, null, 2));
  } else {
    const state = await apiFetch('/api/properties/state');
    const stats = await apiFetch('/api/properties/stats');
    console.log(JSON.stringify({ state: state.properties, stats: stats.properties }, null, 2));
  }
}

async function cmdConfig() {
  const config = await apiFetch('/api/game/config');
  console.log(JSON.stringify(config, null, 2));
}

async function cmdLeaderboard() {
  const lb = await apiFetch('/api/leaderboard?limit=100');
  console.log(JSON.stringify(lb, null, 2));
}

// ─────────────────────────────────────────
// Main
// ─────────────────────────────────────────

const USAGE = `Usage: node agent-play.js <command> [args]

Setup:    setup [base58_private_key]   — generate new wallet or import existing
Auth:     auth
Actions:  init | buy <id> [slots] | sell <id> <slots> | shield <id> [hours]
          claim | bank-steal <id> | steal <wallet> <id>
Dice:     dice-roll | dice-status | dice-buy <id> [slots]
          dice-claim-snake-eyes | dice-claim-defense | dice-claim-compound
          dice-claim-cooldown-reset | dice-claim-steal-cooldown-reset
Read:     status | properties [id] | config | leaderboard
          balance [address] | scan-wallets <addr1> [addr2] ...

Wallet auto-discovered at <skillDir>/.wallet.json if no env is set.
Env (optional): WALLET_FILE, WALLET_PRIVATE_KEY, BACKEND_URL, SOLANA_RPC`;

async function main() {
  const [command, ...args] = process.argv.slice(2);

  if (!command || command === '--help' || command === '-h') {
    console.log(USAGE);
    process.exit(0);
  }

  // Setup doesn't need an existing wallet
  if (command === 'setup') return cmdSetup(args);

  // These don't need a wallet (or handle it internally)
  const noWallet = ['properties', 'config', 'leaderboard', 'balance', 'scan-wallets'];
  if (noWallet.includes(command)) {
    switch (command) {
      case 'properties':   return cmdProperties(args);
      case 'config':       return cmdConfig();
      case 'leaderboard':  return cmdLeaderboard();
      case 'balance':      return cmdBalance(args);
      case 'scan-wallets': return cmdScanWallets(args);
    }
  }

  // All other commands need a wallet
  const keypair = loadWallet();

  switch (command) {
    case 'auth':       return cmdAuth(keypair);
    case 'init':       return cmdInit(keypair);
    case 'buy':        return cmdBuy(keypair, args);
    case 'sell':       return cmdSell(keypair, args);
    case 'shield':     return cmdShield(keypair, args);
    case 'claim':      return cmdClaim(keypair);
    case 'bank-steal': return cmdBankSteal(keypair, args);
    case 'steal':      return cmdSteal(keypair, args);
    case 'status':     return cmdStatus(keypair);
    // Dice commands
    case 'dice-roll':   return cmdDiceRoll(keypair);
    case 'dice-status': return cmdDiceStatus(keypair);
    case 'dice-buy':    return cmdDiceBuy(keypair, args);
    case 'dice-claim-snake-eyes':          return cmdDiceClaimSnakeEyes(keypair);
    case 'dice-claim-defense':             return cmdDiceClaimDefense(keypair);
    case 'dice-claim-compound':            return cmdDiceClaimCompound(keypair);
    case 'dice-claim-cooldown-reset':      return cmdDiceClaimCooldownReset(keypair);
    case 'dice-claim-steal-cooldown-reset': return cmdDiceClaimStealCooldownReset(keypair);
    default:
      console.error(`Unknown command: ${command}`);
      console.log(USAGE);
      process.exit(1);
  }
}

main().catch((err) => {
  fail(err.message || String(err));
});
