---
name: iauotpay-api
description: |
  Purchase API keys from iAutoPay Fact API using USDC on Base chain. Use this skill when:
  - Buying API keys for AI agent payment services
  - Managing API key subscriptions (1/7/30 days)
  - Checking user account information and usage statistics
  - Checking server information and pricing
  - Integrating crypto payments for API access
---

# iAutoPay Fact API

Base URLs:
- **fact-api**: `https://apipaymcp.okart.fun` (Payment API)
- **napi-ser**: `http://ipaynapi.gpuart.cn` (User Management & API Keys)

## Network Configuration

- **Chain**: Base Sepolia (Testnet)
- **Chain ID**: eip155:84532
- **Asset**: `0x036CbD53842c5426634e7929541eC2318f3dCF7e` (USDC)
- **Payee**: `0x1a85156c2943b63febeee7883bd84a7d1cf0da0c`

## Pricing

| Duration | Price (USDC) |
|----------|--------------|
| 1 day    | 0.09         |
| 7 days   | 0.49         |
| 30 days  | 0.99         |

## Endpoints

### fact-api (Payment Service)

### GET /info - Server Information

Get current server status, pricing, and configuration.

```bash
curl "https://apipaymcp.okart.fun/info"
```

**Response:**
```json
{
  "name": "iAutoPay Fact API",
  "version": "0.1.0",
  "environment": "dev",
  "network": "eip155:84532",
  "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
  "prices": {
    "1day": "90000",
    "1dayUsdc": 0.09,
    "7days": "490000",
    "7daysUsdc": 0.49,
    "30days": "990000",
    "30daysUsdc": 0.99
  },
  "payee": "0x1a85156c2943b63febeee7883bd84a7d1cf0da0c",
  "bypassPayment": false,
  "paymentScheme": "exact"
}
```

### POST /v1/buy-apikey - Purchase API Key

Buy an API key with specified duration. Payment is handled via EIP-3009 signed payment in the request header.

```bash
curl -X POST "https://apipaymcp.okart.fun/v1/buy-apikey" \
  -H "Content-Type: application/json" \
  -H "PAYMENT-SIGNATURE: '{\"from\":\"0x...\",\"to\":\"0x...\",\"value\":\"90000\",\"validAfter\":\"0\",\"validBefore\":\"1738368000\",\"nonce\":\"0x...\",\"v\":27,\"r\":\"0x...\",\"s\":\"0x...\"}'" \
  -d '{"duration": 7}'
```

**Request Body:**
```json
{
  "duration": 7
}
```

**Headers:**
| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Content-Type | string | Yes | "application/json" |
| PAYMENT-SIGNATURE | string | Yes | EIP-3009 signed payment payload (JSON string) |

**PAYMENT-SIGNATURE Payload:**
```json
{
  "from": "0x1234567890abcdef1234567890abcdef12345678",
  "to": "0x1a85156c2943b63febeee7883bd84a7d1cf0da0c",
  "value": "490000",
  "validAfter": "0",
  "validBefore": "1738368000",
  "nonce": "0xabc123...",
  "v": 27,
  "r": "0x...",
  "s": "0x..."
}
```

**Duration Options:**
| Value | Duration | Price |
|-------|----------|-------|
| 1     | 1 day    | 0.09 USDC |
| 7     | 7 days   | 0.49 USDC |
| 30    | 30 days  | 0.99 USDC |

**Response:**
```json
{
  "apiKey": "sk-7ac3d7c8fed74b0a8ae8f949e017e9f5",
  "txHash": "0x1f62f45e5ae6e8cd637048d0f099d324f749f61d35906ffe481e36e92689769b",
  "payState": "paid",
  "durationDays": 7,
  "transactionId": "ed66d250-7353-473d-bc73-0bd7541f40c0"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| apiKey | string | Your API key (use this for authentication) |
| txHash | string | Blockchain transaction hash |
| payState | string | Payment status ("paid") |
| durationDays | number | API key duration in days |
| transactionId | string | Unique transaction ID |

### POST /v1/transfer - Pay Stablecoin

Pay USDC to any address using EIP-3009 off-chain signature.

### GET /user/me - Get User Information

Get your user account information, API keys, and usage statistics. **Requires authentication with your API key.**

```bash
curl "http://ipaynapi.gpuart.cn/user/me" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_xxx",
      "walletAddress": "0x1234567890abcdef1234567890abcdef12345678",
      "createdAt": 1772072451317,
      "lastPurchasedAt": 1772072457962,
      "status": "active",
      "totalPurchases": 2
    },
    "activeApiKeys": 2,
    "totalSpent": 1480000,
    "apiKeys": [
      {
        "apiKey": "sk-xxx",
        "durationDays": 7,
        "createdAt": "2026-02-26T02:01:12.904Z",
        "expiresAt": "2026-03-05T02:01:12.904Z",
        "status": "active"
      }
    ],
    "recentTransactions": [...]
  }
}
```

**Note**: The first purchase automatically creates your user account. No separate registration is required!

### GET /user/my-keys - List User API Keys

Get all API keys for your user account. **Requires authentication with your API key.**

```bash
curl "http://ipaynapi.gpuart.cn/user/my-keys" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "apiKey": "sk-xxx",
      "durationDays": 7,
      "createdAt": "2026-02-26T02:01:12.904Z",
      "expiresAt": "2026-03-05T02:01:12.904Z",
      "status": "active"
    }
  ]
}
```

### POST /v1/transfer - Pay Stablecoin

Pay USDC to any address using EIP-3009 off-chain signature.

```bash
curl -X POST "https://apipaymcp.okart.fun/v1/transfer" \
  -H "Content-Type: application/json" \
  -H "PAYMENT-SIGNATURE: '{\"from\":\"0x...\",\"to\":\"0x...\",\"value\":\"10000\",\"validAfter\":\"0\",\"validBefore\":\"1738368000\",\"nonce\":\"0x...\",\"v\":27,\"r\":\"0x...\",\"s\":\"0x...\"}'" \
  -d '{"to": "0x1234567890abcdef1234567890abcdef12345678", "amount": "10000", "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"}'
```

**Request Body:**
```json
{
  "to": "0x1234567890abcdef1234567890abcdef12345678",
  "amount": "10000",
  "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| to | string | Yes | Recipient wallet address |
| amount | string | Yes | Amount in smallest unit (10000 = 0.01 USDC) |
| asset | string | Yes | Token contract address (USDC on Base Sepolia) |

**Headers:**
| Header | Type | Required | Description |
|--------|------|----------|-------------|
| Content-Type | string | Yes | "application/json" |
| PAYMENT-SIGNATURE | string | Yes | EIP-3009 signed payment payload (JSON string) |

**Response:**
```json
{
  "success": true,
  "transactionHash": "0x1234567890abcdef...",
  "from": "0xabcdef1234567890abcdef1234567890abcdef12",
  "to": "0x1234567890abcdef1234567890abcdef12345678",
  "amount": "0.010000",
  "deductedAmount": "0.010000 USDC",
  "currentBalance": "9.990000 USDC"
}
```

## User Management (New Feature)

The iAutoPay system now includes **automatic user registration**. When you purchase an API key for the first time, a user account is automatically created and linked to your wallet address.

### Auto-Registration Flow

1. **First Purchase**: Call `/v1/buy-apikey` with your signed payment
2. **Auto-Create User**: System automatically creates user account
3. **API Key Assigned**: API key is linked to your user account
4. **User Info Available**: Use `/user/me` to view account details

No separate registration step is required!

### User Endpoints

#### GET /user/me - Get User Information

Get your user account information, API keys, and usage statistics.

```bash
curl "http://ipaynapi.gpuart.cn/user/me" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_xxx",
      "walletAddress": "0x1234567890abcdef1234567890abcdef12345678",
      "createdAt": 1772072451317,
      "lastPurchasedAt": 1772072457962,
      "status": "active",
      "totalPurchases": 2
    },
    "activeApiKeys": 2,
    "totalSpent": 1480000,
    "apiKeys": [
      {
        "apiKey": "sk-xxx",
        "durationDays": 7,
        "createdAt": "2026-02-26T02:01:12.904Z",
        "expiresAt": "2026-03-05T02:01:12.904Z",
        "status": "active"
      }
    ],
    "recentTransactions": [...]
  }
}
```

#### GET /user/my-keys - List User API Keys

Get all API keys for your user account.

```bash
curl "http://ipaynapi.gpuart.cn/user/my-keys" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "apiKey": "sk-xxx",
      "durationDays": 7,
      "createdAt": "2026-02-26T02:01:12.904Z",
      "expiresAt": "2026-03-05T02:01:12.904Z",
      "status": "active"
    }
  ]
}
```

### GET /refresh_pricing - Refresh Pricing

Refresh pricing information from server (cached).

```bash
curl "https://apipaymcp.okart.fun/refresh_pricing"
```

**Response:**
```json
{
  "success": true,
  "prices": {
    "1day": "90000",
    "1dayUsdc": 0.09,
    "7days": "490000",
    "7daysUsdc": 0.49,
    "30days": "990000",
    "30daysUsdc": 0.99
  },
  "updatedAt": "2026-02-25T12:00:00Z"
}

```

### napi-ser (User Management)

### GET /user/me - Get User Information

Get your user account information, API keys, and usage statistics. **Requires authentication with your API key.**

```bash
curl "http://ipaynapi.gpuart.cn/user/me" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_xxx",
      "walletAddress": "0x1234567890abcdef1234567890abcdef12345678",
      "createdAt": 1772072451317,
      "lastPurchasedAt": 1772072457962,
      "status": "active",
      "totalPurchases": 2
    },
    "activeApiKeys": 2,
    "totalSpent": 1480000,
    "apiKeys": [
      {
        "apiKey": "sk-xxx",
        "durationDays": 7,
        "createdAt": "2026-02-26T02:01:12.904Z",
        "expiresAt": "2026-03-05T02:01:12.904Z",
        "status": "active"
      }
    ],
    "recentTransactions": [...]
  }
}
```

**Note**: The first purchase automatically creates your user account. No separate registration is required!

### GET /user/my-keys - List User API Keys

Get all API keys for your user account. **Requires authentication with your API key.**

```bash
curl "http://ipaynapi.gpuart.cn/user/my-keys" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "apiKey": "sk-xxx",
      "durationDays": 7,
      "createdAt": "2026-02-26T02:01:12.904Z",
      "expiresAt": "2026-03-05T02:01:12.904Z",
      "status": "active"
    }
  ]
}
```

## Payment Flow

The Fact API uses **EIP-3009 (Transfer With Authorization)** for off-chain payment signing. This means you don't need to send an on-chain transaction first - you sign a payment authorization and include it in the API request.

**Steps:**
1. **Get Payment Info**: Call `/info` to get the payee address and USDC contract address
2. **Sign Payment**: Create an EIP-3009 signature using your wallet's private key
3. **Buy API Key**: Call `/v1/buy-apikey` with signed payment in the `PAYMENT-SIGNATURE` header
4. **Auto-Registration**: The first purchase automatically creates your user account
5. **Get User Info**: Use `/user/me` endpoint with your API key to check account details

**Important: Auto-Registration**
- No separate registration step required
- First purchase automatically creates user account
- User account is linked to your wallet address
- All future purchases are associated with the same user account

**User Management Endpoints (napi-ser):**
- `GET /user/me` - Get user information, API keys, and statistics
- `GET /user/my-keys` - List all API keys for your account

**EIP-3009 Signature Requirements:**
- **Domain**: Token name, version (2 for USDC), chainId, verifyingContract (USDC address)
- **Type**: TransferWithAuthorization(from, to, value, validAfter, validBefore, nonce)
- **Valid Before**: Current timestamp + 8 hours (28800 seconds)

**USDC Contract**: `0x036CbD53842c5426634e7929541eC2318f3dCF7e` (Base Sepolia)
**Payee**: `0x1a85156c2943b63febeee7883bd84a7d1cf0da0c`

## CLI Scripts

This skill includes ready-to-use CLI scripts for all endpoints.

**Dependencies:**
```bash
# TypeScript/Bun
bun add viem dotenv

# Python
pip install web3 requests python-dotenv
```

### Get Server Info

```bash
# Python
python scripts/info.py

# TypeScript/Bun
bun run scripts/info.ts
```

### Get Wallet Address

```bash
# Python
python scripts/get_address.py

# TypeScript/Bun
bun run scripts/get_address.ts
```

### Buy API Key

```bash
# Python
python scripts/buy_apikey.py --duration 7

# TypeScript/Bun
bun run scripts/buy_apikey.ts --duration 7
```

### Refresh Pricing

```bash
# Python
python scripts/refresh_pricing.py

# TypeScript/Bun
bun run scripts/refresh_pricing.ts
```

## Python Implementation

### info.py
```python
import requests

def get_info():
    response = requests.get("https://apipaymcp.okart.fun/info")
    return response.json()

if __name__ == "__main__":
    info = get_info()
    print(f"Environment: {info['environment']}")
    print(f"Network: {info['network']}")
    print(f"Payee: {info['payee']}")
    print(f"Asset: {info['asset']}")
    print(f"Pricing:")
    for key, value in info['prices'].items():
        print(f"  {key}: {value}")
```

### get_address.py
```python
from web3 import Web3
import os

def get_address(private_key: str = None):
    if private_key is None:
        private_key = os.environ.get('AUTOPAY_PKEY')
        if not private_key:
            raise ValueError("AUTOPAY_PKEY environment variable not set")
    
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)
    return account.address

if __name__ == "__main__":
    address = get_address()
    print(f"Your Wallet Address: {address}")
```

### buy_apikey.py
```python
import requests
from web3 import Web3
import json
import time
import os

def buy_apikey(duration: int, private_key: str = None):
    if private_key is None:
        private_key = os.environ.get('AUTOPAY_PKEY')
        if not private_key:
            raise ValueError("AUTOPAY_PKEY environment variable not set")
    
    w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))
    account = w3.eth.account.from_key(private_key)
    
    # Step 1: Get payment quote
    info_response = requests.get("https://apipaymcp.okart.fun/info")
    info = info_response.json()
    
    payee_address = info['payee']
    usdc_address = info['asset']
    price_in_usdc = info['prices'][f'{duration}daysUsdc']
    
    # USDC uses 6 decimals
    amount = int(price_in_usdc * 10 ** 6)
    
    # Step 2: Create EIP-3009 signature
    # For Base Sepolia USDC: name="USDC", version="2"
    domain = {
        "name": "USDC",
        "version": "2",
        "chainId": 84532,
        "verifyingContract": usdc_address
    }
    
    message_types = {
        "TransferWithAuthorization": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"}
        ]
    }
    
    nonce = os.urandom(32).hex()
    now = int(time.time())
    valid_after = 0
    valid_before = now + 28800  # 8 hours
    
    message = {
        "from": account.address,
        "to": payee_address,
        "value": amount,
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": f"0x{nonce}"
    }
    
    # Sign typed data
    signed_message = w3.eth.account.sign_typed_data(
        private_key=private_key,
        domain=domain,
        message_types=message_types,
        message=message
    )
    
    signature_payload = {
        "from": account.address,
        "to": payee_address,
        "value": str(amount),
        "validAfter": str(valid_after),
        "validBefore": str(valid_before),
        "nonce": f"0x{nonce}",
        "v": signed_message.v,
        "r": signed_message.r.hex(),
        "s": signed_message.s.hex()
    }
    
    # Step 3: Call buy-apikey with EIP-3009 signature
    buy_response = requests.post(
        "https://apipaymcp.okart.fun/v1/buy-apikey",
        headers={
            "Content-Type": "application/json",
            "PAYMENT-SIGNATURE": json.dumps(signature_payload)
        },
        json={"duration": duration}
    )
    
    if buy_response.status_code != 200:
        raise Exception(f"Buy API key failed: {buy_response.text}")
    
    return {
        "apiKey": buy_response.json()['apiKey'],
        "txHash": buy_response.json()['txHash'],
        "payState": buy_response.json()['payState'],
        "durationDays": buy_response.json()['durationDays'],
        "transactionId": buy_response.json()['transactionId']
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, choices=[1, 7, 30], required=True)
    args = parser.parse_args()
    
    result = buy_apikey(args.duration)
    print(json.dumps(result, indent=2))
```

### refresh_pricing.py
```python
import requests

def refresh_pricing():
    response = requests.get("https://apipaymcp.okart.fun/refresh_pricing")
    return response.json()

if __name__ == "__main__":
    pricing = refresh_pricing()
    print(f"Pricing updated at: {pricing.get('updatedAt', 'N/A')}")
    if 'prices' in pricing:
        print(f"1 day: ${pricing['prices']['1dayUsdc']} USDC")
        print(f"7 days: ${pricing['prices']['7daysUsdc']} USDC")
        print(f"30 days: ${pricing['prices']['30daysUsdc']} USDC")
```

## TypeScript Implementation

### info.ts
```typescript
async function getInfo() {
  const response = await fetch("https://apipaymcp.okart.fun/info");
  return response.json();
}

const info = await getInfo();
console.log(`Environment: ${info.environment}`);
console.log(`Network: ${info.network}`);
console.log(`Payee: ${info.payee}`);
console.log(`Asset: ${info.asset}`);
console.log("Pricing:");
Object.entries(info.prices).forEach(([key, value]) => {
  console.log(`  ${key}: ${value}`);
});
```

### get_address.ts
```typescript
import { privateKeyToAccount } from "viem/accounts";

function getAddress(privateKey?: `0x${string}`): string {
  const key = privateKey || (process.env.AUTOPAY_PKEY as `0x${string}`);
  if (!key) {
    throw new Error("AUTOPAY_PKEY environment variable not set");
  }
  
  const account = privateKeyToAccount(key);
  return account.address;
}

const address = getAddress();
console.log(`Your Wallet Address: ${address}`);
```

### buy_apikey.ts
```typescript
import { createWalletClient, http, parseUnits } from "viem";
import { baseSepolia } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";
import crypto from "crypto";

const transferWithAuthorizationTypes = {
  TransferWithAuthorization: [
    { name: "from", type: "address" },
    { name: "to", type: "address" },
    { name: "value", type: "uint256" },
    { name: "validAfter", type: "uint256" },
    { name: "validBefore", type: "uint256" },
    { name: "nonce", type: "bytes32" },
  ],
} as const;

async function buyApikey(duration: number, privateKey: `0x${string}` | undefined = undefined) {
  const key = privateKey || (process.env.AUTOPAY_PKEY as `0x${string}`)
  if (!key) {
    throw new Error("AUTOPAY_PKEY environment variable not set")
  }
  
  const account = privateKeyToAccount(key);
  const client = createWalletClient({
    account,
    chain: baseSepolia,
    transport: http()
  });
  
  // Step 1: Get payment quote
  const infoResponse = await fetch("https://apipaymcp.okart.fun/info");
  const info = await infoResponse.json();
  
  const payeeAddress = info.payee as `0x${string}`;
  const usdcAddress = info.asset as `0x${string}`;
  const priceInUsdc = info.prices[`${duration}daysUsdc`];
  
  // USDC uses 6 decimals
  const amount = parseUnits(priceInUsdc.toString(), 6);
  
  // Step 2: Create EIP-3009 signature
  // For Base Sepolia USDC: name="USDC", version="2"
  const nonce = `0x${crypto.randomBytes(32).toString("hex")}` as `0x${string}`;
  const now = Math.floor(Date.now() / 1000);
  const validAfter = BigInt(0);
  const validBefore = BigInt(now + 28800); // 8 hours
  
  const signature = await client.signTypedData({
    domain: {
      name: "USDC",
      version: "2",
      chainId: 84532,
      verifyingContract: usdcAddress,
    },
    types: transferWithAuthorizationTypes,
    primaryType: "TransferWithAuthorization",
    message: {
      from: account.address,
      to: payeeAddress,
      value: amount,
      validAfter,
      validBefore,
      nonce,
    },
  });
  
  const signaturePayload = {
    from: account.address,
    to: payeeAddress,
    value: amount.toString(),
    validAfter: validAfter.toString(),
    validBefore: validBefore.toString(),
    nonce,
    v: Number((signature.slice(-2) as `0x${string}`)),
    r: signature.slice(0, 66) as `0x${string}`,
    s: `0x${signature.slice(66, 130)}` as `0x${string}`
  };
  
  // Step 3: Call buy-apikey with EIP-3009 signature
  const buyResponse = await fetch("https://apipaymcp.okart.fun/v1/buy-apikey", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "PAYMENT-SIGNATURE": JSON.stringify(signaturePayload)
    },
    body: JSON.stringify({ duration })
  });
  
  if (buyResponse.status !== 200) {
    throw new Error(`Buy API key failed: ${await buyResponse.text()}`);
  }
  
  const buyData = await buyResponse.json();
  
  return {
    apiKey: buyData.apiKey,
    txHash: buyData.txHash,
    payState: buyData.payState,
    durationDays: buyData.durationDays,
    transactionId: buyData.transactionId
  };
}
```

### refresh_pricing.ts
```typescript
async function refreshPricing() {
  const response = await fetch("https://apipaymcp.okart.fun/refresh_pricing");
  return response.json();
}

const pricing = await refreshPricing();
console.log(`Updated: ${pricing.updatedAt}`);
if (pricing.prices) {
  console.log(`1 day: $${pricing.prices['1dayUsdc']} USDC`);
  console.log(`7 days: $${pricing.prices['7daysUsdc']} USDC`);
  console.log(`30 days: $${pricing.prices['30daysUsdc']} USDC`);
}
```

## Complete Purchase Flow

```typescript
// 1. Check server info and pricing
const info = await fetch("https://apipaymcp.okart.fun/info").then(r => r.json());
console.log(`Current pricing: ${JSON.stringify(info.prices)}`);
console.log(`Payee address: ${info.payee}`);
console.log(`USDC contract: ${info.asset}`);

// 2. Create EIP-3009 signature
const privateKey = process.env.AUTOPAY_PKEY as `0x${string}`
const account = privateKeyToAccount(privateKey);
const client = createWalletClient({
  account,
  chain: baseSepolia,
  transport: http()
});

const nonce = `0x${crypto.randomBytes(32).toString("hex")}`;
const now = Math.floor(Date.now() / 1000);
const validAfter = BigInt(0);
const validBefore = BigInt(now + 28800); // 8 hours
const amount = parseUnits("0.49", 6); // for 7-day key

const signature = await client.signTypedData({
  domain: {
    name: "USDC",
    version: "2",
    chainId: 84532,
    verifyingContract: info.asset,
  },
  types: transferWithAuthorizationTypes,
  primaryType: "TransferWithAuthorization",
  message: {
    from: account.address,
    to: info.payee,
    value: amount,
    validAfter,
    validBefore,
    nonce,
  },
});

const signaturePayload = {
  from: account.address,
  to: info.payee,
  value: amount.toString(),
  validAfter: validAfter.toString(),
  validBefore: validBefore.toString(),
  nonce,
  v: Number((signature.slice(-2) as `0x${string}`)),
  r: signature.slice(0, 66) as `0x${string}`,
  s: `0x${signature.slice(66, 130)}` as `0x${string}`
};

// 3. Buy API key with EIP-3009 signature
const purchase = await fetch("https://apipaymcp.okart.fun/v1/buy-apikey", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "PAYMENT-SIGNATURE": JSON.stringify(signaturePayload)
  },
  body: JSON.stringify({
    duration: 7
  })
}).then(r => r.json());

console.log(`   API Key: ${result.apiKey}`);
console.log(`   TX Hash: ${result.txHash}`);
console.log(`   Pay State: ${result.payState}`);
console.log(`   Duration: ${result.durationDays} days`);
console.log(`   Transaction ID: ${result.transactionId}`);
```

## Error Handling

All endpoints return errors as:
```json
{
  "code": "PAYMENT_FAILED",
  "message": "Insufficient USDC balance",
  "details": { "required": "0.49", "available": "0.25" }
}
```

Common error codes:
- `INVALID_DURATION` (400) - Duration must be 1, 7, or 30
- `PAYMENT_FAILED` (402) - Payment transaction failed
- `INSUFFICIENT_BALANCE` (402) - Not enough USDC in wallet
- `RATE_LIMITED` (429) - Too many requests
- `INTERNAL_ERROR` (500) - Server error

## Security Notes

### Private Key Management

**Never commit private keys to version control!**

**Auto-Registration Security:**
- User accounts are automatically created on first purchase
- No separate registration endpoint required
- User account is linked to your wallet address
- All future purchases are automatically associated with your user account
- User data is accessible via `/user/me` endpoint with your API key

**Recommended approaches:**

1. **Environment Variables** (Recommended)
    ```bash
    # Set in shell
    export AUTOPAY_PKEY="0x..."
    
    # Or in .env file
    echo "AUTOPAY_PKEY=0x..." > .env
    ```

2. **CLI Arguments** (For testing)
    ```bash
    # Use AUTOPAY_PKEY environment variable
    export AUTOPAY_PKEY="0x..."
    python scripts/buy_apikey.py --duration 7
    bun run scripts/buy_apikey.ts --duration 7
    ```

3. **For Skill Implementation**
   - Pass private key via environment variables
   - Never hardcode in code
   - Use `dotenv` to load from `.env` file

**Best Practices:**
- Use a dedicated wallet for API purchases (not main wallet)
- Test on Base Sepolia (Chain ID: 84532) before mainnet
- Store API keys securely (environment variables or secret manager)
- Verify transaction on Base Sepolia explorer before using API key
- Rotate API keys regularly
