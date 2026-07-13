#!/bin/bash
# Plan a journey using Skånetrafiken
# Usage: ./journey.sh <from-id> <from-type> <to-id> <to-type> [datetime] [mode]
#
# Point Types:
#   STOP_AREA  - Bus/train station (ID from search-location.sh)
#   ADDRESS    - Street address (ID from search-location.sh)
#   POI        - Point of interest (ID from search-location.sh)
#   LOCATION   - Raw coordinates as "lat#lon" (e.g., "55.572401#12.927215")
#
# DateTime formats (always Swedish time - CET/CEST):
#   (none)           - Travel now
#   "18:30"          - Today at 18:30
#   "tomorrow 09:00" - Tomorrow at 09:00
#   "2026-01-15 09:00" - Specific date at 09:00
#
# Modes:
#   depart (default) - Depart at specified time
#   arrive           - Arrive by specified time
#
# Examples:
#   # STOP_AREA to STOP_AREA (station to station)
#   ./journey.sh 9021012080000000 STOP_AREA 9021012080040000 STOP_AREA
#
#   # ADDRESS to STOP_AREA (search: ./search-location.sh "Kalendegatan 12C")
#   ./journey.sh 9920012000214063 ADDRESS 9021012080000000 STOP_AREA "09:00"
#
#   # LOCATION to STOP_AREA (GPS coordinates, lat#lon format)
#   ./journey.sh "55.572401#12.927215" LOCATION 9021012080000000 STOP_AREA
#
#   # Cross-border: Malmö C to Copenhagen
#   ./journey.sh 9021012080000000 STOP_AREA 9921000008600626 STOP_AREA "18:00"

set -euo pipefail

# Cleanup temp files on exit
trap 'rm -f /tmp/skanetrafiken_response_$$.json' EXIT

# All times are Swedish (Europe/Stockholm)
SWEDISH_TZ="Europe/Stockholm"

FROM_ID="${1:-}"
FROM_TYPE="${2:-}"
TO_ID="${3:-}"
TO_TYPE="${4:-}"
DATETIME_INPUT="${5:-}"
MODE="${6:-depart}"

if [ -z "$FROM_ID" ] || [ -z "$FROM_TYPE" ] || [ -z "$TO_ID" ] || [ -z "$TO_TYPE" ]; then
    echo "Usage: $0 <from-id> <from-type> <to-id> <to-type> [datetime] [mode]"
    echo ""
    echo "Point Types:"
    echo "  STOP_AREA  - Bus/train station (use search-location.sh to find ID)"
    echo "  ADDRESS    - Street address (use search-location.sh to find ID)"
    echo "  POI        - Point of interest (use search-location.sh to find ID)"
    echo "  LOCATION   - Raw coordinates as 'lat#lon' (e.g., '55.572401#12.927215')"
    echo ""
    echo "DateTime formats:"
    echo "  18:30              - Today at 18:30"
    echo "  tomorrow 09:00     - Tomorrow at 09:00"
    echo "  YYYY-MM-DD HH:MM   - Specific date (e.g., $(date +%Y-%m)-15 09:00)"
    echo ""
    echo "Mode: 'depart' (default) or 'arrive'"
    echo ""
    echo "Examples:"
    echo "  # STOP_AREA to STOP_AREA (station to station)"
    echo "  $0 9021012080000000 STOP_AREA 9021012080040000 STOP_AREA"
    echo ""
    echo "  # ADDRESS to STOP_AREA (home to station)"
    echo "  # Search first: ./search-location.sh 'Kalendegatan 12C'"
    echo "  $0 9920012000214063 ADDRESS 9021012080000000 STOP_AREA"
    echo ""
    echo "  # LOCATION to STOP_AREA (GPS coordinates to station)"
    echo "  $0 '55.572401#12.927215' LOCATION 9021012080000000 STOP_AREA"
    echo ""
    echo "  # Cross-border: Malmö C to Copenhagen"
    echo "  $0 9021012080000000 STOP_AREA 9921000008600626 STOP_AREA"
    exit 1
fi

# URL encode the from/to IDs (handles # in coordinates)
FROM_ID_ENCODED=$(printf '%s' "$FROM_ID" | jq -sRr @uri)
TO_ID_ENCODED=$(printf '%s' "$TO_ID" | jq -sRr @uri)

# Detect platform: GNU date (Linux) or BSD date (macOS)
if date -d "2024-01-01" >/dev/null 2>&1; then
    DATE_TYPE="gnu"
else
    DATE_TYPE="bsd"
fi

# Get today's date in Swedish timezone
get_today() {
    TZ="$SWEDISH_TZ" date +%Y-%m-%d
}

# Get tomorrow's date in Swedish timezone
get_tomorrow() {
    if [[ "$DATE_TYPE" == "gnu" ]]; then
        TZ="$SWEDISH_TZ" date -d "tomorrow" +%Y-%m-%d
    else
        TZ="$SWEDISH_TZ" date -v+1d +%Y-%m-%d
    fi
}

# Convert Swedish time to UTC for API
# Input: DATE_PART (YYYY-MM-DD), TIME_PART (HH:MM)
# Output: ISO 8601 UTC datetime string
swedish_to_utc() {
    local date_part="$1"
    local time_part="$2"
    local epoch

    if [[ "$DATE_TYPE" == "gnu" ]]; then
        epoch=$(TZ="$SWEDISH_TZ" date -d "${date_part} ${time_part}" +%s)
        date -u -d "@${epoch}" +%Y-%m-%dT%H:%M:%S.000Z
    else
        epoch=$(TZ="$SWEDISH_TZ" date -j -f "%Y-%m-%d %H:%M" "${date_part} ${time_part}" +%s)
        TZ=UTC date -r "$epoch" +%Y-%m-%dT%H:%M:%S.000Z
    fi
}

# Convert UTC time from API to Swedish time for display
# Input: ISO 8601 UTC datetime string (e.g., 2026-01-12T21:12:00Z)
# Output: HH:MM in Swedish timezone
utc_to_swedish_time() {
    local utc_time="$1"
    local clean="${utc_time%.000Z}"
    clean="${clean%Z}"
    local epoch

    if [[ "$DATE_TYPE" == "gnu" ]]; then
        epoch=$(date -u -d "${clean}" +%s)
        TZ="$SWEDISH_TZ" date -d "@${epoch}" +%H:%M
    else
        epoch=$(TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%S" "$clean" +%s 2>/dev/null) || {
            echo "${utc_time:11:5}"
            return
        }
        TZ="$SWEDISH_TZ" date -r "$epoch" +%H:%M
    fi
}

# Convert UTC time from API to Swedish date for display
# Input: ISO 8601 UTC datetime string
# Output: YYYY-MM-DD in Swedish timezone
utc_to_swedish_date() {
    local utc_time="$1"
    local clean="${utc_time%.000Z}"
    clean="${clean%Z}"
    local epoch

    if [[ "$DATE_TYPE" == "gnu" ]]; then
        epoch=$(date -u -d "${clean}" +%s)
        TZ="$SWEDISH_TZ" date -d "@${epoch}" +%Y-%m-%d
    else
        epoch=$(TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%S" "$clean" +%s 2>/dev/null) || {
            echo "${utc_time:0:10}"
            return
        }
        TZ="$SWEDISH_TZ" date -r "$epoch" +%Y-%m-%d
    fi
}

# Build base URL
BASE_URL="https://www.skanetrafiken.se/gw-tps/api/v2/Journey"
PARAMS="fromPointId=${FROM_ID_ENCODED}&fromPointType=${FROM_TYPE}&toPointId=${TO_ID_ENCODED}&toPointType=${TO_TYPE}"
PARAMS="${PARAMS}&priority=SHORTEST_TIME&journeysAfter=5&walkSpeed=NORMAL&maxWalkDistance=2000&allowWalkToOtherStop=true"

# Handle datetime
if [ -n "$DATETIME_INPUT" ]; then
    INPUT_LOWER=$(echo "$DATETIME_INPUT" | tr '[:upper:]' '[:lower:]')

    # Extract time
    if [[ "$DATETIME_INPUT" =~ ([0-9]{1,2}:[0-9]{2}) ]]; then
        TIME_PART="${BASH_REMATCH[1]}"
    else
        echo "Error: Could not parse time from '$DATETIME_INPUT'"
        echo "Expected format: HH:MM (e.g., 09:00, 18:30)"
        exit 1
    fi

    # Determine the date
    if [[ "$INPUT_LOWER" == *"tomorrow"* ]]; then
        DATE_PART=$(get_tomorrow)
        DATE_DISPLAY="tomorrow"
    elif [[ "$DATETIME_INPUT" =~ ([0-9]{4}-[0-9]{2}-[0-9]{2}) ]]; then
        DATE_PART="${BASH_REMATCH[1]}"
        DATE_DISPLAY="$DATE_PART"
    else
        DATE_PART=$(get_today)
        DATE_DISPLAY="today"
    fi

    # Convert local time to UTC for API
    DATETIME=$(swedish_to_utc "$DATE_PART" "$TIME_PART") || {
        echo "Error: Failed to convert time to UTC"
        exit 1
    }
    PARAMS="${PARAMS}&journeyDateTime=${DATETIME}"

    if [ "$MODE" = "arrive" ]; then
        PARAMS="${PARAMS}&arrival=true"
        echo "Searching for journeys arriving by ${TIME_PART} on ${DATE_DISPLAY} (${DATE_PART})..."
    else
        PARAMS="${PARAMS}&arrival=false"
        echo "Searching for journeys departing at ${TIME_PART} on ${DATE_DISPLAY} (${DATE_PART})..."
    fi
else
    PARAMS="${PARAMS}&arrival=false"
    echo "Searching for journeys now..."
fi

echo "From: $FROM_ID ($FROM_TYPE)"
echo "To: $TO_ID ($TO_TYPE)"
echo "---"

# Make API call
HTTP_CODE=$(curl -s --max-time 30 -w "%{http_code}" --compressed "${BASE_URL}?${PARAMS}" \
    -H "search-engine-environment: TjP" \
    -H "accept: application/json" \
    -H "user-agent: skanetrafiken-agent-skill/1.1" \
    -o /tmp/skanetrafiken_response_$$.json)

if [[ "$HTTP_CODE" -ne 200 ]]; then
    echo "Error: API request failed with HTTP status ${HTTP_CODE}" >&2
    rm -f /tmp/skanetrafiken_response_$$.json
    exit 1
fi

RESPONSE=$(cat /tmp/skanetrafiken_response_$$.json)
rm -f /tmp/skanetrafiken_response_$$.json

# Validate JSON response
if ! echo "$RESPONSE" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON response from API" >&2
    exit 1
fi

# Check for API errors
ERROR=$(echo "$RESPONSE" | jq -r '.error // empty')
if [[ -n "$ERROR" ]]; then
    echo "API Error: $ERROR" >&2
    exit 1
fi

# Check journey count
JOURNEY_COUNT=$(echo "$RESPONSE" | jq '.journeys | length')

if [ "$JOURNEY_COUNT" -eq 0 ]; then
    echo "No journeys found."
    echo ""
    echo "Tips:"
    echo "  - Try a different time"
    echo "  - Check if service runs at this hour"
    echo "  - Try nearby stops"
    exit 1
fi

echo "Found $JOURNEY_COUNT journey option(s):"
echo ""

# Helper to format deviation
format_deviation() {
    local dev="$1"
    # Skip if empty, null, or non-numeric
    if [[ -z "$dev" ]] || [[ "$dev" == "null" ]] || ! [[ "$dev" =~ ^-?[0-9]+$ ]]; then
        echo ""
    elif (( dev > 0 )); then
        echo " [+${dev} min late]"
    elif (( dev < 0 )); then
        echo " [${dev} min early]"
    fi
}

# Helper to format transport type
format_type() {
    case "$1" in
        Walk) echo "WALK" ;;
        Bus) echo "BUS" ;;
        Train) echo "TRAIN" ;;
        TrainOresund) echo "ORESUND" ;;
        Tram) echo "TRAM" ;;
        Metro) echo "METRO" ;;
        Ferry) echo "FERRY" ;;
        *) echo "OTHER" ;;
    esac
}

# Extract journey data as JSON and process with proper timezone conversion
JOURNEY_DATA=$(echo "$RESPONSE" | jq -c '.journeys[:5][]')

OPTION_NUM=0
while IFS= read -r journey; do
    ((OPTION_NUM++)) || true

    # Extract basic journey info in single jq call
    IFS=$'\t' read -r FROM_NAME TO_NAME DEPART_TIME_UTC ARRIVE_TIME_UTC DEPART_DEV ARRIVE_DEV DEPART_PASSED CHANGES STATUS_TEXT < <(
        echo "$journey" | jq -r '[
            .routeLinks[0].from.name,
            .routeLinks[-1].to.name,
            .routeLinks[0].from.time,
            .routeLinks[-1].to.time,
            (.routeLinks[0].from.deviation | tostring),
            (.routeLinks[-1].to.deviation | tostring),
            (.routeLinks[0].from.passed // false | tostring),
            (.noOfChanges | tostring),
            (.deviationTag.text // "-")
        ] | @tsv'
    )
    # Handle null strings from jq
    [[ "$DEPART_DEV" == "null" ]] && DEPART_DEV=""
    [[ "$ARRIVE_DEV" == "null" ]] && ARRIVE_DEV=""
    [[ "$STATUS_TEXT" == "-" ]] && STATUS_TEXT=""

    # Convert times to local timezone
    DEPART_LOCAL=$(utc_to_swedish_time "$DEPART_TIME_UTC")
    ARRIVE_LOCAL=$(utc_to_swedish_time "$ARRIVE_TIME_UTC")
    DATE_LOCAL=$(utc_to_swedish_date "$DEPART_TIME_UTC")

    # Format deviations
    DEPART_DEV_STR=$(format_deviation "$DEPART_DEV")
    ARRIVE_DEV_STR=$(format_deviation "$ARRIVE_DEV")
    PASSED_STR=""
    [[ "$DEPART_PASSED" == "true" ]] && PASSED_STR=" [PASSED]"

    echo "══════════════════════════════════════════════════════════════"
    echo "OPTION ${OPTION_NUM}: ${FROM_NAME} → ${TO_NAME}"
    echo "══════════════════════════════════════════════════════════════"
    echo "Date:    ${DATE_LOCAL}"
    echo "Depart:  ${DEPART_LOCAL}${DEPART_DEV_STR}${PASSED_STR}"
    echo "Arrive:  ${ARRIVE_LOCAL}${ARRIVE_DEV_STR}"
    echo "Changes: ${CHANGES}"
    [[ -n "$STATUS_TEXT" ]] && echo "Status:  ⚠️  ${STATUS_TEXT}"
    echo ""
    echo "LEGS:"

    # Process each leg - extract all fields in single jq call per leg
    while IFS=$'\t' read -r LEG_TYPE WALK_DIST LINE_NAME LINE_NO LEG_FROM_TIME LEG_FROM_NAME LEG_FROM_DEV LEG_FROM_POS LEG_TO_TIME LEG_TO_NAME LEG_TO_DEV LEG_TO_POS DIRECTION; do
        # Convert placeholders to empty
        [[ "$WALK_DIST" == "-" ]] && WALK_DIST=""
        [[ "$LINE_NAME" == "-" ]] && LINE_NAME=""
        [[ "$LINE_NO" == "-" ]] && LINE_NO=""
        [[ "$LEG_FROM_DEV" == "null" ]] && LEG_FROM_DEV=""
        [[ "$LEG_FROM_POS" == "-" ]] && LEG_FROM_POS=""
        [[ "$LEG_TO_DEV" == "null" ]] && LEG_TO_DEV=""
        [[ "$LEG_TO_POS" == "-" ]] && LEG_TO_POS=""
        [[ "$DIRECTION" == "-" ]] && DIRECTION=""

        if [[ "$LEG_TYPE" == "Walk" ]]; then
            echo "  → WALK ${WALK_DIST} from ${LEG_FROM_NAME} to ${LEG_TO_NAME}"
        else
            TYPE_ICON=$(format_type "$LEG_TYPE")
            LEG_FROM_LOCAL=$(utc_to_swedish_time "$LEG_FROM_TIME")
            LEG_TO_LOCAL=$(utc_to_swedish_time "$LEG_TO_TIME")
            LEG_FROM_DEV_STR=$(format_deviation "$LEG_FROM_DEV")
            LEG_TO_DEV_STR=$(format_deviation "$LEG_TO_DEV")

            echo "  → ${TYPE_ICON} ${LINE_NAME} ${LINE_NO}"
            POS_STR=""
            [[ -n "$LEG_FROM_POS" ]] && POS_STR=" [${LEG_FROM_POS}]"
            echo "    From: ${LEG_FROM_LOCAL} ${LEG_FROM_NAME}${LEG_FROM_DEV_STR}${POS_STR}"
            POS_STR=""
            [[ -n "$LEG_TO_POS" ]] && POS_STR=" [${LEG_TO_POS}]"
            echo "    To:   ${LEG_TO_LOCAL} ${LEG_TO_NAME}${LEG_TO_DEV_STR}${POS_STR}"
            [[ -n "$DIRECTION" ]] && echo "    Direction: ${DIRECTION}"
        fi
        echo ""
    done < <(echo "$journey" | jq -r '.routeLinks[] | [
        .line.type,
        (.line.distance // "-"),
        (.line.name // "-"),
        (.line.no // "-"),
        .from.time,
        .from.name,
        (.from.deviation | tostring),
        (.from.pos // "-"),
        .to.time,
        .to.name,
        (.to.deviation | tostring),
        (.to.pos // "-"),
        (.line.towards // "-")
    ] | @tsv')

    # Check for disruptions
    DISRUPTIONS=$(echo "$journey" | jq -r '[.routeLinks[].deviations // [] | .[] | .text] | unique | .[]' 2>/dev/null)
    if [[ -n "$DISRUPTIONS" ]]; then
        echo "⚠️  DISRUPTIONS:"
        while IFS= read -r disruption; do
            echo "  • ${disruption}"
        done <<< "$DISRUPTIONS"
    fi
done <<< "$JOURNEY_DATA"
