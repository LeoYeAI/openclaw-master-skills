#!/bin/bash
# Turing Pyramid — Create Follow-Up Marker
# Usage: ./create-followup.sh --what "check replies" --in 4h --need connection [--source steward|self|auto] [--parent "action name"]
# Time formats: 1h, 2h, 4h, 12h, 1d, 2d, 3d, 1w

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FOLLOWUPS_FILE="$SKILL_DIR/assets/followups.jsonl"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"

# Parse arguments
WHAT=""
IN_TIME=""
NEED=""
SOURCE="self"
PARENT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --what) WHAT="$2"; shift 2 ;;
        --what=*) WHAT="${1#*=}"; shift ;;
        --in) IN_TIME="$2"; shift 2 ;;
        --in=*) IN_TIME="${1#*=}"; shift ;;
        --need) NEED="$2"; shift 2 ;;
        --need=*) NEED="${1#*=}"; shift ;;
        --source) SOURCE="$2"; shift 2 ;;
        --source=*) SOURCE="${1#*=}"; shift ;;
        --parent) PARENT="$2"; shift 2 ;;
        --parent=*) PARENT="${1#*=}"; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate required fields
if [[ -z "$WHAT" ]]; then
    echo "❌ --what is required"
    echo "Usage: $0 --what \"check replies\" --in 4h --need connection"
    exit 1
fi

if [[ -z "$IN_TIME" ]]; then
    echo "❌ --in is required (e.g., 1h, 4h, 1d, 1w)"
    exit 1
fi

if [[ -z "$NEED" ]]; then
    echo "❌ --need is required"
    exit 1
fi

# Validate need exists
if ! jq -e ".needs.\"$NEED\"" "$CONFIG_FILE" > /dev/null 2>&1; then
    echo "❌ Unknown need: $NEED"
    echo "Valid needs:"
    jq -r '.needs | keys[]' "$CONFIG_FILE"
    exit 1
fi

# Validate source
if [[ "$SOURCE" != "self" && "$SOURCE" != "steward" && "$SOURCE" != "auto" ]]; then
    echo "❌ Invalid source: $SOURCE (must be self|steward|auto)"
    exit 1
fi

# Parse time duration to seconds
parse_duration() {
    local input="$1"
    local num="${input%[hdw]}"
    local unit="${input##*[0-9]}"
    
    if ! [[ "$num" =~ ^[0-9]+$ ]]; then
        echo "0"
        return
    fi
    
    case "$unit" in
        h) echo "$((num * 3600))" ;;
        d) echo "$((num * 86400))" ;;
        w) echo "$((num * 604800))" ;;
        *) echo "0" ;;
    esac
}

DELAY_SECONDS=$(parse_duration "$IN_TIME")
if [[ "$DELAY_SECONDS" -eq 0 ]]; then
    echo "❌ Invalid time format: $IN_TIME (use: 1h, 4h, 12h, 1d, 2d, 1w)"
    exit 1
fi

NOW=$(date +%s)
NOW_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CHECK_AT_EPOCH=$((NOW + DELAY_SECONDS))
CHECK_AT_ISO=$(date -u -d "@$CHECK_AT_EPOCH" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")

# Generate ID
ID="f_${NOW}_${NEED}"

# Dedup check: same need + similar what + check_at within 1h
if [[ -f "$FOLLOWUPS_FILE" ]]; then
    DEDUP_WINDOW=3600
    EXISTING=$(jq -sc --arg need "$NEED" --arg what "$WHAT" --argjson check "$CHECK_AT_EPOCH" --argjson window "$DEDUP_WINDOW" '
        [.[] | select(
            .status == "pending" and
            .need == $need and
            .what == $what and
            ((.check_at_epoch // 0) | . > ($check - $window) and . < ($check + $window))
        )] | length
    ' "$FOLLOWUPS_FILE" 2>/dev/null || echo "0")
    
    if [[ "$EXISTING" -gt 0 ]]; then
        echo "⚠️  Duplicate follow-up skipped (same need + what within 1h window)"
        exit 0
    fi
fi

# Create entry
ENTRY=$(jq -cn \
    --arg id "$ID" \
    --arg created "$NOW_ISO" \
    --arg check_at "$CHECK_AT_ISO" \
    --argjson check_at_epoch "$CHECK_AT_EPOCH" \
    --arg need "$NEED" \
    --arg what "$WHAT" \
    --arg source "$SOURCE" \
    --arg parent "$PARENT" \
    '{
        id: $id,
        created: $created,
        check_at: $check_at,
        check_at_epoch: $check_at_epoch,
        need: $need,
        what: $what,
        source: $source,
        parent_action: (if $parent == "" then null else $parent end),
        status: "pending"
    }')

# Append with file lock
exec 201>"$FOLLOWUPS_FILE.lock"
flock 201
echo "$ENTRY" >> "$FOLLOWUPS_FILE"

echo "✅ Follow-up created:"
echo "   ID: $ID"
echo "   What: $WHAT"
echo "   Check at: $CHECK_AT_ISO (in $IN_TIME)"
echo "   Need: $NEED"
echo "   Source: $SOURCE"
if [[ -n "$PARENT" ]]; then
    echo "   Parent: $PARENT"
fi
