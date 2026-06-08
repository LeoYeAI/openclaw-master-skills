# OpenSea Marketplace API

This reference covers the marketplace endpoints for buying and selling NFTs on OpenSea.

## Overview

OpenSea uses the **Seaport protocol** for all marketplace orders. The API provides endpoints to:
- Query existing listings and offers
- Build new listings and offers (returns unsigned Seaport orders)
- Fulfill orders (accept listings or offers)
- Cancel orders

**Important**: Creating and fulfilling orders requires wallet signatures. The API returns order data that must be signed client-side before submission.

## Base URL and Authentication

```
Base URL: https://api.opensea.io/api/v2
Auth: x-api-key: $OPENSEA_API_KEY
```

## Supported Chains

| Chain | Identifier |
|-------|------------|
| Ethereum | `ethereum` |
| Polygon | `matic` |
| Arbitrum | `arbitrum` |
| Optimism | `optimism` |
| Base | `base` |
| Avalanche | `avalanche` |
| Klaytn | `klaytn` |
| Zora | `zora` |
| Blast | `blast` |
| Sepolia (testnet) | `sepolia` |

---

## Read Operations (GET)

### Get Best Listing for NFT

Returns the lowest-priced active listing for an NFT.

```bash
GET /api/v2/listings/collection/{collection_slug}/nfts/{identifier}/best
```

**Parameters:**
- `collection_slug`: Collection slug (e.g., `boredapeyachtclub`)
- `identifier`: NFT identifier (token ID)

**Example:**
```bash
scripts/opensea-get.sh "/api/v2/listings/collection/boredapeyachtclub/nfts/1234/best"
```

### Get Best Offer for NFT

Returns the highest active offer for an NFT.

```bash
GET /api/v2/offers/collection/{collection_slug}/nfts/{identifier}/best
```

**Example:**
```bash
scripts/opensea-get.sh "/api/v2/offers/collection/boredapeyachtclub/nfts/1234/best"
```

### Get All Listings for Collection

Returns all active listings for a collection.

```bash
GET /api/v2/listings/collection/{collection_slug}/all
```

**Query parameters:**
- `limit`: Page size (default 50, max 100)
- `next`: Cursor for pagination

**Example:**
```bash
scripts/opensea-listings-collection.sh boredapeyachtclub 50
```

### Get All Offers for Collection

Returns all active offers for a collection.

```bash
GET /api/v2/offers/collection/{collection_slug}/all
```

**Example:**
```bash
scripts/opensea-offers-collection.sh boredapeyachtclub 50
```

### Get Listings for Specific NFT

```bash
GET /api/v2/orders/{chain}/seaport/listings
```

**Query parameters:**
- `asset_contract_address`: Contract address
- `token_ids`: Comma-separated token IDs
- `limit`, `next`: Pagination

**Example:**
```bash
scripts/opensea-get.sh "/api/v2/orders/ethereum/seaport/listings" "asset_contract_address=0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d&token_ids=1234"
```

### Get Offers for Specific NFT

```bash
GET /api/v2/orders/{chain}/seaport/offers
```

**Query parameters:**
- `asset_contract_address`: Contract address
- `token_ids`: Comma-separated token IDs

**Example:**
```bash
scripts/opensea-get.sh "/api/v2/orders/ethereum/seaport/offers" "asset_contract_address=0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d&token_ids=1234"
```

### Get Order by Hash

Retrieve details of a specific order.

```bash
GET /api/v2/orders/chain/{chain}/protocol/{protocol_address}/hash/{order_hash}
```

**Example:**
```bash
scripts/opensea-get.sh "/api/v2/orders/chain/ethereum/protocol/0x0000000000000068f116a894984e2db1123eb395/hash/0x..."
```

---

## Write Operations (POST)

### Build a Listing

Creates an unsigned Seaport listing order. Returns order parameters to sign.

```bash
POST /api/v2/orders/{chain}/seaport/listings
```

**Request body:**
```json
{
  "parameters": {
    "offerer": "0xYourWalletAddress",
    "offer": [{
      "itemType": 2,
      "token": "0xContractAddress",
      "identifierOrCriteria": "1234",
      "startAmount": "1",
      "endAmount": "1"
    }],
    "consideration": [{
      "itemType": 0,
      "token": "0x0000000000000000000000000000000000000000",
      "identifierOrCriteria": "0",
      "startAmount": "1000000000000000000",
      "endAmount": "1000000000000000000",
      "recipient": "0xYourWalletAddress"
    }],
    "startTime": "1704067200",
    "endTime": "1735689600",
    "orderType": 0,
    "zone": "0x0000000000000000000000000000000000000000",
    "zoneHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "salt": "random_salt_value",
    "conduitKey": "0x0000007b02230091a7ed01230072f7006a004d60a8d4e71d599b8104250f0000",
    "totalOriginalConsiderationItems": 1
  },
  "signature": "0xSignedOrderSignature"
}
```

**Item Types:**
- `0`: Native currency (ETH, MATIC, etc.)
- `1`: ERC20 token
- `2`: ERC721 NFT
- `3`: ERC1155 NFT

**Example (curl):**
```bash
curl -X POST "https://api.opensea.io/api/v2/orders/ethereum/seaport/listings" \
  -H "x-api-key: $OPENSEA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"parameters": {...}, "signature": "0x..."}'
```

### Build an Offer

Creates an unsigned Seaport offer order.

```bash
POST /api/v2/orders/{chain}/seaport/offers
```

**Request body structure** (similar to listings, but offer contains payment and consideration contains NFT):
```json
{
  "parameters": {
    "offerer": "0xBuyerWalletAddress",
    "offer": [{
      "itemType": 1,
      "token": "0xWETHAddress",
      "identifierOrCriteria": "0",
      "startAmount": "1000000000000000000",
      "endAmount": "1000000000000000000"
    }],
    "consideration": [{
      "itemType": 2,
      "token": "0xNFTContractAddress",
      "identifierOrCriteria": "1234",
      "startAmount": "1",
      "endAmount": "1",
      "recipient": "0xBuyerWalletAddress"
    }]
  },
  "signature": "0x..."
}
```

### Fulfill a Listing (Buy NFT)

Accept an existing listing to purchase an NFT.

```bash
POST /api/v2/listings/fulfillment_data
```

**Request body:**
```json
{
  "listing": {
    "hash": "0xOrderHash",
    "chain": "ethereum",
    "protocol_address": "0x0000000000000068f116a894984e2db1123eb395"
  },
  "fulfiller": {
    "address": "0xBuyerWalletAddress"
  }
}
```

**Response:** Returns transaction data for the buyer to submit on-chain.

### Fulfill an Offer (Sell NFT)

Accept an existing offer to sell your NFT.

```bash
POST /api/v2/offers/fulfillment_data
```

**Request body:**
```json
{
  "offer": {
    "hash": "0xOfferOrderHash",
    "chain": "ethereum",
    "protocol_address": "0x0000000000000068f116a894984e2db1123eb395"
  },
  "fulfiller": {
    "address": "0xSellerWalletAddress"
  },
  "consideration": {
    "asset_contract_address": "0xNFTContract",
    "token_id": "1234"
  }
}
```

### Cancel an Order

Cancel an active listing or offer.

```bash
POST /api/v2/orders/chain/{chain}/protocol/{protocol_address}/hash/{order_hash}/cancel
```

**Note:** Cancellation requires an on-chain transaction. The API returns the transaction data to execute.

---

## Workflow: Buying an NFT

1. **Find the NFT** - Use `opensea-nft.sh` to get NFT details
2. **Check listings** - Use `opensea-get.sh` to get best listing
3. **Get fulfillment data** - POST to `/api/v2/listings/fulfillment_data`
4. **Execute transaction** - Sign and submit the returned transaction data

```bash
# Step 1: Get NFT info
./scripts/opensea-nft.sh ethereum 0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d 1234

# Step 2: Get best listing
./scripts/opensea-get.sh "/api/v2/listings/collection/boredapeyachtclub/nfts/1234/best"

# Step 3: Request fulfillment (requires POST - see marketplace scripts)
./scripts/opensea-fulfill-listing.sh ethereum 0x_order_hash 0x_your_wallet
```

## Workflow: Selling an NFT (Creating a Listing)

1. **Build the listing** - POST to `/api/v2/orders/{chain}/seaport/listings`
2. **Sign the order** - Use wallet to sign the Seaport order
3. **Submit signed order** - POST again with signature
4. **Monitor** - Check listing via `/api/v2/listings/collection/{slug}/all`

## Workflow: Making an Offer

1. **Ensure WETH approval** - Buyer needs WETH allowance for Seaport
2. **Build the offer** - POST to `/api/v2/orders/{chain}/seaport/offers`
3. **Sign the order** - Wallet signature required
4. **Submit** - POST with signature

## Workflow: Accepting an Offer

1. **View offers** - Use `opensea-offers-collection.sh`
2. **Get fulfillment data** - POST to `/api/v2/offers/fulfillment_data`
3. **Execute** - Submit the returned transaction

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request - invalid parameters |
| 401 | Unauthorized - missing or invalid API key |
| 404 | Not found - order/NFT doesn't exist |
| 429 | Rate limited - too many requests |
| 500 | Server error |

## Rate Limits

- Standard: 60 requests/minute
- With API key: Higher limits (check your dashboard)

---

## Seaport Contract Addresses

| Chain | Seaport 1.6 Address |
|-------|---------------------|
| All chains | `0x0000000000000068F116a894984e2DB1123eB395` |

---

## Tips

1. **Always use WETH for offers** - Native ETH cannot be used for offers due to ERC20 approval requirements
2. **Check approval status** - Before creating listings, ensure Seaport has approval for your NFTs
3. **Test on Sepolia first** - Use testnet before mainnet transactions
4. **Handle expiration** - Orders have startTime/endTime - check these before fulfilling
5. **Monitor events** - Use Stream API for real-time order updates
