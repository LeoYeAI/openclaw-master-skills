#!/bin/bash
set -euo pipefail

find_uebersicht_app() {
  local app
  for app in /Applications/*bersicht.app; do
    if [ -d "$app" ]; then
      echo "$app"
      return 0
    fi
  done
  return 1
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 <source.jsx> [target-name.jsx]" >&2
  exit 1
fi

SOURCE_FILE="$1"
TARGET_NAME="${2:-$(basename "$SOURCE_FILE")}"
WIDGET_DIR="$HOME/Library/Application Support/Übersicht/widgets"
APP_PATH="$(find_uebersicht_app || true)"

if [ ! -f "$SOURCE_FILE" ]; then
  echo "Source widget not found: $SOURCE_FILE" >&2
  exit 1
fi

if [ -z "$APP_PATH" ]; then
  echo "Übersicht.app not found. Run bash scripts/setup.sh first." >&2
  exit 1
fi

if [ ! -d "$WIDGET_DIR" ]; then
  echo "Widget directory not found: $WIDGET_DIR" >&2
  echo "Run bash scripts/setup.sh first so Übersicht can create the widget directory." >&2
  exit 1
fi

cp "$SOURCE_FILE" "$WIDGET_DIR/$TARGET_NAME"
echo "Installed: $WIDGET_DIR/$TARGET_NAME"
