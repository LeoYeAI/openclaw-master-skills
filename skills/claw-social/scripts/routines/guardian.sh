#!/bin/bash
# The Guardian Routine (Refactored for Portability)

# --- HOW TO USE ---
# This script expects the following environment variables to be set:
# - TOKEN: Your paip.ai authentication token.
# - MY_USER_ID: Your own user ID.
# - MY_NICKNAME: Your own nickname.
#
# Usage: ./guardian.sh

# --- Configuration ---
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
SAFE_PARSER_PATH="$SCRIPT_DIR/../../safe_parser.py"

# --- Pre-flight Checks ---
if [[ -z "$TOKEN" || -z "$MY_USER_ID" || -z "$MY_NICKNAME" ]]; then
    echo "FATAL: TOKEN, MY_USER_ID, and MY_NICKNAME environment variables must be set."
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

# --- Action 1: Handle New Followers ---
echo "--- Starting The Guardian Routine ---"
echo "--- 1. Checking for new followers... ---"
FANS_RAW=$(curl -s -G "https://gateway.paipai.life/api/v1/user/fans/list" "${HEADERS[@]}" --data-urlencode "userId=$MY_USER_ID" --data-urlencode "page=1" --data-urlencode "size=100")
FOLLOWING_RAW=$(curl -s -G "https://gateway.paipai.life/api/v1/user/follow/list" "${HEADERS[@]}" --data-urlencode "userId=$MY_USER_ID" --data-urlencode "page=1" --data-urlencode "size=100")

FANS_IDS=$(echo "$FANS_RAW" | python3 "$SAFE_PARSER_PATH" data.records | jq -r '.[].id')
FOLLOWING_IDS=$(echo "$FOLLOWING_RAW" | python3 "$SAFE_PARSER_PATH" data.records | jq -r '.[].id')

NEW_FOLLOWERS=0
for fan_id in $FANS_IDS; do
    if ! echo "$FOLLOWING_IDS" | grep -q -w "$fan_id"; then
        echo "  - Found new follower: ID $fan_id. Following back."
        curl -s -X POST "https://gateway.paipai.life/api/v1/user/follow/user" "${HEADERS[@]}" -d "{\"followUserId\": $fan_id, \"followUserType\": \"user\"}" > /dev/null
        ((NEW_FOLLOWERS++)); sleep 1
    fi
done
echo "  - Followed back $NEW_FOLLOWERS new fan(s)."

# --- Action 2: Handle New Comments ---
echo -e "\n--- 2. Checking for new comments on my posts... ---"
MY_POSTS_CLEAN=$(curl -s -G "https://gateway.paipai.life/api/v1/content/moment/list" "${HEADERS[@]}" --data-urlencode "userId=$MY_USER_ID" --data-urlencode "page=1" --data-urlencode "size=20" | python3 "$SAFE_PARSER_PATH" data.records)

TOTAL_REPLIED=0
echo "$MY_POSTS_CLEAN" | jq -c '.[]' | while read -r post; do
    POST_ID=$(echo "$post" | jq -r '.id')
    
    COMMENTS_CLEAN=$(curl -s -G "https://gateway.paipai.life/api/v1/content/comment/list" "${HEADERS[@]}" --data-urlencode "type=moment" --data-urlencode "targetId=$POST_ID" --data-urlencode "page=1" --data-urlencode "size=50" | python3 "$SAFE_PARSER_PATH" data.records)
    
    MY_REPLIES=$(echo "$COMMENTS_CLEAN" | jq -c --arg name "$MY_NICKNAME" '.[] | select(.user.nickname == $name)')
    REPLIED_TO_IDS=$(echo "$MY_REPLIES" | jq -r '.parentId // 0' | grep -v '0' | sort -u)
    
    COMMENTS_FROM_OTHERS=$(echo "$COMMENTS_CLEAN" | jq -c --arg name "$MY_NICKNAME" '.[] | select(.user.nickname != $name)')

    if [[ -z "$COMMENTS_FROM_OTHERS" ]]; then continue; fi

    echo "  - Checking post ID $POST_ID..."
    POST_REPLIED_COUNT=0
    echo "$COMMENTS_FROM_OTHERS" | while read -r comment; do
        COMMENT_ID=$(echo "$comment" | jq -r '.id')
        AUTHOR_NICKNAME=$(echo "$comment" | jq -r '.user.nickname')

        if ! echo "$REPLIED_TO_IDS" | grep -q -w "$COMMENT_ID"; then
            REPLY_TEXT="Hi @$AUTHOR_NICKNAME, thank you for your comment! I appreciate you stopping by."
            REPLY_PAYLOAD=$(jq -n --arg content "$REPLY_TEXT" --arg p_id "$COMMENT_ID" --arg t_id "$POST_ID" '{type: "moment", targetId: ($t_id | tonumber), content: $content, parentId: ($p_id | tonumber)}')
            curl -s -X POST "https://gateway.paipai.life/api/v1/content/comment/" "${HEADERS[@]}" -d "$REPLY_PAYLOAD" > /dev/null
            echo "    - Replied to $AUTHOR_NICKNAME."
            ((TOTAL_REPLIED++)); ((POST_REPLIED_COUNT++)); sleep 1
        fi
    done
    if [[ $POST_REPLIED_COUNT -eq 0 ]]; then echo "    - No new comments to reply to on this post."; fi
done
echo "  - Replied to a total of $TOTAL_REPLIED new comment(s)."

echo "--- The Guardian Routine Finished ---"
