# Debug & Trace API Reference

## Overview

MegaNode provides Debug and Trace APIs for advanced transaction analysis and smart contract debugging. These are high-CU-cost methods available on Growth tier and above.

**API Endpoint Format:** `https://{chain}-{network}.nodereal.io/v1/{API-key}`

**Supported chain slugs:** `eth-mainnet`, `bsc-mainnet`, `opbnb-mainnet`, `polygon-mainnet`

---

## Table of Contents

1. [Debug Methods](#debug-methods) -- Standard built-in Geth tracers
2. [Debug Pro Methods (JavaScript Tracers)](#debug-pro-methods-javascript-tracers) -- Custom JavaScript tracer support
3. [Trace Methods](#trace-methods) -- Parity-compatible execution analysis
4. [Complete Method Summary](#complete-method-summary) -- All methods and chain support
5. [Chain-Specific Endpoint Examples](#chain-specific-endpoint-examples) -- Endpoint URLs per chain
6. [Tracer Options](#tracer-options) -- Built-in and custom tracers
7. [Troubleshooting](#troubleshooting) -- Common issues and solutions
8. [Documentation](#documentation) -- Official reference links

---

## Debug Methods

Standard debug methods for transaction and block tracing. These use built-in Geth tracers such as `callTracer`, `prestateTracer`, and `4byteTracer`.

---

### `debug_traceTransaction`

Replays any transaction that may have been executed prior to this one before it will finally attempt to execute the transaction that corresponds to the given hash.

**Supported Chains:** ETH, BSC, Polygon, Avalanche C-Chain, Arbitrum One (Nitro)

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `transactionHash` | `string` | Yes | The hash of the transaction to trace |
| `tracer` | `object` | Yes (on most chains) | The tracer configuration object. Set `"tracer": "callTracer"` for call hierarchy, `"prestateTracer"` for pre-execution state, or `"4byteTracer"` for function signatures. Not required on Arbitrum. |

#### Returns (callTracer)

| Field | Type | Description |
|-------|------|-------------|
| `from` | `string` | The address the transaction is sent from |
| `to` | `string` | The address the transaction is directed to |
| `gas` | `string` | The gas provided for the transaction execution (hex) |
| `gasUsed` | `string` | The gas used for the transaction execution (hex) |
| `input` | `string` | The data sent along with the transaction |
| `output` | `string` | The output data |
| `type` | `string` | Type of the transaction (e.g., `CALL`, `STATICCALL`) |
| `value` | `string` | The value transferred in Wei (hex) |
| `calls` | `array` | Nested sub-calls made during execution |
| `error` | `string` | Error message if the transaction reverted |

#### Curl Example

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "debug_traceTransaction",
    "params": [
      "0x34bd3463c504e6188a8549a70973bfdb944a42a16e4ee44cb1467e7843753174",
      {"tracer": "callTracer"}
    ],
    "id": 0
  }'
```

#### Response Example

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "type": "CALL",
        "gas": "0x45844",
        "output": "0x08c379a0...",
        "calls": [
            {
                "input": "0x0902f1ac",
                "output": "0x000000000000000000000000000000000000000000011c6a552be13a04d16ed4...",
                "type": "STATICCALL",
                "from": "0x602af6edcfdd2c23589b9ef1c39f89bc87e01f35",
                "to": "0x524ebbfdbf8ac97bea24f6a142104e5dfaddf49d",
                "gas": "0x42d45",
                "gasUsed": "0xbb1"
            }
        ],
        "from": "0x979d9dd23d71a414eb6aad8b5543f42348315093",
        "to": "0x602af6edcfdd2c23589b9ef1c39f89bc87e01f35",
        "value": "0x0",
        "gasUsed": "0x29d7",
        "input": "0x9aad4418...",
        "error": "execution reverted"
    }
}
```

---

### `debug_traceCall`

Lets you run an `eth_call` within the context of the given block execution using the final state of the parent block as the base.

**Supported Chains:** ETH, BSC, Polygon, Avalanche C-Chain, Arbitrum One (Nitro)

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `object` | `object` | Yes | The transaction call object (see fields below) |
| `blockNumber` | `string` | Yes | The block number in hex format, or `"latest"`, `"earliest"`, `"pending"` |
| `tracer` | `object` | Yes (on most chains) | The tracer configuration object, e.g. `{"tracer": "callTracer"}`. Not required on Arbitrum. |

**Transaction call object fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from` | `string` | No | The address the transaction is sent from |
| `to` | `string` | Yes | The address the transaction is directed to |
| `gas` | `string` | No | The gas provided for the transaction execution (hex) |
| `gasPrice` | `string` | No | The gas price (hex) |
| `value` | `string` | No | The value transferred in Wei (hex) |
| `data` | `string` | No | The data sent along with the transaction |

#### Returns (callTracer)

| Field | Type | Description |
|-------|------|-------------|
| `from` | `string` | The address the transaction is sent from |
| `to` | `string` | The address the transaction is directed to |
| `gas` | `string` | The gas provided for the transaction execution (hex) |
| `gasUsed` | `string` | The gas used (hex) |
| `input` | `string` | The data sent along with the transaction |
| `output` | `string` | The output data |
| `type` | `string` | Type of the transaction |
| `value` | `string` | The value transferred in Wei (hex) |

#### Curl Example

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "debug_traceCall",
    "params": [
      {
        "from": "0x4982085c9e2f89f2ecb8131eca71afad896e89cb",
        "to": "0xce56d6ff4f9c8dbcacc5f848ca8c60ba5469ae70",
        "gas": "0x7148",
        "value": "0x11c37937e08000"
      },
      "latest",
      {"tracer": "callTracer"}
    ],
    "id": 0
  }'
```

#### Response Example

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "type": "CALL",
        "from": "0x4982085c9e2f89f2ecb8131eca71afad896e89cb",
        "to": "0xce56d6ff4f9c8dbcacc5f848ca8c60ba5469ae70",
        "value": "0x11c37937e08000",
        "gas": "0x1f40",
        "gasUsed": "0x0",
        "input": "0x",
        "output": "0x"
    }
}
```

> **Note:** On Arbitrum One (Nitro), the tracer parameter is not required. The response format differs -- it returns `structLogs` instead of callTracer output:
> ```json
> {
>     "jsonrpc": "2.0",
>     "id": 1,
>     "result": {
>         "gas": 22182,
>         "failed": false,
>         "returnValue": "",
>         "structLogs": []
>     }
> }
> ```

---

### `debug_traceBlockByNumber`

Replays all transactions that were included in the block identified by block number.

**Supported Chains:** ETH, BSC, Polygon, Avalanche C-Chain, Arbitrum One (Nitro)

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `blockNumber` | `string` | Yes | The block number in hex format, or `"latest"`, `"earliest"`, `"pending"` |
| `tracer` | `object` | Yes (on most chains) | The tracer configuration object, e.g. `{"tracer": "callTracer"}`. Not required on Arbitrum. |

#### Returns

An array of trace objects, one per transaction in the block. Each trace object contains:

| Field | Type | Description |
|-------|------|-------------|
| `result` | `object` | Trace result with `from`, `to`, `gas`, `gasUsed`, `input`, `output`, `type`, `value`, and optionally `calls` |

#### Curl Example

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "debug_traceBlockByNumber",
    "params": [
      "0x1233174",
      {"tracer": "callTracer"}
    ],
    "id": 0
  }'
```

#### Response Example

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": [
        {
            "result": {
                "type": "CALL",
                "from": "0x4982085c9e2f89f2ecb8131eca71afad896e89cb",
                "to": "0xce56d6ff4f9c8dbcacc5f848ca8c60ba5469ae70",
                "value": "0x11c37937e08000",
                "gas": "0x7148",
                "gasUsed": "0x0",
                "input": "0x",
                "output": "0x"
            }
        },
        {
            "result": {
                "type": "CALL",
                "from": "0x66a1777e55b416c56ad8f2a4bfeef9c2695328b9",
                "to": "0xe9e7cea3dedca5984780bafc599bd69add087d56",
                "value": "0x0",
                "gas": "0x7f3a",
                "gasUsed": "0x3887",
                "input": "0xa9059cbb...",
                "output": "0x0000000000000000000000000000000000000000000000000000000000000001"
            }
        }
    ]
}
```

---

### `debug_traceBlockByHash`

Replays all transactions that were included in the block identified by block hash.

**Supported Chains:** ETH, BSC, Polygon, Avalanche C-Chain, Arbitrum One (Nitro)

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `blockHash` | `string` | Yes | The block hash |
| `tracer` | `object` | Yes (on most chains) | The tracer configuration object, e.g. `{"tracer": "callTracer"}`. Not required on Arbitrum. |

#### Returns

Same structure as `debug_traceBlockByNumber` -- an array of trace objects, one per transaction in the block.

#### Curl Example

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "debug_traceBlockByHash",
    "params": [
      "0x97b49e43632ac70c46b4003434058b18db0ad809617bd29f3448d46ca9085576",
      {"tracer": "callTracer"}
    ],
    "id": 1
  }'
```

#### Response Example

Same format as `debug_traceBlockByNumber`. See above.

---

## Debug Pro Methods (JavaScript Tracers)

Compared with traditional debug API, the Debug Pro API supports customized JavaScript tracers. These methods allow writing custom JavaScript tracer logic for advanced analysis. All Debug Pro methods use the `debug_jstrace*` prefix.

---

### `debug_jstraceTransaction`

Replays any transaction that may have been executed prior to this one before it will finally attempt to execute the transaction that corresponds to the given hash. Supports customized JavaScript tracers.

**Supported Chains:** BSC, ETH, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `transactionHash` | `string` | Yes | The hash of the transaction |
| `tracer` | `object` | Yes | The tracer configuration. Supports built-in tracers like `"callTracer"` or custom JavaScript tracer strings. |

#### Returns (callTracer)

| Field | Type | Description |
|-------|------|-------------|
| `from` | `string` | The address the transaction is sent from |
| `to` | `string` | The address the transaction is directed to |
| `gas` | `string` | The gas provided for the transaction execution (hex) |
| `gasUsed` | `string` | The gas used (hex) |
| `input` | `string` | The data sent along with the transaction |
| `output` | `string` | The output data |
| `type` | `string` | Type of the transaction |
| `value` | `string` | The value transferred in Wei (hex) |
| `calls` | `array` | Nested sub-calls made during execution |
| `error` | `string` | Error message if the transaction reverted |

#### Curl Example

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "debug_jstraceTransaction",
    "params": [
      "0x34bd3463c504e6188a8549a70973bfdb944a42a16e4ee44cb1467e7843753174",
      {"tracer": "callTracer"}
    ],
    "id": 0
  }'
```

#### Response Example

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "type": "CALL",
        "gas": "0x45844",
        "output": "0x08c379a0...",
        "calls": [
            {
                "input": "0x0902f1ac",
                "output": "0x000000000000000000000000000000000000000000011c6a552be13a04d16ed4...",
                "type": "STATICCALL",
                "from": "0x602af6edcfdd2c23589b9ef1c39f89bc87e01f35",
                "to": "0x524ebbfdbf8ac97bea24f6a142104e5dfaddf49d",
                "gas": "0x42d45",
                "gasUsed": "0xbb1"
            }
        ],
        "from": "0x979d9dd23d71a414eb6aad8b5543f42348315093",
        "to": "0x602af6edcfdd2c23589b9ef1c39f89bc87e01f35",
        "value": "0x0",
        "gasUsed": "0x29d7",
        "input": "0x9aad4418...",
        "error": "execution reverted"
    }
}
```

---

### `debug_jstraceCall`

Lets you run an `eth_call` within the context of the given block execution using the final state of the parent block as the base. Supports customized JavaScript tracers.

**Supported Chains:** BSC, ETH, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `object` | `object` | No | The transaction call object (see `debug_traceCall` for field details) |
| `blockNumber` | `string` | Yes | The block number in hex format, or `"latest"` |
| `tracer` | `object` | Yes | The tracer configuration object |

#### Returns (callTracer)

Same structure as `debug_jstraceTransaction`.

#### Curl Example

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "debug_jstraceCall",
    "params": [
      {
        "from": "0x4982085c9e2f89f2ecb8131eca71afad896e89cb",
        "to": "0xce56d6ff4f9c8dbcacc5f848ca8c60ba5469ae70",
        "gas": "0x7148",
        "value": "0x11c37937e08000"
      },
      "latest",
      {"tracer": "callTracer"}
    ],
    "id": 0
  }'
```

#### Response Example

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "type": "CALL",
        "from": "0x4982085c9e2f89f2ecb8131eca71afad896e89cb",
        "to": "0xce56d6ff4f9c8dbcacc5f848ca8c60ba5469ae70",
        "value": "0x11c37937e08000",
        "gas": "0x1f40",
        "gasUsed": "0x0",
        "input": "0x",
        "output": "0x"
    }
}
```

---

### `debug_jstraceBlockByNumber`

Replays all transactions that were included in a block by block number. Supports customized JavaScript tracers.

**Supported Chains:** BSC, ETH, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `blockNumber` | `string` | Yes | The block number in hex format |
| `tracer` | `object` | Yes | The tracer configuration object |

#### Returns

An array of trace result objects, one per transaction in the block.

#### Curl Example

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "debug_jstraceBlockByNumber",
    "params": [
      "0x1233174",
      {"tracer": "callTracer"}
    ],
    "id": 0
  }'
```

#### Response Example

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": [
        {
            "result": {
                "type": "CALL",
                "from": "0x4982085c9e2f89f2ecb8131eca71afad896e89cb",
                "to": "0xce56d6ff4f9c8dbcacc5f848ca8c60ba5469ae70",
                "value": "0x11c37937e08000",
                "gas": "0x7148",
                "gasUsed": "0x0",
                "input": "0x",
                "output": "0x"
            }
        },
        {
            "result": {
                "type": "CALL",
                "from": "0x66a1777e55b416c56ad8f2a4bfeef9c2695328b9",
                "to": "0xe9e7cea3dedca5984780bafc599bd69add087d56",
                "value": "0x0",
                "gas": "0x7f3a",
                "gasUsed": "0x3887",
                "input": "0xa9059cbb...",
                "output": "0x0000000000000000000000000000000000000000000000000000000000000001"
            }
        }
    ]
}
```

---

### `debug_jstraceBlockByHash`

Replays all transactions that were included in a block by block hash. Supports customized JavaScript tracers.

**Supported Chains:** BSC, ETH, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `blockHash` | `string` | Yes | The block hash |
| `tracer` | `object` | Yes | The tracer configuration object |

#### Returns

Same structure as `debug_jstraceBlockByNumber` -- an array of trace result objects.

#### Curl Example

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "debug_jstraceBlockByHash",
    "params": [
      "0xcb1e9e529fddcfdad8c4d43eabf8264d55d13305105cf760dfdae166ddc42046",
      {"tracer": "callTracer"}
    ],
    "id": 0
  }'
```

#### Response Example

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": [
        {
            "result": {
                "from": "0x4982085c9e2f89f2ecb8131eca71afad896e89cb",
                "to": "0xce56d6ff4f9c8dbcacc5f848ca8c60ba5469ae70",
                "value": "0x11c37937e08000",
                "gas": "0x7148",
                "gasUsed": "0x0",
                "input": "0x",
                "output": "0x",
                "type": "CALL"
            }
        },
        {
            "result": {
                "gas": "0x7f3a",
                "gasUsed": "0x3887",
                "input": "0xa9059cbb...",
                "output": "0x0000000000000000000000000000000000000000000000000000000000000001",
                "type": "CALL",
                "from": "0x66a1777e55b416c56ad8f2a4bfeef9c2695328b9",
                "to": "0xe9e7cea3dedca5984780bafc599bd69add087d56",
                "value": "0x0"
            }
        }
    ]
}
```

---

## Trace Methods

OpenEthereum/Parity-compatible trace methods for detailed execution analysis. These return structured trace data following the Parity trace format.

---

### `trace_block`

Returns traces created at a given block.

**Supported Chains:** ETH, BSC, opBNB, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `blockNumber` | `string` | Yes | Integer of a block number (hex), or `"earliest"`, `"latest"`, `"pending"` |

#### Returns

An array of trace objects with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `action` | `object` | The ParityTrace object (see below) |
| `blockHash` | `string` | The hash of the block where this transaction was in |
| `blockNumber` | `integer` | The block number |
| `result` | `object` | Contains `gasUsed` and `output` |
| `subtraces` | `integer` | Number of sub-calls made by the transaction |
| `traceAddress` | `array` | List of indices into the call tree |
| `transactionHash` | `string` | The hash of the transaction |
| `transactionPosition` | `integer` | The transaction position in the block |
| `type` | `string` | The type of action (e.g., `call`, `create`) |

**ParityTrace action object:**

| Field | Type | Description |
|-------|------|-------------|
| `from` | `string` | The address of the sender |
| `callType` | `string` | The type of method (e.g., `call`, `delegatecall`) |
| `gas` | `string` | The gas provided by the sender (hex) |
| `input` | `string` | The data sent along with the transaction |
| `to` | `string` | The address of the receiver |
| `value` | `string` | The value sent with this transaction (hex) |

#### Curl Example

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "method": "trace_block",
    "params": ["0x2ed119"],
    "id": 1,
    "jsonrpc": "2.0"
  }'
```

#### Response Example

```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "action": {
        "callType": "call",
        "from": "0xaa7b131dc60b80d3cf5e59b5a21a666aa039c951",
        "gas": "0x0",
        "input": "0x",
        "to": "0xd40aba8166a212d6892125f079c33e6f5ca19814",
        "value": "0x4768d7effc3fbe"
      },
      "blockHash": "0x7eb25504e4c202cf3d62fd585d3e238f592c780cca82dacb2ed3cb5b38883add",
      "blockNumber": 3068185,
      "result": {
        "gasUsed": "0x0",
        "output": "0x"
      },
      "subtraces": 0,
      "traceAddress": [],
      "transactionHash": "0x07da28d752aba3b9dd7060005e554719c6205c8a3aea358599fc9b245c52f1f6",
      "transactionPosition": 0,
      "type": "call"
    },
    {
      "action": {
        "callType": "call",
        "from": "0x4f11ba23bb526c0486d83c6a8f18f632f3fc172a",
        "gas": "0x0",
        "input": "0x",
        "to": "0x7ed1e469fcb3ee19c0366d829e291451be638e59",
        "value": "0x446cde325fbfbe"
      },
      "blockHash": "0x7eb25504e4c202cf3d62fd585d3e238f592c780cca82dacb2ed3cb5b38883add",
      "blockNumber": 3068185,
      "result": {
        "gasUsed": "0x0",
        "output": "0x"
      },
      "subtraces": 0,
      "traceAddress": [],
      "transactionHash": "0x056f11efb5da4ff7cf8523cfcef08393e5dd2ff3ab3223e4324426d285d7ae92",
      "transactionPosition": 1,
      "type": "call"
    }
  ],
  "id": 0
}
```

---

### `trace_transaction`

Returns all traces of a given transaction.

**Supported Chains:** ETH, BSC, opBNB, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `hash` | `string` | Yes | The hash of the transaction |

#### Returns

An array of Parity trace objects (same structure as `trace_block` results).

#### Curl Example

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "method": "trace_transaction",
    "params": ["0x17104ac9d3312d8c136b7f44d4b8b47852618065ebfa534bd2d3b5ef218ca1f3"],
    "id": 1,
    "jsonrpc": "2.0"
  }'
```

#### Response Example

```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "action": {
        "callType": "call",
        "from": "0x83806d539d4ea1c140489a06660319c9a303f874",
        "gas": "0x1a1f8",
        "input": "0x",
        "to": "0x1c39ba39e4735cb65978d4db400ddd70a72dc750",
        "value": "0x7a16c911b4d00000"
      },
      "blockHash": "0x7eb25504e4c202cf3d62fd585d3e238f592c780cca82dacb2ed3cb5b38883add",
      "blockNumber": 3068185,
      "result": {
        "gasUsed": "0x2982",
        "output": "0x"
      },
      "subtraces": 2,
      "traceAddress": [],
      "transactionHash": "0x17104ac9d3312d8c136b7f44d4b8b47852618065ebfa534bd2d3b5ef218ca1f3",
      "transactionPosition": 2,
      "type": "call"
    },
    {
      "action": {
        "callType": "call",
        "from": "0x1c39ba39e4735cb65978d4db400ddd70a72dc750",
        "gas": "0x13e99",
        "input": "0x16c72721",
        "to": "0x2bd2326c993dfaef84f696526064ff22eba5b362",
        "value": "0x0"
      },
      "blockHash": "0x7eb25504e4c202cf3d62fd585d3e238f592c780cca82dacb2ed3cb5b38883add",
      "blockNumber": 3068185,
      "result": {
        "gasUsed": "0x183",
        "output": "0x0000000000000000000000000000000000000000000000000000000000000001"
      },
      "subtraces": 0,
      "traceAddress": [0],
      "transactionHash": "0x17104ac9d3312d8c136b7f44d4b8b47852618065ebfa534bd2d3b5ef218ca1f3",
      "transactionPosition": 2,
      "type": "call"
    },
    {
      "action": {
        "callType": "call",
        "from": "0x1c39ba39e4735cb65978d4db400ddd70a72dc750",
        "gas": "0x8fc",
        "input": "0x",
        "to": "0x70faa28a6b8d6829a4b1e649d26ec9a2a39ba413",
        "value": "0x7a16c911b4d00000"
      },
      "blockHash": "0x7eb25504e4c202cf3d62fd585d3e238f592c780cca82dacb2ed3cb5b38883add",
      "blockNumber": 3068185,
      "result": {
        "gasUsed": "0x0",
        "output": "0x"
      },
      "subtraces": 0,
      "traceAddress": [1],
      "transactionHash": "0x17104ac9d3312d8c136b7f44d4b8b47852618065ebfa534bd2d3b5ef218ca1f3",
      "transactionPosition": 2,
      "type": "call"
    }
  ],
  "id": 0
}
```

---

### `trace_call`

Executes the given call and returns a number of possible traces for it.

**Supported Chains:** ETH, BSC, opBNB, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `object` | `object` | Yes | Call options, same as `eth_call` (see fields below) |
| `traceType` | `array` | Yes | Array of trace types: `"trace"`, `"stateDiff"` |
| `blockNumber` | `string` | No | Block number (hex) or `"latest"`, `"earliest"` |

**Call object fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from` | `string` | No | 20 bytes -- the address the transaction is sent from |
| `to` | `string` | No | 20 bytes -- the address the transaction is directed to (optional when creating new contract) |
| `gas` | `string` | No | The gas provided for the transaction execution (hex) |
| `gasPrice` | `string` | No | The gas price used for each paid gas (hex) |
| `value` | `string` | No | The value sent with this transaction (hex) |
| `data` | `string` | No | 4-byte hash of the method signature followed by encoded parameters |

#### Returns

| Field | Type | Description |
|-------|------|-------------|
| `output` | `string` | The output data (hex) |
| `stateDiff` | `object` | Information on altered Ethereum state (if requested) |
| `trace` | `array` | Array of trace objects with `action`, `result`, `subtraces`, `traceAddress`, `type` |
| `vmTrace` | `object` | VM-level trace (null unless requested) |

#### Curl Example

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "method": "trace_call",
    "params": [
      {
        "from": null,
        "to": "0x6b175474e89094c44da98b954eedeac495271d0f",
        "data": "0x70a082310000000000000000000000006E0d01A76C3Cf4288372a29124A26D4353EE51BE"
      },
      ["trace"],
      "latest"
    ],
    "id": 1,
    "jsonrpc": "2.0"
  }'
```

#### Response Example

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "output": "0x0000000000000000000000000000000000000000000000000858898f93629000",
    "stateDiff": null,
    "trace": [
      {
        "action": {
          "from": "0x0000000000000000000000000000000000000000",
          "callType": "call",
          "gas": "0x2fa9cc8",
          "input": "0x70a082310000000000000000000000006e0d01a76c3cf4288372a29124a26d4353ee51be",
          "to": "0x6b175474e89094c44da98b954eedeac495271d0f",
          "value": "0x0"
        },
        "result": {
          "gasUsed": "0xa2a",
          "output": "0x0000000000000000000000000000000000000000000000000858898f93629000"
        },
        "subtraces": 0,
        "traceAddress": [],
        "type": "call"
      }
    ],
    "vmTrace": null
  }
}
```

---

### `trace_get`

Returns the trace at the given position within a transaction.

**Supported Chains:** ETH, BSC, opBNB, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `hash` | `string` | Yes | Transaction hash |
| `indices` | `array` | Yes | Array of index positions of the traces (e.g., `["0x0"]`) |

#### Returns

A single Parity trace object.

#### Curl Example

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "method": "trace_get",
    "params": [
      "0x17104ac9d3312d8c136b7f44d4b8b47852618065ebfa534bd2d3b5ef218ca1f3",
      ["0x0"]
    ],
    "id": 1,
    "jsonrpc": "2.0"
  }'
```

#### Response Example

```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "result": {
    "action": {
      "callType": "call",
      "from": "0x1c39ba39e4735cb65978d4db400ddd70a72dc750",
      "gas": "0x13e99",
      "input": "0x16c72721",
      "to": "0x2bd2326c993dfaef84f696526064ff22eba5b362",
      "value": "0x0"
    },
    "blockHash": "0x7eb25504e4c202cf3d62fd585d3e238f592c780cca82dacb2ed3cb5b38883add",
    "blockNumber": 3068185,
    "result": {
      "gasUsed": "0x183",
      "output": "0x0000000000000000000000000000000000000000000000000000000000000001"
    },
    "subtraces": 0,
    "traceAddress": [0],
    "transactionHash": "0x17104ac9d3312d8c136b7f44d4b8b47852618065ebfa534bd2d3b5ef218ca1f3",
    "transactionPosition": 2,
    "type": "call"
  }
}
```

---

### `trace_filter`

Returns traces matching a given filter criteria.

**Supported Chains:** ETH, BSC, opBNB, Polygon

#### Parameters

A single `object` parameter with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fromBlock` | `string` | No | Starting block number (hex) or tag |
| `toBlock` | `string` | No | Ending block number (hex) or tag |
| `fromAddress` | `array` | No | Array of sender addresses to filter |
| `toAddress` | `array` | No | Array of receiver addresses to filter |
| `after` | `integer` | No | The offset trace number |
| `count` | `integer` | No | Number of traces to return in a batch |
| `mode` | `string` | No | `"union"` or `"intersection"` |

#### Returns

An array of Parity trace objects (same structure as `trace_block`).

#### Curl Example

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "method": "trace_filter",
    "params": [
      {
        "fromBlock": "0xc26f54",
        "toBlock": "0xc26f54"
      }
    ],
    "id": 1,
    "jsonrpc": "2.0"
  }'
```

#### Response Example

```json
{
    "jsonrpc": "2.0",
    "result": [
        {
            "action": {
                "callType": "call",
                "from": "0x15dce17509846b420b1f5c158fe3d7518204abb6",
                "gas": "0xed2a4",
                "input": "0x00000000...",
                "to": "0x000000000000abe945c436595ce765a8a261317b",
                "value": "0x0"
            },
            "blockHash": "0xe0583a364c20fa67748ca92e276df63919c67e12fdc9bdbc17deae8cf730cf35",
            "blockNumber": 12742484,
            "result": {
                "gasUsed": "0x4551d",
                "output": "0x00000000000000000000000000000000000000000000000000d96b96f61c5e87"
            },
            "subtraces": 12,
            "traceAddress": [],
            "transactionHash": "0x87951d0547018db2c4817282a53e2015d91934b42d1b8d8bba1bef7cb480f263",
            "transactionPosition": 0,
            "type": "call"
        }
    ]
}
```

---

### `trace_replayTransaction`

Traces a call to `eth_sendRawTransaction` without making the call, returning the traces. Replays a specific transaction with tracing enabled.

**Supported Chains:** ETH, BSC, opBNB, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `hash` | `string` | Yes | The hash of the transaction |
| `traceType` | `array` | Yes | Array of trace types: `"trace"`, `"stateDiff"` |

#### Returns

| Field | Type | Description |
|-------|------|-------------|
| `output` | `string` | The output data (hex) |
| `stateDiff` | `object` | Information on altered Ethereum state (null if not requested) |
| `trace` | `array` | Array of trace objects with `action`, `result`, `subtraces`, `traceAddress`, `type` |
| `vmTrace` | `object` | VM-level trace (null unless requested) |

#### Curl Example

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "method": "trace_replayTransaction",
    "params": [
      "0x02d4a872e096445e80d05276ee756cefef7f3b376bcec14246469c0cd97dad8f",
      ["trace"]
    ],
    "id": 1,
    "jsonrpc": "2.0"
  }'
```

#### Response Example

```json
{
  "jsonrpc": "2.0",
  "result": {
    "output": "0x",
    "stateDiff": null,
    "trace": [
      {
        "action": {
          "callType": "call",
          "from": "0x00a63d34051602b2cb268ea344d4b8bc4767f2d4",
          "gas": "0x0",
          "input": "0x",
          "to": "0x87cc0d78ee64a9f11b5affdd9ea523872eae14e4",
          "value": "0x810e988a393f2000"
        },
        "result": {
          "gasUsed": "0x0",
          "output": "0x"
        },
        "subtraces": 0,
        "traceAddress": [],
        "type": "call"
      }
    ],
    "vmTrace": null
  },
  "id": 0
}
```

---

### `trace_replayBlockTransactions`

Replays all transactions in a block returning the requested traces for each transaction.

**Supported Chains:** ETH, BSC, opBNB, Polygon

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `blockNumber` | `string` | Yes | Integer of a block number (hex), or `"earliest"`, `"latest"`, `"pending"` |
| `traceType` | `array` | Yes | Array of trace types: `"trace"`, `"stateDiff"` |

#### Returns

An array of trace results, one per transaction. Each element has:

| Field | Type | Description |
|-------|------|-------------|
| `output` | `string` | The output data (hex) |
| `stateDiff` | `object` | State diff (null if not requested) |
| `trace` | `array` | Array of trace objects |
| `transactionHash` | `string` | The transaction hash |
| `vmTrace` | `object` | VM trace (null unless requested) |

#### Curl Example

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "method": "trace_replayBlockTransactions",
    "params": [
      "0x2ed119",
      ["trace"]
    ],
    "id": 1,
    "jsonrpc": "2.0"
  }'
```

#### Response Example

```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "output": "0x",
      "stateDiff": null,
      "trace": [
        {
          "action": {
            "callType": "call",
            "from": "0xaa7b131dc60b80d3cf5e59b5a21a666aa039c951",
            "gas": "0x0",
            "input": "0x",
            "to": "0xd40aba8166a212d6892125f079c33e6f5ca19814",
            "value": "0x4768d7effc3fbe"
          },
          "result": {
            "gasUsed": "0x0",
            "output": "0x"
          },
          "subtraces": 0,
          "traceAddress": [],
          "type": "call"
        }
      ],
      "transactionHash": "0x07da28d752aba3b9dd7060005e554719c6205c8a3aea358599fc9b245c52f1f6",
      "vmTrace": null
    },
    {
      "output": "0x",
      "stateDiff": null,
      "trace": [
        {
          "action": {
            "callType": "call",
            "from": "0x4f11ba23bb526c0486d83c6a8f18f632f3fc172a",
            "gas": "0x0",
            "input": "0x",
            "to": "0x7ed1e469fcb3ee19c0366d829e291451be638e59",
            "value": "0x446cde325fbfbe"
          },
          "result": {
            "gasUsed": "0x0",
            "output": "0x"
          },
          "subtraces": 0,
          "traceAddress": [],
          "type": "call"
        }
      ],
      "transactionHash": "0x056f11efb5da4ff7cf8523cfcef08393e5dd2ff3ab3223e4324426d285d7ae92",
      "vmTrace": null
    }
  ],
  "id": 0
}
```

---

## Complete Method Summary

| Category | Method | Supported Chains |
|----------|--------|-----------------|
| **Debug** | `debug_traceTransaction` | ETH, BSC, Polygon, Avalanche C-Chain, Arbitrum Nitro |
| **Debug** | `debug_traceCall` | ETH, BSC, Polygon, Avalanche C-Chain, Arbitrum Nitro |
| **Debug** | `debug_traceBlockByNumber` | ETH, BSC, Polygon, Avalanche C-Chain, Arbitrum Nitro |
| **Debug** | `debug_traceBlockByHash` | ETH, BSC, Polygon, Avalanche C-Chain, Arbitrum Nitro |
| **Debug Pro** | `debug_jstraceTransaction` | BSC, ETH, Polygon |
| **Debug Pro** | `debug_jstraceCall` | BSC, ETH, Polygon |
| **Debug Pro** | `debug_jstraceBlockByNumber` | BSC, ETH, Polygon |
| **Debug Pro** | `debug_jstraceBlockByHash` | BSC, ETH, Polygon |
| **Trace** | `trace_block` | ETH, BSC, opBNB, Polygon |
| **Trace** | `trace_transaction` | ETH, BSC, opBNB, Polygon |
| **Trace** | `trace_call` | ETH, BSC, opBNB, Polygon |
| **Trace** | `trace_get` | ETH, BSC, opBNB, Polygon |
| **Trace** | `trace_filter` | ETH, BSC, opBNB, Polygon |
| **Trace** | `trace_replayTransaction` | ETH, BSC, opBNB, Polygon |
| **Trace** | `trace_replayBlockTransactions` | ETH, BSC, opBNB, Polygon |

---

## Chain-Specific Endpoint Examples

| Chain | Endpoint Example |
|-------|-----------------|
| Ethereum | `https://eth-mainnet.nodereal.io/v1/your-api-key` |
| BNB Smart Chain | `https://bsc-mainnet.nodereal.io/v1/your-api-key` |
| opBNB | `https://opbnb-mainnet.nodereal.io/v1/your-api-key` |
| Polygon | `https://polygon-mainnet.nodereal.io/v1/your-api-key` |
| Avalanche C-Chain | `https://open-platform.nodereal.io/your-api-key/avalanche-c/ext/bc/C/rpc` |
| Arbitrum One (Nitro) | `https://open-platform.nodereal.io/your-api-key/arbitrum-nitro/` |

---

## Tracer Options

The `debug_*` and `debug_jstrace*` methods accept a tracer configuration object. Common built-in tracers:

| Tracer | Description |
|--------|-------------|
| `callTracer` | Returns the call hierarchy with input/output data, gas usage, and nested calls |
| `prestateTracer` | Returns the pre-execution state of all accounts accessed by the transaction |
| `4byteTracer` | Returns 4-byte function signatures encountered during execution |

For Debug Pro (`debug_jstrace*`) methods, you can also provide custom JavaScript tracer strings:

```json
{
  "tracer": "{ result: [], fault: function() {}, step: function(log) { if(log.op.toString() === 'SSTORE') this.result.push(log.stack.peek(0)); } }"
}
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `method not found` for debug methods | Free tier does not include Debug/Trace | Upgrade to Growth tier or above |
| Timeout on `trace_filter` | Block range too large | Reduce `fromBlock`/`toBlock` range; use `count` to limit results |
| `debug_traceBlockByNumber` timeout | Block has too many transactions | Use `debug_traceTransaction` on individual tx hashes instead |
| JS tracer syntax error | Invalid JavaScript in custom tracer | Test tracer logic locally; ensure `result`, `fault`, `step` functions exist |
| Empty `stateDiff` in replay | No state changes in transaction | Transaction may be a pure read or failed early |
| High CU consumption | Debug/Trace methods are expensive | Use `callTracer` instead of `vmTrace`; avoid `trace_filter` on large ranges |
| Different response format on Arbitrum | Arbitrum uses struct logs format | Arbitrum returns `structLogs` array instead of callTracer objects |

## Documentation

- **Debug API Reference:** https://docs.nodereal.io/reference/debug_tracetransaction
- **Debug Pro API Reference:** https://docs.nodereal.io/reference/debug_jstracetransaction
- **Trace API Reference:** https://docs.nodereal.io/reference/trace_block
- **API Reference:** https://docs.nodereal.io/reference
- **Find API Key & Endpoint:** https://docs.nodereal.io/docs/find-api-key-endpoint
- **Pricing:** https://nodereal.io/pricing
