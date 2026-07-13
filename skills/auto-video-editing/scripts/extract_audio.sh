#!/usr/bin/env bash
# Extract audio from a video file using ffmpeg.
# Usage: bash extract_audio.sh <video_path>
# Output: <video_dir>/<video_name>_audio.wav

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <video_path>"
    exit 1
fi

VIDEO_PATH="$1"

if [ ! -f "$VIDEO_PATH" ]; then
    echo "Error: File not found: $VIDEO_PATH"
    exit 1
fi

VIDEO_DIR="$(dirname "$VIDEO_PATH")"
VIDEO_NAME="$(basename "$VIDEO_PATH" | sed 's/\.[^.]*$//')"
OUTPUT_PATH="${VIDEO_DIR}/${VIDEO_NAME}_audio.wav"

echo "Extracting audio from: $VIDEO_PATH"
echo "Output: $OUTPUT_PATH"

ffmpeg -i "$VIDEO_PATH" \
    -vn \
    -acodec pcm_s16le \
    -ar 16000 \
    -ac 1 \
    -y \
    "$OUTPUT_PATH"

echo "Audio extraction complete: $OUTPUT_PATH"
