# OpenSea REST API Reference

## Base URL and Authentication

```
Base URL: https://api.opensea.io
Auth header: x-api-key: $OPENSEA_API_KEY
```

## Pagination

List endpoints support cursor-based pagination:
- `limit`: Page size (default varies, max 100)
- `next`: Cursor token from previous response

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

## Endpoint Reference

### Collections

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/collections/{slug}` | GET | Single collection details |
| `/api/v2/collections/{slug}/stats` | GET | Collection statistics (floor, volume) |
| `/api/v2/collections` | GET | List multiple collections |

### NFTs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/chain/{chain}/contract/{contract}/nfts/{token_id}` | GET | Single NFT details |
| `/api/v2/collection/{slug}/nfts` | GET | NFTs by collection |
| `/api/v2/chain/{chain}/account/{address}/nfts` | GET | NFTs by wallet |
| `/api/v2/chain/{chain}/contract/{contract}/nfts` | GET | NFTs by contract |
| `/api/v2/nft/{contract}/{token_id}/refresh` | POST | Refresh NFT metadata |

### Listings

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/listings/collection/{slug}/all` | GET | All listings for collection |
| `/api/v2/listings/collection/{slug}/nfts/{token_id}/best` | GET | Best listing for NFT |
| `/api/v2/orders/{chain}/seaport/listings` | GET | Listings by contract/token |
| `/api/v2/orders/{chain}/seaport/listings` | POST | Create new listing |
| `/api/v2/listings/fulfillment_data` | POST | Get buy transaction data |

### Offers

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/offers/collection/{slug}/all` | GET | All offers for collection |
| `/api/v2/offers/collection/{slug}/nfts/{token_id}/best` | GET | Best offer for NFT |
| `/api/v2/orders/{chain}/seaport/offers` | GET | Offers by contract/token |
| `/api/v2/orders/{chain}/seaport/offers` | POST | Create new offer |
| `/api/v2/offers/fulfillment_data` | POST | Get sell transaction data |

### Orders

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/orders/chain/{chain}/protocol/{protocol}/{hash}` | GET | Get order by hash |
| `/api/v2/orders/chain/{chain}/protocol/{protocol}/{hash}/cancel` | POST | Cancel order |

### Events

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/events/collection/{slug}` | GET | Events by collection |
| `/api/v2/events/chain/{chain}/contract/{contract}/nfts/{token_id}` | GET | Events by NFT |
| `/api/v2/events/chain/{chain}/account/{address}` | GET | Events by account |

### Accounts

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/accounts/{address}` | GET | Account profile |

## Event Types

For the events endpoint, filter with `event_type`:
- `sale` - NFT sold
- `transfer` - NFT transferred
- `listing` - New listing created
- `offer` - New offer made
- `cancel` - Order cancelled
- `redemption` - NFT redeemed

## Rate Limits

- Without API key: 40 requests/minute
- With API key: Higher limits (varies by tier)

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request - check parameters |
| 401 | Unauthorized - missing/invalid API key |
| 404 | Resource not found |
| 429 | Rate limited |
| 500 | Server error |

## Tips

1. Use collection slugs (not addresses) for collection endpoints
2. Use chain identifiers for NFT/account endpoints
3. All timestamps are Unix epoch seconds
4. Prices are in wei (divide by 10^18 for ETH)
5. Use `jq` to parse JSON responses: `./script.sh | jq '.nft.name'`
