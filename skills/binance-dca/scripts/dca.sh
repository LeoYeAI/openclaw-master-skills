#!/usr/bin/env bash
# Binance DCA (Dollar-Cost Averaging) Tool
# Requires: BINANCE_API_KEY, BINANCE_SECRET_KEY env vars
# Usage: dca.sh <action> [options]
#
# Actions:
#   buy       - Execute a DCA buy order
#   plan      - Show DCA plan projection
#   history   - Show recent DCA order history
#   price     - Get current price for a pair
#   balance   - Show account balance for an asset
#
# No personal data is stored. All credentials via env vars only.

set -euo pipefail

BASE_URL="${BINANCE_BASE_URL:-https://api.binance.com}"
RECV_WINDOW="${BINANCE_RECV_WINDOW:-5000}"

# --- Helpers ---

die() { echo "ERROR: $*" >&2; exit 1; }

check_keys() {
  [[ -n "${BINANCE_API_KEY:-}" ]] || die "BINANCE_API_KEY not set"
  [[ -n "${BINANCE_SECRET_KEY:-}" ]] || die "BINANCE_SECRET_KEY not set"
}

timestamp() { echo $(($(date +%s) * 1000)); }

sign() {
  local query="$1"
  echo -n "$query" | openssl dgst -sha256 -hmac "$BINANCE_SECRET_KEY" | sed 's/^.* //'
}

api_public() {
  local endpoint="$1" query="${2:-}"
  curl -sf "${BASE_URL}${endpoint}?${query}" 2>/dev/null || die "API request failed: ${endpoint}"
}

api_signed() {
  local method="$1" endpoint="$2" query="${3:-}"
  check_keys
  local ts
  ts=$(timestamp)
  query="${query:+${query}&}recvWindow=${RECV_WINDOW}&timestamp=${ts}"
  local sig
  sig=$(sign "$query")
  query="${query}&signature=${sig}"

  if [[ "$method" == "GET" ]]; then
    curl -sf -H "X-MBX-APIKEY: ${BINANCE_API_KEY}" \
      "${BASE_URL}${endpoint}?${query}" 2>/dev/null || die "Signed API request failed: ${endpoint}"
  else
    curl -sf -X "$method" -H "X-MBX-APIKEY: ${BINANCE_API_KEY}" \
      -d "$query" "${BASE_URL}${endpoint}" 2>/dev/null || die "Signed API request failed: ${endpoint}"
  fi
}

# --- Actions ---

action_price() {
  local symbol="${1:-BTCUSDT}"
  symbol=$(echo "$symbol" | tr '[:lower:]' '[:upper:]')
  local resp
  resp=$(api_public "/api/v3/ticker/price" "symbol=${symbol}")
  local price
  price=$(echo "$resp" | grep -o '"price":"[^"]*"' | head -1 | cut -d'"' -f4)
  echo "${symbol} = ${price}"
}

action_balance() {
  local asset="${1:-USDT}"
  asset=$(echo "$asset" | tr '[:lower:]' '[:upper:]')
  local resp
  resp=$(api_signed "GET" "/api/v3/account")
  local free locked
  free=$(echo "$resp" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for b in data.get('balances', []):
    if b['asset'] == '${asset}':
        print(b['free'])
        break
else:
    print('0.00000000')
" 2>/dev/null || echo "parse error")
  locked=$(echo "$resp" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for b in data.get('balances', []):
    if b['asset'] == '${asset}':
        print(b['locked'])
        break
else:
    print('0.00000000')
" 2>/dev/null || echo "parse error")
  echo "${asset}: free=${free}, locked=${locked}"
}

action_buy() {
  local symbol="${1:-BTCUSDT}" amount="${2:-}" type="${3:-MARKET}"
  symbol=$(echo "$symbol" | tr '[:lower:]' '[:upper:]')
  type=$(echo "$type" | tr '[:lower:]' '[:upper:]')

  [[ -n "$amount" ]] || die "Usage: dca.sh buy <SYMBOL> <QUOTE_AMOUNT> [MARKET|LIMIT]"

  # Validate amount is a number
  [[ "$amount" =~ ^[0-9]+\.?[0-9]*$ ]] || die "Amount must be a number, got: ${amount}"

  echo "Placing ${type} buy: ${symbol} for ${amount} USDT..."

  local query="symbol=${symbol}&side=BUY&type=${type}&quoteOrderQty=${amount}"

  if [[ "$type" == "LIMIT" ]]; then
    local price="${4:-}"
    [[ -n "$price" ]] || die "LIMIT orders require a price: dca.sh buy <SYMBOL> <AMOUNT> LIMIT <PRICE>"
    query="symbol=${symbol}&side=BUY&type=LIMIT&timeInForce=GTC&quoteOrderQty=${amount}&price=${price}"
  fi

  local resp
  resp=$(api_signed "POST" "/api/v3/order" "$query")

  # Parse response
  local status order_id filled_qty
  status=$(echo "$resp" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
  order_id=$(echo "$resp" | grep -o '"orderId":[0-9]*' | head -1 | cut -d: -f2)
  filled_qty=$(echo "$resp" | grep -o '"executedQty":"[^"]*"' | head -1 | cut -d'"' -f4)

  if [[ -n "$status" ]]; then
    echo "Order #${order_id}: ${status}"
    echo "Filled: ${filled_qty} ${symbol%%USDT*}"
  else
    echo "Response: ${resp}"
  fi
}

action_history() {
  local symbol="${1:-BTCUSDT}" limit="${2:-10}"
  symbol=$(echo "$symbol" | tr '[:lower:]' '[:upper:]')

  local resp
  resp=$(api_signed "GET" "/api/v3/myTrades" "symbol=${symbol}&limit=${limit}")

  echo "Last ${limit} trades for ${symbol}:"
  echo "---"
  echo "$resp" | python3 -c "
import sys, json
trades = json.load(sys.stdin)
for t in trades:
    side = 'BUY' if t.get('isBuyer') else 'SELL'
    print(f\"{t['time']//1000} | {side} | qty={t['qty']} | price={t['price']} | fee={t['commission']} {t['commissionAsset']}\")
if not trades:
    print('No trades found.')
" 2>/dev/null || echo "$resp"
}

action_plan() {
  local amount="${1:-50}" frequency="${2:-7}" periods="${3:-12}" symbol="${4:-BTCUSDT}"
  symbol=$(echo "$symbol" | tr '[:lower:]' '[:upper:]')

  # Get current price
  local price_resp price
  price_resp=$(api_public "/api/v3/ticker/price" "symbol=${symbol}")
  price=$(echo "$price_resp" | grep -o '"price":"[^"]*"' | head -1 | cut -d'"' -f4)

  echo "DCA Plan: ${symbol}"
  echo "=========================="
  echo "Buy amount:  \$${amount} per buy"
  echo "Frequency:   every ${frequency} days"
  echo "Duration:    ${periods} buys"
  echo "Current:     ${price}"
  echo "=========================="

  python3 -c "
amount = float('${amount}')
periods = int('${periods}')
freq = int('${frequency}')
price = float('${price}')

total_invested = amount * periods
btc_at_current = total_invested / price
total_days = freq * periods

print(f'Total invest:  \${total_invested:,.2f}')
print(f'At cur. price: {btc_at_current:.8f} ${symbol%%USDT*}')
print(f'Time span:     {total_days} days (~{total_days/30:.1f} months)')
print()
print('Scenario Analysis (if avg price over period is):')
for pct in [-30, -20, -10, 0, 10, 20, 50, 100]:
    avg = price * (1 + pct/100)
    coins = total_invested / avg
    value = coins * price * (1 + pct/100)
    pnl = value - total_invested
    pnl_pct = (pnl / total_invested) * 100
    sign = '+' if pnl >= 0 else ''
    print(f'  {pct:+4d}% -> avg \${avg:>10,.2f} -> {coins:.8f} BTC -> PnL: {sign}\${pnl:>10,.2f} ({sign}{pnl_pct:.1f}%)')
" 2>/dev/null || die "Python3 required for plan calculations"
}

# --- Main ---

action="${1:-help}"
shift 2>/dev/null || true

case "$action" in
  price)   action_price "$@" ;;
  balance) action_balance "$@" ;;
  buy)     action_buy "$@" ;;
  history) action_history "$@" ;;
  plan)    action_plan "$@" ;;
  *)
    echo "Binance DCA Tool"
    echo ""
    echo "Usage: dca.sh <action> [options]"
    echo ""
    echo "Actions:"
    echo "  price   [SYMBOL]                    - Get current price (default: BTCUSDT)"
    echo "  balance [ASSET]                     - Check balance (default: USDT)"
    echo "  buy     <SYMBOL> <AMOUNT> [TYPE]    - Place DCA buy order"
    echo "  history [SYMBOL] [LIMIT]            - Recent trade history"
    echo "  plan    [AMT] [FREQ_DAYS] [BUYS] [SYMBOL] - DCA projection"
    echo ""
    echo "Environment:"
    echo "  BINANCE_API_KEY     - Your Binance API key"
    echo "  BINANCE_SECRET_KEY  - Your Binance secret key"
    echo "  BINANCE_BASE_URL    - API base URL (default: https://api.binance.com)"
    ;;
esac
