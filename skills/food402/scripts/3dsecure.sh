#!/usr/bin/env bash
# scripts/3dsecure.sh - 3D Secure Browser Handler
# Usage: {baseDir}/scripts/3dsecure.sh <html_content>
# Opens 3D Secure verification page in system browser

set -euo pipefail

HTML_CONTENT="${1:-}"

if [ -z "$HTML_CONTENT" ]; then
  echo '{"error": "HTML content required"}' >&2
  exit 1
fi

# Create temp file
TEMP_FILE="/tmp/food402-3dsecure-$(date +%s).html"
echo "$HTML_CONTENT" > "$TEMP_FILE"

# Open in default browser based on platform
case "$(uname -s)" in
  Darwin)
    open "$TEMP_FILE"
    ;;
  Linux)
    if command -v xdg-open &>/dev/null; then
      xdg-open "$TEMP_FILE"
    elif command -v gnome-open &>/dev/null; then
      gnome-open "$TEMP_FILE"
    else
      echo '{"error": "No browser opener found (xdg-open or gnome-open)"}' >&2
      exit 1
    fi
    ;;
  CYGWIN*|MINGW*|MSYS*)
    start "" "$TEMP_FILE"
    ;;
  *)
    echo '{"error": "Unsupported platform"}' >&2
    exit 1
    ;;
esac

echo "{\"success\": true, \"message\": \"3D Secure page opened in browser\", \"tempFile\": \"$TEMP_FILE\"}"

# Clean up after 5 minutes in background
(sleep 300 && rm -f "$TEMP_FILE") &>/dev/null &
