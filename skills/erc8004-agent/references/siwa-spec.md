# SIWA — Sign In With Agent

> Part of the 8004 Agent Skill v0.0.1

**Protocol Version 1.0 — Authentication protocol for ERC-8004 registered agents**

SIWA enables ERC-8004 agents to authenticate with off-chain services by signing a structured plaintext message with their Ethereum private key. Inspired by SIWE (EIP-4361), SIWA extends the pattern to include ERC-8004 identity fields (`agentId`, `agentRegistry`) and verifies onchain ownership of the agent NFT.

## Message Format (ABNF)

```abnf
siwa-message = domain %s" wants you to sign in with your Agent account:" LF
               address LF LF
               [ statement LF ] LF
               %s"URI: " uri LF
               %s"Version: " version LF
               %s"Agent ID: " agent-id LF
               %s"Agent Registry: " agent-registry LF
               %s"Chain ID: " chain-id LF
               %s"Nonce: " nonce LF
               %s"Issued At: " issued-at
               [ LF %s"Expiration Time: " expiration-time ]
               [ LF %s"Not Before: " not-before ]
               [ LF %s"Request ID: " request-id ]

domain          = authority          ; RFC 3986 authority (host[:port])
address         = "0x" 40HEXDIG     ; EIP-55 checksummed Ethereum address
statement       = *( reserved / unreserved / " " )  ; no LF
uri             = URI               ; RFC 3986
version         = "1"               ; fixed for this spec version
agent-id        = 1*DIGIT           ; ERC-721 tokenId on the Identity Registry
agent-registry  = namespace ":" chain-id-ref ":" registry-address
                                    ; e.g. "eip155:84532:0x8004AA63..."
namespace       = "eip155"          ; EVM namespace
chain-id-ref    = 1*DIGIT           ; EIP-155 chain ID
registry-address= "0x" 40HEXDIG    ; Identity Registry contract address
chain-id        = 1*DIGIT           ; EIP-155 chain ID for the signing session
nonce           = 8*ALPHANUM        ; server-generated, ≥ 8 alphanumeric chars
issued-at       = date-time         ; RFC 3339
expiration-time = date-time         ; RFC 3339 (OPTIONAL)
not-before      = date-time         ; RFC 3339 (OPTIONAL)
request-id      = *VCHAR            ; system-specific identifier (OPTIONAL)
```

## Field Definitions

| Field | Required | Description |
|---|---|---|
| `domain` | YES | Origin domain requesting authentication. MUST match the server's actual origin. |
| `address` | YES | Ethereum address performing the signing. MUST be EIP-55 checksummed. |
| `statement` | NO | Human-readable purpose string. |
| `uri` | YES | RFC 3986 URI of the resource being authenticated to. |
| `version` | YES | MUST be `"1"`. |
| `agentId` | YES | The ERC-721 tokenId of the agent in the Identity Registry. |
| `agentRegistry` | YES | Colon-separated string: `eip155:{chainId}:{identityRegistryAddress}`. |
| `chainId` | YES | EIP-155 Chain ID the session is bound to. |
| `nonce` | YES | Server-generated random string, ≥ 8 alphanumeric characters. Must be single-use. |
| `issuedAt` | YES | RFC 3339 datetime when the message was created. |
| `expirationTime` | NO | RFC 3339 datetime after which the message is invalid. |
| `notBefore` | NO | RFC 3339 datetime before which the message is invalid. |
| `requestId` | NO | Opaque identifier for the sign-in request. |

## Example Message

```
api.myplatform.com wants you to sign in with your Agent account:
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0

Authenticate as a registered ERC-8004 agent.

URI: https://api.myplatform.com/siwa
Version: 1
Agent ID: 42
Agent Registry: eip155:84532:0x8004A818BFB912233c491871b3d84c89A494BD9e
Chain ID: 84532
Nonce: kX9f2mPqR7wL
Issued At: 2025-09-01T12:00:00Z
Expiration Time: 2025-09-01T12:10:00Z
```

## Authentication Flow

### 1. Nonce Request

```
POST /siwa/nonce
Content-Type: application/json

{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
  "agentId": 42,
  "agentRegistry": "eip155:84532:0x8004A818BFB912233c491871b3d84c89A494BD9e"
}
```

Server response:

```json
{
  "nonce": "kX9f2mPqR7wL",
  "issuedAt": "2025-09-01T12:00:00Z",
  "expirationTime": "2025-09-01T12:10:00Z"
}
```

The server MUST store the nonce associated with the address and mark it as consumed after one use.

### 2. Agent Signs Message

The agent constructs the full SIWA message string from the fields and signs using EIP-191 `personal_sign` (prefix `"\x19Ethereum Signed Message:\n" + len(message) + message`).

```typescript
const message = buildSIWAMessage({
  domain: 'api.myplatform.com',
  address: wallet.address,
  statement: 'Authenticate as a registered ERC-8004 agent.',
  uri: 'https://api.myplatform.com/siwa',
  version: '1',
  agentId: 42,
  agentRegistry: 'eip155:84532:0x8004A818BFB912233c491871b3d84c89A494BD9e',
  chainId: 84532,
  nonce: 'kX9f2mPqR7wL',
  issuedAt: '2025-09-01T12:00:00Z',
  expirationTime: '2025-09-01T12:10:00Z'
});

const signature = await wallet.signMessage(message);
```

### 3. Verification Request

```
POST /siwa/verify
Content-Type: application/json

{
  "message": "<full SIWA message string>",
  "signature": "0x..."
}
```

### 4. Server Verification Steps

The server MUST perform ALL of the following:

1. **Parse** — Validate the message conforms to the SIWA ABNF format.
2. **Recover** — Use `ecrecover` (via `ethers.verifyMessage`) to recover the signer address from the signature.
3. **Address match** — Confirm recovered address matches the `address` field in the message.
4. **Domain binding** — Confirm the `domain` field matches the server's own origin.
5. **Nonce** — Confirm the `nonce` was issued by this server and has not been consumed.
6. **Time window** — If `expirationTime` is present, confirm `now < expirationTime`. If `notBefore` is present, confirm `now >= notBefore`.
7. **Onchain ownership** — Call `ownerOf(agentId)` on the Identity Registry at the address specified in `agentRegistry`. Confirm the returned owner matches the recovered signer address.
8. **Consume nonce** — Mark the nonce as used to prevent replay.

If all checks pass, issue a session token (JWT or equivalent) containing at minimum: `address`, `agentId`, `agentRegistry`, `chainId`, `iat`, `exp`.

### 5. Server Response

Success:

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "agent": {
    "agentId": 42,
    "agentRegistry": "eip155:84532:0x8004A818BFB912233c491871b3d84c89A494BD9e",
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
  }
}
```

Failure:

```json
{
  "success": false,
  "error": "Signature does not match agent owner"
}
```

## Smart Contract Wallet Support

For smart contract wallets (e.g., ERC-4337 accounts), verification SHOULD fall back to ERC-1271 `isValidSignature(hash, signature)` if `ecrecover` does not match. This mirrors the ERC-8004 spec's support for EIP-1271 alongside EIP-712.

## Security Considerations

- **Replay protection**: Nonces MUST be single-use and server-generated. Servers SHOULD expire unused nonces after a short TTL (e.g., 5–10 minutes).
- **Domain binding**: The `domain` field MUST match the requesting origin to prevent phishing. Agents SHOULD verify the domain before signing.
- **Onchain verification is mandatory**: Unlike SIWE, SIWA REQUIRES the server to verify onchain ownership. This is the key differentiator — proving the signer is a registered ERC-8004 agent.
- **Key management**: Agent private keys SHOULD be stored in secure enclaves, environment variables, or TEEs. Never expose keys in client-side code.
- **Transfer handling**: If an agent NFT is transferred, the previous owner's SIWA sessions become invalid (ownership check fails). Servers SHOULD set reasonable session TTLs.
- **agentWallet vs owner**: The `agentWallet` metadata key in ERC-8004 is for payment routing. SIWA authenticates the **owner** (the address that holds the NFT). Servers MAY optionally also accept signatures from the `agentWallet` address if the use case warrants it.

## Comparison with SIWE (EIP-4361)

| Aspect | SIWE (EIP-4361) | SIWA |
|---|---|---|
| Purpose | Human wallet auth | Agent identity auth |
| Identity proof | Owns an Ethereum address | Owns an ERC-8004 agent NFT |
| Onchain check | None required | `ownerOf(agentId)` REQUIRED |
| Extra fields | None | `agentId`, `agentRegistry` |
| Signing standard | EIP-191 | EIP-191 (same) |
| Contract wallets | ERC-1271 | ERC-1271 (same) |
| Message prefix | "wants you to sign in with your Ethereum account" | "wants you to sign in with your Agent account" |
