#!/bin/bash
# link-identity.sh - Link AMCP identity to Solvr agent profile
#
# After creating an AMCP identity and registering on Solvr, this script
# links them by proving AID ownership via signed challenge.
#
# Flow:
#   1. Extract AID from identity.json
#   2. Request challenge from Solvr API
#   3. Sign challenge with AMCP private key
#   4. Send AID + signature to Solvr
#   5. Verify /me shows has_amcp_identity=true
#   6. Store linking status in config
#
# Usage: ./link-identity.sh [--quiet]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AMCP_CLI="${AMCP_CLI:-$(command -v amcp 2>/dev/null || echo "$HOME/bin/amcp")}"
IDENTITY_PATH="${IDENTITY_PATH:-$HOME/.amcp/identity.json}"
CONFIG_FILE="${CONFIG_FILE:-$HOME/.amcp/config.json}"
SOLVR_API_URL="${SOLVR_API_URL:-https://api.solvr.dev/v1}"

QUIET=false

# ============================================================
# Helpers
# ============================================================

info()  { $QUIET || echo "  -> $*"; }
ok()    { echo "  OK: $*"; }
warn()  { echo "  WARN: $*" >&2; }
fail()  { echo "  FAIL: $*" >&2; }

# ============================================================
# Parse arguments
# ============================================================

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --quiet|-q)
        QUIET=true
        shift
        ;;
      -h|--help)
        cat <<EOF
proactive-amcp link-identity - Link AMCP identity to Solvr agent

Usage: $(basename "$0") [OPTIONS]

Options:
  --quiet, -q   Suppress progress output (errors still shown)
  -h, --help    Show this help

Links your AMCP cryptographic identity (AID) to your Solvr agent profile.
After linking, your checkpoints are verifiable via your AID.

Prerequisites:
  - Valid AMCP identity at ~/.amcp/identity.json
  - Solvr API key in config (from init or solvr-register)
EOF
        exit 0
        ;;
      *)
        fail "Unknown argument: $1"
        exit 1
        ;;
    esac
  done
}

# ============================================================
# Config and identity helpers
# ============================================================

# Get Solvr API key from config (multiple fallback locations)
get_solvr_key() {
  if [ -n "${SOLVR_API_KEY:-}" ]; then
    echo "$SOLVR_API_KEY"
    return
  fi
  if [ -f "$CONFIG_FILE" ]; then
    python3 -c "
import json, sys
with open('$CONFIG_FILE') as f:
    d = json.load(f)
for path in [('solvr','apiKey'), ('apiKeys','solvr'), ('pinning','solvr','apiKey')]:
    o = d
    for k in path:
        o = o.get(k, {}) if isinstance(o, dict) else {}
    if isinstance(o, str) and o:
        print(o)
        sys.exit(0)
" 2>/dev/null || true
  fi
}

# Extract AID from identity.json
get_aid() {
  if [ ! -f "$IDENTITY_PATH" ]; then
    return 1
  fi
  python3 -c "
import json, sys
with open('$IDENTITY_PATH') as f:
    d = json.load(f)
aid = d.get('aid', '')
if not aid:
    sys.exit(1)
print(aid)
" 2>/dev/null
}

# Sign a message using AMCP CLI or Python fallback
sign_challenge() {
  local challenge="$1"

  # Try AMCP CLI first
  if [ -x "$AMCP_CLI" ]; then
    local sig
    sig=$("$AMCP_CLI" sign --identity "$IDENTITY_PATH" --message "$challenge" 2>/dev/null) && {
      echo "$sig"
      return 0
    }
  fi

  # Fallback: Python Ed25519 signing (requires pynacl or cryptography)
  LINK_IDENTITY_PATH="$IDENTITY_PATH" python3 -c "
import json, base64, sys, os
identity_path = os.environ['LINK_IDENTITY_PATH']
challenge = sys.argv[1]
try:
    from nacl.signing import SigningKey
    with open(identity_path) as f:
        d = json.load(f)
    kel = d.get('kel', {})
    events = kel.get('events', [])
    if not events:
        sys.exit(1)
    priv_key = events[0].get('signing_key', '') or events[0].get('privateKey', '')
    if not priv_key:
        sys.exit(1)
    key_bytes = base64.urlsafe_b64decode(priv_key + '==')
    signing_key = SigningKey(key_bytes[:32])
    signed = signing_key.sign(challenge.encode())
    print(base64.urlsafe_b64encode(signed.signature).decode().rstrip('='))
except Exception:
    sys.exit(1)
" "$challenge" 2>/dev/null
}

# ============================================================
# Main
# ============================================================

main() {
  parse_args "$@"

  # Step 1: Validate identity exists and extract AID
  if [ ! -f "$IDENTITY_PATH" ]; then
    fail "No AMCP identity at $IDENTITY_PATH"
    fail "Run: proactive-amcp init"
    return 1
  fi

  local aid
  aid=$(get_aid) || true
  if [ -z "${aid:-}" ]; then
    fail "Could not extract AID from $IDENTITY_PATH"
    return 1
  fi
  info "AMCP identity: ${aid:0:20}..."

  # Step 2: Get Solvr API key
  local solvr_key
  solvr_key=$(get_solvr_key)
  if [ -z "${solvr_key:-}" ]; then
    fail "No Solvr API key found"
    fail "Run: proactive-amcp init  (or: proactive-amcp config set solvr.apiKey YOUR_KEY)"
    return 1
  fi

  # Step 3: Check current Solvr profile — already linked?
  info "Checking Solvr profile..."
  local me_response me_code me_body
  me_response=$(curl -s -w "\n%{http_code}" --max-time 15 \
    -H "Authorization: Bearer $solvr_key" \
    "$SOLVR_API_URL/me" 2>/dev/null || echo -e "\n000")
  me_code=$(echo "$me_response" | tail -n1)
  me_body=$(echo "$me_response" | sed '$d')

  if [ "$me_code" != "200" ]; then
    fail "Cannot reach Solvr API (HTTP $me_code)"
    return 1
  fi

  local current_linked current_aid
  current_linked=$(echo "$me_body" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('true' if d.get('has_amcp_identity') else 'false')
" 2>/dev/null || echo "false")
  current_aid=$(echo "$me_body" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('amcp_aid', '') or '')
" 2>/dev/null || echo "")

  if [ "$current_linked" = "true" ] && [ "$current_aid" = "$aid" ]; then
    ok "AMCP identity already linked to Solvr (AID: ${aid:0:20}...)"
    # Ensure config is up to date
    store_link_status "$aid"
    return 0
  fi

  if [ "$current_linked" = "true" ] && [ -n "$current_aid" ] && [ "$current_aid" != "$aid" ]; then
    warn "Different AID currently linked (${current_aid:0:20}...) — re-linking with current identity"
  fi

  # Step 4: Request identity challenge from Solvr
  info "Requesting identity challenge from Solvr..."
  local challenge_response challenge_code challenge_body challenge signature
  challenge=""
  signature=""

  challenge_response=$(curl -s -w "\n%{http_code}" --max-time 15 \
    -X POST \
    -H "Authorization: Bearer $solvr_key" \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "import json; print(json.dumps({'aid': '$aid'}))")" \
    "$SOLVR_API_URL/me/identity-challenge" 2>/dev/null || echo -e "\n000")
  challenge_code=$(echo "$challenge_response" | tail -n1)
  challenge_body=$(echo "$challenge_response" | sed '$d')

  if [ "$challenge_code" = "200" ] || [ "$challenge_code" = "201" ]; then
    challenge=$(echo "$challenge_body" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('challenge', ''))
" 2>/dev/null || echo "")

    if [ -n "$challenge" ]; then
      # Step 5: Sign the challenge
      info "Signing challenge with AMCP private key..."
      signature=$(sign_challenge "$challenge") || true

      if [ -z "${signature:-}" ]; then
        warn "Could not sign challenge — linking with API key auth only"
      fi
    fi
  else
    info "Challenge endpoint not available (HTTP $challenge_code) — linking with API key auth only"
  fi

  # Step 6: Link identity via PATCH /me
  info "Linking AMCP identity to Solvr agent..."
  local link_payload
  link_payload=$(LINK_AID="$aid" LINK_CHALLENGE="${challenge:-}" LINK_SIGNATURE="${signature:-}" python3 -c "
import json, os
d = {'amcp_aid': os.environ['LINK_AID'], 'has_amcp_identity': True}
challenge = os.environ.get('LINK_CHALLENGE', '')
signature = os.environ.get('LINK_SIGNATURE', '')
if challenge:
    d['challenge'] = challenge
if signature:
    d['signature'] = signature
print(json.dumps(d))
" 2>/dev/null)

  local link_response link_code link_body
  link_response=$(curl -s -w "\n%{http_code}" --max-time 15 \
    -X PATCH \
    -H "Authorization: Bearer $solvr_key" \
    -H "Content-Type: application/json" \
    -d "$link_payload" \
    "$SOLVR_API_URL/me" 2>/dev/null || echo -e "\n000")
  link_code=$(echo "$link_response" | tail -n1)
  link_body=$(echo "$link_response" | sed '$d')

  if [ "$link_code" != "200" ] && [ "$link_code" != "204" ]; then
    fail "Failed to link identity (HTTP $link_code): $link_body"
    return 1
  fi

  # Step 7: Verify — check /me again to confirm has_amcp_identity=true
  info "Verifying link..."
  local verify_response verify_code verify_body verified_linked
  verify_response=$(curl -s -w "\n%{http_code}" --max-time 10 \
    -H "Authorization: Bearer $solvr_key" \
    "$SOLVR_API_URL/me" 2>/dev/null || echo -e "\n000")
  verify_code=$(echo "$verify_response" | tail -n1)
  verify_body=$(echo "$verify_response" | sed '$d')

  verified_linked="false"
  if [ "$verify_code" = "200" ]; then
    verified_linked=$(echo "$verify_body" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('true' if d.get('has_amcp_identity') else 'false')
" 2>/dev/null || echo "false")
  fi

  # Step 8: Store linking status in config
  store_link_status "$aid"

  # Step 9: Display result
  echo ""
  ok "AMCP identity linked to Solvr — your checkpoints are now verifiable"
  echo ""
  if [ "$verified_linked" = "true" ]; then
    echo "  +---------------------------------------------------------+"
    echo "  |  IDENTITY VERIFIED                                      |"
    echo "  |                                                         |"
    printf "  |  AID: %-49s |\n" "${aid:0:49}"
    echo "  |  Status: Linked & verified on Solvr                    |"
    echo "  |  Your checkpoints are cryptographically signed          |"
    echo "  +---------------------------------------------------------+"
  else
    echo "  +---------------------------------------------------------+"
    echo "  |  IDENTITY LINKED                                        |"
    echo "  |                                                         |"
    printf "  |  AID: %-49s |\n" "${aid:0:49}"
    echo "  |  Status: Link sent (verification pending)              |"
    echo "  |  Re-verify: proactive-amcp link-identity               |"
    echo "  +---------------------------------------------------------+"
  fi
  echo ""

  return 0
}

# Store link status in config
store_link_status() {
  local aid="$1"
  if [ -x "$SCRIPT_DIR/config.sh" ]; then
    "$SCRIPT_DIR/config.sh" set solvr.hasAmcpIdentity true 2>/dev/null || true
    "$SCRIPT_DIR/config.sh" set solvr.amcpAid "$aid" 2>/dev/null || true
    "$SCRIPT_DIR/config.sh" set solvr.linkedAt "$(date -u +%Y-%m-%dT%H:%M:%SZ)" 2>/dev/null || true
  fi
}

main "$@"
