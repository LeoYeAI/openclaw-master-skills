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
            with the payment header  (X-PAYMENT in v1, PAYMENT-SIGNATURE in v2)
4. Server → verifies + settles the payment via a facilitator, then returns
            200 OK  + the resource  + a settlement-receipt header
```

Because payment is just an HTTP header, x402 works with any HTTP client and any agent framework. This skill teaches you how to **be the payer (client)**. To *discover* paid services and to *sell* your own, see the companion [`payai`](../payai/) skill.

## Protocol versions: v1 vs v2 (READ THIS)

x402 has two wire versions in the wild, and the **header names differ**. A `402` response tells you which one you're dealing with via its `x402Version` field (and its network format). The PayAI facilitator supports **both** — always match what the server offered.

| | **v1** (`x402Version: 1`) | **v2** (`x402Version: 2`) |
|---|---|---|
| Requirements (server → client) | JSON body `accepts` (some servers also use a `PAYMENT-REQUIRED` header) | **`PAYMENT-REQUIRED`** header, base64 (often also in the body) |
| Payment (client → server) | **`X-PAYMENT`** | **`PAYMENT-SIGNATURE`** |
| Receipt (server → client) | `X-PAYMENT-RESPONSE` | `PAYMENT-RESPONSE` |
| Network id | plain string — `base`, `solana` | **CAIP-2** — `eip155:8453`, `solana:<genesis-hash>` |
| Client packages | `x402-fetch`, `x402-axios` | `@x402/fetch`, `@x402/axios` + `@x402/evm` / `@x402/svm` |

**Rule of thumb for the manual flow:** read `x402Version` from the 402 response, then use the matching payment header (`x402Version >= 2` → `PAYMENT-SIGNATURE`, else `X-PAYMENT`) and echo that same version number back in your payload. Never hardcode the `network` string — copy the exact value from the `accepts` entry (it may be `solana` **or** `solana:5eykt4Us…`).

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

When a server returns `402`, an `accepts` array describes the ways to pay. In **v1** it's in the JSON body; in **v2** it's a base64-encoded `PAYMENT-REQUIRED` **header** (and usually mirrored in the body too — decode whichever is present). Each entry describes one option:

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

The x402 ecosystem ships drop-in HTTP wrappers that detect a `402`, pay it, and transparently retry — turning "pay for this" into a normal `fetch`. **You don't choose a facilitator as the payer** — the *seller* runs one and settles your payment; you just sign. The wrapper also picks the right header (`X-PAYMENT` vs `PAYMENT-SIGNATURE`) for the version the server offered.

**v2 (current — builder pattern, registers a scheme per chain):**

```javascript
// npm i @x402/fetch @x402/core @x402/evm @x402/svm
import { x402Client } from "@x402/core";
import { wrapFetchWithPayment } from "@x402/fetch";
import { ExactEvmScheme } from "@x402/evm/exact/client";
import { ExactSvmScheme } from "@x402/svm/exact/client";

const client = new x402Client();
client.register("eip155:*", new ExactEvmScheme(evmSigner));   // any EVM chain
client.register("solana:*", new ExactSvmScheme(svmSigner));   // any Solana cluster

const fetchWithPay = wrapFetchWithPayment(fetch, client);
const res  = await fetchWithPay("https://api.example.com/paid-endpoint"); // pays on 402
const data = await res.json();
```

**v1 (legacy — still accepted by the facilitator):**

```javascript
// npm i x402-fetch
import { wrapFetchWithPayment } from "x402-fetch";
const fetchWithPay = wrapFetchWithPayment(fetch, walletClient); // EVM wallet or Solana signer
const res = await fetchWithPay("https://api.example.com/paid-endpoint");
```

`x402-axios` / `@x402/axios` provide the same thing as an Axios interceptor.

> Library APIs evolve — confirm exact signatures against the x402 docs (https://x402.gitbook.io/x402) and PayAI's docs (https://docs.payai.network). Solana (`@x402/svm`) is newer than EVM; if a library path doesn't fit, fall back to Option B.

### Option B — Manual flow (works everywhere, no SDK)

This is the fully-explicit flow. It always works because it only uses the wallet SDK for your chain plus `fetch`.

#### B.1 — Solana (USDC, facilitator pays gas) — **v1 wire format**

This builds the **v1** Solana payment (`X-PAYMENT`), which the PayAI facilitator still accepts. It's the simplest correct manual path. For strict **v2** Solana endpoints, see the note after the code.

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
  // 1. Trigger the 402 and read the requirements from the JSON body
  let res = await fetch(url, init);
  if (res.status !== 402) return res;              // nothing to pay
  const reqs = await res.clone().json().catch(() => null);
  const req  = (reqs?.accepts || []).find(a => String(a.network).startsWith("solana"));
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

  // 3. Encode the v1 payment payload and re-send the request with X-PAYMENT
  const paymentPayload = {
    x402Version: 1,
    scheme: "exact",
    network: req.network,                                     // echo the exact string the server gave
    payload: { transaction: Buffer.from(tx.serialize()).toString("base64") },
  };
  const header = Buffer.from(JSON.stringify(paymentPayload)).toString("base64");

  res = await fetch(url, { ...init, headers: { ...(init.headers || {}), "X-PAYMENT": header } });
  return res;                                                 // 200 OK + X-PAYMENT-RESPONSE receipt
}
```

> **Some servers settle server-side** (they read your payment header, call the facilitator, then return the resource). **Others** — like the `sp3nd` skill in this repo — ask the client to call the facilitator's `/verify` then `/settle` directly and confirm out of band. Read the server's docs. The facilitator endpoints are: `POST /verify` and `POST /settle`, each taking `{ paymentPayload, paymentRequirements }` and returning `{ isValid }` / `{ success, transaction }`.

> **Paying a strict v2 Solana endpoint?** v2 changes the wire format: the header is `PAYMENT-SIGNATURE`, and the payload is a different envelope — `{ x402Version: 2, resource, accepted, payload: { transaction } }` (where `accepted` is the `accepts` entry you chose). The signed transaction must also include a **Memo** instruction — the seller's `extra.memo` if present, otherwise a random nonce for replay protection. Rather than hand-roll all that, use **`@x402/svm`** (Option A) — it builds the v2 payload, memo/nonce, and blockhash pinning correctly. The manual code above is the simpler v1 format.

#### B.2 — EVM (Base, Polygon, Arbitrum, …) via EIP-3009

On EVM, the `exact` scheme uses an **EIP-3009 `transferWithAuthorization`** signature — you sign a typed message authorizing the transfer; no on-chain tx or gas from you at signing time. The **v1** payload is:

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

Base64-encode that and send it as `X-PAYMENT`, exactly as in the Solana v1 case. **v2** uses `PAYMENT-SIGNATURE` with a different envelope (`{ x402Version: 2, resource, accepted, payload }`) and CAIP-2 networks (`eip155:8453`). Producing the EIP-712 signature by hand is error-prone in either version — use `@x402/fetch` + `@x402/evm` (Option A), which builds the signature, envelope, and header for you.

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
- **Requirements header (v2, server → client):** `PAYMENT-REQUIRED: base64(requirements)` (v1 puts them in the JSON body).
- **Payment header (client → server):** `PAYMENT-SIGNATURE` in **v2**, `X-PAYMENT` in **v1** — base64(paymentPayload).
- **Receipt header (server → client):** `PAYMENT-RESPONSE` in **v2**, `X-PAYMENT-RESPONSE` in **v1**.
- **Pick the version** from the 402's `x402Version`; the facilitator accepts both.
- **Default facilitator:** `https://facilitator.payai.network` (Solana + 9 EVM chains).
- **USDC decimals:** 6 (so `1000000` base units = $1.00).
- **USDC mint (Solana mainnet):** `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- **USDC contract (Base mainnet):** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **Solana gas:** paid by the facilitator (`extra.feePayer`), not by you.
- **Client libraries:** v2 — `@x402/fetch`, `@x402/axios` (+ `@x402/evm`, `@x402/svm`); v1 — `x402-fetch`, `x402-axios`.
- **Discover & sell x402 services:** see the [`payai`](../payai/) skill.
- **Docs:** x402 protocol — https://x402.gitbook.io/x402 · PayAI facilitator — https://docs.payai.network
