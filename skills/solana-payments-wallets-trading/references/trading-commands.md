# Trading Commands Reference

## Browse Tokens

```bash
sol token browse [category]
```

Discover tokens by category — what's trending, what's traded most, what just launched.

### Categories

| Category | Description |
|----------|-------------|
| `trending` | Top trending tokens by search + trade activity |
| `top-traded` | Most traded tokens by volume |
| `top-organic` | Highest organic score (real vs wash trading) |
| `recent` | Recently launched tokens |
| `lst` | Liquid staking tokens |
| `verified` | Jupiter-verified tokens |

### Examples

```bash
sol token browse                             # list available categories
sol token browse trending                    # trending tokens (default 1h interval)
sol token browse top-traded --interval 24h   # most traded over 24h
sol token browse top-organic --interval 6h   # highest organic score
sol token browse recent --limit 10           # 10 most recently launched
sol token browse lst                         # liquid staking tokens
sol token browse verified --limit 50         # top 50 verified tokens
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--interval <interval>` | 1h | Time window: `5m`, `1h`, `6h`, `24h` (trending, top-traded, top-organic only) |
| `--limit <n>` | 20 | Number of results to show |

### Example Output

```
#   Symbol  Name       Mint                                          Price      24h     Volume 24h  Organic  Holders
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 1  FART    Fartcoin   9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump  $0.14    +6.7%      $23.4M      96%  165,304
 2  BONK    Bonk       DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263  $0.00002 +3.2%      $18.1M      89%  820,451
 3  WIF     dogwifhat  EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm  $1.23    -1.5%      $12.7M      92%  432,100
```

Full mint addresses, organic scores, and holder counts are shown when
available — useful for distinguishing tokens that share a symbol
(e.g. multiple $TRUMP tokens).

Browse results are recycled into the local token cache, so `sol token info` and `sol token price` resolve instantly for any token you've browsed.

## Swap Tokens

```bash
sol token swap <amount> <from> <to>
```

Swaps tokens by querying all registered routers in parallel and picking the best price. Currently supports Jupiter and DFlow.

### Examples

```bash
sol token swap 50 usdc bonk               # buy BONK — best price wins
sol token swap 1.5 sol usdc               # sell SOL for USDC
sol token swap 100 usdc sol --wallet bot   # from a specific wallet
sol token swap 50 usdc bonk --quote-only   # preview without executing
sol token swap 50 usdc bonk --slippage 100 # 1% slippage (100 bps)
sol token swap 50 usdc bonk --router jupiter  # force a specific router
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--slippage <bps>` | 50 | Slippage tolerance in basis points (50 = 0.5%) |
| `--router <name>` | best | Router: `best`, `jupiter`, `dflow` |
| `--quote-only` | false | Show quote without executing |
| `--wallet <name>` | default | Wallet to swap from |

### Example Output

Quote preview (`--quote-only`):

```
Swap Quote:
  50 USDC → 2500000.000000 BONK
  Price impact: 0.0100%
  Route: USDC → BONK (via jupiter)
  Slippage: 0.5%
```

Executed swap:

```
Swap executed!
  50 USDC → 2500000.000000 BONK
  Signature: 4xK9...abc
  Explorer: https://solscan.io/tx/4xK9...abc
```

### Token Resolution

Tokens can be specified by symbol (`sol`, `usdc`, `bonk`) or mint
address. Resolution order:

1. Hardcoded well-known list (SOL, USDC, USDT, JUP, BONK, mSOL,
   jitoSOL, bSOL, ETH, wBTC, PYTH, JTO, WEN, RNDR, JLP)
2. Local SQLite cache (24-hour TTL)
3. Jupiter Token API (ranked by liquidity)

For safety with unfamiliar tokens, verify with `sol token info <symbol>`
first, or use the mint address directly.

## Send Tokens

```bash
sol token send <amount> <token> <recipient>
```

Send SOL or any SPL token to a wallet address.

### Examples

```bash
sol token send 2 sol 7nY...xyz
sol token send 50 usdc GkX...abc
sol token send 1000 bonk AgE...def
sol token send 0.5 sol 7nY...xyz --wallet trading
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--wallet <name>` | default | Wallet to send from |

### Example Output

```
Sent 50 USDC to GkX...abc
  Signature: 5aB...xyz
  Explorer: https://solscan.io/tx/5aB...xyz
```

## Check Prices

```bash
sol token price <symbols...>
```

### Examples

```bash
sol token price sol                       # single token
sol token price sol usdc bonk eth         # multiple at once
```

### Example Output

```
SOL: $150.25
USDC: $1.00
BONK: $0.000020
ETH: $3,245.80
```

Prices come from Jupiter Price API with CoinGecko fallback.

## Token Info

```bash
sol token info <symbol>
```

Shows token metadata — mint address, decimals, total supply. Useful
for verifying which token a symbol resolves to before transacting.

### Example Output

```
BONK — Bonk
  Mint:     DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
  Decimals: 5
```

## List Tokens

```bash
sol token list                            # default wallet
sol token list --wallet trading           # specific wallet
```

Lists all tokens held in the wallet with balances. The full mint
address is shown so you can distinguish tokens that share a symbol.

### Example Output

```
Token   Balance       Mint
───────────────────────────────────────────────────────────────────────────
SOL     12.500000     So11111111111111111111111111111111111111112
USDC    250.000000    EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
BONK    5000000.000000  DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
```

## Burn Tokens

```bash
sol token burn <symbol> [amount]
```

### Examples

```bash
sol token burn bonk 1000                  # burn specific amount
sol token burn bonk --all                 # burn entire balance
sol token burn bonk --all --close         # burn and close the account
```

### Flags

| Flag | Description |
|------|-------------|
| `--all` | Burn entire balance |
| `--close` | Close the token account after burning (reclaims ~0.002 SOL rent) |
| `--wallet <name>` | Wallet to burn from |

## Close Token Accounts

```bash
sol token close [symbol]
```

Closes empty token accounts and reclaims rent (~0.002 SOL each).

### Examples

```bash
sol token close usdc                      # close specific account
sol token close --all                     # close all empty accounts
sol token close --all --burn              # burn dust + close all
```

### Flags

| Flag | Description |
|------|-------------|
| `--all` | Close all eligible accounts |
| `--burn` | Burn remaining dust before closing |
| `--wallet <name>` | Wallet to close accounts in |

## DCA (Dollar-Cost Average)

```bash
sol token dca new <amount> <from> <to> --every <interval> --count <n>
sol token dca list
sol token dca cancel <orderKey>
```

Create recurring swap orders using Jupiter's Recurring API.

### Examples

```bash
sol token dca new 500 usdc sol --every day --count 10     # buy SOL daily for 10 days
sol token dca new 1000 usdc bonk --every hour --count 20  # hourly BONK buys
sol token dca new 500 usdc sol --every day --count 10 --quote-only  # preview
sol token dca list                                         # active orders
sol token dca list --history                               # past orders
sol token dca cancel <orderKey>                            # cancel an order
```

### Flags (new)

| Flag | Default | Description |
|------|---------|-------------|
| `--every <interval>` | required | Interval: `minute`, `hour`, `day`, `week`, `month` |
| `--count <n>` | 10 | Number of orders |
| `--wallet <name>` | default | Wallet to use |
| `--quote-only` | false | Preview without executing |

### Constraints

- Total value >= $100 USD
- At least 2 orders
- Each order >= $50 USD

## Limit Orders

```bash
sol token limit new <amount> <from> <to> --at <targetPrice>
sol token limit list
sol token limit cancel <orderKey>
```

Place limit orders using Jupiter's Trigger API. The order fills when the output token reaches your target USD price.

### Examples

```bash
sol token limit new 50 usdc bonk --at 0.000003     # buy BONK at $0.000003
sol token limit new 0.5 sol usdc --at 0.90          # buy USDC at $0.90/USDC
sol token limit new 50 usdc bonk --at 0.000003 --quote-only  # preview
sol token limit list                                 # active orders
sol token limit list --history                       # filled/cancelled
sol token limit cancel <orderKey>                    # cancel an order
```

### Flags (new)

| Flag | Default | Description |
|------|---------|-------------|
| `--at <price>` | required | Target USD price for the output token |
| `--slippage <bps>` | 0 | Slippage tolerance (0 = exact fill only) |
| `--wallet <name>` | default | Wallet to use |
| `--quote-only` | false | Preview without executing |

### How target price works

You specify the USD price at which you want to acquire the output token. The CLI calculates the output amount:
`outputAmount = (inputAmount * inputPriceUsd) / targetPriceUsd`

If the target price is above the current market price, the order may fill immediately.

### Constraints

- Minimum order size: $5 USD

## Sync Token Cache

```bash
sol token sync
```

Refreshes the local token metadata cache from Jupiter's token list.
Normally not needed — tokens are cached on first use.
