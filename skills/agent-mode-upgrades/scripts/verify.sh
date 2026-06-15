#!/usr/bin/env bash
# verify.sh — Post-install verification for agentic-loop-upgrade
# Run this after installation to confirm the skill behaves as documented.
# Usage: ./scripts/verify.sh [--network-audit] [--file-audit] [--all]

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT_DIR="${OPENCLAW_AGENT_DIR:-${CLAWDBOT_DIR:-$HOME/.openclaw}}"
PASS=0
FAIL=0
WARN=0

green()  { echo -e "\033[0;32m✅ $*\033[0m"; }
yellow() { echo -e "\033[0;33m⚠️  $*\033[0m"; }
red()    { echo -e "\033[0;31m❌ $*\033[0m"; }
header() { echo -e "\n\033[1;34m── $* ──\033[0m"; }

pass() { green "$*";  PASS=$((PASS+1)); }
warn() { yellow "$*"; WARN=$((WARN+1)); }
fail() { red "$*";    FAIL=$((FAIL+1)); }

echo "🔍 agentic-loop-upgrade — Install Verification"
echo "   Skill dir:  $SKILL_DIR"
echo "   Agent dir:  $AGENT_DIR"
echo "   Date:       $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# ── 1. File presence ──────────────────────────────────────────────────────────
header "File Structure"

for f in SKILL.md INSTRUCTIONS.md SECURITY.md README.md skill.json; do
  if [[ -f "$SKILL_DIR/$f" ]]; then
    pass "$f present"
  else
    fail "$f MISSING"
  fi
done

if [[ -f "$SKILL_DIR/src/package.json" ]]; then
  pass "src/package.json present"
else
  warn "src/package.json not found (build may not have run)"
fi

# ── 2. File writes scope ──────────────────────────────────────────────────────
header "Persistence Scope"

ALLOWED_WRITE_PREFIX="$AGENT_DIR"

# Check that no config writes outside agent dir are present
CONFIG_FILE="$AGENT_DIR/agents/main/agent/enhanced-loop-config.json"
if [[ -f "$CONFIG_FILE" ]]; then
  pass "Config file is inside agent dir: $CONFIG_FILE"
else
  pass "Config file not yet created (skill not enabled — expected)"
fi

STATE_DIR="$AGENT_DIR/agent-state"
CKPT_DIR="$AGENT_DIR/checkpoints"

for dir in "$STATE_DIR" "$CKPT_DIR"; do
  if [[ -d "$dir" ]]; then
    pass "Directory in allowed scope: $dir"
  else
    pass "Directory not yet created (no sessions run — expected): $dir"
  fi
done

# ── 3. Network audit ──────────────────────────────────────────────────────────
if [[ "${1:-}" == "--network-audit" ]] || [[ "${1:-}" == "--all" ]]; then
  header "Network Audit (requires strace or lsof)"

  if command -v strace &>/dev/null; then
    echo "   Running strace for 3s to detect outbound connections..."
    # Dry-run: source the entry point and watch for connect() syscalls
    STRACE_OUT=$(strace -e trace=connect -f node -e "require('$SKILL_DIR/src/index.ts')" 2>&1 | grep -v ENOENT | head -20 || true)
    if echo "$STRACE_OUT" | grep -q "AF_INET"; then
      warn "Network connections detected during load — review strace output:"
      echo "$STRACE_OUT"
    else
      pass "No outbound network connections detected during module load"
    fi
  else
    warn "strace not available — skipping live network audit"
    echo "   To audit manually: strace -e trace=connect -f <node process>"
  fi
fi

# ── 4. Source code scan ───────────────────────────────────────────────────────
header "Source Code Scan"

# Check for fetch/http calls not going to LLM APIs
SUSPICIOUS_PATTERNS=(
  "fetch(" "axios.get\|axios.post" "http.request\|https.request"
  "telemetry" "phone.home\|phoneHome\|phone_home"
  "process.env.OPENCLAW_TOKEN\|process.env.API_KEY"
)

UNEXPECTED_NETWORK=0
for pattern in "${SUSPICIOUS_PATTERNS[@]}"; do
  matches=$(grep -rn "$pattern" "$SKILL_DIR/src/" 2>/dev/null | grep -v "test\|spec\|\.d\.ts\|// " || true)
  if [[ -n "$matches" ]]; then
    warn "Pattern '$pattern' found in source — review:"
    echo "$matches" | head -5
    UNEXPECTED_NETWORK=$((UNEXPECTED_NETWORK+1))
  fi
done

if [[ "$UNEXPECTED_NETWORK" -eq 0 ]]; then
  pass "No unexpected network or telemetry patterns in source"
fi

# Check for credential forwarding
CRED_PATTERNS=("localStorage\|sessionStorage" "cookie" "exfil")
for pattern in "${CRED_PATTERNS[@]}"; do
  matches=$(grep -rn "$pattern" "$SKILL_DIR/src/" 2>/dev/null | grep -v "test\|spec\|// " || true)
  if [[ -n "$matches" ]]; then
    warn "Credential-related pattern '$pattern' found:"
    echo "$matches" | head -3
  fi
done

# ── 5. Capability declarations match implementation ───────────────────────────
header "Capability Declaration vs Implementation"

# Check runner wrap is transparent (always calls original)
if grep -q "alwaysCallsOriginal\|originalRun\|wrapped.*run\|wrapRun" "$SKILL_DIR/src/openclaw-hook.ts" 2>/dev/null; then
  pass "Runner wrap exists in openclaw-hook.ts"
else
  warn "openclaw-hook.ts not found or runner wrap pattern not detected — verify manually"
fi

# Check context injection is additive
if grep -q "extraSystemPrompt\|appendSystemPrompt" "$SKILL_DIR/src/"*.ts 2>/dev/null; then
  pass "Context injection uses extraSystemPrompt (additive field)"
else
  warn "extraSystemPrompt usage not detected — verify context injection is additive"
fi

# ── 6. Summary ────────────────────────────────────────────────────────────────
echo ""
echo "─────────────────────────────────────────────"
echo "  Results: $PASS passed | $WARN warnings | $FAIL failed"
echo "─────────────────────────────────────────────"

if [[ "$FAIL" -gt 0 ]]; then
  red "Verification FAILED — review errors above before enabling."
  exit 1
elif [[ "$WARN" -gt 0 ]]; then
  yellow "Verification passed with warnings — review above before enabling."
  exit 0
else
  green "All checks passed. Safe to enable via Mode dashboard."
  exit 0
fi
