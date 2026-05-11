# Pricing Reference — Plans, Compute Units & Rate Limits

## Overview

MegaNode uses a Compute Unit (CU) based pricing model. Each API method consumes a specific number of CUs, and monthly quotas are determined by your pricing plan. Rate limits are enforced via CUPS (Compute Units Per Second).

---

## Table of Contents

1. [Pricing Plans](#pricing-plans) -- Plan tiers and feature comparison
2. [Add-on CU Packs](#add-on-cu-packs) -- Purchase additional compute units
3. [CUPS (Compute Units Per Second)](#cups-compute-units-per-second) -- Rate limits per plan
4. [Compute Unit Costs by Method](#compute-unit-costs-by-method) -- Per-method CU pricing table
5. [Billing Details](#billing-details) -- Quota resets and payment info
6. [Error Responses](#error-responses) -- Rate limit error formats
7. [Cost Optimization Tips](#cost-optimization-tips) -- Reduce CU consumption strategies

---

## Pricing Plans

| Feature | Free | Growth | Team | Business |
|---------|------|--------|------|----------|
| **Monthly Cost** | $0 | $31/mo | $159/mo | $399/mo |
| **Annual Cost** | $0 | $372/yr | $1,908/yr | $4,788/yr |
| **Monthly CUs** | 10,000,000 | 500,000,000 | 2,000,000,000 | 5,000,000,000 |
| **CUPS (Rate Limit)** | 300 | 700 | 1,500 | 3,000 |
| **API Keys** | 3 | 15 | 30 | 50 |
| **HTTPS & WSS** | Yes | Yes | Yes | Yes |
| **Archive Data** | Yes | Yes | Yes | Yes |
| **Enhanced APIs** | Yes | Yes | Yes | Yes |
| **Debug API** | Yes | Yes | Yes | Yes |
| **Mainnet + Testnet** | Yes | Yes | Yes | Yes |
| **Support** | Discord | Discord | VIP | VIP |

**Annual billing saves 20%** across all paid plans.

---

## Add-on CU Packs

Additional CUs can be purchased when monthly quota is insufficient:

- **Rate:** $1/month per 5,000,000 CU
- **Example:** $20/month for 100,000,000 additional CUs
- **Payment:** Stripe or PayPal

---

## CUPS (Compute Units Per Second)

CUPS is the rate limit — maximum CUs consumed per second across all API keys in an account.

| Plan | CUPS Limit |
|------|------------|
| Free | 300 |
| Growth | 700 |
| Team | 1,500 |
| Business | 3,000 |

CUPS resets every second. Exceeding the limit returns an error.

---

## Compute Unit Costs by Method

### Standard Methods (5-150 CUs)

| CU Cost | Methods |
|---------|---------|
| **5** | `eth_accounts`, `eth_blockNumber`, `eth_chainId`, `eth_syncing`, `net_listening`, `net_version`, `web3_clientVersion` |
| **10** | `eth_subscribe`, `eth_uninstallFilter`, `eth_unsubscribe`, `web3_sha3`, `net_peerCount` |
| **15** | `eth_gasPrice`, `eth_getBalance`, `eth_getBlockByNumber`, `eth_getCode`, `eth_getStorageAt`, `eth_getTransactionByHash`, `eth_getTransactionReceipt`, `eth_maxPriorityFeePerGas`, `eth_feeHistory` |
| **18** | `eth_getBlockByHash`, `eth_getBlockTransactionCountByHash`, `eth_getBlockTransactionCountByNumber`, `eth_newFilter`, `eth_newBlockFilter`, `eth_newPendingTransactionFilter`, `eth_getFilterChanges`, `eth_getUncle*` methods |
| **20** | `eth_call` |
| **25** | `eth_getTransactionCount` |
| **50** | `eth_getFilterLogs`, `eth_getLogs` |
| **75** | `eth_estimateGas` |
| **150** | `eth_sendRawTransaction` |

### Enhanced API Methods (25-300 CUs)

| CU Cost | Methods |
|---------|---------|
| **25** | `nr_getTokenBalance20`, `nr_getTotalSupply20`, `nr_getTokenMeta`, `nr_getTokenHoldings`, `nr_getTokenCount`, `nr_getNFTHoldings`, `nr_getNFTHoldingCount`, `nr_getNFTInventory`, `nr_getAssetTransfersCount`, `nr_getContractCreationTransaction`, `nr_getBlockNumberByTimeStamp` |
| **50** | `nr_getTokenHolderCount`, `nr_getNFTHolderCount`, `nr_getNFTCollectionHolderCount`, `nr_getAssetTransfers`, `nr_getTransactionByAddress`, `nr_getDailyBlockCountAndReward`, `nr_getDailyBlockReward` |
| **100** | `nr_getTokenHolders`, `nr_getNFTHolders`, `nr_getNFTHoldersWithBalance`, `nr_getAccountList`, `nr_getAccountListCount` |

### Debug & Trace Methods (280-18,000 CUs)

| CU Cost | Methods |
|---------|---------|
| **280** | `debug_traceTransaction`, `debug_traceCall` |
| **1,000-1,200** | `eth_getDiffAccounts`, `eth_getDiffAccountsWithTxHash` |
| **1,800** | `debug_traceBlockByNumber`, `debug_traceBlockByHash` |
| **2,000-2,500** | `trace_block`, `trace_replayBlockTransactions`, `trace_replayTransaction` |
| **3,000** | `txpool_content` |
| **10,000** | `trace_filter` |
| **18,000** | `debug_jstraceBlockByNumber`, `debug_jstraceBlockByHash` |

### Special Charges

| Type | CU Cost |
|------|---------|
| Unsupported/unknown methods | 2 CUs per request |
| Incorrect method names | 2 CUs per request |
| WebSocket bandwidth | 0.04 CU per byte |
| Batch request limit | Max 500 requests per batch |

---

## Billing Details

- **CU quota resets** on the 1st of each month
- **Mid-month signups** are prorated
- **CU usage aggregates** across all API keys within an account
- **Payment methods:** Credit cards, PayPal (no cryptocurrency accepted)

---

## Error Responses

### Rate Limit Exceeded (CUPS)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32005,
    "message": "Your account has exceeded its Compute Units Per Second capacity..."
  }
}
```

### Monthly CU Quota Exceeded

HTTP Status: `429`

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32005,
    "message": "ran out of cu"
  }
}
```

---

## Cost Optimization Tips

### Low-Cost Patterns
- Use `eth_blockNumber` (5 CU) to check for new blocks before fetching details
- Batch related calls to reduce overhead (up to 500 per batch)
- Cache block data locally — blocks are immutable once finalized
- Use `eth_getBlockByNumber` (15 CU) instead of `eth_getBlockByHash` (18 CU)

### Avoid High-Cost Patterns
- Minimize `trace_filter` calls (10,000 CU each)
- Avoid `debug_jstrace*` methods in production (18,000 CU each)
- Don't poll `txpool_content` frequently (3,000 CU each)
- Filter WebSocket subscriptions tightly (0.04 CU/byte adds up)

### Monitoring
- Track CU consumption via the MegaNode dashboard
- Set up alerts before hitting monthly quota
- Review per-method CU costs when designing API integrations
