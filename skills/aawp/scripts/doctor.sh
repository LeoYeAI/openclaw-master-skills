#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

LOCK="/tmp/.aawp-daemon.lock"
START_OUT="/tmp/aawp-start.out"
ENSURE_OUT="/tmp/aawp-ensure.out"
LOG="/tmp/aawp.log"
CORE="$ROOT/core/aawp-core.node"
CFG="$ROOT/.agent-config"

say() { printf '%s\n' "$*"; }
ok() { say "OK   $*"; }
warn() { say "WARN $*"; }
fail() { say "FAIL $*"; }

[ -f "$CORE" ] && ok "core binary present" || fail "missing core binary: $CORE"
if [ -d "$CFG" ] && [ -f "$CFG/seed.enc" ]; then
  ok "agent config provisioned"
elif [ -d "$CFG" ]; then
  warn "agent config dir exists but seed.enc missing — run: bash scripts/provision.sh"
else
  warn "not provisioned — run: bash scripts/provision.sh"
fi

if [ -f "$LOCK" ]; then
  ok "lock file present"
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
  if [ -n "$SOCK" ] && [ -S "$SOCK" ]; then ok "socket present: $SOCK"; else fail "socket missing/stale: ${SOCK:-<empty>}"; fi
else
  fail "lock file missing"
fi

if "$SCRIPT_DIR/ensure-daemon.sh" >/tmp/aawp-doctor-health.out 2>&1; then
  ADDR=$(tail -n 1 /tmp/aawp-doctor-health.out)
  ok "daemon healthy: $ADDR"
else
  fail "daemon unhealthy"
fi

[ -f "$START_OUT" ] && { say "--- tail $START_OUT ---"; tail -n 10 "$START_OUT"; } || warn "no start log"
[ -f "$ENSURE_OUT" ] && { say "--- tail $ENSURE_OUT ---"; tail -n 10 "$ENSURE_OUT"; } || warn "no ensure log"
[ -f "$LOG" ] && { say "--- tail $LOG ---"; tail -n 20 "$LOG"; } || warn "no signer log"
