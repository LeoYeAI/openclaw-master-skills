#!/bin/bash
# analytics.sh — Pull mining stats from refinORE API
# Usage: analytics.sh <command> <api_url> <api_key> [limit]
# Commands: history, pnl, round, apr, rewards, staking
set -euo pipefail

CMD="${1:?Usage: analytics.sh <history|pnl|round|apr|rewards|staking> <api_url> <api_key> [limit]}"
API_URL="${2:-${REFINORE_API_URL:-https://automine.refinore.com/api}}"
API_KEY="${3:-${REFINORE_API_KEY:-}}"
LIMIT="${4:-50}"

if [ -z "$API_KEY" ]; then
  echo "❌ No credentials."
  echo "Usage: analytics.sh <command> <api_url> <api_key>"
  exit 1
fi

AUTH_HEADER="x-api-key: $API_KEY"

# Helper: get wallet address
get_wallet() {
  curl -s "$API_URL/account/me" -H "$AUTH_HEADER" | \
    python3 -c "import sys,json; print(json.load(sys.stdin).get('wallet_address',''))" 2>/dev/null
}

case "$CMD" in
  history)
    echo "=== Mining History (last $LIMIT) ==="
    curl -s "$API_URL/mining/history?limit=$LIMIT" -H "$AUTH_HEADER" | python3 -m json.tool 2>/dev/null
    ;;
  pnl)
    echo "=== Session P&L ==="
    RESPONSE=$(curl -s "$API_URL/mining/session" -H "$AUTH_HEADER")
    echo "$RESPONSE" | python3 -c "
import json,sys
d=json.load(sys.stdin)
s = d.get('session', d)
if 'hasActiveSession' in d and not d['hasActiveSession']:
  print('No active session.')
else:
  rounds = s.get('total_rounds', 0)
  wins = s.get('total_wins', 0)
  losses = s.get('total_losses', 0)
  deployed = float(s.get('total_sol_deployed', 0) or 0)
  won = float(s.get('total_sol_won', 0) or 0)
  rate = (wins/rounds*100) if rounds > 0 else 0
  print(f'Rounds: {rounds} | Wins: {wins} | Losses: {losses} | Win Rate: {rate:.1f}%')
  print(f'SOL Deployed: {deployed:.6f} | SOL Won: {won:.6f}')
  print(f'Net P&L: {won - deployed:.6f} SOL')
" 2>/dev/null
    ;;
  round)
    echo "=== Current Round ==="
    curl -s "$API_URL/rounds/current" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f'Round: {d.get(\"round_number\")}')
print(f'Deployed: {d.get(\"total_deployed_sol\",0):.4f} SOL')
print(f'Motherlode: {d.get(\"motherlode_formatted\",0)} ORE (hit: {d.get(\"motherlode_hit\",False)})')
" 2>/dev/null
    ;;
  apr)
    echo "=== Staking APR ==="
    curl -s "$API_URL/refinore-apr" | python3 -m json.tool 2>/dev/null
    ;;
  rewards)
    echo "=== Mining Rewards ==="
    WALLET=$(get_wallet)
    if [ -z "$WALLET" ]; then echo "❌ Could not get wallet"; exit 1; fi
    curl -s "$API_URL/rewards?wallet=$WALLET" -H "$AUTH_HEADER" | python3 -m json.tool 2>/dev/null
    ;;
  staking)
    echo "=== Staking Info ==="
    WALLET=$(get_wallet)
    if [ -z "$WALLET" ]; then echo "❌ Could not get wallet"; exit 1; fi
    curl -s "$API_URL/staking/info?wallet=$WALLET" -H "$AUTH_HEADER" | python3 -m json.tool 2>/dev/null
    ;;
  *)
    echo "Unknown command: $CMD"
    echo "Available: history, pnl, round, apr, rewards, staking"
    exit 1
    ;;
esac
