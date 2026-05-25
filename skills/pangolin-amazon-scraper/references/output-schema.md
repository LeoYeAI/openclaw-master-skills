# Output Schema Reference

This document describes the JSON output structure produced by `scripts/pangolin.py`.

## Success Envelope

All successful responses follow this structure:

```json
{
  "success": true,
  "task_id": "02b3e90810f0450ca6d41244d6009d0f",
  "url": "https://www.amazon.com/dp/B0DYTF8L2W",
  "metadata": {
    "executionTime": 1791,
    "parserType": "amzProductDetail",
    "parsedAt": "2026-01-13T06:42:01.861Z"
  },
  "results": [ ... ],
  "results_count": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` for successful responses |
| `task_id` | string | Unique task identifier for this request |
| `url` | string | The URL that was scraped |
| `metadata` | object | Execution metadata (may be absent in legacy format) |
| `metadata.executionTime` | int | Execution time in milliseconds |
| `metadata.parserType` | string | Parser used for this request |
| `metadata.parsedAt` | string | ISO 8601 timestamp of when parsing completed |
| `results` | array | Array of result objects (structure varies by parser) |
| `results_count` | int | Number of items in `results` |

## Error Envelope

All errors (both script-level and API-level) follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "hint": "Actionable suggestion to resolve the issue"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `false` for errors |
| `error.code` | string | Machine-readable error code (see table below) |
| `error.message` | string | Human-readable error description |
| `error.hint` | string | Actionable suggestion (optional for some errors) |

### Error Codes

| Code | Meaning | Typical Exit Code |
|------|---------|-------------------|
| `MISSING_ENV` | No credentials configured | 4 |
| `AUTH_FAILED` | Email/password incorrect | 4 |
| `RATE_LIMIT` | HTTP 429 rate limiting | 3 |
| `NETWORK` | Connection or HTTP error | 3 |
| `SSL_CERT` | SSL certificate verification failed | 3 |
| `API_ERROR` | Pangolin API returned non-zero code | 1 |
| `USAGE_ERROR` | Invalid CLI arguments or missing required inputs | 2 |

## Per-Parser Result Fields

### amzProductDetail

Single product detail page. Returns 1 result object.

**Guaranteed fields:**

| Field | Type | Example |
|-------|------|---------|
| `asin` | string | `"B0DYTF8L2W"` |
| `title` | string | `"Wireless Mouse, 2.4G Ergonomic..."` |
| `price` | string | `"$29.99"` |
| `image` | string | `"https://m.media-amazon.com/images/I/..."` |

**Common fields (usually present):**

| Field | Type | Description |
|-------|------|-------------|
| `brand` | string | Brand name |
| `star` | string | Star rating, e.g., `"4.5"` |
| `rating` | string | Number of ratings, e.g., `"1,234"` |
| `strikethroughPrice` | string | Original price before discount |
| `images` | array[string] | Additional product images |
| `highResolutionImages` | array[string] | High-resolution image URLs |
| `galleryThumbnails` | array[string] | Gallery thumbnail URLs |
| `inStock` | string | Stock status, e.g., `"In Stock"` |
| `seller` | string | Seller name |
| `shipper` | string | Shipping provider |
| `merchant_id` | string | Merchant identifier |
| `has_cart` | boolean | Whether "Add to Cart" is available |
| `features` | array[string] | Bullet-point feature list |
| `badge` | string | Product badge text |
| `acBadge` | string | Amazon's Choice badge text |
| `color` | string | Selected color variant |
| `size` | string | Selected size variant |
| `category_id` | string | Category node ID |
| `category_name` | string | Category name |
| `bestSellersRank` | string | BSR string, e.g., `"#1,234"` |
| `deliveryTime` | string | Delivery estimate, e.g., `"Tomorrow"` |
| `first_date` | string | First available date |
| `coupon` | string | Active coupon text |
| `sales` | string | Sales volume, e.g., `"10K+ bought in past month"` |
| `pkg_dims` | string | Package dimensions |
| `pkg_weight` | string | Package weight |
| `product_dims` | string | Product dimensions |
| `product_weight` | string | Product weight |
| `ratingDistribution` | object | Star distribution breakdown |
| `reviews` | array | Embedded review snippets |
| `aiReviewsSummary` | string | AI-generated review summary |
| `productDescription` | string | Full product description |
| `productOverview` | object | Structured product overview |
| `attributes` | array | Product attribute key-value pairs |
| `otherAsins` | array | Related/variant ASINs |

### amzKeyword

Keyword search results. Returns multiple result objects.

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `asin` | string | Yes | Product ASIN |
| `title` | string | Yes | Product title |
| `price` | string | Yes | Price string |
| `star` | string | No | Star rating |
| `rating` | string | No | Number of ratings |
| `image` | string | Yes | Product image URL |
| `sales` | string | No | Sales volume text |
| `rank` | int | No | Position in search results |
| `sponsored` | boolean | No | Whether the listing is sponsored |
| `spRank` | int | No | Sponsored rank position |
| `badge` | string | No | Badge text (e.g., "Best Seller") |
| `delivery` | string | No | Delivery info |

### amzProductOfCategory

Category listing results. Returns multiple result objects.

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `asin` | string | Yes | Product ASIN |
| `title` | string | Yes | Product title |
| `price` | string | Yes | Price string |
| `star` | string | No | Star rating |
| `rating` | string | No | Number of ratings |
| `image` | string | Yes | Product image URL |

### amzProductOfSeller

Seller product listing. Returns multiple result objects.

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `asin` | string | Yes | Product ASIN |
| `title` | string | Yes | Product title |
| `price` | string | Yes | Price string |
| `star` | string | No | Star rating |
| `rating` | string | No | Number of ratings |
| `image` | string | Yes | Product image URL |

### amzBestSellers

Bestseller ranking results. Returns multiple result objects.

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `asin` | string | Yes | Product ASIN |
| `rank` | int | Yes | Bestseller rank position |
| `title` | string | Yes | Product title |
| `price` | string | Yes | Price string |
| `star` | string | No | Star rating |
| `rating` | string | No | Number of ratings |
| `image` | string | Yes | Product image URL |

### amzNewReleases

New releases ranking. Returns multiple result objects.

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `asin` | string | Yes | Product ASIN |
| `rank` | int | Yes | New release rank position |
| `title` | string | Yes | Product title |
| `price` | string | Yes | Price string |
| `star` | string | No | Star rating |
| `rating` | string | No | Number of ratings |
| `image` | string | Yes | Product image URL |

### amzFollowSeller

Seller/variant options for a product. Returns 1 result object with nested data.

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `options` | array | Yes | Available variant/seller options |
| `price` | string | Yes | Price for the current option |
| `delivery` | string | No | Delivery estimate |
| `shipsFrom` | string | No | Shipping origin |
| `soldBy` | string | No | Seller name |

### amzReviewV2

Product reviews. Returns multiple review objects.

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `date` | string | Yes | Review date (e.g., `"2026-01-13"`) |
| `country` | string | Yes | Reviewer's country |
| `star` | string | Yes | Star rating (e.g., `"5.0"`) |
| `author` | string | Yes | Reviewer name |
| `title` | string | Yes | Review title |
| `content` | string | Yes | Review body text |
| `purchased` | boolean | Yes | Whether the reviewer made a verified purchase |
| `vineVoice` | boolean | Yes | Whether the reviewer is a Vine Voice |
| `helpful` | string | No | Helpful vote text (e.g., `"5 people found this helpful"`) |
| `reviewId` | string | Yes | Unique review identifier |
| `reviewLink` | string | No | URL to the review |
| `authorId` | string | No | Author's Amazon ID |
| `authorLink` | string | No | URL to the author's profile |
| `attributes` | array | No | Additional review attributes |

## Field Presence Notes

- **Guaranteed** fields are always present in the result object when the API returns successfully.
- **Optional/Common** fields depend on the product listing, availability of data on Amazon, and the specific Amazon marketplace.
- Fields may be empty strings (`""`) or `null` even when present.
- Price formats vary by region (e.g., `"$29.99"`, `"EUR 24,99"`, `"2,980"` for JPY).
- Star ratings are returned as strings, not numbers.
- The `results` array may be empty (`[]`) if no matching data was found.
