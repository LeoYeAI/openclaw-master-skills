#!/usr/bin/env bash
# competitor-patent-watch.sh — daily JSONL feed of new patents filed by a competitor.
#
# Pulls every patent filed by COMPETITOR since SINCE_DATE, paginating until exhausted,
# de-duplicates by application number against a local cursor file, and emits only
# newly-seen records to stdout (one JSON per line).
#
# Usage:
#   KIPRIS_PLUS_KEY=xxx ./competitor-patent-watch.sh "Apple Inc." 20260101 .apple-cursor
#
# Designed to be run from cron — pipe stdout into your downstream alerting/storage.

set -euo pipefail

COMPETITOR="${1:-삼성전자주식회사}"
SINCE="${2:-$(date -v-30d +%Y%m%d 2>/dev/null || date -d '30 days ago' +%Y%m%d)}"
CURSOR_FILE="${3:-./.kipris-cursor-$(echo "$COMPETITOR" | tr -c '[:alnum:]' '_')}"

CLI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bin/kipris-cli"

touch "$CURSOR_FILE"
PAGE=1
NEW=0
while :; do
  BATCH=$("$CLI" applicant --name "$COMPETITOR" --start-date "$SINCE" --rows 100 --page "$PAGE")
  COUNT=$(printf '%s\n' "$BATCH" | grep -c '^{' || true)
  [ "$COUNT" -eq 0 ] && break
  printf '%s\n' "$BATCH" | while IFS= read -r line; do
    APPNO=$(printf '%s' "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('applicationNumber','') or d.get('app_no',''))")
    [ -z "$APPNO" ] && continue
    if ! grep -qx "$APPNO" "$CURSOR_FILE"; then
      printf '%s\n' "$line"
      printf '%s\n' "$APPNO" >> "$CURSOR_FILE"
      NEW=$((NEW+1))
    fi
  done
  [ "$COUNT" -lt 100 ] && break
  PAGE=$((PAGE+1))
  sleep 0.1
done

echo "watch: $NEW new patents for '$COMPETITOR' since $SINCE" >&2
