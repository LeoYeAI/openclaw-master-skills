#!/bin/bash
# List dmails in inbox
# Usage: list.sh [filter]
# filter: unread, sent, archive, or any tag

set -e

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
fi
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env"
    exit 1
fi

FILTER="${1:-}"

# Get all dmails as JSON
DMAILS=$(npx @didcid/keymaster list-dmail 2>/dev/null)

if [ "$DMAILS" = "{}" ]; then
    echo "No messages in inbox."
    exit 0
fi

# Format output
echo "$DMAILS" | jq -r --arg filter "$FILTER" '
    to_entries | 
    map(select(
        if $filter == "" then true
        else .value.tags | contains([$filter])
        end
    )) |
    sort_by(.value.date) | reverse |
    .[] | 
    "\(.value.date | split("T")[0]) | \(.value.sender // "Unknown") | \(.value.message.subject) | [\(.value.tags | join(","))] | \(.key | split(":")[2][:12])..."
' | column -t -s '|'
