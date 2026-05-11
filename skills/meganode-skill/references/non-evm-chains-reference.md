# Non-EVM Chains API Reference

## Overview

MegaNode supports several non-EVM blockchain networks, each with their own API protocols. This reference covers Aptos, NEAR, and Avalanche C-Chain APIs available through MegaNode.

> **Klaytn** (54+ klay_* methods) is documented in [klaytn-reference.md](klaytn-reference.md).

---

## Table of Contents

1. [Aptos Node API](#aptos-node-api) -- REST API for Aptos blockchain
2. [NEAR RPC](#near-rpc) -- JSON-RPC access for NEAR
3. [Avalanche C-Chain (AVAX API)](#avalanche-c-chain-avax-api) -- EVM and AVAX-specific methods
4. [Notes](#notes) -- Usage notes and caveats

---

## Aptos Node API

Aptos is a proof-of-stake Layer 1 blockchain utilizing the Move programming language. NodeReal provides REST API services for the Aptos network and is one of the top Validators.

**Supported Networks:**
- Aptos Mainnet
- Aptos Testnet

**API Endpoint:**
```
https://aptos-mainnet.nodereal.io/v1/{apiKey}/v1
https://aptos-testnet.nodereal.io/v1/{apiKey}/v1
```

**Protocol:** REST API (not JSON-RPC)

### General Endpoints

#### Get Ledger Info

Get the latest ledger information, including chain ID, role type, ledger versions, epoch, etc.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /` |
| Category | General |
| Operation ID | `get_ledger_info` |

**Response fields:** `chain_id` (uint8), `epoch` (string/uint64), `ledger_version` (string/uint64), `oldest_ledger_version` (string/uint64), `ledger_timestamp` (string/uint64), `node_role` ("validator" or "full_node"), `oldest_block_height` (string/uint64), `block_height` (string/uint64)

**Response headers:** `X-APTOS-CHAIN-ID`, `X-APTOS-LEDGER-VERSION`, `X-APTOS-LEDGER-OLDEST-VERSION`, `X-APTOS-LEDGER-TIMESTAMPUSEC`, `X-APTOS-EPOCH`, `X-APTOS-BLOCK-HEIGHT`, `X-APTOS-OLDEST-BLOCK-HEIGHT`

**Example:**
```bash
curl https://aptos-mainnet.nodereal.io/v1/{apiKey}/v1/
```

---

#### Check Basic Node Health

By default checks that it can get the latest ledger info and returns 200. If `duration_secs` is provided, returns 200 only if ledger timestamp is within that threshold.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /-/healthy` |
| Category | General |
| Operation ID | `healthy` |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| duration_secs | uint32 | No | Threshold in seconds that the server can be behind to be considered healthy |

**Example:**
```bash
curl https://aptos-mainnet.nodereal.io/v1/{apiKey}/v1/-/healthy?duration_secs=30
```

---

### Account Endpoints

#### Get Account

Retrieves high level information about an account such as its sequence number and authentication key. Returns 404 if the account does not exist.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /accounts/{address}` |
| Category | Accounts |
| Operation ID | `get_account` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| address | hex string | Yes | Address with or without `0x` prefix |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ledger_version | string/uint64 | No | Ledger version to get state of account. If not provided, uses latest. |

**Response fields:** `sequence_number` (string/uint64), `authentication_key` (hex string)

**Example:**
```bash
curl https://aptos-mainnet.nodereal.io/v1/{apiKey}/v1/accounts/0x1
```

---

#### Get Account Resources

Retrieves all account resources for a given account and a specific ledger version. If the requested ledger version has been pruned, the server responds with 410.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /accounts/{address}/resources` |
| Category | Accounts |
| Operation ID | `get_account_resources` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| address | hex string | Yes | Address with or without `0x` prefix |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ledger_version | string/uint64 | No | Ledger version. If not provided, uses latest. |

**Response:** Array of `MoveResource` objects, each with `type` (MoveStructTag) and `data` (MoveStructValue)

**Example:**
```bash
curl https://aptos-mainnet.nodereal.io/v1/{apiKey}/v1/accounts/0x1/resources
```

---

#### Get Account Resource

Retrieves an individual resource from a given account.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /accounts/{address}/resource/{resource_type}` |
| Category | Accounts |
| Operation ID | `get_account_resource` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| address | hex string | Yes | Address with or without `0x` prefix |
| resource_type | MoveStructTag | Yes | Name of struct, e.g. `0x1::account::Account` |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ledger_version | string/uint64 | No | Ledger version. If not provided, uses latest. |

**Example:**
```bash
curl https://aptos-mainnet.nodereal.io/v1/{apiKey}/v1/accounts/0x1/resource/0x1::account::Account
```

---

#### Get Account Modules

Retrieves all account modules' bytecode for a given account.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /accounts/{address}/modules` |
| Category | Accounts |
| Operation ID | `get_account_modules` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| address | hex string | Yes | Address with or without `0x` prefix |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| ledger_version | string/uint64 | No | Ledger version. If not provided, uses latest. |

**Response:** Array of `MoveModuleBytecode` objects with `bytecode` (hex) and `abi` (MoveModule)

---

#### Get Account Module

Retrieves an individual module from a given account.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /accounts/{address}/module/{module_name}` |
| Category | Accounts |
| Operation ID | `get_account_module` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| address | hex string | Yes | Address with or without `0x` prefix |
| module_name | string | Yes | Name of module to retrieve, e.g. `coin` |

---

#### Get Account Transactions

Retrieves transactions from an account. If the start version is too far in the past, a 410 will be returned.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /accounts/{address}/transactions` |
| Category | Transactions |
| Operation ID | `get_account_transactions` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| address | hex string | Yes | Address with or without `0x` prefix |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | string/uint64 | No | Ledger version to start list of transactions. Default is 0. |
| limit | integer/uint16 | No | Max number of transactions to retrieve. Default is 25. |

---

### Block Endpoints

#### Get Block by Height

Get the transactions in a block and the corresponding block information.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /blocks/by_height/{block_height}` |
| Category | Blocks |
| Operation ID | `get_block_by_height` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| block_height | uint64 | Yes | Block height to look up |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| with_transactions | boolean | No | Include transactions in the response. Default false. |

---

#### Get Block by Version

Get the block containing a given version.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /blocks/by_version/{version}` |
| Category | Blocks |
| Operation ID | `get_block_by_version` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| version | uint64 | Yes | Ledger version to look up block |

---

### Transaction Endpoints

#### Get Transactions

Retrieve on-chain committed transactions with pagination.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /transactions` |
| Category | Transactions |
| Operation ID | `get_transactions` |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | string/uint64 | No | Ledger version to start listing |
| limit | integer/uint16 | No | Max number of transactions. Default 25. |

---

#### Get Transaction by Hash

Look up a transaction by its hash.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /transactions/by_hash/{txn_hash}` |
| Category | Transactions |
| Operation ID | `get_transaction_by_hash` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| txn_hash | hex string | Yes | Hash of the transaction |

---

#### Get Transaction by Version

Look up a transaction by its version (ledger version).

| Detail | Value |
|--------|-------|
| Endpoint | `GET /transactions/by_version/{txn_version}` |
| Category | Transactions |
| Operation ID | `get_transaction_by_version` |

---

#### Submit Transaction

Submit a signed transaction to the network. Accepts JSON or BCS format.

| Detail | Value |
|--------|-------|
| Endpoint | `POST /transactions` |
| Category | Transactions |
| Operation ID | `submit_transaction` |

**Content-Type:** `application/json` for JSON format, `application/x.aptos.signed_transaction+bcs` for BCS format

---

#### Submit Batch Transactions

Submit multiple transactions in a single batch request.

| Detail | Value |
|--------|-------|
| Endpoint | `POST /transactions/batch` |
| Category | Transactions |
| Operation ID | `submit_batch_transactions` |

---

#### Simulate Transaction

Simulates a transaction without committing it. Returns exact transaction outputs and events. Useful for estimating maximum gas units.

| Detail | Value |
|--------|-------|
| Endpoint | `POST /transactions/simulate` |
| Category | Transactions |
| Operation ID | `simulate_transaction` |

---

#### Encode Submission

Encodes a `UserTransactionRequest` as BCS for signing. Useful for languages without BCS support.

| Detail | Value |
|--------|-------|
| Endpoint | `POST /transactions/encode_submission` |
| Category | Transactions |
| Operation ID | `encode_submission` |

---

#### Estimate Gas Price

Returns the estimated gas price based on the median of the last 100,000 transactions.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /estimate_gas_price` |
| Category | Transactions |
| Operation ID | `estimate_gas_price` |

---

### Event Endpoints

#### Get Events by Event Handle

Uses account address, event handle, and field name to return events matching that event type.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /accounts/{address}/events/{event_handle}/{field_name}` |
| Category | Events |
| Operation ID | `get_events_by_event_handle` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| address | hex string | Yes | Account address |
| event_handle | MoveStructTag | Yes | Event handle struct name, e.g. `0x1::account::Account` |
| field_name | string | Yes | Name of the field in the event handle struct, e.g. `coin_register_events` |

---

#### Get Events by Creation Number

Returns events for an account by creation number.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /accounts/{address}/events/{creation_number}` |
| Category | Events |
| Operation ID | `get_events_by_creation_number` |

---

#### Get Events by Event Key

Returns events by event key.

| Detail | Value |
|--------|-------|
| Endpoint | `GET /events/{event_key}` |
| Category | Events |
| Operation ID | `get_events_by_event_key` |

---

### Table Endpoints

#### Get Table Item

Get a table item by its key at a specific ledger version.

| Detail | Value |
|--------|-------|
| Endpoint | `POST /tables/{table_handle}/item` |
| Category | Tables |
| Operation ID | `get_table_item` |

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| table_handle | hex string | Yes | Table handle hex encoded 32-byte string |

**Request Body (TableItemRequest):** `key_type` (MoveType), `value_type` (MoveType), `key` (value matching key_type)

---

### Aptos Complete Endpoint Index

| Endpoint | Method | Category | Description |
|----------|--------|----------|-------------|
| `/` | GET | General | Get ledger info |
| `/-/healthy` | GET | General | Check node health |
| `/accounts/{address}` | GET | Accounts | Get account info |
| `/accounts/{address}/resources` | GET | Accounts | Get all account resources |
| `/accounts/{address}/resource/{resource_type}` | GET | Accounts | Get specific resource |
| `/accounts/{address}/modules` | GET | Accounts | Get all account modules |
| `/accounts/{address}/module/{module_name}` | GET | Accounts | Get specific module |
| `/accounts/{address}/transactions` | GET | Transactions | Get account transactions |
| `/blocks/by_height/{block_height}` | GET | Blocks | Get block by height |
| `/blocks/by_version/{version}` | GET | Blocks | Get block by version |
| `/transactions` | GET | Transactions | List transactions |
| `/transactions/by_hash/{txn_hash}` | GET | Transactions | Get transaction by hash |
| `/transactions/by_version/{txn_version}` | GET | Transactions | Get transaction by version |
| `/transactions` | POST | Transactions | Submit transaction |
| `/transactions/batch` | POST | Transactions | Submit batch transactions |
| `/transactions/simulate` | POST | Transactions | Simulate transaction |
| `/transactions/encode_submission` | POST | Transactions | Encode submission for signing |
| `/estimate_gas_price` | GET | Transactions | Estimate gas price |
| `/accounts/{address}/events/{event_handle}/{field_name}` | GET | Events | Get events by event handle |
| `/accounts/{address}/events/{creation_number}` | GET | Events | Get events by creation number |
| `/events/{event_key}` | GET | Events | Get events by event key |
| `/tables/{table_handle}/item` | POST | Tables | Get table item |

### Using Aptos SDK

```javascript
import { Aptos, AptosConfig, Network } from "@aptos-labs/ts-sdk";

const config = new AptosConfig({
  fullnodeUrl: `https://aptos-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}/v1`,
});
const aptos = new Aptos(config);

const balance = await aptos.getAccountResource({
  accountAddress: "0x1",
  resourceType: "0x1::coin::CoinStore<0x1::aptos_coin::AptosCoin>",
});
```

---

## NEAR RPC

NEAR is a sharded proof-of-stake blockchain. NodeReal provides JSON-RPC 2.0 access to the NEAR network.

**Supported Networks:**
- NEAR Mainnet

**API Endpoint:**
```
https://open-platform.nodereal.io/{apiKey}/near/
```

**Protocol:** JSON-RPC 2.0

### Access Key / Account Query Methods

All query methods use the `query` JSON-RPC method with different `request_type` values.

> **Note:** For all query methods, you can use either `finality` or `block_id` as a parameter, but not both. `finality` can be `"final"` or `"optimistic"`. `block_id` can be a block number (integer) or block hash (string).

---

#### query - view_account

Returns basic information about the account.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| request_type | string | `"view_account"` |
| finality | string | `"final"` or `"optimistic"` (or use `block_id` instead) |
| account_id | string | The account ID |

**Returns:** `amount`, `locked`, `code_hash`, `storage_usage`, `storage_paid_at`, `block_height`, `block_hash`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method": "query","params": {"request_type": "view_account", "finality": "final", "account_id": "prophet.poolv1.near"},"id":1,"jsonrpc":"2.0"}'
```

---

#### query - view_access_key

Returns information about a single access key for a given account.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| request_type | string | `"view_access_key"` |
| finality | string | `"final"` or `"optimistic"` (or use `block_id`) |
| account_id | string | The account ID |
| public_key | string | The public key |

**Returns:** `nonce`, `permission` (FullAccess or FunctionCall with `allowance`, `receiver_id`, `method_names`), `block_height`, `block_hash`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method": "query","params": {"request_type": "view_access_key", "finality": "final", "account_id": "relay.aurora", "public_key": "ed25519:168vdqFUxij2yvsxYgAGoykJMX7tgrPKVCH484A8nHP"},"id":1,"jsonrpc":"2.0"}'
```

---

#### query - view_access_key_list

Queries all the access keys for a given account.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| request_type | string | `"view_access_key_list"` |
| finality | string | `"final"` or `"optimistic"` (or use `block_id`) |
| account_id | string | The account ID |

**Returns:** `keys` (array of `public_key` and `access_key` objects), `block_height`, `block_hash`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method": "query","params": {"request_type": "view_access_key_list", "finality": "final", "account_id": "relay.aurora"},"id":1,"jsonrpc":"2.0"}'
```

---

#### query - view_code

Returns the base64 encoded contract code (Wasm binary) deployed to the account.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| request_type | string | `"view_code"` |
| finality | string | `"final"` or `"optimistic"` (or use `block_id`) |
| account_id | string | The account ID |

**Returns:** `hash`, `block_height`, `block_hash`, `code_base64`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method": "query","params": {"request_type": "view_code", "finality": "final", "account_id": "prophet.poolv1.near"},"id":1,"jsonrpc":"2.0"}'
```

---

#### query - view_state

Returns the contract state (key-value pairs) based on the key prefix encoded in base64.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| request_type | string | `"view_state"` |
| finality | string | `"final"` or `"optimistic"` (or use `block_id`) |
| account_id | string | The account ID |
| prefix_base64 | string | Key prefix encoded in base64 (empty string for all) |

**Returns:** `block_hash`, `block_height`, `proof`, `values` (array of `key`, `value`, `proof`)

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method": "query","params": {"request_type": "view_state", "finality": "final", "account_id": "kiln.poolv1.near", "prefix_base64": ""},"id":1,"jsonrpc":"2.0"}'
```

---

#### query - call_function

Allows calling a contract method as a view function.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| request_type | string | `"call_function"` |
| finality | string | `"final"` or `"optimistic"` (or use `block_id`) |
| account_id | string | The account ID |
| method_name | string | The method name, e.g. `"get_owner_id"` |
| args_base64 | string | Method arguments encoded in base64 |

**Returns:** `block_height`, `block_hash`, `logs`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method": "query","params": {"request_type": "call_function", "finality": "final", "account_id": "account_id", "method_name": "get_account", "args_base64": "e30="},"id":1,"jsonrpc":"2.0"}'
```

---

### Block / Chunk Methods

#### block

Queries block information for the given block height, hash, or finality.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| finality | string | `"final"` or `"optimistic"` (use instead of `block_id`) |
| block_id | int/string | Block number or block hash (use instead of `finality`) |

**Returns:** `author`, `chunks` (array with `chunk_hash`, `gas_limit`, `gas_used`, `shard_id`, etc.), `header` (with `hash`, `height`, `timestamp`, `epoch_id`, `gas_price`, `total_supply`, etc.)

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method": "block","params": {"finality": "final"},"id":1,"jsonrpc":"2.0"}'
```

---

#### chunk

Returns details about a particular chunk. Use a block detail query to obtain a valid chunk hash.

**Parameters (use one of):**

| Name | Type | Description |
|------|------|-------------|
| chunk_id | string | Hash of the chunk |
| block_id + shard_id | int, int | Block ID and shard ID |

**Returns:** `author`, `header` (with `chunk_hash`, `gas_limit`, `gas_used`, `shard_id`, etc.), `transactions` (array), `receipts` (array)

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method": "chunk","params": {"block_id": 80712125, "shard_id": 0},"id":1,"jsonrpc":"2.0"}'
```

---

### Transaction Methods

#### tx

Queries transaction status by hash and returns the final transaction outcome.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| transaction hash | string | Hash of the transaction |
| sender account id | string | Account ID of the sender |

**Returns:** `receipts_outcome`, `status`, `transaction` (with `actions`, `hash`, `nonce`, `public_key`, `receiver_id`, `signer_id`), `transaction_outcome`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc": "2.0", "method": "tx", "params": ["Ce4DPVFyDRdx54iLoSiKA6gqwGnE5V4mTZyVvFDQsvmN","relay.aurora"],"id":1}'
```

---

#### broadcast_tx_async

Sends a transaction and returns the transaction hash immediately (non-blocking).

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| signed transaction | string | Signed transaction encoded in base64 |

**Returns:** Transaction hash

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method":"broadcast_tx_async","params":["DgAAAHNlbmRlci50ZXN0bmV0..."],"id":1,"jsonrpc":"2.0"}'
```

---

#### broadcast_tx_commit

Sends a transaction and waits until the transaction is fully complete (10 second timeout).

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| signed transaction | string | Signed transaction encoded in base64 |

**Returns:** `status`, `transaction`, `transaction_outcome`, `receipts_outcome`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method":"broadcast_tx_commit","params":["signedtransaction base64 encoded"],"id":1,"jsonrpc":"2.0"}'
```

---

### Network / Node Methods

#### status

Returns the current list of validators and node status (sync status, nearcore version, protocol version, etc.).

**Parameters:** None

**Returns:** `chain_id`, `latest_protocol_version`, `node_key`, `protocol_version`, `rpc_addr`, `sync_info` (with `latest_block_hash`, `latest_block_height`, `syncing`, etc.), `validators`, `version`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc": "2.0", "method": "status", "params": [],"id":1}'
```

---

#### validators

Queries active validators on the network.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| block hash or number | string/int/null | Block hash, number, or `[null]` for latest |

**Returns:** `current_proposals`, `current_validators` (with `account_id`, `public_key`, `stake`, `num_produced_blocks`, etc.), `next_validators`, `current_fishermen`, `next_fishermen`, `prev_epoch_kickout`, `epoch_start_height`, `epoch_height`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method": "validators", "params": [null],"id":1,"jsonrpc":"2.0"}'
```

---

#### network_info

Returns the current state of node network connections (active peers, bandwidth, etc.).

**Parameters:** None

**Returns:** `active_peers`, `num_active_peers`, `peer_max_count`, `sent_bytes_per_sec`, `received_bytes_per_sec`, `known_producers`

**Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/near/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc": "2.0", "method": "network_info", "params": [],"id":1}'
```

---

### NEAR Complete Method Index

| Method | Category | Description |
|--------|----------|-------------|
| `query` (view_account) | Accounts | Get account info |
| `query` (view_access_key) | Accounts | Get single access key |
| `query` (view_access_key_list) | Accounts | Get all access keys |
| `query` (view_code) | Accounts | Get contract code |
| `query` (view_state) | Accounts | Get contract state |
| `query` (call_function) | Accounts | Call contract view function |
| `block` | Blocks | Get block by height/hash/finality |
| `chunk` | Blocks | Get chunk details |
| `tx` | Transactions | Get transaction status |
| `broadcast_tx_async` | Transactions | Send transaction (non-blocking) |
| `broadcast_tx_commit` | Transactions | Send transaction (blocking) |
| `status` | Network | Get node status |
| `validators` | Network | Get validator info |
| `network_info` | Network | Get network connections |

---

---

## Avalanche C-Chain (AVAX API)

Avalanche C-Chain supports standard EVM JSON-RPC methods via the RPC endpoint, plus Avalanche-specific `avax.*` methods via the AVAX endpoint.

**Supported Networks:**
- Avalanche C-Chain (mainnet)

**API Endpoints:**
```
https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/rpc    (EVM RPC API)
https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/avax   (AVAX-specific API)
```

**Protocol:** JSON-RPC 2.0

### AVAX-Specific Methods

#### avax.getAtomicTx

Returns the specified atomic (cross-chain) transaction.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| txID | string | Transaction ID |
| encoding | string | (optional) Encoding format, can only be `"hex"` |

**Returns:** `tx` (encoded transaction), `encoding`, `blockHeight`

**Example:**
```bash
curl -X POST https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/avax \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"avax.getAtomicTx",
    "params":{
        "txID":"2GD5SRYJQr2kw5jE73trBFiAgVQyrCaeg223TaTyJFYXf2kPty",
        "encoding": "hex"
    }
}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tx": "0x00000000...",
    "encoding": "hex",
    "blockHeight": "1"
  },
  "id": 1
}
```

---

#### avax.getAtomicTxStatus

Get the status of an atomic transaction sent to the network.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| txID | string | Transaction ID in cb58 format |

**Returns:** `status` (`"Accepted"`, `"Processing"`, `"Rejected"`, or `"Unknown"`), `blockHeight` (when accepted)

**Example:**
```bash
curl -X POST https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/avax \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "avax.getAtomicTxStatus",
    "params": {
        "txID": "2QouvFWUbjuySRxeX5xMbNCuAaKWfbk5FeEa2JmoF85RKLk2dD"
    }
}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": "Accepted",
    "blockHeight": "1"
  }
}
```

---

#### avax.getUTXOs

Get the UTXOs that reference a given address.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| addresses | []string | List of addresses |
| limit | int | (optional) Max UTXOs to return (max 1024) |
| startIndex | object | (optional) Pagination with `address` and `utxo` fields |
| sourceChain | string | Chain ID or alias for imports |
| encoding | string | (optional) Can only be `"hex"` |

**Returns:** `numFetched` (int), `utxos` ([]string), `endIndex` (object with `address` and `utxo`)

**Example:**
```bash
curl -X POST https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/avax \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"avax.getUTXOs",
    "params":{
        "addresses":["C-avax18jma8ppw3nhx5r4ap8clazz0dps7rv5ukulre5"],
        "sourceChain": "X",
        "startIndex": {
            "address": "C-avax18jma8ppw3nhx5r4ap8clazz0dps7rv5ukulre5",
            "utxo": "22RXW7SWjBrrxu2vzDkd8uza7fuEmNpgbj58CxBob9UbP37HSB"
        },
        "encoding": "hex"
    }
}'
```

---

#### avax.issueTx

Send a signed transaction to the network.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| tx | string | Signed transaction |
| encoding | string | (optional) Can only be `"hex"` |

**Returns:** `txID` (string) - The transaction ID

**Example:**
```bash
curl -X POST https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/avax \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "jsonrpc":"2.0",
    "id":1,
    "method":"avax.issueTx",
    "params":{
        "tx":"0x0000000900000...",
        "encoding": "hex"
    }
}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "txID": "NUPLwbt2hsYxpQg4H2o451hmTWQ4JZx2zMzM4SinwtHgAdX1JLPHXvWSXEnpecStLj"
  }
}
```

---

### Avalanche C-Chain Complete Method Index

#### AVAX-Specific Methods (via `/avax` endpoint)

| Method | Description |
|--------|-------------|
| `avax.getAtomicTx` | Get an atomic (cross-chain) transaction |
| `avax.getAtomicTxStatus` | Get status of an atomic transaction |
| `avax.getUTXOs` | Get UTXOs for addresses |
| `avax.issueTx` | Send a signed transaction |

#### EVM-Compatible Methods (via `/rpc` endpoint)
The Avalanche C-Chain also supports standard EVM JSON-RPC methods (`eth_*`) via the RPC endpoint. See the main EVM API reference for those methods.

---

## Notes

- Non-EVM chains do NOT support Enhanced APIs (`nr_` methods)
- Archive node access varies by chain -- check [supported-chains.md](supported-chains.md)
- Each chain has its own SDK ecosystem -- NodeReal endpoints are compatible with standard chain SDKs
- CU costs for non-EVM methods may differ from EVM methods -- check the MegaNode dashboard
- Aptos uses REST API (HTTP GET/POST) while NEAR uses JSON-RPC 2.0
- Avalanche C-Chain has both EVM RPC and AVAX-specific API endpoints
