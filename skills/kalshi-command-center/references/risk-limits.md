# Kalshi Command Center — Risk Limits Framework

Complete risk management documentation for Kalshi trading in the Command Center.

## Hard Limits

All hard limits are enforced by `_check_risk()` before order placement:

| Limit | Value | Enforced | Rationale |
|-------|-------|----------|-----------|
| Max single trade cost | $25.00 USD | On `buy_command()` | Prevents overallocation to single trade |
| Max position size | 100 contracts | On `buy_command()` | Prevents excessive leverage |
| Max daily loss | $50.00 USD | Via Kelly sizing (if available) | Portfolio protection |

## Trade Audit Logging

Every trade is logged to `~/.openclaw/logs/trades.jsonl` with full event history:

### Events Logged

1. **Trade Submitted** (`trade_submitted`)
   - Logged before API call
   - Fields: ticker, side, quantity, price_cents, cost_estimate/proceeds_estimate

2. **Trade Placed** (`trade_placed`)
   - Logged after successful API response
   - Fields: ticker, order_id, status (executed/resting/pending)

3. **Trade Failed** (`trade_failed`)
   - Logged on exception
   - Fields: ticker, error message (truncated to 200 chars)

4. **Trade Blocked** (`trade_blocked`)
   - Logged when risk check fails
   - Fields: ticker, side, quantity, price_cents, reason

### Example Log Entry

```json
{
  "timestamp": "2026-02-26T14:35:22.123456+00:00",
  "event": "trade_placed",
  "ticker": "ECON-INFL-2026",
  "side": "yes",
  "quantity": 10,
  "price_cents": 35,
  "cost_estimate": 3.50,
  "order_id": "order-123456",
  "status": "resting"
}
```

### Parsing Logs

```bash
# View last 20 trades
tail -20 ~/.openclaw/logs/trades.jsonl | python -m json.tool

# Count blocked trades
grep "trade_blocked" ~/.openclaw/logs/trades.jsonl | wc -l

# Sum total cost (requires jq)
grep "trade_placed" ~/.openclaw/logs/trades.jsonl \
  | jq '.cost_estimate // .proceeds_estimate' \
  | awk '{s+=$1} END {print "Total:", s}'
```

## Risk Validation Gates (Optional)

If `proactive.triggers.validate_risk` module is available, execute picks are additionally validated against:

- **Exposure Limit**: Total capital allocated to open positions
- **Drawdown Limit**: Realized loss since session start
- **VaR Limit**: Value at risk across portfolio
- **Correlation Limit**: Cross-market correlation penalty

## Pre-Trade Checklist

Before executing any trade:

1. **Check Portfolio**
   ```bash
   python kalshi_commands.py portfolio
   ```
   Review cash balance, existing positions, and P&L impact.

2. **Get Live Market Data**
   ```bash
   python kalshi_commands.py get TICKER
   ```
   Confirm order book has liquidity (non-zero bid/ask), spread is reasonable (<5%).

3. **Review Risk**
   - Cost: `quantity * price_cents / 100` ≤ $25.00
   - Quantity: ≤ 100 contracts
   - Daily loss: check logs for sum of losses

4. **Place Order**
   ```bash
   python kalshi_commands.py buy TICKER side quantity price
   ```

## Defensive Patterns

### Limit Order Strategy (Recommended)

Place bids/asks below/above current market to get better fills:

```bash
# Market: 35/37¢
# Bid at 36¢ to improve from 37¢ ask
python kalshi_commands.py buy ECON-INFL-2026 yes 10 36

# Market: 65/67¢ (NO side)
# Post ask at 62¢ to improve from 61¢ bid
python kalshi_commands.py sell ECON-INFL-2026 no 10 62
```

### Position Monitoring

Check open orders and positions frequently:

```bash
# List resting orders
python kalshi_commands.py orders

# Cancel if market moved unfavorably
python kalshi_commands.py cancel ORDER_ID
```

### Exit Strategy

Exit losing positions when:
- Daily loss exceeds $50 (hard stop)
- Position P&L falls below -20% for >2 days
- Market thesis invalidated by news

```bash
# Check current P&L
python kalshi_commands.py portfolio

# Sell position at current bid
python kalshi_commands.py get TICKER  # check bid
python kalshi_commands.py sell TICKER yes 10 BID_PRICE
```

## Risk Metrics

### Sharpe Ratio (Post-Trade Analysis)

```
Sharpe = (avg_return - risk_free_rate) / std_dev_return
```

For Kalshi prediction markets (discrete 0-100 events), estimate:
- `avg_return` = mean P&L per trade
- `std_dev_return` = std dev of P&L across trades
- `risk_free_rate` ≈ 0.04 (4% annual, ~0.01% daily)

### Maximum Drawdown

```
Max_DD = (peak_portfolio_value - trough_value) / peak_portfolio_value
```

From trade logs:

```python
import json
logs = [json.loads(l) for l in open("~/.openclaw/logs/trades.jsonl")]
gains = [l.get("pnl", 0) for l in logs if "pnl" in l]
peak = max(gains)
trough = min(gains)
max_dd = (peak - trough) / peak if peak > 0 else 0
print(f"Max Drawdown: {max_dd:.1%}")
```

## Bankruptcy Protection

To prevent account ruin:

1. **Hard Loss Limit**: Stop trading if cumulative daily loss ≥ $50
2. **Position Concentration**: No single trade >$25 (forces diversification)
3. **Quantity Cap**: ≤100 contracts (prevents over-leveraging low-price markets)
4. **Audit Logging**: Full trail of trades for post-mortems

## Kalshi API Error Handling

The Command Center classifies API errors and retries intelligently:

| Error Type | Retry? | Message | Action |
|------------|--------|---------|--------|
| Network timeout | ✅ Yes (2s backoff) | "Can't reach Kalshi API" | Wait and retry |
| 401/403 Auth | ❌ No | "Auth failed — check credentials" | Fix credentials in config |
| 429 Rate limit | ✅ Yes (2s backoff) | "Rate limited — try in a minute" | Back off, don't hammer API |
| Unknown | ❌ No | "Kalshi API error: {msg}" | Check logs, investigate |

## Debugging Risk Blocks

If trades are blocked:

1. **Check Cost Cap**
   ```
   blocked if: quantity * price_cents / 100 > $25.00
   ```
   Example: 30 contracts @ 90¢ = $27.00 ❌ (exceeds $25)

2. **Check Quantity Cap**
   ```
   blocked if: quantity > 100
   ```
   Example: 150 contracts ❌ (exceeds 100)

3. **Check Daily Loss**
   ```bash
   # Sum losses from today
   grep "$(date +%Y-%m-%d)" ~/.openclaw/logs/trades.jsonl \
     | grep "trade_placed" \
     | python -c "import json, sys; [print(json.loads(l).get('pnl', 0)) for l in sys.stdin]" \
     | awk '{s+=$1} END {if (s < -50) print "DAILY LOSS LIMIT EXCEEDED"}'
   ```

## Risk Optimization

### Position Sizing via Kelly Criterion

If available, `execute` command uses Kelly sizing:

```
f* = (p × b − q) / b

where:
  f* = fraction of bankroll to bet
  p = estimated probability (decimal)
  q = 1 - p
  b = decimal odds (price_cents / 100 - 1)
```

Example: 60% confidence on 35¢ market
```
b = 35/100 - 1 = -0.65 (unfavorable)
f* = (0.6 × -0.65 - 0.4) / -0.65 = 0.25 → bet 25% of bankroll
```

Kelly is capped to prevent over-leverage:
- Max 10% of bankroll per trade (fractional Kelly: f*/10)
- Min 1 contract (avoids micro-positions)
- Halved if daily loss approaching limit

## Compliance & Audit

### Monthly Risk Review

```bash
python -c "
import json
from pathlib import Path
from datetime import datetime

logs = Path.home() / '.openclaw' / 'logs' / 'trades.jsonl'
entries = [json.loads(l) for l in open(logs)]

# Filter last month
month_start = datetime(2026, 2, 1)
month_entries = [e for e in entries if datetime.fromisoformat(e['timestamp']) >= month_start]

# Stats
total_trades = len([e for e in month_entries if e['event'] in ('trade_placed', 'buy_placed', 'sell_placed')])
total_blocked = len([e for e in month_entries if e['event'] == 'trade_blocked'])
total_cost = sum([e.get('cost_estimate', 0) for e in month_entries if e['event'].endswith('_placed')])

print(f'Month: {total_trades} trades, {total_blocked} blocked, ${total_cost:.2f} invested')
"
```

## References

- **Kalshi API Docs**: https://kalshi.com/api
- **Kelly Criterion**: https://en.wikipedia.org/wiki/Kelly_criterion
- **Position Sizing**: https://www.investopedia.com/terms/p/positionsizing.asp
