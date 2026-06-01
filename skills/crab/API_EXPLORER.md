# Onchain Explorer API 接口文档

本文档描述 `onchain_explorer` 模块提供的链上数据查询接口。

---

## 概述

### 功能范围

| 功能 | 支持链 | 数据源 |
|------|--------|--------|
| 合约 ABI/源码查询 | ETH, BSC | Etherscan V2 API |
| Token 转账历史 | ETH, BSC | Alchemy |
| Token 转账历史 | SOL | Helius |
| 地址综合信息 | SOL | Helius |

### 认证要求

所有接口都需要 **Crab Auth** 签名认证（除 `/api/health` 外）：

| Header | 说明 |
|--------|------|
| `X-Crab-Timestamp` | Unix 时间戳（24 小时有效期） |
| `X-Crab-Signature` | ECDSA-SHA256 十六进制签名 |
| `X-Crab-Key` | 公钥（Base64 DER 格式） |
| `X-Crab-Address` | 签名地址（0x...） |

签名消息格式：`CRAB-AUTH:{timestamp}:{address}`

### 通用响应格式

**成功响应**
```json
{
  "ok": true,
  "data": { ... }
}
```

**失败响应**
```json
{
  "ok": false,
  "error": {
    "code": "error_code",
    "message": "Error description."
  }
}
```

---

## 接口列表

### 1. 合约源码/ABI 查询

查询合约的 ABI、源代码及编译信息。

**端点**
```
POST /api/explorer/contract
```

**请求参数**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `chain` | string | ✅ | 链名称：`ETH` 或 `BSC` |
| `address` | string | ✅ | 合约地址 |

**请求示例**
```json
{
  "chain": "ETH",
  "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7"
}
```

**成功响应（已验证合约）**
```json
{
  "ok": true,
  "data": {
    "verified": true,
    "contractName": "TetherToken",
    "compilerVersion": "v0.4.18+commit.9cf6e910",
    "optimizationUsed": true,
    "abi": [...],
    "sourceCode": "pragma solidity ^0.4.17; ...",
    "licenseType": "MIT",
    "proxy": false,
    "implementation": null
  }
}
```

**成功响应（未验证合约）**
```json
{
  "ok": true,
  "data": {
    "verified": false,
    "message": "未开源"
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| `verified` | boolean | 合约是否已验证/开源 |
| `message` | string | 未验证时的提示信息 |
| `contractName` | string | 合约名称 |
| `compilerVersion` | string | Solidity 编译器版本 |
| `optimizationUsed` | boolean | 是否启用优化 |
| `abi` | array | 合约 ABI |
| `sourceCode` | string \| object | 源代码（多文件时为对象） |
| `licenseType` | string | 许可证类型 |
| `proxy` | boolean | 是否为代理合约 |
| `implementation` | string \| null | 代理合约的实现地址 |

**错误码**

| 错误码 | HTTP 状态 | 说明 |
|--------|----------|------|
| `missing_input` | 400 | 缺少 `chain` 或 `address` |
| `unsupported_chain` | 400 | 仅支持 ETH 和 BSC |
| `explorer_unavailable` | 502 | 上游服务不可用 |

---

### 2. ETH、BSCToken 转账历史

查询钱包地址的 ETH、BSC Token 转账记录（包括转入和转出）。

**端点**
```
POST /api/explorer/token-history
```

**请求参数**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `chain` | string | ✅ | 链名称：`ETH`、`BSC` |
| `address` | string | ✅ | 钱包地址 |


**请求示例（ETH/BSC）**
```json
{
  "chain": "ETH",
  "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
  "limit": 20
}
```

**成功响应（ETH/BSC）**
```json
{
  "ok": true,
  "data": {
    "transfers": [
      {
        "uniqueId": "0x123...abc-erc20-USDT",
        "hash": "0x123...abc",
        "blockNum": "0x10f1234",
        "from": "0xabc...",
        "to": "0xdef...",
        "value": 1000.5,
        "asset": "USDT",
        "category": "erc20",
        "metadata": {
          "blockTimestamp": "2024-01-15T10:30:00Z"
        }
      }
    ],
    "outPageKey": "next_page_cursor_out",
    "inPageKey": "next_page_cursor_in"
  }
}
```


**错误码**

| 错误码 | HTTP 状态 | 说明 |
|--------|----------|------|
| `missing_input` | 400 | 缺少 `chain` 或 `address` |
| `unsupported_chain` | 400 | 仅支持 ETH、BSC |
| `explorer_unavailable` | 502 | 上游服务不可用 |

---

### 3. SOL 地址综合信息

查询 Solana 地址的余额和最近转账记录。

**端点**
```
POST /api/explorer/sol-address
```

**请求参数**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `address` | string | ✅ | Solana 地址 |
| `txLimit` | number | ❌ | 最近交易数量（默认 10） |

**请求示例**
```json
{
  "address": "vines1vzrYbzLMRdu58ou5XTby4qAqVRLmqo36NKPTg",
  "txLimit": 5
}
```

**成功响应**
```json
{
  "ok": true,
  "data": {
    "balances": {
      "nativeBalance": {
        "lamports": 1500000000,
        "price_per_sol": 150.25,
        "total_price": 225.375
      },
      "tokens": [
        {
          "mint": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
          "amount": 1000000,
          "decimals": 6,
          "tokenAccount": "abc..."
        }
      ]
    },
    "recentTransactions": [
      {
        "signature": "5abc...xyz",
        "timestamp": 1705312200,
        "type": "TRANSFER",
        "fee": 5000,
        "tokenTransfers": [...]
      }
    ]
  }
}
```

**响应字段说明**

| 字段 | 说明 |
|------|------|
| `balances.nativeBalance` | SOL 原生余额信息 |
| `balances.tokens` | SPL Token 余额列表 |
| `recentTransactions` | 最近转账记录（type 固定为 `TRANSFER`） |

**错误码**

| 错误码 | HTTP 状态 | 说明 |
|--------|----------|------|
| `missing_input` | 400 | 缺少 `address` |
| `explorer_unavailable` | 502 | 上游服务不可用 |

---
