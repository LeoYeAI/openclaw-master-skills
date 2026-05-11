#!/bin/bash
# token-counter.sh — Estimate system prompt token overhead from workspace files
# Usage: bash token-counter.sh [workspace-path]
# Counts chars in bootstrap files that get injected into every request

set -euo pipefail

WORKSPACE="${1:-$HOME/.openclaw/workspace}"
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     System Prompt Token Estimator        ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

# Bootstrap files that get injected into system prompt
BOOTSTRAP_FILES=(
  "AGENTS.md"
  "SOUL.md"
  "TOOLS.md"
  "IDENTITY.md"
  "USER.md"
  "HEARTBEAT.md"
  "BOOTSTRAP.md"
  "system.md"
)

TOTAL_CHARS=0
TOTAL_TOKENS=0

echo -e "${BOLD}Workspace Bootstrap Files:${NC}"
echo ""
printf "  %-25s %10s %12s %s\n" "FILE" "CHARS" "~TOKENS" "STATUS"
printf "  %-25s %10s %12s %s\n" "----" "-----" "-------" "------"

for f in "${BOOTSTRAP_FILES[@]}"; do
  FILEPATH="$WORKSPACE/$f"
  if [ -f "$FILEPATH" ]; then
    CHARS=$(wc -c < "$FILEPATH")
    # Rough estimate: 1 token ≈ 4 chars for English text
    TOKENS=$((CHARS / 4))
    TOTAL_CHARS=$((TOTAL_CHARS + CHARS))
    TOTAL_TOKENS=$((TOTAL_TOKENS + TOKENS))
    
    if [ "$TOKENS" -gt 2000 ]; then
      STATUS="${RED}LARGE — consider trimming${NC}"
    elif [ "$TOKENS" -gt 500 ]; then
      STATUS="${YELLOW}moderate${NC}"
    else
      STATUS="${GREEN}ok${NC}"
    fi
    
    printf "  %-25s %10s %12s " "$f" "$CHARS" "~$TOKENS"
    echo -e "$STATUS"
  else
    printf "  %-25s %10s %12s " "$f" "-" "-"
    echo -e "${GREEN}not present${NC}"
  fi
done

echo ""
echo -e "${BOLD}Subtotal (workspace files):${NC} ~$TOTAL_TOKENS tokens ($TOTAL_CHARS chars)"

# Check for skill files that might be loaded
echo ""
echo -e "${BOLD}Skill Directories:${NC}"
SKILL_DIR="$WORKSPACE/skills"
if [ -d "$SKILL_DIR" ]; then
  for skill in "$SKILL_DIR"/*/; do
    if [ -f "${skill}SKILL.md" ]; then
      CHARS=$(wc -c < "${skill}SKILL.md")
      TOKENS=$((CHARS / 4))
      SKILL_NAME=$(basename "$skill")
      printf "  %-25s %10s %12s " "$SKILL_NAME/SKILL.md" "$CHARS" "~$TOKENS"
      echo -e "${CYAN}loaded on activation${NC}"
    fi
  done
else
  echo "  No skills directory found"
fi

# Estimate total system prompt
echo ""
echo -e "${BOLD}── Overhead Estimate ──${NC}"
echo ""

# OpenClaw base system prompt (instructions, tool schemas, etc.)
BASE_PROMPT_TOKENS=65000
TOOL_SCHEMA_TOKENS=7000

GRAND_TOTAL=$((BASE_PROMPT_TOKENS + TOOL_SCHEMA_TOKENS + TOTAL_TOKENS))

echo "  OpenClaw base instructions:  ~${BASE_PROMPT_TOKENS} tokens"
echo "  Tool schemas (~20 tools):    ~${TOOL_SCHEMA_TOKENS} tokens"
echo "  Your workspace files:        ~${TOTAL_TOKENS} tokens"
echo "  ─────────────────────────────────────"
echo -e "  ${BOLD}Estimated total overhead:     ~${GRAND_TOTAL} tokens${NC}"
echo ""

# Cost per request at different tiers
echo -e "${BOLD}── Cost Per Request (overhead only) ──${NC}"
echo ""

node -e "
const tokens = $GRAND_TOTAL;
const tiers = [
  { name: 'Free (OpenRouter)', inputPerM: 0, outputPerM: 0 },
  { name: 'DeepSeek V3.2',     inputPerM: 0.27, outputPerM: 1.10 },
  { name: 'MiniMax M2.5',      inputPerM: 0.50, outputPerM: 1.10 },
  { name: 'Haiku 4.5',         inputPerM: 0.80, outputPerM: 4.00 },
  { name: 'Sonnet 4.6',        inputPerM: 3.00, outputPerM: 15.00 },
  { name: 'Opus 4.6',          inputPerM: 15.00, outputPerM: 75.00 },
];

for (const t of tiers) {
  const inputCost = (tokens / 1000000) * t.inputPerM;
  const outputEst = (500 / 1000000) * t.outputPerM; // ~500 token avg response
  const total = inputCost + outputEst;
  const monthly = total * 50 * 30;
  console.log('  ' + t.name.padEnd(22) + ' \$' + total.toFixed(4) + '/req → \$' + monthly.toFixed(0) + '/month (50 req/day)');
}
" 2>/dev/null

echo ""
echo -e "${BOLD}── Trim Opportunities ──${NC}"
echo ""

# Check for specific trimming opportunities
if [ -f "$WORKSPACE/BOOTSTRAP.md" ]; then
  BS_TOKENS=$(($(wc -c < "$WORKSPACE/BOOTSTRAP.md") / 4))
  echo -e "  ${RED}⚠ BOOTSTRAP.md still present (~$BS_TOKENS tokens). Delete after setup.${NC}"
fi

for f in "${BOOTSTRAP_FILES[@]}"; do
  FILEPATH="$WORKSPACE/$f"
  if [ -f "$FILEPATH" ]; then
    TOKENS=$(($(wc -c < "$FILEPATH") / 4))
    if [ "$TOKENS" -gt 2000 ]; then
      echo -e "  ${YELLOW}⚠ $f is large (~$TOKENS tokens). Review for content that could move to a skill.${NC}"
    fi
  fi
done

echo ""
echo -e "${BOLD}Done.${NC}"
