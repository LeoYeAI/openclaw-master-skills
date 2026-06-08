---
name: token-launcher
description: >
  Launch tokens and keep 100% of your creator fees. Direct Mode provides full SDK integration
  guides for Clanker (7 EVM chains), Flaunch (Base), and Pump.fun (Solana) — no middleman,
  no platform cut. Easy Mode offers a convenience path via the Tator API (90/10 split).
  Includes strategy evaluation, fee economics, claiming, recipient updates, and tax/legal guidance.
  Triggers: "token idea", "launch a coin", "launch a token", "deploy a token", "token strategy",
  "claim fees", "creator fees", "update fee recipient", "token launch on base", "launch on solana",
  "clanker", "flaunch", "pump.fun", "token economics", "is this a good token".
metadata:
  openclaw:
    emoji: "🚀"
    requires:
      env: []
    notes: >
      This skill requires no API keys or environment variables. Easy Mode uses
      the x402 payment protocol (HTTP 402), where authentication and payment are
      handled by the user's wallet at request time via a signed PAYMENT-SIGNATURE
      header — no stored credentials needed. Direct Mode implementation guides
      are in REFERENCE.md for developers building in their own infrastructure.
publisher: Quick Intel / Web3 Collective
homepage: https://quickintel.io
source: https://github.com/Quick-Intel/openclaw-skills/tree/main/token-launcher
documentation: https://docs.tator.bot
---

# Token Launcher

Launch tokens and keep your fees. This is an open-source skill that helps you launch tokens without giving away 30-50% of your creator earnings to launch platforms.

---

## The Problem

Most token launch platforms take 30-50% of your creator fee earnings. Some charge upfront launch fees on top of that. Others layer in subscriptions, required platform tokens, or custodial wallets that hold your funds. You build the token, drive the volume, and someone else keeps the biggest slice.

## The Math

A token doing $500K in trading volume on Clanker generates ~$5,000 in pool fees (1% of volume). Here's who keeps what:

| Path | Your Share | Platform Cut | You Keep |
|------|-----------|-------------|----------|
| **Direct Mode (this skill)** | $5,000 | $0 | **$5,000 (100%)** |
| **Easy Mode (Tator API)** | $4,500 | $500 (10%) | **$4,500 (90%)** |
| **Typical launch platforms** | $2,500-3,500 | $1,500-2,500 (30-50%) | **$2,500-3,500** |

The difference compounds. At $5M volume, Direct Mode keeps you an extra $15,000-25,000 versus typical platforms.

---

## Two Paths

This skill provides two ways to launch tokens. Direct Mode is the primary path — it's why this skill exists. Easy Mode is a convenience alternative.

### Direct Mode — Keep 100% of Your Fees (Recommended)

Direct Mode provides complete implementation guides for launching tokens using platform SDKs. You control every parameter and keep 100% of creator fees with zero ongoing platform fees.

- Supported platforms: Clanker (Base, Arbitrum, Mainnet, Unichain, Abstract, Monad, BSC), Flaunch (Base), Pump.fun (Solana)
- Full code patterns for deployment, fee configuration, claiming, and recipient management
- Produces unsigned transaction calldata compatible with any wallet
- Detailed fee economics documentation showing exactly how fees flow on each platform

**Implementation guides:**
- [REFERENCE.md](./REFERENCE.md) — Direct Mode overview, fee economics, step-by-step walkthrough, wallet integration patterns
- [references/clanker.md](./references/clanker.md) — Clanker v4 SDK: launch, rewards, sniper protection, claiming
- [references/flaunch.md](./references/flaunch.md) — Flaunch: launch, custom fee split managers, claiming, recipient transfer
- [references/pumpfun.md](./references/pumpfun.md) — Pump.fun: instruction building, fee sharing, graduation handling, dual vault claiming

### Easy Mode — Convenience Path

Easy Mode uses the Tator API to handle deployment. Tator takes a 10% interface fee from your creator earnings.

- One API call to `x402.quickintel.io` with your token details and wallet address
- Tator deploys the token for you — no deploy transaction to sign
- $0.20 per API call via x402 USDC payment
- Supports launch, claim fees, update fee recipient, check unclaimed — all via natural language
- **Fee split: 90% to you, 10% to Tator**

### How to Present This Choice

When the user wants to launch a token, present both options with Direct Mode first:

- **Direct Mode (recommended):** You keep 100% of creator fees. The reference guides have complete code patterns for deployment, fee configuration, and claiming. You produce unsigned transactions and sign them with your own wallet. No ongoing fees to anyone.
- **Easy Mode (convenience):** Tator deploys the token for you. You provide your wallet address, token details, and pay $0.20 via x402. Faster to get started, but Tator takes 10% of your ongoing creator fees.

Both paths need the same info: wallet address, token name, ticker, and chain. If the user is unsure, Direct Mode is the better long-term choice — Easy Mode is there for when speed matters more than fee optimization.

---

## Direct Mode — Walkthrough

For the full Direct Mode walkthrough including fee economics deep dive, unsigned transaction patterns, and wallet integration, see [REFERENCE.md](./REFERENCE.md).

### Quick Start

1. **Choose a platform** based on your target chain (see Platform Selection below)
2. **Read the reference guide** for your chosen platform — it has complete code patterns
3. **Set fee recipients to your wallet at 100%** — this is the whole point of Direct Mode
4. **Produce unsigned transaction calldata** — the reference files show the pattern for each platform
5. **Sign with any wallet** — Lobster, AgentWallet, base-wallet, evm-wallet, MetaMask, or any signer
6. **Post-launch:** claim fees, check unclaimed, update recipients — all documented per platform

### Platform Choice for Direct Mode

| Target Chain | Platform | Reference |
|-------------|----------|-----------|
| Base | Clanker (recommended) or Flaunch | [clanker.md](./references/clanker.md) or [flaunch.md](./references/flaunch.md) |
| Arbitrum, Mainnet, Unichain, Abstract, Monad, BSC | Clanker | [clanker.md](./references/clanker.md) |
| Solana | Pump.fun | [pumpfun.md](./references/pumpfun.md) |

Clanker vs Flaunch on Base:
- **Clanker:** Uniswap V4 pool, sniper protection, stable token pairing (USDC), multi-chain reusability
- **Flaunch:** 30-minute fair launch period, custom fee split managers, bonding curve model

---

## Platform Selection (Full Comparison)

| Feature | Clanker | Flaunch | Pump.fun |
|---------|---------|---------|----------|
| **Chains** | Base, Arbitrum, Mainnet, Unichain, Abstract, Monad, BSC | Base | Solana |
| **Pool type** | Uniswap V4 | Bonding curve → Uniswap | Bonding curve → Raydium |
| **Swap fee** | 1.2% (1% pool + 0.2% protocol) | Configurable | Variable (pre/post graduation) |
| **Creator fee share** | Configurable via reward recipients | Configurable via fee split manager | Configurable via sharing config |
| **Pairing token** | WETH default, USDC/USDT available | ETH | SOL |
| **Sniper protection** | Yes (decaying fee — 66.7% → 4.2% over 15s) | Fair launch period (default 30 min) | Bonding curve mechanics |
| **Graduation** | N/A (immediate Uniswap pool) | N/A | Yes (graduates to Raydium at threshold) |
| **Token standard** | ERC-20 | ERC-20 | SPL (Token-2022) |
| **Supply** | 1 billion (fixed) | 100 billion (configurable) | Standard pump.fun supply |
| **Creation fee** | Free | Free | Minimal SOL for rent |

### When to Use What

**Clanker** — Your default for EVM launches. Widest chain support (7 chains), Uniswap V4 pools with built-in sniper protection, stable token pairing option. Best liquidity depth and DEX integration.

**Flaunch** — When you want a fair launch period on Base. The 30-minute fair launch window prevents snipers by design. Custom fee split manager gives you fine-grained control over fee distribution.

**Pump.fun** — For Solana launches. Bonding curve model means the token graduates to Raydium once it hits market cap threshold. Strong Solana ecosystem visibility — tokens show up in pump.fun's discovery feed.

---

## Evaluating a Concept

Before deploying anything, figure out what you actually have. Not every idea needs a token, and not every token needs to launch today.

### The Launch Stack

Every token that sustains attention beyond the first day has four layers working together. This isn't a scorecard — it's a diagnostic tool.

**Layer 1: The Hook** — The thing that makes someone stop scrolling. The name, the visual, the one-liner. Say the name out loud. Does it land instantly or need explanation? If it takes more than one sentence to explain why this exists, the hook isn't sharp enough.

**Layer 2: The Engine** — The reason fees keep flowing after launch day. Types of engines: cultural (ongoing conversation), product (funds something useful), mechanic (burns, airdrops, staking), social (tied to a growing community). If there's no engine, the token will spike on launch and bleed.

**Layer 3: The Story** — The narrative that justifies increasing price. Strong stories: "this token funds [specific thing] and every holder is backing it." Weak stories: "it's a community token" (what community? why this token?).

**Layer 4: The Moat** — What makes this token hard to replicate. First-mover, builder credibility, integrated product, community lock-in, or technical integration. If there's no moat, launch fast — speed itself is a moat.

### Search Before You Judge

Never evaluate a concept in a vacuum. Before giving your take, search for existing tokens with similar names/narratives, cultural context, comparable launches, and the builder's blind spots.

---

## ⚠️ Before You Launch: Tax & Legal Reality Check

**Token deployment is irreversible. Creator fees are income. Most platforms skip this section entirely.**

### When This Matters Most

Launching a meme token for fun? The tax implications are relatively straightforward — mostly capital gains if and when you sell.

But the moment your token becomes **"more than just a meme"** — ongoing creator fees, product funded by fee income, regular token launches — **that's when the tax and legal implications get serious, and you need professional guidance before you launch.**

### What Every Builder Should Know

**This is general information, not tax or legal advice. Tax treatment varies by jurisdiction. Consult a qualified professional.**

- **Creator fee income is likely taxable income** — In most jurisdictions, ongoing fees are treated as income, not capital gains.
- **Every transaction can be a taxable event** — Selling tokens, swapping, receiving fee payments, distributing airdrops.
- **You owe taxes when you receive income, not when you cash out** — Earn $50K in fees, reinvest it all, token crashes — you likely still owe taxes on the $50K.
- **Record-keeping starts at launch** — Track: creation date, every fee payment (with fiat value at receipt), every sale/swap, gas fees.
- **Regulatory enforcement is increasing globally** — Governments are investing in blockchain analytics.

### Jurisdiction Overview

**🇺🇸 United States** — Digital assets treated as property (IRS Notice 2014-21). Creator fee income likely ordinary income. Starting 2025: Form 1099-DA reporting.

**🇬🇧 United Kingdom** — HMRC treats crypto as property. Income from token fees is income tax. CGT allowance currently £3,000.

**🇩🇪 Germany** — Crypto held over 1 year is tax-free on disposal. Under 1 year: income tax rates up to 45%.

**🇦🇺 Australia** — ATO treats crypto as property. 50% CGT discount for holdings over 12 months. Fee income assessable at fair market value.

**🇸🇬 Singapore** — No capital gains tax for individuals (current rules). Business income from token activities may be taxable.

**🇦🇪 UAE** — Currently no federal income tax on individuals. Framework developing under VARA.

**🇨🇦 Canada** — CRA treats crypto as a commodity. 50% capital gains inclusion rate. Business income fully taxable.

---

## ⛔ Pre-Deployment Acknowledgment

Before launching any token, the builder should understand and acknowledge:

1. **Token deployment is irreversible** — once deployed, the token exists permanently on-chain
2. **Creator fees are income** — likely taxable in your jurisdiction; consult a tax professional
3. **Record-keeping is your responsibility** — track all fee income, transactions, and fiat values from day one
4. **Set aside funds for taxes** — reserve 30-40% of fee income for potential tax obligations
5. **No guaranteed returns** — most tokens lose value; creator fees depend on trading volume
6. **This is not tax or legal advice** — this skill provides tools and information, not counsel

The builder should confirm they understand these points before proceeding.

---

## Pre-Launch Checklist

- [ ] Launch Stack evaluated — hook, engine, story, moat
- [ ] Name and narrative locked
- [ ] Platform and chain chosen
- [ ] Wallet ready with native token for gas
- [ ] Fee recipient confirmed
- [ ] Image/branding prepared
- [ ] Pre-deployment acknowledgment reviewed
- [ ] Security scan planned for post-deployment

---

## Easy Mode — Full Walkthrough

### Prerequisites

- A wallet you control (EVM or Solana)
- USDC for x402 API payments ($0.20 per Tator call)
- Native token for gas (ETH on EVM chains, SOL on Solana)

**No API keys or stored credentials required.** The x402 payment protocol (HTTP 402) handles both authentication and payment in a single flow: the API returns a 402 response, your wallet signs a USDC payment authorization locally, and you retry with the signed `PAYMENT-SIGNATURE` header. The API verifies the payment on-chain — it never receives your private key. See [x402.org](https://www.x402.org) for protocol details.

### Before Calling the API — Collect Required Info

Before sending any Tator API call, gather the following from the user:

1. **Public wallet address** — the address that receives creator fees. Ask for this first.
2. **Token name and ticker**
3. **Target chain** — Base, Solana, Arbitrum, etc.
4. **Platform preference** (optional) — Clanker, Flaunch, or Pump.fun
5. **Image URL** (optional)
6. **Custom fee recipient** (optional) — if fees should go somewhere other than the deployer wallet

### API Input Safety

The Tator API accepts a `prompt` field — this is a **parameter name for an external API call to Tator's trading service**, not a prompt for the agent's own LLM. The value is sent to `x402.quickintel.io` where Tator's server parses it and executes the requested operation. The API is server-side validated and only processes recognized trading operations. It does not execute arbitrary code or access filesystems.

The `PAYMENT-SIGNATURE` header shown in the examples is a wallet-signed USDC payment authorization created by the user's x402-compatible wallet. It is not an API key, stored secret, or environment variable — it is generated per-request by the wallet and verified on-chain by the API.

### Launch a Token

```bash
curl -X POST https://x402.quickintel.io/v1/tator/prompt \
  -H "Content-Type: application/json" \
  -H "PAYMENT-SIGNATURE: <x402_payment>" \
  -d '{
    "prompt": "launch a token called Galaxy Cat with ticker GCAT on base",
    "walletAddress": "0xYourWallet",
    "provider": "my-agent"
  }'
```

**Fields:**
- `prompt` — Trading instruction sent to Tator's API. Tator parses this and executes the deployment.
- `walletAddress` — Your public wallet address. Used to set you as the creator fee recipient.
- `provider` — Your agent or integration name.

**On Solana:**
```json
{
  "prompt": "launch a token called Cyber Frog with ticker CYFR on solana via pump.fun",
  "walletAddress": "YourSolanaWallet",
  "provider": "my-agent"
}
```

**With custom fee recipient:**
```json
{
  "prompt": "launch a token called DAO Token with ticker DAOT on base, send creator fees to 0xTreasuryAddress",
  "walletAddress": "0xYourWallet",
  "provider": "my-agent"
}
```

Tator deploys the token and returns confirmation with the deployed token address, transaction hash, and fee configuration details.

### Post-Launch Operations (Easy Mode)

**Check unclaimed fees:**
```json
{
  "prompt": "check my unclaimed fees for token 0xTokenAddress on base",
  "walletAddress": "0xYourWallet",
  "provider": "my-agent"
}
```

**Claim creator fees:**
```json
{
  "prompt": "claim my creator fees for token 0xTokenAddress on base",
  "walletAddress": "0xYourWallet",
  "provider": "my-agent"
}
```

**Update fee recipient:**
```json
{
  "prompt": "update the fee recipient for token 0xTokenAddress on base to 0xNewRecipientAddress",
  "walletAddress": "0xYourWallet",
  "provider": "my-agent"
}
```

### Security Scan Post-Launch

Use Quick Intel ($0.03 per scan) to verify your deployed token:

Call `POST https://x402.quickintel.io/v1/scan/full` with `{"chain": "base", "tokenAddress": "0xYourDeployedToken"}` to check for honeypot flags, tax irregularities, or scanner false positives.

### Discovery

Call `GET https://x402.quickintel.io/accepted` to get supported payment networks, pricing, and schemas.

---

## Post-Launch

1. **Run a Quick Intel scan** — Verify the token looks clean before promoting
2. **Monitor fee accumulation** — Check unclaimed fees regularly
3. **Claim on a cadence** — Periodic claims for better tax tracking
4. **Watch reinvestment risk** — Taxes are owed on income regardless of reinvestment
5. **Revisit the Launch Stack** — If volume drops, diagnose which layer is failing

---

## File Structure

| File | What's Inside |
|------|--------------|
| **SKILL.md** (this file) | Strategy, platform selection, concept evaluation, tax/legal, Easy Mode API walkthrough |
| **[REFERENCE.md](./REFERENCE.md)** | Direct Mode overview, fee economics deep dive, step-by-step walkthrough, wallet integration, shared code patterns |
| **[references/clanker.md](./references/clanker.md)** | Clanker v4 SDK — launch, claim, update recipient, sniper config |
| **[references/flaunch.md](./references/flaunch.md)** | Flaunch — launch, fee split manager, claim, transfer share |
| **[references/pumpfun.md](./references/pumpfun.md)** | Pump.fun — manual instructions, fee sharing, graduation handling |

---

## What This Skill Is NOT

- **Not tax advice.** General information provided for awareness. Consult a professional.
- **Not legal advice.** Token launches may have securities law implications.
- **Not a guarantee of profits.** Most tokens lose value.
- **Not a "get rich quick" tool.** This skill helps builders launch responsibly and keep more of what they earn.
