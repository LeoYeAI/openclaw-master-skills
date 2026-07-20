#!/usr/bin/env node

// SECURITY MANIFEST:
// Environment variables accessed: N8N_WEBHOOK_URL, N8N_WEBHOOK_SECRET (only)
// External endpoints called: ${N8N_WEBHOOK_URL}/webhook/openclaw-{{SERVICE}}-{{ACTION}} (only)
// Local files read: none
// Local files written: none

// ============================================================
// OpenClaw n8n Webhook Trigger: {{SERVICE}}-{{ACTION}}
//
// Node.js implementation — zero shell injection surface.
// Uses only Node.js built-in modules (no npm dependencies).
// Requires Node.js 22+ (always available in OpenClaw).
//
// Usage: node trigger.js <action> <payload_json>
// ============================================================

'use strict';

const https = require('https');
const http = require('http');
const { URL } = require('url');

const action = process.argv[2];
const payloadStr = process.argv[3];

if (!action || !payloadStr) {
  process.stderr.write('Usage: trigger.js <action> <payload_json>\n');
  process.exit(1);
}

const webhookUrl = process.env.N8N_WEBHOOK_URL;
const webhookSecret = process.env.N8N_WEBHOOK_SECRET;

if (!webhookUrl) {
  process.stderr.write('Error: N8N_WEBHOOK_URL environment variable not set\n');
  process.exit(1);
}
if (!webhookSecret) {
  process.stderr.write('Error: N8N_WEBHOOK_SECRET environment variable not set\n');
  process.exit(1);
}

let payload;
try {
  payload = JSON.parse(payloadStr);
} catch (e) {
  process.stderr.write(`Error: Invalid JSON payload: ${e.message}\n`);
  process.exit(1);
}

const body = JSON.stringify({
  action: action,
  payload: payload,
  metadata: {
    triggered_by: 'openclaw-agent',
    timestamp: new Date().toISOString()
  }
});

// Safely construct URL — no shell expansion possible in Node.js
const safeAction = encodeURIComponent(action);
const targetUrl = new URL(`/webhook/openclaw-${safeAction}`, webhookUrl);
const protocol = targetUrl.protocol === 'https:' ? https : http;

const options = {
  hostname: targetUrl.hostname,
  port: targetUrl.port || (targetUrl.protocol === 'https:' ? 443 : 80),
  path: targetUrl.pathname,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-webhook-secret': webhookSecret,
    'Content-Length': Buffer.byteLength(body)
  },
  timeout: 30000
};

const req = protocol.request(options, (res) => {
  let responseBody = '';
  res.on('data', (chunk) => { responseBody += chunk; });
  res.on('end', () => {
    const code = res.statusCode;
    if (code >= 200 && code < 300) {
      process.stdout.write(`SUCCESS (HTTP ${code}): ${responseBody}\n`);
      process.exit(0);
    } else if (code === 401) {
      process.stderr.write(`AUTH_ERROR (HTTP 401): Webhook secret mismatch. Verify N8N_WEBHOOK_SECRET.\n`);
      process.exit(1);
    } else if (code === 404) {
      process.stderr.write(`NOT_FOUND (HTTP 404): Workflow inactive or path incorrect.\n`);
      process.exit(1);
    } else if (code === 429) {
      process.stderr.write(`RATE_LIMITED (HTTP 429): Too many requests. Retry after 60 seconds.\n`);
      process.exit(1);
    } else {
      process.stderr.write(`ERROR (HTTP ${code}): ${responseBody}\n`);
      process.exit(1);
    }
  });
});

req.on('timeout', () => {
  process.stderr.write('ERROR: Request timed out after 30 seconds\n');
  req.destroy();
  process.exit(1);
});

req.on('error', (e) => {
  process.stderr.write(`ERROR: ${e.message}\n`);
  process.exit(1);
});

req.write(body);
req.end();
