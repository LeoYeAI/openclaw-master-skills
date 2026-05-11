# AWP Subnet Commands

**API Base URL**: `{API_BASE}/api` (default `https://tapi.awp.sh/api`, override via `AWP_API_URL` env var)

> **IMPORTANT**: Always use the bundled `scripts/*.py` files for write operations — they handle ABI encoding natively in Python, require only python3, and work without Foundry or curl/jq.
> The `cast calldata` examples below are for reference only; do NOT run them directly.

## Setup (reference only — bundled scripts handle this automatically)

```bash
# 以下为参考说明，实际操作使用 scripts/*.py 自动完成
REGISTRY=$(curl -s {API_BASE}/api/registry)
AWP_REGISTRY=$(echo $REGISTRY | jq -r '.awpRegistry')
AWP_TOKEN=$(echo $REGISTRY | jq -r '.awpToken')
STAKE_NFT=$(echo $REGISTRY | jq -r '.stakeNFT')
SUBNET_NFT=$(echo $REGISTRY | jq -r '.subnetNFT')
DAO_ADDR=$(echo $REGISTRY | jq -r '.dao')

WALLET_ADDR=$(awp-wallet receive | jq -r '.eoaAddress')
```

---

## M1 · Register Subnet

### LP Cost Calculation

```solidity
function initialAlphaPrice() view returns (uint256)   // on AWPRegistry
// INITIAL_ALPHA_MINT = 100,000,000 x 10^18
// lpCost = INITIAL_ALPHA_MINT x initialAlphaPrice / 10^18
```

### SubnetParams Struct (6 fields — skillsURI is back!)

```solidity
struct SubnetParams {
    string name;               // Alpha token name (1-64 bytes)
    string symbol;             // Alpha token symbol (1-16 bytes)
    address subnetManager;     // address(0) = auto-deploy SubnetManager proxy
    bytes32 salt;              // CREATE2 salt; bytes32(0) = use subnetId as salt
    uint128 minStake;          // Minimum stake for agents (0 = no minimum)
    string skillsURI;          // Skills file URI (IPFS/HTTPS)
}
```

> **Note**: `subnetManager = address(0)` auto-deploys a SubnetManager proxy with Merkle distribution and AWP strategies (Reserve/AddLiquidity/BuybackBurn). The subnet registrant receives DEFAULT_ADMIN_ROLE on the deployed SubnetManager.

### Contract Calls

```solidity
// Step 1: Approve AWP to AWPRegistry (NOT StakeNFT)
function approve(address spender, uint256 amount) returns (bool)   // on AWPToken
// spender = awpRegistry address

// Step 2: Register subnet (after approve receipt)
function registerSubnet(SubnetParams params) returns (uint256 subnetId)   // on AWPRegistry
// params.salt = bytes32(0) uses subnetId as CREATE2 salt
// params.subnetManager = address(0) auto-deploys SubnetManager proxy

// Gasless (requires prior AWP approve to AWPRegistry)
function registerSubnetFor(address user, SubnetParams params, uint256 deadline, uint8 v, bytes32 r, bytes32 s)

// Fully gasless (ERC-2612 permit + EIP-712 — no prior approve needed)
function registerSubnetForWithPermit(
    address user, SubnetParams params, uint256 deadline,
    uint8 permitV, bytes32 permitR, bytes32 permitS,
    uint8 registerV, bytes32 registerR, bytes32 registerS
)
```

### Vanity Address (optional)

Compute a CREATE2 salt for a vanity Alpha token address before registering:

```
POST /vanity/compute-salt
```
**Request:** empty body or `{}`

**Response:**
```json
{
  "salt": "0x530c11b79dce8dd3f7300373b2fdf33756a9cf6308415950b1a086be39aee365",
  "address": "0xA1b275f674f70f9fa216eE15B47640DcCD77cafe",
  "source": "pool",
  "elapsed": "1ms"
}
```

Use the returned `salt` as `SubnetParams.salt` in `registerSubnet()` to deploy the Alpha token at the vanity address. `source` is `"pool"` (from pre-mined salt pool) or `"mined"` (real-time mining fallback).

> Rate limit: compute-salt **20 requests per IP per hour**; upload-salts **5 requests per IP per hour**.

| Code | Body | Meaning |
|------|------|---------|
| 408 | `{"error": "search timed out..."}` | No match found within 120s timeout |
| 429 | `{"error": "rate limit exceeded"}` | IP rate limit exceeded |
| 500 | `{"error": "..."}` | Mining engine error |

### Vanity Salt Pool System

Manage the pre-mined salt pool for fast vanity address allocation:

```
GET /vanity/mining-params
```
Returns parameters for offline salt mining tools:
```json
{"factoryAddress": "0xAe8E...", "initCodeHash": "0xec76...", "vanityRule": "0x0A01FFFF0C0A0F0E"}
```

```
POST /vanity/upload-salts
```
Batch upload pre-mined salts (max 1000/request). Each salt is verified for CREATE2 correctness + vanityRule compliance:
```json
// Request
{"salts": [{"salt": "0x1234...", "address": "0xa1...cafe"}, ...]}
// Response
{"inserted": 98, "rejected": 2}
```

```
GET /vanity/salts
```
List available (unclaimed) salts. Supports `?limit=` pagination.

```
GET /vanity/salts/count
```
```json
{"available": 42}
```

### Complete Command Templates

```bash
# Gasless registration (recommended — no ETH needed, AWP only):
python3 scripts/relay-register-subnet.py --token {T} --name "MySubnet" --symbol "MSUB" --skills-uri "ipfs://QmHash"
```

### Gasless Subnet Registration — EIP-712 Template

For fully gasless registration via `POST /relay/register-subnet`, the user signs two messages:

**1. ERC-2612 Permit signature** (authorizes AWPRegistry to spend AWP):
```bash
# Get permit nonce from AWPToken contract via RPC (NOT from /api/nonce — that returns the registry nonce)
# nonces(address) selector = 0x7ecebe00
PERMIT_NONCE=$(python3 -c "
import json, urllib.request
addr = '$WALLET_ADDR'.lower().replace('0x','').zfill(64)
payload = json.dumps({'jsonrpc':'2.0','method':'eth_call','params':[{'to':'$AWP_TOKEN','data':'0x7ecebe00'+addr},'latest'],'id':1}).encode()
req = urllib.request.Request('$RPC_URL', data=payload, headers={'Content-Type':'application/json'})
r = json.loads(urllib.request.urlopen(req).read())
print(int(r['result'],16))
")
DEADLINE=$(date -d '+1 hour' +%s)

awp-wallet sign-typed-data --token {T} --data '{
  "types": {
    "EIP712Domain": [
      {"name": "name", "type": "string"},
      {"name": "version", "type": "string"},
      {"name": "chainId", "type": "uint256"},
      {"name": "verifyingContract", "type": "address"}
    ],
    "Permit": [
      {"name": "owner", "type": "address"},
      {"name": "spender", "type": "address"},
      {"name": "value", "type": "uint256"},
      {"name": "nonce", "type": "uint256"},
      {"name": "deadline", "type": "uint256"}
    ]
  },
  "primaryType": "Permit",
  "domain": {
    "name": "AWP Token",
    "version": "1",
    "chainId": 8453,
    "verifyingContract": "'$AWP_TOKEN'"
  },
  "message": {
    "owner": "'$WALLET_ADDR'",
    "spender": "'$AWP_REGISTRY'",
    "value": '$LP_COST_WEI',
    "nonce": '$PERMIT_NONCE',
    "deadline": '$DEADLINE'
  }
}'
```

**2. EIP-712 RegisterSubnet signature** (authorizes registration parameters):
```bash
# Get AWPRegistry nonce (from API, no Foundry needed)
NONCE=$(curl -s {API_BASE}/api/nonce/$WALLET_ADDR | python3 -c "import sys,json; print(json.load(sys.stdin).get('nonce',0))")

awp-wallet sign-typed-data --token {T} --data '{
  "types": {
    "EIP712Domain": [
      {"name": "name", "type": "string"},
      {"name": "version", "type": "string"},
      {"name": "chainId", "type": "uint256"},
      {"name": "verifyingContract", "type": "address"}
    ],
    "RegisterSubnet": [
      {"name": "user", "type": "address"},
      {"name": "name", "type": "string"},
      {"name": "symbol", "type": "string"},
      {"name": "subnetManager", "type": "address"},
      {"name": "salt", "type": "bytes32"},
      {"name": "minStake", "type": "uint128"},
      {"name": "skillsURI", "type": "string"},
      {"name": "nonce", "type": "uint256"},
      {"name": "deadline", "type": "uint256"}
    ]
  },
  "primaryType": "RegisterSubnet",
  "domain": {
    "name": "AWPRegistry",
    "version": "1",
    "chainId": 8453,
    "verifyingContract": "'$AWP_REGISTRY'"
  },
  "message": {
    "user": "'$WALLET_ADDR'",
    "name": "{subnetName}",
    "symbol": "{subnetSymbol}",
    "subnetManager": "0x0000000000000000000000000000000000000000",
    "salt": "'$SALT'",
    "minStake": {minStakeWei},
    "skillsURI": "{skillsURI}",
    "nonce": '$NONCE',
    "deadline": '$DEADLINE'
  }
}'
```

**3. Submit to relay:**
```bash
curl -X POST {API_BASE}/api/relay/register-subnet \
  -H "Content-Type: application/json" \
  -d '{
    "user": "'$WALLET_ADDR'",
    "name": "{subnetName}", "symbol": "{subnetSymbol}",
    "subnetManager": "0x0000000000000000000000000000000000000000",
    "salt": "'$SALT'", "minStake": "{minStakeWei}",
    "skillsURI": "{skillsURI}",
    "deadline": '$DEADLINE',
    "permitSignature": "{permitSigHex}",
    "registerSignature": "{registerSigHex}"
  }'
```

**Relay error responses:**

| Code | Body | Meaning |
|------|------|---------|
| 400 | `{"error": "invalid user address"}` | Malformed Ethereum address |
| 400 | `{"error": "deadline is missing or expired"}` | Deadline is 0 or in the past |
| 400 | `{"error": "missing signature"}` | Signature field empty |
| 400 | `{"error": "invalid signature"}` | EIP-712 signature verification failed |
| 400 | `{"error": "signature expired"}` | On-chain deadline check failed |
| 400 | `{"error": "invalid subnet params (name 1-64 bytes, symbol 1-16 bytes)"}` | Name/symbol length violation |
| 400 | `{"error": "subnet manager address required (auto-deploy not available)"}` | No default SubnetManager impl set |
| 400 | `{"error": "insufficient AWP balance"}` | User lacks AWP for subnet registration |
| 400 | `{"error": "insufficient AWP allowance"}` | Permit signature did not authorize enough AWP |
| 400 | `{"error": "contract is paused"}` | AWPRegistry is in emergency pause state |
| 400 | `{"error": "relay transaction failed"}` | Unrecognized on-chain revert |
| 429 | `{"error": "rate limit exceeded: max 100 requests per 3600s"}` | IP rate limit exceeded |

---

## M2 · Subnet Lifecycle

### Contract Calls

```solidity
function activateSubnet(uint256 subnetId)   // Pending -> Active, NFT owner only
function pauseSubnet(uint256 subnetId)      // Active -> Paused, NFT owner only
function resumeSubnet(uint256 subnetId)     // Paused -> Active, NFT owner only
```

Always check current status via `GET /subnets/{id}` before calling.

### Subnet REST Response

```json
{
  "subnet_id": 1,
  "owner": "0x...",
  "name": "My Subnet",
  "symbol": "MSUB",
  "subnet_contract": "0x...",
  "skills_uri": "ipfs://QmSkills...",
  "alpha_token": "0x...",
  "lp_pool": "0x...",
  "status": "Active",
  "created_at": 1710000000,
  "activated_at": 1710000100,
  "min_stake": 0,
  "immunity_ends_at": null,
  "burned": false
}
```

### Complete Command Templates

```bash
python3 scripts/onchain-subnet-lifecycle.py --token {T} --subnet {subnetId} --action activate
python3 scripts/onchain-subnet-lifecycle.py --token {T} --subnet {subnetId} --action pause
python3 scripts/onchain-subnet-lifecycle.py --token {T} --subnet {subnetId} --action resume
```

---

## M3 · Update Skills URI

### Contract Call

```solidity
function setSkillsURI(uint256 subnetId, string skillsURI)   // on SubnetNFT
// NFT owner only
// Emits SkillsURIUpdated(subnetId, skillsURI)
// subnetId = SubnetNFT tokenId (they correspond 1:1)
```

### Complete Command Template

```bash
python3 scripts/onchain-subnet-update.py --token {T} --subnet {subnetId} --skills-uri "{skillsURI}"
```

---

## M4 · Set Minimum Stake

### Contract Call

```solidity
function setMinStake(uint256 subnetId, uint128 minStake)   // on SubnetNFT
// NFT owner only
// minStake in wei (0 = no minimum)
// Emits MinStakeUpdated(subnetId, minStake)
```

### Complete Command Template

```bash
python3 scripts/onchain-subnet-update.py --token {T} --subnet {subnetId} --min-stake {minStakeWei}
```
