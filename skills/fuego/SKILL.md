---
name: fuego
description: Local Solana agent wallet with local infra for transfers (SOL, USDC, USDT), Jupiter swaps, and x402 purch.
homepage: https://fuego.cash
version: 1.4.0
metadata:
  {
    "openclaw":
      {
        "emoji": "🔥",
        "requires": { "bins": ["curl", "node", "cargo"], "env": [] },
        "optional": { "bins": [], "env": [] },
      },
  }
---

# Fuego SKILL

Local Solana agent wallet with local infra for transfers (SOL, USDC, USDT), Jupiter swaps, and x402 purch.

## Quick Start

### 1. Install fuego-cli
```bash
npm install -g fuego-cli
```

### 2. Create Wallet
```bash
fuego create

# Output:
# Address: DmFyLRiJtc4Bz75hjAqPaEJpDfRe4GEnRLPwc3EgeUZF
# Wallet config: ~/.fuego/wallet-config.json
# Backup: ~/.config/solana/fuego-backup.json
```

### 3. Install Fuego Project

**Prerequisites:** Rust 1.85+ and Cargo are required to build the server.

```bash
# For OpenClaw agents (auto-detects ~/.openclaw/workspace)
fuego install

# For manual installs (specify path)
fuego install --path ~/projects/fuego
```

### 4. Configure Jupiter API Key (Optional - for Swaps)

If you want to do token swaps via Jupiter, you need an API key:

1. Sign up at https://portal.jup.ag
2. Create a new API key (free tier available)
3. Add to your Fuego config at `~/.fuego/config.json`:

```json
{
  "rpcUrl": "https://api.mainnet-beta.solana.com",
  "network": "mainnet-beta",
  "jupiterKey": "your-jupiter-api-key-here"
}
```

Without this key, swaps will not work. Balance checks and transfers work without it.

### 5. Start Server
```bash
fuego serve

# Output:
# Fuego server running on http://127.0.0.1:8080
```

### 6. Show Address to Human
```bash
fuego address

# Output:
# Your Fuego Address
# Name: default
# Public Key: DmFy...eUZF
```

Share this address so humans can fund the wallet. They can send SOL from any Solana wallet (Phantom, Solflare, etc.).

### 7. Fund the Wallet

**Option A: MoonPay (for fiat → crypto)**
- Visit: https://buy.moonpay.com/?currency=SOL&address=YOUR_ADDRESS
- Minimum: ~$30 USD
- Instant to wallet

**Option B: Manual transfer**
- Human copies address from above
- Sends SOL from their wallet to your Fuego address
- SOL needed for transaction fees (0.001 SOL per tx)

---

## Send Transactions

**Use the CLI - this is the recommended approach:**

```bash
fuego send <recipient> <amount> --token USDC --yes
```

This single command:
- Builds transaction with fresh blockhash
- Signs locally (zero network key exposure)
- Submits to chain with proper error handling
- Returns signature + explorer link
- Supports address book contacts
- Works with SOL, USDC, USDT via `--token` flag

**Example:**
```bash
fuego send GvCoHGGBR97Yphzc6SrRycZyS31oUYBM8m9hLRtJT7r5 0.25 --token USDC --yes
```

---

## Token Swaps via Jupiter

### Step 1: Get a Quote First
Always show the user the expected rate before executing:

```bash
fuego quote --input BONK --output USDC --amount 100000
```

Output shows:
- Input amount (with token decimals handled automatically)
- Expected output amount
- Price impact
- Route details

### Step 2: Execute the Swap
After user confirms the quote:

```bash
fuego swap --input BONK --output USDC --amount 100000 --slippage 1.0
```

**Parameters:**
- `--input` - Input token symbol (SOL, USDC, BONK, etc.) or mint address
- `--output` - Output token symbol or mint address
- `--amount` - Amount in token units (e.g., 100000 for 100000 BONK)
- `--slippage` - Slippage tolerance in percent (default: 0.5%)

The swap script automatically:
- Fetches correct token decimals from on-chain
- Uses BigInt for precision (no floating point errors)
- Throws error if decimals cannot be determined (prevents incorrect amounts)

**Prerequisites:**
- Jupiter API key must be configured in `~/.fuego/config.json`
- See Step 4 in Quick Start for setup instructions

---

## Agent-Ready Architecture

```
Agent/Script
       ↓ POST /build-transfer-sol
Fuego Server (localhost:8080)
  • Builds unsigned transaction with fresh blockhash
  • Returns base64-encoded transaction + memo
       ↓ Unsigned Transaction
Agent/Script
  • Loads ~/.fuego/wallet.json (simple JSON, no password!)
  • Signs transaction locally
       ↓ Signed Transaction
Fuego Server (localhost:8080)
  • POST /submit-transaction
  • Broadcasts to Solana mainnet
       ↓ On-chain
Solana Network
```

**Security Model:**
- Private keys never leave your machine (client-side signing for all transfers)
- File permissions provide real security (chmod 600)
- No network key exposure (localhost-only server)
- Standard Solana format (compatible with CLI tools)

**One Exception - x402 Payments:**
The `/x402-purch` endpoint handles the complete payment flow internally (including signing) because x402 requires server-side proof-of-payment generation. This is a deliberate security trade-off: the server temporarily accesses the private key only to sign the specific x402 payment transaction, then immediately clears it from memory. This enables seamless agent purchasing while maintaining the local-first architecture for all other operations.

---

## API Reference

### GET /wallet-address
Get the local wallet address dynamically.

```bash
curl http://127.0.0.1:8080/wallet-address
```

**Response:**
```json
{
  "success": true,
  "data": {
    "address": "DmFyLRiJtc4Bz75hjAqPaEJpDfRe4GEnRLPwc3EgeUZF",
    "network": "mainnet-beta",
    "source": "wallet"
  }
}
```

### POST /balance - Check SOL Balance
```bash
curl -X POST http://127.0.0.1:8080/balance \
  -H "Content-Type: application/json" \
  -d '{"network": "mainnet-beta", "address": "YOUR_ADDRESS"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sol": 1.234567890,
    "lamports": 1234567890,
    "network": "mainnet-beta"
  }
}
```

### POST /tokens - Check All Token Balances
```bash
curl -X POST http://127.0.0.1:8080/tokens \
  -H "Content-Type: application/json" \
  -d '{"network": "mainnet-beta", "address": "YOUR_ADDRESS"}'
```

Returns SOL + all SPL token balances (USDC, USDT, BONK, etc.)

### POST /build-transfer-sol - Build SOL Transfer
```bash
curl -X POST http://127.0.0.1:8080/build-transfer-sol \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "from_address": "YOUR_ADDRESS",
    "to_address": "RECIPIENT_ADDRESS",
    "amount": "0.001",
    "yid": "agent-transfer-123"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction": "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAEDAb...",
    "blockhash": "J7rBdM33dHKtJwjp...AbCdEfGhIjKl",
    "memo": "fuego|SOL|f:YOUR_ADDRESS|t:RECIPIENT|a:1000000|yid:agent-transfer-123|n:",
    "network": "mainnet-beta"
  }
}
```

### POST /build-transfer-usdc - Build USDC Transfer
```bash
curl -X POST http://127.0.0.1:8080/build-transfer-usdc \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "from_address": "YOUR_ADDRESS",
    "to_address": "RECIPIENT_ADDRESS",
    "amount": "10.50",
    "yid": "agent-usdc-456"
  }'
```

### POST /build-transfer-usdt - Build USDT Transfer
```bash
curl -X POST http://127.0.0.1:8080/build-transfer-usdt \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "from_address": "YOUR_ADDRESS",
    "to_address": "RECIPIENT_ADDRESS",
    "amount": "25.75",
    "yid": "agent-usdt-789"
  }'
```

### POST /submit-transaction - Broadcast Signed Transaction
```bash
curl -X POST http://127.0.0.1:8080/submit-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "transaction": "BASE64_SIGNED_TRANSACTION"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "signature": "5J7XzY...9KpQrS",
    "explorer_link": "https://explorer.solana.com/tx/5J7XzY...9KpQrS?cluster=mainnet-beta"
  }
}
```

---

## Agent Integration Patterns

### For Agents Writing Code (Node.js, etc.)

**Just call the CLI via subprocess. That's it.**

The CLI handles everything: building, signing, submitting, error handling. Don't wrap it in a class — just use it directly.

**Node.js/TypeScript:**
```javascript
import { execSync } from 'child_process';

// Send payment
const result = execSync(
  'fuego send GvCo... 0.25 --token USDC --yes',
  { encoding: 'utf-8' }
);
console.log(result);
```

### Alternative: Raw API Integration (Not Recommended)

If you absolutely must use raw API calls instead of the CLI, use the endpoints documented below. But the CLI is strongly preferred.

---

## Complete API Reference

### GET /
Root endpoint - returns server status.

```bash
curl http://127.0.0.1:8080/
```

**Response:**
```
Fuego Server
```

### GET /health
Health check endpoint.

```bash
curl http://127.0.0.1:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "fuego-server",
  "version": "0.1.0"
}
```

### GET /network
Get the default network configuration.

```bash
curl http://127.0.0.1:8080/network
```

**Response:**
```json
{
  "network": "mainnet-beta"
}
```

### GET /wallet-address
Get the local wallet address dynamically.

```bash
curl http://127.0.0.1:8080/wallet-address
```

**Response:**
```json
{
  "success": true,
  "data": {
    "address": "DmFyLRiJtc4Bz75hjAqPaEJpDfRe4GEnRLPwc3EgeUZF",
    "network": "mainnet-beta",
    "source": "wallet"
  }
}
```

### POST /latest-hash
Get the latest blockhash for transaction building.

```bash
curl -X POST http://127.0.0.1:8080/latest-hash \
  -H "Content-Type: application/json" \
  -d '{"network": "mainnet-beta"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "blockhash": "J7rBdM33dHKtJwjp...",
    "network": "mainnet-beta"
  }
}
```

### POST /sol-balance - Check SOL Balance
```bash
curl -X POST http://127.0.0.1:8080/sol-balance \
  -H "Content-Type: application/json" \
  -d '{"network": "mainnet-beta", "address": "YOUR_ADDRESS"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "address": "YOUR_ADDRESS",
    "lamports": 105113976,
    "sol": 0.105113976,
    "network": "mainnet-beta"
  }
}
```

### POST /usdc-balance - Check USDC Balance
```bash
curl -X POST http://127.0.0.1:8080/usdc-balance \
  -H "Content-Type: application/json" \
  -d '{"network": "mainnet-beta", "address": "YOUR_ADDRESS"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "usdc": 150.250000,
    "raw_amount": "150250000",
    "network": "mainnet-beta"
  }
}
```

### POST /usdt-balance - Check USDT Balance
```bash
curl -X POST http://127.0.0.1:8080/usdt-balance \
  -H "Content-Type: application/json" \
  -d '{"network": "mainnet-beta", "address": "YOUR_ADDRESS"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "usdt": 75.500000,
    "raw_amount": "75500000",
    "network": "mainnet-beta"
  }
}
```

### POST /tokens - Check All Token Balances
```bash
curl -X POST http://127.0.0.1:8080/tokens \
  -H "Content-Type: application/json" \
  -d '{"network": "mainnet-beta", "address": "YOUR_ADDRESS"}'
```

Returns SOL + all SPL token balances (USDC, USDT, BONK, etc.)

**Response:**
```json
{
  "success": true,
  "data": {
    "wallet": "DmFyLRiJtc4Bz75hjAqPaEJpDfRe4GEnRLPwc3EgeUZF",
    "network": "mainnet",
    "sol_balance": 0.105113976,
    "sol_lamports": 105113976,
    "token_count": 2,
    "tokens": [
      {
        "symbol": "USDC",
        "ui_amount": 28.847897,
        "decimals": 6,
        "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
      }
    ]
  }
}
```

### POST /all-transactions - Get Transaction History
```bash
curl -X POST http://127.0.0.1:8080/all-transactions \
  -H "Content-Type: application/json" \
  -d '{"network": "mainnet-beta", "address": "YOUR_ADDRESS", "limit": 20}'
```

Returns all wallet transactions. Fuego transactions (those with `fuego|` in the memo) are styled with rich details in the dashboard.

### POST /build-transfer-sol - Build SOL Transfer
```bash
curl -X POST http://127.0.0.1:8080/build-transfer-sol \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "from_address": "YOUR_ADDRESS",
    "to_address": "RECIPIENT_ADDRESS",
    "amount": "0.001",
    "yid": "agent-transfer-123"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transaction": "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAEDAb...",
    "blockhash": "J7rBdM33dHKtJwjp...AbCdEfGhIjKl",
    "memo": "fuego|SOL|f:YOUR_ADDRESS|t:RECIPIENT|a:1000000|yid:agent-transfer-123|n:",
    "network": "mainnet-beta"
  }
}
```

### POST /build-transfer-usdc - Build USDC Transfer
```bash
curl -X POST http://127.0.0.1:8080/build-transfer-usdc \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "from_address": "YOUR_ADDRESS",
    "to_address": "RECIPIENT_ADDRESS",
    "amount": "10.50",
    "yid": "agent-usdc-456"
  }'
```

### POST /build-transfer-usdt - Build USDT Transfer
```bash
curl -X POST http://127.0.0.1:8080/build-transfer-usdt \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "from_address": "YOUR_ADDRESS",
    "to_address": "RECIPIENT_ADDRESS",
    "amount": "25.75",
    "yid": "agent-usdt-789"
  }'
```

### POST /submit-transaction - Broadcast Signed Transaction
```bash
curl -X POST http://127.0.0.1:8080/submit-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "transaction": "BASE64_SIGNED_TRANSACTION"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "signature": "5J7XzY...9KpQrS",
    "explorer_link": "https://explorer.solana.com/tx/5J7XzY...9KpQrS?cluster=mainnet-beta"
  }
}
```

### POST /submit-versioned-transaction - Broadcast Versioned Transaction
```bash
curl -X POST http://127.0.0.1:8080/submit-versioned-transaction \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "transaction": "BASE64_VERSIONED_TRANSACTION"
  }'
```

### POST /x402-purch - x402 Payment (Server-Side Signing)
Complete x402 payment flow including server-side signing. Used for Purch.xyz integrations.

```bash
curl -X POST http://127.0.0.1:8080/x402-purch \
  -H "Content-Type: application/json" \
  -d '{
    "network": "mainnet-beta",
    "product_url": "https://amazon.com/dp/B071G6PFDR",
    "email": "user@example.com",
    "shipping_name": "John Doe",
    "shipping_address_line1": "123 Main St",
    "shipping_city": "Austin",
    "shipping_state": "TX",
    "shipping_postal_code": "78701",
    "shipping_country": "US"
  }'
```

---

## Security Best Practices

### What Makes Fuego Secure

1. **File Permissions = Real Security**
   ```bash
   # Wallet files are chmod 600 (user read/write only)
   ls -la ~/.fuego/wallet.json
   # -rw------- 1 user user 658 Feb 18 15:01 wallet.json
   ```

2. **Client-Side Signing (with one exception)**
   - Private keys never sent over network (for transfers, swaps, etc.)
   - Signing happens locally in CLI/scripts
   - Server only sees signed transactions (public data)
   - Exception: x402 payments require server-side signing for proof-of-payment generation. Key is loaded only for that specific transaction, then cleared from memory.

3. **Localhost-Only Server**
   - Server binds to 127.0.0.1 (local only)
   - No external network exposure
   - No firewall configuration needed

4. **Standard Format Compatibility**
   ```bash
   # Compatible with Solana CLI tools
   solana-keygen pubkey ~/.fuego/wallet.json  # Works
   solana balance ~/.fuego/wallet.json        # Works
   ```

### Agent Security Checklist

- Keep `~/.fuego/wallet.json` secure (it's your private key!)
- Don't commit wallet files to version control
- Only run server on localhost (default behavior)
- Regularly backup `~/.config/solana/fuego-backup.json`
- Verify transactions on Solana Explorer
- Monitor wallet balance regularly
- Use strong system-level user isolation

---

## Troubleshooting

### Common Issues

**"Wallet not initialized" error**
```bash
# Solution: Create wallet with fuego-cli
fuego create
```

**"Server not running" error**
```bash
# Solution: Start server
fuego serve
```

**"Connection refused" error**
```bash
# Check if server is running
curl http://127.0.0.1:8080/health

# If not running, start it
fuego serve
```

**"Fuego server not found" error**
```bash
# Solution: Install the fuego project
fuego install
```

**"Transaction simulation failed" error**
```bash
# Usual cause: Insufficient balance
# Check all token balances first
curl -X POST http://127.0.0.1:8080/tokens \
  -H "Content-Type: application/json" \
  -d '{"network": "mainnet-beta", "address": "YOUR_ADDRESS"}'
```

**"Invalid signature" error**
```bash
# Wallet file might be corrupted
# Restore from backup
cp ~/.config/solana/fuego-backup.json ~/.fuego/wallet.json
```

**Version mismatch / unexpected behavior**
```bash
# Ensure all components are up to date
fuego update

# This updates both fuego-cli and the fuego project
# Restart server after updating: fuego serve
```

---

## Supported Tokens & Networks

### Transfer Tokens (fuego send)
These tokens are supported by `fuego send`:

| Token | Mint Address | Decimals | Status |
|-------|-------------|----------|--------|
| **SOL** | Native | 9 | Live |
| **USDC** | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6 | Live |
| **USDT** | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenEqw` | 6 | Live |

### Swap Tokens (fuego swap / Jupiter)
`fuego swap` supports **any token tradable on Jupiter**, including:
- SOL, USDC, USDT (above)
- BONK, JUP, PYTH, RAY, ORCA
- Any SPL token with liquidity on Jupiter

See https://jup.ag for full token list.

### Network Support
- **mainnet-beta** - Production Solana network
- **devnet** - Development/testing network
- **testnet** - Solana testnet (limited use)

---

Ready to build autonomous Solana agents? Start with Fuego.
