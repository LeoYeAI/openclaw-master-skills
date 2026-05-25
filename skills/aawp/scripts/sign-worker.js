#!/usr/bin/env node
'use strict';

const net = require('net');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const addon = require(process.env.AAWP_CORE || require('path').join(__dirname, '..', 'core', 'aawp-core.node'));

const C = process.env.AAWP_CONFIG || require('path').join(__dirname, '..', '.agent-config');
const LOCK = '/tmp/.aawp-daemon.lock';

function fail(msg) {
  process.stdout.write(JSON.stringify({ error: String(msg || 'worker failed') }));
  process.exit(1);
}

function readToken() {
  try {
    const persisted = fs.readFileSync('/tmp/.aawp-ai-token', 'utf8').trim();
    if (persisted && persisted.length === 64) return persisted;
  } catch (_) {}
  const envToken = process.env.AAWP_AI_TOKEN || '';
  if (envToken && envToken.length === 64) return envToken;
  return null;
}

function rotateLocalToken(current) {
  const next = crypto.createHmac('sha256', Buffer.from(current, 'hex')).update('rotate').digest('hex');
  try { fs.writeFileSync('/tmp/.aawp-ai-token', next, { mode: 0o600 }); } catch (_) {}
  return next;
}

function socketQuery(sock, obj, aiToken) {
  return new Promise((resolve, reject) => {
    const ts = Math.floor(Date.now() / 1000);
    const hmac = addon._h0(ts);
    const payload = { ...obj, ts, hmac, ai_token: aiToken };
    const c = net.createConnection(sock, () => c.end(JSON.stringify(payload)));
    let d = '';
    c.on('data', x => d += x);
    c.on('end', () => {
      try { resolve(JSON.parse(d)); } catch (e) { reject(new Error('bad response')); }
    });
    c.on('error', reject);
    setTimeout(() => { c.destroy(); reject(new Error('socket timeout')); }, 30000);
  });
}

(async () => {
  try {
    const arg = process.argv[2];
    if (!arg) fail('missing payload');
    const payload = JSON.parse(arg);

    let lockData;
    try { lockData = JSON.parse(fs.readFileSync(LOCK, 'utf8')); }
    catch (_) { fail('daemon not running'); }
    if (!lockData || !lockData.sock || !fs.existsSync(lockData.sock)) fail('daemon socket missing');

    const aiToken = readToken();
    if (!aiToken) fail('missing AAWP_AI_TOKEN');

    addon._i0(C, process.env.AAWP_SKILL || require('path').resolve(__dirname, '..'));

    // Inject guardian private key as gas_key for sign requests (replaces internal relay key)
    if (payload.cmd === 'sign' && !payload.gas_key) {
      try {
        const gPath = path.join(process.env.AAWP_SKILL || require('path').resolve(__dirname, '..'), 'config/guardian.json');
        const g = JSON.parse(fs.readFileSync(gPath, 'utf8'));
        if (g.privateKey) payload.gas_key = g.privateKey.replace(/^0x/, '');
      } catch (_) {}
    }

    const result = await socketQuery(lockData.sock, payload, aiToken);
    rotateLocalToken(aiToken);
    process.stdout.write(JSON.stringify(result));
    process.exit(0);
  } catch (err) {
    fail(err && err.message ? err.message : String(err));
  }
})();
