# Gateway Overview

The Alchemy Agentic Gateway lets agents easily access Alchemy's developer platform, authenticating with SIWE and paying per-request with USDC via the x402 protocol.

## Base URL

```
https://x402.alchemy.com
```

The gateway exposes four API routes:

| Route | Example | Description |
|-------|---------|-------------|
| `/:chainNetwork/v2` | `/eth-mainnet/v2` | Node JSON-RPC + Token API + Transfers API |
| `/:chainNetwork/nft/v3/*` | `/eth-mainnet/nft/v3/getNFTsForOwner?owner=0x...` | NFT API v3 (REST) |
| `/data/v1/*` | `/data/v1/assets/tokens/by-address` | Portfolio API (not chain-specific) |
| `/prices/v1/*` | `/prices/v1/tokens/by-symbol?symbols=ETH` | Prices API (current + historical) |

See [reference](reference.md) for all endpoints, supported chains, and available methods.

## End-to-End Flow

1. **Set up a wallet** — Use an existing Ethereum wallet or generate a new private key.
2. **Fund the wallet** — Load USDC on a supported payment network (Base Mainnet or Base Sepolia for testnet).
3. **Create a SIWE token** — Sign a SIWE message with your private key. This proves wallet ownership.
4. **Send a request** — Call any gateway route with the `Authorization: SIWE <token>` header. For quick queries without an npm project, see the [curl-workflow](curl-workflow.md) for a lightweight curl-based alternative.
5. **Handle 402 Payment Required** — If the gateway returns 402, create an x402 payment from the response and retry with a `Payment-Signature` header.
6. **Receive the result** — After payment, the gateway proxies the request to Alchemy and returns the result. Subsequent requests with the same SIWE token do not require payment again.

## Required npm Packages

```bash
npm install viem siwe @x402/core @x402/evm @x402/fetch
```

| Package | Purpose |
|---------|---------|
| `viem` | Ethereum wallet creation, message signing, account derivation |
| `siwe` | SIWE (Sign-In With Ethereum) message construction |
| `@x402/core` | x402 client, HTTP client, payment payload encoding |
| `@x402/evm` | EVM-specific payment scheme registration (`exact` scheme) |
| `@x402/fetch` | `wrapFetchWithPayment` — auto-handles 402 → sign → retry |