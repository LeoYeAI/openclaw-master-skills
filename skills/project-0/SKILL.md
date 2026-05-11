---
name: project0
version: 2.2.6
description: >
  Permissionless DeFi yield and credit on Solana via the Project 0 (P0) protocol.
  Deposit funds to earn yield across Solana's highest-yielding venues.
  Borrow stablecoins against deposited collateral instead of selling crypto.
  Execute advanced yield strategies via rate arbitrage and looping.
  All operations are on-chain and permissionless -- no accounts, no approval process.
  Note: This skill requires a wallet keypair to sign transactions. Use a dedicated
  wallet with limited funds -- never expose your main private key. The agent will
  always ask for confirmation before signing. Read-only operations need no keypair.
homepage: https://0.xyz
metadata:
  openclaw:
    requires:
      env:
        - RPC_URL
        - WALLET_KEYPAIR
        - WALLET_ADDRESS
        - P0_ACCOUNT
        - JUPITER_API_KEY
    primaryEnv: RPC_URL
---

# Project 0 Skill

## What is Project 0?

P0 is a permissionless DeFi prime broker on Solana. It provides unified margin
accounts that span multiple lending venues (P0 native, Kamino, Drift), giving
agents access to the best yields and deepest liquidity across the ecosystem.
All operations are on-chain, non-custodial, and require no signup.

**Documentation:**

- Protocol overview: https://docs.0.xyz/
- TypeScript SDK: https://docs.0.xyz/typescript-sdk/overview

### Use Case 1: Yield + Credit

Deposit funds to earn the best yield across DeFi. When the user needs
liquidity (e.g. to make a purchase), borrow stablecoins against deposited
collateral instead of selling crypto. The user keeps earning yield while
accessing cash.

**Flow:** Deposit -> Earn yield -> Borrow stablecoins when needed -> Repay.

**Example prompts:**

- "Deposit my SOL on P0 for the best yield."
- "I need $500 USDC but don't want to sell my SOL."
- "What is the cheapest stablecoin to borrow on P0?"

### Use Case 2: Advanced Yield Strategies

Find the absolute best yields on Solana, which often come from rate arbitrage
and looping strategies. These involve depositing one asset, borrowing another,
and managing the leveraged position. Higher yields, but requires active health
monitoring.

**Flow:** Identify strategy -> Deposit collateral -> Borrow -> Monitor health.

**Example prompts:**

- "What are the highest-yield strategies on P0 right now?"
- "Set up a bbSOL/SOL rate arb on P0."
- "Put my funds to work on P0 for the best yield."

---

## Agent Workflow

When a user asks to earn yield, deposit, borrow, or manage positions on P0,
follow these steps in order. Do NOT skip ahead to writing code.

### Step 1: Check wallet balances

Resolve the wallet address: check `.env` for `WALLET_ADDRESS`, or derive
it from the keypair if `WALLET_KEYPAIR` is set, or ask the user.

Fetch the wallet's token holdings from the wallet API (see Wallet endpoint
below). No credentials needed. Use the `address` field from each token to
match against P0 banks by `mint`.

### Step 2: Fetch P0 data

Fetch banks and strategies from the P0 APIs (see Read-Only APIs below).

### Step 3: Recommend optimal action

Determine which use case fits the user's request:

- If the user wants to **earn yield or access credit**, recommend the best
  deposit opportunity and mention borrowing as an option (Use Case 1).
- If the user wants the **highest possible yield** or mentions strategies,
  rate arbs, or looping, recommend the best strategy and explain the
  deposit + borrow setup required (Use Case 2).

Match wallet holdings to available bank yields. For each token the wallet
holds, find the best deposit APY from the banks data. Compare across all
holdings to find the highest overall yield.

If the wallet holds tokens that have no corresponding P0 bank (e.g.
memecoins), suggest swapping them into a supported token.

If swapping to a different token would yield significantly more, recommend
the swap and explain the tradeoff.

Consider depositing multiple assets if the wallet holds several supported
tokens -- not just the single highest-yield one.

**Present the plan to the user with specific numbers before executing.**

Example: _"Your wallet holds 0.09 bbSOL (~$18) and 0.10 SOL (~$15). bbSOL
earns 15.2% APY on P0 vs SOL at 4.9%. I recommend depositing your bbSOL
for the higher yield. Shall I proceed?"_

### Step 4: Collect credentials

Before executing on-chain operations, the agent needs an RPC URL and a
wallet keypair.

**RPC URL:** Check `.env` for `RPC_URL`, `SOLANA_RPC_URL`, or `HELIUS_RPC_URL`.
If not found, ask the user: _"I need a paid Solana RPC URL to execute
transactions. (Helius has a free tier at https://www.helius.dev)"_

**Wallet address:** Check `.env` for `WALLET_ADDRESS`. If set, use it for
read-only operations (wallet balances, account discovery) without needing
the keypair. The keypair is only required when signing transactions.

**Wallet keypair:** If the user provided a keypair path in their message,
use it directly. Otherwise check `.env` for `WALLET_KEYPAIR`. If neither,
ask: _"I need a Solana keypair to sign transactions. Set `WALLET_KEYPAIR`
in your `.env` to the file path, or tell me where your keypair JSON file
is."_

**P0 account (optional):** Check `.env` for `P0_ACCOUNT`. If set, use it
directly when loading the account (skip discovery/prompt). If not set,
follow the account discovery logic in "Create or load account" below.

Do not fabricate URLs, file paths, or account addresses. Wait for the user
to provide real values.

### Step 5: Collect swap credentials (only if needed)

If the plan from step 3 involves swapping tokens, the agent needs a Jupiter
API key.

Check for an existing key in the environment:

- Look for `JUPITER_API_KEY` or `JUP_API_KEY` in the environment variables
  or `.env` file
- If found, use it and skip the prompt

If no key is found, ask the user:

_"I need a Jupiter API key for the token swap. Get a free one at
https://portal.jup.ag (60 req/min)"_

If no swap is needed, skip this step entirely.

### Step 6: Execute

Execute the plan from step 3. Swap first if needed (see Swapping Tokens
section), then deposit, borrow, etc. Report results with Solscan links:
`https://solscan.io/tx/${signature}`

---

## Read-Only: Fetching Data from P0

Use the public HTTP APIs for read-only tasks. No SDK, no wallet, no RPC needed.

### Banks endpoint

`GET https://ai.0.xyz/api/banks`

Returns every lending pool (bank) with rates, metadata, and pricing. Only
collateral-tier banks are included (isolated banks are filtered out). The
response is a lightweight projection (9 fields per bank) with deposit APY
pre-computed.

```typescript
const res = await fetch("https://ai.0.xyz/api/banks");
const banks = await res.json();
```

**Fields per bank:**

| Field           | Description                                                                   |
| --------------- | ----------------------------------------------------------------------------- |
| `bank_address`  | On-chain bank address (use with SDK `client.getBank()`)                       |
| `symbol`        | Token symbol (SOL, USDC, JitoSOL, ...)                                        |
| `mint`          | Token mint address                                                            |
| `mint_decimals` | Token decimal places (9 for SOL, 6 for USDC)                                  |
| `venue`         | Lending venue (P0, Kamino, Drift)                                             |
| `deposit_apy`   | Effective deposit APY as percentage (pre-computed, includes underlying yield) |
| `borrow_apy`    | Borrow APY as percentage                                                      |
| `usd_price`     | Oracle price in USD                                                           |
| `token_program` | Token program (TOKEN_PROGRAM_ID or TOKEN_2022)                                |

The `deposit_apy` field already includes underlying token yield (e.g. LST staking
rates). No manual computation needed -- just sort by `deposit_apy` descending.

**Borrowing is only available on P0 venue banks.** Kamino and Drift banks are
deposit-only -- you can earn yield on them but cannot borrow from them. When
looking for borrow opportunities, filter to `venue === "P0"`.

**Finding best deposit yields:**

Sort banks by `deposit_apy` descending.

**Finding cheapest stablecoin borrows:**

Filter where `venue` is `"P0"` and `symbol` is in `[USDC, USDT, USDG, USDS, HYUSD]`,
sort by `borrow_apy` ascending.

**Matching wallet holdings to banks:** Use the `mint` field to match tokens in
the wallet to available banks. A wallet token account's mint address corresponds
to a bank's `mint` field.

### Strategies endpoint

`GET https://ai.0.xyz/api/strategies`

Returns precomputed strategies showing the best deposit/borrow combinations
with projected APYs. Useful for finding which token to deposit and which to
borrow for the best spread.

```typescript
const res = await fetch("https://ai.0.xyz/api/strategies");
const strategies = await res.json();
```

**Fields per strategy:**

| Field                  | Description                                           |
| ---------------------- | ----------------------------------------------------- |
| `heading`              | Human-readable name (e.g. "bbSOL/SOL Rate Arbitrage") |
| `primaryBankAddress`   | Bank to deposit into                                  |
| `secondaryBankAddress` | Bank to borrow from                                   |
| `spread`               | Rate spread between deposit and borrow                |
| `leverage`             | Leverage multiplier                                   |
| `apy`                  | Projected APY (decimal, e.g. 0.085 = 8.5%)            |

The endpoint returns the top strategies sorted by APY descending. The `heading`
field describes the strategy type (e.g. "Rate Arbitrage", "Loop", etc.).

**Using strategies to plan deposits and borrows:**

Strategies show which deposit/borrow pairs have the best spread. The agent can
execute these as separate deposit + borrow operations:

```typescript
// Strategies are already sorted by APY descending
const best = strategies[0];
// best.primaryBankAddress = bank to deposit into
// best.secondaryBankAddress = bank to borrow from
// Execute as: deposit into primaryBank, then borrow from secondaryBank
```

**Connecting strategies to banks:** Use `primaryBankAddress` and
`secondaryBankAddress` to look up bank details from the banks endpoint.

### Wallet endpoint

`GET https://ai.0.xyz/api/wallet/{address}`

Returns all token holdings for a Solana wallet with balances and USD values.
No API key or RPC needed. Tokens are sorted by USD value descending.

```typescript
const res = await fetch(`https://ai.0.xyz/api/wallet/${walletAddress}`);
const data = await res.json();
// data.wallet, data.total_usd_value, data.tokens[]
```

Returns `{ wallet, total_usd_value, tokens[] }` where each token has:

| Field       | Description                              |
| ----------- | ---------------------------------------- |
| `address`   | Token mint address (matches bank `mint`) |
| `symbol`    | Token symbol (SOL, USDC, bbSOL, ...)     |
| `name`      | Token name                               |
| `decimals`  | Token decimal places                     |
| `balance`   | Human-readable balance (UI amount)       |
| `usd_price` | Price per token in USD                   |
| `usd_value` | Total USD value of this holding          |

---

## On-Chain: Interacting with the Protocol

Use the TypeScript SDK for actions that require signing: create account, deposit,
withdraw, borrow, repay. Requires a Solana keypair and user authorization.

### Prerequisites

- Node.js >= 18
- Solana keypair (JSON byte array)
- Funded wallet (SOL for tx fees + tokens to deposit)
- **Paid RPC endpoint** -- check `.env` for `RPC_URL`, otherwise ask user
  (see Agent Workflow step 4)
- **Wallet address** -- optionally check `.env` for `WALLET_ADDRESS` for
  read-only operations (see Agent Workflow step 4)
- **Wallet keypair** -- check `.env` for `WALLET_KEYPAIR`, or use path
  provided by user in their message (see Agent Workflow step 4)
- **P0 account** -- optionally check `.env` for `P0_ACCOUNT` to skip
  account selection (see Agent Workflow step 4)
- **Jupiter API key** -- check `.env` for `JUPITER_API_KEY`, only needed
  for swaps (see Agent Workflow step 5)

### Wallet setup

The agent needs a Solana keypair to sign transactions. Resolve the path
using this priority:

1. If the user provided a path in their message, use it directly
2. Check `.env` for `WALLET_KEYPAIR`
3. If neither, ask: _"I need a Solana keypair to sign transactions. Set
   `WALLET_KEYPAIR` in your `.env` to the file path, or tell me where
   your keypair JSON file is."_

```typescript
import { Keypair } from "@solana/web3.js";
import fs from "fs";

// keypairPath from user message, or WALLET_KEYPAIR from .env
const wallet = Keypair.fromSecretKey(
  Uint8Array.from(JSON.parse(fs.readFileSync(keypairPath, "utf-8"))),
);
```

To generate a new keypair:

```bash
solana-keygen new --outfile ~/.config/solana/id.json
# Then add to .env: WALLET_KEYPAIR=~/.config/solana/id.json
```

### Install

```bash
npm install @0dotxyz/p0-ts-sdk
```

`@solana/web3.js` (1.98.4) is bundled as a direct dependency -- no need to
install it separately.

Full SDK documentation: https://docs.0.xyz/typescript-sdk/overview

### Initialize client

```typescript
import { Connection } from "@solana/web3.js";
import { Project0Client, getConfig } from "@0dotxyz/p0-ts-sdk";

// RPC_URL from .env or provided by user
const connection = new Connection(RPC_URL, "confirmed");
const config = getConfig("production");
const client = await Project0Client.initialize(connection, config);
```

Reuse the client instance. Do not reinitialize per operation.

### Create or load account

A P0 account (MarginfiAccount) is an on-chain PDA that holds positions.
One wallet can own multiple accounts via different `accountIndex` values.
Each account has isolated positions and risk — collateral in one account
is NOT accessible from another.

```typescript
import { PublicKey } from "@solana/web3.js";

let wrappedAccount: MarginfiAccountWrapper;

// If P0_ACCOUNT is set in .env, use it directly
if (process.env.P0_ACCOUNT) {
  wrappedAccount = await client.fetchAccount(
    new PublicKey(process.env.P0_ACCOUNT),
  );
} else {
  const accountAddresses = await client.getAccountAddresses(wallet.publicKey);

  if (accountAddresses.length === 0) {
    // No accounts -- create one
    const createTx = await client.createMarginfiAccountTx(
      wallet.publicKey,
      0, // accountIndex
    );
    createTx.recentBlockhash = (
      await connection.getLatestBlockhash()
    ).blockhash;
    createTx.sign(wallet);
    const createSig = await connection.sendRawTransaction(createTx.serialize());
    await connection.confirmTransaction(createSig, "confirmed");

    const created = await client.getAccountAddresses(wallet.publicKey);
    wrappedAccount = await client.fetchAccount(created[0]!);
  } else if (accountAddresses.length === 1) {
    // Single account -- use it
    wrappedAccount = await client.fetchAccount(accountAddresses[0]!);
  } else {
    // Multiple accounts -- ask the user which to use
    // Present: "You have N P0 accounts:
    //   1) 3p16...s4aq
    //   2) 7xKm...2fNp
    //   Which account should I use?"
    wrappedAccount = await client.fetchAccount(chosenAddress);
  }
} // end P0_ACCOUNT else
```

**IMPORTANT — persist the account address.** If you deposited in a previous
step, store `wrappedAccount.address` and reuse it for subsequent operations
(borrow, withdraw, repay). Do NOT re-discover accounts and blindly pick
`accountAddresses[0]` — it may be a different account than the one you
deposited into.

---

## Core Operations

### Deposit

Returns a legacy transaction. Amounts are in UI units (human-readable numbers).

**SOL gas reserve:** When depositing SOL, always keep at least **0.01 SOL** in
the wallet for transaction fees. Depositing the entire SOL balance will cause
subsequent transactions to fail.

```typescript
const depositTx = await wrappedAccount.makeDepositTx(bankAddress, 100);
depositTx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
depositTx.sign(wallet);
const sig = await connection.sendRawTransaction(depositTx.serialize());
await connection.confirmTransaction(sig, "confirmed");
```

### Withdraw

Returns a versioned transaction bundle. Send each tx sequentially.

```typescript
const withdrawResult = await wrappedAccount.makeWithdrawTx(
  bankAddress,
  50,
  false, // set true to withdraw all
);
for (const tx of withdrawResult.transactions) {
  tx.sign([wallet]);
  const sig = await connection.sendRawTransaction(tx.serialize());
  await connection.confirmTransaction(sig, "confirmed");
}
```

### Borrow

Returns a versioned transaction bundle (may include oracle crank txs).

**Pre-borrow checks are mandatory.** Skipping these will result in failed
transactions (program error 6009) or wasted fees.

```typescript
// 1. Verify this account has collateral
if (wrappedAccount.activeBalances.length === 0) {
  throw new Error("Account has no deposits -- deposit collateral first");
}

// 2. Check max borrow capacity for this bank
const maxBorrow = wrappedAccount.computeMaxBorrowForBank(bankAddress);
if (maxBorrow.isZero()) {
  throw new Error(
    "No borrow capacity -- check this is the correct account and it has " +
      "sufficient collateral. If the wallet has multiple accounts, ask the " +
      "user which one to use.",
  );
}

// 3. Clamp to max (leave 5% buffer for price movement)
const amount = Math.min(desiredAmount, maxBorrow.toNumber() * 0.95);

// 4. Build and send (verify each tx -- see Transaction Verification below)
const borrowResult = await wrappedAccount.makeBorrowTx(bankAddress, amount);
for (const tx of borrowResult.transactions) {
  tx.sign([wallet]);
  const sig = await connection.sendRawTransaction(tx.serialize());
  const confirmation = await connection.confirmTransaction(sig, "confirmed");
  if (confirmation.value.err) {
    throw new Error(
      `Borrow tx failed: ${JSON.stringify(confirmation.value.err)}`,
    );
  }
}
```

### Repay

Returns a legacy transaction.

```typescript
// Repay specific amount
const repayTx = await wrappedAccount.makeRepayTx(bankAddress, 50, false);

// Repay all debt
const repayAllTx = await wrappedAccount.makeRepayTx(bankAddress, 0, true);

repayTx.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;
repayTx.sign(wallet);
const sig = await connection.sendRawTransaction(repayTx.serialize());
await connection.confirmTransaction(sig, "confirmed");
```

### Transaction verification

After sending any transaction, always verify it succeeded on-chain.
`confirmTransaction` only confirms the tx was included in a block — it does
NOT check whether the program executed successfully. A transaction can be
"confirmed" but still fail at the program level (e.g., error 6009:
"RiskEngine rejected").

```typescript
const sig = await connection.sendRawTransaction(tx.serialize());
const confirmation = await connection.confirmTransaction(sig, "confirmed");

// CRITICAL -- check for program-level errors
if (confirmation.value.err) {
  throw new Error(
    `Transaction failed: ${JSON.stringify(confirmation.value.err)}` +
      `\nhttps://solscan.io/tx/${sig}`,
  );
}

// Only report success AFTER this check passes
console.log(`Success: https://solscan.io/tx/${sig}`);
```

**Never report a transaction as successful without checking
`confirmation.value.err`.** If `err` is not null, the transaction landed
on-chain but the program rejected it — the user's funds were not moved.

**Retry policy:** If a transaction fails, do NOT retry more than once.
Report the failure with the Solscan link and the error message, and let the
user decide how to proceed.

---

## Swapping Tokens via Jupiter

If the wallet holds a different token than what a strategy requires (e.g.
holds SOL but the best yield is for bbSOL), swap first using the Jupiter API.

**Jupiter requires an API key.** Check `.env` for `JUPITER_API_KEY` or
`JUP_API_KEY`. If not found, ask the user: _"I need a Jupiter API key for
the token swap. Get a free one at https://portal.jup.ag (60 req/min)"_

### Get a quote and execute swap

```typescript
import { VersionedTransaction } from "@solana/web3.js";

// JUP_API_KEY from .env or provided by user
const inputMint = "So11111111111111111111111111111111111111112"; // SOL
const outputMint = "Bybit2vBJGhPF52GBdNaQfUJ6ZpThSgHBobjWZpLPb4B"; // bbSOL
const amount = 100000000; // raw integer units (0.1 SOL = 100000000 lamports)

// 1. Get quote
const quoteResponse = await (
  await fetch(
    `https://api.jup.ag/swap/v1/quote?inputMint=${inputMint}` +
      `&outputMint=${outputMint}` +
      `&amount=${amount}` +
      `&slippageBps=50` +
      `&restrictIntermediateTokens=true`,
    { headers: { "x-api-key": JUP_API_KEY } },
  )
).json();

// 2. Build swap transaction
const swapResponse = await (
  await fetch("https://api.jup.ag/swap/v1/swap", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": JUP_API_KEY,
    },
    body: JSON.stringify({
      quoteResponse,
      userPublicKey: wallet.publicKey.toBase58(),
      dynamicComputeUnitLimit: true,
      dynamicSlippage: true,
      prioritizationFeeLamports: {
        priorityLevelWithMaxLamports: {
          maxLamports: 1000000,
          priorityLevel: "veryHigh",
        },
      },
    }),
  })
).json();

// 3. Sign and send
const swapTx = VersionedTransaction.deserialize(
  Buffer.from(swapResponse.swapTransaction, "base64"),
);
swapTx.sign([wallet]);
const sig = await connection.sendRawTransaction(swapTx.serialize());
await connection.confirmTransaction(sig, "confirmed");
console.log(`Swap: https://solscan.io/tx/${sig}`);
```

`amount` is in raw integer units (lamports for SOL, smallest unit for SPL).
Use `mint_decimals` from the banks API to convert.

---

## Health Monitoring & Portfolio

### Checking portfolio positions

```typescript
import { MarginRequirementType } from "@0dotxyz/p0-ts-sdk";

// List all active positions
for (const balance of wrappedAccount.activeBalances) {
  const bank = client.getBank(balance.bankPk);
  if (!bank) continue;
  const bankAddr = balance.bankPk.toBase58();
  const multiplier = client.assetShareValueMultiplierByBank.get(bankAddr);
  const qty = balance.computeQuantityUi(bank, multiplier);
  // Optionally fetch bank metadata from banks API for symbol/venue labels
  if (qty.assets.gt(0))
    console.log(`Deposit: ${qty.assets.toFixed(4)} ${bankAddr}`);
  if (qty.liabilities.gt(0))
    console.log(`Borrow:  ${qty.liabilities.toFixed(4)} ${bankAddr}`);
}

// Account-level metrics
const health = wrappedAccount.computeHealthComponentsFromCache(
  MarginRequirementType.Maintenance,
);
const healthFactor = health.assets.dividedBy(health.liabilities).toNumber();
console.log(
  `Account value: $${wrappedAccount.computeAccountValue().toFixed(2)}`,
);
console.log(`Health factor: ${healthFactor.toFixed(2)}`);
console.log(
  `Free collateral: $${wrappedAccount.computeFreeCollateralFromCache().toFixed(2)}`,
);
console.log(`Net APY: ${(wrappedAccount.computeNetApy() * 100).toFixed(2)}%`);
```

### Health factor reference

| Health Factor | Status                          |
| ------------- | ------------------------------- |
| > 2.0         | Healthy                         |
| 1.1 - 2.0     | Monitor closely                 |
| 1.0 - 1.1     | Danger -- repay or deposit more |
| < 1.0         | Liquidatable                    |

---

## Error Reference

| Error                          | Cause                                          | Resolution                                               |
| ------------------------------ | ---------------------------------------------- | -------------------------------------------------------- |
| `Bank not found`               | No bank for the given address                  | Verify bank address from banks API                       |
| `Insufficient free collateral` | Not enough collateral to borrow                | Deposit more or borrow less                              |
| `Simulation failed`            | Transaction would fail on-chain                | Check logs -- often stale oracle or insufficient balance |
| `Transaction expired`          | Blockhash expired before confirmation          | Retry with fresh blockhash                               |
| `Account not found`            | P0 account address does not exist              | Verify address or create a new account                   |
| `Program error 6009`           | RiskEngine rejected (bad health/stale oracles) | Verify correct account has collateral; check health      |
| `429 Too Many Requests`        | RPC rate limited                               | Use a paid RPC provider                                  |
