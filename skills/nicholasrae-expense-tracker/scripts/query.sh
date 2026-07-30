#!/usr/bin/env bash
# query.sh — Query the expense ledger with filters
# Usage: query.sh [--from DATE] [--to DATE] [--category CAT] [--vendor VENDOR] [--format summary|detail|json]
#
# SECURITY: All user input is passed via jq --arg (data, never code).
# No string interpolation into jq filters — prevents jq injection.

set -euo pipefail

# --- Check dependencies ---
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed. Install with: brew install jq" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LEDGER="${SKILL_DIR}/expenses/ledger.json"

# --- Defaults ---
FROM_DATE=""
TO_DATE=""
CATEGORY=""
VENDOR=""
FORMAT="summary"

# --- Parse args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --from)     FROM_DATE="$2"; shift 2 ;;
    --to)       TO_DATE="$2";   shift 2 ;;
    --category) CATEGORY="$2";  shift 2 ;;
    --vendor)   VENDOR="$2";    shift 2 ;;
    --format)   FORMAT="$2";    shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# --- Input validation (dates must match YYYY-MM-DD) ---
if [[ -n "$FROM_DATE" ]] && ! echo "$FROM_DATE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
  echo "Error: --from must be YYYY-MM-DD, got '$FROM_DATE'" >&2; exit 1
fi
if [[ -n "$TO_DATE" ]] && ! echo "$TO_DATE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
  echo "Error: --to must be YYYY-MM-DD, got '$TO_DATE'" >&2; exit 1
fi

# --- Check ledger exists ---
if [[ ! -f "$LEDGER" ]]; then
  echo "No ledger found. No expenses recorded yet." >&2
  exit 0
fi

# --- Safe query: all user values passed as --arg (never interpolated into filter code) ---
RESULTS=$(jq \
  --arg from     "$FROM_DATE" \
  --arg to       "$TO_DATE" \
  --arg cat      "$CATEGORY" \
  --arg vendor   "$VENDOR" \
  'map(select(
    ($from   == "" or .date >= $from) and
    ($to     == "" or .date <= $to) and
    ($cat    == "" or (.category | ascii_downcase) == ($cat | ascii_downcase)) and
    ($vendor == "" or (.vendor   | ascii_downcase | contains($vendor | ascii_downcase)))
  ))' "$LEDGER")

COUNT=$(echo "$RESULTS" | jq 'length')

if [[ "$COUNT" -eq 0 ]]; then
  echo "No expenses found matching your filters."
  exit 0
fi

case "$FORMAT" in
  json)
    echo "$RESULTS" | jq .
    ;;
  detail)
    TOTAL=$(echo "$RESULTS" | jq '[.[].amount] | add')
    echo "=== Expense Detail ==="
    echo ""
    echo "$RESULTS" | jq -r '.[] |
      "  #\(.id | tostring | . + " " * (4 - length))  \(.date)  \(
        if .amount < 0
        then "-$\(.amount * -1 | tostring | if contains(".") then . else . + ".00" end)"
        else " $\(.amount      | tostring | if contains(".") then . else . + ".00" end)"
        end | .[0:12] | . + " " * (12 - length))  \(
        .category | .[0:16] | . + " " * (16 - length))  \(.vendor)\(
        if .notes != "" then " (\(.notes))" else "" end)"'
    echo ""
    printf "  Total: \$%.2f (%d items)\n" "$TOTAL" "$COUNT"
    ;;
  summary|*)
    echo "=== Spending Summary ==="
    [[ -n "$FROM_DATE" || -n "$TO_DATE" ]] && echo "  Period: ${FROM_DATE:-earliest} to ${TO_DATE:-latest}"
    [[ -n "$CATEGORY" ]] && echo "  Category: $CATEGORY"
    [[ -n "$VENDOR"   ]] && echo "  Vendor: $VENDOR"
    echo ""
    echo "$RESULTS" | jq -r '
      group_by(.category) |
      map({category: .[0].category, total: (map(.amount) | add), count: length}) |
      sort_by(-.total) | .[] |
      "  \(.category): $\(.total | tostring |
        if contains(".") then (split(".") | .[0] + "." + (.[1] + "00")[0:2])
        else . + ".00" end) (\(.count) \(if .count == 1 then "item" else "items" end))"'
    TOTAL=$(echo "$RESULTS" | jq '[.[].amount] | add')
    echo ""
    printf "  TOTAL: \$%.2f (%d items)\n" "$TOTAL" "$COUNT"
    ;;
esac
