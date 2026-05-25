# Amazon Scrape API Reference

Scrape Amazon product data: details, search results, category listings, best sellers, and more.

## Endpoint

```
POST https://scrapeapi.pangolinfo.com/api/v1/scrape
```

Note: Amazon uses **v1** endpoint, not v2 (which is used by Google SERP APIs).

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

## Request Body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| url | Conditional | string | Amazon page URL. Not required if `site` + `content` are provided. |
| site | Conditional | string | Amazon site code (e.g. `amz_us`). Not required if `url` is provided. |
| content | Conditional | string | Content identifier (see content mapping below). Not required if `url` is provided. |
| parserName | Yes | string | Parser type (see below) |
| format | Yes | string | `"json"`, `"rawHtml"`, or `"markdown"` |
| bizContext | Yes | object | Business context |
| bizContext.zipcode | Yes | string | Zipcode for localized pricing |

### Input Modes

**Mode 1: URL-based (legacy)**
Provide `url` directly. `site` and `content` are optional.

```json
{
  "url": "https://www.amazon.com/dp/B0DYTF8L2W",
  "parserName": "amzProductDetail",
  "format": "json",
  "bizContext": {"zipcode": "10041"}
}
```

**Mode 2: Content-based (recommended)**
Provide `site` + `content`. No URL needed.

```json
{
  "site": "amz_us",
  "content": "B0DYTF8L2W",
  "parserName": "amzProductDetail",
  "format": "json",
  "bizContext": {"zipcode": "10041"}
}
```

### Content Mapping by Parser

| Parser | content value | Example |
|--------|-------------|---------|
| `amzProductDetail` | ASIN | `B0DYTF8L2W` |
| `amzKeyword` | Keyword | `wireless mouse` |
| `amzProductOfCategory` | Category Node ID | `172282` |
| `amzProductOfSeller` | Seller ID | `A1B2C3D4E5` |
| `amzBestSellers` | Category keyword | `electronics` |
| `amzNewReleases` | Category keyword | `toys` |
| `amzFollowSeller` | ASIN | `B0DYTF8L2W` |

### Amazon Site Codes

| Site Code | Region | Domain |
|-----------|--------|--------|
| `amz_us` | United States | amazon.com |
| `amz_uk` | United Kingdom | amazon.co.uk |
| `amz_ca` | Canada | amazon.ca |
| `amz_de` | Germany | amazon.de |
| `amz_fr` | France | amazon.fr |
| `amz_jp` | Japan | amazon.co.jp |
| `amz_it` | Italy | amazon.it |
| `amz_es` | Spain | amazon.es |
| `amz_au` | Australia | amazon.com.au |
| `amz_mx` | Mexico | amazon.com.mx |
| `amz_sa` | Saudi Arabia | amazon.sa |
| `amz_ae` | UAE | amazon.ae |
| `amz_br` | Brazil | amazon.com.br |

## Parser Types

| Parser | Use Case |
|--------|----------|
| `amzProductDetail` | Single product page |
| `amzKeyword` | Keyword search results |
| `amzProductOfCategory` | Category listing |
| `amzProductOfSeller` | Seller's products |
| `amzBestSellers` | Best sellers ranking |
| `amzNewReleases` | New releases ranking |
| `amzFollowSeller` | Variants / other sellers |

## Response

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "json": [
      {
        "metadata": {
          "executionTime": 1791,
          "parserType": "amzProductDetail",
          "parsedAt": "2026-01-13T06:42:01.861Z"
        },
        "code": 0,
        "data": {
          "results": [
            {
              "asin": "B0DYTF8L2W",
              "title": "Product Title",
              "brand": "Brand Name",
              "price": "$29.99",
              "star": "4.5",
              "rating": "1,234",
              "image": "https://m.media-amazon.com/images/...",
              "images": ["url1", "url2"],
              "inStock": "In Stock",
              "seller": "Seller Name",
              "features": ["Feature 1", "Feature 2"],
              "category_name": "Electronics",
              "bestSellersRank": "#1,234",
              "deliveryTime": "Tomorrow",
              "sales": "10K+ bought in past month"
            }
          ]
        }
      }
    ],
    "url": "https://www.amazon.com/dp/B0DYTF8L2W",
    "taskId": "02b3e90810f0450ca6d41244d6009d0f"
  }
}
```

### Response Metadata

| Field | Type | Description |
|-------|------|-------------|
| metadata.executionTime | int | Execution time in milliseconds |
| metadata.parserType | string | Parser used for this request |
| metadata.parsedAt | string | ISO timestamp of when parsing completed |

### Product Detail Fields (amzProductDetail)

**Core:**
`asin`, `title`, `brand`, `price`, `strikethroughPrice`, `star`, `rating`, `image`, `images`, `highResolutionImages`, `galleryThumbnails`

**Inventory & Seller:**
`inStock`, `merchant_id`, `seller`, `shipper`, `has_cart`

**Attributes:**
`color`, `size`, `features`, `badge`, `acBadge` (Amazon's Choice)

**Category & Ranking:**
`category_id`, `category_name`, `bestSellersRank`

**Dimensions:**
`pkg_dims`, `pkg_weight`, `product_dims`, `product_weight`

**Reviews & AI:**
`ratingDistribution`, `reviews`, `aiReviewsSummary`

**Structured Data:**
`productDescription`, `productOverview`, `attributes`, `otherAsins`

**Additional:**
`deliveryTime`, `first_date`, `coupon`, `sales`

### Keyword Search Fields (amzKeyword)

`asin`, `title`, `price`, `star`, `rating`, `image`, `sales`, `rank`, `sponsored`, `spRank`, `badge`, `delivery`

### Category/Seller Product Fields (amzProductOfCategory / amzProductOfSeller)

`asin`, `title`, `price`, `star`, `rating`, `image`

### Ranking Fields (amzBestSellers / amzNewReleases)

`asin`, `rank`, `title`, `price`, `star`, `rating`, `image`

### Variant Fields (amzFollowSeller)

`options`, `price`, `delivery`, `shipsFrom`, `soldBy`

## Amazon Review API

Fetch product reviews with star filtering and sorting. Uses the same v1 endpoint.

### Request Body

```json
{
  "url": "https://www.amazon.com",
  "format": "json",
  "parserName": "amzReviewV2",
  "bizContext": {
    "bizKey": "review",
    "asin": "B00163U4LK",
    "pageCount": 1,
    "filterByStar": "critical",
    "sortBy": "recent"
  }
}
```

### bizContext Parameters

| Field | Type | Description |
|-------|------|-------------|
| bizKey | string | Must be `"review"` |
| asin | string | Amazon product ASIN |
| pageCount | int | Number of pages to fetch (5 credits per page) |
| filterByStar | string | Star filter (see below) |
| sortBy | string | `"recent"` or `"helpful"` |

### filterByStar Options

| Value | Description |
|-------|-------------|
| `all_stars` | All reviews |
| `five_star` | 5-star reviews only |
| `four_star` | 4-star reviews only |
| `three_star` | 3-star reviews only |
| `two_star` | 2-star reviews only |
| `one_star` | 1-star reviews only |
| `positive` | Positive reviews (4-5 stars) |
| `critical` | Critical reviews (1-3 stars) |

### Review Response Fields

Each review object contains:

`date`, `country`, `star`, `reviewLink`, `author`, `title`, `authorId`, `content`, `purchased`, `vineVoice`, `authorLink`, `attributes`, `helpful`, `reviewId`

### Review Response Example

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "json": [
      {
        "metadata": {"executionTime": 153, "parserType": "amzReviewV2", "parsedAt": "..."},
        "code": 0,
        "data": {
          "results": [
            {
              "date": "2026-01-13",
              "country": "United States",
              "star": "5.0",
              "author": "Tucker&Emily",
              "title": "Perfect",
              "content": "Great coat. It fits well and is very attractive.",
              "purchased": true,
              "vineVoice": false,
              "helpful": "",
              "reviewId": "R1IIVEFNGPSLW3"
            }
          ]
        }
      }
    ],
    "url": "https://www.amazon.com",
    "taskId": "..."
  }
}
```

## Cost

| Format | Credits |
|--------|---------|
| Scrape `json` | 1 per request |
| Scrape `rawHtml` / `markdown` | 0.75 per request |
| Reviews | 5 per page |

Average response time: ~5 seconds.
