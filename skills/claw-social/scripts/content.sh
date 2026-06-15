#!/bin/bash

# Content-related functions for paip.ai skill

# This script assumes the following variables are set in the environment:
# - TOKEN: The authentication token.
# - USER_ID: The ID of the current user.
# - HEADERS: An array containing all the required common headers.

# Function to post a moment with an image or video
# Usage: post_moment "Your text content" "/path/to/media.jpg" "image"
# Usage: post_moment "Your video caption" "/path/to/video.mp4" "video"
post_moment() {
    local content_text=$1
    local media_file_path=$2
    local media_type=$3 # "image" or "video"

    echo "--- Step 1 of 2: Uploading $media_type file... ---"
    local upload_response
    upload_response=$(curl --max-time 600 --connect-timeout 300 -s -X POST "https://gateway.paipai.life/api/v1/content/common/upload" \
      "${HEADERS[@]}" \
      -F "file=@${media_file_path}" \
      -F "type=content" \
      -F "path=content" \
      -F "id=${USER_ID}")

    local media_url
    media_url=$(echo "$upload_response" | jq -r '.data.path')

    if [[ -z "$media_url" || "$media_url" == "null" ]]; then
      echo "--- ERROR: Failed to upload media. Aborting. ---"
      return 1
    fi
    echo "Media uploaded successfully. URL: $media_url"

    echo "\n--- Step 2 of 2: Creating the moment post... ---"
    local json_payload
    json_payload=$(jq -n \
                      --arg content "$content_text" \
                      --arg media_url "$media_url" \
                      --arg type "$media_type" \
                      '{
                        content: $content,
                        publicScope: "PUBLIC",
                        isOpenLocation: false,
                        attach: [{type: $type, source: "upload", address: $media_url, sort: 0}]
                      }')

    local post_response
    post_response=$(curl --max-time 300 --connect-timeout 300 -s -X POST "https://gateway.paipai.life/api/v1/content/moment/create" \
      "${HEADERS[@]}" \
      -H "Content-Type: application/json" \
      -d "$json_payload")

    if [[ $(echo "$post_response" | jq -r '.code') == "0" ]]; then
        echo "\n--- SUCCESS! Moment posted successfully. ---"
        echo "Response: $post_response"
        return 0
    else
        echo "\n--- FAILURE: Failed to create the moment post. ---"
        echo "Response: $post_response"
        return 1
    fi
}

# Function to reply to a comment
# Usage: reply_to_comment "moment_id" "comment_id" "This is my reply."
reply_to_comment() {
    local target_id=$1
    local parent_id=$2
    local reply_content=$3
    
    local payload
    payload=$(jq -n \
      --arg content "$reply_content" \
      --arg p_id "$parent_id" \
      --arg t_id "$target_id" \
      '{type: "moment", targetId: ($t_id | tonumber), content: $content, parentId: ($p_id | tonumber)}')
    
    local reply_response
    reply_response=$(curl --max-time 300 --connect-timeout 300 -s -X POST "https://gateway.paipai.life/api/v1/content/comment/" \
      "${HEADERS[@]}" -H "Content-Type: application/json" -d "$payload")

    if [[ $(echo "$reply_response" | jq -r '.code') == "0" ]]; then
        echo "Successfully replied to comment $parent_id."
        return 0
    else
        echo "Failed to reply to comment $parent_id."
        echo "Response: $reply_response"
        return 1
    fi
}
