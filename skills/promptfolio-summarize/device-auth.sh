#!/usr/bin/env bash
set -euo pipefail

API_URL="${PROMPTFOLIO_API_URL:-https://promptfolio.club}"
DEVICE_ENDPOINT="${API_URL%/}/api/auth/device"
POLL_ENDPOINT="${API_URL%/}/api/auth/device/poll"
CONFIG_DIR="${HOME}/.promptfolio"
CONFIG_FILE="${CONFIG_DIR}/config.json"
DEFAULT_POLL_INTERVAL=5
POLL_INTERVAL="${PROMPTFOLIO_AUTH_POLL_INTERVAL:-${DEFAULT_POLL_INTERVAL}}"
MAX_ATTEMPTS="${PROMPTFOLIO_AUTH_MAX_POLLS:-120}"

json_get() {
  local key="$1"
  local json="$2"
  printf '%s' "$json" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p"
}

json_get_number() {
  local key="$1"
  local json="$2"
  printf '%s' "$json" | tr -d '\n' | sed -n "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\\([0-9][0-9]*\\).*/\\1/p"
}

json_escape() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

open_url() {
  local url="$1"
  if [ "${PROMPTFOLIO_AUTH_NO_OPEN:-0}" = "1" ]; then
    return 1
  fi

  if command -v open >/dev/null 2>&1; then
    open "$url" >/dev/null 2>&1 && return 0
    open -a "Google Chrome" "$url" >/dev/null 2>&1 && return 0
    open -a "Safari" "$url" >/dev/null 2>&1 && return 0
    open -a "Firefox" "$url" >/dev/null 2>&1 && return 0
  fi
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 && return 0
  fi
  if command -v gio >/dev/null 2>&1; then
    gio open "$url" >/dev/null 2>&1 && return 0
  fi
  if command -v wslview >/dev/null 2>&1; then
    wslview "$url" >/dev/null 2>&1 && return 0
  fi
  if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -Command "Start-Process '$url'" >/dev/null 2>&1 && return 0
  fi
  if command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /C start "" "$url" >/dev/null 2>&1 && return 0
  fi
  return 1
}

echo "Starting promptfolio device authorization..."
create_resp="$(curl -sS -X POST "$DEVICE_ENDPOINT" -H "Content-Type: application/json" -d '{}')" || {
  echo "Failed to request device authorization code."
  echo "Check network / DNS connectivity to ${API_URL} and try again."
  exit 1
}

device_code="$(json_get "deviceCode" "$create_resp")"
user_code="$(json_get "userCode" "$create_resp")"
interval_from_server="$(json_get_number "interval" "$create_resp")"

if [ -n "$interval_from_server" ] && [ "${PROMPTFOLIO_AUTH_POLL_INTERVAL:-}" = "" ]; then
  POLL_INTERVAL="$interval_from_server"
fi

if [ -z "$device_code" ] || [ -z "$user_code" ]; then
  echo "Unexpected response from /api/auth/device:"
  echo "$create_resp"
  exit 1
fi

auth_url="${API_URL%/}/me?device=1&code=${user_code}"
echo "Device code: ${user_code}"
echo "Authorization URL: ${auth_url}"

if open_url "$auth_url"; then
  echo "Opened browser automatically. Continue authorization there."
  echo "If browser did not open, manually visit: ${auth_url}"
else
  echo "Could not auto-open browser in this environment."
  echo "Please open this URL manually: ${auth_url}"
fi

echo "Polling for authorization..."
for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  poll_resp="$(curl -sS -w "\n%{http_code}" -X POST "$POLL_ENDPOINT" -H "Content-Type: application/json" -d "{\"deviceCode\":\"${device_code}\"}")" || {
    echo "Poll request failed; retrying..."
    sleep "$POLL_INTERVAL"
    continue
  }

  body="$(printf '%s' "$poll_resp" | sed '$d')"
  code="$(printf '%s' "$poll_resp" | tail -n1 | tr -d '\r')"
  ts="$(date '+%H:%M:%S')"

  case "$code" in
    200)
      token="$(json_get "token" "$body")"
      user_id="$(json_get "userId" "$body")"
      user_name="$(json_get "userName" "$body")"

      if [ -z "$token" ] || [ -z "$user_id" ]; then
        echo "Authorization succeeded but response payload is incomplete:"
        echo "$body"
        exit 1
      fi

      mkdir -p "$CONFIG_DIR"
      api_url_escaped="$(json_escape "$API_URL")"
      token_escaped="$(json_escape "$token")"
      user_id_escaped="$(json_escape "$user_id")"
      user_name_escaped="$(json_escape "${user_name:-}")"

      cat > "$CONFIG_FILE" <<JSON
{
  "api_url": "${api_url_escaped}",
  "api_token": "${token_escaped}",
  "user_id": "${user_id_escaped}",
  "user_name": "${user_name_escaped}",
  "last_sync": null
}
JSON
      chmod 600 "$CONFIG_FILE" 2>/dev/null || true
      echo "Authorization complete. Saved config to ${CONFIG_FILE}"
      exit 0
      ;;
    202)
      echo "[${ts}] pending (${attempt}/${MAX_ATTEMPTS})"
      if [ $((attempt % 12)) -eq 0 ]; then
        echo "Still pending. Ensure you approved in browser: ${auth_url}"
      fi
      sleep "$POLL_INTERVAL"
      ;;
    410|404)
      echo "Authorization failed (HTTP ${code}):"
      echo "$body"
      exit 2
      ;;
    *)
      echo "[${ts}] unexpected HTTP ${code}"
      [ -n "$body" ] && echo "$body"
      sleep "$POLL_INTERVAL"
      ;;
  esac
done

echo "Timed out waiting for device authorization."
echo "Re-run the command and authorize again: ${auth_url}"
exit 3
