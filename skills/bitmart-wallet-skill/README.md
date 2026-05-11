# bitmart-wallet-ai

BitMart Web3 Wallet skill for AI agents — token search, market data, smart money tracking, address balances, and swap quotes across 5 chains.

## Capabilities

- **Token Search**: Fuzzy search tokens by name or symbol across supported chains
- **Chain Details**: Query chain information by chain ID (Solana, BSC, Ethereum, Arbitrum, Base)
- **Token Info**: Get complete token details by platform token ID
- **K-Line Chart**: Historical candlestick data (Solana tokens only)
- **Hot Token Ranking**: Trending token rankings by time window
- **xStock Ranking**: US stock mapped token rankings
- **Smart Money P&L Ranking**: 7-day smart money profit/loss rankings with filters
- **Smart Money Address Analysis**: Holdings, transaction history, profit analysis for a given wallet address
- **Address Balance**: Token balance list for a wallet address
- **Address Recent Transactions**: Recent transaction history grouped by date
- **Swap Quote**: Token swap price quotes (quote only, no execution)
- **Batch Price**: Batch query token prices

## Supported Chains

| Chain | Chain ID |
|-------|----------|
| Solana | 2001 |
| BSC | 2002 |
| Ethereum | 2003 |
| Arbitrum | 2004 |
| Base | 2007 |

## API Endpoints

| Category | Count | Auth |
|----------|-------|------|
| Token & Chain Data | 3 endpoints | NONE |
| Market Data | 3 endpoints | NONE |
| Smart Money | 2 endpoints | NONE |
| Asset & Swap | 4 endpoints | NONE |

**Total: 12 endpoints**

## Authentication

No API key required. All endpoints accept direct HTTP POST requests.

## Rate Limit

15 requests per second per IP.

## Usage

Ask your AI agent in natural language:

```text
What's the price of TRUMP on Solana?
```

```text
Show me the top smart money wallets by 7-day profit
```

```text
Check token balances for address 0x4396e479fe8270487f301b7c5cc92e8cd59ef91a on BSC
```

```text
Show recent transactions for address 2h4hhjuWxEo4uyzGAxzWvpdSotAozchjpfyefvVWvi8R on Solana
```

```text
How much SOL do I get for swapping 100 USDT on Solana?
```

```text
What are the hot tokens in the last 24 hours?
```

## Related Skills

- [bitmart-exchange-spot](../bitmart-exchange-spot/) — Spot trading
- [bitmart-exchange-futures](../bitmart-exchange-futures/) — Futures / contract trading
