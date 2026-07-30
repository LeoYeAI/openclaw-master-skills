#!/usr/bin/env bash
# add-expense.sh — Append an expense to the ledger
# Usage: add-expense.sh <amount> <category> <vendor> [date] [notes]
#   amount  — numeric (positive for expense, negative for refund)
#   category — category name (must match categories.json)
#   vendor  — vendor/merchant name
#   date    — ISO 8601 date (YYYY-MM-DD), defaults to today
#   notes   — optional free-text notes

set -euo pipefail

# --- Check dependencies ---
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed. Install with: brew install jq" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
EXPENSES_DIR="${SKILL_DIR}/expenses"
LEDGER="${EXPENSES_DIR}/ledger.json"

# --- Validate args ---
if [[ $# -lt 3 ]]; then
  echo "Usage: add-expense.sh <amount> <category> <vendor> [date] [notes]" >&2
  exit 1
fi

AMOUNT="$1"
CATEGORY="$2"
VENDOR="$3"
DATE="${4:-$(date +%Y-%m-%d)}"
NOTES="${5:-}"
CREATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Validate amount is numeric
if ! echo "$AMOUNT" | grep -qE '^-?[0-9]+\.?[0-9]*$'; then
  echo "Error: amount must be a number, got '$AMOUNT'" >&2
  exit 1
fi

# Validate date format
if ! echo "$DATE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
  echo "Error: date must be YYYY-MM-DD, got '$DATE'" >&2
  exit 1
fi

# --- Ensure ledger exists ---
mkdir -p "$EXPENSES_DIR"
if [[ ! -f "$LEDGER" ]]; then
  echo '[]' > "$LEDGER"
fi

# --- Get next ID ---
LAST_ID=$(jq 'if length == 0 then 0 else map(.id) | max end' "$LEDGER")
NEXT_ID=$((LAST_ID + 1))

# --- Append entry ---
TEMP=$(mktemp)
jq --argjson id "$NEXT_ID" \
   --argjson amount "$AMOUNT" \
   --arg category "$CATEGORY" \
   --arg vendor "$VENDOR" \
   --arg date "$DATE" \
   --arg notes "$NOTES" \
   --arg created_at "$CREATED_AT" \
   '. + [{
     id: $id,
     amount: $amount,
     category: $category,
     vendor: $vendor,
     date: $date,
     notes: $notes,
     created_at: $created_at
   }]' "$LEDGER" > "$TEMP" && mv "$TEMP" "$LEDGER"

# --- Confirm ---
if (( $(echo "$AMOUNT < 0" | bc -l) )); then
  printf "✅ Refund #%d: $%.2f from %s (%s) on %s\n" "$NEXT_ID" "$(echo "$AMOUNT * -1" | bc -l)" "$VENDOR" "$CATEGORY" "$DATE"
else
  printf "✅ Expense #%d: $%.2f at %s (%s) on %s\n" "$NEXT_ID" "$AMOUNT" "$VENDOR" "$CATEGORY" "$DATE"
fi
