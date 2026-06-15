#!/usr/bin/env node
/**
 * upload.mjs — Cross-platform report upload for AgentAudit
 * Works on Windows, macOS, and Linux. No bash/jq required.
 *
 * Usage:
 *   node scripts/upload.mjs <report.json>
 *   node scripts/upload.mjs -              # read from stdin
 *
 * Requires: Node.js 18+ (for built-in fetch)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REGISTRY_URL = 'https://www.agentaudit.dev';
const MAX_PAYLOAD = 512_000;
const MAX_RETRIES = 3;

// ── Helpers ──────────────────────────────────────────────

function loadApiKey() {
  // 1. Environment variable (highest priority)
  if (process.env.AGENTAUDIT_API_KEY) return process.env.AGENTAUDIT_API_KEY;

  // 2. Skill-local credentials
  const skillCred = process.env.AGENTAUDIT_HOME
    ? path.join(process.env.AGENTAUDIT_HOME, 'config', 'credentials.json')
    : path.join(__dirname, '..', 'config', 'credentials.json');

  if (fs.existsSync(skillCred)) {
    try {
      const data = JSON.parse(fs.readFileSync(skillCred, 'utf8'));
      if (data.api_key) return data.api_key;
    } catch {}
  }

  // 3. User-level config
  const home = process.env.HOME || process.env.USERPROFILE || '';
  const xdg = process.env.XDG_CONFIG_HOME || path.join(home, '.config');
  const userCred = path.join(xdg, 'agentaudit', 'credentials.json');

  if (fs.existsSync(userCred)) {
    try {
      const data = JSON.parse(fs.readFileSync(userCred, 'utf8'));
      if (data.api_key) return data.api_key;
    } catch {}
  }

  return '';
}

async function fetchRetry(url, options, retries = MAX_RETRIES) {
  let lastError;
  let delay = 2000;
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(url, { ...options, signal: AbortSignal.timeout(60_000) });
      return res;
    } catch (err) {
      lastError = err;
      if (i < retries - 1) {
        await new Promise(r => setTimeout(r, delay));
        delay *= 2;
      }
    }
  }
  throw lastError;
}

function die(msg) {
  console.error(msg);
  process.exit(1);
}

// ── Read input ───────────────────────────────────────────

const input = process.argv[2];
if (!input) {
  die('Usage: node scripts/upload.mjs <report.json>\n   or: cat report.json | node scripts/upload.mjs -');
}

let rawJson;
if (input === '-') {
  // Read from stdin
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  rawJson = Buffer.concat(chunks).toString('utf8');
} else {
  if (!fs.existsSync(input)) die(`File not found: ${input}`);
  const stat = fs.statSync(input);
  if (stat.size > MAX_PAYLOAD) die(`Payload too large (${stat.size} bytes, max ${MAX_PAYLOAD}).`);
  rawJson = fs.readFileSync(input, 'utf8');
}

if (rawJson.length > MAX_PAYLOAD) die(`Payload too large (max ${MAX_PAYLOAD} bytes).`);

let report;
try {
  report = JSON.parse(rawJson);
} catch (e) {
  die(`Invalid JSON: ${e.message}`);
}

// ── API key ──────────────────────────────────────────────

const apiKey = loadApiKey();
if (!apiKey) {
  die('No API key found. Set AGENTAUDIT_API_KEY or run: node scripts/register.mjs <agent-name>');
}

// ── Validate required fields ─────────────────────────────

const sourceUrl = report.source_url || '';
if (!sourceUrl) {
  die([
    'VALIDATION ERROR: Missing required field "source_url"',
    '',
    'The report must include a public source URL to the package repository.',
    'Add to your report JSON:',
    '  "source_url": "https://github.com/owner/repo"',
  ].join('\n'));
}
if (!/^https?:\/\//.test(sourceUrl)) {
  die(`VALIDATION ERROR: source_url must be a valid HTTP(S) URL\n   Got: ${sourceUrl}`);
}
console.log(`source_url: ${sourceUrl}`);

const pkgName = report.skill_slug || report.package_name || '';
if (!pkgName) die('VALIDATION ERROR: Missing "skill_slug" or "package_name" field.');
console.log(`package: ${pkgName}`);

if (report.risk_score == null) die('VALIDATION ERROR: Missing "risk_score" field (integer 0-100).');
if (!report.result) die('VALIDATION ERROR: Missing "result" field (safe|caution|unsafe).');

// Auto-fix findings_count
const actualFc = Array.isArray(report.findings) ? report.findings.length : 0;
if (report.findings_count == null) {
  console.log(`Missing "findings_count" — auto-setting to ${actualFc}`);
  report.findings_count = actualFc;
} else if (report.findings_count !== actualFc) {
  console.log(`findings_count (${report.findings_count}) doesn't match findings array (${actualFc}) — correcting`);
  report.findings_count = actualFc;
}

// Ensure skill_slug is set
if (!report.skill_slug) {
  report.skill_slug = pkgName;
}

// Version tracking note
if (report.commit_sha || report.content_hash) {
  console.log('Report contains version info (commit_sha/content_hash) — passing through');
} else {
  console.log('Version info will be computed by backend enrichment');
}

// ── Upload ───────────────────────────────────────────────

console.log(`\nUploading report to ${REGISTRY_URL}/api/reports ...`);

let res;
try {
  res = await fetchRetry(`${REGISTRY_URL}/api/reports`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(report),
  });
} catch (err) {
  if (err.name === 'TimeoutError') {
    console.error('Upload timed out (60s). The server may be processing a large repository.');
    console.error('The report may still have been accepted — check the registry or retry.');
    process.exit(28);
  }
  die(`Upload failed: ${err.message}`);
}

const body = await res.text();
let data;
try { data = JSON.parse(body); } catch { data = null; }

// Handle rate limiting
if (res.status === 429) {
  console.log('Rate limited (429). Waiting 30s and retrying...');
  await new Promise(r => setTimeout(r, 30_000));
  try {
    res = await fetchRetry(`${REGISTRY_URL}/api/reports`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(report),
    });
    const body2 = await res.text();
    try { data = JSON.parse(body2); } catch { data = null; }
  } catch (err) {
    die(`Retry failed: ${err.message}`);
  }
}

if (res.status >= 200 && res.status < 300 && data) {
  const reportId = data.report_id || 'unknown';
  const findingsCreated = Array.isArray(data.findings_created) ? data.findings_created.length : 0;
  const enrichment = data.enrichment_status || 'unknown';
  console.log('Report uploaded successfully!');
  console.log(`Report ID: ${reportId}`);
  console.log(`Findings created: ${findingsCreated}`);
  if (enrichment === 'pending') {
    console.log('Enrichment running in background (PURL, SWHID, version info computed async)');
  }
  console.log(JSON.stringify(data, null, 2));
} else if (res.status === 401) {
  die('Authentication failed (HTTP 401). Your API key may be invalid or expired.\nRe-register: node scripts/register.mjs <agent-name>');
} else {
  die(`Upload failed (HTTP ${res.status}):\n${body}`);
}
