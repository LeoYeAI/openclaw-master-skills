# Making Requests

The gateway supports JSON-RPC, NFT, Prices, and Portfolio APIs — all with the same SIWE auth and x402 payment flow. See [reference](reference.md) for the full list of supported endpoints, chain network slugs, and API methods.

Use either `@x402/fetch` or `@x402/axios` to make requests. Both automatically handle the 402 → sign → retry flow so you don't need to manage payments manually.

## Option A: `@x402/fetch`

```bash
npm install @x402/fetch @x402/core @x402/evm viem
```

```typescript
import { x402Client } from "@x402/core/client";
import { x402HTTPClient } from "@x402/core/http";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { toClientEvmSigner } from "@x402/evm";
import { wrapFetchWithPayment } from "@x402/fetch";
import { privateKeyToAccount } from "viem/accounts";
import { createPublicClient, http } from "viem";
import { base } from "viem/chains";

// Setup (do once)
const account = privateKeyToAccount("0x..." as `0x${string}`);
const publicClient = createPublicClient({ chain: base, transport: http() });
const signer = toClientEvmSigner(account, publicClient);
const client = new x402Client();
registerExactEvmScheme(client, { signer });
const httpClient = new x402HTTPClient(client);
const paidFetch = wrapFetchWithPayment(fetch, httpClient);

// Make a request
const response = await paidFetch("https://x402.alchemy.com/eth-mainnet/v2", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
    Authorization: `SIWE ${siweToken}`,
  },
  body: JSON.stringify({
    id: 1,
    jsonrpc: "2.0",
    method: "eth_blockNumber",
  }),
});

const result = await response.json();
// { id: 1, jsonrpc: "2.0", result: "0x134e82c" }
```

## Option B: `@x402/axios`

```bash
npm install @x402/axios @x402/core @x402/evm axios viem
```

```typescript
import axios from "axios";
import { x402Client } from "@x402/core/client";
import { x402HTTPClient } from "@x402/core/http";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { toClientEvmSigner } from "@x402/evm";
import { wrapAxiosWithPayment } from "@x402/axios";
import { privateKeyToAccount } from "viem/accounts";
import { createPublicClient, http } from "viem";
import { base } from "viem/chains";

// Setup (do once)
const account = privateKeyToAccount("0x..." as `0x${string}`);
const publicClient = createPublicClient({ chain: base, transport: http() });
const signer = toClientEvmSigner(account, publicClient);
const client = new x402Client();
registerExactEvmScheme(client, { signer });
const httpClient = new x402HTTPClient(client);
const paidAxios = wrapAxiosWithPayment(axios.create(), httpClient);

// Make a request
const { data } = await paidAxios.post(
  "https://x402.alchemy.com/eth-mainnet/v2",
  {
    id: 1,
    jsonrpc: "2.0",
    method: "eth_blockNumber",
  },
  {
    headers: {
      Authorization: `SIWE ${siweToken}`,
    },
  },
);

// { id: 1, jsonrpc: "2.0", result: "0x134e82c" }
```

## How It Works

Both wrappers follow the same flow:

1. Send the request with the `Authorization` header.
2. If **200** — return the result immediately.
3. If **402** — read the `accepts` array, create a signed USDC payment using the registered `x402Client`, and **retry** with a `Payment-Signature` header.
4. Subsequent calls with the same SIWE token return 200 without payment.

## REST API Endpoints (Prices, Portfolio, NFT)

The `paidFetch`/`paidAxios` wrappers are designed for JSON-RPC endpoints
(`/:chainNetwork/v2`). For REST API POST endpoints like
`/prices/v1/tokens/historical`, use **plain `fetch`** with the
`Authorization: SIWE <token>` header instead. The x402 wrapper can
corrupt POST request bodies on REST endpoints, causing 400 errors.

The SIWE token alone is sufficient for authentication on all endpoints
once payment has been established (e.g., via an initial GET request
through `paidFetch`).

## Selecting a Payment Network

If the 402 response offers multiple payment networks, control which one is selected by passing a selector to the `x402Client` constructor:

```typescript
const client = new x402Client(
  (_x402Version, requirements) => {
    const selected = requirements.find((r) => r.network === "eip155:8453");
    if (!selected) throw new Error("Base Mainnet payment not available");
    return selected;
  },
);
```

The default behavior picks the first option.

## Response Scenarios

### 200 — Success

```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "result": "0x134e82c"
}
```

The response includes an `X-Protocol-Version: x402/2.0` header.

### 401 — Unauthorized

Authentication failed. See [authentication](authentication.md) for error codes.

```json
{
  "error": "Unauthorized",
  "message": "Invalid SIWE message format",
  "code": "INVALID_SIWE"
}
```

### 402 — Payment Required

The wallet has no account or credits. When using `@x402/fetch` or `@x402/axios`, this is handled automatically. The raw 402 body looks like:

```json
{
  "x402Version": 2,
  "error": "PAYMENT-SIGNATURE header is required",
  "resource": {
    "url": "https://x402.alchemy.com/eth-mainnet/v2",
    "description": "Payment required to access this resource",
    "mimeType": "application/json"
  },
  "accepts": [
    {
      "scheme": "exact",
      "network": "eip155:8453",
      "amount": "10000",
      "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "payTo": "0x658dc531A7FE637F7BA31C3dDd4C9bf8A27c81e5",
      "maxTimeoutSeconds": 300,
      "extra": {
        "name": "USD Coin",
        "version": "2"
      }
    }
  ]
}
```

## Supported Chains and Endpoints

See [reference](reference.md) for supported chain network slugs, all available routes, and detailed API method documentation.
