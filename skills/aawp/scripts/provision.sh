#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# AAWP Provision — One-click initialization / reset
# ═══════════════════════════════════════════════════════════════════
#
# Usage:
#   bash scripts/provision.sh          # first-time init
#   bash scripts/provision.sh --reset  # wipe + re-init (DESTROYS existing wallet!)
#
# What it does:
#   1. Kills any running daemon
#   2. Cleans stale lock files (including chattr +i protected ones)
#   3. Creates .agent-config directory
#   4. Calls _p0() to generate seed.enc + shard_B + shard_C
#   5. Injects shard_B into .ocx_entropy ELF section of aawp-core.node
#   6. Updates binary hash file
#   7. Fixes known config issues (EIP-55 checksums)
#   8. Starts daemon and verifies health
#
# Requirements:
#   - objcopy (binutils)
#   - node >= 18
#   - aawp-core.node must have .ocx_entropy section
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG="$ROOT/.agent-config"
CORE="$ROOT/core/aawp-core.node"
HASH="$CORE.hash"
SHARD_C="/var/lib/aawp/.cache/fonts.idx"
LOCK="/tmp/.aawp-daemon.lock"
SHARD_TMP="/tmp/.aawp-shard-b-$$"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { printf "${CYAN}[AAWP]${NC} %s\n" "$*"; }
ok()    { printf "${GREEN}[AAWP] ✅ %s${NC}\n" "$*"; }
warn()  { printf "${YELLOW}[AAWP] ⚠️  %s${NC}\n" "$*"; }
die()   { printf "${RED}[AAWP] ❌ %s${NC}\n" "$*" >&2; exit 1; }

# ── Preflight ──────────────────────────────────────────────────────
command -v objcopy >/dev/null 2>&1 || die "objcopy not found (install binutils)"
command -v node    >/dev/null 2>&1 || die "node not found"
[ -f "$CORE" ] || die "Core binary not found: $CORE"
objdump -h "$CORE" 2>/dev/null | grep -q '\.ocx_entropy' \
  || die "Binary missing .ocx_entropy section — wrong build?"

cd "$ROOT"

# ── Parse args ─────────────────────────────────────────────────────
RESET=false
RESET_GUARDIAN=false
for arg in "$@"; do
  case "$arg" in
    --reset) RESET=true ;;
    --reset-guardian) RESET_GUARDIAN=true ;;
    -h|--help)
      echo "Usage: bash scripts/provision.sh [--reset] [--reset-guardian]"
      echo "  --reset            Wipe existing wallet and re-provision (DESTRUCTIVE)"
      echo "  --reset-guardian   Also regenerate the guardian keypair (requires --reset)"
      exit 0
      ;;
    *) die "Unknown arg: $arg" ;;
  esac
done

# ── Check if already provisioned ──────────────────────────────────
if [ -f "$CFG/seed.enc" ] && [ "$RESET" = false ]; then
  warn "Already provisioned ($CFG/seed.enc exists)"
  warn "Use --reset to wipe and re-provision (DESTROYS existing wallet!)"
  info "If daemon won't start, try: bash scripts/restart-daemon.sh"
  exit 0
fi

if [ "$RESET" = true ] && [ -f "$CFG/seed.enc" ]; then
  warn "⚠️  RESET MODE — this will DESTROY the current wallet signer key!"
  printf "    Type 'yes' to confirm: "
  read -r confirm
  if [ "$confirm" != "yes" ]; then
    die "Aborted."
  fi
fi

# ── Step 1: Kill existing daemon ──────────────────────────────────
info "Stopping existing daemon..."
pgrep -f 'node.*start-daemon\.js' 2>/dev/null | while read pid; do
  kill "$pid" 2>/dev/null || true
done || true
sleep 1

# ── Step 2: Clean ALL stale lock/state files ──────────────────────
info "Cleaning stale lock files..."
# The token consumption lock is a chattr +i file in /tmp/.d*
for f in /tmp/.d*; do
  if [ -f "$f" ]; then
    chattr -i "$f" 2>/dev/null || true
    rm -f "$f" 2>/dev/null || true
  fi
done
rm -f "$LOCK" /tmp/.aawp-ai-token

if [ "$RESET" = true ]; then
  info "Wiping old provision data..."
  rm -rf "$CFG"
  rm -f "$SHARD_C"
  rm -f "$ROOT/seed.enc"  # cleanup misplaced seed.enc in skill root
  rm -f /tmp/aawp.log /tmp/aawp-start.out /tmp/aawp-ensure.out  # clear old logs
  # guardian.json is preserved across resets (same guardian reused by default)
  if [ "$RESET_GUARDIAN" = true ]; then
    info "Also resetting guardian keypair..."
    rm -f "$ROOT/config/guardian.json"
  fi
fi

# ── Step 3: Create config directory ───────────────────────────────
mkdir -p "$CFG"
ok "Config directory ready: $CFG"

# ── Step 4: Provision (generate seed + shards) ────────────────────
info "Provisioning signer key..."
node -e "
  const addon = require('$ROOT/core/aawp-core.node');
  const fs = require('fs');
  const shardB = addon._p0('$CFG');
  fs.writeFileSync('$SHARD_TMP', shardB);
  if (!fs.existsSync('$CFG/seed.enc')) {
    console.error('ERROR: seed.enc not created');
    process.exit(1);
  }
  console.log('shard_B: ' + Buffer.from(shardB).toString('hex'));
" || die "Provision (_p0) failed"

[ -f "$SHARD_TMP" ] || die "shard_B file not written"
SHARD_SIZE=$(stat -c%s "$SHARD_TMP" 2>/dev/null || stat -f%z "$SHARD_TMP")
[ "$SHARD_SIZE" -ge 16 ] || die "shard_B too small ($SHARD_SIZE bytes)"

ok "Seed + shards generated"

# ── Step 5: Inject shard_B into binary ────────────────────────────
info "Injecting shard_B into binary..."
objcopy --update-section ".ocx_entropy=$SHARD_TMP" "$CORE" \
  || die "objcopy injection failed"
ok "shard_B injected into .ocx_entropy section"

# Verify injection
INJECTED=$(objcopy --dump-section .ocx_entropy=/dev/stdout "$CORE" 2>/dev/null | od -A n -t x1 | tr -d ' \n')
EXPECTED=$(od -A n -t x1 "$SHARD_TMP" | tr -d ' \n')
if [ "$INJECTED" != "$EXPECTED" ]; then
  die "shard_B injection verification failed!"
fi
ok "shard_B verified in binary"

# Clean up shard_B temp file
rm -f "$SHARD_TMP"

# ── Step 6: Update binary hash ────────────────────────────────────
info "Updating binary hash..."
sha256sum "$CORE" | awk '{print $1}' > "$HASH"
ok "Hash updated: $(cat "$HASH")"

# ── Step 7: Fix known config issues ──────────────────────────────
info "Checking chain config..."
CHAINS="$ROOT/config/chains.json"
if [ -f "$CHAINS" ]; then
  # Fix EIP-55 checksums using node
  node -e "
    const fs = require('fs');
    const { getAddress } = require('ethers');
    const path = '$CHAINS';
    let raw = fs.readFileSync(path, 'utf8');
    let changed = false;
    // Find all 0x addresses and fix checksums
    const fixed = raw.replace(/\"(0x[0-9a-fA-F]{40})\"/g, (match, addr) => {
      try {
        const cs = getAddress(addr.toLowerCase());
        if (cs !== addr) { changed = true; return '\"' + cs + '\"'; }
      } catch (_) {}
      return match;
    });
    if (changed) {
      fs.writeFileSync(path, fixed);
      console.log('Fixed address checksums in chains.json');
    } else {
      console.log('chains.json checksums OK');
    }
  " 2>/dev/null || warn "Could not validate chain config checksums (ethers not found?)"
fi

# ── Step 8: Start daemon ──────────────────────────────────────────
info "Starting daemon..."

# Clean locks again (provision may have created a new one)
for f in /tmp/.d*; do
  if [ -f "$f" ]; then
    chattr -i "$f" 2>/dev/null || true
    rm -f "$f" 2>/dev/null || true
  fi
done
rm -f "$LOCK" /tmp/.aawp-ai-token

OUT="/tmp/aawp-start.out"
nohup node scripts/start-daemon.js > "$OUT" 2>&1 &
DAEMON_PID=$!

for i in $(seq 1 20); do
  if grep -q '\[AAWP\] healthy address=' "$OUT" 2>/dev/null; then
    ADDR=$(grep -o 'healthy address=0x[0-9a-f]*' "$OUT" | head -1 | cut -d= -f2)
    ok "Daemon healthy!"
    echo ""
    printf "${GREEN}══════════════════════════════════════════════${NC}\n"
    printf "${GREEN}  AAWP Provision Complete${NC}\n"
    printf "${GREEN}══════════════════════════════════════════════${NC}\n"
    printf "  Signer:  ${CYAN}${ADDR}${NC}\n"
    printf "  Config:  $CFG\n"
    printf "  Binary:  $CORE\n"
    printf "  Hash:    $(cat "$HASH")\n"
    printf "${GREEN}══════════════════════════════════════════════${NC}\n"
    echo ""
    info "Next: fund guardian, then run:"
    info "  node scripts/wallet-manager.js --chain base create"
    exit 0
  fi
  if ! kill -0 "$DAEMON_PID" 2>/dev/null; then
    echo ""
    cat "$OUT" 2>/dev/null || true
    die "Daemon exited during startup — check /tmp/aawp-start.out"
  fi
  sleep 1
done

cat "$OUT" 2>/dev/null || true
die "Daemon healthcheck timeout"
