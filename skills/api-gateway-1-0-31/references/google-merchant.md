# Google Merchant Routing Reference

**App name:** `google-merchant`
**Base URL proxied:** `merchantapi.googleapis.com`

## API Path Pattern

```
/google-merchant/{sub-api}/{version}/accounts/{accountId}/{resource}
```

The Merchant API uses sub-APIs: `products`, `accounts`, `datasources`, `reports`, `promotions`, `inventories`, `notifications`, `conversions`, `lfp`

## Common Endpoints

### List Products
```bash
GET /google-merchant/products/v1/accounts/{accountId}/products
```

### Get Product
```bash
GET /google-merchant/products/v1/accounts/{accountId}/products/{productId}
```

Product ID format: `contentLanguage~feedLabel~offerId` (e.g., `en~US~sku123`)

### Insert Product Input
```bash
POST /google-merchant/products/v1/accounts/{accountId}/productInputs:insert?dataSource=accounts/{accountId}/dataSources/{dataSourceId}
Content-Type: application/json

{
  "offerId": "sku123",
  "contentLanguage": "en",
  "feedLabel": "US",
  "attributes": {
    "title": "Product Title",
    "link": "https://example.com/product",
    "imageLink": "https://example.com/image.jpg",
    "availability": "in_stock",
    "price": {"amountMicros": "19990000", "currencyCode": "USD"}
  }
}
```

### Delete Product Input
```bash
DELETE /google-merchant/products/v1/accounts/{accountId}/productInputs/{productId}?dataSource=accounts/{accountId}/dataSources/{dataSourceId}
```

### List Data Sources
```bash
GET /google-merchant/datasources/v1/accounts/{accountId}/dataSources
```

### Search Reports
```bash
POST /google-merchant/reports/v1/accounts/{accountId}/reports:search
Content-Type: application/json

{
  "query": "SELECT offer_id, title, clicks FROM product_performance_view WHERE date BETWEEN '2026-01-01' AND '2026-01-31'"
}
```

### List Promotions
```bash
GET /google-merchant/promotions/v1/accounts/{accountId}/promotions
```

### Get Account
```bash
GET /google-merchant/accounts/v1/accounts/{accountId}
```

### List Local Inventories
```bash
GET /google-merchant/inventories/v1/accounts/{accountId}/products/{productId}/localInventories
```

## Notes

- Authentication is automatic - the router injects the OAuth token
- Account ID is your Merchant Center numeric ID (visible in MC URL)
- Product IDs use format `contentLanguage~feedLabel~offerId`
- Monetary values use micros (divide by 1,000,000)
- Products can only be inserted in data sources of type `API`
- Uses token-based pagination with `pageSize` and `pageToken`

## Resources

- [Merchant API Overview](https://developers.google.com/merchant/api/overview)
- [Merchant API Reference](https://developers.google.com/merchant/api/reference/rest)
- [Products Guide](https://developers.google.com/merchant/api/guides/products/overview)
- [Reports Guide](https://developers.google.com/merchant/api/guides/reports)
