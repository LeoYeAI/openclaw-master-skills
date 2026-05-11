#!/usr/bin/env bash
# Home Assistant CLI wrapper — Definitive Skill
# Usage: ha.sh <command> [args...]
#
# Based on home-assistant skill by its original author, enhanced with
# dashboard, areas, inventory, and safety features.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if present
if [[ -f "$SKILL_DIR/.env" ]]; then
  set -a
  source "$SKILL_DIR/.env"
  set +a
fi

# Load config file if present
CONFIG_FILE="${HA_CONFIG:-$HOME/.config/homeassistant/config.json}"
if [[ -f "$CONFIG_FILE" ]]; then
  HA_URL="${HA_URL:-$(jq -r '.url // empty' "$CONFIG_FILE" 2>/dev/null || true)}"
  HA_TOKEN="${HA_TOKEN:-$(jq -r '.token // empty' "$CONFIG_FILE" 2>/dev/null || true)}"
fi

: "${HA_URL:?Set HA_URL environment variable or configure $CONFIG_FILE}"
: "${HA_TOKEN:?Set HA_TOKEN environment variable or configure $CONFIG_FILE}"

# Blocked entities file
BLOCKED_FILE="$SKILL_DIR/blocked_entities.json"

cmd="${1:-help}"
shift || true

# --- Helpers ---

api() {
  curl -s -H "Authorization: Bearer $HA_TOKEN" -H "Content-Type: application/json" "$@"
}

check_blocked() {
  local entity="$1"
  if [[ -f "$BLOCKED_FILE" ]]; then
    local is_blocked
    is_blocked=$(jq -r --arg e "$entity" '.blocked // [] | map(select(. == $e)) | length' "$BLOCKED_FILE" 2>/dev/null || echo "0")
    if [[ "$is_blocked" -gt 0 ]]; then
      echo "❌ BLOCKED: $entity is in blocked_entities.json and cannot be controlled."
      exit 1
    fi
  fi
}

CRITICAL_DOMAINS="lock alarm_control_panel"

warn_critical() {
  local entity="$1"
  local domain="${entity%%.*}"
  local is_cover_garage=false

  # Check if it's a cover with garage device_class
  if [[ "$domain" == "cover" ]]; then
    local dc
    dc=$(api "$HA_URL/api/states/$entity" 2>/dev/null | jq -r '.attributes.device_class // ""')
    [[ "$dc" == "garage" || "$dc" == "gate" ]] && is_cover_garage=true
  fi

  for cd in $CRITICAL_DOMAINS; do
    if [[ "$domain" == "$cd" ]] || $is_cover_garage; then
      echo "⚠️  CRITICAL: $entity is a security-sensitive device ($domain)."
      echo "   The agent MUST confirm with the user before executing this action."
      echo "   If running interactively, type YES to proceed or anything else to cancel."
      read -r -p "   Confirm? " response 2>/dev/null || return 0
      if [[ "${response,,}" != "yes" && "${response,,}" != "y" ]]; then
        echo "❌ Cancelled."
        exit 1
      fi
      return 0
    fi
  done
}

# --- Commands ---

case "$cmd" in

  # --- State ---

  state|get)
    entity="${1:?Usage: ha.sh state <entity_id>}"
    api "$HA_URL/api/states/$entity" | jq -r '.state // "unknown"'
    ;;

  full|states)
    entity="${1:?Usage: ha.sh full <entity_id>}"
    api "$HA_URL/api/states/$entity" | jq
    ;;

  # --- Control ---

  on|turn_on)
    entity="${1:?Usage: ha.sh on <entity_id> [brightness]}"
    check_blocked "$entity"
    warn_critical "$entity"
    domain="${entity%%.*}"
    brightness="${2:-}"
    if [[ -n "$brightness" ]]; then
      api -X POST "$HA_URL/api/services/$domain/turn_on" \
        -d "{\"entity_id\": \"$entity\", \"brightness\": $brightness}" >/dev/null
    else
      api -X POST "$HA_URL/api/services/$domain/turn_on" \
        -d "{\"entity_id\": \"$entity\"}" >/dev/null
    fi
    echo "✓ $entity turned on"
    ;;

  off|turn_off)
    entity="${1:?Usage: ha.sh off <entity_id>}"
    check_blocked "$entity"
    warn_critical "$entity"
    domain="${entity%%.*}"
    api -X POST "$HA_URL/api/services/$domain/turn_off" \
      -d "{\"entity_id\": \"$entity\"}" >/dev/null
    echo "✓ $entity turned off"
    ;;

  toggle)
    entity="${1:?Usage: ha.sh toggle <entity_id>}"
    check_blocked "$entity"
    warn_critical "$entity"
    domain="${entity%%.*}"
    api -X POST "$HA_URL/api/services/$domain/toggle" \
      -d "{\"entity_id\": \"$entity\"}" >/dev/null
    echo "✓ $entity toggled"
    ;;

  # --- Scenes & Scripts ---

  scene)
    scene="${1:?Usage: ha.sh scene <scene_name>}"
    [[ "$scene" == scene.* ]] || scene="scene.$scene"
    api -X POST "$HA_URL/api/services/scene/turn_on" \
      -d "{\"entity_id\": \"$scene\"}" >/dev/null
    echo "✓ Scene $scene activated"
    ;;

  script)
    script="${1:?Usage: ha.sh script <script_name>}"
    [[ "$script" == script.* ]] || script="script.$script"
    api -X POST "$HA_URL/api/services/script/turn_on" \
      -d "{\"entity_id\": \"$script\"}" >/dev/null
    echo "✓ Script $script executed"
    ;;

  automation|trigger)
    auto="${1:?Usage: ha.sh automation <automation_name>}"
    [[ "$auto" == automation.* ]] || auto="automation.$auto"
    api -X POST "$HA_URL/api/services/automation/trigger" \
      -d "{\"entity_id\": \"$auto\"}" >/dev/null
    echo "✓ Automation $auto triggered"
    ;;

  # --- Climate ---

  climate|temp)
    entity="${1:?Usage: ha.sh climate <entity_id> <temperature>}"
    temp="${2:?Usage: ha.sh climate <entity_id> <temperature>}"
    check_blocked "$entity"
    api -X POST "$HA_URL/api/services/climate/set_temperature" \
      -d "{\"entity_id\": \"$entity\", \"temperature\": $temp}" >/dev/null
    echo "✓ $entity set to ${temp}°"
    ;;

  # --- Discovery ---

  list)
    filter="${1:-all}"
    if [[ "$filter" == "all" ]]; then
      api "$HA_URL/api/states" | jq -r '.[].entity_id' | sort
    else
      # Normalize: "lights" -> "light", "switches" -> "switch"
      filter="${filter%s}"
      api "$HA_URL/api/states" | jq -r --arg d "$filter" \
        '.[] | select(.entity_id | startswith($d + ".")) | "\(.entity_id): \(.state)"' | sort
    fi
    ;;

  search)
    pattern="${1:?Usage: ha.sh search <pattern>}"
    api "$HA_URL/api/states" | jq -r --arg p "$pattern" \
      '.[] | select(.entity_id | test($p; "i")) | "\(.entity_id): \(.state)"'
    ;;

  areas)
    api -X POST "$HA_URL/api/template" \
      -d '{"template": "{% for area in areas() %}{{ area }}\n{% endfor %}"}' 2>/dev/null \
      || echo "Template API not available. List areas from HA UI."
    ;;

  # --- Dashboard ---

  dashboard|status)
    echo "=== 🏠 Home Assistant Dashboard ==="
    echo ""

    echo "👥 Presence:"
    api "$HA_URL/api/states" | jq -r '.[] | select(.entity_id | startswith("person.")) | "  \(.attributes.friendly_name // .entity_id): \(.state)"'
    echo ""

    echo "💡 Lights ON:"
    LIGHTS=$(api "$HA_URL/api/states" | jq -r '.[] | select(.entity_id | startswith("light.")) | select(.state == "on") | "  \(.attributes.friendly_name // .entity_id)"')
    if [[ -z "$LIGHTS" ]]; then echo "  (none)"; else echo "$LIGHTS"; fi
    echo ""

    echo "🌡️ Temperature:"
    api "$HA_URL/api/states" | jq -r '.[] | select(.entity_id | startswith("sensor.")) | select(.attributes.device_class == "temperature") | "  \(.attributes.friendly_name // .entity_id): \(.state)\(.attributes.unit_of_measurement // "")"'
    echo ""

    echo "🔒 Locks:"
    LOCKS=$(api "$HA_URL/api/states" | jq -r '.[] | select(.entity_id | startswith("lock.")) | "  \(.attributes.friendly_name // .entity_id): \(.state)"')
    if [[ -z "$LOCKS" ]]; then echo "  (none configured)"; else echo "$LOCKS"; fi
    echo ""

    echo "🚪 Open doors/windows:"
    DOORS=$(api "$HA_URL/api/states" | jq -r '.[] | select(.entity_id | startswith("binary_sensor.")) | select(.state == "on") | select(.attributes.device_class == "door" or .attributes.device_class == "window") | "  \(.attributes.friendly_name // .entity_id)"')
    if [[ -z "$DOORS" ]]; then echo "  (all closed)"; else echo "$DOORS"; fi
    ;;

  # --- Generic ---

  call)
    domain="${1:?Usage: ha.sh call <domain> <service> [json_data]}"
    service="${2:?Usage: ha.sh call <domain> <service> [json_data]}"
    data="${3:-{}}"
    api -X POST "$HA_URL/api/services/$domain/$service" -d "$data"
    ;;

  notify)
    message="${1:?Usage: ha.sh notify <message> [title] [service]}"
    title="${2:-Home Assistant}"
    service="${3:-notify}"
    api -X POST "$HA_URL/api/services/notify/$service" \
      -d "{\"message\": \"$message\", \"title\": \"$title\"}" >/dev/null
    echo "✓ Notification sent: $message"
    ;;

  info)
    api "$HA_URL/api/" | jq
    ;;

  # --- Inventory ---

  inventory)
    if command -v node &>/dev/null; then
      node "$SCRIPT_DIR/inventory.js"
    else
      echo "Node.js not found. Install it or run: curl + jq entity listing instead."
      echo "Falling back to basic entity list..."
      api "$HA_URL/api/states" | jq -r 'group_by(.entity_id | split(".")[0]) | .[] | "## \(.[0].entity_id | split(".")[0] | ascii_upcase)\n\([ .[] | "  \(.entity_id): \(.state)"] | join("\n"))\n"'
    fi
    ;;

  # --- Help ---

  help|*)
    cat <<EOF
🏠 Home Assistant CLI — Definitive Skill

Usage: ha.sh <command> [args...]

State:
  state <entity>              Get entity state value
  full <entity>               Get full state with attributes
  dashboard                   Quick status of everything

Control:
  on <entity> [brightness]    Turn on (optional brightness 0-255)
  off <entity>                Turn off
  toggle <entity>             Toggle on/off
  scene <name>                Activate scene
  script <name>               Run script
  automation <name>           Trigger automation
  climate <entity> <temp>     Set temperature
  notify <msg> [title] [svc]  Send notification

Discovery:
  list [domain]               List entities (light, switch, all)
  search <pattern>            Search entities by name
  areas                       List all areas
  inventory                   Generate full entity inventory

Generic:
  call <domain> <svc> [json]  Call any service
  info                        Get HA instance info

Examples:
  ha.sh on light.living_room 200
  ha.sh scene movie_night
  ha.sh list light
  ha.sh search kitchen
  ha.sh dashboard
  ha.sh notify "Door open" "Alert"
EOF
    ;;
esac
