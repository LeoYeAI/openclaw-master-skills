#!/bin/bash
# open-report.sh — Platform-aware browser opener for HTML reports
# Usage: open-report.sh <report.html>
# Compatible: macOS (open), Linux (xdg-open), WSL (wslview)
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: open-report.sh <report.html>" >&2
  exit 1
fi

REPORT_FILE="$1"

if [[ ! -f "$REPORT_FILE" ]]; then
  echo "File not found: $REPORT_FILE" >&2
  exit 1
fi

# Resolve to absolute path
if [[ "$REPORT_FILE" != /* ]]; then
  REPORT_FILE="$(cd "$(dirname "$REPORT_FILE")" && pwd)/$(basename "$REPORT_FILE")"
fi

# Detect platform and open
OS="$(uname -s)"
case "$OS" in
  Darwin)
    open "$REPORT_FILE"
    echo "{\"opened\":true,\"method\":\"open\",\"platform\":\"macOS\",\"file\":\"$REPORT_FILE\"}"
    ;;
  Linux)
    # Check for WSL
    if grep -qi microsoft /proc/version 2>/dev/null; then
      if command -v wslview >/dev/null 2>&1; then
        wslview "$REPORT_FILE"
        echo "{\"opened\":true,\"method\":\"wslview\",\"platform\":\"WSL\",\"file\":\"$REPORT_FILE\"}"
      elif command -v explorer.exe >/dev/null 2>&1; then
        explorer.exe "$(wslpath -w "$REPORT_FILE" 2>/dev/null || echo "$REPORT_FILE")"
        echo "{\"opened\":true,\"method\":\"explorer.exe\",\"platform\":\"WSL\",\"file\":\"$REPORT_FILE\"}"
      else
        echo "{\"opened\":false,\"error\":\"No browser opener found in WSL\",\"file\":\"$REPORT_FILE\"}" >&2
        exit 1
      fi
    elif command -v xdg-open >/dev/null 2>&1; then
      xdg-open "$REPORT_FILE"
      echo "{\"opened\":true,\"method\":\"xdg-open\",\"platform\":\"Linux\",\"file\":\"$REPORT_FILE\"}"
    else
      echo "{\"opened\":false,\"error\":\"xdg-open not found\",\"file\":\"$REPORT_FILE\"}" >&2
      exit 1
    fi
    ;;
  *)
    echo "{\"opened\":false,\"error\":\"Unsupported OS: $OS\",\"file\":\"$REPORT_FILE\"}" >&2
    exit 1
    ;;
esac
