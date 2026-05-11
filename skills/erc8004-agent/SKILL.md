---
name: 8004-agent
version: 0.0.1
description: >
  8004 Agent Skill for registering AI agents on the ERC-8004 Trustless Agents
  standard and authenticating them via SIWA (Sign In With Agent). Use this skill when an agent
  needs to: (1) create or manage an Ethereum wallet for onchain identity, (2) register on the
  ERC-8004 Identity Registry as an NFT-based agent identity (SIGN UP), (3) authenticate with a
  server by proving ownership of an ERC-8004 identity using a signed challenge (SIGN IN / SIWA),
  (4) build or update an ERC-8004 registration file (metadata JSON with endpoints, trust models,
  services), (5) upload agent metadata to IPFS or base64 data URI, (6) look up or verify an
  agent's onchain registration. The agent persists public identity state in MEMORY.md. Private
  keys are held in a separate keyring proxy server — the agent can request signatures but never
  access the key itself.
  Triggers on: ERC-8004, trustless agents, agent registration, SIWA, Sign In With Agent,
  agent identity NFT, Agent0 SDK, agent wallet, agent keystore, keyring proxy.
---

# 8004 Agent Skill v0.0.1

Register AI agents onchain (ERC-8004) and authenticate them via **SIWA (Sign In With Agent)**.

## Overview

ERC-8004 ("Trustless Agents") provides three onchain registries deployed as per-chain singletons:

- **Identity Registry** — ERC-721 NFTs. Each agent gets a unique `agentId` (tokenId) and an `agentURI` pointing to a JSON registration file.
- **Reputation Registry** — Feedback signals (score, tags) from clients to agents.
- **Validation Registry** — Third-party validator attestations (zkML, TEE, staked re-execution).

**SIWA (Sign In With Agent)** is a challenge-response authentication protocol (inspired by SIWE / EIP-4361) where an agent proves ownership of an ERC-8004 identity by signing a structured message. See [references/siwa-spec.md](references/siwa-spec.md).

---

## Security Architecture

> **Full details**: [references/security-model.md](references/security-model.md)

The agent's private key is the root of its onchain identity. It must be protected against prompt injection, accidental exposure, and file system snooping.

### Principle: The private key NEVER enters the agent process

All signing is delegated to a **keyring proxy server** — a separate process that holds the encrypted private key and exposes only HMAC-authenticated signing endpoints. The agent can request signatures but can never extract the key, even under full compromise (arbitrary code execution via prompt injection).

```
Agent Process                     Keyring Proxy Server (port 3100)
(auto-detected from               (holds encrypted private key)
 KEYRING_PROXY_URL)

createWallet()
  |
  +--> POST /create-wallet
       + HMAC-SHA256 header  ---> Generates key, encrypts to disk
                              <-- Returns { address } only

signMessage("hello")
  |
  +--> POST /sign-message
       + HMAC-SHA256 header  ---> Validates HMAC + timestamp (30s window)
                                  Loads key, signs, discards key
                              <-- Returns { signature, address }
```

**Why this is secure:**

| Property | Detail |
|---|---|
| **Key isolation** | Private key lives in a separate OS process; never enters agent memory |
| **Transport auth** | HMAC-SHA256 over method + path + body + timestamp; 30-second replay window |
| **Audit trail** | Every signing request is logged with timestamp, endpoint, source IP, success/failure |
| **Compromise limit** | Even full agent takeover can only request signatures — cannot extract the key |

**Environment variables:**

| Variable | Used by | Purpose |
|---|---|---|
| `KEYRING_PROXY_URL` | Agent | Proxy server URL — private (e.g. `http://keyring-proxy:3100`) or public |
| `KEYRING_PROXY_SECRET` | Both | HMAC shared secret |
| `KEYRING_PROXY_PORT` | Proxy server | Listen port (default: 3100) |
| `AGENT_PRIVATE_KEY` | Proxy server | Hex-encoded private key (0x...) — use an existing wallet instead of generating one |
| `KEYSTORE_PASSWORD` | Proxy server | Password for the encrypted-file keystore (not needed with `AGENT_PRIVATE_KEY`) |

> **Auto-detection**: When `KEYRING_PROXY_URL` is set, `KEYSTORE_BACKEND` automatically defaults to `proxy` — no need to set it manually. When `AGENT_PRIVATE_KEY` is set on the proxy server, `KEYSTORE_BACKEND` defaults to `env`.
>
> The proxy server stores keys using an AES-encrypted V3 JSON Keystore (scrypt KDF) by default. To use an existing wallet instead, set `AGENT_PRIVATE_KEY` on the proxy server — the key is held in memory at runtime (no encrypted file needed).

### Keystore API

The `@buildersgarden/siwa/keystore` module exposes ONLY these operations — none return the private key:

```
createWallet()           → { address, backend }     // Creates key, returns ONLY address
signMessage(msg)         → { signature, address }   // Signs via proxy, key never exposed
signTransaction(tx)      → { signedTx, address }    // Same pattern
signAuthorization(auth)  → SignedAuthorization       // EIP-7702 delegation signing
getAddress()             → string                    // Public address only
hasWallet()              → boolean
```

> `getSigner()` is **not available** with the proxy backend — use `signMessage()` / `signTransaction()` instead.

### IMPORTANT: Install and use the SDK

The agent MUST use the `@buildersgarden/siwa` SDK to interact with the keyring proxy. The SDK handles HMAC authentication automatically.

**Step 1 — Install the SDK** (if not already available in your environment):

```bash
npm install @buildersgarden/siwa
```

**Step 2 — Set environment variables:**

```
KEYRING_PROXY_URL=https://your-keyring-proxy.up.railway.app
KEYRING_PROXY_SECRET=<your-shared-secret>
```

**Step 3 — Use the SDK functions** (never call the proxy HTTP endpoints directly):

```typescript
import { createWallet, signMessage, getAddress } from '@buildersgarden/siwa/keystore';

const info = await createWallet();           // SDK handles HMAC auth internally
const { signature } = await signMessage(msg); // SDK handles HMAC auth internally
const address = await getAddress();           // SDK handles HMAC auth internally
```

The SDK reads `KEYRING_PROXY_URL` and `KEYRING_PROXY_SECRET` from environment variables and constructs the correct HMAC headers automatically.

### Fallback: Manual HMAC authentication (without SDK)

If you absolutely cannot install the SDK (e.g. non-Node.js environment, restricted runtime), you can call the proxy HTTP endpoints directly using the HMAC protocol described below. **Prefer the SDK whenever possible.**

**Headers required on every request** (except `GET /health`):

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |
| `X-Keyring-Timestamp` | Current time as Unix epoch **milliseconds** (e.g. `1738792800000`) |
| `X-Keyring-Signature` | HMAC-SHA256 hex digest of the payload string (see below) |

**HMAC payload format** — a single string with four parts separated by newlines (`\n`):

```
{METHOD}\n{PATH}\n{TIMESTAMP}\n{BODY}
```

| Part | Value |
|---|---|
| `METHOD` | HTTP method, uppercase (always `POST`) |
| `PATH` | Endpoint path (e.g. `/create-wallet`, `/sign-message`) |
| `TIMESTAMP` | Same value as the `X-Keyring-Timestamp` header |
| `BODY` | The raw JSON request body string (e.g. `{}` or `{"message":"hello"}`) |

**Compute the signature:**

```
HMAC-SHA256(secret, "POST\n/create-wallet\n1738792800000\n{}") → hex digest
```

**Timestamp window:** The server rejects requests where the timestamp differs from server time by more than **30 seconds**.

**Example — create a wallet (Node.js without SDK):**

```typescript
import crypto from 'crypto';

const PROXY_URL = process.env.KEYRING_PROXY_URL;
const SECRET = process.env.KEYRING_PROXY_SECRET;

async function proxyRequest(path: string, body: Record<string, unknown> = {}) {
  const bodyStr = JSON.stringify(body);
  const timestamp = Date.now().toString();
  const payload = `POST\n${path}\n${timestamp}\n${bodyStr}`;
  const signature = crypto.createHmac('sha256', SECRET).update(payload).digest('hex');

  const res = await fetch(`${PROXY_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Keyring-Timestamp': timestamp,
      'X-Keyring-Signature': signature,
    },
    body: bodyStr,
  });

  if (!res.ok) throw new Error(`${path} failed (${res.status}): ${await res.text()}`);
  return res.json();
}

// Usage
const wallet = await proxyRequest('/create-wallet');        // { address, backend }
const addr = await proxyRequest('/get-address');             // { address }
const sig = await proxyRequest('/sign-message', { message: 'hello' }); // { signature, address }
```

**Example — create a wallet (Python):**

```python
import hmac, hashlib, json, time, requests, os

PROXY_URL = os.environ["KEYRING_PROXY_URL"]
SECRET = os.environ["KEYRING_PROXY_SECRET"]

def proxy_request(path, body=None):
    if body is None:
        body = {}
    body_str = json.dumps(body, separators=(",", ":"))
    timestamp = str(int(time.time() * 1000))
    payload = f"POST\n{path}\n{timestamp}\n{body_str}"
    signature = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    resp = requests.post(
        f"{PROXY_URL}{path}",
        headers={
            "Content-Type": "application/json",
            "X-Keyring-Timestamp": timestamp,
            "X-Keyring-Signature": signature,
        },
        data=body_str,
    )
    resp.raise_for_status()
    return resp.json()

wallet = proxy_request("/create-wallet")       # {"address": "0x...", "backend": "..."}
sig = proxy_request("/sign-message", {"message": "hello"})  # {"signature": "0x...", "address": "0x..."}
```

**Available endpoints:**

| Endpoint | Body | Response |
|---|---|---|
| `POST /create-wallet` | `{}` | `{ address, backend }` |
| `POST /has-wallet` | `{}` | `{ hasWallet: boolean }` |
| `POST /get-address` | `{}` | `{ address }` |
| `POST /sign-message` | `{ message: string }` | `{ signature, address }` |
| `POST /sign-transaction` | `{ tx: { to, data, nonce, chainId, type, maxFeePerGas, ... } }` | `{ signedTx, address }` |
| `POST /sign-authorization` | `{ auth: { chainId, address, nonce } }` | `{ signedAuthorization }` |
| `GET /health` | — | `{ status: "ok", backend }` (no auth required) |

### MEMORY.md: Public Data Only

MEMORY.md stores the agent's public identity state — **never the private key**:

```markdown
## Wallet
- **Address**: `0x1234...abcd`       <- public
- **Keystore Backend**: `proxy`      <- which backend holds the key
- **Created At**: `2026-02-04T...`

## Registration
- **Status**: `registered`
- **Agent ID**: `42`
- **Agent Registry**: `eip155:84532:0x8004AA63...`
...
```

**Lifecycle rules**:

1. **Before any action** — Read MEMORY.md. If wallet exists, skip creation. If registered, skip re-registration.
2. **After wallet creation** — Write address + backend info to MEMORY.md. Private key goes to proxy keystore only.
3. **After registration** — Write agentId, agentRegistry, agentURI, chainId to MEMORY.md.
4. **After SIWA sign-in** — Append session token under Sessions.

**Template**: [assets/MEMORY.md.template](assets/MEMORY.md.template)

---

## Deploying the Keyring Proxy

Before signing anything, the agent needs a running **keyring proxy** — the separate process that holds the private key and performs all cryptographic operations.

### Option A — Railway (Recommended)

Deploy with one click using the Railway template:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/siwa-keyring-proxy?referralCode=ZUrs1W)

This deploys a single `keyring-proxy` service built from `packages/keyring-proxy/Dockerfile`. Set these environment variables in Railway:

| Variable | Required | Description |
|---|---|---|
| `KEYRING_PROXY_SECRET` | Yes | Shared HMAC-SHA256 secret. Must match your agent. |
| `KEYSTORE_PASSWORD` | Conditional | Password for the encrypted-file keystore (default backend). |
| `AGENT_PRIVATE_KEY` | Conditional | Hex-encoded private key (0x...) to use an existing wallet instead. |

After deployment, note the proxy URL (e.g. `https://your-keyring-proxy.up.railway.app`). Set it as `KEYRING_PROXY_URL` on your agent.

> Full deployment guide with architecture details, OpenClaw gateway setup, and verification steps: [https://siwa.builders.garden/docs/deploy](https://siwa.builders.garden/docs/deploy)

### Option B — Docker (Self-hosted)

```bash
docker build -f packages/keyring-proxy/Dockerfile -t keyring-proxy .
docker run -p 3100:3100 \
  -e KEYRING_PROXY_SECRET=your-secret \
  -e KEYSTORE_PASSWORD=your-password \
  keyring-proxy
```

### Option C — Local Development

```bash
cd packages/siwa-testing
pnpm run proxy
```

Once the proxy is running, set these environment variables on the agent:

```
KEYRING_PROXY_URL=http://localhost:3100   # or your Railway URL
KEYRING_PROXY_SECRET=your-shared-secret
```

The `proxy` keystore backend is auto-detected when `KEYRING_PROXY_URL` is set — no need to set `KEYSTORE_BACKEND` manually.

---

## Workflow: SIGN UP (Agent Registration)

### Step 0: Check MEMORY.md + Keystore

```typescript
import { hasWallet } from '@buildersgarden/siwa/keystore';
import { ensureMemoryExists, hasWalletRecord, isRegistered } from '@buildersgarden/siwa/memory';

ensureMemoryExists('./MEMORY.md', './assets/MEMORY.md.template');

if (await hasWallet() && isRegistered('./MEMORY.md')) {
  // Already registered — skip to SIGN IN or update
}
if (await hasWallet() && hasWalletRecord('./MEMORY.md')) {
  // Wallet exists — skip to Step 2
}
// Otherwise proceed to Step 1
```

### Step 1: Create Wallet (key goes to proxy, address goes to MEMORY.md)

```typescript
import { createWallet } from '@buildersgarden/siwa/keystore';
import { writeMemoryField } from '@buildersgarden/siwa/memory';

const info = await createWallet();  // <- key created in proxy, NEVER returned

// Write ONLY public data to MEMORY.md
writeMemoryField('Address', info.address);
writeMemoryField('Keystore Backend', info.backend);
if (info.keystorePath) writeMemoryField('Keystore Path', info.keystorePath);
writeMemoryField('Created At', new Date().toISOString());
```

### Step 1b: Fund the Wallet (REQUIRED before registration)

**STOP — the wallet must have ETH for gas before any onchain transaction can succeed.** Registration, URI updates, and metadata changes all require gas fees.

After creating the wallet, you MUST:

1. **Show the user the wallet address and the target chain** so they can send funds:
   - Address: the value returned by `createWallet()` or `getAddress()`
   - Chain: the chain where the agent will register (e.g. Base Sepolia chainId `84532`, Base mainnet chainId `8453`)
2. **Tell the user to send ETH** (or the chain's native gas token) to that address on that chain.
3. **Wait for the user to confirm** they have funded the wallet before proceeding to registration.

For testnets, suggest using a faucet:
- **Base Sepolia**: [Base Sepolia faucet](https://www.alchemy.com/faucets/base-sepolia) or bridge from ETH Sepolia
- **ETH Sepolia**: [Sepolia faucet](https://www.alchemy.com/faucets/ethereum-sepolia)

> **Do NOT attempt to register or send any onchain transaction until the wallet is funded.** The transaction will fail with an insufficient funds error.

Example message to show the user:

```
Wallet created successfully!

  Address: 0x1234...abcd
  Chain:   Base Sepolia (chainId 84532)

Please send some ETH to this address on Base Sepolia to cover gas fees.
You can use a faucet: https://www.alchemy.com/faucets/base-sepolia

Let me know once the wallet is funded and I'll proceed with registration.
```

### Step 2: Build the Registration File

Create a JSON file following the ERC-8004 schema. Use [assets/registration-template.json](assets/registration-template.json) as a starting point.

Required fields: `type`, `name`, `description`, `image`, `services`, `active`.

After building, update MEMORY.md profile:

```typescript
writeMemoryField('Name', registrationFile.name);
writeMemoryField('Description', registrationFile.description);
```

### Step 3: Upload Metadata

**Option A — IPFS (Pinata, recommended):**

```typescript
const res = await fetch('https://api.pinata.cloud/pinning/pinJSONToIPFS', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.PINATA_JWT}`
  },
  body: JSON.stringify({ pinataContent: registrationFile })
});
const { IpfsHash } = await res.json();
const agentURI = `ipfs://${IpfsHash}`;
```

**Option B — Base64 data URI:**

```typescript
const encoded = Buffer.from(JSON.stringify(registrationFile)).toString('base64');
const agentURI = `data:application/json;base64,${encoded}`;
```

### Step 4: Register Onchain (signed via proxy)

With the proxy backend, the agent builds the transaction and delegates signing to the proxy:

```typescript
import { signTransaction, getAddress } from '@buildersgarden/siwa/keystore';
import { writeMemoryField } from '@buildersgarden/siwa/memory';

const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const address = await getAddress();

const IDENTITY_REGISTRY_ABI = [
  'function register(string agentURI) external returns (uint256 agentId)',
  'event Registered(uint256 indexed agentId, string agentURI, address indexed owner)'
];

// Build the transaction
const iface = new ethers.Interface(IDENTITY_REGISTRY_ABI);
const data = iface.encodeFunctionData('register', [agentURI]);
const nonce = await provider.getTransactionCount(address);
const feeData = await provider.getFeeData();

const txReq = {
  to: REGISTRY_ADDRESS, data, nonce, chainId,
  type: 2,
  maxFeePerGas: feeData.maxFeePerGas,
  maxPriorityFeePerGas: feeData.maxPriorityFeePerGas,
  gasLimit: (await provider.estimateGas({ to: REGISTRY_ADDRESS, data, from: address })) * 120n / 100n,
};

// Sign via proxy — key never enters this process
const { signedTx } = await signTransaction(txReq);
const txResponse = await provider.broadcastTransaction(signedTx);
const receipt = await txResponse.wait();

// Parse event for agentId
for (const log of receipt.logs) {
  try {
    const parsed = iface.parseLog({ topics: log.topics as string[], data: log.data });
    if (parsed?.name === 'Registered') {
      const agentId = parsed.args.agentId.toString();
      const agentRegistry = `eip155:${chainId}:${REGISTRY_ADDRESS}`;

      // Persist PUBLIC results to MEMORY.md
      writeMemoryField('Status', 'registered');
      writeMemoryField('Agent ID', agentId);
      writeMemoryField('Agent Registry', agentRegistry);
      writeMemoryField('Agent URI', agentURI);
      writeMemoryField('Chain ID', chainId.toString());
      writeMemoryField('Registered At', new Date().toISOString());
    }
  } catch { /* skip non-matching logs */ }
}
```

See [references/contract-addresses.md](references/contract-addresses.md) for deployed addresses per chain.

### Alternative: Agent0 SDK

```typescript
import { SDK } from 'agent0-sdk';
import { readMemory } from '@buildersgarden/siwa/memory';

// Note: Agent0 SDK takes a private key string. If using the SDK,
// you'll need a non-proxy backend or load the key within a narrow scope.
// Prefer the signTransaction() approach above for proxy integration.
```

### Alternative: create-8004-agent CLI

```bash
npx create-8004-agent
```

After `npm run register`, update MEMORY.md with the output agentId.

---

## Workflow: SIGN IN (SIWA — Sign In With Agent)

Full spec: [references/siwa-spec.md](references/siwa-spec.md)

### Step 0: Read Public Identity from MEMORY.md

```typescript
import { readMemory, isRegistered } from '@buildersgarden/siwa/memory';

const memory = readMemory('./MEMORY.md');
if (!isRegistered()) {
  throw new Error('Agent not registered. Run SIGN UP workflow first.');
}

const address = memory['Address'];
const agentId = parseInt(memory['Agent ID']);
const agentRegistry = memory['Agent Registry'];
const chainId = parseInt(memory['Chain ID']);
```

### Step 1: Request Nonce from Server

```typescript
const nonceRes = await fetch('https://api.targetservice.com/siwa/nonce', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ address, agentId, agentRegistry })
});
const { nonce, issuedAt, expirationTime } = await nonceRes.json();
```

### Step 2: Sign via Proxy (key never exposed)

```typescript
import { signSIWAMessage } from '@buildersgarden/siwa/siwa';

// signSIWAMessage internally calls keystore.signMessage()
// which delegates to the keyring proxy — the key never enters this process.
const { message, signature } = await signSIWAMessage({
  domain: 'api.targetservice.com',
  address,
  statement: 'Authenticate as a registered ERC-8004 agent.',
  uri: 'https://api.targetservice.com/siwa',
  agentId,
  agentRegistry,
  chainId,
  nonce,
  issuedAt,
  expirationTime
});
```

### Step 3: Submit and Persist Session

```typescript
import { appendToMemorySection } from '@buildersgarden/siwa/memory';

const verifyRes = await fetch('https://api.targetservice.com/siwa/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message, signature })
});
const session = await verifyRes.json();

if (session.success) {
  appendToMemorySection('Sessions',
    `- **${agentId}@api.targetservice.com**: \`${session.token}\` (exp: ${expirationTime || 'none'})`
  );
}
```

### SIWA Message Format

```
{domain} wants you to sign in with your Agent account:
{address}

{statement}

URI: {uri}
Version: 1
Agent ID: {agentId}
Agent Registry: {agentRegistry}
Chain ID: {chainId}
Nonce: {nonce}
Issued At: {issuedAt}
[Expiration Time: {expirationTime}]
[Not Before: {notBefore}]
[Request ID: {requestId}]
```

### Server-Side Verification

The server MUST:

1. Recover signer from signature (EIP-191)
2. Match recovered address to message address
3. Validate domain binding, nonce, time window
4. **Call `ownerOf(agentId)` onchain** to confirm signer owns the agent NFT
5. *(Optional)* Evaluate `SIWAVerifyCriteria` — activity status, required services, trust models, reputation score
6. Issue session token

`verifySIWA()` in `@buildersgarden/siwa/siwa` accepts an optional `criteria` parameter (6th argument) to enforce requirements after the ownership check:

```typescript
import { verifySIWA } from '@buildersgarden/siwa/siwa';

const result = await verifySIWA(message, signature, domain, nonceValid, provider, {
  mustBeActive: true,              // agent metadata.active must be true
  requiredServices: ['MCP'],       // ServiceType values from ERC-8004
  requiredTrust: ['reputation'],   // TrustModel values from ERC-8004
  minScore: 0.5,                   // minimum reputation score
  minFeedbackCount: 10,            // minimum feedback count
  reputationRegistryAddress: '0x8004BAa1...9b63',
});

// result.agent contains the full AgentProfile when criteria are provided
```

See the test server's `verifySIWARequest()` for a full reference implementation.

| Endpoint | Method | Description |
|---|---|---|
| `/siwa/nonce` | POST | Generate and return a nonce |
| `/siwa/verify` | POST | Accept `{ message, signature }`, verify, return session/JWT |

---

## MEMORY.md Quick Reference

| Section | When Written | Key Fields |
|---|---|---|
| **Wallet** | Step 1 of SIGN UP | Address, Keystore Backend, Created At |
| **Registration** | Step 4 of SIGN UP | Status, Agent ID, Agent Registry, Agent URI, Chain ID |
| **Agent Profile** | Step 2 of SIGN UP | Name, Description, Image |
| **Services** | After adding endpoints | One line per service |
| **Sessions** | After each SIWA sign-in | Token, domain, expiry per session |
| **Notes** | Any time | Free-form (funding tx, faucet used, etc.) |

**What is NOT in MEMORY.md**: Private keys, keystore passwords, mnemonic phrases.

---

## Reference Files

- **[references/security-model.md](references/security-model.md)** — Threat model, keystore architecture, prompt injection defense
- **[references/siwa-spec.md](references/siwa-spec.md)** — Full SIWA protocol specification (message ABNF, field definitions, security considerations)
- **[references/contract-addresses.md](references/contract-addresses.md)** — Deployed registry addresses per chain, ABI fragments
- **[references/registration-guide.md](references/registration-guide.md)** — Detailed registration file schema, endpoint types, update flows

## Core Library (`@buildersgarden/siwa` package)

- **`@buildersgarden/siwa/keystore`** — Secure key storage abstraction with keyring proxy support
- **`@buildersgarden/siwa/memory`** — MEMORY.md read/write helpers (public data only)
- **`@buildersgarden/siwa/siwa`** — SIWA message building, signing (via keystore), and server-side verification (with optional criteria)
- **`@buildersgarden/siwa/registry`** — Read agent profiles (`getAgent`) and reputation (`getReputation`) from on-chain registries. Exports ERC-8004 typed values: `ServiceType`, `TrustModel`, `ReputationTag`
- **`@buildersgarden/siwa/proxy-auth`** — HMAC-SHA256 authentication utilities for the keyring proxy

## Assets

- **[assets/MEMORY.md.template](assets/MEMORY.md.template)** — Template for the agent's public identity memory file
- **[assets/registration-template.json](assets/registration-template.json)** — Starter registration file template
