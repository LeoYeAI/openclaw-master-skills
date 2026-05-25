'use strict';
/**
 * start-daemon.js — AAWP persistent daemon launcher
 * Must be called by OpenClaw ONLY. Generates AI gate token, arms daemon,
 * writes socket path to lock file. wallet-manager.js connects to this daemon.
 *
 * Usage: node start-daemon.js
 * Exits 0 on success, prints socket path to stdout.
 */
const crypto = require('crypto');
const fs = require('fs');
const net = require('net');
const addon = require('../core/aawp-core.node');
const C = process.env.AAWP_CONFIG || require('path').join(__dirname, '..', '.agent-config');
const S = process.env.AAWP_SKILL || require('path').resolve(__dirname, '..');
const LOCK = '/tmp/.aawp-daemon.lock';

// Generate random 32-byte AI gate token
const token = crypto.randomBytes(32).toString('hex');
process.env.AAWP_AI_TOKEN = token;

// Clean up stale lock/socket/token files from crashed daemon
try {
  const stale = JSON.parse(fs.readFileSync(LOCK, 'utf8'));
  if (stale.sock) try { fs.unlinkSync(stale.sock); } catch (_) {}
  fs.unlinkSync(LOCK);
} catch (_) {}
try { fs.unlinkSync('/tmp/.aawp-ai-token'); } catch (_) {}

function socketQuery(sock, payload, timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    const ts = Math.floor(Date.now() / 1000);
    const hmac = addon._h0(ts);
    const req = JSON.stringify({ ...payload, ts, hmac });
    const c = net.createConnection(sock, () => c.end(req));
    let data = '';
    const timer = setTimeout(() => {
      c.destroy();
      reject(new Error('healthcheck timeout'));
    }, timeoutMs);
    c.on('data', chunk => { data += chunk; });
    c.on('end', () => {
      clearTimeout(timer);
      try { resolve(JSON.parse(data)); }
      catch (_) { reject(new Error('invalid healthcheck response')); }
    });
    c.on('error', err => {
      clearTimeout(timer);
      reject(err);
    });
  });
}

async function waitForHealthy(sock, timeoutMs = 10000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (fs.existsSync(sock)) {
      try {
        const res = await socketQuery(sock, { cmd: 'address' }, 2000);
        if (res && res.address) return res;
      } catch (_) {}
    }
    await new Promise(r => setTimeout(r, 250));
  }
  throw new Error(`daemon healthcheck failed for socket ${sock}`);
}

async function main() {
  // Start daemon (reads env var, arms gate, clears env var internally)
  addon._l0(C, S, '/tmp/aawp.log');
  const sock = addon._x0();

  let health;
  try {
    health = await waitForHealthy(sock, 12000);
  } catch (err) {
    try { fs.unlinkSync(LOCK); } catch (_) {}
    console.error('[AAWP] startup failed:', err.message || err);
    process.exit(1);
  }

  // Write lock file only after successful healthcheck.
  fs.writeFileSync(LOCK, JSON.stringify({ sock }), { mode: 0o600 });

  console.log(sock);
  console.log('[AAWP] healthy address=' + health.address);

  let _tokenDelivered = false;
  try {
    fs.writeSync(3, 'TOKEN:' + token + '\n');
    _tokenDelivered = true;
  } catch (_) {}
  if (!_tokenDelivered) {
    console.log('TOKEN:' + token);
  }
  try { fs.writeFileSync('/tmp/.aawp-ai-token', token, { mode: 0o600 }); } catch (_) {}

  // Keep the token file synchronized with daemon-side one-time rotation.
  let lastToken = token;
  setInterval(() => {
    try {
      const next = addon._a0();
      if (next && next !== lastToken) {
        fs.writeFileSync('/tmp/.aawp-ai-token', next, { mode: 0o600 });
        lastToken = next;
      }
    } catch (_) {}
  }, 500);

  // Keep process alive — daemon runs in Rust background thread, needs host process.
  setInterval(() => {}, 60000);
}

main().catch(err => {
  console.error('[AAWP] fatal startup error:', err && err.message ? err.message : String(err));
  process.exit(1);
});

process.on('SIGTERM', () => {
  try { fs.unlinkSync(LOCK); } catch (_) {}
  process.exit(0);
});
process.on('SIGINT', () => {
  try { fs.unlinkSync(LOCK); } catch (_) {}
  process.exit(0);
});
