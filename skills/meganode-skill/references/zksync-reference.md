# zkSync RPC Reference

## Overview

zkSync Era (zkEVM L2) with both standard Ethereum JSON-RPC and zkSync-exclusive methods.

**Endpoint:**
```
https://open-platform.nodereal.io/{apiKey}/zksync/
```

**Supported Networks:** zkSync Era (mainnet)

## Ethereum JSON-RPC Methods

Standard eth_* methods are supported (eth_call, eth_getBalance, eth_blockNumber, eth_getTransactionByHash, etc.).

## zkSync Exclusive Methods (zks_*)

| Method | Description |
|--------|-------------|
| `zks_estimateFee` | Estimate fee for a transaction |
| `zks_estimateGasL1ToL2` | Estimate gas for L1 to L2 transaction |
| `zks_getAllAccountBalances` | Get all token balances for an account |
| `zks_getBlockDetails` | Get zkSync-specific block details (L1 batch, commit/prove/execute hashes) |
| `zks_getBridgeContracts` | Get L1/L2 default bridge addresses |
| `zks_getBytecodeByHash` | Get bytecode by hash |
| `zks_getConfirmedTokens` | Get token info within a range |
| `zks_getL1BatchBlockRange` | Get block range in an L1 batch |
| `zks_getL1BatchDetails` | Get L1 batch details |
| `zks_getL2ToL1LogProof` | Get proof for L2 to L1 log |
| `zks_getL2ToL1MsgProof` | Get proof for L2 to L1 message |
| `zks_getMainContract` | Get zkSync Era contract address |
| `zks_getRawBlockTransactions` | Get raw transaction data in a block |
| `zks_getTestnetPaymaster` | Get testnet paymaster address |
| `zks_getTokenPrice` | Get token price in USD |
| `zks_getTransactionDetails` | Get zkSync-specific tx details (commit/prove/execute hashes) |
| `zks_L1BatchNumber` | Get latest L1 batch number |
| `zks_L1ChainId` | Get underlying L1 chain ID |

### zks_estimateFee

```bash
curl https://open-platform.nodereal.io/{apiKey}/zksync/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method":"zks_estimateFee","params":[{"from":"0x1111111111111111111111111111111111111111","to":"0x2222222222222222222222222222222222222222","data":"0xffffffff"}],"id":1,"jsonrpc":"2.0"}'
```

**Returns:** `gas_limit`, `gas_per_pubdata_limit`, `max_fee_per_gas`, `max_priority_fee_per_gas`

### zks_getBlockDetails

```bash
curl https://open-platform.nodereal.io/{apiKey}/zksync/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method":"zks_getBlockDetails","params":[140599],"id":1,"jsonrpc":"2.0"}'
```

### zks_getAllAccountBalances

```bash
curl https://open-platform.nodereal.io/{apiKey}/zksync/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"method":"zks_getAllAccountBalances","params":["0x98E9D288743839e96A8005a6B51C770Bbf7788C0"],"id":1,"jsonrpc":"2.0"}'
```

---
