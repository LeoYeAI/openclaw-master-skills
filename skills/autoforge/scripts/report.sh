#!/bin/bash
# AutoForge Report — Live progress updates with Unicode bars
# Supports: Telegram, Discord, Slack, stdout (ANSI fallback)
#
# Usage: ./report.sh [results.tsv] [skill-name] [--final] [--json]
#
# Environment:
#   AF_CHANNEL   — Messaging channel (telegram, discord, slack). Default: telegram
#   AF_CHAT_ID   — Chat/group ID for delivery. If unset, prints to stdout.
#   AF_TOPIC_ID  — Thread/topic ID within the chat (optional).
#
# Examples:
#   AF_CHAT_ID="-100123456" AF_TOPIC_ID="2211" ./report.sh results.tsv "My Skill"
#   ./report.sh results.tsv "My Skill" --final
#   ./report.sh results.tsv "My Skill" --json

set -euo pipefail

RESULTS_FILE="${1:-results.tsv}"
SKILL_NAME="${2:-Skill}"
shift 2 2>/dev/null || true

# Parse flags
FINAL_FLAG="false"
JSON_FLAG=""
for arg in "$@"; do
  case "$arg" in
    --final) FINAL_FLAG="true" ;;
    --json)  JSON_FLAG="yes" ;;
  esac
done

# Configuration from environment
CHANNEL="${AF_CHANNEL:-telegram}"
CHAT_ID="${AF_CHAT_ID:-}"
TOPIC_ID="${AF_TOPIC_ID:-}"

# --- Validation ---

if [ ! -f "$RESULTS_FILE" ]; then
  echo "Error: Results file not found: $RESULTS_FILE" >&2
  exit 1
fi

LINE_COUNT=$(tail -n +2 "$RESULTS_FILE" 2>/dev/null | wc -l | tr -d ' ')
if [ "$LINE_COUNT" -eq 0 ]; then
  echo "Error: No data rows in $RESULTS_FILE" >&2
  exit 1
fi

# --- Data Extraction ---

TOTAL=$(tail -n +2 "$RESULTS_FILE" | wc -l | tr -d ' ')
KEEP=$(tail -n +2 "$RESULTS_FILE" | awk -F'\t' '{s=$NF} s=="keep"||s=="best"||s=="improved"||s=="retained"||s=="baseline" {c++} END{print c+0}')
DISCARD=$(tail -n +2 "$RESULTS_FILE" | awk -F'\t' '$NF=="discard" {c++} END{print c+0}')
BEST=$(tail -n +2 "$RESULTS_FILE" | awk -F'\t' '{val=$3; gsub(/%/,"",val); if(val ~ /^[0-9.]+$/ && val+0>max+0)max=val} END{print max+0}')
BEST_ITER=$(tail -n +2 "$RESULTS_FILE" | awk -F'\t' -v best="$BEST" '{val=$3; gsub(/%/,"",val); if(val ~ /^[0-9.]+$/ && val+0==best+0){print NR; exit}}')
LAST_RATE=$(tail -n +2 "$RESULTS_FILE" | tail -1 | awk -F'\t' '{print $3}')
LAST_STATUS=$(tail -n +2 "$RESULTS_FILE" | tail -1 | awk -F'\t' '{print $NF}')

# --- JSON Output ---

if [ "$JSON_FLAG" = "yes" ]; then
  # Collect iteration data as JSON array
  ITER_JSON=$(tail -n +2 "$RESULTS_FILE" | awk -F'\t' '
    BEGIN { printf "[" }
    NR>1 { printf "," }
    {
      gsub(/"/, "\\\"", $2);
      gsub(/"/, "\\\"", $4);
      gsub(/%/, "", $3);
      printf "{\"iteration\":%s,\"summary\":\"%s\",\"pass_rate\":%s,\"change\":\"%s\",\"status\":\"%s\"}", $1, $2, ($3 ~ /^[0-9.]+$/ ? $3 : "0"), $4, $5
    }
    END { printf "]" }
  ')

  cat <<EOF
{
  "skill": "${SKILL_NAME}",
  "total_iterations": ${TOTAL},
  "kept": ${KEEP},
  "discarded": ${DISCARD},
  "best_pass_rate": ${BEST},
  "best_iteration": ${BEST_ITER:-0},
  "last_rate": "${LAST_RATE}",
  "last_status": "${LAST_STATUS}",
  "final": ${FINAL_FLAG},
  "iterations": ${ITER_JSON}
}
EOF
  exit 0
fi

# --- Build Unicode Bar Display ---

ITER_LINES=""
while IFS=$'\t' read -r iter summary rate change status; do
  rate_num="${rate//%/}"
  # Skip non-numeric rates (audit mode: PASS/FAIL)
  if ! echo "$rate_num" | grep -qE '^[0-9.]+$'; then
    rate_num="0"
  fi

  # Build progress bar (pure bash)
  filled=$((rate_num / 5))
  empty=$((20 - filled))
  bar=""
  for ((b=0; b<filled; b++)); do bar="${bar}█"; done
  for ((b=0; b<empty; b++)); do bar="${bar}░"; done

  case "$status" in
    keep|improved|retained|best) icon="✅" ;;
    discard)  icon="❌" ;;
    crash)    icon="💥" ;;
    baseline) icon="📍" ;;
    *)        icon="🔹" ;;
  esac

  ITER_LINES="${ITER_LINES}
${icon} Iter ${iter}  ${bar}  ${rate}"
done < <(tail -n +2 "$RESULTS_FILE")

# --- Build Message ---

if [ "$FINAL_FLAG" = "true" ]; then
  case "$LAST_STATUS" in
    improved|best) CONCLUSION="✅ Loop converged — improvement found" ;;
    retained)      CONCLUSION="➡️ Loop stable — no further improvement potential" ;;
    discard)       CONCLUSION="⚠️ Last attempt discarded — best state from Iter ${BEST_ITER}" ;;
    *)             CONCLUSION="🏁 Loop finished" ;;
  esac

  # Channel-specific formatting
  case "$CHANNEL" in
    discord)
      # Discord: no markdown in code blocks, simpler formatting
      MSG="📊 **AutoForge complete: ${SKILL_NAME}**
${ITER_LINES}

──────────────────────
Iterations: ${TOTAL}  ✅ Keep: ${KEEP}  ❌ Discard: ${DISCARD}
🏆 Best pass rate: ${BEST}% (Iter ${BEST_ITER})

${CONCLUSION}

_In --dry-run mode: No changes written. Approve for --live?_"
      ;;
    *)
      MSG="📊 *AutoForge complete: ${SKILL_NAME}*
${ITER_LINES}

──────────────────────
Iterations: ${TOTAL}  ✅ Keep: ${KEEP}  ❌ Discard: ${DISCARD}
🏆 Best pass rate: ${BEST}% (Iter ${BEST_ITER})

${CONCLUSION}

_In --dry-run mode: No changes written. Approve for --live?_"
      ;;
  esac
else
  case "$CHANNEL" in
    discord)
      MSG="📊 **AutoForge: ${SKILL_NAME}**
${ITER_LINES}

──────────────────────
Iterations: ${TOTAL}  ✅ Keep: ${KEEP}  ❌ Discard: ${DISCARD}
🏆 Best: ${BEST}%"
      ;;
    *)
      MSG="📊 *AutoForge: ${SKILL_NAME}*
${ITER_LINES}

──────────────────────
Iterations: ${TOTAL}  ✅ Keep: ${KEEP}  ❌ Discard: ${DISCARD}
🏆 Best: ${BEST}%"
      ;;
  esac
fi

# --- Deliver ---

if [ -n "$CHAT_ID" ] && command -v openclaw &>/dev/null; then
  # Build openclaw command
  CMD="openclaw message send --channel ${CHANNEL} --target ${CHAT_ID}"
  if [ -n "$TOPIC_ID" ]; then
    CMD="${CMD} --thread-id ${TOPIC_ID}"
  fi
  CMD="${CMD} --message"

  $CMD "$MSG"
else
  # Stdout fallback with ANSI colors
  if [ -t 1 ]; then
    # Terminal: add colors
    echo ""
    echo -e "\033[1;36m${MSG}\033[0m"
    echo ""
    if [ -z "$CHAT_ID" ]; then
      echo -e "\033[33mTip: Set AF_CHAT_ID to deliver reports to a channel.\033[0m"
    fi
    if ! command -v openclaw &>/dev/null; then
      echo -e "\033[33mTip: Install openclaw CLI for channel delivery.\033[0m"
    fi
  else
    # Piped: plain text
    echo "$MSG"
  fi
fi
