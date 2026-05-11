#!/bin/bash
# ClawLaunch CLI wrapper
# Usage: clawlaunch.sh <command> [args]
#
# Launch and trade AI agent tokens on ClawLaunch bonding curve (Base).
# Requires: curl, jq
#
# Configuration:
#   Option 1: Set CLAWLAUNCH_API_KEY environment variable
#   Option 2: Create ~/.clawdbot/skills/clawlaunch/config.json with apiKey

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${HOME}/.clawdbot/skills/clawlaunch/config.json"

usage() {
  cat <<EOF
ClawLaunch CLI - AI Agent Token Launchpad on Base

Usage: clawlaunch.sh <command> [options]

Commands:
  tokens [--limit N]              List all tokens (default limit: 50)
  quote <token> <action> <amount> Get price quote (action: buy|sell)
  launch <name> <symbol>          Launch a new token
  buy <token> <wallet> <eth>      Get buy transaction calldata
  sell <token> <wallet> [amount]  Get sell transaction calldata (omit amount to sell all)

Options:
  --help, -h                      Show this help message
  --json                          Output raw JSON (default: formatted)

Examples:
  clawlaunch.sh tokens --limit 10
  clawlaunch.sh quote 0x1234... buy 100000000000000000
  clawlaunch.sh launch "MoonCat" "MCAT"
  clawlaunch.sh buy 0x1234... 0x5678... 500000000000000000
  clawlaunch.sh sell 0x1234... 0x5678...          # sell all
  clawlaunch.sh sell 0x1234... 0x5678... 1000000000000000000

Fee Structure:
  Total fee: 1% (fixed)
  - Platform: 0.05%
  - Creator: 0.95% (you keep this!)

Rate Limits:
  - /agent/launch: 10/hour
  - /token/buy|sell: 50/hour
  - /token/quote|/tokens: 100/min

More info: https://www.clawlaunch.fun
EOF
}

# Handle help early (before API key check)
case "${1:-}" in
  -h|--help|help|"")
    usage
    exit 0
    ;;
esac

# Load config from file or environment
if [ -f "$CONFIG_FILE" ]; then
  API_KEY=$(jq -r '.apiKey // empty' "$CONFIG_FILE" 2>/dev/null || echo "")
  API_URL=$(jq -r '.apiUrl // "https://www.clawlaunch.fun/api/v1"' "$CONFIG_FILE" 2>/dev/null)
else
  API_KEY="${CLAWLAUNCH_API_KEY:-}"
  API_URL="${CLAWLAUNCH_URL:-https://www.clawlaunch.fun/api/v1}"
fi

# Validate API key exists
if [ -z "$API_KEY" ]; then
  echo "Error: No API key configured" >&2
  echo "" >&2
  echo "Configure via one of:" >&2
  echo "  1. Set CLAWLAUNCH_API_KEY environment variable" >&2
  echo "  2. Create $CONFIG_FILE with:" >&2
  echo '     {"apiKey": "YOUR_KEY_HERE"}' >&2
  exit 2
fi

# Check dependencies
command -v curl >/dev/null 2>&1 || { echo "Error: curl is required" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "Error: jq is required" >&2; exit 1; }

# API call helper
api_call() {
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"

  if [ "$method" = "GET" ]; then
    curl -s -X GET "${API_URL}${endpoint}" \
      -H "x-api-key: $API_KEY"
  else
    curl -s -X POST "${API_URL}${endpoint}" \
      -H "Content-Type: application/json" \
      -H "x-api-key: $API_KEY" \
      -d "$data"
  fi
}

# Command: tokens
cmd_tokens() {
  local limit="${1:-50}"
  api_call GET "/tokens?limit=${limit}"
}

# Command: quote
cmd_quote() {
  local token="$1"
  local action="$2"
  local amount="$3"

  if [[ ! "$action" =~ ^(buy|sell)$ ]]; then
    echo "Error: action must be 'buy' or 'sell'" >&2
    exit 1
  fi

  api_call POST "/token/quote" "{\"tokenAddress\":\"$token\",\"action\":\"$action\",\"amount\":\"$amount\"}"
}

# Command: launch
cmd_launch() {
  local name="$1"
  local symbol="$2"
  local agent_id="${3:-clawlaunch-cli-$$}"

  # Validate symbol format
  if [[ ! "$symbol" =~ ^[A-Z0-9]+$ ]]; then
    echo "Error: Symbol must be uppercase letters and numbers only (e.g., MCAT, AI123)" >&2
    exit 1
  fi

  if [ ${#symbol} -gt 8 ]; then
    echo "Error: Symbol must be 8 characters or less" >&2
    exit 1
  fi

  if [ ${#name} -gt 32 ]; then
    echo "Error: Name must be 32 characters or less" >&2
    exit 1
  fi

  api_call POST "/agent/launch" "{\"agentId\":\"$agent_id\",\"name\":\"$name\",\"symbol\":\"$symbol\"}"
}

# Command: buy
cmd_buy() {
  local token="$1"
  local wallet="$2"
  local eth_amount="$3"
  local slippage="${4:-200}"

  api_call POST "/token/buy" "{\"tokenAddress\":\"$token\",\"walletAddress\":\"$wallet\",\"ethAmount\":\"$eth_amount\",\"slippageBps\":$slippage}"
}

# Command: sell
cmd_sell() {
  local token="$1"
  local wallet="$2"
  local amount="${3:-}"
  local slippage="${4:-200}"

  if [ -z "$amount" ]; then
    # Sell all
    api_call POST "/token/sell" "{\"tokenAddress\":\"$token\",\"walletAddress\":\"$wallet\",\"sellAll\":true,\"slippageBps\":$slippage}"
  else
    api_call POST "/token/sell" "{\"tokenAddress\":\"$token\",\"walletAddress\":\"$wallet\",\"tokenAmount\":\"$amount\",\"slippageBps\":$slippage}"
  fi
}

# Parse command line
COMMAND="${1:-}"
shift || true

case "$COMMAND" in
  tokens)
    limit="50"
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --limit)
          limit="$2"
          shift 2
          ;;
        *)
          shift
          ;;
      esac
    done
    cmd_tokens "$limit"
    ;;
  quote)
    if [ $# -lt 3 ]; then
      echo "Usage: clawlaunch.sh quote <token_address> <action> <amount>" >&2
      echo "  action: buy or sell" >&2
      echo "  amount: wei (e.g., 100000000000000000 = 0.1 ETH)" >&2
      exit 1
    fi
    cmd_quote "$1" "$2" "$3"
    ;;
  launch)
    if [ $# -lt 2 ]; then
      echo "Usage: clawlaunch.sh launch <name> <symbol> [agent_id]" >&2
      echo "  name: Token name (1-32 chars)" >&2
      echo "  symbol: Token symbol (1-8 chars, A-Z0-9)" >&2
      exit 1
    fi
    cmd_launch "$@"
    ;;
  buy)
    if [ $# -lt 3 ]; then
      echo "Usage: clawlaunch.sh buy <token_address> <wallet_address> <eth_amount> [slippage_bps]" >&2
      echo "  eth_amount: wei (e.g., 500000000000000000 = 0.5 ETH)" >&2
      echo "  slippage_bps: optional, default 200 (2%)" >&2
      exit 1
    fi
    cmd_buy "$@"
    ;;
  sell)
    if [ $# -lt 2 ]; then
      echo "Usage: clawlaunch.sh sell <token_address> <wallet_address> [token_amount] [slippage_bps]" >&2
      echo "  token_amount: wei (omit to sell all)" >&2
      echo "  slippage_bps: optional, default 200 (2%)" >&2
      exit 1
    fi
    cmd_sell "$@"
    ;;
  -h|--help|help)
    usage
    ;;
  "")
    usage
    exit 0
    ;;
  *)
    echo "Error: Unknown command '$COMMAND'" >&2
    echo "Run 'clawlaunch.sh --help' for usage" >&2
    exit 1
    ;;
esac
