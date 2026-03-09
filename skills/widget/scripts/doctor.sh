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

APP_PATH="$(find_uebersicht_app || true)"
WIDGET_DIR="$HOME/Library/Application Support/Übersicht/widgets"

if [ -n "$APP_PATH" ]; then
  echo "OK   app        $APP_PATH"
else
  echo "FAIL app        Übersicht.app not found"
fi

if [ -d "$WIDGET_DIR" ]; then
  echo "OK   widgets    $WIDGET_DIR"
else
  echo "FAIL widgets    $WIDGET_DIR"
fi

if [ -n "$APP_PATH" ] && [ -d "$WIDGET_DIR" ]; then
  exit 0
fi

exit 1
