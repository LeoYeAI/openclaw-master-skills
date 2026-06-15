#!/usr/bin/env node
/**
 * gate.mjs — Cross-platform security gate for AgentAudit
 * Works on Windows, macOS, and Linux. No bash/jq required.
 *
 * Usage:
 *   node scripts/gate.mjs <manager> <package>
 *   node scripts/gate.mjs npm express
 *   node scripts/gate.mjs pip requests
 *
 * Exit codes: 0=PASS, 1=BLOCK, 2=WARN, 3=UNKNOWN
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

function gateJson(gate, pkg, score, summary) {
  return JSON.stringify({ gate, package: pkg, score, ...summary });
}

// ── Args ─────────────────────────────────────────────────

const manager = process.argv[2];
const pkg = process.argv[3];

if (!manager || !pkg) {
  console.error('Usage: node scripts/gate.mjs <manager> <package>');
  console.error('       node scripts/gate.mjs npm express');
  process.exit(1);
}

const apiKey = loadApiKey();
const encoded = encodeURIComponent(pkg);

// ── Check API ────────────────────────────────────────────

let checkData;
try {
  const headers = {};
  if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;
  const res = await fetchRetry(`${API_URL}/api/check?package=${encoded}`, { headers });
  checkData = await res.json();
} catch (err) {
  console.error(`Registry unreachable: ${err.message}`);
  console.log(gateJson('WARN', pkg, null, { reason: 'registry_unreachable' }));
  process.exit(2);
}

// Not yet audited
if (!checkData.exists) {
  console.log(gateJson('UNKNOWN', pkg, null, { reason: 'not_audited' }));
  process.exit(3);
}

const score = checkData.trust_score ?? 100;
const total = checkData.total_findings ?? 0;
const auditLevel = checkData.audit_level || 'unknown';
const summary = {
  critical: checkData.critical ?? 0,
  high: checkData.high ?? 0,
  medium: checkData.medium ?? 0,
  low: checkData.low ?? 0,
  total_findings: total,
  audit_level: auditLevel,
};

// ── Decision ─────────────────────────────────────────────

if (score >= 70) {
  console.log(gateJson('PASS', pkg, score, summary));
  process.exit(0);
} else if (score >= 40) {
  console.log(gateJson('WARN', pkg, score, summary));

  // Show top findings on stderr for the agent to read
  if (total > 0) {
    try {
      const headers = {};
      if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;
      const fRes = await fetchRetry(`${API_URL}/api/findings?package=${encoded}`, { headers });
      const fData = await fRes.json();
      const findings = (fData.findings || [])
        .filter(f => f.by_design !== true && f.by_design !== 'true')
        .slice(0, 5);
      console.error(JSON.stringify(findings.map(f => ({
        severity: f.severity,
        title: f.title,
        by_design: f.by_design,
      }))));
    } catch {}
  }
  process.exit(2);
} else {
  console.log(gateJson('BLOCK', pkg, score, summary));

  if (total > 0) {
    try {
      const headers = {};
      if (apiKey) headers['Authorization'] = `Bearer ${apiKey}`;
      const fRes = await fetchRetry(`${API_URL}/api/findings?package=${encoded}`, { headers });
      const fData = await fRes.json();
      const findings = (fData.findings || [])
        .filter(f => f.by_design !== true && f.by_design !== 'true')
        .slice(0, 5);
      console.error(JSON.stringify(findings.map(f => ({
        severity: f.severity,
        title: f.title,
        by_design: f.by_design,
      }))));
    } catch {}
  }
  process.exit(1);
}
