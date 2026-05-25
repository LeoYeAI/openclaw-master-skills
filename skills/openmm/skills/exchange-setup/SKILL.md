---
name: openmm-exchange-setup
version: 0.1.0
description: "Step-by-step guide to configure exchange API credentials for OpenMM."
tags: [openmm, setup, exchanges, configuration]
metadata:
  openclaw:
    emoji: "🔑"
    requires:
      bins: [openmm]
    install:
      - kind: node
        package: "@3rd-eye-labs/openmm"
        bins: [openmm]
---

# OpenMM Exchange Setup

Interactive guide for configuring exchange API credentials in OpenMM.

## When to Use

Use this skill when:
- Setting up OpenMM for the first time
- Adding a new exchange
- Troubleshooting connection issues

## Supported Exchanges

| Exchange | Min Order | Credentials Required |
|----------|-----------|---------------------|
| MEXC | 1 USDT | API key + Secret |
| Gate.io | 1 USDT | API key + Secret |
| Bitget | 1 USDT | API key + Secret + Passphrase |
| Kraken | 5 EUR/USD | API key + Secret |

## Setup Workflow

### Step 1: Create API Keys

Guide user to the exchange's API management page:

```
MEXC:    https://www.mexc.com/ucenter/api
Gate.io: https://www.gate.io/myaccount/apikeys
Kraken:  https://www.kraken.com/u/security/api
Bitget:  https://www.bitget.com/account/newapi
```

### Step 2: Configure Permissions

Required permissions for each exchange:

**MEXC:**
- Enable Spot Trading
- Enable Reading
- Disable Withdrawals (safety)
- IP whitelist recommended

**Gate.io:**
- Spot Trade
- Spot Read
- No Withdraw permission
- IP whitelist recommended

**Kraken:**
- Query Funds
- Query Open Orders & Trades
- Create & Modify Orders
- No Withdraw permission

**Bitget:**
- Trade
- Read Only
- No Transfer permission
- Note the Passphrase — it is set when creating the API key

### Step 3: Set Environment Variables

OpenMM uses environment variables for credentials. Add them to your `.env` file or export in your shell:

```bash
# MEXC
export MEXC_API_KEY="your_mexc_api_key"
export MEXC_SECRET="your_mexc_secret_key"

# Gate.io
export GATEIO_API_KEY="your_gateio_api_key"
export GATEIO_SECRET="your_gateio_secret_key"

# Bitget (requires passphrase)
export BITGET_API_KEY="your_bitget_api_key"
export BITGET_SECRET="your_bitget_secret_key"
export BITGET_PASSPHRASE="your_bitget_passphrase"

# Kraken
export KRAKEN_API_KEY="your_kraken_api_key"
export KRAKEN_SECRET="your_kraken_secret_key"
```

Or create a `.env` file in the project root:

```env
MEXC_API_KEY=your_mexc_api_key
MEXC_SECRET=your_mexc_secret_key
GATEIO_API_KEY=your_gateio_api_key
GATEIO_SECRET=your_gateio_secret_key
BITGET_API_KEY=your_bitget_api_key
BITGET_SECRET=your_bitget_secret_key
BITGET_PASSPHRASE=your_bitget_passphrase
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_SECRET=your_kraken_secret_key
```

### Step 4: Verify Connection

Test that credentials work by checking balances:

```bash
# MEXC
openmm balance --exchange mexc

# Gate.io
openmm balance --exchange gateio

# Bitget
openmm balance --exchange bitget

# Kraken
openmm balance --exchange kraken
```

### Step 5: Test Market Data

Confirm market data access:

```bash
openmm ticker --exchange mexc --symbol BTC/USDT
openmm orderbook --exchange kraken --symbol ADA/EUR --limit 5
```

## MCP Server Setup

To use OpenMM as an MCP server, add to your MCP client config:

```json
{
  "mcpServers": {
    "openmm": {
      "command": "npx",
      "args": ["@qbtlabs/openmm-mcp"],
      "env": {
        "MEXC_API_KEY": "your_key",
        "MEXC_SECRET": "your_secret",
        "KRAKEN_API_KEY": "your_key",
        "KRAKEN_SECRET": "your_secret"
      }
    }
  }
}
```

Only include env vars for exchanges you want to use.

## Troubleshooting

### "credentials not found"
- Verify environment variables are set: `echo $MEXC_API_KEY`
- Check `.env` file is in the correct directory
- Ensure variable names match exactly (e.g. `MEXC_SECRET` not `MEXC_SECRET_KEY`)

### "credentials validation failed" (Bitget)
- Verify all three vars: `BITGET_API_KEY`, `BITGET_SECRET`, `BITGET_PASSPHRASE`
- The passphrase is set when creating the API key on Bitget

### "authentication failed" (Kraken)
- Verify `KRAKEN_API_KEY` and `KRAKEN_SECRET`
- Check key permissions on Kraken API settings page

### "Timestamp Error"
- System clock may be out of sync
- Run: `sudo ntpdate time.google.com`

### "Rate Limited"
- Reduce request frequency
- Check exchange's rate limit docs

## Security Best Practices

1. **Never enable withdrawals** — trading doesn't need it
2. **Use IP whitelisting** — restrict to your server's IP
3. **Never commit `.env` files** — add `.env` to `.gitignore`
4. **Rotate keys periodically** — every 90 days recommended
5. **Use separate keys for testing** — don't mix testnet/mainnet
