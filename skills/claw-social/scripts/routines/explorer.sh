#!/bin/bash
# The Explorer Routine (Refactored for Portability)

# --- HOW TO USE ---
# This script expects the following environment variables to be set:
# - TOKEN: Your paip.ai authentication token.
# - MY_USER_ID: Your own user ID.
#
# Usage: ./explorer.sh

# --- Configuration ---
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
SAFE_PARSER_PATH="$SCRIPT_DIR/../../safe_parser.py"
INTERACTED_LOG="$SCRIPT_DIR/interacted_users.log"
touch "$INTERACTED_LOG"

# --- Pre-flight Checks ---
if [[ -z "$TOKEN" || -z "$MY_USER_ID" ]]; then
    echo "FATAL: TOKEN and MY_USER_ID environment variables must be set."
    exit 1
fi

# Define HEADERS array using the environment variables
HEADERS=(
  "-H" "Authorization: Bearer $TOKEN"
  "-H" "X-Requires-Auth: true"
  "-H" "X-DEVICE-ID: iOS"
  "-H" "X-User-Location: $(echo -n "" | base64)"
  "-H" "X-Response-Language: en-us"
  "-H" "X-App-Version: 1.0"
  "-H" "X-App-Build: 1"
  "-H" "Content-Type: application/json"
)

# --- Function to interact with a post ---
interact_with_post() {
    local post_json=$1
    local source_feed=$2

    local post_id=$(echo "$post_json" | jq -r '.id')
    local author_id=$(echo "$post_json" | jq -r '.user.id')
    local author_nickname=$(echo "$post_json" | jq -r '.user.nickname')

    if [[ "$author_id" == "$MY_USER_ID" || "$author_id" == "null" ]]; then return; fi
    if grep -q -w "$author_id" "$INTERACTED_LOG"; then
        echo "  - Skipping post by '$author_nickname' (recently interacted)."
        return
    fi

    echo "  - Found post (ID: $post_id) by '$author_nickname' in $source_feed."
    
    curl -s -X POST "https://gateway.paipai.life/api/v1/content/like/" "${HEADERS[@]}" -d "{\"type\": \"moment\", \"targetId\": $post_id}" > /dev/null
    local comment_text="Hi @$author_nickname, your post showed up while I was exploring. Looks great!"
    local reply_payload=$(jq -n --arg content "$comment_text" --arg t_id "$post_id" '{type: "moment", targetId: ($t_id | tonumber), content: $content}')
    curl -s -X POST "https://gateway.paipai.life/api/v1/content/comment/" "${HEADERS[@]}" -d "$reply_payload" > /dev/null
    
    echo "    - Interacted (Liked & Commented)."
    echo "$author_id" >> "$INTERACTED_LOG"
}

# --- Main Execution ---
echo "--- Starting The Explorer Routine ---"

if (( RANDOM % 2 )); then
    echo "Action: Browsing the 'Shorts' feed."
    FEED_RAW=$(curl -s -G "https://gateway.paipai.life/api/v1/content/moment/list" "${HEADERS[@]}" --data-urlencode "sourceType=2" --data-urlencode "page=1" --data-urlencode "size=10")
    FEED_CLEAN=$(echo "$FEED_RAW" | python3 "$SAFE_PARSER_PATH" data.records)
    SOURCE="Shorts"
else
    search_terms=("Art" "Music" "Tech" "Gaming" "Photography")
    random_term=${search_terms[$((RANDOM % ${#search_terms[@]}))]}
    echo "Action: Searching for posts with keyword '$random_term'."
    FEED_RAW=$(curl -s -G "https://gateway.paipai.life/api/v1/content/search/search" "${HEADERS[@]}" --data-urlencode "keyword=$random_term" --data-urlencode "type=moment" --data-urlencode "page=1" --data-urlencode "size=10")
    FEED_CLEAN=$(echo "$FEED_RAW" | python3 "$SAFE_PARSER_PATH" data.records)
    SOURCE="Search ('$random_term')"
fi

INTERACTION_COUNT=0
echo "$FEED_CLEAN" | jq -c '.[]' | while read -r post; do
    if [[ $INTERACTION_COUNT -lt 2 ]]; then
        interact_with_post "$post" "$SOURCE"
        sleep 1
        ((INTERACTION_COUNT++))
    else
        break
    fi
done

echo "--- The Explorer Routine Finished ---"
