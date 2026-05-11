---
name: okx-dex-swap
description: >
  Execute token swaps on-chain via OKX DEX Aggregator API (v6). Use this skill when a user wants to:
  1. Build a complete swap flow: get swap calldata -> sign transaction -> broadcast to chain
  2. Execute token-to-token swaps with slippage protection, MEV protection, and Jito tips (Solana)
  3. Integrate OKX DEX swap + broadcast into applications, bots, or scripts
  This skill covers the FULL lifecycle: /swap endpoint (get tx data) + /broadcast-transaction endpoint (submit signed tx).
  For quote-only (no execution), use the okx-dex-quote skill instead.
version: 1.0.0
allowed_tools: [bash_tool, create_file, str_replace, view]
required_context: [api_key, secret_key, passphrase, user_wallet_address, private_key_or_signer]
license: MIT
author: Claude Assistant
tags: [defi, dex, okx, swap, broadcast, web3, onchain, evm, solana, mev-protection]
---

# OKX DEX Swap & Broadcast Skill

## Overview

This skill generates production-ready code for the **complete on-chain swap flow** using the OKX DEX Aggregator:

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌───────────┐
│  Quote   │ ──▶ │   Swap   │ ──▶ │   Sign   │ ──▶ │ Broadcast │
│ (optional│     │ API Call │     │   Tx     │     │  to Chain │
│  preview)│     │          │     │          │     │           │
└─────────┘     └──────────┘     └──────────┘     └───────────┘
```

**Two API endpoints involved:**

| Step | Endpoint | Method | Purpose |
|------|----------|--------|---------|
| Swap | `/api/v6/dex/aggregator/swap` | GET | Get transaction calldata for the swap |
| Broadcast | `/api/v6/dex/pre-transaction/broadcast-transaction` | POST | Submit signed transaction to the chain |

**Key features:**
- Full swap lifecycle with transaction signing
- Auto-slippage calculation based on market conditions
- MEV (sandwich attack) protection on ETH, BSC, SOL, BASE
- Jito tips for Solana priority transactions
- Token approval handling (ERC-20 approve)
- Commission/referral fee splitting
- Price impact protection with configurable thresholds

## Prerequisites

### Required Credentials
- `OKX_ACCESS_KEY` — API key
- `OKX_SECRET_KEY` — Secret key for HMAC signing
- `OKX_PASSPHRASE` — Account passphrase

### Wallet Requirements
- **EVM chains**: Private key or a signer (e.g., web3.py Account, ethers.js Wallet)
- **Solana**: Keypair for transaction signing
- The wallet must have sufficient balance of the `fromToken` and native token for gas

### Environment
- **Python**: `requests`, `web3` (for EVM signing), `solders` / `solana-py` (for Solana)
- **Node.js**: `axios`, `ethers` (for EVM signing), `@solana/web3.js` (for Solana)

## Workflow

### Step 1: Call the Swap API

**Endpoint:**
```
GET https://web3.okx.com/api/v6/dex/aggregator/swap
```

**Required parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chainIndex` | String | Yes | Chain ID (e.g., `1` = Ethereum, `501` = Solana) |
| `amount` | String | Yes | Amount in raw units with decimals (e.g., `1000000` for 1 USDT) |
| `swapMode` | String | Yes | `exactIn` (default) or `exactOut` |
| `fromTokenAddress` | String | Yes | Sell token contract address |
| `toTokenAddress` | String | Yes | Buy token contract address |
| `slippagePercent` | String | Yes | Slippage tolerance (e.g., `0.5` = 0.5%). EVM: 0-100, Solana: 0 to <100 |
| `userWalletAddress` | String | Yes | User's wallet address that will sign and send the tx |

**Important optional parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `approveTransaction` | Boolean | Set `true` to get ERC-20 approval calldata in response |
| `approveAmount` | String | Custom approval amount (raw units). If omitted, approves exact swap amount |
| `swapReceiverAddress` | String | Recipient address if different from sender |
| `feePercent` | String | Commission fee %. Max 3% (EVM) / 10% (Solana) |
| `fromTokenReferrerWalletAddress` | String | Wallet to receive fromToken commission |
| `toTokenReferrerWalletAddress` | String | Wallet to receive toToken commission |
| `autoSlippage` | Boolean | Auto-calculate optimal slippage (overrides `slippagePercent`) |
| `maxAutoslippagePercent` | String | Cap for auto-slippage |
| `priceImpactProtectionPercent` | String | Max price impact allowed (0-100, default 90) |
| `gasLevel` | String | `slow`, `average` (default), or `fast` |
| `gaslimit` | String | Custom gas limit in wei (EVM only) |
| `dexIds` | String | Restrict to specific DEX IDs (comma-separated) |
| `excludeDexIds` | String | Exclude specific DEX IDs (comma-separated) |
| `directRoute` | Boolean | Single-pool routing only (Solana only) |
| `disableRFQ` | String | Disable time-sensitive RFQ liquidity sources |
| `callDataMemo` | String | Custom 64-byte hex data to include on-chain |

**Solana-specific parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `computeUnitPrice` | String | Priority fee (like gasPrice on EVM) |
| `computeUnitLimit` | String | Compute budget (like gasLimit on EVM) |
| `tips` | String | Jito tips in SOL (min 0.0000000001, max 2). Set `computeUnitPrice=0` when using tips |

**Swap API response structure:**

```json
{
  "code": "0",
  "data": [{
    "routerResult": {
      "chainIndex": "1",
      "fromToken": { "tokenSymbol": "USDC", "decimal": "6", ... },
      "toToken": { "tokenSymbol": "WBTC", "decimal": "8", ... },
      "fromTokenAmount": "100000000000",
      "toTokenAmount": "90281915",
      "tradeFee": "1.35",
      "estimateGasFee": "1248837",
      "priceImpactPercent": "0.07",
      "dexRouterList": [...]
    },
    "tx": {
      "from": "0x77660f...",
      "to": "0x5E1f62...",
      "value": "0",
      "data": "0xf2c42696...",
      "gas": "1248837",
      "gasPrice": "557703374",
      "maxPriorityFeePerGas": "500000000",
      "minReceiveAmount": "90191633",
      "slippagePercent": "0.1",
      "signatureData": [...]
    }
  }],
  "msg": ""
}
```

**Key fields in `tx` object:**

| Field | Description |
|-------|-------------|
| `from` | Sender wallet address |
| `to` | OKX DEX router contract address |
| `data` | Transaction calldata (the swap instruction) |
| `value` | Native token amount to send (in wei). `"0"` for ERC-20 swaps |
| `gas` | Estimated gas limit (already padded +50%) |
| `gasPrice` | Gas price in wei |
| `maxPriorityFeePerGas` | EIP-1559 priority fee |
| `minReceiveAmount` | Minimum output at max slippage |
| `signatureData` | Approval calldata (if `approveTransaction=true`) or Jito tips calldata |

### Step 2: Handle Token Approval (EVM Only)

For ERC-20 tokens (not native ETH/BNB), you need to approve the DEX router to spend your tokens BEFORE the swap.

**When `approveTransaction=true` in the request:**
The response `tx.signatureData` contains the approval info:
```json
{
  "approveContract": "0x40aA958dd87FC8305b97f2BA922CDdCa374bcD7f",
  "approveTxCalldata": "0x095ea7b3..."
}
```

**Approval flow:**
1. Parse `signatureData` to get `approveContract` and `approveTxCalldata`
2. Send an approval transaction: `to=approveContract`, `data=approveTxCalldata`
3. Wait for approval tx to be confirmed
4. Then send the swap transaction

**IMPORTANT**: For native tokens (ETH, BNB, etc. using `0xeeee...eeee`), no approval is needed.

### Step 3: Sign the Transaction

**EVM chains (Python / web3.py):**
```python
tx_params = {
    "from": tx_data["from"],
    "to": tx_data["to"],
    "value": int(tx_data["value"]),
    "data": tx_data["data"],
    "gas": int(tx_data["gas"]),
    "gasPrice": int(tx_data["gasPrice"]),
    "nonce": w3.eth.get_transaction_count(wallet_address),
    "chainId": chain_id,
}
signed = w3.eth.account.sign_transaction(tx_params, private_key)
signed_tx_hex = signed.raw_transaction.hex()
```

**EVM chains (Node.js / ethers.js):**
```javascript
const tx = {
  from: txData.from,
  to: txData.to,
  value: txData.value,
  data: txData.data,
  gasLimit: txData.gas,
  gasPrice: txData.gasPrice,
  nonce: await provider.getTransactionCount(walletAddress),
  chainId: chainId,
};
const signedTx = await wallet.signTransaction(tx);
```

**Solana:**
Use `solders` or `@solana/web3.js` to deserialize, sign, and serialize the transaction from `tx.data`.

### Step 4: Broadcast the Signed Transaction

**Endpoint:**
```
POST https://web3.okx.com/api/v6/dex/pre-transaction/broadcast-transaction
```

**IMPORTANT**: This is a POST request with a JSON body (unlike the GET-based swap/quote endpoints).

**Request body:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `signedTx` | String | Yes | The hex-encoded signed transaction string |
| `chainIndex` | String | Yes | Chain ID (e.g., `"1"` for Ethereum) |
| `address` | String | Yes | Sender wallet address |
| `extraData` | String | No | JSON string with extra options (see below) |

**extraData options (JSON string):**

| Field | Type | Description |
|-------|------|-------------|
| `enableMevProtection` | Boolean | Enable MEV (sandwich) protection. Supported: ETH, BSC, SOL, BASE |
| `jitoSignedTx` | String | Base58-encoded signed Jito transaction (Solana only). Required when `tips` > 0 |

**Signing algorithm for POST requests:**
```
prehash = timestamp + "POST" + request_path + json_body
signature = Base64(HMAC-SHA256(secret_key, prehash))
```

Note: For POST, the `request_path` has NO query string. The JSON body is appended directly to the prehash string.

**Broadcast response:**
```json
{
  "code": "0",
  "data": [{
    "orderId": "0e1d79837afce1e149b6ab54b6e2edce8130c3f8",
    "txHash": "0xd394f356a16b618ed839c66c935c9cccc5dde0af832ff9b468677eea38759db5"
  }],
  "msg": ""
}
```

| Field | Description |
|-------|-------------|
| `orderId` | OKX internal order tracking ID |
| `txHash` | On-chain transaction hash. Use this to check status on block explorer |

### Step 5: Verify Transaction

After broadcasting, verify the transaction was confirmed:
- **EVM**: Check `txHash` on Etherscan / block explorer, or use `web3.eth.wait_for_transaction_receipt()`
- **Solana**: Check on Solscan, or use `connection.confirmTransaction()`

## Best Practices

### Security
- **NEVER hardcode private keys** in code. Use environment variables, keystore files, or hardware wallets.
- **NEVER log private keys, signed transactions, or secret keys** in production.
- Always validate token addresses and amounts before sending.
- Check `isHoneyPot` on both tokens before proceeding.
- Use `priceImpactProtectionPercent` (recommend setting to `10` or lower for safety).

### Slippage Configuration
- **Stable pairs** (USDC/USDT): `0.1%` - `0.5%`
- **Major pairs** (ETH/USDC): `0.5%` - `1%`
- **Volatile/low-liquidity tokens**: `1%` - `5%`
- **Meme coins**: `5%` - `15%` (or higher, but be cautious)
- Use `autoSlippage=true` with `maxAutoslippagePercent` for optimal auto-calculation.

### MEV Protection
- Enable `enableMevProtection: true` for large trades on ETH, BSC, SOL, BASE.
- On Solana, combine with Jito tips for priority + MEV protection.
- When using Jito tips, set `computeUnitPrice=0` to avoid wasting fees.

### Token Approval Strategy
- For one-time swaps: approve exact amount (`approveAmount = swap amount`).
- For repeated swaps: consider a larger approval (e.g., max uint256) to save gas on future swaps, but understand the security trade-off.
- Always check existing allowance before sending a new approval.

### Uni V3 Liquidity Edge Case
When swapping through Uniswap V3 pools, if the liquidity for the pair is drained mid-swap, the router will only consume part of your input tokens. The OKX DEX Router smart contract will automatically refund the remainder. Ensure your integration contract supports receiving token refunds.

### Amount Handling
- **Always use strings** for amounts to avoid floating-point precision loss.
- Python: `int()` for calculations, never `float()`.
- JavaScript: `BigInt` or `ethers.parseUnits()` for amounts.
- Formula: `raw_amount = human_amount * 10^decimals`

### Error Handling
- Check `response["code"] == "0"` before processing.
- If broadcast fails, do NOT automatically retry without checking nonce — you may double-spend.
- Common errors:
  - `401` = Signature mismatch (check POST signing includes body)
  - `429` = Rate limited
  - Swap returns error = insufficient balance, invalid params, or liquidity issue
  - Broadcast returns error = already executed, nonce too low, insufficient gas

### Commission/Referral Fees
- Only ONE of `fromTokenReferrerWalletAddress` or `toTokenReferrerWalletAddress` per tx.
- Solana: referrer wallet must have SOL deposited for activation.
- TON: limited DEX support (Stonfi V2, Dedust).
- BSC: no commission through Four.meme swaps.

## Examples

### Example 1: Python — Complete EVM Swap Flow

```python
import os, hmac, hashlib, base64, json, requests
from datetime import datetime, timezone
from urllib.parse import urlencode
from web3 import Web3

# === Configuration ===
API_KEY = os.environ["OKX_ACCESS_KEY"]
SECRET_KEY = os.environ["OKX_SECRET_KEY"]
PASSPHRASE = os.environ["OKX_PASSPHRASE"]
PRIVATE_KEY = os.environ["WALLET_PRIVATE_KEY"]

BASE_URL = "https://web3.okx.com"
CHAIN_INDEX = "1"  # Ethereum
CHAIN_ID = 1
RPC_URL = "https://eth.llamarpc.com"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
WALLET = account.address


def _sign_request(timestamp, method, request_path, body=""):
    prehash = timestamp + method + request_path + body
    mac = hmac.new(SECRET_KEY.encode(), prehash.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()


def _headers(method, request_path, body=""):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    sig = _sign_request(timestamp, method, request_path, body)
    return {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": sig,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }


# --- Step 1: Get swap calldata ---
def get_swap_data(from_token, to_token, amount, slippage="0.5"):
    params = {
        "chainIndex": CHAIN_INDEX,
        "fromTokenAddress": from_token,
        "toTokenAddress": to_token,
        "amount": amount,
        "swapMode": "exactIn",
        "slippagePercent": slippage,
        "userWalletAddress": WALLET,
        "approveTransaction": "true",
    }
    query = urlencode(params)
    path = f"/api/v6/dex/aggregator/swap?{query}"
    headers = _headers("GET", path)

    resp = requests.get(BASE_URL + path, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data["code"] != "0":
        raise Exception(f"Swap API error: {data['msg']}")
    return data["data"][0]


# --- Step 2: Handle approval (if needed) ---
def send_approval_if_needed(swap_result):
    sig_data = swap_result["tx"].get("signatureData", [])
    if not sig_data:
        return None

    for item in sig_data:
        parsed = json.loads(item) if isinstance(item, str) else item
        if "approveContract" in parsed:
            approve_tx = {
                "from": WALLET,
                "to": Web3.to_checksum_address(parsed["approveContract"]),
                "data": parsed["approveTxCalldata"],
                "gas": 60000,
                "gasPrice": w3.eth.gas_price,
                "nonce": w3.eth.get_transaction_count(WALLET),
                "chainId": CHAIN_ID,
            }
            signed = w3.eth.account.sign_transaction(approve_tx, PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            print(f"Approval confirmed: {tx_hash.hex()}")
            return receipt
    return None


# --- Step 3: Sign the swap transaction ---
def sign_swap_tx(swap_result):
    tx_data = swap_result["tx"]
    tx_params = {
        "from": Web3.to_checksum_address(tx_data["from"]),
        "to": Web3.to_checksum_address(tx_data["to"]),
        "value": int(tx_data["value"]),
        "data": tx_data["data"],
        "gas": int(tx_data["gas"]),
        "gasPrice": int(tx_data["gasPrice"]),
        "nonce": w3.eth.get_transaction_count(WALLET),
        "chainId": CHAIN_ID,
    }
    signed = w3.eth.account.sign_transaction(tx_params, PRIVATE_KEY)
    return signed.raw_transaction.hex()


# --- Step 4: Broadcast via OKX ---
def broadcast_tx(signed_tx_hex, enable_mev=True):
    path = "/api/v6/dex/pre-transaction/broadcast-transaction"
    body_dict = {
        "chainIndex": CHAIN_INDEX,
        "address": WALLET,
        "signedTx": signed_tx_hex,
    }
    if enable_mev:
        body_dict["extraData"] = json.dumps({"enableMevProtection": True})

    body_str = json.dumps(body_dict)
    headers = _headers("POST", path, body_str)

    resp = requests.post(BASE_URL + path, headers=headers, data=body_str, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data["code"] != "0":
        raise Exception(f"Broadcast error: {data['msg']}")
    return data["data"][0]


# === Execute full swap ===
if __name__ == "__main__":
    ETH = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
    amount = str(10 ** 17)  # 0.1 ETH

    print("1. Getting swap data...")
    swap = get_swap_data(ETH, USDC, amount, slippage="0.5")

    router = swap["routerResult"]
    to_dec = int(router["toToken"]["decimal"])
    out_human = int(router["toTokenAmount"]) / (10 ** to_dec)
    print(f"   Expected output: {out_human:,.2f} {router['toToken']['tokenSymbol']}")
    print(f"   Price impact: {router.get('priceImpactPercent', 'N/A')}%")
    print(f"   Min receive: {int(swap['tx']['minReceiveAmount']) / (10 ** to_dec):,.2f}")

    # Honeypot check
    if router["toToken"].get("isHoneyPot"):
        print("   HONEYPOT DETECTED — aborting!")
        exit(1)

    print("2. Handling approval...")
    send_approval_if_needed(swap)

    print("3. Signing swap transaction...")
    signed_hex = sign_swap_tx(swap)

    print("4. Broadcasting with MEV protection...")
    result = broadcast_tx(signed_hex, enable_mev=True)
    print(f"   Order ID: {result['orderId']}")
    print(f"   Tx Hash: {result['txHash']}")
    print(f"   View: https://etherscan.io/tx/{result['txHash']}")
```

### Example 2: Node.js — Complete EVM Swap Flow

```javascript
const crypto = require("crypto");
const https = require("https");
const { ethers } = require("ethers");

const API_KEY = process.env.OKX_ACCESS_KEY;
const SECRET_KEY = process.env.OKX_SECRET_KEY;
const PASSPHRASE = process.env.OKX_PASSPHRASE;
const PRIVATE_KEY = process.env.WALLET_PRIVATE_KEY;

const BASE_URL = "https://web3.okx.com";
const CHAIN_INDEX = "1";
const CHAIN_ID = 1;

const provider = new ethers.JsonRpcProvider("https://eth.llamarpc.com");
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

function sign(timestamp, method, path, body = "") {
  return crypto
    .createHmac("sha256", SECRET_KEY)
    .update(timestamp + method + path + body)
    .digest("base64");
}

function headers(method, path, body = "") {
  const ts = new Date().toISOString();
  return {
    "OK-ACCESS-KEY": API_KEY,
    "OK-ACCESS-SIGN": sign(ts, method, path, body),
    "OK-ACCESS-PASSPHRASE": PASSPHRASE,
    "OK-ACCESS-TIMESTAMP": ts,
    "Content-Type": "application/json",
  };
}

async function getSwapData(fromToken, toToken, amount, slippage = "0.5") {
  const params = new URLSearchParams({
    chainIndex: CHAIN_INDEX,
    fromTokenAddress: fromToken,
    toTokenAddress: toToken,
    amount,
    swapMode: "exactIn",
    slippagePercent: slippage,
    userWalletAddress: wallet.address,
    approveTransaction: "true",
  });
  const path = `/api/v6/dex/aggregator/swap?${params}`;
  const h = headers("GET", path);

  const resp = await fetch(`${BASE_URL}${path}`, { headers: h });
  const data = await resp.json();
  if (data.code !== "0") throw new Error(`Swap error: ${data.msg}`);
  return data.data[0];
}

async function broadcastTx(signedTx, enableMev = true) {
  const path = "/api/v6/dex/pre-transaction/broadcast-transaction";
  const bodyObj = {
    chainIndex: CHAIN_INDEX,
    address: wallet.address,
    signedTx,
    ...(enableMev && {
      extraData: JSON.stringify({ enableMevProtection: true }),
    }),
  };
  const bodyStr = JSON.stringify(bodyObj);
  const h = headers("POST", path, bodyStr);

  const resp = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: h,
    body: bodyStr,
  });
  const data = await resp.json();
  if (data.code !== "0") throw new Error(`Broadcast error: ${data.msg}`);
  return data.data[0];
}

async function main() {
  const ETH = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee";
  const USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48";
  const amount = (10n ** 17n).toString(); // 0.1 ETH

  console.log("1. Getting swap data...");
  const swap = await getSwapData(ETH, USDC, amount);

  const txData = swap.tx;
  console.log(`   Min receive: ${txData.minReceiveAmount}`);

  console.log("2. Signing transaction...");
  const tx = {
    from: txData.from,
    to: txData.to,
    value: txData.value,
    data: txData.data,
    gasLimit: txData.gas,
    gasPrice: txData.gasPrice,
    nonce: await provider.getTransactionCount(wallet.address),
    chainId: CHAIN_ID,
  };
  const signedTx = await wallet.signTransaction(tx);

  console.log("3. Broadcasting with MEV protection...");
  const result = await broadcastTx(signedTx);
  console.log(`   Tx Hash: ${result.txHash}`);
}

main().catch(console.error);
```

### Example 3: Solana Swap with Jito Tips

When using Jito tips on Solana:
1. Set `tips` parameter (e.g., `"0.001"` SOL) in the swap request
2. Set `computeUnitPrice=0` (avoid double-paying for priority)
3. The `signatureData` in response contains the Jito tips calldata
4. Sign BOTH the main transaction AND the Jito transaction
5. Broadcast with both `signedTx` and `jitoSignedTx` in `extraData`

```python
# Solana-specific broadcast with Jito
body = {
    "chainIndex": "501",
    "address": solana_wallet_pubkey,
    "signedTx": base58_signed_main_tx,
    "extraData": json.dumps({
        "enableMevProtection": True,
        "jitoSignedTx": base58_signed_jito_tx
    })
}
```

**IMPORTANT**: For Solana, `signedTx` and `jitoSignedTx` must BOTH be provided when using tips.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `401 Unauthorized` on broadcast | POST signing error | Ensure prehash = `timestamp + "POST" + path + jsonBody`. The body must be the exact JSON string. |
| `401 Unauthorized` on swap | GET signing error | Ensure prehash = `timestamp + "GET" + path_with_query_string`. |
| Approval tx fails | Insufficient ETH for gas | Ensure wallet has native token for gas fees. |
| Swap tx reverts | Slippage exceeded | Increase `slippagePercent` or use `autoSlippage=true`. |
| `minReceiveAmount` is 0 | Extreme slippage or bad params | Check token addresses and amounts. Reduce trade size. |
| Broadcast returns no txHash | MEV protection routing delay | Wait and check `orderId` status. MEV-protected txs may take longer. |
| "Nonce too low" on broadcast | Tx already sent or nonce reused | Fetch fresh nonce before signing. Never reuse nonces. |
| Solana broadcast fails | Missing `jitoSignedTx` | When `tips > 0`, you must provide both `signedTx` and `jitoSignedTx`. |
| Token refund not received | Uni V3 liquidity drained | Ensure your contract supports receiving token refunds from the router. |
| Commission not working on BSC | Four.meme restriction | Commission is not supported for swaps through Four.meme on BSC. |
| `priceImpactPercent` very negative | Low liquidity | Reduce amount or split into multiple smaller swaps. |

## Reference: POST vs GET Signing

The OKX API uses different signing for GET and POST:

| Method | Prehash Format |
|--------|---------------|
| GET | `timestamp + "GET" + path_with_query` |
| POST | `timestamp + "POST" + path + json_body` |

The Swap endpoint is **GET**, the Broadcast endpoint is **POST**. Getting this wrong is the #1 cause of `401` errors.

## Reference: MEV Protection Support

| Chain | `enableMevProtection` | Jito Tips |
|-------|----------------------|-----------|
| Ethereum | Yes | No |
| BSC | Yes | No |
| Solana | Yes | Yes |
| Base | Yes | No |
| Others | Not yet | Not yet |

## Reference: Common Chain IDs

| Chain | chainIndex | Chain ID (for tx signing) |
|-------|-----------|--------------------------|
| Ethereum | 1 | 1 |
| BSC | 56 | 56 |
| Polygon | 137 | 137 |
| Arbitrum | 42161 | 42161 |
| Optimism | 10 | 10 |
| Base | 8453 | 8453 |
| Avalanche | 43114 | 43114 |
| Solana | 501 | N/A |
| Unichain | 130 | 130 |
