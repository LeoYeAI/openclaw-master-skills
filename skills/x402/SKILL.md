---
name: x402
description: Pay for any HTTP 402-gated API, tool, or resource autonomously with stablecoins (USDC) over the x402 payment protocol — on Solana and EVM chains (Base, Polygon, Arbitrum, Avalanche, Sei, and more) — using the open PayAI facilitator. Use whenever an agent hits an HTTP 402 Payment Required response, needs to call a paid API without signing up for an account or API key, or wants to buy machine-priced services with crypto and no human in the loop.
metadata: {"openclaw":{"emoji":"💸","homepage":"https://payai.network","primaryEnv":"SOLANA_PRIVATE_KEY"}}
---

# x402 — Pay for Anything on the Web with One Line of Crypto

## What is x402?

**x402** is an open payment protocol that revives the long-dormant `HTTP 402 Payment Required` status code so that **machines can pay machines**. A server prices a resource; a client (your agent) pays for it inline with a stablecoin transfer; the server delivers the resource. No accounts, no API keys, no OAuth, no credit card, no human checkout.

The whole thing happens in a single retried HTTP request:

```
1. Agent  → GET/POST  https://api.example.com/paid-endpoint
2. Server → 402 Payment Required   { accepts: [ { network, asset, amount, payTo, ... } ] }
3. Agent  → build + sign a stablecoin payment, re-send the SAME request
            with header:  X-PAYMENT: <base64 payment payload>
4. Server → verifies + settles the payment via a facilitator, then returns
            200 OK  + the resource  + header  X-PAYMENT-RESPONSE: <base64 receipt>
```

Because payment is just an HTTP header, x402 works with any HTTP client and any agent framework. This skill teaches you how to **be the payer (client)**. To *discover* paid services and to *sell* your own, see the companion [`payai`](../payai/) skill.

## When to use this skill

Reach for x402 whenever you encounter any of these:

- A request comes back **`402 Payment Required`** (check `response.status === 402`).
- You need data or compute from a **paid API** but have no account or API key for it.
- A task would be faster/cheaper done by **paying a specialized agent or tool** than doing it yourself.
- You are wiring an agent to **buy machine-priced resources** (inference, data, files, RPC calls, physical goods) with USDC autonomously.

## Prerequisites

| You need | Why |
|---|---|
| A funded **wallet** on the payment chain | To hold the USDC you'll spend. Solana keypair, or an EVM private key. |
| **USDC** in that wallet | The near-universal x402 settlement asset (a 1:1 USD stablecoin). |
| A **facilitator** URL | A service that verifies and broadcasts your payment. Default: `https://facilitator.payai.network` (multi-chain). |

> On **Solana**, you do **not** need SOL for gas — the facilitator acts as the transaction **fee payer**. You only spend USDC. On EVM chains, gas handling depends on the scheme (see below).

## The payment requirements object

When a server returns `402`, the body (or, for some servers, a `PAYMENT-REQUIRED` header) contains an `accepts` array. Each entry describes one way to pay:

```json
{
  "x402Version": 1,
  "error": "Payment required",
  "accepts": [
    {
      "scheme": "exact",
      "network": "solana",
      "asset": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
      "payTo": "2nkTRv3qxk7n2eYYjFAndReVXaV7sTF3Z9pNimvp5jcp",
      "maxAmountRequired": "10000",
      "resource": "https://api.example.com/paid-endpoint",
      "description": "1 API call",
      "mimeType": "application/json",
      "maxTimeoutSeconds": 300,
      "extra": { "feePayer": "2wKupLR9q6wXYppw8Gr2NvWxKBUqm4PPJKkQfoxHDBg4" }
    }
  ]
}
```

Field notes:

- **`scheme`** — almost always `"exact"` (pay an exact amount). PayAI also supports `"upto"` on EVM for metered/streaming usage.
- **`network`** — `"solana"` / `"solana-devnet"`, or an EVM name like `"base"`, or a v2 CAIP-2 id like `"eip155:8453"` (Base) / `"solana:5eykt4Us..."`.
- **`asset`** — the token to pay in. On Solana it's the USDC **mint** (`EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`). On Base it's the USDC contract (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`).
- **`maxAmountRequired`** (a.k.a. `amount`) — the price in the asset's **base units** (USDC has **6 decimals**, so `10000` = $0.01).
- **`payTo`** — the recipient (the seller's wallet / token account).
- **`extra.feePayer`** — on Solana, the facilitator wallet that pays network gas. Set this as your transaction's fee payer.

Pick the `accepts` entry whose `network` matches a chain you hold USDC on. If several match, prefer the cheapest / a chain you already have funds on.

## Two ways to pay

### Option A — Use an x402 client library (recommended)

The x402 ecosystem ships drop-in HTTP wrappers that detect a `402`, pay it, and transparently retry — turning "pay for this" into a normal `fetch`:

- `x402-fetch` — wraps the native `fetch`
- `x402-axios` — an Axios interceptor

Point the wrapper's facilitator at PayAI and hand it a wallet. Conceptually:

```javascript
import { wrapFetchWithPayment } from "x402-fetch";
// signer = your Solana or EVM wallet/keypair
const fetchWithPay = wrapFetchWithPayment(fetch, signer, {
  facilitator: { url: "https://facilitator.payai.network" },
});

// Just call the paid endpoint — payment happens automatically on 402:
const res = await fetchWithPay("https://api.example.com/paid-endpoint");
const data = await res.json();
```

> Library APIs evolve — confirm the exact signature against the x402 docs (https://x402.gitbook.io/x402) and PayAI's facilitator docs (https://docs.payai.network). If a library doesn't yet support your chain (Solana support is newer than EVM), fall back to Option B.

### Option B — Manual flow (works everywhere, no SDK)

This is the fully-explicit flow. It always works because it only uses the wallet SDK for your chain plus `fetch`.

#### B.1 — Solana (USDC, facilitator pays gas)

```javascript
// npm i @solana/web3.js @solana/spl-token
import {
  Connection, Keypair, PublicKey,
  TransactionMessage, VersionedTransaction, ComputeBudgetProgram,
} from "@solana/web3.js";
import { getAssociatedTokenAddress, createTransferCheckedInstruction } from "@solana/spl-token";

const FACILITATOR = "https://facilitator.payai.network";
const USDC_MINT   = new PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v");
const connection  = new Connection(process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com");
const keypair     = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(process.env.SOLANA_PRIVATE_KEY)));

async function payX402Solana(url, init = {}) {
  // 1. Trigger the 402
  let res = await fetch(url, init);
  if (res.status !== 402) return res;              // nothing to pay
  const body = await res.clone().json().catch(() => null);
  const req  = (body?.accepts || []).find(a => a.network?.startsWith("solana"));
  if (!req) throw new Error("No Solana payment option offered");

  // 2. Build a USDC transfer where the FACILITATOR is the fee payer
  const payTo     = new PublicKey(req.payTo);
  const feePayer  = new PublicKey(req.extra.feePayer);      // PayAI pays gas, not you
  const amount    = BigInt(req.maxAmountRequired || req.amount);
  const sourceATA = await getAssociatedTokenAddress(USDC_MINT, keypair.publicKey);
  const destATA   = await getAssociatedTokenAddress(USDC_MINT, payTo);
  const { blockhash } = await connection.getLatestBlockhash();

  const message = new TransactionMessage({
    payerKey: feePayer,
    recentBlockhash: blockhash,
    instructions: [
      ComputeBudgetProgram.setComputeUnitLimit({ units: 30_000 }),
      ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 1 }),
      createTransferCheckedInstruction(sourceATA, USDC_MINT, destATA, keypair.publicKey, amount, 6),
    ],
  });
  const tx = new VersionedTransaction(message.compileToV0Message());
  tx.sign([keypair]);                                        // you sign as the token owner; facilitator co-signs on settle

  // 3. Encode the x402 payment payload and re-send the request with X-PAYMENT
  const paymentPayload = {
    x402Version: req.x402Version ?? 1,
    scheme: "exact",
    network: req.network,
    payload: { transaction: Buffer.from(tx.serialize()).toString("base64") },
  };
  const header = Buffer.from(JSON.stringify(paymentPayload)).toString("base64");

  res = await fetch(url, { ...init, headers: { ...(init.headers || {}), "X-PAYMENT": header } });
  return res;                                                // 200 OK + X-PAYMENT-RESPONSE receipt header
}
```

> **Some servers settle server-side** (they read your `X-PAYMENT` header, call the facilitator, then return the resource). **Others** — like the `sp3nd` skill in this repo — ask the client to call the facilitator's `/verify` then `/settle` directly and confirm out of band. Read the server's docs. The facilitator endpoints are: `POST /verify` and `POST /settle`, each taking `{ paymentPayload, paymentRequirements }` and returning `{ isValid }` / `{ success, transaction }`.

#### B.2 — EVM (Base, Polygon, Arbitrum, …) via EIP-3009

On EVM, the `exact` scheme uses an **EIP-3009 `transferWithAuthorization`** signature — you sign a typed message authorizing the transfer; no on-chain tx or gas from you at signing time. The payload is:

```json
{
  "x402Version": 1,
  "scheme": "exact",
  "network": "base",
  "payload": {
    "signature": "0x…",
    "authorization": {
      "from": "0xYourWallet",
      "to": "0xSellerWallet",
      "value": "10000",
      "validAfter": "0",
      "validBefore": "1799999999",
      "nonce": "0x…32bytes"
    }
  }
}
```

Base64-encode that and send it as `X-PAYMENT`, exactly as in the Solana case. The easiest way to produce the signature correctly is the `x402-fetch` / `x402-axios` library (Option A), which handles the EIP-712 domain and nonce for you.

## Choosing a facilitator

A **facilitator** is a neutral service that verifies a payment is valid and broadcasts/settles it on-chain. This skill defaults to the **PayAI facilitator** because it is multi-chain and requires no signup:

```
https://facilitator.payai.network
```

Enumerate exactly what it supports at runtime:

```bash
curl -s https://facilitator.payai.network/supported | jq '.kinds[] | {scheme, network}'
```

As of writing, PayAI's facilitator settles **Solana** (mainnet + devnet, x402 v1 and v2) and **9 EVM chains** — Base, Avalanche, Sei, Polygon, X Layer, SKALE, and Arbitrum (v1 and v2, including the `upto` metered scheme). Always trust the live `/supported` response over this list.

## Helper script

`scripts/inspect-402.mjs` (zero dependencies, Node 18+) probes any URL and, if it returns `402`, decodes and pretty-prints the payment requirements — a safe dry run before you spend anything:

```bash
node scripts/inspect-402.mjs https://api.example.com/paid-endpoint
```

Use it to confirm the network, asset, amount, and `payTo` **before** wiring up a real payment.

## Safety checklist for autonomous payments

- **Verify the price.** Read `maxAmountRequired` and convert from base units (÷ 10^6 for USDC). Enforce a per-call and per-session spend cap.
- **Verify the network + asset** against `/supported` — never pay in an asset or on a chain you didn't intend.
- **Confirm `payTo`** matches the service you meant to pay when it matters (e.g. a known merchant wallet).
- **Never expose private keys.** Load `SOLANA_PRIVATE_KEY` / EVM keys from the environment or a signer service — never hardcode them, never log them.
- **Prefer devnet/testnet** (`solana-devnet`, `base-sepolia`) while developing.

## Key facts

- **Protocol:** x402 (`HTTP 402 Payment Required`) — payment as an HTTP header.
- **Payment header (client → server):** `X-PAYMENT: base64(paymentPayload)`.
- **Receipt header (server → client):** `X-PAYMENT-RESPONSE: base64(settlementReceipt)`.
- **Default facilitator:** `https://facilitator.payai.network` (Solana + 9 EVM chains).
- **USDC decimals:** 6 (so `1000000` base units = $1.00).
- **USDC mint (Solana mainnet):** `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- **USDC contract (Base mainnet):** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **Solana gas:** paid by the facilitator (`extra.feePayer`), not by you.
- **Client libraries:** `x402-fetch`, `x402-axios`.
- **Discover & sell x402 services:** see the [`payai`](../payai/) skill.
- **Docs:** x402 protocol — https://x402.gitbook.io/x402 · PayAI facilitator — https://docs.payai.network
