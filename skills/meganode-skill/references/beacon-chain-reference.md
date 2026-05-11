# ETH Beacon Chain API Reference

## Overview

MegaNode provides Ethereum Beacon Chain (Consensus Layer) API endpoints for interacting with the Ethereum Proof-of-Stake consensus mechanism. These are standard Ethereum Beacon Node REST APIs (not JSON-RPC) that enable querying validator data, block information, attestations, sync committees, and other consensus-layer state.

API Specification: Eth Beacon Node API v2.3.0 (Eth2Spec v1.1.0)

---

## Endpoint

```
https://eth2-beacon-mainnet.nodereal.io/v1/{API-key}
```

All requests send and receive JSON by default. Include `Content-Type: application/json` and `Accept: application/json` headers. Some endpoints also support SSZ format via `Accept: application/octet-stream`.

---

## Table of Contents

1. [Beacon -- State Queries](#1-beacon--state-queries)
2. [Beacon -- Block Queries](#2-beacon--block-queries)
3. [Beacon -- Pool (GET)](#3-beacon--pool-get)
4. [Beacon -- Pool (POST)](#4-beacon--pool-post)
5. [Validator -- Duties](#5-validator--duties)
6. [Validator -- Block Production](#6-validator--block-production)
7. [Validator -- Attestation](#7-validator--attestation)
8. [Validator -- Sync Committee](#8-validator--sync-committee)
9. [Validator -- Subscriptions and Registration](#9-validator--subscriptions-and-registration)
10. [Validator -- Publishing](#10-validator--publishing)
11. [Node](#11-node)
12. [Config](#12-config)
13. [Debug](#13-debug)

---

## Common Parameter Values

### State ID (`{state_id}`)

Used across all `/eth/v1/beacon/states/{state_id}/...` endpoints:

| Value | Description |
|-------|-------------|
| `"head"` | Canonical head in node's view |
| `"genesis"` | Genesis state |
| `"finalized"` | Last finalized state |
| `"justified"` | Last justified state |
| `<slot>` | Slot number (e.g., `"12345"`) |
| `<hex root>` | State root as hex string |

### Block ID (`{block_id}`)

Used across all `/eth/v1/beacon/blocks/{block_id}/...` and `/eth/v1/beacon/headers/{block_id}` endpoints:

| Value | Description |
|-------|-------------|
| `"head"` | Canonical head block |
| `"genesis"` | Genesis block |
| `"finalized"` | Last finalized block |
| `<slot>` | Slot number (e.g., `"12345"`) |
| `<hex root>` | Block root as hex string |

---

## 1. Beacon -- State Queries

### getGenesis

Retrieve details of the chain's genesis which can be used to identify chain.

```
GET /eth/v1/beacon/genesis
```

**Parameters:** None

**Response (200):**

```json
{
  "data": {
    "genesis_time": "1590832934",
    "genesis_validators_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
    "genesis_fork_version": "0x00000000"
  }
}
```

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `genesis_time` | string | Unix time in seconds at which the Eth2.0 chain began |
| `genesis_validators_root` | string (hex, 32 bytes) | Root hash of genesis validators |
| `genesis_fork_version` | string (hex, 4 bytes) | Fork version number |

---

### getStateRoot

Calculates HashTreeRoot for state with given `stateId`. If `stateId` is root, same value will be returned.

```
GET /eth/v1/beacon/states/{state_id}/root
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier (`"head"`, `"genesis"`, `"finalized"`, `"justified"`, slot, or state root) |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": {
    "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
  }
}
```

---

### getStateFork

Returns Fork object for state with given `stateId`.

```
GET /eth/v1/beacon/states/{state_id}/fork
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": {
    "previous_version": "0x00000000",
    "current_version": "0x00000000",
    "epoch": "1"
  }
}
```

---

### getStateFinalityCheckpoints

Returns finality checkpoints for state with given `stateId`. If finality is not yet achieved, checkpoint returns epoch 0 and ZERO_HASH as root.

```
GET /eth/v1/beacon/states/{state_id}/finality_checkpoints
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": {
    "previous_justified": {
      "epoch": "1",
      "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
    },
    "current_justified": {
      "epoch": "1",
      "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
    },
    "finalized": {
      "epoch": "1",
      "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
    }
  }
}
```

---

### getStateValidators

Returns filterable list of validators with their balance, status, and index.

```
GET /eth/v1/beacon/states/{state_id}/validators
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier |

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | array[string] | No | Validator public keys (hex, 48 bytes with 0x prefix) or validator indices. Max 30 items. |
| `status` | array[string] | No | Filter by validator status. Values: `pending_initialized`, `pending_queued`, `active_ongoing`, `active_exiting`, `active_slashed`, `exited_unslashed`, `exited_slashed`, `withdrawal_possible`, `withdrawal_done`. Also accepts: `active`, `pending`, `exited`, `withdrawal`. |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": [
    {
      "index": "1",
      "balance": "32000000000",
      "status": "active_ongoing",
      "validator": {
        "pubkey": "0x93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a",
        "withdrawal_credentials": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
        "effective_balance": "32000000000",
        "slashed": false,
        "activation_eligibility_epoch": "1",
        "activation_epoch": "1",
        "exit_epoch": "18446744073709551615",
        "withdrawable_epoch": "18446744073709551615"
      }
    }
  ]
}
```

**Validator statuses:**

| Status | Description |
|--------|-------------|
| `pending_initialized` | First deposit processed, but not enough funds or not end of first epoch |
| `pending_queued` | Waiting to get activated, has enough funds, in queue |
| `active_ongoing` | Must be attesting, has not initiated any exit |
| `active_exiting` | Still active, but filed voluntary request to exit |
| `active_slashed` | Still active, but slashed and scheduled to exit |
| `exited_unslashed` | Reached exit epoch, not slashed, cannot withdraw yet |
| `exited_slashed` | Reached exit epoch, was slashed, longer withdrawal period |
| `withdrawal_possible` | After exit, permitted to move funds |
| `withdrawal_done` | Funds have been moved away |

---

### getStateValidator

Returns validator specified by state and id or public key along with status and balance.

```
GET /eth/v1/beacon/states/{state_id}/validators/{validator_id}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier |
| `validator_id` | string | Yes | Hex encoded public key (bytes48 with 0x prefix) or validator index |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": {
    "index": "1",
    "balance": "32000000000",
    "status": "active_ongoing",
    "validator": {
      "pubkey": "0x93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a",
      "withdrawal_credentials": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
      "effective_balance": "32000000000",
      "slashed": false,
      "activation_eligibility_epoch": "1",
      "activation_epoch": "1",
      "exit_epoch": "18446744073709551615",
      "withdrawable_epoch": "18446744073709551615"
    }
  }
}
```

---

### getStateValidatorBalances

Returns filterable list of validator balances.

```
GET /eth/v1/beacon/states/{state_id}/validator_balances
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier |

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | array[string] | No | Hex encoded public keys or validator indices. Max 30 items. |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": [
    {
      "index": "1",
      "balance": "32000000000"
    }
  ]
}
```

---

### getEpochCommittees

Retrieves the committees for the given state.

```
GET /eth/v1/beacon/states/{state_id}/committees
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier |

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `epoch` | string | No | Fetch committees for the given epoch. Defaults to epoch of the state. |
| `index` | string | No | Restrict to matching committee index |
| `slot` | string | No | Restrict to matching slot |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": [
    {
      "index": "1",
      "slot": "1",
      "validators": ["1", "2", "3"]
    }
  ]
}
```

---

### getEpochSyncCommittees

Retrieves the sync committees for the given state.

```
GET /eth/v1/beacon/states/{state_id}/sync_committees
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier |

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `epoch` | string | No | Fetch sync committees for the given epoch. Defaults to epoch of the state. |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": {
    "validators": ["1", "2", "3"],
    "validator_aggregates": [
      ["1", "2"],
      ["3", "4"]
    ]
  }
}
```

---

## 2. Beacon -- Block Queries

### getBlockHeaders

Retrieves block headers matching given query. By default fetches current head slot blocks.

```
GET /eth/v1/beacon/headers
```

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `slot` | string | No | Slot number |
| `parent_root` | string | No | Parent root hex string (0x-prefixed, 32 bytes) |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": [
    {
      "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
      "canonical": true,
      "header": {
        "message": {
          "slot": "1",
          "proposer_index": "1",
          "parent_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
          "state_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
          "body_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
        },
        "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505"
      }
    }
  ]
}
```

---

### getBlockHeader

Retrieves block header for given block id.

```
GET /eth/v1/beacon/headers/{block_id}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `block_id` | string | Yes | Block identifier (`"head"`, `"genesis"`, `"finalized"`, slot, or block root) |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": {
    "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
    "canonical": true,
    "header": {
      "message": {
        "slot": "1",
        "proposer_index": "1",
        "parent_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
        "state_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
        "body_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
      },
      "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505"
    }
  }
}
```

---

### publishBlock

Publish a signed beacon block to the beacon network.

```
POST /eth/v1/beacon/blocks
```

**Request body:** `SignedBeaconBlock` object (JSON or SSZ)

**Responses:**

| Code | Description |
|------|-------------|
| 200 | Block validated and broadcast |
| 202 | Block broadcast but failed validation |
| 400 | Invalid block |
| 500 | Internal error |

---

### publishBlindedBlock

Publish a signed blinded beacon block. The node constructs the full `SignedBeaconBlock` by swapping `transactions_root` for the full list of transactions.

```
POST /eth/v1/beacon/blinded_blocks
```

**Request body:** `SignedBlindedBeaconBlock` object (JSON or SSZ)

**Responses:**

| Code | Description |
|------|-------------|
| 200 | Block validated and broadcast |
| 202 | Block broadcast but failed validation |
| 400 | Invalid block |
| 500 | Internal error |

---

### getBlockV2

Retrieves block details for given block id. Supports JSON and SSZ response formats.

```
GET /eth/v2/beacon/blocks/{block_id}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `block_id` | string | Yes | Block identifier |

**Response headers:**

| Name | Description |
|------|-------------|
| `Eth-Consensus-Version` | Block version: `phase0`, `altair`, or `bellatrix` |

**Response (200):**

```json
{
  "version": "phase0",
  "execution_optimistic": false,
  "data": {
    "message": {
      "slot": "1",
      "proposer_index": "1",
      "parent_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
      "state_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
      "body": { "..." : "..." }
    },
    "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505"
  }
}
```

---

### getBlockRoot

Retrieves hashTreeRoot of BeaconBlock/BeaconBlockHeader.

```
GET /eth/v1/beacon/blocks/{block_id}/root
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `block_id` | string | Yes | Block identifier |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": {
    "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
  }
}
```

---

### getBlockAttestations

Retrieves attestations included in requested block.

```
GET /eth/v1/beacon/blocks/{block_id}/attestations
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `block_id` | string | Yes | Block identifier |

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": [
    {
      "aggregation_bits": "0x01",
      "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505",
      "data": {
        "slot": "1",
        "index": "1",
        "beacon_block_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
        "source": {
          "epoch": "1",
          "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
        },
        "target": {
          "epoch": "1",
          "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
        }
      }
    }
  ]
}
```

---

## 3. Beacon -- Pool (GET)

### getPoolAttestations

Retrieves attestations known by the node but not necessarily incorporated into any block.

```
GET /eth/v1/beacon/pool/attestations
```

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `slot` | string | No | Filter by slot |
| `committee_index` | string | No | Filter by committee index |

**Response (200):**

```json
{
  "data": [
    {
      "aggregation_bits": "0x01",
      "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505",
      "data": {
        "slot": "1",
        "index": "1",
        "beacon_block_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
        "source": { "epoch": "1", "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2" },
        "target": { "epoch": "1", "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2" }
      }
    }
  ]
}
```

---

### getPoolAttesterSlashings

Retrieves attester slashings known by the node but not necessarily incorporated into any block.

```
GET /eth/v1/beacon/pool/attester_slashings
```

**Parameters:** None

**Response (200):**

```json
{
  "data": [
    {
      "attestation_1": {
        "attesting_indices": ["1"],
        "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505",
        "data": {
          "slot": "1",
          "index": "1",
          "beacon_block_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
          "source": { "epoch": "1", "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2" },
          "target": { "epoch": "1", "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2" }
        }
      },
      "attestation_2": { "..." : "..." }
    }
  ]
}
```

---

### getPoolProposerSlashings

Retrieves proposer slashings known by the node but not necessarily incorporated into any block.

```
GET /eth/v1/beacon/pool/proposer_slashings
```

**Parameters:** None

**Response (200):**

```json
{
  "data": [
    {
      "signed_header_1": {
        "message": {
          "slot": "1",
          "proposer_index": "1",
          "parent_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
          "state_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
          "body_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
        },
        "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505"
      },
      "signed_header_2": { "..." : "..." }
    }
  ]
}
```

---

### getPoolVoluntaryExits

Retrieves voluntary exits known by the node but not necessarily incorporated into any block.

```
GET /eth/v1/beacon/pool/voluntary_exits
```

**Parameters:** None

**Response (200):**

```json
{
  "data": [
    {
      "message": {
        "epoch": "1",
        "validator_index": "1"
      },
      "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505"
    }
  ]
}
```

---

## 4. Beacon -- Pool (POST)

### submitPoolAttestations

Submits Attestation objects to the node. Each attestation is processed individually. Successfully validated attestations are published on the appropriate subnet.

```
POST /eth/v1/beacon/pool/attestations
```

**Request body:** Array of `Attestation` objects

**Responses:** 200 (success), 400 (one or more attestations failed validation)

---

### submitPoolAttesterSlashings

Submits AttesterSlashing object to node's pool. If valid, node broadcasts to network.

```
POST /eth/v1/beacon/pool/attester_slashings
```

**Request body:** `AttesterSlashing` object

**Responses:** 200 (success), 400 (invalid slashing)

---

### submitPoolProposerSlashings

Submits ProposerSlashing object to node's pool. If valid, node broadcasts to network.

```
POST /eth/v1/beacon/pool/proposer_slashings
```

**Request body:** `ProposerSlashing` object

**Responses:** 200 (success), 400 (invalid slashing)

---

### submitPoolVoluntaryExit

Submits SignedVoluntaryExit object to node's pool. If valid, node broadcasts to network.

```
POST /eth/v1/beacon/pool/voluntary_exits
```

**Request body:** `SignedVoluntaryExit` object

**Responses:** 200 (success), 400 (invalid voluntary exit)

---

### submitPoolSyncCommitteeSignatures

Submits sync committee signature objects to the node. Valid signatures are published on all applicable subnets. Required for Altair networks (not present in phase0).

```
POST /eth/v1/beacon/pool/sync_committees
```

**Request body:** Array of `SyncCommitteeMessage` objects

**Responses:** 200 (success), 400 (one or more signatures failed validation)

---

## 5. Validator -- Duties

### getAttesterDuties

Requests the beacon node to provide a set of attestation duties for validators in a particular epoch.

```
POST /eth/v1/validator/duties/attester/{epoch}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `epoch` | string | Yes | Should only be allowed 1 epoch ahead |

**Request body:** JSON array of validator indices (strings)

```json
["1", "2", "3"]
```

**Response (200):**

```json
{
  "dependent_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
  "execution_optimistic": false,
  "data": [
    {
      "pubkey": "0x93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a",
      "validator_index": "1",
      "committee_index": "1",
      "committee_length": "1",
      "committees_at_slot": "1",
      "validator_committee_index": "1",
      "slot": "1"
    }
  ]
}
```

---

### getProposerDuties

Request beacon node to provide all validators scheduled to propose a block in the given epoch.

```
GET /eth/v1/validator/duties/proposer/{epoch}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `epoch` | string | Yes | Epoch number |

**Response (200):**

```json
{
  "dependent_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
  "execution_optimistic": false,
  "data": [
    {
      "pubkey": "0x93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a",
      "validator_index": "1",
      "slot": "1"
    }
  ]
}
```

---

### getSyncCommitteeDuties

Requests the beacon node to provide a set of sync committee duties for a particular epoch.

```
POST /eth/v1/validator/duties/sync/{epoch}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `epoch` | string | Yes | Must satisfy: `epoch // EPOCHS_PER_SYNC_COMMITTEE_PERIOD <= current_epoch // EPOCHS_PER_SYNC_COMMITTEE_PERIOD + 1` |

**Request body:** JSON array of validator indices (strings)

```json
["1", "2", "3"]
```

**Response (200):**

```json
{
  "execution_optimistic": false,
  "data": [
    {
      "pubkey": "0x93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a",
      "validator_index": "1",
      "validator_sync_committee_indices": ["0", "1"]
    }
  ]
}
```

---

## 6. Validator -- Block Production

### produceBlock (deprecated)

Requests a beacon node to produce a valid block (phase0 only). Use `produceBlockV2` instead.

```
GET /eth/v1/validator/blocks/{slot}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `slot` | string | Yes | The slot for which the block should be proposed |

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `randao_reveal` | string (hex, 96 bytes) | Yes | The validator's randao reveal value |
| `graffiti` | string (hex, 32 bytes) | No | Arbitrary data validator wants to include |

---

### produceBlockV2

Requests a beacon node to produce a valid block, which can then be signed by a validator. Supports all fork versions.

```
GET /eth/v2/validator/blocks/{slot}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `slot` | string | Yes | The slot for which the block should be proposed |

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `randao_reveal` | string (hex, 96 bytes) | Yes | The validator's randao reveal value |
| `graffiti` | string (hex, 32 bytes) | No | Arbitrary data validator wants to include |

**Response headers:**

| Name | Description |
|------|-------------|
| `Eth-Consensus-Version` | Block version: `phase0`, `altair`, or `bellatrix` |

**Response (200):** Unsigned `BeaconBlock` object

---

### produceBlindedBlock

Requests a beacon node to produce a valid blinded block (transactions root only, no full transactions list). Pre-Bellatrix returns a regular `BeaconBlock`.

```
GET /eth/v1/validator/blinded_blocks/{slot}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `slot` | string | Yes | The slot for which the block should be proposed |

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `randao_reveal` | string (hex, 96 bytes) | Yes | The validator's randao reveal value |
| `graffiti` | string (hex, 32 bytes) | No | Arbitrary data validator wants to include |

**Response (200):** Unsigned `BlindedBeaconBlock` object

---

## 7. Validator -- Attestation

### produceAttestationData

Requests that the beacon node produce an AttestationData.

```
GET /eth/v1/validator/attestation_data
```

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `slot` | string | Yes | The slot for which attestation data should be created |
| `committee_index` | string | Yes | The committee index for which attestation data should be created |

**Response (200):**

```json
{
  "data": {
    "slot": "1",
    "index": "1",
    "beacon_block_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
    "source": {
      "epoch": "1",
      "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
    },
    "target": {
      "epoch": "1",
      "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
    }
  }
}
```

---

### getAggregatedAttestation

Aggregates all attestations matching given attestation data root and slot.

```
GET /eth/v1/validator/aggregate_attestation
```

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `attestation_data_root` | string (hex, 32 bytes) | Yes | HashTreeRoot of AttestationData that validator wants aggregated |
| `slot` | string | Yes | Slot number |

**Response (200):** Aggregated `Attestation` object with same `AttestationData` root.

```json
{
  "data": {
    "aggregation_bits": "0x01",
    "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505",
    "data": {
      "slot": "1",
      "index": "1",
      "beacon_block_root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
      "source": { "epoch": "1", "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2" },
      "target": { "epoch": "1", "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2" }
    }
  }
}
```

---

## 8. Validator -- Sync Committee

### produceSyncCommitteeContribution

Requests that the beacon node produce a sync committee contribution.

```
GET /eth/v1/validator/sync_committee_contribution
```

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `slot` | string | Yes | The slot for which a sync committee contribution should be created |
| `subcommittee_index` | string | Yes | The subcommittee index for which to produce the contribution |
| `beacon_block_root` | string (hex, 32 bytes) | Yes | Block root at the slot |

**Response (200):** `SyncCommitteeContribution` object

---

## 9. Validator -- Subscriptions and Registration

### prepareBeaconCommitteeSubnet

Signal beacon node to prepare for a committee subnet. The node will search for peers on the subnet. If the validator is an aggregator, the node will announce subnet subscription and aggregate attestations.

```
POST /eth/v1/validator/beacon_committee_subscriptions
```

**Request body:** Array of subscription objects:

```json
[
  {
    "validator_index": "1",
    "committee_index": "1",
    "committees_at_slot": "1",
    "slot": "1",
    "is_aggregator": true
  }
]
```

**Responses:** 200 (success), 400 (invalid request), 500 (internal error)

---

### prepareSyncCommitteeSubnets

Subscribe to a number of sync committee subnets. Required for Altair networks when the validator client has an active validator in an active sync committee.

```
POST /eth/v1/validator/sync_committee_subscriptions
```

**Request body:** Array of subscription objects:

```json
[
  {
    "validator_index": "1",
    "sync_committee_indices": ["0", "1"],
    "until_epoch": "1"
  }
]
```

**Responses:** 200 (success), 400 (invalid request), 500 (internal error)

---

### prepareBeaconProposer

Provide beacon node with proposals for the given validators. Supplies fee recipient information required when proposing blocks. Information persists through the call epoch plus two additional epochs.

```
POST /eth/v1/validator/prepare_beacon_proposer
```

**Request body:** Array of proposer preparation objects:

```json
[
  {
    "validator_index": "1",
    "fee_recipient": "0xabcf8e0d4e9587369b2301d0790347320302cc09"
  }
]
```

**Responses:** 200 (success), 400 (invalid request)

---

### registerValidator

Provide beacon node with registrations for validators to the external builder network. Sends information to the builder network for MEV-boost block building.

```
POST /eth/v1/validator/register_validator
```

**Request body:** Array of `SignedValidatorRegistration` objects:

```json
[
  {
    "message": {
      "fee_recipient": "0xabcf8e0d4e9587369b2301d0790347320302cc09",
      "gas_limit": "30000000",
      "timestamp": "1234567890",
      "pubkey": "0x93247f2209abcacf57b75a51dafae777f9dd38bc7053d1af526f220a7489a6d3a2753e5f3e8b1cfe39b56f43611df74a"
    },
    "signature": "0x1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505cc411d61252fb6cb3fa0017b679f8bb2305b26a285fa2737f175668d0dff91cc1b66ac1fb663c9bc59509846d6ec05345bd908eda73e670af888da41af171505"
  }
]
```

**Responses:** 200 (success), 400 (invalid registration)

---

## 10. Validator -- Publishing

### publishAggregateAndProofs

Verifies given aggregate and proofs and publishes them on appropriate gossipsub topic.

```
POST /eth/v1/validator/aggregate_and_proofs
```

**Request body:** Array of `SignedAggregateAndProof` objects

**Responses:** 200 (success), 400 (validation failed)

---

### publishContributionAndProofs

Publish multiple signed sync committee contribution and proofs.

```
POST /eth/v1/validator/contribution_and_proofs
```

**Request body:** Array of `SignedContributionAndProof` objects

**Responses:** 200 (success), 400 (validation failed)

---

## 11. Node

### getNetworkIdentity

Retrieves data about the node's network presence.

```
GET /eth/v1/node/identity
```

**Parameters:** None

**Response (200):**

```json
{
  "data": {
    "peer_id": "QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7DWjhx5N",
    "enr": "enr:-IS4QHCYrYZbAKWCBRlAy5zzaDZXJBGkcnh4MHcBFZntXNFrdvJjX04jRzjzCBOonrkTfj499SZuOh8R33Ls8RRcy5wBgmlkgnY0gmlwhH8AAAGJc2VjcDI1NmsxoQPKY0yuDUmstAHYpMa2_oxVtw0RW_QAdpzBQA8yWM0xOIN1ZHCCdl8",
    "p2p_addresses": ["/ip4/127.0.0.1/tcp/9000/p2p/QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7DWjhx5N"],
    "discovery_addresses": ["/ip4/127.0.0.1/udp/9000"],
    "metadata": {
      "seq_number": "1",
      "attnets": "0x0000000000000000"
    }
  }
}
```

---

### getPeers

Retrieves data about the node's network peers.

```
GET /eth/v1/node/peers
```

**Query parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state` | array[string] | No | Filter by peer state: `disconnected`, `connecting`, `connected`, `disconnecting` |
| `direction` | array[string] | No | Filter by connection direction: `inbound`, `outbound` |

**Response (200):**

```json
{
  "data": [
    {
      "peer_id": "QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7DWjhx5N",
      "enr": "enr:...",
      "last_seen_p2p_address": "/ip4/127.0.0.1/tcp/9000",
      "state": "connected",
      "direction": "inbound"
    }
  ]
}
```

---

### getPeer

Retrieves data about a specific peer.

```
GET /eth/v1/node/peers/{peer_id}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `peer_id` | string | Yes | Cryptographic hash of a peer's public key (libp2p peer ID) |

**Response (200):** Single peer data object (same structure as getPeers item)

---

### getPeerCount

Retrieves number of known peers.

```
GET /eth/v1/node/peer_count
```

**Parameters:** None

**Response (200):**

```json
{
  "data": {
    "disconnected": "1",
    "connecting": "2",
    "connected": "3",
    "disconnecting": "0"
  }
}
```

---

### getSyncingStatus

Requests the beacon node to describe if it's currently syncing or not.

```
GET /eth/v1/node/syncing
```

**Parameters:** None

**Response (200):**

```json
{
  "data": {
    "head_slot": "1",
    "sync_distance": "1",
    "is_syncing": true,
    "is_optimistic": false
  }
}
```

---

### getNodeVersion

Requests that the beacon node identify information about its implementation (similar to HTTP User-Agent).

```
GET /eth/v1/node/version
```

**Parameters:** None

**Response (200):**

```json
{
  "data": {
    "version": "Lighthouse/v2.1.1-b0ac3464/x86_64-linux"
  }
}
```

---

### getHealth

Returns node health status in HTTP status codes. Useful for load balancers.

```
GET /eth/v1/node/health
```

**Parameters:** None

**Responses:**

| Code | Description |
|------|-------------|
| 200 | Node is ready |
| 206 | Node is syncing but can serve incomplete data |
| 503 | Node not initialized or having issues |

---

## 12. Config

### getSpec

Retrieve specification configuration used on this node. Includes constants, presets, and configuration for all hard forks. Values starting with 0x are returned as hex strings; numeric values are returned as quoted integers.

```
GET /eth/v1/config/spec
```

**Parameters:** None

**Response (200):**

```json
{
  "data": {
    "MAX_COMMITTEES_PER_SLOT": "64",
    "TARGET_COMMITTEE_SIZE": "128",
    "MAX_VALIDATORS_PER_COMMITTEE": "2048",
    "SLOTS_PER_EPOCH": "32",
    "SECONDS_PER_SLOT": "12",
    "EPOCHS_PER_SYNC_COMMITTEE_PERIOD": "256",
    "DEPOSIT_CONTRACT_ADDRESS": "0x00000000219ab540356cBB839Cbe05303d7705Fa",
    "..." : "..."
  }
}
```

---

### getDepositContract

Retrieve Eth1 deposit contract address and chain ID.

```
GET /eth/v1/config/deposit_contract
```

**Parameters:** None

**Response (200):**

```json
{
  "data": {
    "chain_id": "1",
    "address": "0x00000000219ab540356cBB839Cbe05303d7705Fa"
  }
}
```

---

### getForkSchedule

Retrieve all forks, past present and future, of which this node is aware.

```
GET /eth/v1/config/fork_schedule
```

**Parameters:** None

**Response (200):**

```json
{
  "data": [
    {
      "previous_version": "0x00000000",
      "current_version": "0x01000000",
      "epoch": "74240"
    }
  ]
}
```

---

## 13. Debug

### getState (deprecated)

Returns full BeaconState object for given stateId. Use `getStateV2` instead.

```
GET /eth/v1/debug/beacon/states/{state_id}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier |

**Response (200):** Full `BeaconState` object (JSON or SSZ)

---

### getStateV2

Returns full BeaconState object for given stateId. Supports JSON and SSZ response formats.

```
GET /eth/v2/debug/beacon/states/{state_id}
```

**Path parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `state_id` | string | Yes | State identifier |

**Response headers:**

| Name | Description |
|------|-------------|
| `Eth-Consensus-Version` | State version: `phase0`, `altair`, or `bellatrix` |

**Response (200):** Full `BeaconState` object with `version` field

---

### getDebugChainHeads (deprecated)

Retrieves all possible chain heads (leaves of fork choice tree). Use `getDebugChainHeadsV2` instead.

```
GET /eth/v1/debug/beacon/heads
```

**Parameters:** None

**Response (200):**

```json
{
  "data": [
    {
      "slot": "1",
      "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2"
    }
  ]
}
```

---

### getDebugChainHeadsV2

Retrieves all possible chain heads (leaves of fork choice tree).

```
GET /eth/v2/debug/beacon/heads
```

**Parameters:** None

**Response (200):**

```json
{
  "data": [
    {
      "slot": "1",
      "root": "0xcf8e0d4e9587369b2301d0790347320302cc0943d5a1884560367e8208d920f2",
      "execution_optimistic": false
    }
  ]
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "code": 400,
  "message": "Invalid state ID: current",
  "stacktraces": []
}
```

Common HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 202 | Accepted (broadcast successful, validation pending) |
| 206 | Partial content (node syncing) |
| 400 | Invalid request parameters |
| 404 | Resource not found |
| 500 | Beacon node internal error |
| 503 | Service unavailable |

---

## Code Examples

### Query Genesis Info

```javascript
const BEACON_URL = `https://eth2-beacon-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`;

const response = await fetch(`${BEACON_URL}/eth/v1/beacon/genesis`);
const { data } = await response.json();
console.log("Genesis time:", data.genesis_time);
console.log("Genesis validators root:", data.genesis_validators_root);
console.log("Genesis fork version:", data.genesis_fork_version);
```

### Get Validator Info

```javascript
const BEACON_URL = `https://eth2-beacon-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`;

const response = await fetch(
  `${BEACON_URL}/eth/v1/beacon/states/head/validators?id=0,1,2&status=active_ongoing`
);
const { data } = await response.json();
data.forEach(v => {
  console.log(`Validator ${v.index}: ${v.status}, Balance: ${v.balance} gwei`);
  console.log(`  Pubkey: ${v.validator.pubkey}`);
  console.log(`  Effective balance: ${v.validator.effective_balance}`);
  console.log(`  Slashed: ${v.validator.slashed}`);
});
```

### Get Block Header

```javascript
const BEACON_URL = `https://eth2-beacon-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`;

const response = await fetch(`${BEACON_URL}/eth/v1/beacon/headers/head`);
const { data } = await response.json();
console.log("Slot:", data.header.message.slot);
console.log("Proposer:", data.header.message.proposer_index);
console.log("Block root:", data.root);
```

### Get Attester Duties

```javascript
const BEACON_URL = `https://eth2-beacon-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`;

const response = await fetch(`${BEACON_URL}/eth/v1/validator/duties/attester/100`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(["0", "1", "2"])
});
const { data, dependent_root } = await response.json();
data.forEach(duty => {
  console.log(`Validator ${duty.validator_index}: slot ${duty.slot}, committee ${duty.committee_index}`);
});
```

### Check Sync Status

```javascript
const BEACON_URL = `https://eth2-beacon-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`;

const response = await fetch(`${BEACON_URL}/eth/v1/node/syncing`);
const { data } = await response.json();
if (data.is_syncing) {
  console.log(`Syncing... Head slot: ${data.head_slot}, Distance: ${data.sync_distance}`);
} else {
  console.log(`Fully synced at slot ${data.head_slot}`);
}
```

### Get Finality Checkpoints

```javascript
const BEACON_URL = `https://eth2-beacon-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`;

const response = await fetch(`${BEACON_URL}/eth/v1/beacon/states/head/finality_checkpoints`);
const { data } = await response.json();
console.log("Finalized epoch:", data.finalized.epoch);
console.log("Justified epoch:", data.current_justified.epoch);
console.log("Previous justified epoch:", data.previous_justified.epoch);
```

---

## Quick Reference Table

### Beacon State Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| GET | `/eth/v1/beacon/genesis` | Get genesis details | getgenesis-1.md |
| GET | `/eth/v1/beacon/states/{state_id}/root` | Get state SSZ HashTreeRoot | getstateroot-1.md |
| GET | `/eth/v1/beacon/states/{state_id}/fork` | Get fork object for state | getstatefork-1.md |
| GET | `/eth/v1/beacon/states/{state_id}/finality_checkpoints` | Get finality checkpoints | getstatefinalitycheckpoints-1.md |
| GET | `/eth/v1/beacon/states/{state_id}/validators` | Get validators from state | getstatevalidators-1.md |
| GET | `/eth/v1/beacon/states/{state_id}/validators/{validator_id}` | Get specific validator | getstatevalidator-1.md |
| GET | `/eth/v1/beacon/states/{state_id}/validator_balances` | Get validator balances | getstatevalidatorbalances-1.md |
| GET | `/eth/v1/beacon/states/{state_id}/committees` | Get epoch committees | getepochcommittees-1.md |
| GET | `/eth/v1/beacon/states/{state_id}/sync_committees` | Get sync committees | getepochsynccommittees-1.md |

### Beacon Block Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| GET | `/eth/v1/beacon/headers` | Get block headers | getblockheaders-1.md |
| GET | `/eth/v1/beacon/headers/{block_id}` | Get specific block header | getblockheader-1.md |
| GET | `/eth/v2/beacon/blocks/{block_id}` | Get full block (v2) | getblockv2-1.md |
| GET | `/eth/v1/beacon/blocks/{block_id}/root` | Get block root | getblockroot-1.md |
| GET | `/eth/v1/beacon/blocks/{block_id}/attestations` | Get block attestations | getblockattestations-1.md |
| POST | `/eth/v1/beacon/blocks` | Publish signed block | publishblock-1.md |
| POST | `/eth/v1/beacon/blinded_blocks` | Publish signed blinded block | publishblindedblock-1.md |

### Beacon Pool Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| GET | `/eth/v1/beacon/pool/attestations` | Get pool attestations | getpoolattestations-1.md |
| POST | `/eth/v1/beacon/pool/attestations` | Submit attestations | submitpoolattestations-1.md |
| GET | `/eth/v1/beacon/pool/attester_slashings` | Get attester slashings | getpoolattesterslashings-1.md |
| POST | `/eth/v1/beacon/pool/attester_slashings` | Submit attester slashing | submitpoolattesterslashings-1.md |
| GET | `/eth/v1/beacon/pool/proposer_slashings` | Get proposer slashings | getpoolproposerslashings-1.md |
| POST | `/eth/v1/beacon/pool/proposer_slashings` | Submit proposer slashing | submitpoolproposerslashings-1.md |
| GET | `/eth/v1/beacon/pool/voluntary_exits` | Get voluntary exits | getpoolvoluntaryexits-1.md |
| POST | `/eth/v1/beacon/pool/voluntary_exits` | Submit voluntary exit | submitpoolvoluntaryexit-1.md |
| POST | `/eth/v1/beacon/pool/sync_committees` | Submit sync committee signatures | submitpoolsynccommitteesignatures-1.md |

### Validator Duty Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| POST | `/eth/v1/validator/duties/attester/{epoch}` | Get attester duties | getattesterduties.md |
| GET | `/eth/v1/validator/duties/proposer/{epoch}` | Get proposer duties | getproposerduties.md |
| POST | `/eth/v1/validator/duties/sync/{epoch}` | Get sync committee duties | getsynccommitteeduties.md |

### Validator Block Production Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| GET | `/eth/v1/validator/blocks/{slot}` | Produce block (deprecated) | produceblock.md |
| GET | `/eth/v2/validator/blocks/{slot}` | Produce block v2 | produceblockv2.md |
| GET | `/eth/v1/validator/blinded_blocks/{slot}` | Produce blinded block | produceblindedblock.md |

### Validator Attestation and Sync Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| GET | `/eth/v1/validator/attestation_data` | Produce attestation data | produceattestationdata.md |
| GET | `/eth/v1/validator/aggregate_attestation` | Get aggregated attestation | getaggregatedattestation.md |
| POST | `/eth/v1/validator/aggregate_and_proofs` | Publish aggregate and proofs | publishaggregateandproofs.md |
| GET | `/eth/v1/validator/sync_committee_contribution` | Produce sync committee contribution | producesynccommitteecontribution.md |
| POST | `/eth/v1/validator/contribution_and_proofs` | Publish contribution and proofs | publishcontributionandproofs.md |

### Validator Subscription and Registration Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| POST | `/eth/v1/validator/beacon_committee_subscriptions` | Subscribe to committee subnets | preparebeaconcommitteesubnet.md |
| POST | `/eth/v1/validator/sync_committee_subscriptions` | Subscribe to sync committee subnets | preparesynccommitteesubnets.md |
| POST | `/eth/v1/validator/prepare_beacon_proposer` | Prepare beacon proposer | preparebeaconproposer.md |
| POST | `/eth/v1/validator/register_validator` | Register validator with builder network | registervalidator.md |

### Node Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| GET | `/eth/v1/node/identity` | Get node network identity | getnetworkidentity.md |
| GET | `/eth/v1/node/peers` | Get connected peers | getpeers.md |
| GET | `/eth/v1/node/peers/{peer_id}` | Get specific peer | getpeer.md |
| GET | `/eth/v1/node/peer_count` | Get peer count | getpeercount.md |
| GET | `/eth/v1/node/syncing` | Get sync status | getsyncingstatus.md |
| GET | `/eth/v1/node/version` | Get node version | getnodeversion.md |
| GET | `/eth/v1/node/health` | Get node health | gethealth.md |

### Config Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| GET | `/eth/v1/config/spec` | Get chain specification | getspec.md |
| GET | `/eth/v1/config/deposit_contract` | Get deposit contract info | getdepositcontract.md |
| GET | `/eth/v1/config/fork_schedule` | Get fork schedule | getforkschedule.md |

### Debug Endpoints

| Method | Path | Description | Source |
|--------|------|-------------|--------|
| GET | `/eth/v1/debug/beacon/states/{state_id}` | Get full beacon state (deprecated) | getstate-1.md |
| GET | `/eth/v2/debug/beacon/states/{state_id}` | Get full beacon state v2 | getstatev2-1.md |
| GET | `/eth/v1/debug/beacon/heads` | Get fork choice heads (deprecated) | getdebugchainheads-1.md |
| GET | `/eth/v2/debug/beacon/heads` | Get fork choice heads v2 | getdebugchainheadsv2-1.md |

---

## Use Cases

- **Staking monitoring:** Track validator performance, balances, and duties via state and validator endpoints
- **Consensus analysis:** Monitor finality checkpoints, fork choice, and chain health
- **Block production:** Track proposer duties, produce blocks, and publish signed blocks
- **Attestation workflow:** Produce attestation data, aggregate attestations, and publish proofs
- **Sync committee participation:** Get sync committee duties, produce contributions, and subscribe to subnets
- **Infrastructure health:** Monitor node sync status, peer connectivity, and node version
- **MEV-boost integration:** Register validators with builder network for blinded block production
