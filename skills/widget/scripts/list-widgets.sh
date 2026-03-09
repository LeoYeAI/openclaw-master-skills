#!/bin/bash
set -euo pipefail

WIDGET_DIR="$HOME/Library/Application Support/Übersicht/widgets"

if [ ! -d "$WIDGET_DIR" ]; then
  echo "Widget directory not found: $WIDGET_DIR" >&2
  exit 1
fi

find "$WIDGET_DIR" -maxdepth 1 -type f \( -name '*.jsx' -o -name '*.jsx.disabled' \) \
  | sort
