# API Services — Detailed Usage

For the summary table with base URLs, see the main SKILL.md.

---

## Super API

Real-time on-chain Super Token balances.

`GET /super-token-balance?chain={chainId}&token={tokenAddress}&account={accountAddress}`

Returns connected/unconnected balances, net flow rate, and underlying token
details.

Wrapped by `scripts/balance.mjs` — prefer the script for one-off lookups.

[Swagger](https://superapi.kazpi.com/)

## CMS

Can return unlisted Super Tokens (not just those in the tokenlist). Can get
CoinGecko IDs for price lookups.

[Swagger](https://cms.superfluid.pro/api-docs) ·
[OpenAPI](https://cms.superfluid.pro/openapi.json) ·
[Repo](https://github.com/superfluid-org/superfluid.pro/tree/main/cms)

## Points

SUP points campaigns (Stack.so replacement). Same repo as CMS.

[API docs](https://cms.superfluid.pro/points/api-docs) ·
[OpenAPI](https://cms.superfluid.pro/points/openapi.json)

## Accounting

Splits per-second streams into chunked granularity (e.g. streamed per day).
Handles CFA and ERC-20 transfers only — **no GDA support**.

[Swagger](https://accounting.superfluid.dev/v1/swagger) ·
[Repo](https://github.com/superfluid-org/accounting-api)

## Allowlist

`GET /api/allowlist/{account}/{chainId}` — check if an account is
allowlisted for automations (vesting, flow scheduling, auto-wrap).

## Whois

Resolves across ENS, AF, Farcaster, Lens, etc.
- `GET /api/resolve/{address}` — address → profile/name
- `GET /api/reverse-resolve/{handle}` — name/handle → address

GOTCHA: despite the names, `resolve` takes an address and `reverse-resolve`
takes a name.

## Token Prices

Simpler alternative to CMS for price lookups. Provides prices for all listed
SuperTokens where the token (or underlying) is known to CoinGecko.

Endpoint: `GET /v1/{canonical-network-name}/{token-address}`

[Repo](https://github.com/d10r/sf-token-prices-api/)

## Claim Programs

Returns all SUP reward programs across seasons. Each entry has `appId`,
`name`, `season`, `category`, `url`, and a nested `program.onchainInfo` with
`poolAddress`, `fundingFlowRate`, `totalAllocated`, `totalClaimed`,
`totalMembers`, and funding timestamps.

The response uses tRPC's `superjson` format (top-level `json` + `meta` keys).
Filter by `program.onchainInfo.isFundingFinished` to find active campaigns.
