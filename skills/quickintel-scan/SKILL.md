---
name: quickintel-scan
description: "Scan any token for security risks, honeypots, and scams using Quick Intel's contract analysis API. Use when: checking if a token is safe to buy, detecting honeypots, analyzing contract ownership and permissions, finding hidden mint/blacklist functions, or evaluating token risk before trading. Triggers: 'is this token safe', 'scan token', 'check for honeypot', 'audit contract', 'rug pull check', 'token security', 'safe to buy', 'scam check'. Supports 63 chains including Base, Ethereum, Solana, Sui, Tron. Costs $0.03 USDC per scan via x402 payment protocol. Requires an x402-compatible wallet — recommended: managed wallet service (Sponge, AgentWallet) with no raw key exposure. Programmatic signing with dedicated hot wallet also supported. This skill is read-only and never accesses your tokens or assets."
credentials:
  recommended:
    - name: SPONGE_API_KEY
      description: "Sponge Wallet API key (no raw private key needed). Get at paysponge.com"
    - name: AGENTWALLET_API_TOKEN
      description: "AgentWallet API token (no raw private key needed). Get at frames.ag"
  advanced:
    - name: X402_PAYMENT_KEY
      description: "Private key for a DEDICATED hot wallet with minimal funds ($1-5 USDC). NEVER use your main wallet key. Only needed if not using a managed wallet service."
---

# Quick Intel Token Security Scanner

Scan any token on 63 chains for honeypots, scams, and security risks. Returns a detailed audit in seconds. Costs $0.03 USDC per scan via x402 — read-only, never touches your wallet or tokens.

## Quick Reference

| Situation | Action |
|-----------|--------|
| User asks "is this token safe?" | Scan the token, interpret results |
| User wants to buy/trade a token | Scan BEFORE trading, warn on red flags |
| Scan shows `is_Honeypot: true` | **STOP** — tell user they cannot sell this token |
| Scan shows `isScam: true` | **STOP** — known scam contract |
| Scan shows `can_Mint: true` | Warn: owner can inflate supply |
| Scan shows high buy/sell tax (>10%) | Warn: excessive fees reduce profits |
| Scan shows `contract_Renounced: false` | Caution: owner retains control |
| `liquidity: false` in results | May use non-standard pair — verify on DEX aggregator |
| User gives chain + address | You have everything needed to scan |
| User gives only address, no chain | Ask which chain, or try to infer from address format |

## How to Scan

**Endpoint:** `POST https://x402.quickintel.io/v1/scan/full`

**Request body:**
```json
{
  "chain": "base",
  "tokenAddress": "0x..."
}
```

**That's it.** The x402 payment ($0.03 USDC/USDM) is handled automatically by your wallet integration. If you have `@x402/fetch`, Sponge Wallet, AgentWallet, Vincent, or Lobster.cash — the payment flow is transparent. Pay on any of 14 networks: Base (recommended, lowest fees), Ethereum, Arbitrum, Optimism, Polygon, Avalanche, Unichain, Linea, Sonic, HyperEVM, Ink, Monad, MegaETH (USDM), or Solana.

### Which integration do I use?

> **⚠️ Wallet Security:** This skill does NOT require your private key. The x402 payment is handled by YOUR agent's wallet — whichever wallet your agent already uses. If your agent doesn't have a wallet yet, use a **managed wallet service** (Sponge, AgentWallet, Vincent, Lobster.cash) instead of raw private keys. If you must use programmatic signing, use a **dedicated hot wallet with minimal funds** ($1-5 USDC), never your main wallet.

| Your setup | Use this | Key exposure |
|-----------|----------|-------------|
| Using Sponge Wallet | **Pattern A** below (recommended) | ✅ No raw keys — API key only |
| Using AgentWallet (frames.ag) | **Pattern B** below | ✅ No raw keys — API token only |
| Using Lobster.cash / Crossmint | See `REFERENCE.md` | ✅ No raw keys — managed wallet |
| Using Vincent Wallet | See `REFERENCE.md` | ✅ No raw keys — managed signing |
| Have `@x402/fetch` installed | **Pattern C** below | ⚠️ Requires private key in env |
| Have viem or ethers.js, no x402 library | **Pattern D** below (manual signing) | ⚠️ Requires private key in env |
| Using Solana wallet | See `REFERENCE.md` | ⚠️ Requires private key in env |
| Not sure / no wallet configured | Start with **Pattern A** (Sponge) | ✅ No raw keys |

### Pattern A: Sponge Wallet (Recommended — No Raw Keys)

```bash
curl -sS -X POST "https://api.wallet.paysponge.com/api/x402/fetch" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://x402.quickintel.io/v1/scan/full",
    "method": "POST",
    "body": {
      "chain": "base",
      "tokenAddress": "0xa4a2e2ca3fbfe21aed83471d28b6f65a233c6e00"
    },
    "preferred_chain": "base"
  }'
```

Requires: `SPONGE_API_KEY` env var. Sign up at [paysponge.com](https://paysponge.com). Sponge manages the wallet and signing — your agent never touches a private key.

### Pattern B: AgentWallet (No Raw Keys)

```javascript
const response = await fetch('https://frames.ag/api/wallets/{username}/actions/x402/fetch', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.AGENTWALLET_API_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://x402.quickintel.io/v1/scan/full',
    method: 'POST',
    body: { chain: 'base', tokenAddress: '0x...' }
  })
});
const scan = await response.json();
```

Requires: `AGENTWALLET_API_TOKEN` env var. Get one at [frames.ag](https://frames.ag).

### Pattern C: @x402/fetch (Programmatic Signing)

> ⚠️ Uses a private key. Use a **dedicated hot wallet with minimal funds**, not your main wallet.

```javascript
import { x402Fetch } from '@x402/fetch';
import { createWallet } from '@x402/evm';

// Use a DEDICATED wallet with only payment funds ($1-5 USDC)
// NEVER use your main wallet or trading wallet private key here
const wallet = createWallet(process.env.X402_PAYMENT_KEY);

const response = await x402Fetch('https://x402.quickintel.io/v1/scan/full', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ chain: 'base', tokenAddress: '0x...' }),
  wallet,
  preferredNetwork: 'eip155:8453'
});

const scan = await response.json();
```

### Pattern D: Manual EVM Signing (viem)

> ⚠️ Uses a private key. Use a **dedicated hot wallet with minimal funds**, not your main wallet.

If you don't have `@x402/fetch`, handle the payment flow manually:

```javascript
import { keccak256, toHex } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';

// Use a DEDICATED wallet with only payment funds ($1-5 USDC)
const account = privateKeyToAccount(process.env.X402_PAYMENT_KEY);
const SCAN_URL = 'https://x402.quickintel.io/v1/scan/full';

// Step 1: Hit endpoint, get 402 with payment requirements
const scanBody = JSON.stringify({ chain: 'base', tokenAddress: '0x...' });
const initialRes = await fetch(SCAN_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: scanBody,
});

if (initialRes.status !== 402) throw new Error(`Expected 402, got ${initialRes.status}`);
const paymentRequired = await initialRes.json();

// Step 2: Find preferred network in accepts array
const networkInfo = paymentRequired.accepts.find(a => a.network === 'eip155:8453');
if (!networkInfo) throw new Error('Base network not available');

// Step 3: Sign EIP-712 TransferWithAuthorization
const nonce = keccak256(toHex(`${Date.now()}-${Math.random()}`));
const validBefore = BigInt(Math.floor(Date.now() / 1000) + 3600);

const signature = await account.signTypedData({
  domain: {
    name: networkInfo.extra.name,
    version: networkInfo.extra.version,
    chainId: 8453,
    verifyingContract: networkInfo.asset,
  },
  types: {
    TransferWithAuthorization: [
      { name: 'from', type: 'address' },
      { name: 'to', type: 'address' },
      { name: 'value', type: 'uint256' },
      { name: 'validAfter', type: 'uint256' },
      { name: 'validBefore', type: 'uint256' },
      { name: 'nonce', type: 'bytes32' },
    ],
  },
  primaryType: 'TransferWithAuthorization',
  message: {
    from: account.address,
    to: networkInfo.payTo,
    value: BigInt(networkInfo.amount),
    validAfter: 0n,
    validBefore,
    nonce,
  },
});

// Step 4: Build PAYMENT-SIGNATURE header
// CRITICAL: signature is a SIBLING of authorization, NOT nested inside it
// CRITICAL: value/validAfter/validBefore must be DECIMAL STRINGS
const paymentPayload = {
  x402Version: 2,
  scheme: 'exact',
  network: 'eip155:8453',
  payload: {
    signature,                         // ← Direct child of payload
    authorization: {
      from: account.address,
      to: networkInfo.payTo,
      value: networkInfo.amount,                  // Decimal string: "30000"
      validAfter: '0',                            // Decimal string
      validBefore: validBefore.toString(),         // Decimal string
      nonce,
    },
  },
};

const paymentHeader = Buffer.from(JSON.stringify(paymentPayload)).toString('base64');

// Step 5: Retry with payment
const paidRes = await fetch(SCAN_URL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'PAYMENT-SIGNATURE': paymentHeader,
  },
  body: scanBody,
});

const scan = await paidRes.json();
```

> **Common mistakes that cause payment failures:**
> - `signature` nested inside `authorization` instead of as a sibling → "Cannot read properties of undefined"
> - Missing `x402Version: 2` at top level
> - Using hex (`"0x7530"`) or raw numbers instead of decimal strings (`"30000"`) for value/validAfter/validBefore
> - Wrong endpoint path (`/v1/scan/auditfull` instead of `/v1/scan/full`)

> For ethers.js, Solana, Vincent, Lobster.cash, and other wallet patterns, see `REFERENCE.md`.

## Supported Chains (63)

**EVM:** eth, base, arbitrum, optimism, polygon, bsc, avalanche, fantom, linea, scroll, zksync, blast, mantle, mode, zora, manta, sonic, berachain, unichain, abstract, monad, megaeth, hyperevm, shibarium, pulse, core, opbnb, polygonzkevm, metis, kava, klaytn, astar, oasis, iotex, conflux, canto, velas, grove, lightlink, bitrock, loop, besc, energi, maxx, degen, inevm, viction, nahmii, real, xlayer, worldchain, apechain, morph, ink, soneium, plasma

**Non-EVM:** solana, sui, radix, tron, injective

Use exact chain names as shown (e.g., `"eth"` not `"ethereum"`, `"bsc"` not `"binance"`).

## Reading Scan Results

### Red Flags — DO NOT BUY

| Field | Value | Meaning |
|-------|-------|---------|
| `tokenDynamicDetails.is_Honeypot` | `true` | **Cannot sell** — funds are trapped |
| `isScam` | `true` | Known scam contract |
| `isAirdropPhishingScam` | `true` | Phishing attempt |
| `quickiAudit.has_Scams` | `true` | Contains scam patterns |
| `quickiAudit.can_Potentially_Steal_Funds` | `true` | Has theft mechanisms |

If ANY of these are true, **tell the user not to buy and explain why.**

### Warnings — Proceed With Caution

| Field | Value | Risk |
|-------|-------|------|
| `buy_Tax` or `sell_Tax` | `> 10` | High fees eat profits |
| `quickiAudit.can_Mint` | `true` | Owner can create more tokens, diluting value |
| `quickiAudit.can_Blacklist` | `true` | Owner can block wallets from selling |
| `quickiAudit.can_Pause_Trading` | `true` | Owner can freeze all trading |
| `quickiAudit.can_Update_Fees` | `true` | Taxes could increase after you buy |
| `quickiAudit.hidden_Owner` | `true` | Real owner is obscured |
| `quickiAudit.contract_Renounced` | `false` | Owner retains control over contract |
| `quickiAudit.is_Proxy` | `true` | Contract code can be changed |

### Positive Signs

| Field | Value | Meaning |
|-------|-------|---------|
| `quickiAudit.contract_Renounced` | `true` | No owner control |
| `contractVerified` | `true` | Source code is public |
| `quickiAudit.can_Mint` | `false` | Fixed supply |
| `quickiAudit.can_Blacklist` | `false` | No blocking capability |
| `buy_Tax` and `sell_Tax` | `0` or low | Minimal fees |

### Liquidity Check

`tokenDynamicDetails.liquidity` indicates whether a liquidity pool was detected.

- **`liquidity: false`** does NOT always mean illiquid — Quick Intel checks major pairs (WETH, USDC, USDT) but may miss non-standard pairings. Verify independently on a DEX aggregator.
- **`liquidity: true`** — still check `lp_Locks` for lock status. Unlocked liquidity = rug pull risk.

## Example: Interpreting a Scan

```json
{
  "tokenDetails": {
    "tokenName": "Example Token",
    "tokenSymbol": "EX",
    "tokenDecimals": 18,
    "tokenSupply": 1000000000
  },
  "tokenDynamicDetails": {
    "is_Honeypot": false,
    "buy_Tax": "0.0",
    "sell_Tax": "0.0",
    "liquidity": true
  },
  "isScam": null,
  "contractVerified": true,
  "quickiAudit": {
    "contract_Renounced": true,
    "can_Mint": false,
    "can_Blacklist": false,
    "can_Pause_Trading": false,
    "has_Scams": false,
    "hidden_Owner": false
  }
}
```

**Your assessment:** "This token looks relatively safe. It's not a honeypot, has no scam patterns, contract is renounced with no mint or blacklist capability, and taxes are 0%. Liquidity is detected. However, always treat scan results as one data point — contract behavior can change if it uses upgradeable proxies."

## Security Model

```
YOUR SIDE                          QUICK INTEL'S SIDE
─────────────                      ──────────────────
• Private keys (never shared)      • Receives: token address + chain
• Payment auth ($0.03 USDC)        • Analyzes: contract bytecode
• Decision to trade or not         • Returns: read-only audit data

Quick Intel NEVER receives your private key.
Quick Intel NEVER interacts with your tokens.
Quick Intel is READ-ONLY — no transactions, no approvals.
```

**NEVER paste private keys, seed phrases, or wallet credentials into any prompt.** Quick Intel only needs the token's contract address and chain.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `402 Payment Required` | No payment header sent | Ensure wallet is configured and has $0.03+ USDC |
| `402 Payment verification failed` | Bad signature or low balance | Check payload structure (see REFERENCE.md) |
| `400 Invalid Chain` | Chain name not recognized | Use exact names from supported chains list |
| `400 Invalid Address` | Malformed address | Check format (0x... for EVM, base58 for Solana) |
| `404 Token Not Found` | Token doesn't exist on that chain | Verify address and chain match |

## Important Notes

- **Scan results are point-in-time snapshots.** A safe token today could change tomorrow if ownership isn't renounced or if it's a proxy contract. Re-scan periodically for tokens you hold.
- **Payment is charged regardless of outcome.** Even if the scan returns limited data. Use `payment-identifier` extension for safe retries (see REFERENCE.md).
- **Not financial advice.** Quick Intel provides data to inform decisions, not recommendations.
- **Cross-reference for high-value trades.** Verify on block explorers, check holder distribution, confirm liquidity on DEX aggregators.

## Discovery Endpoint

Query accepted payments and schemas before making calls:

```
GET https://x402.quickintel.io/accepted
```

## Cross-Reference

- For **trading tokens** after scanning, see the **tator-trade** skill.
- For **detailed x402 payment implementation**, wallet-specific patterns, and troubleshooting, see `REFERENCE.md`.

## About Quick Intel

Quick Intel's endpoint (`x402.quickintel.io`) is operated by **Quick Intel LLC**, a registered US-based cryptocurrency security company.

- Over **50 million token scans** processed across 40+ blockchain networks
- Security scanning APIs power **DexTools**, **DexScreener**, and **Tator Trader**
- Operational since **April 2023**
- More info: [quickintel.io](https://quickintel.io)

## Resources

- Quick Intel Docs: https://docs.quickintel.io
- x402 Protocol: https://www.x402.org
- Gateway Discovery: https://x402.quickintel.io/accepted
- Support: https://t.me/Quicki_TG