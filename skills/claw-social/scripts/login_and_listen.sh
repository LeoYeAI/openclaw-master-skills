#!/bin/bash
# A wrapper script to handle paip.ai login and start the websocket listener.

set -e

# --- Configuration ---
BASE_URL="https://gateway.paipai.life/api/v1"
WORKSPACE_DIR="$HOME/.openclaw/workspace"
TOKEN_FILE="$WORKSPACE_DIR/.session_token"
USER_ID_FILE="$WORKSPACE_DIR/.paipai_user_id"
DEVICE_ID_FILE="$WORKSPACE_DIR/.session_device_id"
LISTENER_SCRIPT_PATH="$(dirname "$0")/start_websocket_listener.sh"

# --- Functions ---
log() {
  echo "[login_and_listen] $1"
}

generate_device_id() {
  if [ ! -f "$DEVICE_ID_FILE" ]; then
    log "Generating new device ID..."
    DEVICE_ID="openclaw-$(LC_ALL=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 8)"
    echo "$DEVICE_ID" > "$DEVICE_ID_FILE"
    log "Device ID saved to $DEVICE_ID_FILE"
  else
    DEVICE_ID=$(cat "$DEVICE_ID_FILE")
    log "Using existing device ID from $DEVICE_ID_FILE"
  fi
}

# --- Main Logic ---
if [ "$#" -ne 2 ]; then
  log "Usage: $0 <email> <password>"
  exit 1
fi

EMAIL="$1"
PASSWORD="$2"

generate_device_id

log "Attempting to log in as $EMAIL..."

# Perform login
LOGIN_RESPONSE=$(curl --max-time 300 -s -X POST "$BASE_URL/user/login" \
  -H "Content-Type: application/json" \
  -H "X-DEVICE-ID: $DEVICE_ID" \
  -H "X-Response-Language: en-us" \
  -d "{\"loginType\": 1, \"username\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

# Check for login failure
if ! echo "$LOGIN_RESPONSE" | grep -q '"code":0'; then
  log "Login failed!"
  ERROR_MESSAGE=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"message":"\([^"]*\)".*/\1/p')
  log "Error: $ERROR_MESSAGE"
  exit 1
fi

log "Login successful."

# Extract token
TOKEN=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')

if [ -z "$TOKEN" ]; then
  log "Could not extract token from login response."
  log "Response: $LOGIN_RESPONSE"
  exit 1
fi

# Save the new token to be used immediately
echo "$TOKEN" > "$TOKEN_FILE"
log "Token saved to $TOKEN_FILE"

log "Fetching current user info to get User ID..."

# Get user info using the new token
USER_INFO_RESPONSE=$(curl --max-time 300 -s -X GET "$BASE_URL/user/current/user" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-DEVICE-ID: $DEVICE_ID" \
  -H "X-Response-Language: en-us")

# Check for failure
if ! echo "$USER_INFO_RESPONSE" | grep -q '"code":0'; then
  log "Failed to fetch user info!"
  ERROR_MESSAGE=$(echo "$USER_INFO_RESPONSE" | sed -n 's/.*"message":"\([^"]*\)".*/\1/p')
  log "Error: $ERROR_MESSAGE"
  exit 1
fi

# Extract user ID
USER_ID=$(echo "$USER_INFO_RESPONSE" | sed -n 's/.*"id":\([0-9]*\).*/\1/p')

if [ -z "$USER_ID" ]; then
  log "Could not extract user ID from user info response."
  log "Response: $USER_INFO_RESPONSE"
  exit 1
fi

# Save user ID
echo "$USER_ID" > "$USER_ID_FILE"
log "User ID ($USER_ID) saved to $USER_ID_FILE"

# Start the websocket listener
log "Starting the WebSocket listener in the background..."
export PAIPAI_TOKEN="$TOKEN"
export PAIPAI_USER_ID="$USER_ID"

if [ ! -x "$LISTENER_SCRIPT_PATH" ]; then
    log "Listener script not executable. Attempting to chmod..."
    chmod +x "$LISTENER_SCRIPT_PATH"
fi

bash "$LISTENER_SCRIPT_PATH"

log "Listener script initiated. Check /tmp/websocket_listener.log for status."
log "Process finished."
