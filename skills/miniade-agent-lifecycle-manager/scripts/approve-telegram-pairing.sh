#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <agent_id> <pairing_code>"
  exit 1
fi

AGENT_ID="$1"
PAIRING_CODE="$2"

openclaw pairing approve "$PAIRING_CODE" --channel telegram --account "$AGENT_ID"
echo "Approved pairing for agent=$AGENT_ID"
