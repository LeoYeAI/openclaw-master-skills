#!/usr/bin/env bash
# Refresh and output a Google OAuth access token from ClawEmail credentials.
# Usage: token.sh [credentials-file]
# Caches token for 50 minutes (access tokens last 60 min).
set -euo pipefail

CREDS_FILE="${1:-${CLAWEMAIL_CREDENTIALS:-$HOME/.config/clawemail/credentials.json}}"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/clawemail"
CACHE_FILE="$CACHE_DIR/access_token"

mkdir -p "$CACHE_DIR"

# Return cached token if fresh (< 50 minutes old)
if [[ -f "$CACHE_FILE" ]]; then
    age=$(( $(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null) ))
    if (( age < 3000 )); then
        cat "$CACHE_FILE"
        exit 0
    fi
fi

if [[ ! -f "$CREDS_FILE" ]]; then
    echo "ERROR: Credentials file not found: $CREDS_FILE" >&2
    echo "Save your ClawEmail credentials JSON to ~/.config/clawemail/credentials.json" >&2
    echo "or set CLAWEMAIL_CREDENTIALS=/path/to/credentials.json" >&2
    exit 1
fi

# Extract fields from credentials JSON
CLIENT_ID=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['client_id'])" "$CREDS_FILE")
CLIENT_SECRET=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['client_secret'])" "$CREDS_FILE")
REFRESH_TOKEN=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['refresh_token'])" "$CREDS_FILE")

# Exchange refresh token for access token
RESPONSE=$(curl -s -X POST https://oauth2.googleapis.com/token \
    -d "client_id=$CLIENT_ID" \
    -d "client_secret=$CLIENT_SECRET" \
    -d "refresh_token=$REFRESH_TOKEN" \
    -d "grant_type=refresh_token")

ACCESS_TOKEN=$(echo "$RESPONSE" | python3 -c "import json,sys;print(json.load(sys.stdin)['access_token'])")

if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "None" ]]; then
    echo "ERROR: Failed to refresh access token" >&2
    echo "$RESPONSE" >&2
    exit 1
fi

echo -n "$ACCESS_TOKEN" > "$CACHE_FILE"
echo -n "$ACCESS_TOKEN"
