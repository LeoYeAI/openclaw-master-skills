# Prediction Market Commands Reference

Browse, search, and trade prediction markets via Jupiter. Markets are
sourced from Polymarket and Kalshi. Settlements are in USDC.

## Browse Events

```bash
sol predict list [category]
```

Browse prediction events. Categories: `crypto`, `sports`, `politics`,
`esports`, `culture`, `economics`, `tech`, `finance`, `climate & science`.

### Examples

```bash
sol predict list                           # all events
sol predict list crypto                    # crypto events only
sol predict list sports --filter trending  # trending sports events
sol predict list --limit 10               # limit results
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--filter <type>` | none | Filter: `new`, `live`, `trending`, `upcoming` |
| `--limit <n>` | 20 | Number of results |

### Example Output

```
Event ID     Title                                              Category  Markets  Volume
─────────────────────────────────────────────────────────────────────────────────────────
POLY-89525   What price will Solana hit in 2026?                crypto          5  $125.0K
POLY-91234   Will Bitcoin reach $200k in 2026?                  crypto          3  $89.2K
POLY-88001   Champions League Winner 2026                       sports          8  $45.1K

Showing 3 events. Run `sol predict event <id>` to see markets.
```

## Search Events

```bash
sol predict search <query>
```

Search events by keyword.

### Examples

```bash
sol predict search "solana"
sol predict search "super bowl" --limit 5
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--limit <n>` | 20 | Number of results |

## View Event Details

```bash
sol predict event <eventId>
```

Shows an event and all its markets with YES/NO prices.

### Examples

```bash
sol predict event POLY-89525
```

### Example Output

```
What price will Solana hit in 2026?
Category: crypto | Volume: $125.0K | Status: live

Market ID      Market         YES     NO   Volume  Status
──────────────────────────────────────────────────────────────────
POLY-701571    ↑ 200         $0.35  $0.65  $50.0K  live
POLY-701572    ↑ 300         $0.15  $0.85  $32.1K  live
POLY-701573    ↑ 500         $0.05  $0.95  $18.4K  live

Run `sol predict buy <amount> yes|no <marketId>` to buy contracts.
```

## View Market Details

```bash
sol predict market <marketId>
```

Shows detailed market info — YES/NO prices, volume, resolution status,
and orderbook depth (top 10 levels).

### Examples

```bash
sol predict market POLY-701571
```

### Example Output

```
↑ 200
YES: $0.3500 | NO: $0.6500 | Volume: $50.0K
Status: live

YES Orderbook
Price   Qty
────────────
 $0.35  150
 $0.34  200
 $0.33   80

NO Orderbook
Price   Qty
────────────
 $0.65  200
 $0.66  120
```

## Buy Contracts

```bash
sol predict buy <amount> <yes|no> <marketId>
```

Buy YES or NO contracts with USDC. The amount is in USD.

### Examples

```bash
sol predict buy 5 yes POLY-701571               # buy YES contracts with $5
sol predict buy 10 no POLY-559652                # buy NO contracts with $10
sol predict buy 5 yes POLY-701571 --max-price 0.40  # limit entry price
sol predict buy 5 yes POLY-701571 --wallet trading
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--max-price <price>` | none | Maximum price per contract (0–1) |
| `--wallet <name>` | default | Wallet to use |

### Example Output

```
Bought 14.28 YES contracts at $0.3500
  Cost: $5.00 USDC
  Position: 7gK3a2...def
  Tx: https://solscan.io/tx/4xK9...abc

Run `sol predict positions` to track your positions.
```

### Permission

Requires `canPredict = true` in `~/.sol/config.toml`.

### Notes

- Minimum deposit is approximately $2 USDC.
- Cost basis is recorded at buy time for P&L tracking.
- Positions appear in `sol predict positions` and `sol portfolio`.

## Sell a Position

```bash
sol predict sell <positionPubkey>
```

Close an open position by selling the contracts.

### Examples

```bash
sol predict sell 7gK...abc
sol predict sell 7gK...abc --wallet trading
sol predict sell 7gK...abc --min-price 0.50
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--min-price <price>` | none | Minimum sell price per contract (0–1) |
| `--wallet <name>` | default | Wallet that owns the position |

### Permission

Requires `canPredict = true`.

## Claim Winnings

```bash
sol predict claim <positionPubkey>
```

Claim winnings on a resolved market. Only works if the market has
settled and the position is on the winning side.

### Examples

```bash
sol predict claim 7gK...abc
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--wallet <name>` | default | Wallet that owns the position |

### Permission

Requires `canPredict = true`.

### Notes

Winning contracts pay out $1.00 each. The CLI calculates realized P&L
relative to your cost basis.

## View Positions

```bash
sol predict positions
```

Lists all open and claimable prediction positions with cost basis,
current value, and unrealized P&L.

### Examples

```bash
sol predict positions
sol predict positions --wallet trading
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--wallet <name>` | default | Wallet to check |

### Example Output

```
Position     Market                                      Side  Contracts  Cost    Value   P&L      Status
────────────────────────────────────────────────────────────────────────────────────────────────────────
7gK3a2..abc  Solana hit in 2026? — ↑ 200                 YES      14.28  $5.00   $5.71   +$0.71   open
9xK4b3..def  Bitcoin reach $200k? — YES                  YES       8.00  $10.00  $8.40   -$1.60   open
```

Claimable positions are highlighted — run `sol predict claim` to
collect winnings.

## Transaction History

```bash
sol predict history
```

Shows prediction market transaction history (buys, sells, claims).

### Examples

```bash
sol predict history
sol predict history --wallet trading
sol predict history --limit 10
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--wallet <name>` | default | Wallet to check |
| `--limit <n>` | 50 | Number of entries |

## Portfolio Integration

Prediction positions appear in `sol portfolio` alongside tokens,
staked SOL, and lending positions. Each position shows:

- Market name (event + market title)
- Side (YES / NO)
- Contracts held
- Cost basis and current value
- Unrealized P&L

Snapshots include prediction positions, so `sol portfolio compare`
tracks how positions change over time.

## Permissions

Write commands (`buy`, `sell`, `claim`) are gated by the `canPredict`
permission. Read commands (`list`, `search`, `event`, `market`,
`positions`, `history`) are always available.

```toml
[permissions]
canPredict = false   # disables buy/sell/claim
```

## Geo-Restrictions

Jupiter's prediction markets API is not available from US and South
Korea IP addresses. Commands will fail with a network error from these
locations.
