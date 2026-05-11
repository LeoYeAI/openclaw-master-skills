# Manual x402 Payment

When the gateway returns **402**, you must create an x402 payment and retry the request with a `Payment-Signature` header.

## Extracting Payment Requirements from a 402 Response

Always decode the payment requirements from the **`PAYMENT-REQUIRED` response header** using `decodePaymentRequiredHeader()` from `@x402/core/http`:

```typescript
import { decodePaymentRequiredHeader } from "@x402/core/http";

const encoded = response.headers.get("PAYMENT-REQUIRED")!;
const paymentRequired = decodePaymentRequiredHeader(encoded);
```

## Creating and Encoding the Payment

```typescript
import { x402Client } from "@x402/core/client";
import {
  decodePaymentRequiredHeader,
  encodePaymentSignatureHeader,
  x402HTTPClient,
} from "@x402/core/http";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { privateKeyToAccount } from "viem/accounts";

async function createPaymentFromResponse(
  privateKey: `0x${string}`,
  response: Response,
): Promise<string> {
  const account = privateKeyToAccount(privateKey);

  // 1. Create x402 client and register the EVM "exact" payment scheme
  const client = new x402Client();
  registerExactEvmScheme(client, { signer: account });
  const httpClient = new x402HTTPClient(client);

  // 2. Decode payment requirements from the PAYMENT-REQUIRED header
  const encoded = response.headers.get("PAYMENT-REQUIRED")!;
  const paymentRequired = decodePaymentRequiredHeader(encoded);

  // 3. Create the signed payment payload
  const paymentPayload = await httpClient.createPaymentPayload(paymentRequired);

  // 4. Encode as a header value
  return encodePaymentSignatureHeader(paymentPayload);
}
```

## Sending the Payment

Add the encoded payment as a `Payment-Signature` header on the retry request:

```typescript
const retryResponse = await fetch("https://x402.alchemy.com/eth-mainnet/v2", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
    Authorization: `SIWE ${token}`,
    "Payment-Signature": paymentSignature, // from createPayment()
  },
  body: JSON.stringify({
    id: 1,
    jsonrpc: "2.0",
    method: "eth_blockNumber",
  }),
});
```

## Payment Details

- **Asset**: USDC (6 decimals)
- **Scheme**: `exact` — uses EIP-3009 gasless `transferWithAuthorization`
- **Amount**: Specified in the 402 response `accepts` array (USDC atomic units, 6 decimals)
- **Signing**: The `@x402/evm` package signs an EIP-712 typed message authorizing the USDC transfer. No on-chain gas is needed from the payer.
- **Settlement**: The gateway's facilitator (Coinbase CDP) submits the signed authorization on-chain.

## Selecting a Payment Option

The 402 `accepts` array may contain multiple options (different networks). Pick one that matches a network where your wallet holds USDC:

```typescript
// Example: select the Base Mainnet option
const option = paymentRequired.accepts.find(
  (opt) => opt.network === "eip155:8453",
);
```

## Payment Error Responses

If a payment fails verification or settlement, the gateway returns 402 with additional error info:

```json
{
  "x402Version": 2,
  "error": "Payment verification failed: insufficient_balance",
  "accepts": [ ... ],
  "extensions": {
    "paymentError": {
      "info": {
        "type": "verify_failed",
        "reason": "insufficient_balance",
        "payer": "0x..."
      }
    }
  }
}
```

Error types: `verify_failed`, `settle_failed`, `settle_timeout`, `payment_error`.
