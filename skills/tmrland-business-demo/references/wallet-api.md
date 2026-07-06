# Wallet API

Base URL: `/api/v1/wallet`

All endpoints require authentication via Bearer token. Each user has two wallets (personal and business) created automatically on registration. Use the `wallet_type` query parameter to select which wallet to operate on.

---

## GET /api/v1/wallet

Retrieve the current user's wallet balances.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `wallet_type` | str | No | `"personal"` (default) or `"business"` |

### Request Example

```
GET /api/v1/wallet?wallet_type=business
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "wallet_type": "business",
  "business_id": null,
  "usd_balance": "2450.00",
  "usdc_balance": "0.00",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |

---

## POST /api/v1/wallet/charge

Add funds to the wallet (simulated top-up for MVP).

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `wallet_type` | str | No | `"personal"` (default) or `"business"` |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `amount` | Decimal | Yes | Amount to add, must be > 0 and <= 100,000 |
| `currency` | str | No | Currency code, default `"USD"`. Accepted: `"USD"`, `"USDC"` |

### Request Example

```json
{
  "amount": "500.00",
  "currency": "USD"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "wallet_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "type": "charge",
  "amount": "500.00",
  "currency": "USD",
  "related_order_id": null,
  "status": "completed",
  "description": "Wallet top-up",
  "created_at": "2026-02-27T11:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Amount must be greater than 0"` | Non-positive amount |
| 400 | `"Amount exceeds maximum limit"` | Amount > 100,000 |
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | Invalid amount or currency format |

---

## POST /api/v1/wallet/withdraw

Withdraw funds from the wallet. Businesses use this to cash out earnings.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `wallet_type` | str | No | `"personal"` (default) or `"business"` |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `amount` | Decimal | Yes | Amount to withdraw, must be > 0 and <= 100,000 |
| `currency` | str | No | Currency code, default `"USD"`. Accepted: `"USD"`, `"USDC"` |

### Request Example

```json
{
  "amount": "1000.00",
  "currency": "USD"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "wallet_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "type": "withdraw",
  "amount": "1000.00",
  "currency": "USD",
  "related_order_id": null,
  "status": "completed",
  "description": "Wallet withdrawal",
  "created_at": "2026-02-27T15:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Insufficient balance"` | Available balance < requested amount |
| 400 | `"Amount must be greater than 0"` | Non-positive amount |
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | Invalid amount or currency format |

---

## GET /api/v1/wallet/transactions

List wallet transactions with pagination.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `wallet_type` | str | No | `"personal"` (default) or `"business"` |
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `20`, max `100` |

### Request Example

```
GET /api/v1/wallet/transactions?wallet_type=business&offset=0&limit=20
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "aabb0011-2233-4455-6677-8899aabbccdd",
      "wallet_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "type": "transfer_in",
      "amount": "7600.00",
      "currency": "USD",
      "related_order_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "status": "completed",
      "description": "Escrow release for order 11223344 (after 5% fee)",
      "created_at": "2026-03-01T16:30:00Z"
    },
    {
      "id": "ccdd2233-4455-6677-8899-aabbccddeeff",
      "wallet_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "type": "charge",
      "amount": "500.00",
      "currency": "USD",
      "related_order_id": null,
      "status": "completed",
      "description": "Wallet top-up",
      "created_at": "2026-02-27T15:00:00Z"
    }
  ],
  "total": 2
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | Invalid offset or limit value |

---

## POST /api/v1/wallet/kyc

Submit KYC (Know Your Customer) verification information.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `full_name` | str | Yes | Legal full name, max 200 characters |
| `id_type` | str | Yes | Identity document type (e.g. `"passport"`, `"id_card"`, `"driver_license"`), max 50 characters |
| `id_number` | str | Yes | Identity document number, max 100 characters |

### Request Example

```json
{
  "full_name": "张明",
  "id_type": "id_card",
  "id_number": "310101199001011234"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "kyc_status": "verified",
  "kyc_data": {
    "full_name": "张明",
    "id_type": "id_card",
    "id_number": "310101****1234"
  }
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"KYC already submitted"` | KYC data already exists for this user |
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | Missing or invalid fields |

---

## GET /api/v1/wallet/kyc

Retrieve the current user's KYC status and masked data.

**Auth:** Required

### Request Body

None.

### Request Example

```
GET /api/v1/wallet/kyc
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "kyc_status": "verified",
  "kyc_data": {
    "full_name": "张明",
    "id_type": "id_card",
    "id_number": "310101****1234"
  }
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"KYC data not found"` | User has not submitted KYC |
