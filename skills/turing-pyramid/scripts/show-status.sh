#!/bin/bash
# Turing Pyramid — Show Current Status
# Displays all needs with tension levels

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$SKILL_DIR/assets/needs-config.json"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"

if [[ ! -f "$STATE_FILE" ]]; then
    echo "❌ Not initialized. Run: ./scripts/init.sh"
    exit 1
fi

echo "🔺 Turing Pyramid — Current Status"
echo "==================================="
echo ""

NOW=$(date +%s)

# Process each need and calculate tension
echo "| Need          | Imp | Decay | Hours | Sat | Dep | Tension |"
echo "|---------------|-----|-------|-------|-----|-----|---------|"

needs=$(jq -r '.needs | keys[]' "$CONFIG_FILE")

for need in $needs; do
    importance=$(jq -r ".needs.\"$need\".importance" "$CONFIG_FILE")
    decay_rate=$(jq -r ".needs.\"$need\".decay_rate_hours" "$CONFIG_FILE")
    last_sat=$(jq -r ".\"$need\".last_satisfied" "$STATE_FILE")
    
    if [[ "$last_sat" == "null" || -z "$last_sat" ]]; then
        hours_since="∞"
        satisfaction=0
    else
        last_sat_epoch=$(date -d "$last_sat" +%s 2>/dev/null || echo 0)
        hours_since=$(( (NOW - last_sat_epoch) / 3600 ))
        decay_steps=$(( hours_since / decay_rate ))
        satisfaction=$(( 3 - decay_steps ))
        [[ $satisfaction -lt 0 ]] && satisfaction=0
    fi
    
    deprivation=$(( 3 - satisfaction ))
    tension=$(( importance * deprivation ))
    
    printf "| %-13s | %3d | %5dh | %5s | %3d | %3d | %7d |\n" \
        "$need" "$importance" "$decay_rate" "$hours_since" "$satisfaction" "$deprivation" "$tension"
done | sort -t'|' -k8 -rn

echo ""
echo "Legend: Imp=Importance, Sat=Satisfaction(0-3), Dep=Deprivation, Tension=Imp×Dep"
echo "Higher tension = higher priority"

# Spontaneity surplus display
SCRIPTS_DIR="$SKILL_DIR/scripts"
source "$SCRIPTS_DIR/spontaneity.sh" 2>/dev/null
show_surplus_status "$STATE_FILE" "$CONFIG_FILE" "false"
show_noise_status "$STATE_FILE" "$CONFIG_FILE"
