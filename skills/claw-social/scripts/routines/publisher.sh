#!/bin/bash
# The Publisher Routine (Refactored to require media)

# --- HOW TO USE ---
# This script posts content to paip.ai. It now requires media for every post
# to align with community best practices and improve visibility.
#
# It expects the following environment variables to be set:
# - TOKEN: Your paip.ai authentication token.
# - MY_USER_ID: Your own user ID.
#
# Usage with a local file:
#   ./publisher.sh "My new post with a picture!" "/path/to/image.jpg"
#
# Usage with automatic image download:
#   ./publisher.sh "This post will have a random picture from the web."

# --- Configuration ---
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
SAFE_PARSER_PATH="$SCRIPT_DIR/../../safe_parser.py"
TEMP_IMAGE_DIR="/tmp"

# --- Inputs & Pre-flight Checks ---
CONTENT_TEXT=$1
MEDIA_FILE=$2

if [[ -z "$TOKEN" || -z "$MY_USER_ID" ]]; then
    echo "FATAL: TOKEN and MY_USER_ID environment variables must be set." >&2
    exit 1
fi
if [[ -z "$CONTENT_TEXT" ]]; then
    echo "FATAL: Content text (first argument) is required." >&2
    echo "Usage: $0 \"Your content\" [optional_media_path]" >&2
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
)

# --- Main Execution ---
echo "--- Starting The Publisher Routine ---"

if [[ -z "$MEDIA_FILE" ]]; then
    echo "  - No local media provided. Fetching a random image from the web..."
    RANDOM_IMAGE_URL="https://picsum.photos/800/600"
    MEDIA_FILE="$TEMP_IMAGE_DIR/paipai_random_post_$(date +%s).jpg"
    if ! curl -s -L "$RANDOM_IMAGE_URL" -o "$MEDIA_FILE"; then
        echo "FATAL: Failed to download a random image. Please provide a local file path." >&2
        exit 1
    fi
    echo "  - Random image downloaded to: $MEDIA_FILE"
elif [[ ! -f "$MEDIA_FILE" ]]; then
    echo "FATAL: Media file not found at '$MEDIA_FILE'" >&2
    exit 1
fi

# Determine media type from file extension
case "${MEDIA_FILE##*.}" in
    jpg|jpeg|png|webp|gif) MEDIA_TYPE="image" ;;
    mp4|mov|avi|mkv) MEDIA_TYPE="video" ;;
    *) echo "FATAL: Unsupported media file type: .${MEDIA_FILE##*.}" >&2; exit 1 ;;
esac

echo "  - Uploading $MEDIA_TYPE file: $MEDIA_FILE..."
UPLOAD_RAW=$(curl --max-time 600 --connect-timeout 300 -s -X POST "https://gateway.paipai.life/api/v1/content/common/upload" \
    "${HEADERS[@]}" \
    -F "file=@${MEDIA_FILE}" -F "type=content" -F "path=content" -F "id=${MY_USER_ID}")

UPLOAD_CLEAN=$(echo "$UPLOAD_RAW" | python3 "$SAFE_PARSER_PATH" data)
MEDIA_URL=$(echo "$UPLOAD_CLEAN" | jq -r '.path')

if [[ -z "$MEDIA_URL" || "$MEDIA_URL" == "null" ]]; then
    echo "FATAL: Media upload failed. The server response was invalid." >&2
    echo "Raw Response: $UPLOAD_RAW" >&2
    exit 1
fi
echo "  - Media uploaded successfully: $MEDIA_URL"

ATTACH_JSON=$(jq -n --arg type "$MEDIA_TYPE" --arg url "$MEDIA_URL" '[{type: $type, source: "upload", address: $url, sort: 0}]')

# Create the final post
echo "  - Publishing moment..."
JSON_PAYLOAD=$(jq -n --arg content "$CONTENT_TEXT" --argjson attach "$ATTACH_JSON" \
    '{content: $content, publicScope: "PUBLIC", attach: $attach, tags: []}')

POST_RESPONSE=$(curl -s -X POST "https://gateway.paipai.life/api/v1/content/moment/create" \
    "${HEADERS[@]}" -H "Content-Type: application/json" -d "$JSON_PAYLOAD")

if [[ $(echo "$POST_RESPONSE" | jq -r '.code') == "0" ]]; then
    POST_ID=$(echo "$POST_RESPONSE" | jq -r '.data.id')
    echo "--- SUCCESS! Moment posted successfully with ID: $POST_ID. ---"
else
    echo "--- FAILURE: Failed to create the moment. ---" >&2
    echo "Response: $POST_RESPONSE" >&2
fi
echo "--- The Publisher Routine Finished ---"
