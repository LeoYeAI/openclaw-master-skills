# Data Transformations Reference

Complete reference for type conversions, field mappings, and data transformations when working with Moralis Data API.

## Table of Contents

- [Block Number Handling](#block-number-handling)
- [Timestamp Conversions](#timestamp-conversions)
- [Balance/Amount Handling](#balanceamount-handling)
- [snake_case to camelCase Patterns](#snake_case--camelcase-patterns)
- [Boolean String Handling](#boolean-string-handling)
- [Common Field Mappings](#common-field-mappings)
- [Type Conversion Utility Functions](#type-conversion-utility-functions)
- [Best Practices](#best-practices)

---

## Block Number Handling

**NEVER hex, always decimal:**

```typescript
// Most endpoints return decimal (NOT hex)
block_number: 12386788           → number (use directly)
block_number: "12386788"         → parseInt(block_number, 10)
```

**Rare exceptions:**
Some specialized endpoints may return hex strings, but **always verify in the endpoint rule file first**.

## Timestamp Conversions

### ISO 8601 to Unix Timestamp

```typescript
// ISO 8601 string → Unix timestamp (milliseconds)
"2021-05-07T11:08:35.000Z" → new Date(timestamp).getTime()
```

### Unix Timestamp (Seconds) to Milliseconds

```typescript
// Unix timestamp (seconds) → milliseconds
1620394115 → timestamp * 1000
```

### Detecting Timestamp Format

```typescript
function parseTimestamp(timestamp: any): number {
  if (typeof timestamp === 'number') {
    // Unix timestamp (check if seconds or milliseconds)
    return timestamp < 10000000000 ? timestamp * 1000 : timestamp;
  } else if (typeof timestamp === 'string') {
    // ISO 8601 string
    return new Date(timestamp).getTime();
  }
  return timestamp;
}
```

## Balance/Amount Handling

### Native Token Balances (Wei/Smallest Unit)

```typescript
// Native token balances: Wei/Smallest unit → Formatted
balance: "1000000000000000000"

// Option 1: Manual conversion
const formatted = (Number(BigInt(balance)) / 1e18).toFixed(6);

// Option 2: Using ethers.js
import { formatUnits } from 'ethers';
const formatted = formatUnits(balance, 18);

// Option 3: Use getWalletTokenBalancesPrice which returns formatted field
```

### Token Balances with Decimals

```typescript
// ERC20 token balances with decimals field
{
  "balance": "1000000000000000000",
  "decimals": 18
}

// Convert to human-readable
const formatted = (parseInt(balance) / Math.pow(10, decimals)).toFixed(6);
```

## snake_case → camelCase Patterns

### General Pattern

```typescript
// API response → TypeScript interface
{
  token_address: string;
  from_address_label: string;
  block_number: string;
  total_token_balances: number;
}
→ {
  tokenAddress: string;
  fromAddressLabel: string;
  blockNumber: string;
  totalTokenBalances: number;
}
```

### Automatic Transformation Function

```typescript
function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

// Example: toCamelCase('token_address') → 'tokenAddress'
```

## Boolean String Handling

API often returns boolean values as strings "true"/"false" or "1"/"0":

```typescript
// API returns "1" or "0", not boolean
receipt_status: "1"   → status: receipt_status === "1" ? "success" : "failed"

// API returns "true" or "false" strings
possible_spam: "false" → possibleSpam === "true"
possible_spam: "true"  → possibleSpam === "true"

// Normalize to boolean
function toBool(value: string | boolean): boolean {
  if (typeof value === 'boolean') return value;
  return value === 'true' || value === '1';
}
```

## Common Field Mappings

### Entity/Label Fields

```typescript
from_address_entity       → fromAddressEntity
from_address_entity_logo  → fromAddressEntityLogo
from_address_label        → fromAddressLabel
to_address_entity         → toAddressEntity
to_address_entity_logo    → toAddressEntityLogo
to_address_label          → toAddressLabel
owner_of_entity           → ownerOfEntity
owner_of_entity_logo      → ownerOfEntityLogo
owner_of_label            → ownerOfLabel
```

### Transaction Fields

```typescript
block_number        → blockNumber
block_timestamp     → blockTimestamp (ISO string!)
transaction_hash    → hash (or txHash)
receipt_gas_used    → receiptGasUsed
receipt_status      → status ("1" = success)
transaction_index   → transactionIndex
```

### Token/NFT Fields

```typescript
token_address       → tokenAddress
token_id            → tokenId (keep as string!)
token_decimal       → tokenIdDecimal (when in decimal format)
contract_type       → contractType
possible_spam       → possibleSpam (string "true"/"false")
verified_collection → verifiedCollection (string "true"/"false")
```

### DeFi Fields

```typescript
protocol_address   → protocolAddress
protocol_name      → protocolName
protocol_logo      → protocolLogo
defi_summary      → defiSummary
```

### Blockchain Fields

```typescript
block_hash        → blockHash
block_number      → blockNumber
block_timestamp   → blockTimestamp
transaction_hash  → hash (or txHash)
gas_used          → gasUsed
gas_price         → gasPrice
```

## Type Conversion Utility Functions

### Safe Number Parsing

```typescript
function safeParseInt(value: any, radix: number = 10): number {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') return parseInt(value, radix);
  return 0;
}

function safeParseFloat(value: any): number {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') return parseFloat(value);
  return 0;
}
```

### Safe BigInt Handling

```typescript
function toBigInt(value: any): bigint | null {
  if (typeof value === 'bigint') return value;
  if (typeof value === 'string' && value) {
    try {
      return BigInt(value);
    } catch {
      return null;
    }
  }
  return null;
}
```

## Best Practices

1. **Always check the endpoint rule file** for exact field names and types
2. **Never assume data types** - Verify with actual API response examples
3. **Handle optional fields** with optional chaining (`?.`) or default values
4. **Test with real data** - Use actual API responses, not just examples
5. **Log unexpected values** - If you see unexpected formats, verify in rule file
