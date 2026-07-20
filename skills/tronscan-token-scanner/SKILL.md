---
name: tronscan-token-scanner
description: |
  Scan TRON tokens for total supply, market cap, price, rating, launch time, holders.
  Includes TRX: TRX price, TRX supply, market cap, daily net change, and supply trend.
  Use when user asks "how is this token", "USDT price", "top holders", "TRX market cap", "token due diligence", "supply of contract address", or provides a token contract address.
  Do NOT use for token list or trending rankings (use tronscan-token-list or tronscan-data-insights).
metadata:
  author: tronscan-mcp
  version: "1.0"
  mcp-server: https://mcp.tronscan.org/mcp
---

# Token Scanner

## Overview

| Tool | Function | Use Case |
|------|----------|----------|
| getTokenPrice | Token price (default TRX) | TRX price or any token price |
| getFunds | TRX supply & market | TRX supply, market cap, burn |
| getTrxVolume | TRX history | TRX historical price, volume, market cap |
| getTurnover | TRX turnover | TRX turnover, supply, revenue, mint/burn |
| getTrxVolumeSourceList | TRX price sources | TRX price data source list |
| getTrc20TokenDetail | TRC20/721/1155 detail | Name, symbol, supply, holders, price |
| getTrc10TokenDetail | TRC10 detail | Name, issuer, supply, description |
| getTrc20TokenHolders | TRC20/721/1155 holders | Holder list, balance, share |
| getTrc10TokenHolders | TRC10 holders | TRC10 holder list |
| getTokenPositionDistribution | Position distribution | Holder count by balance range |
| getTrc20TotalSupply | TRC20 supply | Circulating / total supply |
| getTrc721Inventory | TRC721 inventory | NFT contract inventory |
| getTrc1155Inventory | TRC1155 inventory | Multi-token contract inventory |
| getToken10Transfers | TRC10 transfers | TRC10 token transfer records for an address |
| getTokenAnalysis | Token analysis | Token transfer and holder analysis data |
| getTokenAssetValueInfo | Asset value chart | Asset value change chart for a token in an account |
| getTokenBalanceFlow | Balance flow | Token balance flow records for an account |
| getTokenTransferAnalysis | Transfer amount | Transfer amount of core tokens on TRON |
| getTokenTvc | Token TVC | On-chain Total Value Captured (TVC) data |
| getTrc1155TokenInventory | TRC1155 token holders | Holder info for a specific token ID in TRC1155 |
| getTrc20TransferCount | TRC20 transfer count | Transfer count stats for a TRC20 token in an account |
| getTrc721Transfers | TRC721 transfers | Transfer history for a specific TRC721 NFT |
| getTrxTransfers | TRX transfers | TRX transfer records for an address |

## Use Cases

1. **TRX price, TRX supply, TRX market cap**: Use `getTokenPrice` (default token is TRX) for current price; use `getFunds` for real-time TRX supply, market cap, and burn; use `getTrxVolume` for historical price/volume; use `getTurnover` for supply, mint/burn, turnover.
2. **Token Overview**: Get name, symbol, supply, holders, price via `getTrc20TokenDetail` or `getTrc10TokenDetail`.
3. **Holder Analysis**: Use `getTrc20TokenHolders` / `getTrc10TokenHolders` for list; use `getTokenPositionDistribution` for concentration.
4. **Price & Valuation**: Use `getTokenPrice` and detail tools for market cap.
5. **Supply**: Use `getTrc20TotalSupply` for TRC20 supply/circulation.
6. **Launch Time**: Available in token detail responses (creation/deploy time).
7. **NFT / Multi-token**: Use `getTrc721Inventory` and `getTrc1155Inventory` for inventory.

## MCP Server

- **Prerequisite**: [TronScan MCP Guide](https://mcpdoc.tronscan.org)

## Tools

### getTokenPrice

- **API**: `getTokenPrice` — Get token price (default: TRX)
- **Use when**: User asks for "TRX price", "current TRX price", or any token price.
- **Note**: Omit or pass default to get TRX price.

### getFunds

- **API**: `getFunds` — Get TRX real-time supply, market cap, and burn data
- **Use when**: User asks for "TRX supply", "TRX circulation", "TRX market cap", or "TRX burn".

### getTrxVolume

- **API**: `getTrxVolume` — Get TRX historical price, volume, and market cap data
- **Use when**: User asks for "TRX history", "TRX price history", or "TRX volume trend".
- **Input**: startTimestamp, endTimestamp, limit, source.

### getTurnover

- **API**: `getTurnover` — Get TRX turnover, supply, revenue, mint and burn statistics
- **Use when**: User asks for "TRX turnover", "TRX mint/burn", or "TRX supply change".
- **Input**: from, start, end, type (as per API).

### getTrxVolumeSourceList

- **API**: `getTrxVolumeSourceList` — Get TRX price data source list
- **Use when**: User asks for "TRX price source" or "where TRX price comes from".

### getTrc20TokenDetail

- **API**: `getTrc20TokenDetail` — Get TRC20/TRC721/TRC1155 token details (name, symbol, supply, holders, price, etc.)
- **Use when**: User asks for "token info", "token details", or specifies a contract address.
- **Input**: Contract address (and token type if needed).

### getTrc10TokenDetail

- **API**: `getTrc10TokenDetail` — Get TRC10 token details (name, abbreviation, issuer, supply, description, etc.)
- **Use when**: Token is TRC10 (native asset).

### getTrc20TokenHolders / getTrc10TokenHolders

- **API**: `getTrc20TokenHolders` — Get TRC20/TRC721/TRC1155 holder list (address, balance, share); `getTrc10TokenHolders` — Get TRC10 holder list
- **Use when**: User asks for "token holders" or "top holders".

### getTokenPositionDistribution

- **API**: `getTokenPositionDistribution` — Get token position distribution (holder count and share by balance range)
- **Use when**: User asks for "holder distribution" or "concentration".

### getTrc20TotalSupply

- **API**: `getTrc20TotalSupply` — Get TRC20 circulating supply and total supply
- **Use when**: User asks for "supply" or "circulation" of a TRC20.

### getToken10Transfers

- **API**: `getToken10Transfers` — Get TRC10 token transfer records for an address
- **Use when**: User asks for "TRC10 transfer history" for a specific token and address.
- **Input**: `address`, `trc10Id` (both required); optional pagination and filters. Note: start+limit ≤ 10000.

### getTokenAnalysis

- **API**: `getTokenAnalysis` — Get analysis data for token transfers and holders
- **Use when**: User asks for "token activity analysis", "transfer trends", or "holder stats over time".
- **Input**: Optional `token`, `startDay`, `endDay`, `type`.

### getTokenAssetValueInfo

- **API**: `getTokenAssetValueInfo` — Get asset value change chart for a specific token in an account
- **Use when**: User asks for "how has the value of my token changed" or "token asset value history".
- **Input**: `accountAddress`, `tokenAddress` (both required); optional `startTime`, `endTime`.

### getTokenBalanceFlow

- **API**: `getTokenBalanceFlow` — Get balance flow change records for a token in an account
- **Use when**: User asks for "token balance history" or "how my token balance changed over time".
- **Input**: `accountAddress`, `tokenAddress` (both required); optional `endTime`.

### getTokenTransferAnalysis

- **API**: `getTokenTransferAnalysis` — Get transfer amount of core tokens on TRON
- **Use when**: User asks for "token transfer volume", "core token transfer analysis".
- **Input**: Optional `token`, `days`.

### getTokenTvc

- **API**: `getTokenTvc` — Get token on-chain Total Value Captured (TVC) data (default last 7 days)
- **Use when**: User asks for "token TVC", "on-chain value captured", or "token economic activity".
- **Input**: Optional `startTime`, `endTime`.

### getTrc1155TokenInventory

- **API**: `getTrc1155TokenInventory` — Get holder info for a specific token ID in a TRC1155 contract
- **Use when**: User asks for "who holds token ID X in this TRC1155 contract".
- **Input**: `contract`, `tokenId` (both required); optional `start`, `limit`. Note: start+limit ≤ 10000.

### getTrc20TransferCount

- **API**: `getTrc20TransferCount` — Get transfer count statistics for a TRC20 token in an account
- **Use when**: User asks for "how many times has this address transferred this token".
- **Input**: `accountAddress`, `tokenAddress` (both required).

### getTrc721Transfers

- **API**: `getTrc721Transfers` — Get transfer history for a specific TRC721 NFT token
- **Use when**: User asks for "NFT transfer history" for a specific contract and token ID.
- **Input**: `contract`, `tokenId` (both required); optional `start`, `limit`. Note: start+limit ≤ 10000.

### getTrxTransfers

- **API**: `getTrxTransfers` — Get TRX transfer records for an address
- **Use when**: User asks for "TRX transfer history", "TRX in/out", or "TRX transaction records".
- **Input**: `address` (required); optional `direction`, `startTimestamp`, `endTimestamp`, `start`, `limit`. Note: start+limit ≤ 10000.

## Token Risk Fields

TronScan token APIs return several risk-related fields. **No single field is conclusive — always combine multiple signals before drawing a safety conclusion.**

### tokenLevel

API field name: `tokenLevel` (string `"0"`–`"4"`).

| Value | Rating | Meaning |
|-------|--------|---------|
| `"0"` | Unknown | Cannot be determined |
| `"1"` | Neutral | Neutral |
| `"2"` | OK | Passes basic security checks |
| `"3"` | Suspicious | Suspicious |
| `"4"` | Unsafe | Unsafe |

Always convert to the rating label before presenting to users. Never show the raw numeric string (e.g. show `"OK"`, not `"2"`).

`tokenLevel` is an **auxiliary signal only**. A token rated `"2"` (OK) may still be a counterfeit — always cross-verify with the fields below.

### tokenCanShow

Boolean. Indicates whether TronScan considers this token suitable for display. `false` means TronScan has flagged the token as unsuitable for general display (e.g. spam, extreme risk). **`tokenCanShow` is independent of `tokenLevel`** — do not infer one from the other.

### blueTag

String. The name of the recognized project this token officially belongs to (e.g. `"Tether"`, `"TRON Foundation"`). An empty string means no project association. A non-empty `blueTag` is a strong positive trust signal.

### publicTag

String. A public category label assigned to the token by TronScan (e.g. `"Stablecoin"`, `"DeFi"`). An empty string means no public tag. A non-empty value indicates the token is a known, categorized asset.

### vip

Boolean. Indicates whether the token or its project has VIP/premium status on TronScan. Treat as a secondary positive trust signal when `true`.

### red_tag

Returned by the `/api/security/account/data` endpoint. String enum:

| Value | Meaning |
|-------|---------|
| `"Suspicious"` | The address or token has been flagged as suspicious / potentially fraudulent |
| `""` (empty) | No fraud warning |

If `red_tag` is `"Suspicious"`, treat it as the strongest negative signal and warn the user immediately.

## Recommended Risk Judgment Order

When assessing whether a token is safe or official, apply signals in this priority order:

1. **red_tag** — Highest priority. If `"Suspicious"`, the address/token has been flagged for fraud or scam — warn the user immediately.
2. **vip** — VIP/premium project indicator.
4. **blueTag / publicTag** — Whether the token is affiliated with a known project or public category.
5. **tokenLevel** — Auxiliary. Use for additional context, not as primary evidence.
6. **Holder concentration** — Use `getTokenPositionDistribution`; a top-heavy distribution is a red flag.

**Rule**: Never declare a token "safe" or "official" based on a single field.

### Example: Counterfeit Token Scenario

> User: "Is this USDT contract safe?"

A malicious actor may deploy a token named "Tether USD" with symbol "USDT" that passes `tokenLevel = "2"` (OK). Correct check:
1. `red_tag` — Not flagged (new token, not yet reported)
2. `blueTag` — Empty string (no project affiliation)
3. `publicTag` — Empty string
4. **Conclusion**: Despite `tokenLevel = "2"`, this token is suspicious. The real USDT has `blueTag: "Tether"`. Advise the user to verify the contract address matches the known USDT address (`TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t`).

## Workflow: Query Token Info

> User: "What is USDT?" or "Tell me about this token" (provides token name/symbol as text)

1. **Resolve text to address** — If user provides name/symbol (e.g. "USDT", "BTT"), use **tronscan-search** `search` with `term` and `type: "token"` to get contract address (`token_id` in result). If user already provides contract address, skip this step.
2. **tronscan-token-scanner** — Call `getTrc20TokenDetail` (or `getTrc10TokenDetail`) with the contract address / asset ID from step 1.
3. **Convert tokenLevel** — Map raw `tokenLevel` (0–4) to rating text before presenting:
   - `"0"` → Unknown | `"1"` → Neutral | `"2"` → OK | `"3"` → Suspicious | `"4"` → Unsafe
4. **Optional** — `getTrc20TokenHolders` / `getTokenPositionDistribution` for holder list; `getTokenPrice` for USD conversion if values are in TRX.
5. **Present to user** — Return name, symbol, supply, holders, price, market cap (prefer USD), and **rating** (converted text, not raw level).

**Key**: Never show raw `tokenLevel` (e.g. `"2"`) to users; always convert to rating label (e.g. `"OK"`). Also check `tokenCanShow`, `blueTag`, and `red_tag` before drawing safety conclusions — see **Token Risk Fields** section.

## Workflow: Query TRX Info

> User: "What is TRX?" or "TRX price/supply/market cap/detail/info" (queries TRON native token)

1. **tronscan-token-scanner** — Call `getTrc10TokenDetail` with **asset ID = 0**. TRX is TRON's native token (TRC10), id = 0.
2. **Enrich with** — `getFunds` (supply, market cap, burn); `getTokenPrice` (current USD price); `getTurnover` (turnover, mint/burn); `getTrxVolume` (24h volume, price change, historical); `getTrc10TokenHolders` (holder count). For total/yesterday transfer count, use **tronscan-transaction-info** `getTransactionStatistics` or **tronscan-data-insights** if needed.
3. **Present to user** — Return a rich summary including:
   - **Basic**: name, symbol, description, issuance time
   - **Supply**: total supply, circulating supply
   - **Price**: current price (USD), 24h change
   - **Market**: market cap (USD), 24h volume
   - **Chain**: burn amount, turnover, mint/burn stats (if available)
   - **Activity**: holders, total transfer count, yesterday's transfer count
   - **Links**: whitepaper, media links (if available)

**Note**: No search step needed; TRX is always asset ID 0.

## Workflow: Search by Name, Then Analyze

> User: "What is the USDT contract address on TRON? Who are the top holders?"

1. **tronscan-search** — Use `search` with `term: "USDT"`, `type: "token"` to resolve name/symbol to TRC20 contract address (`token_id` in result).
2. **tronscan-token-scanner** — Call `getTrc20TokenDetail` with contract address for supply, holders, price, market cap, rating.
3. **tronscan-token-scanner** — `getTrc20TokenHolders` / `getTokenPositionDistribution` for top holders and concentration.
4. Optional **tronscan-account-profiler** — For top holder addresses, call `getAccountDetail` or `getTokenAssetOverview` for wallet profile.

**Data handoff**: Contract address from step 1 feeds into tronscan-token-scanner in steps 2–3; holder addresses from step 3 feed into tronscan-account-profiler in step 4.

## Troubleshooting

- **MCP connection failed**: If you see "Connection refused", verify TronScan MCP is connected in Settings > Extensions.
- **API rate limit / 429**: TronScan API has call count and frequency limits when no API key is used. If you encounter rate limiting or 429 errors, go to [TronScan Developer API](https://tronscan.org/#/developer/api) to apply for an API key, then add it to your MCP configuration and retry.

### Invalid contract address or asset ID
TRC20/TRC721/TRC1155 require contract address; TRC10 requires asset ID. Do not mix them.

## Notes

- For TRX: use `getTokenPrice`, `getFunds`, `getTrxVolume`, `getTurnover` for price, supply, market cap, and trends.
- For "rating" or risk metrics, combine with contract analysis (contract verification, holders, distribution).
- TRC20/TRC721/TRC1155 use contract address; TRC10 uses asset ID.
- **market_cap, price, volume units**: Check whether values are in USD or TRX. Prefer returning USD to users. If only TRX is available, query TRX price via `getTokenPrice` and convert to USD before returning.
