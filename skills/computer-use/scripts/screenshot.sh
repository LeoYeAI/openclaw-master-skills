#!/bin/bash
# screenshot.sh - Capture screen and return base64 PNG
# Resolution: 1024x768 (XGA)

export DISPLAY=:99
OUTPUT_DIR="/tmp/computer-use"
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +%s%N)
FILE="$OUTPUT_DIR/screenshot_$TIMESTAMP.png"

# Take screenshot
scrot -o "$FILE" 2>/dev/null

if [ ! -f "$FILE" ]; then
    echo "ERROR: Failed to take screenshot" >&2
    exit 1
fi

# Output base64
base64 -w0 "$FILE"

# Cleanup
rm -f "$FILE"
