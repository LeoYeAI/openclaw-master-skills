# Lending Commands Reference

Multi-protocol lending and borrowing across Kamino, MarginFi, Drift,
Jupiter Lend, and Loopscale. The CLI aggregates rates from all
protocols and auto-selects the best one, or you can target a specific
protocol with `--protocol`.

## Supported Protocols

| Protocol | Deposit | Withdraw | Borrow | Repay | Notes |
|----------|---------|----------|--------|-------|-------|
| Kamino | Yes | Yes | Yes | Yes | SDK-based, health factor monitoring |
| MarginFi | Yes | Yes | Yes | Yes | SDK-based, multiple accounts per wallet |
| Drift | Yes | Yes | No | No | SDK-based, spot market deposits |
| Jupiter Lend | Yes | Yes | No | No | REST API, deposit/withdraw only |
| Loopscale | Yes | Yes | Yes | Yes | REST API, order-book lending, fixed-term borrows |

## Check Rates

```bash
sol lend rates [tokens...]
sol lend rates --protocol <name>
```

Shows deposit and borrow APY across all protocols (or a specific
one). The best deposit rate per token is marked with `*`.

### Examples

```bash
sol lend rates usdc                    # USDC rates across all protocols
sol lend rates sol usdc                # SOL and USDC rates
sol lend rates --protocol kamino       # Only Kamino rates
```

### Example Output

```
Lending Rates — USDC

Protocol     Token  Deposit APY  Borrow APY  Utilization  Total Deposited
──────────────────────────────────────────────────────────────────────────
loopscale    USDC       8.50% *       6.00%       72.1%         $45.2M
kamino       USDC       4.50%         8.20%       63.3%        $150.0M
marginfi     USDC       3.80%         7.10%       58.9%         $82.5M
drift        USDC       3.20%            —        45.2%         $30.1M
jup-lend     USDC       2.90%            —        40.0%         $20.0M

* = best rate. Run `sol lend deposit <amount> <token>` to start earning.
```

## Deposit

```bash
sol lend deposit <amount> <token>
```

Deposits tokens to earn yield. Without `--protocol`, auto-picks the
protocol with the best deposit rate for that token.

### Examples

```bash
sol lend deposit 100 usdc                     # best rate wins
sol lend deposit 5 sol --protocol marginfi    # target MarginFi
sol lend deposit 100 usdc --wallet trading
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--wallet <name>` | default | Wallet to deposit from |
| `--protocol <name>` | auto | Protocol to use (kamino, marginfi, drift, jup-lend, loopscale) |

## Withdraw

```bash
sol lend withdraw <amount|max> <token>
```

Withdraws tokens from a lending position. Without `--protocol`,
auto-detects which protocol holds the deposit. If deposits exist
on multiple protocols, you must specify one.

### Examples

```bash
sol lend withdraw 50 usdc                     # partial withdrawal
sol lend withdraw max sol                     # withdraw everything
sol lend withdraw max usdc --protocol kamino
```

Use `max` to withdraw the entire deposited amount.

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--wallet <name>` | default | Wallet that owns the deposit |
| `--protocol <name>` | auto | Protocol to withdraw from |

## Borrow

```bash
sol lend borrow <amount> <token> --collateral <token>
```

Borrows tokens against collateral. Supported on Kamino, MarginFi,
and Loopscale. Without `--protocol`, defaults to Kamino.

### Examples

```bash
sol lend borrow 500 usdc --collateral sol
sol lend borrow 0.1 usdc --collateral sol --protocol loopscale
```

### Flags

| Flag | Description |
|------|-------------|
| `--collateral <token>` | Required. Token to use as collateral |
| `--wallet <name>` | Wallet that owns the collateral |
| `--protocol <name>` | Protocol to borrow from (default: kamino) |

### Protocol differences

- **Kamino / MarginFi**: Pool-based variable rates. Health factor
  monitored in real time.
- **Loopscale**: Order-book with fixed-rate, fixed-term loans
  (1-day default, auto-refinances). Rate shown at borrow time
  reflects the actual rate locked in.

## Repay

```bash
sol lend repay <amount|max> <token>
```

Repays borrowed tokens. Without `--protocol`, auto-detects which
protocol holds the loan.

### Examples

```bash
sol lend repay 250 usdc                       # partial repay
sol lend repay max usdc                       # repay full debt
sol lend repay max usdc --protocol loopscale
```

Use `max` to repay the entire borrowed amount.

## View Positions

```bash
sol lend positions
sol lend positions --protocol <name>
sol lend positions --wallet trading
```

Lists all deposits and borrows across all protocols — token, amount,
APY, USD value, and health factor (where available).

The CLI warns when health factor drops below 1.1.

### Example Output

```
Lending Positions — main

Protocol    Token  Type      Amount      Value     APY
─────────────────────────────────────────────────────────
kamino      USDC   deposit   100.00      $100.00   4.50%
loopscale   USDC   borrow    50.00       $50.00    6.00%

Health factor: 2.50
```

## Health Factor

Health factor = total collateral value / total borrow value (weighted
by liquidation thresholds). Below 1.0 means liquidation risk.

- **> 2.0**: Safe
- **1.1 – 2.0**: Monitor closely
- **< 1.1**: CLI warns — consider repaying or adding collateral
- **< 1.0**: Liquidation possible

Note: Loopscale uses fixed-term LTV at origination rather than a
real-time health factor, so health factor is not shown for Loopscale
positions.
