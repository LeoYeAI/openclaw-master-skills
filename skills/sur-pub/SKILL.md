---
name: SURGE OpenClaw (Dev)
description: Create and trade tokens on SURGE via API (DEV). Full lifecycle — wallet setup, one-time free funding, token launch, and trading (pre-DEX + post-DEX). Base URL: back.surgedevs.xyz.
author: SURGE
version: 6.0.0
tags: [token-launch, trading, defi, evm, solana, base, raydium, launchpad, bonding-curve, aerodrome, post-dex, dev]
auth:
  type: api-key
  header: X-API-Key
  management: User creates keys at app.surgedevs.xyz → Settings → API Keys
---

# SURGE OpenClaw — AI Agent Skill (Dev)

**This is the DEV skill.** API base URL: **https://back.surgedevs.xyz**. Use this for development and testing.

You are helping the user create and trade tokens on the SURGE launchpad. This document tells you **everything** you need to know. Follow it step by step.

---

## TL;DR — What This Skill Does

- User can **create a token** on EVM (Base) or Solana — for **free** (one time)
- After creation, user can **buy and sell** tokens — both pre-DEX (bonding curve / launchpad) **and** post-DEX (Aerodrome on Base / Raydium CPMM on Solana)
- **Trading auto-routes** by token phase — same endpoints work for both pre-DEX and post-DEX
- All wallets are **server-managed** — no private keys needed from user
- You (the AI agent) handle the entire process through API calls

---

## Before You Start — Checklist

Before doing anything, make sure you have:

| # | What | How to check |
|---|------|-------------|
| 1 | **API Key** | User gives you a key starting with `sk-surge-...`. If they don't have one — see "How to Get an API Key" below. |
| 2 | **Working API** | Call `GET /openclaw/launch-info`. If 401 — key is bad. If 200 — you're good. |

### How to Get an API Key

If the user doesn't have an API key yet, tell them exactly this:

> **To get your API key (DEV):**
> 1. Go to [app.surgedevs.xyz](https://app.surgedevs.xyz)
> 2. Sign up / log in (you can use your wallet, email, or social login)
> 3. Go to **Settings → API Keys**
> 4. Click **Generate** and give it a name (e.g. "My Agent")
> 5. **Copy the key immediately** — it's shown only once!
> 6. Give the key to me and I'll handle everything from here
>
> You can have up to 5 active keys. If you lose one, revoke it and create a new one.

Once you have the key, proceed to Step 0.

---

## Step 0: Load Configuration (do this silently)

Call this **before talking to the user about tokens**:

```
GET /openclaw/launch-info
Header: X-API-Key: {key}
Base URL: https://back.surgedevs.xyz
```

This gives you live data — fees, chains, categories. **Never hardcode these values.**

You now know:
- Which chains are available and their fees
- `minBalance` — how much the wallet needs
- Available categories for tokens
- File size limits

If this fails with **401** — tell the user their API key is invalid and point them to app.surgedevs.xyz → Settings → API Keys.

---

## Step 1: Create a Wallet

The user needs a server-managed wallet. One wallet per chain type (EVM or Solana).

**For EVM (Base, BNB):**
```
POST /openclaw/wallet/create
Header: X-API-Key: {key}
```

**For Solana:**
```
POST /openclaw/wallet/create-solana
Header: X-API-Key: {key}
```

Response:
```json
{
  "walletId": "vun3srwayi6z1h8momm83tdr",
  "address": "0xD29c...Be2E",
  "chainType": "EVM",
  "needsFunding": true,
  "isNew": true
}
```

- Save `walletId` — you'll need it for everything
- If `isNew: false` — wallet already existed, that's fine
- The wallet is linked to the user's account

**Tell the user:**
> I've created a server-managed wallet for you. No private keys to worry about — everything is handled securely on our side.

---

## Step 2: Fund the Wallet (ONE TIME FREE)

**Important rule: The platform funds each wallet exactly ONCE for free.** This covers the gas + minimum buy for the first token launch. After that, the user pays for everything themselves.

```
POST /openclaw/wallet/{walletId}/fund
Header: X-API-Key: {key}
```

**If successful** (`needsFunding: false`):
> Your wallet has been funded! You get one free token launch from SURGE — gas and fees are covered.

**If already funded** (second call):
> This wallet was already funded. The free launch is a one-time gift. If you need more funds (for trading, etc.), send ETH/SOL directly to your wallet address: `{address}`

**If funding fails** (e.g. platform funder is low):
> Automatic funding didn't go through right now. You can either:
> 1. Try again in a few minutes
> 2. Send funds manually to your wallet address: `{address}` on the Base network
>
> The minimum balance needed is **{minBalance}** (from launch-info).

---

## Step 3: Check Balance

```
GET /openclaw/wallet/{walletId}/balance
Header: X-API-Key: {key}
```

Response includes `sufficient: true/false` and `minRequired` per chain.

**If `sufficient: true`** — proceed to token creation.

**If `sufficient: false`** — tell the user:
> Your wallet balance is **{balance}** but you need at least **{minRequired}**. Please send **{minRequired - balance}** to your wallet address: `{address}` on **{chain}**.

---

## Step 4: Collect Token Information

Now collect what's needed to launch the token. **Ask one group at a time. Don't dump everything at once.**

### 4a. Name, Ticker, Description (REQUIRED)

Ask:
> Let's create your token! I need three things to start:
> 1. **Token name** — the full name (e.g. "NeuralNet Token")
> 2. **Ticker** — short symbol, 3-5 letters (e.g. "NNET")
> 3. **Description** — one sentence about what the token is for (e.g. "Decentralized AI compute marketplace")

Rules:
- If user gives only a ticker — ask for the full name
- If user gives a paragraph as description — say: "Great, I'll use that as the detailed description. Can you give me a one-liner tagline too?"
- **Never make up names, tickers, or descriptions yourself**

### 4b. Logo Image (REQUIRED)

Ask:
> Now I need a logo for your token. Send me a **direct link** to an image file (PNG, JPG, or WEBP, max 5MB).

**How to get a direct image link:**

If the user has a file on their computer, tell them:

> Upload your image to get a direct link. The easiest way:
> ```
> curl -F "file=@your-logo.png" https://file.io
> ```
> This will give you a direct URL. Send it to me!
>
> **Other options:**
> - [imgur.com](https://imgur.com) → upload → right-click image → "Copy image address" (must start with `i.imgur.com`)
> - [postimages.org](https://postimages.org) → upload → copy "Direct link"
> - Any public URL that ends in .png / .jpg / .webp

**Validate before accepting:**
- URL must start with `http://` or `https://`
- Must be a **direct file link**, not a gallery page
  - GOOD: `https://i.imgur.com/abc123.png`, `https://file.io/abc123`
  - BAD: `https://imgur.com/abc123` (gallery page)
  - BAD: `https://drive.google.com/file/d/...` (preview page, not direct)

### 4c. Chain (REQUIRED)

Build this question from launch-info data:

> Which blockchain do you want to launch on?
>
> Available:
> - **Base** (EVM) — fee: {fee} ETH
> - **Solana** — fee: {fee} SOL
>
> Base is recommended for most projects. Solana is great for high-speed, low-cost trading.

Map the user's choice to the correct `chainId` from launch-info. The user should never see raw IDs.

**This determines everything else:**
- EVM → use `/launch`, needs `ethAmount`
- Solana → use `/launch-solana`, needs `preBuyAmount`

### 4d. Initial Buy Amount (REQUIRED)

**If EVM chain:**

Ask:
> How much ETH do you want for the initial buy? This buys the very first tokens when your contract launches.
>
> - Minimum: slightly more than **{fee} ETH** (the contract fee)
> - Recommended: **{fee × 2} ETH** for a good start
> - This determines the starting price — bigger amount = higher starting price

| User says | What to do |
|-----------|-----------|
| Less than or equal to fee | "The contract fee is {fee} ETH. Your amount must be higher. I'd recommend {fee × 2}." |
| Reasonable (0.01–1 ETH) | Accept |
| Very large (10+ ETH) | "That's {amount} ETH — are you sure?" |

**If Solana chain:**

First ask which currency:
> Which currency do you want for your token's fundraising pool?
>
> - **SOL** (default) — fundraising goal: 85 SOL. Your initial buy is in SOL.
> - **USD1** (stablecoin) — fundraising goal: 12,500 USD1. Your initial buy is in USD1.
>
> Most projects use SOL. USD1 is for stablecoin-based pools.

Then ask for the amount:
> How much {SOL/USD1} for the initial buy? Even a small amount like **0.01** works.

**Important about funding:**
- If user picks **SOL** — the one-time free funding covers platform fee + gas + min preBuy. They're ready to go.
- If user picks **USD1** — the free funding only covers SOL (for platform fee + gas). The user **must have USD1 tokens in their wallet** for the initial buy. Tell them:
  > Since you chose USD1, you'll need USD1 tokens in your Solana wallet for the initial buy. The platform covers SOL fees, but USD1 you provide yourself. Send USD1 to your wallet address: `{address}`

### 4e. Category (OPTIONAL — but suggest it)

Based on what the user already told you, suggest 2-3 matching categories:

> Based on your description, this sounds like an **AI** project. Should I set the category to `ai`? Or is it more `defi` / `infrastructure`?

Available categories: `ai`, `infrastructure`, `meme`, `rwa`, `defi`, `privacy`, `derivatives`, `gamefi`, `robotics`, `depin`, `desci`, `healthcare`, `education`, `socialfi`

**Don't list all 14.** Just suggest the best 2-3 matches.

### 4f. Optional Extras

Ask once:
> Want to add any extras? All optional — you can add them later on app.surgedevs.xyz:
> - **Banner image** (wide header, 1200×400 ideal)
> - **Detailed description** (markdown supported)
> - **Pitch deck or whitepaper** (PDF, up to 100MB)
> - **Social links** (website, Twitter/X, Telegram, Discord, GitHub)
> - **Team description**

If user says "no" / "skip" — move to confirmation.

**For files (banner, pitch deck, whitepaper)** — same upload process:
> Upload your file to get a link:
> ```
> curl -F "file=@your-file.pdf" https://file.io
> ```

**Convert social handles automatically:**
- `@neuralnet` → `https://x.com/neuralnet`
- `t.me/neuralnet` → `https://t.me/neuralnet`
- `discord.gg/abc` → `https://discord.gg/abc`

---

## Step 5: Confirm Before Launch

**ALWAYS show a summary. ALWAYS wait for explicit "yes".**

> Here's your token ready to launch:
>
> **Token:** {name} ({ticker})
> **Description:** {description}
> **Category:** {category or "not set"}
> **Chain:** {chainName}
> **Initial buy:** {ethAmount} ETH (chain fee: {fee} ETH)
> **Logo:** {logoUrl}
> **Wallet:** {walletId}
> {any other filled fields}
>
> **This is irreversible.** Once launched, the token goes live immediately.
>
> Ready to launch? (yes/no)

- Only proceed after explicit "yes" / "go" / "launch" / "do it"
- If user says "change X" — update that field and show summary again

---

## Step 6: Launch

**EVM:**
```
POST /openclaw/launch
Header: X-API-Key: {key}
Content-Type: application/json

{
  "name": "NeuralNet Token",
  "ticker": "NNET",
  "description": "Decentralized AI compute marketplace",
  "logoUrl": "https://i.imgur.com/abc123.png",
  "chainId": "CHAIN_ID_FROM_LAUNCH_INFO",
  "walletId": "YOUR_WALLET_ID",
  "ethAmount": "0.01"
}
```

**Solana:**
```
POST /openclaw/launch-solana
Header: X-API-Key: {key}
Content-Type: application/json

{
  "name": "NeuralNet Token",
  "ticker": "NNET",
  "description": "Decentralized AI compute marketplace",
  "logoUrl": "https://i.imgur.com/abc123.png",
  "chainId": "SOLANA_CHAIN_ID_FROM_LAUNCH_INFO",
  "walletId": "YOUR_SOLANA_WALLET_ID",
  "preBuyAmount": "0.5"
}
```

---

## Step 7: After Launch

**EVM success — tell the user:**
> Your token **{name} ({ticker})** is live!
>
> Transaction: https://basescan.org/tx/{txHash}
> View on SURGE (DEV): https://app.surgedevs.xyz
>
> It may take a minute to appear on the platform. Your token is now trading on the bonding curve — anyone can buy and sell!

**Solana success:**
> Your token **{name} ({ticker})** is live!
>
> Transaction: https://solscan.io/tx/{signature}
> Token: https://solscan.io/token/{mint}
> View on SURGE (DEV): https://app.surgedevs.xyz
>
> Your token is now trading on the Raydium launchpad!

---

## Error Handling — What to Tell the User

When something goes wrong, **don't show raw errors**. Translate them:

| Error contains | What to say |
|---------------|-------------|
| `"image"` or `"download"` | "I couldn't download your logo. Make sure it's a **direct link** to an image file, not a gallery page. Try uploading to file.io: `curl -F 'file=@logo.png' https://file.io`" |
| `"explicit"` | "Your image was flagged as inappropriate. Please use a different image." |
| `"fee"` or `"ethAmount"` | "The amount is too low. The current fee on {chain} is **{fee}** — your amount must be higher. Try **{fee × 2}**." |
| `"not a Solana wallet"` | "You're using an EVM wallet for Solana. Let me create a Solana wallet for you." → Call `/wallet/create-solana` |
| `"Wallet not found"` | "That wallet doesn't exist. Let me create a new one for you." → Call `/wallet/create` |
| `"already funded"` | "Your wallet was already funded with the free launch. For more funds, send to your wallet address: `{address}`" |
| `"insufficient funds"` | "Your wallet doesn't have enough balance. Send at least **{minBalance}** to `{address}` on **{chain}**." |
| `"not on bonding curve"` | "This token has graduated to the DEX. Don't worry — our API handles DEX trading automatically. Try your buy/sell again." |
| `"arithmetic underflow"` | "The sell amount is too large for the current pool. Try selling a smaller amount." |
| `"Daily funding limit"` | "Platform funding is temporarily unavailable. Send funds manually to `{address}`." |
| 401 | "Your API key is invalid or expired. Go to app.surgedevs.xyz → Settings → API Keys to generate a new one." |
| 429 | "Too many requests. Wait a moment and try again." |
| 500 | "Server error — not your fault. Let's try again in a minute." |

---

## Trading (After Token Launch)

After a token is launched, you can buy and sell. **Trading requires the wallet to have funds — the free funding only covers the first launch.**

Tell the user:
> To trade, you'll need funds in your wallet. Send ETH/SOL to your wallet address: `{address}`

### How Trading Works — Auto-Routing

**You don't need to choose the trading method.** The API automatically detects the token phase and routes your trade:

- **Pre-DEX (bonding curve / launchpad)** — Trade directly on the SURGE bonding curve (EVM) or Raydium launchpad (Solana)
- **Post-DEX (Aerodrome / Raydium CPMM)** — After graduation (100% bonding curve), the token migrates to a DEX. The API swaps automatically via Aerodrome (Base) or Raydium CPMM (Solana)

**Same endpoints, same parameters, regardless of phase.** Just call `/buy` or `/sell`.

### EVM Trading — Check Token Phase (optional)

```
POST /openclaw/token-status
{ "chainId": "1", "tokenAddress": "0x..." }
```

| Phase | Meaning | How `/buy` and `/sell` work |
|-------|---------|-----------|
| `bonding_curve` | Pre-DEX, active trading | Trades via BondingETHRouter (bonding curve) |
| `migrated_to_dex` | Graduated to Aerodrome DEX | Trades via Aerodrome Router (DEX swap with `agentToken`) |
| `not_launched` | Not active | Cannot trade — returns error |

The response includes `agentTokenAddress` for post-DEX tokens. You don't need it — the API handles routing automatically.

### EVM Price Quote (Post-DEX only)

```
POST /openclaw/quote
{
  "chainId": "1",
  "tokenAddress": "0x...",
  "amount": "0.01",
  "side": "buy"
}
```

Returns `amountIn`, `amountOut`, `phase`. Only works for `migrated_to_dex` tokens.

### Buy EVM Tokens

```
POST /openclaw/buy
{
  "chainId": "1",
  "walletId": "abc123",
  "tokenAddress": "0x...",
  "ethAmount": "0.01",
  "amountOutMin": "0"
}
```

Works for **both** bonding curve and post-DEX. The API detects the phase automatically.

### Sell EVM Tokens

```
POST /openclaw/sell
{
  "chainId": "1",
  "walletId": "abc123",
  "tokenAddress": "0x...",
  "tokenAmount": "1000",
  "amountOutMin": "0"
}
```

Notes:
- Auto-approves ERC-20 allowance if needed (both bonding curve and Aerodrome router)
- Don't sell too much at once — can cause revert on small pools
- `amountOutMin: "0"` = no slippage protection (use `getQuote` to set a reasonable value for post-DEX)
- For post-DEX sells: you're selling the `agentToken`, but pass the original `tokenAddress` — the API resolves it

### Buy Solana Tokens

```
POST /openclaw/buy-solana
{
  "chainId": "3",
  "walletId": "sol_wallet_id",
  "mintAddress": "7pB8z...",
  "solAmount": "0.01"
}
```

Works for **both** Raydium launchpad (pre-DEX) and CPMM (post-DEX).

### Sell Solana Tokens

```
POST /openclaw/sell-solana
{
  "chainId": "3",
  "walletId": "sol_wallet_id",
  "mintAddress": "7pB8z...",
  "tokenAmount": "1000"
}
```

Notes:
- Gas fees paid by platform (gas sponsorship)
- 5% slippage applied automatically
- `mintAddress` = the `mint` from launch response
- Post-DEX: uses Raydium Transaction API for CPMM swap

---

## API Reference — All Endpoints

### Authentication

Every request:
```
X-API-Key: sk-surge-...
```

### Base URL (DEV)
```
https://back.surgedevs.xyz
```

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| `GET /launch-info` | 30/min |
| `POST /launch`, `/launch-solana` | 5/min |
| `POST /wallet/create*` | 5/min |
| `GET /wallet/:id` | 20/min |
| `GET /wallet/:id/balance` | 10/min |
| `POST /wallet/:id/fund` | 3/min |
| `POST /token-status`, `/quote` | 20/min |
| `POST /buy`, `/sell`, `/buy-solana`, `/sell-solana` | 10/min |

---

### GET /openclaw/launch-info

Live config: fees, chains, categories, file limits.

Response:
```json
{
  "chains": [
    {
      "chainId": "1",
      "chainName": "Base",
      "networkId": "8453",
      "chainType": "EVM",
      "fee": "0.005",
      "feeRaw": "5000000000000000",
      "feeSymbol": "ETH",
      "estimatedGas": "0.00003",
      "minBalance": "0.00536"
    },
    {
      "chainId": "3",
      "chainName": "Solana",
      "networkId": "solana",
      "chainType": "SOLANA",
      "fee": "0.1",
      "feeRaw": "100000000",
      "feeSymbol": "SOL",
      "minBalance": "0.136",
      "defaults": {
        "supply": 1000000000,
        "decimals": 6,
        "totalSellPercent": 80,
        "fundraisingGoal": { "SOL": "85", "USD1": "12500" },
        "fundraisingMints": ["SOL", "USD1"]
      }
    }
  ],
  "categories": ["ai", "infrastructure", "meme", ...],
  "limits": {
    "maxImageSize": "5MB",
    "maxDocSize": "100MB",
    "allowedImageTypes": ["image/png", "image/jpeg", "image/jpg", "image/webp"],
    "allowedDocTypes": ["application/pdf"]
  }
}
```

---

### POST /openclaw/wallet/create

Create/get EVM wallet. One per user. Returns existing if already created.

### POST /openclaw/wallet/create-solana

Create/get Solana wallet. One per user.

Response:
```json
{
  "walletId": "vun3srwayi6z1h8momm83tdr",
  "address": "0xD29c35526C950862dba83FcDaE4D3801CD23Be2E",
  "chainType": "EVM",
  "needsFunding": true,
  "isNew": true
}
```

---

### GET /openclaw/wallet/:walletId

Wallet info from DB (not on-chain).

### GET /openclaw/wallet/:walletId/balance

Real-time on-chain balance. Returns `sufficient` and `minRequired` per chain.

---

### POST /openclaw/wallet/:walletId/fund

**One-time free funding.** Works only once per wallet.

Success response:
```json
{
  "walletId": "...",
  "needsFunding": false,
  "funding": [{ "chain": "Base", "amount": "0.006", "txHash": "0x...", "success": true }]
}
```

Already funded response:
```json
{
  "needsFunding": false,
  "funding": [],
  "message": "Wallet already funded. For additional funds, send directly to the wallet address."
}
```

---

### POST /openclaw/launch

Deploy EVM token. See Step 6 for full request format.

Required: `name`, `ticker`, `description`, `logoUrl`, `chainId`, `walletId`, `ethAmount`

Optional: `bannerUrl`, `fullDescription`, `projectName`, `category`, `pitchDeckUrl`, `whitepaperUrl`, `websiteLink`, `githubLink`, `telegramLink`, `discordLink`, `xLink`, `teamShortDescription`, `teamMembers`

### POST /openclaw/launch-solana

Deploy Solana token.

Required: `name`, `ticker`, `description`, `logoUrl`, `chainId`, `walletId`, `preBuyAmount`

Optional: `fundraisingMint` ("SOL" or "USD1"), plus same optional fields as EVM.

---

### POST /openclaw/token-status

Check EVM token phase. Request: `{ "chainId": "1", "tokenAddress": "0x..." }`
Returns: `phase` (`bonding_curve` | `migrated_to_dex` | `not_launched`), `agentTokenAddress`, `price`, `marketCap`, `liquidity`.

### POST /openclaw/quote

Get Aerodrome price quote (post-DEX only). Request: `{ "chainId", "tokenAddress", "amount", "side": "buy"|"sell" }`
Returns: `amountIn`, `amountOut`, `phase`.

### POST /openclaw/buy

Buy EVM tokens. **Auto-routes** by phase: bonding curve (pre-DEX) or Aerodrome (post-DEX).
Fields: `chainId`, `walletId`, `tokenAddress`, `ethAmount`, `amountOutMin?`

### POST /openclaw/sell

Sell EVM tokens. **Auto-routes** by phase: bonding curve (pre-DEX) or Aerodrome (post-DEX).
Fields: `chainId`, `walletId`, `tokenAddress`, `tokenAmount`, `amountOutMin?`

### POST /openclaw/buy-solana

Buy Solana tokens. **Auto-routes** by phase: Raydium launchpad (pre-DEX) or CPMM (post-DEX).
Fields: `chainId`, `walletId`, `mintAddress`, `solAmount`

### POST /openclaw/sell-solana

Sell Solana tokens. **Auto-routes** by phase: Raydium launchpad (pre-DEX) or CPMM (post-DEX).
Fields: `chainId`, `walletId`, `mintAddress`, `tokenAmount`

---

### API Key Management (JWT auth — at app.surgedevs.xyz)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/openclaw/api-keys` | POST | Generate new key. Body: `{ "name": "My Bot" }`. Max 5 active. |
| `/openclaw/api-keys` | GET | List all keys (prefix only) |
| `/openclaw/api-keys/:keyId` | DELETE | Revoke a key |

---

## Agent Rules (Non-Negotiable)

| # | Rule |
|---|------|
| 1 | **Never invent data.** Don't make up names, tickers, descriptions, or URLs. Always ask. |
| 2 | **Never hardcode fees.** Always use `GET /launch-info`. |
| 3 | **Always confirm before launch.** Show summary → wait for "yes". Irreversible. |
| 4 | **Suggest, don't list.** For categories — suggest 2-3, don't dump 14. |
| 5 | **Validate URLs.** Direct image link, not gallery page. |
| 6 | **Convert handles.** `@name` → `https://x.com/name` |
| 7 | **2-3 questions per message.** Don't overwhelm. |
| 8 | **Don't re-ask.** If user mentioned info earlier, use it. |
| 9 | **Never ask for private keys.** Wallets are server-managed. |
| 10 | **One free launch.** After that, user funds manually. Be clear about this upfront. |
| 11 | **Translate errors.** Never show raw JSON errors. Use the error table above. |
| 12 | **Help with file uploads.** Always suggest `curl -F "file=@file" https://file.io` when user needs to provide a file URL. |
