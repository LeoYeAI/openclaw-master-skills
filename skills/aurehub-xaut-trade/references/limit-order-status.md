# Limit Order Query

All commands below assume CWD is `$SCRIPTS_DIR` and env is sourced. Each Bash block must begin with:

```bash
source ~/.aurehub/.env
cd "$SCRIPTS_DIR"
```

> `--api-url` and `--chain-id` are omitted from examples below — the script reads defaults from `limit_order.uniswapx_api` and `networks.ethereum_mainnet.chain_id` in `~/.aurehub/config.yaml`.

## 1. Query a Single Order (by orderHash)

```bash
RESULT=$(node limit-order.js status \
  --order-hash "$ORDER_HASH")

STATUS=$(echo "$RESULT" | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).status")
```

## 2. List All Open Orders (by wallet address)

```bash
WALLET_ADDRESS=$(node swap.js address | node -p "JSON.parse(require('fs').readFileSync(0,'utf8')).address")
RESULT=$(node limit-order.js list \
  --wallet       "$WALLET_ADDRESS" \
  --order-status open)   # Optional: open / filled / expired / cancelled — omit to return all
```

Returns JSON: `{ address, total, orders: [{ orderHash, status, inputToken, inputAmount, outputToken, outputAmount, txHash, createdAt }] }`

## 3. Status Display

| status | Display |
|--------|---------|
| `open` | Order active; remaining time = deadline - current time |
| `filled` | Filled: show txHash and actual settled amounts (settledAmounts) |
| `expired` | Expired; can re-place the order |
| `cancelled` | Cancelled |
| `not_found` | orderHash does not exist or has been purged from the API (may be cleared after expiry) |

## 4. Error Handling

- API unreachable: prompt to check network, suggest retrying later
- `not_found`: suggest the orderHash may be wrong, or the order has expired and been purged
