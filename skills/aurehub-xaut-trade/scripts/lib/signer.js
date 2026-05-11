import { readFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

/** Expand leading ~ to the user's home directory. */
function expandTilde(p) {
  if (typeof p === 'string' && p.startsWith('~/')) {
    return join(homedir(), p.slice(2));
  }
  return p;
}
import { pbkdf2Sync } from 'crypto';
import { Wallet } from 'ethers6';

// sodium-native is a CJS module; we import it via createRequire
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const sodium = require('sodium-native');
const b4a = require('b4a');
const bip39 = require('bip39-mnemonic');

// ---------------------------------------------------------------------------
// WDK vault decryption helpers
//
// @tetherto/wdk-secret-manager uses bare-crypto for PBKDF2 key derivation,
// which relies on Bare-runtime native bindings (.bare files) incompatible
// with standard Node.js.  We replicate the same algorithm using Node.js
// built-in `crypto.pbkdf2Sync` + `sodium-native`, producing byte-for-byte
// identical results.
//
// Vault format:
//   { encryptedEntropy: <hex>, salt: <hex> }
//
// Encryption format (from WdkSecretManager source):
//   byte 0     : version (0)
//   bytes 1..N : nonce   (crypto_secretbox_NONCEBYTES = 24)
//   bytes N+1..: ciphertext (1 + plaintextLen + MACBYTES)
//                  plain[0]  = original payload length
//                  plain[1..]: payload bytes
// ---------------------------------------------------------------------------

/**
 * Derive a 32-byte key from password + salt using PBKDF2-SHA256.
 * Matches WdkSecretManager#deriveKeyFromPassKey() (100 000 iterations).
 *
 * @param {string|Buffer} password
 * @param {Buffer} salt  16-byte salt
 * @returns {Buffer}
 */
function wdkDeriveKey(password, salt) {
  return pbkdf2Sync(password, salt, 100_000, 32, 'sha256');
}

/**
 * Decrypt a WDK-encrypted payload.
 * Matches WdkSecretManager.decrypt().
 *
 * @param {Buffer} payload  Encrypted bytes
 * @param {Buffer} key      32-byte derived key
 * @returns {Buffer}  Decrypted entropy bytes
 */
function wdkDecrypt(payload, key) {
  const NONCEBYTES = sodium.crypto_secretbox_NONCEBYTES;
  const MACBYTES = sodium.crypto_secretbox_MACBYTES;

  if (payload[0] !== 0) throw new Error('WDK vault: unsupported encryption version');

  const nonce = payload.subarray(1, 1 + NONCEBYTES);
  const cipher = payload.subarray(1 + NONCEBYTES);
  const plain = b4a.alloc(cipher.byteLength - MACBYTES);

  if (!sodium.crypto_secretbox_open_easy(plain, cipher, nonce, key)) {
    throw new Error('WDK vault: decryption failed — wrong password or corrupted vault');
  }

  const bytes = plain[0];
  const result = b4a.alloc(bytes);
  result.set(plain.subarray(1, 1 + bytes));
  sodium.sodium_memzero(plain);
  return result;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Create an ethers.Wallet connected to `provider` from the wallet backend
 * specified by cfg.env.WALLET_MODE.
 *
 * Supported modes:
 *   'foundry' — decrypt a Foundry keystore JSON file with KEYSTORE_PASSWORD_FILE
 *   'wdk'     — decrypt a WDK vault file with WDK_PASSWORD_FILE
 *
 * @param {{ env: object, yaml: object, configDir: string }} cfg
 *   Config object returned by loadConfig().
 * @param {import('ethers').Provider|null} provider
 *   ethers provider to connect the wallet to (may be null/undefined).
 * @param {{ keystoreDir?: string }} [opts]
 *   Optional overrides for testing (e.g. keystoreDir to override Foundry default).
 * @returns {Promise<import('ethers').Wallet>}
 */
export async function createSigner(cfg, provider, opts = {}) {
  const walletMode = cfg?.env?.WALLET_MODE;

  if (!walletMode) {
    throw new Error(
      'WALLET_MODE not set in .env. Run setup to select a wallet mode.',
    );
  }

  if (walletMode === 'foundry') {
    return _createFoundrySigner(cfg, provider, opts);
  }

  if (walletMode === 'wdk') {
    return _createWdkSigner(cfg, provider);
  }

  throw new Error(
    `Unknown wallet_mode "${walletMode}". Expected "foundry" or "wdk".`,
  );
}

// ---------------------------------------------------------------------------
// Foundry keystore backend
// ---------------------------------------------------------------------------

async function _createFoundrySigner(cfg, provider, opts) {
  const accountName = cfg.env.FOUNDRY_ACCOUNT;
  if (!accountName) {
    throw new Error('FOUNDRY_ACCOUNT not set in .env');
  }

  const keystoreDir =
    opts.keystoreDir ?? join(homedir(), '.foundry', 'keystores');
  const keystorePath = join(expandTilde(keystoreDir), accountName);

  let keystoreJson;
  try {
    keystoreJson = readFileSync(keystorePath, 'utf8');
  } catch (err) {
    throw new Error(
      `Foundry keystore not found at "${keystorePath}": ${err.message}`,
    );
  }

  const passwordFile = expandTilde(cfg.env.KEYSTORE_PASSWORD_FILE);
  if (!passwordFile) {
    throw new Error('KEYSTORE_PASSWORD_FILE not set in .env');
  }

  let password;
  try {
    password = readFileSync(passwordFile, 'utf8').trim();
  } catch (err) {
    throw new Error(
      `Cannot read KEYSTORE_PASSWORD_FILE "${passwordFile}": ${err.message}`,
    );
  }

  const wallet = await Wallet.fromEncryptedJson(keystoreJson, password);
  return provider ? wallet.connect(provider) : wallet;
}

// ---------------------------------------------------------------------------
// WDK vault backend
// ---------------------------------------------------------------------------

async function _createWdkSigner(cfg, provider) {
  const vaultPath = expandTilde(
    cfg.env.WDK_VAULT_FILE ??
    join(homedir(), '.aurehub', '.wdk_vault'),
  );

  let vaultJson;
  try {
    vaultJson = readFileSync(vaultPath, 'utf8');
  } catch (err) {
    throw new Error(`WDK vault not found at "${vaultPath}": ${err.message}`);
  }

  const vault = JSON.parse(vaultJson);
  if (!vault.encryptedEntropy || !vault.salt) {
    throw new Error(
      'WDK vault is missing required fields: encryptedEntropy, salt',
    );
  }

  const passwordFile = expandTilde(
    cfg.env.WDK_PASSWORD_FILE ??
    join(homedir(), '.aurehub', '.wdk_password'),
  );

  let password;
  try {
    password = readFileSync(passwordFile, 'utf8').trim();
  } catch (err) {
    throw new Error(
      `Cannot read WDK_PASSWORD_FILE "${passwordFile}": ${err.message}`,
    );
  }

  const salt = Buffer.from(vault.salt, 'hex');
  const encryptedEntropy = Buffer.from(vault.encryptedEntropy, 'hex');

  const key = wdkDeriveKey(password, salt);
  const entropy = wdkDecrypt(encryptedEntropy, key);
  key.fill(0);
  let wallet;
  try {
    const mnemonic = bip39.entropyToMnemonic(entropy);
    wallet = Wallet.fromPhrase(mnemonic);
  } finally {
    sodium.sodium_memzero(entropy);
  }
  return provider ? wallet.connect(provider) : wallet;
}
