# Portal API Reference -- Account & Usage Management

## Overview

The Portal API provides programmatic access to MegaNode account management, CU (Compute Unit) consumption monitoring, and usage analytics. This enables developers to build dashboards, set up alerts, and track API usage without logging into the web console.

---

## Table of Contents

1. [Base URL](#base-url) -- Portal API endpoint URLs
2. [API Methods](#api-methods) -- CU consumption and detail endpoints
3. [Code Examples](#code-examples) -- JavaScript integration samples
4. [Use Cases](#use-cases) -- Monitoring and alerting scenarios
5. [Best Practices](#best-practices) -- Recommended usage guidelines

---

## Base URL

```
https://portal-api.nodereal.io/v1/{apiKey}
```

Alternative server:
```
https://rpc-portal.bk.nodereal.cc/v1/{apiKey}
```

---

## API Methods

### GET `/{apiKey}/cu-consumption`

Get your account's Compute Unit consumption data broken down by method and network for a given time range.

**Parameters:**

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| `apiKey` | path | `string` | Yes | Your MegaNode API key |
| `startTime` | query | `string` | Yes | Start time for the query range |
| `endTime` | query | `string` | Yes | End time for the query range |

**Example Request:**

```bash
curl "https://portal-api.nodereal.io/v1/{apiKey}/cu-consumption?startTime=2024-01-01&endTime=2024-01-31"
```

**Response Schema:**

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "startTime": 1704067200,
    "endTime": 1706745600,
    "totalConsumption": 150000000,
    "records": [
      {
        "method": "eth_call",
        "network": "bsc-mainnet",
        "cost": 50000,
        "count": 2500
      },
      {
        "method": "eth_getBalance",
        "network": "eth-mainnet",
        "cost": 30000,
        "count": 2000
      }
    ]
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `code` | `integer` | Response code (0 = success) |
| `msg` | `string` | Response message |
| `data.startTime` | `integer` | Start time as Unix timestamp |
| `data.endTime` | `integer` | End time as Unix timestamp |
| `data.totalConsumption` | `integer` | Total CU consumed in the period |
| `data.records` | `array` | Per-method breakdown |
| `data.records[].method` | `string` | RPC method name |
| `data.records[].network` | `string` | Network identifier (e.g., "bsc-mainnet") |
| `data.records[].cost` | `integer` | Total CU cost for this method/network |
| `data.records[].count` | `integer` | Number of requests |

**Error Responses:**

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid request (bad date format, missing parameters) |
| 403 | Internal error or unauthorized |

---

### GET `/{apiKey}/cu-detail`

Get your account's CU plan details including quota, usage, and rate limits.

**Parameters:**

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| `apiKey` | path | `string` | Yes | Your MegaNode API key |

**Example Request:**

```bash
curl "https://portal-api.nodereal.io/v1/{apiKey}/cu-detail"
```

**Response Schema:**

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "plan": "growth",
    "autoscaling": false,
    "cups": 300,
    "totalQuota": 350000000,
    "usage": 150000000,
    "remainingQuota": 200000000
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `code` | `integer` | Response code (0 = success) |
| `msg` | `string` | Response message |
| `data.plan` | `string` | Current plan name (e.g., "free", "growth", "team", "enterprise") |
| `data.autoscaling` | `boolean` | Whether autoscaling is enabled for overage |
| `data.cups` | `integer` | Compute Units Per Second (rate limit) |
| `data.totalQuota` | `integer` | Total monthly CU quota |
| `data.usage` | `integer` | CU used so far this billing period |
| `data.remainingQuota` | `integer` | Remaining CU available this billing period |

---

## Code Examples

### Check CU Usage

```javascript
async function getCUConsumption(apiKey, startTime, endTime) {
  const url = new URL(`https://portal-api.nodereal.io/v1/${apiKey}/cu-consumption`);
  url.searchParams.set("startTime", startTime);
  url.searchParams.set("endTime", endTime);

  const response = await fetch(url);
  const data = await response.json();

  if (data.code !== 0) {
    throw new Error(`Portal API error: ${data.msg}`);
  }

  return data.data;
}

// Usage
const usage = await getCUConsumption(
  process.env.NODEREAL_API_KEY,
  "2024-01-01",
  "2024-01-31"
);
console.log(`Total CU consumed: ${usage.totalConsumption}`);
console.log("Per-method breakdown:");
for (const record of usage.records) {
  console.log(`  ${record.method} (${record.network}): ${record.cost} CU, ${record.count} requests`);
}
```

### Check Plan and Quota

```javascript
async function getCUDetail(apiKey) {
  const response = await fetch(`https://portal-api.nodereal.io/v1/${apiKey}/cu-detail`);
  const data = await response.json();

  if (data.code !== 0) {
    throw new Error(`Portal API error: ${data.msg}`);
  }

  return data.data;
}

// Usage
const detail = await getCUDetail(process.env.NODEREAL_API_KEY);
console.log(`Plan: ${detail.plan}`);
console.log(`CUPS (rate limit): ${detail.cups}`);
console.log(`Usage: ${detail.usage} / ${detail.totalQuota} CU`);
console.log(`Remaining: ${detail.remainingQuota} CU`);
console.log(`Autoscaling: ${detail.autoscaling}`);

// Alert if approaching quota
const usagePercent = (detail.usage / detail.totalQuota) * 100;
if (usagePercent > 90) {
  console.warn(`WARNING: CU usage at ${usagePercent.toFixed(1)}%`);
}
```

### Usage Alert System

```javascript
async function checkUsageAlerts(apiKey) {
  const detail = await getCUDetail(apiKey);
  const usagePercent = (detail.usage / detail.totalQuota) * 100;

  const thresholds = [
    { level: 90, severity: "critical" },
    { level: 75, severity: "warning" },
    { level: 50, severity: "info" },
  ];

  for (const threshold of thresholds) {
    if (usagePercent >= threshold.level) {
      console.log(`[${threshold.severity.toUpperCase()}] CU usage at ${usagePercent.toFixed(1)}% (${detail.usage}/${detail.totalQuota})`);
      // Send alert via your preferred notification system
      break;
    }
  }
}
```

---

## Use Cases

- **Usage dashboards:** Build internal monitoring for CU consumption trends
- **Cost alerts:** Trigger alerts when approaching monthly CU quota (50%, 75%, 90% thresholds)
- **Per-method analytics:** Identify which API methods consume the most CUs to optimize hot paths
- **Per-network tracking:** Monitor usage across different chains and networks
- **Capacity planning:** Track CUPS (rate limit) against actual throughput needs

---

## Best Practices

- Query CU consumption daily to catch usage spikes early
- Set up alerts at 50%, 75%, and 90% of monthly CU quota
- Use per-method breakdown to optimize high-CU-cost patterns (e.g., replace `debug_traceTransaction` at 280 CU with `eth_getTransactionReceipt` at 15 CU where possible)
- Monitor the `cups` field to understand your rate limit -- if hitting rate limits, consider upgrading your plan
- Check `autoscaling` status -- if disabled, your service will be rate-limited when quota is exhausted
- CU quota is account-level, not per-key -- monitor total usage across all API keys
