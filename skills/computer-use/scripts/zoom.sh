#!/bin/bash
# zoom.sh - Capture cropped region of screen
# Usage: zoom.sh X1 Y1 X2 Y2
# Returns base64 of the cropped region

export DISPLAY=:99
OUTPUT_DIR="/tmp/computer-use"
mkdir -p "$OUTPUT_DIR"

X1=$1
Y1=$2
X2=$3
Y2=$4

if [ -z "$X1" ] || [ -z "$Y1" ] || [ -z "$X2" ] || [ -z "$Y2" ]; then
    echo "ERROR: Usage: zoom.sh X1 Y1 X2 Y2" >&2
    exit 1
fi

TIMESTAMP=$(date +%s%N)
FULL_FILE="$OUTPUT_DIR/full_$TIMESTAMP.png"
CROP_FILE="$OUTPUT_DIR/crop_$TIMESTAMP.png"

# Take full screenshot
scrot -o "$FULL_FILE" 2>/dev/null

if [ ! -f "$FULL_FILE" ]; then
    echo "ERROR: Failed to take screenshot" >&2
    exit 1
fi

# Calculate crop dimensions
WIDTH=$((X2 - X1))
HEIGHT=$((Y2 - Y1))

# Crop using ImageMagick
convert "$FULL_FILE" -crop "${WIDTH}x${HEIGHT}+${X1}+${Y1}" +repage "$CROP_FILE"

if [ ! -f "$CROP_FILE" ]; then
    echo "ERROR: Failed to crop screenshot" >&2
    rm -f "$FULL_FILE"
    exit 1
fi

# Output base64
base64 -w0 "$CROP_FILE"

# Cleanup
rm -f "$FULL_FILE" "$CROP_FILE"
