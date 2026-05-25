#!/usr/bin/env node
'use strict';
const net = require('net');
const addon = require(process.env.AAWP_CORE || '/root/clawd/skills/aawp/core/aawp-core.node');
const C = process.env.AAWP_CONFIG || '/root/clawd/skills/aawp/.agent-config';

function sendTx(params) {
  return new Promise((resolve, reject) => {
    const sock = addon._x0();
    const ts = Math.floor(Date.now() / 1000);
    const req = Object.assign({}, params, { ts, hmac: addon._h0(ts, C) });
    const client = net.createConnection(sock, () => { client.write(JSON.stringify(req)); client.end(); });
    let data = '';
    client.on('data', c => { data += c; });
    client.on('end', () => {
      try { const r = JSON.parse(data); r.error ? reject(new Error(r.error)) : resolve(r.result); }
      catch(e) { reject(new Error('Bad response')); }
    });
    client.on('error', reject);
  });
}

module.exports = { sendTx };
if (require.main === module) {
  const a = process.argv[2];
  if (!a) { console.error('Usage: client.js <json>'); process.exit(1); }
  sendTx(JSON.parse(a)).then(tx => console.log('TX:', tx)).catch(e => { console.error(e.message); process.exit(1); });
}
