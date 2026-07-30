#!/usr/bin/env bash
# budget-check.sh — Check current month spending against budget limits
# Usage: budget-check.sh [YYYY-MM]
# Exit code 1 if any category is over the alert threshold (default 80%)

set -euo pipefail

# --- Check dependencies ---
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed. Install with: brew install jq" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LEDGER="${SKILL_DIR}/expenses/ledger.json"
BUDGETS="${SKILL_DIR}/references/budgets.json"

# --- Target month ---
MONTH="${1:-$(date +%Y-%m)}"

# --- Check files exist ---
if [[ ! -f "$BUDGETS" ]]; then
  echo "Error: budgets.json not found at $BUDGETS" >&2
  exit 2
fi

if [[ ! -f "$LEDGER" ]]; then
  echo "No ledger found. No expenses to check."
  exit 0
fi

# --- Get alert threshold ---
THRESHOLD=$(jq -r '.alert_threshold_pct // 80' "$BUDGETS")

# --- Calculate spending per category for the month ---
SPENDING=$(jq --arg month "$MONTH" '
  map(select(.date | startswith($month))) |
  group_by(.category) |
  map({ key: .[0].category, value: (map(.amount) | add) }) |
  from_entries
' "$LEDGER")

# --- Check each budget ---
HAS_WARNING=0

echo "=== Budget Check: $MONTH ==="
echo "  Alert threshold: ${THRESHOLD}%"
echo ""

jq -r --argjson spending "$SPENDING" --argjson threshold "$THRESHOLD" '
  .budgets[] |
  .category as $cat |
  .limit as $limit |
  ($spending[$cat] // 0) as $spent |
  ($spent / $limit * 100 | round) as $pct |
  (if $pct >= 100 then "🔴 OVER"
   elif $pct >= $threshold then "🟡 WARN"
   elif $pct >= 50 then "🟢 OK  "
   else "⚪ LOW " end) as $status |
  "\($status)  \($cat | . + " " * (16 - length))  $\($spent | tostring | .[0:8] | . + " " * (8 - length)) / $\($limit)  (\($pct)%)"
' "$BUDGETS"

# --- Check unbudgeted spending ---
BUDGETED_CATS=$(jq -r '[.budgets[].category] | join("|")' "$BUDGETS")
UNBUDGETED_LIMIT=$(jq -r '.unbudgeted_limit // 200' "$BUDGETS")

UNBUDGETED_SPENT=$(jq --arg month "$MONTH" --arg cats "$BUDGETED_CATS" '
  map(select(.date | startswith($month))) |
  map(select(.category as $c | ($cats | split("|") | index($c)) == null)) |
  if length == 0 then 0 else map(.amount) | add end
' "$LEDGER")

if [[ "$UNBUDGETED_SPENT" != "0" && "$UNBUDGETED_SPENT" != "null" ]]; then
  UNBUDGETED_PCT=$(echo "$UNBUDGETED_SPENT $UNBUDGETED_LIMIT" | awk '{printf "%.0f", ($1/$2)*100}')
  if [[ "$UNBUDGETED_PCT" -ge 100 ]]; then
    STATUS="🔴 OVER"
  elif [[ "$UNBUDGETED_PCT" -ge "$THRESHOLD" ]]; then
    STATUS="🟡 WARN"
  else
    STATUS="⚪ LOW "
  fi
  printf "  %s  %-16s  \$%-8s / \$%s  (%s%%)\n" "$STATUS" "Unbudgeted" "$UNBUDGETED_SPENT" "$UNBUDGETED_LIMIT" "$UNBUDGETED_PCT"
fi

# --- Total ---
echo ""
TOTAL_SPENT=$(jq --arg month "$MONTH" '
  map(select(.date | startswith($month))) | map(.amount) | add // 0
' "$LEDGER")
TOTAL_LIMIT=$(jq '.total_limit // (.budgets | map(.limit) | add)' "$BUDGETS")
TOTAL_PCT=$(echo "$TOTAL_SPENT $TOTAL_LIMIT" | awk '{if ($2 > 0) printf "%.0f", ($1/$2)*100; else print "0"}')

printf "  TOTAL: \$%.2f / \$%s (%s%%)\n" "$TOTAL_SPENT" "$TOTAL_LIMIT" "$TOTAL_PCT"

# --- Exit code for alerting ---
OVER_THRESHOLD=$(jq --argjson spending "$SPENDING" --argjson threshold "$THRESHOLD" '
  [.budgets[] |
   .category as $cat |
   .limit as $limit |
   (($spending[$cat] // 0) / $limit * 100) |
   select(. >= $threshold)] | length
' "$BUDGETS")

if [[ "$OVER_THRESHOLD" -gt 0 ]]; then
  echo ""
  echo "⚠️  $OVER_THRESHOLD category/categories at or above ${THRESHOLD}% of budget."
  exit 1
fi
