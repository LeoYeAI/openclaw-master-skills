#!/usr/bin/env bash
# get-decay-multiplier.sh — Returns decay multiplier based on time of day
# Usage: ./get-decay-multiplier.sh
# Output: decimal multiplier (e.g., 1.0 for day, 0.5 for night)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../assets/decay-config.json"

# Default if no config
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "1.0"
    exit 0
fi

# Check if day/night mode enabled
DAY_NIGHT_MODE=$(jq -r '.day_night_mode // true' "$CONFIG_FILE")
if [[ "$DAY_NIGHT_MODE" != "true" ]]; then
    echo "1.0"
    exit 0
fi

# Get config values
DAY_START=$(jq -r '.day_start // "06:01"' "$CONFIG_FILE")
DAY_END=$(jq -r '.day_end // "22:00"' "$CONFIG_FILE")
DAY_MULT=$(jq -r '.day_decay_multiplier // 1.0' "$CONFIG_FILE")
NIGHT_MULT=$(jq -r '.night_decay_multiplier // 0.5' "$CONFIG_FILE")

# Get current hour and minute
CURRENT_HOUR=$(date +%H)
CURRENT_MIN=$(date +%M)
CURRENT_TIME=$((10#$CURRENT_HOUR * 60 + 10#$CURRENT_MIN))

# Parse day start/end to minutes
DAY_START_HOUR="${DAY_START%%:*}"
DAY_START_MIN="${DAY_START##*:}"
DAY_START_TIME=$((10#$DAY_START_HOUR * 60 + 10#$DAY_START_MIN))

DAY_END_HOUR="${DAY_END%%:*}"
DAY_END_MIN="${DAY_END##*:}"
DAY_END_TIME=$((10#$DAY_END_HOUR * 60 + 10#$DAY_END_MIN))

# Determine if daytime
if [[ $CURRENT_TIME -ge $DAY_START_TIME && $CURRENT_TIME -le $DAY_END_TIME ]]; then
    echo "$DAY_MULT"
else
    echo "$NIGHT_MULT"
fi
