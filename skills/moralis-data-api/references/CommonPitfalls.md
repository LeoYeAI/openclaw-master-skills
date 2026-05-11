# Common Pitfalls Reference

Complete reference for common mistakes, bugs, and gotchas when working with Moralis Data API.

## Table of Contents

- [Data Type Assumptions](#data-type-assumptions-most-common-bug-source)
- [Endpoint Path Inconsistencies](#endpoint-path-inconsistencies)
- [HTTP Method Surprises](#http-method-surprises)
- [Response Wrapper Structures](#response-wrapper-structures)
- [TypeScript Property Names](#typescript-property-names)
- [Other Common Issues](#other-common-issues)
- [Debugging Tips](#debugging-tips)
- [Prevention Checklist](#prevention-checklist)

---

## Data Type Assumptions (MOST COMMON BUG SOURCE)

**NEVER assume these without checking the rule file:**

| Field          | Wrong Assumption            | Reality                                 |
| -------------- | --------------------------- | --------------------------------------- |
| `block_number` | Hex string `"0xf2b5a4"`     | Decimal number `12386788`               |
| `timestamp`    | Unix timestamp `1620394115` | ISO string `"2021-05-07T11:08:35.000Z"` |
| `decimals`     | Always number               | Can be string `"18"` or number `18`     |
| `balance`      | Number                      | Always string (BigInt required)         |

### Impact of Wrong Assumptions

**Parsing block_number as hex:**
```typescript
// ❌ WRONG
const blockNumber = parseInt(data.block_number, 16); // Returns huge wrong number

// ✅ CORRECT
const blockNumber = typeof data.block_number === 'number'
  ? data.block_number
  : parseInt(data.block_number, 10);
```

**Parsing timestamp as number:**
```typescript
// ❌ WRONG
const timestamp = data.timestamp; // 2021-05-07... is invalid number

// ✅ CORRECT
const timestamp = typeof data.timestamp === 'string'
  ? new Date(data.timestamp).getTime()
  : data.timestamp;
```

**Treating balance as number:**
```typescript
// ❌ WRONG
const value = data.balance / 1e18; // "1000000000000000000" → NaN

// ✅ CORRECT
const value = Number(BigInt(data.balance)) / 1e18;
```

## Endpoint Path Inconsistencies

Not all endpoints follow the same pattern. Always verify exact path in rule file.

### Common Path Patterns

| Endpoint Type              | Path Pattern                            | Example                         | Notes                                    |
| ------------------------- | -------------------------------------- | -------------------------------- | ----------------------------------------- |
| Direct address           | `/{address}`                             | `getWalletTransactions`          | Simple replacement                          |
| Token balance            | `/{address}/erc20`                        | `getWalletTokenBalancesPrice`        | ERC20 suffix (with prices)                            |
| NFT balance             | `/{address}/nft`                          | `getWalletNFTs`                | NFT suffix                              |
| Wallet stats            | `/wallets/{address}/stats`               | `getWalletStats`                | ⚠️ Note `/wallets/` prefix           |
| DeFi positions          | `/wallets/{address}/defi/positions`       | `getDefiPositionsSummary`     | ⚠️ Multi-segment path                 |
| Block by number         | `/block/{number}`                         | `getBlock`                      | Path param name is `{number}`       |
| Latest block number      | `/latestBlockNumber/{chain}`              | `getLatestBlockNumber`          | ⚠️ Chain is PATH param           |
| Token price             | `/erc20/{token_address}/price`            | `getTokenPrice`                 | Token address in path                |
| Resolve ENS             | `/resolve/ens/{domain}`                   | `resolveENSDomain`              | ⚠️ Includes `/ens/` in path       |
| Resolve Unstoppable    | `/resolve/{domain}/address`                | `resolveDomain`                 | Different domain field              |

### Common Path Param Mistakes

```typescript
// ❌ WRONG - Using endpoint name instead of param name
const url = `/latestBlockNumber/${chain}`;

// ✅ CORRECT - Using exact param name from rule file
const url = `/latestBlockNumber/${chain}`;

// Check rule file for exact param name:
// Path: `/latestBlockNumber/{chain}` → param is `chain`
// Path: `/:address/erc20` → param is `address`
```

## HTTP Method Surprises

Most endpoints are GET, but some use different methods. Always verify in rule file.

### Common Method Table

| Action          | HTTP Method | Endpoint                              |
| --------------- | ------------- | ------------------------------------- |
| Query data       | GET          | Most endpoints                      |
| Create stream    | PUT          | Streams API (NOT Data API)          |
| Update stream    | POST         | Streams API (NOT Data API)          |
| Delete stream    | DELETE       | Streams API (NOT Data API)          |
| Query metadata   | GET          | `/erc20/metadata` (used to be POST) |

### Rare POST Endpoints in Data API

As of API v2.2, most Data API endpoints use GET. Historical POST endpoints have been updated to GET with query parameters.

**Example: Token metadata**
```typescript
// ❌ OLD (deprecated) - POST with request body
fetch('/erc20/metadata', {
  method: 'POST',
  body: { token_addresses: [address] }
});

// ✅ CURRENT - GET with query params
fetch(`/erc20/metadata?token_addresses=${address}`, {
  method: 'GET'
});
```

## Response Wrapper Structures

Before writing code that accesses `.map()`, `.length`, or `.forEach`, verify the response structure.

### Wrapper Type Detection

```typescript
interface WrappedResponse<T = any> {
  result?: T[];
  cursor?: string;
  page?: string;
  page_size?: string;
}

function isWrapped(data: any): data is WrappedResponse<any> {
  return data.result !== undefined || data.cursor !== undefined || data.page !== undefined;
}

function isDirectArray(data: any): data is any[] {
  return Array.isArray(data);
}
```

### Common Wrapper Mistakes

**Assuming array when it's wrapped:**
```typescript
// ❌ WRONG - Assumes array
data.map(tx => tx.hash) // Error: data.map is not a function

// ✅ CORRECT - Check if wrapped first
const results = isWrapped(data) ? data.result : data;
results.map(tx => tx.hash);
```

**Assuming wrapped when it's an array:**
```typescript
// ❌ WRONG - Assumes wrapper
data.result.map(token => token.address) // Error: data.result is undefined

// ✅ CORRECT - Check if array first
const results = isDirectArray(data) ? data : data.result || [];
results.map(token => token.address);
```

**Accessing undefined nested properties:**
```typescript
// ❌ WRONG - No optional chaining
const txHash = data.result[0].transaction_hash; // Error if result[0] is undefined

// ✅ CORRECT - Use optional chaining
const txHash = data.result?.[0]?.transaction_hash;
```

## TypeScript Property Names

### Property Name Restrictions

TypeScript doesn't allow property names starting with numbers.

**Problem:**
```typescript
// ❌ WON'T COMPILE
interface TokenPrice {
  24hrPercentChange: string;
}
```

**Solutions:**

Option 1: Use quoted property names
```typescript
// ✅ CORRECT
interface TokenPrice {
  "24hrPercentChange": string;
}
```

Option 2: Rename the property
```typescript
// ✅ CORRECT
interface TokenPrice {
  hr24PercentChange: string;
}
```

### Common Renaming Patterns

```typescript
// API response → TypeScript interface
{
  "24hrPercentChange": string  → hr24PercentChange
  "1dVolume": string           → oneDayVolume
  "7dVolume": string           → sevenDayVolume
  "30dVolume": string          → thirtyDayVolume
}
```

## Other Common Issues

### Chain ID Format

**Always use hex format for chain IDs:**
```typescript
// ❌ WRONG - String names
const chain = 'eth';

// ✅ CORRECT - Hex format
const chain = '0x1';

// Common hex chain IDs
"0x1"     // Ethereum
"0x89"    // Polygon
"0x38"    // BSC
"0xa4b1"  // Arbitrum
"0xa"     // Optimism
"0x2105"  // Base
"0xa86a"  // Avalanche
"0xfa"     // Fantom
```

### Address Format Verification

```typescript
function isValidEVMAddress(address: string): boolean {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
}

function isValidSolanaAddress(address: string): boolean {
  // Base58 format check
  return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(address);
}

// Usage
const address = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045';
if (!isValidEVMAddress(address)) {
  throw new Error('Invalid EVM address');
}
```

### Path Parameter Replacement

```typescript
// ❌ WRONG - Not replacing all path params
const url = '/:address/erc20'; // Still has :address

// ✅ CORRECT - Replace path params with actual values
const url = `/${address}/erc20`;

// For multiple params
const url = `/${address}/nft?chain=${chain}&limit=${limit}`;
```

### Base URL Confusion

```typescript
// Data API
const DATA_API_URL = 'https://deep-index.moralis.io/api/v2.2';

// Streams API (different!)
const STREAMS_API_URL = 'https://api.moralis-streams.com';

// ❌ WRONG - Mixing base URLs
fetch(`${DATA_API_URL}/streams/evm`); // Wrong endpoint

// ✅ CORRECT - Use correct base URL
fetch(`${STREAMS_API_URL}/streams/evm`);
```

### Decimal vs Hex Numbers

```typescript
function parseBlockNumber(value: any): number {
  // Most endpoints return decimal
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    // Check if it's hex (starts with 0x)
    if (value.startsWith('0x')) {
      console.warn('Hex block number detected - verify in endpoint rule file');
      return parseInt(value, 16);
    }
    return parseInt(value, 10);
  }
  throw new Error('Invalid block number format');
}

// Usage
const blockNumber = parseBlockNumber(data.block_number);
```

## Debugging Tips

### Logging Response Structure

```typescript
async function safeFetch(url: string): Promise<any> {
  const response = await fetch(url);

  // Log raw response for debugging
  console.log('Raw response:', response);

  // Check structure before processing
  if (Array.isArray(response)) {
    console.log('Detected: Direct array');
  } else if (response.result !== undefined) {
    console.log('Detected: Wrapped response');
    if (response.cursor !== undefined) {
      console.log('Detected: Cursor pagination');
    }
  } else {
    console.log('Detected: Single object');
  }

  return response;
}
```

### Common Error Messages and Causes

| Error Message                      | Likely Cause                          | Solution                           |
| --------------------------------- | ------------------------------------- | ---------------------------------- |
| "Cannot read property 'result'"     | Response is direct array               | Use `data` instead of `data.result` |
| "Cannot read property 'cursor'"   | No pagination on this endpoint       | Don't use cursor parameter           |
| "map is not a function"          | Assumed array, got object            | Check for `.result` wrapper         |
| "Property does not exist on type" | Wrong field name (case sensitive) | Verify exact name in rule file      |
| NaN when parsing numbers            | Wrong number format/radix         | Check hex vs decimal                |
| Invalid Date when parsing timestamp | Wrong timestamp format             | Check ISO vs Unix                  |

## Prevention Checklist

Before implementing ANY endpoint:

- [ ] Read the endpoint rule file
- [ ] Check the HTTP method (GET vs POST vs PUT vs DELETE)
- [ ] Check the exact endpoint path (path params vs query params)
- [ ] Verify the "Example Response" structure
- [ ] Note EVERY field name (snake_case vs camelCase)
- [ ] Note EVERY data type (string vs number vs boolean)
- [ ] Check for wrapper structure (`result`, `cursor`, `page`)
- [ ] Test with real API response (not just examples)

Skipping any of these steps will result in bugs.
