---
name: opensea
description: Query NFT data, trade on the Seaport marketplace, and swap ERC20 tokens across Ethereum, Base, Arbitrum, Optimism, Polygon, and more.
---

# OpenSea API

Query NFT data, trade on the Seaport marketplace, and swap ERC20 tokens across Ethereum, Base, Arbitrum, Optimism, Polygon, and more.

## Quick start

1. Set `OPENSEA_API_KEY` in your environment
2. **Preferred:** Use the `opensea` CLI (`@opensea/cli`) for all queries and operations
3. Alternatively, use the shell scripts in `scripts/` or the MCP server

```bash
export OPENSEA_API_KEY="your-api-key"

# Install the CLI globally (or use npx)
npm install -g @opensea/cli

# Get collection info
opensea collections get boredapeyachtclub

# Get floor price and volume stats
opensea collections stats boredapeyachtclub

# Get NFT details
opensea nfts get ethereum 0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d 1234

# Get best listings for a collection
opensea listings best boredapeyachtclub --limit 5

# Search across OpenSea
opensea search "cool cats"

# Get trending tokens
opensea tokens trending --limit 5

# Get a swap quote
opensea swaps quote \
  --from-chain base --from-address 0x0000000000000000000000000000000000000000 \
  --to-chain base --to-address 0xTokenAddress \
  --quantity 0.02 --address 0xYourWallet
```

## Task guide

> **Recommended:** Use the `opensea` CLI (`@opensea/cli`) as your primary tool. It covers all the operations below with a consistent interface, structured output, and built-in pagination. Install with `npm install -g @opensea/cli` or use `npx @opensea/cli`. The shell scripts in `scripts/` remain available as alternatives.

### Token swaps

OpenSea's API includes a cross-chain DEX aggregator for swapping ERC20 tokens with optimal routing across all supported chains.

| Task | CLI Command | Alternative |
|------|------------|-------------|
| Get swap quote with calldata | `opensea swaps quote --from-chain <chain> --from-address <addr> --to-chain <chain> --to-address <addr> --quantity <qty> --address <wallet>` | `get_token_swap_quote` (MCP) or `opensea-swap.sh` |
| Get trending tokens | `opensea tokens trending [--chains <chains>] [--limit <n>]` | `get_trending_tokens` (MCP) |
| Get top tokens by volume | `opensea tokens top [--chains <chains>] [--limit <n>]` | `get_top_tokens` (MCP) |
| Get token details | `opensea tokens get <chain> <address>` | `get_tokens` (MCP) |
| Search tokens | `opensea search <query> --types token` | `search_tokens` (MCP) |
| Check token balances | `get_token_balances` (MCP) | — |

### Reading NFT data

| Task | CLI Command | Alternative |
|------|------------|-------------|
| Get collection details | `opensea collections get <slug>` | `opensea-collection.sh <slug>` |
| Get collection stats | `opensea collections stats <slug>` | `opensea-collection-stats.sh <slug>` |
| List NFTs in collection | `opensea nfts list-by-collection <slug> [--limit <n>]` | `opensea-collection-nfts.sh <slug> [limit] [next]` |
| Get single NFT | `opensea nfts get <chain> <contract> <token_id>` | `opensea-nft.sh <chain> <contract> <token_id>` |
| List NFTs by wallet | `opensea nfts list-by-account <chain> <address> [--limit <n>]` | `opensea-account-nfts.sh <chain> <address> [limit]` |
| List NFTs by contract | `opensea nfts list-by-contract <chain> <contract> [--limit <n>]` | — |
| Get collection traits | `opensea collections traits <slug>` | — |
| Get contract details | `opensea nfts contract <chain> <address>` | — |
| Refresh NFT metadata | `opensea nfts refresh <chain> <contract> <token_id>` | — |

### Marketplace queries

| Task | CLI Command | Alternative |
|------|------------|-------------|
| Get best listings for collection | `opensea listings best <slug> [--limit <n>]` | `opensea-best-listing.sh <slug> <token_id>` |
| Get best listing for specific NFT | `opensea listings best-for-nft <slug> <token_id>` | `opensea-best-listing.sh <slug> <token_id>` |
| Get best offer for NFT | `opensea offers best-for-nft <slug> <token_id>` | `opensea-best-offer.sh <slug> <token_id>` |
| List all collection listings | `opensea listings all <slug> [--limit <n>]` | `opensea-listings-collection.sh <slug> [limit]` |
| List all collection offers | `opensea offers all <slug> [--limit <n>]` | `opensea-offers-collection.sh <slug> [limit]` |
| Get collection offers | `opensea offers collection <slug> [--limit <n>]` | `opensea-offers-collection.sh <slug> [limit]` |
| Get trait offers | `opensea offers traits <slug> --type <type> --value <value>` | — |
| Get order by hash | — | `opensea-order.sh <chain> <order_hash>` |

### Marketplace actions (POST)

| Task | Script |
|------|--------|
| Get fulfillment data (buy NFT) | `opensea-fulfill-listing.sh <chain> <order_hash> <buyer>` |
| Get fulfillment data (accept offer) | `opensea-fulfill-offer.sh <chain> <order_hash> <seller> <contract> <token_id>` |
| Generic POST request | `opensea-post.sh <path> <json_body>` |

### Search

| Task | CLI Command |
|------|------------|
| Search collections | `opensea search <query> --types collection` |
| Search NFTs | `opensea search <query> --types nft` |
| Search tokens | `opensea search <query> --types token` |
| Search accounts | `opensea search <query> --types account` |
| Search multiple types | `opensea search <query> --types collection,nft,token` |
| Search on specific chain | `opensea search <query> --chains base,ethereum` |

### Events and monitoring

| Task | CLI Command | Alternative |
|------|------------|-------------|
| List recent events | `opensea events list [--event-type <type>] [--limit <n>]` | — |
| Get collection events | `opensea events by-collection <slug> [--event-type <type>]` | `opensea-events-collection.sh <slug> [event_type] [limit]` |
| Get events for specific NFT | `opensea events by-nft <chain> <contract> <token_id>` | — |
| Get events for account | `opensea events by-account <address>` | — |
| Stream real-time events | — | `opensea-stream-collection.sh <slug>` (requires websocat) |

Event types: `sale`, `transfer`, `mint`, `listing`, `offer`, `trait_offer`, `collection_offer`

### Accounts

| Task | CLI Command |
|------|------------|
| Get account details | `opensea accounts get <address>` |

### Generic requests

| Task | Script |
|------|--------|
| Any GET endpoint | `opensea-get.sh <path> [query]` |
| Any POST endpoint | `opensea-post.sh <path> <json_body>` |

## Buy/Sell workflows

### Buying an NFT

1. Find the NFT and check its listing:
   ```bash
   ./scripts/opensea-best-listing.sh cool-cats-nft 1234
   ```

2. Get the order hash from the response, then get fulfillment data:
   ```bash
   ./scripts/opensea-fulfill-listing.sh ethereum 0x_order_hash 0x_your_wallet
   ```

3. The response contains transaction data to execute on-chain

### Selling an NFT (accepting an offer)

1. Check offers on your NFT:
   ```bash
   ./scripts/opensea-best-offer.sh cool-cats-nft 1234
   ```

2. Get fulfillment data for the offer:
   ```bash
   ./scripts/opensea-fulfill-offer.sh ethereum 0x_offer_hash 0x_your_wallet 0x_nft_contract 1234
   ```

3. Execute the returned transaction data

### Creating listings/offers

Creating new listings and offers requires wallet signatures. Use `opensea-post.sh` with the Seaport order structure - see `references/marketplace-api.md` for full details.

## OpenSea CLI (`@opensea/cli`)

The [OpenSea CLI](https://github.com/ProjectOpenSea/opensea-cli) is the recommended way for AI agents to interact with OpenSea. It provides a consistent command-line interface and a programmatic TypeScript/JavaScript SDK.

### Installation

```bash
# Install globally
npm install -g @opensea/cli

# Or use without installing
npx @opensea/cli collections get mfers
```

### Authentication

```bash
# Set via environment variable (recommended)
export OPENSEA_API_KEY="your-api-key"
opensea collections get mfers

# Or pass inline
opensea --api-key your-api-key collections get mfers
```

### CLI Commands

| Command | Description |
|---|---|
| `collections` | Get, list, stats, and traits for NFT collections |
| `nfts` | Get, list, refresh metadata, and contract details for NFTs |
| `listings` | Get all, best, or best-for-nft listings |
| `offers` | Get all, collection, best-for-nft, and trait offers |
| `events` | List marketplace events (sales, transfers, mints, etc.) |
| `search` | Search collections, NFTs, tokens, and accounts |
| `tokens` | Get trending tokens, top tokens, and token details |
| `swaps` | Get swap quotes for token trading |
| `accounts` | Get account details |

Global options: `--api-key`, `--chain` (default: ethereum), `--format` (json/table/toon), `--base-url`, `--timeout`, `--verbose`

### Output Formats

- **JSON** (default): Structured output for agents and scripts
- **Table**: Human-readable tabular output (`--format table`)
- **TOON**: Token-Oriented Object Notation, uses ~40% fewer tokens than JSON — ideal for LLM/AI agent context windows (`--format toon`)

```bash
# JSON output (default)
opensea collections stats mfers

# Human-readable table
opensea --format table collections stats mfers

# Compact TOON format (best for AI agents)
opensea --format toon tokens trending --limit 5
```

### Pagination

All list commands support cursor-based pagination with `--limit` and `--next`:

```bash
# First page
opensea collections list --limit 5

# Pass the "next" cursor from the response to get the next page
opensea collections list --limit 5 --next "LXBrPTEwMDA..."
```

### Programmatic SDK

The CLI also exports a TypeScript/JavaScript SDK for use in scripts and applications:

```typescript
import { OpenSeaCLI, OpenSeaAPIError } from "@opensea/cli"

const client = new OpenSeaCLI({ apiKey: process.env.OPENSEA_API_KEY })

const collection = await client.collections.get("mfers")
const { nfts } = await client.nfts.listByCollection("mfers", { limit: 5 })
const { listings } = await client.listings.best("mfers", { limit: 10 })
const { asset_events } = await client.events.byCollection("mfers", { eventType: "sale" })
const { tokens } = await client.tokens.trending({ chains: ["base"], limit: 5 })
const results = await client.search.query("mfers", { limit: 5 })

// Swap quote
const { quote, transactions } = await client.swaps.quote({
  fromChain: "base",
  fromAddress: "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
  toChain: "base",
  toAddress: "0x3ec2156d4c0a9cbdab4a016633b7bcf6a8d68ea2",
  quantity: "1000000",
  address: "0xYourWalletAddress",
})

// Error handling
try {
  await client.collections.get("nonexistent")
} catch (error) {
  if (error instanceof OpenSeaAPIError) {
    console.error(error.statusCode)   // e.g. 404
    console.error(error.responseBody) // raw API response
    console.error(error.path)         // request path
  }
}
```

### TOON Format for AI Agents

TOON (Token-Oriented Object Notation) is a compact serialization format that uses ~40% fewer tokens than JSON, making it ideal for piping CLI output into LLM context windows:

```bash
opensea --format toon tokens trending --limit 3
```

Example output:
```
tokens[3]{name,symbol,chain,market_cap,price_usd}:
  Ethereum,ETH,ethereum,250000000000,2100.50
  Bitcoin,BTC,bitcoin,900000000000,48000.00
  Solana,SOL,solana,30000000000,95.25
next: abc123
```

TOON is also available programmatically:

```typescript
import { formatToon } from "@opensea/cli"

const data = await client.tokens.trending({ limit: 5 })
console.log(formatToon(data))
```

### CLI Exit Codes

- `0` - Success
- `1` - API error
- `2` - Authentication error

---

## Shell Scripts Reference

The `scripts/` directory contains shell scripts that wrap the OpenSea REST API directly using `curl`. These are an alternative to the CLI above.

### NFT & Collection Scripts
| Script | Purpose |
|--------|---------|
| `opensea-get.sh` | Generic GET (path + optional query) |
| `opensea-post.sh` | Generic POST (path + JSON body) |
| `opensea-collection.sh` | Fetch collection by slug |
| `opensea-collection-stats.sh` | Fetch collection statistics |
| `opensea-collection-nfts.sh` | List NFTs in collection |
| `opensea-nft.sh` | Fetch single NFT by chain/contract/token |
| `opensea-account-nfts.sh` | List NFTs owned by wallet |

### Marketplace Scripts
| Script | Purpose |
|--------|---------|
| `opensea-listings-collection.sh` | All listings for collection |
| `opensea-listings-nft.sh` | Listings for specific NFT |
| `opensea-offers-collection.sh` | All offers for collection |
| `opensea-offers-nft.sh` | Offers for specific NFT |
| `opensea-best-listing.sh` | Lowest listing for NFT |
| `opensea-best-offer.sh` | Highest offer for NFT |
| `opensea-order.sh` | Get order by hash |
| `opensea-fulfill-listing.sh` | Get buy transaction data |
| `opensea-fulfill-offer.sh` | Get sell transaction data |

### Token Swap Scripts
| Script | Purpose |
|--------|---------|
| `opensea-swap.sh` | **Swap tokens via OpenSea MCP** |

### Monitoring Scripts
| Script | Purpose |
|--------|---------|
| `opensea-events-collection.sh` | Collection event history |
| `opensea-stream-collection.sh` | Real-time WebSocket events |

## Supported chains

`ethereum`, `matic`, `arbitrum`, `optimism`, `base`, `avalanche`, `klaytn`, `zora`, `blast`, `sepolia`

## References

- [OpenSea CLI GitHub](https://github.com/ProjectOpenSea/opensea-cli) - Full CLI and SDK documentation
- [CLI Reference](https://github.com/ProjectOpenSea/opensea-cli/blob/main/docs/cli-reference.md) - Complete command reference
- [SDK Reference](https://github.com/ProjectOpenSea/opensea-cli/blob/main/docs/sdk.md) - Programmatic SDK API
- [CLI Examples](https://github.com/ProjectOpenSea/opensea-cli/blob/main/docs/examples.md) - Real-world usage examples
- `references/rest-api.md` - REST endpoint families and pagination
- `references/marketplace-api.md` - Buy/sell workflows and Seaport details
- `references/stream-api.md` - WebSocket event streaming
- `references/seaport.md` - Seaport protocol and NFT purchase execution
- `references/token-swaps.md` - **Token swap workflows via MCP**

## OpenSea MCP Server

An official OpenSea MCP server provides direct LLM integration for token swaps and NFT operations. When enabled, Claude can execute swaps, query token data, and interact with NFT marketplaces directly.

**Setup:**

1. Go to the [OpenSea Developer Portal](https://opensea.io/settings/developer) and verify your email
2. Generate a new API key for REST API access
3. Generate a separate MCP token for the MCP server

Add to your MCP config:
```json
{
  "mcpServers": {
    "opensea": {
      "url": "https://mcp.opensea.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

Or use the inline token format: `https://mcp.opensea.io/YOUR_MCP_TOKEN/mcp`

### Token Swap Tools
| MCP Tool | Purpose |
|----------|---------|
| `get_token_swap_quote` | **Get swap calldata for token trades** |
| `get_token_balances` | Check wallet token holdings |
| `search_tokens` | Find tokens by name/symbol |
| `get_trending_tokens` | Hot tokens by momentum |
| `get_top_tokens` | Top tokens by 24h volume |
| `get_tokens` | Get detailed token info |

### NFT Tools
| MCP Tool | Purpose |
|----------|---------|
| `search_collections` | Search NFT collections |
| `search_items` | Search individual NFTs |
| `get_collections` | Get detailed collection info |
| `get_items` | Get detailed NFT info |
| `get_nft_balances` | List NFTs owned by wallet |
| `get_trending_collections` | Trending NFT collections |
| `get_top_collections` | Top collections by volume |
| `get_activity` | Trading activity for collections/items |
| `get_upcoming_drops` | Upcoming NFT mints |

### Profile & Utility Tools
| MCP Tool | Purpose |
|----------|---------|
| `get_profile` | Wallet profile with holdings/activity |
| `account_lookup` | Resolve ENS/address/username |
| `get_chains` | List supported chains |
| `search` | AI-powered natural language search |
| `fetch` | Get full details by entity ID |

---

## Token Swaps via MCP

OpenSea MCP supports ERC20 token swaps across supported DEXes - not just NFTs!

### Get Swap Quote
```bash
mcporter call opensea.get_token_swap_quote --args '{
  "fromContractAddress": "0x0000000000000000000000000000000000000000",
  "fromChain": "base",
  "toContractAddress": "0xb695559b26bb2c9703ef1935c37aeae9526bab07",
  "toChain": "base",
  "fromQuantity": "0.02",
  "address": "0xYourWalletAddress"
}'
```

**Parameters:**
- `fromContractAddress`: Token to swap from (use `0x0000...0000` for native ETH)
- `toContractAddress`: Token to swap to
- `fromChain` / `toChain`: Chain identifiers
- `fromQuantity`: Amount in human-readable units (e.g., "0.02" for 0.02 ETH)
- `address`: Your wallet address

**Response includes:**
- `swapQuote`: Price info, fees, slippage impact
- `swap.actions[0].transactionSubmissionData`: Ready-to-use calldata

### Execute the Swap
```javascript
import { createWalletClient, http } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';

// Extract from swap quote response
const txData = response.swap.actions[0].transactionSubmissionData;

const wallet = createWalletClient({ 
  account: privateKeyToAccount(PRIVATE_KEY), 
  chain: base, 
  transport: http() 
});

const hash = await wallet.sendTransaction({
  to: txData.to,
  data: txData.data,
  value: BigInt(txData.value)
});
```

### Check Token Balances
```bash
mcporter call opensea.get_token_balances --args '{
  "address": "0xYourWallet",
  "chains": ["base", "ethereum"]
}'
```

## Generating a wallet

To execute swaps or buy NFTs, you need an Ethereum wallet (private key + address).

### Using Node.js
```javascript
import crypto from 'crypto';
import { privateKeyToAccount } from 'viem/accounts';

const privateKey = '0x' + crypto.randomBytes(32).toString('hex');
const account = privateKeyToAccount(privateKey);

console.log('Private Key:', privateKey);
console.log('Address:', account.address);
```

### Using OpenSSL
```bash
# Generate private key
PRIVATE_KEY="0x$(openssl rand -hex 32)"
echo "Private Key: $PRIVATE_KEY"

# Derive address (requires node + viem)
node --input-type=module -e "
import { privateKeyToAccount } from 'viem/accounts';
console.log('Address:', privateKeyToAccount('$PRIVATE_KEY').address);
"
```

### Using cast (Foundry)
```bash
cast wallet new
```

**Important:** Store private keys securely. Never commit them to git or share publicly.

## Requirements

- `OPENSEA_API_KEY` environment variable (for CLI, SDK, and REST API scripts)
- `OPENSEA_MCP_TOKEN` environment variable (for MCP server, separate from API key)
- Node.js >= 18.0.0 (for `@opensea/cli`)
- `curl` for REST shell scripts
- `websocat` (optional) for Stream API
- `jq` (recommended) for parsing JSON responses from shell scripts

Get both credentials at [opensea.io/settings/developer](https://opensea.io/settings/developer).
