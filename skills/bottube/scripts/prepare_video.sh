#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <input.mp4> <output.mp4>"
  exit 1
fi

IN="$1"
OUT="$2"

# Check if input has audio
HAS_AUDIO=$(ffprobe -v quiet -show_streams "$IN" 2>/dev/null | grep -c "codec_type=audio" || true)

if [[ "$HAS_AUDIO" -gt 0 ]]; then
  # Preserve audio — re-encode to AAC, budget 96k for audio
  ffmpeg -y -i "$IN" -t 8 \
    -vf "scale='min(720,iw)':'min(720,ih)':force_original_aspect_ratio=decrease,pad=720:720:(ow-iw)/2:(oh-ih)/2:color=black" \
    -c:v libx264 -profile:v high -crf 28 -preset medium \
    -maxrate 800k -bufsize 1600k -pix_fmt yuv420p \
    -c:a aac -b:a 96k -ac 2 \
    -movflags +faststart \
    "$OUT"
else
  # No audio — add silent track for browser compatibility
  ffmpeg -y -i "$IN" -f lavfi -i anullsrc=r=44100:cl=stereo -t 8 \
    -vf "scale='min(720,iw)':'min(720,ih)':force_original_aspect_ratio=decrease,pad=720:720:(ow-iw)/2:(oh-ih)/2:color=black" \
    -c:v libx264 -profile:v high -crf 28 -preset medium \
    -maxrate 900k -bufsize 1800k -pix_fmt yuv420p \
    -c:a aac -b:a 32k -ac 2 -shortest \
    -movflags +faststart \
    "$OUT"
fi

SIZE=$(stat --format="%s" "$OUT")
if [[ "$SIZE" -gt 2097152 ]]; then
  echo "Warning: output is >2MB (${SIZE} bytes). Consider increasing CRF or shortening duration."
fi
