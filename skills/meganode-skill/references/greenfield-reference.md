# Greenfield API Reference

## Overview

API reference for BNB Greenfield decentralized storage network services available through the NodeReal MegaNode platform. This document covers the Greenfield Enhanced API for querying on-chain data (transactions, policies, bucket statistics) and the Greenfield Billing API for cost tracking and quota management.

## Table of Contents

1. [Greenfield Enhanced API](#1-greenfield-enhanced-api) -- Enhanced API methods for querying transactions, policies, and daily bucket data on BNB Greenfield
2. [Greenfield Billing API](#2-greenfield-billing-api) -- Billing and quota tracking for BNB Greenfield storage operations, including total cost, monthly bills, and real-time bills

---

## 1. Greenfield Enhanced API

Enhanced API methods for BNB Greenfield decentralized storage network.

**Base endpoints:**

| Network | Endpoint |
|---------|----------|
| Mainnet | `https://open-platform.nodereal.io/{apiKey}/greenfieldscan-mainnet/` |
| Testnet | `https://open-platform.nodereal.io/{apiKey}/greenfieldscan-testnet/` |

---

### Get transaction list by address

```
GET /greenfield/tx/list/by_address/{address}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| address | path | yes | Account address |
| page | query | yes | Page number |
| per_page | query | yes | Items per page |
| max_height | query | no | Maximum block height |
| tx_type | query | no | Transaction type filter |

**Response example:**
```json
[
  {
    "hash": [0],
    "height": 0,
    "index": 0,
    "time": "string",
    "tx_result": {
      "code": 0,
      "codespace": "string",
      "fee": "string",
      "gas_used": 0,
      "gas_wanted": 0,
      "module": "string",
      "type": "string"
    }
  }
]
```

---

### Get policy list by resource ID

```
GET /greenfield/permission/policy/list/by_resource/{id}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| id | path | yes | Resource ID |
| page | query | yes | Page number |
| per_page | query | yes | Items per page |

**Response:** Array of policy objects with `actions`, `policyID`, `principalType`, `resourceType`, `effect`, `expirationTime`, `removed`.

---

### Get daily bucket list

Returns daily bucket total charged storage size. Updated every few hours.

```
GET /greenfield/chart/daily_bucket/list
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| page | query | yes | Page number |
| per_page | query | yes | Items per page |
| owner | query | no | Filter by owner address |

**Response example:**
```json
[
  {
    "bucketID": [0],
    "bucketName": "string",
    "bucketNumID": "string",
    "dailyTotalChargedStorageSize": ["string"],
    "owner": [0]
  }
]
```

---

## 2. Greenfield Billing API

Billing and quota tracking for BNB Greenfield storage operations. Data updated daily at UTC 00:00.

**Base endpoints:**

| Network | Endpoint |
|---------|----------|
| Mainnet | `https://open-platform.nodereal.io/{apiKey}/greenfieldbilling-mainnet/` |
| Testnet | `https://open-platform.nodereal.io/{apiKey}/greenfieldbilling-testnet/` |

---

### Get total cost by owner address

```
GET /greenfield/total_cost/list/by_owner/{owner}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| owner | path | yes | Owner address |

**Response example:**
```json
[
  {
    "Cost": "string",
    "address": [0]
  }
]
```

---

### Get total cost by payment address

```
GET /greenfield/total_cost/list/by_payment/{payment}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| payment | path | yes | Payment address |

---

### Get monthly bill by owner address

```
GET /greenfield/bill_monthly/list/by_owner/{owner}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| owner | path | yes | Owner address |
| start_month | query | no | Start month |
| start_year | query | no | Start year |
| end_month | query | no | End month |
| end_year | query | no | End year |

**Response example:**
```json
[
  {
    "bills": [
      {
        "ReadCost": "string",
        "StoreCost": "string",
        "TotalCost": "string",
        "address": [0],
        "month": 0,
        "year": 0
      }
    ]
  }
]
```

---

### Get monthly bill by payment address

```
GET /greenfield/bill_monthly/list/by_payment/{payment}
```

Same parameters and response structure as the owner variant.

---

### Get real time bill by owner address

```
GET /greenfield/bill_realtime/list/by_owner/{owner}
```

### Get real time bill count by owner address

```
GET /greenfield/bill_realtime/count/by_owner/{owner}
```

### Get real time bill by payment address

```
GET /greenfield/bill_realtime/list/by_payment/{payment}
```

### Get real time bill count by payment address

```
GET /greenfield/bill_realtime/count/by_payment/{payment}
```

---

### Greenfield Billing API Summary

| Method | HTTP | Description |
|--------|------|-------------|
| `/greenfield/total_cost/list/by_owner/{owner}` | GET | Total cost by owner |
| `/greenfield/total_cost/list/by_payment/{payment}` | GET | Total cost by payment address |
| `/greenfield/bill_monthly/list/by_owner/{owner}` | GET | Monthly bill by owner |
| `/greenfield/bill_monthly/list/by_payment/{payment}` | GET | Monthly bill by payment address |
| `/greenfield/bill_realtime/list/by_owner/{owner}` | GET | Real-time bill by owner |
| `/greenfield/bill_realtime/count/by_owner/{owner}` | GET | Real-time bill count by owner |
| `/greenfield/bill_realtime/list/by_payment/{payment}` | GET | Real-time bill by payment address |
| `/greenfield/bill_realtime/count/by_payment/{payment}` | GET | Real-time bill count by payment address |

---
