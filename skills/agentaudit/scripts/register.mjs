#!/usr/bin/env node
/**
 * register.mjs — Cross-platform agent registration for AgentAudit
 * Works on Windows, macOS, and Linux. No bash/jq required.
 *
 * Usage:
 *   node scripts/register.mjs <agent-name>
 *
 * Creates credentials at:
 *   - <skill-dir>/config/credentials.json (skill-local)
 *   - ~/.config/agentaudit/credentials.json (user-level backup)
 *
 * Requires: Node.js 18+ (for built-in fetch)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const API_URL = 'https://www.agentaudit.dev';

// ── Helpers ──────────────────────────────────────────────

function writeCredentials(filePath, data) {
  const json = JSON.stringify(data, null, 2);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, json, { mode: 0o600 });
}

async function validateKeyAgainstServer(apiKey) {
  try {
    const res = await fetch(`${API_URL}/api/auth/validate`, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
      signal: AbortSignal.timeout(5_000),
    });
    return res.status === 200;
  } catch {
    return false;
  }
}

// ── Args ─────────────────────────────────────────────────

const agentName = process.argv[2];
if (!agentName) {
  console.error('Usage: node scripts/register.mjs <agent-name>');
  console.error('Example: node scripts/register.mjs my-security-bot');
  process.exit(1);
}

// Validate agent name (parity with register.sh)
if (!/^[a-zA-Z0-9._-]{2,64}$/.test(agentName)) {
  console.error('Invalid agent name. Use only alphanumeric, dashes, underscores, dots (2-64 chars).');
  process.exit(1);
}

// ── Check existing key ───────────────────────────────────

const skillCredDir = path.join(__dirname, '..', 'config');
const skillCredFile = path.join(skillCredDir, 'credentials.json');
const home = process.env.HOME || process.env.USERPROFILE || '';
const xdg = process.env.XDG_CONFIG_HOME || path.join(home, '.config');
const userCredDir = path.join(xdg, 'agentaudit');
const userCredFile = path.join(userCredDir, 'credentials.json');

// Check both credential locations and validate against server
for (const checkFile of [skillCredFile, userCredFile]) {
  if (fs.existsSync(checkFile)) {
    try {
      const existing = JSON.parse(fs.readFileSync(checkFile, 'utf8'));
      if (existing.api_key) {
        const valid = await validateKeyAgainstServer(existing.api_key);
        if (valid) {
          console.log(`Already registered as "${existing.agent_name || 'unknown'}". Key validated against server.`);
          console.log(`  Key found in ${checkFile}`);
          // Ensure both locations have the key
          if (checkFile === userCredFile && !fs.existsSync(skillCredFile)) {
            writeCredentials(skillCredFile, { api_key: existing.api_key, agent_name: existing.agent_name });
            console.log(`  Restored skill-local copy to: ${skillCredFile}`);
          }
          process.exit(0);
        } else {
          console.log(`Cached key in ${checkFile} is stale (server validation failed). Re-registering...`);
          try { fs.unlinkSync(skillCredFile); } catch {}
          try { fs.unlinkSync(userCredFile); } catch {}
          break;
        }
      }
    } catch {}
  }
}

// ── Register ─────────────────────────────────────────────

console.log(`Registering agent "${agentName}" at ${API_URL}...`);

let res;
try {
  res = await fetch(`${API_URL}/api/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ agent_name: agentName }),
    signal: AbortSignal.timeout(15_000),
  });
} catch (err) {
  console.error(`Registration failed: ${err.message}`);
  process.exit(1);
}

if (!res.ok) {
  const text = await res.text();
  console.error(`Registration failed (HTTP ${res.status}): ${text}`);
  process.exit(1);
}

const data = await res.json();
const cred = { api_key: data.api_key, agent_name: data.agent_name };

// Save to skill-local (mode 600 — only owner can read)
writeCredentials(skillCredFile, cred);
console.log(`Saved to: ${skillCredFile}`);

// Save to user-level backup (mode 600)
try {
  writeCredentials(userCredFile, cred);
  console.log(`Backup saved to: ${userCredFile}`);
} catch (err) {
  console.log(`Could not save user-level backup: ${err.message}`);
}

console.log('');
console.log(`Registered as: ${data.agent_name}`);
console.log('You can now use gate.mjs and upload.mjs.');
