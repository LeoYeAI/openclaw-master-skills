---
name: payai
description: Discover, pay for, and sell agent services over the x402 protocol using the PayAI Network. Browse the PayAI Bazaar — a live directory of paid APIs and agent services — pay any of them autonomously with USDC on Solana or EVM chains via the open PayAI facilitator, and expose your own endpoints as x402-monetized resources so other agents pay you. Use when an agent needs to find a paid tool/API/service, settle an x402 payment across chains, or accept crypto payments for the work it does.
metadata: {"openclaw":{"emoji":"🌐","homepage":"https://payai.network","primaryEnv":"SOLANA_PRIVATE_KEY"}}
---

# PayAI — The Payment Network for Autonomous Agents

## What is PayAI?

**PayAI** is an open payment network that lets AI agents **find, pay for, and sell** services to each other using the [x402 protocol](https://x402.gitbook.io/x402) — HTTP-native payments settled in stablecoins (USDC). It has three parts an agent cares about:

1. **The facilitator** (`https://facilitator.payai.network`) — a neutral, no-signup service that **verifies** and **settles** x402 payments across many chains. It settles **Solana** (and pays the gas for you) and **9 EVM chains**.
2. **The Bazaar** (`/discovery/resources`) — a live, queryable directory of paid x402 resources: APIs, tools, and agent services you can call and pay for right now.
3. **Merchant support** — libraries and facilitator endpoints that let *your* agent price an endpoint in USDC and get paid by other agents.

Think of PayAI as the marketplace + settlement layer. This skill covers **discovering** services and **selling** yours. For the mechanics of *constructing and signing a payment*, use the companion [`x402`](../x402/) skill.

## When to use this skill

- You need a capability (data, inference, a tool, a physical good) and want to **find an agent/API that sells it**.
- You have an x402 payment to **verify or settle** and need a facilitator.
- You want to know **which chains/assets** are supported before paying.
- You want to **monetize** your own agent or API so other agents pay you in USDC.

## Part 1 — Discover services (the Bazaar)

Query the live directory of paid resources:

```bash
curl -s "https://facilitator.payai.network/discovery/resources?limit=25" | jq
```

The response is a paginated list of resources:

```json
{
  "x402Version": 1,
  "items": [
    {
      "resource": "https://tripadvisor.x402.paysponge.com/api/v1/location/:locationId/details",
      "type": "http",
      "method": "GET",
      "accepts": [
        {
          "scheme": "exact",
          "network": "eip155:8453",
          "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
          "payTo": "0x6302D9e6DBB22fEC3c350551568Bb39B4b35Ad57",
          "amount": "10000",
          "maxTimeoutSeconds": 300
        }
      ],
      "inputSchema": { "type": "http", "method": "GET", "pathParams": { "locationId": "154943" } },
      "outputSchema": { "type": "json", "example": {} },
      "lastUpdated": "2026-07-24T05:18:11.665Z"
    }
  ],
  "pagination": { "limit": 25, "offset": 0 }
}
```

Each item tells you everything needed to call and pay for it:

- **`resource`** — the URL to call (with `:param` path params described in `inputSchema`).
- **`method`** — HTTP verb.
- **`accepts`** — the same payment-requirements array you'd get from a `402` (network, asset, price, `payTo`).
- **`inputSchema` / `outputSchema`** — how to call it and what comes back.

### Workflow: find → pay → use

1. **Search** the Bazaar for a resource that does what you need (filter `items` by keywords in `resource`, or by a `network`/asset you hold).
2. **Read the price** from `accepts[].amount` (base units; USDC = 6 decimals).
3. **Call + pay** using the [`x402`](../x402/) skill — send the request, get a `402`, build the payment, retry with `X-PAYMENT`.

`scripts/discover.mjs` (zero dependencies, Node 18+) fetches the Bazaar and prints a readable table, with optional filtering:

```bash
node scripts/discover.mjs                 # list recent resources
node scripts/discover.mjs --network solana # only Solana-payable resources
node scripts/discover.mjs --query weather  # match resource URL/description
```

## Part 2 — The facilitator API

Base URL: `https://facilitator.payai.network`. No API key, no signup.

### `GET /supported` — which chains & schemes settle

```bash
curl -s https://facilitator.payai.network/supported | jq '.kinds[] | {scheme, network}'
```

Returns the authoritative list. Currently:

| Chain | Networks | x402 versions |
|---|---|---|
| **Solana** | `solana`, `solana-devnet`, `solana:<genesis>` (v2) | v1 + v2 |
| **Base** | `base`, `base-sepolia`, `eip155:8453` | v1 + v2 (incl. `upto`) |
| **Polygon** | `polygon`, `polygon-amoy`, `eip155:137` | v1 + v2 |
| **Arbitrum** | `arbitrum`, `arbitrum-sepolia`, `eip155:42161` | v1 + v2 |
| **Avalanche** | `avalanche`, `avalanche-fuji`, `eip155:43114` | v1 + v2 |
| **Sei** | `sei`, `sei-testnet`, `eip155:1329` | v1 + v2 |
| **X Layer** | `xlayer`, `xlayer-testnet`, `eip155:196` | v1 + v2 |
| **SKALE** | `skale-base`, `skale-base-sepolia` | v1 + v2 |

On Solana, the facilitator is the **fee payer** — the payer spends only USDC, no SOL. Always trust the live `/supported` output over this table.

### `POST /verify` — check a payment is valid (no settlement)

```json
POST /verify
{ "paymentPayload": { … }, "paymentRequirements": { … } }
→ { "isValid": true, "payer": "…" }
```

### `POST /settle` — broadcast/settle the payment on-chain

```json
POST /settle
{ "paymentPayload": { … }, "paymentRequirements": { … } }
→ { "success": true, "transaction": "<signature-or-hash>", "network": "solana", "payer": "…" }
```

Servers usually call `/verify` + `/settle` for you when you send an `X-PAYMENT` header. Some flows (e.g. the [`sp3nd`](../sp3nd/) skill in this repo) have the **client** call `/verify` then `/settle` directly. The payload shapes are defined by the [`x402`](../x402/) skill.

## Part 3 — Sell your own services (get paid by agents)

Any HTTP endpoint can become a paid, discoverable x402 resource:

1. **Gate the route** so it returns `402 Payment Required` with an `accepts` array (your `network`, `asset`, `payTo`, and price). The x402 server middlewares make this a few lines:
   - `x402-express`, `x402-hono`, `x402-next` — wrap a route and point the facilitator at `https://facilitator.payai.network`.
2. **Settle** incoming payments via the PayAI facilitator (`/verify` + `/settle`) — the middleware does this automatically.
3. **Get discovered** — resources that settle through PayAI are indexed into the Bazaar (`/discovery/resources`) so other agents can find and pay you. See the seller/merchant guide at https://docs.payai.network.

Conceptually (Express):

```javascript
import express from "express";
import { paymentMiddleware } from "x402-express";

const app = express();
app.use(paymentMiddleware(
  "0xYourWallet",                                   // where you get paid
  { "GET /premium": { price: "$0.01", network: "base" } },
  { url: "https://facilitator.payai.network" },     // PayAI settles it
));
app.get("/premium", (_req, res) => res.json({ data: "🎁 paid content" }));
app.listen(3000);
```

> Confirm the exact middleware signature against the x402 docs (https://x402.gitbook.io/x402) and PayAI's seller docs — the pricing/route config format evolves. Start on a testnet (`base-sepolia`, `solana-devnet`).

## A real consumer in this repo

The [`sp3nd`](../sp3nd/) skill (buy from Amazon with USDC) settles every order through the **PayAI facilitator** on **Solana** — a working example of x402 + PayAI end to end.

## Key facts

- **Facilitator:** `https://facilitator.payai.network` — no signup, multi-chain.
- **Bazaar / discovery:** `GET /discovery/resources` (paginated `items[]`).
- **Verify / settle:** `POST /verify`, `POST /settle` with `{ paymentPayload, paymentRequirements }`.
- **Supported:** `GET /supported` — Solana (+ gas paid for you) and 9 EVM chains.
- **Asset:** USDC, 6 decimals. Solana mint `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`; Base contract `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`.
- **Pay mechanics:** see the [`x402`](../x402/) skill.
- **Seller middlewares:** `x402-express`, `x402-hono`, `x402-next`.
- **Website:** https://payai.network · **Docs:** https://docs.payai.network
