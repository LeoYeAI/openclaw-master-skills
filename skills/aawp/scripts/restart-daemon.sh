#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCK="/tmp/.aawp-daemon.lock"
OUT="/tmp/aawp-start.out"
LOG="/tmp/aawp.log"

cd "$ROOT"

echo "[AAWP] stopping old daemon (if any)..."
pgrep -f 'node scripts/start-daemon\.js' 2>/dev/null | while read pid; do
  # Only kill if it's actually running from the aawp skill dir
  if readlink -f /proc/$pid/cwd 2>/dev/null | grep -q aawp; then
    kill "$pid" 2>/dev/null
  fi
done || true
sleep 1

if [ -f "$LOCK" ]; then
  SOCK=$(python3 - <<'PY'
import json
p='/tmp/.aawp-daemon.lock'
try:
    with open(p) as f:
        print(json.load(f).get('sock',''))
except Exception:
    print('')
PY
)
  [ -n "$SOCK" ] && rm -f "$SOCK" || true
fi

# Remove chattr-locked token consumption file (computed from CREATION_SALT)
for f in /tmp/.d*; do
  if [ -f "$f" ]; then
    chattr -i "$f" 2>/dev/null || true
    rm -f "$f" 2>/dev/null || true
  fi
done
rm -f "$LOCK" /tmp/.aawp-ai-token

echo "[AAWP] starting daemon..."
nohup node scripts/start-daemon.js > "$OUT" 2>&1 &
DAEMON_PID=$!
echo "[AAWP] pid=$DAEMON_PID"

for i in $(seq 1 20); do
  if grep -q '\[AAWP\] healthy address=' "$OUT" 2>/dev/null; then
    echo "[AAWP] daemon healthy"
    cat "$OUT"
    exit 0
  fi
  if ! kill -0 "$DAEMON_PID" 2>/dev/null; then
    echo "[AAWP] daemon exited during startup"
    cat "$OUT" 2>/dev/null || true
    exit 1
  fi
  sleep 1
done

echo "[AAWP] healthcheck timeout"
cat "$OUT" 2>/dev/null || true
exit 1
