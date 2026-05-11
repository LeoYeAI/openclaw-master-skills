#!/usr/bin/env bash
# sentinel-premium-check.sh — Check text against premium patterns JSON
# Used internally by sentinel-input.sh and sentinel-output.sh when premium pack is installed.
#
# Usage:
#   echo "text" | sentinel-premium-check.sh [input|output]
#
# Looks for premium_patterns.json in:
#   1. ~/.sentinel/premium_patterns.json
#   2. SKILL_DIR/patterns/premium_patterns.json

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
MODE="${1:-input}"

# Find premium patterns
PREMIUM_FILE=""
if [[ -f "$HOME/.sentinel/premium_patterns.json" ]]; then
  PREMIUM_FILE="$HOME/.sentinel/premium_patterns.json"
elif [[ -f "$SKILL_DIR/patterns/premium_patterns.json" ]]; then
  PREMIUM_FILE="$SKILL_DIR/patterns/premium_patterns.json"
fi

if [[ -z "$PREMIUM_FILE" ]]; then
  # No premium patterns — pass through silently
  echo '{"premium":false,"threats":[]}'
  exit 0
fi

INPUT=$(cat)
if [[ -z "$INPUT" ]]; then
  echo '{"premium":true,"threats":[]}'
  exit 0
fi

THREATS=()
SEVERITY="CLEAN"

update_severity() {
  local new="$1"
  case "$SEVERITY" in
    CLEAN)   SEVERITY="$new" ;;
    WARNING) [[ "$new" == "HIGH" || "$new" == "CRITICAL" ]] && SEVERITY="$new" ;;
    HIGH)    [[ "$new" == "CRITICAL" ]] && SEVERITY="$new" ;;
  esac
}

# Check if jq is available
if ! command -v jq &>/dev/null; then
  echo '{"premium":true,"threats":[],"error":"jq not installed"}'
  exit 0
fi

# Determine which categories to check based on mode
if [[ "$MODE" == "input" ]]; then
  CATEGORIES=$(jq -r 'to_entries[] | select(.key | test("prompt_injection|data_exfil|command_injection|social_engineering|metadata_ssrf|encoding_evasion|file_system")) | .key' "$PREMIUM_FILE" 2>/dev/null)
else
  CATEGORIES=$(jq -r 'to_entries[] | select(.key | test("secret_patterns|crypto")) | .key' "$PREMIUM_FILE" 2>/dev/null)
fi

# Iterate categories and patterns
while IFS= read -r category; do
  [[ -z "$category" ]] && continue

  cat_severity=$(jq -r ".[\"$category\"].severity // \"HIGH\"" "$PREMIUM_FILE" 2>/dev/null)
  patterns=$(jq -r ".[\"$category\"].patterns[]" "$PREMIUM_FILE" 2>/dev/null)

  while IFS= read -r pattern; do
    [[ -z "$pattern" ]] && continue

    if echo "$INPUT" | LC_ALL=en_US.UTF-8 grep -qP "$pattern" 2>/dev/null; then
      THREATS+=("$category")
      update_severity "$cat_severity"
      break  # One match per category is enough
    fi
  done <<< "$patterns"
done <<< "$CATEGORIES"

THREAT_COUNT=${#THREATS[@]}

if [[ $THREAT_COUNT -eq 0 ]]; then
  echo '{"premium":true,"threats":[]}'
  exit 0
fi

# Build JSON output
THREATS_JSON="["
for i in "${!THREATS[@]}"; do
  [[ $i -gt 0 ]] && THREATS_JSON+=","
  THREATS_JSON+="\"${THREATS[$i]}\""
done
THREATS_JSON+="]"

echo "{\"premium\":true,\"severity\":\"$SEVERITY\",\"threat_count\":$THREAT_COUNT,\"threats\":$THREATS_JSON}"
exit 1
