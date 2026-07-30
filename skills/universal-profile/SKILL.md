---
name: universal-profile
description: Manage LUKSO Universal Profiles — identity, permissions, tokens, blockchain operations. Cross-chain support for Base and Ethereum.
version: 0.9.0
author: frozeman
---

# Universal Profile Skill

Authorize your bot: create a profile at [my.universalprofile.cloud](https://my.universalprofile.cloud), generate a controller key, authorize via [Authorization UI](https://openclaw.universalprofile.cloud).

## Core Concepts

- **UP (Universal Profile)** = smart contract account (LSP0/ERC725Account). This is the on-chain identity.
- **KeyManager (LSP6)** = access control. Controllers have permission bitmasks.
- **Controller** = EOA with permissions to act on behalf of the UP.
- All calls to external contracts MUST route through UP via `execute()` so `msg.sender` = UP address.
- Exception: `setData()`/`setDataBatch()` can be called directly on UP (checks permissions internally).

## Execution Models

### Direct (all chains — controller pays gas)
```
Controller → UP.execute(operation, target, value, data) → Target
```
The controller calls `execute()` directly on the UP contract. The UP internally verifies permissions via its KeyManager (LSP20 lsp20VerifyCall). **Do NOT call the KeyManager's execute() function directly.** Always call the UP.

### Gasless Relay (LUKSO ONLY — chains 42/4201)
```
Controller signs LSP25 → Relay API submits → KeyManager.executeRelayCall() → UP
```
The controller signs a message, then the LUKSO relay service submits the transaction. **Do NOT call executeRelayCall() yourself — the relay API does this.**

**⚠️ CRITICAL: The relay/gasless option exists ONLY on LUKSO mainnet (42) and testnet (4201). On Base, Ethereum, and all other chains, the controller must hold native ETH and pay gas directly. There is no gasless alternative.**

Typical gas costs: LUKSO ~free via relay, Base ~$0.001-0.01/tx, Ethereum ~$0.10-1.00/tx.

## Networks

| Chain | ID | RPC | Explorer | Relay | Token |
|---|---|---|---|---|---|
| LUKSO | 42 | `https://42.rpc.thirdweb.com` | `https://explorer.lukso.network` | `https://relayer.mainnet.lukso.network/api` | LYX |
| LUKSO Testnet | 4201 | `https://rpc.testnet.lukso.network` | `https://explorer.testnet.lukso.network` | `https://relayer.testnet.lukso.network/api` | LYXt |
| Base | 8453 | `https://mainnet.base.org` | `https://basescan.org` | ❌ | ETH |
| Ethereum | 1 | `https://eth.llamarpc.com` | `https://etherscan.io` | ❌ | ETH |

## CLI

```
up status                                      # Config, keys, connectivity
up profile info [<address>] [--chain <chain>]  # Profile details
up profile configure <address> [--chain lukso]  # Save UP for use
up key generate [--save] [--password <pw>]     # Generate controller keypair
up permissions encode <perm1> [<perm2> ...]    # Encode to bytes32
up permissions decode <hex>                    # Decode to names
up permissions presets                         # List presets
up authorize url [--permissions <preset|hex>]  # Generate auth URL
up quota                                       # Check relay gas quota (LUKSO only)
```

Presets: `read-only` 🟢 | `token-operator` 🟡 | `nft-trader` 🟡 | `defi-trader` 🟠 | `profile-manager` 🟡 | `full-access` 🔴

## Credentials

Config lookup order: `UP_CREDENTIALS_PATH` env → `~/.openclaw/universal-profile/config.json` → `~/.clawdbot/universal-profile/config.json`

Key lookup order: `UP_KEY_PATH` env → `~/.openclaw/credentials/universal-profile-key.json` → `~/.clawdbot/credentials/universal-profile-key.json`

Canonical path for new credentials: `~/.openclaw/credentials/universal-profile-key.json`

Skill config path: `~/.openclaw/skills/universal-profile/config.json`

Expected JSON format:
```json
{
  "universalProfile": {
    "address": "0xYourUniversalProfileAddress"
  },
  "controller": {
    "address": "0xYourControllerAddress",
    "privateKey": "0xYourPrivateKey"
  }
}
```

Key file permissions: `chmod 600`. Keys loaded only for signing, then cleared. The skill warns if credential files are readable by group/others.

## Permissions (bytes32 BitArray)

| Permission | Hex | Risk | Notes |
|---|---|---|---|
| CHANGEOWNER | 0x01 | 🔴 | |
| ADDCONTROLLER | 0x02 | 🟠 | |
| EDITPERMISSIONS | 0x04 | 🟠 | |
| ADDEXTENSIONS | 0x08 | 🟡 | |
| CHANGEEXTENSIONS | 0x10 | 🟡 | |
| ADDUNIVERSALRECEIVERDELEGATE | 0x20 | 🟡 | |
| CHANGEUNIVERSALRECEIVERDELEGATE | 0x40 | 🟡 | |
| REENTRANCY | 0x80 | 🟡 | |
| SUPER_TRANSFERVALUE | 0x0100 | 🟠 | Any recipient |
| TRANSFERVALUE | 0x0200 | 🟡 | AllowedCalls only |
| SUPER_CALL | 0x0400 | 🟠 | Any contract |
| CALL | 0x0800 | 🟡 | AllowedCalls only |
| SUPER_STATICCALL | 0x1000 | 🟢 | |
| STATICCALL | 0x2000 | 🟢 | |
| SUPER_DELEGATECALL | 0x4000 | 🔴 | |
| DELEGATECALL | 0x8000 | 🔴 | |
| DEPLOY | 0x010000 | 🟡 | |
| SUPER_SETDATA | 0x020000 | 🟠 | Any key |
| SETDATA | 0x040000 | 🟡 | AllowedERC725YDataKeys only |
| ENCRYPT | 0x080000 | 🟢 | |
| DECRYPT | 0x100000 | 🟢 | |
| SIGN | 0x200000 | 🟢 | |
| EXECUTE_RELAY_CALL | 0x400000 | 🟢 | |

SUPER variants = unrestricted. Regular = restricted to AllowedCalls/AllowedERC725YDataKeys. Prefer restricted.

## Transactions

### Direct Execution (all chains)
```javascript
// Controller calls UP.execute() directly — works on LUKSO, Base, Ethereum
const provider = new ethers.JsonRpcProvider(rpcUrl);  // use correct RPC for chain
const wallet = new ethers.Wallet(controllerPrivateKey, provider);
const up = new ethers.Contract(upAddress, ['function execute(uint256,address,uint256,bytes) payable returns (bytes)'], wallet);
await (await up.execute(0, recipient, ethers.parseEther('0.01'), '0x')).wait();
```

### Gasless Relay (LUKSO only)

**LSP25 Relay Signature — EIP-191 v0, do NOT use `signMessage()`:**
```javascript
const encoded = ethers.solidityPacked(
  ['uint256','uint256','uint256','uint256','uint256','bytes'],
  [25, chainId, nonce, validityTimestamps, msgValue, payload]
);
const prefix = new Uint8Array([0x19, 0x00]);
const msg = new Uint8Array([...prefix, ...ethers.getBytes(kmAddress), ...ethers.getBytes(encoded)]);
const signature = ethers.Signature.from(new ethers.SigningKey(privateKey).sign(ethers.keccak256(msg))).serialized;
```

**Relay API:**
```
POST https://relayer.mainnet.lukso.network/api/execute
{ "address": "0xUP", "transaction": { "abi": "0xpayload", "signature": "0x...", "nonce": 0, "validityTimestamps": "0x0" } }
```

The `payload` for relay calls is the full `UP.execute(...)` calldata. The relay service calls `KeyManager.executeRelayCall()` — you never call the KM directly.

For `setData` via relay, the payload is the `setData(...)` calldata (NOT wrapped in `execute()`).

Nonce channels: `getNonce(controller, channelId)` — same channel = sequential, different = parallel.
Validity timestamps: `(startTimestamp << 128) | endTimestamp`. Use `0` for no restriction.

## Cross-Chain Deployment (LSP23)

UPs can be redeployed at the same address on other chains by replaying the original LSP23 factory calldata.

### Factory & Implementations (identical addresses on LUKSO, Base, Ethereum)

| Contract | Address |
|---|---|
| LSP23 Factory | `0x2300000A84D25dF63081feAa37ba6b62C4c89a30` |
| UniversalProfileInit v0.14.0 | `0x3024D38EA2434BA6635003Dc1BDC0daB5882ED4F` |
| LSP6KeyManagerInit v0.14.0 | `0x2Fe3AeD98684E7351aD2D408A43cE09a738BF8a4` |
| PostDeploymentModule | `0x000000000066093407b6704B89793beFfD0D8F00` |

### Workflow
1. Retrieve original deployment calldata: `node commands/cross-chain-deploy-data.js <upAddress> [--verify]`
2. Fund controller with ETH on target chain
3. Submit same calldata to factory: `wallet.sendTransaction({ to: factoryAddress, data: calldata, value: 0n })`
4. Authorize controller on new chain via [Authorization UI](https://openclaw.universalprofile.cloud) (permissions are per-chain)

### Limitations
- Legacy UPs (pre-LSP23, old lsp-factory) have no deployment events
- Determinism requires identical salt + implementations + init data

## LSP Ecosystem

| LSP | Interface ID | Name | Purpose |
|---|---|---|---|
| LSP0 | 0x24871b3d | ERC725Account | Smart contract account (UP) |
| LSP1 | 0x6bb56a14 | UniversalReceiver | Notification hooks |
| LSP2 | — | ERC725Y JSON Schema | Key encoding |
| LSP3 | — | Profile Metadata | Name, avatar, links, tags |
| LSP4 | — | Digital Asset Metadata | Token name, symbol, type |
| LSP5 | — | ReceivedAssets | Tracks owned tokens/NFTs |
| LSP6 | 0x23f34c62 | KeyManager | Permission-based access control |
| LSP7 | 0xc52d6008 | DigitalAsset | Fungible tokens (like ERC20) |
| LSP8 | 0x3a271706 | IdentifiableDigitalAsset | NFTs (bytes32 token IDs) |
| LSP9 | 0x28af17e6 | Vault | Sub-account for asset segregation |
| LSP14 | 0x94be5999 | Ownable2Step | Two-step ownership transfer |
| LSP25 | 0x5ac79908 | ExecuteRelayCall | Gasless meta-transactions (LUKSO only) |
| LSP26 | 0x2b299cea | FollowerSystem | On-chain follow/unfollow |
| LSP28 | — | TheGrid | Customizable profile grid layouts |

Full ABIs, interface IDs, and ERC725Y data keys in `lib/constants.js`.

## LSP26 Follow/Unfollow

Contract: `0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA` (LUKSO mainnet).

MUST route through UP via `execute()` — never call directly from controller.
```javascript
const followData = lsp26Iface.encodeFunctionData('follow', [targetAddress]);
// Direct: km.execute(up.encodeFunctionData('execute', [0, LSP26_ADDR, 0, followData]))
// Relay: sign + submit via relay API
```

## VerifiableURI (LSP2)

Format: `0x` + `00006f357c6a0020` (8-byte header) + `keccak256hash` (32 bytes) + `url as UTF-8 hex`

Header = verificationMethod(2) + hashFunction(4=keccak256(utf8)) + hashLength(2=0x0020).

Decoding: skip 80 hex chars (2 + 8 + 4 + 64 + 2 prefix), rest = UTF-8 URL.

**Common mistakes:** forgetting `0020` hash length bytes, not pinning IPFS before on-chain tx, hash mismatch from re-serialization.

### LSP3 Profile Update Procedure
1. Read current: `getData(0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5)` → decode VerifiableURI → fetch JSON
2. Modify JSON
3. Use `{ verification: { method: "keccak256(bytes)", data: "0x..." }, url: "ipfs://..." }` for images
4. Pin images + JSON to IPFS, verify accessible via gateway
5. Compute `keccak256(exactJsonBytes)`, encode VerifiableURI
6. `setData(LSP3_KEY, verifiableUri)` from controller
7. Verify: read back, decode, fetch, confirm

LSP3 key: `0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5`
LSP28 key: `0x724141d9918ce69e6b8afcf53a91748466086ba2c74b94cab43c649ae2ac23ff`

## LSP28 TheGrid

Grid layout JSON at LSP28 key as VerifiableURI.
```json
{ "LSP28TheGrid": [{ "title": "My Grid", "gridColumns": 2, "visibility": "public",
  "grid": [
    { "width": 1, "height": 1, "type": "TEXT", "properties": { "title": "Hi", "text": "...", "backgroundColor": "#1a1a2e", "textColor": "#fff" } },
    { "width": 2, "height": 2, "type": "IMAGES", "properties": { "type": "grid", "images": ["https://..."] } },
    { "width": 1, "height": 1, "type": "X", "properties": { "type": "post", "username": "handle", "id": "tweetId", "theme": "dark" } }
  ]
}] }
```
Types: `IFRAME`, `TEXT`, `IMAGES`, `X`, `INSTAGRAM`, `QR_CODE`, `ELFSIGHT`. gridColumns 2–4, width/height 1–3.

## Forever Moments (LUKSO only)

Social NFT platform. Agent API at `https://www.forevermoments.life/api/agent/v1`.

### 3-Step Relay Flow
1. **Build** — `POST /moments/build-mint` (or `/collections/build-join`, etc.) → get `derived.upExecutePayload`
2. **Prepare** — `POST /relay/prepare` with `{ upAddress, controllerAddress, payload }` → get `hashToSign`, `nonce`
3. **Sign & Submit** — sign `hashToSign` as RAW DIGEST (`SigningKey.sign()`, NOT `signMessage()`) → `POST /relay/submit`

### Endpoints
- `/collections/build-join` — join collection
- `/collections/build-create` + `/collections/finalize-create` — create collection (2-step)
- `/moments/build-mint` — mint Moment NFT
- `/relay/prepare` + `/relay/submit` — relay flow
- `/api/pinata` (NOT `/api/agent/v1/pinata`) — pin file to IPFS (multipart)

### Metadata (LSP4)
```json
{ "LSP4Metadata": { "name": "Title", "description": "...",
  "images": [[{ "width": 1024, "height": 1024, "url": "ipfs://Qm..." }]],
  "icon": [{ "width": 1024, "height": 1024, "url": "ipfs://Qm..." }],
  "tags": ["tag1"], "createdAt": "2026-02-08T16:30:00.000Z" } }
```

Known collection "Art by the Machine": `0x439f6793b10b0a9d88ad05293a074a8141f19d77`

### URLs
- Collection: `https://www.forevermoments.life/collections/<addr>`
- Moment: `https://www.forevermoments.life/moments/<addr>`
- Profile: `https://www.forevermoments.life/profile/<addr>`

## Error Codes

| Code | Cause |
|---|---|
| UP_PERMISSION_DENIED | Controller lacks required permission |
| UP_RELAY_FAILED | Relay error — check quota (LUKSO only) |
| UP_INVALID_SIGNATURE | Wrong chainId, used nonce, or expired timestamps |
| UP_QUOTA_EXCEEDED | Monthly relay quota exhausted (LUKSO only) |
| UP_NOT_AUTHORIZED | Not a controller — use [Authorization UI](https://openclaw.universalprofile.cloud) |

## Security

- Grant minimum permissions. Prefer CALL over SUPER_CALL.
- Use AllowedCalls/AllowedERC725YDataKeys to restrict.
- Avoid DELEGATECALL and CHANGEOWNER unless necessary.
- Never log/print/transmit private keys.
- Test on testnet (4201) first.
- `config set` restricted to safe keys only.

## ERC725.js — Reading & Writing UP Data

**Package:** `@erc725/erc725.js` — the standard library for reading, encoding, and decoding ERC725Y data on Universal Profiles. **Use this for all profile data operations** (reading profiles, permissions, assets, encoding setData payloads).

Full reference: [`references/ERC725-JS.md`](references/ERC725-JS.md)

### Quick Start
```js
import ERC725 from '@erc725/erc725.js';
import { LSP3Schema, LSP5Schema, LSP6Schema } from '@erc725/erc725.js/schemas';

// Connect to a UP
const erc725 = new ERC725(LSP3Schema, upAddress, 'https://42.rpc.thirdweb.com', {
  ipfsGateway: 'https://api.universalprofile.cloud/ipfs/',
});

// Read profile (fetches + verifies IPFS content)
const profile = await erc725.fetchData('LSP3Profile');

// Encode data for setData/setDataBatch
const { keys, values } = erc725.encodeData([{
  keyName: 'LSP3Profile',
  value: { json: profileJson, url: 'ipfs://Qm...' },
}]);
```

### Key Operations
- **`getData(key)`** — read raw decoded value from contract
- **`fetchData(key)`** — read + download linked content (IPFS) + verify hash
- **`encodeData(data)`** — encode for `setData()`/`setDataBatch()` → `{ keys, values }`
- **`decodeData(data)`** — decode raw contract bytes back to structured data
- **`encodeKeyName(name)`** — hash a key name to bytes32
- **Built-in schemas:** LSP1–LSP12, LSP17 (import from `@erc725/erc725.js/schemas`)

### Common Patterns
```js
// Read permissions
const erc725 = new ERC725(LSP6Schema, upAddress, RPC_URL);
const perms = await erc725.getData({
  keyName: 'AddressPermissions:Permissions:<address>',
  dynamicKeyParts: [controllerAddress],
});

// Read received assets
const erc725 = new ERC725(LSP5Schema, upAddress, RPC_URL);
const assets = await erc725.getData('LSP5ReceivedAssets[]');

// Encode VerifiableURI (auto-hashes JSON)
erc725.encodeData([{
  keyName: 'LSP3Profile',
  value: { json: myJson, url: 'ipfs://QmNew...' },
}]);
```

### Important Notes
- **Array encoding:** Always set `totalArrayLength` + `startingIndex` when modifying arrays to avoid corrupting contract state
- **Dynamic keys:** Use `dynamicKeyParts` for Mapping key types (e.g., permissions per address)
- **Backend:** Also install `isomorphic-fetch`
- **VerifiableURI:** Pass `{ json, url }` for auto-hashing, or `{ verification, url }` for pre-computed

## Dependencies

Node.js 18+, ethers.js v6, @erc725/erc725.js, viem.

## Links

[LUKSO Docs](https://docs.lukso.tech/) · [Universal Everything](https://universaleverything.io/) · [LSP6 Spec](https://docs.lukso.tech/standards/access-control/lsp6-key-manager) · [Authorization UI](https://openclaw.universalprofile.cloud)

Profile URLs: always use `https://universaleverything.io/<address>`
