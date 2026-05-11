# SIWE Authentication

Every request to the gateway must include an `Authorization` header with a SIWE token. The token proves wallet ownership without transmitting the private key.

## Token Format

```
Authorization: SIWE <base64(siwe_message)>.<signature>
```

## Step-by-Step Token Generation

### Step 1: Derive an account from a private key

```typescript
import { privateKeyToAccount } from "viem/accounts";

const account = privateKeyToAccount("0x<your_private_key>" as `0x${string}`);
// account.address → "0xYourChecksummedAddress"
```

### Step 2: Create a SIWE message

```typescript
import { SiweMessage } from "siwe";

function generateNonce(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let nonce = "";
  for (let i = 0; i < 16; i++) {
    nonce += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return nonce;
}

const siweMessage = new SiweMessage({
  domain: "x402.alchemy.com",
  address: account.address,
  statement: "Sign in to Alchemy Gateway",
  uri: "https://x402.alchemy.com",
  version: "1",
  chainId: 8453,
  nonce: generateNonce(),
  expirationTime: new Date(Date.now() + 3_600_000).toISOString(), // 1 hour
});

const messageText = siweMessage.prepareMessage();
```

### Step 3: Sign the message

```typescript
import { createWalletClient, http } from "viem";
import { base } from "viem/chains";

const walletClient = createWalletClient({
  account,
  chain: base,
  transport: http(),
});

const signature = await walletClient.signMessage({ message: messageText });
```

### Step 4: Encode the token

Base64-encode the message text, then join it with the signature using a `.` separator:

```typescript
const base64Message = Buffer.from(messageText).toString("base64");
const token = `${base64Message}.${signature}`;
```

### Step 5: Set the Authorization header

```typescript
const authHeader = `SIWE ${token}`;
// Use as: { Authorization: authHeader }
```

## SIWE Message Fields

| Field | Value | Notes |
|-------|-------|-------|
| `domain` | `x402.alchemy.com` | Must match the gateway's configured domain |
| `address` | Your wallet address | Checksummed Ethereum address |
| `statement` | `Sign in to Alchemy Gateway` | Human-readable intent |
| `uri` | `https://x402.alchemy.com` | Must use `https://` + domain |
| `version` | `1` | SIWE spec version |
| `chainId` | `8453` | Base Mainnet chain ID |
| `nonce` | Random alphanumeric string | At least 8 characters |
| `expirationTime` | ISO 8601 timestamp | Recommended: 1 hour from now |

## Auth Error Codes

When authentication fails, the gateway returns HTTP 401 with a JSON body:

```json
{
  "error": "Unauthorized",
  "message": "<description>",
  "code": "<error_code>"
}
```

| Code | Cause | How to fix |
|------|-------|------------|
| `MISSING_AUTH` | No `Authorization` header provided | Add the `Authorization: SIWE <token>` header to your request |
| `INVALID_AUTH_FORMAT` | Token is not in `base64.signature` format or Base64 decoding failed | Ensure the token is `base64(message).signature` with exactly one `.` separator |
| `INVALID_SIWE` | SIWE message could not be parsed | Check that you called `siweMessage.prepareMessage()` and Base64-encoded the full output |
| `INVALID_SIGNATURE` | Signature does not match the message signer | Ensure the same account that created the SIWE message also signed it |
| `INVALID_DOMAIN` | SIWE message domain does not match `x402.alchemy.com` | Set `domain` to `x402.alchemy.com` (or `localhost` for local dev) |
| `MESSAGE_EXPIRED` | SIWE message `expirationTime` has passed or `notBefore` is in the future | Generate a new SIWE token — the current one has expired |

## Handling Auth Errors

If you receive a 401 response, parse the `code` field and take the appropriate action:

- **Regenerable errors** (`MESSAGE_EXPIRED`): Generate a fresh SIWE token and retry the request.
- **Configuration errors** (`INVALID_DOMAIN`, `MISSING_AUTH`, `INVALID_AUTH_FORMAT`): Fix the token generation code — these will not resolve by retrying.
- **Signing errors** (`INVALID_SIGNATURE`, `INVALID_SIWE`): The token is malformed. Re-check steps 2–4 of the token generation flow.

```typescript
if (response.status === 401) {
  const body = await response.json();

  if (body.code === "MESSAGE_EXPIRED") {
    // Token expired — regenerate and retry
    const newToken = await generateNewSiweToken();
    // retry request with new token...
  } else {
    // Configuration or signing error — do not retry, fix the code
    throw new Error(`Auth failed (${body.code}): ${body.message}`);
  }
}
```
