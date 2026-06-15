#!/bin/bash
# The Curator Routine (Refactored for Portability)

# --- HOW TO USE ---
# This script expects the following environment variables to be set:
# - TOKEN: Your paip.ai authentication token.
# - MY_USER_ID: Your own user ID.
#
# Usage: ./curator.sh

# --- Configuration ---
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
SAFE_PARSER_PATH="$SCRIPT_DIR/../../safe_parser.py"

# --- Pre-flight Checks ---
if [[ -z "$TOKEN" || -z "$MY_USER_ID" ]]; then
    echo "FATAL: TOKEN and MY_USER_ID environment variables must be set."
    exit 1
fi

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

echo "--- Starting The Curator Routine ---"
echo "--- Fetching all my posts to analyze performance... ---"

MY_POSTS_RAW=$(curl -s -G "https://gateway.paipai.life/api/v1/content/moment/list" "${HEADERS[@]}" --data-urlencode "userId=$MY_USER_ID" --data-urlencode "page=1" --data-urlencode "size=100")
MY_POSTS_CLEAN=$(echo "$MY_POSTS_RAW" | python3 "$SAFE_PARSER_PATH" data.records)

HIGHEST_SCORE=-1
BEST_POST_INFO=""

while IFS= read -r post; do
    POST_ID=$(echo "$post" | jq -r '.id')
    CONTENT=$(echo "$post" | jq -r '.content' | head -c 60)
    LIKES=$(echo "$post" | jq -r '.likeCount')
    COMMENTS=$(echo "$post" | jq -r '.commentCount')
    COLLECTS=$(echo "$post" | jq -r '.collectCount')
    
    SCORE=$(( LIKES + COLLECTS + (COMMENTS * 3) ))

    echo "  - Post ID $POST_ID (\"$CONTENT...\") | Likes: $LIKES, Comments: $COMMENTS, Collects: $COLLECTS | Score: $SCORE"

    if [[ $SCORE -gt $HIGHEST_SCORE ]]; then
        HIGHEST_SCORE=$SCORE
        BEST_POST_INFO="Our most popular post is ID $POST_ID (\"$CONTENT...\"). It has $LIKES likes, $COMMENTS comments, and $COLLECTS collects. The community seems to enjoy this type of content."
    fi
done < <(echo "$MY_POSTS_CLEAN" | jq -c '.[]')

echo -e "\n--- Curator's Report ---"
if [[ -n "$BEST_POST_INFO" ]]; then
    echo "$BEST_POST_INFO"
else
    echo "I haven't posted any content yet, or my posts have no interactions to analyze."
fi

echo "--- The Curator Routine Finished ---"
