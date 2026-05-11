# Response Patterns Reference

Complete reference for pagination patterns and response wrapper structures in Moralis Data API.

## Table of Contents

- [Pattern 1: No Pagination (Single Result)](#pattern-1-no-pagination-single-result)
- [Pattern 2: Simple Cursor/Page](#pattern-2-simple-cursorpage)
- [Pattern 3: Full Pagination with Metadata](#pattern-3-full-pagination-with-metadata)
- [Pattern 4: Direct Array (No Wrapper)](#pattern-4-direct-array-no-wrapper)
- [How to Detect Which Pattern](#how-to-detect-which-pattern)
- [Common Access Patterns](#common-access-patterns)
- [Error Handling by Pattern](#error-handling-by-pattern)
- [Best Practices](#best-practices)

---

## Pattern 1: No Pagination (Single Result)

### Description
Returns a single object with no pagination.

### Common Endpoints
- `getBlock`
- `getTransaction`
- `getTransactionVerbose`
- `getNativeBalance`
- `getTokenPrice`
- `getPairPrice`
- `getDateToBlock`
- `getLatestBlockNumber`

### Example Response

```typescript
{
  "hash": "0x...",
  "block_number": 12386788,
  "timestamp": "2021-05-07T11:08:35.000Z"
}
```

### Usage Pattern

```typescript
// No array handling needed
const block = await getBlock(blockNumber);
console.log(block.hash);
console.log(block.block_number);
```

## Pattern 2: Simple Cursor/Page

### Description
Returns wrapped object with `result`, `cursor`, `page`, and `page_size`. Data is in `result` array.

### Common Endpoints
- `getWalletTransactions`
- `getWalletTransactionsVerbose`

### Example Response

```typescript
{
  "cursor": "<cursor_value>",
  "page": "2",
  "page_size": "100",
  "result": [
    { "hash": "0x...", ... },
    { "hash": "0x...", ... }
  ]
}
```

### Usage Pattern

```typescript
// First page
const { result, cursor, page } = await getWalletTransactions(address, chain, limit);

// Next page
const { result: nextResults, cursor: nextCursor, page: nextPage } =
  await getWalletTransactions(address, chain, limit, cursor);

// Process results
result.forEach(tx => {
  console.log(tx.hash);
});
```

## Pattern 3: Full Pagination with Metadata

### Description
Returns wrapped object with `page`, `page_size`, `cursor`, and `result`. Similar to Pattern 2 but with explicit `page` field.

### Common Endpoints
- `getWalletHistory`
- `getNFTTransfers`
- `getErc20Transfers` (getWalletTokenTransfers)
- `getWalletNFTTransfers`
- `getTokenTransfers`

### Example Response

```typescript
{
  "page": "1",
  "page_size": "100",
  "cursor": "<cursor_value>",
  "result": [
    { "token_address": "0x...", ... },
    { "token_address": "0x...", ... }
  ]
}
```

### Usage Pattern

```typescript
// First page
const { result, cursor, page, pageSize } = await getWalletHistory(address, chain, limit);

// Next page
const { result: nextResults, cursor: nextCursor, page: nextPage } =
  await getWalletHistory(address, chain, limit, cursor);

// Process results
result.forEach(item => {
  console.log(item.token_address);
});
```

## Pattern 4: Direct Array (No Wrapper)

### Description
Returns an array directly at top level. No wrapper object.

### Common Endpoints
- `getWalletTokenBalancesPrice`
- `getTokenMetadata` (sometimes, depends on endpoint)
- `getTokenOwners`
- `getWalletNFTs`
- `getContractNFTs`
- `getMultipleTokenMetadata`

### Example Response

```typescript
[
  {
    "token_address": "0x...",
    "name": "USDC",
    "symbol": "USDC",
    "decimals": 6,
    "balance": "100000000"
  },
  {
    "token_address": "0x...",
    "name": "USDT",
    "symbol": "USDT",
    "decimals": 18,
    "balance": "500000000000000000000"
  }
]
```

### Usage Pattern

```typescript
// Direct array access - no .result needed
const tokens = await getWalletTokenBalancesPrice(address, chain);

tokens.forEach(token => {
  console.log(token.token_address);
  console.log(token.balance);
});
```

## How to Detect Which Pattern

### Step-by-Step Detection

1. **Read the endpoint rule file** - Look for "Example Response" section
2. **Check if `result` key exists** - If yes, data is wrapped
3. **Check if `cursor` key exists** - If yes, pagination is supported
4. **Check if top-level is array** - If yes, direct array response
5. **Verify with example** - Match the example response structure in rule file

### Detection Helper Function

```typescript
interface ApiResponse<T = any> {
  result?: T[];
  cursor?: string;
  page?: string;
  page_size?: string;
}

function getResponseStructure(data: any): 'single' | 'cursor' | 'direct-array' {
  // Direct array
  if (Array.isArray(data)) return 'direct-array';

  // Wrapped with result
  if (data.result !== undefined) {
    if (data.cursor !== undefined) return 'cursor';
    if (data.page !== undefined) return 'cursor';
    return 'wrapped'; // result exists but no cursor
  }

  // Single object
  return 'single';
}
```

## Common Access Patterns

### Safe Data Extraction

```typescript
// Pattern 1: Single result
const block: any = await getBlock(blockNumber);

// Pattern 2/3: Wrapped with result
const { result: transactions } = await getWalletTransactions(address, chain);

// Pattern 4: Direct array
const tokens = await getWalletTokenBalancesPrice(address, chain);

// Universal safe access
function extractData<T = any>(response: any): T | T[] {
  if (Array.isArray(response)) return response;
  if (response.result) return response.result;
  return response;
}
```

### Pagination Wrapper

```typescript
async function fetchAllPages<T = any>(
  fetchFn: (cursor?: string) => Promise<{ result: T[]; cursor?: string }>,
  maxPages: number = 10
): Promise<T[]> {
  const allResults: T[] = [];
  let cursor: string | undefined;

  for (let i = 0; i < maxPages; i++) {
    const { result, cursor: newCursor } = await fetchFn(cursor);
    allResults.push(...result);

    if (!newCursor) break; // No more pages
    cursor = newCursor;
  }

  return allResults;
}

// Usage
const allTransactions = await fetchAllPages(
  (cursor) => getWalletTransactions(address, chain, 100, cursor)
);
```

## Error Handling by Pattern

### Pattern 1: Single Result

```typescript
try {
  const block = await getBlock(blockNumber);
  if (!block) {
    throw new Error('Block not found');
  }
} catch (error) {
  console.error('Failed to fetch block:', error);
}
```

### Pattern 2/3: Cursor/Page

```typescript
try {
  const { result, cursor } = await getWalletTransactions(address, chain, limit);
  if (!result || result.length === 0) {
    console.log('No transactions found');
    return [];
  }
} catch (error) {
  console.error('Failed to fetch transactions:', error);
}
```

### Pattern 4: Direct Array

```typescript
try {
  const tokens = await getWalletTokenBalancesPrice(address, chain);
  if (!tokens || tokens.length === 0) {
    console.log('No tokens found');
    return [];
  }
} catch (error) {
  console.error('Failed to fetch tokens:', error);
}
```

## Best Practices

1. **Always read the endpoint rule file first** - Example response shows exact structure
2. **Never assume array vs object** - Check if `result` wrapper exists
3. **Use optional chaining** - Access wrapped data safely: `data.result?.[0]?.field`
4. **Test pagination** - Verify cursor works by fetching 2 pages in development
5. **Handle empty results** - Some endpoints return empty arrays or empty `result`
6. **Log response structure** - If unexpected, verify against rule file example
