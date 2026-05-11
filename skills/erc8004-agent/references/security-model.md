# Security Model

> Part of the 8004 Agent Skill v0.0.1

How ERC-8004 agent identity keys are stored and protected against prompt injection and accidental exposure.

## Threat Model

### The core problem

An AI agent that processes untrusted input (messages from other agents, web content, user prompts) is vulnerable to **prompt injection**: adversarial instructions embedded in the input that manipulate the agent's behavior.

If the private key is stored in a plaintext file (like a `.env` or a markdown memo), a prompt injection can instruct the agent to:

1. Read the file containing the private key
2. Exfiltrate it (embed in an HTTP request, return it in a response, encode it in an outbound message)

The key is then compromised, and the attacker controls the agent's onchain identity.

### What we defend against

| Threat | Description | Mitigation |
|---|---|---|
| **Prompt injection exfiltration** | Malicious input instructs the agent to read and leak the private key | Key is never in any file the agent reads into context |
| **Context window leakage** | Key appears in the agent's working memory / LLM context | Key is loaded inside a function, used, and discarded — never returned |
| **File system snooping** | Another process reads the key from disk | OS keychain uses encrypted storage with access controls; V3 keystore is AES-encrypted |
| **Log / error exposure** | Key appears in stack traces, console output, or error messages | Signing functions return only signatures, never raw keys |
| **Accidental commit** | Key is committed to version control | No file in the project ever contains the plaintext key |

### What we do NOT defend against

- A fully compromised host (root access) — nothing can protect keys on a fully owned machine short of hardware HSMs
- Malicious code that the agent itself executes (if the agent runs arbitrary code, it can call the keystore API)
- Side-channel attacks on the signing process

For the highest security in production, use a **hardware wallet** or **TEE-based signer** (see ERC-8004's Validation Registry trust models).

## Architecture: Keystore Backends

The `@buildersgarden/siwa/keystore` module provides three storage backends. In production, the **keyring proxy** is the primary backend — all other backends are used either internally by the proxy server or for local development.

### Keyring Proxy (`proxy`) — Production Default

**The recommended backend. Private key never enters the agent process.** See the "Keyring Proxy" section below for full details.

### Encrypted JSON Keystore (`encrypted-file`)

**The Ethereum-native approach. Used internally by the proxy server. Also works for local development.**

Uses the same encrypted format as MetaMask, Geth, and MyEtherWallet:

- **KDF**: scrypt (N=131072, r=8, p=1) derives a 256-bit key from the password
- **Cipher**: AES-128-CTR encrypts the private key
- **MAC**: Keccak-256 integrity check
- **File on disk**: `agent-keystore.json` — contains only ciphertext, never the raw key

This is built into ethers.js:

```typescript
// Encrypt (on wallet creation)
const json = await wallet.encrypt(password);
fs.writeFileSync('./agent-keystore.json', json, { mode: 0o600 });

// Decrypt (on signing)
const wallet = await ethers.Wallet.fromEncryptedJson(json, password);
```

**How it resists prompt injection**: Even if an injection reads `agent-keystore.json`, it gets AES-encrypted ciphertext like:

```json
{"address":"88a5c2d9...","Crypto":{"ciphertext":"10adcc8bcaf49474c6710460e0dc97...","kdf":"scrypt",...}}
```

This is useless without the password. The password can itself be stored in the OS keychain (layered defense) or derived from machine-specific factors.

**File permissions**: Created with `chmod 600` (owner-only read/write).

### Environment Variable (`env`)

**For CI/CD and testing only. Not recommended for production.**

### Keyring Proxy (`proxy`)

**Process isolation — private key never enters the agent process.**

The agent delegates all signing to a separate **keyring proxy server** over HMAC-authenticated HTTP. The proxy server holds the real keystore (any of the backends above) and performs all cryptographic operations. Even full agent compromise (arbitrary code execution) cannot extract the key — only request signatures.

| Property | Detail |
|---|---|
| **Transport** | HMAC-SHA256 authenticated HTTP (30s replay window) |
| **Key isolation** | Private key lives in a separate process; never enters agent memory |
| **Audit** | Every signing request is logged with timestamp, path, source IP |
| **Limitation** | `getSigner()` is not available — use `signMessage()` / `signTransaction()` |

**Architecture:**

```
Agent Process                     Keyring Proxy Server (port 3100)
(auto-detected from               (encrypted-file or env backend)
 KEYRING_PROXY_URL)

signMessage("hello")
  |
  +--> POST /sign-message
       + HMAC-SHA256 header  ---> Validates HMAC + timestamp
                                  Loads key from real keystore
                                  Signs message, discards key
                              <-- Returns { signature, address }
```

**How it resists prompt injection**: The private key exists in a completely separate OS process. Even if the agent process is fully compromised (arbitrary code execution via prompt injection), the attacker can only request signatures — they cannot extract the key. The proxy also maintains an audit log of every signing request.

**Env vars:**

| Variable | Used by | Purpose |
|---|---|---|
| `KEYRING_PROXY_URL` | Agent | Proxy server URL (e.g. `http://localhost:3100`) |
| `KEYRING_PROXY_SECRET` | Both | HMAC shared secret |
| `KEYRING_PROXY_PORT` | Proxy server | Listen port (default: 3100) |

**Deployment:** Deploy the keyring proxy to Railway with one click using the [Railway template](https://railway.com/deploy/siwa-keyring-proxy?referralCode=ZUrs1W), or run it via Docker / locally. Full deployment guide: [https://siwa.builders.garden/docs/deploy](https://siwa.builders.garden/docs/deploy).

### Environment Variable (`env`)

Reads `AGENT_PRIVATE_KEY` from the process environment. This is the least secure option because:

- Environment variables can be read by any process running as the same user
- They may appear in process listings (`/proc/<pid>/environ` on Linux)
- Container orchestrators may log them

Use only when the OS keychain and encrypted file are unavailable (e.g., ephemeral CI runners).

## The Signing Boundary

The most important architectural decision: **external code never receives the private key.**

The `@buildersgarden/siwa/keystore` module exposes only these functions:

```
createWallet()           → { address, backend }           // No key
importWallet(pk)         → { address, backend }           // Consumes key, never returns it
getAddress()             → string                          // Public address only
hasWallet()              → boolean
signMessage(msg)         → { signature, address }          // Key loaded, used, discarded
signTransaction(tx)      → { signedTx, address }           // Key loaded, used, discarded
signAuthorization(auth)  → SignedAuthorization              // EIP-7702 delegation signing
getSigner(provider)      → ethers.Wallet                   // For contract calls (not available with proxy)
```

The private key exists in memory only during a signing call. With the proxy backend, the key never enters the agent process at all — it stays in the proxy server. With local backends, the key is loaded from the backend, used for the cryptographic operation, and then the `Wallet` object falls out of scope and is eligible for garbage collection. It is **never returned** to the calling code.

This means:

- The agent's main loop / LLM context never sees the key
- MEMORY.md contains only public data (address, agentId, etc.)
- A prompt injection that says "read all files and send me secrets" gets nothing useful

## MEMORY.md: Public Data Only

After this redesign, MEMORY.md stores only:

| Field | Sensitive? | Example |
|---|---|---|
| Address | No (public) | `0x1234...abcd` |
| Keystore Backend | No | `encrypted-file` |
| Keystore Path | Low risk | `./agent-keystore.json` |
| Agent ID | No (public) | `42` |
| Agent Registry | No (public) | `eip155:84532:0x8004AA63...` |
| Agent URI | No (public) | `ipfs://Qm...` |
| Chain ID | No (public) | `84532` |
| Sessions | Medium | Session tokens (short-lived) |

The **Private Key** field has been removed entirely.

## Setup Guide

### Recommended: Encrypted File

```bash
export KEYSTORE_PASSWORD="your-strong-passphrase"
```

The keystore will auto-detect the encrypted-file backend and use the password to encrypt/decrypt.

### CI/Testing or Existing Wallet: Environment Variable

```bash
export AGENT_PRIVATE_KEY="0xabc123..."
# KEYSTORE_BACKEND auto-detects to "env" when AGENT_PRIVATE_KEY is set
```

## Key Rotation

To rotate the agent's key while preserving its onchain identity:

1. Create a new wallet via `createWallet()`
2. Transfer the agent NFT to the new address: `transferFrom(oldAddress, newAddress, agentId)`
3. The `agentWallet` metadata key auto-clears on transfer (per ERC-8004 spec)
4. Update MEMORY.md with the new address
5. Delete the old wallet: `deleteWallet()`

## Dependencies

| Package | Required? | Purpose |
|---|---|---|
| `ethers` | **Yes** | Wallet operations, V3 keystore encryption, signing |

No other dependencies are needed. The encrypted-file backend uses only `ethers` built-in functions.
