#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCK="/tmp/.aawp-daemon.lock"

# Bootstrap: download missing binaries if needed
bash "$SCRIPT_DIR/bootstrap.sh"
OUT="/tmp/aawp-ensure.out"

cd "$ROOT"

# Auto-provision on first run
if [ ! -f "$ROOT/.agent-config/seed.enc" ]; then
  echo "[AAWP] Not provisioned — running first-time setup..."
  bash "$ROOT/scripts/provision.sh"
  exit $?
fi

healthcheck() {
  AAWP_SKILL="$ROOT" AAWP_CONFIG="$ROOT/.agent-config" AAWP_CORE="$ROOT/core/aawp-core.node" \
  node - <<'NODE'
const fs = require('fs');
const net = require('net');
const path = require('path');
const S = process.env.AAWP_SKILL;
const C = process.env.AAWP_CONFIG;
const addon = require(process.env.AAWP_CORE);
const lockPath = '/tmp/.aawp-daemon.lock';

function fail(msg) {
  console.error(msg);
  process.exit(1);
}

function query(sock, payload, timeoutMs = 3000) {
  return new Promise((resolve, reject) => {
    const ts = Math.floor(Date.now() / 1000);
    const hmac = addon._h0(ts);
    const req = JSON.stringify({ ...payload, ts, hmac });
    const c = net.createConnection(sock, () => c.end(req));
    let data = '';
    const timer = setTimeout(() => {
      c.destroy();
      reject(new Error('timeout'));
    }, timeoutMs);
    c.on('data', chunk => { data += chunk; });
    c.on('end', () => {
      clearTimeout(timer);
      try { resolve(JSON.parse(data)); }
      catch (_) { reject(new Error('invalid json')); }
    });
    c.on('error', err => {
      clearTimeout(timer);
      reject(err);
    });
  });
}

(async () => {
  let lock;
  try {
    lock = JSON.parse(fs.readFileSync(lockPath, 'utf8'));
  } catch (_) {
    fail('no lock');
  }
  if (!lock.sock || !fs.existsSync(lock.sock)) fail('missing socket');

  addon._i0(C, S);
  const res = await query(lock.sock, { cmd: 'address' });
  if (!res || !res.address) fail('bad healthcheck response');
  console.log(res.address);
})().catch(err => fail(err && err.message ? err.message : String(err)));
NODE
}

if healthcheck > "$OUT" 2>&1; then
  echo "[AAWP] daemon healthy"
  cat "$OUT"
  exit 0
fi

echo "[AAWP] daemon unhealthy — restarting"
"$SCRIPT_DIR/restart-daemon.sh"
