# Quick Intel x402 Payment Reference

Complete implementation guide for all wallet types and payment flows. Most agents won't need this — if you're using `@x402/fetch`, Sponge, AgentWallet, Vincent, or Lobster.cash, the payment flow is automatic. This reference is for manual integration or debugging.

> **⚠️ Security Notice:** Patterns that use programmatic signing (viem, ethers.js, @x402/fetch, Solana) require a private key in an environment variable. **Always use a dedicated hot wallet with minimal funds ($1-5 USDC)** for x402 payments. Never use your main wallet, trading wallet, or any wallet holding significant assets. Managed wallet services (Sponge, AgentWallet, Vincent, Lobster.cash) are preferred as they never expose raw private keys to your agent.

## x402 Payment Flow Overview

```
1. POST to endpoint → 2. Get 402 response → 3. Sign payment → 4. Retry with header → 5. Get scan results
```

The 402 response contains a `PAYMENT-REQUIRED` header (base64 JSON) with accepted payment networks, amounts, and signing parameters.

## Payment Networks

| Network | CAIP-2 ID | Token | Address |
|---------|-----------|-------|---------|
| Base | `eip155:8453` | USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Ethereum | `eip155:1` | USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| Arbitrum | `eip155:42161` | USDC | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |
| Optimism | `eip155:10` | USDC | `0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85` |
| Polygon | `eip155:137` | USDC | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| Avalanche | `eip155:43114` | USDC | `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` |
| Unichain | `eip155:130` | USDC | `0x078D782b760474a361dDA0AF3839290b0EF57AD6` |
| Linea | `eip155:59144` | USDC | `0x176211869cA2b568f2A7D4EE941E073a821EE1ff` |
| Sonic | `eip155:146` | USDC | `0x29219dd400f2Bf60E5a23d13Be72B486D4038894` |
| HyperEVM | `eip155:999` | USDC | `0xb88339CB7199b77E23DB6E890353E22632Ba630f` |
| Ink | `eip155:57073` | USDC | `0x2D270e6886d130D724215A266106e6832161EAEd` |
| Monad | `eip155:143` | USDC | `0x754704Bc059F8C67012fEd69BC8a327a5aafb603` |
| MegaETH | `eip155:6342` | USDM | `0xFAfDdbb3FC7688494971a79cc65DCa3EF82079E7` |
| Solana | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` | USDC | Native USDC SPL |

**Cost:** $0.03 USDC (30000 atomic units with 6 decimals) on any network. Base recommended for lowest fees.

## PAYMENT-SIGNATURE Payload Structure (Critical)

### EVM Payload (Decoded from base64)

```json
{
  "x402Version": 2,
  "scheme": "exact",
  "network": "eip155:8453",
  "payload": {
    "signature": "0x804f6127...1b",
    "authorization": {
      "from": "0xYourWalletAddress",
      "to": "0xPayToAddressFrom402Response",
      "value": "30000",
      "validAfter": "0",
      "validBefore": "1771454085",
      "nonce": "0xa1b2c3d4...bytes32hex"
    }
  }
}
```

### Solana Payload (Decoded from base64)

```json
{
  "x402Version": 2,
  "scheme": "exact",
  "network": "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",
  "payload": {
    "transaction": "base64-encoded-partially-signed-solana-transaction"
  }
}
```

### Field Rules

| Field | Type | Notes |
|-------|------|-------|
| `x402Version` | Number | **Must be `2`** |
| `scheme` | String | Always `"exact"` |
| `network` | String | CAIP-2 ID from 402 response |
| `signature` | String | **Direct child of `payload`, NOT inside `authorization`** |
| `value` | String | **Decimal string** (e.g., `"30000"`) — not hex, not BigInt |
| `validAfter` | String | **Decimal string** Unix timestamp. Use `"0"` for immediate |
| `validBefore` | String | **Decimal string** Unix timestamp. Set ~1 hour future |
| `nonce` | String | `0x`-prefixed bytes32 hex. Must be unique per payment |

## Common Mistakes

### 1. Signature nested inside authorization (WRONG)

```json
// ❌ WRONG — causes "Cannot read properties of undefined"
{ "payload": { "authorization": { "signature": "0x...", "from": "0x..." } } }

// ✅ CORRECT — signature is a SIBLING of authorization
{ "payload": { "signature": "0x...", "authorization": { "from": "0x..." } } }
```

### 2. Missing x402Version

```json
// ❌ WRONG
{ "scheme": "exact", "network": "eip155:8453", "payload": { ... } }

// ✅ CORRECT
{ "x402Version": 2, "scheme": "exact", "network": "eip155:8453", "payload": { ... } }
```

### 3. Wrong value format

```json
// ❌ WRONG — hex or raw numbers
{ "value": "0x7530" }
{ "value": 30000 }

// ✅ CORRECT — decimal string
{ "value": "30000" }
```

### 4. Wrong endpoint

```
❌ /v1/scan/auditfull
✅ /v1/scan/full
```

## Wallet Integration Patterns

### Pattern 1: @x402/fetch (Simplest — Recommended)

```javascript
import { x402Fetch } from '@x402/fetch';
import { createWallet } from '@x402/evm';

const wallet = createWallet(process.env.X402_PAYMENT_KEY);

const response = await x402Fetch('https://x402.quickintel.io/v1/scan/full', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    chain: 'base',
    tokenAddress: '0xa4a2e2ca3fbfe21aed83471d28b6f65a233c6e00'
  }),
  wallet,
  preferredNetwork: 'eip155:8453'
});

const scan = await response.json();
```

### Pattern 2: Manual EVM Signing (viem)

```javascript
import { keccak256, toHex } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';

const account = privateKeyToAccount(process.env.X402_PAYMENT_KEY);
const SCAN_URL = 'https://x402.quickintel.io/v1/scan/full';

// Step 1: Get 402 response
const scanBody = JSON.stringify({ chain: 'base', tokenAddress: '0x...' });
const initialRes = await fetch(SCAN_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: scanBody,
});
const paymentRequired = await initialRes.json();

// Step 2: Find preferred network
const networkInfo = paymentRequired.accepts.find(a => a.network === 'eip155:8453');

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

// Step 4: Build payment header
const paymentPayload = {
  x402Version: 2,
  scheme: 'exact',
  network: 'eip155:8453',
  payload: {
    signature,
    authorization: {
      from: account.address,
      to: networkInfo.payTo,
      value: networkInfo.amount,
      validAfter: '0',
      validBefore: validBefore.toString(),
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

### Pattern 3: Manual EVM Signing (ethers.js v6)

```javascript
import { ethers } from 'ethers';

const wallet = new ethers.Wallet(process.env.X402_PAYMENT_KEY);
const SCAN_URL = 'https://x402.quickintel.io/v1/scan/full';

// Step 1: Get 402 response
const scanBody = JSON.stringify({ chain: 'base', tokenAddress: '0x...' });
const initialRes = await fetch(SCAN_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: scanBody,
});
const paymentRequired = await initialRes.json();
const networkInfo = paymentRequired.accepts.find(a => a.network === 'eip155:8453');

// Step 2: Sign
const nonce = ethers.keccak256(ethers.toUtf8Bytes(`${Date.now()}-${Math.random()}`));
const validBefore = BigInt(Math.floor(Date.now() / 1000) + 3600);

const domain = {
  name: networkInfo.extra.name,
  version: networkInfo.extra.version,
  chainId: 8453,
  verifyingContract: networkInfo.asset,
};
const types = {
  TransferWithAuthorization: [
    { name: 'from', type: 'address' },
    { name: 'to', type: 'address' },
    { name: 'value', type: 'uint256' },
    { name: 'validAfter', type: 'uint256' },
    { name: 'validBefore', type: 'uint256' },
    { name: 'nonce', type: 'bytes32' },
  ],
};
const message = {
  from: wallet.address,
  to: networkInfo.payTo,
  value: BigInt(networkInfo.amount),
  validAfter: 0n,
  validBefore,
  nonce,
};

const signature = await wallet.signTypedData(domain, types, message);

// Step 3: Build header and retry (same as viem pattern above)
const paymentPayload = {
  x402Version: 2,
  scheme: 'exact',
  network: 'eip155:8453',
  payload: {
    signature,
    authorization: {
      from: wallet.address,
      to: networkInfo.payTo,
      value: networkInfo.amount,
      validAfter: '0',
      validBefore: validBefore.toString(),
      nonce,
    },
  },
};

const paymentHeader = Buffer.from(JSON.stringify(paymentPayload)).toString('base64');
const paidRes = await fetch(SCAN_URL, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'PAYMENT-SIGNATURE': paymentHeader },
  body: scanBody,
});
const scan = await paidRes.json();
```

### Pattern 4: Solana Wallet (SVM)

```javascript
import { createSvmClient } from '@x402/svm/client';
import { toClientSvmSigner } from '@x402/svm';
import { wrapFetchWithPayment } from '@x402/fetch';
import { createKeyPairSignerFromBytes } from '@solana/kit';
import { base58 } from '@scure/base';

const keypair = await createKeyPairSignerFromBytes(
  base58.decode(process.env.X402_SOLANA_PAYMENT_KEY)
);
const signer = toClientSvmSigner(keypair);
const client = createSvmClient({ signer });
const paidFetch = wrapFetchWithPayment(fetch, client);

const response = await paidFetch('https://x402.quickintel.io/v1/scan/full', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ chain: 'base', tokenAddress: '0x...' })
});
const scan = await response.json();
```

### Pattern 5: AgentWallet (frames.ag)

```javascript
const response = await fetch('https://frames.ag/api/wallets/{username}/actions/x402/fetch', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${AGENTWALLET_API_TOKEN}`,
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

### Pattern 6: Sponge Wallet (One-Liner)

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

### Pattern 7: Vincent Wallet (heyvincent.ai)

```javascript
const paymentAuth = await vincent.signPayment({
  network: 'eip155:8453',
  amount: '30000',
  token: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  recipient: recipientFromHeader
});

const response = await fetch('https://x402.quickintel.io/v1/scan/full', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'PAYMENT-SIGNATURE': paymentAuth.encoded
  },
  body: JSON.stringify({ chain: 'base', tokenAddress: '0x...' })
});
```

### Other Compatible Wallets

Any wallet supporting x402 or EIP-3009 works, including Lobster.cash (Crossmint-powered agent wallets with Visa card integration). See their respective documentation.

## Payment-Identifier (Idempotency)

Prevent double-charging on retries:

```javascript
const paymentPayload = {
  x402Version: 2,
  scheme: 'exact',
  network: 'eip155:8453',
  payload: { /* ... */ },
  extensions: {
    'payment-identifier': {
      paymentId: 'pay_' + crypto.randomUUID().replace(/-/g, '')
    }
  }
};
```

If the gateway has already processed a request with the same payment ID, it returns the cached response without charging again. IDs must be 16-128 characters, alphanumeric with hyphens and underscores.

## x402 Headers Reference

| Header | Direction | Description |
|--------|-----------|-------------|
| `PAYMENT-REQUIRED` | Response (402) | Base64 JSON with payment requirements |
| `PAYMENT-SIGNATURE` | Request (retry) | Base64 JSON with signed payment proof |
| `PAYMENT-RESPONSE` | Response (200) | Base64 JSON with settlement tx hash |

Legacy `X-PAYMENT` header is accepted for v1 backward compatibility.

## Full Response Schema

```json
{
  "tokenDetails": {
    "tokenName": "string",
    "tokenSymbol": "string",
    "tokenDecimals": 18,
    "tokenSupply": 1000000000,
    "tokenCreatedDate": 1736641803000
  },
  "tokenDynamicDetails": {
    "is_Honeypot": false,
    "buy_Tax": "0.0",
    "sell_Tax": "0.0",
    "transfer_Tax": "0.0",
    "has_Trading_Cooldown": false,
    "liquidity": false
  },
  "isScam": null,
  "isAirdropPhishingScam": false,
  "contractVerified": true,
  "quickiAudit": {
    "contract_Renounced": true,
    "hidden_Owner": false,
    "is_Proxy": false,
    "can_Mint": false,
    "can_Blacklist": false,
    "can_Update_Fees": false,
    "can_Pause_Trading": false,
    "has_Suspicious_Functions": false,
    "has_Scams": false,
    "can_Potentially_Steal_Funds": false
  }
}
```

## Resources

- Quick Intel Docs: https://docs.quickintel.io
- x402 Protocol: https://www.x402.org
- x402 EVM Spec: https://github.com/coinbase/x402/blob/main/specs/schemes/exact/scheme_exact_evm.md
- Gateway Discovery: https://x402.quickintel.io/accepted
- Quick Intel: https://quickintel.io
- Support: https://t.me/Quicki_TG