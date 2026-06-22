#!/usr/bin/env node
/**
 * NervePay Quick Track Helper
 *
 * Simplified wrapper for tracking external API calls.
 * Use this immediately after EVERY external API call.
 *
 * USAGE:
 *   # Minimal (required fields only)
 *   node nervepay-track.mjs openai /v1/chat/completions success
 *   node nervepay-track.mjs stripe /v1/charges failure
 *
 *   # With response time
 *   node nervepay-track.mjs openai /v1/chat/completions success 1250
 *
 *   # With cost
 *   node nervepay-track.mjs openai /v1/chat/completions success 1250 0.05
 *
 *   # Full details
 *   node nervepay-track.mjs openai /v1/chat/completions success 1250 0.05 POST USD
 */

import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { spawn } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Parse arguments
const [serviceName, endpoint, successStr, responseTimeStr, amountStr, method, currency] = process.argv.slice(2);

if (!serviceName || !endpoint || !successStr) {
  console.error('Usage: nervepay-track.mjs SERVICE ENDPOINT success|failure [RESPONSE_TIME_MS] [AMOUNT] [METHOD] [CURRENCY]');
  console.error('');
  console.error('Examples:');
  console.error('  nervepay-track.mjs openai /v1/chat/completions success');
  console.error('  nervepay-track.mjs openai /v1/chat/completions success 1250');
  console.error('  nervepay-track.mjs openai /v1/chat/completions success 1250 0.05');
  console.error('  nervepay-track.mjs stripe /v1/charges failure 850 10.00 POST USD');
  process.exit(1);
}

const success = successStr.toLowerCase() === 'success';

// Build tracking payload
const payload = {
  service_name: serviceName,
  endpoint: endpoint,
  success: success,
};

if (method) payload.method = method;
if (responseTimeStr) payload.response_time_ms = parseInt(responseTimeStr, 10);
if (amountStr) payload.amount = amountStr;
if (currency) payload.currency = currency;

// Call the main nervepay-request.mjs script
const requestScript = join(__dirname, 'nervepay-request.mjs');
const body = JSON.stringify(payload);

const child = spawn('node', [requestScript, 'POST', '/v1/agent-identity/track-service', body], {
  stdio: 'inherit',
  env: process.env
});

child.on('exit', (code) => {
  process.exit(code || 0);
});
