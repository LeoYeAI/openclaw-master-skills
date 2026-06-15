/**
 * web-autopilot: Encrypted Credential Storage
 * Stores login credentials (username/password) encrypted with AES-256-GCM.
 * Encryption key derived from machine identity + optional user passphrase.
 */

import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

const CREDENTIALS_FILE = path.join(process.env.HOME || '~', '.openclaw/rpa/credentials.enc');
const ALGORITHM = 'aes-256-gcm';
const KEY_LENGTH = 32;
const IV_LENGTH = 16;
const SALT_LENGTH = 32;
const TAG_LENGTH = 16;
const PBKDF2_ITERATIONS = 100_000;

// ─── Key Derivation ──────────────────────────────────────────────────────────

/** Derive encryption key from machine identity + optional passphrase */
function deriveKey(salt: Buffer, passphrase?: string): Buffer {
  // Machine-specific base: hostname + username + home dir
  const machineId = `${os.hostname()}:${os.userInfo().username}:${process.env.HOME || ''}`;
  const secret = passphrase ? `${machineId}:${passphrase}` : machineId;
  return crypto.pbkdf2Sync(secret, salt, PBKDF2_ITERATIONS, KEY_LENGTH, 'sha512');
}

// ─── Encrypt / Decrypt ───────────────────────────────────────────────────────

function encrypt(plaintext: string, passphrase?: string): Buffer {
  const salt = crypto.randomBytes(SALT_LENGTH);
  const iv = crypto.randomBytes(IV_LENGTH);
  const key = deriveKey(salt, passphrase);
  const cipher = crypto.createCipheriv(ALGORITHM, key, iv);
  const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  // Format: salt(32) + iv(16) + tag(16) + ciphertext
  return Buffer.concat([salt, iv, tag, encrypted]);
}

function decrypt(data: Buffer, passphrase?: string): string {
  const salt = data.subarray(0, SALT_LENGTH);
  const iv = data.subarray(SALT_LENGTH, SALT_LENGTH + IV_LENGTH);
  const tag = data.subarray(SALT_LENGTH + IV_LENGTH, SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
  const ciphertext = data.subarray(SALT_LENGTH + IV_LENGTH + TAG_LENGTH);
  const key = deriveKey(salt, passphrase);
  const decipher = crypto.createDecipheriv(ALGORITHM, key, iv);
  decipher.setAuthTag(tag);
  return decipher.update(ciphertext) + decipher.final('utf8');
}

// ─── Credential Store ────────────────────────────────────────────────────────

export interface Credential {
  username: string;
  password: string;
  authType?: string;         // e.g. "passwordAuth"
  loginApiPath?: string;     // e.g. "/api/sso/login"
  extraFields?: Record<string, any>;  // additional login form fields
}

interface CredentialStore {
  version: number;
  credentials: Record<string, Credential>;  // keyed by SSO domain
}

function getPassphrase(): string | undefined {
  return process.env.RPA_CREDENTIAL_KEY || undefined;
}

function loadStore(): CredentialStore {
  if (!fs.existsSync(CREDENTIALS_FILE)) {
    return { version: 1, credentials: {} };
  }
  try {
    const data = fs.readFileSync(CREDENTIALS_FILE);
    const json = decrypt(data, getPassphrase());
    return JSON.parse(json);
  } catch (err: any) {
    if (err.message?.includes('Unsupported state') || err.message?.includes('auth tag')) {
      throw new Error('凭证解密失败。如果设置了 RPA_CREDENTIAL_KEY 请确认一致。');
    }
    throw err;
  }
}

function saveStore(store: CredentialStore): void {
  const dir = path.dirname(CREDENTIALS_FILE);
  fs.mkdirSync(dir, { recursive: true });
  const json = JSON.stringify(store, null, 2);
  const encrypted = encrypt(json, getPassphrase());
  fs.writeFileSync(CREDENTIALS_FILE, encrypted, { mode: 0o600 });
}

// ─── Public API ──────────────────────────────────────────────────────────────

/** Save or update credentials for a domain */
export function saveCredential(domain: string, cred: Credential): void {
  const store = loadStore();
  store.credentials[domain] = cred;
  saveStore(store);
}

/** Get credentials for a domain, returns null if not found */
export function getCredential(domain: string): Credential | null {
  const store = loadStore();
  return store.credentials[domain] || null;
}

/** Delete credentials for a domain */
export function deleteCredential(domain: string): boolean {
  const store = loadStore();
  if (domain in store.credentials) {
    delete store.credentials[domain];
    saveStore(store);
    return true;
  }
  return false;
}

/** List all stored domains (no passwords exposed) */
export function listCredentials(): { domain: string; username: string }[] {
  const store = loadStore();
  return Object.entries(store.credentials).map(([domain, cred]) => ({
    domain,
    username: cred.username,
  }));
}

/** Extract credentials from a recording.json and save them */
export function extractAndSaveFromRecording(recordingPath: string): { domain: string; username: string } | null {
  const data = JSON.parse(fs.readFileSync(recordingPath, 'utf8'));
  for (const req of data.requests || []) {
    const url: string = req.url || '';
    const method: string = req.method || '';
    if (method !== 'POST') continue;

    // Detect SSO login APIs
    const body = typeof req.postData === 'string' ? (() => { try { return JSON.parse(req.postData); } catch { return null; } })() : (req.postData || req.body);
    if (!body) continue;

    // Pattern 1: SSO API style { authType, credential: { username, password } }
    if (body.credential?.username && body.credential?.password) {
      const domain = new URL(url).hostname;
      const cred: Credential = {
        username: body.credential.username,
        password: body.credential.password,
        authType: body.authType || 'passwordAuth',
        loginApiPath: new URL(url).pathname,
        extraFields: Object.fromEntries(Object.entries(body).filter(([k]) => !['credential', 'authType'].includes(k))),
      };
      saveCredential(domain, cred);
      return { domain, username: cred.username };
    }

    // Pattern 2: Direct { username, password } in body
    if (body.username && body.password && (url.includes('login') || url.includes('auth'))) {
      const domain = new URL(url).hostname;
      const cred: Credential = {
        username: body.username,
        password: body.password,
        loginApiPath: new URL(url).pathname,
      };
      saveCredential(domain, cred);
      return { domain, username: cred.username };
    }
  }
  return null;
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

if (require.main === module) {
  const [cmd, ...args] = process.argv.slice(2);
  switch (cmd) {
    case 'list':
      console.log(JSON.stringify(listCredentials(), null, 2));
      break;
    case 'save': {
      const [domain, username, password] = args;
      if (!domain || !username || !password) { console.error('Usage: credentials.ts save <domain> <username> <password>'); process.exit(1); }
      saveCredential(domain, { username, password });
      console.log(`✅ Saved credentials for ${domain}`);
      break;
    }
    case 'delete': {
      const [domain] = args;
      if (!domain) { console.error('Usage: credentials.ts delete <domain>'); process.exit(1); }
      deleteCredential(domain) ? console.log(`✅ Deleted ${domain}`) : console.log(`⚠️ Not found: ${domain}`);
      break;
    }
    case 'extract': {
      const [recordingPath] = args;
      if (!recordingPath) { console.error('Usage: credentials.ts extract <recording.json>'); process.exit(1); }
      const result = extractAndSaveFromRecording(recordingPath);
      result ? console.log(`✅ Extracted and saved: ${result.domain} (${result.username})`) : console.log('⚠️ No login credentials found in recording');
      break;
    }
    default:
      console.log('Usage: credentials.ts <list|save|delete|extract>');
  }
}
