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
if [ -z "$APP_PATH" ]; then
  echo "Übersicht.app not found" >&2
  exit 1
fi

open "$APP_PATH"
echo "Started: $APP_PATH"
