#!/usr/bin/env bash
# Generate a one-time pairing code for the Clack iOS app.
# The code expires in 5 minutes.
set -euo pipefail

# Read token and port from systemd service
SERVICE_FILE="/etc/systemd/system/clack.service"
if [[ ! -f "$SERVICE_FILE" ]]; then
  echo "ERROR: Clack service not found. Run setup.sh first."
  exit 1
fi

RELAY_AUTH_TOKEN=$(grep "RELAY_AUTH_TOKEN=" "$SERVICE_FILE" | head -1 | sed 's/.*RELAY_AUTH_TOKEN=//')
PORT=$(grep "VOICE_RELAY_PORT=" "$SERVICE_FILE" | head -1 | sed 's/.*VOICE_RELAY_PORT=//')
PORT="${PORT:-9878}"

if [[ -z "$RELAY_AUTH_TOKEN" ]]; then
  echo "ERROR: Could not read auth token from service file."
  exit 1
fi

# Check service is running
if ! systemctl is-active --quiet clack; then
  echo "ERROR: Clack service is not running. Start it with: sudo systemctl start clack"
  exit 1
fi

# Generate pairing code
RESPONSE=$(curl -s "http://localhost:${PORT}/pair?token=${RELAY_AUTH_TOKEN}")
CODE=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['code'])" 2>/dev/null)

if [[ -z "$CODE" ]]; then
  echo "ERROR: Could not generate pairing code."
  echo "Response: $RESPONSE"
  exit 1
fi

echo ""
echo "  ┌─────────────────────────────────────────┐"
echo "  │                                         │"
echo "  │   Pairing Code:  $CODE                  │"
echo "  │                                         │"
echo "  │   Enter this in the Clack app:          │"
echo "  │   Settings → Server → Pair              │"
echo "  │                                         │"
echo "  │   Expires in 5 minutes.                 │"
echo "  └─────────────────────────────────────────┘"
echo ""
