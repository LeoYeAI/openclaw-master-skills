# LP (Liquidity Pool) Commands Reference

Multi-protocol liquidity provision across Orca, Raydium, Meteora, and
Kamino. Browse pools, deposit liquidity, manage positions, claim fees,
and farm rewards — all from a single `sol lp` interface.

## Supported Protocols

| Protocol | Pools | Positions | Deposit | Withdraw | Claim Fees | Farm | Create Pool |
|----------|-------|-----------|---------|----------|------------|------|-------------|
| Orca | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Raydium | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Meteora | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Kamino | Yes | Yes | Yes | Yes | Yes | No | No |

## Pool Types

- **AMM (full-range)** — Liquidity spread across the entire price range.
  Simpler to manage, no rebalancing needed, but lower capital efficiency.
- **CLMM (concentrated liquidity)** — You pick a price range. Earns
  more fees when price stays in range, but earns nothing when out of
  range. Orca, Raydium, and Meteora all offer CLMM pools. Meteora
  calls theirs DLMM (Dynamic Liquidity Market Maker) with discrete
  price bins instead of ticks.
- **Kamino vaults** — Auto-managed concentrated liquidity. Kamino
  strategies automatically rebalance the price range, so you get CLMM
  efficiency without manual management.

## Browse Pools

```bash
sol lp pools [tokenA] [tokenB]
```

Lists pools with TVL, APY, 24h volume, and fee rate. Without
arguments, shows the highest-TVL pools across all protocols.

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--protocol <name>` | all | Filter by protocol (orca, raydium, meteora, kamino) |
| `--sort <field>` | tvl | Sort by: tvl, apy, volume |
| `--type <type>` | all | Filter by pool type: amm, clmm |
| `--limit <n>` | 20 | Max results |

### Examples

```bash
sol lp pools sol usdc                          # SOL/USDC pools across all protocols
sol lp pools sol --protocol orca               # All SOL pools on Orca
sol lp pools --sort apy --type clmm            # Highest APY CLMM pools
```

### Example Output

```
Protocol  Pool ID                                       Pair       Type  TVL      APY     Volume 24h  Fee
───────────────────────────────────────────────────────────────────────────────────────────────────────────
orca      HJPjKft4yAhLf2ti4cMZY8E7ybSz2a3PSwKzTrP4pump  SOL/USDC   clmm  $25.0M  12.00%  $8.0M       0.04%
raydium   9xK4b3deFGh1234567890abcdef1234567890abcdef12  SOL/USDC   clmm  $18.2M   9.50%  $5.2M       0.05%
meteora   4bC7ghiJKL1234567890abcdef1234567890abcdef1234  SOL/USDC   dlmm  $12.1M  15.20%  $6.8M       0.03%
```

Full pool IDs are shown so you can copy-paste them into
`sol lp deposit`, `sol lp info`, or other commands.

## Pool Info

```bash
sol lp info <poolId>
```

Shows detailed info for a single pool — protocol, type, pair, fee
rate, current price, TVL, APY, volume, and protocol-specific
parameters (tick spacing, bin step).

### Examples

```bash
sol lp info HJPj...abc                         # Pool details
sol lp info HJPj...abc --wallet main           # Include your positions in this pool
```

## Configs

```bash
sol lp configs
```

Lists available pool creation configurations per protocol. Each protocol
has specific parameters — fee tiers, tick spacings (Orca/Raydium CLMM),
bin steps (Meteora DLMM), and creation fees (Raydium CPMM). Use this to
discover valid values before running `sol lp create`.

- **Fee (bps)** — Base trading fee in basis points. Lower fees attract
  more volume; higher fees earn more per trade.
- **Tick spacing** — Minimum price increment for CLMM positions. Smaller
  = more precise ranges but higher gas. Orca and Raydium CLMM use this.
- **Bin step** — Meteora DLMM equivalent of tick spacing. Each bin
  represents a `(1 + binStep/10000)` price multiplier.
- **Create fee** — One-time SOL fee to create a pool (Raydium CPMM).

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--protocol <name>` | all | Filter by protocol |
| `--type <type>` | all | Filter by pool type: amm, clmm |

### Examples

```bash
sol lp configs                              # all protocols
sol lp configs --protocol raydium           # Raydium CLMM + CPMM configs
sol lp configs --protocol meteora           # Meteora DLMM presets from on-chain
sol lp configs --type clmm                  # CLMM configs only
```

## Positions

```bash
sol lp positions
```

Shows all LP positions across protocols — token amounts, USD value,
unclaimed fees, and price range status. CLMM positions show whether
the current price is in range.

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--wallet <name>` | default | Wallet to check |
| `--protocol <name>` | all | Filter by protocol |

### P&L Table

When cost basis data is available, positions also show:
- **Deposit** — USD value at deposit time
- **Current** — Current USD value
- **IL** — Impermanent loss in USD
- **Fees** — Total fees earned
- **Net P&L** — Fees minus IL plus any price appreciation
- **Fee/IL** — Ratio of fees earned to IL (> 1.0 means fees exceed IL)

### Out-of-Range Warning

CLMM positions that are out of range are flagged — they are not
earning fees. The CLI suggests rebalancing:

```
2 positions out of range (not earning fees).
  Consider rebalancing: sol lp withdraw <id> && sol lp deposit <pool> ...
```

## Deposit

```bash
sol lp deposit <poolId> <amount> <token> [amountB] [tokenB]
```

Adds liquidity to a pool. For CLMM pools, specify a price range with
`--lower-price`/`--upper-price` or `--range`. Without range flags on
a CLMM pool, the protocol picks a default range.

### Single vs Dual Token

- **Single token**: `sol lp deposit <poolId> 100 usdc` — the protocol
  swaps internally to balance the pair.
- **Dual token**: `sol lp deposit <poolId> 5 sol 750 usdc` — provide
  both sides of the pair explicitly.

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--wallet <name>` | default | Wallet to use |
| `--position <id>` | new | Add to an existing position instead of creating a new one |
| `--lower-price <n>` | — | CLMM: lower price bound |
| `--upper-price <n>` | — | CLMM: upper price bound |
| `--range <pct>` | — | CLMM: +/- percentage of current price (e.g. 10 = 10% above and below) |
| `--slippage <bps>` | 100 | Slippage tolerance in basis points |
| `--quote-only` | — | Preview deposit amounts without executing |
| `--protocol <name>` | auto | Target a specific protocol |

### Examples

```bash
sol lp deposit HJPj...abc 100 usdc                              # single token, protocol auto-detected
sol lp deposit HJPj...abc 5 sol 750 usdc                        # dual token
sol lp deposit HJPj...abc 100 usdc --range 10                   # CLMM: +/-10% of current price
sol lp deposit HJPj...abc 100 usdc --lower-price 130 --upper-price 170  # CLMM: explicit range
sol lp deposit HJPj...abc 50 usdc --position 9xK...def          # add to existing position
```

## Withdraw

```bash
sol lp withdraw <positionId>
```

Removes liquidity from a position. By default withdraws 100% and
closes the position (reclaims rent). Use `--percent` for partial
withdrawal or `--keep` to leave the position open after a full
withdrawal.

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--percent <n>` | 100 | Partial withdrawal (1-100), does not auto-close |
| `--keep` | — | Don't close position on 100% withdraw |
| `--wallet <name>` | default | Wallet that owns the position |
| `--slippage <bps>` | 100 | Slippage tolerance |
| `--protocol <name>` | auto | Protocol (auto-detected from position) |

### Examples

```bash
sol lp withdraw 9xK...abc                     # full withdrawal, close position
sol lp withdraw 9xK...abc --percent 50        # withdraw half, keep position open
sol lp withdraw 9xK...abc --keep              # withdraw all but keep position open
```

## Claim Fees

```bash
sol lp claim <positionId>
```

Claims uncollected trading fees and rewards from a position without
withdrawing liquidity.

### Examples

```bash
sol lp claim 9xK...abc                        # claim fees from position
```

## Farm

Farming earns additional token rewards on top of trading fees by
staking LP positions in incentive programs.

### List Farms

```bash
sol lp farm list
```

Shows staked positions and pending farm rewards.

### Stake

```bash
sol lp farm stake <positionId>
```

Stakes an LP position in a farm to earn additional rewards.

### Unstake

```bash
sol lp farm unstake <positionId>
```

Unstakes an LP position from a farm.

### Harvest

```bash
sol lp farm harvest <positionId>
```

Claims pending farm rewards without unstaking.

### Examples

```bash
sol lp farm list                               # see staked positions and pending rewards
sol lp farm stake 9xK...abc                    # stake position in farm
sol lp farm unstake 9xK...abc                  # remove from farm
sol lp farm harvest 9xK...abc                  # claim farm rewards
```

## Create Pool

```bash
sol lp create <tokenA> <tokenB> <amountA> <amountB> --protocol <name>
```

Creates a new liquidity pool. The `--protocol` flag is required.
Protocol-specific parameters control the pool type and pricing.

### Flags

| Flag | Description |
|------|-------------|
| `--protocol <name>` | Required. Protocol to create pool on |
| `--fee-tier <bps>` | Fee tier in basis points |
| `--initial-price <n>` | Starting price of tokenA in terms of tokenB |
| `--tick-spacing <n>` | Orca/Raydium CLMM: tick spacing |
| `--bin-step <n>` | Meteora DLMM: bin step size |
| `--type <type>` | Pool type: amm or clmm |
| `--wallet <name>` | Wallet to use |

### Examples

```bash
sol lp create sol usdc 10 1500 --protocol orca --type clmm --fee-tier 4
sol lp create mytoken usdc 1000000 500 --protocol raydium --initial-price 0.0005
sol lp create sol usdc 5 750 --protocol meteora --bin-step 1
```

## Permissions

LP commands use the same permissions as lending:

| Permission | Gated subcommands |
|---|---|
| `canLend` | `lp deposit`, `lp farm stake`, `lp create` |
| `canWithdrawLend` | `lp withdraw`, `lp claim`, `lp farm unstake`, `lp farm harvest` |

Read-only commands (`lp pools`, `lp info`, `lp positions`, `lp farm list`)
are always available regardless of permissions.

## Impermanent Loss

When you provide liquidity, price changes between the two tokens cause
your position to rebalance — you end up holding more of the cheaper
token and less of the expensive one compared to simply holding. This
difference is called impermanent loss (IL).

- IL increases with price divergence between the two tokens
- Concentrated (CLMM) positions amplify IL within the range but earn
  more fees to compensate
- Fees earned can offset IL — the Fee/IL ratio in `sol lp positions`
  shows whether fees are winning (> 1.0x) or losing (< 1.0x)
- IL is "impermanent" because it reverses if prices return to the
  original ratio — but if you withdraw while prices have diverged,
  the loss is realized

Stablecoin pairs (USDC/USDT) have minimal IL. Volatile pairs
(SOL/memecoin) can have significant IL but also earn higher fees.
