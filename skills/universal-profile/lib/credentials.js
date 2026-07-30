/**
 * Universal Profile Credentials Helper
 * Handles credential loading from multiple possible locations
 */

import fs from 'fs';
import { promises as fsp } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Get the user's home directory with fallback for Windows
 * @returns {string}
 */
function getHomeDir() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (!home) {
    throw new Error(
      'Cannot determine home directory. Set the HOME (or USERPROFILE on Windows) environment variable.'
    );
  }
  return home;
}

/**
 * Possible credential locations (in priority order)
 */
function getCredentialPaths() {
  const home = getHomeDir();
  return [
    // 1. Environment variable (highest priority)
    process.env.UP_CREDENTIALS_PATH,

    // 2. OpenClaw standard location
    path.join(home, '.openclaw', 'universal-profile', 'config.json'),

    // 3. Legacy clawdbot location
    path.join(home, '.clawdbot', 'universal-profile', 'config.json'),
  ];
}

function getKeyPaths() {
  const home = getHomeDir();
  return [
    // Environment variable
    process.env.UP_KEY_PATH,

    // OpenClaw standard
    path.join(home, '.openclaw', 'credentials', 'universal-profile-key.json'),

    // Legacy clawdbot
    path.join(home, '.clawdbot', 'credentials', 'universal-profile-key.json'),
  ];
}

/**
 * Warn if credential file has insecure permissions (group/others can read)
 * @param {string} filePath
 */
function warnIfInsecurePermissions(filePath) {
  try {
    const stat = fs.statSync(filePath);
    const mode = stat.mode;
    // Check if group (0o070) or others (0o007) have any permissions
    if (mode & 0o077) {
      console.warn(
        `⚠️  Credential file ${filePath} is readable by group/others (mode ${(mode & 0o777).toString(8)}). ` +
        `Run: chmod 600 ${filePath}`
      );
    }
  } catch {
    // Ignore — file might not exist yet or stat might fail on some platforms
  }
}

/**
 * Find and load credentials
 * @returns {Object} Credentials object with universalProfile and controller
 * @throws {Error} If no credentials found
 */
export function loadCredentials() {
  const credentialPaths = getCredentialPaths();
  const keyPaths = getKeyPaths();

  // Try config.json locations
  for (const credPath of credentialPaths.filter(Boolean)) {
    if (fs.existsSync(credPath)) {
      try {
        warnIfInsecurePermissions(credPath);
        const config = JSON.parse(fs.readFileSync(credPath, 'utf8'));

        // If controller.privateKey is in config, we're done
        if (config.controller?.privateKey) {
          return config;
        }

        // Otherwise, try to load key from separate file
        for (const keyPath of keyPaths.filter(Boolean)) {
          if (fs.existsSync(keyPath)) {
            warnIfInsecurePermissions(keyPath);
            const keyData = JSON.parse(fs.readFileSync(keyPath, 'utf8'));
            return {
              ...config,
              controller: {
                ...config.controller,
                ...keyData.controller,
              }
            };
          }
        }

        // Config found but no key
        throw new Error(`Found config at ${credPath} but no private key found`);
      } catch (error) {
        if (error.code === 'ENOENT') continue;
        throw error;
      }
    }
  }

  // Try key-only files (some setups might only have the key file)
  for (const keyPath of keyPaths.filter(Boolean)) {
    if (fs.existsSync(keyPath)) {
      try {
        warnIfInsecurePermissions(keyPath);
        return JSON.parse(fs.readFileSync(keyPath, 'utf8'));
      } catch (error) {
        if (error.code === 'ENOENT') continue;
        throw error;
      }
    }
  }

  // No credentials found anywhere
  throw new Error(
    'Universal Profile credentials not found!\n\n' +
    'Searched locations:\n' +
    credentialPaths.filter(Boolean).map(p => `  - ${p}`).join('\n') +
    '\n\nTo fix:\n' +
    '  1. Set UP_CREDENTIALS_PATH environment variable, or\n' +
    '  2. Place credentials in ~/.openclaw/universal-profile/config.json, or\n' +
    '  3. Place credentials in ~/.openclaw/credentials/universal-profile-key.json\n\n' +
    'Expected JSON format:\n' +
    '  {\n' +
    '    "universalProfile": { "address": "0x..." },\n' +
    '    "controller": { "address": "0x...", "privateKey": "0x..." }\n' +
    '  }\n\n' +
    'See SKILL.md for setup instructions.'
  );
}

/**
 * Get the canonical credential file path (where new credentials should be saved)
 * @returns {string} Canonical path for credentials
 */
export function getCredentialPath() {
  const home = getHomeDir();
  return path.join(home, '.openclaw', 'credentials', 'universal-profile-key.json');
}

/**
 * Get credential file path (for reference — returns first found path, or null)
 * @returns {string|null} Path to credentials file, or null if not found
 */
export function getCredentialsPath() {
  const credentialPaths = getCredentialPaths();
  const keyPaths = getKeyPaths();

  for (const credPath of credentialPaths.filter(Boolean)) {
    if (fs.existsSync(credPath)) return credPath;
  }
  for (const keyPath of keyPaths.filter(Boolean)) {
    if (fs.existsSync(keyPath)) return keyPath;
  }
  return null;
}

/**
 * Save credentials to the canonical path with secure permissions
 * @param {Object} creds - Credentials object to save
 * @returns {Promise<string>} Path where credentials were saved
 */
export async function saveCredentials(creds) {
  validateCredentials(creds);

  const credPath = getCredentialPath();
  const credDir = path.dirname(credPath);

  // Ensure directory exists
  await fsp.mkdir(credDir, { recursive: true });

  // Write with restrictive permissions (owner read/write only)
  const data = JSON.stringify(creds, null, 2);
  await fsp.writeFile(credPath, data, { mode: 0o600, encoding: 'utf8' });

  return credPath;
}

/**
 * Validate credentials structure
 * @param {Object} creds - Credentials object
 * @throws {Error} If credentials are invalid
 */
export function validateCredentials(creds) {
  if (!creds.universalProfile?.address) {
    throw new Error('Missing universalProfile.address in credentials');
  }
  if (!creds.controller?.address) {
    throw new Error('Missing controller.address in credentials');
  }
  if (!creds.controller?.privateKey) {
    throw new Error('Missing controller.privateKey in credentials');
  }

  // Validate address format
  const addressRegex = /^0x[a-fA-F0-9]{40}$/;
  if (!addressRegex.test(creds.universalProfile.address)) {
    throw new Error('Invalid universalProfile.address format');
  }
  if (!addressRegex.test(creds.controller.address)) {
    throw new Error('Invalid controller.address format');
  }

  // Validate private key format (with or without 0x prefix)
  const keyRegex = /^(0x)?[a-fA-F0-9]{64}$/;
  if (!keyRegex.test(creds.controller.privateKey)) {
    throw new Error('Invalid controller.privateKey format');
  }
}

/**
 * Load and validate credentials (convenience function)
 * @returns {Object} Validated credentials
 */
export function loadAndValidateCredentials() {
  const creds = loadCredentials();
  validateCredentials(creds);
  return creds;
}
