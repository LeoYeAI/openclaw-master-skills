---
name: breeze-x402-payment-api
description: Operates Breeze x402 payment-gated endpoints for balance checks, deposits, and withdrawals on Solana. Use when the user asks to manage Breeze positions or execute paid x402 API calls.
compatibility: Requires Node.js and network access to x402 API and Solana RPC. Requires a funded Solana wallet for x402 USDC micropayments.
metadata: {"openclaw":{"requires":{"bins":["node"],"env":["WALLET_PRIVATE_KEY"]},"primaryEnv":"WALLET_PRIVATE_KEY"}}
---

# Breeze x402 Payment API

Interact with [Breeze](https://breeze.baby) through its x402 payment-gated HTTP API. Each protected request pays a small USDC micropayment, then returns API data or an unsigned Solana transaction.

## Quick Start: Minimum Viable Flow

This is the fastest path from zero to a working deposit. Read this before anything else.

**What you need:**
- A Solana wallet funded with USDC and ~0.01 SOL (for transaction fees)
- Node.js installed

### Step 0: Generate a wallet (skip if you already have one)

Run once to create and save a keypair:

```js
// generate-wallet.js
const { Keypair } = require('@solana/web3.js');
const fs = require('fs');

// Install first: npm install @solana/web3.js --legacy-peer-deps
const bs58Module = require('bs58');
const bs58 = bs58Module.default || bs58Module;

const keypair = Keypair.generate();
const secretKeyBase58 = bs58.encode(keypair.secretKey);

console.log('Public key (fund this address):', keypair.publicKey.toBase58());

// Save secret key to file — never print it to the console
fs.writeFileSync('wallet-backup.json', JSON.stringify(Array.from(keypair.secretKey)));
fs.writeFileSync('.env', `WALLET_PRIVATE_KEY=${secretKeyBase58}\n`);
console.log('Saved .env with WALLET_PRIVATE_KEY and wallet-backup.json — keep both secret and out of git!');
```

```bash
node generate-wallet.js
```

Fund the printed public key with USDC and at least 0.01 SOL before continuing. The `.env` file now contains your `WALLET_PRIVATE_KEY`.

### Step 1: Preflight checks

Verify everything is reachable before writing code:

```bash
# x402 server health
curl https://x402.breeze.baby/healthz

# Breeze strategy info (no auth needed)
curl https://api.breeze.baby/strategy-info/43620ba3-354c-456b-aa3c-5bf7fa46a6d4

# Wallet USDC balance (replace YOUR_WALLET_ADDRESS)
curl https://api.mainnet-beta.solana.com \
  -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":["YOUR_WALLET_ADDRESS",{"mint":"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},{"encoding":"jsonParsed"}]}'
```

Expected: healthz returns `{"status":"ok"}`, strategy-info returns strategy data, token query shows your USDC balance. If any of these fail, fix the connectivity issue before proceeding.

### Step 2: Install

```bash
npm install @faremeter/fetch @faremeter/payment-solana @faremeter/wallet-solana @faremeter/info @solana/web3.js bs58 --legacy-peer-deps
```

> **`--legacy-peer-deps` is required for npm.** Without it, `@faremeter/*` peer dependency conflicts cause npm to silently remove `@solana/web3.js`.

### Step 3: Run the deposit script

Save as `deposit.js` and run with `node deposit.js`:

```js
// deposit.js — CommonJS, no TypeScript needed
'use strict';

const { wrap } = require('@faremeter/fetch');
const { createPaymentHandler } = require('@faremeter/payment-solana/exact');
const { createLocalWallet } = require('@faremeter/wallet-solana');
const { Connection, Keypair, PublicKey, VersionedTransaction, Transaction } = require('@solana/web3.js');

// bs58 exports .default in some CJS environments
const bs58Module = require('bs58');
const bs58 = bs58Module.default || bs58Module;

async function main() {
  const WALLET_PRIVATE_KEY = process.env.WALLET_PRIVATE_KEY;
  if (!WALLET_PRIVATE_KEY) throw new Error('Set WALLET_PRIVATE_KEY env var');

  const API_URL = 'https://x402.breeze.baby';
  const STRATEGY_ID = '43620ba3-354c-456b-aa3c-5bf7fa46a6d4';
  const USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v';
  const DEPOSIT_AMOUNT = 1_000_000; // 1 USDC (6 decimals)

  // Setup
  const keypair = Keypair.fromSecretKey(bs58.decode(WALLET_PRIVATE_KEY));
  const connection = new Connection('https://api.mainnet-beta.solana.com');
  const wallet = await createLocalWallet('mainnet-beta', keypair);
  const paymentHandler = createPaymentHandler(wallet, new PublicKey(USDC_MINT), connection);
  const fetchWithPayment = wrap(fetch, { handlers: [paymentHandler] });

  console.log('Wallet:', keypair.publicKey.toBase58());

  // Build deposit transaction
  const res = await fetchWithPayment(`${API_URL}/deposit`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      amount: DEPOSIT_AMOUNT,
      user_key: keypair.publicKey.toBase58(),
      strategy_id: STRATEGY_ID,
      base_asset: USDC_MINT,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Deposit failed (${res.status}): ${text}`);
  }

  // Parse transaction string (may be bare or JSON-wrapped)
  const raw = (await res.text()).trim();
  const txString = raw.startsWith('"') ? JSON.parse(raw) : raw;

  // Sign and send (try versioned tx first, fall back to legacy)
  const bytes = Buffer.from(txString, 'base64');
  let sig;
  try {
    const tx = VersionedTransaction.deserialize(bytes);
    tx.sign([keypair]);
    sig = await connection.sendRawTransaction(tx.serialize());
  } catch {
    const tx = Transaction.from(bytes);
    tx.partialSign(keypair);
    sig = await connection.sendRawTransaction(tx.serialize());
  }

  await connection.confirmTransaction(sig, 'confirmed');
  console.log('Done! View transaction:', `https://solscan.io/tx/${sig}`);
}

main().catch(console.error);
```

```bash
# Set WALLET_PRIVATE_KEY from the .env created in Step 0
export $(cat .env | xargs) && node deposit.js
```

---

## Endpoint Paths: x402 API vs Direct REST API

> **These are different APIs with different paths.** Do not mix them up.

| API | Base URL | Endpoints | Auth method |
|-----|----------|-----------|-------------|
| **x402 (this skill)** | `https://x402.breeze.baby` | `/balance/:fund_user`<br>`/deposit`<br>`/withdraw`<br>`/healthz` (free) | USDC micropayment via x402 protocol |
| **Direct REST API** | `https://api.breeze.baby` | `/deposit/tx`<br>`/withdraw/tx`<br>`/strategy-info/:id` | `x-api-key` header |

This skill uses the **x402 API**. The direct REST API uses different paths and API key auth — do not mix them.

---

## When to use this skill

- "check my Breeze balance" or "show positions/yield"
- "deposit X token into Breeze strategy"
- "withdraw X token from Breeze strategy"
- "sign and send the transaction built by the API"

## Required inputs

- `WALLET_PRIVATE_KEY` (base58 secret key — see Step 0 to generate one)
- Optional `STRATEGY_ID` (defaults to `43620ba3-354c-456b-aa3c-5bf7fa46a6d4` — you can use any Breeze strategy ID)
- Optional `X402_API_URL` (default `https://x402.breeze.baby`)
- Optional `SOLANA_RPC_URL` (default `https://api.mainnet-beta.solana.com`)
- Optional `BASE_ASSET` mint (default USDC mint)

## Security rules

- Never print or echo `WALLET_PRIVATE_KEY`.
- Never return raw secret values in tool output.
- If a command fails, redact secrets before showing logs.
- Add `wallet-backup.json` to `.gitignore` immediately.

## Dependencies and install

```bash
# npm (--legacy-peer-deps required)
npm install @faremeter/fetch @faremeter/payment-solana @faremeter/wallet-solana @faremeter/info @solana/web3.js bs58 --legacy-peer-deps
```

```bash
# pnpm
pnpm add @faremeter/fetch @faremeter/payment-solana @faremeter/wallet-solana @faremeter/info @solana/web3.js bs58
```

```bash
# bun
bun add @faremeter/fetch @faremeter/payment-solana @faremeter/wallet-solana @faremeter/info @solana/web3.js bs58
```

## Setup: Payment-Wrapped Fetch (TypeScript)

Use this setup once per runtime. It automatically handles x402 challenges (`402` → build payment proof → retry request):

```typescript
import { wrap } from "@faremeter/fetch";
import { createPaymentHandler } from "@faremeter/payment-solana/exact";
import { createLocalWallet } from "@faremeter/wallet-solana";
import { Connection, Keypair, PublicKey } from "@solana/web3.js";
import bs58 from "bs58";

const API_URL = (process.env.X402_API_URL ?? "https://x402.breeze.baby").replace(/\/$/, "");
const SOLANA_RPC_URL = process.env.SOLANA_RPC_URL ?? "https://api.mainnet-beta.solana.com";
const STRATEGY_ID = process.env.STRATEGY_ID || "43620ba3-354c-456b-aa3c-5bf7fa46a6d4";
const BASE_ASSET = process.env.BASE_ASSET ?? "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";
const WALLET_PRIVATE_KEY = process.env.WALLET_PRIVATE_KEY!;

const keypair = Keypair.fromSecretKey(bs58.decode(WALLET_PRIVATE_KEY));
const connection = new Connection(SOLANA_RPC_URL);
const wallet = await createLocalWallet("mainnet-beta", keypair);
const walletPublicKey = keypair.publicKey.toBase58();
const USDC_MINT = new PublicKey(BASE_ASSET);
const paymentHandler = createPaymentHandler(wallet, USDC_MINT, connection);

const fetchWithPayment = wrap(fetch, { handlers: [paymentHandler] });
```

## API endpoint contract

### Check Balance

```
GET /balance/:fund_user
```

Returns JSON with positions, deposited amounts, yield earned, and APY.
Values are in base units. Convert to human amounts with token decimals.

```typescript
const response = await fetchWithPayment(
	`${API_URL}/balance/${encodeURIComponent(walletPublicKey)}`,
	{ method: "GET" },
);
const balances = await response.json();
```

### Deposit

```
POST /deposit
Content-Type: application/json
```

Builds an unsigned deposit transaction.
`amount` must be base units (example: `10_000_000` = 10 USDC).

```typescript
const response = await fetchWithPayment(`${API_URL}/deposit`, {
	method: "POST",
	headers: { "content-type": "application/json" },
	body: JSON.stringify({
		amount: 10_000_000, // 10 USDC (6 decimals)
		user_key: walletPublicKey,
		strategy_id: STRATEGY_ID,
		base_asset: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
	}),
});
const txString = await response.text(); // encoded unsigned transaction
```

### Withdraw

```
POST /withdraw
Content-Type: application/json
```

Builds an unsigned withdrawal transaction. Supports optional WSOL handling flags.
`amount` must be base units.

```typescript
const response = await fetchWithPayment(`${API_URL}/withdraw`, {
	method: "POST",
	headers: { "content-type": "application/json" },
	body: JSON.stringify({
		amount: 5_000_000,
		user_key: walletPublicKey,
		strategy_id: STRATEGY_ID,
		base_asset: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
		all: false,
		exclude_fees: true, // always recommended
		// For wrapped SOL withdrawals only:
		// unwrap_wsol_ata: true,     // unwrap WSOL to native SOL
		// create_wsol_ata: true,     // create WSOL ATA if needed
		// detect_wsol_ata: true,     // auto-detect WSOL ATA existence
	}),
});
const txString = await response.text();
```

Withdraw parameters:

| Parameter         | Type    | Required | Description                                    |
| ----------------- | ------- | -------- | ---------------------------------------------- |
| `amount`          | number  | yes      | Amount in base units                           |
| `user_key`        | string  | yes      | User's Solana public key                       |
| `strategy_id`     | string  | yes      | Breeze strategy ID (default: `43620ba3-354c-456b-aa3c-5bf7fa46a6d4`, or any valid strategy) |
| `base_asset`      | string  | yes      | Token mint address                             |
| `all`             | boolean | no       | Withdraw entire position                       |
| `exclude_fees`    | boolean | no       | Exclude fees from amount (recommended: `true`) |
| `unwrap_wsol_ata` | boolean | no       | Unwrap WSOL to native SOL after withdraw       |
| `create_wsol_ata` | boolean | no       | Create WSOL ATA if it doesn't exist            |
| `detect_wsol_ata` | boolean | no       | Auto-detect WSOL ATA and set flags accordingly |

WSOL handling: when withdrawing WSOL (`So11111111111111111111111111111111111111112`), pass `unwrap_wsol_ata: true` to receive native SOL.

### Health Check

```
GET /healthz
```

Free endpoint (no x402 payment required). Returns `{"status":"ok"}` when the service is running. Use this to verify connectivity before making paid requests.

## Workflow checklists

Copy a checklist into your working notes and mark each step complete.

### Balance workflow

Task Progress:
- [ ] Read `wallet public key` input
- [ ] Call `GET /balance/:fund_user` with URL-encoded wallet key
- [ ] Verify `response.ok`; if not, capture status/body and stop
- [ ] Parse JSON response
- [ ] Convert base units to human-readable values using token decimals
- [ ] Return balances, yield, and APY clearly

### Deposit workflow

Task Progress:
- [ ] Confirm token mint and decimals
- [ ] Convert user amount to base units (`floor(amount * 10^decimals)`)
- [ ] Call `POST /deposit` with validated payload
- [ ] Verify `response.ok`; if not, capture status/body and stop
- [ ] Extract transaction string from response text
- [ ] Sign and broadcast transaction on Solana
- [ ] Confirm transaction and return explorer link

### Withdraw workflow

Task Progress:
- [ ] Confirm token mint and decimals
- [ ] Convert user amount to base units unless `all=true`
- [ ] Set `exclude_fees: true` unless user asks otherwise
- [ ] For WSOL + native SOL output, set `unwrap_wsol_ata: true`
- [ ] Call `POST /withdraw` with validated payload
- [ ] Verify `response.ok`; if not, capture status/body and stop
- [ ] Extract transaction string from response text
- [ ] Sign and broadcast transaction on Solana
- [ ] Confirm transaction and return explorer link

## Signing and Sending Transactions

Deposit and withdraw return encoded unsigned transactions. Normalize then sign/send:

```typescript
import { VersionedTransaction, Transaction } from "@solana/web3.js";

function extractTransactionString(responseText: string): string {
	const trimmed = responseText.trim();
	try {
		const parsed = JSON.parse(trimmed);
		if (typeof parsed === "string") return parsed;
		throw new Error("expected transaction string");
	} catch (e) {
		if (e instanceof SyntaxError) return trimmed;
		throw e;
	}
}

async function signAndSend(txString: string) {
	const bytes = Uint8Array.from(Buffer.from(txString, "base64"));

	// Try versioned transaction first, then legacy
	try {
		const tx = VersionedTransaction.deserialize(bytes);
		tx.sign([keypair]);
		const sig = await connection.sendRawTransaction(tx.serialize());
		await connection.confirmTransaction(sig, "confirmed");
		return sig;
	} catch {
		const tx = Transaction.from(bytes);
		tx.partialSign(keypair);
		const sig = await connection.sendRawTransaction(tx.serialize());
		await connection.confirmTransaction(sig, "confirmed");
		return sig;
	}
}
```

Validation loop:

1. Build/parse transaction string.
2. Try `VersionedTransaction` path.
3. If it fails, try legacy `Transaction` path.
4. Confirm transaction.
5. If both deserializations fail, return a clear decoding error and do not continue.

## Failure handling

- `400` errors: payload issue. Re-check required fields and amount positivity.
- `401/403`: wallet/payment authorization issue. Verify wallet and x402 payment capability.
- `402`: payment challenge not satisfied. Re-run request through wrapped fetch and do not bypass payment handler.
- `500+`: upstream or proxy issue. Retry once with short backoff, then report failure.
- Transaction send failure: return explicit error with stage (`deserialize`, `sign`, `send`, or `confirm`).

## Response format to user

For successful deposit/withdraw, return:

- Action (`deposit` or `withdraw`)
- Token + human amount
- Base-unit amount used in request
- Solana transaction signature
- Explorer URL (`https://solscan.io/tx/{sig}`)

For balance, return:

- Per-token deposited amount
- Yield earned
- APY details when present
- Note that raw API values are base units and were converted

## Supported Tokens

| Token   | Mint                                           | Decimals |
| ------- | ---------------------------------------------- | -------- |
| USDC    | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` | 6        |
| USDT    | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` | 6        |
| USDS    | `USDSwr9ApdHk5bvJKMjzff41FfuX8bSxdKcR81vTwcA`  | 6        |
| SOL     | `So11111111111111111111111111111111111111112`  | 9        |
| JitoSOL | `J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn` | 9        |
| mSOL    | `mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So`  | 9        |
| JupSOL  | `jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v`  | 9        |
| JLP     | `27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4` | 6        |

## Environment Variables

| Variable             | Required | Default                                | Description                       |
| -------------------- | -------- | -------------------------------------- | --------------------------------- |
| `WALLET_PRIVATE_KEY` | yes      | —                                      | Base58-encoded Solana private key |
| `STRATEGY_ID`        | no       | `43620ba3-354c-456b-aa3c-5bf7fa46a6d4` | Breeze strategy ID — any valid strategy ID works |
| `X402_API_URL`       | no       | `https://x402.breeze.baby`             | x402 payment API URL              |
| `SOLANA_RPC_URL`     | no       | `https://api.mainnet-beta.solana.com`  | Solana RPC endpoint               |
| `BASE_ASSET`         | no       | USDC mint                              | Default token mint for operations |

## External Endpoints

This skill sends requests to:
- `https://x402.breeze.baby` — Breeze x402 payment-gated API (deposits, withdrawals, balances)
- `https://api.mainnet-beta.solana.com` — Solana RPC (transaction signing and broadcasting)

## Security & Privacy

This skill requires `WALLET_PRIVATE_KEY` as an environment variable for signing Solana transactions and x402 USDC micropayments. The key is read from the process environment at runtime and is never logged, printed, or returned in output. By using this skill, small USDC micropayments are sent from your wallet to gate API access. Only install this skill if you trust Breeze with your wallet's signing capability for USDC transactions.

## Additional reference

See [agent-using-x402](https://github.com/anagrambuild/breeze-agent-kit/tree/main/apps/examples/agent-using-x402) for a full TypeScript implementation.
