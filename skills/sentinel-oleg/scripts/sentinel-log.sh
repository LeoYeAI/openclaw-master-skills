#!/usr/bin/env bash
# sentinel-log.sh — View Claw Sentinel audit log
#
# Usage:
#   sentinel-log.sh                    # Show last 10 entries
#   sentinel-log.sh --last 20          # Show last N entries
#   sentinel-log.sh --severity CRITICAL # Filter by severity
#   sentinel-log.sh --today            # Show today's entries
#   sentinel-log.sh --stats            # Summary statistics
#   sentinel-log.sh --clear            # Clear log (with confirmation)

set -euo pipefail

SENTINEL_LOG="${SENTINEL_LOG:-$HOME/.sentinel/threats.jsonl}"

if [[ ! -f "$SENTINEL_LOG" ]]; then
  echo "No threats logged yet. Log file: $SENTINEL_LOG"
  exit 0
fi

show_entries() {
  local entries="$1"
  if [[ -z "$entries" ]]; then
    echo "No matching entries."
    return
  fi

  echo "$entries" | while IFS= read -r line; do
    ts=$(echo "$line" | grep -oP '"timestamp":"[^"]*"' | cut -d'"' -f4)
    dir=$(echo "$line" | grep -oP '"direction":"[^"]*"' | cut -d'"' -f4)
    sev=$(echo "$line" | grep -oP '"severity":"[^"]*"' | cut -d'"' -f4)
    cats=$(echo "$line" | grep -oP '"categories":"[^"]*"' | cut -d'"' -f4)
    count=$(echo "$line" | grep -oP '"threat_count":[0-9]*' | cut -d: -f2)

    case "$sev" in
      CRITICAL) EMOJI="🔴" ;;
      HIGH)     EMOJI="🟠" ;;
      WARNING)  EMOJI="🟡" ;;
      *)        EMOJI="⚪" ;;
    esac

    printf "%s %s %-8s [%-6s] %-30s threats: %s\n" "$EMOJI" "$ts" "$sev" "$dir" "$cats" "${count:-?}"
  done
}

case "${1:-}" in
  --last)
    N="${2:-10}"
    entries=$(tail -n "$N" "$SENTINEL_LOG")
    echo "=== Last $N entries ==="
    show_entries "$entries"
    ;;

  --severity)
    SEV="${2:-CRITICAL}"
    entries=$(grep "\"severity\":\"$SEV\"" "$SENTINEL_LOG" || true)
    echo "=== Entries with severity: $SEV ==="
    show_entries "$entries"
    ;;

  --today)
    TODAY=$(date -u +%Y-%m-%d)
    entries=$(grep "$TODAY" "$SENTINEL_LOG" || true)
    echo "=== Today's entries ($TODAY) ==="
    show_entries "$entries"
    ;;

  --stats)
    TOTAL=$(wc -l < "$SENTINEL_LOG")
    CRITICAL=$(grep -c '"severity":"CRITICAL"' "$SENTINEL_LOG" 2>/dev/null || echo 0)
    HIGH=$(grep -c '"severity":"HIGH"' "$SENTINEL_LOG" 2>/dev/null || echo 0)
    WARNING=$(grep -c '"severity":"WARNING"' "$SENTINEL_LOG" 2>/dev/null || echo 0)
    INPUT_COUNT=$(grep -c '"direction":"input"' "$SENTINEL_LOG" 2>/dev/null || echo 0)
    OUTPUT_COUNT=$(grep -c '"direction":"output"' "$SENTINEL_LOG" 2>/dev/null || echo 0)

    echo "=== Claw Sentinel Statistics ==="
    echo ""
    echo "Total threats logged:  $TOTAL"
    echo ""
    echo "By severity:"
    echo "  🔴 CRITICAL: $CRITICAL"
    echo "  🟠 HIGH:     $HIGH"
    echo "  🟡 WARNING:  $WARNING"
    echo ""
    echo "By direction:"
    echo "  ← Input:    $INPUT_COUNT"
    echo "  → Output:   $OUTPUT_COUNT"
    echo ""
    echo "Log file: $SENTINEL_LOG"
    echo "Log size: $(du -h "$SENTINEL_LOG" | cut -f1)"
    ;;

  --clear)
    echo "This will permanently delete all logged threats."
    read -p "Are you sure? (yes/no): " confirm
    if [[ "$confirm" == "yes" ]]; then
      > "$SENTINEL_LOG"
      echo "✅ Log cleared."
    else
      echo "Cancelled."
    fi
    ;;

  *)
    entries=$(tail -n 10 "$SENTINEL_LOG")
    echo "=== Last 10 entries ==="
    show_entries "$entries"
    echo ""
    echo "Options: --last N | --severity LEVEL | --today | --stats | --clear"
    ;;
esac
