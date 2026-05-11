#!/usr/bin/env bash
set -euo pipefail

# Open the preview page in the browser after draft upload.
#
# Reads API credentials from ~/.promptfolio/config.json.

CONFIG="${HOME}/.promptfolio/config.json"
API_URL=$(sed -n 's/.*"api_url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$CONFIG" | head -n1)

PREVIEW_URL="${API_URL}/me/preview"

if command -v open >/dev/null 2>&1; then
  open "$PREVIEW_URL"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$PREVIEW_URL"
fi

echo "Preview URL: $PREVIEW_URL"
