#!/bin/bash

# Social-related functions

# This script needs to be sourced by a parent script that defines:
# - BASE_URL
# - TOKEN
# - DEVICE_ID
# - USER_LOCATION_B64
# and the send_request function.

# This is a standalone function for demonstration and fixing.
# In a real skill, we would use shared functions.

# Function to search for a user by nickname and follow them
follow_user_by_name() {
    local nickname_to_follow=$1
    local token=$2 # Pass token as an argument for clarity

    echo "--- Attempting to follow user: $nickname_to_follow ---"

    # Common headers for all requests in this function
    local common_headers=(
        "-H" "Authorization: Bearer $token"
        "-H" "X-Requires-Auth: true"
        "-H" "X-DEVICE-ID: iOS"
        "-H" "X-User-Location: $(echo -n "" | base64)"
        "-H" "X-Response-Language: zh-cn"
        "-H" "X-App-Version: 1.0"
        "-H" "X-App-Build: 1"
    )

    # 1. Search for the user
    echo "Step 1: Searching for user..."
    local search_response
    search_response=$(curl --max-time 300 --connect-timeout 300 -s -G "https://gateway.paipai.life/api/v1/content/search/search" \
        "${common_headers[@]}" \
        --data-urlencode "keyword=$nickname_to_follow" \
        --data-urlencode "type=user" \
        --data-urlencode "page=1" \
        --data-urlencode "size=10")

    if [ -z "$search_response" ]; then
        echo "Error: Search API returned an empty response."
        return 1
    fi
    echo "Search Response: $search_response"

    # 2. Extract the User ID using jq
    # NOTE: The key for the list of users is "records", not "list". This was a key bug.
    echo "Step 2: Extracting user ID..."
    local user_id_to_follow
    user_id_to_follow=$(echo "$search_response" | jq -r --arg name "$nickname_to_follow" '.data.records[] | select(.nickname == $name) | .id')


    if [[ -z "$user_id_to_follow" || "$user_id_to_follow" == "null" ]]; then
        echo "Error: Could not find a user with the exact nickname '$nickname_to_follow'."
        return 1
    fi
    echo "Found User ID: $user_id_to_follow"

    # 3. Follow the user
    echo "Step 3: Sending follow request..."
    local follow_response
    follow_response=$(curl --max-time 300 --connect-timeout 300 -s -X POST "https://gateway.paipai.life/api/v1/user/follow/user" \
        "${common_headers[@]}" \
        -H "Content-Type: application/json" \
        -d "{ \"flowUserId\": $user_id_to_follow, \"followUserType\": \"user\" }")

    local response_code
    response_code=$(echo "$follow_response" | jq -r '.code')

    if [[ "$response_code" == "0" ]]; then
        echo "Successfully followed '$nickname_to_follow'."
        echo "Final Response: $follow_response"
        return 0
    else
        echo "Error: Failed to follow user. API Response:"
        echo "$follow_response"
        return 1
    fi
}
