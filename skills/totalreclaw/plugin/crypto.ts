/**
 * TotalReclaw Plugin - Crypto Operations
 *
 * All cryptographic primitives used by the OpenClaw plugin. These must
 * produce byte-for-byte identical output to the TotalReclaw client library
 * (`client/src/crypto/`) so that memories written by one can be read by
 * the other.
 *
 * Key derivation chain:
 *   master_password + salt
 *     -> Argon2id(t=3, m=65536, p=4, dkLen=32) -> masterKey
 *     -> HKDF-SHA256(masterKey, salt, "totalreclaw-auth-key-v1",       32) -> authKey
 *     -> HKDF-SHA256(masterKey, salt, "totalreclaw-encryption-key-v1", 32) -> encryptionKey
 *     -> HKDF-SHA256(masterKey, salt, "openmemory-dedup-v1",          32) -> dedupKey
 *
 * Encryption: AES-256-GCM (12-byte IV, 16-byte tag)
 * Blind indices: SHA-256 of lowercase tokens
 * Content fingerprint: HMAC-SHA256(dedupKey, normalizeText(plaintext))
 */

import { argon2id } from '@noble/hashes/argon2.js';
import { hkdf } from '@noble/hashes/hkdf.js';
import { sha256 } from '@noble/hashes/sha2.js';
import { hmac } from '@noble/hashes/hmac.js';
import { mnemonicToSeedSync, validateMnemonic } from '@scure/bip39';
import { wordlist } from '@scure/bip39/wordlists/english.js';
import { stemmer } from 'porter-stemmer';
import crypto from 'node:crypto';

// ---------------------------------------------------------------------------
// Key Derivation
// ---------------------------------------------------------------------------

/** HKDF context strings -- must match client/src/crypto/kdf.ts exactly. */
const AUTH_KEY_INFO = 'totalreclaw-auth-key-v1';
const ENCRYPTION_KEY_INFO = 'totalreclaw-encryption-key-v1';
const DEDUP_KEY_INFO = 'openmemory-dedup-v1';

/** Argon2id parameters -- OWASP recommendations, matching client defaults. */
const ARGON2_TIME_COST = 3;
const ARGON2_MEMORY_COST = 65536; // 64 MB in KiB
const ARGON2_PARALLELISM = 4;
const ARGON2_DK_LEN = 32;

/** AES-256-GCM constants. */
const IV_LENGTH = 12;
const TAG_LENGTH = 16;
const KEY_LENGTH = 32;

/**
 * Check if the input looks like a BIP-39 mnemonic (12 or 24 words from the BIP-39 English wordlist).
 */
function isBip39Mnemonic(input: string): boolean {
  const words = input.trim().split(/\s+/);
  if (words.length !== 12 && words.length !== 24) return false;
  return validateMnemonic(input.trim(), wordlist);
}

/**
 * Derive encryption keys from a BIP-39 mnemonic.
 * Uses the 512-bit BIP-39 seed as HKDF input (NOT the derived private key)
 * for proper key separation from the Ethereum signing key.
 */
function deriveKeysFromMnemonic(
  mnemonic: string,
): { authKey: Buffer; encryptionKey: Buffer; dedupKey: Buffer; salt: Buffer } {
  // BIP-39: mnemonic -> 512-bit seed via PBKDF2(mnemonic, "mnemonic", 2048 rounds)
  const seed = mnemonicToSeedSync(mnemonic.trim());

  // Use first 32 bytes of seed as deterministic salt for HKDF
  // (BIP-39 mnemonics are self-salting via PBKDF2, no random salt needed)
  const salt = Buffer.from(seed.slice(0, 32));

  // HKDF-SHA256 from the full 512-bit seed, using distinct info strings
  const enc = (s: string) => Buffer.from(s, 'utf8');
  const seedBuf = Buffer.from(seed);

  const authKey = Buffer.from(
    hkdf(sha256, seedBuf, salt, enc(AUTH_KEY_INFO), 32),
  );
  const encryptionKey = Buffer.from(
    hkdf(sha256, seedBuf, salt, enc(ENCRYPTION_KEY_INFO), 32),
  );
  const dedupKey = Buffer.from(
    hkdf(sha256, seedBuf, salt, enc(DEDUP_KEY_INFO), 32),
  );

  return { authKey, encryptionKey, dedupKey, salt };
}

/**
 * Derive auth, encryption, and dedup keys from a recovery phrase.
 *
 * If the password is a valid BIP-39 mnemonic (12 or 24 words), keys are
 * derived from the 512-bit BIP-39 seed via HKDF. Otherwise, the legacy
 * Argon2id path is used.
 *
 * For the Argon2id path: if no salt is provided a fresh 32-byte random salt
 * is generated. Pass an existing salt when restoring a previously-registered
 * account so that the derived keys match the original registration.
 *
 * @returns Object containing authKey, encryptionKey, dedupKey, and salt (all Buffers).
 */
export function deriveKeys(
  password: string,
  existingSalt?: Buffer,
): { authKey: Buffer; encryptionKey: Buffer; dedupKey: Buffer; salt: Buffer } {
  // Auto-detect BIP-39 mnemonic vs arbitrary password
  if (isBip39Mnemonic(password)) {
    // BIP-39 path: mnemonic is self-salting, existingSalt is ignored for derivation
    // but we still return the deterministic salt for server registration
    return deriveKeysFromMnemonic(password);
  }

  // Legacy path: arbitrary password via Argon2id
  const salt = existingSalt ?? crypto.randomBytes(32);

  // Step 1 -- Argon2id to derive a 32-byte master key.
  // @noble/hashes argon2id accepts Uint8Array for both password and salt.
  const masterKey = argon2id(
    Buffer.from(password, 'utf8'),
    salt,
    { t: ARGON2_TIME_COST, m: ARGON2_MEMORY_COST, p: ARGON2_PARALLELISM, dkLen: ARGON2_DK_LEN },
  );

  // Step 2 -- HKDF-SHA256 for each sub-key using distinct info strings.
  // @noble/hashes v2 requires Uint8Array for info param.
  const enc = (s: string) => Buffer.from(s, 'utf8');
  const authKey = Buffer.from(
    hkdf(sha256, masterKey, salt, enc(AUTH_KEY_INFO), 32),
  );
  const encryptionKey = Buffer.from(
    hkdf(sha256, masterKey, salt, enc(ENCRYPTION_KEY_INFO), 32),
  );
  const dedupKey = Buffer.from(
    hkdf(sha256, masterKey, salt, enc(DEDUP_KEY_INFO), 32),
  );

  return { authKey, encryptionKey, dedupKey, salt: Buffer.from(salt) };
}

// ---------------------------------------------------------------------------
// LSH Seed Derivation
// ---------------------------------------------------------------------------

/**
 * HKDF context string for LSH seed derivation.
 *
 * The LSH hasher needs a deterministic seed so that the same master key
 * always generates the same random hyperplane matrices. We derive this seed
 * from the master key using HKDF with a unique info string.
 *
 * For the BIP-39 path the HKDF input is the 512-bit BIP-39 seed; for the
 * Argon2id path it is the 32-byte master key.
 */
const LSH_SEED_INFO = 'openmemory-lsh-seed-v1';

/**
 * Derive a 32-byte seed for the LSH hasher from the master key derivation
 * chain.
 *
 * Call this once during initialization and pass the result to `new LSHHasher(seed, dims)`.
 *
 * For the BIP-39 path we use the full 512-bit BIP-39 seed as IKM; for the
 * Argon2id path we use the 32-byte Argon2id-derived master key. In both
 * cases the salt from `deriveKeys()` is reused for domain separation.
 */
export function deriveLshSeed(
  password: string,
  salt: Buffer,
): Uint8Array {
  if (isBip39Mnemonic(password)) {
    const seed = mnemonicToSeedSync(password.trim());
    return new Uint8Array(
      hkdf(sha256, Buffer.from(seed), salt, Buffer.from(LSH_SEED_INFO, 'utf8'), 32),
    );
  }

  // Argon2id path: re-derive the master key, then HKDF with LSH info string.
  const masterKey = argon2id(
    Buffer.from(password, 'utf8'),
    salt,
    { t: ARGON2_TIME_COST, m: ARGON2_MEMORY_COST, p: ARGON2_PARALLELISM, dkLen: ARGON2_DK_LEN },
  );

  return new Uint8Array(
    hkdf(sha256, masterKey, salt, Buffer.from(LSH_SEED_INFO, 'utf8'), 32),
  );
}

// ---------------------------------------------------------------------------
// Auth Key Hash
// ---------------------------------------------------------------------------

/**
 * Compute the SHA-256 hash of the auth key.
 *
 * The server stores SHA256(authKey) during registration and uses it to look
 * up users on every request. The hex string returned here is what the plugin
 * sends to `/v1/register` as `auth_key_hash`.
 */
export function computeAuthKeyHash(authKey: Buffer): string {
  return Buffer.from(sha256(authKey)).toString('hex');
}

// ---------------------------------------------------------------------------
// AES-256-GCM Encrypt / Decrypt
// ---------------------------------------------------------------------------

/**
 * Encrypt a UTF-8 plaintext string with AES-256-GCM.
 *
 * Wire format (base64-encoded):
 *   [iv: 12 bytes][tag: 16 bytes][ciphertext: variable]
 *
 * This matches `serializeEncryptedData` in `client/src/crypto/aes.ts`.
 */
export function encrypt(plaintext: string, encryptionKey: Buffer): string {
  if (encryptionKey.length !== KEY_LENGTH) {
    throw new Error(`Invalid key length: expected ${KEY_LENGTH}, got ${encryptionKey.length}`);
  }

  const iv = crypto.randomBytes(IV_LENGTH);
  const cipher = crypto.createCipheriv('aes-256-gcm', encryptionKey, iv, {
    authTagLength: TAG_LENGTH,
  });

  const ciphertext = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();

  // Combine: iv || tag || ciphertext  (same order as client library)
  const combined = Buffer.concat([iv, tag, ciphertext]);
  return combined.toString('base64');
}

/**
 * Decrypt a base64-encoded AES-256-GCM blob back to a UTF-8 string.
 *
 * Expects the wire format produced by `encrypt()` above.
 */
export function decrypt(encryptedBase64: string, encryptionKey: Buffer): string {
  if (encryptionKey.length !== KEY_LENGTH) {
    throw new Error(`Invalid key length: expected ${KEY_LENGTH}, got ${encryptionKey.length}`);
  }

  const combined = Buffer.from(encryptedBase64, 'base64');

  if (combined.length < IV_LENGTH + TAG_LENGTH) {
    throw new Error('Encrypted data too short');
  }

  const iv = combined.subarray(0, IV_LENGTH);
  const tag = combined.subarray(IV_LENGTH, IV_LENGTH + TAG_LENGTH);
  const ciphertext = combined.subarray(IV_LENGTH + TAG_LENGTH);

  const decipher = crypto.createDecipheriv('aes-256-gcm', encryptionKey, iv, {
    authTagLength: TAG_LENGTH,
  });
  decipher.setAuthTag(tag);

  const plaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  return plaintext.toString('utf8');
}

// ---------------------------------------------------------------------------
// Blind Indices
// ---------------------------------------------------------------------------

/**
 * Generate blind indices (SHA-256 hashes of tokens) for a text string.
 *
 * Tokenization rules (must match `client/src/crypto/blind.ts#tokenize`):
 *   1. Lowercase
 *   2. Remove punctuation (keep Unicode letters, numbers, whitespace)
 *   3. Split on whitespace
 *   4. Filter tokens shorter than 2 characters
 *
 * Each surviving token is SHA-256 hashed and returned as a hex string.
 * The returned array is deduplicated.
 */
export function generateBlindIndices(text: string): string[] {
  const tokens = text
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, ' ') // Remove punctuation, keep letters/numbers
    .split(/\s+/)
    .filter((t) => t.length >= 2);

  const seen = new Set<string>();
  const indices: string[] = [];

  for (const token of tokens) {
    // Exact word hash (unchanged behavior).
    const hash = Buffer.from(sha256(Buffer.from(token, 'utf8'))).toString('hex');
    if (!seen.has(hash)) {
      seen.add(hash);
      indices.push(hash);
    }

    // Stemmed word hash. The stem is prefixed with "stem:" before hashing
    // to avoid collisions between a word that happens to equal another
    // word's stem (e.g., the word "commun" vs the stem of "community").
    const stem = stemmer(token);
    if (stem.length >= 2 && stem !== token) {
      const stemHash = Buffer.from(
        sha256(Buffer.from(`stem:${stem}`, 'utf8'))
      ).toString('hex');
      if (!seen.has(stemHash)) {
        seen.add(stemHash);
        indices.push(stemHash);
      }
    }
  }

  return indices;
}

// ---------------------------------------------------------------------------
// Content Fingerprint (Dedup)
// ---------------------------------------------------------------------------

/**
 * Normalize text for deterministic fingerprinting.
 *
 * Steps (matching `client/src/crypto/fingerprint.ts#normalizeText`):
 *   1. Unicode NFC normalization
 *   2. Lowercase
 *   3. Collapse whitespace (spaces/tabs/newlines to single space)
 *   4. Trim leading/trailing whitespace
 */
function normalizeText(text: string): string {
  return text
    .normalize('NFC')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Compute an HMAC-SHA256 content fingerprint for exact-duplicate detection.
 *
 * The server stores this fingerprint and uses it to reject duplicate writes
 * without ever seeing the plaintext.
 *
 * @returns 64-character hex string.
 */
export function generateContentFingerprint(plaintext: string, dedupKey: Buffer): string {
  const normalized = normalizeText(plaintext);
  return Buffer.from(
    hmac(sha256, dedupKey, Buffer.from(normalized, 'utf8')),
  ).toString('hex');
}
