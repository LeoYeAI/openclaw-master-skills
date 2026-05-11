# MegaFuel API Reference -- Gasless Transactions

## Overview

MegaFuel is NodeReal's paymaster implementation based on BNB Chain's BEP-322 Proposer-Builder Separation (PBS) architecture. It enables gas fee sponsorship for EOA wallets on BSC and opBNB, allowing dApps to cover transaction costs for their users.

The MegaFuel API is organized into three categories:

- **Sponsor API** -- Core transaction sponsorship and monitoring (public-facing, no API key required)
- **Public Policy API** -- Policy management via authenticated Sponsor endpoint (requires MegaNode API key)
- **Private Policy API** -- Same methods as Public Policy API, but scoped to private policies via `X-MegaFuel-Policy-Uuid` header (requires MegaNode API key)

## Table of Contents

1. [Endpoints](#endpoints) -- Network URLs and authentication
2. [SDKs](#sdks) -- Client libraries and tools
3. [pm_isSponsorable](#pm_issponsorable) -- Check transaction sponsorship eligibility
4. [eth_sendRawTransaction (via MegaFuel)](#eth_sendrawtransaction-via-megafuel) -- Submit sponsored raw transactions
5. [eth_getTransactionCount (via MegaFuel)](#eth_gettransactioncount-via-megafuel) -- Get nonce via MegaFuel
6. [pm_getSponsorTxByTxHash](#pm_getsponsortxbytxhash) -- Look up sponsor tx by hash
7. [pm_getSponsorTxByBundleUuid](#pm_getsponsortxbybundleuuid) -- Look up sponsor tx by bundle
8. [pm_getBundleByUuid](#pm_getbundlebyuuid) -- Get bundle details by UUID
9. [pm_health](#pm_health) -- Check MegaFuel service health
10. [pm_addToWhitelist](#pm_addtowhitelist) -- Add addresses to whitelist
11. [pm_rmFromWhitelist](#pm_rmfromwhitelist) -- Remove addresses from whitelist
12. [pm_emptyWhitelist](#pm_emptywhitelist) -- Clear all whitelist entries
13. [pm_getWhitelist](#pm_getwhitelist) -- Retrieve current whitelist entries
14. [pm_getPolicyByUuid](#pm_getpolicybyuuid) -- Get policy details by UUID
15. [pm_listPoliciesByOwner](#pm_listpoliciesbyowner) -- List policies for an owner
16. [pm_updatePolicy](#pm_updatepolicy) -- Modify an existing policy
17. [pm_getPolicySpendData](#pm_getpolicyspenddata) -- Get policy spending summary
18. [pm_getPolicyDailySpendRecord](#pm_getpolicydailyspendrecord) -- Get daily policy spend records
19. [pm_getUserSpendData](#pm_getuserspenddata) -- Get user spending summary
20. [pm_getUserDailySpendRecord](#pm_getuserdailyspendrecord) -- Get daily user spend records
21. [pm_getSponsorTxByTxHash (Sponsor endpoint)](#pm_getsponsortxbytxhash-sponsor-endpoint) -- Sponsor-scoped tx hash lookup
22. [pm_getSponsorTxByBundleUuid (Sponsor endpoint)](#pm_getsponsortxbybundleuuid-sponsor-endpoint) -- Sponsor-scoped bundle UUID lookup
23. [pm_getBundleByUuid (Sponsor endpoint)](#pm_getbundlebyuuid-sponsor-endpoint) -- Sponsor-scoped bundle details lookup
24. [pm_listDepositsByPolicyUuid](#pm_listdepositsbypolicyuuid) -- List deposits for a policy
25. [pm_listPolicyAudits](#pm_listpolicyaudits) -- View policy audit trail
26. [pm_isSponsorable (Private Policy)](#pm_issponsorable-private-policy) -- Private policy sponsorship check
27. [eth_sendRawTransaction (Private Policy)](#eth_sendrawtransaction-private-policy) -- Submit private policy transactions
28. [eth_getTransactionCount (Private Policy)](#eth_gettransactioncount-private-policy) -- Get nonce via private policy
29. [Timeout Thresholds](#timeout-thresholds) -- Network timeout configurations
30. [Best Practices](#best-practices) -- Recommended usage patterns
31. [Documentation](#documentation) -- Links to external resources

## Endpoints

### Public Endpoints (Sponsor API)

No API key required. Used by wallets and dApps for transaction sponsorship.

| Network | Endpoint |
|---------|----------|
| BSC Mainnet | `https://bsc-megafuel.nodereal.io/` |
| BSC Testnet | `https://bsc-megafuel-testnet.nodereal.io/` |
| opBNB Mainnet | `https://opbnb-megafuel.nodereal.io/` |
| opBNB Testnet | `https://opbnb-megafuel-testnet.nodereal.io/` |

### Authenticated Endpoints (Public Policy API / Sponsor Management)

Requires a MegaNode API key created via [NodeReal MegaNode](https://nodereal.io/meganode).

| Network | Endpoint |
|---------|----------|
| Mainnet | `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` |
| Testnet | `https://open-platform-ap.nodereal.io/{apiKey}/megafuel-testnet` |

### Private Policy Endpoints

Same authenticated endpoints as above, but with an additional required header:

| Header | Value | Description |
|--------|-------|-------------|
| `X-MegaFuel-Policy-Uuid` | UUID string (e.g. `8fabe013-6619-4181-bb8d-6fe0a62421f3`) | Specifies which private policy the caller wants to use |

Private policy endpoints use a network ID path parameter:

| Network | Endpoint |
|---------|----------|
| Mainnet | `https://open-platform-ap.nodereal.io/{apiKey}/megafuel/{networkId}` |
| Testnet | `https://open-platform-ap.nodereal.io/{apiKey}/megafuel-testnet/{networkId}` |

**Supported networkId values:**
- BSC Mainnet: `56`
- BSC Testnet: `97`
- opBNB Mainnet: `201`
- opBNB Testnet: `5611`

## SDKs

- **JavaScript SDK:** [megafuel-js-sdk](https://github.com/node-real/megafuel-js-sdk)
- **Go SDK:** [megafuel-go-sdk](https://github.com/node-real/megafuel-go-sdk)

---

# Sponsor API

Methods available on the public MegaFuel endpoints (BSC/opBNB). These are used by wallets and dApps to check sponsorability, submit gasless transactions, and query transaction/bundle status.

---

## `pm_isSponsorable`

Check if a given transaction can be sponsored via MegaFuel.

**Supported chains:** BSC (mainnet/testnet), opBNB (mainnet/testnet)

**Parameters** (single object in params array):

| Parameter | Type | Description |
|-----------|------|-------------|
| `from` | string | 20 Bytes -- The sender address of the transaction |
| `to` | string | 20 Bytes -- The recipient address of the transaction |
| `value` | string | The value of the transaction in hexadecimal |
| `data` | string | Additional data for the transaction in hexadecimal |
| `gas` | string | The gas limit of the transaction in hexadecimal |

**curl example:**

```bash
curl -X POST https://bsc-megafuel.nodereal.io/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_isSponsorable",
    "params": [{
      "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
      "to": "0xCD9C02358c223a3E788c0b9D94b98D434c7aa0f1",
      "value": "0x2386f26fc10000",
      "data": "0xd46e8dd67c5d32be8d46e8dd67c5d32be8058bb8eb970870f072445675058bb8eb970870f072445675",
      "gas": "0x2901a"
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "sponsorable": true,
    "sponsorName": "MyDApp Sponsor",
    "sponsorIcon": "https://example.com/icon.png",
    "sponsorWebsite": "https://example.com"
  }
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `sponsorable` | boolean | Mandatory. Indicates if the transaction is eligible for sponsorship |
| `sponsorName` | string | Optional. Name of the policy sponsor |
| `sponsorIcon` | string | Optional. Icon URL of the policy sponsor |
| `sponsorWebsite` | string | Optional. Website URL of the policy sponsor |

---

## `eth_sendRawTransaction` (via MegaFuel)

Submit a signed zero-gas transaction to the MegaFuel endpoint for gasless execution.

**Supported chains:** BSC (mainnet/testnet), opBNB (mainnet/testnet)

**Headers:**

| Header | Required | Description |
|--------|----------|-------------|
| `User-Agent` | Recommended | Your wallet name or brand name (e.g. `The-wallet-name/v1.0.0`). Recorded for statistical analysis. |

**Parameters** (array of 1 string):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | The signed transaction data |

**curl example:**

```bash
curl -X POST https://bsc-megafuel.nodereal.io/ \
  -H "Content-Type: application/json" \
  -H "User-Agent: The-wallet-name/v1.0.0" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "eth_sendRawTransaction",
    "params": ["0xF8A882018B8083012E6E9455D398326F99059FF775485246999027B319795580B844A9059CBB000000000000000000000000F161CE1AE27D369C1E2935647F4B7FAA60D2A3B5000000000000000000000000000000000000000000000001AE361FC1451C00008193A009A71BBC6C4368A6C6355E863496BA93CC0D1CE1E342D5A83A5B117B5634EFE3A06E8CAB7D2CDDC31474E5F5B0EF88DB8D7B7A731FE550B0F91BE801EA007B4F59"]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x97655c2f35b153a0818beabd9cf9603d3116c41a08f63d66194814f98b712905"
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | string | 32 Bytes -- The transaction hash, or the zero hash if the transaction is not yet available |

---

## `eth_getTransactionCount` (via MegaFuel)

Get the nonce (number of transactions sent) from the MegaFuel endpoint. Always use this instead of the standard RPC to prevent nonce conflicts.

**Supported chains:** BSC (mainnet/testnet), opBNB (mainnet/testnet)

**Parameters** (array of 2 strings):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | 20 Bytes -- The address to query |
| `params[1]` | string | Block tag: `pending`, `latest`, `safe`, `finalized`, `earliest`, or a hex block number |

**curl example:**

```bash
curl -X POST https://bsc-megafuel.nodereal.io/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "eth_getTransactionCount",
    "params": ["0xDE08B1Fd79b7016F8DD3Df11f7fa0FbfdF07c941", "pending"]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x1"
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | string | Hex value of the transaction count (nonce) |

---

## `pm_getSponsorTxByTxHash`

Get a sponsored transaction record by its transaction hash.

**Supported chains:** BSC (mainnet/testnet), opBNB (mainnet/testnet)

**Parameters** (array of 1 string):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | 32 Bytes -- The user transaction hash |

**curl example:**

```bash
curl -X POST https://bsc-megafuel.nodereal.io/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getSponsorTxByTxHash",
    "params": ["0x97655c2f35b153a0818beabd9cf9603d3116c41a08f63d66194814f98b712905"]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "txHash": "0x97655c2f35b153a0818beabd9cf9603d3116c41a08f63d66194814f98b712905",
    "bundleUuid": "ff5f4d48-2774-4a5e-837c-5b44644c84e1",
    "status": "confirmed",
    "gasPrice": "0x3B9ACA00",
    "gasFee": "0x1DCD6500",
    "bornBlockNumber": 12345678,
    "chainId": 56
  }
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `txHash` | string | Transaction hash uniquely identifying the transaction |
| `bundleUuid` | string (uuid) | UUID of the bundle associated with this transaction |
| `status` | string | Transaction status: `new`, `pending`, `failed`, `confirmed`, or `invalid` |
| `gasPrice` | string | Hex string of the gas price set for executing the transaction |
| `gasFee` | string | Hex string of the total gas fee incurred by the transaction |
| `bornBlockNumber` | integer (int64) | Block number at which the transaction was initially processed |
| `chainId` | integer | Blockchain network identifier |

---

## `pm_getSponsorTxByBundleUuid`

Get a sponsored transaction record by its bundle UUID.

**Supported chains:** BSC (mainnet/testnet), opBNB (mainnet/testnet)

**Parameters** (array of 1 string):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | Bundle UUID |

**curl example:**

```bash
curl -X POST https://bsc-megafuel.nodereal.io/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getSponsorTxByBundleUuid",
    "params": ["ff5f4d48-2774-4a5e-837c-5b44644c84e1"]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "txHash": "0x97655c2f35b153a0818beabd9cf9603d3116c41a08f63d66194814f98b712905",
    "bundleUuid": "ff5f4d48-2774-4a5e-837c-5b44644c84e1",
    "status": "confirmed",
    "gasPrice": "0x3B9ACA00",
    "gasFee": "0x1DCD6500",
    "bornBlockNumber": 12345678,
    "chainId": 56
  }
}
```

**Response fields:** Same as `pm_getSponsorTxByTxHash`.

---

## `pm_getBundleByUuid`

Get bundle information by bundle UUID. A bundle groups multiple sponsored transactions together.

**Supported chains:** BSC (mainnet/testnet), opBNB (mainnet/testnet)

**Parameters** (array of 1 string):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | Bundle UUID |

**curl example:**

```bash
curl -X POST https://bsc-megafuel.nodereal.io/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getBundleByUuid",
    "params": ["ff5f4d48-2774-4a5e-837c-5b44644c84e1"]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "bundleUuid": "ff5f4d48-2774-4a5e-837c-5b44644c84e1",
    "status": "confirmed",
    "avgGasPrice": "0x3B9ACA00",
    "bornBlockNumber": 12345678,
    "confirmedBlockNumber": 12345680,
    "confirmedDate": 1700000000,
    "chainId": 56
  }
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `bundleUuid` | string (uuid) | UUID of the transaction bundle |
| `status` | string | Bundle status: `new`, `pending`, `failed`, `confirmed`, or `invalid` |
| `avgGasPrice` | string | Hex string of the average gas price of transactions within the bundle |
| `bornBlockNumber` | integer (int64) | Block number when the bundle was initially submitted |
| `confirmedBlockNumber` | integer (int64) | Block number when the bundle was confirmed |
| `confirmedDate` | integer (int64) | Unix timestamp when the bundle was confirmed |
| `chainId` | integer | Blockchain network identifier |

---

# Public Policy API

Methods available on the authenticated Sponsor endpoint (`https://open-platform-ap.nodereal.io/{apiKey}/megafuel`). Requires a MegaNode API key. Used by sponsors to manage policies, whitelists, and view spending data.

---

## `pm_health`

Get the system health status of the MegaFuel service.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel`

**Parameters:** None (empty array)

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_health",
    "params": []
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": true
}
```

---

## `pm_addToWhitelist`

Add accounts or contract methods to a certain whitelist for a policy.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (single object in params array):

| Parameter | Type | Description |
|-----------|------|-------------|
| `policyUuid` | string | Policy UUID |
| `whitelistType` | string | One of: `FromAccountWhitelist`, `ToAccountWhitelist`, `ContractMethodSigWhitelist`, `BEP20ReceiverWhiteList` |
| `values` | array of strings | For account whitelists: 20-byte addresses (e.g. `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`). For `ContractMethodSigWhitelist`: 4-byte method signatures (e.g. `0xa9059cbb` for `transfer(address,uint256)`) |

**Whitelist types:**

| Whitelist Type | Value Format | Purpose |
|----------------|--------------|---------|
| `FromAccountWhitelist` | 20-byte address | Only specified sender addresses get sponsorship |
| `ToAccountWhitelist` | 20-byte address | Restricts which contracts can be interacted with |
| `ContractMethodSigWhitelist` | 4-byte method sig | Limits callable contract methods |
| `BEP20ReceiverWhiteList` | 20-byte address | Specifies allowed token receiver addresses |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_addToWhitelist",
    "params": [{
      "policyUuid": "22a1e2e5-1234-11fd-9223-bc9ee5f5abc0",
      "whitelistType": "ToAccountWhitelist",
      "values": ["0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"]
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": true
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | boolean | `true` if values were successfully added, otherwise `false` |

---

## `pm_rmFromWhitelist`

Remove given values from a certain whitelist type for a policy.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (single object in params array):

| Parameter | Type | Description |
|-----------|------|-------------|
| `policyUuid` | string | Policy UUID |
| `whitelistType` | string | One of: `FromAccountWhitelist`, `ToAccountWhitelist`, `ContractMethodSigWhitelist`, `BEP20ReceiverWhiteList` |
| `values` | array of strings | Address or method sig values to remove |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_rmFromWhitelist",
    "params": [{
      "policyUuid": "22a1e2e5-1234-11fd-9223-bc9ee5f5abc0",
      "whitelistType": "ToAccountWhitelist",
      "values": ["0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"]
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": true
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | boolean | `true` if values were successfully removed, otherwise `false` |

---

## `pm_emptyWhitelist`

Remove all values from a certain whitelist type for a policy.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (single object in params array):

| Parameter | Type | Description |
|-----------|------|-------------|
| `policyUuid` | string | Policy UUID |
| `whitelistType` | string | One of: `FromAccountWhitelist`, `ToAccountWhitelist`, `ContractMethodSigWhitelist`, `BEP20ReceiverWhiteList` |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_emptyWhitelist",
    "params": [{
      "policyUuid": "22a1e2e5-1234-11fd-9223-bc9ee5f5abc0",
      "whitelistType": "ToAccountWhitelist"
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": true
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | boolean | `true` if all values for the given whitelist type were successfully removed, otherwise `false` |

---

## `pm_getWhitelist`

Get all values from a certain whitelist type with pagination.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (single object in params array):

| Parameter | Type | Description |
|-----------|------|-------------|
| `policyUuid` | string | Policy UUID |
| `whitelistType` | string | One of: `FromAccountWhitelist`, `ToAccountWhitelist`, `ContractMethodSigWhitelist`, `BEP20ReceiverWhiteList` |
| `offset` | string | Pagination offset. Must be less than 100000. Default: `0` |
| `limit` | string | Pagination limit. Must be less than 100000. Default: `0` |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getWhitelist",
    "params": [{
      "policyUuid": "22a1e2e5-1234-11fd-9223-bc9ee5f5abc0",
      "whitelistType": "ToAccountWhitelist",
      "offset": 0,
      "limit": 100
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "0xCD9C02358c223a3E788c0b9D94b98D434c7aa0f1"
  ]
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `result` | array of strings | Account addresses or contract method hex values in the whitelist |

---

## `pm_getPolicyByUuid`

Get detailed information about a specific policy using its UUID.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel`

**Parameters** (array of 1 string):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | Policy UUID |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getPolicyByUuid",
    "params": ["22a1e2e5-1234-11fd-9223-bc9ee5f5abc0"]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "uuid": "22a1e2e5-1234-11fd-9223-bc9ee5f5abc0",
    "name": "My Policy",
    "type": 1,
    "network": 56,
    "owner": "550e8400-e29b-41d4-a716-446655440000",
    "start": 1700000000,
    "end": 1800000000,
    "activated": true,
    "fromWhitelistEnabled": false,
    "toWhitelistEnabled": true,
    "contractMethodSigWhitelistEnabled": true,
    "bep20ReceiverWhitelistEnabled": false,
    "createTimestamp": 1700000000,
    "updateTimestamp": 1700100000,
    "sponsorName": "MyDApp",
    "sponsorIcon": "https://example.com/icon.png",
    "sponsorWebsite": "https://example.com",
    "maxGasCostPerAddr": "1000000000000000000",
    "maxGasCostPerAddrPerDay": "100000000000000000",
    "maxGasCost": "10000000000000000000",
    "maxTxCountPerAddrPerDay": "100",
    "minSupportedAmount": "0",
    "sponsoredGasfee": "500000000000000000",
    "remainingBalance": "9500000000000000000"
  }
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | string (uuid) | Unique identifier for the policy |
| `name` | string | Name of the policy (max 64 characters) |
| `type` | integer | Type of the policy |
| `network` | integer | Chain ID of the network |
| `owner` | string (uuid) | UUID of the policy owner |
| `start` | integer (int64) | Start timestamp of the policy |
| `end` | integer (int64) | End timestamp of the policy |
| `activated` | boolean | Whether the policy is currently activated |
| `fromWhitelistEnabled` | boolean | Whether the from-address whitelist is enabled |
| `toWhitelistEnabled` | boolean | Whether the to-address whitelist is enabled |
| `contractMethodSigWhitelistEnabled` | boolean | Whether the contract method signature whitelist is enabled |
| `bep20ReceiverWhitelistEnabled` | boolean | Whether the BEP20 receiver whitelist is enabled |
| `createTimestamp` | integer (int64) | Timestamp when the policy was created |
| `updateTimestamp` | integer (int64) | Timestamp when the policy was last updated |
| `sponsorName` | string | Name of the policy sponsor (max 64 characters) |
| `sponsorIcon` | string | URL of the sponsor's icon (max 2048 characters) |
| `sponsorWebsite` | string | URL of the sponsor's website (max 2048 characters) |
| `maxGasCostPerAddr` | string | Maximum gas cost allowed per address (wei) |
| `maxGasCostPerAddrPerDay` | string | Maximum gas cost allowed per address per day (wei) |
| `maxGasCost` | string | Maximum total gas cost allowed for the policy (wei) |
| `maxTxCountPerAddrPerDay` | string | Maximum number of transactions allowed per address per day |
| `minSupportedAmount` | string | Minimum amount that needs to be supported (wei) |
| `sponsoredGasfee` | string | Total amount of gas fees sponsored under this policy (wei) |
| `remainingBalance` | string | Remaining balance available for sponsoring gas fees (wei) |

---

## `pm_listPoliciesByOwner`

Lists all policies and their associated costs and balances for the authenticated owner.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel`

**Parameters:** None (empty array)

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_listPoliciesByOwner",
    "params": []
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "uuid": "22a1e2e5-1234-11fd-9223-bc9ee5f5abc0",
      "name": "My Policy",
      "type": 1,
      "network": 56,
      "owner": "550e8400-e29b-41d4-a716-446655440000",
      "start": 1700000000,
      "end": 1800000000,
      "activated": true,
      "fromWhitelistEnabled": false,
      "toWhitelistEnabled": true,
      "contractMethodSigWhitelistEnabled": true,
      "bep20ReceiverWhitelistEnabled": false,
      "createTimestamp": 1700000000,
      "updateTimestamp": 1700100000,
      "sponsorName": "MyDApp",
      "sponsorIcon": "https://example.com/icon.png",
      "sponsorWebsite": "https://example.com",
      "maxGasCostPerAddr": "1000000000000000000",
      "maxGasCostPerAddrPerDay": "100000000000000000",
      "maxGasCost": "10000000000000000000",
      "maxTxCountPerAddrPerDay": "100",
      "minSupportedAmount": "0",
      "sponsoredGasfee": "500000000000000000",
      "remainingBalance": "9500000000000000000"
    }
  ]
}
```

**Response fields:** Array of policy objects. Each object has the same fields as `pm_getPolicyByUuid` response.

---

## `pm_updatePolicy`

Update a gas sponsorship policy configuration.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel`

**Parameters** (single object in params array):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uuid` | string (uuid) | Yes | Policy unique identifier |
| `name` | string | No | Policy display name (max 256 characters) |
| `maxGasCostPerAddr` | string | No | Max gas cost per address in wei |
| `maxGasCostPerAddrPerDay` | string | No | Daily gas limit per address in wei |
| `minSupportedAmount` | string | No | Minimum transaction amount in wei |
| `maxTxCountPerAddrPerDay` | string | No | Max daily transactions per address |
| `start` | integer (int64) | No | Policy start timestamp |
| `end` | integer (int64) | No | Policy end timestamp |
| `sponsorName` | string | No | Sponsor display name |
| `sponsorIcon` | string | No | Sponsor icon URL |
| `sponsorWebsite` | string | No | Sponsor website URL |
| `activated` | boolean | No | Whether the policy is activated |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_updatePolicy",
    "params": [{
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Summer Promotion",
      "maxGasCostPerAddr": "2000000000000000000",
      "maxGasCostPerAddrPerDay": "200000000000000000",
      "maxTxCountPerAddrPerDay": "200",
      "activated": true
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Summer Promotion",
    "type": 1,
    "network": 56,
    "activated": true,
    "maxGasCostPerAddr": "2000000000000000000",
    "maxGasCostPerAddrPerDay": "200000000000000000",
    "maxTxCountPerAddrPerDay": "200",
    "remainingBalance": "9500000000000000000"
  }
}
```

**Response fields:** Returns the full updated policy object (same fields as `pm_getPolicyByUuid`).

---

## `pm_getPolicySpendData`

Get a policy's total spending data by policy UUID.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (array of 1 string):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | Policy UUID |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getPolicySpendData",
    "params": ["22a1e2e5-1234-11fd-9223-bc9ee5f5abc0"]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": 1,
    "cost": "0x1BC16D674EC80000",
    "updateAt": 1700100000,
    "chainId": 56
  }
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer (int64) | Unique identifier of the spending data record |
| `cost` | string | Hex string of the total cost accumulated under the policy |
| `updateAt` | integer (int64) | Timestamp of the last update to this spending record |
| `chainId` | integer | Blockchain network identifier |

---

## `pm_getPolicyDailySpendRecord`

Get daily spend record information for a policy.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel`

**Parameters** (single object in params array):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policyUuid` | string | Yes | Policy UUID |
| `startDate` | string | No | Start date for filtering, format `YYYY-MM-DD`. If specified, `endDate` must also be provided |
| `endDate` | string | No | End date for filtering, format `YYYY-MM-DD`. If specified, `startDate` must also be provided |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getPolicyDailySpendRecord",
    "params": [{
      "policyUuid": "22a1e2e5-1234-11fd-9223-bc9ee5f5abc0",
      "startDate": "2024-09-01",
      "endDate": "2024-09-01"
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "policyUuid": "550e8400-e29b-41d4-a716-446655440000",
      "costInDollar": 12345.67890123,
      "dailyCostInDollar": 123.45678901,
      "snapshotTime": "2024-05-31",
      "chainId": 56,
      "dailyTxCount": 150,
      "totalTxCount": 1500,
      "cost": "1000000000000000000",
      "dailyCost": "10000000000000000",
      "remaining": "500000000000000000"
    }
  ]
}
```

**Response fields (each item in array):**

| Field | Type | Description |
|-------|------|-------------|
| `policyUuid` | string (uuid) | Policy unique identifier |
| `costInDollar` | number (double) | Total cost in USD |
| `dailyCostInDollar` | number (double) | Daily cost in USD |
| `snapshotTime` | string (date) | Snapshot date in `YYYY-MM-DD` format |
| `chainId` | integer | Blockchain network ID |
| `dailyTxCount` | integer (int64) | Daily transaction count |
| `totalTxCount` | integer (int64) | Total transaction count |
| `cost` | string | Total cost in wei (string format) |
| `dailyCost` | string | Daily cost in wei (string format) |
| `remaining` | string | Remaining balance in wei (string format) |

---

## `pm_getUserSpendData`

Get a user's spending data by their address and policy UUID.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (array of 2 strings):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | 20 Bytes -- User (from) address |
| `params[1]` | string | Policy UUID |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getUserSpendData",
    "params": [
      "0xDE08B1Fd79b7016F8DD3Df11f7fa0FbfdF07c941",
      "22a1e2e5-1234-11fd-9223-bc9ee5f5abc0"
    ]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": 1,
    "userAddress": "0xDE08B1Fd79b7016F8DD3Df11f7fa0FbfdF07c941",
    "policyID": 123,
    "gasCost": "0x1BC16D674EC80000",
    "gasCostCurDay": "0xDE0B6B3A7640000",
    "txCountCurDay": 5,
    "updateAt": 1700100000,
    "chainId": 56
  }
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer (int64) | Unique identifier of the spending data record |
| `userAddress` | string | Ethereum address of the user |
| `policyID` | integer (int64) | Internal policy identifier |
| `gasCost` | string | Hex string of the total gas cost accumulated by the user |
| `gasCostCurDay` | string | Hex string of the user's total gas cost for the current day |
| `txCountCurDay` | integer (int64) | Count of transactions processed by the user today |
| `updateAt` | integer (int64) | Timestamp of the last update to this record |
| `chainId` | integer | Blockchain network identifier |

---

## `pm_getUserDailySpendRecord`

Get daily spend record information for a specific user under a policy.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (single object in params array):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `userAddress` | string | Yes | 20 Bytes -- User address |
| `policyUuid` | string | Yes | Policy UUID |
| `startDate` | string | No | Start date for filtering, format `YYYY-MM-DD`. If specified, `endDate` must also be provided |
| `endDate` | string | No | End date for filtering, format `YYYY-MM-DD`. If specified, `startDate` must also be provided |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getUserDailySpendRecord",
    "params": [{
      "userAddress": "0xDE08B1Fd79b7016F8DD3Df11f7fa0FbfdF07c941",
      "policyUuid": "22a1e2e5-1234-11fd-9223-bc9ee5f5abc0",
      "startDate": "2024-09-01",
      "endDate": "2024-09-01"
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "id": 1,
      "userAddress": "0xDE08B1Fd79b7016F8DD3Df11f7fa0FbfdF07c941",
      "policyID": 123,
      "snapshotTime": "2024-09-01",
      "cost": "0x1BC16D674EC80000",
      "dailyCost": "0xDE0B6B3A7640000",
      "chainId": 56
    }
  ]
}
```

**Response fields (each item in array):**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer (int64) | Unique identifier of the user spend data snapshot |
| `userAddress` | string | Ethereum address of the user |
| `policyID` | integer (int64) | Internal policy identifier |
| `snapshotTime` | string (date) | Snapshot date in `YYYY-MM-DD` format |
| `cost` | string | Hex string of the total cost accumulated by the user under the policy |
| `dailyCost` | string | Hex string of the daily cost incurred by the user |
| `chainId` | integer | Blockchain network identifier |

---

## `pm_getSponsorTxByTxHash` (Sponsor endpoint)

Same method as in the Sponsor API section, but accessible via the authenticated endpoint.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (array of 1 string):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | 32 Bytes -- The user transaction hash |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getSponsorTxByTxHash",
    "params": ["0x97655c2f35b153a0818beabd9cf9603d3116c41a08f63d66194814f98b712905"]
  }'
```

**Response:** Same as the public endpoint version (see Sponsor API section above).

---

## `pm_getSponsorTxByBundleUuid` (Sponsor endpoint)

Same method as in the Sponsor API section, but accessible via the authenticated endpoint.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (array of 1 string):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | Bundle UUID |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getSponsorTxByBundleUuid",
    "params": ["ff5f4d48-2774-4a5e-837c-5b44644c84e1"]
  }'
```

**Response:** Same as the public endpoint version (see Sponsor API section above).

---

## `pm_getBundleByUuid` (Sponsor endpoint)

Same method as in the Sponsor API section, but accessible via the authenticated endpoint.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel` (mainnet) or `megafuel-testnet` (testnet)

**Parameters** (array of 1 string):

| Parameter | Type | Description |
|-----------|------|-------------|
| `params[0]` | string | Bundle UUID |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_getBundleByUuid",
    "params": ["ff5f4d48-2774-4a5e-837c-5b44644c84e1"]
  }'
```

**Response:** Same as the public endpoint version (see Sponsor API section above).

---

## `pm_listDepositsByPolicyUuid`

List deposit records for a policy.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel`

**Parameters** (single object in params array):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policyUuid` | string (uuid) | Yes | Policy unique identifier |
| `offset` | integer | No | Pagination offset (0-1000). Default: `0` |
| `limit` | integer | No | Page size (1-100). Default: `10` |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_listDepositsByPolicyUuid",
    "params": [{
      "policyUuid": "550e8400-e29b-41d4-a716-446655440000",
      "offset": 0,
      "limit": 10
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "deposits": [
      {
        "policyId": 67890,
        "policyUuid": "550e8400-e29b-41d4-a716-446655440000",
        "txHash": "0x5f99f06b7e5d78a2d03b49aca7547b5d4d4e75b0b2b3d9e7f8a1c6d5e8f9a0b",
        "sponsor": "550e8400-e29b-41d4-a716-446655440000",
        "createTimestamp": 1717027200,
        "amountStr": "1000000000000000000"
      }
    ],
    "totalCount": 30
  }
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `deposits` | array | Array of deposit records |
| `deposits[].policyId` | integer (uint64) | Internal policy ID |
| `deposits[].policyUuid` | string (uuid) | Policy UUID |
| `deposits[].txHash` | string | Transaction hash of the deposit (0x-prefixed, 64 hex chars) |
| `deposits[].sponsor` | string (uuid) | UUID of the sponsor |
| `deposits[].createTimestamp` | integer (uint64) | Block creation time (unix timestamp) |
| `deposits[].amountStr` | string | Amount in wei (string format) |
| `totalCount` | integer (int64) | Total number of matching deposit records |

---

## `pm_listPolicyAudits`

Retrieve policy audit logs that track changes to policies.

**Endpoint:** `https://open-platform-ap.nodereal.io/{apiKey}/megafuel`

**Parameters** (single object in params array):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uuid` | string (uuid) | No | Filter by policy UUID (nullable) |
| `limit` | integer | No | Page size (1-100). Default: `10` |
| `offset` | integer | No | Pagination offset (0-1000). Default: `0` |
| `start` | integer (int64) | No | Start timestamp for time range filter |
| `end` | integer (int64) | No | End timestamp for time range filter |

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_listPolicyAudits",
    "params": [{
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "limit": 10,
      "offset": 0
    }]
  }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "logs": [
      {
        "id": 12345,
        "policyID": 67890,
        "policyUUID": "550e8400-e29b-41d4-a716-446655440000",
        "actionType": "UpdatePolicy",
        "oldValues": {
          "maxGasCost": "1000000000000000000"
        },
        "newValues": {
          "maxGasCost": "2000000000000000000"
        },
        "requestArgs": {
          "name": "Summer Promotion"
        },
        "operator": "user@example.com",
        "owner": "550e8400-e29b-41d4-a716-446655440000",
        "operationTime": 1717027200
      }
    ],
    "count": 150
  }
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `logs` | array | Array of audit log entries |
| `logs[].id` | integer (uint64) | Log entry unique ID |
| `logs[].policyID` | integer (uint64) | Internal policy ID |
| `logs[].policyUUID` | string (uuid) | External policy identifier |
| `logs[].actionType` | string | One of: `AddToWhitelist`, `RmFromWhitelist`, `EmptyWhitelist`, `UpdatePolicy`, `CreatePolicy` |
| `logs[].oldValues` | object | Previous values before the change |
| `logs[].newValues` | object | New values after the change |
| `logs[].requestArgs` | object (nullable) | Original request arguments |
| `logs[].operator` | string | Operator identifier (e.g. email) |
| `logs[].owner` | string (uuid) | Owner UUID |
| `logs[].operationTime` | integer (int64) | Unix timestamp in seconds |
| `count` | integer (int64) | Total matching records |

---

# Private Policy API

The Private Policy API uses the same methods as the Public Policy API and Sponsor API, but scoped to a specific private policy. All requests require:

1. A MegaNode API key in the URL path
2. The `X-MegaFuel-Policy-Uuid` header to specify which private policy to use
3. A `networkId` path parameter to specify the target chain

**Base URL pattern:**
- Mainnet: `https://open-platform-ap.nodereal.io/{apiKey}/megafuel/{networkId}`
- Testnet: `https://open-platform-ap.nodereal.io/{apiKey}/megafuel-testnet/{networkId}`

**Required header:**

| Header | Value |
|--------|-------|
| `X-MegaFuel-Policy-Uuid` | UUID of the private policy (e.g. `8fabe013-6619-4181-bb8d-6fe0a62421f3`) |

**Available networkId values:**

| Network | networkId |
|---------|-----------|
| BSC Mainnet | `56` |
| BSC Testnet | `97` |
| opBNB Mainnet | `201` |
| opBNB Testnet | `5611` |

### Available Methods

The following methods are available on the Private Policy endpoint. Parameters and responses are identical to their public counterparts documented above.

---

## `pm_isSponsorable` (Private Policy)

Check if a transaction is sponsorable under a specific private policy.

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel/56 \
  -H "Content-Type: application/json" \
  -H "X-MegaFuel-Policy-Uuid: 8fabe013-6619-4181-bb8d-6fe0a62421f3" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "pm_isSponsorable",
    "params": [{
      "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
      "to": "0xCD9C02358c223a3E788c0b9D94b98D434c7aa0f1",
      "value": "0x2386f26fc10000",
      "data": "0xd46e8dd67c5d32be8d46e8dd67c5d32be8058bb8eb970870f072445675058bb8eb970870f072445675",
      "gas": "0x2901a"
    }]
  }'
```

**Response:** Same as the public `pm_isSponsorable`.

---

## `eth_sendRawTransaction` (Private Policy)

Submit a signed transaction via a private policy.

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel/56 \
  -H "Content-Type: application/json" \
  -H "X-MegaFuel-Policy-Uuid: 8fabe013-6619-4181-bb8d-6fe0a62421f3" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "eth_sendRawTransaction",
    "params": ["0xF8A882018B8083012E6E9455D398326F99059FF775485246999027B319795580B844A9059CBB000000000000000000000000F161CE1AE27D369C1E2935647F4B7FAA60D2A3B5000000000000000000000000000000000000000000000001AE361FC1451C00008193A009A71BBC6C4368A6C6355E863496BA93CC0D1CE1E342D5A83A5B117B5634EFE3A06E8CAB7D2CDDC31474E5F5B0EF88DB8D7B7A731FE550B0F91BE801EA007B4F59"]
  }'
```

**Response:** Same as the public `eth_sendRawTransaction`.

---

## `eth_getTransactionCount` (Private Policy)

Get the nonce via a private policy endpoint.

**curl example:**

```bash
curl -X POST https://open-platform-ap.nodereal.io/{apiKey}/megafuel/56 \
  -H "Content-Type: application/json" \
  -H "X-MegaFuel-Policy-Uuid: 8fabe013-6619-4181-bb8d-6fe0a62421f3" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "eth_getTransactionCount",
    "params": ["0xDE08B1Fd79b7016F8DD3Df11f7fa0FbfdF07c941", "pending"]
  }'
```

**Response:** Same as the public `eth_getTransactionCount`.

---

# Complete Method Index

| Method | Category | Endpoint Type | Description |
|--------|----------|---------------|-------------|
| `pm_isSponsorable` | Sponsor API | Public / Private | Check if a transaction is eligible for sponsorship |
| `eth_sendRawTransaction` | Sponsor API | Public / Private | Submit a signed gasless transaction |
| `eth_getTransactionCount` | Sponsor API | Public / Private | Get nonce from MegaFuel endpoint |
| `pm_getSponsorTxByTxHash` | Sponsor API | Public / Authenticated | Get sponsor tx details by tx hash |
| `pm_getSponsorTxByBundleUuid` | Sponsor API | Public / Authenticated | Get sponsor tx details by bundle UUID |
| `pm_getBundleByUuid` | Sponsor API | Public / Authenticated | Get bundle info by UUID |
| `pm_health` | Public Policy API | Authenticated | Check system health |
| `pm_addToWhitelist` | Public Policy API | Authenticated | Add entries to a whitelist |
| `pm_rmFromWhitelist` | Public Policy API | Authenticated | Remove entries from a whitelist |
| `pm_emptyWhitelist` | Public Policy API | Authenticated | Clear all entries from a whitelist |
| `pm_getWhitelist` | Public Policy API | Authenticated | Get whitelist entries with pagination |
| `pm_getPolicyByUuid` | Public Policy API | Authenticated | Get policy details by UUID |
| `pm_listPoliciesByOwner` | Public Policy API | Authenticated | List all policies for the owner |
| `pm_updatePolicy` | Public Policy API | Authenticated | Update policy configuration |
| `pm_getPolicySpendData` | Public Policy API | Authenticated | Get total spending data for a policy |
| `pm_getPolicyDailySpendRecord` | Public Policy API | Authenticated | Get daily spend records for a policy |
| `pm_getUserSpendData` | Public Policy API | Authenticated | Get user spending data by address and policy |
| `pm_getUserDailySpendRecord` | Public Policy API | Authenticated | Get daily spend records for a user |
| `pm_listDepositsByPolicyUuid` | Public Policy API | Authenticated | List deposits for a policy |
| `pm_listPolicyAudits` | Public Policy API | Authenticated | Retrieve policy audit logs |

---

## Timeout Thresholds

| Network | Timeout |
|---------|---------|
| BSC | 120 seconds |
| opBNB | 42 seconds |

If a transaction is not mined within the timeout threshold, consider it failed and implement fallback to standard (gas-paying) transaction submission.

---

## Best Practices

- Always check `pm_isSponsorable` before setting gas price to zero
- Display `sponsorName` to users for transparency
- Implement fallback to standard transaction on sponsorship failure
- Get nonce from MegaFuel endpoint (`eth_getTransactionCount`), not standard RPC, to avoid nonce conflicts
- Include `User-Agent` header with wallet/dApp identifier when calling `eth_sendRawTransaction`
- Implement timeout-based failure detection (120s BSC, 42s opBNB)
- For private policies, always include the `X-MegaFuel-Policy-Uuid` header

---

## Documentation

- **MegaFuel Guide:** https://docs.nodereal.io/docs/megafuel
- **Sponsor Guidelines:** https://docs.nodereal.io/docs/megafuel-sponsor-guidelines
- **Policy Management:** https://docs.nodereal.io/docs/megafuel-policy-management
- **Private Policy:** https://docs.nodereal.io/docs/private-policy
- **BEP-322 Specification:** https://github.com/bnb-chain/BEPs/blob/master/BEPs/BEP-322.md
- **API Reference:** https://docs.nodereal.io/reference
