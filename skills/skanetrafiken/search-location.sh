#!/bin/bash
# Search Skånetrafiken stops/locations by name
# Usage: ./search-location.sh <name> [limit]
#
# Returns: Point ID, Name, Type, Coordinates

set -euo pipefail

# Cleanup temp files on exit
trap 'rm -f /tmp/skanetrafiken_points_$$.json' EXIT

QUERY="${1:-}"
LIMIT="${2:-3}"

if [ -z "$QUERY" ]; then
    echo "Usage: $0 <location-name> [limit]"
    echo "  limit: Number of results to show (default: 3, max: 10)"
    echo ""
    echo "Example: $0 \"malmö c\""
    echo "Example: $0 \"lund\" 5"
    exit 1
fi

# Validate and cap limit
if ! [[ "$LIMIT" =~ ^[0-9]+$ ]] || [ "$LIMIT" -lt 1 ]; then
    LIMIT=3
elif [ "$LIMIT" -gt 10 ]; then
    LIMIT=10
fi

# URL encode the query
ENCODED_QUERY=$(printf '%s' "$QUERY" | jq -sRr @uri)

echo "Searching for: $QUERY"
echo "---"

# Make API call with error handling
HTTP_CODE=$(curl -s --max-time 30 -w "%{http_code}" --compressed "https://www.skanetrafiken.se/gw-tps/api/v2/Points?name=${ENCODED_QUERY}" \
    -H "search-engine-environment: TjP" \
    -H "accept: application/json" \
    -H "user-agent: skanetrafiken-agent-skill/1.1" \
    -o /tmp/skanetrafiken_points_$$.json)

if [[ "$HTTP_CODE" -ne 200 ]]; then
    echo "Error: API request failed with HTTP status ${HTTP_CODE}" >&2
    rm -f /tmp/skanetrafiken_points_$$.json
    exit 1
fi

RESPONSE=$(cat /tmp/skanetrafiken_points_$$.json)
rm -f /tmp/skanetrafiken_points_$$.json

# Validate JSON response
if ! echo "$RESPONSE" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON response from API" >&2
    exit 1
fi

# Check if we got results
POINT_COUNT=$(echo "$RESPONSE" | jq '.points | length // 0')

if [ "$POINT_COUNT" -eq 0 ]; then
    echo "No locations found for: $QUERY"
    echo ""
    echo "Tips:"
    echo "  - Check spelling (Swedish: å, ä, ö)"
    echo "  - Try more specific name (e.g., 'Malmö C' not 'Malmö')"
    echo "  - Try nearby landmarks"
    exit 1
fi

echo "Found $POINT_COUNT location(s):"
echo ""

# Output formatted results
echo "$RESPONSE" | jq -r --argjson limit "$LIMIT" '
    .points[:$limit][] |
    "ID: \(.id2)\nName: \(.name)\nType: \(.type)\nArea: \(.area // "Skåne")\nCoordinates: \(.lat), \(.lon)\n\(if .outsideOperatingArea == true then "⚠️  Outside Skåne operating area\n" else "" end)---"
'

# Show if more results available
SHOWN=$((LIMIT < POINT_COUNT ? LIMIT : POINT_COUNT))
if [ "$POINT_COUNT" -gt "$SHOWN" ]; then
    echo "(Showing $SHOWN of $POINT_COUNT results. Use: $0 \"$QUERY\" <limit> for more)"
fi
