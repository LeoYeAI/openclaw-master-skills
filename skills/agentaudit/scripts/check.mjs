#!/usr/bin/env node
/**
 * check.mjs — Cross-platform package check for AgentAudit
 * Works on Windows, macOS, and Linux. No bash/jq required.
 *
 * Usage:
 *   node scripts/check.mjs <package-name>
 *   node scripts/check.mjs --hash <sha256|git-sha|purl|swhid>
 *
 * Requires: Node.js 18+ (for built-in fetch)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const API_URL = 'https://www.agentaudit.dev';
const MAX_RETRIES = 3;

// ── Helpers ──────────────────────────────────────────────

function loadApiKey() {
  if (process.env.AGENTAUDIT_API_KEY) return process.env.AGENTAUDIT_API_KEY;

  const skillCred = process.env.AGENTAUDIT_HOME
    ? path.join(process.env.AGENTAUDIT_HOME, 'config', 'credentials.json')
    : path.join(__dirname, '..', 'config', 'credentials.json');

  if (fs.existsSync(skillCred)) {
    try {
      const data = JSON.parse(fs.readFileSync(skillCred, 'utf8'));
      if (data.api_key) return data.api_key;
    } catch {}
  }

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

async function fetchRetry(url, options = {}, retries = MAX_RETRIES) {
  let lastError;
  let delay = 2000;
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url, { ...options, signal: AbortSignal.timeout(10_000) });
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

// ── Args ─────────────────────────────────────────────────

const args = process.argv.slice(2);
if (args.length < 1) {
  console.error('Usage: node scripts/check.mjs <package-name>');
  console.error('       node scripts/check.mjs --hash <hash-value>');
  process.exit(1);
}

const apiKey = loadApiKey();
const headers = {};
if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;

// ── Hash lookup mode ─────────────────────────────────────

if (args[0] === '--hash' || args[0] === '-H') {
  if (args.length < 2) {
    console.error('Usage: node scripts/check.mjs --hash <hash-value>');
    process.exit(1);
  }
  const hash = args[1];
  const encoded = encodeURIComponent(hash);

  console.log(`Looking up hash '${hash}' against ${API_URL}...`);
  console.log('');

  let data;
  try {
    const res = await fetchRetry(`${API_URL}/api/lookup?hash=${encoded}`, { headers });
    data = await res.json();
  } catch {
    console.log('Registry unreachable. Cannot look up hash.');
    process.exit(2);
  }

  const detectedType = data.detected_type || 'unknown';
  const total = data.total_matches || 0;
  const reports = data.reports || [];
  const findings = data.findings || [];

  console.log(`   Type: ${detectedType}`);
  console.log(`   Matches: ${total} (${reports.length} reports, ${findings.length} findings)`);
  console.log('');

  if (reports.length > 0) {
    console.log('   Reports:');
    for (const r of reports) {
      console.log(`   - ${r.skill_slug} — score ${r.risk_score}, matched ${r.matched_field}`);
    }
    console.log('');
  }

  if (findings.length > 0) {
    console.log('   Findings:');
    for (const f of findings) {
      console.log(`   - [${(f.severity || '').toUpperCase()}] ${f.asf_id}: ${f.title} (matched ${f.matched_field})`);
    }
    console.log('');
  }

  if (total === 0) {
    console.log('No audit data matches this hash.');
  }
  process.exit(0);
}

// ── Package name mode ────────────────────────────────────

const pkg = args[0];
const encoded = encodeURIComponent(pkg);

console.log(`Checking '${pkg}' against ${API_URL}...`);
console.log('');

// Fetch trust score from /api/check
let checkData;
try {
  const res = await fetchRetry(`${API_URL}/api/check?package=${encoded}`, { headers });
  checkData = await res.json();
} catch {
  console.log('Registry unreachable. Cannot verify package.');
  console.log('Try again later or run a local LLM audit on the source.');
  process.exit(2);
}

if (!checkData.exists) {
  console.log(`No audit data found for '${pkg}'.`);
  console.log('This package has not been scanned yet.');
  console.log('Consider submitting an audit: node scripts/upload.mjs <report.json>');
  process.exit(0);
}

const score = checkData.trust_score ?? 0;
const crit = checkData.critical ?? 0;
const high = checkData.high ?? 0;
const med = checkData.medium ?? 0;
const low = checkData.low ?? 0;

// Fetch findings for by_design count
let byDesign = 0;
try {
  const fRes = await fetchRetry(`${API_URL}/api/findings?package=${encoded}`, { headers });
  const fData = await fRes.json();
  byDesign = (fData.findings || []).filter(f => f.by_design === true || f.by_design === 'true').length;
} catch {}

// Decision
let icon, verdict;
if (score >= 70) {
  icon = 'PASS'; verdict = 'Safe to install';
} else if (score >= 40) {
  icon = 'CAUTION'; verdict = 'Review findings before installing';
} else {
  icon = 'UNSAFE'; verdict = 'Do not install without careful review';
}

console.log(`${icon} ${pkg} — Score: ${score}/100`);
console.log(`   ${verdict}`);
console.log('');
console.log(`   Findings: ${crit} critical | ${high} high | ${med} medium | ${low} low | ${byDesign} by-design`);
console.log('');

// Show top findings if score is low
if (score < 70) {
  console.log('   Top findings:');
  try {
    const fRes = await fetchRetry(`${API_URL}/api/findings?package=${encoded}`, { headers });
    const fData = await fRes.json();
    const top = (fData.findings || [])
      .filter(f => f.by_design !== true && f.by_design !== 'true')
      .slice(0, 5);
    for (const f of top) {
      console.log(`   - [${(f.severity || '').toUpperCase()}] ${f.title} (${f.file || 'unknown'})`);
    }
  } catch {}
}
